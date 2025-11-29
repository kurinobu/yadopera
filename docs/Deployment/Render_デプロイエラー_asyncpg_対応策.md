# Render.comデプロイエラー asyncpg 対応策

**エラー内容**: `ModuleNotFoundError: No module named 'asyncpg'`

**原因**: 
- `requirements.txt`に`asyncpg`パッケージが含まれていない
- `DATABASE_URL`が`postgresql+asyncpg://`形式のため、`asyncpg`パッケージが必要
- `sqlalchemy[asyncio]`をインストールしても、`asyncpg`は別途インストールする必要がある

---

## 対応策

### 対応策: requirements.txtにasyncpgを追加

**手順**:
1. `backend/requirements.txt`を編集
2. Databaseセクションに`asyncpg`を追加

**修正内容**:

`backend/requirements.txt`のDatabaseセクションに以下を追加:

```txt
# Database
sqlalchemy[asyncio]==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0  # 追加
pgvector==0.2.4
```

**注意**: `asyncpg`のバージョンは、`sqlalchemy[asyncio]`と互換性のあるバージョンを指定してください。

---

## 実装手順

1. `backend/requirements.txt`を編集
2. `asyncpg==0.29.0`を追加（Databaseセクション）
3. 変更をコミット・プッシュ
   ```bash
   git add backend/requirements.txt
   git commit -m "Fix: Add asyncpg to requirements.txt for Render.com deployment"
   git push origin develop
   ```
4. Render.comで自動的に再デプロイが開始される

---

## 確認事項

- `asyncpg`はPostgreSQLの非同期ドライバーです
- `postgresql+asyncpg://`形式の接続URLを使用する場合、`asyncpg`パッケージが必要です
- `sqlalchemy[asyncio]`だけでは`asyncpg`はインストールされません

---

**次のステップ**: `requirements.txt`に`asyncpg`を追加して、再デプロイしてください。

