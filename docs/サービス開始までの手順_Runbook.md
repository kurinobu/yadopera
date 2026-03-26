# サービス開始までの手順 Runbook

**作成日**: 2026年3月19日  
**最終更新日**: 2026年3月26日（A-4 本番ブラウザ実施記録を追記）  
**目的**: 本番リリース当日に、手順漏れなく安全にサービス開始するための実行手順書。  
**対象環境**: `main`（本番） / Render（Backend + Frontend） / 本番DB / Redis / Stripe本番。  
**前提**: すべての修正・検証は Docker 環境で完了済みであること。

**ゲート（必読）**: **`docs/サービス開始までの手順整理_実装計画.md` §6.0（全テスト完了ゲート）** を満たすまで、**Stripe 本番キー（live）の投入**および **`landing/` の実装・本番（`main`/GitHub Pages）反映**は行わない（**未了テストがある間は次工程に進まない**）。

**LP・公式サイト（`landing/`）**: **§6.0 通過後**に実装し、**§6.2 順9**（**順8 Go** 等の条件も実装計画どおり）。本 Runbook は主に **Render SaaS 本番** と **Stripe 本番切替**向け。

**補足（2026-03-23）**: **原則**、`landing/` の実装・本番反映は **§6.0 完了後**。**生命・安全・法務上の緊急**のみ、Owner が本書または `docs/` に**例外と理由を記録**したうえで最小限の変更を許容しうる。**`develop` のみでは `yadopera.com` は変わらない**。記録: `docs/20260321_LPティザー_GitHubPages_ブランチとデプロイ不手際_記録.md`。
**補足（2026-03-21・メール）**: `yadopera.com` の受信はムームーDNSで **`MX -> sv16366.xserver.jp`（pref=50）** を使用。Web（GitHub Pages）の A/CNAME とは別管理。

---

## 0. 役割分担

- **実行担当（Dev）**: 手順実行、ログ収集、一次判定。
- **確認担当（Reviewer）**: 各フェーズのチェック項目を読み合わせし承認。
- **最終承認者（Owner）**: Go/No-Go判定、公開可否決定。

---

## 1. T-14日〜T-1日 事前準備

### 1.1 コード凍結前確認（T-14日〜T-7日）

- [ ] 残存課題のうち「本番開始を阻害する項目」を棚卸しし、対応方針を確定。
- [ ] `develop` の最新動作を Docker で再確認（API/管理画面/ゲスト導線）。
- [ ] `feature/* -> develop` マージを完了し、未マージ差分をゼロにする。
- [ ] 旧運用メモとの不整合（旧Vercel記述など）を本Runbookに統一。

### 1.2 本番設定準備（T-7日〜T-3日）

現状 `render.yaml` は**ステージングのみ**。本番用 Web Service が**未作成**の場合は、先に実装計画 **`docs/サービス開始までの手順整理_実装計画.md` §6.1.1** のチェックリストで **Render 本番 Backend / Frontend を新規作成**し、`main`・Dockerfile／static ビルド・本番環境変数を設定してから下記を確認する。

- [ ] Render本番 Backend サービス設定（ブランチ `main`）を確認。
- [ ] Render本番 Frontend サービス設定（ブランチ `main`）を確認。
- [ ] 本番 `DATABASE_URL` / `REDIS_URL` / `SECRET_KEY` / `CORS_ORIGINS` を確認。
- [ ] **Stripe 本番キー（live）**と Price ID、Webhook Secret は **§6.0 完了まで Render 本番には設定しない**（準備段階では **読み合わせ・Stripe ダッシュボード側の確認のみ**可。誤って test と混在させない）。
- [ ] ログ・監視確認手段（Render Logs / Stripe event logs）を準備。

### 1.3 データ保全準備（T-2日〜T-1日）

- [ ] **本番 DB 方針**: **ステージング DB のレコードを本番へ移行しない**（一括ダンプインポートは行わない）。**本番での検証に必要なデータのみ**、目的限定で投入・作成してよい（実装計画 §6.2 順6）。
- [ ] 本番DBバックアップ手順を確定（管理コンソールまたは `pg_dump`）。
- [ ] ロールバック時に戻す対象（アプリ/DB/環境変数）を明文化。
- [ ] 障害連絡チャネルと判断者を固定（Ownerに即時連絡可能な状態）。
- [ ] 破壊系 SQL（`TRUNCATE/DELETE/DROP`）は、実行前に接続先指紋（`current_database()/inet_server_addr()/inet_server_port()`）と主要件数（`users/facilities/faqs/messages`）を採取し、**接続先ホストと対象テーブル集合の 2段階承認**を Owner から得る。
- [ ] 破壊系 SQL の直前に `pg_dump -Fc` を取得し、取得ファイル名・サイズ・保存先を記録する（取得確認なしで実行しない）。

