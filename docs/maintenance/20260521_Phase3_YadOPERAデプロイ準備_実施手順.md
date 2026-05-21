# Phase 3: YadOPERA デプロイ準備 — 実施手順（画面・コマンド単位）

**作成日**: 2026-05-21  
**親文書**: [ConoHa VPS 移転統合 引き継ぎ](./20260521_ConoHaVPS_移転統合_引き継ぎ.md)  
**前提**: [Phase 2 実施手順](./20260521_Phase2_ConoHa初期設定_実施手順.md) **完了**（2026-05-21）

---

## 次会話引き継ぎ（Step 2 即開始・2026-05-21）

### 次会話プロンプト早見表（何を貼るか）

| 名前 | 行数 | いつ使う | 確実さ |
|------|------|----------|--------|
| **4行ブロック（推奨）** | 4 | **次会話の最初** — いちばん迷わない | ◎ 最も確実 |
| **2行ブロック（短縮）** | 2 | 文書パスは分かるが長文は嫌なとき | ○ ほぼ足りる |
| **1行のみ** | 1 | `Step 2を開始します` だけ | △ 文書を読まず最初から説明しがち |

**4行ブロック** = 下のコード枠の **4文をまとめてコピー**したもの（「4行」は改行の数。別ファイルではない）。

### 4行ブロック（推奨・次会話はこれを貼る）

```
Phase 3 の続き。Step 2（staging Frontend）から開始。
docs/maintenance/20260521_Phase3_YadOPERAデプロイ準備_実施手順.md の
「次会話引き継ぎ（Step 2 即開始）」と §Step 2 を読み、画面操作単位でナビしてください。
憶測禁止。Step 完了時は文書のチェックリストを更新してから次へ。
```

| 行 | 意味（エージェントへの指示） |
|----|------------------------------|
| 1 | Phase 3 の**続き**で、**Step 2（Frontend）** から始める（Step 1 からやり直さない） |
| 2 | 正本はこの md。§**次会話引き継ぎ** と §**Step 2** を読む（確定値・2-A〜2-G） |
| 3 | 画面操作単位でナビ（憶測で UI を書かない） |
| 4 | Step が終わったら**文書のチェックリストを更新**してから次へ（Step 1 の反省対策） |

### 2行ブロック（短縮版）

```
Step 2を開始します。
docs/maintenance/20260521_Phase3_YadOPERAデプロイ準備_実施手順.md の「次会話引き継ぎ（Step 2 即開始）」から。憶測禁止。
```

### 1行のみ（非推奨）

```
Step 2を開始します
```

→ どの Phase・どの文書か伝わらないため、**4行または2行を推奨**。

### 進捗サマリ

| 項目 | 状態 |
|------|------|
| Phase 2 | ✅ 完了 |
| Phase 3 Step 1 Backend | ✅ `yadopera-backend-staging`・health **200** |
| Phase 3 Step 2 **2-A** Backend CORS | ✅ 再 Deploy **Done**（`955cccb`）・health **200** |
| Phase 3 Step 2 **2-B** Create | ✅ `yadopera-frontend-staging` |
| Phase 3 Step 2 **2-C** Provider | ✅ Github・`develop`・Build Path `/`・Save 済 |
| **Phase 3 Step 2 Frontend** | ⏳ **未完了** — `/` のみ Vue・`/admin/login` は **nginx 404**（SPA `try_files` 不足・`frontend/nixpacks.toml` 追加後に再 Deploy） |
| Phase 3 全体 | **未完了** |
| Phase 4 DB リストア | 未（Phase 3 完了後） |

### 次会話で Cursor が最初に読む節（順番固定）

