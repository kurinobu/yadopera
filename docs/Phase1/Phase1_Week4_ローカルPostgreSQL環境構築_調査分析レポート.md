# Phase 1 Week 4 ローカルPostgreSQL環境構築 調査分析レポート

**作成日**: 2025年11月28日  
**目的**: ローカルPostgreSQL環境構築のための調査分析  
**対象**: pgvector検索テストを実行可能にするための環境構築

---

## 1. 現状分析

### 1.1 現在のテスト環境

**テストデータベース設定** (`backend/tests/conftest.py`):
- **使用DB**: SQLite（メモリ内）: `sqlite+aiosqlite:///:memory:`
- **問題点**: 
  - pgvector拡張が使用できない
  - `test_vector_search.py`のpgvector検索テストがスキップされている
  - Week 2で実装したRAG機能のテストが実行できない

**スキップされているテスト**:
```python
@pytest.mark.skip(reason="pgvector is not available in SQLite test database")
async def test_search_similar_faqs_with_data(...)
```

### 1.2 既存のPostgreSQL環境

**docker-compose.yml設定**:
- **イメージ**: `pgvector/pgvector:pg15`
- **ポート**: `5433:5432`（ホスト:コンテナ）
- **ユーザー**: `yadopera_user`
- **パスワード**: `yadopera_password`
- **データベース**: `yadopera`
- **拡張**: pgvector拡張対応済み

**pgvector拡張有効化**:
- マイグレーション: `001_enable_pgvector.py`
- コマンド: `CREATE EXTENSION IF NOT EXISTS vector`

### 1.3 データベース接続設定

**本番/開発環境** (`backend/app/database.py`):
- 非同期接続: `postgresql+asyncpg://`
- 接続プール: `pool_size=20`, `max_overflow=10`
- 設定: `app/core/config.py`から`DATABASE_URL`を取得

**テスト環境** (`backend/tests/conftest.py`):
- 現在: SQLite（メモリ内）
- 必要: PostgreSQL + pgvector対応

---

## 2. 要件定義

### 2.1 目的

1. **pgvector検索テストの実行**
   - `test_vector_search.py`の全テストを実行可能にする
   - Week 2で実装したRAG機能のテストを実行可能にする

2. **テスト環境の分離**
   - 本番/開発環境（`yadopera`）とテスト環境（`yadopera_test`）を分離
   - テスト実行時にテスト用データベースを使用

3. **環境変数による切り替え**
   - `USE_POSTGRES_TEST=true`でPostgreSQLテスト環境を有効化
   - デフォルトはSQLite（既存テストとの互換性維持）

### 2.2 必要な機能

1. **テスト用PostgreSQLデータベース作成**
   - データベース名: `yadopera_test`
   - pgvector拡張有効化
   - マイグレーション実行

2. **conftest.pyの修正**
   - PostgreSQLテスト環境のサポート追加
   - 環境変数による切り替え
   - テスト用データベースの初期化・クリーンアップ

3. **テスト実行方法**
   - 通常テスト: `pytest`（SQLite使用）
   - pgvectorテスト: `USE_POSTGRES_TEST=true pytest`（PostgreSQL使用）

---

## 3. 実装方針

### 3.1 アプローチ

**ハイブリッドアプローチ**:
- **デフォルト**: SQLite（既存テストとの互換性維持）
- **オプション**: PostgreSQL（pgvectorテスト用）

**理由**:
- 既存のSQLiteテストを壊さない
- pgvectorが必要なテストのみPostgreSQLを使用
- 環境変数による簡単な切り替え

### 3.2 実装手順

1. **テスト用データベース作成**
   - `docker-compose.yml`にテスト用データベース追加（オプション）
   - または、既存のPostgreSQLコンテナに`yadopera_test`データベース作成

2. **conftest.py修正**
   - 環境変数`USE_POSTGRES_TEST`のチェック
   - PostgreSQLテスト環境のセットアップ
   - pgvector拡張有効化
   - テスト用データベースの初期化・クリーンアップ

3. **テストマーカー追加**
   - `@pytest.mark.postgres`: PostgreSQL必須テスト
   - `@pytest.mark.skipif`: PostgreSQL未使用時にスキップ

4. **ドキュメント更新**
   - テスト実行方法の説明
   - 環境変数の説明

---

## 4. 技術的詳細

### 4.1 テスト用データベースURL

**PostgreSQLテスト環境**:
```
postgresql+asyncpg://yadopera_user:yadopera_password@localhost:5433/yadopera_test
```

**SQLiteテスト環境**（既存）:
```
sqlite+aiosqlite:///:memory:
```

### 4.2 conftest.py修正内容

**追加機能**:
1. 環境変数`USE_POSTGRES_TEST`のチェック
2. PostgreSQLテスト環境のセットアップ
3. pgvector拡張有効化
4. テスト用データベースの初期化（マイグレーション実行）
5. テスト後のクリーンアップ（テーブル削除）

**実装例**:
```python
import os
USE_POSTGRES_TEST = os.getenv("USE_POSTGRES_TEST", "false").lower() == "true"

if USE_POSTGRES_TEST:
    TEST_DATABASE_URL = "postgresql+asyncpg://yadopera_user:yadopera_password@localhost:5433/yadopera_test"
    # PostgreSQLテスト環境のセットアップ
else:
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    # SQLiteテスト環境のセットアップ
```

### 4.3 pgvector拡張有効化

**方法1: マイグレーション実行**
```python
async with test_engine.begin() as conn:
    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    await conn.run_sync(Base.metadata.create_all)
```

**方法2: 手動実行**
```sql
CREATE DATABASE yadopera_test;
\c yadopera_test
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4.4 テストマーカー

**pytest.iniに追加**:
```ini
markers =
    postgres: requires PostgreSQL + pgvector
