# pgvector拡張有効化 実行手順

**方法**: Railway CLIを使用してSQLを実行

---

## ステップ1: Railwayにログイン

ターミナルで以下を実行:

```bash
railway login
```

ブラウザが開くので、Railwayアカウントでログインしてください。

---

## ステップ2: プロジェクトをリンク

ログイン後、以下を実行:

```bash
railway link
```

プロジェクトを選択するよう求められたら、PostgreSQLサービスが作成されているプロジェクトを選択してください。

---

## ステップ3: PostgreSQLサービスに接続

以下を実行:

```bash
railway connect postgres
```

psqlが起動します。

---

## ステップ4: pgvector拡張を有効化

psqlが起動したら、以下のSQLを実行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## ステップ5: 確認

拡張が有効化されたか確認:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

結果が表示されれば、拡張は有効化されています。

---

## ステップ6: psqlを終了

```sql
\q
```

または `Ctrl+D` で終了

---

**次のステップ**: pgvector拡張の有効化が完了したら、Redisサービスの追加に進みます。


