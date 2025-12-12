# Phase 1: ステップ12 施設設定画面 調査分析レポート

**作成日**: 2025年12月5日  
**実施者**: Auto (AI Assistant)  
**対象**: 施設設定画面の作成に関する調査分析  
**状態**: ✅ **調査分析完了**

---

## 1. 精読した関連書類

### 1.1 主要ドキュメント

1. **要約定義書** (`docs/Summary/yadopera-v03-summary.md`)
   - バージョン: v0.3.2
   - 最終更新日: 2025年12月1日
   - **大原則**: 根本解決 > 暫定解決、シンプル構造 > 複雑構造、統一・同一化 > 特殊独自、具体的 > 一般、拙速 < 安全確実

2. **アーキテクチャ設計書** (`docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`)
   - バージョン: v0.3
   - 最終更新日: 2025年11月21日
   - 管理画面のページ遷移図に「🏠 施設設定」が記載されている（サイドバーメニュー内）
   - `/admin/facility`のルーティングが記載されている
   - `FacilitySettings.vue`コンポーネントが記載されている

3. **Phase 1引き継ぎ書** (`docs/Phase1/Phase1_引き継ぎ書_20251204_153010.md`)
   - バージョン: v1.6
   - 最終更新日: 2025年12月4日
   - ステップ12（施設設定画面の作成）がクリティカルな問題として追加されている

4. **Phase 1完了条件・進捗状況・残存課題・ステップ計画** (`docs/Phase1/Phase1_完了条件_進捗状況_残存課題_ステップ計画_20251204_完全版.md`)
   - ステップ12の詳細な実施内容が記載されている

5. **Phase 1重要事項 施設設定画面 ステップ計画追加** (`docs/Phase1/Phase1_重要事項_施設設定画面_ステップ計画追加_20251205.md`)
   - 「スタッフ不在時間帯」の検討が記載されている

---

## 2. 大原則の確認

### 2.1 開発・実装の大原則（要約定義書より）

**実装や修正の基本は要約定義書やアーキテクチャ設計書などを準拠し、方向性は以下の優先順位を遵守する：**

1. **根本解決 > 暫定解決**
   - 一時的な回避策ではなく、根本原因を解決する
   - パッチワーク的な修正を避け、設計レベルでの解決を優先

2. **シンプル構造 > 複雑構造**
   - 過度に複雑な実装を避け、理解しやすく保守しやすい構造を選択
   - 不要な抽象化や過剰な設計を避ける

3. **統一・同一化 > 特殊独自**
   - 既存のパターンや規約に従い、統一された実装を優先
   - 特殊な実装や独自の方法を避け、標準的なアプローチを採用

4. **具体的 > 一般**
   - 抽象的な説明ではなく、具体的な実装方法や手順を明確にする
   - 曖昧な表現を避け、実行可能な具体的な内容を記載

5. **拙速 < 安全確実**
   - 速度よりも安全性と確実性を優先
   - テストを省略せず、十分な検証を行ってから本番環境に反映

**この大原則は、すべての開発・実装・修正作業において最優先で遵守する。**

---

## 3. 現状の調査結果

### 3.1 施設設定画面の存在確認

**調査結果**:
- ❌ 施設設定画面（`FacilitySettings.vue`）が存在しない
- ❌ `/admin/facility/settings`のルーティングが存在しない
- ❌ サイドバーメニューに「施設設定」のメニュー項目が存在しない

**確認したファイル**:
- `frontend/src/views/admin/`: `FacilitySettings.vue`が存在しない
- `frontend/src/router/admin.ts`: `/admin/facility/settings`のルーティングが存在しない
- `frontend/src/components/admin/Sidebar.vue`: 「施設設定」のメニュー項目が存在しない

### 3.2 バックエンドAPIの存在確認

**調査結果**:
- ❌ `GET /api/v1/admin/facility/settings`: 存在しない
- ❌ `PUT /api/v1/admin/facility/settings`: 存在しない
- ✅ `GET /api/v1/facility/{slug}`: 存在する（公開API、ゲスト側用）

**確認したファイル**:
- `backend/app/api/v1/admin/`: `facility.py`が存在しない
- `backend/app/api/v1/facility.py`: 存在するが、公開APIのみ

### 3.3 施設モデルの確認

