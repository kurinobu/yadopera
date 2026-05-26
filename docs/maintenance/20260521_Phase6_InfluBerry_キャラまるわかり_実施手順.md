# Phase 6: InfluBerry・キャラまるわかり — 実施手順（Dokploy 実装）

**作成日**: 2026-05-24  
**親文書**: [ConoHa VPS 移転統合 引き継ぎ](./20260521_ConoHaVPS_移転統合_引き継ぎ.md)  
**前提**: [Phase 5 YadOPERA サービス再開](./20260521_Phase5_YadOPERAサービス再開_実施手順.md) **完了**（2026-05-24）

**Phase 7**（DNS・外部公開・品質ゲート）は **本 Phase 6 完了後**。本書は **ConoHa 上でのビルド・起動・DB 接続** まで。

---

## 次会話引き継ぎ（Phase 7 開始・2026-05-26）

### Phase 6 完了宣言（事実）

| 項目 | 状態 |
|------|------|
| YadOPERA 本番・ステージング | ✅ ConoHa 稼働継続（Phase 5 完了・Phase 6 全期間 200 維持） |
| InfluBerry staging | ✅ Dokploy 稼働・`staging-influberry.local` 暫定ホストで 200 取得（commit `f6f8725`・2026-05-25） |
| キャラまるわかり (motivation_app) staging | ✅ Dokploy 稼働・`staging-motivation.local` 暫定ホストで 200 + 正規 title 取得（commit `604aefa`・Deploy 41s・2026-05-26） |
| Phase 6 完了証跡 | [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md) ／ [20260525_phase6_influberry_partial.md](../evidence/20260525_phase6_influberry_partial.md) |
| 事前調査・訂正履歴 | [20260525_motivation_app_事前調査_調査分析報告書.md](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md)（訂正版・C-1/C-2/C-3） |
| 要約定義書 | [yadopera-v04-summary.md](../Summary/yadopera-v04-summary.md) v4.1.0 |
| Phase 7 で触らない（凍結） | YadOPERA api/app の Dokploy env／Stripe Webhook／Brevo Authorized IPs／influberry-staging の env／motivation-app-staging の env |

### 次会話に貼るプロンプト（推奨・このままコピー・2026-05-26 19:25 Phase 7 開始版）

```
Phase 7（DNS 本ドメイン化・HTTPS 化）を引き継ぎ再開します。
正本: docs/maintenance/20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md
親:   docs/maintenance/20260521_ConoHaVPS_移転統合_引き継ぎ.md §Phase 7
前提: docs/evidence/20260526_phase6_motivation_app_complete.md（Phase 6 完了）

正本「次会話引き継ぎ」§現在地点（Phase 7 着手前）から 1 Step ずつナビしてください。
最初に 7-A の Owner 確認（GitHub Visibility / ムームー DNS 現状 / Brevo 認可 IP /
C-1・C-2・C-3 ローテーション要否）を Owner と読み合わせてください。
憶測禁止。コピペ用ブロックは 1 つのコード欄にまとめる。Mac≠VPS。git は Mac のみ。
YadOPERA api/app・Stripe・既存 Brevo・既存 Dokploy env は触らない。
Phase 6 は完了済み（暫定 hostname 'staging-influberry.local' / 'staging-motivation.local'
で疎通確認済）。
```

### 旧プロンプト（参考保存）

<details>
<summary>2026-05-25 17:02 / 6-D 開始版</summary>

```
Phase 6（InfluBerry・キャラまるわかり実装）を引き継ぎ再開します。
正本: docs/maintenance/20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md
証跡: docs/evidence/20260525_phase6_influberry_partial.md
6-A〜6-E（InfluBerry 部分・staging-influberry.local で疎通確認済）まで完了。
次の作業は 6-D（motivation_app）の事前確認から開始してください。
（後略）
```

</details>

<details>
<summary>2026-05-25 16:40 / 6-E ステップ 2 解消用</summary>

```
Phase 6（InfluBerry・キャラまるわかり実装）を引き継ぎ再開します。
（後略）
```

</details>

<details>
<summary>2026-05-24 開始時</summary>

```
Phase 6（InfluBerry・キャラまるわかり実装）を開始します。
（後略）
```

</details>

### 現在地点（2026-05-26 19:08 時点・事実のみ・本会話で記録）

