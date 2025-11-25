# Phase 0 ステップ計画

**作成日**: 2025年11月25日  
**バージョン**: v1.0  
**対象**: やどぺら Phase 0（準備期間）  
**期間**: 1週間

---

## 全体概要

Phase 0では、MVP開発開始前の準備タスクを実施します。各ステップは独立して完了可能で、ステップ・バイ・ステップで進めます。

**前提条件**:
- ✅ Render アカウント準備完了（Render Pro）
- ✅ アーキテクチャ設計書v0.3作成完了

---

## ステップ1: GitHub リポジトリ作成・初期設定

**目的**: コード管理の基盤を構築

**タスク**:
1. GitHubで新規リポジトリ作成
   - リポジトリ名: `yadopera`（または適宜）
   - 公開設定: Private（初期段階）
   - README.md: 自動生成しない（後で作成）
   - .gitignore: 自動生成しない（後で作成）
   - ライセンス: 未設定（後で決定）

2. ローカルリポジトリ初期化
   ```bash
   git init
   git remote add origin <リポジトリURL>
   ```

3. `.gitignore`作成
   - Python用（`__pycache__/`, `*.pyc`, `.env`, `venv/`等）
   - Node.js用（`node_modules/`, `.env.local`等）
   - Docker用（`.docker/`等）
   - IDE用（`.vscode/`, `.idea/`等）
   - OS用（`.DS_Store`等）

4. ブランチ戦略決定
   - `main`: 本番環境用
   - `develop`: 開発用
   - `feature/*`: 機能開発用
   - 初期ブランチ: `main`

5. 初回コミット（空コミットまたはREADMEのみ）
   ```bash
   git add .gitignore
   git commit -m "Initial commit: Add .gitignore"
   git branch -M main
   git push -u origin main
   ```

**完了基準**:
- [ ] GitHubリポジトリ作成完了
- [ ] ローカルリポジトリ初期化完了
- [ ] `.gitignore`作成・コミット完了
- [ ] ブランチ戦略決定・文書化完了

**所要時間**: 30分

---

## ステップ2: プロジェクト構造作成

**目的**: 開発環境のディレクトリ構造を整備

**タスク**:
1. ルートディレクトリ構造作成
   ```
   yadopera/
   ├── backend/          # FastAPI バックエンド
   ├── frontend/         # Vue.js フロントエンド
   ├── docs/             # ドキュメント（既存）
   ├── docker-compose.yml
   ├── .gitignore        # ステップ1で作成済み
   └── README.md         # 後で作成
   ```

2. `backend/`ディレクトリ構造作成
   ```
   backend/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── core/
   │   │   ├── __init__.py
   │   │   └── config.py
   │   └── api/
   │       └── __init__.py
   ├── alembic/
   │   └── versions/
   ├── alembic.ini
   ├── requirements.txt
   ├── .env.example
   └── Dockerfile
   ```

3. `frontend/`ディレクトリ構造作成
   ```
   frontend/
   ├── src/
   │   ├── main.ts
   │   ├── App.vue
   │   └── components/
   ├── public/
   ├── package.json
   ├── .env.example
   ├── Dockerfile
   ├── vite.config.ts
   └── tsconfig.json
   ```

4. 各ディレクトリに`.gitkeep`ファイル作成（空ディレクトリをGit管理）

**完了基準**:
- [ ] ルートディレクトリ構造作成完了
- [ ] `backend/`ディレクトリ構造作成完了
- [ ] `frontend/`ディレクトリ構造作成完了
- [ ] 構造をコミット

**所要時間**: 15分

---

## ステップ3: Docker環境セットアップ

**目的**: 開発環境をDockerで統一し、再現性を確保

**タスク**:
1. `docker-compose.yml`作成
   - PostgreSQL 15（pgvector拡張対応）
   - Redis 7.2
   - Backend（FastAPI）
   - Frontend（Vite開発サーバー）
   - ネットワーク設定
   - ボリューム設定

