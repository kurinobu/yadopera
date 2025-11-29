# Render.comとRailway手動設定 調査分析レポート

**作成日**: 2025年11月28日  
**フェーズ**: Phase 1 Week 4  
**目的**: Render.comとRailwayの手動設定を実行するための調査分析と準備

---

## 1. 現状理解サマリー

### 1.1 プロジェクト概要

- **プロジェクト名**: やどぺら（Yadopera）
- **説明**: 小規模宿泊施設向けAI多言語自動案内システム
- **現在のフェーズ**: Phase 1 Week 4（統合・テスト・ステージング環境構築）
- **進捗**: Phase 1 Week 1-3完了、Week 4進行中

### 1.2 デプロイ戦略（決定版）

**Phase 1-3（現在）**:
- **Web Service**: Render.com Pro（既存契約、使用量次第、約¥2,000/月）
- **PostgreSQL**: Railway Hobby（既存契約、追加料金なし）
- **Redis**: Railway Hobby（既存契約、追加料金なし）
- **フロントエンド**: Render.com Static Site（新規追加予定）

**Phase 4以降**:
- **Web Service**: Render.com Pro（継続）
- **PostgreSQL**: Render.com Managed PostgreSQL（¥6,000/月）に移行
- **Redis**: Render.com Redis Cloud（¥3,000/月）に移行
- **フロントエンド**: Render.com Static Site（継続）

### 1.3 ブランチ戦略

- `main`: 本番環境用ブランチ
- `develop`: ステージング環境用ブランチ（作成予定）
- `feature/*`: 機能開発用ブランチ

---

## 2. 必要な設定項目

### 2.1 Render.com Pro設定

#### 2.1.1 Web Service作成（ステージング）

**設定項目**:
- **Name**: `yadopera-backend-staging`
- **Region**: `Tokyo`（または最寄りのリージョン）
- **Branch**: `develop`（作成後）
- **Root Directory**: `backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Pro（既存契約）

#### 2.1.2 環境変数設定（Render.com）

**必須環境変数**:
```bash
# データベース接続（Railway Hobby PostgreSQL）
DATABASE_URL=postgresql+asyncpg://user:password@railway-host:5432/yadopera_staging

# Redis接続（Railway Hobby Redis）
REDIS_URL=redis://railway-redis-host:6379/0

# OpenAI API
OPENAI_API_KEY=sk-...（既存キーを使用）

# JWT署名用シークレットキー
SECRET_KEY=your-secret-key-here（32文字以上）

# CORS設定
CORS_ORIGINS=https://yadopera-frontend-staging.onrender.com（フロントエンドURL）

# 環境設定
ENVIRONMENT=staging
DEBUG=False

# ログレベル
LOG_LEVEL=INFO
```

**注意事項**:
- `DATABASE_URL`は`postgresql+asyncpg://`形式である必要がある（`database.py`で自動変換されるが、明示的に設定推奨）
- `SECRET_KEY`は強力なランダム文字列を生成（例: `openssl rand -hex 32`）
- `CORS_ORIGINS`はフロントエンドURLを設定（Render.com Static SiteのURL）

#### 2.1.3 自動デプロイ設定

- **Auto-Deploy**: `Yes`
- **Branch**: `develop`
- **Pull Request Previews**: `Enabled`（オプション）

#### 2.1.4 ヘルスチェック設定

- **Health Check Path**: `/api/v1/health`（実装確認が必要）
- **Health Check Interval**: デフォルト設定

### 2.2 Railway Hobby設定

#### 2.2.1 PostgreSQLサービス追加

**設定項目**:
- **Service Name**: `yadopera-postgres-staging`
- **Database**: PostgreSQL 15
- **Plan**: Hobby（既存契約、追加料金なし）
- **Storage**: 1GB（Hobbyプランの制限）

**接続情報取得**:
- Railwayダッシュボードで接続URLを取得
- 形式: `postgresql://user:password@host:port/database`
- このURLを`DATABASE_URL`としてRender.comに設定

**pgvector拡張有効化**:
- RailwayのPostgreSQLサービスでSQLを実行
- `CREATE EXTENSION IF NOT EXISTS vector;`

#### 2.2.2 Redisサービス追加

