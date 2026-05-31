# motivation_app 事前調査 — 調査分析報告書（2026-05-25）

**記録日**: 2026-05-25 17:32 JST（初版）／**2026-05-26 19:10 訂正版**  
**記録目的**: Phase 6 6-D（motivation_app の ConoHa Dokploy 載せ替え）着手前の事前調査・大原則 8（品質ゲートと証跡）に基づく証跡  
**親文書**: [20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md](../../maintenance/20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md)  
**関連証跡**: [20260525_phase6_influberry_partial.md](../../evidence/20260525_phase6_influberry_partial.md) ／ [20260526_phase6_motivation_app_complete.md](../../evidence/20260526_phase6_motivation_app_complete.md)  
**Phase 6 方針（Owner 確定・2026-05-25 17:30）**: **Render と同じ状態で載せ替え／動けば問題なし／問題は証跡に残す／本 Phase でコードは触らない**

---

## 0. 訂正履歴と誓約遵守の記録（2026-05-26 追記）

> **記録方針**: 履歴改変はしない。初版（§1〜§10）はそのまま残し、本セクションで「初版に不備があった事実」「Owner 指摘」「私の誓約」「訂正後の事実」を明示する。

### 0.1 初版（2026-05-25 17:32）の不備

| # | 不備内容 | 根本原因 | 影響 |
|---|----------|----------|------|
| M-1 | §4「重大発見」を **C-1 / C-2 の 2 件**としか書かなかった | `app.py:138` 付近の grep 範囲を絞り込みすぎた | **C-3（管理者パスワード `'kurikuri'` のコード固定）を見落とし** |
| M-2 | §3.4 環境変数表に **`ANTHROPIC_MODEL` / `CLAUDE_*` 3 / `SMTP_*` 4 / `USE_*` 2 / `*_TOKEN_*` 2 / `WARNING_THRESHOLD` / `API_TRAFFIC_PERCENTAGE` が欠落** | コード grep に `head_limit=120` を設定し、超過分を見落とした | 6-D-6 Environment 設定で必須キー漏れの可能性（実際は `.env` 突合で 6-D-6 直前に補正できた） |
| M-3 | 6-D-6 直前ナビで「Mac `.env` の `SECRET_KEY` をそのままコピー」と指示 | `.env` 実在キーを未確認のまま指示 | Owner が「ここに必ず SECRET_KEY があるのですね？」と確認 → **`.env` に SECRET_KEY が無いことが判明**・新規生成方針に切替（6-D-6 直前で補正できた・実害なし） |
| M-4 | 初版 6-D-6 のテンプレを bash grep + echo で `.env` を抽出する方式にした | `.env` 内の `# コメント` 付き行・クォート (`"..."`) の扱いを未検証 | Dokploy 投入値が破損する可能性（実害発生前に Owner 指摘で気付き、dotenv パーサー版に切替） |

### 0.2 Owner 指摘・誓約

**Owner 指摘（2026-05-26 18:40 前後）**:
> 「憶測でものをいうやつは信用できない」「憶測で進めると時間とトークンを無駄にする」「憶測発言しないことを誓約しろ」「誓約していないお前の発言は一切読んでいない」

**私（Cursor）の誓約（2026-05-26 18:41 JST 宣言・本書記録）**:
1. 未確認の事実を「ある」「無い」と断言しない
2. すべてのナビ提示の前に、事実確認した範囲と未確認の範囲を明示する
3. 実測根拠のないことは「未確認」と書き、Owner 判断を仰ぐ
4. `head_limit` や exclusion で取りこぼした可能性がある場合はその旨を明示して再調査を提案
5. 大原則 1〜8 のいずれかに違反する提示があれば即時停止し、訂正してから再開
6. 同じ憶測ミスを繰り返した場合は、私の責任として明示的に謝罪し、原因と再発防止策を提示

### 0.3 訂正後の事実（実測根拠付き・初版を上書きせず本セクションに記載）

