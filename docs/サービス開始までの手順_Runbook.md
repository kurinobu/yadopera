# サービス開始までの手順 Runbook

**作成日**: 2026年3月19日  
**最終更新日**: 2026年3月29日（§3.4.1 Stripe Webhook「イベントの配信」手順・D3）  
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

**個人開発について**: 上記 3 役割は**同一人物が兼務**する想定でよい。Runbook に「Owner」とある箇所は **本人の最終確認** と読み替える。**§6.0 のローカルで機械的に実行できる部分**は **§1.4.1** にコピペ済み。

---

## 1. T-14日〜T-1日 事前準備

### 1.1 コード凍結前確認（T-14日〜T-7日）

- [x] 残存課題のうち「本番開始を阻害する項目」を棚卸しし、対応方針を確定。  
  - 実装計画 §14.1（本番ブロッカー棚卸し）に記録済み。
- [x] `develop` の最新動作を Docker で再確認（API/管理画面/ゲスト導線）。  
  - §1.4（品質ゲート）で Docker 回帰を完了記録済み。
- [x] `feature/* -> develop` マージを完了し、未マージ差分をゼロにする。  
  - §2.1〜§2.3 の反映記録と `develop -> main` 実施記録で整合確認済み。
- [x] 旧運用メモとの不整合（旧Vercel記述など）を本Runbookに統一。  
  - 実装計画・総括・本Runbookで GitHub Pages / Render 方針へ統一済み。

### 1.2 本番設定準備（T-7日〜T-3日）

現状 `render.yaml` は**ステージングのみ**。本番用 Web Service が**未作成**の場合は、先に実装計画 **`docs/サービス開始までの手順整理_実装計画.md` §6.1.1** のチェックリストで **Render 本番 Backend / Frontend を新規作成**し、`main`・Dockerfile／static ビルド・本番環境変数を設定してから下記を確認する。

- [x] Render本番 Backend サービス設定（ブランチ `main`）を確認。  
  - §2.3 の本番 Backend デプロイ記録で確認済み。
- [x] Render本番 Frontend サービス設定（ブランチ `main`）を確認。  
  - §2.3 の本番 Frontend デプロイ記録で確認済み。
- [x] 本番 `DATABASE_URL` / `REDIS_URL` / `SECRET_KEY` / `CORS_ORIGINS` を確認。  
  - 本番立ち上げ時の環境設定確認を §2.x 実行ログに反映済み。
- [x] **Stripe 本番キー（live）**と Price ID、Webhook Secret は **§6.0 完了まで Render 本番には設定しない**（準備段階では **読み合わせ・Stripe ダッシュボード側の確認のみ**可。誤って test と混在させない）。  
  - §1.5 および §2.3 の記録と整合（§6.0 完了後に live 設定）。
- [x] ログ・監視確認手段（Render Logs / Stripe event logs）を準備。  
  - §1.2 〜 §4 の監視手順として運用化済み。

### 1.3 データ保全準備（T-2日〜T-1日）

- [x] **本番 DB 方針**: **ステージング DB のレコードを本番へ移行しない**（一括ダンプインポートは行わない）。**本番での検証に必要なデータのみ**、目的限定で投入・作成してよい（実装計画 §6.2 順6）。  
  - §1.3・§3.5 の記録で方針適用済み。
- [x] 本番DBバックアップ手順を確定（管理コンソールまたは `pg_dump`）。  
  - §2.2 で `pg_dump` 取得と保管先記録済み。
- [x] ロールバック時に戻す対象（アプリ/DB/環境変数）を明文化。  
  - §1.3 および §6（ロールバック手順）に明文化済み。
- [x] 障害連絡チャネルと判断者を固定（Ownerに即時連絡可能な状態）。  
  - §0 役割分担・§1.3 記載済み。
- [x] 破壊系 SQL（`TRUNCATE/DELETE/DROP`）は、実行前に接続先指紋（`current_database()/inet_server_addr()/inet_server_port()`）と主要件数（`users/facilities/faqs/messages`）を採取し、**接続先ホストと対象テーブル集合の 2段階承認**を Owner から得る。  
  - §10 テンプレート化済み（必須運用として固定）。
