# サービス開始までの手順 Runbook

**作成日**: 2026年3月19日  
**最終更新日**: 2026年3月23日（§1.4 に `docs/20260323_Runbook1.4_品質ゲート進行記録.md` への参照を追加）  
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

### 1.4 品質ゲート・全テスト完了（§6.0）（T-7日以前推奨）

実装計画 **§6.0** および **§6.2 順2**。**未完了のテストが 1 件でもある間は、Stripe live 投入・LP 実装・本番 LP 反映・順7 以降に進まない。**  
**コマンド・ファイル一覧のドラフト**: 実装計画 **§14.2**。ブロッカー棚卸し: **§14.1**。  
**自動テストの実行証跡（記録例）**: `docs/20260323_6.0品質ゲート_実行記録.md`（手元ターミナル・リポジトリルート・`docker compose` 起動が前提）。  
**§1.4 全体の進行・チェックリスト（大原則に沿った順番）**: `docs/20260323_Runbook1.4_品質ゲート進行記録.md`（ステップ 1〜6・Owner 記録欄）。

- [ ] **Docker** で API / 管理画面 / ゲスト導線の回帰（証跡：日付・実施者。上記 **進行記録** ステップ 2 に記入可）。
- [ ] **リポジトリ内で自動実行可能なテストをすべて実行し合格**（pytest / スクリプト / CI 等。**§14.2** をチェックリスト化し証跡を残す）。
- [ ] **テスト用データ生成や外部連携が必要なテスト**は、Render 設定・認証情報が必要なものは **Owner と共同**で実施し、結果を記録する。
- [ ] **ステージング**で Stripe **test mode** の必須シナリオ完走（実装計画 **§6.5** と同一項目でチェック）。
- [ ] **Owner による「全テスト完了」確認**を本書実施記録または `docs/` に記載。
- [ ] 本番ブロッカー Issue がゼロ、または Owner 承認の許容例外として文書化。

### 1.5 Stripe 本番キー（live）を Render 本番に入れる**直前**（T-3日〜T-1日）

**前提**: **§1.4（§6.0）がすべて完了していること。** 未完了なら **本節の環境変数設定は実施しない**。

実装計画 **§6.4** に準拠。ステージングで一度通っていても **本番直前に再実行**推奨。

- [ ] **§6.0 完了・Owner 記録**を再確認。
- [ ] 本番用 Price ID / Webhook エンドポイント（本番 API URL）/ 署名シークレットの**読み合わせ**（test と live の混在なし）。
- [ ] `docs/領収証_インボイス対応化_設定計画.md` と表示・番号体系が整合。
- [ ] この読み合わせ**後**に、Render 本番の **`STRIPE_*` を live に設定**する（設定タイミングは Owner と合意し実施記録に残す）。

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

**`onrender.com` で 404 になるときの確認**  
- ホスト名の打ち間違い（例: `staging` と `production` の取り違え、ハイフンの欠落）。  
- `http://` ではなく **`https://`** で開く。  
- それでも 404 のとき: Render Static Site の **Redirects/Rewrites** に `/* -> /index.html`（Rewrite 200）があるか確認（SPA の深いパスに必須）。

**大原則: 本番 Backend の `FRONTEND_URL`（メール確認の成否に直結）**  
- 確認メールのリンクは `{FRONTEND_URL}/admin/verify-email?token=...` で生成される（アプリ実装どおり）。  
- **DNS でまだ解決できないドメイン（例: 未設定の `app.yadopera.com`）を `FRONTEND_URL` にしたままだと、ユーザーがメールから確認できず、DB の `email_verified` が更新されない。**  
- カスタムドメインが **Verified** になるまでは、`FRONTEND_URL` を **実際にブラウザで開ける本番フロントのオリジン**（例: `https://yadopera-frontend-production.onrender.com`、末尾スラッシュなし）に合わせる。変更後は **確認メールの再送**が必要。

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

- [ ] ログイン -> ダッシュボード表示。
- [ ] FAQ一覧表示。
- [ ] プラン・請求ページ表示。
- [ ] 請求履歴・領収書導線表示。
  - 2026-03-23 メモ（検証時）: 本番で未登録のままログイン資格の提示を求めるのは順序が逆。**先に §3.2 の手順1〜3** を実施する。API検証で `kuriblog@gmail.com` は 401（パスワード不一致）・DB上はユーザーあり、という事象のみ記録。

### 3.3 主要導線（ゲスト）

- [x] 施設URLアクセス。  
  - 2026-03-23 実測: `https://yadopera-frontend-production.onrender.com/f/384` / `/f/384/welcome` / `/f/384/chat` がいずれも `200`（Rewrite設定後）。
- [x] 会話開始・メッセージ送信。  
  - 2026-03-23 実測: `POST /api/v1/chat`（`facility_id=384`）で `session_id=bdb7665e-2d41-40b3-9b93-6a9fa1496cd4` を取得し、応答生成を確認。
- [x] FAQベース応答・履歴表示。  
  - 2026-03-23 実測: `GET /api/v1/chat/history/bdb7665e-2d41-40b3-9b93-6a9fa1496cd4?facility_id=384` で `user/assistant` の2件履歴を確認（履歴表示系APIは正常）。

### 3.4 決済・Webhook（本番キー切替直後）

実装計画 **§6.4「本番キー切替直後」**・**§6.5** のシナリオに沿って確認する。

- [ ] Stripe Webhook の受信ログにエラー多発がない（署名検証失敗が続いていない）。
- [ ] **新規登録〜有料プラン**（または合意したテスト施設のみの実決済）で Customer / Subscription / 管理画面表示が一致。
- [ ] プラン変更・解約でサブスク状態と DB / 画面が整合。
- [ ] 請求履歴・領収書（・インボイス要件）が致命障害なく開ける。
- [ ] 失敗イベントをログで追跡可能（必要なら Stripe ダッシュボードで再送確認）。

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

**Document Version**: 2.2  
**Last Updated**: 2026年3月24日  
**Status**: §3.3（主要導線: ゲスト）まで完了。残タスクは §3.2（管理者導線）と §3.4（決済・Webhook）。