#### C-3（新規発見）: `app.py:138` 管理者パスワード `'kurikuri'` のコード固定

**実測（`/Users/kurinobu/motivation_app/app.py`）**:

```python
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')
if not ADMIN_PASSWORD_HASH:
    ADMIN_PASSWORD_HASH = generate_password_hash('kurikuri')
    logger.warning("ADMIN_PASSWORD_HASHが環境変数にないため、デフォルト値を使用します")
```

| 観点 | 評価 |
|------|------|
| リスク | GitHub Visibility が Public なら管理者ログインパスワードが漏洩済み・任意の第三者が管理画面に入れる可能性 |
| Phase 6 対処 | **Render 時代と同じ挙動**を維持するため Dokploy `ADMIN_PASSWORD_HASH` を**意図的に未設定**（Owner 方針「Render と同じ状態で載せ替え」） |
| Phase 7+ 申し送り | コード修正（`raise RuntimeError(...)` 化）・パスワード変更・DB 上で管理者ハッシュを管理する仕組みに変更 |

#### 環境変数表 訂正（`head_limit` なし再 grep + `.env` 全件突合）

| 分類 | 件数 | 内容 | Phase 6 取扱 |
|------|------|------|-------------|
| **A 分類（コード参照 ∩ `.env` あり）** | 15 | `BREVO_API_KEY` / `BREVO_SENDER_EMAIL` / `BREVO_SENDER_NAME` / `FROM_EMAIL` / `FROM_NAME` / `ANTHROPIC_API_KEY` / **`ANTHROPIC_MODEL`** / `USE_MOCK_API` / `API_TRAFFIC_PERCENTAGE` / **`CLAUDE_MAX_RETRIES`** / **`CLAUDE_RETRY_DELAY_BASE`** / **`CLAUDE_TIMEOUT_SECONDS`** / `BASE_URL` / `DATABASE_URL`（コード参照あり / `.env` ロカル値・本番は ConoHa Postgres） / `FLASK_ENV` | Dokploy 投入（`DATABASE_URL` と `BASE_URL` は ConoHa 値に置換） |
| **B 分類（コード参照 / `.env` 無し）** | 5 | `SECRET_KEY` → 新規生成（α 案・Owner 承認）／ **`ADMIN_PASSWORD_HASH` → 意図的未設定（C-3 fallback 容認）** ／ `DATA_PATH` / `FLASK_DATA_PATH` / `PORT` → fallback で動作（PORT は Dockerfile で固定） | 5 件中 1 件のみ投入（`SECRET_KEY`） |
| **C 分類（`.env` あり / コード非参照）** | 8 | `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `HOURLY_TOKEN_LIMIT` / `MONTHLY_TOKEN_BUDGET` / `WARNING_THRESHOLD` / `USE_REAL_API` | Dokploy 未投入（grep 範囲外で参照される可能性は留保・Phase 7+ で確認） |

→ 結果として 6-D-6 で **17 行 Save Successful**・Deploy Done・疎通 200。M-2 の影響は 6-D-6 直前で補正できたため**実害なし**。

#### 6-D-6 テンプレ 訂正（dotenv パーサー版）

初版の bash grep + echo 方式を廃止し、**`motivation_app` の `requirements.txt` に含まれる `python-dotenv==1.0.1` の `dotenv_values()` を使ってパース**する方式に変更。これは `app.py:23` の `load_dotenv()` と同じパーサーであり、**Flask 起動時に読む値と完全一致**することが保証される。詳細実装は [20260526_phase6_motivation_app_complete.md §5](../../evidence/20260526_phase6_motivation_app_complete.md#5-6-d-6-environment-投入手法dotenv-パーサー版大原則-1-根本解決) を参照。

### 0.4 §4「重大発見」C-1 / C-2 / C-3 統合表

| ID | 場所 | 内容 | Phase 6 対処 | Phase 7+ 申し送り |
|----|------|------|--------------|-------------------|
| C-1 | `app.py:50-52` | 旧 Render DB の `DATABASE_URL`（パスワード入り）ハードコード フォールバック | Dokploy `DATABASE_URL` 必須設定で到達回避 | コード fail-fast 化／旧 Render DB は Phase 8 解約で自動消滅 |
| C-2 | `blueprints/mail/services.py:457,554` | Brevo API キー実値ハードコード フォールバック | Dokploy `BREVO_API_KEY` 必須設定で到達回避 | GitHub Visibility 確認 → Brevo キー ローテーション ／ git history から削除 |
| **C-3** | `app.py:138` | 管理者パスワード `'kurikuri'` のコード固定 | **意図的未設定**で Render 時代と同じ挙動を維持 | コード fail-fast 化／管理者パスワード変更／DB 上の管理者ハッシュ運用 |

---

## 1. 結論サマリ（先に読む）

| 項目 | 結論 |
|------|------|
| Phase 6 スコープ | **Dockerfile 追加 + Dokploy 載せ替え + 疎通確認** のみ |
| コード修正 | **本 Phase では実施しない**（C-1/C-2 含めて） |
| Dockerfile 方針 | Python 3.12 単一ステージ・モノリス Flask 用・InfluBerry と同流派（大原則 3） |
| ハードコード機密（C-1/C-2） | **証跡として記録 → Phase 6 完了後に Owner 判断でローテーション/コード修正**（Phase 7 申し送り） |
| 運用カバー策 | Dokploy Environment で `DATABASE_URL`・`BREVO_API_KEY` を **必須項目として設定**することで、ハードコード フォールバック到達を防ぐ |
| 大原則整合 | 1 根本解決<暫定 = ⚠️ 本 Phase は暫定／2 シンプル = ✅／3 統一 = ✅／4 具体的 = ✅／5 安全確実 = ✅（スコープ限定）／6 Docker = ✅／7 LP 非該当／8 品質ゲート+証跡 = ✅（本書） |

---

## 2. 調査範囲（事実のみ）

**対象**: `/Users/kurinobu/motivation_app`（Mac ローカル・GitHub `kurinobu/motivation_app`）  
**実施日**: 2026-05-25 17:00〜17:30 JST  
**実施手段**: Cursor 経由のローカル読み取り（Read / Glob / Grep のみ・**変更なし**）  
**確認していないもの**: GitHub Visibility（Public/Private）・GitHub リポジトリの commit 履歴・`.env` の中身（秘密・読まない）

---

## 3. リポジトリ事実（実測）

### 3.1 構成

| 項目 | 結果 |
|------|------|
| アーキテクチャ | Flask モノリス（Vue/フロントビルドなし・Jinja テンプレートのみ） |
| トップディレクトリ | `app/` **無し** ／ `templates/`・`static/`・`blueprints/`・`models/`・`services/`・`migrations/` を直下に保持 |
| `Dockerfile` | **無し** |
| `Procfile` / `render.yaml` / `railway.toml` / `runtime.txt` / `pyproject.toml` / `Pipfile` / `gunicorn.conf.py` / `.env.example` | **全て無し** |
| `requirements.txt` | 有り |
| `wsgi.py` | 有り（`from app import app` で `app.py` の `app` を gunicorn に渡す） |
| `app.py` | 有り（Flask app 定義・SQLAlchemy 初期化・`db.create_all()` 起動時実行・APScheduler を起動） |
| ルート直下 `__init__.py` | 有り（パッケージ化されている） |
| `.gitignore` | `.env` 含む（秘密ファイルは Git 外） |

### 3.2 requirements.txt（実測）

```text
blinker==1.9.0
click==8.1.8
Flask==3.1.0
gunicorn==23.0.0
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
packaging==24.2
Werkzeug==3.1.3
SQLAlchemy==2.0.34
psycopg2-binary==2.9.9
Flask-SQLAlchemy==3.1.0
python-dotenv==1.0.1
APScheduler==3.10.4
anthropic==0.5.0
httpx==0.23.0
Flask-Migrate==4.0.5
setuptools>=59.6.0
reportlab==4.1.0
Pillow==10.2.0
requests==2.31.0
brevo-python==1.2.0
```

→ **ネイティブビルド依存なし**（`psycopg2-binary` は wheel・`Pillow` は wheel）。Python `3.12-slim-bookworm` で `pip install` のみで完結可能。

### 3.3 起動方法

| 観点 | 実測 |
|------|------|
| Render 時代の起動 | `gunicorn wsgi:app`（推定・`render.yaml` が無いため Render Dashboard の Start Command に依存） |
| 推奨起動 | `gunicorn wsgi:app --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120` |
| `--workers 1` の根拠 | `app.py:9` で `from apscheduler.schedulers.background import BackgroundScheduler` を import・起動時にバックグラウンドスケジューラが動く可能性。**ワーカー多重起動でメール多重送信などの副作用リスク**を回避するため 1 worker に限定 |
| `--timeout 120` の根拠 | `reportlab` PDF 生成・`brevo-python` API 通信のため余裕を持つ |

### 3.4 環境変数（実コード `os.environ.get` 実測）

#### 必須（フォールバックがあっても運用上必要）

| キー | 出現箇所 | フォールバック | 必要性 |
|------|---------|---------------|--------|
| `DATABASE_URL` | `app.py:50`, `config.py:14`, `update_schema.py:16` | **C-1（後述）** | **必須**（ConoHa Postgres `motivation_app` を指す URL） |
| `SECRET_KEY` | `app.py:46`, `config.py:11` | `secrets.token_hex(16)` / `os.urandom(24).hex()` | **必須**（セッション署名の安定性を担保） |
| `FLASK_ENV` | `app.py:192`, `config.py:57` | `default` → `DevelopmentConfig` | **必須**（`production` を指定） |
| `ADMIN_PASSWORD_HASH` | `app.py:141` | リテラル既定値（コード内・確認していない） | **必須**（管理画面のログイン） |
| `BREVO_API_KEY` | `blueprints/mail/services.py:457,554` | **C-2（後述）** | **必須**（メール送信） |
| `BREVO_SENDER_EMAIL` | `services.py:458,555` | `os.environ.get('FROM_EMAIL', 'motifinder@air-edison.com')` | **必須**（送信元アドレス） |
| `BREVO_SENDER_NAME` | `services.py:459,556` | `os.environ.get('FROM_NAME', 'キャラまるわかり')` | **必須**（送信元名） |
| `BASE_URL` | `services.py:13`, `blueprints/utils/url_helpers.py:7` | `https://olovolo.online` | **必須**（メール本文の URL 生成。Phase 6 は `http://160.251.199.237` 暫定） |
| `PORT` | gunicorn `--bind` | （Dockerfile で `ENV PORT=5002` 既定） | **必須**（Dokploy が注入） |