### 1.4 品質ゲート・全テスト完了（§6.0）（T-7日以前推奨）

実装計画 **§6.0** および **§6.2 順2**。**未完了のテストが 1 件でもある間は、Stripe live 投入・LP 実装・本番 LP 反映・順7 以降に進まない。**  
**コマンド・ファイル一覧のドラフト**: 実装計画 **§14.2**。ブロッカー棚卸し: **§14.1**。  
**自動テストの実行証跡（記録例）**: `docs/20260323_6.0品質ゲート_実行記録.md`（手元ターミナル・リポジトリルート・`docker compose` 起動が前提）。  
**§1.4 全体の進行・チェックリスト（大原則に沿った順番）**: `docs/20260323_Runbook1.4_品質ゲート進行記録.md`（ステップ 1〜6・Owner 記録欄）。

- [x] **Docker** で API / 管理画面 / ゲスト導線の回帰（証跡：日付・実施者。上記 **進行記録** ステップ 2 に記入可）。
- [x] **リポジトリ内で自動実行可能なテストをすべて実行し合格**（pytest / スクリプト / CI 等。**§14.2** をチェックリスト化し証跡を残す）。
- [x] **テスト用データ生成や外部連携が必要なテスト**は、Render 設定・認証情報が必要なものは **Owner と共同**で実施し、結果を記録する。
- [x] **ステージング**で Stripe **test mode** の必須シナリオ完走（実装計画 **§6.5** と同一項目でチェック）。
- [x] **本番環境**で、開発者管理画面の主要導線（ログイン/施設一覧/CSV導線）を確認する（ステージング実施済みのみでは不可）。
- [x] **本番環境**で、FAQ CSV 一括登録（開発者管理画面の方法D）を**テスト用データで**実施し、投入・更新・監査ログを確認する（本番データを破壊しない条件で実施）。
- [x] **Owner による「全テスト完了」確認**を本書実施記録または `docs/` に記載。
- [x] 本番ブロッカー Issue がゼロ、または Owner 承認の許容例外として文書化。

### 1.5 Stripe 本番キー（live）を Render 本番に入れる**直前**（T-3日〜T-1日）

**前提**: **§1.4（§6.0）がすべて完了していること。** 未完了なら **本節の環境変数設定は実施しない**。

実装計画 **§6.4** に準拠。ステージングで一度通っていても **本番直前に再実行**推奨。

- [x] **§6.0 完了・Owner 記録**を再確認。
- [x] 本番用 Price ID / Webhook エンドポイント（本番 API URL）/ 署名シークレットの**読み合わせ**（test と live の混在なし）。
- [ ] `docs/領収証_インボイス対応化_設定計画.md` と表示・番号体系が整合。
- [x] この読み合わせ**後**に、Render 本番の **`STRIPE_*` を live に設定**する（設定タイミングは Owner と合意し実施記録に残す）。
  - 2026-03-24 実施: Stripe live の Price / Webhook（`/api/v1/webhooks/stripe`）を作成し、Render 本番 `yadopera-backend-production` の `STRIPE_*` を live 値へ更新。保存後に自動デプロイ完了を確認。

---

## 2. 当日手順（T=0）

### 2.1 リリース開始宣言

- [x] 作業開始時刻を記録。  
  - 2026-03-23 16:56:24 +0900（実行記録）
- [x] `develop` と `main` の最終差分確認（意図しない差分がないこと）。  
  - 2026-03-23 時点: `origin/main...origin/develop = 2 / 118`（差分あり。反映対象コミットの最終選定が必要）
  - `main` のみの 2 コミット: `e6831dd`（`landing/index.html` ティザー同期）、`720caff`（`landing/webauth.html`）。
  - 判定: **含める（決定）**。`main` 先行 2 コミットは今回リリース対象として扱う。
- [x] 作業中は `main` への直接コミット禁止、緊急時以外は手順外作業を行わない。  
  - 本セッションでは `main` への直接操作を実施していない。

### 2.2 事前バックアップ

- [x] 本番DBバックアップを取得。  
  - 2026-03-23 18:15 JST、PostgreSQL 18.1 に対し `postgres:18` コンテナの `pg_dump` で取得完了（サーバー/クライアント版数差異を解消）。
