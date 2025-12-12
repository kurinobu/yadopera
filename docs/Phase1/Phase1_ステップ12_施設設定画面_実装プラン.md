# Phase 1: ステップ12 施設設定画面 実装プラン

**作成日**: 2025年12月5日  
**実施者**: Auto (AI Assistant)  
**対象**: 施設設定画面の作成に関する実装プラン  
**状態**: ✅ **実装プラン立案完了**

---

## 1. 実装プランの概要

### 1.1 目的

施設管理者が施設情報を編集できる画面を作成し、以下の問題を根本的に解決する：
- 施設管理者が施設情報を編集できない問題
- 夜間時間帯（22:00-8:00）がハードコードされている問題
- パスワード変更機能がない問題

### 1.2 大原則への準拠

1. **根本解決 > 暫定解決**: 施設設定画面を作成することで、施設管理者が設定を変更できるようにする根本的な解決を実現
2. **シンプル構造 > 複雑構造**: JSONフィールドを使用してシンプルな実装を採用、既存のパターンに従う
3. **統一・同一化 > 特殊独自**: 既存の管理画面のパターンに従い、統一された実装を維持
4. **具体的 > 一般**: 具体的な実装内容を明確にする
5. **拙速 < 安全確実**: 十分な検証を行い、安全に実装する

---

## 2. 実装内容の詳細

### 2.1 データベース設計

#### 2.1.1 施設モデルの拡張

**追加フィールド**:
```python
# backend/app/models/facility.py
staff_absence_periods = Column(JSON, default=[])  # スタッフ不在時間帯（JSON配列）
icon_url = Column(String(255), nullable=True)  # アイコンURL（Phase 1では任意）
```

**データ構造**:
```json
{
  "staff_absence_periods": [
    {
      "start_time": "22:00",
      "end_time": "08:00",
      "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    },
    {
      "start_time": "12:00",
      "end_time": "14:00",
      "days_of_week": ["mon", "tue", "wed", "thu", "fri"]
    }
  ]
}
```

**理由**: 
- シンプル構造 > 複雑構造の大原則に従う
- Phase 1では十分な機能を提供できる
- Phase 2以降で必要に応じて別テーブルに移行可能

#### 2.1.2 マイグレーション

**Alembicマイグレーション**:
- `backend/alembic/versions/XXX_add_facility_settings.py`を作成
- `staff_absence_periods`フィールドを追加（デフォルト: `[]`）
- `icon_url`フィールドを追加（nullable=True）

---

### 2.2 バックエンドAPI実装

#### 2.2.1 施設設定取得API

**エンドポイント**: `GET /api/v1/admin/facility/settings`

**実装ファイル**: `backend/app/api/v1/admin/facility.py`（新規作成）

**レスポンススキーマ**: `FacilitySettingsResponse`

**実装内容**:
```python
@router.get("/settings", response_model=FacilitySettingsResponse)
async def get_facility_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    施設設定取得
    
    JWT認証必須。現在のユーザーが所属する施設の設定を返却します。
    """
    # ユーザーが所属する施設IDを取得
    facility_id = current_user.facility_id
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any facility"
        )
    
    # 施設情報を取得
    facility = await db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    
    # レスポンスを構築
    return FacilitySettingsResponse.from_orm(facility)
```

**レスポンス例**:
```json
{
  "facility": {
    "id": 1,
    "name": "やどぺらゲストハウス",
    "email": "info@example.com",
    "phone": "090-1234-5678",
    "address": "京都府京都市...",
    "wifi_ssid": "Yadopera-Guest",
    "wifi_password": "********",
    "check_in_time": "15:00",
    "check_out_time": "11:00",
    "house_rules": "禁煙、門限23:00、静粛時間22:00-8:00",
    "local_info": "最寄り駅: 京都駅（徒歩10分）、コンビニ: セブンイレブン（徒歩3分）",
    "languages": ["en"],
    "timezone": "Asia/Tokyo",
    "staff_absence_periods": [
      {
        "start_time": "22:00",
        "end_time": "08:00",
        "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
      }
    ],
    "icon_url": null
  }
}
```

#### 2.2.2 施設設定更新API

**エンドポイント**: `PUT /api/v1/admin/facility/settings`

**実装ファイル**: `backend/app/api/v1/admin/facility.py`

**リクエストスキーマ**: `FacilitySettingsUpdateRequest`

