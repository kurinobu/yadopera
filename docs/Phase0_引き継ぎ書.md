# Phase 0 引き継ぎ書

**作成日**: 2025年11月25日  
**最終更新日**: 2025年11月26日  
**バージョン**: v2.1  
**対象**: やどぺら Phase 0（準備期間）引き継ぎ  
**進捗**: ステップ10-1完了（10/11ステップ、90.9%）

---

## 1. プロジェクト概要

### 1.1 プロジェクト情報

- **プロジェクト名**: やどぺら（Yadopera）
- **説明**: 小規模宿泊施設向けAI多言語自動案内システム
- **GitHubリポジトリ**: https://github.com/kurinobu/yadopera.git
- **ブランチ**: `main`
- **現在のフェーズ**: Phase 0（準備期間）

### 1.2 技術スタック

**バックエンド**:
- FastAPI 0.109.0
- Python 3.11
- PostgreSQL 15（pgvector拡張）
- Redis 7.2
- Alembic 1.13.1

**フロントエンド**:
- Vue.js 3.4+
- TypeScript 5.3+
- Vite 5.0+
- Tailwind CSS 3.4+

**インフラ**:
- Docker & Docker Compose
- Render.com（本番環境予定）

---

## 2. 進捗状況

### 2.1 完了したステップ

| ステップ | 完了日 | 主な成果物 | コミット |
|---------|--------|-----------|---------|
| ステップ1: GitHub リポジトリ作成・初期設定 | 2025-11-25 | `.gitignore`, リポジトリ初期化 | `9781b7c` |
| ステップ2: プロジェクト構造作成 | 2025-11-25 | ディレクトリ構造 | `c5386db` |
| ステップ3: Docker環境セットアップ | 2025-11-25 | `docker-compose.yml`, Dockerfiles | `6769dca` |
| ステップ4: Backend初期設定 | 2025-11-25 | `requirements.txt`, `main.py`, `config.py`, Alembic | 最新 |
| ステップ5: Frontend初期設定 | 2025-11-25 | `package.json`, `vite.config.ts`, `tsconfig.json`等 | `640a0f6` |
| ステップ6: データベース・Redis環境構築確認 | 2025-11-25 | PostgreSQL + pgvector、Redis動作確認 | `640a0f6` |
| ステップ7: 全サービス起動確認 | 2025-11-25 | Backend/Frontend動作確認完了 | `640a0f6` |
| ステップ8: README.md作成 | 2025-11-25 | プロジェクトドキュメント作成 | `1e237a6` |
| ステップ9: 外部サービス準備 | 2025-11-25 | OpenAI API キー設定、準備状況ドキュメント化 | `41dfac0` |
| ステップ10-1: ランディングページ実装・改善 | 2025-11-26 | LP実装、PoC説明追加、カラーリング変更、Formspree実装、オンライン説明会セクションコメントアウト | 未コミット |

### 2.2 未完了のステップ

| ステップ | ステータス | 優先度 | 予定工数 |
|---------|----------|--------|---------|
| ステップ10-2: Vercelデプロイ | ⏳ 未着手 | 高 | 30分 |
| ステップ10-3: カスタムドメイン設定 | ⏳ 未着手 | 高 | 10分 |
| ステップ10-4: Google Analytics設定 | ⏳ 未着手 | 高 | 30分 |
| ステップ10-5: HTMLに測定ID設定 | ⏳ 未着手 | 高 | 10分 |
| ステップ10-6: 動作確認 | ⏳ 未着手 | 高 | 10分 |
| ステップ11: やどびと多言語優先度アンケート実施 | ⏳ 未着手 | 低 | 2時間 |

**進捗率**: 90.9%（ステップ10-1完了、ステップ10-2〜10-6未実施）

---

## 3. 実装済みファイル一覧

### 3.1 ルートディレクトリ

```
yadopera/
├── .gitignore                    ✅ 作成済み
├── docker-compose.yml            ✅ 作成済み
├── README.md                     ✅ 作成済み（ステップ8）
└── docs/                         ✅ 既存
```

### 3.2 Backend

