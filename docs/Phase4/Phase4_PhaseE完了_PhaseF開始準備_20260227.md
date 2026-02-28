# Phase 4: Phase E 完了・Phase F 開始準備

**作成日**: 2026年2月27日  
**目的**: Phase E（従量課金との連携）の完了記録と、次セッションで Phase F（ステージングデプロイ・入念テスト）を即座に開始するための引き継ぎ。  
**次セッション**: **Phase F を開始する。**

---

## 1. Phase E 完了サマリ

| 項目 | 状態 |
|------|------|
| **#15** プラン超過時のメーター送信 | ✅ 実装・動作確認済み（`report_usage_to_meter`、`_report_usage_to_stripe_if_needed`、請求期間・質問数と整合） |
| **#16** Mini プランの従量（同一メーター） | ✅ 実装・動作確認済み（Mini は全質問で 1 件報告） |
| **ローカル動作確認** | ✅ Docker で `verify_phaseE_usage_billing.py` 実行 → 8 項目 OK |
| **ステージング動作確認** | ✅ `verify_phaseE_usage_billing_staging.py` で GET /api/v1/developer/health/phase-e → 7 項目 OK（2026-02-27） |
| **デプロイ** | ✅ develop にコミット・プッシュ済み。Render ステージングは e9ed7c2 でデプロイ済み。 |
| **バックアップ** | `backups/20260226_phaseE_usage_billing/`（実装前の chat_service.py・stripe_service.py） |

**未実施（Phase F で実施）**: 有料プラン施設で質問送信し、Stripe ダッシュボードの Meter events にイベントが記録されるかの**実機確認**。

---

## 2. 次セッションで行うこと（Phase F: ステージングデプロイ・入念テスト）

**計画書**: [Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md](Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md) の「Phase F: ステージングデプロイ・入念テスト（3〜5日）」および「8. ステージングテスト計画」に従う。

| # | 内容 |
|---|------|
| 17 | ステージング環境に環境変数を設定し、バックエンド・フロントをデプロイ。 → **済**（e9ed7c2 デプロイ済み。必要に応じて追加の環境変数確認。） |
| 18 | 「8. ステージングテスト計画」に従い、**Docker** および**ステージング**でテストを実施。 |
| 19 | 不具合修正・ドキュメント更新（本計画書の「実施済み」反映）。 |

### 2.1 Phase F で実施するチェックリスト（未実施分）

計画書 8.3 のうち、**未実施または Phase E 追加で必要な項目**:

| # | 項目 | Docker | ステージング | 備考 |
|---|------|--------|--------------|------|
| 1 | Stripe Webhook 署名検証が正しく動作（不正 payload は 400） | ✅ 完了 2026-02-27 | ✅ 2026-02-28 | 手順: `backend/scripts/verify_phaseF_webhook_signature.py`。ステージングで 2 件とも 400 を確認済み。 |
| 2 | 新規登録時に Stripe Customer が作成される | ✅ 実装済 2026-02-28 | 要デプロイ後確認 | [Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md](Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md) 3.2 に沿い `auth_service.register_facility_async_stripe` を実装。有料プラン登録時にバックグラウンドで Customer/Subscription 作成。 |
| 3 | 有料プラン選択時、サブスクが作成され DB の `stripe_subscription_id` 等が更新される | スクリプト済 | ✅ 2026-02-27 | プラン変更→ Mini 成功。POST /plans/change 200、Stripe subscriptions 200、Webhook subscription.created 200（facility_id=364）。 |
| 7 | Webhook で `invoice.paid` / `subscription.deleted` 等を受けたとき DB が期待どおり更新される | スクリプト済 | ☐ | `phaseF_verify_webhook_db_after_cancel.py`（--email/--id、--expect-canceled）。[Webhook_DB更新_検証手順_20260226.md](Webhook_DB更新_検証手順_20260226.md) 参照。 |
| **11** | **Phase E: 従量課金メーター実機確認**（Mini または超過で質問送信 → Stripe Meter にイベント記録） | スクリプト済 | 送信OK | `phaseF_send_guest_chat_for_meter_test.py` でゲストチャット送信まで実行済み。有料プラン＋stripe_customer_id の施設でメーター記録を確認する場合は、先にプラン変更で Stripe 連携してから実行。 |

