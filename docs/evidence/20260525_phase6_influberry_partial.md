# Phase 6 InfluBerry — 部分完了証跡（2026-05-25）

**記録日**: 2026-05-25 16:40 JST（初版）／ 2026-05-25 17:02 JST（6-E ステップ 2 解消・追記）  
**判定**: **6-A〜6-E（InfluBerry 部分）完了**・**6-D（motivation_app）は未着手**  
**親文書**: [20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md](../maintenance/20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md)  
**前提**: [YadOPERA ConoHa 移行完了（2026-05-24）](./20260524_yadopera_conoha_migration_complete.md)

---

## 1. 実施範囲（事実のみ）

| Step | 状態 | 根拠（実測） |
|------|------|--------------|
| 6-A 事前確認 | ✅ | `GET https://api.yadopera.com/api/v1/health` → `healthy` / app `HTTP/2 200` / 両リポジトリに **Dockerfile 無し** / Phase 0 ダンプ 2 ファイル Mac 上に存在 / VPS Postgres コンテナ `airedison-airedisonpostgres-wsxrdk.1.u4sww14dlpycjo7m804ztty3e` / `\l` に `influberry_staging` / `motivation_app` |
| 6-B Phase 4-E リストア | ✅ | `pg_restore` 後 `\dt public.*`: `influberry_staging` **9 テーブル**（`alembic_version`,`invoice_status_history`,`invoices`,`monthly_snapshots`,`monthly_summary`,`monthly_targets`,`project_status_history`,`projects`,`users`） / `motivation_app` **9 テーブル**（`bigfive_diagnoses`,`contacts`,`detailed_diagnoses`,`download_logs`,`email_logs`,`enneagram_diagnoses`,`mcclelland_diagnoses`,`page_access_logs`,`subscribers`）。 `pg_restore` ログには `constraint already exists` の WARNING（influberry 77 件・motivation 53 件）あり・**テーブル本体は確立** |
| 6-C-0 Dockerfile 追加 | ✅ | `/Users/kurinobu/projects/influberry_v2/Dockerfile` 新規作成 → `staging` に push。initial commit `c3eb3f5` でビルド失敗（後述）→ 修正 commit `f6f8725` で `COPY --from=frontend-build /app/frontend/dist /app/frontend/dist` を追加 |
| 6-C-1 Dokploy Application | ✅ | GitHub App `Dokploy-air-edison` の Repository access に `influberry` を追加 / Dokploy `air-edison/production` に Application **`influberry-staging`** 新規作成 / Provider `Github` Account `Dokploy-air-edison` Repo `kurinobu/influberry` Branch `staging` Build Path `/` Save 成功 / Build Type **Dockerfile**（Path 既定・Context `.`） Save 成功 / Domain `Host 160.251.199.237 / Path / / Port 5001 / HTTP / Cert none` Save 成功 |
| 6-C-2 Environment Settings | ✅ | Save 成功（行: `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=staging`, `PORT=5001`, `FRONTEND_URL=http://160.251.199.237`, `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REDIRECT_URI=https://influberry.jp/api/auth/tiktok/callback`）。`DATABASE_URL` は `postgresql://postgres:<pass>@airedison-airedisonpostgres-wsxrdk:5432/influberry_staging`（`+asyncpg` 無し・Flask + psycopg2 仕様） |
| 6-E ステップ 1 Deploy | ✅ | 2 回目 Deploy（commit `f6f8725`）**Done**・所要 **29 秒** / Swarm `airedison-influberrystaging-qqn2hl` **1/1** |
| **6-E ステップ 2 疎通** | ✅ | Domain Host を `staging-influberry.local` に変更（YadOPERA Domains は無変更）後、Mac から `curl -H "Host: staging-influberry.local" http://160.251.199.237/` で **`<title>InfluBerry - インフルエンサー案件管理・請求書自動生成SaaS</title>`** を取得・`/api/auth/me` **401**（認証ミドルウェア応答＝アプリ到達）・YadOPERA 側は health `healthy` / `app` 200 / `staging-app` 200 を維持（2026-05-25 17:00 実測） |

---

## 2. 6-E ステップ 2 ブロッカー解消記録（2026-05-25 17:00 完了）

### 2.1 ブロッカー発生時の実測（16:40 時点・原因究明用）

```text
$ curl -sS -o /dev/null -w "status=%{http_code} time=%{time_total}s\n" "http://160.251.199.237/"
status=200 time=0.053970s

$ curl -sS -o /dev/null -w "status=%{http_code} time=%{time_total}s\n" "http://160.251.199.237/api/auth/me"
status=404 time=0.058652s

$ curl -sS "http://160.251.199.237/" | head -c 300
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>YadOPERA</title>
    ...

$ ssh root@160.251.199.237 'docker service ls | grep -i influberry'
htmgekz0e2kt   airedison-influberrystaging-qqn2hl   replicated   1/1   ...
```

### 2.2 原因確定（2026-05-25 16:51 画面確認・実測）

Dokploy `air-edison/production` の Domains 画面を確認した結果、**Host `160.251.199.237` / Path `/` の 3 つの Application 衝突**が原因と確定:

