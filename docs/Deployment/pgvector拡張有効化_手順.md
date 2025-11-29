# pgvector拡張有効化手順

**現在の状態**: Variablesタブを開いている

---

## ステップ: Dataタブに移動してSQLを実行

### 1. Dataタブに移動

1. Railwayダッシュボードの左側のサイドバーで、PostgreSQLサービスを確認
2. サービス名をクリック（または既に選択されている）
3. 上部のタブから「**Data**」タブをクリック
   - 現在は「Variables」タブにいるので、「Data」タブに切り替える

### 2. Query/SQLタブを開く

1. 「Data」タブが開いたら、以下のいずれかを確認:
   - 「Query」タブがある場合: それをクリック
   - 「SQL」タブがある場合: それをクリック
   - 「Query Editor」や「SQL Editor」というボタンがある場合: それをクリック
   - 直接SQLを入力できるテキストエリアがある場合: そこを使用

### 3. pgvector拡張を有効化

以下のSQLを実行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**実行方法**:
- SQLを入力エリアに貼り付け
- 「Run」または「Execute」ボタンをクリック
- または「Enter」キーを押す（エディタによって異なる）

### 4. 実行結果を確認

- 成功メッセージが表示される
- エラーがないことを確認

---

## 確認方法

拡張が有効化されたか確認する場合、以下のSQLを実行:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

結果が表示されれば、拡張は有効化されています。

---

## トラブルシューティング

### Dataタブが見つからない場合

1. 左側のサイドバーでPostgreSQLサービスが選択されているか確認
2. サービス名をクリックしてサービス詳細を開く
3. 上部のタブ一覧を確認（Variables, Data, Settings, Metrics等）

### SQLを実行できない場合

1. 「Query」や「SQL」タブが表示されているか確認
2. 別の方法として、Railway CLIを使用することも可能:
   ```bash
   railway connect postgres
   ```
   その後、psqlで接続してSQLを実行

---

**次のステップ**: pgvector拡張の有効化が完了したら、Redisサービスの追加に進みます。

