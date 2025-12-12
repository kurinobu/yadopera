# Phase 1: スタッフ不在時間帯対応キュー 説明文問題 調査分析レポート

**作成日**: 2025年12月5日  
**対象**: スタッフ不在時間帯対応キューページの説明文の問題  
**状態**: ✅ **調査分析完了**

---

## 1. 問題の概要

### 1.1 確認された問題

**現在の表示**:
```
スタッフ不在時間帯（22:00-07:30、11:00-15:00）にエスカレーションされた質問は、自動的に07:30にスタッフへ通知されます。
```

**問題点**:
- 複数の時間帯（22:00-07:30、11:00-15:00）が設定されている場合
- 説明文では「自動的に07:30にスタッフへ通知」と表示されている
- これは最初の時間帯（22:00-07:30）の終了時刻（07:30）のみを表示している
- 11:00-15:00の時間帯にエスカレーションが発生した場合も「07:30に通知」と表示される

### 1.2 調査すべき点

1. **ロジックの問題か？**
   - 11:00-15:00の時間帯にエスカレーションが発生した場合、実際に15:00に通知されるロジックが実装されているか？

2. **表記の問題か？**
   - ロジックは正しく実装されているが、説明文が完成されていないのか？

---

## 2. 調査結果

### 2.1 バックエンドのロジック確認

#### 2.1.1 通知時刻計算ロジック（`staff_absence.py`）

**ファイル**: `backend/app/utils/staff_absence.py`

**実装内容**:
```python
def get_next_notification_time(
    current_time: datetime,
    current_weekday: str,
    staff_absence_periods: List[Dict]
) -> datetime:
    """
    次の通知時刻を計算
    """
    # 現在のスタッフ不在時間帯を取得
    current_period = None
    for period in staff_absence_periods:
        days_of_week = period.get("days_of_week", [])
        if days_of_week and current_weekday not in days_of_week:
            continue
        
        start_time_str = period.get("start_time")
        end_time_str = period.get("end_time")
        
        if start_time_str and end_time_str:
            current_period = period
            break  # ← 最初に該当する時間帯を使用
    
    # 該当する時間帯の終了時刻を計算
    end_time_str = current_period.get("end_time")
    # ... 終了時刻を返す
```

**動作**:
- 現在時刻が該当する時間帯を探す（最初に該当する時間帯を使用）
- その時間帯の終了時刻を返す
- **11:00-15:00の時間帯にエスカレーションが発生した場合、15:00に通知されるロジックは正しく実装されている**

#### 2.1.2 キュー追加時のロジック（`overnight_queue_service.py`）

**ファイル**: `backend/app/services/overnight_queue_service.py`

**実装内容**:
```python
async def add_to_overnight_queue(
    self,
    facility_id: int,
    escalation_id: int,
    guest_message: str,
    db: AsyncSession
) -> OvernightQueue:
    # ...
    # 次の通知時刻を計算（スタッフ不在時間帯の終了時刻）
    scheduled_time_local = get_next_notification_time(
        current_time=local_now,
        current_weekday=current_weekday,
        staff_absence_periods=staff_absence_periods
    )
    # ...
    overnight_queue = OvernightQueue(
        # ...
        scheduled_notify_at=scheduled_time  # ← 計算された通知時刻を保存
    )
```

**動作**:
- `get_next_notification_time`を呼び出して、現在時刻が該当する時間帯の終了時刻を計算
- その時刻を`scheduled_notify_at`に保存
- **11:00-15:00の時間帯にエスカレーションが発生した場合、15:00に通知されるロジックは正しく実装されている**

### 2.2 フロントエンドの説明文生成ロジック

#### 2.2.1 説明文生成ロジック（`OvernightQueue.vue`）

**ファイル**: `frontend/src/views/admin/OvernightQueue.vue`