**すでにステージング OK の項目**（2026-02-26）: #4 プラン変更、#5 解約、#6 請求履歴・領収書、#8 月次ダッシュボード、#9 プラン変更後 QR・FAQ・チャット、#10 Free プラン扱い。

### 2.2 Phase F で残っている課題（2026-02-28 更新）

| # | 課題 | 状態 | 次のアクション |
|---|------|------|----------------|
| **#1 ステージング** | Webhook 署名検証をステージングで実行 | ✅ 完了 2026-02-28 | 2 件とも 400 を確認済み。 |
| **#2** | 新規登録時に Stripe Customer を作成する | ✅ 実装完了 2026-02-28 | デプロイ後、Docker/ステージングで有料プラン新規登録 → DB の stripe_customer_id / stripe_subscription_id を確認。 |
| **#7** | Webhook 受信時（subscription.deleted 等）の DB 更新検証 | 未実施（☐） | 解約実行 → Stripe Webhook 200 → DB で stripe_subscription_id=NULL, plan_type=Free を確認。`DATABASE_URL="..." python backend/scripts/phaseF_verify_webhook_db_after_cancel.py --email "..." --expect-canceled`。手順: [Webhook_DB更新_検証手順_20260226.md](Webhook_DB更新_検証手順_20260226.md)。 |
| **#11** | 従量課金メーターの実機確認 | 送信は済・Meter 確認は未 | 有料プラン＋stripe_customer_id の施設でゲストチャット送信後、Stripe ダッシュボード **Billing → Meter events** でイベントが記録されていることを目視確認。 |

※ #3 は 2026-02-27 にステージングで完了（プラン変更→Mini 成功）。#4〜#6, #8〜#10 は 2026-02-26 にステージング OK。

---

## 3. Phase F 開始時に開くドキュメント・参照先

| 順 | ドキュメント | 用途 |
|---|--------------|------|
| 1 | **本ドキュメント**（Phase4_PhaseE完了_PhaseF開始準備_20260227.md） | 次セッションの入口。Phase F の作業内容・未実施チェック一覧。 |
| 2 | [Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md](Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md) | Phase F（17・18・19）、**8. ステージングテスト計画**（8.1 原則、8.2 テスト環境、8.3 チェックリスト、8.4 ブラウザテスト、8.5 テスト実施記録）。 |
| 3 | [Webhook_DB更新_検証手順_20260226.md](Webhook_DB更新_検証手順_20260226.md) | #7 Webhook 受信時の DB 更新検証手順。 |
| 4 | [Stripe設定確認_20260225.md](Stripe設定確認_20260225.md) | メーター `Usage-based`、Price ID・環境変数一覧。Phase E 実機確認時の参照。 |
| 5 | [Phase4_PhaseF_テスト手順_20260227.md](Phase4_PhaseF_テスト手順_20260227.md) | **Phase F 各項目の実施手順**（#1〜#11 の具体的な手順・#11 メーター実機確認）。 |

---

## 4. 環境・URL（Phase F 実施時）

| 種別 | URL / 情報 |
|------|-------------|
| **ステージング バックエンド** | https://yadopera-backend-staging.onrender.com |
| **ステージング フロント** | https://yadopera-frontend-staging.onrender.com |
| **Phase E ステージング検証** | `DEVELOPER_PASSWORD=... python backend/scripts/verify_phaseE_usage_billing_staging.py`（開発者パスワードは Render の環境変数と同一） |
| **ローカル Phase E 検証** | `docker compose run --rm backend python scripts/verify_phaseE_usage_billing.py` |

---

## 5. 関連ファイル一覧（Phase E で追加・変更したもの）

