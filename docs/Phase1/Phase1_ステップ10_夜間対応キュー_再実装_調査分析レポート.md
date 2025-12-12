# Phase 1: ステップ10 夜間対応キュー 再実装 調査分析レポート

**作成日**: 2025年12月5日  
**実施者**: Auto (AI Assistant)  
**対象**: ステップ10 夜間対応キューセクションの「対応済み」ボタンの再実装に関する調査分析  
**状態**: ✅ **調査分析完了**

---

## 1. 精読した関連書類

### 1.1 主要ドキュメント

1. **Phase 1完了条件・進捗状況・残存課題・ステップ計画** (`docs/Phase1/Phase1_完了条件_進捗状況_残存課題_ステップ計画_20251204_完全版.md`)
   - ステップ10の詳細な再実装内容が記載されている
   - ステップ12完了後に再実装することが決定されている

2. **Phase 1ステップ12 施設設定画面 実装完了レポート** (`docs/Phase1/Phase1_ステップ12_施設設定画面_実装完了レポート.md`)
   - 施設設定画面の実装が完了している
   - `staff_absence_periods`フィールドが追加されている

3. **Phase 1ステップ10 夜間対応キュー 設定と説明文 調査分析レポート** (`docs/Phase1/Phase1_ステップ10_夜間対応キュー_設定と説明文_調査分析レポート_20251205.md`)
   - 夜間時間帯設定の調査結果が記載されている

---

## 2. 現状の実装状況

### 2.1 「対応済み」ボタンの実装状況

#### バックエンド
- ✅ **API実装完了**: `PUT /api/v1/admin/overnight-queue/{queue_id}/resolve`
  - ファイル: `backend/app/api/v1/admin/overnight_queue.py`（158-228行目）
  - 機能: 夜間対応キューアイテムを対応済みとしてマーク
  - 実装状況: 正常に動作する

#### フロントエンド
- ✅ **API連携完了**: `overnightQueueApi.resolveQueueItem()`
  - ファイル: `frontend/src/api/overnightQueue.ts`（43-45行目）
- ✅ **UI実装完了**: `OvernightQueue.vue`で「対応済み」ボタンが実装されている
  - ファイル: `frontend/src/views/admin/OvernightQueue.vue`（264-275行目）
  - 機能: ボタンクリック時にAPIを呼び出し、キュー一覧を再取得

**結論**: 「対応済み」ボタンの機能自体は実装済みで、正常に動作する。

---

## 3. ハードコードされた時間帯（22:00-8:00）の使用箇所

### 3.1 バックエンド

#### 3.1.1 `OvernightQueueService`クラス

**ファイル**: `backend/app/services/overnight_queue_service.py`

**箇所1: クラス定数（25-26行目）**
```python
NIGHT_START = time(22, 0)  # 22:00
NIGHT_END = time(8, 0)     # 8:00
```

**箇所2: `add_to_overnight_queue`メソッド（61行目）**
```python
if local_now.hour >= 22 or local_now.hour < 8:
    # 夜間時間帯
```

**箇所3: `add_to_overnight_queue`メソッド（64-68行目）**
```python
if local_now.hour < 8:
    # 0:00-8:00 → 当日8:00
    scheduled_time_local = local_now.replace(hour=8, minute=0, second=0, microsecond=0)
else:
    # 22:00-23:59 → 翌日8:00
    scheduled_time_local = (local_now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
```

**箇所4: `process_scheduled_notifications`メソッド（169-170行目）**
```python
OvernightQueue.scheduled_notify_at >= now.replace(hour=8, minute=0, second=0, microsecond=0),
OvernightQueue.scheduled_notify_at < now.replace(hour=8, minute=30, second=0, microsecond=0),
```

**問題点**:
- `NIGHT_START`と`NIGHT_END`が使用されていない（コメントのみ）
- 実際の判定は`local_now.hour >= 22 or local_now.hour < 8`で行われている
- 通知時刻は常に8:00に固定されている

#### 3.1.2 `ChatService`クラス

**ファイル**: `backend/app/services/chat_service.py`

**箇所: `process_chat_message`メソッド（135行目）**
```python
# 夜間時間帯（22:00-8:00）の場合
if current_hour >= 22 or current_hour < 8:
    # 夜間対応キューに追加
```

**問題点**:
- ハードコードされた時間帯判定（22:00-8:00）
- 施設設定から取得したスタッフ不在時間帯を使用していない

### 3.2 フロントエンド

#### 3.2.1 `OvernightQueue.vue`

**ファイル**: `frontend/src/views/admin/OvernightQueue.vue`