#### 任意（フォールバックで動作可）

| キー | 既定値 | 説明 |
|------|--------|------|
| `DATA_PATH` | `data` | データディレクトリ |
| `FROM_EMAIL` / `FROM_NAME` | `BREVO_SENDER_*` の代替 | 送信元の旧キー名 |
| `ANTHROPIC_API_KEY` | （未調査） | `requirements.txt` に `anthropic==0.5.0`・実コード grep には未ヒット・将来機能の可能性 |

---

## 4. 重大発見（C-1 / C-2）— 本 Phase スコープ外・証跡として記録

### 4.1 C-1: `app.py:52` 旧 Render DB のハードコード フォールバック

**実測（`/Users/kurinobu/motivation_app/app.py`）**:

```python
# 環境変数からデータベースURLを取得
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = 'postgresql://motivation_user:JdU5Ql5i444xgshYfdbI5wiTXXs6PK0z@dpg-cvp5hoidbo4c73basldg-a.singapore-postgres.render.com/motivation_db_squv'
    logger.warning("DATABASE_URLが環境変数にないため、デフォルト値を使用します")
```

| 観点 | 評価 |
|------|------|
| リスク | 環境変数欠落時に **旧 Render DB（Singapore）へ接続を試みる**。Render 解約後（Phase 8）は到達不可で起動エラー、解約前は本番外データに接続する事故 |
| Phase 6 対処 | **コードは触らない**（Owner 方針）。代わりに **Dokploy `DATABASE_URL` を必ず設定**して、フォールバックに到達させない |
| Phase 7+ 申し送り | コード修正で fail-fast 化（環境変数欠落 → 起動失敗）／旧 Render DB ロールパスワードの無効化は Render 解約（Phase 8）で自動消滅 |

