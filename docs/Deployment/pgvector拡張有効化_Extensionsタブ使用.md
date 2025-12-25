# pgvector拡張有効化手順（Extensionsタブ使用）

**現在の状態**: Databaseタブを開いている
**表示されているタブ**: Data, Extensions, Credentials, Connect

---

## ステップ: Extensionsタブでpgvectorを有効化

### 1. Extensionsタブを開く

1. 「Database」タブ内の「**Extensions**」タブをクリック
2. Extensionsタブが開きます

### 2. pgvector拡張を探す

Extensionsタブには、利用可能な拡張の一覧が表示されるはずです。

**確認事項**:
- `vector` または `pgvector` という拡張があるか確認
- 拡張の一覧が表示されているか確認
- 「Enable」や「Add」ボタンがあるか確認

### 3. pgvector拡張を有効化

**方法1: 拡張一覧から有効化**
- `vector` または `pgvector` を見つける
- 「Enable」や「Add」ボタンをクリック
- または、拡張名をクリックして有効化

**方法2: 検索機能がある場合**
- 検索ボックスに「vector」と入力
- 見つかった拡張を有効化

---

## 代替方法: Railway CLIを使用

Extensionsタブでpgvectorが見つからない場合、Railway CLIを使用することもできます。

### Railway CLIで接続

1. ターミナルで以下を実行:

```bash
# Railway CLIがインストールされている場合
railway connect postgres
```

2. psqlが起動したら、以下のSQLを実行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. 確認:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## 確認方法

拡張が有効化されたか確認する場合:

1. Extensionsタブで `vector` が有効（Enabled）になっているか確認
2. または、以下のSQLを実行（CLIまたは別の方法で）:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

**次のステップ**: pgvector拡張の有効化が完了したら、Redisサービスの追加に進みます。