| Step | 状態 | 根拠 |
|------|------|------|
| **6-A** | ✅ | YadOPERA health `healthy`・両 DB 存在確認・両リポジトリ Dockerfile **無し**（実測） |
| **6-B** | ✅ | `influberry_staging` `public` **9 テーブル**・`motivation_app` `public` **9 テーブル**（`\dt` 実測） |
| **6-C-0** | ✅ | `influberry_v2` に Dockerfile 追加（initial: `c3eb3f5`・stage-2 修正: `f6f8725`）を `staging` に push |
| **6-C-1** | ✅ | GitHub App `Dokploy-air-edison` に `influberry` 追加・Dokploy で `influberry-staging` Application 作成・Provider Github/staging/Build Path `/`・Build Type Dockerfile（Context `.`）・Domain `Host:160.251.199.237 Port:5001 HTTP /`（後に `staging-influberry.local` に変更） |
| **6-C-2** | ✅ | Environment Settings 保存（`DATABASE_URL`/`SECRET_KEY`/`FLASK_ENV=staging`/`PORT=5001`/`FRONTEND_URL`/TIKTOK 3 行） |
| **6-E ステップ 1** | ✅ | Deploy **Done**（29s・commit `f6f8725`）・Swarm `airedison-influberrystaging-qqn2hl` **1/1** |
| **6-E ステップ 2（InfluBerry 疎通）** | ✅ | Domains 画面確認で `yadopera-frontend-staging` / `yadopera-frontend-production` が `Host:160.251.199.237` を保持していたことを確認 → **InfluBerry 側のみ** Host を `staging-influberry.local` に変更（YadOPERA 無変更）→ Mac から `curl -H "Host: staging-influberry.local"` で `<title>InfluBerry - インフルエンサー案件管理・請求書自動生成SaaS</title>` 取得・`/api/auth/me` **401**（認証ミドルウェア応答）／同時に `api.yadopera.com` health `healthy`・`app.yadopera.com` 200・`staging-app.yadopera.com` 200 維持（2026-05-25 17:00 実測） |
| **6-D-0** | ✅ | motivation_app 事前調査完了・[調査分析報告書](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md)（訂正版・C-1/C-2/C-3 全件記録）作成 |
| **6-D-1** | ✅ | `/Users/kurinobu/motivation_app/Dockerfile` 新規（Python 3.12.6-slim-bookworm 単一ステージ・PORT 5002・gunicorn 1 worker / 4 threads / 120s） |
| **6-D-3** | ✅ | Mac から `kurinobu/motivation_app` `main` に push・commit **`604aefa`**（full: `604aefa88851478911589aa5a449fe133d99e7fc`）・fast-forward `05dd682..604aefa` |
| **6-D-4** | ✅ | GitHub App `Dokploy-air-edison` に `kurinobu/motivation_app` Repository access 追加（既存 2 リポジトリ維持） |
| **6-D-5** | ✅ | Dokploy `air-edison/production` に **`motivation-app-staging`** 新規作成（Swarm `airedison-motivationappstaging-rex1my`）・Provider Github/`kurinobu/motivation_app`/`main`・Build Type Dockerfile・Domain `staging-motivation.local`/Port 5002/HTTP/Cert none |
| **6-D-6** | ✅ | Environment Settings **17 行** Save Successful（dotenv パーサー版テンプレで生成・C-3 `ADMIN_PASSWORD_HASH` は意図的未設定で Render 時代と同じ fallback 動作） |
| **6-D-8** | ✅ | Deploy **Done**・所要 **41 秒**・commit `604aefa88851478911589aa5a449fe133d99e7fc` |
| **6-D-9** | ✅ | Mac curl で **YadOPERA health `healthy` / app 200 / staging-app 200 / InfluBerry 200 + title / motivation_app 200 + `<title>キャラまるわかり - 3つの心理学理論で自己診断</title>`** 取得（2026-05-26 19:07 実測） |
| **6-D-10** | ✅ | 証跡 [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md) 作成 |
| **6-F** | ✅ | 本書チェックリスト全 `[x]`・親引き継ぎ Phase 6 ✅ 化 |
| **Phase 7** | 未 | DNS・HTTPS 本番ドメイン（別 Phase）／`influberry-staging` Domain Host を `staging.influberry.jp` に・`motivation-app-staging` Domain Host を本ドメインに切替予定 |

### 次会話の最初の作業

**Phase 7 着手前確認**（読み取りのみ・YadOPERA / InfluBerry / motivation_app 無影響）:

1. ムームードメイン現状（Owner 確認）: `influberry.jp` / `staging.influberry.jp` の現向き先・motivation_app 本ドメイン所有有無
2. GitHub `kurinobu/motivation_app` Visibility（Public/Private）→ C-2 Brevo キー ローテーション要否判断
3. Brevo Authorized IPs（YadOPERA で `160.251.199.237` 追加済を流用可・追加作業不要）
4. C-1/C-2/C-3 のローテーション要否を Owner と読み合わせ → Phase 7 / Phase 8 / 別 Phase に振り分け
5. Phase 7 専用手順書 `202605xx_Phase7_DNS本ドメイン_実施手順.md` 新規作成方針合意

**やらないこと**: YadOPERA の Domains 編集・`yadopera-backend-*` の env 変更・本番 Stripe / Brevo 操作・influberry-staging / motivation-app-staging の env / Build 設定変更（Phase 7 完了まで凍結）

