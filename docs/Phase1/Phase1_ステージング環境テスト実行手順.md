# Phase 1 ステージング環境テスト実行手順

**作成日**: 2025年12月1日  
**対象**: Phase 1（MVP開発）ステージング環境でのテスト実行  
**目的**: Phase 1完了のためのステージング環境でのテスト実行手順を提示

---

## 1. 前提条件の確認

### 1.1 完了済み項目

- ✅ Railway PostgreSQL作成完了
- ✅ Railway pgvector拡張有効化完了（2025-11-29）
- ✅ Railway Redis作成完了
- ✅ Render.com Web Service作成完了
- ✅ Render.com 環境変数設定完了
- ✅ Render.com デプロイ成功（2025-11-29）
- ✅ ステージング環境動作確認完了（2025-11-29）

---

## 2. Railway接続情報の取得

### 2.1 PostgreSQL接続情報の取得

1. Railwayダッシュボードにアクセス: https://railway.app
2. プロジェクトを選択
3. PostgreSQLサービス（pgvector-pg18）を選択
4. 「Variables」タブで接続情報を確認:
   - `DATABASE_PUBLIC_URL`（公開エンドポイント）をコピー
   - 形式: `postgresql://postgres:password@host:port/database`

**注意**: テスト実行には`DATABASE_PUBLIC_URL`を使用します（外部接続用）

### 2.2 Redis接続情報の取得

1. RailwayダッシュボードでRedisサービスを選択
2. 「Variables」タブで接続情報を確認:
   - `REDIS_PUBLIC_URL`または`REDIS_URL`をコピー
   - 形式: `redis://default:password@host:port`

---

## 3. 環境変数の設定

### 3.1 環境変数の設定方法

**ローカル環境で環境変数を設定**:

```bash
cd /Users/kurinobu/projects/yadopera/backend

# Railwayダッシュボードから取得した接続情報を使用
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@host:port/database"
export REDIS_URL="redis://default:password@host:port"
export USE_POSTGRES_TEST="true"
export USE_OPENAI_MOCK="true"
export SECRET_KEY="test-secret-key-for-staging-tests-minimum-32-characters-long"
export CORS_ORIGINS="http://localhost:5173"
```

**重要**:
- `TEST_DATABASE_URL`は`postgresql+asyncpg://`形式を使用（`postgresql://`ではない）
- `DATABASE_PUBLIC_URL`の値を`postgresql+asyncpg://`に変換して使用
- `USE_POSTGRES_TEST=true`を設定することで、PostgreSQL + pgvectorテスト環境が有効化される
- `USE_OPENAI_MOCK=true`を設定することで、OpenAI APIのモックが使用される（高速・低コスト）

### 3.2 環境変数の確認

```bash
# 環境変数が正しく設定されているか確認
echo "TEST_DATABASE_URL: $TEST_DATABASE_URL"
echo "REDIS_URL: $REDIS_URL"
echo "USE_POSTGRES_TEST: $USE_POSTGRES_TEST"
echo "USE_OPENAI_MOCK: $USE_OPENAI_MOCK"
```

---

## 4. テスト実行

### 4.1 テスト実行方法

#### 方法1: スクリプトを使用（推奨）

```bash
cd /Users/kurinobu/projects/yadopera/backend

# 環境変数を設定（上記の「3.1 環境変数の設定方法」を参照）
export TEST_DATABASE_URL="..."
export REDIS_URL="..."
export USE_POSTGRES_TEST="true"
export USE_OPENAI_MOCK="true"
export SECRET_KEY="..."
export CORS_ORIGINS="http://localhost:5173"

# テスト実行スクリプトを実行
./run_staging_tests.sh
```

#### 方法2: 直接pytestを実行

```bash
cd /Users/kurinobu/projects/yadopera/backend

# 環境変数を設定（上記の「3.1 環境変数の設定方法」を参照）
export TEST_DATABASE_URL="..."
export REDIS_URL="..."
export USE_POSTGRES_TEST="true"
export USE_OPENAI_MOCK="true"
export SECRET_KEY="..."
export CORS_ORIGINS="http://localhost:5173"

# 全テスト実行（詳細出力）
pytest tests/ -v

# または、結果をファイルに保存
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pytest tests/ -v --tb=short > "test_results_staging_${TIMESTAMP}.txt" 2>&1
```

### 4.2 テストファイル一覧（12ファイル）

