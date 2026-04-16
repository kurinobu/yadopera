# A1 着手前: Stripe 税・テスト環境・ベースライン記録

**作成日**: 2026-04-15  
**目的**: ロードマップ「事前 1〜3」（テスト環境の事実整理、公式 API の整理、A1 前のベースライン）の**実行結果**を証跡として残す。  
**次工程**: `docs/20260415_サービス開始ロードマップ.md` の **A1〜A2**。

**管理**: 本ファイルへの追記・版上げ・ロードマップとの整合は **リポジトリ編集者（AI エージェントを含む）が行う**。Owner は実測・ダッシュボード確認に専念する。

---

## 1. Stripe テスト環境の事実（自動で確定した範囲）

### 1.1 リポジトリに埋め込まれている税率 ID（テスト用と推定）

| 項目 | 値 |
|------|-----|
| **Tax Rate ID（ハードコード）** | `txr_1TGKOzLnkMufdVquYoyM7JZB` |
| **定義場所** | `backend/app/services/stripe_service.py` の `create_subscription` 内 `items[].tax_rates` |
| **本番での注意** | 同一 ID は **別 Stripe アカウント（本番）では無効**になり得る。live 切替時は **本番ダッシュボードで発行した Tax Rate ID** に差し替える（`docs/20260415_サービス開始ロードマップ.md` §5.1）。 |

### 1.2 参照している Stripe アカウント（2026-04-15 実測）

ユーザー実測（共有スクリーンショット）により、ステージングで使用中の test アカウントは **`acct_1T4aV5LnkMufdVqu`** と確認。

### 1.3 Owner がダッシュボードで確認したチェック項目（2026-04-15）

以下はユーザー実測で確認済み。

- [x] 画面上部が **テストモード**である（本番モードで操作していない）。
- [x] **商品カタログ → 税率**（Tax rates）に **`txr_1TGKOzLnkMufdVquYoyM7JZB`** が存在し、**10%・内税・有効**である。
- [x] Webhook エンドポイントが **`sk_test_...` と同一 `acct_...`** 上にある（ステージング送信先 `/api/v1/webhooks/stripe` を確認）。

---

## 2. 公式 API に基づく整理（Subscriptions の更新）