- [x] バックアップ取得時刻と保管先を記録。  
  - 保管先: `/Users/kurinobu/projects/yadopera/backups/production_db_manual_dump_20260323/yadopera_prod_20260323.dump`（約 9.6MB）
- [x] バックアップ復元手順の確認（最低1回、机上確認）。  
  - 復元対象（DB/環境変数/アプリ）を §1.3・§6 と突合済み。実DBの取得は本番権限待ち。

### 2.3 デプロイ実施

- [x] `develop` で最終確認済みコミットを `main` に反映。  
  - 2026-03-23 実施: `main` に `origin/develop` をマージ（`landing/index.html` 競合は今回方針どおり `main` 先行内容を採用）し、`8dd263a` を `origin/main` へ push 済み。
  - 2026-03-26 追記: `origin/develop` の先端 `96178b1` を `main` へ fast-forward 反映し、`origin/main` に push 済み（`19f2172..96178b1`）。
- [x] **`STRIPE_*` 本番（live）**: **§1.4（§6.0）完了前**は Render 本番に live を入れない（test のまま、または未課金で動作確認する）。**live は §1.5 を満たした後**に設定する。  
  - §1.4 完了を記録済み。live 投入は未実施（本番作業フェーズで実施）。
- [x] `main` push 後、Render 自動デプロイ開始を確認。  
  - 2026-03-23 実施: `yadopera-production`（Production）配下で `yadopera-frontend-production` / `yadopera-backend-production` を `branch=main` で作成し、`8dd263a` の自動デプロイ開始を Events で確認。
- [x] Backend/Frontend のデプロイ完了ステータスを確認。  
  - 2026-03-23 22:39 JST: Backend Events に `Your service is live` を確認。  
  - Frontend も `yadopera-frontend-production` が Live 表示であることを確認。

### 2.4 DBマイグレーション確認

- [x] 本番環境で `alembic upgrade head` が完了していることを確認。  
  - Render Backend デプロイログで migration 実行後に起動完了・Live 化を確認。
- [x] `alembic_version` が期待リビジョンであることを確認。  
  - 本番DBへ接続し `select version_num from alembic_version;` を実行、`022` を確認（`backend/alembic/versions/022_add_overage_behavior_to_facilities.py` と一致）。
- [x] 主要テーブルの存在確認（facilities/messages/faqs/stripe関連カラム）。  
  - `facilities` / `messages` / `faqs` を確認。  
  - `facilities` の Stripe 連携列 `stripe_customer_id` / `stripe_subscription_id` / `subscription_status` / `cancel_at_period_end` を確認。

### 2.x 実行ログ（2026-03-23 現在）

- §1.4（品質ゲート）は `docs/20260323_Runbook1.4_品質ゲート進行記録.md` で完了記録済み。  
- §2.2（本番DBバックアップ）は完了。  
- §2.3 の `develop -> main` 反映は完了（`8dd263a` push）。  
- Render 本番 `yadopera-production` 配下で Backend / Frontend の作成・設定・デプロイを完了し、双方 Live を確認。  
- Backend は初回失敗（`rootDir` と `Dockerfile` の重複指定）を修正し、`Root Directory=backend` / `Dockerfile=./Dockerfile` で再デプロイ成功。  
- §2.4 は本番DB接続で `alembic_version=022`、主要テーブル、Stripe関連カラム確認まで完了。  
- 疎通確認: `GET /api/v1/health=200`、Backend ルート `200`、Frontend ルート `200`。
- Frontend の SPA ルート直アクセス（`/admin/login` / `/f/:facilityId`）が 404 になる問題を検知し、Render `Redirects/Rewrites` に `/* -> /index.html (Rewrite, 200)` を追加して復旧（再確認で各URL 200）。

---

## 3. リリース直後の機能確認（30分以内）

### 3.0 本番にブラウザで入るURL（必読）

**いま使える本番フロントのホスト名は、Render が付与した次の1つだけです（コピー用）**  
`https://yadopera-frontend-production.onrender.com`

| 目的 | そのまま開くURL（`https` を含む） |
|------|-----------------------------------|
| トップ | `https://yadopera-frontend-production.onrender.com/` |
| **新規登録（施設登録）** | **`https://yadopera-frontend-production.onrender.com/admin/register`** |
| ログイン | `https://yadopera-frontend-production.onrender.com/admin/login` |
| パスワード再設定 | `https://yadopera-frontend-production.onrender.com/admin/password-reset` |

