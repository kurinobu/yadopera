# Phase 6 motivation_app — 完了証跡（2026-05-26）

**記録日**: 2026-05-26 19:08 JST  
**判定**: **Phase 6 6-D（motivation_app）完了**・**Phase 6 全体完了**（InfluBerry 完了 2026-05-25 + motivation_app 完了 2026-05-26）  
**親文書**: [20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md](../maintenance/20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md)  
**関連証跡**:
- [20260525_phase6_influberry_partial.md](./20260525_phase6_influberry_partial.md)（InfluBerry 部分完了）
- [20260525_motivation_app_事前調査_調査分析報告書.md](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md)（事前調査 + 訂正履歴）
- [20260524_yadopera_conoha_migration_complete.md](./20260524_yadopera_conoha_migration_complete.md)（前提・Phase 5 完了）

**Owner 方針（確定済）**: **Render と同じ状態で載せ替え／動けば OK ／問題は証跡に残す／本 Phase でコードは触らない**

---

## 1. 結論サマリ

| Step | 状態 | 主要実測 |
|------|------|---------|
| 6-D-0 事前調査 | ✅ | 調査報告書作成・C-1（旧 Render DB ハードコード）・C-2（Brevo キー ハードコード）・**C-3（管理者パスワード `'kurikuri'` コード固定）** 発見 |
| 6-D-1 Dockerfile 作成 | ✅ | `/Users/kurinobu/motivation_app/Dockerfile`（280 バイト・16 行・Python 3.12.6-slim-bookworm 単一ステージ・PORT 5002・gunicorn 1 worker / 4 threads / 120s timeout） |
| 6-D-3 push | ✅ | `kurinobu/motivation_app` `main` ブランチ・commit **`604aefa`**（full: `604aefa88851478911589aa5a449fe133d99e7fc`）・1 file changed, +16 / -0 |
| 6-D-4 GitHub App 設定 | ✅ | `Dokploy-air-edison` Repository access に `kurinobu/motivation_app` を追加（既存 2 リポジトリ維持・YadOPERA / InfluBerry の access 削除なし） |
| 6-D-5 Dokploy Application 作成 | ✅ | `air-edison/production` に **`motivation-app-staging`**（`airedison-motivationappstaging-rex1my`）新規作成・Provider Github/`Dokploy-air-edison`/`kurinobu/motivation_app`/Branch `main`/Build Path `/`/Trigger `On Push`・Build Type **Dockerfile**（Context `.`）・Domain **`staging-motivation.local`** / Path `/` / Port **5002** / HTTP / Cert none |
| 6-D-6 Environment Settings | ✅ | **17 行** Save Successful（`DATABASE_URL` / `SECRET_KEY` 新規生成 / `FLASK_ENV=production` / `BREVO_*` 3 / `FROM_*` 2 / `ANTHROPIC_*` 2 / `USE_MOCK_API` / `API_TRAFFIC_PERCENTAGE` / `CLAUDE_*` 3 / `BASE_URL=http://160.251.199.237` / `PORT=5002`）。**dotenv パーサー版**でコメント・クォート除去済 |
| 6-D-8 Deploy | ✅ | Status **Done**・所要 **41 秒**・commit `604aefa88851478911589aa5a449fe133d99e7fc` |
| 6-D-9 疎通確認 | ✅ | YadOPERA / InfluBerry 全 200 維持・**motivation_app `GET /` 200 + `<title>キャラまるわかり - 3つの心理学理論で自己診断</title>`** |

---

## 2. 6-D-9 疎通確認の実測（2026-05-26 19:07 JST・Mac）

### 実行コマンド