### 4.2 C-2: `blueprints/mail/services.py:457,554` Brevo API キーのハードコード フォールバック

**実測（`/Users/kurinobu/motivation_app/blueprints/mail/services.py`・現行ファイル）**:

```python
brevo_api_key = os.environ.get('BREVO_API_KEY', 'xkeysib-ae0b...（実キー値は本書に転記しない。リポジトリ motivation_app/blueprints/mail/services.py:457,554 に存在）')
```

**注**: 実キー値は **GitHub Push Protection が検出するレベルの機密**。本書には伏字化して掲載し、実値はリポジトリ内（および Phase 7+ Owner ローテーション時の Brevo 管理画面）でのみ参照する。

| 観点 | 評価 |
|------|------|
| リスク | 実 Brevo API キーがリポジトリ内に存在。GitHub Visibility が Public であれば**既に漏洩済み**。Private でも Owner 退職時等のリスク |
| 漏洩有無の確定 | **未確認**（GitHub Visibility 未確認・git history も未確認） |
| Phase 6 対処 | **コードは触らない**（Owner 方針）。代わりに **Dokploy `BREVO_API_KEY` を必ず設定** ／ Brevo 管理画面の **Authorized IPs に `160.251.199.237` を追加**（YadOPERA 用に既追加済・追加作業不要）|
| Phase 7+ 申し送り | (1) GitHub Visibility 確認 → Public なら **即時 Brevo キーローテーション**／(2) コード修正で fail-fast 化／(3) 旧キーは git history から削除（git filter-repo・履歴改変は要慎重） |