**`https://app.yadopera.com` が「サイトにアクセスできません」になる理由（2026-03-23 時点では正常）**  
- 公開DNSで `app.yadopera.com` が **まだ存在しない（NXDOMAIN）** 状態。ムームーDNS等に **CNAME（Render が指示するターゲット）** をまだ追加していないか、反映前のため、ブラウザからは名前解決できない。  
- **カスタムドメインを使うには**: Render の当該 Static Site → **Custom Domains** で `app.yadopera.com` を追加し、表示された **CNAME** を DNS に登録し、検証が **Verified** になるまで待つ。完了までは **上表の `onrender.com` のURL** を使う。
- **運用方針の明文化**: ムームーDNSの変更（`app.yadopera.com` / `api.yadopera.com` の CNAME 追加）は、**カスタムドメイン運用へ切り替える時にのみ必要**。`onrender.com` 運用を継続する限り、Stripe live 切替のためだけに DNS 変更は必須ではない。

**`onrender.com` で 404 になるときの確認**  
- ホスト名の打ち間違い（例: `staging` と `production` の取り違え、ハイフンの欠落）。  
- `http://` ではなく **`https://`** で開く。  
- それでも 404 のとき: Render Static Site の **Redirects/Rewrites** に `/* -> /index.html`（Rewrite 200）があるか確認（SPA の深いパスに必須）。

**大原則: 本番 Backend の `FRONTEND_URL`（メール確認の成否に直結）**  
- 確認メールのリンクは `{FRONTEND_URL}/admin/verify-email?token=...` で生成される（アプリ実装どおり）。  
- **DNS でまだ解決できないドメイン（例: 未設定の `app.yadopera.com`）を `FRONTEND_URL` にしたままだと、ユーザーがメールから確認できず、DB の `email_verified` が更新されない。**  
- カスタムドメインが **Verified** になるまでは、`FRONTEND_URL` を **実際にブラウザで開ける本番フロントのオリジン**（例: `https://yadopera-frontend-production.onrender.com`、末尾スラッシュなし）に合わせる。変更後は **確認メールの再送**が必要。

**大原則: 本番 Frontend の `VITE_API_BASE_URL`（ブラウザが API を呼ぶ先・ビルド時に埋め込み）**  
- フロントは `https://yadopera-frontend-production.onrender.com` でも、ここが `https://api.yadopera.com` など **まだ DNS で解決できないホスト**だと、DevTools では **`net::ERR_NAME_NOT_RESOLVED`** となり、画面上は「ネットワークエラーが発生しました」になる（**CORS の前段**で失敗する）。  
- **`api.yadopera.com` が Verified になるまでは**、`VITE_API_BASE_URL` を **実際に名前解決・HTTPS 応答できる本番 Backend のオリジン**（例: `https://yadopera-backend-production.onrender.com`、**末尾に `/api/v1` を付けない**）にし、Static Site を **再ビルド・再デプロイ**する。  
- API 用カスタムドメインの DNS が有効になったら、`VITE_API_BASE_URL` を `https://api.yadopera.com` に戻して再デプロイすればよい。**Backend の `CORS_ORIGINS`** には、当該フロントのオリジン（上記 `onrender.com` または将来の `app.yadopera.com`）を含める。

### 3.1 基本ヘルス

- [x] `GET /api/v1/health` が 200。  
  - 2026-03-23 実測: `https://yadopera-backend-production.onrender.com/api/v1/health` = `200`
- [x] ルート応答が 200（Backend）。  
  - 2026-03-23 実測: `https://yadopera-backend-production.onrender.com/` = `200`
- [x] Frontendのトップ表示が正常。  
  - 2026-03-23 実測: `https://yadopera-frontend-production.onrender.com/` = `200`

### 3.2 主要導線（管理者）

**実施順（必須）**: 本番で **まだ施設登録（管理アカウント作成）をしていない場合は、ログイン確認より先に** 次を実施する。資格情報を第三者に渡す・チャットに貼る必要はない。

1. **新規登録（本番アプリ）**: `https://yadopera-frontend-production.onrender.com/admin/register` で施設・メール・パスワードを登録する。  
2. **メール確認**: アプリが要求する場合は、確認メールのリンクを完了する（届かないときは Brevo・DNS・迷惑メールを確認）。  
3. **ログイン（本番アプリ）**: `https://yadopera-frontend-production.onrender.com/admin/login` で、手順1で設定したメール・パスワードを使う。  
4. **既にメールが本番DBに存在するが自分で登録した覚えがない**／**パスワード不明**のとき: 新規登録ではなく `https://yadopera-frontend-production.onrender.com/admin/password-reset` で再設定する。

**対象のログイン先**: Render / GitHub / Docker ではなく、上記 **本番 Yadopera 管理画面** のみ。

