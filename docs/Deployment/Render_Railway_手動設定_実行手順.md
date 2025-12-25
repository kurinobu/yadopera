# Render.comとRailway手動設定 実行手順

**作成日**: 2025年11月28日  
**フェーズ**: Phase 1 Week 4  
**目的**: ステージング環境を構築するための手動設定手順

---

## 前提条件

- ✅ バックアップ完了（`docs/Backups/20251128_145259_deployment_setup/`）
- ✅ `develop`ブランチが存在（リモートにも存在）
- ✅ Render.com Proアカウント（既存契約）
- ✅ Railway Hobbyアカウント（既存契約）
- ✅ OpenAI APIキー（既存）

---

## 設定手順

### ステップ1: developブランチに切り替え

```bash
cd /Users/kurinobu/projects/yadopera
git checkout develop
git pull origin develop
```

**確認**: 現在`develop`ブランチにいることを確認

---

### ステップ2: Railway Hobby設定（先に実施）

#### 2.1 PostgreSQLサービス追加

1. Railwayダッシュボードにログイン: https://railway.app
2. 既存プロジェクトを選択、または新規プロジェクト作成
3. 「New」→「Database」→「Add PostgreSQL」を選択
4. サービス名を設定: `yadopera-postgres-staging`
5. 接続情報を取得:
   - 「Variables」タブで`DATABASE_URL`を確認
   - または「Connect」タブで接続URLを確認
   - 形式: `postgresql://user:password@host:port/database`
6. **重要**: 接続URLをメモ（後でRender.comに設定）

#### 2.2 pgvector拡張有効化

1. RailwayのPostgreSQLサービスで「Data」タブを開く
2. SQLクエリを実行:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. 実行結果を確認（成功メッセージが表示される）

#### 2.3 Redisサービス追加

1. Railwayダッシュボードで同じプロジェクト内
2. 「New」→「Database」→「Add Redis」を選択
3. サービス名を設定: `yadopera-redis-staging`
4. 接続情報を取得:
   - 「Variables」タブで`REDIS_URL`を確認
   - または「Connect」タブで接続URLを確認
   - 形式: `redis://user:password@host:port/0`
5. **重要**: 接続URLをメモ（後でRender.comに設定）

---

### ステップ3: SECRET_KEY生成

```bash
# SECRET_KEY生成（32文字以上）
openssl rand -hex 32
```

**重要**: 生成されたキーをメモ（後でRender.comに設定）

---

### ステップ4: Render.com Pro設定

#### 4.1 Web Service作成

1. Render.comダッシュボードにログイン: https://dashboard.render.com
2. 「New +」→「Web Service」を選択
3. GitHubリポジトリを接続（初回のみ）:
   - 「Connect account」→ GitHubアカウントを選択
   - リポジトリ `kurinobu/yadopera` を選択
4. 以下の設定を行う:
   - **Name**: `yadopera-backend-staging`
   - **Region**: `Tokyo`（または最寄りのリージョン）
   - **Branch**: `develop`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Pro（既存契約を選択）

#### 4.2 環境変数設定

1. Render.comのWeb Serviceダッシュボードで「Environment」タブを開く
2. 以下の環境変数を追加（「Add Environment Variable」をクリック）:

```bash
# データベース接続（Railway Hobby PostgreSQL）
# ステップ2.1で取得した接続URLを使用
# 注意: postgresql:// を postgresql+asyncpg:// に変更する必要がある場合がある
DATABASE_URL=postgresql+asyncpg://user:password@railway-host:5432/yadopera_staging

# Redis接続（Railway Hobby Redis）
# ステップ2.3で取得した接続URLを使用
REDIS_URL=redis://railway-redis-host:6379/0

# OpenAI API
OPENAI_API_KEY=sk-...（既存キーを使用）

# JWT署名用シークレットキー
# ステップ3で生成したキーを使用
SECRET_KEY=your-secret-key-here

# CORS設定
# フロントエンドURL（後で設定、一旦仮のURL）
CORS_ORIGINS=https://yadopera-frontend-staging.onrender.com

# 環境設定
ENVIRONMENT=staging
DEBUG=False

# ログレベル
LOG_LEVEL=INFO
```

**重要事項**:
- `DATABASE_URL`は`postgresql+asyncpg://`形式である必要がある
- Railwayから取得したURLが`postgresql://`形式の場合は、`postgresql+asyncpg://`に変更
- `SECRET_KEY`はステップ3で生成したキーを使用
- `CORS_ORIGINS`は後でフロントエンドURLに更新

#### 4.3 自動デプロイ設定

1. 「Settings」タブで以下を設定:
   - **Auto-Deploy**: `Yes`
   - **Branch**: `develop`
   - **Pull Request Previews**: `Enabled`（オプション）

#### 4.4 ヘルスチェック設定

1. 「Settings」タブで以下を設定:
   - **Health Check Path**: `/health`または`/api/v1/health`
   - **Health Check Interval**: デフォルト設定

---

### ステップ5: フロントエンド設定（Render.com Static Site）