**設定項目**:
- **Service Name**: `yadopera-redis-staging`
- **Database**: Redis 7.2
- **Plan**: Hobby（既存契約、追加料金なし）

**接続情報取得**:
- Railwayダッシュボードで接続URLを取得
- 形式: `redis://user:password@host:port/0`
- このURLを`REDIS_URL`としてRender.comに設定

**注意事項**:
- Redisはオプション（PostgreSQLで対応可能な場合もある）
- セッション管理とキャッシュに使用

### 2.3 フロントエンド設定（Render.com Static Site）

#### 2.3.1 Static Site作成（ステージング）

**設定項目**:
- **Name**: `yadopera-frontend-staging`
- **Branch**: `develop`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`
- **Environment**: `Node`

#### 2.3.2 環境変数設定（フロントエンド）

```bash
# APIベースURL（Render.comバックエンド）
VITE_API_BASE_URL=https://yadopera-backend-staging.onrender.com

# 環境設定
VITE_ENVIRONMENT=staging
```

---

## 3. 実装確認事項

### 3.1 バックエンド実装確認

#### 3.1.1 ヘルスチェックエンドポイント

**確認項目**:
- `/api/v1/health`エンドポイントが実装されているか
- データベース接続確認が含まれているか
- Redis接続確認が含まれているか

**確認結果**:
- ✅ `/health`エンドポイントが実装済み（`backend/app/main.py` 82-97行目）
- ✅ `/api/v1/health`エンドポイントが実装済み（`backend/app/api/v1/health.py`）
- ✅ データベース接続確認が含まれている
- ✅ Redis接続確認が含まれている
- ✅ 両方のエンドポイントが利用可能（`/health`と`/api/v1/health`）

**推奨設定**:
- Render.comのヘルスチェックパス: `/health`または`/api/v1/health`

#### 3.1.2 データベース接続設定

**確認項目**:
- `backend/app/database.py`で`postgresql://`から`postgresql+asyncpg://`への変換が実装されているか
- 接続プール設定が適切か

**確認済み**:
- ✅ `database.py`で自動変換が実装済み（19-25行目）
- ✅ 接続プール設定が適切（28-35行目）

#### 3.1.3 環境変数設定

**確認項目**:
- `backend/app/core/config.py`で必要な環境変数が定義されているか
- デフォルト値が適切か

**確認済み**:
- ✅ `Settings`クラスで必要な環境変数が定義済み
- ✅ `DATABASE_URL`, `REDIS_URL`, `OPENAI_API_KEY`, `SECRET_KEY`が必須
- ✅ `CORS_ORIGINS`はデフォルト値あり（開発環境用）

### 3.2 フロントエンド実装確認

#### 3.2.1 環境変数設定

**確認項目**:
- `frontend/.env.example`が存在するか
- `VITE_API_BASE_URL`が使用されているか

**確認方法**:
- `frontend/src/api/axios.ts`を確認
- または`frontend/src/api/`配下のAPIクライアントを確認

---

## 4. 設定手順（詳細）

### 4.1 事前準備

#### 4.1.1 developブランチ作成

```bash
# developブランチを作成
git checkout -b develop

# リモートにプッシュ
git push -u origin develop
```

#### 4.1.2 シークレットキー生成

```bash
# SECRET_KEY生成（32文字以上）
openssl rand -hex 32
```

### 4.2 Railway Hobby設定（先に実施）

#### 4.2.1 PostgreSQLサービス追加

1. Railwayダッシュボードにログイン
2. 既存プロジェクトを選択、または新規プロジェクト作成
3. 「New」→「Database」→「Add PostgreSQL」を選択
4. サービス名: `yadopera-postgres-staging`
5. 接続情報を取得:
   - 「Variables」タブで`DATABASE_URL`を確認
   - または「Connect」タブで接続URLを確認
6. pgvector拡張有効化:
   - 「Data」タブでSQLクエリを実行
   - `CREATE EXTENSION IF NOT EXISTS vector;`

#### 4.2.2 Redisサービス追加

1. Railwayダッシュボードで同じプロジェクト内
2. 「New」→「Database」→「Add Redis」を選択
3. サービス名: `yadopera-redis-staging`
4. 接続情報を取得:
   - 「Variables」タブで`REDIS_URL`を確認
   - または「Connect」タブで接続URLを確認