- [x] ログイン -> ダッシュボード表示。
- [x] FAQ一覧表示。
- [x] プラン・請求ページ表示。
- [x] 請求履歴・領収書導線表示。
  - 2026-03-24 実施記録: 本番管理画面で上記4項目を確認完了（メールアドレス確認完了後）。
  - 2026-03-23 メモ（検証時）: 本番で未登録のままログイン資格の提示を求めるのは順序が逆。**先に §3.2 の手順1〜3** を実施する。API検証で `kuriblog@gmail.com` は 401（パスワード不一致）・DB上はユーザーあり、という事象のみ記録。

### 3.3 主要導線（ゲスト）

- [x] 施設URLアクセス。  
  - 2026-03-23 実測: `https://yadopera-frontend-production.onrender.com/f/384` / `/f/384/welcome` / `/f/384/chat` がいずれも `200`（Rewrite設定後）。
- [x] 会話開始・メッセージ送信。  
  - 2026-03-23 実測: `POST /api/v1/chat`（`facility_id=384`）で `session_id=bdb7665e-2d41-40b3-9b93-6a9fa1496cd4` を取得し、応答生成を確認。
- [x] FAQベース応答・履歴表示。  
  - 2026-03-23 実測: `GET /api/v1/chat/history/bdb7665e-2d41-40b3-9b93-6a9fa1496cd4?facility_id=384` で `user/assistant` の2件履歴を確認（履歴表示系APIは正常）。

### 3.3.1 A-4 スタッフ通知メール（受付番号・Brevo）

実装計画: `docs/エスカレーション_A-4_スタッフ通知メール_実装計画.md`。開発時の自動テストは `backend/scripts/run_a4_tests_with_docker_postgres.sh`（Docker PostgreSQL 前提）。

**用語**: 本節・運用説明では **スタッフ不在時間帯対応キュー** と書く（旧称「夜間キュー」は文書に増やさない）。正本: `docs/開発規約/文書用語_スタッフ不在時間帯対応キュー.md`。

**§3.3.1 調査記録（2026-03-26）**: リポジトリの `render.yaml`・`backend/.env.example`・公開ヘルス・Docker 上 pytest、ならびにこれまでのステージング作業記録に基づき判定。本番は別途 Dashboard で同じ項目を目視すること。

- [x] Backend に **`BREVO_API_KEY`** / **`BREVO_SENDER_EMAIL`**（および送信者名）／**`FRONTEND_URL`**（管理画面リンクのベース）が、対象環境で設定されている。  
  - **ステージング**: `render.yaml` に **`FRONTEND_URL=https://yadopera-frontend-staging.onrender.com`** を確認。`BREVO_*` は Blueprint に列挙されていないため **Render Dashboard の `yadopera-backend-staging` 環境変数で設定**が正本。**`GET https://yadopera-backend-staging.onrender.com/api/v1/health` → 200**（2026-03-26 実行）でサービス稼働を確認。過去のステージング作業で **`BREVO_API_KEY` および `FRONTEND_URL` が Dashboard に存在する画面**があり、スタッフ通知メール経路まで到達した記録がある。**`BREVO_SENDER_EMAIL` / `BREVO_SENDER_NAME`** は Dashboard のキー一覧で **空でないことを最終目視**すること（未設定時は Brevo 送信が成立しない）。  
  - **本番**: リリース当日に **同キーが本番 Web サービスに入っているか**を必ず Dashboard で確認（本記録はステージング中心）。
  - **本番（2026-03-26 利用者実施）**: Render `yadopera-backend-production` の Environment で `BREVO_API_KEY` と `FRONTEND_URL` が設定済みであることを目視確認し、実送信テスト（下記）で経路到達を再確認。
- [x] 通知先となる **施設の `Facility.email`** が有効な受信箱である（テスト送信で到達確認してよい）。  
  - **ステージング**: `docs/セッション引き継ぎ_A-4_FAQ未解決リスト_20260325.md` §6 に、**`Facility.email` を有効アドレスへ修正したうえでスタッフ通知メールの送達が復旧した**事実記録あり。**施設を増やす・本番化するたびに宛先の有効性を再確認**すること。
  - **本番（2026-03-26 利用者実施）**: Free プランで新規登録した施設で「スタッフへ連絡」を実行し、施設宛メールの到達を確認。