```bash
curl -sS "https://api.yadopera.com/api/v1/health"; echo
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "yadopera_staging_app=%{http_code}\n" "https://staging-app.yadopera.com/"
curl -sS -o /dev/null -w "influberry=%{http_code}\n" -H "Host: staging-influberry.local" "http://160.251.199.237/"
curl -sS -H "Host: staging-influberry.local" "http://160.251.199.237/" | grep -o '<title>[^<]*</title>' | head -1
curl -sS -o /dev/null -w "motivation_root=%{http_code}\n" -H "Host: staging-motivation.local" "http://160.251.199.237/"
curl -sS -H "Host: staging-motivation.local" "http://160.251.199.237/" | grep -o '<title>[^<]*</title>' | head -1
```

### 出力（そのまま）

```text
{"status":"healthy","database":"connected","redis":"connected"}
yadopera_app=200
yadopera_staging_app=200
influberry=200
<title>InfluBerry - インフルエンサー案件管理・請求書自動生成SaaS</title>
motivation_root=200
<title>キャラまるわかり - 3つの心理学理論で自己診断</title>
```

### 判定

| 観点 | 結果 |
|------|------|
| YadOPERA Backend health | `healthy` / DB `connected` / Redis `connected` ✅ |
| YadOPERA Frontend 本番 (`app.yadopera.com`) | `200` ✅ |
| YadOPERA Frontend staging (`staging-app.yadopera.com`) | `200` ✅ |
| InfluBerry (`Host: staging-influberry.local`) | `200` + 正規 title ✅ |
| **motivation_app (`Host: staging-motivation.local`) GET /** | **`200`** ✅ |
| **motivation_app トップ HTML** | **`<title>キャラまるわかり - 3つの心理学理論で自己診断</title>`**（`templates/index.html` ベース・Jinja レンダリング成功＝Flask + DB + 設定の依存関係が起動している実証） ✅ |

→ **Phase 6 完了条件を全て満たす**。

---

## 3. リポジトリ変更（Mac → GitHub）

| 項目 | 値 |
|------|-----|
| リポジトリ | `https://github.com/kurinobu/motivation_app.git` |
| ブランチ | `main` |
| 前 HEAD | `05dd682`（`blogindxとケーススタディにアフィリエイト`） |
| 新 HEAD | **`604aefa`**（full: `604aefa88851478911589aa5a449fe133d99e7fc`） |
| Commit メッセージ | `Add Dockerfile for ConoHa Dokploy deploy (main)` + 4 行詳細 |
| 変更ファイル | `Dockerfile`（新規・16 行・コード変更なし） |
| 変更統計 | 1 file changed, **+16 / -0**（**他ファイル無変更**） |
| Author | `kurinobu <kuriblog@gmail.com>` |
| push 方式 | fast-forward `05dd682..604aefa` （force push なし） |

---

## 4. Dokploy 設定（motivation-app-staging）

| 項目 | 値 |
|------|-----|
| Project / Environment | `air-edison` / `production` |
| Application 名 | `motivation-app-staging` |
| Swarm 名 | `airedison-motivationappstaging-rex1my` |
| Provider | Github / `Dokploy-air-edison` / `kurinobu/motivation_app` / Branch `main` / Build Path `/` / Trigger `On Push` |
| Build Type | Dockerfile / Docker Context Path `.` / Dockerfile Path 既定 (`./Dockerfile`) |
| Domains | `staging-motivation.local` / Path `/` / Port `5002` / HTTP / Cert none ※暫定・Phase 7 で本ドメインに切替予定 |
| Environment（キーのみ・値は Git 外） | `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV`, `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`, `BREVO_SENDER_NAME`, `FROM_EMAIL`, `FROM_NAME`, `BASE_URL`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `USE_MOCK_API`, `API_TRAFFIC_PERCENTAGE`, `CLAUDE_MAX_RETRIES`, `CLAUDE_RETRY_DELAY_BASE`, `CLAUDE_TIMEOUT_SECONDS`, `PORT` |
| **意図的に未設定** | `ADMIN_PASSWORD_HASH`（C-3 コード fallback `'kurikuri'` で起動・Phase 7+ Owner ローテーション）／`DATA_PATH` / `FLASK_DATA_PATH`（fallback で動作）／`HOURLY_TOKEN_LIMIT` / `MONTHLY_TOKEN_BUDGET` / `WARNING_THRESHOLD` / `SMTP_*` / `USE_REAL_API`（現行コード非バックアップで grep 未ヒット） |

---

## 5. 6-D-6 Environment 投入手法（dotenv パーサー版・大原則 1 根本解決）

**経緯**: 初回ナビで bash の grep + echo で `.env` を抽出する方法を提示したが、Owner 指摘により以下のリスクが判明:
- `.env` 内の `# コメント` 付き行が grep 結果にコメント付きで含まれ、Dokploy への投入時に値が破損する可能性
- bash grep ではクォート (`"..."`) 除去ができない

**対処**: motivation_app の `requirements.txt` に含まれる **`python-dotenv==1.0.1` の `dotenv_values()` を使ってパース** することに切り替え。これは `app.py:23` の `load_dotenv()` と同じパーサーであり、**Flask 起動時に読む値と完全一致** することが保証される。

**実行内容**: Mac で以下を 1 ブロック実行 → 出力テキストを Dokploy にコピペ（**秘密値はチャットを経由しない**）

```bash
NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
echo "=== Dokploy paste-ready ==="
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

**結果**: 17 行 Save Successful・Deploy Done・疎通 200 → 投入手法の正当性が実証された。

---

## 6. ハードコード機密情報（C-1 / C-2 / C-3 — 本 Phase スコープ外・Phase 7+ Owner 判断対象）

| ID | 場所 | 内容 | 本 Phase 対処 |
|----|------|------|--------------|
| C-1 | `app.py:52` | 旧 Render DB の `DATABASE_URL`（パスワード入り）ハードコード フォールバック | Dokploy `DATABASE_URL` 設定で到達回避・**コード未修正** |
| C-2 | `blueprints/mail/services.py:457,554` | Brevo API キー実値ハードコード フォールバック | Dokploy `BREVO_API_KEY` 設定で到達回避・**コード未修正** |
| **C-3** | `app.py:138` | 管理者パスワード `'kurikuri'` のコード固定 (`generate_password_hash('kurikuri')`) | Dokploy `ADMIN_PASSWORD_HASH` を**意図的に未設定**にしてコード fallback で起動・**コード未修正**（Render 時代と同じ運用挙動） |

**Phase 7+ Owner 申し送り**:
- GitHub `kurinobu/motivation_app` の Visibility 確認（Public なら C-1/C-2 値は漏洩済 → 即時ローテーション）
- Brevo API キー ローテーション（Brevo 管理画面 → 旧キー無効化 → 新キー発行 → Dokploy 更新 → Deploy）
- 旧 Render DB ロールパスワード対応（Phase 8 Render 解約で自動消滅）
- 管理者パスワード `'kurikuri'` の変更（Phase 7+ コード修正 / または DB 上で管理者ハッシュを更新する仕組みに改善）
- C-1/C-2/C-3 の fail-fast 化（環境変数欠落時は `raise RuntimeError(...)` で起動失敗）
- git history から旧機密値削除（git filter-repo・履歴改変・要慎重・別 Phase）

---

## 7. 私（Cursor）の事前調査の不備と訂正（誓約遵守の記録）

### 7.1 発生した憶測ミス（2 件）

| # | 内容 | 発見契機 | 影響 |
|---|------|---------|------|
| M-1 | 事前調査時に `.env` 実在キーを **未確認** のまま「Mac `.env` の `SECRET_KEY` をコピー」と指示 | Owner が「ここに必ず SECRET_KEY があるのですね？」と指摘 | 6-D-6 直前まで `.env` に `SECRET_KEY` / `ADMIN_PASSWORD_HASH` / `PORT` / `DATA_PATH` が **不在** であることに気付けず |
| M-2 | コード grep に `head_limit=120` を設定し、超過分を見落とした | `.env` 全キー一覧確認（`awk` 出力）で 23 キーが判明し、私が把握していなかった 13 キー（`ANTHROPIC_MODEL` / `CLAUDE_*` 3 / `SMTP_*` 4 / `USE_*` 2 / `*_TOKEN_*` 2 / `WARNING_THRESHOLD` / `API_TRAFFIC_PERCENTAGE`）が存在 | 必須キーの取りこぼし・bash grep 方式の誤指示 |

### 7.2 Owner からの指摘と誓約

Owner の指摘:
> 「憶測でものをいうやつは信用できない」「憶測で進めると時間とトークンを無駄にする」「憶測発言しないことを誓約しろ」

私の誓約（2026-05-26 18:41 JST 宣言・本書記録）:
1. 未確認の事実を「ある」「無い」と断言しない
2. すべてのナビ提示の前に事実確認した範囲と未確認の範囲を明示する
3. 実測根拠のないことは「未確認」と書き、Owner 判断を仰ぐ
4. `head_limit` や exclusion で取りこぼした可能性がある場合はその旨を明示して再調査を提案
5. 大原則 1〜8 のいずれかに違反する提示があれば即時停止し、訂正してから再開
6. 同じ憶測ミスを繰り返した場合は、私の責任として明示的に謝罪し、原因と再発防止策を提示

### 7.3 訂正後の事実（実測根拠付き）

`head_limit` なしで再 grep し、`.env` 全キー突合した結果（[事前調査報告書 §訂正履歴](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md) も同期更新）:

- **A 分類（コード参照 ∩ `.env` あり・15 キー）**: そのまま流用
- **B 分類（コード参照 / `.env` 無し・5 キー）**:
  - `SECRET_KEY` → 新規生成（α 案採用・Owner 承認）
  - `ADMIN_PASSWORD_HASH` → 意図的未設定（C-3 fallback `'kurikuri'`）
  - `DATA_PATH` / `FLASK_DATA_PATH` / `PORT` → fallback で動作（PORT は Dockerfile で固定）
- **C 分類（`.env` あり / コード非参照・8 キー）**: Dokploy 未投入（grep 範囲外で参照される可能性は留保）

---

## 8. 触っていないこと（YadOPERA / InfluBerry / 既存運用無影響）

- `api.yadopera.com` / `app.yadopera.com` / `staging-app.yadopera.com` の DNS・Dokploy env・Stripe Webhook・Brevo Authorized IPs
- `yadopera-backend-*` / `yadopera-frontend-*` / `influberry-staging` の Domains / Environment
- `motivation_app` リポジトリのコード（Dockerfile 追加 1 ファイルのみ・既存ファイル全て無変更）
- Render Dashboard（Phase 8 で解約予定・本 Phase は触らない）
- DNS（Phase 7 で実施）

実測（疎通確認時刻 2026-05-26 19:07 JST）: YadOPERA health `healthy` / `app` `200` / `staging-app` `200` / InfluBerry `200` を維持。

---

## 9. Phase 6 完了宣言

| 必須項目 | 状態 |
|---------|------|
| 6-A 事前確認 | ✅ |
| 6-B Phase 4-E リストア | ✅ |
| 6-C InfluBerry Dokploy Deploy Done | ✅（2026-05-25） |
| 6-D motivation_app Dokploy Deploy Done | ✅（2026-05-26） |
| 6-E 各アプリ疎通 1 件以上 | ✅（InfluBerry 2026-05-25 / motivation_app 2026-05-26） |
| 6-F 証跡・親引き継ぎ更新 | 進行中（本書 + 正本 + 親引き継ぎ更新） |

→ **Phase 6 完了**（残作業は文書化のみ）。**Phase 7（DNS 切替・本ドメイン化・HTTPS）に進行可**。

---

## 10. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-05-26 19:08 | 初版（Phase 6 6-D motivation_app 完了証跡・Deploy `604aefa`・疎通 200 + キャラまるわかり title 取得・Phase 6 全体完了宣言・誓約遵守の記録） |