**調査結果**:
- ✅ `Facility`モデルが存在する（`backend/app/models/facility.py`）
- ❌ 「スタッフ不在時間帯」の設定フィールドが存在しない
- ✅ 既存のフィールド:
  - `name`: 施設名
  - `slug`: URL用識別子
  - `email`: メールアドレス
  - `phone`: 電話番号
  - `address`: 住所
  - `wifi_ssid`: WiFi SSID
  - `wifi_password`: WiFiパスワード（暗号化保存）
  - `check_in_time`: チェックイン時間
  - `check_out_time`: チェックアウト時間
  - `house_rules`: 館内ルール
  - `local_info`: 周辺情報
  - `languages`: 対応言語（配列）
  - `timezone`: タイムゾーン
  - `subscription_plan`: サブスクリプションプラン
  - `monthly_question_limit`: 月間質問数上限
  - `is_active`: アクティブフラグ

### 3.4 パスワード変更機能の確認

**調査結果**:
- ✅ パスワードリセット機能が存在する（`/admin/password-reset`）
- ❌ パスワード変更機能（ログイン中にパスワードを変更する機能）が存在しない

**確認したファイル**:
- `frontend/src/views/admin/Login.vue`: パスワードリセットリンクが存在する
- `backend/app/api/v1/auth.py`: パスワードリセットAPIが存在する
- `backend/app/core/security.py`: `hash_password`、`verify_password`関数が存在する

### 3.5 ハンバーガーメニューの確認

**調査結果**:
- ✅ ハンバーガーメニューが存在する（`Sidebar.vue`）
- ✅ モバイル対応が実装されている（`isMobileMenuOpen`プロパティ）
- ❌ 「施設設定」のメニュー項目が存在しない

**確認したファイル**:
- `frontend/src/components/admin/Sidebar.vue`: ハンバーガーメニューが実装されている
- `frontend/src/components/admin/Header.vue`: ハンバーガーメニューボタンが存在する

---

## 4. 問題の詳細分析

### 4.1 クリティカルな問題

**問題**: 施設設定画面が存在しない

**影響**:
1. **施設管理者が施設情報を編集できない**
   - 施設名、住所、電話番号などの基本情報を変更できない
   - WiFi設定を変更できない
   - チェックイン/アウト時間を変更できない

2. **夜間時間帯（22:00-8:00）などの設定を変更できない**
   - 現在、夜間時間帯がハードコードされている（`backend/app/services/overnight_queue_service.py`）
   - 施設ごとに異なる時間帯を設定できない
   - 「スタッフ不在時間帯」という柔軟な設定ができない

3. **パスワード変更機能がない**
   - ログイン中にパスワードを変更できない
   - パスワードリセット機能のみが存在する

4. **アイコン設定機能がない**
   - 施設のアイコンを設定できない

### 4.2 アーキテクチャ設計書との整合性

**アーキテクチャ設計書の記載**:
- `/admin/facility`のルーティングが記載されている
- `FacilitySettings.vue`コンポーネントが記載されている
- サイドバーメニューに「🏠 施設設定」が記載されている

**実際の実装**:
- ❌ ルーティングが存在しない
- ❌ コンポーネントが存在しない
- ❌ メニュー項目が存在しない

**結論**: アーキテクチャ設計書には記載されているが、実際の実装が存在しない。これは設計と実装の不整合である。

---

## 5. 施設設定画面のプラン

### 5.1 設置場所

**決定事項**: ハンバーガーメニュー内（サイドバーメニュー）

**理由**:
- アーキテクチャ設計書に「🏠 施設設定」がサイドバーメニューに記載されている
- 既存の管理画面のパターンに従う（ダッシュボード、FAQ管理、夜間対応キュー、QRコード発行など）
- モバイル対応も既に実装されている

### 5.2 必須項目

#### 5.2.1 パスワード変更

**理由**:
- セキュリティ上、ログイン中にパスワードを変更できる機能が必要
- パスワードリセット機能のみでは不十分

**実装内容**:
- 現在のパスワード入力
- 新しいパスワード入力（確認用も含む）
- パスワード強度チェック（最小8文字、複雑度）
- バックエンドAPI: `PUT /api/v1/admin/auth/password`

#### 5.2.2 スタッフ不在時間帯（夜間対応時間帯）設定

**理由**:
- 現在、夜間時間帯（22:00-8:00）がハードコードされている
- 施設ごとに異なる時間帯を設定できるようにする必要がある
- 「スタッフ不在時間帯」という括りで柔軟な設定を可能にする