### 次会話で Cursor が読む順

1. **本節**  
2. [§6-A 事前確認](#step-6-a-事前確認)  
3. [§6-B Phase 4-E リストア](#step-6-b-phase-4-e-リストア未実施なら先に)（未実施なら）  
4. [§6-C InfluBerry](#step-6-c-influberry-dokploy) から順にナビ  
5. [§Phase 6 完了チェックリスト](#phase-6-完了チェックリスト)

**やらないこと**: YadOPERA 本番 DNS / env の変更・Phase 8 Render 解約・PublishDone（Phase 9）

### 確定値（コピペ用・秘密なし）

| 項目 | 値 |
|------|-----|
| VPS IP | `160.251.199.237` |
| SSH | `ssh root@160.251.199.237` |
| Dokploy | `http://160.251.199.237:3000` |
| Project / Environment | **`air-edison`** / **`production`** |
| Postgres Swarm 名（Phase 4 実績） | `airedison-airedisonpostgres-wsxrdk` |
| DB 名（InfluBerry） | **`influberry_staging`** |
| DB 名（キャラまるわかり） | **`motivation_app`** |
| Brevo Authorized IPs | **`160.251.199.237`** 追加済み（Phase 5・2026-05-24） |
| YadOPERA 本番 | `https://api.yadopera.com` / `https://app.yadopera.com`（**変更しない**） |

### リポジトリ（Mac 手元・git は Mac のみ）

| サービス | パス | GitHub（`origin` 実績） |
|----------|------|-------------------------|
| InfluBerry | `/Users/kurinobu/projects/influberry_v2` | `https://github.com/kurinobu/influberry.git` |
| キャラまるわかり | `/Users/kurinobu/motivation_app` | `https://github.com/kurinobu/motivation_app.git` |

### ダンプ（Phase 0・Git 外）

| DB | ファイル（`railway-dumps/`） |
|----|------------------------------|
| `influberry_staging` | `influberry_influberry-staging_20260521_120240.dump` |
| `motivation_app` | `influberry_motivation_app_db_20260521_120240.dump` |

パス: `/Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/railway-dumps/`

### コードベース事実（2026-05-24 確認・憶測なし）

| 項目 | InfluBerry | motivation_app |
|------|------------|----------------|
| 構成 | Flask + Vue（`frontend/dist` → `app/static/`） | Flask モノリス（Jinja） |
| **Dockerfile** | **リポジトリ内に無し** | **リポジトリ内に無し** |
| 既存デプロイ定義 | `render.yaml`（`gunicorn wsgi:app`・health `/api/auth/me`） | `render.yaml` 無し |
| 起動（Render 実績） | `gunicorn wsgi:app` | `wsgi.py` あり・gunicorn は `requirements.txt` に記載 |
| 主要 env | `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV`, `FRONTEND_URL`, TikTok OAuth 3 キー | `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV`, `BREVO_*`, `ANTHROPIC_*`, `BASE_URL` 等 |

**Phase 6 で必要になりうる作業（未着手）**: 各リポジトリに **Dockerfile 新規作成**、または Dokploy **Nixpacks** 等 — **次会話でリポジトリと Dokploy 画面を確認してから** 1 方式に決める（憶測で書かない）。

### InfluBerry ドメイン（既存 Render 文書・`docs/phase3_staging_deployment_preparation.md`）

| 環境 | URL（Render 時代の記載） |
|------|--------------------------|
| 本番 | `https://influberry.jp` |
| staging | `https://staging.influberry.jp` |

**Phase 6** では ConoHa 上の **起動・DB 接続** を優先。**DNS 切替は Phase 7**（ムームー画面を見てから記録）。

---

## Phase 5 完了状態（Phase 6 の前提）

| 項目 | 状態 |
|------|------|
| YadOPERA 本番 | ✅ `api` / `app`・Stripe Webhook・5-G ログイン |
| Postgres on VPS | ✅ `yadopera` / `yadopera_staging` リストア済 |
| `influberry_staging` / `motivation_app` | ✅ **DB 作成（4-B）**・⏳ **データリストア（4-E）未** |
| 証跡 | [20260524_conoha_phase5_service_resume.md](../evidence/20260524_conoha_phase5_service_resume.md) |

---

## 実施順序（概要）

```
6-A  事前確認（DB 状態・Dokploy・リポジトリ・秘密情報の所在）
6-B  Phase 4-E リストア（未実施なら先に）
6-C  InfluBerry — Dockerfile/ビルド方針 → Dokploy Application → env → Deploy
6-D  motivation_app — 同上
6-E  疎通（health または既知エンドポイント・IP 暫定可）
6-F  証跡・チェックリスト → Phase 7 へ
```

**目安時間**: 3〜6 時間（Dockerfile 新規作成を含む場合は上限寄り）

---

## Step 6-A: 事前確認

**Mac または VPS**（読み取りのみ）。

### 1. YadOPERA 本番が壊れていないこと

```bash
curl -sS "https://api.yadopera.com/api/v1/health"
curl -sS -I "https://app.yadopera.com/" | head -3
```

期待: health `healthy`・app **200**

### 2. VPS — DB 存在確認（SSH 後・1 ブロック）

```bash
PG=$(docker ps --format '{{.Names}}' | grep 'airedison-airedisonpostgres-wsxrdk' | head -1)
echo "PG=$PG"
docker exec -i "$PG" psql -U postgres -d postgres -c "\l" | grep -E 'influberry_staging|motivation_app'
```

### 3. Dokploy 画面

`http://160.251.199.237:3000` → **air-edison** / **production** — 既存 Application 一覧を確認（InfluBerry / motivation 用が **無い** 状態から開始）。

### 4. 報告（秘密なし）

- `\l` に `influberry_staging` / `motivation_app` があるか  
- 4-E リストア済みか不明なら **6-B へ**  
- InfluBerry / motivation の **GitHub 連携**に使う Dokploy Provider アカウント名（スクショ）

---

## Step 6-B: Phase 4-E リストア（未実施なら先に）

**正本コマンド**: [Phase4 §Step 4-E](./20260521_Phase4_DBリストア_実施手順.md#step-4-e-influberry--motivation_app任意同セッション可)

**Mac** — ダンプ SCP（未配置なら）:

```bash
DUMPS=/Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/railway-dumps
VPS=root@160.251.199.237
scp "$DUMPS/influberry_influberry-staging_20260521_120240.dump" "$VPS:/tmp/"
scp "$DUMPS/influberry_motivation_app_db_20260521_120240.dump" "$VPS:/tmp/"
```

**VPS** — リストア（Phase 4 文書どおり）:

```bash
PG=$(docker ps --format '{{.Names}}' | grep 'airedison-airedisonpostgres-wsxrdk' | head -1)
docker cp /tmp/influberry_influberry-staging_20260521_120240.dump "$PG:/tmp/influberry_staging.dump"
docker exec -i "$PG" pg_restore -U postgres -d influberry_staging --no-owner --no-acl /tmp/influberry_staging.dump

docker cp /tmp/influberry_motivation_app_db_20260521_120240.dump "$PG:/tmp/motivation_app.dump"
docker exec -i "$PG" pg_restore -U postgres -d motivation_app --no-owner --no-acl /tmp/motivation_app.dump
```

**確認**: エラー行の有無をログで記録。件数確認 SQL は **次会話でテーブル名をリポジトリ/DB から確定してから**（憶測で `SELECT` を書かない）。

---

## Step 6-C: InfluBerry（Dokploy）

### 6-C-0: ビルド方針（未決 — 次会話で確定）

**事実**: `influberry_v2` に **Dockerfile 無し**。`render.yaml` の build は次の順:

1. `pip install -r requirements.txt`
2. `cd frontend && npm install && npm run build`
3. `cp -r frontend/dist/* app/static/`

**起動**: `gunicorn wsgi:app`  
**health（Render）**: `/api/auth/me`

→ Phase 6 では **Dockerfile 追加（Mac で git push）** または Dokploy ビルド設定を **画面と render.yaml を見て** 決める。

### 6-C-1: Dokploy Application（方針確定後）

| 項目 | 想定（確定前・参考） |
|------|----------------------|
| Name | `influberry-staging` 等 — **画面で命名** |
| Branch | `staging`（Render staging 実績）または Owner 指定 |
| Repository | `kurinobu/influberry` |
| Port | Render は `PORT` 注入 — **コンテナ Port は Deploy ログで確認** |

### 6-C-2: Environment（ランタイム・秘密は Git 外）

`render.yaml` / `config.py` より **キー名**:

- `DATABASE_URL` — Internal ホスト・DB **`influberry_staging`**（Phase 4-F と同型で DB 名のみ差し替え）
- `SECRET_KEY`
- `FLASK_ENV`
- `FRONTEND_URL` — Phase 6 暫定は IP または未確定ドメイン（**Phase 7 前に確定**）
- `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REDIRECT_URI` — 手元 `.env` または Render 退避

**DATABASE_URL 形式（Flask/SQLAlchemy・プレースホルダ）**:

```text
postgresql://postgres:＜POSTGRES_PASSWORD＞@airedison-airedisonpostgres-wsxrdk:5432/influberry_staging
```

※ YadOPERA Backend の `postgresql+asyncpg://` とは **ドライバ prefix が異なる**可能性 — **接続エラー時はリポジトリの `DATABASE_URL` 実例を正**とする。

---

## Step 6-D: motivation_app（Dokploy）

**Owner 方針（2026-05-25 17:30 確定）**: **Render と同じ状態で載せ替え／動けば OK ／問題は証跡に残す／本 Phase でコードは触らない**  
**事前調査報告書**: [20260525_motivation_app_事前調査_調査分析報告書.md](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md) ← **6-D 着手前に必読**

### 6-D 重大事項（要 Owner 認識・2026-05-26 訂正版）

`motivation_app` リポジトリには以下のハードコード機密情報が存在することが事前調査で判明（詳細は[調査報告書 §0 訂正履歴 / §4](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md)）:

| ID | 場所 | 内容 | Phase 6 対処 |
|----|------|------|--------------|
| C-1 | `app.py:50-52` | 旧 Render DB の DATABASE_URL（パスワード入り）ハードコード フォールバック | **コード修正なし**・Dokploy `DATABASE_URL` を必ず設定して到達回避 |
| C-2 | `blueprints/mail/services.py:457,554` | Brevo API キー実値ハードコード フォールバック | **コード修正なし**・Dokploy `BREVO_API_KEY` を必ず設定して到達回避／Phase 7+ で Owner ローテーション |
| **C-3** | `app.py:138` | 管理者パスワード `'kurikuri'` のコード固定 (`generate_password_hash('kurikuri')`) | **コード修正なし**・Dokploy `ADMIN_PASSWORD_HASH` を**意図的に未設定**にして Render 時代と同じ fallback 動作を維持 |

→ **Dokploy Environment Settings で §6-D-6 の必須キー（A 分類 15 + 新規生成 SECRET_KEY + PORT = 17 行）を漏れなく投入**することが Phase 6 の品質ゲート。

### Sub-Step 一覧（実行順序・実績反映版）

| Sub-Step | 内容 | 影響範囲 | 実績 |
|----------|------|----------|------|
| **6-D-1** | Dockerfile 作成（Mac ローカル・push なし） | Mac | ✅ 16 行 |
| **6-D-2** | Owner が Dockerfile 内容をレビュー → 承認 | — | ✅ |
| **6-D-3** | Mac から `git add Dockerfile && git commit && git push origin main` | GitHub `kurinobu/motivation_app` のみ | ✅ commit `604aefa` |
| **6-D-4** | Dokploy GitHub App `Dokploy-air-edison` に `motivation_app` リポジトリを Repository access に追加 | Dokploy 設定（YadOPERA / InfluBerry 無影響） | ✅ |
| **6-D-5** | Dokploy Application `motivation-app-staging` を新規作成（Provider GitHub / Branch `main` / Build Path `/` / Build Type Dockerfile・**Domain も同画面で `staging-motivation.local` / Port 5002 / HTTP / Cert none を Save**） | Dokploy 新規 | ✅ Swarm `airedison-motivationappstaging-rex1my` |
| **6-D-6** | Environment Settings に **dotenv パーサー版テンプレ**で生成した 17 行を Save（**§6-D-6 必須キー一覧** 参照） | Dokploy 設定 | ✅ Save Successful |
| **6-D-8** | Deploy 実行 → Deploy ログ確認 | Dokploy / VPS | ✅ Done / 41 秒 |
| **6-D-9** | Mac から疎通確認（YadOPERA 全 200 維持／InfluBerry 全 200 維持／motivation_app `Host:` 偽装で 200 + トップ HTML） | Mac curl | ✅ 全期待値クリア |
| **6-D-10** | 証跡 `docs/evidence/20260526_phase6_motivation_app_complete.md` 作成・Phase 6 完了チェックリスト更新 | docs | ✅ 本書 |

### 6-D-1: Dockerfile 内容（InfluBerry 同流派・モノリス Flask 用）

**配置**: `/Users/kurinobu/motivation_app/Dockerfile`

```dockerfile
FROM python:3.12.6-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data

ENV PORT=5002

EXPOSE 5002

CMD ["sh", "-c", "gunicorn wsgi:app --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120"]
```

**設計根拠**（事前調査 §3.2〜3.3 に基づく・憶測なし）:

| 行 | 根拠 |
|----|------|
| `FROM python:3.12.6-slim-bookworm` | InfluBerry と統一（大原則 3）／`requirements.txt` が wheel のみで完結 |
| マルチステージ無し | フロントビルド不要（Jinja のみ・大原則 2 シンプル） |
| apt-get install 無し | `psycopg2-binary` / `Pillow` / `reportlab` は wheel 完備（事前調査で確認） |
| `mkdir -p data` | `DATA_PATH` 既定が `data`・コンテナ起動前に作成 |
| `ENV PORT=5002` | InfluBerry が 5001 使用・**衝突回避**で 5002 |
| `gunicorn wsgi:app` | `wsgi.py` の `from app import app` を読む（Render 実績と同等） |
| `--workers 1` | APScheduler 多重起動回避（事前調査 §5） |
| `--threads 4 --timeout 120` | reportlab PDF / Brevo API 通信のため |

### 6-D-3: コミットメッセージ（推奨）

```
Add Dockerfile for ConoHa Dokploy deploy (main)

- Python 3.12.6-slim-bookworm single stage
- gunicorn wsgi:app, 1 worker / 4 threads (APScheduler safe)
- PORT 5002 (InfluBerry uses 5001)
- No code changes - Render と同じ状態で Docker 化のみ
```

### 6-D-6: Environment Settings 必須キー一覧（**dotenv パーサー版・2026-05-26 訂正版**）

#### 6-D-6-a: テンプレ生成スクリプト（Mac で 1 ブロック実行）

`.env` 全件突合と訂正済み env キー一覧（[調査報告書 §0.3](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md#03-訂正後の事実実測根拠付き初版を上書きせず本セクションに記載)）に基づく。bash grep + echo 方式は `.env` の `# コメント` 行・クォート (`"..."`) を破損させるリスクがあるため、**`motivation_app` 自身が起動時に使う `python-dotenv==1.0.1` の `dotenv_values()` で同じパースを行う**（大原則 1 根本解決・同一化）。

```bash
echo "=== Dokploy paste-ready (17 lines expected) ==="
python3 <<'PY_EOF'
import secrets
from dotenv import dotenv_values
env = dotenv_values('/Users/kurinobu/motivation_app/.env')
KEYS_FROM_ENV = [
    'BREVO_API_KEY','BREVO_SENDER_EMAIL','BREVO_SENDER_NAME',
    'FROM_EMAIL','FROM_NAME','ANTHROPIC_API_KEY','ANTHROPIC_MODEL',
    'USE_MOCK_API','API_TRAFFIC_PERCENTAGE',
    'CLAUDE_MAX_RETRIES','CLAUDE_RETRY_DELAY_BASE','CLAUDE_TIMEOUT_SECONDS',
]
print("DATABASE_URL=postgresql://postgres:<POSTGRES_PASSWORD>@airedison-airedisonpostgres-wsxrdk:5432/motivation_app")
print(f"SECRET_KEY={secrets.token_urlsafe(48)}")
print("FLASK_ENV=production")
for k in KEYS_FROM_ENV:
    print(f"{k}={env.get(k)}")
print("BASE_URL=http://160.251.199.237")
print("PORT=5002")
PY_EOF
echo "=== END ==="
```

**注意**: `<POSTGRES_PASSWORD>` は Mac で `cat /Users/kurinobu/projects/yadopera/.env.local | grep POSTGRES_PASSWORD` 等で確認し、Dokploy 画面で**直接書き換えてから** Save する（チャットには貼らない）。

#### 6-D-6-b: 出力 17 行の内訳

事前調査 [§0.3 訂正後の事実](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md#03-訂正後の事実実測根拠付き初版を上書きせず本セクションに記載) の A 分類 / B 分類に基づく。

| # | キー | 由来 | 備考 |
|---|------|------|------|
| 1 | `DATABASE_URL` | テンプレに直書き → `<POSTGRES_PASSWORD>` だけ Dokploy 画面で置換 | **C-1 到達回避のため必須**・DB 名は `motivation_app` |
| 2 | `SECRET_KEY` | `secrets.token_urlsafe(48)` 新規生成 | Render 値と分けて漏洩リスク分離 |
| 3 | `FLASK_ENV` | テンプレで `production` 固定 | `config.py:57` の `ProductionConfig` を選択 |
| 4 | `BREVO_API_KEY` | `.env` から `dotenv_values()` で取得 | **C-2 到達回避のため必須**・Brevo Authorized IPs に `160.251.199.237` は YadOPERA Phase 5 で追加済 |
| 5 | `BREVO_SENDER_EMAIL` | `.env` から | services.py のメール送信元 |
| 6 | `BREVO_SENDER_NAME` | `.env` から | services.py のメール送信元名 |
| 7 | `FROM_EMAIL` | `.env` から | services.py の旧キー fallback |
| 8 | `FROM_NAME` | `.env` から | services.py の旧キー fallback |
| 9 | `ANTHROPIC_API_KEY` | `.env` から | Claude API 利用 |
| 10 | `ANTHROPIC_MODEL` | `.env` から | Claude モデル指定 |
| 11 | `USE_MOCK_API` | `.env` から | Claude API モック切替 |
| 12 | `API_TRAFFIC_PERCENTAGE` | `.env` から | Claude API 流量 |
| 13 | `CLAUDE_MAX_RETRIES` | `.env` から | Claude リトライ回数 |
| 14 | `CLAUDE_RETRY_DELAY_BASE` | `.env` から | Claude リトライ間隔基数 |
| 15 | `CLAUDE_TIMEOUT_SECONDS` | `.env` から | Claude タイムアウト |
| 16 | `BASE_URL` | テンプレで `http://160.251.199.237` 固定 | Phase 6 暫定・Phase 7 で本ドメインに切替・メール本文の URL 生成元 |
| 17 | `PORT` | テンプレで `5002` 固定 | Dockerfile 既定と一致・Dokploy 注入と冗長だが明示 |

#### 6-D-6-c: 意図的に未設定（Render 時代と同じ fallback 動作を維持）

| キー | コード fallback | 理由 |
|------|----------------|------|
| `ADMIN_PASSWORD_HASH` | **`app.py:138` で `generate_password_hash('kurikuri')`**（C-3） | Owner 方針「Render と同じ状態で載せ替え」・Phase 7+ で変更判断 |
| `DATA_PATH` / `FLASK_DATA_PATH` | `config.py` 既定 `data` | Dockerfile で `mkdir -p data` 済 |
| `SMTP_*` (4 件) / `HOURLY_TOKEN_LIMIT` / `MONTHLY_TOKEN_BUDGET` / `WARNING_THRESHOLD` / `USE_REAL_API` | コード参照なし（grep 範囲外で参照される可能性は留保） | Phase 7+ で要確認 |

### 6-D-8: Deploy ログ確認ポイント

- `db.create_all()` 成功ログ
- `データベース接続テスト成功`（`app.py:97`）
- `gunicorn ... Booting worker with pid: ...`
- **エラーパターン**: `psycopg2.OperationalError: could not translate host name "dpg-..."` ← **C-1 フォールバックに到達した証拠**・即 `DATABASE_URL` 設定確認

### 6-D-9: 疎通確認コマンド（1 ブロック・Mac 実行・読み取りのみ）

Domain Save 後に実行:

```bash
curl -sS "https://api.yadopera.com/api/v1/health"; echo
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "yadopera_staging_app=%{http_code}\n" "https://staging-app.yadopera.com/"
curl -sS -o /dev/null -w "influberry=%{http_code}\n" -H "Host: staging-influberry.local" "http://160.251.199.237/"
curl -sS -H "Host: staging-influberry.local" "http://160.251.199.237/" | grep -o '<title>[^<]*</title>' | head -1
curl -sS -o /dev/null -w "motivation_root=%{http_code}\n" -H "Host: motivation-app-staging.local" "http://160.251.199.237/"
curl -sS -H "Host: motivation-app-staging.local" "http://160.251.199.237/" | grep -o '<title>[^<]*</title>' | head -1
```

**期待値**: YadOPERA health `healthy` ／app・staging-app 200／influberry 200 ＋ InfluBerry title／motivation_root 200 ＋ motivation_app の title

---

## Step 6-E: Deploy 後疎通

**ビルド方針・Domain 確定後**にコマンドを 1 ブロックで追記（Phase 3/5 と同様）。

InfluBerry Render 実績: `GET /api/auth/me`（要認証の場合は 401 でも **到達** とみなすか — **実測で記録**）。

---

## Step 6-F: 証跡・Phase 7 へ

- [x] [20260525_phase6_influberry_partial.md](../evidence/20260525_phase6_influberry_partial.md)（InfluBerry 部分完了）
- [x] [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md)（motivation_app 完了 + Phase 6 全体完了宣言）
- [x] 本書 [Phase 6 完了チェックリスト](#phase-6-完了チェックリスト) を全て `[x]`
- [x] 親引き継ぎ Phase 6 を ✅ → **Phase 7**（DNS・外部公開・本ドメイン化）

---

## Phase 6 完了チェックリスト

**必須（InfluBerry 部分・2026-05-25 完了）**

- [x] 6-A: 事前確認（YadOPERA 本番 OK・DB 存在・Dokploy 一覧）
- [x] 6-B: `influberry_staging` / `motivation_app` リストア（各 9 テーブル）
- [x] 6-C: InfluBerry Dokploy **Deploy Done**・DB 接続エラーなし（ログ確認）
- [x] 6-E（InfluBerry 部分）: `Host: staging-influberry.local` 偽装で 200 + InfluBerry title 取得・`/api/auth/me` 401（到達）／YadOPERA 全 200 維持

**必須（motivation_app 部分・2026-05-26 完了）**

- [x] 6-D-0: 事前調査（[調査分析報告書](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md) 作成・**C-1/C-2/C-3** 発見・Owner 方針確定・2026-05-26 訂正版反映）
- [x] 6-D-1: motivation_app に Dockerfile 追加・Mac で commit（push 前に Owner レビュー）
- [x] 6-D-3: Mac から `kurinobu/motivation_app` `main` に push — commit **`604aefa`**（full: `604aefa88851478911589aa5a449fe133d99e7fc`）
- [x] 6-D-5: Dokploy Application `motivation-app-staging`（Swarm `airedison-motivationappstaging-rex1my`）作成（Provider / Branch / Build / Domain `staging-motivation.local` Port 5002 Save 成功）
- [x] 6-D-6: Environment Settings **dotenv パーサー版テンプレで 17 行**保存成功（**C-1 / C-2 fallback 到達回避 / C-3 のみ意図的未設定で Render 時代と同じ動作を維持**）
- [x] 6-D-8: Deploy Done・Swarm レプリカ 1/1・所要 41 秒
- [x] 6-D-9: 疎通確認 — YadOPERA 全 200 維持（api `healthy` / app 200 / staging-app 200）／InfluBerry 200 + 正規 title／motivation_app `Host: staging-motivation.local` で **200 + `<title>キャラまるわかり - 3つの心理学理論で自己診断</title>`** 取得（2026-05-26 19:07）
- [x] 6-D-10: 証跡 [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md) 作成

**必須（共通）**

- [x] 6-F: Phase 6 完了証跡作成（InfluBerry partial + motivation_app complete の 2 文書で代替）・親引き継ぎ更新・誓約遵守の訂正履歴を調査報告書に追加

**Phase 6 完了宣言**: 上記 **必須**すべて `[x]` → **Phase 7**（DNS・本ドメイン化・HTTPS）**着手可**。

**Phase 6 に含めない（Phase 7+ Owner 判断対象）**:
- `influberry.jp` / `staging.influberry.jp` / motivation_app 本ドメイン等の **DNS 切替**（Phase 7）
- TLS letsencrypt 化（Phase 7）
- C-1（`app.py:52` 旧 Render DB ハードコード）・C-2（`services.py` Brevo キー ハードコード）・**C-3（`app.py:138` 管理者パスワード 'kurikuri' コード固定）** の **コード修正**（Owner 判断・Phase 7+）
- Brevo API キー **ローテーション**（Owner 作業・Phase 7 着手前推奨）
- GitHub `kurinobu/motivation_app` Visibility 確認（Owner 作業・Phase 7 着手前必須）
- 管理者パスワード `'kurikuri'` の変更（Owner 作業・Phase 7+）
- `motivation_app` Render 解約（Phase 8）

---

## ナビ原則（Phase 2〜5 継承）

1. **ユーザーのスクショ・ターミナル出力が正**  
2. **プレースホルダ禁止** — 確定したホスト名・Application 名だけ  
3. **Step 完了のたびに** 本書と [親引き継ぎ](./20260521_ConoHaVPS_移転統合_引き継ぎ.md) を更新  
4. **YadOPERA 本番を壊さない** — 共有 Postgres / Traefik / Dokploy 操作は影響範囲を確認  
5. **DNS** — ムームー画面を見てから書く

---

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-05-24 | 初版（Phase 6 次会話引き継ぎ・6-A〜6-F・Phase 5 前提・リポジトリ事実） |
| 2026-05-25 16:40 | 6-A〜6-E ステップ 1 実績反映・6-E ステップ 2 ブロッカー記録・引き継ぎプロンプト更新・証跡 `20260525_phase6_influberry_partial.md` を関連付け |
| 2026-05-25 17:02 | 6-E ステップ 2 解消（`influberry-staging` Domain Host を `staging-influberry.local` に変更／YadOPERA Domains 無変更／Mac から Host 偽装 curl で InfluBerry HTML 取得・`/api/auth/me` 401 到達確認／YadOPERA health/app/staging-app 全 200 維持）。InfluBerry 部分完了・次は 6-D motivation_app。引き継ぎプロンプト更新。 |
| 2026-05-25 17:32 | 6-D 事前調査完了・[調査分析報告書](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md) 作成。C-1（app.py:52 旧 Render DB ハードコード）・C-2（services.py Brevo キー ハードコード）を発見。Owner 方針「Render と同じ状態で載せ替え／コード修正なし／問題は証跡」確定（大原則 5・8 ／スコープ管理）。Step 6-D を Sub-Step 6-D-1〜6-D-10 に再構成・Dockerfile 内容と Environment 必須 9 キーを正本に明記。Phase 6 完了チェックリストに 6-D-1〜6-D-10 追加・Phase 7+ 申し送り（Brevo キー ローテーション・コード fail-fast 化・GitHub Visibility 確認・DNS 切替）を明記。 |
| 2026-05-26 19:10 | **Phase 6 全体完了**：6-D-1〜6-D-10 を全て実施・完了反映。commit `604aefa` / Deploy Done 41s / 17 行 Save / 疎通 200 + キャラまるわかり title 取得を全て事実として記録。6-D 重大事項に **C-3（app.py:138 管理者パスワード 'kurikuri' コード固定）** を追加。6-D-6 の必須キー一覧を **dotenv パーサー版テンプレ**に置換（bash grep + echo 方式の `# コメント`・クォート破損リスクを根本解決・大原則 1）。6-D-5 を「Domain Save まで同画面で実施」に統合・6-D-7 を 6-D-5 に統合。証跡 [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md) を新規作成・Phase 7 引き継ぎプロンプトを冒頭に提示。事前調査報告書に §0 訂正履歴（M-1〜M-4 と誓約）を追記して履歴保全。 |