| Application | Domain Host | Path | Port | TLS |
|-------------|-------------|------|------|-----|
| `yadopera-frontend-staging` | `160.251.199.237` | `/` | 80 | HTTP（none） |
| `yadopera-frontend-staging` | `staging-app.yadopera.com` | `/` | 80 | HTTPS（letsencrypt） |
| `yadopera-frontend-production` | `160.251.199.237` | `/` | 80 | HTTP（none） |
| `yadopera-frontend-production` | `app.yadopera.com` | `/` | 80 | HTTPS（letsencrypt） |
| `influberry-staging` | `160.251.199.237` | `/` | 5001 | HTTP（none）← 競合・先勝ち不可 |

→ Traefik が YadOPERA Frontend を先勝ちで配信していた。

### 2.3 対処（YadOPERA Domains は一切触らない）

| 対象 | 変更前 | 変更後 |
|------|--------|--------|
| `influberry-staging` Domains（1 行のみ） | Host `160.251.199.237` / Path `/` / Port `5001` / HTTP / Cert none | Host **`staging-influberry.local`** / Path `/` / Port `5001` / HTTP / Cert none |
| `yadopera-frontend-staging` Domains | （触らず・無変更） | （触らず・無変更） |
| `yadopera-frontend-production` Domains | （触らず・無変更） | （触らず・無変更） |
| `yadopera-backend-*` Environment / Domains | （触らず・無変更） | （触らず・無変更） |
| DNS / Stripe / Brevo | （触らず・無変更） | （触らず・無変更） |

選定理由: `.local` は公的 DNS に解決させないため外部到達不可・テスト専用。Mac からは `curl -H "Host: staging-influberry.local"` の **Host ヘッダ偽装** のみで疎通確認できる。

### 2.4 解消後の実測（2026-05-25 17:00・Mac）

```bash
curl -sS "https://api.yadopera.com/api/v1/health"; echo
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "yadopera_staging_app=%{http_code}\n" "https://staging-app.yadopera.com/"
curl -sS -o /dev/null -w "ip_default=%{http_code}\n" "http://160.251.199.237/"
curl -sS "http://160.251.199.237/" | grep -o '<title>[^<]*</title>' | head -1
curl -sS -o /dev/null -w "influberry_root=%{http_code}\n" -H "Host: staging-influberry.local" "http://160.251.199.237/"
curl -sS -H "Host: staging-influberry.local" "http://160.251.199.237/" | grep -o '<title>[^<]*</title>' | head -1
curl -sS -o /dev/null -w "influberry_auth_me=%{http_code}\n" -H "Host: staging-influberry.local" "http://160.251.199.237/api/auth/me"
```

```text
{"status":"healthy","database":"connected","redis":"connected"}
yadopera_app=200
yadopera_staging_app=200
ip_default=200
<title>YadOPERA</title>
influberry_root=200
<title>InfluBerry - インフルエンサー案件管理・請求書自動生成SaaS</title>
influberry_auth_me=401
```

### 2.5 判定

| 観点 | 結果 |
|------|------|
| YadOPERA Backend health | `healthy` / DB `connected` / Redis `connected` ✅ |
| YadOPERA `app.yadopera.com` | `200` ✅ |
| YadOPERA `staging-app.yadopera.com` | `200` ✅ |
| IP 直叩き（`http://160.251.199.237/`） | `200` / `<title>YadOPERA</title>`（既存どおり・変更なし） ✅ |
| InfluBerry 到達（Host 偽装） | `200` / `<title>InfluBerry - インフルエンサー案件管理・請求書自動生成SaaS</title>` ✅ |
| InfluBerry `/api/auth/me` | `401`（認証必要・到達済み＝Flask アプリと依存関係が起動している証拠） ✅ |

→ **6-E ステップ 2（InfluBerry 疎通）完了**。YadOPERA 影響ゼロ確認済み。

### 2.6 Phase 7 への申し送り（DNS 確定後に再設定が必要）

- 現状 `staging-influberry.local` は外部到達不可（テスト用）。Phase 7 で `staging.influberry.jp` の DNS を ConoHa VPS に向ける際、Dokploy `influberry-staging` Domain Host を `staging.influberry.jp` に変更し、TLS（letsencrypt）を有効化する。
- `160.251.199.237` の Host を持つ Application が 3 つある状態（YadOPERA Frontend × 2 + InfluBerry なし）は Phase 6 完了時点では **YadOPERA Frontend × 2 のみ**。Phase 7 で IP Host の整理が必要かは別途判断（Phase 6 範囲外）。

---

## 3. リポジトリ変更（Mac → GitHub）