**実装内容**:
- 複数の時間帯を設定できるUI
- 時間帯の追加・削除機能
- 例: 22:00-8:00、12:00-14:00など
- データベース: `staff_absence_periods`テーブル（新規作成）または`Facility`モデルにJSONフィールドを追加

**データ構造案**:
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

#### 5.2.3 アイコン設定（任意）

**理由**:
- 施設のアイコンを設定することで、視覚的な識別が容易になる
- ゲスト画面での表示に使用できる可能性がある

**実装内容**:
- 画像アップロード機能
- 画像プレビュー機能
- 画像のリサイズ・最適化
- バックエンドAPI: `POST /api/v1/admin/facility/icon`（S3またはローカルストレージに保存）

**注意**: Phase 1では任意項目として実装し、Phase 2以降で本格的に使用する

### 5.3 その他の設定項目（提案）

#### 5.3.1 基本情報

- 施設名（`name`）
- メールアドレス（`email`）
- 電話番号（`phone`）
- 住所（`address`）

#### 5.3.2 WiFi設定

- WiFi SSID（`wifi_ssid`）
- WiFiパスワード（`wifi_password`、暗号化保存）

#### 5.3.3 チェックイン/アウト時間

- チェックイン時間（`check_in_time`）
- チェックアウト時間（`check_out_time`）

#### 5.3.4 館内ルール・周辺情報

- 館内ルール（`house_rules`）
- 周辺情報（`local_info`）

#### 5.3.5 対応言語

- 対応言語（`languages`、配列）

#### 5.3.6 タイムゾーン

- タイムゾーン（`timezone`）

---

## 6. 実装計画

### 6.1 データベース設計

#### 6.1.1 施設モデルの拡張

**オプション1: JSONフィールドを追加**
```python
staff_absence_periods = Column(JSON, default=[])
```