- [x] **ゲスト画面に表示される受付番号**と、**スタッフ通知メールの件名・本文に記載される受付番号**が一致する（いずれも DB の **`escalations.id`**）。チャット経由のエスカレーション（AI がエスカレーションが必要と判断して記録が付くケース）と「スタッフに連絡」のいずれか一方で確認してよい。  
  - **実装・自動検証**: `send_staff_escalation_notification` は **`escalations.id` のみ**を件名・本文に埋め込む。Docker PostgreSQL 上で **`backend/scripts/run_a4_tests_with_docker_postgres.sh` → 10 passed**（2026-03-26 再実行）。  
  - **ステージング（利用者実施）**: ゲストの「スタッフに連絡」で **受付番号表示**・**`POST .../escalate` 200**・**メール本文の受付番号一致**を確認した記録がある（即時送信経路）。**新規検証時**は受信トレイまたは Brevo 送信ログでも再確認すること。
  - **本番（2026-03-26 利用者実施）**: 件名 `【YadOPERA】スタッフ連絡受付番号 95（やどぴとホテル）` の到達を確認。メール本文の受付番号 `95` と管理画面会話詳細の受付番号 `95` が一致。
- [x] **スタッフ不在時間帯**に **スタッフ不在時間帯対応キュー**へ入れた場合は、**一括通知処理**（管理画面の手動実行 `POST /api/v1/admin/overnight-queue/process` または運用で定めたバッチ）を実行したあと、**同じ受付番号**でメールが届くことを、ステージングまたは本番で確認する。  
  - **コード・Docker**: `process_scheduled_notifications` から `send_staff_escalation_notification` を呼ぶ経路は **上記 pytest に含まれ 10 passed**。  
  - **ステージング（利用者実施・前会話）**: 施設設定で **16:00〜17:00 をスタッフ不在時間帯**とし、その間にゲストで **「スタッフに連絡」**。**約30分待機後（16:31 以降）**に **`/admin/overnight-queue` の手動実行**→ **メール未到達ではなく到達**、**受付番号一致**、**対応済み**まで実施済み。**当時 Runbook へ未記載だったため、ここに追記（2026-03-26）**。
- [x] FAQ管理画面の「未解決質問リスト」について、該当行の `question` / `message_id` を Network の `GET /api/v1/admin/escalations/unresolved-questions` で同定し、FAQ追加で叩かれる `POST /api/v1/admin/faq-suggestions/generate/{message_id}` の `{message_id}` が一致することを確認（不一致は `get_unresolved_questions()` の `question/message_id` 選定ロジック不整合の可能性）。詳しくは `docs/セッション引き継ぎ_A-4_FAQ未解決リスト_20260325.md`。  
  - **2026-03-26 ステージング実施例**: 受付番号 `id` 91・`message_id` **2552**・質問「新しいバスタオルが借りたいです」について、`POST .../faq-suggestions/generate/2552` が **201**、`source_message_id` **2552**・`suggested_question` が同文言で一致することを確認済み。
  - **2026-03-26 本番実施例（利用者）**: 未解決質問「アイロンを貸してくれますか？」の `FAQ追加` 操作で、Network 上の `faq-suggestions/generate/2566` が **201**（2回）となることを確認。画面上の FAQ 追加提案カードが同質問文脈で更新されることを確認。

### 3.4 決済・Webhook（本番キー切替直後）

実装計画 **§6.4「本番キー切替直後」**・**§6.5** のシナリオに沿って確認する。

- [ ] Stripe Webhook の受信ログにエラー多発がない（署名検証失敗が続いていない）。
- [ ] **新規登録〜有料プラン**（または合意したテスト施設のみの実決済）で Customer / Subscription / 管理画面表示が一致。  
  - 2026-03-24 方針: **Owner 決定により実課金テストは実施しない**。高額課金リスク回避のため、無課金確認のみを実施。
- [ ] プラン変更・解約でサブスク状態と DB / 画面が整合。  
  - 2026-03-24 方針: 上記決定に従い、実課金を伴う操作は実施しない。
- [ ] 請求履歴・領収書（・インボイス要件）が致命障害なく開ける。  
  - 2026-03-24 方針: 実請求確定を伴う確認は保留。
- [x] 失敗イベントをログで追跡可能（必要なら Stripe ダッシュボードで再送確認）。  
  - 2026-03-24 実測: Webhook受信口 `GET=405` / 署名なし `POST=400` を確認し、署名検証が有効であることを確認（無課金確認）。

### 3.5 残存課題（Stripe live 前の必須）