**実装内容**:
```python
@router.put("/settings", response_model=FacilitySettingsResponse)
async def update_facility_settings(
    request: FacilitySettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    施設設定更新
    
    JWT認証必須。現在のユーザーが所属する施設の設定を更新します。
    """
    # ユーザーが所属する施設IDを取得
    facility_id = current_user.facility_id
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any facility"
        )
    
    # 施設情報を取得
    facility = await db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    
    # 施設情報を更新
    # ... 更新処理
    
    await db.commit()
    await db.refresh(facility)
    
    return FacilitySettingsResponse.from_orm(facility)
```

#### 2.2.3 パスワード変更API

**エンドポイント**: `PUT /api/v1/admin/auth/password`

**実装ファイル**: `backend/app/api/v1/admin/auth.py`（既存ファイルに追加）

**リクエストスキーマ**: `PasswordChangeRequest`

**実装内容**:
```python
@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    パスワード変更
    
    JWT認証必須。現在のユーザーのパスワードを変更します。
    """
    # 現在のパスワードを検証
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # 新しいパスワードを検証
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match"
        )
    
    # パスワード強度チェック（最小8文字）
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # パスワードをハッシュ化して更新
    current_user.password_hash = hash_password(request.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}
```

#### 2.2.4 スキーマ定義

**実装ファイル**: `backend/app/schemas/facility.py`（拡張）

**追加スキーマ**:
```python
class StaffAbsencePeriod(BaseModel):
    """スタッフ不在時間帯"""
    start_time: str = Field(..., description="開始時刻（HH:MM形式）")
    end_time: str = Field(..., description="終了時刻（HH:MM形式）")
    days_of_week: List[str] = Field(..., description="曜日（['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']）")

class FacilitySettingsResponse(BaseModel):
    """施設設定レスポンス"""
    facility: FacilityResponse
    staff_absence_periods: List[StaffAbsencePeriod] = Field(default_factory=list)

class FacilitySettingsUpdateRequest(BaseModel):
    """施設設定更新リクエスト"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    wifi_ssid: Optional[str] = None
    wifi_password: Optional[str] = None  # 変更時のみ
    check_in_time: Optional[str] = None  # "15:00"形式
    check_out_time: Optional[str] = None  # "11:00"形式
    house_rules: Optional[str] = None
    local_info: Optional[str] = None
    staff_absence_periods: Optional[List[StaffAbsencePeriod]] = None

class PasswordChangeRequest(BaseModel):
    """パスワード変更リクエスト"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
```

---

### 2.3 フロントエンド実装

#### 2.3.1 画面構成

**実装ファイル**: `frontend/src/views/admin/FacilitySettings.vue`

**セクション構成**:

1. **基本情報セクション**
   - 施設名（`name`）
   - メールアドレス（`email`）
   - 電話番号（`phone`）
   - 住所（`address`）

2. **WiFi設定セクション**
   - WiFi SSID（`wifi_ssid`）
   - WiFiパスワード（`wifi_password`、表示/非表示切り替え）

3. **チェックイン/アウト時間セクション**
   - チェックイン時間（`check_in_time`、時刻入力）
   - チェックアウト時間（`check_out_time`、時刻入力）

4. **館内ルール・周辺情報セクション**
   - 館内ルール（`house_rules`、テキストエリア、デフォルト例文あり）
   - 周辺情報（`local_info`、テキストエリア、デフォルト例文あり）
   - **注意**: 200文字制限を緩和（1000文字程度に拡張）

5. **対応言語セクション（表示のみ）**
   - 対応言語（`languages`、表示のみ、設定不可）
   - 説明文: 「現在は英語のみ対応。多言語対応はPhase 2以降で実装予定です。」

6. **タイムゾーンセクション（表示のみ）**
   - タイムゾーン（`timezone`、表示のみ、設定不可）
   - 説明文: 「現在は日本国内のみ対応のため、タイムゾーンは固定です。」

7. **スタッフ不在時間帯セクション**
   - 時間帯一覧（追加・削除機能）
   - 各時間帯: 開始時刻、終了時刻、曜日選択（複数選択可能）
   - デフォルト: 22:00-8:00（全曜日）

8. **パスワード変更セクション**
   - 現在のパスワード（`current_password`）
   - 新しいパスワード（`new_password`）
   - 新しいパスワード（確認）（`confirm_password`）
   - パスワード強度チェック（最小8文字）