- [x] 破壊系 SQL の直前に `pg_dump -Fc` を取得し、取得ファイル名・サイズ・保存先を記録する（取得確認なしで実行しない）。  
  - §2.2 実施記録および §10 手順で運用固定済み。

### 1.4 品質ゲート・全テスト完了（§6.0）（T-7日以前推奨）

実装計画 **§6.0** および **§6.2 順2**。**未完了のテストが 1 件でもある間は、Stripe live 投入・LP 実装・本番 LP 反映・順7 以降に進まない。**  
**コマンド・ファイル一覧のドラフト**: 実装計画 **§14.2**。ブロッカー棚卸し: **§14.1**。  
**自動テストの実行証跡（記録例）**: `docs/20260323_6.0品質ゲート_実行記録.md`（手元ターミナル・リポジトリルート・`docker compose` 起動が前提）。  
**§1.4 全体の進行・チェックリスト（大原則に沿った順番）**: `docs/20260323_Runbook1.4_品質ゲート進行記録.md`（ステップ 1〜6・Owner 記録欄）。

- [x] **Docker** で API / 管理画面 / ゲスト導線の回帰（証跡：日付・実施者。上記 **進行記録** ステップ 2 に記入可）。
- [x] **リポジトリ内で自動実行可能なテストをすべて実行し合格**（pytest / スクリプト / CI 等。**§14.2** をチェックリスト化し証跡を残す）。
- [x] **テスト用データ生成や外部連携が必要なテスト**は、Render 設定・認証情報が必要なものは **本人（Owner）が接続情報を用意して**実施し、結果を記録する（個人開発では兼任）。
- [x] **ステージング**で Stripe **test mode** の必須シナリオ完走（実装計画 **§6.5** と同一項目でチェック）。
- [x] **本番環境**で、開発者管理画面の主要導線（ログイン/施設一覧/CSV導線）を確認する（ステージング実施済みのみでは不可）。
- [x] **本番環境**で、FAQ CSV 一括登録（開発者管理画面の方法D）を**テスト用データで**実施し、投入・更新・監査ログを確認する（本番データを破壊しない条件で実施）。
- [x] **Owner による「全テスト完了」確認**を本書実施記録または `docs/` に記載。
- [x] 本番ブロッカー Issue がゼロ、または Owner 承認の許容例外として文書化。

### 1.4.1 §6.0 ローカル検証（コピペ実行・記録）— 手順 1〜5

**目的**: 「§14.2 を見ろ」で終わらせず、**ターミナルに貼って実行し、終わったら結果を返信・記録**できる形に固定する。  
**作業起点**: `docker-compose.yml` がある **リポジトリルート**（以下 `cd` はその前提）。

**初めて用（用語・貼り間違い防止）**

| 用語 | 意味 |
|------|------|
| **CI** | *Continuous Integration*。**GitHub にコードを push したときに自動で走るチェック**（このリポジトリだと `.github/workflows/staging-deploy.yml` の **テスト ジョブ**）。手順 1 は **その自動テストと同じ設定**で手元でも pytest を回す、という意味。 |
| **pytest** | Python 用の **自動テスト実行ツール**。`backend/tests/` のテストを一括実行し、不具合がないかを機械的に確認する。 |
| **リポジトリ** | いま開発している **このプロジェクト一式が入ったフォルダ**（あなたの Mac 上では多くは `…/projects/yadopera`）。**Git** で管理されているコードのかたまり、の意味でも同じ。 |
| **`cd backend`** | **ターミナル**で、「いまいるフォルダを、中の `backend` フォルダに移す」コマンド。**ブラウザの URL 欄には書かない。** |

**`bash` ブロック（`cd` や `pytest` の行）はどこに貼るか**  
→ **ターミナル**（macOS なら **ターミナル.app** や **Cursor 内のターミナル**＝画面下のパネルでプロンプトが `％` や `$` で始まる窓）。**Chrome のアドレスバーには貼らない。**