```

**テストでの使用**:
```python
@pytest.mark.postgres
@pytest.mark.asyncio
async def test_search_similar_faqs_with_data(...):
    # PostgreSQL + pgvectorが必要なテスト
    pass
```

---

## 5. 実装チェックリスト

### 5.1 データベース準備

- [ ] テスト用データベース`yadopera_test`作成
- [ ] pgvector拡張有効化確認
- [ ] 接続確認（`psql`またはPythonスクリプト）

### 5.2 conftest.py修正

- [ ] 環境変数`USE_POSTGRES_TEST`のチェック追加
- [ ] PostgreSQLテスト環境のセットアップ追加
- [ ] pgvector拡張有効化処理追加
- [ ] テスト用データベースの初期化処理追加
- [ ] テスト後のクリーンアップ処理追加

### 5.3 テストマーカー追加

- [ ] `pytest.ini`に`postgres`マーカー追加
- [ ] `test_vector_search.py`にマーカー追加
- [ ] その他のpgvectorテストにマーカー追加

### 5.4 テスト実行確認

- [ ] SQLiteテストが正常に実行される（既存テスト）
- [ ] PostgreSQLテストが正常に実行される（`USE_POSTGRES_TEST=true pytest`）
- [ ] pgvector検索テストが正常に実行される
- [ ] テストカバレッジが適切である

### 5.5 ドキュメント更新

- [ ] README.mdにテスト実行方法追加
- [ ] 環境変数の説明追加
- [ ] トラブルシューティング追加

---

## 6. 実行手順（実装後）

### 6.1 テスト用データベース作成

```bash
# Docker ComposeでPostgreSQLコンテナ起動
docker-compose up -d postgres

# テスト用データベース作成
docker-compose exec postgres psql -U yadopera_user -d postgres -c "CREATE DATABASE yadopera_test;"

# pgvector拡張有効化
docker-compose exec postgres psql -U yadopera_user -d yadopera_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 6.2 テスト実行

**通常テスト（SQLite）**:
```bash
cd backend
pytest
```

**PostgreSQLテスト（pgvector検索テスト含む）**:
```bash
cd backend
USE_POSTGRES_TEST=true pytest
```

**特定のテストのみ実行**:
```bash
cd backend
USE_POSTGRES_TEST=true pytest tests/test_vector_search.py -v
```

### 6.3 マイグレーション実行（テスト用データベース）

```bash
cd backend
# テスト用データベースにマイグレーション実行
DATABASE_URL=postgresql://yadopera_user:yadopera_password@localhost:5433/yadopera_test alembic upgrade head
```

---

## 7. 注意事項

### 7.1 データベース分離

- **本番/開発環境**: `yadopera`データベース
- **テスト環境**: `yadopera_test`データベース
- **理由**: テスト実行時のデータ汚染を防ぐ

### 7.2 テスト実行前の確認

- PostgreSQLコンテナが起動していること
- テスト用データベースが作成されていること
- pgvector拡張が有効化されていること

### 7.3 パフォーマンス

- PostgreSQLテストはSQLiteテストより遅い可能性がある
- テスト実行時間を考慮して、必要なテストのみPostgreSQLを使用

### 7.4 環境変数の扱い

- `USE_POSTGRES_TEST`は環境変数として設定
- `.env`ファイルには含めない（テスト実行時に指定）
- CI/CDでは環境変数として設定

---

## 8. トラブルシューティング

### 8.1 よくある問題

**問題1: データベース接続エラー**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
- **解決策**: PostgreSQLコンテナが起動しているか確認
- **確認**: `docker-compose ps postgres`

**問題2: pgvector拡張エラー**
```
ERROR: extension "vector" does not exist
```
- **解決策**: pgvector拡張を有効化
- **実行**: `CREATE EXTENSION IF NOT EXISTS vector;`

**問題3: テスト用データベースが存在しない**
```
FATAL: database "yadopera_test" does not exist
```
- **解決策**: テスト用データベースを作成
- **実行**: `CREATE DATABASE yadopera_test;`

**問題4: マイグレーションエラー**
```
alembic.util.exc.CommandError: Target database is not up to date
```
- **解決策**: テスト用データベースにマイグレーション実行
- **実行**: `alembic upgrade head`

---

## 9. 参考資料

### 9.1 関連ドキュメント

- **Phase 0引き継ぎ書**: `docs/Phase0/Phase0_引き継ぎ書.md` セクション5（Docker環境）
- **Phase 1 Week 4ステップ計画**: `docs/Phase1/Phase1_Week4_ステップ計画.md` 残存課題
- **Phase 1 Week 2ステップ計画**: `docs/Phase1/Phase1_Week2_ステップ計画.md` ステップ6（pgvector検索実装）

### 9.2 技術資料

- **pgvector公式ドキュメント**: https://github.com/pgvector/pgvector
- **SQLAlchemy非同期接続**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **pytest環境変数**: https://docs.pytest.org/en/stable/how-to/usage.html#environment-variables

---

## 10. 次のステップ

### 10.1 実装準備完了

この調査分析レポートに基づいて、以下の実装を準備：

1. **conftest.py修正**
   - PostgreSQLテスト環境のサポート追加
   - 環境変数による切り替え

2. **テスト用データベース作成**
   - `yadopera_test`データベース作成
   - pgvector拡張有効化

3. **テストマーカー追加**
   - `pytest.ini`にマーカー追加
   - テストファイルにマーカー追加

4. **ドキュメント更新**
   - README.mdにテスト実行方法追加

### 10.2 実装指示待ち

**ユーザーの指示があるまで修正しない**（調査分析のみ完了）

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025-11-28  
**Status**: 調査分析完了、実装準備完了