| 種別 | パス |
|------|------|
| バックエンド | `backend/app/services/stripe_service.py`（report_usage_to_meter）、`backend/app/services/chat_service.py`（_report_usage_to_stripe_if_needed） |
| 設定 | `backend/app/core/config.py`（STRIPE_METER_EVENT_NAME 等）、`backend/.env.example` |
| 検証エンドポイント | `backend/app/api/v1/developer/health.py`（GET /api/v1/developer/health/phase-e） |
| スキーマ | `backend/app/schemas/developer.py`（PhaseEHealthResponse, PhaseECheckItem） |
| スクリプト | `backend/scripts/verify_phaseE_usage_billing.py`、`backend/scripts/verify_phaseE_usage_billing_staging.py` |
| バックアップ | `backups/20260226_phaseE_usage_billing/` |

### 5.1 Phase F で追加したスクリプト・ドキュメント（2026-02-27）

| 種別 | パス | 用途 |
|------|------|------|
| スクリプト | `backend/scripts/verify_phaseF_webhook_signature.py` | #1 Webhook 署名検証（不正 payload → 400/503） |
| スクリプト | `backend/scripts/phaseF_inspect_facilities_stripe.py` | #3/#7 DB 確認（施設の Stripe 列一覧）。`DATABASE_URL`、任意 `--email`/`--id` |
| スクリプト | `backend/scripts/phaseF_test_plan_change_and_verify_db.py` | #3 プラン変更 API ＋ DB 検証。要 `DATABASE_URL`, `API_BASE_URL`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` |
| スクリプト | `backend/scripts/phaseF_verify_webhook_db_after_cancel.py` | #7 解約後 DB 状態確認。`--email`/`--id`、任意 `--expect-canceled` |
| スクリプト | `backend/scripts/phaseF_send_guest_chat_for_meter_test.py` | #11 ゲストチャット 1 件送信。`DATABASE_URL`, `API_BASE_URL`、任意 `FACILITY_ID` |
| ドキュメント | `docs/Phase4/Phase4_PhaseF_テスト手順_20260227.md` | #1〜#11 の実施手順 |
| ドキュメント | `docs/Phase4/Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md` | #2 実装計画（大原則準拠） |
| ドキュメント | `docs/Phase4/Phase4_PhaseF_502_No_such_price_調査_20260227.md` | 502 原因調査・Render 再設定・プラン変更成功の記録 |
| バックアップ | `backups/20260227_phaseF_tests/` | 本セッション開始時のバックアップ |
| バックアップ | `backups/20260228_phaseF_stripe_customer_on_register/` | 2026-02-28 #2 実装前（auth_service.py） |

---

## 6. 本セッション（2026-02-27）で実行したタスク・テスト結果一覧

| # | タスク・テスト | 結果 | 記録先 |
|---|----------------|------|--------|
| 1 | バックアップ作成 | 完了 | `backups/20260227_phaseF_tests/` |
| 2 | #1 Webhook 署名検証（Docker） | OK | 計画書 8.3・9。未設定時 503 で拒否を確認。 |
| 3 | #2 新規登録時 Stripe Customer | 計画書作成 | [Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md](Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md)。実装は未。 |
| 4 | #3/#7/#11 用 DB 確認スクリプト作成 | 完了 | phaseF_inspect_facilities_stripe.py 他 4 本。 |
| 5 | #3 プラン変更＋DB 検証（test71, test61） | 当初 502 | 502 原因: Stripe「No such price」。調査メモに記録。 |
| 6 | 502 調査・API キー一致確認・Price ID 確認 | 完了 | アカウント一致。正しい ID は末尾 **I**。環境変数再設定を推奨。 |
| 7 | Render の STRIPE_PRICE_ID_MINI 再設定 | ユーザー実施 | コピー＆ペーストで再設定。 |
| 8 | #3 プラン変更（test61→Mini）再実行 | OK | POST /plans/change 200、Stripe subscriptions 200、Webhook subscription.created 200（facility_id=364）。 |
| 9 | #7 解約後 DB 確認スクリプト | 作成済・検証は未 | phaseF_verify_webhook_db_after_cancel.py。解約→Webhook→DB 確認は次セッション。 |
| 10 | #11 ゲストチャット送信（FACILITY_ID=365） | 送信 OK | phaseF_send_guest_chat_for_meter_test.py。Meter 実機確認（ダッシュボード目視）は未。 |
| 11 | 計画書・テスト実施記録・調査メモ更新 | 完了 | 8.3 チェックリスト、9. テスト実施記録、502 調査メモに反映。 |

