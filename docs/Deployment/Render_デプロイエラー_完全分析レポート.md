# Render.comデプロイエラー 完全分析レポート

**分析日時**: 2025年11月28日
**エラー**: `ModuleNotFoundError: No module named 'asyncpg'`

---

## エラーログの完全分析

### エラーの発生箇所

```
File "/opt/render/project/src/backend/alembic/env.py", line 73, in run_migrations_online
    connectable = engine_from_config(
                  ^^^^^^^^^^^^^^^^^^^
...
File "/opt/render/project/src/.venv/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 1079, in import_dbapi
    return AsyncAdapt_asyncpg_dbapi(__import__("asyncpg"))
                                    ^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'asyncpg'
```

### エラーの流れ

1. **Python 3.11.8の使用**: ✅ 成功
2. **パッケージのインストール**: ✅ 成功（`pydantic-core-2.14.6`も含む）
3. **`alembic upgrade head`の実行**: ❌ 失敗
   - `alembic/env.py`の`run_migrations_online()`関数が実行される
   - `engine_from_config()`が`postgresql+asyncpg://`形式のURLを受け取る
   - SQLAlchemyが`asyncpg`パッケージをインポートしようとする
   - `asyncpg`がインストールされていないため、エラーが発生

---

## 根本原因の分析

### 原因1: requirements.txtにasyncpgが含まれていない

**現状**:
- `requirements.txt`に`asyncpg`パッケージが含まれていない
- `sqlalchemy[asyncio]`だけでは`asyncpg`はインストールされない

**証拠**:
```txt
# Database
sqlalchemy[asyncio]==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
pgvector==0.2.4
# asyncpgが含まれていない
```

### 原因2: alembic/env.pyの設計上の問題

**現状**:
- `alembic/env.py`の`run_migrations_online()`関数は`engine_from_config()`を使用
- これは**同期エンジン**を作成する関数
- しかし、`postgresql+asyncpg://`形式のURLを使用している

**問題点**:
- Alembicは通常、**同期エンジン**を使用する
- `postgresql+asyncpg://`形式のURLは**非同期エンジン**用
- SQLAlchemyは`postgresql+asyncpg://`形式のURLを見ると、`asyncpg`パッケージをインポートしようとする
- しかし、`asyncpg`がインストールされていないため、エラーが発生

**コード**:
```python
# alembic/env.py
def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()  # postgresql+asyncpg://形式
    connectable = engine_from_config(  # 同期エンジンを作成
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
```

### 原因3: DATABASE_URLの形式の不一致

**現状**:
- Render.comの環境変数`DATABASE_URL`は`postgresql+asyncpg://`形式で設定されている
- これは`app/database.py`で使用される（非同期エンジン用）
- しかし、`alembic/env.py`でも使用されている（同期エンジン用）

**問題点**:
- `app/database.py`は非同期エンジンを使用するため、`postgresql+asyncpg://`形式が必要
- `alembic/env.py`は同期エンジンを使用するため、`postgresql://`形式が必要
- 同じ環境変数を使用しているため、形式の不一致が発生

---

## 設計上の問題点

### 問題1: Alembicとアプリケーションの接続方式の不一致

**アプリケーション側** (`app/database.py`):
- 非同期エンジンを使用（`create_async_engine`）
- `postgresql+asyncpg://`形式のURLが必要

**Alembic側** (`alembic/env.py`):
- 同期エンジンを使用（`engine_from_config`）
- `postgresql://`形式のURLが必要

### 問題2: 環境変数の使い分けができていない

**現状**:
- `DATABASE_URL`をアプリケーションとAlembicの両方で使用
- しかし、必要な形式が異なる

**理想**:
- アプリケーション用: `DATABASE_URL`（`postgresql+asyncpg://`形式）
- Alembic用: `DATABASE_URL`または別の環境変数（`postgresql://`形式）

---

## 対応策

### 対応策1: requirements.txtにasyncpgを追加（即座の対応）

**手順**:
1. `backend/requirements.txt`に`asyncpg==0.29.0`を追加
2. 変更をコミット・プッシュ
3. Render.comで再デプロイ

**メリット**:
- 最も簡単な対応
- 即座に問題を解決できる

**デメリット**:
- 設計上の問題は解決しない
- Alembicが同期エンジンを使用しているという根本的な問題は残る

### 対応策2: alembic/env.pyを非同期対応に修正（根本的な対応）

**手順**:
1. `alembic/env.py`を非同期エンジンを使用するように修正
2. `run_migrations_online()`関数を非同期関数に変更
3. `create_async_engine`を使用するように変更

**メリット**:
- 設計上の問題を解決できる
- アプリケーションとAlembicの接続方式が一致する

**デメリット**:
- 実装が複雑
- Alembicの非同期対応が必要

### 対応策3: DATABASE_URLを同期形式に変更（推奨しない）

**手順**:
1. Render.comの環境変数`DATABASE_URL`を`postgresql://`形式に変更
2. `app/database.py`で`postgresql://`を`postgresql+asyncpg://`に変換（既に実装済み）

**メリット**:
- Alembicが正常に動作する

**デメリット**:
- `app/database.py`の変換ロジックに依存する
- 環境変数の形式が直感的でない

---

## 推奨対応

### 即座の対応: 対応策1（asyncpgを追加）

**理由**:
- 最も簡単で確実な方法
- 即座に問題を解決できる
- 設計上の問題は後で対応可能

### 長期的な対応: 対応策2（Alembicを非同期対応）

**理由**:
- 設計上の問題を根本的に解決できる
- アプリケーションとAlembicの接続方式が一致する

---

## 結論

**根本原因**:
1. `requirements.txt`に`asyncpg`パッケージが含まれていない
2. `alembic/env.py`が同期エンジンを使用しているが、`postgresql+asyncpg://`形式のURLを使用している
3. SQLAlchemyが`asyncpg`パッケージをインポートしようとするが、インストールされていない

**即座の対応**:
- `requirements.txt`に`asyncpg==0.29.0`を追加

**長期的な対応**:
- `alembic/env.py`を非同期対応に修正することを検討

---

**次のステップ**: 対応策1を実装して、即座に問題を解決してください。