```
backend/
├── Dockerfile                    ✅ 作成済み
├── .dockerignore                 ✅ 作成済み
├── requirements.txt              ✅ 作成済み
├── .env.example                  ✅ 作成済み
├── .env                          ✅ 作成済み（ローカルのみ、Git管理外）
├── alembic.ini                   ✅ 作成済み
├── alembic/
│   ├── __init__.py               ✅ 作成済み
│   ├── env.py                    ✅ 作成済み
│   ├── script.py.mako            ✅ 作成済み
│   └── versions/
│       └── 001_enable_pgvector.py ✅ 作成済み
└── app/
    ├── __init__.py               ✅ 作成済み
    ├── main.py                   ✅ 作成済み
    ├── api/
    │   └── __init__.py           ✅ 作成済み
    └── core/
        ├── __init__.py           ✅ 作成済み
        └── config.py             ✅ 作成済み
```

### 3.3 Frontend

```
frontend/
├── Dockerfile                    ✅ 作成済み
├── .dockerignore                 ✅ 作成済み
├── package.json                  ✅ 作成済み（ステップ5）
├── .env.example                  ✅ 作成済み（ステップ5）
├── vite.config.ts                ✅ 作成済み（ステップ5）
├── tsconfig.json                 ✅ 作成済み（ステップ5）
├── tsconfig.node.json            ✅ 作成済み（ステップ5）
├── tailwind.config.js            ✅ 作成済み（ステップ5）
├── postcss.config.js             ✅ 作成済み（ステップ5）
├── index.html                    ✅ 作成済み（ステップ5）
├── .eslintrc.cjs                 ✅ 作成済み（ステップ5）
├── public/                       ✅ ディレクトリ作成済み
└── src/
    ├── main.ts                   ✅ 作成済み（ステップ5）
    ├── App.vue                   ✅ 作成済み（ステップ5）
    ├── style.css                 ✅ 作成済み（ステップ5）
    ├── vite-env.d.ts             ✅ 作成済み（ステップ5）
    └── components/               ✅ ディレクトリ作成済み
```

### 3.4 Landing Page

```
landing/
├── index.html                    ✅ 作成済み（ステップ10-1）
├── vercel.json                   ✅ 作成済み（ステップ10-1）
├── README.md                     ✅ 作成済み（ステップ10-1）
├── analytics-setup.md            ✅ 作成済み（ステップ10-1）
├── BROWSER_TEST.md               ✅ 作成済み（ステップ10-1）
└── index.html.backup_*           ✅ バックアップファイル（複数）
```

**ステップ10-1の改善内容**:
- PoC説明追加（「PoCとは」サブセクション）
- カラーリング変更（#38b7ee、#0c4a6e）
- Formspree実装（フォームID: meowddgp）
- オンライン説明会セクションコメントアウト

---

## 4. 環境変数設定

### 4.1 Backend環境変数（`.env.example`）

```env
# Database
DATABASE_URL=postgresql://yadopera_user:yadopera_password@postgres:5432/yadopera

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# App
ENVIRONMENT=development
DEBUG=True

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4.2 設定状況

- ✅ `backend/.env`作成済み（実際の値設定済み）
- ✅ `frontend/.env.example`作成済み
- ✅ OpenAI API キー設定済み（ステップ9）

---

## 5. Docker環境

### 5.1 docker-compose.yml構成

- **postgres**: PostgreSQL 15（pgvector拡張）
  - ポート: 5433（ホスト）→ 5432（コンテナ）
  - ユーザー: `yadopera_user`
  - パスワード: `yadopera_password`
  - データベース: `yadopera`

- **redis**: Redis 7.2-alpine
  - ポート: 6379

- **backend**: FastAPI
  - ポート: 8000
  - ホットリロード有効

- **frontend**: Vite開発サーバー
  - ポート: 5173
  - ホットリロード有効

### 5.2 起動コマンド

```bash
# 全サービス起動
docker-compose up -d

# バックグラウンド起動
docker-compose up -d

# 特定サービスのみ起動（例: PostgreSQL + Redis）
docker-compose up -d postgres redis

# 停止
docker-compose down

