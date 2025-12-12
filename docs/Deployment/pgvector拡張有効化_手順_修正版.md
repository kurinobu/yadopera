# pgvector拡張有効化手順（修正版）

**現在の状態**: Variablesタブを開いている
**利用可能なタブ**: Deployments, Database, Backups, Variables, Metrics, Settings

---

## ステップ: DatabaseタブでSQLを実行

### 1. Databaseタブに移動

1. 上部のタブ一覧から「**Database**」タブをクリック
2. Databaseタブが開きます

### 2. Query/SQLエディタを探す

「Database」タブを開いたら、以下のいずれかを探してください:

- **「Query」タブ**または**「SQL」タブ**がある場合: それをクリック
- **「Query Editor」**や**「SQL Editor」**というボタンがある場合: それをクリック
- **直接SQLを入力できるテキストエリア**がある場合: そこを使用
- **「Run Query」**や**「Execute」**ボタンがある場合: その近くにSQL入力エリアがあるはず

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

### DatabaseタブにSQLエディタがない場合

1. 「Database」タブ内に別のサブタブ（Query, SQL, Editor等）がないか確認
2. 画面の上部や下部に「Query」や「SQL」というボタンがないか確認
3. 別の方法として、Railway CLIを使用することも可能:
   ```bash
   railway connect postgres
   ```
   その後、psqlで接続してSQLを実行

---

**次のステップ**: pgvector拡張の有効化が完了したら、Redisサービスの追加に進みます。


