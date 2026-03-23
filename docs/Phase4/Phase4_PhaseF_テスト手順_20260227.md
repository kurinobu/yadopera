# Phase F: ステージングテスト 実施手順

**作成日**: 2026年2月27日  
**目的**: Phase F チェックリスト（#1, #2, #3, #7, #11）の実施手順をまとめ、実施者が迷わず実行できるようにする。  
**参照**: [Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md](Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md) 8. ステージングテスト計画

### 実施結果（2026-02-27 / 2026-02-28 更新）

| # | 項目 | Docker | ステージング | 備考 |
|---|------|--------|--------------|------|
| 1 | Webhook 署名検証 | OK | ✅ 2026-02-28 | ステージングで 2 件とも 400 を確認。 |
| 2 | 新規登録時 Customer | 実装済 2026-02-28 | 要デプロイ後確認 | `auth_service.register_facility_async_stripe` で有料プラン登録時に Customer/Subscription 作成。 |
| 3 | プラン変更・DB 更新 | - | OK | 502「No such price」は Render の STRIPE_PRICE_ID_MINI 再設定で解消。test61→Mini 成功。 |
| 7 | Webhook DB 更新 | スクリプト用意 | 未 | 解約→Webhook→DB 確認。`phaseF_verify_webhook_db_after_cancel.py --expect-canceled`。 |
| 11 | メーター実機確認 | 送信スクリプト実行済 | 送信 OK | ダッシュボードでの Meter 目視確認は未（有料プラン施設で要実施）。 |

502 調査の詳細: [Phase4_PhaseF_502_No_such_price_調査_20260227.md](Phase4_PhaseF_502_No_such_price_調査_20260227.md)。

---

## 1. #1 Webhook 署名検証（不正 payload → 400）

### 期待動作
- 不正な body または不正な `stripe-signature` で `POST /api/v1/webhooks/stripe` すると **400** が返る。
- `STRIPE_WEBHOOK_SECRET` 未設定時は **503** が返る（受付拒否）。

### Docker での実施手順
1. `docker compose up -d` でバックエンドを起動。
2. 実行:
   ```bash
   docker compose run --rm -e API_BASE_URL=http://backend:8000 backend python scripts/verify_phaseF_webhook_signature.py
   ```
3. 結果: 2 件とも OK（400 または 503）であれば #1 合格。

### ステージングでの実施手順
1. ステージングは `STRIPE_WEBHOOK_SECRET` が設定されている想定。
2. 実行:
   ```bash
   API_BASE_URL="https://yadopera-backend-staging.onrender.com" python backend/scripts/verify_phaseF_webhook_signature.py
   ```
   （要: `pip install httpx`、backend はリポジトリルートで実行）
3. 結果: 2 件とも **400** であれば #1 合格。

---

## 2. #2 新規登録時の Stripe Customer

### 実装（2026-02-28 完了）
- [Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md](Phase4_PhaseF_新規登録時Stripe_Customer_実装計画_20260227.md) 3.2 に沿い、有料プラン登録時に `register_facility_async_stripe` で Stripe Customer および Subscription を別トランザクションで作成。

### 動作確認方法

**Docker での確認**
1. `backend/.env` に Stripe テストキーと各 `STRIPE_PRICE_ID_*` を設定。
2. `docker compose up -d` で postgres / redis / backend を起動。
3. 新規登録 API を呼ぶ（有料プラン指定）:
   ```bash
   curl -s -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test-phasef2@example.com","password":"TestPass123!","facility_name":"Test Facility","subscription_plan":"mini"}'
   ```
4. 数秒待ったあと、DB で該当施設を確認（メールで検索）:
   ```bash
   docker compose exec postgres psql -U yadopera_user -d yadopera -c "SELECT id, name, email, plan_type, stripe_customer_id, stripe_subscription_id FROM facilities WHERE email='test-phasef2@example.com';"
   ```
   - `stripe_customer_id` と `stripe_subscription_id` が NULL でなければ OK。

**ステージングでの確認**
1. develop を Render にデプロイしたあと、ステージングの新規登録画面で有料プラン（例: Mini）を選んで登録。
2. `DATABASE_URL` を設定したうえで `phaseF_inspect_facilities_stripe.py --email "登録したメール"` を実行し、該当施設の `stripe_customer_id` / `stripe_subscription_id` が設定されていることを確認。

---

## 3. #3 有料プラン選択時サブスク作成・DB 更新

### 期待動作
- 管理画面「プラン・請求」で有料プランに変更すると、Stripe に Customer（未作成時）・Subscription が作成され、DB の `stripe_subscription_id` / `subscription_status` / `plan_type` 等が更新される。