**フォルダの開き方（Finder でよい）**  
→ Finder で **`docker-compose.yml` というファイルがあるフォルダ**＝リポジトリルート。そこまで行ったら、**Cursor のメニュー「ファイル → フォルダを開く」**でも同じフォルダを開ける。ターミナルをそのフォルダで開いたあと、手順の `cd backend` が意味を持つ。

**結果を AI / レビューに返すとき**: 各ブロック実行後の **`echo EXIT:$?` の行**と、**ターミナル出力の末尾 20〜40 行**を貼る（長い場合はログファイルに保存したパスを書く）。

**要否の答え（1〜5）**

| # | 内容 | やらなくていいか |
|---|------|-------------------|
| **1** | pytest（CI と同条件） | **必須**。やらないと §6.0 の自動テスト相当が未完。 |
| **2** | `npm run build` | **必須**。型チェック兼本番ビルド。 |
| **3** | PostgreSQL 統合 pytest | **推奨**。**省略する場合は理由と日付を自分の記録に残す**（時間短縮のみの省略はリスク了解の上）。 |
| **4** | Docker 起動＋ブラウザ回帰（**§9.3 含む**） | **必須**（大原則: Docker で検証）。 |
| **5** | ステージング Stripe（実装計画 **§6.5**） | **Stripe live 投入・本番 LP 反映など「金銭・公開に直結する工程」の前に必須**。ローカル 1〜4 だけでは **代替にならない**。 |

#### コピペだけ・この順番（ホスト・パス例）

説明は後段の「手順 1」以降。**まずは下を上から実行**する。パスが違う Mac では **`/Users/kurinobu/projects/yadopera` を自分のリポジトリに置換**。

**1 / 5 — pytest** → `EXIT:0` なら **2 / 5** へ。

```bash
cd /Users/kurinobu/projects/yadopera/backend
USE_POSTGRES_TEST=false USE_OPENAI_MOCK=true pytest tests/ -v --tb=short
echo EXIT:$?
```

**2 / 5 — フロント build** → `EXIT:0` なら **3 / 5**（省略する場合は記録に理由）。

```bash
cd /Users/kurinobu/projects/yadopera/frontend
npm run build
echo EXIT:$?
```

**3 / 5 — PostgreSQL 統合 pytest**（**Docker が起動していること**。初回だけ DB 作成ブロックから）。

```bash
cd /Users/kurinobu/projects/yadopera
docker compose exec postgres psql -U yadopera_user -d postgres -c "CREATE DATABASE yadopera_test;"
docker compose exec -e USE_POSTGRES_TEST=true -e USE_OPENAI_MOCK=true \
  -e TEST_DATABASE_URL=postgresql+asyncpg://yadopera_user:yadopera_password@postgres:5432/yadopera_test \
  backend pytest tests/ -v --tb=short
echo EXIT:$?
```

**4 / 5 — Docker＋マイグレ** → 終了後ブラウザで **§9.3**。

```bash
cd /Users/kurinobu/projects/yadopera
docker compose up -d --build
docker compose exec backend alembic upgrade head
echo EXIT:$?
```

**5 / 5 — ステージング Stripe**: コマンド1本では不可。**`docs/サービス開始までの手順整理_実装計画.md` の `### 6.5 必須シナリオ（ステージング・Stripe test mode）`** のチェックリストを手で打勾。（**`docs/20260327_…調査修正案.md` の §6.5「フェーズ依存」とは別**。）

---

#### 手順 1（必須）— バックエンド pytest（GitHub Actions と同条件）

ホストに Python 依存が入っている場合（速い）:

```bash
cd backend
USE_POSTGRES_TEST=false USE_OPENAI_MOCK=true pytest tests/ -v --tb=short
echo EXIT:$?
```

Docker で backend が動いている場合（代替・大原則に近い）:

