# pgvector拡張有効化手順（Connectタブ使用）

**現在の状態**: Extensionsタブで「vector」を検索したが、拡張が見つからない
**解決方法**: Connectタブから接続情報を取得して、psqlでSQLを実行

---

## ステップ: Connectタブから接続してSQLを実行

### 方法1: Railway CLIを使用（推奨）

#### 1. Railway CLIのインストール確認

ターミナルで以下を実行:

```bash
railway --version
```

インストールされていない場合:

```bash
# macOS
brew install railway

# または npm経由
npm install -g @railway/cli
```

#### 2. Railwayにログイン

```bash
railway login
```

ブラウザが開くので、Railwayアカウントでログイン

#### 3. プロジェクトとサービスを選択

```bash
# プロジェクトを選択
railway link

# PostgreSQLサービスに接続
railway connect postgres
```

#### 4. pgvector拡張を有効化

psqlが起動したら、以下のSQLを実行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 5. 確認

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

結果が表示されれば、拡張は有効化されています。

---

### 方法2: Connectタブから接続情報を取得してpsqlで接続

#### 1. Connectタブを開く

1. 「Database」タブ内の「**Connect**」タブをクリック
2. Connectタブが開きます

#### 2. 接続情報を確認

Connectタブには、以下のような接続情報が表示されるはずです:
- 接続URL
- ホスト名、ポート、データベース名、ユーザー名、パスワード

#### 3. ローカルのpsqlで接続

ターミナルで以下を実行（接続情報を実際の値に置き換える）:

```bash
psql "postgresql://postgres:パスワード@ホスト名:ポート/データベース名"
```

または、接続情報を個別に指定:

```bash
psql -h ホスト名 -p ポート -U postgres -d データベース名
```

パスワードを入力するよう求められたら、Variablesタブで確認したパスワードを入力

#### 4. pgvector拡張を有効化

psqlが接続できたら、以下のSQLを実行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 5. 確認

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

### 方法3: Render.comのShellから実行（後で実行）

pgvector拡張の有効化は、Render.comのデプロイ後でも実行可能です。

1. Render.comのWeb Serviceの「Shell」タブを開く
2. 以下のコマンドでPostgreSQLに接続:

```bash
psql $DATABASE_URL
```

3. SQLを実行:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 推奨方法

**方法1（Railway CLI）**を推奨します。最も簡単で確実です。

---

**次のステップ**: pgvector拡張の有効化が完了したら、Redisサービスの追加に進みます。