### 4.3 参考: 既知の旧データ・問題なし

- `config.py:31` `GOOGLE_ANALYTICS_ID = 'G-VGZ9TTE1PY'` ハードコード → **公開値・問題なし**
- ルート直下に大量の `app.py.backup_*` `*.backup_*` バックアップファイル → Phase 6 スコープ外（cleanup は Owner 判断）

---

## 5. APScheduler 多重起動リスク（運用カバー済）

| 観点 | 評価 |
|------|------|
| リスク | `app.py:9` が `BackgroundScheduler` を import し起動時開始。Dokploy Swarm で **複数レプリカ**になるとスケジュールメールが多重送信される可能性 |
| Phase 6 対処 | (1) gunicorn `--workers 1` でプロセス内の多重化を防ぐ／(2) Dokploy Application で **レプリカ 1** を維持（Swarm の `--replicas 1`・Dokploy 既定） |
| Phase 7+ 申し送り | スループット要件が出たら、APScheduler を **別 Application（常駐ワーカー）** に分離して gunicorn 側で worker 数を増やせるようにする |

---

## 6. 大原則照合（事前確認）

| 大原則 | 本 Phase 6 6-D での扱い | 評価 |
|--------|------------------------|------|
| 1 根本解決 > 暫定 | C-1/C-2 は **本 Phase では暫定運用カバー**（Dokploy env 必須設定）／コード修正は Phase 7+ | ⚠️ 暫定（Owner 確認済・スコープ管理） |
| 2 シンプル構造 > 複雑 | Dockerfile は単一ステージ Python 3.12-slim | ✅ |
| 3 統一・同一化 > 特殊独自 | InfluBerry と同じベースイメージ・同じ起動コマンドパターン | ✅ |
| 4 具体的 > 一般 | 本書および Phase 6 手順書で全コマンド・全 env キーを具体的に明記 | ✅ |
| 5 安全確実 > 拙速 | YadOPERA 無影響確認を各 Step で実施／Phase 6 完了後に Owner 判断ローテーション | ✅ |
| 6 Docker 環境必須 | Dockerfile 新規追加 | ✅ |
| 7 LP は `main` + GitHub Pages | motivation_app は LP ではないため非該当 | — |
| 8 品質ゲートと証跡 | 本書（事前調査）／6-D 完了後の作業報告／Phase 6 完了チェック | ✅ |