- [x] **開発者管理画面（本番）**の動作確認（ログイン、主要統計、施設一覧、CSV導線）。
- [x] **FAQ CSV 一括登録（本番）**の動作確認（テスト用データ、投入結果、監査ログ）。
- [x] **本番データ整理**: テスト投入データおよびPoC由来データ（メール重複で新規登録に影響する可能性があるもの）の扱いを確定し、削除を実施した。  
  - 2026-03-24 実施: 本番DB `public`（`alembic_version` 除く）を `TRUNCATE ... RESTART IDENTITY CASCADE`。主要テーブル `count(*)=0`、全25テーブル合計 `0` を確認。
- [x] 上記項目を実施記録へ追記し、§1.4（§6.0）完了判定に反映する。

### 3.6 Stripe 審査ブロッカー解消（2026-03-24 方針確定）

背景（Owner 相談）:
- Stripe ダッシュボードで「支払いを一時停止」と表示され、`アカウントのステータス` で追加情報提出タスクが残っている。
- ティザー中心公開のため、審査側が必要情報（特商法・規約・運営者情報・問い合わせ導線）を十分に確認できていない可能性が高い。

実施順（大原則準拠）:
1. [x] **Stripe 審査タスクを先に解消**（最新WebサイトURL提出、必要項目入力）。  
   - 2026-03-24 実施: `yadopera.com` および legal URL を提出し、Stripe ステータスが **審査中** に遷移。
2. [x] `landing/` の **LP + legal 一式**を `main` / GitHub Pages に公開し、審査確認可能な状態にする。  
   - 2026-03-24 実施: ティザー運用を維持したまま、`/legal/*` 導線を `yadopera.com` から辿れる状態に更新。
3. [x] 公開中は `landing/index.html` の CTA を **アプリ新規登録へ直結しない**（一時停止文言または問い合わせ導線へ差し替え）。
4. [ ] Stripe 側で「支払い一時停止」解除を確認し、解除日時を記録する。
5. [ ] 解除後に §3.4 / §4 の監視確認を再実施して Go/No-Go 判定へ進む。

採用方針（比較結論）:
- **採用**: 「アプリ導線を一時停止した LP を `main` 公開して審査を受ける」。
- **非採用**: ティザーに法務リンクだけを追加する最小修正案（審査観点の情報網羅・導線明瞭性が不足しやすいため）。

---

## 4. 監視（2時間〜24時間）

- [ ] 5xx比率、タイムアウト、重大例外の監視。
- [ ] ログイン失敗率の急増がないことを確認。
- [ ] 決済関連イベント失敗（署名検証失敗/Price不一致）を監視。
- [ ] 問い合わせ窓口に重大障害報告がないか確認。

---

## 5. Go / No-Go 判定

### 5.1 Go 条件

- [ ] health/API/Frontend が安定稼働。
- [ ] 認証・ゲストチャット・FAQ・請求導線が動作。
- [ ] 重大ログ（クリティカル）が許容範囲内。

### 5.2 No-Go 条件

- [ ] DBマイグレーション失敗、または不整合発生。
- [ ] ログイン不能・API 5xx連続発生。
- [ ] Stripe連携の致命障害（課金状態不整合、Webhook連続失敗）。

No-Go 1件でも発生した場合は、即座にロールバック判断へ移る。

---

## 6. ロールバック手順（緊急時）

1. Ownerがロールバック実行を決裁。  
2. `main` を直前安定コミットへ戻し再デプロイ。  
3. 必要時は本番DBを事前バックアップ地点へ復元。  
4. サービス復旧確認（health、ログイン、主要画面）。  
5. 事故記録（発生時刻、原因、対応、再発防止）を文書化。

---

## 7. 実施記録テンプレート

- 実施日:
- 実施者:
- 確認者:
- 対象コミット:
- 開始時刻:
- 完了時刻:
- Go/No-Go判定:
- 判定理由:
- インシデント有無:
- 備考:

---

## 8. DNS 事実メモ（2026-03-21）

### 8.1 現在値（ムームーDNS）

- A（`@`）: `185.199.108.153` / `185.199.109.153` / `185.199.110.153` / `185.199.111.153`（GitHub Pages）
- CNAME（`www`）: `kurinobu.github.io`
- MX（`@`）: `sv16366.xserver.jp`（pref=50, Xserver mail）
- TXT（SPF）: `v=spf1 include:spf.brevo.com ~all`
- TXT（Brevo code）: `brevo-code:8f18c221fe04778fe02ccca6a5ccb98c`
- CNAME（DKIM）: `brevo1._domainkey -> b1.yadopera-com.dkim.brevo.com` / `brevo2._domainkey -> b2.yadopera-com.dkim.brevo.com`
- TXT（DMARC）: `v=DMARC1; p=none; rua=mailto:rua@dmarc.brevo.com`