#### 5.1 Static Site作成

1. Render.comダッシュボードで「New +」→「Static Site」を選択
2. GitHubリポジトリを接続（既に接続済みの場合は選択）
3. 以下の設定を行う:
   - **Name**: `yadopera-frontend-staging`
   - **Branch**: `develop`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist`

#### 5.2 環境変数設定

1. Static Siteダッシュボードで「Environment」タブを開く
2. 以下の環境変数を追加:

```bash
# APIベースURL（Render.comバックエンド）
# ステップ4.1で作成したWeb ServiceのURLを使用
VITE_API_BASE_URL=https://yadopera-backend-staging.onrender.com

# 環境設定
VITE_ENVIRONMENT=staging
```

**注意**: `VITE_API_BASE_URL`はバックエンドのURL（Render.com Web ServiceのURL）

#### 5.3 バックエンドのCORS設定を更新

1. Render.comのWeb Serviceダッシュボードで「Environment」タブを開く
2. `CORS_ORIGINS`環境変数を更新:
   - フロントエンドのURL（Static SiteのURL）に更新
   - 例: `https://yadopera-frontend-staging.onrender.com`

---

### ステップ6: データベースマイグレーション

#### 6.1 マイグレーション実行

1. Render.comのWeb Serviceダッシュボードで「Shell」タブを開く
2. 以下のコマンドを実行:

```bash
cd backend
alembic upgrade head
```

**確認項目**:
- マイグレーションが正常に完了するか
- pgvector拡張が有効化されているか（Railwayで確認済み）
- 全テーブルが作成されているか

---

### ステップ7: 動作確認

#### 7.1 バックエンド確認

1. Render.comのWeb Service URLにアクセス
   - 例: `https://yadopera-backend-staging.onrender.com`
2. ヘルスチェックエンドポイントにアクセス:
   - `/health`または`/api/v1/health`
3. レスポンスを確認:
   ```json
   {
     "status": "ok",
     "database": "ok",
     "redis": "ok"
   }
   ```
4. Swagger UI確認:
   - `/docs`エンドポイントにアクセス
   - Swagger UIが表示されることを確認

#### 7.2 フロントエンド確認

1. Render.comのStatic Site URLにアクセス
   - 例: `https://yadopera-frontend-staging.onrender.com`
2. ページが正常に表示されることを確認
3. ブラウザの開発者ツールでコンソールエラーがないことを確認
4. ネットワークタブでAPIリクエストが正常に送信されることを確認

#### 7.3 CORS確認

1. フロントエンドからバックエンドAPIへのリクエストを確認
2. CORSエラーがないことを確認
3. エラーがある場合は、`CORS_ORIGINS`環境変数を確認

---

## トラブルシューティング

### データベース接続エラー

**症状**: バックエンドが起動しない、データベース接続エラー

**対策**:
1. `DATABASE_URL`が`postgresql+asyncpg://`形式であることを確認
2. Railwayの接続URLが正しいか確認
3. パスワードに特殊文字が含まれている場合はURLエンコードが必要

### Redis接続エラー

**症状**: Redis接続エラーがログに表示される

**対策**:
1. `REDIS_URL`が`redis://`形式であることを確認
2. Railwayの接続URLが正しいか確認

### CORSエラー

**症状**: フロントエンドからバックエンドAPIへのリクエストが失敗

**対策**:
1. `CORS_ORIGINS`にフロントエンドURLが含まれているか確認
2. フロントエンドURLが完全なURL形式（`https://...`）であることを確認

### デプロイエラー

**症状**: Render.comでデプロイが失敗する

**対策**:
1. ビルドログを確認
2. `requirements.txt`が存在するか確認
3. 依存関係が正しくインストールされるか確認

---

## 確認チェックリスト

### Railway Hobby設定
- [ ] PostgreSQLサービスが作成されている
- [ ] PostgreSQL接続URLが取得できている
- [ ] pgvector拡張が有効化されている
- [ ] Redisサービスが作成されている
- [ ] Redis接続URLが取得できている

### Render.com Pro設定
- [ ] Web Serviceが作成されている
- [ ] 環境変数が正しく設定されている
- [ ] 自動デプロイが有効になっている
- [ ] デプロイが正常に完了している

### フロントエンド設定
- [ ] Static Siteが作成されている
- [ ] 環境変数が正しく設定されている
- [ ] ビルドが正常に完了している

### 動作確認
- [ ] バックエンドヘルスチェックが正常に動作する
- [ ] フロントエンドからバックエンドAPIへの接続が正常に動作する
- [ ] CORSエラーがない
- [ ] データベースマイグレーションが正常に完了している

---

## 参考資料

- **調査分析レポート**: `docs/Deployment/Render_Railway_手動設定_調査分析レポート.md`
- **ステージング環境構築手順**: `docs/Deployment/ステージング環境構築手順.md`
- **Phase 1 Week 4ステップ計画**: `docs/Phase1/Phase1_Week4_ステップ計画.md`

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025-11-28  
**Status**: 実行手順作成完了


