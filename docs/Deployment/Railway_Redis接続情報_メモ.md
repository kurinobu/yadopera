# Railway Redis接続情報メモ

**取得日時**: 2025年11月28日
**Redisサービス**: yadopera-redis-staging

---

## Redis接続情報

### REDIS_URL（内部エンドポイント）
```
redis://default:QIpOCNjyhqyHYoaGBUWWaALyuWmVGYjd@redis.railway.internal:6379
```

**用途**: Railway内部サービス間接続用（Render.comからは使用不可）

### REDIS_PUBLIC_URL（公開エンドポイント）
```
redis://default:QIpOCNjyhqyHYoaGBUWWaALyuWmVGYjd@shuttle.proxy.rlwy.net:28858
```

**用途**: Render.comから接続する場合に使用
**注意**: 外部接続のためegress feesが発生する可能性あり

---

## Render.comでの設定

Render.comの環境変数`REDIS_URL`には、以下の値を設定:

```
redis://default:QIpOCNjyhqyHYoaGBUWWaALyuWmVGYjd@shuttle.proxy.rlwy.net:28858
```

**重要**: 
- `REDIS_PUBLIC_URL`の値を使用（外部接続のため）

---

## 次のステップ

1. Render.com Pro Web Service作成
2. 環境変数設定（DATABASE_URL、REDIS_URL等）


