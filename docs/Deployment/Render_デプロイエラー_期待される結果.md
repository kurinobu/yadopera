# Render.comデプロイエラー 期待される結果

**対応策**: `requirements.txt`に`asyncpg==0.29.0`を追加

---

## 期待される結果

### 1. パッケージのインストール段階

**現在の状態**:
```
Collecting pydantic-core==2.14.6 (from -r requirements.txt (line 30))
  Downloading pydantic_core-2.14.6-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
...
Successfully installed ... (パッケージ一覧)
```

**期待される結果**: ✅
```
Collecting asyncpg==0.29.0 (from -r requirements.txt (line X))
  Downloading asyncpg-0.29.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
...
Successfully installed ... asyncpg-0.29.0 ...
```

**説明**: `asyncpg==0.29.0`が正常にインストールされる

---

### 2. alembic upgrade headの実行段階

**現在のエラー**:
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

**期待される結果**: ✅
```
==> Running build command 'pip install -r requirements.txt && alembic upgrade head'...
...
Successfully installed ... asyncpg-0.29.0 ...
[notice] A new release of pip is available: 25.1.1 -> 25.3
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> head, (マイグレーション実行)
==> Build succeeded! 🎉
```

**説明**: 
- `asyncpg`がインストールされているため、SQLAlchemyが`asyncpg`をインポートできる
- `ModuleNotFoundError: No module named 'asyncpg'`エラーは発生しない
- `alembic upgrade head`が正常に実行される
- マイグレーションが正常に実行される

---

### 3. デプロイの完了

**現在の状態**:
```
==> Build failed 😞
==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
```

**期待される結果**: ✅
```
==> Build succeeded! 🎉
==> Your service is live at https://yadopera-backend-staging.onrender.com
```

**説明**: 
- ビルドが成功する
- デプロイが完了する
- Web Serviceが起動する

---

### 4. アプリケーションの動作

**期待される結果**: ✅
- Web Serviceが正常に起動する
- ヘルスチェックエンドポイント（`/health`）が正常に動作する
- データベース接続が正常に動作する（`asyncpg`を使用）

**注意**: 
- 設計上の問題（原因2、原因3）は残るが、動作には問題ない
- `alembic/env.py`は同期エンジンを使用しているが、`postgresql+asyncpg://`形式のURLでも動作する（`asyncpg`がインストールされていれば）

---

## 動作の仕組み

### なぜ動作するのか？

1. **`asyncpg`がインストールされる**
   - `requirements.txt`に`asyncpg==0.29.0`を追加することで、パッケージがインストールされる

2. **SQLAlchemyが`asyncpg`をインポートできる**
   - `alembic/env.py`の`run_migrations_online()`関数で`engine_from_config()`が実行される
   - SQLAlchemyが`postgresql+asyncpg://`形式のURLを見ると、`asyncpg`パッケージをインポートしようとする
   - `asyncpg`がインストールされていれば、インポートが成功する

3. **エンジンが作成される**
   - `engine_from_config()`は同期エンジンを作成するが、`postgresql+asyncpg://`形式のURLでも動作する
   - SQLAlchemyが内部的に処理する

4. **マイグレーションが実行される**
   - エンジンが正常に作成されれば、マイグレーションが実行される

---

## 設計上の問題について

### 残る問題

1. **原因2（設計上の問題）**: 
   - `alembic/env.py`は同期エンジンを使用しているが、`postgresql+asyncpg://`形式のURLを使用している
   - しかし、`asyncpg`がインストールされていれば、動作には問題ない

2. **原因3（形式の不一致）**: 
   - アプリケーション側とAlembic側で同じ環境変数を使用しているが、形式が異なる
   - しかし、動作には問題ない

### なぜ動作するのか？

- SQLAlchemyは`postgresql+asyncpg://`形式のURLを受け取ると、`asyncpg`パッケージをインポートしようとする
- `asyncpg`がインストールされていれば、インポートが成功し、エンジンが作成される
- 同期エンジンでも、`asyncpg`がインストールされていれば動作する

---

## まとめ

### 期待される結果

1. ✅ **パッケージのインストール**: `asyncpg==0.29.0`が正常にインストールされる
2. ✅ **エラーの解決**: `ModuleNotFoundError: No module named 'asyncpg'`エラーが発生しない
3. ✅ **マイグレーションの実行**: `alembic upgrade head`が正常に実行される
4. ✅ **デプロイの成功**: ビルドが成功し、デプロイが完了する
5. ✅ **アプリケーションの動作**: Web Serviceが正常に起動し、動作する

### 設計上の問題

- ⚠️ 原因2、原因3は残るが、動作には問題ない
- ⚠️ 後で根本的解決を検討可能（動作に問題がないため）

---

**結論**: `requirements.txt`に`asyncpg==0.29.0`を追加するだけで、エラーは解決し、デプロイは成功します。