**オプション2: 別テーブルを作成**
```python
class StaffAbsencePeriod(Base):
    __tablename__ = "staff_absence_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    days_of_week = Column(ARRAY(String), nullable=False)  # ["mon", "tue", ...]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**推奨**: オプション1（JSONフィールド）を採用
- シンプル構造 > 複雑構造の大原則に従う
- Phase 1では十分な機能を提供できる
- Phase 2以降で必要に応じて別テーブルに移行可能

#### 6.1.2 アイコン設定

**オプション1: S3に保存**
- ファイルパスを`Facility`モデルに保存
- `icon_url = Column(String(255))`

**オプション2: ローカルストレージに保存**
- ファイルパスを`Facility`モデルに保存
- `icon_url = Column(String(255))`

**推奨**: オプション1（S3）を採用（Phase 2以降で実装）
- Phase 1では任意項目として、実装を簡略化

### 6.2 バックエンドAPI設計

#### 6.2.1 施設設定取得API

```
GET /api/v1/admin/facility/settings
```

**レスポンス**:
```json
{
  "facility": {
    "id": 1,
    "name": "やどぺらゲストハウス",
    "email": "info@example.com",
    "phone": "090-1234-5678",
    "address": "京都府京都市...",
    "wifi_ssid": "Yadopera-Guest",
    "wifi_password": "********",  // マスク表示
    "check_in_time": "15:00",
    "check_out_time": "11:00",
    "house_rules": "...",
    "local_info": "...",
    "languages": ["en", "ja"],
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

#### 6.2.2 施設設定更新API

```
PUT /api/v1/admin/facility/settings
```

**リクエストボディ**:
```json
{
  "name": "やどぺらゲストハウス",
  "email": "info@example.com",
  "phone": "090-1234-5678",
  "address": "京都府京都市...",
  "wifi_ssid": "Yadopera-Guest",
  "wifi_password": "new_password",  // 変更時のみ
  "check_in_time": "15:00",
  "check_out_time": "11:00",
  "house_rules": "...",
  "local_info": "...",
  "languages": ["en", "ja"],
  "timezone": "Asia/Tokyo",
  "staff_absence_periods": [
    {
      "start_time": "22:00",
      "end_time": "08:00",
      "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    }
  ]
}
```

#### 6.2.3 パスワード変更API

```
PUT /api/v1/admin/auth/password
```

**リクエストボディ**:
```json
{
  "current_password": "current_password",
  "new_password": "new_password",
  "confirm_password": "new_password"
}
```

### 6.3 フロントエンド設計

#### 6.3.1 画面構成

**セクション1: 基本情報**
- 施設名
- メールアドレス
- 電話番号
- 住所

**セクション2: WiFi設定**
- WiFi SSID
- WiFiパスワード（表示/非表示切り替え）

**セクション3: チェックイン/アウト時間**
- チェックイン時間
- チェックアウト時間

**セクション4: 館内ルール・周辺情報**
- 館内ルール（テキストエリア）
- 周辺情報（テキストエリア）

**セクション5: 対応言語**
- 対応言語（複数選択）

**セクション6: タイムゾーン**
- タイムゾーン（ドロップダウン）

**セクション7: スタッフ不在時間帯**
- 時間帯一覧（追加・削除機能）
- 各時間帯: 開始時刻、終了時刻、曜日選択

**セクション8: パスワード変更**
- 現在のパスワード
- 新しいパスワード
- 新しいパスワード（確認）

**セクション9: アイコン設定（任意）**
- 画像アップロード
- 画像プレビュー

#### 6.3.2 ルーティング

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

#### 6.3.3 サイドバーメニューへの追加

```typescript
{
  to: '/admin/facility/settings',
  label: '施設設定',
  icon: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })
  ])
}
```

---

## 7. 設定項目の提案（まとめ）

### 7.1 必須項目

1. **パスワード変更**
   - 現在のパスワード入力
   - 新しいパスワード入力（確認用も含む）
   - パスワード強度チェック

2. **スタッフ不在時間帯（夜間対応時間帯）設定**
   - 複数の時間帯を設定できるUI
   - 時間帯の追加・削除機能
   - 各時間帯: 開始時刻、終了時刻、曜日選択

3. **アイコン設定（任意）**
   - 画像アップロード機能
   - 画像プレビュー機能
   - Phase 1では任意項目として実装

### 7.2 その他の設定項目

1. **基本情報**
   - 施設名、メールアドレス、電話番号、住所

2. **WiFi設定**
   - WiFi SSID、WiFiパスワード（暗号化保存）

3. **チェックイン/アウト時間**
   - チェックイン時間、チェックアウト時間

4. **館内ルール・周辺情報**
   - 館内ルール、周辺情報

5. **対応言語**
   - 対応言語（複数選択）

6. **タイムゾーン**
   - タイムゾーン（ドロップダウン）

---

## 8. 大原則への準拠確認

### 8.1 根本解決 > 暫定解決

✅ **準拠**: 施設設定画面を作成することで、施設管理者が設定を変更できるようにする根本的な解決を実現

### 8.2 シンプル構造 > 複雑構造

✅ **準拠**: 
- JSONフィールドを使用してシンプルな実装を採用
- 既存のパターンに従い、統一された実装を維持

### 8.3 統一・同一化 > 特殊独自

✅ **準拠**: 
- 既存の管理画面のパターンに従う
- 既存のAPIパターンに従う
- 既存のUIコンポーネントを再利用

### 8.4 具体的 > 一般

✅ **準拠**: 
- 具体的な実装内容を明確にする
- 具体的なAPI設計を明確にする
- 具体的なUI設計を明確にする

### 8.5 拙速 < 安全確実

✅ **準拠**: 
- 十分な検証を行い、安全に実装する
- テストを省略せず、十分な検証を行う

---

## 9. 次のステップ

### 9.1 実装前の確認事項

1. ✅ 調査分析完了
2. ⏳ ユーザーからの指示待ち（修正しないでください）

### 9.2 実装時の注意事項

1. **データベースマイグレーション**
   - `Facility`モデルに`staff_absence_periods`フィールドを追加
   - Alembicマイグレーションを作成

2. **バックエンドAPI実装**
   - `backend/app/api/v1/admin/facility.py`を作成
   - `backend/app/schemas/facility.py`を拡張

3. **フロントエンド実装**
   - `frontend/src/views/admin/FacilitySettings.vue`を作成
   - `frontend/src/router/admin.ts`にルーティングを追加
   - `frontend/src/components/admin/Sidebar.vue`にメニュー項目を追加

4. **動作確認**
   - ローカル環境での動作確認
   - ブラウザの開発者ツールでエラーの確認
   - ネットワークリクエストの確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-05  
**Status**: ✅ **調査分析完了**