---

## 7. 次のセッション開始時の始め方

### ステップ 1: 入口ドキュメントを開く

1. **このドキュメント**を開く: `docs/Phase4/Phase4_PhaseE完了_PhaseF開始準備_20260227.md`
2. **「2.2 Phase F で残っている課題」** を確認し、実施する課題を決める。

### ステップ 2: 優先して実施する課題（推奨順）

| 順 | 課題 | やること | 状態 |
|----|------|----------|------|
| 1 | **#2 新規登録時 Stripe Customer** | 3.2 実装案に沿い `register_facility_async_stripe` を実装済み（2026-02-28）。デプロイ後、有料プランで新規登録 → DB で stripe_customer_id / stripe_subscription_id を確認。 | ✅ 実装済 |
| 2 | #1 ステージング | リポジトリルートで `API_BASE_URL=https://yadopera-backend-staging.onrender.com python backend/scripts/verify_phaseF_webhook_signature.py` を実行し、2 件とも 400 であることを確認。 | ✅ 完了 2026-02-28 |
| 3 | #7 Webhook DB 更新 | [Webhook_DB更新_検証手順_20260226.md](Webhook_DB更新_検証手順_20260226.md) に従い、解約実行 → Webhook 200 → DB 確認。`DATABASE_URL` を設定したうえで `phaseF_verify_webhook_db_after_cancel.py --email "..." --expect-canceled` で検証。 | ☐ |
| 4 | #11 メーター実機確認 | 有料プランかつ stripe_customer_id ありの施設（例: 施設 364）で `phaseF_send_guest_chat_for_meter_test.py` を実行後、Stripe ダッシュボード **Billing → Meter events** でイベントが 1 件増えていることを確認。 | ☐ |

### ステップ 3: 参照するドキュメント

- **#2 実装時**: [Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md](Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md)
- **#1/#7/#11 手順**: [Phase4_PhaseF_テスト手順_20260227.md](Phase4_PhaseF_テスト手順_20260227.md)
- **#7 詳細**: [Webhook_DB更新_検証手順_20260226.md](Webhook_DB更新_検証手順_20260226.md)
- **計画書全体**: [Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md](Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md)

### ステップ 4: 環境

- **ステージング バックエンド**: https://yadopera-backend-staging.onrender.com
- **ステージング フロント**: https://yadopera-frontend-staging.onrender.com
- **DB 確認時**: `DATABASE_URL` は環境変数で渡す（リポジトリに記載しない）。

---

## 8. まとめ

| 項目 | 状態 |
|------|------|
| Phase E 実装 | ✅ 完了（従量課金メーター送信・Mini/超過分の報告） |
| Phase E 動作確認 | ✅ 完了（ローカル 8 項目・ステージング 7 項目 OK） |
| ステージングデプロイ | ✅ 完了（e9ed7c2。Phase F 用のデプロイは済） |
| Phase F 本セッション | ✅ #1 Docker 完了、#2 計画書作成、#3 ステージング OK、#7/#11 スクリプト作成・一部実行。502 解消（Render 再設定）。 |
| Phase F 残課題 | #2 実装・#1 ステージングは 2026-02-28 に完了。残りは #7 検証、#11 メーター実機確認。 |

**次セッション開始時**: 本ドキュメントの **「7. 次のセッション開始時の始め方」** に従い、**ステップ 2** の #7（Webhook DB 更新検証）と #11（メーター実機確認）を実施。#2 はデプロイ後に有料プラン新規登録で動作確認を推奨。