### 4.3 Render.com Pro設定

#### 4.3.1 Web Service作成

1. Render.comダッシュボードにログイン
2. 「New +」→「Web Service」を選択
3. GitHubリポジトリを接続（初回のみ）
4. 以下の設定を行う:
   - **Name**: `yadopera-backend-staging`
   - **Region**: `Tokyo`（または最寄りのリージョン）
   - **Branch**: `develop`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Pro（既存契約）

#### 4.3.2 環境変数設定

1. Render.comのWeb Serviceダッシュボードで「Environment」タブを開く
2. 以下の環境変数を追加:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@railway-host:5432/yadopera_staging
REDIS_URL=redis://railway-redis-host:6379/0
OPENAI_API_KEY=sk-...（既存キー）
SECRET_KEY=your-secret-key-here（生成したキー）
CORS_ORIGINS=https://yadopera-frontend-staging.onrender.com
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=INFO
```

**注意事項**:
- `DATABASE_URL`と`REDIS_URL`はRailwayから取得した接続URLを使用
- `SECRET_KEY`は事前に生成したキーを使用
- `CORS_ORIGINS`はフロントエンドURL（後で設定）

#### 4.3.3 自動デプロイ設定

1. 「Settings」タブで以下を設定:
   - **Auto-Deploy**: `Yes`
   - **Branch**: `develop`
   - **Pull Request Previews**: `Enabled`（オプション）

### 4.4 フロントエンド設定（Render.com Static Site）

#### 4.4.1 Static Site作成

1. Render.comダッシュボードで「New +」→「Static Site」を選択
2. GitHubリポジトリを接続（既に接続済みの場合は選択）
3. 以下の設定を行う:
   - **Name**: `yadopera-frontend-staging`
   - **Branch**: `develop`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist`

#### 4.4.2 環境変数設定

1. Static Siteダッシュボードで「Environment」タブを開く
2. 以下の環境変数を追加:

```bash
VITE_API_BASE_URL=https://yadopera-backend-staging.onrender.com
VITE_ENVIRONMENT=staging
```

**注意事項**:
- `VITE_API_BASE_URL`はバックエンドのURL（Render.com Web ServiceのURL）
- バックエンドの`CORS_ORIGINS`にフロントエンドURLを追加する必要がある

### 4.5 データベースマイグレーション

#### 4.5.1 マイグレーション実行

1. Render.comのWeb Serviceダッシュボードで「Shell」タブを開く
2. 以下のコマンドを実行:

```bash
cd backend
alembic upgrade head
```

**確認項目**:
- マイグレーションが正常に完了するか
- pgvector拡張が有効化されているか
- 全テーブルが作成されているか

---

## 5. 接続確認手順

### 5.1 バックエンド接続確認

#### 5.1.1 ヘルスチェック

1. Render.comのWeb Service URLにアクセス
2. `/api/v1/health`エンドポイントにアクセス
3. レスポンスを確認:
   - データベース接続: OK
   - Redis接続: OK
   - OpenAI API: OK（オプション）

#### 5.1.2 Swagger UI確認

1. `/docs`エンドポイントにアクセス
2. Swagger UIが表示されることを確認
3. APIエンドポイントが正常に表示されることを確認

### 5.2 フロントエンド接続確認

#### 5.2.1 ページ表示確認

1. Render.comのStatic Site URLにアクセス
2. ページが正常に表示されることを確認
3. コンソールエラーがないことを確認

#### 5.2.2 API接続確認

1. ブラウザの開発者ツールでネットワークタブを開く
2. フロントエンドからバックエンドAPIへのリクエストを確認
3. CORSエラーがないことを確認

---

## 6. トラブルシューティング

### 6.1 データベース接続エラー

**症状**:
- バックエンドが起動しない
- データベース接続エラーがログに表示される

**原因と対策**:
1. **接続URL形式エラー**:
   - `DATABASE_URL`が`postgresql+asyncpg://`形式であることを確認
   - `database.py`で自動変換されるが、明示的に設定推奨

2. **接続情報エラー**:
   - Railwayの接続URLが正しいか確認
   - パスワードに特殊文字が含まれている場合はURLエンコードが必要

