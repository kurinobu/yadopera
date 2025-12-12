# pgvector拡張有効化 実行手順（詳細版）

**現在のディレクトリ**: `landing`
**推奨**: プロジェクトルートディレクトリから実行

---

## ステップ1: プロジェクトルートディレクトリに移動

現在 `landing` ディレクトリにいるので、プロジェクトルートに移動:

```bash
cd /Users/kurinobu/projects/yadopera
```

または、相対パスで:

```bash
cd ..
```

---

## ステップ2: Railwayにログイン

プロジェクトルートディレクトリで以下を実行:

```bash
railway login
```

**Enterキーを押すと**、ブラウザが開きます。Railwayアカウントでログインしてください。

---

## ステップ3: プロジェクトをリンク

ログイン後、以下を実行:

```bash
railway link
```

プロジェクトを選択するよう求められたら、PostgreSQLサービスが作成されているプロジェクトを選択してください。

---

## ステップ4: PostgreSQLサービスに接続

以下を実行:

```bash
railway connect postgres
```

psqlが起動します。

---

## ステップ5: pgvector拡張を有効化

psqlが起動したら、以下のSQLを実行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## ステップ6: 確認

拡張が有効化されたか確認:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

結果が表示されれば、拡張は有効化されています。

---

## ステップ7: psqlを終了

```sql
\q
```

または `Ctrl+D` で終了

---

**次のステップ**: pgvector拡張の有効化が完了したら、Redisサービスの追加に進みます。