2. `backend/Dockerfile`作成
   - Python 3.11ベースイメージ
   - 依存関係インストール
   - アプリケーションコピー
   - ポート8000公開

3. `frontend/Dockerfile`作成（開発用）
   - Node.js 18ベースイメージ
   - 依存関係インストール
   - Vite開発サーバー起動
   - ポート5173公開

4. `.dockerignore`作成（backend/とfrontend/）
   - 不要ファイルを除外

5. 動作確認（後続ステップで詳細確認）

**完了基準**:
- [ ] `docker-compose.yml`作成完了
- [ ] `backend/Dockerfile`作成完了
- [ ] `frontend/Dockerfile`作成完了
- [ ] `.dockerignore`作成完了
- [ ] ファイルをコミット

**所要時間**: 1時間

**注意**: この時点ではまだサービスは起動しません（依存関係未設定のため）

---

## ステップ4: Backend初期設定

**目的**: FastAPIプロジェクトの骨格を作成

**タスク**:
1. `backend/requirements.txt`作成
   - FastAPI 0.109+
   - SQLAlchemy 2.0+（async対応）
   - Alembic 1.13+
   - uvicorn 0.27+
   - python-jose 3.3+（JWT認証）
   - passlib 1.7+（bcrypt）
   - psycopg2-binary（PostgreSQL接続）
   - pgvector（ベクトル検索）
   - openai（OpenAI API）
   - langchain 0.1+
   - tiktoken 0.5+
   - redis（Redis接続）
   - python-dotenv（環境変数管理）

2. `backend/.env.example`作成
   ```
   # Database
   DATABASE_URL=postgresql://user:password@postgres:5432/yadopera
   
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
   ```

3. `backend/app/main.py`作成（最小構成）
   ```python
   from fastapi import FastAPI
   
   app = FastAPI(title="やどぺら API", version="0.3.0")
   
   @app.get("/")
   def read_root():
       return {"message": "やどぺら API v0.3"}
   
   @app.get("/health")
   def health_check():
       return {"status": "ok"}
   ```

4. `backend/app/core/config.py`作成（環境変数読み込み）
   ```python
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       database_url: str
       redis_url: str
       openai_api_key: str
       secret_key: str
       algorithm: str = "HS256"
       access_token_expire_minutes: int = 10080
       environment: str = "development"
       debug: bool = True
       
       class Config:
           env_file = ".env"
   ```

5. Alembic初期化
   ```bash
   cd backend
   alembic init alembic
   ```

6. `alembic.ini`設定
   - `sqlalchemy.url`を環境変数から読み込むように設定

7. 初期マイグレーションファイル作成（pgvector拡張有効化）
   ```python
   # alembic/versions/001_enable_pgvector.py
   def upgrade():
       op.execute("CREATE EXTENSION IF NOT EXISTS vector")
   
   def downgrade():
       op.execute("DROP EXTENSION IF EXISTS vector")
   ```

**完了基準**:
- [ ] `requirements.txt`作成完了
- [ ] `.env.example`作成完了
- [ ] `app/main.py`作成完了
- [ ] `app/core/config.py`作成完了
- [ ] Alembic初期化完了
- [ ] 初期マイグレーションファイル作成完了
- [ ] ファイルをコミット

**所要時間**: 1.5時間

---

## ステップ5: Frontend初期設定

**目的**: Vue.js 3 + TypeScriptプロジェクトの骨格を作成

**タスク**:
1. `frontend/package.json`作成
   - Vue.js 3.4+
   - TypeScript 5.3+
   - Vite 5.0+
   - Tailwind CSS 3.4+
   - Pinia 2.1+（状態管理）
   - Axios 1.6+（HTTPクライアント）
   - Vite PWA Plugin 0.19+
   - 開発依存関係（ESLint, Prettier等）

2. `frontend/.env.example`作成
   ```
   VITE_API_BASE_URL=http://localhost:8000
   VITE_APP_NAME=やどぺら
   ```

3. Vite + Vue 3プロジェクト初期化
   ```bash
   cd frontend
   npm install
   ```

