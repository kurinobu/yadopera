# pgvector拡張確認 次のステップ

**現在の状態**: pgvector-pg17テンプレートで新しいPostgreSQLサービスを作成完了

---

## 次のステップ

### ステップ1: 新しいPostgreSQLサービスでpgvector拡張を確認

1. 新しいPostgreSQLサービスを選択
2. 「Extensions」タブを開く
3. `vector` で検索
4. pgvector拡張が表示されるか確認

### ステップ2: pgvector拡張を有効化

pgvector拡張が表示されたら、有効化します。

**方法1: Extensionsタブから有効化**
- `vector` 拡張を見つける
- 「Enable」や「Add」ボタンをクリック

**方法2: Railway CLIでSQLを実行**
- `railway connect postgres` で接続
- `CREATE EXTENSION IF NOT EXISTS vector;` を実行

### ステップ3: 接続情報を取得

1. 新しいPostgreSQLサービスの「Variables」タブを開く
2. `DATABASE_URL` と `DATABASE_PUBLIC_URL` を確認
3. 接続URLをメモ（後でRender.comに設定）

---

## 確認事項

- [ ] 新しいPostgreSQLサービスが作成されている
- [ ] pgvector拡張が利用可能か確認
- [ ] pgvector拡張を有効化
- [ ] 接続URLを取得