| 項目 | 値 |
|------|-----|
| リポジトリ | `https://github.com/kurinobu/influberry.git` |
| ブランチ | `staging` |
| 追加ファイル | `Dockerfile`（マルチステージ: `node:20.19.0-bookworm-slim` + `python:3.12.6-slim-bookworm`） |
| commit 1（初版・ビルド失敗） | `c3eb3f5` — `Add Dockerfile for ConoHa Dokploy deploy (staging)` |
| commit 2（修正・ビルド成功） | `f6f8725` — `Fix Dockerfile: copy frontend dist from build stage` |
| 修正内容 | stage-2 に `COPY --from=frontend-build /app/frontend/dist /app/frontend/dist` を追加（初版はマルチステージ間でビルド成果物を引き継いでおらず `cp: cannot stat 'frontend/dist/*': No such file or directory` で失敗） |
| バックアップ | `/Users/kurinobu/projects/influberry_v2/Dockerfile.bak_20260525_pre_stage_fix`（Mac 手元のみ・`.gitignore` で除外） |

---

## 4. Dokploy 設定（influberry-staging）

| 項目 | 値 |
|------|-----|
| Project / Environment | `air-edison` / `production` |
| Application 名 | `influberry-staging` |
| Swarm 名 | `airedison-influberrystaging-qqn2hl` |
| Provider | Github / `Dokploy-air-edison` / `kurinobu/influberry` / Branch `staging` / Build Path `/` / Trigger `On Push` |
| Build Type | Dockerfile / Path 既定 / Context `.` |
| Domains（2026-05-25 17:00 時点） | **`staging-influberry.local`** / Path `/` / Port `5001` / HTTP / Cert none ※暫定・Phase 7 で `staging.influberry.jp` に切替予定 |
| Environment（キーのみ・値は Git 外） | `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV=staging`, `PORT=5001`, `FRONTEND_URL=http://160.251.199.237`, `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REDIRECT_URI` |

---

## 5. 触っていないこと（YadOPERA 影響なし）

- `api.yadopera.com` / `app.yadopera.com` の DNS・Dokploy env・Stripe Webhook
- `yadopera-backend-*` / `yadopera-frontend-*` の Domains / Environment
- `staging-app.yadopera.com` / `staging-api.yadopera.com`
- `motivation_app` Dokploy Application（Phase 6 6-D・未着手）
- Brevo・OpenAI・Render・Railway

確認: Phase 5 完了時の YadOPERA health は本会話開始時も終了時も `{"status":"healthy","database":"connected","redis":"connected"}` を返している。

---

## 6. 機密情報の取り扱い（インシデント記録・要 Owner 判断）

本会話中、Dokploy Environment Settings 画面のスクリーンショットがチャットに共有された際、次の機密値が暗号化されない状態で画面上に表示されました。**チャット共有の合意の上**で進行しましたが、運用安全のため **Phase 6 完了後にローテーション**を Owner 判断で実施してください。

| 項目 | 推奨アクション |
|------|--------------|
| `SECRET_KEY` (InfluBerry) | `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` で再生成・Dokploy env 上書き・再 Deploy |
| Postgres `postgres` ロール パスワード | Dokploy `air-edison-postgres` 上でパスワード変更 → 全 Application の `DATABASE_URL` 更新（YadOPERA 含む・**影響大**） |
| `TIKTOK_CLIENT_SECRET` | TikTok 開発者画面で再発行 → InfluBerry env 上書き |

---

## 7. 次会話へ（コピペ用プロンプト）

### 7.1 推奨（2026-05-25 17:02・6-D 開始用）

```
Phase 6（InfluBerry・キャラまるわかり実装）を引き継ぎ再開します。
正本: docs/maintenance/20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md
証跡: docs/evidence/20260525_phase6_influberry_partial.md
6-A〜6-E（InfluBerry 部分・staging-influberry.local で疎通確認済）まで完了。
次の作業は 6-D（motivation_app）の事前確認から開始してください。
最初に motivation_app のリポジトリ事実（Dockerfile 有無・wsgi・requirements）と
VPS 上の DB motivation_app の \dt を読み取り（無変更）で確認させてください。
憶測禁止。コピペ用ブロックは 1 つのコード欄にまとめる。Mac≠VPS。git は Mac のみ。
YadOPERA api/app・Stripe・DNS・Brevo は触らない。Phase 5 は完了済み
（docs/evidence/20260524_yadopera_conoha_migration_complete.md）。
```

### 7.2 旧（2026-05-25 16:40・参考保存）

```
Phase 6（InfluBerry・キャラまるわかり実装）を引き継ぎ再開します。
正本: docs/maintenance/20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md
「次会話引き継ぎ（Phase 6 即開始）」§現在地点（2026-05-25 16:40 時点）から 1 Step ずつナビしてください。
証跡: docs/evidence/20260525_phase6_influberry_partial.md
6-A〜6-E ステップ 1 は完了。次の作業は 6-E ステップ 2 のブロッカー解消
（Traefik ルーティングが InfluBerry に届かない・本文が YadOPERA HTML）。
最初に yadopera-frontend-staging / -production の Domains を画面で確認させてください。
憶測禁止。コピペ用ブロックは 1 つのコード欄にまとめる。Mac≠VPS。git は Mac のみ。
YadOPERA api/app・Stripe・DNS・Brevo は触らない。Phase 5 は完了済み
（docs/evidence/20260524_yadopera_conoha_migration_complete.md）。
```