**箇所: 説明文（43行目）**
```vue
<p class="text-sm text-blue-700 dark:text-blue-300">
  夜間（22:00-8:00）にエスカレーションされた質問は、自動的に翌朝8:00にスタッフへ通知されます。
  MVP期間中は「手動実行」ボタンで通知処理を実行できます。
</p>
```

**問題点**:
- ハードコードされた時間帯（22:00-8:00）が表示されている
- 施設設定で変更したスタッフ不在時間帯が反映されていない
- 通知時刻が8:00固定と表示されている

#### 3.2.2 `FacilitySettings.vue`

**ファイル**: `frontend/src/views/admin/FacilitySettings.vue`

**箇所: 説明文（218行目）**
```vue
<p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
  スタッフが不在の時間帯を設定します。この時間帯にエスカレーションが発生した場合、夜間対応キューに追加されます。
</p>
```

**問題点**:
- 「夜間対応キュー」という名称が使用されている
- 名称の変更が必要かもしれない

---

## 4. 「夜間対応キュー」という名称の使用箇所

### 4.1 バックエンド

- `backend/app/services/overnight_queue_service.py`: クラス名、コメント、ログメッセージ
- `backend/app/api/v1/admin/overnight_queue.py`: APIエンドポイント、コメント
- `backend/app/services/chat_service.py`: コメント
- `backend/app/services/dashboard_service.py`: コメント
- `backend/app/schemas/overnight_queue.py`: スキーマ名、コメント

### 4.2 フロントエンド

- `frontend/src/views/admin/OvernightQueue.vue`: ページタイトル、説明文
- `frontend/src/components/admin/OvernightQueueList.vue`: コンポーネント名、表示テキスト
- `frontend/src/views/admin/Dashboard.vue`: コメント
- `frontend/src/components/admin/Sidebar.vue`: メニュー項目名
- `frontend/src/components/admin/Header.vue`: ページ名
- `frontend/src/router/admin.ts`: ルート名
- `frontend/src/api/overnightQueue.ts`: APIクライアント名、コメント
- `frontend/src/types/dashboard.ts`: 型定義名、コメント
- `frontend/src/views/admin/FacilitySettings.vue`: 説明文

### 4.3 データベース

- `backend/app/models/overnight_queue.py`: モデル名、テーブル名
- `backend/alembic/versions/002_initial_tables.py`: テーブル名

### 4.4 名称変更の検討

**現状**: 「夜間対応キュー」という名称が広く使用されている

**検討事項**:
- 「スタッフ不在時間帯」に変更するか？
- 「不在対応キュー」に変更するか？
- 現状の「夜間対応キュー」を維持するか？

**推奨**: 
- 機能名としては「夜間対応キュー」を維持（既存のコードベースとの整合性）
- ただし、説明文では「スタッフ不在時間帯」という表現を使用する
- 例: 「スタッフ不在時間帯にエスカレーションされた質問は、自動的に翌朝にスタッフへ通知されます。」

---

## 5. 施設設定からスタッフ不在時間帯を取得する方法

### 5.1 データベース構造

**ファイル**: `backend/app/models/facility.py`

**フィールド**: `staff_absence_periods`
- 型: `JSON`
- デフォルト値: `[]`
- データ構造:
```json
[
  {
    "start_time": "22:00",
    "end_time": "08:00",
    "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
  }
]
```

### 5.2 API

**エンドポイント**: `GET /api/v1/admin/facility/settings`

**レスポンス**: `FacilitySettingsResponse`
- `staff_absence_periods`: `List[StaffAbsencePeriod]`

### 5.3 取得方法

1. **バックエンド**: `Facility`モデルから直接取得
   ```python
   facility = await db.get(Facility, facility_id)
   staff_absence_periods = facility.staff_absence_periods or []
   ```

2. **フロントエンド**: APIから取得
   ```typescript
   const settings = await facilityApi.getFacilitySettings()
   const staffAbsencePeriods = settings.staff_absence_periods
   ```

---

## 6. 修正が必要な箇所の詳細

### 6.1 バックエンド

#### 6.1.1 `OvernightQueueService.add_to_overnight_queue`

**修正内容**:
1. `NIGHT_START`と`NIGHT_END`を削除
2. 施設設定から`staff_absence_periods`を取得
3. 現在時刻がスタッフ不在時間帯に該当するか判定
4. 複数の時間帯に対応
5. 通知時刻を動的に計算（最初の不在時間帯の終了時刻を使用）

**修正箇所**:
- 25-26行目: `NIGHT_START`と`NIGHT_END`を削除
- 48-97行目: `add_to_overnight_queue`メソッドを修正