---

## 7. 推奨方針（Phase 6 6-D 実行手順）

**Owner 方針確定済**: Render と同じ状態で載せ替え／動けば OK ／問題は証跡。コードは触らない。

### 7.1 Sub-Step 一覧

| Sub-Step | 内容 | 影響範囲 | Mac/VPS/Dokploy |
|----------|------|----------|------------------|
| 6-D-1 | Dockerfile 作成（`/Users/kurinobu/motivation_app/Dockerfile` 新規）| Mac ローカルのみ・push なし | Mac |
| 6-D-2 | Owner が Dockerfile 内容をレビュー → 承認 | — | （Owner 判断） |
| 6-D-3 | Mac で `git add Dockerfile && git commit && git push origin main` | GitHub `kurinobu/motivation_app` の main ブランチに 1 ファイル追加 | Mac |
| 6-D-4 | Dokploy GitHub App `Dokploy-air-edison` に `motivation_app` リポジトリを Repository access に追加 | Dokploy 設定・YadOPERA / InfluBerry 無影響 | Dokploy 画面 |
| 6-D-5 | Dokploy `air-edison/production` に Application `motivation-app-staging` 新規作成（Provider GitHub / Branch `main` / Build Path `/` / Build Type Dockerfile） | Dokploy 新規 Application | Dokploy 画面 |
| 6-D-6 | Environment Settings で **§3.4 の必須キーを全て設定**（C-1/C-2 フォールバックを到達させない運用カバー） | Dokploy 設定 | Dokploy 画面 |
| 6-D-7 | Domain 設定: `motivation-app-staging.local`（暫定 hostname・InfluBerry と同流派・大原則 3）／ Port は Dockerfile 既定の `5002`／HTTP のみ／Cert none | Dokploy Traefik | Dokploy 画面 |
| 6-D-8 | Deploy 実行 → Deploy ログで ImportError 等の起動失敗が無いか確認 | Dokploy / VPS コンテナ | Dokploy 画面 |
| 6-D-9 | Mac から 1 ブロックで疎通確認（YadOPERA 全 200 維持／InfluBerry 全 200 維持／motivation_app `Host: motivation-app-staging.local` でトップ HTML 取得） | Mac curl のみ（読み取り） | Mac |
| 6-D-10 | 証跡 `docs/evidence/20260525_phase6_motivation_app_complete.md` を新規作成・正本 Phase 6 完了チェックリストを更新 | docs のみ | Mac |

### 7.2 各 Sub-Step の安全担保

- 6-D-1〜6-D-3: Git push は Mac の **`kurinobu/motivation_app` のみ**。YadOPERA / InfluBerry の GitHub リポジトリには触らない
- 6-D-4: Dokploy GitHub App への repository access 追加は Read 権限のみ・既存リポジトリに影響なし
- 6-D-5〜6-D-7: Dokploy Application は **新規** ・既存 Application の設定は変更しない
- 6-D-6: Environment Settings の値は **`.env` から手で転記**（チャットには貼らない・秘密値は画面入力のみ）
- 6-D-8: Deploy 失敗時は **画面でロールバックボタンを押下** ／コードは触らない／同じ commit を再 Deploy
- 6-D-9: 全 curl は読み取り（GET）のみ・YadOPERA への影響なし