# ボリュームも削除
docker-compose down -v
```

### 5.3 動作確認済み

- ✅ PostgreSQL接続確認（PostgreSQL 15.15）
- ✅ pgvector拡張有効化確認（vector 0.8.1）
- ✅ Redis接続確認（Redis 7.2.12）
- ✅ Backend動作確認（http://localhost:8000）
- ✅ Frontend動作確認（http://localhost:5173）
- ✅ Swagger UI表示確認（http://localhost:8000/docs）

---

## 6. 次のセッションで実施するステップ

### 6.1 ステップ10-1: ランディングページ実装・改善 ✅ 完了

**完了日**: 2025-11-26

**成果物**:
- `landing/index.html`: 12セクション構成のLP（ヒーロー、課題提起、コンセプト、3つの価値、仕組み、導入効果、PoC募集、選ばれる理由、料金、FAQ、運営者情報、最終CTA）
- `landing/vercel.json`: Vercelデプロイ設定
- `landing/README.md`: デプロイ手順とカスタマイズ方法
- `landing/analytics-setup.md`: Google Analytics設定ガイド
- `landing/BROWSER_TEST.md`: ブラウザテストガイド
- **PoC説明追加**: PoCセクションに「PoCとは」サブセクションを追加（契約内容、関係性、期待される協力内容）
- **カラーリング変更**: ヒーローセクション `#38b7ee`、フッター `#0c4a6e`、`#38bdf8` → `#38b7ee` にすべて置き換え
- **Formspree実装**: フォームID `meowddgp`、action属性設定、method属性 `POST`、JavaScript修正完了
- **オンライン説明会セクション**: コメントアウト（説明会予約リンクが未設定のため）
- レスポンシブデザイン対応（Tailwind CSS CDN使用）
- Google Analytics 4実装（測定ID未設定、Vercelデプロイ後に設定）

**ブラウザテスト結果（2025-11-26）**:
- ✅ テストURL: http://localhost:8001
- ✅ ページ表示: 正常
- ✅ セクション表示: 11セクション表示（オンライン説明会セクションはコメントアウト）
- ✅ レスポンシブデザイン: 動作確認済み
- ✅ ナビゲーション: 動作確認済み
- ✅ カラーリング: 正常（#38b7ee、#0c4a6e）
- ✅ フォーム送信テスト: Formspree連携確認済み
- ✅ 構文チェック: 正常

**完了した改善**:
1. ✅ **PoC説明追加**: PoCセクションに「PoCとは」サブセクションを追加
2. ✅ **カラーリング変更**: 指定色（#38b7ee、#0c4a6e）に変更
3. ✅ **Formspree実装**: フォーム送信機能をFormspreeに接続（フォームID: meowddgp）
4. ✅ **オンライン説明会セクション**: コメントアウト（404エラー回避）

### 6.2 ステップ10-2〜10-6: ランディングページデプロイ・Google Analytics設定 ⏳ 未実施

**優先度**: 高（最優先）  
**合計所要時間**: 約1時間30分

**ステップ10-2: Vercelデプロイ**（30分）
- Vercelアカウント作成・GitHub連携
- プロジェクト作成（Root Directory: `landing`）
- デプロイ実行

**ステップ10-3: カスタムドメイン設定**（10分）
- `tabipera.com` を追加
- DNS設定実施
- SSL証明書自動設定

**ステップ10-4: Google Analytics 4プロパティ作成**（30分）
- プロパティ作成（ウェブサイトURL: `https://tabipera.com`）
- 測定ID取得（`G-XXXXXXXXXX`）

**ステップ10-5: HTMLに測定ID設定**（10分）
- `landing/index.html`の`G-XXXXXXXXXX`を実際の測定IDに置き換え
- コミット・プッシュ
- Vercel自動再デプロイ

**ステップ10-6: 動作確認**（10分）
- `https://tabipera.com` でアクセス確認
- Google Analyticsのリアルタイムレポートで確認

**詳細**: `docs/Phase0_ステップ10_正しい実施順序.md` を参照

### 6.3 ステップ11: やどびと多言語優先度アンケート実施（優先度: 低、並行実施可能）

**タスク**:
1. アンケート設計（質問項目決定）
2. フォーム作成（Google Forms等）
3. 配信準備（やどびとユーザーリスト、メール文面）
4. アンケート配信
5. 結果集計（回答期限後、Phase 1開発中に実施）

**所要時間**: 2時間（配信まで）

**目的**: Phase 2の言語優先順位決定

---

## 7. 重要な注意事項

### 7.1 環境変数