#### 6.1.2 `ChatService.process_chat_message`

**修正内容**:
1. 施設設定から`staff_absence_periods`を取得
2. 現在時刻がスタッフ不在時間帯に該当するか判定
3. 複数の時間帯に対応

**修正箇所**:
- 125-149行目: 夜間対応キュー処理のロジックを修正

#### 6.1.3 `OvernightQueueService.process_scheduled_notifications`

**修正内容**:
1. 通知時刻の判定を動的に変更（8:00固定ではなく、スタッフ不在時間帯の終了時刻を使用）

**修正箇所**:
- 149-223行目: `process_scheduled_notifications`メソッドを修正

### 6.2 フロントエンド

#### 6.2.1 `OvernightQueue.vue`

**修正内容**:
1. 施設設定からスタッフ不在時間帯を取得
2. 説明文を動的に生成
3. 通知時刻を動的に表示

**修正箇所**:
- 42-45行目: 説明文を修正
- 161-276行目: スクリプト部分を修正（施設設定取得の追加）

#### 6.2.2 `FacilitySettings.vue`

**修正内容**:
1. 説明文の「夜間対応キュー」を「スタッフ不在時間帯対応キュー」などに変更（検討が必要）

**修正箇所**:
- 218行目: 説明文を修正

---

## 7. 実装方針

### 7.1 スタッフ不在時間帯の判定ロジック

**要件**:
1. 複数の時間帯に対応
2. 曜日に対応
3. 日を跨ぐ時間帯に対応（例: 22:00-8:00）

**実装案**:
```python
def is_in_staff_absence_period(
    current_time: datetime,
    current_weekday: str,
    staff_absence_periods: List[Dict]
) -> bool:
    """
    現在時刻がスタッフ不在時間帯に該当するか判定
    
    Args:
        current_time: 現在時刻（施設のタイムゾーン）
        current_weekday: 現在の曜日（'mon', 'tue', ...）
        staff_absence_periods: スタッフ不在時間帯のリスト
    
    Returns:
        bool: スタッフ不在時間帯に該当する場合True
    """
    for period in staff_absence_periods:
        # 曜日のチェック
        if current_weekday not in period.get("days_of_week", []):
            continue
        
        start_time_str = period.get("start_time")
        end_time_str = period.get("end_time")
        
        if not start_time_str or not end_time_str:
            continue
        
        # 時刻をパース
        start_hour, start_minute = map(int, start_time_str.split(":"))
        end_hour, end_minute = map(int, end_time_str.split(":"))
        
        start_time = time(start_hour, start_minute)
        end_time = time(end_hour, end_minute)
        current_time_only = current_time.time()
        
        # 日を跨ぐ時間帯の判定（例: 22:00-8:00）
        if start_time > end_time:
            # 日を跨ぐ場合
            if current_time_only >= start_time or current_time_only < end_time:
                return True
        else:
            # 同日内の場合
            if start_time <= current_time_only < end_time:
                return True
    
    return False
```

### 7.2 通知時刻の計算

**要件**:
1. スタッフ不在時間帯の終了時刻を取得
2. 複数の時間帯がある場合は、最初の時間帯の終了時刻を使用
3. 日を跨ぐ時間帯に対応

**実装案**:
```python
def get_next_notification_time(
    current_time: datetime,
    current_weekday: str,
    staff_absence_periods: List[Dict]
) -> datetime:
    """
    次の通知時刻を計算
    
    Args:
        current_time: 現在時刻（施設のタイムゾーン）
        current_weekday: 現在の曜日
        staff_absence_periods: スタッフ不在時間帯のリスト
    
    Returns:
        datetime: 次の通知時刻
    """
    # 現在のスタッフ不在時間帯を取得
    current_period = None
    for period in staff_absence_periods:
        if current_weekday in period.get("days_of_week", []):
            current_period = period
            break
    
    if not current_period:
        # デフォルト: 翌朝8:00
        return (current_time + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    end_time_str = current_period.get("end_time")
    if not end_time_str:
        # デフォルト: 翌朝8:00
        return (current_time + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    end_hour, end_minute = map(int, end_time_str.split(":"))
    
    # 日を跨ぐ時間帯の場合
    start_time_str = current_period.get("start_time")
    if start_time_str:
        start_hour, start_minute = map(int, start_time_str.split(":"))
        if start_hour > end_hour or (start_hour == end_hour and start_minute > end_minute):
            # 日を跨ぐ場合
            if current_time.hour < end_hour or (current_time.hour == end_hour and current_time.minute < end_minute):
                # 当日の終了時刻
                return current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            else:
                # 翌日の終了時刻
                return (current_time + timedelta(days=1)).replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    
    # 同日内の場合
    if current_time.hour < end_hour or (current_time.hour == end_hour and current_time.minute < end_minute):
        # 当日の終了時刻
        return current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    else:
        # 翌日の終了時刻
        return (current_time + timedelta(days=1)).replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
```

