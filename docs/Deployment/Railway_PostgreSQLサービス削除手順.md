# Railway PostgreSQLサービス削除手順

---

## 削除手順

### ステップ1: Railwayダッシュボードでサービスを選択

1. Railwayダッシュボードにアクセス: https://railway.app
2. プロジェクト「yadopera-postgres-staging」を開く
3. 左側のサイドバーで、削除したいPostgreSQLサービス（「Postgres」など）をクリック

### ステップ2: Settingsタブを開く

1. サービスを選択した状態で、上部のタブから「**Settings**」タブをクリック

### ステップ3: サービスを削除

1. Settingsタブの下部に「**Delete Service**」または「**Remove Service**」というボタンがある
2. ボタンをクリック
3. 確認ダイアログが表示される
4. サービス名を入力して確認（「Postgres」など）
5. 「Delete」または「Remove」ボタンをクリック

---

## 注意事項

- **削除すると、データベース内のすべてのデータが失われます**
- ステージング環境でまだデータがない場合は問題ありません
- 削除後、新しいPostgreSQLサービス（pgvector-pg17）を作成します

---

## 次のステップ

削除が完了したら:
1. 「New」→「Database」→「**pgvector-pg17**」を選択
2. 新しいPostgreSQLサービスを作成
3. サービス名: `yadopera-postgres-staging`
4. 新しい接続URLを取得