- **`.env`ファイルはGit管理しない**（`.gitignore`で除外済み）
- `.env.example`をコピーして`.env`を作成し、実際の値を設定
- `SECRET_KEY`は強力なランダム文字列を生成（例: `openssl rand -hex 32`）

### 7.2 Docker

- 初回起動時は依存関係のインストールに時間がかかる
- ボリュームを使用しているため、データは永続化される
- `docker-compose down -v`でボリュームも削除される（注意）

### 7.3 Alembic

- マイグレーション実行前に`backend/.env`で`DATABASE_URL`を設定
- 初回マイグレーション: `alembic upgrade head`
- マイグレーション確認: `alembic current`

### 7.4 依存関係

- Backend: `requirements.txt`に記載済み
- Frontend: `package.json`に記載済み

---

## 8. トラブルシューティング

### 8.1 よくある問題

**問題**: Docker Composeでサービスが起動しない
- **解決策**: ログを確認（`docker-compose logs <service_name>`）
- ポートが既に使用されている場合は変更

**問題**: PostgreSQL接続エラー
- **解決策**: `DATABASE_URL`の形式を確認
- コンテナ名が正しいか確認（`postgres`）

**問題**: Alembicマイグレーションエラー
- **解決策**: `DATABASE_URL`が正しく設定されているか確認
- pgvector拡張が有効化されているか確認

**問題**: Frontendが表示されない
- **解決策**: Frontendコンテナが起動していることを確認
- ログを確認（`docker-compose logs frontend`）

---

## 9. ブランチ戦略とデプロイ戦略

### 9.1 現在のブランチ戦略

**計画されているブランチ**:
- `main`: 本番環境用ブランチ
- `develop`: 開発用ブランチ
- `feature/*`: 機能開発用ブランチ

**現在の状況**:
- 初期ブランチ: `main`
- `develop`ブランチは未作成

### 9.2 デプロイ戦略（現状）

**現在の設計**（アーキテクチャ設計書v0.3より）:
- デプロイフロー: `git push origin main` → Render.com（自動デプロイ）
- ステージング環境の計画: **明記されていない**

**懸念事項**:
- テストケースをデプロイする場合、直接`main`にデプロイする必要がある
- ステージング環境がないため、本番環境へのリスクが高い

### 9.3 推奨される改善案

**オプション1: ステージング環境の追加**