---

## 8. 名称変更の検討

### 8.1 「夜間対応キュー」という名称について

**現状**:
- コードベース全体で「夜間対応キュー」という名称が使用されている
- データベースのテーブル名も`overnight_queues`
- APIエンドポイントも`/admin/overnight-queue`

**検討事項**:
1. **名称を変更する場合**:
   - メリット: 「スタッフ不在時間帯」という概念により適した名称になる
   - デメリット: コードベース全体の変更が必要、データベースのテーブル名変更が必要

2. **名称を維持する場合**:
   - メリット: 既存のコードベースとの整合性が保たれる
   - デメリット: 「夜間」という表現が不正確になる可能性がある

**推奨**:
- **名称は維持**（コードベース全体の変更を避ける）
- **説明文を修正**（「スタッフ不在時間帯」という表現を使用）
- 例: 「スタッフ不在時間帯にエスカレーションされた質問は、自動的にスタッフ不在時間帯終了後にスタッフへ通知されます。」

---

## 9. 修正が必要な箇所の一覧

### 9.1 バックエンド

1. **`backend/app/services/overnight_queue_service.py`**
   - `NIGHT_START`と`NIGHT_END`を削除
   - `add_to_overnight_queue`メソッドを修正（スタッフ不在時間帯の判定を追加）
   - `process_scheduled_notifications`メソッドを修正（通知時刻を動的に変更）

2. **`backend/app/services/chat_service.py`**
   - `process_chat_message`メソッドを修正（スタッフ不在時間帯の判定を追加）

3. **新規作成: ユーティリティ関数**
   - `is_in_staff_absence_period`: スタッフ不在時間帯の判定
   - `get_next_notification_time`: 通知時刻の計算

### 9.2 フロントエンド

1. **`frontend/src/views/admin/OvernightQueue.vue`**
   - 施設設定からスタッフ不在時間帯を取得
   - 説明文を動的に生成
   - 通知時刻を動的に表示

2. **`frontend/src/views/admin/FacilitySettings.vue`**
   - 説明文の修正（検討が必要）

3. **`frontend/src/api/facility.ts`**
   - 既に`getFacilitySettings`が実装済み（追加不要）

---

## 10. 実装の優先順位

### 10.1 最優先（必須）

1. **バックエンド: スタッフ不在時間帯の判定ロジック実装**
   - `OvernightQueueService.add_to_overnight_queue`の修正
   - `ChatService.process_chat_message`の修正

2. **バックエンド: 通知時刻の動的計算**
   - `OvernightQueueService.add_to_overnight_queue`の修正

### 10.2 高優先度

3. **フロントエンド: 説明文の動的表示**
   - `OvernightQueue.vue`の修正

4. **バックエンド: 通知処理の修正**
   - `OvernightQueueService.process_scheduled_notifications`の修正

### 10.3 中優先度

5. **フロントエンド: 説明文の修正**
   - `FacilitySettings.vue`の説明文修正（検討が必要）

---

## 11. 注意事項

### 11.1 後方互換性

- 既存のデータベースレコードとの互換性を保つ必要がある
- `staff_absence_periods`が空の場合のデフォルト動作を定義する必要がある

### 11.2 エラーハンドリング

- 施設設定が取得できない場合の処理
- `staff_absence_periods`が不正な形式の場合の処理
- 時間帯のパースエラーの処理

### 11.3 パフォーマンス

- 施設設定の取得はキャッシュを検討する
- スタッフ不在時間帯の判定は効率的に実装する

---

## 12. 次のステップ

### 12.1 実装前の確認事項

- [x] ステップ12（施設設定画面の作成）が完了している
- [x] `staff_absence_periods`フィールドが追加されている
- [x] 施設設定APIが実装されている
- [ ] ユーザーからの実装指示を待つ

### 12.2 実装時の注意事項

1. **バックエンド**:
   - ユーティリティ関数を新規作成
   - 既存のメソッドを段階的に修正
   - テストを十分に実施

2. **フロントエンド**:
   - 施設設定を取得して説明文を動的に生成
   - エラーハンドリングを実装

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-05  
**Status**: ✅ **調査分析完了**