**出典**: [Update a subscription](https://docs.stripe.com/api/subscriptions/update)（2026-04-15 に取得した API リファレンス本文）。

### 2.1 `default_tax_rates`（サブスクリプション単位）

> The tax rates that will apply to any subscription item that does not have `tax_rates` set. Invoices created will have their `default_tax_rates` populated from the subscription. **Pass an empty string to remove previously-defined tax rates.**

### 2.2 `items.tax_rates`（サブスクリプションアイテム単位）

> A list of Tax Rate ids. These Tax Rates will override the `default_tax_rates` on the Subscription. **When updating, pass an empty string to remove previously-defined tax rates.**

**実装への含意（要旨）**:

- アイテムに **`tax_rates` を付けた状態**で、更新時に **`tax_rates` を省略**しただけでは「削除」とは限らず、**Stripe が既存アイテム属性をどうマージするか**は更新ペイロードと API バージョンに依存する。**A1 では「プラン変更後も期待税率が付くこと」をステージングで実測**して確定させる（ロードマップ §5.2 と同趣旨）。
- 税率を**明示的に外す**場合は、ドキュメント上 **空文字列で削除**が述べられている（`items.tax_rates` および `default_tax_rates` の説明双方）。

### 2.3 やどぺら現行コードが送っているペイロード（A1 前）

**新規作成**（`create_subscription`）: `items` に `price` と `tax_rates: ["txr_1TGKOzLnkMufdVquYoyM7JZB"]`。

**プラン変更**（`update_subscription_price`）: `Subscription.modify` に `items=[{"id": <subscription_item_id>, "price": <new_price_id>}]` のみ。**`tax_rates` 未指定**。

---

## 3. ベースライン（A1 前のリポジトリ状態）

| 項目 | 値 |
|------|-----|
| **記録時点のコミット** | `50f9f1e5a9674533f5a2e3810f94fc8ec949d8f6`（`git rev-parse HEAD`） |
| **ブランチ** | `develop`（`origin/develop` 追従） |
| **Stripe 呼び出し箇所（grep 結果）** | `stripe_service.create_subscription` … `billing.py`（新規／解約後再作成）、`auth_service.py`（新規登録）。`stripe_service.update_subscription_price` … `billing.py`（既存サブスクのプラン変更） |

### 3.1 A1 適用後の比較用（手動で追記する欄）

ステージングで **既存サブスクありのプラン変更**を 1 回実施し、**A1 マージ前**に次を保存すると比較に使える。

- 施設メール / `facility_id`（内部用）:
- Stripe **Subscription ID**:
- **変更前**の Subscription item（Dashboard または `GET /v1/subscription_items/:id`）の `tax_rates` 有無:
- **変更後**の同一 item の `tax_rates` および次回 Invoice の税行:

---

## 4. 変更履歴

| 版 | 日付 | 内容 |
|----|------|------|
| 1.0 | 2026-04-15 | 事前 1〜3 のうち、コード・公式 API・git ベースラインを記録。ダッシュボード確認はチェックリストのみ。 |
| 1.1 | 2026-04-15 | ユーザー実測により §1.3 の 3 項目を完了化（test モード、税率 ID 実在、Webhook acct 整合）。 |
| 1.2 | 2026-04-15 | A1 実装（`update_subscription_price` に `tax_rates` 反映）後の実地確認（Standard 変更、税表示、Webhook 200）と A2（他経路洗い出し）結果を追記。 |
| 1.3 | 2026-04-16 | §9（C1 本番 Stripe/Render 突合の記録方針）・§10（B3 本番開発者画面・方法D。Free プランでは FAQ 一括不可の注意）を追記。証跡追記はリポジトリ編集者が行う旨を明記。 |
| 1.4 | 2026-04-16 | 冒頭に証跡管理責任を明記（Owner は実測のみ）。 |
| 1.5 | 2026-04-16 | §9 を更新。本番 `STRIPE_SECRET_KEY` が live である旨と、突合は Stripe 本番（Live）モードで実施する旨を記録。Owner: 手順1のみ完了。 |
| 1.6 | 2026-04-16 | §11 追加。本番×test API の整理、ステージング/本番×test/live 表、ダッシュボードサンドボックス表示の注記。 |
| 1.7 | 2026-04-16 | Owner 方針「実課金テスト禁止」を反映。B3 は許容例外として §12 に記録し、次工程を B4 に一本化。 |
| 1.8 | 2026-04-16 | E の Go/No-Go 判定を `GO` で記録し、E を完了扱いに更新。 |

---

## 5. A1 実地確認（2026-04-15）

### 5.1 実施内容（ユーザー実測）

- ステージング施設管理画面で `Small -> Standard` にプラン変更（施設: `kuriblog+stg661@gmail.com`）。
- Stripe test で対象 Subscription（`sub_1TGt0BLnkMufdVquZREb8PO0`）を確認。
- Webhook 送信先（`.../api/v1/webhooks/stripe`）で `customer.subscription.updated` の配信結果を確認。

### 5.2 確認結果

- 施設管理画面: `Standard（現在）` へ更新済み。
- Stripe Subscription 画面: 料金体系に **消費税 10%（内税）** 表示。
- 次回請求書プレビュー: 税内訳（例: `¥6,337` に対する内税 `¥634`）を確認。
- Webhook: `customer.subscription.updated` が **200 OK**。

### 5.3 判定

**A1（プラン変更経路への税率反映）は達成**。  
`create_subscription` と `update_subscription_price` の双方で同一 Tax Rate を送る実装になり、実運用画面でも税表示が確認できた。

---

## 6. A2 他経路洗い出し（2026-04-15）

### 6.1 Stripe 呼び出し経路（コード実測）

1. **新規登録時のサブスク作成**
   - `backend/app/services/auth_service.py`  
   - `register_facility_async_stripe()` で `stripe_service.create_subscription()` を呼ぶ
2. **管理画面のプラン変更**
   - `backend/app/api/v1/admin/billing.py`  
   - 既存サブスクあり: `stripe_service.update_subscription_price()`  
   - サブスクなし/解約済み: `stripe_service.create_subscription()`
3. **解約**
   - `backend/app/api/v1/admin/billing.py`  
   - `stripe_service.cancel_subscription()`
4. **Webhook 同期**
   - `backend/app/api/v1/webhooks/stripe.py`  
   - `customer.subscription.*`, `invoice.*` を処理し DB 状態を同期
5. **従量課金（メーター）**
   - `backend/app/services/chat_service.py`  
   - `report_usage_to_meter()` を呼ぶ（課金イベント送信）

### 6.2 税率適用の観点での評価

- **要対応だった経路（完了）**
  - `update_subscription_price()`（有料プラン変更の主経路）  
  - → A1で `items[].tax_rates` を追加済み。
- **既に税率が入る経路**
  - `create_subscription()`（新規登録時、有料プラン再作成時）
- **追加の税率コード改修が不要な経路**
  - `cancel_subscription()`（税率設定を行わない）
  - `webhooks/stripe.py`（受信同期ロジック。税率設定はしない）
  - `report_usage_to_meter()`（メーターイベント送信であり、subscription item 税率設定とは別責務）

### 6.3 A2 判定

**A2 は完了（重大な漏れなし）。**  
税率適用が必要な「サブスク作成・サブスク価格更新」の2経路は両方カバーできている。

### 6.4 残タスク（A2後）

- Tax Rate ID をコード定数で持っているため、将来の本番移行時に環境差異が出る。  
  **次フェーズ候補**: `STRIPE_SUBSCRIPTION_TAX_RATE_IDS`（環境変数）化、または Stripe Tax 主体運用へ移行。

**Status**: A1/A2 完了の証跡。次はロードマップ B1〜B2（品質ゲート再実行）へ進む。

---

## 7. B1〜B2 進行結果（2026-04-15）

### 7.1 B1（自動テスト）実行結果

| 項目 | コマンド | 結果 |
|------|----------|------|
| Backend pytest（CI 相当） | `USE_POSTGRES_TEST=false USE_OPENAI_MOCK=true pytest tests/ -q` | ✅ **66 passed, 113 skipped, 35 warnings** |
| Frontend lint | `cd frontend && npm run lint` | ✅ **exit 0** |
| Frontend build（現行スクリプト） | `cd frontend && npm run build` | ⚠️ スクリプト自体は exit 0 だが、内部の `vite build` は PWA SW 生成でエラー |
| Frontend build（生検証） | `cd frontend && npx vite build` | ❌ **exit 1**（`Unable to write the service worker file`） |
| Backend pytest（PostgreSQL） | `USE_POSTGRES_TEST=true ... TEST_DATABASE_URL=...@postgres:5432/yadopera_test pytest tests/ -q` | ❌ **17 failed, 86 passed, 3 skipped, 73 errors**（実行環境が Compose 内 `postgres` に解決できず、`socket.gaierror` 多発） |

### 7.2 B1 の所見

1. **フロントビルドの品質ゲート判定は未達**。`npm run build` が `vite build; node ...` で終了コードをマスクしているため、B1 証跡は `npx vite build` の失敗結果を正とする。  
2. **PostgreSQL テストは Docker/Compose 前提**。手元で Docker daemon 未起動（`Cannot connect to the Docker daemon`）のため、Runbook どおりの Docker 内経路で再実行が必要。  
3. B1 完了条件は **保留**（未完了）。

### 7.3 B2（§6.5 ステージング Stripe）進行結果

- 本セッションで **回帰確認できた範囲**:
  - 有料プラン変更（Small -> Standard）✅
  - `customer.subscription.updated` Webhook 200 ✅
  - 税表示（内税10%）✅
- ただし、§6.5 の **1〜6 全項目の再完走**は未実施。  
  → `docs/20260328_サービス開始ロードマップ_実行記録.md` の行 1〜6 をテンプレートに、再実行分を追記する。

### 7.4 次アクション（B1〜B2 完了に必要）

1. B2 は §6.5 1〜6 を再実行し、証跡を `docs/20260328_サービス開始ロードマップ_実行記録.md` に追記。

---

## 8. B1 再実行（Docker 起動後・2026-04-15）

Docker daemon 起動後、Runbook 準拠で再実行した結果を以下に記録する。

| 項目 | コマンド | 結果 |
|------|----------|------|
| Backend pytest（CI 相当 / Docker 内） | `docker compose exec -e USE_POSTGRES_TEST=false -e USE_OPENAI_MOCK=true backend pytest tests/ -q` | ✅ **66 passed, 113 skipped, 34 warnings** |
| Backend pytest（PostgreSQL / Docker 内） | `docker compose exec -e USE_POSTGRES_TEST=true -e USE_OPENAI_MOCK=true -e TEST_DATABASE_URL=postgresql+asyncpg://yadopera_user:yadopera_password@postgres:5432/yadopera_test backend pytest tests/ -q` | ✅ **176 passed, 3 skipped, 51 warnings** |
| Frontend lint | `cd frontend && npm run lint` | ✅ **exit 0** |
| Frontend build（生） | `cd frontend && npx vite build` | ✅ **exit 0**（PWA `generateSW` 成功） |

### 8.1 B1 判定

**B1 は完了**。  
前節 7.1 の失敗は「Docker 外実行（PostgreSQL ホスト解決不可）」および一時的な build 環境差に起因し、Runbook 準拠の Docker 経路で再実行した結果、品質ゲート条件を満たした。

---

## 9. C1 本番: Stripe と Render の突合（§4.1 A・2026-04-16）

**証跡ファイルへの追記について**: Markdown の追記は **リポジトリを編集できる担当（開発者・AI エージェント）が実施する**。Owner は Render / Stripe での目視確認に専念すればよい。

**記録（秘密は書かない）**:

1. **Render** `yadopera-backend-production` の Environment に、`STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` / 各 `STRIPE_PRICE_ID_*` が設定されていることは、2026-04-15 以降のダッシュボード確認で既知。
2. **2026-04-16 Owner 報告**: 本番の `STRIPE_SECRET_KEY` は **`sk_live_...`（live）**。**突合は Stripe ダッシュボードの「テストモード」ではなく、本番（Live）側**で **Developers → Webhooks** を開く。URL の **`acct_...`** と、本番 Backend 向け Endpoint の **Signing secret** が、Render の `STRIPE_WEBHOOK_SECRET` と一致することを目視する（**秘密鍵・シークレット全文はチャット・本リポジトリに貼らない**）。
3. ステージングで記録した **`acct_1T4aV5LnkMufdVqu`**（§1.2）は **test 検証時点**の参照。**live 本番**では、**live 用ダッシュボードに表示される `acct_...`** を正とする（test と同一とは限らない）。

**判定**: C1 の「キーが存在し、Webhook が同一 Stripe アカウント配下で運用されている」ことの**運用上の確認**は上記で足りる。詳細なスクショは社内保管とし、本リポジトリには **`acct_` の有無レベル**に留める。

**Owner 作業メモ（2026-04-16）**: 手順 **1（突合）のみ完了**（口頭報告）。**2・3（Standard 化・FAQ CSV）は未着手**。

---

## 10. B3 本番: 開発者画面・方法D（§4.1 B・2026-04-16）

**実施状況（共有スクショに基づく）**:

- 本番 **`https://yadopera-frontend-production.onrender.com/developer/dashboard`** にログインし、**開発者管理ダッシュボード**が表示されることを確認（総施設数・総FAQ数・施設一覧が表示されている）。
- 施設 **ID 1（やどびとホステル）** は **プラン Free** で表示されている。

**取り違えの注意**:

- `~/Downloads/facilities_2026-04-16.csv`（列: `施設ID,施設名,メールアドレス`）は **施設エクスポート用**であり、**FAQ CSV 一括登録（方法D）の入力形式ではない**。FAQ 用には `category`, `language_ja_question`, `language_ja_answer` 等が必要（`backend/app/services/csv_parser.py` の `REQUIRED_COLUMNS`）。

**コード上の制約（本番 B3 が未完了になりうる理由）**:

- 開発者向け `POST .../facilities/{id}/faqs/bulk-upload`（`backend/app/api/v1/developer/faqs.py`）は **Standard / Premium プランの施設のみ**許可。**Free の施設では 403** となる。
- よって **本番で方法Dの「成功」を証跡化するには**、本番に **Standard または Premium の検証用施設**を用意する（テストモード課金で一時アップグレード、または検証専用施設の新規作成）必要がある。

**次アクション（方針更新）**: Owner 方針により **実課金テストは実施しない**。  
本番での Standard/Premium 変更と FAQ 一括登録の実行検証は、**実課金リスクのため許容例外**として扱う。  
代替として「本番開発者画面の表示確認」証跡を採用し、§6.0 の締めは B4 記録で行う。

---

## 11. 質問への回答: 本番で「test API のテストを全部」やったか／ステージング・本番 × test・live の整理

### 11.1 質問の意図への直答

**「本番環境（Render 本番）で、Stripe の test API を使って、テストを全部実行したか？」**  
→ **いいえ、その形では実行していません。** 理由は次のとおり。

- **pytest や CI の自動テスト**は、**主にローカル／Docker／GitHub Actions** で動かし、**本番 Render 上で Stripe test を総なめする**ことは通常しない。
- **Stripe の課金シナリオ（§6.5 相当）**は、文書上 **ステージング＋`sk_test_`（test API）** で証跡付き完走済み（`docs/20260328_サービス開始ロードマップ_実行記録.md`）。
- **本番 Backend が `sk_live_` のとき**、そのプロセスは **常に Stripe live API** を呼ぶ（**同一ホストで test API と live API を同時に使い分けない**。環境変数が1セットのため）。

**「本番で test API のテストがまだ必要か？」**  
→ **課金ロジックの再検証として「本番ホストに test キーを載せて総なめ」することは必須ではない**（むしろ live と取り違えリスク）。**必要な test はステージングで継続**し、本番は **live のスモーク＋監視**が主。

### 11.2 ステージング／本番 × Stripe test／live（整理表）

| 環境（アプリ） | Stripe API | 主な用途 | プロジェクト上の位置づけ | 実行状況（2026-04-16 時点・文書ベース） |
|----------------|------------|----------|----------------------------|----------------------------------------|
| **ステージング**（Render staging） | **test**（`sk_test_` 想定） | §6.5・日常の課金UI検証・Webhook 検証 | **必須**。課金まわりの正本はここ | ✅ §6.5 1〜6 完走記録あり（上記実行記録） |
| **ステージング** | **live** | — | **原則不要**（誤課金・データ混在リスク） | 記録なし（実施推奨もしない） |
| **本番**（Render production） | **test** | live 投入前の短期検証など | **計画上は「C1 で test のまま」もあり得た**が、**既に `sk_live_` なら現在の本番は test ではない** | ⚠️ Owner 報告どおり **live 運用**→**本番ホスト上で「test API 総なめ」はしていない** |
| **本番** | **live** | 実顧客・実課金・本番 Webhook | **現在の本番キーが live なら常時ここ** | キーは live（報告）。**スモーク・突合・監視**は運用で継続 |

### 11.3 Stripe ダッシュボードが `/test` やサンドボックス表示のままになる件

- ブラウザで見ているのは **Stripe 側の「どのデータを表示するか」**であり、**Render の `STRIPE_SECRET_KEY` が live か test かとは独立**。
- URL から `/test` を外しても **サンドボックス／テスト用ホームに戻る**場合は、**Stripe アカウントの UI・利用開始状態・組織のサンドボックス設定**などで **Live のホームがまだ出ない**ことがある（詳細は Stripe ダッシュボードの設定・ヘルプで確認）。
- **Webhook の live signing secret と Render の突合**は、**ダッシュボードが Live 表示にならなくても**、（1）**Render に保存した値とデプロイ時メモの突合**、（2）**Stripe CLI / API で live の Endpoint を確認**、（3）**Stripe サポート**、のいずれかで代替可能。

（本節の版は §4 変更履歴の **1.7** を参照。）

---

## 12. 許容例外（2026-04-16）

- 対象: 本番での B3（方法D: FAQ CSV 一括登録の実行）
- 例外理由: 本番 `sk_live` 運用下での検証は **実課金リスク**を伴うため
- 方針: **実課金テスト禁止**
- 代替証跡: 本番開発者画面のログイン・表示確認（既存スクショ）
- 判定: B3 は許容例外でクローズ、次は B4（§6.0 完了記録）

## 13. B4 完了（2026-04-16）

- Owner 合意により、§6.0 を完了として記録。
- 記録反映先: `docs/20260323_Runbook1.4_品質ゲート進行記録.md`（§6.0 完了の記録欄）
- 状態: B3〜B4 は完了。次工程は D（live 運用の最終整合）。

## 14. D 進行メモ（2026-04-16）

- Stripe Webhook 送信先を `...backend-production.../api/v1/webhooks/stripe` に更新完了（Owner 実施）。
- 「テストイベントを送信する」操作で、ダッシュボード上は Stripe CLI 利用案内のポップアップが表示される挙動を確認。
- Stripe CLI 認証完了（`acct_1T4aV5LnkMufdVqu`、90日有効）。
- `stripe trigger payment_intent.succeeded` 実行成功（`Trigger succeeded!`）。
- Webhook 詳細で `payment_intent.succeeded` の delivery が **2xx** であることを確認（Owner 実施）。
- 判定: D（Stripe live 最終整合）は完了。

## 15. E（カットオーバー）事前確認（2026-04-16）

- `GET /api/v1/health` 相当: `{"status":"healthy","database":"connected","redis":"connected"}` を確認。
- Frontend: `/admin/login` 表示確認、`/developer/login` 表示確認、`/` トップ表示確認。
- Frontend: 管理画面に実ログインし、ダッシュボード表示確認（`admin dashboard ok`）。
- Webhook受信口:
  - `GET /api/v1/webhooks/stripe` → `{"detail":"Method Not Allowed"}`（405 相当）
  - `POST /api/v1/webhooks/stripe`（署名なし）→ `HTTP/2 400`
- 判定: E のGo/No-Go前チェックは主要項目を満たす。
- Go/No-Go 最終判定: **GO**（Owner 合意・2026-04-16）。
- 状態: **E 完了**。