4. `vite.config.ts`作成
   - Vueプラグイン設定
   - TypeScript設定
   - 環境変数設定
   - PWA設定（後で詳細化）

5. `tsconfig.json`作成
   - TypeScript設定
   - Vue SFC型定義

6. `src/main.ts`作成（最小構成）
   ```typescript
   import { createApp } from 'vue'
   import App from './App.vue'
   
   createApp(App).mount('#app')
   ```

7. `src/App.vue`作成（最小構成）
   ```vue
   <template>
     <div>
       <h1>やどぺら</h1>
       <p>開発環境構築中</p>
     </div>
   </template>
   ```

8. ESLint, Prettier設定（オプション）

**完了基準**:
- [ ] `package.json`作成完了
- [ ] `.env.example`作成完了
- [ ] Vite + Vue 3プロジェクト初期化完了
- [ ] `vite.config.ts`作成完了
- [ ] `tsconfig.json`作成完了
- [ ] `src/main.ts`作成完了
- [ ] `src/App.vue`作成完了
- [ ] ファイルをコミット

**所要時間**: 1.5時間

---

## ステップ6: データベース・Redis環境構築確認

**目的**: PostgreSQL + pgvector、Redisの動作確認

**タスク**:
1. Docker ComposeでPostgreSQL + Redis起動
   ```bash
   docker-compose up -d postgres redis
   ```

2. PostgreSQL接続確認
   ```bash
   docker-compose exec postgres psql -U user -d yadopera
   ```

3. pgvector拡張有効化確認
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   \dx  -- 拡張一覧確認
   ```

4. Redis接続確認
   ```bash
   docker-compose exec redis redis-cli ping
   # 応答: PONG
   ```

5. 環境変数設定
   - `backend/.env`作成（`.env.example`をコピーして実際の値を設定）

**完了基準**:
- [ ] PostgreSQL起動・接続確認完了
- [ ] pgvector拡張有効化確認完了
- [ ] Redis起動・接続確認完了
- [ ] `backend/.env`作成完了（実際の値設定）

**所要時間**: 30分

---

## ステップ7: 全サービス起動確認

**目的**: Docker Composeで全サービスが正常に起動することを確認

**タスク**:
1. `docker-compose up`実行
   ```bash
   docker-compose up
   ```

2. Backend動作確認
   - `http://localhost:8000/`にアクセス
   - `http://localhost:8000/docs`でSwagger UI表示確認
   - `http://localhost:8000/health`でヘルスチェック確認

3. Frontend動作確認
   - `http://localhost:5173`でVite開発サーバー起動確認
   - ブラウザでアクセスして「やどぺら」表示確認

4. ログ確認
   - エラーがないことを確認
   - 警告があれば記録

5. 停止確認
   ```bash
   docker-compose down
   ```

**完了基準**:
- [ ] `docker-compose up`で全サービス起動完了
- [ ] Backend: Swagger UI表示確認完了
- [ ] Frontend: Vite開発サーバー起動確認完了
- [ ] エラーなし確認完了

**所要時間**: 30分

---

## ステップ8: README.md作成

**目的**: 開発環境セットアップ手順を文書化

**タスク**:
1. ルート`README.md`作成
   - プロジェクト概要
   - 技術スタック
   - 開発環境セットアップ手順
   - 環境変数設定方法
   - `docker-compose up`実行手順
   - トラブルシューティング
   - 開発規約（リンク）

2. `backend/README.md`作成（オプション）
   - Backend固有のセットアップ手順

3. `frontend/README.md`作成（オプション）
   - Frontend固有のセットアップ手順

**完了基準**:
- [ ] ルート`README.md`作成完了
- [ ] セットアップ手順記載完了
- [ ] ファイルをコミット

**所要時間**: 1時間

---

## ステップ9: 外部サービス準備

**目的**: 開発・本番環境で使用する外部サービスのアカウント準備

**タスク**:
1. OpenAI API キー取得
   - OpenAIアカウント作成（未作成の場合）
   - API キー生成
   - 使用量制限設定確認
   - `backend/.env`に設定