9. **アイコン設定セクション（任意、Phase 1では簡略化）**
   - 画像アップロード機能（Phase 2以降で実装）
   - 現状はプレースホルダーのみ

#### 2.3.2 UIコンポーネント

**既存コンポーネントの再利用**:
- `Loading`: ローディング表示
- `Modal`: モーダル表示（必要に応じて）
- 既存のフォームコンポーネントのパターンを参考

**新規コンポーネント**:
- `StaffAbsencePeriodForm`: スタッフ不在時間帯の入力フォーム
- `PasswordChangeForm`: パスワード変更フォーム

#### 2.3.3 APIクライアント

**実装ファイル**: `frontend/src/api/facility.ts`（拡張）

**追加メソッド**:
```typescript
// 施設設定取得
export const getFacilitySettings = async (): Promise<FacilitySettingsResponse> => {
  const response = await api.get<FacilitySettingsResponse>('/admin/facility/settings')
  return response.data
}

// 施設設定更新
export const updateFacilitySettings = async (
  data: FacilitySettingsUpdateRequest
): Promise<FacilitySettingsResponse> => {
  const response = await api.put<FacilitySettingsResponse>('/admin/facility/settings', data)
  return response.data
}

// パスワード変更
export const changePassword = async (
  data: PasswordChangeRequest
): Promise<void> => {
  await api.put('/admin/auth/password', data)
}
```

#### 2.3.4 ルーティング

**実装ファイル**: `frontend/src/router/admin.ts`（拡張）

**追加ルート**:
```typescript
{
  path: '/admin/facility/settings',
  name: 'FacilitySettings',
  component: () => import('@/views/admin/FacilitySettings.vue'),
  meta: {
    layout: 'admin',
    requiresAuth: true
  }
}
```

#### 2.3.5 サイドバーメニューへの追加

**実装ファイル**: `frontend/src/components/admin/Sidebar.vue`（拡張）

**追加メニュー項目**:
```typescript
{
  to: '/admin/facility/settings',
  label: '施設設定',
  icon: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })
  ])
}
```

**メニュー順序**: FAQ管理の後、夜間対応キューの前

---

## 3. デフォルト値と例文

### 3.1 館内ルールのデフォルト例文

```
禁煙、門限23:00、静粛時間22:00-8:00、ゴミ出しは毎週火曜日・金曜日
```

### 3.2 周辺情報のデフォルト例文

```
最寄り駅: 京都駅（徒歩10分）、コンビニ: セブンイレブン（徒歩3分）、レストラン: 多数あり
```

### 3.3 スタッフ不在時間帯のデフォルト値

```json
[
  {
    "start_time": "22:00",
    "end_time": "08:00",
    "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
  }
]
```

---

## 4. バリデーション

### 4.1 施設設定のバリデーション

- **施設名**: 必須、1-255文字
- **メールアドレス**: 必須、メール形式
- **電話番号**: 任意、50文字以内
- **住所**: 任意、テキスト
- **WiFi SSID**: 任意、100文字以内
- **WiFiパスワード**: 変更時のみ、100文字以内
- **チェックイン時間**: 任意、時刻形式（HH:MM）
- **チェックアウト時間**: 任意、時刻形式（HH:MM）
- **館内ルール**: 任意、1000文字以内（200文字制限を緩和）
- **周辺情報**: 任意、1000文字以内（200文字制限を緩和）
- **スタッフ不在時間帯**: 任意、配列形式、各時間帯のバリデーション
  - `start_time`: 必須、時刻形式（HH:MM）
  - `end_time`: 必須、時刻形式（HH:MM）
  - `days_of_week`: 必須、配列、有効な曜日（['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']）

### 4.2 パスワード変更のバリデーション

- **現在のパスワード**: 必須、1文字以上
- **新しいパスワード**: 必須、最小8文字
- **確認パスワード**: 必須、新しいパスワードと一致

---

## 5. エラーハンドリング

### 5.1 バックエンドエラーハンドリング

- **400 Bad Request**: バリデーションエラー
- **403 Forbidden**: ユーザーが施設に所属していない
- **404 Not Found**: 施設が見つからない
- **500 Internal Server Error**: サーバーエラー

### 5.2 フロントエンドエラーハンドリング

- 既存のパターンに従う（`FaqManagement.vue`を参考）
- エラーメッセージをユーザーフレンドリーに表示
- ネットワークエラーの場合は再試行ボタンを表示

