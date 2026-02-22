# クーポン機能「公式サイトURL」追加 — 調査分析と実装提案

**作成日**: 2026年2月21日  
**準拠**: リードゲットオプション実装計画書・大原則（要約定義書 v0.3.18）  
**指示があるまで修正（実装）しない。**

---

## 1. 確認：固定フッターまわりの表示言語

### 結論

**現状は日本語のみです。ゲストの端末設定やURLの `?lang=` には依存していません。**

### 根拠

| 対象 | 内容 |
|------|------|
| **ゲスト画面の言語** | Welcome / Chat / LanguageSelect では `route.query.lang`（例: `?lang=ja`, `?lang=en`）で言語を切り替え、API にも `language` を渡している。 |
| **固定フッター** | `GuestOptionFooter.vue` のボタン文言「オトクなクーポン」は**ハードコードされた日本語**。`lang` や i18n を参照していない。 |
| **クーポンエントリーモーダル** | `CouponEntryModal.vue` のタイトル・説明・ラベル・ボタン（「オトクなクーポンを受け取る」「お名前（任意）」「メールアドレス」「閉じる」「キャンセル」「クーポンを受け取る」等）も**すべて日本語でハードコード**。 |

したがって、**固定フッターからモーダル・送信完了までの一連の表示は、現仕様では日本語のみ**です。多言語対応する場合は、既存のゲスト画面と同様に `route.query.lang` を参照し、文言を言語別に切り替える改修が必要になります。

---

## 2. 追加要件の整理

- **管理画面**: 宿泊施設管理者ページの「クーポン設定」に**「公式サイトURL」**を設定する項目を追加する。
- **メール**: ゲストが登録したメールアドレスに送るクーポン送付メールに、**その公式サイトのURLを記載**する。

---

## 3. 調査結果

### 3.1 計画書の大原則との対応

| 原則 | 本追加での適用 |
|------|----------------|
| 根本解決 > 暫定解決 | 公式サイトURLは施設マスタ（DB）に保持し、管理API・メール送信で参照する。一時的な入力や手動運用にしない。 |
| シンプル構造 > 複雑構造 | 1カラム追加（`official_website_url`）に留め、既存の施設設定・クーポン設定の流れに載せる。 |
| 统一・同一化 > 特殊独自 | 既存の施設設定（GET/PUT `/admin/facility/settings`）、Alembic マイグレーション、Brevo メール送信のパターンに合わせる。 |
| 具体的 > 一般 | カラム名・スキーマ名・画面ラベル・メール文言を本提案で明示する。 |
| 拙速 < 安全確実 | 実装後は Docker 環境でテストし、ステージングで確認してから本番を検討する。 |

### 3.2 現状の関連実装

| 対象 | 現状 |
|------|------|
| **施設モデル** | `backend/app/models/facility.py` にクーポン用に `coupon_enabled`, `coupon_discount_percent`, `coupon_description`, `coupon_validity_months` あり。URL 用カラムはなし（`icon_url` のみ）。 |
| **施設設定API** | `GET/PUT /admin/facility/settings` で上記4項目を取得・更新。レスポンスは `FacilityResponse`、更新は `FacilitySettingsUpdateRequest`。 |
| **管理画面** | `FacilitySettings.vue` の「クーポン設定（リード獲得）」で ON/OFF・割引率・クーポン文言・有効期限を編集。公式サイトURLの入力欄はなし。 |
| **クーポン送付メール** | `EmailService.send_coupon_email()` が `to_email`, `to_name`, `facility_name`, `discount_percent`, `description`, `valid_until` を受け、HTML/テキストで「公式サイトからご予約」と記載。**URL の引数・表示はなし。** |
| **リード登録・送信** | `LeadService.create_lead_and_send_coupon()` が施設オブジェクトから `coupon_*` を渡し、`send_coupon_email()` を呼び出し。 |

### 3.3 公開API・ゲスト画面について

- ゲスト向け施設公開API（`GET /api/v1/facility/{slug}`）では、クーポン有効時のみ `CouponPublic`（割引率・文言・有効期限）を返している。
- **公式サイトURLはゲスト画面の表示用には不要**（「オトクなクーポン」ボタンやモーダルにURLを出さず、メールで案内する想定）。そのため、公開APIや `CouponPublic` に公式サイトURLを追加する必要はない。