2. メール送信サービス準備（オプション、Phase 1で使用）
   - SendGrid、Mailgun等のアカウント作成
   - API キー取得
   - `backend/.env`に設定（後で使用）

3. その他外部サービス（必要に応じて）
   - 分析ツール（Google Analytics等）
   - エラートラッキング（Sentry等）

**完了基準**:
- [ ] OpenAI API キー取得完了
- [ ] `backend/.env`に設定完了
- [ ] メール送信サービス準備完了（オプション）

**所要時間**: 30分

**注意**: API キーは`.env`に設定し、`.gitignore`で除外されていることを確認

---

## ステップ10: 簡易ランディングページ（LP）作成

**目的**: PoC応募導線の構築、説明コスト削減

**タスク**:
1. LP構成決定
   - セクション構成確認（PoCプロモーション要件書参照）
   - デザイン方針決定

2. 技術スタック決定
   - 静的HTML/CSS/JavaScript
   - または Vite + Vue.js 3（SPA）
   - デプロイ先: Vercel、Netlify、GitHub Pages等

3. LP実装
   - ヒーローセクション
   - 課題提起セクション
   - 解決策セクション
   - 仕組みセクション
   - 料金セクション
   - FAQセクション
   - CTAセクション（PoC応募フォーム、説明会予約）

4. フォーム実装
   - PoC応募フォーム（Google Forms、Typeform等）
   - 説明会予約フォーム（Googleカレンダー連携等）

5. レスポンシブデザイン対応
   - スマホ最適化

6. デプロイ
   - 静的ホスティングサービスにデプロイ
   - カスタムドメイン設定（`tabipera.com`）

**完了基準**:
- [ ] LP構成決定完了
- [ ] LP実装完了
- [ ] フォーム実装完了
- [ ] レスポンシブデザイン対応完了
- [ ] デプロイ完了
- [ ] 動作確認完了

**所要時間**: 4-6時間

**注意**: デモ動画は後で追加可能

---

## ステップ11: やどびと多言語優先度アンケート実施

**目的**: Phase 2の言語優先順位決定

**タスク**:
1. アンケート設計
   - 質問項目決定
     - ゲスト国籍TOP5
     - 言語対応の困難度ランキング
     - 希望対応言語
   - Google Forms等でフォーム作成

2. 配信準備
   - やどびとユーザーリスト準備
   - メール文面作成

3. アンケート配信
   - やどびとユーザーへメール送信
   - 回答期限設定（例: 2週間）

4. 結果集計（回答期限後）
   - 回答データ分析
   - 優先言語決定
   - 結果をドキュメント化

**完了基準**:
- [ ] アンケート設計完了
- [ ] フォーム作成完了
- [ ] 配信準備完了
- [ ] アンケート配信完了

**所要時間**: 2時間（配信まで）

**注意**: 結果集計は回答期限後（Phase 1開発中）に実施

---

## Phase 0完了基準（全体）

すべてのステップが完了したら、以下を確認:

- [ ] ステップ1: GitHub リポジトリ作成完了
- [ ] ステップ2: プロジェクト構造作成完了
- [ ] ステップ3: Docker環境セットアップ完了
- [ ] ステップ4: Backend初期設定完了
- [ ] ステップ5: Frontend初期設定完了
- [ ] ステップ6: データベース・Redis環境構築確認完了
- [ ] ステップ7: 全サービス起動確認完了
- [ ] ステップ8: README.md作成完了
- [ ] ステップ9: 外部サービス準備完了
- [ ] ステップ10: 簡易ランディングページ作成完了
- [ ] ステップ11: やどびと多言語優先度アンケート実施完了

**合計所要時間**: 約12-15時間（1週間で実施可能）

---

## 次のステップ

Phase 0完了後、Phase 1（MVP開発）を開始します。

**Phase 1概要**:
- Week 1: バックエンド基盤
- Week 2: AI対話エンジン
- Week 3: フロントエンド
- Week 4: 統合・テスト

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-25  
**Status**: 準備完了