---

## 6. 実装順序

### 6.1 ステップ1: データベースマイグレーション

1. `Facility`モデルに`staff_absence_periods`フィールドを追加
2. `Facility`モデルに`icon_url`フィールドを追加
3. Alembicマイグレーションを作成・実行

### 6.2 ステップ2: バックエンドAPI実装

1. `backend/app/schemas/facility.py`を拡張
2. `backend/app/api/v1/admin/facility.py`を作成
3. `backend/app/api/v1/admin/auth.py`にパスワード変更APIを追加
4. `backend/app/api/v1/router.py`にルーターを追加

### 6.3 ステップ3: フロントエンド実装

1. `frontend/src/api/facility.ts`を拡張
2. `frontend/src/types/facility.ts`を拡張
3. `frontend/src/views/admin/FacilitySettings.vue`を作成
4. `frontend/src/router/admin.ts`にルーティングを追加
5. `frontend/src/components/admin/Sidebar.vue`にメニュー項目を追加

### 6.4 ステップ4: 動作確認

1. ローカル環境での動作確認
2. ブラウザの開発者ツールでエラーの確認
3. ネットワークリクエストの確認
4. バリデーションの確認

---

## 7. 注意事項

### 7.1 館内ルール・周辺情報の文字数制限

- **AIエンジンでの制限**: `backend/app/ai/engine.py`の200文字制限を緩和（500文字程度に拡張）
- **データベース**: `Text`型のため制限なし
- **フロントエンド**: 1000文字程度の制限を設定（UIの制限）

### 7.2 対応言語とタイムゾーン

- **対応言語**: 表示のみ（設定不可）、説明文を追加
- **タイムゾーン**: 表示のみ（設定不可）、説明文を追加

### 7.3 アイコン設定

- Phase 1では簡略化（プレースホルダーのみ）
- Phase 2以降で本格的に実装

### 7.4 スタッフ不在時間帯の実装

- JSONフィールドを使用（シンプル構造）
- Phase 2以降で必要に応じて別テーブルに移行可能

---

## 8. テスト項目

### 8.1 バックエンドテスト

- [ ] 施設設定取得APIのテスト
- [ ] 施設設定更新APIのテスト
- [ ] パスワード変更APIのテスト
- [ ] バリデーションテスト
- [ ] エラーハンドリングテスト

### 8.2 フロントエンドテスト

- [ ] 施設設定画面の表示テスト
- [ ] フォーム入力のテスト
- [ ] バリデーションのテスト
- [ ] API連携のテスト
- [ ] エラーハンドリングのテスト

### 8.3 統合テスト

- [ ] 施設設定の更新フローのテスト
- [ ] パスワード変更フローのテスト
- [ ] スタッフ不在時間帯の設定フローのテスト

---

## 9. 完了条件

### 9.1 必須条件

- [ ] データベースマイグレーションが完了
- [ ] バックエンドAPIが実装完了
- [ ] フロントエンド画面が実装完了
- [ ] ルーティングが追加完了
- [ ] サイドバーメニューに追加完了
- [ ] ローカル環境での動作確認完了
- [ ] ブラウザの開発者ツールでエラーがない
- [ ] ネットワークリクエストが正常に送信されている

### 9.2 任意条件（Phase 1では簡略化）

- [ ] アイコン設定機能（Phase 2以降で実装）

---

## 10. 成果物

### 10.1 バックエンド

- `backend/app/models/facility.py`（拡張）
- `backend/app/schemas/facility.py`（拡張）
- `backend/app/api/v1/admin/facility.py`（新規作成）
- `backend/app/api/v1/admin/auth.py`（拡張）
- `backend/alembic/versions/XXX_add_facility_settings.py`（新規作成）

### 10.2 フロントエンド

- `frontend/src/views/admin/FacilitySettings.vue`（新規作成）
- `frontend/src/api/facility.ts`（拡張）
- `frontend/src/types/facility.ts`（拡張）
- `frontend/src/router/admin.ts`（拡張）
- `frontend/src/components/admin/Sidebar.vue`（拡張）

### 10.3 ドキュメント

- `docs/Phase1/Phase1_ステップ12_施設設定画面_実装完了レポート.md`（実装完了後に作成）

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-05  
**Status**: ✅ **実装プラン立案完了**