### 8.2 チェック手順（受信障害時）

1. `dig MX yadopera.com +short` または MXToolbox で公開 MX が `sv16366.xserver.jp` か確認。  
2. エックスサーバーの「メールソフト設定」で受信サーバー名（`sv****.xserver.jp`）を確認。  
3. 1 と 2 が不一致なら、ムームーDNSの MX をエックスサーバー側に合わせて修正。  
4. 反映後に `info@` / `support@` などで実受信テストを行う。  

---

## 9. 引き継ぎ記録（2026-03-24）

- 認証メール再送・確認エラーの調査経緯、失敗事例、暫定復旧、次セッション向け TODO は次を参照。  
  `docs/20260324_本番認証メール確認障害_調査記録と次セッション引き継ぎ.md`
- §6.0 再判定のための本番動作テスト実行結果（実施分/未実施分/残存課題）は次を参照。  
  `docs/20260324_本番動作テスト実行記録.md`
- 追記（同日）: 本番で開発者導線ログイン・開発者API・方法D（`facility_id=371`）を実施し、CSV 15件登録成功。重複施設（`facility_id=370`）は 400 を確認。テスト投入FAQの扱い（保持/削除）は Owner 判断待ち。
- 追記（同日）: Owner 指示により本番DBデータを全削除し、`count(*)=0` を確認。§6.0 の Owner 最終判定が `Go` となったため、§1.5（Stripe live 投入直前）に着手開始。
- 追記（同日）: Stripe live 側の Webhook 送信先を新UIで作成（5イベント選択）し、Render 本番 `STRIPE_WEBHOOK_SECRET` を更新。`/api/v1/health=200`、`/api/v1/webhooks/stripe` は `GET=405` / `POST(署名なし)=400` を確認し、受信口の稼働条件（署名必須）と整合。
- 追記（同日）: Stripe 審査ブロッカー（支払い一時停止表示）対応として、`landing` の LP/法務ページを `main`（GitHub Pages）で審査提示し、アプリ導線は一時停止して審査解除を先行する方針を採用。
- 追記（同日）: Stripe 追加情報提出後、`アカウントのステータス` が **審査中** に遷移したことを確認。
- 追記（同日）: ステージングDB全消失インシデントの原因調査・復旧・再発防止を記録。  
  `docs/20260324_ステージングDB全消失インシデント_原因調査報告.md`

---

## 10. 破壊系SQL 実行前チェックテンプレート（必須）

対象: `TRUNCATE` / `DELETE` / `DROP` を含む作業。  
原則: **以下 1〜5 が揃うまで実行しない。**

1. 接続先指紋の採取（ログ保存）
```bash
DATABASE_URL="postgresql://<user>:<pass>@<host>:<port>/<db>"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "select now() as ts, current_database() as db, inet_server_addr() as host, inet_server_port() as port;"
```

2. 主要件数の事前採取（最低4テーブル）
```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "
select 'users' as table_name, count(*) as rows from public.users
union all select 'facilities', count(*) from public.facilities
union all select 'faqs', count(*) from public.faqs
union all select 'messages', count(*) from public.messages;"
```

3. 直前バックアップ取得（サイズ確認まで）
```bash
mkdir -p backups/pre_destructive_$(date +%Y%m%d_%H%M%S)
docker run --rm -v \"$PWD/backups:/backup\" postgres:18 \
  pg_dump "$DATABASE_URL" -Fc -f /backup/pre_destructive_$(date +%Y%m%d_%H%M%S).dump
ls -lh backups | rg "pre_destructive_"
```

4. Owner 2段階承認（必須）
- 承認A: 接続先ホスト/DB 名
- 承認B: 対象テーブル集合と実行SQL

5. 実行後の件数採取（before/after を同一記録に残す）
```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "
select 'users' as table_name, count(*) as rows from public.users
union all select 'facilities', count(*) from public.facilities
union all select 'faqs', count(*) from public.faqs
union all select 'messages', count(*) from public.messages;"
```

---

**Document Version**: 2.9  
**Last Updated**: 2026年3月26日  
**Status**: §3.2（管理者）・§3.3（ゲスト）に加え、**§3.3.1 A-4（スタッフ通知メール）を本番ブラウザ実施で再確認**。Free プラン新規登録施設で「スタッフへ連絡」→ メール到達（受付番号一致）→ 管理画面会話詳細反映 → FAQ管理「未解決質問リスト」反映 → `FAQ追加` の `generate/{message_id}` 201 を確認。`main` は `96178b1` まで反映済み。