### Docker での実施手順
1. Stripe テストキーを `backend/.env` に設定（`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, 各 `STRIPE_PRICE_ID_*`, `STRIPE_METER_EVENT_NAME`）。
2. バックエンド・フロントを起動。Free プランのテスト施設でログイン。
3. 「プラン・請求」→「プラン変更」→ 有料プラン（例: Mini）を選択して実行。
4. 成功メッセージ・現在プラン表示が変わることを確認。
5. DB 確認: 該当施設の `stripe_customer_id`, `stripe_subscription_id`, `subscription_status`, `plan_type` が設定されていること。

### ステージングでの実施手順・DB 確認スクリプト
- 2026-02-26 に実施済み（#4 プラン変更 OK）。2026-02-27 に #3 としてプラン変更→Mini 成功を再確認（施設 364、test61）。必要に応じて再度 Free → 有料で実行し、DB で `stripe_customer_id` / `stripe_subscription_id` を確認。
- **DB 確認スクリプト**（`DATABASE_URL` は環境変数で渡す。リポジトリに記載しない）:
  - 施設一覧の Stripe 列: `DATABASE_URL="..." python backend/scripts/phaseF_inspect_facilities_stripe.py`（オプション: `--email`, `--id`）
  - プラン変更＋DB 検証: `DATABASE_URL="..." API_BASE_URL="..." ADMIN_EMAIL="..." ADMIN_PASSWORD="..." python backend/scripts/phaseF_test_plan_change_and_verify_db.py`（省略時は Mini へ変更）

---

## 4. #7 Webhook 受信時の DB 更新

- 手順書: [Webhook_DB更新_検証手順_20260226.md](Webhook_DB更新_検証手順_20260226.md) に従う。
- 解約実行 → Stripe が `customer.subscription.deleted` を送信 → Webhook が 200 → DB の `plan_type=Free`, `stripe_subscription_id=NULL` 等を確認。
- Stripe ダッシュボード「開発者」→「Webhook」→ 対象エンドポイントの「最近のイベント」で 200 を確認。
- **DB 確認スクリプト**: `DATABASE_URL="..." python backend/scripts/phaseF_verify_webhook_db_after_cancel.py --email "施設メール"` で解約前の状態を表示。解約実行後、`--expect-canceled` を付けて再実行すると期待値（NULL/canceled/Free）と照合。

---

## 5. #11 Phase E: 従量課金メーター実機確認

### 期待動作
- 有料プラン（Mini または Small/Standard/Premium で質問数超過）の施設でゲストがチャットで質問を送信すると、Stripe のメーターに使用量イベントが送信される。
- Stripe ダッシュボード（テストモード）: **Billing** → **Meter events**（または該当メーターのイベント一覧）で、送信後にイベントが記録されていること。

### 実施手順
1. ステージング（または Docker）で、有料プランの施設のゲストチャット URL を開く。
2. ゲストとして 1 件以上質問を送信する。
3. Stripe ダッシュボードにログイン → **Billing** → **Meter events**（メーター名: 「質問数従量 (¥30/質問)」または `Usage-based`）を開く。
4. 直近で当該施設（またはテスト用顧客）に紐づくイベントが 1 件以上増えていることを確認。

### スクリプトでの送信（#11）
- `DATABASE_URL="..." API_BASE_URL="..." python backend/scripts/phaseF_send_guest_chat_for_meter_test.py` で、有料プランかつ `stripe_customer_id` が設定されている施設を 1 件選びゲストチャットを 1 件送信する。指定する場合は `FACILITY_ID=...`、言語は `CHAT_LANGUAGE=ja`（省略時 ja）。
- **注意**: メーターにイベントが記録されるのは有料プラン（Mini は全質問、他は超過分）のみ。Free プラン施設で送信してもメーターには出ない。有料でメーター確認する場合は、先にプラン変更 API で該当施設の Stripe 連携を行ってから本スクリプトを実行する。

### 補足
- Mini プラン: 質問 1 件につき 1 イベント送信。
- Small/Standard/Premium: 請求期間内の質問数がプラン上限を超えた分のみ 1 件ずつ送信。
- メーターのイベント名は環境変数 `STRIPE_METER_EVENT_NAME`（例: `Usage-based`）と Stripe ダッシュボードの設定が一致している必要あり（[Stripe設定確認_20260225.md](Stripe設定確認_20260225.md) 参照）。

---

## 6. 実施記録の反映

- 各項目の結果（OK/NG）は [Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md](Stripe実装_解約_領収書_プラン変更_実装計画_20260223.md) の **8.3 チェックリスト** および **9. テスト実施記録** に記入する。
- NG の場合は不具合内容・修正対応を同じドキュメントまたはリンク先に記録する。