---

## 4. 実装提案（大原則に準拠）

### 4.1 データベース

- **テーブル**: `facilities`（既存）
- **追加カラム**:  
  - `official_website_url` — `VARCHAR(500)` 相当、NULL 可。  
  - 意味: 宿泊施設の公式予約サイト等のURL。クーポン送付メールで「こちらからご予約」として表示する。

**理由**: 施設ごとに1つ持てば足りるため、既存の施設マスタに1カラム追加する形とする。クーポン設定セクションでだけ編集するが、将来的に他用途（LPリンク等）にも流用可能。

### 4.2 バックエンド

| 箇所 | 内容 |
|------|------|
| **Alembic** | 新規マイグレーション（例: `016_add_official_website_url_to_facilities.py`）で `facilities.official_website_url` を追加。 |
| **モデル** | `Facility` に `official_website_url = Column(String(500), nullable=True)` を追加。 |
| **スキーマ** | `FacilityResponse` に `official_website_url: Optional[str] = None` を追加。`FacilitySettingsUpdateRequest` に `official_website_url: Optional[str] = Field(None, max_length=500)` を追加。 |
| **管理API** | 既存の `GET/PUT /admin/facility/settings` の取得・更新処理で `official_website_url` をそのまま扱う（追加実装は最小限）。 |
| **EmailService** | `send_coupon_email()` に引数 `official_website_url: Optional[str] = None` を追加。HTML/テキスト本文で、URL が存在する場合のみ「公式サイト: {URL}」または「ご予約はこちら: {URL}」を1行追加する。 |
| **LeadService** | `create_lead_and_send_coupon()` 内で `send_coupon_email()` を呼ぶ際、`getattr(facility, "official_website_url", None)` を渡す。 |

**メール本文の扱い（案）**

- URL がある場合のみ、有効期限の近くまたは「ご予約はこちら」の一文を追加。
- 例（HTML）: `<p>ご予約はこちら: <a href="{url}">{url}</a></p>`
- 例（テキスト）: `ご予約はこちら: {url}`
- URL が未設定の場合は従来どおり「公式サイトからご予約」の文言のみとし、行の追加はしない。

### 4.3 フロントエンド（管理画面）

| 箇所 | 内容 |
|------|------|
| **型** | `frontend/src/types/facility.ts` の施設設定用型（`FacilityResponse` 相当の管理用・`FacilitySettingsUpdateRequest` 相当）に `official_website_url?: string | null` を追加。 |
| **施設設定画面** | 「クーポン設定（リード獲得）」セクション内、既存の「有効期限（発行日から何ヶ月）」の下（または「クーポン文言」の下）に、**「公式サイトURL」**の入力欄を1つ追加。 |
| **表示** | ラベル例: 「公式サイトURL（任意）」、プレースホルダー例: 「https://example.com」、`maxlength="500"`、`type="url"` または `type="text"`。 |
| **送受信** | `fetchSettings` で `response.facility.official_website_url` をフォームに反映。`handleSave` の `updateData` に `official_website_url` を含め、既存の施設設定APIに送る。 |

### 4.4 公開API・CouponPublic

- **変更なし**。ゲスト画面や公開APIで公式サイトURLを返す・表示する必要はないため、`CouponPublic` や `get_facility_public_info` の戻りには含めない。

### 4.5 実装順序（案）

1. マイグレーション追加・適用（`official_website_url`）
2. モデル・スキーマ・管理API（取得・更新）の修正
3. `EmailService.send_coupon_email()` のシグネチャと本文の拡張、`LeadService` の呼び出し修正
4. 管理画面の型・フォーム・送受信の修正
5. Docker 環境でメール本文まで含めた動作確認

---

## 5. まとめ

- **確認**: 固定フッターからモーダル・送信完了までの表示は**現状日本語のみ**。端末設定や `?lang=` には未対応。
- **追加**: 施設に「公式サイトURL」を1項目持ち、管理の「クーポン設定」で入力し、クーポン送付メールにそのURLを記載する。上記のとおり DB・API・メール・管理画面を既存パターンに合わせて拡張する実装で、大原則に準拠できる。

**指示があるまで、本提案に基づくコード修正は行いません。**