```bash
docker compose exec backend env USE_POSTGRES_TEST=false USE_OPENAI_MOCK=true pytest tests/ -v --tb=short
echo EXIT:$?
```

**成功の目安**: 終了コード `0`。失敗時は失敗したテスト名とスタック先頭を記録。

---

#### 手順 2（必須）— フロントエンド本番ビルド

```bash
cd frontend
npm run build
echo EXIT:$?
```

**成功の目安**: 終了コード `0`、最後に `built in ...` および PWA / `dist/` 生成の記述。  
**補足**: `npm run lint` は **実行してよい**が `--fix` が付くため、勝手にファイルが変わる。差分を確認してからコミットすること。

---

#### 手順 3（推奨）— PostgreSQL 上で pytest（Docker 起動後）

**初回のみ**テスト用 DB 作成（2 回目以降「already exists」ならスキップ可）:

```bash
docker compose exec postgres psql -U yadopera_user -d postgres -c "CREATE DATABASE yadopera_test;"
```

統合テスト本番:

```bash
docker compose exec -e USE_POSTGRES_TEST=true -e USE_OPENAI_MOCK=true \
  -e TEST_DATABASE_URL=postgresql+asyncpg://yadopera_user:yadopera_password@postgres:5432/yadopera_test \
  backend pytest tests/ -v --tb=short
echo EXIT:$?
```

**省略した場合**: 記録例「手順3省略・理由: （例）当日時間不足・SQLite 経路のみ実施予定・リスク承知」。

---

#### 手順 4（必須）— Docker 起動と画面回帰（§9.3）

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
echo EXIT:$?
```

続けてブラウザで **少なくとも**: 管理ログイン → **`/admin/faqs`（FAQ管理）** で **§9.3**（件数行・Network の `faq_limit`）を実施。必要ならゲストチャット等も。  
**記録**: 実施日時・確認した URL 一覧・§9.3 を満たしたか（スクショ or 短文）。

#### `develop` を push したあと（Render ステージング）— `RENDER_GIT_COMMIT` の見方

**よくある失敗**: 手順書の **`YOUR-STAGING-BACKEND`** という**置き換え前の文字**をそのままアドレスバーに貼ると **Google 検索**になる。**置き換えない文字は貼らない。**

| 使う / 使わない | URL |
|-----------------|-----|
| **使う（Backend・この1本をコピペ）** | **`https://yadopera-backend-staging.onrender.com/__debug_env`** |
| 使わない（フロント。ダッシュボードはここだが debug は出ない） | `https://yadopera-frontend-staging.onrender.com/...` |
| 無いパス（404 になる） | `.../api/v1/__debug_env`（**正しくはルート直下の** `/__debug_env` のみ） |

**手順**: 新しいタブを開く → アドレスバーに上記 **Backend の URL を丸ごと**貼る → Enter → JSON の **`RENDER_GIT_COMMIT`** が、想定コミット（例: `8087da9` 始まり）と一致するか見る。`null` のときは Render のデプロイログでコミットを確認。

---

#### 手順 5（金銭・本番公開の前に必須）— ステージング Stripe 等

**コピペ1本では完結しない**（URL・アカウント・Stripe test mode）。**`docs/サービス開始までの手順整理_実装計画.md` §6.5** の項目を**そのままチェックリスト化し、実行した行に日付と結果を書く**。  
ローカルで 1〜4 だけ通っても **§6.0 全体完了の宣言はできない**（5 が未実施なら）。

---

**詳細なファイル一覧・補助スクリプト**: 実装計画 **§14.2**。証跡の記録例: `docs/20260323_6.0品質ゲート_実行記録.md`。

### 1.5 Stripe 本番キー（live）を Render 本番に入れる**直前**（T-3日〜T-1日）

**前提**: **§1.4（§6.0）がすべて完了していること。** 未完了なら **本節の環境変数設定は実施しない**。

実装計画 **§6.4** に準拠。ステージングで一度通っていても **本番直前に再実行**推奨。

