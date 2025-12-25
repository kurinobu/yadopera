# YadOPERA

**YadOPERA** = 「宿」 + 「ぺらぺら（流暢に話す）」

小規模宿泊施設向け外国人ゲスト対応自動化SaaS。QRコードをスマホで読み取るだけで、AIが24時間多言語自動応答。

## 📋 目次

- [プロジェクト概要](#プロジェクト概要)
- [技術スタック](#技術スタック)
- [開発環境セットアップ](#開発環境セットアップ)
- [環境変数設定](#環境変数設定)
- [サービス起動](#サービス起動)
- [API エンドポイント](#api-エンドポイント)
- [トラブルシューティング](#トラブルシューティング)
- [開発規約](#開発規約)
- [関連ドキュメント](#関連ドキュメント)

## プロジェクト概要

### サービス概要

小規模宿泊施設（ゲストハウス・ホステル、15-60床）向けの外国人ゲスト対応自動化システムです。

**ゲスト側の特徴**:
- アプリ不要、QRコードのみでアクセス
- 好きな言語で24時間質問可能
- 平均3秒以内レスポンス
- ダークモード対応
- デバイス間セッション統合

**宿側の特徴**:
- 外国人ゲスト対応70%自動化（MVP目標）
- 月額¥3,980〜 または 従量課金¥1,980+¥30/質問
- 初期費用¥0
- 20-30件FAQテンプレート提供
- 未解決質問からワンクリックFAQ追加

### 現在のフェーズ

**Phase 0（準備期間）** - 進捗: 7/11ステップ完了（63.6%）

詳細は [`docs/Phase0_進捗状況.md`](docs/Phase0_進捗状況.md) を参照してください。

## 技術スタック

### バックエンド

- **FastAPI** 0.109.0 - Python Webフレームワーク
- **Python** 3.11+
- **SQLAlchemy** 2.0.25 - ORM（async対応）
- **Alembic** 1.13.1 - データベースマイグレーション
- **PostgreSQL** 15+ - データベース（pgvector拡張）
- **Redis** 7.2+ - キャッシュ・セッション管理
- **OpenAI API** - GPT-4o-mini、text-embedding-3-small

### フロントエンド

- **Vue.js** 3.4+ - フロントエンドフレームワーク
- **TypeScript** 5.3+ - 型安全性
- **Vite** 5.0+ - ビルドツール
- **Tailwind CSS** 3.4+ - CSSフレームワーク
- **Pinia** 2.1+ - 状態管理
- **Axios** 1.6+ - HTTPクライアント
- **Vite PWA Plugin** 0.19+ - PWA対応

### インフラ

- **Docker & Docker Compose** - コンテナ環境
- **Render.com** - 本番環境（予定）
- **Cloudflare** - CDN、DDoS保護（予定）

## 開発環境セットアップ

### 前提条件

- Docker Desktop がインストールされていること
- Git がインストールされていること

### セットアップ手順

1. **リポジトリのクローン**

```bash
git clone https://github.com/kurinobu/yadopera.git
cd yadopera
```

2. **環境変数の設定**

詳細は [環境変数設定](#環境変数設定) を参照してください。

3. **Docker Composeでサービス起動**

```bash
docker-compose up -d
```

初回起動時は、依存関係のインストールに時間がかかります。

4. **動作確認**

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Swagger UI: http://localhost:8000/docs

## 環境変数設定

### Backend環境変数

`backend/.env.example` をコピーして `backend/.env` を作成し、実際の値を設定してください。

```bash
cp backend/.env.example backend/.env
```

#### 必須環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `DATABASE_URL` | PostgreSQL接続URL | `postgresql://yadopera_user:yadopera_password@postgres:5432/yadopera` |
| `REDIS_URL` | Redis接続URL | `redis://redis:6379/0` |
| `OPENAI_API_KEY` | OpenAI APIキー | `sk-...` |
| `SECRET_KEY` | JWT署名用シークレットキー | ランダム文字列（`openssl rand -hex 32`で生成） |

#### オプション環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `ALGORITHM` | `HS256` | JWTアルゴリズム |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | アクセストークン有効期限（分） |
| `ENVIRONMENT` | `development` | 環境（development/production） |
| `DEBUG` | `True` | デバッグモード |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | CORS許可オリジン（カンマ区切り） |

### Frontend環境変数

`frontend/.env.example` をコピーして `frontend/.env` を作成してください（開発環境では通常不要）。

```bash
cp frontend/.env.example frontend/.env
```

| 変数名 | 説明 | デフォルト値 |
|--------|------|------------|
| `VITE_API_BASE_URL` | Backend APIのベースURL | `http://localhost:8000` |
| `VITE_APP_NAME` | アプリケーション名 | `YadOPERA` |

## サービス起動

### 全サービス起動

```bash
docker-compose up -d
```

### 特定サービスのみ起動

```bash
# PostgreSQL + Redisのみ
docker-compose up -d postgres redis

# Backendのみ（PostgreSQL + Redisが起動している前提）
docker-compose up -d backend
```

### ログ確認

```bash
# 全サービスのログ
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f backend
docker-compose logs -f frontend
```

### サービス停止

```bash
# サービス停止（データは保持）
docker-compose down

# ボリュームも削除（データも削除される）
docker-compose down -v
```

## API エンドポイント

### ゲスト側API

- `GET /api/v1/facility/{slug}` - 施設情報取得
- `POST /api/v1/chat` - チャットメッセージ送信
- `GET /api/v1/chat/history/{session_id}` - 会話履歴取得
- `POST /api/v1/chat/feedback` - ゲストフィードバック送信
- `POST /api/v1/session/link` - セッション統合
- `GET /api/v1/session/token/{token}` - トークン検証

### 管理側API

- `POST /api/v1/auth/login` - ログイン
- `POST /api/v1/auth/logout` - ログアウト
- `GET /api/v1/admin/dashboard` - ダッシュボードデータ
- `GET/POST/PUT/DELETE /api/v1/admin/faqs` - FAQ管理
- `GET /api/v1/admin/overnight-queue` - 夜間対応キュー
- `GET /api/v1/admin/feedback-stats` - フィードバック統計

詳細なAPI仕様は Swagger UI（http://localhost:8000/docs）を参照してください。

## トラブルシューティング

### Docker Composeでサービスが起動しない

**問題**: コンテナが起動しない、またはすぐに停止する

**解決策**:
1. ログを確認する
   ```bash
   docker-compose logs <service_name>
   ```
2. ポートが既に使用されている場合は、`docker-compose.yml`のポート番号を変更する
3. Docker Desktopが起動していることを確認する

### PostgreSQL接続エラー

**問題**: `DATABASE_URL`の接続エラー

**解決策**:
1. `DATABASE_URL`の形式を確認する
   - 形式: `postgresql://user:password@host:port/database`
   - Docker Compose内では `postgres` がホスト名
2. PostgreSQLコンテナが起動していることを確認する
   ```bash
   docker-compose ps postgres
   ```
3. コンテナ名が正しいか確認する（`postgres`）

### pgvector拡張エラー

**問題**: Alembicマイグレーションでpgvector拡張エラー

**解決策**:
1. PostgreSQLコンテナが `pgvector/pgvector:pg15` イメージを使用していることを確認する
2. 手動で拡張を有効化する
   ```bash
   docker-compose exec postgres psql -U yadopera_user -d yadopera -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

### Redis接続エラー

**問題**: Redis接続できない

**解決策**:
1. Redisコンテナが起動していることを確認する
   ```bash
   docker-compose ps redis
   ```
2. 接続確認
   ```bash
   docker-compose exec redis redis-cli ping
   # 応答: PONG
   ```

### Frontendが表示されない

**問題**: `http://localhost:5173` にアクセスできない

**解決策**:
1. Frontendコンテナが起動していることを確認する
   ```bash
   docker-compose ps frontend
   ```
2. ログを確認する
   ```bash
   docker-compose logs frontend
   ```
3. ポート5173が使用可能か確認する

### 環境変数が読み込まれない

**問題**: `backend/.env`の設定が反映されない

**解決策**:
1. `.env`ファイルが正しい場所にあることを確認する（`backend/.env`）
2. 環境変数の形式を確認する（`KEY=value`、スペースなし）
3. Backendコンテナを再起動する
   ```bash
   docker-compose restart backend
   ```

## 開発規約

### 重要な原則

**⚠️ Docker環境必須の原則**

**Dockerを使わない修正もテストも意味がない**

- すべての修正・テストはDocker環境（docker-compose）で実行する
- ローカル環境で直接実行した修正やテストは無効であり、再実施が必要
- Docker環境での動作確認が完了してから、ステージング環境へのデプロイを検討する
- この原則は、環境の違いによる不具合を防ぎ、本番環境に近い状態での検証を保証するために必須

詳細は [`docs/Summary/yadopera-v03-summary.md`](docs/Summary/yadopera-v03-summary.md) の「0. 大原則（開発・実装の基本方針）」セクションを参照してください。

### ブランチ戦略

**採用戦略**: オプション2（サブドメインでのテストURL作成）

- `main`: 本番環境用ブランチ
  - URL: `https://yadopera.com`
  - データベース: Render.com PostgreSQL（Managed）
  - Redis: Redis Cloud（External）
- `develop`: ステージング環境用ブランチ
  - URL: `https://staging.yadopera.com`
  - データベース: Railway Hobby PostgreSQL（契約済み）
  - Redis: Railway Hobby Redis（契約済み）
- `feature/*`: 機能開発用ブランチ

**デプロイフロー**:
1. `feature/*` → `develop`（マージ）
2. `develop` → Render.com ステージング環境（自動デプロイ）
3. テスト完了後、`develop` → `main`（マージ）
4. `main` → Render.com 本番環境（自動デプロイ）

### コミットメッセージ

- プレフィックスを使用: `Add`, `Fix`, `Update`, `Refactor`, `Docs`
- 例: `Add Phase 0 steps 5-7: Frontend setup, DB/Redis verification`

### コードスタイル

- **Backend**: PythonのPEP 8に準拠
- **Frontend**: ESLint、Prettierを使用

詳細は各ディレクトリの設定ファイルを参照してください。

### デプロイ環境

**ステージング環境**:
- 実装フェーズ: Phase 1 Week 4
- 目的: 開発・テスト用
- データベース: Railway Hobby PostgreSQL（契約済み）

**本番環境**:
- 実装フェーズ: Phase 4（本格展開準備）
- 目的: 本番運用
- データベース: Render.com PostgreSQL（Managed）

詳細は [`docs/やどぺら_v0.3_アーキテクチャ設計書.md`](docs/やどぺら_v0.3_アーキテクチャ設計書.md) の「14. デプロイメント」セクションを参照してください。

## 関連ドキュメント

### プロジェクトドキュメント

- [Phase 0 ステップ計画](docs/Phase0_ステップ計画.md)
- [Phase 0 進捗状況](docs/Phase0_進捗状況.md)
- [Phase 0 引き継ぎ書](docs/Phase0_引き継ぎ書.md)
- [Phase 0 実装整合性分析レポート](docs/Phase0_実装整合性分析レポート.md)

### 設計ドキュメント

- [やどぺら v0.3 要約定義書](docs/yadopera-v03-summary.md)
- [やどぺら v0.3 アーキテクチャ設計書](docs/やどぺら_v0.3_アーキテクチャ設計書.md)

### 外部リンク

- GitHubリポジトリ: https://github.com/kurinobu/yadopera.git
- Render.com: 本番環境（予定）

## ライセンス

（未設定）

## 問い合わせ

- **開発者**: Air
- **ブログ**: https://air-edison.com
- **Twitter**: @kbqjp

---

**Document Version**: v1.0  
**Last Updated**: 2025-11-25  
**Status**: Phase 0 進行中