**実装内容**:
```javascript
const descriptionText = computed(() => {
  // ...
  // すべての時間帯を表示用の文字列に変換
  const periodStrings = periods.map((period, index) => {
    const startTime = period.start_time
    const endTime = period.end_time
    return `${startTime}-${endTime}`
  })
  
  // すべての時間帯を「、」で区切って表示
  const periodsDisplay = periodStrings.join('、')
  
  // 最初の時間帯の終了時刻を通知時刻として使用（複数時間帯がある場合は最初の時間帯の終了時刻）
  const firstPeriod = periods[0]  // ← 問題: 最初の時間帯のみを使用
  const notifyTime = firstPeriod.end_time
  
  return `スタッフ不在時間帯（${periodsDisplay}）にエスカレーションされた質問は、自動的に${notifyTime}にスタッフへ通知されます。...`
})
```

**問題点**:
- すべての時間帯を表示している（`periodsDisplay`）
- しかし、通知時刻は最初の時間帯（`periods[0]`）の終了時刻のみを使用している
- **これが表記の問題の原因**

---

## 3. 結論

### 3.1 ロジックの問題か？表記の問題か？

**結論**: **表記の問題**

**理由**:
1. **ロジックは正しく実装されている**
   - 11:00-15:00の時間帯にエスカレーションが発生した場合、15:00に通知されるロジックは正しく実装されている
   - `get_next_notification_time`関数が、現在時刻が該当する時間帯の終了時刻を正しく計算している

2. **表記が完成されていない**
   - フロントエンドの説明文が、最初の時間帯の終了時刻のみを表示している
   - 複数の時間帯がある場合、各時間帯ごとに異なる通知時刻があることを説明できていない

### 3.2 具体的な問題

**現在の実装**:
- 時間帯1（22:00-07:30）にエスカレーション → 07:30に通知 ✅
- 時間帯2（11:00-15:00）にエスカレーション → 15:00に通知 ✅（ロジックは正しい）
- 説明文: 「自動的に07:30にスタッフへ通知」 ❌（表記が不正確）

**問題の原因**:
- 説明文が「最初の時間帯の終了時刻」のみを表示している
- 複数の時間帯がある場合、各時間帯ごとに異なる通知時刻があることを説明できていない

---

## 4. 修正案

### 4.1 修正方針

**オプション1: 各時間帯ごとに通知時刻を表示**
```
スタッフ不在時間帯（22:00-07:30、11:00-15:00）にエスカレーションされた質問は、各時間帯の終了時刻（07:30、15:00）にスタッフへ通知されます。
```

**オプション2: 一般的な説明**
```
スタッフ不在時間帯にエスカレーションされた質問は、その時間帯の終了時刻にスタッフへ通知されます。
```

**オプション3: 時間帯ごとに詳細に表示**
```
スタッフ不在時間帯にエスカレーションされた質問は、各時間帯の終了時刻にスタッフへ通知されます。
- 22:00-07:30 → 07:30に通知
- 11:00-15:00 → 15:00に通知
```

### 4.2 推奨案

**オプション2を推奨**:
- シンプルで分かりやすい
- 複数の時間帯がある場合でも対応できる
- 具体的な時刻を列挙する必要がない

**修正後の説明文**:
```
スタッフ不在時間帯（22:00-07:30、11:00-15:00）にエスカレーションされた質問は、その時間帯の終了時刻にスタッフへ通知されます。「手動実行」ボタンをクリックすると、通知予定時刻が来ている質問をスタッフへ通知します。
```

---

## 5. まとめ

### 5.1 調査結果

- ✅ **ロジックは正しく実装されている**: 11:00-15:00の時間帯にエスカレーションが発生した場合、15:00に通知されるロジックは正しく実装されている
- ❌ **表記が完成されていない**: フロントエンドの説明文が、最初の時間帯の終了時刻のみを表示しているため、複数の時間帯がある場合に正確な説明になっていない

### 5.2 修正が必要な箇所

**ファイル**: `frontend/src/views/admin/OvernightQueue.vue`

**修正内容**:
- 説明文を「その時間帯の終了時刻に通知」という一般的な表現に変更
- 最初の時間帯の終了時刻のみを表示するのではなく、すべての時間帯に対応できる説明文に変更

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-05  
**Status**: ✅ **調査分析完了**


