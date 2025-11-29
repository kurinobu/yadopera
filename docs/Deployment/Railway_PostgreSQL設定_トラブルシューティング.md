# Railway PostgreSQL設定 トラブルシューティング

**状況**: PostgreSQLサービス追加時にサービス名入力画面が表示されない

---

## 現在の状態

- Databaseタブが開いている
- "You have no tables"と表示されている
- "Create table"ボタンがある

**これは正常な状態です**。PostgreSQLサービスは既に作成されています。

---

## 次のステップ

### ステップ1: サービス名の確認・変更

1. Railwayダッシュボードの左側のサイドバーを確認
2. 現在のプロジェクト内のサービス一覧を確認
3. PostgreSQLサービスが表示されているはずです
4. サービス名を変更する場合:
   - サービス名をクリック
   - 「Settings」タブを開く
   - 「Service Name」を変更: `yadopera-postgres-staging`
   - 保存

### ステップ2: 接続情報（DATABASE_URL）の取得

1. PostgreSQLサービスの「Variables」タブを開く
2. `DATABASE_URL`という環境変数を探す
3. 値をコピー（後でRender.comに設定）
   - 形式: `postgresql://user:password@host:port/database`
4. または「Connect」タブを開いて接続情報を確認

**重要**: 接続URLをメモしてください。

### ステップ3: pgvector拡張の有効化

1. PostgreSQLサービスの「Data」タブを開く（現在開いているタブ）
2. 「Query」または「SQL」タブを開く
3. 以下のSQLを実行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

4. 実行結果を確認（成功メッセージが表示される）

---

## 確認事項

- [ ] PostgreSQLサービスが作成されている
- [ ] サービス名が`yadopera-postgres-staging`（または適切な名前）
- [ ] `DATABASE_URL`が取得できている
- [ ] pgvector拡張が有効化されている

---

## 次のステップ

pgvector拡張の有効化が完了したら、次はRedisサービスの追加に進みます。