1. `test_auth.py` - 認証APIテスト
2. `test_ai_engine.py` - RAG統合型AI対話エンジンテスト
3. `test_confidence.py` - 信頼度スコア計算テスト
4. `test_embeddings.py` - 埋め込みベクトル生成テスト
5. `test_vector_search.py` - pgvector検索テスト
6. `test_escalation.py` - エスカレーション判定テスト
7. `test_overnight_queue.py` - 夜間対応キュー処理テスト
8. `test_safety_check.py` - 安全カテゴリ判定テスト
9. `test_chat_service.py` - チャットサービス統合テスト
10. `test_chat_api.py` - チャットAPIエンドポイントテスト
11. `test_session_token.py` - セッション統合トークンテスト
12. `test_integration.py` - 統合テスト

---

## 5. テスト結果の確認

### 5.1 成功基準（完了条件）

**必須条件**:
1. ✅ **すべてのテストがパスする**
   - エラーがない
   - 失敗がない
   - スキップされたテストが最小限である

2. ✅ **テストカバレッジが適切である**
   - 最低カバレッジ: 60%以上
   - 推奨カバレッジ: 80%以上
   - 重要機能: 100%カバレッジ（RAGエンジン、エスカレーション判定等）

3. ✅ **pgvector検索テストが正常に動作する**
   - PostgreSQL環境でのみ実行可能なテストが正常に動作する
   - pgvector拡張が正しく機能していることを確認

4. ✅ **統合テストが正常に動作する**
   - エンドツーエンドフローが正常に動作する
   - 複数の機能が連携して正常に動作する

5. ✅ **テスト結果が記録されている**
   - テスト結果をファイルに保存完了
   - または、テスト結果をドキュメントに記録完了

### 5.2 テスト結果の記録

**テスト結果をファイルに保存**:
```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pytest tests/ -v --tb=short > "test_results_staging_${TIMESTAMP}.txt" 2>&1
```

**テストカバレッジの確認**:
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

---

## 6. トラブルシューティング

### 6.1 よくあるエラーと対処法

#### エラー1: データベース接続エラー

**症状**: `Connection refused`、`could not connect to server`

**対処法**:
1. Railwayダッシュボードで接続情報を再確認
2. `TEST_DATABASE_URL`が正しく設定されているか確認
3. `postgresql+asyncpg://`形式を使用しているか確認
4. ネットワーク接続を確認

#### エラー2: pgvector拡張が有効化されていない

**症状**: `Extension "vector" does not exist`

**対処法**:
1. Railway PostgreSQLでpgvector拡張が有効化されていることを確認
2. `psql`で直接接続して確認: `SELECT * FROM pg_extension WHERE extname = 'vector';`
3. 必要に応じて拡張を有効化: `CREATE EXTENSION IF NOT EXISTS vector;`

#### エラー3: テーブルが存在しない

**症状**: `relation "facilities" does not exist`

**対処法**:
1. Alembicマイグレーションを実行: `alembic upgrade head`
2. テーブルが作成されているか確認: `\dt`（psqlで）

#### エラー4: Event loopエラー

**症状**: `RuntimeError: Task got Future attached to a different loop`

**対処法**:
1. pytest-asyncioの設定を確認
2. テストフィクスチャのスコープを確認
3. `conftest.py`の設定を確認

---

## 7. 完了条件チェックリスト

### 7.1 テスト実行前の確認

- [ ] Railway PostgreSQL接続情報を取得完了
- [ ] Railway Redis接続情報を取得完了
- [ ] ローカル環境で環境変数を設定完了
- [ ] `USE_POSTGRES_TEST=true`を設定完了
- [ ] `USE_OPENAI_MOCK=true`を設定完了
- [ ] テスト実行環境の準備完了

### 7.2 テスト実行後の確認

- [ ] すべてのテストがパスすることを確認
- [ ] テストカバレッジを確認（60%以上）
- [ ] pgvector検索テストが正常に動作することを確認
- [ ] 統合テストが正常に動作することを確認
- [ ] テスト結果を記録完了

---

## 8. 参考資料

- `docs/Phase1/Phase1_ステージング環境テスト計画.md`
- `docs/Phase1/Phase1_完了準備_実行ステップ.md`
- `docs/Phase1/Phase1_残存課題_完了条件_進捗状況_20251129.md`

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-01  
**Status**: ステージング環境テスト実行手順提示完了