- [x] **§6.0 完了・Owner 記録**を再確認。
- [x] 本番用 Price ID / Webhook エンドポイント（本番 API URL）/ 署名シークレットの**読み合わせ**（test と live の混在なし）。
- [x] `docs/領収証_インボイス対応化_設定計画.md` と表示・番号体系が整合。  
  - 2026-03-26: 方針・手順の文書整合を再確認（実課金テストは Owner 方針により保留運用）。
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
  - 2026-03-23 初回確認: `022`。  
  - 2026-03-27 是正後: Render 本番Backend Shellで `alembic upgrade head` を実行し、`022 -> 023` を適用。`select version_num from alembic_version;` で `023` を確認。
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

#### 3.4.1 Stripe ダッシュボード: Webhook「イベントの配信」の見方（フェーズ D3）

**目的**: §3 を毎回全文検索しなくてよいよう、**どこで・何を見るか**を固定する。  
**用語**: 旧資料や一部画面で **Workbench** と書かれることがあるが、**現行の Stripe ダッシュボード**では **開発者（Developers）→ Webhooks** から同じ確認ができる（**Webhook 送信先＝登録したエンドポイント**）。

**操作手順（ステップバイステップ）**

1. [Stripe ダッシュボード](https://dashboard.stripe.com/) にログインする（**本番確認なら test mode をオフ**にし、**test / live の取り違えに注意**）。
2. 左メニュー **開発者**（**Developers**）→ **Webhooks** を開く。
3. 一覧から、YadOPERA 本番 API の **`/api/v1/webhooks/stripe`** を **送信先 URL** にした **エンドポイント**を選ぶ（例: `https://yadopera-backend-production.onrender.com/api/v1/webhooks/stripe`。環境に合わせて読み替える）。
4. エンドポイント詳細で **「イベントの配信」** タブを開く（英語 UI では **Event deliveries**）。
5. **一覧が 0 件のとき**の意味: **まだ該当する課金・サブスク等のイベントが発生しておらず**、Stripe からこのエンドポイントへ **配信ログが積まれていない**状態であることが多い。**「Webhook が壊れている」証拠にはならない**。初回の実課金・プラン変更などが発生した **後**に、**成功（2xx）または失敗**の行が増えるかを見る。
6. **失敗行があるとき**: HTTP ステータス・エラー概要を確認し、必要なら **Stripe 側の再送**と **Render Backend のログ**（`webhook` / `stripe` でフィルタ）を突合する。

**記録例**: 「YYYY-MM-DD・live・エンドポイント URL・イベントの配信 0 件（未課金のため）」または「invoice.payment_succeeded 200 確認」。

- [x] Stripe Webhook の受信ログにエラー多発がない（署名検証失敗が続いていない）。  
  - 2026-03-26: 受信口再確認（`GET=405` / 署名なし `POST=400`）。連続障害の新規報告なし。
- [x] **新規登録〜有料プラン**（または合意したテスト施設のみの実決済）で Customer / Subscription / 管理画面表示が一致。  
  - 2026-03-24 方針: **Owner 決定により実課金テストは実施しない**。高額課金リスク回避のため、無課金確認のみを実施。
- [x] プラン変更・解約でサブスク状態と DB / 画面が整合。  
  - 2026-03-24 方針: 上記決定に従い、実課金を伴う操作は実施しない。
- [x] 請求履歴・領収書（・インボイス要件）が致命障害なく開ける。  
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
4. [x] Stripe 側で「支払い一時停止」解除を確認し、解除日時を記録する。  
   - 2026-03-26 16:01 JST（利用者確認）: Stripe ダッシュボード上で審査通過・制限解除を確認。
5. [x] 解除後に §3.4 / §4 の監視確認を再実施して Go/No-Go 判定へ進む。  
   - 2026-03-26 16:20 JST 再確認: `health=200`、Backend root `200`、Frontend top `200`、Webhook `GET=405` / 署名なし `POST=400` を再測定し、§4・§5 判定へ進行。

採用方針（比較結論）:
- **採用**: 「アプリ導線を一時停止した LP を `main` 公開して審査を受ける」。
- **非採用**: ティザーに法務リンクだけを追加する最小修正案（審査観点の情報網羅・導線明瞭性が不足しやすいため）。

---

## 4. 監視（2時間〜24時間）

- [x] 5xx比率、タイムアウト、重大例外の監視。  
  - 2026-03-26 16:20 JST: 公開ヘルス再測定で `GET /api/v1/health=200`、Backend root `200`、Frontend top `200` を確認。
- [x] ログイン失敗率の急増がないことを確認。  
  - 2026-03-26 16:37 JST: `admin/login` 画面 `200`、`POST /api/v1/auth/login`（誤認証）`401`、`GET /api/v1/admin/plans`（未認証）`403` を確認し、認証系エンドポイント応答は正常。
- [x] 決済関連イベント失敗（署名検証失敗/Price不一致）を監視。  
  - 2026-03-26 16:20 JST: Webhook 受信口 `GET=405` / 署名なし `POST=400` を再確認（署名必須の挙動と整合）。
- [x] 問い合わせ窓口に重大障害報告がないか確認。  
  - 2026-03-26 時点: 本セッション内で重大障害の新規報告なし（既知課題なし）。

---

## 5. Go / No-Go 判定

### 5.1 Go 条件

- [x] health/API/Frontend が安定稼働。  
  - 2026-03-26 再測定: `health=200`、Backend root `200`、Frontend top `200`。
- [x] 認証・ゲストチャット・FAQ・請求導線が動作。  
  - 既存記録（§3.2、§3.3、§3.3.1、§3.5）に加え、2026-03-26 で認証・Webhook入口の再確認を実施。
- [x] 重大ログ（クリティカル）が許容範囲内。  
  - 2026-03-26 時点: 本セッション内で重大障害の新規報告なし。

### 5.2 No-Go 条件

- [x] DBマイグレーション失敗、または不整合発生。  
  - 該当なし（§2.4 で `alembic_version=022` を確認済み、再監視で異常兆候なし）。
- [x] ログイン不能・API 5xx連続発生。  
  - 該当なし（2026-03-26 再測定で主要公開エンドポイントが正常応答）。
- [x] Stripe連携の致命障害（課金状態不整合、Webhook連続失敗）。  
  - 該当なし（Webhook 受信口の署名必須挙動を再確認、重大障害報告なし）。

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

### 9.1 追記（2026-03-26）: 本番DB分離是正・RCA・再発防止

#### 9.1.1 事実（今回の是正で確認できたこと）

- 2026-03-24 時点の事故は、`TRUNCATE ... CASCADE` が Railway 接続先に対して実行されたことが直接原因だった（別紙インシデント報告と一致）。
- 2026-03-26 に Render で本番DB（`yadopera-postgres-production`）を新規作成し、Backend の `DATABASE_URL` を新DBへ差し替えた。
- Backend Shell で `alembic upgrade head` を実行し、`alembic_version=022` を確認。
- 同 Shell で `current_database()/inet_server_addr()/inet_server_port()` を確認し、`yadopera` / Render 内部アドレス（`10.x.x.x`）/ `5432` であることを確認。  
  ※ Railway ホストではないことを確認済み。

#### 9.1.2 なぜ「本番DB新規作成・分離」が抜けたか（RCA）

1. **論理環境名と物理接続先の混同**
   - 「本番作業」という言葉と実際の `DATABASE_URL` の接続先確認が分離され、物理的には Railway 接続のまま運用された。
2. **Runbook のチェックが証跡不足で「完了」化された**
   - `DATABASE_URL` 確認項目に、接続先指紋（DB名/Host/Port）の記録必須が弱く、誤判定を許した。
3. **破壊系SQLの実行ゲート不徹底**
   - 実行前に「本番専用DBか」を機械的に止める手順（指紋採取＋2段階承認＋当日バックアップ）が十分に運用されていなかった。

#### 9.1.3 なぜ本番でも Railway に繋がったか（判定）

- 本番 Backend の `DATABASE_URL` が Railway を向いた状態で運用されていたため。  
- 根拠は、2026-03-24 のバックアップ/復旧/事故記録の全てが `tramway.proxy.rlwy.net:50673/railway` を示していること。

#### 9.1.4 再発防止策（本Runbookに固定）

1. **接続先指紋の必須記録化（DB切替・破壊系SQLの前後）**
   - `current_database()/inet_server_addr()/inet_server_port()` の結果を Runbook に貼るまで次工程へ進まない。
2. **「本番DBは Render Managed」の運用ロック**
   - 本番 Backend の `DATABASE_URL` に Railway ホスト文字列が含まれていたら No-Go。
3. **破壊系SQLの3点セット必須**
   - 直前 `pg_dump -Fc`、Owner 2段階承認、実行後件数採取の3点が揃わない限り実行禁止。
4. **チェックボックスの完了条件を厳格化**
   - 「目視した」だけでなく、「スクショ or コマンド結果」を証跡として残す。
5. **本番/ステージング分離の定期点検**
   - リリース前に、Backend（本番）と Backend（ステージング）の `DATABASE_URL` のホスト差分を必ず相互確認する。

---

### 9.2 追記（2026-03-27）: Free FAQ上限の本番差分是正（A完了）

#### 9.2.1 事実

- A2〜A6 を `develop` で反映後、ステージングは Free 31件目追加が「30件まで」で拒否されることを確認。
- `develop -> main` 反映直後の本番初回検証で、Free 31件目追加時に「20件まで」と表示差分を検知。
- Render 本番Backend Shellで `alembic current` を確認したところ `022`。
- `alembic upgrade head` 実行で `022 -> 023` を適用。
- `select version_num from alembic_version;` で `023`、`select ... from facilities where plan_type='Free';` で `faq_limit=30` を確認。
- 再テストで本番も「30件まで」に統一された。

#### 9.2.2 原因

- 本番のコード差分ではなく、**本番DBに 023 が未適用だったこと**による `facilities.faq_limit` 実値差分。

#### 9.2.3 再発防止（運用固定）

1. 本番デプロイ後の DB確認は `alembic current` / `alembic upgrade head` / `alembic_version` を必須化。
2. Free 上限の運用確認時は、UI表示だけでなく `facilities.faq_limit` 実値のSQL確認をセットで実施。
3. 本番・ステージング比較時は「コードSHA」と「DB revision」の両方が一致して初めて完了判定とする。

---

### 9.3 追記（2026-03-28）: FAQ件数・上限の管理画面確認（ステップバイステップ）

**禁止**: 本節の文字列を **ターミナル（zsh）に貼らない**。ブラウザと開発者ツールだけ使う。ターミナル手順は **§1.4.1**。

#### 実行順（やることだけ·この番号どおり）

**ステップ 1**  
- **場所**: ブラウザ（Chrome 等）のウィンドウ。画面上部の **アドレスバー**（URL を打つ横長い入力欄）。  
- **何を**: FAQ管理ページを開く。  
- **どのように**: アドレスバーをクリック → 中身を全削除 → **`http://localhost:5173/admin/faqs`** と打つ → **Enter**。  
  - ログイン画面になったら、**管理アカウントでログイン**したあと、もう一度同じ URL を開く。  
  - 接続できないときは **先に** `docker compose up -d` 等でフロント（5173）とバックエンドが動いていることを確認（**§1.4.1 手順4**）。

**ステップ 2**  
- **場所**: いま開いているページの **最上部付近**（太い見出し「FAQ管理」のすぐ下）。  
- **何を**: 「現在」「上限」「件」が含まれる **1 行の文**があるか。  
- **どのように**: 目視。 **あればここで打ち切り**（証跡用にスクショを撮る）。 **なければステップ 3 へ。**

**ステップ 3**（ステップ 2 で行が無いときだけ）  
- **場所**: ブラウザ **開発者ツール**（**F12** または **右クリック → 検証**）→ 上のタブの **Network**（ネットワーク）。  
- **何を**: **`admin/facility/settings`** を含む通信 1 件の **応答本文（JSON）**。  
- **どのように**: Network タブを開いた状態で **ページを再読み込み（F5 または Cmd+R）**。一覧の中から **名前に `settings` が付く行**をクリック → **Response / 応答** ペインを開く → JSON 内の **`faq_limit`** の値を読む（数字か **`null`** か）。  
  - ステータスが **200 以外**なら通信失敗（UI に件数行が出ない原因候補）。

**ステップ 4**（ステップ 3 で `faq_limit` が **`null`** で Free 等の上限があるはずなのに困っているときだけ）  
- **場所**: DB クライアントまたは Runbook **§9.2**・**§10** の手順に従った **psql**（本番なら接続先誤り禁止）。  
- **何を**: 対象施設レコードの **`facilities.faq_limit`** とプラン列。  
- **どのように**: SQL で確認（詳細は §9.2）。**※本番 DB は承認・バックアップ後のみ。**

**ステップ 5**  
- **場所**: メモ・`docs/` の検証記録・チャットへの貼り付け。  
- **何を**: 実施結果の証跡。  
- **どのように**: **URL**・**ログインした施設アカウント**・**ステップ 2 の有無（スクショ）**。ステップ 3 をやったなら **`faq_limit` の値**と **HTTP ステータス**を書く。

**補足（フェーズ D1・件数の読み方）**: 一覧の **「Basic (N件)」** は **そのカテゴリのみ**の件数。画面上部 **「現在 X / 上限 Y 件」** の **Y** はプラン別の **全 FAQ 合計の上限**（Free は **30 件**）。内数と合計上限を混同しないこと。詳細は管理画面 **ご利用マニュアル**（**`/admin/manual`**）の **第4章 4.2 FAQ一覧の見方**（`frontend/src/views/admin/Manual.vue`）。**FAQ管理（`/admin/faqs`）の画面には「4.2」の目次は無い**（マニュアル専用）。

**補足（フェーズ D2・CSV 表示）**: FAQ管理画面上部の **CSV一括登録** 系は **Standard / Premium のみ**表示。**Free では非表示は仕様**（調査修正案 §2.5）。登録画面・プラン・請求・マニュアル（第2章・第4章 4.1）に同趣旨を記載。

**補足（フェーズ D3）**: Stripe Webhook の **イベントの配信**（0 件の意味・再確認タイミング）は **§3.4.1**。

**関連**: `docs/20260327_本番検証_チェック結果と課題_調査修正案.md` §7。

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

**Document Version**: 3.2  
**Last Updated**: 2026年3月29日  
**Status**: A（FAQ上限制御）を本番まで完了。`main` 反映後に本番DBの Alembic `022 -> 023` を適用し、Free の `faq_limit=30` を確認。ステージング・本番ともに 31件目拒否が「30件まで」で一致。**§9.3**・**§1.4.1**（§6.0 ローカル 1〜5 のコピペ・要否）を文書化済み。  
**2026-03-29（フェーズ D・ステージング）**: `develop` コミット **`6a48784`** をプッシュしステージングへデプロイ。**実行コミット確認**: `GET https://yadopera-backend-staging.onrender.com/__debug_env` の **`RENDER_GIT_COMMIT`** が上記と一致。**マニュアル D1**: **`https://yadopera-frontend-staging.onrender.com/admin/manual`** → 左 **ご利用マニュアル**（当該 URL）→ 目次 **第4章 → 4.2 FAQ一覧の見方** で文言確認（FAQ管理 `/admin/faqs` とは別画面）。**調査修正案** `docs/20260327_本番検証_チェック結果と課題_調査修正案.md` の **§6 フェーズ A〜D は文書上完了**。**次の作業の正本**: 本 Runbook 続行および **`docs/サービス開始までの手順整理_実装計画.md` §6**（§6.0・§6.5 Stripe ステージング必須シナリオ等）。
