# pgvector-pg17 PostgreSQLサービス作成手順

---

## 作成手順

### ステップ1: Railwayダッシュボードで新しいデータベースを追加

1. Railwayダッシュボードでプロジェクト「yadopera-postgres-staging」を開く
2. 「**New**」ボタンをクリック
3. 「**Database**」を選択
4. テンプレート一覧から「**pgvector-pg17**」を選択
   - 「Open-source vector similarity search for Postgres」という説明があるもの

### ステップ2: サービス名を設定

1. サービス名を設定: `yadopera-postgres-staging`（または任意の名前）
2. 作成を確認

### ステップ3: 接続情報を取得

1. 新しいPostgreSQLサービスが作成される
2. サービスの「**Variables**」タブを開く
3. `DATABASE_URL` と `DATABASE_PUBLIC_URL` を確認
4. 接続URLをメモ（後でRender.comに設定）

---

## 次のステップ

新しいPostgreSQLサービスが作成されたら:
1. Railway CLIで接続してpgvector拡張を確認
2. pgvector拡張を有効化
3. 接続URLをRender.comに設定


