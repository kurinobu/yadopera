# Phase 2: ステージング環境テストユーザー作成手順

**作成日**: 2025年12月13日  
**目的**: ステージング環境のデータベースにテストユーザーを作成する

---

## 1. 前提条件

- Railway PostgreSQLの接続情報を取得済み
- ローカル環境にPython 3.11+がインストールされている
- バックエンドの依存関係がインストールされている

---

## 2. ステージング環境のデータベース接続情報の取得

### 2.1 Railway PostgreSQL接続情報の取得

1. Railwayダッシュボードにアクセス: https://railway.app
2. プロジェクトを選択
3. PostgreSQLサービスを選択
4. 「Variables」タブで接続情報を確認:
   - `DATABASE_PUBLIC_URL`（公開エンドポイント）をコピー
   - 形式: `postgresql://postgres:password@host:port/database`

**注意**: テストユーザー作成には`DATABASE_PUBLIC_URL`を使用します（外部接続用）

---

## 3. テストユーザー作成スクリプトの実行

### 3.1 環境変数の設定

```bash
cd /Users/kurinobu/projects/yadopera/backend

# Railwayダッシュボードから取得した接続情報を使用
export DATABASE_URL="postgresql://postgres:password@host:port/database"

# その他の環境変数（必要に応じて）
export SECRET_KEY="your-secret-key"
```

### 3.2 テストユーザー作成スクリプトの実行

```bash
# ステージング環境用テストデータ作成スクリプトを実行
python create_staging_test_data.py
```

### 3.3 実行結果の確認

**成功時の出力**:
```
✅ 既存のテスト施設を使用します: ID=1, slug=test-facility
✅ テストユーザーを作成しました: ID=1, email=test@example.com

✅ ステージング環境のテストデータ作成が完了しました！

テストユーザー情報:
  メールアドレス: test@example.com
  パスワード: testpassword123
  施設slug: test-facility

管理画面ログインURL: https://yadopera-frontend-staging.onrender.com/admin/login
```

---

## 4. ログインの確認

1. ブラウザで `https://yadopera-frontend-staging.onrender.com/admin/login` にアクセス
2. テストユーザーでログイン:
   - メールアドレス: `test@example.com`
   - パスワード: `testpassword123`
3. ログインが成功することを確認

---

## 5. トラブルシューティング

### 5.1 接続エラー

**エラー**: `Connection refused` または `Connection timeout`

**対処法**:
- Railway PostgreSQLの`DATABASE_PUBLIC_URL`が正しいか確認
- Railway PostgreSQLが起動しているか確認
- ファイアウォール設定を確認

### 5.2 認証エラー

**エラー**: `password authentication failed`

**対処法**:
- Railway PostgreSQLのパスワードが正しいか確認
- `DATABASE_URL`の形式が正しいか確認（`postgresql://`形式）

### 5.3 パスワードハッシュエラー

**エラー**: `bcrypt`の互換性問題

**対処法**:
- スクリプトは自動的に`bcrypt`のフォールバックを使用します
- それでもエラーが発生する場合は、`bcrypt`のバージョンを確認

---

## 6. 参考資料

- `backend/create_staging_test_data.py`
- `backend/create_test_data.py`
- Railway PostgreSQL接続情報: https://railway.app

---

**次のステップ**: ログインが成功したら、ステージング環境での機能テストを実施してください。

