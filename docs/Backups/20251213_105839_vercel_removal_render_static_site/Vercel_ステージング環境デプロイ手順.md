# Vercel ステージング環境デプロイ手順

**作成日**: 2025年12月13日  
**目的**: フロントエンドのステージング環境をVercelにデプロイする

---

## 1. 前提条件

- Vercelアカウント（GitHubアカウントでログイン可能）
- GitHubリポジトリへのアクセス権限
- Render.comバックエンドサービスのURL: `https://yadopera-backend-staging.onrender.com`

---

## 2. Vercelプロジェクトの作成

### 2.1 プロジェクト作成

1. Vercelダッシュボードにログイン: https://vercel.com/dashboard
2. 「Add New」→「Project」を選択
3. GitHubリポジトリを選択（`kurinobu/yadopera`）
4. 以下の設定を行う:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`（デフォルト）
   - **Output Directory**: `dist`（デフォルト）
   - **Install Command**: `npm install`（デフォルト）

### 2.2 ブランチ設定

1. 「Settings」→「Git」タブを開く
2. 以下の設定を行う:
   - **Production Branch**: `main`
   - **Preview Branches**: `develop`（ステージング環境として使用）

---

## 3. 環境変数設定

### 3.1 環境変数の追加

1. Vercelプロジェクトの「Settings」→「Environment Variables」タブを開く
2. 以下の環境変数を追加:

#### Production環境（mainブランチ）
```bash
VITE_API_BASE_URL=https://yadopera-backend.onrender.com
VITE_ENVIRONMENT=production
```

#### Preview環境（developブランチ）
```bash
VITE_API_BASE_URL=https://yadopera-backend-staging.onrender.com
VITE_ENVIRONMENT=staging
```

**重要**: 
- `VITE_API_BASE_URL`はバックエンドのURL（Render.com Web ServiceのURL）
- 環境変数はビルド時に埋め込まれるため、変更後は再デプロイが必要

### 3.2 環境変数の確認

環境変数が正しく設定されているか確認:
- Production環境: `main`ブランチ用
- Preview環境: `develop`ブランチ用

---

## 4. バックエンドのCORS設定を更新

### 4.1 Render.comの環境変数を更新

1. Render.comダッシュボードにログイン
2. `yadopera-backend-staging`サービスの「Environment」タブを開く
3. `CORS_ORIGINS`環境変数を更新:

```bash
CORS_ORIGINS=https://yadopera-frontend-staging.vercel.app,http://localhost:5173
```

**注意**: 
- Vercelの実際のURLに置き換える（デプロイ後に確認）
- 複数のオリジンをカンマ区切りで指定可能
- ローカル開発環境も含める

### 4.2 環境変数の確認

- `CORS_ORIGINS`が正しく設定されているか確認
- 変更後、バックエンドサービスを再デプロイ（自動的に再デプロイされる場合もある）

---

## 5. デプロイの実行

### 5.1 自動デプロイ（推奨）

1. `develop`ブランチにプッシュすると自動的にデプロイされる
2. Vercelダッシュボードでデプロイ状況を確認

### 5.2 手動デプロイ

1. Vercelダッシュボードで「Deployments」タブを開く
2. 「Deploy」ボタンをクリック
3. ブランチを選択（`develop`）
4. デプロイを実行

---

## 6. デプロイ確認

### 6.1 フロントエンドのデプロイ確認

1. Vercelダッシュボードでデプロイ状況を確認
2. デプロイが成功したら、フロントエンドのURLを確認
   - 例: `https://yadopera-frontend-staging.vercel.app`
   - または: `https://yadopera-frontend-staging-[hash].vercel.app`

### 6.2 バックエンドのCORS設定確認

1. Render.comのバックエンドサービスの環境変数を確認
2. フロントエンドのURLが`CORS_ORIGINS`に含まれているか確認
3. 含まれていない場合は、追加して再デプロイ

### 6.3 動作確認

1. **フロントエンドのURLにアクセス**
   - ルートページが表示されることを確認
   - 管理画面のログイン画面が表示されることを確認

2. **ログイン**
   - テストユーザーでログイン（`test@example.com` / `testpassword123`）
   - ログインが成功することを確認

3. **ダッシュボード表示**
   - ログイン後、ダッシュボードが表示されることを確認
   - ブラウザの開発者ツール（Networkタブ）でAPI呼び出しが正常に動作することを確認

4. **CORSエラーの確認**
   - ブラウザの開発者ツール（Consoleタブ）でCORSエラーが発生していないか確認
   - CORSエラーが発生している場合は、バックエンドの`CORS_ORIGINS`設定を再確認

---

## 7. GitHub Actionsの設定確認

### 7.1 シークレットの設定

GitHub Actionsで自動デプロイする場合は、以下のシークレットを設定:

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 以下のシークレットを追加:
   - `VERCEL_TOKEN`: Vercelのアクセストークン
   - `VERCEL_ORG_ID`: Vercelの組織ID
   - `VERCEL_PROJECT_ID`: VercelのプロジェクトID

### 7.2 Vercelトークンの取得

1. Vercelダッシュボードで「Settings」→「Tokens」を開く
2. 「Create Token」をクリック
3. トークン名を入力（例: `github-actions-staging`）
4. トークンをコピーしてGitHubのシークレットに設定

### 7.3 組織IDとプロジェクトIDの取得

1. Vercelダッシュボードでプロジェクトの「Settings」→「General」を開く
2. 「Project ID」をコピー
3. 「Team ID」または「Organization ID」をコピー

---

## 8. トラブルシューティング

### 8.1 ビルドエラー

**症状**: ビルドが失敗する

**対処法**:
1. ビルドログを確認
2. 環境変数が正しく設定されているか確認
3. `package.json`の依存関係を確認
4. ローカル環境で`npm run build`を実行して確認

### 8.2 CORSエラー

**症状**: ブラウザのコンソールにCORSエラーが表示される

**対処法**:
1. バックエンドの`CORS_ORIGINS`環境変数を確認
2. フロントエンドのURLが`CORS_ORIGINS`に含まれているか確認
3. バックエンドサービスを再デプロイ

### 8.3 404エラー

**症状**: ページが表示されない、または404エラーが表示される

**対処法**:
1. `vercel.json`の`rewrites`設定を確認
2. ルーティング設定を確認
3. ビルド出力（`dist`ディレクトリ）を確認

### 8.4 環境変数が反映されない

**症状**: 環境変数を設定したが、ビルド時に反映されない

**対処法**:
1. 環境変数名が`VITE_`で始まっているか確認（Viteの要件）
2. 環境変数を変更後、再デプロイを実行
3. ビルドログで環境変数が正しく読み込まれているか確認

---

## 9. 完了条件

- ✅ フロントエンドのステージング環境がデプロイされている
- ✅ フロントエンドのURLが確認できる
- ✅ バックエンドのCORS設定が正しく設定されている
- ✅ フロントエンドからバックエンドへのAPI呼び出しが正常に動作する
- ✅ 管理画面のログインとダッシュボード表示が正常に動作する
- ✅ CORSエラーが発生していない

---

## 10. 参考資料

- [Vercel Documentation](https://vercel.com/docs)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- `docs/Phase2/Phase2_ステージング環境テスト準備_完全調査分析.md`
- `.github/workflows/staging-deploy.yml`
- `frontend/vercel.json`

---

**次のステップ**: Vercelプロジェクトを作成し、環境変数を設定してデプロイを実行する

