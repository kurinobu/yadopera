# InfluBerry 本番載せ替え + サービス再開 — 実施手順

**作成日**: 2026-05-29  
**正本計画**: [20260529_InfluBerry_本番載せ替え_サービス再開_計画.md](./20260529_InfluBerry_本番載せ替え_サービス再開_計画.md)  
**親**: [サービス再開 三本柱](./20260529_サービス再開_三本柱_実施計画.md)  
**前提**: [① YadOPERA 証跡](../evidence/20260529_yadopera_service_resumption_complete.md) ✅

---

## 実施順序

```
IB-0  凍結確認・YadOPERA ベースライン
IB-1  本番 Application 設計 ✅（2026-05-29・推奨値で確定）
IB-2  Dokploy 本番 Application 作成・Deploy ← **Owner 作業（今ここ）**
IB-3  ムームー influberry.jp A → 160.251.199.237
IB-4  Domains + letsencrypt（influberry.jp）
IB-5  TikTok OAuth 等 env 本番 URL 整合
IB-6  本番 HTTPS 疎通・YadOPERA 無影響
IB-7  証跡
```

---

## IB-0 ✅（2026-05-29）

→ [計画書 IB-0 実施記録](./20260529_InfluBerry_本番載せ替え_サービス再開_計画.md#ib-0-実施記録2026-05-29)

---

## IB-1 ✅（2026-05-29・Owner 入力なし・推奨値で確定）

| 項目 | 確定値 | 根拠 |
|------|--------|------|
| Application 名 | `influberry-production` | YadOPERA 同型 |
| GitHub | `kurinobu/influberry` | Phase 6 実績 |
| Branch | ~~`staging`~~ → **`main`（訂正・TikTok OAuth 実装は main のみ）** | IB-1 時の確認不足。[調査報告](../reports/202605/20260529_influberry_tiktok_oauth_branch_gap_調査報告.md) |
| Port | **5003** | 5001=staging・5002=motivation |
| 暫定 Domain Host | **`influberry-production.local`** | Phase 6 の `staging-influberry.local` と同手法 |
| DB 名 | **`influberry`** | YadOPERA `yadopera` / `yadopera_staging` 分離に倣う |
| DB 初期データ | **B** | VPS 上で `influberry_staging` からコピー（本番専用 dump 無し） |
| `FLASK_ENV` | `production` | |
| `FRONTEND_URL` | `https://influberry.jp` | IB-4 前は未到達でも env は本番 URL |
| `TIKTOK_REDIRECT_URI` | `https://influberry.jp/api/auth/tiktok/callback` | staging env 実績 |
| `SECRET_KEY` | **新規** | Dokploy 保存時に Mac で生成（Git ・本書に書かない） |

---

## IB-1 参考 — 設計メモ（アーカイブ）

### 1.1 staging 実績（写し元・変更しない）

| 項目 | 確定値（Phase 6/7 証跡） |
|------|--------------------------|
| Dokploy Project / Env | `air-edison` / `production` |
| Application 名 | `influberry-staging` |
| URL | `https://staging.influberry.jp/` |
| GitHub | `kurinobu/influberry` |
| Branch | **`staging`**（6-C-1 実績） |
| Build | Dockerfile / Context `.` / Path `/` |
| Domain | Host `staging.influberry.jp` / Path `/` / Port **`5001`** / HTTPS letsencrypt |
| DB 名 | **`influberry_staging`** |
| Postgres Swarm | `airedison-airedisonpostgres-wsxrdk` |
| env キー | `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV`, `PORT`, `FRONTEND_URL`, `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REDIRECT_URI` |
| `FLASK_ENV`（staging） | `staging` |
| `PORT`（staging） | `5001` |
| `TIKTOK_REDIRECT_URI`（staging 時点） | `https://influberry.jp/api/auth/tiktok/callback`（本番 URL のまま） |

**他サービス Port（衝突回避）**: motivation_app staging = **5002**

---

### 1.2 本番設計シート（Owner が空欄を埋めて確定）

| # | 項目 | 推奨（YadOPERA 同型） | Owner 確定値 | メモ |
|---|------|----------------------|--------------|------|
| 1 | Dokploy Application 名 | `influberry-production` | | `influberry-staging` と別 Application |
| 2 | 公開 URL | `https://influberry.jp/` | | IB-3/4 後 |
| 3 | GitHub Repo | `kurinobu/influberry` | | staging と同じ |
| 4 | **Branch** | **`main` または `staging`** | | 6-C は `staging`。本番 Render 名は `influberry-app`。**リポジトリの本番ブランチを画面で確認してから** |
| 5 | Build | Dockerfile / `/` / `.` | | staging と同型 |
| 6 | コンテナ **Port** | **5003**（要 VPS 空き確認） | | 5001=staging・5002=motivation。**空き Port は IB-2 直前に Dokploy 既存一覧で確認** |
| 7 | Domain（IB-2 暫定） | Host `160.251.199.237` または `influberry.local` / Path `/` / 上記 Port / HTTP | | IB-4 で `influberry.jp` + letsencrypt |
| 8 | Postgres **DB 名** | `influberry` | | YadOPERA は `yadopera` / `yadopera_staging` 分離 |
| 9 | DB 初期データ | **要判断** | | 下記 §1.3 |
| 10 | `FLASK_ENV` | `production` | | staging は `staging` |
| 11 | `FRONTEND_URL` | `https://influberry.jp` | | |
| 12 | `TIKTOK_REDIRECT_URI` | `https://influberry.jp/api/auth/tiktok/callback` | | staging env と同 URL（6-C-2 実績） |
| 13 | `SECRET_KEY` | **新規生成**（staging と別） | | staging 値の流用禁止 |
| 14 | `DATABASE_URL` | `postgresql://postgres:<pass>@airedison-airedisonpostgres-wsxrdk:5432/<DB名>` | | `+asyncpg` なし（Flask 実績） |

**IB-1 完了条件**: 上表の「Owner 確定値」がすべて埋まり、Owner が **IB-1 OK** と宣言。

---

### 1.3 DB 初期データ（憶測禁止・Owner 判断必須）

| 選択肢 | 事実 | リスク |
|--------|------|--------|
| **A** 新規空 DB `influberry` + アプリ migration | 手元ダンプ一覧に **本番 InfluBerry 専用 dump は無し**（`influberry_influberry-staging_*.dump` のみ） | 旧 Render 本番データは復元されない |
| **B** `influberry_staging` ダンプを `influberry` に restore | ファイル: `influberry_influberry-staging_20260521_120240.dump`（41KB） | 本番＝staging データのコピーになる |
| **C** 別途取得した本番 dump がある | Owner がパスを指定 | 未確認のため手順書には書かない |

→ **Render `influberry-app` / `influberry-db` は Phase 8 で Deleted**（[Phase 8 証跡](../evidence/20260527_phase8_render_railway_partial.md)）。ConoHa に本番データが無い場合は **A または B** のどちらか。

---

### 1.4 IB-1 確定後のコピペ用（秘密なし・IB-2 で使用）

```text
# Dokploy（IB-2）
Project: air-edison
Environment: production
Application: <Owner #1>
Repository: kurinobu/influberry
Branch: <Owner #4>
Build: Dockerfile / Path / / Context .

# Domain（IB-2 暫定 → IB-4 で influberry.jp）
Host: <暫定>
Path: /
Port: <Owner #6>
HTTPS: none（IB-4 で letsencrypt）

# DB（IB-2 前に VPS で CREATE DATABASE）
DB name: <Owner #8>
Swarm: airedison-airedisonpostgres-wsxrdk

# env キー（値は Git 外・staging と別 SECRET）
DATABASE_URL=
SECRET_KEY=
FLASK_ENV=production
PORT=<Owner #6>
FRONTEND_URL=https://influberry.jp
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=
TIKTOK_REDIRECT_URI=https://influberry.jp/api/auth/tiktok/callback
```

---

## IB-2 — Dokploy 本番 Application 作成・Deploy（Owner 作業）

**Cursor から VPS SSH は不可**（公開鍵未設定）。**IB-2 は Owner が Mac + Dokploy 画面で実施**します。  
完了したらチャットに **`IB-2 OK`** または該当サブ Step の **`IB-2a OK`** と送ってください。

**触らない**: `influberry-staging` の env / Domains・YadOPERA 4 Application。

---

### IB-2a ✅（2026-05-29）

- `PG=airedison-airedisonpostgres-wsxrdk.1.u4sww14dlpycjo7m804ztty3e`
- `CREATE DATABASE influberry` 成功
- `\dt` **9 テーブル**（`users`, `projects`, `invoices` 等）

### IB-2a — VPS: DB `influberry` 作成 + staging からコピー（約 5 分）

**Mac のターミナル**で実行（1 ブロックまとめてコピペ可）:

```bash
ssh root@160.251.199.237
PG=$(docker ps --format '{{.Names}}' | grep 'airedison-airedisonpostgres-wsxrdk' | head -1)
echo "PG=$PG"
docker exec -i "$PG" psql -U postgres -d postgres -c "CREATE DATABASE influberry;"
docker exec -i "$PG" pg_dump -U postgres -d influberry_staging --no-owner --no-acl \
  | docker exec -i "$PG" psql -U postgres -d influberry -q
docker exec -i "$PG" psql -U postgres -d influberry -c "\dt"
exit
```

| 期待 | 意味 |
|------|------|
| `CREATE DATABASE` 成功 | 既にあれば `already exists` → 下の dump だけ再実行するか、中身を Owner 判断 |
| `\dt` で **9 テーブル前後** | staging と同規模（Phase 6 実績） |

→ 終わったら **`IB-2a OK`**

---

### IB-2b ✅（2026-05-29）

- Application `influberry-production`（`airedison-influberryproduction-3d0ili`）
- Domain: `influberry-production.local` / `/` / Port `5003` / HTTP / Cert none
- 画面の `queryA ENOTFOUND influberry-production.local` → **想定内**（Phase 6 `staging-influberry.local` 同様・公的 DNS に無いため）。IB-2e は **Host ヘッダ偽装 curl** で確認。IB-4 で `influberry.jp` に切替。

### IB-2b — Dokploy: Application 新規作成（約 10 分）

1. ブラウザで `http://160.251.199.237:3000` → Project **`air-edison`** → Environment **`production`**
2. **Create Application** → Name: **`influberry-production`**
3. **Provider**: Github / Account **`Dokploy-air-edison`** / Repo **`kurinobu/influberry`** / Branch **`staging`** / Build Path **`/`** → Save
4. **Build Type**: **Dockerfile**（Path 既定・Context **`.`**）→ Save
5. **Domains**（暫定・YadOPERA の Domain は編集しない）:
   - Host: **`influberry-production.local`**
   - Path: **`/`**
   - Port: **`5003`**
   - HTTPS: **off**（Cert none）
   - → Save

→ 終わったら **`IB-2b OK`**

---

### IB-2c ✅（2026-05-29）

- Save 成功（「Environments Added」）
- 8 キー・`DATABASE_URL` 末尾 DB=`influberry`・`FLASK_ENV=production`・`PORT=5003`・`FRONTEND_URL=https://influberry.jp`（値は Git 外）

### IB-2c — Environment Settings（約 10 分）

1. Dokploy → **`influberry-production`** → **Environment**
2. まず **`influberry-staging`** の Environment を別タブで開き、**値をコピーする元**にする（画面を見るだけ・保存しない）
3. **`influberry-production`** に次の **8 行**を入れて Save（値は Git 外）:

| キー | 値の決め方 |
|------|------------|
| `DATABASE_URL` | staging の URL をコピーし、末尾 DB 名だけ **`influberry_staging` → `influberry`** に変更 |
| `SECRET_KEY` | **新規** — Mac で `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` の出力を貼る（staging と別） |
| `FLASK_ENV` | `production` |
| `PORT` | `5003` |
| `FRONTEND_URL` | `https://influberry.jp` |
| `TIKTOK_CLIENT_KEY` | staging と**同じ**（コピー） |
| `TIKTOK_CLIENT_SECRET` | staging と**同じ**（コピー） |
| `TIKTOK_REDIRECT_URI` | `https://influberry.jp/api/auth/tiktok/callback` |

→ Save Successful なら **`IB-2c OK`**

---

### IB-2d ✅（2026-05-29）

- Deploy **Done**（約 18s）・commit `f6f8725`（staging と同じ・Dockerfile 修正版）

### IB-2d — Deploy（約 2〜5 分）

1. **`influberry-production`** → **Deploy** → 完了まで待つ（staging と同様 **Done**）
2. 失敗したら Deploy ログの末尾をチャットに貼る（憶測修正しない）

→ **`IB-2d OK`**

---

### IB-2e ✅（2026-05-29・Mac 相当 curl）

| 確認 | 結果 |
|------|------|
| YadOPERA health | `healthy` |
| `app.yadopera.com` | 200 |
| `influberry-production` title | `<title>InfluBerry - インフルエンサー...` |
| `/api/auth/me` | **401** |

※ HTTP のみ `Host:` 偽装だと **301** になる場合あり。下記 **HTTPS + `--resolve`** を正とする。

### IB-2e — 疎通（Mac・YadOPERA 無影響確認）

```bash
curl -sS "https://api.yadopera.com/api/v1/health"; echo
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sSk --resolve influberry-production.local:443:160.251.199.237 \
  "https://influberry-production.local/" | grep -o '<title>[^<]*</title>' | head -1
curl -sSk -o /dev/null -w "influberry_me=%{http_code}\n" \
  --resolve influberry-production.local:443:160.251.199.237 \
  "https://influberry-production.local/api/auth/me"
curl -sS -o /dev/null -w "staging_influberry=%{http_code}\n" "https://staging.influberry.jp/"
```

| 期待 |
|------|
| YadOPERA health `healthy`・app **200** |
| InfluBerry `<title>InfluBerry` |
| `/api/auth/me` **401**（到達・未ログイン） |
| `staging.influberry.jp` **200**（無影響） |

→ 全部 OK なら **`IB-2 OK`**（IB-3 DNS へ）

---

## IB-3 ✅（2026-05-29）

- ムームー `influberry.jp` ルート A → **`160.251.199.237`**（Owner 画面）
- VPS `dig +short influberry.jp` → **`160.251.199.237`**
- `staging.influberry.jp` A → `160.251.199.237`（変更なし・維持）
- **未対応（任意・後追い可）**: `www` CNAME → まだ `influberry-app.onrender.com`（`www.influberry.jp` は Render 向きのまま）

---

## IB-4 — Dokploy Domains + letsencrypt（`influberry.jp`）

**対象 Application**: **`influberry-production` のみ**（`influberry-staging` は触らない）

### 手順

1. Dokploy → **`influberry-production`** → **Domains**
2. 既存行（`influberry-production.local`）を **Edit** するか、行を追加して本番用にする（**1 行で本番ホストだけ**にするのが安全）:
   - Host: **`influberry.jp`**
   - Path: **`/`**
   - Port: **`5003`**
   - HTTPS: **ON**
   - Certificate provider: **letsencrypt**
   - → **Save**
3. 数分待ち、Dokploy 上で DNS Valid / 証明書発行が進むか確認
4. Mac で確認:

```bash
dig +short influberry.jp
curl -sS -o /dev/null -w "influberry_root=%{http_code}\n" "https://influberry.jp/"
curl -sS "https://influberry.jp/" | grep -o '<title>[^<]*</title>' | head -1
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "staging_influberry=%{http_code}\n" "https://staging.influberry.jp/"
```

| 期待 |
|------|
| `dig` → `160.251.199.237` |
| `https://influberry.jp/` → **200** + InfluBerry title |
| YadOPERA app **200**・staging **200** |

**失敗時**: Domains のエラー文・letsencrypt ログをチャットに貼る（`influberry-production.local` 行が残っていると競合することがある → 本番は `influberry.jp` のみにする）

### IB-4 ✅（2026-05-29）

- Dokploy: `influberry.jp` / Port `5003` / HTTPS letsencrypt
- VPS: `dig` → `160.251.199.237`・`https://influberry.jp/` **200**・InfluBerry title

→ OK なら **`IB-4 OK`**

---

## IB-5 — TikTok ログイン復旧（マスト・訂正タスク）

**原因**: Deploy branch が `staging`（TikTok 無し）。実装は **`main`**。  
**報告**: [20260529_influberry_tiktok_oauth_branch_gap_調査報告.md](../reports/202605/20260529_influberry_tiktok_oauth_branch_gap_調査報告.md)

### IB-5a ✅（2026-05-29）

- `influberry.users`: `tiktok_id`, `tiktok_username`, `tiktok_avatar_url`, `oauth_provider`, `idx_users_tiktok_id` **あり**
- → **IB-5b（migration）スキップ**

### IB-5a — DB カラム確認（VPS）

```bash
PG=$(docker ps --format '{{.Names}}' | grep 'airedison-airedisonpostgres-wsxrdk' | head -1)
docker exec -i "$PG" psql -U postgres -d influberry -c "\d users" | grep -E 'tiktok|oauth_provider'
```

| 期待 | 意味 |
|------|------|
| `tiktok_id` 等 **4 列あり** | IB-5b スキップ可 |
| **無し** | IB-5b で migration 必要（`main` の `20251207120000_add_tiktok_oauth_fields`） |

→ 結果を貼るか **`IB-5a OK`**（列あり/なしを明記）

### IB-5b — migration（IB-5a で列が無い場合のみ）

Owner + Cursor ナビで実施（破壊的操作のため **1 Step 単独**）。

### IB-5c — Dokploy Branch `main` + Redeploy

1. `influberry-production` → Provider → Branch **`main`** → Save
2. Deploy → **Done**
3. `curl -sS -o /dev/null -w "%{http_code}\n" "https://influberry.jp/api/auth/tiktok/login"` → **302 または 200**（404 でないこと）

### IB-5d — 画面確認

- `https://influberry.jp/` に **「TikTokでログイン」** 表示
- クリックで TikTok へ遷移（またはエラー内容を記録）

→ **`IB-5 OK`**

---

## IB-6 — 最終スモーク + YadOPERA 無影響

```bash
curl -sS "https://api.yadopera.com/api/v1/health"; echo
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "influberry=%{http_code}\n" "https://influberry.jp/"
curl -sS -o /dev/null -w "staging_influberry=%{http_code}\n" "https://staging.influberry.jp/"
```

→ すべて期待どおりなら **`IB-6 OK`** → IB-7 証跡

---

## IB-7 以降

証跡 `docs/evidence/20260529_influberry_prod_service_resumption_complete.md`