3. **pgvector拡張エラー**:
   - RailwayのPostgreSQLで`CREATE EXTENSION IF NOT EXISTS vector;`を実行
   - マイグレーションで拡張が有効化されているか確認

### 6.2 Redis接続エラー

**症状**:
- Redis接続エラーがログに表示される
- セッション管理が動作しない

**原因と対策**:
1. **接続URL形式エラー**:
   - `REDIS_URL`が`redis://`形式であることを確認
   - パスワードが含まれている場合は`redis://:password@host:port/0`形式

2. **接続情報エラー**:
   - Railwayの接続URLが正しいか確認
   - ポート番号が正しいか確認

3. **Redis不要の場合**:
   - Redisが不要な場合は、`REDIS_URL`を空文字列に設定（実装確認が必要）

### 6.3 CORSエラー

**症状**:
- フロントエンドからバックエンドAPIへのリクエストが失敗
- ブラウザコンソールにCORSエラーが表示される

**原因と対策**:
1. **CORS設定エラー**:
   - `CORS_ORIGINS`にフロントエンドURLが含まれているか確認
   - 複数のURLがある場合はカンマ区切りで設定

2. **URL形式エラー**:
   - フロントエンドURLが完全なURL形式（`https://...`）であることを確認
   - 末尾のスラッシュがないことを確認

### 6.4 デプロイエラー

**症状**:
- Render.comでデプロイが失敗する
- ビルドエラーが表示される

**原因と対策**:
1. **ビルドコマンドエラー**:
   - `requirements.txt`が存在するか確認
   - 依存関係が正しくインストールされるか確認

2. **マイグレーションエラー**:
   - `alembic upgrade head`が正常に実行されるか確認
   - データベース接続が確立されているか確認

3. **起動コマンドエラー**:
   - `uvicorn`が正しくインストールされているか確認
   - `app.main:app`が正しいパスか確認

---

## 7. 確認チェックリスト

### 7.1 事前準備

- [ ] `develop`ブランチが作成されている
- [ ] `SECRET_KEY`が生成されている
- [ ] Railway Hobbyアカウントにログインできる
- [ ] Render.com Proアカウントにログインできる

### 7.2 Railway Hobby設定

- [ ] PostgreSQLサービスが作成されている
- [ ] PostgreSQL接続URLが取得できている
- [ ] pgvector拡張が有効化されている
- [ ] Redisサービスが作成されている
- [ ] Redis接続URLが取得できている

### 7.3 Render.com Pro設定

- [ ] Web Serviceが作成されている
- [ ] 環境変数が正しく設定されている
- [ ] 自動デプロイが有効になっている
- [ ] デプロイが正常に完了している

### 7.4 フロントエンド設定

- [ ] Static Siteが作成されている
- [ ] 環境変数が正しく設定されている
- [ ] ビルドが正常に完了している
- [ ] ページが正常に表示される

### 7.5 接続確認

- [ ] バックエンドヘルスチェックが正常に動作する
- [ ] フロントエンドからバックエンドAPIへの接続が正常に動作する
- [ ] CORSエラーがない
- [ ] データベースマイグレーションが正常に完了している

---

## 8. 参考資料

### 8.1 ドキュメント

- **ステージング環境構築手順**: `docs/Deployment/ステージング環境構築手順.md`
- **Phase 1 Week 4ステップ計画**: `docs/Phase1/Phase1_Week4_ステップ計画.md`
- **要約定義書**: `docs/Summary/yadopera-v03-summary.md`
- **アーキテクチャ設計書**: `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`
- **引き継ぎ書**: `docs/Phase0/Phase0_引き継ぎ書.md`

### 8.2 外部リンク

- [Render.com Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [PostgreSQL pgvector Documentation](https://github.com/pgvector/pgvector)

---

## 9. 次のステップ

設定完了後、以下のステップを実施:

1. **動作確認**:
   - バックエンドAPIの動作確認
   - フロントエンドの動作確認
   - 統合テストの実行

2. **ドキュメント更新**:
   - 設定手順の更新
   - 環境変数の一覧化
   - トラブルシューティングの追加

3. **本番環境準備**:
   - 本番環境の設定計画
   - カスタムドメイン設定
   - SSL証明書設定

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025-11-28  
**Status**: 調査分析完了、準備完了

