# Railway PostgreSQL接続情報メモ

**取得日時**: 2025年11月28日

---

## PostgreSQL接続情報

### DATABASE_URL（内部エンドポイント）
```
postgresql://postgres:yWKgjgfhAMJXUEQHmqNgLQxalXQsbZNh@postgres.railway.internal:5432/railway
```

**用途**: Railway内部サービス間接続用（Render.comからは使用不可）

### DATABASE_PUBLIC_URL（公開エンドポイント）
```
postgresql://postgres:yWKgjgfhAMJXUEQHmqNgLQxalXQsbZNh@hopper.proxy.rlwy.net:23201/railway
```

**用途**: Render.comから接続する場合に使用
**注意**: 外部接続のためegress feesが発生する可能性あり

---

## Render.comでの設定

Render.comの環境変数`DATABASE_URL`には、以下の形式で設定:

```
postgresql+asyncpg://postgres:yWKgjgfhAMJXUEQHmqNgLQxalXQsbZNh@hopper.proxy.rlwy.net:23201/railway
```

**重要**: 
- `postgresql://`を`postgresql+asyncpg://`に変更
- `DATABASE_PUBLIC_URL`の値を使用（外部接続のため）

---

## 次のステップ

1. pgvector拡張の有効化
2. Redisサービスの追加
3. Render.comでの環境変数設定