1. 本節（次会話引き継ぎ）  
2. [§Step 2: staging Frontend](#step-2-staging-frontend)（下の **2-A〜2-G**）  
3. [本セッションの記録（Step 1）](#本セッションの記録2026-05-21phase-3-step-1) — GitHub 手動 UPDATE・Environment 上部/下部の教訓  
4. [Phase 2 完了状態](#phase-2-完了状態次会話が使う事実)  
5. 必要なら `git log -1 origin/develop` でデプロイ元コミットの鮮度確認  

**やらないこと**: Phase 4（ダンプ）、DNS 本番切替、Phase 3 完了宣言（Frontend まで終わるまで）

### 確定値（コピペ用・秘密なし）

| 項目 | 値 |
|------|-----|
| VPS IP / staging URL（暫定） | `http://160.251.199.237` |
| Dokploy | `http://160.251.199.237:3000` |
| SSH | `ssh root@160.251.199.237` |
| Project / Environment | **`air-edison`** / **`production`** |
| GitHub App | `Dokploy-air-edison`（`kurinobu/yadopera`） |
| `githubId`（DB 手動登録済み） | `PGfqXi-zEu9VG3AXI8tOv` |
| staging ブランチ | **`develop`**（デプロイ元 `955cccb` 時点） |
| Backend 済み | `yadopera-backend-staging`・Domain Host `160.251.199.237`・port **8000** |
| Backend health | `curl -H "Host: 160.251.199.237" http://160.251.199.237/api/v1/health` → **200** |
| Frontend 作成名 | `yadopera-frontend-staging` |
| Frontend Domain（暫定） | Host `160.251.199.237`・port **80**（Static 既定。画面が違えばその値） |
| Postgres Internal（例） | `airedison-airedisonpostgres-wsxrdk` |
| Redis Internal（例） | `airedison-airedisonredis-eolvti` |

**パスワード・API キー・SECRET_KEY**: Dokploy Environment または **Git 外メモ**のみ。文書・チャットに貼らない。

### Step 2 の実施順（次会話はここから・画面単位）

**2-A（先）Backend CORS** — `yadopera-backend-staging` → **Environment** → **Environment Settings**（上部）に **既存行を残し** 追加:

```text
CORS_ORIGINS=http://160.251.199.237
FRONTEND_URL=http://160.251.199.237
```

→ **Save** → **General** → **Deploy** → Done まで待つ → health 200 再確認。

**2-B** **+ Create Service** → **Application** → Name `yadopera-frontend-staging` → Create  

**2-C** **General** → **Provider**: Github `Dokploy-air-edison` / `yadopera` / **`develop`** / Build Path `/` → **Save**  
（Deploy で `Github Provider not found` なら Step 1 と同様 `application.githubId` の手動 UPDATE — [本セッションの記録](#本セッションの記録2026-05-21phase-3-step-1)）

**2-D** **Build Type**: **Static** 推奨（[render.yaml](../../render.yaml) と同様）。無い場合はスクショで確認。  
| 項目 | 値 |
|------|-----|
| Build Command | `cd frontend && npm ci && npm run build` |
| Publish Directory | `dist`（リポ root からの相対なら `frontend/dist` — **画面ラベルに合わせる**） |

**2-E** **Environment Settings**（上部・Vite は **ビルド時** に埋め込み）:

```text
VITE_API_BASE_URL=http://160.251.199.237
VITE_ENVIRONMENT=staging
```

→ **Save**（Build-time Secrets のみに入れない）

**2-F** **Domains** → Create: Host `160.251.199.237`・Container Port **80**・HTTP・Path `/`  

**2-G** **Deploy** → **Deployments** → **View** でビルド成功  

**2-H** **SPA フォールバック**（Vue `createWebHistory`・`/admin/login` 等）— Nixpacks + Publish `dist` では **`/index.html` は 200 だが `/admin/login` が nginx 404** の事例あり（`frontend/nixpacks.toml` だけでは不十分な場合）。対処: **Build Type → Dockerfile**・[frontend/Dockerfile.staging](../../frontend/Dockerfile.staging) + [frontend/nginx.conf](../../frontend/nginx.conf) を **`develop` に push** 後、再 Deploy。画面:

| 項目 | 値 |
|------|-----|
| Build Type | **Dockerfile** |
| Dockerfile Path | `Dockerfile.staging`（Provider Build Path が `frontend` のとき） |
| Docker Context Path | `.` |
| Publish Directory | （Dockerfile 時は使わない） |

完了確認:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" -H "Host: 160.251.199.237" "http://160.251.199.237/admin/login"
# 期待: 200（body は index.html）
```

ブラウザ `http://160.251.199.237/admin/login` で **nginx の「404 Not Found」ではなく** アプリのログイン UI。

**Step 2 完了後**: 本書の [Phase 3 完了チェックリスト](#phase-3-完了チェックリスト) で Step 2 を `[x]` → [Step 4](#step-4-phase-3-完了確認) → Phase 3 全体完了を文書に明記。

### Step 2 で再発しうる事象（Step 1 から）

| 症状 | 対処 |
|------|------|
| Provider 欄にリポが出ない | Settings → **Git**（Profile ではない）で App 連携確認 |
| Deploy 0s・Github Provider not found | `application` に `githubId=PGfqXi-zEu9VG3AXI8tOv` 等（Step 1 記録） |
| 502 / ValidationError `{}` | 環境変数が Build-time のみ → **Environment Settings 上部**へ |
| Static の Publish パス誤り | ビルドログで `dist` の場所を確認 |

### Step 2 完了の確認コマンド

```bash
ssh root@160.251.199.237
docker service ls | grep -i frontend
curl -sS -o /dev/null -w "%{http_code}\n" -H "Host: 160.251.199.237" "http://160.251.199.237/api/v1/health"
curl -sS -o /dev/null -w "%{http_code}\n" -H "Host: 160.251.199.237" "http://160.251.199.237/"
```

**注意（2026-05-21 検証）**: Step 1 完了時点で `http://160.251.199.237/` は **Backend の JSON**（`{"message":"YadOPERA API v0.3",...}`）が返る。Vue の `index.html` ではない。Frontend Deploy 後は **Traefik のルート優先**を確認し、表示が Vue になるまでスクショ・`curl` 本文で検証すること。

---

## 次会話の開始プロンプト（これだけで可）

**Step 1 完了後（推奨）** — 上記 [次会話引き継ぎ（Step 2 即開始）](#次会話引き継ぎstep-2-即開始2026-05-21) のブロックをコピー。

**初回のみ**:

```
Phase 3 を開始
```

または:

```
docs/maintenance/20260521_ConoHaVPS_移転統合_引き継ぎ.md と
docs/maintenance/20260521_Phase3_YadOPERAデプロイ準備_実施手順.md を読んで、
Phase 3（YadOPERA Dokploy デプロイ準備）を画面操作単位でナビしてください。
```

**Cursor（次会話）が最初にすること**

1. 本書と親引き継ぎ §Phase 3 を読む  
2. **[本セッションの記録](#本セッションの記録2026-05-21phase-3-step-1)**（Step 1 完了事実・未確認・手動回避）を読む  
3. **[コードベース・Git・Docker のスナップショット](#コードベースgitdocker-次会話開始時に把握すること)** を読む（「Phase 3 を開始」だけでは不足）  
4. 必要なら **開始時に** `git status` / `git log develop main -3` を再実行して鮮度確認  
5. [Phase 2 完了状態](#phase-2-完了状態次会話が使う事実) を確認  
6. [ナビ原則](#ナビ原則phase-2-の教訓を継承) に従い、**スクショ・出力を見てから** 1 Step ずつ案内  
7. **次の作業は Step 2（Frontend）** — Phase 3 全体は **未完了**  
8. **Phase 4（DB リストア）・Phase 5（DNS 本番公開）は Phase 3 完了後**

**進捗（2026-05-21）**: **Step 1 のみ完了**（Step 2〜4・Phase 3 完了チェックリストは未）

---

## 本セッションの記録（2026-05-21・Phase 3 Step 1）

実施結果と手順ナビの教訓。**パスワード・API キー・SECRET_KEY は本節に書かない**（Git 外メモのみ）。

### Step 1 完了報告（staging Backend）

**完了日**: 2026-05-21  
**宣言**: **Phase 3 Step 1 のみ完了**。Phase 3 全体・Phase 4 以降は **未完了**。

| # | Step 1 完了条件（本書 §Step 1） | 結果 |
|---|--------------------------------|------|
| 1 | Application `yadopera-backend-staging` 作成 | ✅ |
| 2 | GitHub → `yadopera` / **`develop`** | ✅（下記「手動 DB 登録」参照） |
| 3 | Build: `backend/Dockerfile`・context `backend` | ✅ |
| 4 | **Environment Settings**（ランタイム）に必須キー | ✅ `DATABASE_URL`・`REDIS_URL`・`SECRET_KEY`・`ENVIRONMENT=staging`・`DEBUG=False`・`OPENAI_API_KEY`（値は Git 外） |
| 5 | Deploy 成功（crash なし） | ✅ commit **`955cccb`**（`origin/develop`） |
| 6 | Domains: Host **`160.251.199.237`**・Container Port **8000**・HTTP | ✅ |
| 7 | `GET /api/v1/health` → **200** | ✅ `curl -H "Host: 160.251.199.237" http://160.251.199.237/api/v1/health` |
| 8 | Swarm **1/1** | ✅ service `airedison-yadoperabackendstaging-0ihmdd` |

**確認コマンド（再現用）**:

```bash
ssh root@160.251.199.237
docker service ls | grep -i yadopera
curl -sS -o /dev/null -w "%{http_code}\n" -H "Host: 160.251.199.237" "http://160.251.199.237/api/v1/health"
```

### Step 1 時点で未実施・未確認（Step 2 前後で対応）

| 項目 | 状態 | いつ |
|------|------|------|
| `CORS_ORIGINS` / `FRONTEND_URL` | ✅ `http://160.251.199.237`・再 Deploy **Done**（2026-05-21） | — |
| `alembic upgrade head`（Pre-deploy） | **未確認**（画面で設定したか要確認） | マイグレーション要否は Phase 4 前に再確認 |
| `BREVO_*` / `STRIPE_*` | 未設定（任意・Phase 5 前後でも可） | 必要機能を触る前 |
| Step 2 Frontend | **未着手** | 次会話 |
| Phase 3 完了チェックリスト全体 | **未完了** | Frontend Deploy 後 |

### Dokploy / GitHub で発生した事実（次会話が知るべき）

| 事象 | 回避・対応（パスワードは書かない） |
|------|-------------------------------------|
| GitHub App `Dokploy-air-edison`・Install `kurinobu/yadopera` | installation_id **`134291494`** |
| `/api/providers/github/setup` → 500・`Missing code parameter` | `github` テーブルに **`githubInstallationId`** を手動 UPDATE（`githubId=PGfqXi-zEu9VG3AXI8tOv`） |
| Deploy **Github Provider not found** | `application` に `githubId`・`owner`・`repository`・`branch`・`sourceType` を手動 UPDATE |
| **502 / 0/1**・`ValidationError: input_value={}` | 環境変数が **Build-time Secrets のみ** → **Environment Settings（上部）** に移して Save → Deploy で解消 |
| ランタイムログ | **Deployments → View**（ビルド）と **`docker service logs`**（ランタイム）。「Logs タブ」は環境により無い |

**Dokploy Postgres（設定確認用・秘密は載せない）**:

```bash
docker ps --filter name=dokploy-postgres --format '{{.Names}}'
# 例: dokploy-postgres.1.s02dsc65ec439ke2c8e6egy35
docker exec -it dokploy-postgres.1.s02dsc65ec439ke2c8e6egy35 psql -U dokploy -d dokploy -P pager=off
```

### 手順ナビで誤った／不足だった点（事実）

| 内容 | 正しいこと |
|------|------------|
| Backend health 200 だけで「Phase 3 完了」と案内した | **Step 1 のみ完了**。Step 2 Frontend・Step 4 総合確認が残る |
| 完了をチャットのみで伝え、本書を更新しなかった | **本節とチェックリスト・親引き継ぎを同時に更新する**（Phase 2 と同様） |
| Environment の Build-time と Runtime の区別が遅れた | **Environment Settings（行番号付き・上部）** ≠ **Build-time Secrets（下部）** |

### 今後のナビ原則（Phase 3 継続）

1. **Step 完了のたびに** 本書の実績表・チェックリストを更新してから次 Step  
2. **Phase 完了の宣言の前に** 全 Step（必須 / 任意 / 後回し）を一覧する（本書 §ナビ原則 3）  
3. プレースホルダ禁止・スクショ前提（Phase 2 継承）

### ファクトチェック（2026-05-21・記録の検証）

| 記録項目 | エビデンス | 判定 |
|----------|------------|------|
| health **200** | 会話ログ: ユーザー VPS 出力 `curl .../api/v1/health` → `200`（transcript L105） | ✅ |
| Swarm **1/1** | 同上 `airedison-yadoperabackendstaging-0ihmdd\t1/1` | ✅ |
| 再検証（2026-05-21） | 手元から `curl -H "Host: 160.251.199.237" .../api/v1/health` → **200**・body `database":"connected","redis":"connected"` | ✅ |
| Deploy commit **955cccb** | 会話: Deployments スクショ **1. Done**・commit 表示（transcript L84） | ✅ |
| `origin/develop` @ 955cccb | `git log -1 origin/develop`（本日再実行） | ✅ |
| `githubId` / installation **134291494** | ユーザー SQL: SELECT/UPDATE 出力（transcript L62–66） | ✅ |
| Domains Host **160.251.199.237** port **8000** | ユーザー Domains 作成スクショ（transcript L91） | ✅ |
| Build **backend/Dockerfile**・context **backend** | ユーザー Provider/Build Type スクショ Save 判定（transcript L69） | ✅ |
| Environment Settings 6 キーで 502 解消 | `ValidationError input_value={}` ログ → 実値 Save 後 1/1（L94–105） | ✅ |
| `CORS_ORIGINS` / `FRONTEND_URL` 未設定 | Step 1 完了時点の意図どおり未実施（2-A で追加予定） | ✅ 一貫 |
| `alembic upgrade head` | Dokploy 画面で未確認。`render.yaml` に preDeploy あり | ⚠️ **未確認**（記録どおり） |
| Step 2 Frontend | 未作成（`docker service ls \| grep frontend` 想定で空） | ✅ 未着手 |
| Phase 3 全体完了 | Frontend・Step 4 未了 | ✅ 一貫 |

**文書内で直した矛盾**: §実施順序は Step 0/1「完了」なのに完了チェックリストの Step 0 が `[ ]` だった → Step 0 を `[x]` に整合。§Step 4 に残っていた `<STAGING_API_URL>` を実 curl に置換。

**Step 2 向けリスク（未矛盾・要検証）**: Backend と Frontend が **同一 Host `160.251.199.237`** のとき、Traefik が `/` をどちらに渡すか。現状 `/` は API ルート。**Frontend 後はルート・Path のスクショ必須。**

---

## コードベース・Git・Docker（次会話開始時に把握すること）

**結論**: 「Phase 3 を開始」だけでは足りない。**本節 + 下記ファイルを読んでから** Step 0 に入る。鮮度が必要なら `git status` を再実行。

### リポジトリ構造（デプロイ関連のみ）

```text
yadopera/
├── backend/          # FastAPI・Dockerfile（本番ビルド向け）
├── frontend/         # Vue・Dockerfile は dev 用（npm run dev）
├── landing/          # GitHub Pages（ConoHa 不要・main の LP）
├── docker-compose.yml # ローカル開発（Postgres pg15・Redis）
├── render.yaml       # 旧 Render staging 定義（参考）
└── docs/maintenance/ # 移行手順（本書）
```

### Git 状態（スナップショット 2026-05-21・手元 `develop` チェックアウト時）

| 項目 | 値 |
|------|-----|
| **staging デプロイ元ブランチ** | **`develop`**（Dokploy は **GitHub `origin/develop`** を pull。手元未 push 分は含まれない） |
| **本番デプロイ元** | **`main`**（Phase 5 前後） |
| `origin/develop` | `955cccb` — `docs(lp): record final beta CTA wording adjustments` |
| `origin/main` | `d45618f` — `merge: develop into main for beta CTA trial wording` |
| develop vs main | 共通祖先 `c0544ba`。**develop が docs 1 コミット分先行**（LP 文言記録）。**アプリコードの大きな乖離は小さい** |
| 手元 `git status` | **docs / favicon / maintenance 等が大量に未コミット・未 push**（`docs/maintenance/` 含む）。**Dokploy に載るのは push 済みの Git のみ** |

**Phase 3 開始前の判断（ユーザー）**

- staging を **今の手元の未 push 変更込みで試す** → 先に `develop` へ commit & push  
- **リモート `origin/develop` のみで試す** → push 不要（現状 `955cccb`）

### Docker の二系統（混同しない）

| 環境 | 用途 | Postgres | Redis | アプリ |
|------|------|----------|-------|--------|
| **ローカル** `docker-compose` | 開発 | `pgvector:pg15`・port 5433 | `redis:7.2-alpine` | backend + frontend dev |
| **ConoHa Dokploy** | staging/本番 | `pgvector:pg18`（`air-edison-postgres`） | `redis:7`（`air-edison-redis`） | Phase 3 で追加する Application |

- ローカル `.env` / `docker-compose` のホスト名（`postgres` / `redis`）は **Dokploy では使わない** → **Internal Host** を使う。  
- [backend/Dockerfile](../../backend/Dockerfile): `python:3.11-slim`・port 8000・`alembic` は Render/Dokploy の pre-deploy で実行。  
- [frontend/Dockerfile](../../frontend/Dockerfile): **`npm run dev`** のみ。**staging 本番相当は `vite build` + static 配信**（Render は [render.yaml](../../render.yaml) の static 方式）。Dokploy でビルド方法を画面確認すること。

### 開始時に Cursor が読むファイル（最低限）

| 優先 | パス |
|------|------|
| 必須 | 本書、[backend/.env.example](../../backend/.env.example)、[render.yaml](../../render.yaml) |
| 必須 | [backend/Dockerfile](../../backend/Dockerfile)、[frontend/Dockerfile](../../frontend/Dockerfile) |
| 参照 | [yadopera-v04-summary.md](../Summary/yadopera-v04-summary.md)、[やどぺら v0.3 アーキテクチャ設計書](../Architecture/やどぺら_v0.3_アーキテクチャ設計書.md)（DNS・CORS 時） |
| 手元のみ | [RENDER_ENV_INVENTORY](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/RENDER_ENV_INVENTORY.md) |

### 開始時に Cursor が実行してよいコマンド（鮮度確認）

```bash
cd /Users/kurinobu/projects/yadopera
git status -sb
git log --oneline -3 origin/develop
git log --oneline -3 origin/main
git rev-list --left-right --count origin/main...origin/develop
```

---

## Phase 3 の位置づけ

| やる | やらない（後続 Phase） |
|------|------------------------|
| Dokploy に **staging** Backend / Frontend を追加 | ダンプ SCP・リストア（**Phase 4**） |
| Git 連携（`develop`）・環境変数・ビルド・Deploy | ムームー DNS 本番切替（**Phase 5**） |
| `GET /api/v1/health` が **200**（DB 空でも可） | Stripe Webhook URL 本番切替（**Phase 5**） |
| `DATABASE_URL` / `REDIS_URL` を **ConoHa 内**の Internal 向けに設定 | InfluBerry 等（**Phase 6**） |

**番号は 3 → 4 のまま。** 技術的には **Phase 4 を Phase 5 の直前まで**に終わらせる（親引き継ぎ §実施順の注意）。

---

## Phase 2 完了状態（次会話が使う事実）

### VPS / ConoHa

| 項目 | 値 |
|------|-----|
| IP | `160.251.199.237` |
| OS | Ubuntu 22.04.3 LTS |
| ネームタグ | `air-edison_VPS` |
| SSH | `ssh root@160.251.199.237` |
| セキュリティグループ | `IPv4v6-SSH` + `IPv4v6-Web` + **`air-edison-admin-3000`** |

### Dokploy

| 項目 | 値 |
|------|-----|
| URL | `http://160.251.199.237:3000` |
| バージョン | **v0.29.4** |
| 左メニュー | **Databases なし** → **Projects** → **+ Create Service** |

### 既存 Dokploy プロジェクト（インフラ）

| 種別 | Name（表示） | App / Service ID（例） | イメージ | REPLICAS |
|------|--------------|------------------------|----------|----------|
| Project | **`air-edison`** | — | — | — |
| Environment | **`production`** | — | — | — |
| Postgres | `air-edison-postgres` | `airedison-airedisonpostgres-wsxrdk` | `pgvector/pgvector:pg18` | 1/1 |
| Redis | `air-edison-redis` | `airedison-airedisonredis-eolvti` | `redis:7` | 1/1 |

- PG18 ボリュームマウント: **`/var/lib/postgresql`**（`/data` ではない）  
- `vector` 拡張: **0.8.2** 確認済み  
- Redis: **パスワードあり**。`redis-cli PING` は **`-a` 必須**

**接続情報（パスワード・Internal URL）**: Dokploy 各サービス → **General → Internal** から **Git 外**にコピー。本書には書かない。

### 接続 URL の組み立て（staging・Phase 3 用・DB 名は `postgres` のままで可）

Dokploy **Internal Host** をそのまま使う（例・実際の値は画面で確認）:

```text
# Backend 環境変数（asyncpg）
DATABASE_URL=postgresql+asyncpg://postgres:＜POSTGRES_PASSWORD＞@airedison-airedisonpostgres-wsxrdk:5432/postgres

# Redis（パスワードあり）
REDIS_URL=redis://:＜REDIS_PASSWORD＞@airedison-airedisonredis-eolvti:6379/0
```

Phase 4 で DB 名を `yadopera_staging` にしたあと `DATABASE_URL` を差し替える。

---

## ナビ原則（Phase 2 の教訓を継承）

1. **ユーザーのスクショ・ターミナル出力が正** — 推測で UI を書かない  
2. **プレースホルダ禁止** — `$(docker ps ...)` や Internal の実値でコピペ可能に  
3. **Phase 完了の宣言の前に** 全 Step の説明（必須 / 任意 / 後回し）を書く  
4. **1 台集約** — インフラは `air-edison`。アプリ名だけの専用 SG は作らない  
5. Phase 2 手順ミス一覧: [Phase2 §本セッションの記録](./20260521_Phase2_ConoHa初期設定_実施手順.md#本セッションの記録2026-05-21手順ナビの教訓)

---

## 事前準備チェックリスト（Phase 3 開始前）

- [ ] Phase 2 完了（Postgres `1/1`、Redis `PONG`）
- [ ] Dokploy **Internal** から Postgres / Redis のホスト・パスワードを **Git 外**にメモ
- [ ] GitHub リポジトリ `yadopera` へ push 権限（Dokploy 連携用）
- [ ] `develop` ブランチがデプロイ元（staging）
- [ ] 手元に API キー候補: `OPENAI_API_KEY`、Brevo、Stripe（本番 Stripe は **ダッシュボード再取得** — [RENDER_ENV_INVENTORY](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/RENDER_ENV_INVENTORY.md) 参照）
- [ ] 正本: [yadopera-v04-summary.md](../Summary/yadopera-v04-summary.md)

---

## 実施順序

```
Step 0  事前メモ・方針確認（本書・.env.example） 完了
Step 1  staging Backend（Application）— develop・health 完了
Step 2  staging Frontend（Application または static ビルド）— develop
Step 3  ドメイン・HTTPS（任意・Phase 5 前でも staging 用に可）
Step 4  動作確認（/api/v1/health・ビルド成功）
Step 5  本番用 Application は Phase 5 直前でも可（main・ドメイン確定後）
```

---

## Step 0: 方針・参照ファイル

| 用途 | パス |
|------|------|
| 環境変数テンプレ | [backend/.env.example](../../backend/.env.example) |
| 旧 staging 定義（参考） | [render.yaml](../../render.yaml) |
| Backend イメージ | [backend/Dockerfile](../../backend/Dockerfile) |
| Frontend イメージ | [frontend/Dockerfile](../../frontend/Dockerfile)（**dev 用** — 本番は `vite build` 要検討） |
| アーキテクチャ | [やどぺら v0.3 アーキテクチャ設計書](../Architecture/やどぺら_v0.3_アーキテクチャ設計書.md) |

**Frontend 注意**: 現行 [frontend/Dockerfile](../../frontend/Dockerfile) は `npm run dev`。**staging では Dokploy でビルドコマンド `npm run build` + static 配信**、または Dockerfile 修正が必要な場合あり。初回 Deploy で失敗したら Logs を共有。

---

## Step 1: staging Backend（Dokploy Application）

**場所**: ブラウザ Dokploy → **Projects** → **air-edison** → **production**

1. **+ Create Service** → **Application**（Database ではない）
2. 例:

| 項目 | 推奨値 |
|------|--------|
| Name | `yadopera-backend-staging` |
| Source | GitHub → リポジトリ `yadopera` |
| Branch | **`develop`** |
| Build / Dockerfile | `backend/Dockerfile`（Context: `backend` またはリポジトリ root — 画面で確認） |
| Start command（あれば） | `uvicorn app.main:app --host 0.0.0.0 --port 8000`（Dockerfile と同じなら省略可） |

3. **Environment**（値は Internal・手元メモから。以下はキー一覧）:

| キー | 備考 |
|------|------|
| `DATABASE_URL` | 上記 asyncpg 形式・ホストは Postgres Internal |
| `REDIS_URL` | Redis Internal・**パスワード込み** |
| `SECRET_KEY` | 新規生成（32文字以上） |
| `ENVIRONMENT` | `staging` |
| `DEBUG` | `False` |
| `CORS_ORIGINS` | 後で Frontend URL が決まったら更新（仮: `http://160.251.199.237` や staging ドメイン） |
| `FRONTEND_URL` | 同上 |
| `OPENAI_API_KEY` | 手元 |
| `BREVO_*` | 必要なら |
| `STRIPE_*` | staging 用キー（あれば） |

4. **Deploy 前コマンド**（Render と同様）: `alembic upgrade head` が Dokploy の Pre-deploy / Build で設定できるか画面で確認

5. **Deploy** → **Confirm** → **Logs** でビルド成功

6. **確認**（ドメイン or 割当ポートが決まったら）: `GET /api/v1/health` → **200**

### Step 1 完了チェックリスト（2026-05-21 実績）

- [x] Application `yadopera-backend-staging` 作成・Provider（Github / develop）
- [x] Domains: `160.251.199.237` : **8000**
- [x] Environment Settings（ランタイム）必須キー設定
- [x] Deploy 成功・Swarm **1/1**
- [x] health **200**（上記 curl）
- [x] `CORS_ORIGINS` / `FRONTEND_URL` — **2026-05-21**（Step 2-A・`http://160.251.199.237`）
- [ ] Pre-deploy `alembic upgrade head` — **要確認**

**次**: [Step 2: staging Frontend](#step-2-staging-frontend)

SSH でサービス確認（任意）:

```bash
docker service ls | grep -i yadopera
docker service ls | grep airedison
```

---

## Step 2: staging Frontend

**前提**: [Step 1](#step-1-staging-backenddokploy-application) 完了。実施順の詳細は [次会話引き継ぎ §Step 2 の実施順](#step-2-の実施順次会話はここから画面単位)（**2-A → 2-G**）。

### 2-A: Backend CORS（Frontend の前）

`yadopera-backend-staging` → **Environment** → **Environment Settings**（行番号付き・**上部**）:

```text
CORS_ORIGINS=http://160.251.199.237
FRONTEND_URL=http://160.251.199.237
```

→ **Save** → **Deploy** → health **200** 再確認。

### 2-B〜2-G: Frontend Application

| Step | 画面 | 値 |
|------|------|-----|
| 2-B | Create Service → Application | Name: `yadopera-frontend-staging` |
| 2-C | General → Provider | Github・`yadopera`・**`develop`**・Build Path `/` |
| 2-D | Build Type | **Static** 推奨。Build: `cd frontend && npm ci && npm run build`・Publish: `dist` または `frontend/dist`（画面に合わせる） |
| 2-E | Environment Settings（上部） | `VITE_API_BASE_URL=http://160.251.199.237`・`VITE_ENVIRONMENT=staging` |
| 2-F | Domains | Host `160.251.199.237`・port **80**・HTTP |
| 2-G | Deploy | **View** でビルド成功 → ブラウザで `http://160.251.199.237` |

参照: [render.yaml](../../render.yaml) の `yadopera-frontend-staging`（static・`npx vite build`・`dist`）。

**注意**: [frontend/Dockerfile](../../frontend/Dockerfile) は **`npm run dev` のみ** — staging 本番相当は Static ビルド。Dockerfile デプロイは使わない。

### Step 2 完了チェックリスト

- [x] 2-A: Backend `CORS_ORIGINS` / `FRONTEND_URL` 追加・再 Deploy・health 200 — **2026-05-21**（Deployments **Done**・commit `955cccb`・curl **200** `healthy`)
- [x] 2-B: Application `yadopera-frontend-staging` 作成 — **2026-05-21**
- [x] 2-C: Provider（Github / `Dokploy-air-edison` / `yadopera` / `develop` / `/`）Save — **2026-05-21**
- [x] 2-D: Build Type **Nixpacks**・Publish **`dist`**・Build Path **`frontend`**
- [x] 2-E: `VITE_API_BASE_URL`・`VITE_ENVIRONMENT` Save
- [x] 2-F: Domains `160.251.199.237` : **80** HTTP Path `/`
- [x] 2-G: Nixpacks Deploy **Done**（`COPY dist`・`npm run build` 成功）
- [x] Backend Domains Path **`/api`**
- [ ] **2-H SPA フォールバック** — `curl /admin/login` が **200 + index.html**（現状 **nginx 404**）
- [ ] ブラウザ `http://160.251.199.237/admin/login` — **管理ログイン画面**（nginx 404 ではない）
- [ ] Step 2 完了後: [Phase 3 完了チェックリスト](#phase-3-完了チェックリスト) を `[x]`

---

## Step 3: ドメイン（任意・Phase 5 と兼用可）

| 用途 | 例 |
|------|-----|
| staging API | `staging-api.yadopera.com` |
| staging App | `staging-app.yadopera.com` |

ムームー DNS は **Phase 5** で本番とまとめて切替してもよい。Phase 3 は **IP:ポート or Dokploy 付与 URL** だけでも可。

---

## Step 4: Phase 3 完了確認

| # | 確認 |
|---|------|
| 1 | staging Backend **Deploy 成功**（Logs に crash なし） |
| 2 | `curl -sS -o /dev/null -w "%{http_code}" -H "Host: 160.251.199.237" "http://160.251.199.237/api/v1/health"` → **200** |
| 3 | staging Frontend **ビルド成功**（画面表示は最低限） |
| 4 | `DATABASE_URL` が ConoHa Internal の Postgres を向いている |
| 5 | **施設データ・ログイン本番確認は Phase 4 後** |

---

## Phase 3 完了チェックリスト

**全体**: ⏳ **進行中**（2026-05-21 時点で Step 1 のみ完了）

- [x] Step 0: Internal URL・パスワードメモ（セッションで実施・Git 外）— [事前準備](#事前準備チェックリストphase-3-開始前) の細目は未チェックでも可
- [x] Step 1: `yadopera-backend-staging` Deploy・health 200 — **2026-05-21 完了**（[実績](#step-1-完了チェックリスト2026-05-21-実績)）
- [ ] Step 2: `yadopera-frontend-staging` — **未完了**（`/admin/login` が nginx SPA 404）
- [ ] Step 3: ドメイン（任意・未でも Phase 3 可）
- [ ] 環境変数一覧を Git 外に保管

**次**: **Phase 4**（ダンプ SCP・`yadopera` / `yadopera_staging` 作成・リストア）→ **Phase 5**（DNS・Stripe・本番）

---

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-05-21 | 初版（Phase 3 開始用・Phase 2 完了状態込み） |
| 2026-05-21 | §コードベース・Git・Docker スナップショット追加 |
| 2026-05-21 | **Step 1 完了報告**・§本セッションの記録・Step 1 実績チェックリスト・全体は未完了を明記 |
| 2026-05-21 | **次会話引き継ぎ（Step 2 即開始）**・§Step 2 を 2-A〜2-G に展開 |
| 2026-05-21 | ファクトチェック: Step 0 チェックリスト整合・Step 4 curl プレースホルダ削除・§検証メモ追記 |
| 2026-05-21 | **Step 2-A 完了**（CORS 追加・再 Deploy Done・health 200）— 2-B〜G 着手 |
| 2026-05-21 | **Step 2 実質完了**（Nixpacks Done・Backend Path `/api`・`curl /` YadOPERA HTML）— Static/nginx-only 失敗・Build Path `frontend` で解消 |