```
ブランチ構成:
- `main`: 本番環境（https://tabipera.com）
- `develop`: ステージング環境（https://staging.tabipera.com）
- `feature/*`: 機能開発用

デプロイフロー:
1. feature/* → develop（マージ）
2. develop → Render.com ステージング環境（自動デプロイ）
3. テスト完了後、develop → main（マージ）
4. main → Render.com 本番環境（自動デプロイ）
```

**オプション2: サブドメインでのテストURL作成**

```
環境構成:
- 本番: https://tabipera.com
- ステージング: https://staging.tabipera.com
- 開発: https://dev.tabipera.com（オプション）

ブランチ構成:
- `main`: 本番環境
- `develop`: ステージング環境
- `feature/*`: 機能開発用

Render.com設定:
- 本番サービス: mainブランチ → tabipera.com
- ステージングサービス: developブランチ → staging.tabipera.com
```

**推奨**: オプション2（サブドメインでのテストURL作成）を推奨します。

**理由**:
1. リスク分散: 本番環境への影響を最小化
2. テスト環境の独立性: ステージング環境で十分なテストが可能
3. Render.comの機能: 複数のサービスを作成可能
4. コスト: Render.comの無料枠または低コストプランで対応可能

**実装時期**: Phase 1（MVP開発）開始前に決定・実装推奨

---

## 10. 参考資料

### 10.1 ドキュメント

- **Phase 0ステップ計画**: `docs/Phase0_ステップ計画.md`
- **Phase 0進捗状況**: `docs/Phase0_進捗状況.md`
- **Phase 0実装整合性分析レポート**: `docs/Phase0_実装整合性分析レポート.md`
- **Phase 0外部サービス準備状況**: `docs/Phase0_外部サービス準備状況.md`
- **Phase 0ステップ10正しい実施順序**: `docs/Phase0_ステップ10_正しい実施順序.md`
- **Phase 0次のステップ推奨案**: `docs/Phase0_次のステップ_推奨案.md`
- **Phase 0フォーム送信方法調査分析**: `docs/Phase0_フォーム送信方法_調査分析レポート.md`
- **要約定義書**: `docs/yadopera-v03-summary.md`
- **アーキテクチャ設計書**: `docs/やどぺら_v0.3_アーキテクチャ設計書.md`

### 10.2 外部リンク

- GitHubリポジトリ: https://github.com/kurinobu/yadopera.git
- Render.com: アカウント準備済み（Render Pro）

---

## 11. 次のセッション開始時のチェックリスト

### 11.1 環境確認

- [ ] Gitリポジトリの状態確認（`git status`）
- [ ] 最新のコミット確認（`git log --oneline -5`）
- [ ] Dockerが起動しているか確認（`docker ps`）

### 11.2 サービス起動確認

- [ ] `docker-compose up -d`で全サービス起動
- [ ] Backend動作確認（http://localhost:8000）
- [ ] Frontend動作確認（http://localhost:5173）

---

## 12. コミット履歴

### 12.1 主要コミット

```
41dfac0 Add Phase 0 step 9: External services preparation
1e237a6 Add README.md: Project documentation and setup guide
640a0f6 Add Phase 0 steps 5-7: Frontend setup, DB/Redis verification, and full service startup
6769dca Add Docker environment setup (docker-compose.yml, Dockerfiles)
c5386db Add project directory structure
9781b7c Initial commit: Add .gitignore
```

### 12.2 ブランチ

- **main**: 現在のブランチ（本番環境用）
- ブランチ戦略: `main`, `develop`, `feature/*`（計画）

---

## 13. 連絡先・問い合わせ

- **開発者**: Air
- **ブログ**: https://air-edison.com
- **Twitter**: @kbqjp

---

---

## 19. Phase 1 Week 4 ステージング環境構築 失敗記録

**記録日**: 2025年11月28日  
**フェーズ**: Phase 1 Week 4（統合・テスト・ステージング環境構築）  
**結果**: ❌ **完全失敗** - デプロイに失敗し、時間を浪費した

---

### 19.1 実施内容

#### 19.1.1 Railway Hobby設定（中途半端）

**実施内容**:
1. PostgreSQLサービス追加
   - サービス名: `yadopera-postgres-staging`
   - 最初に通常のPostgreSQLサービスを作成
   - pgvector拡張がインストールされていないことを確認
   - pgvector-pg17テンプレートで新しいPostgreSQLサービスを作成
   - **しかし、pgvector拡張は依然としてインストールされていない状態**

2. Redisサービス追加
   - サービス名: `yadopera-redis-staging`
   - Redisサービスは作成された
   - 接続URLは取得済み

**問題点**:
- ⚠️ **pgvector拡張が有効化されていない**: pgvector-pg17テンプレートを使用したが、拡張がインストールされていない
- ⚠️ **設定が中途半端**: PostgreSQLサービスは作成されたが、pgvector拡張が使用できない状態

**接続情報**:
- `DATABASE_PUBLIC_URL`: `postgresql://postgres:q2qvotspe3muf84hanuy5lw6eascqt82@yamanote.proxy.rlwy.net:15647/railway`
- `REDIS_PUBLIC_URL`: `redis://default:QIpOCNjyhqyHYoaGBUWWaALyuWmVGYjd@shuttle.proxy.rlwy.net:28858`

---

#### 19.1.2 Render.com Pro設定（中途半端・未完了）

**実施内容**:
1. Web Service作成
   - サービス名: `yadopera-backend-staging`
   - Python 3.11.8を指定（環境変数`PYTHON_VERSION`）
   - デプロイは失敗

2. 環境変数設定
   - `DATABASE_URL`: Railway PostgreSQL接続URL（`postgresql+asyncpg://`形式）
   - `REDIS_URL`: Railway Redis接続URL
   - `OPENAI_API_KEY`: OpenAI APIキー
   - `SECRET_KEY`: 生成済み
   - その他の環境変数も設定済み

**問題点**:
- ❌ **デプロイが失敗**: `ModuleNotFoundError: No module named 'asyncpg'`エラーが発生
- ⚠️ **設定が中途半端**: Web Serviceは作成されたが、デプロイに失敗している
- ⚠️ **エラーが解決できていない**: 暫定的解決方法を試したが、依然として失敗

---

### 19.2 エラー対応の経緯

#### 19.2.1 最初のエラー: Python 3.13.4でのpydantic-coreビルドエラー

**エラー内容**:
```
error: failed to create directory `/usr/local/cargo/registry/cache/index.crates.io-1949cf8c6b5b557f`
Caused by: Read-only file system (os error 30)
```

**対応**:
- Python 3.11.8を指定（環境変数`PYTHON_VERSION`）
- **結果**: Pythonバージョンは変更されたが、次のエラーが発生

---

#### 19.2.2 2番目のエラー: asyncpgモジュールが見つからない

**エラー内容**:
```
ModuleNotFoundError: No module named 'asyncpg'
```

**分析**:
- `requirements.txt`に`asyncpg`パッケージが含まれていない
- `alembic/env.py`が`postgresql+asyncpg://`形式のURLを使用しているが、`asyncpg`がインストールされていない

**対応**:
- `requirements.txt`に`asyncpg==0.29.0`を追加
- **暫定的解決方法**として提示
- **「エラーは解決する」と断言したが、実際には解決しなかった**

**結果**: ❌ **デプロイは依然として失敗**

---

### 19.3 問題の根本原因

#### 19.3.1 外部サービスの問題解決率: 0%

**現状**:
- Railwayでのpgvector拡張の有効化がうまくいかなかった
- Render.comでのデプロイエラーが複数回発生した
- 外部サービスの最新の仕様やUIを十分に把握できていない
- **すべての外部サービス設定が失敗している**

#### 19.3.2 暫定的解決方法の誤り

**問題点**:
- 「暫定的解決方法でエラーは解決する」と断言したが、実際には解決しなかった
- 根本原因の分析が不十分だった
- 問題を複雑にした

**経緯**:
1. エラーが発生
2. 原因を分析（3つの原因を特定）
3. 「暫定的解決方法でエラーは解決する」と断言
4. `requirements.txt`に`asyncpg==0.29.0`を追加
5. **デプロイは依然として失敗**

---

### 19.4 現在の状態

#### 19.4.1 Railway Hobby設定

**状態**: ⚠️ **中途半端**
- PostgreSQLサービス: 作成済み（pgvector拡張は未インストール）
- Redisサービス: 作成済み
- 接続URL: 取得済み

#### 19.4.2 Render.com Pro設定

**状態**: ❌ **未完了・エラー未解決**
- Web Service: 作成済み
- 環境変数: 設定済み
- **デプロイ: 失敗（エラー未解決）**

#### 19.4.3 エラー状態

**状態**: ❌ **エラー未解決**
- `ModuleNotFoundError: No module named 'asyncpg'`エラーが発生
- 暫定的解決方法を試したが、依然として失敗
- 根本原因の解決が必要

---

### 19.5 教訓

#### 19.5.1 外部サービス設定について

- **外部サービスの問題解決率は0%**: すべての外部サービス設定が失敗している
- **最新の仕様やUIを十分に把握できていない**: 調査が不十分だった
- **暫定的解決方法を過信しない**: 根本原因の解決が必要

#### 19.5.2 エラー対応について

- **「エラーは解決する」と断言しない**: 実際に解決するまで断言しない
- **根本原因の分析を徹底する**: 表面的な対応ではなく、根本原因を特定する
- **問題を複雑にしない**: シンプルな解決方法を優先する

---

### 19.6 次のセッションでの対応

#### 19.6.1 優先事項

1. **エラーの根本原因を特定する**
   - デプロイログを詳細に分析
   - 実際のエラー内容を確認
   - 根本原因を特定

2. **外部サービスの設定を再検討する**
   - Railwayのpgvector拡張の有効化方法を再調査
   - Render.comのデプロイエラーの根本原因を特定
   - 正しい設定方法を確認

3. **暫定的解決方法を避ける**
   - 根本原因の解決を優先
   - 問題を複雑にしない

---

**Document Version**: v2.4  
**Author**: Air  
**Last Updated**: 2025-11-28  
**Status**: Phase 0 進行中（ステップ10-1完了、ステップ10-2〜10-6未実施、ステップ11未実施）、Phase 1 Week 4 ステージング環境構築失敗