---

## 8. Phase 6 完了チェックリスト追加項目（証跡）

正本 [Phase 6 完了チェックリスト](../../maintenance/20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md#phase-6-完了チェックリスト) に以下を追加:

- [ ] 6-D-1: motivation_app に Dockerfile 追加・Mac で commit（push 前に Owner レビュー）
- [ ] 6-D-3: Mac から `kurinobu/motivation_app` `main` に push（commit hash を証跡に記録）
- [ ] 6-D-5: Dokploy Application `motivation-app-staging` 作成（Provider / Branch / Build / Domain Save 成功）
- [ ] 6-D-6: Environment Settings で必須 9 キー保存成功（**`DATABASE_URL` / `BREVO_API_KEY` を含む — 未設定だとハードコード フォールバック C-1/C-2 に到達するため必ず設定**）
- [ ] 6-D-8: Deploy Done・Swarm レプリカ 1/1
- [ ] 6-D-9: 疎通確認 — YadOPERA 全 200 維持／InfluBerry 全 200 維持／motivation_app `Host: motivation-app-staging.local` で 200 + トップ HTML 取得
- [ ] 6-D-10: 証跡 `20260525_phase6_motivation_app_complete.md` 作成

---

## 9. 申し送り（Phase 7・Phase 8 以降）

### Phase 7 着手前に Owner 判断が必要

| # | 項目 | 推奨アクション |
|---|------|---------------|
| F-1 | GitHub `kurinobu/motivation_app` Visibility 確認 | Web UI で確認（1 分）／Public なら F-2 を最優先 |
| F-2 | Brevo API キー ローテーション | Brevo 管理画面で旧キー無効化 → 新キー発行 → Dokploy `BREVO_API_KEY` を新値に更新 → Deploy 再実行 |
| F-3 | C-1 / C-2 コード修正（fail-fast 化） | `app.py:52` / `services.py:457,554` のフォールバックを削除し、環境変数欠落時は `raise RuntimeError(...)` で起動失敗させる |
| F-4 | git history から旧 Brevo キー削除 | git filter-repo（履歴改変・要慎重・別 Phase で検討） |
| F-5 | DNS 確定（Phase 7） | `staging.motivation.<domain>` 等を ConoHa VPS に向け、Dokploy Domain Host を切替（暫定 `motivation-app-staging.local` → 本ドメイン）+ TLS letsencrypt |
| F-6 | Render DB ロールパスワード対応 | Phase 8 で Render 解約により自動消滅・並行作業不要 |

### Phase 8（Render 解約）前に確認

- ConoHa Postgres `motivation_app` で **Phase 6-B リストア済テーブル 9 件**が確かに本番運用に必要な全データを含んでいるか（差分監査）— Owner 判断
- Render 側でメール送信ログ等のエクスポート要否（Brevo 側に履歴があるため通常不要）

---

## 10. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-05-25 17:32 | 初版（Phase 6 6-D 着手前の事前調査・C-1/C-2 発見・Owner 方針「Render と同じ状態で載せ替え」に基づく推奨手順 6-D-1〜6-D-10 策定） |
| 2026-05-26 19:10 | §0 訂正履歴を追加：M-1 (C-3 見落とし) / M-2 (head_limit による env キー取りこぼし) / M-3 (`.env` 内 `SECRET_KEY` 不在を未確認のまま指示) / M-4 (bash grep 方式の env パース指示) を記録。Owner 指摘と私の誓約を明記。訂正後の事実（C-3 新規発見・環境変数表 A/B/C 分類・dotenv パーサー版テンプレ）を追記。初版（§1〜§10）は履歴保全のため改変せず残置。 |
