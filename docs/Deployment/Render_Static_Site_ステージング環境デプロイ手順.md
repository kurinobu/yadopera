# Render.com Static Site ステージング環境デプロイ手順

**作成日**: 2025年12月13日  
**最終更新日**: 2025年12月13日  
**目的**: フロントエンドのステージング環境をRender.com Static Siteにデプロイする（修正案2）

**状態**: ✅ **デプロイ完了（2025-12-13）**

---

## 1. 前提条件

- Render.com Proアカウント（既存契約）
- GitHubリポジトリへのアクセス権限
- Render.comバックエンドサービスのURL: `https://yadopera-backend-staging.onrender.com`

## 1.1 ステージング環境URL（2025-12-13更新）

- **バックエンド**: `https://yadopera-backend-staging.onrender.com`
- **フロントエンド**: `https://yadopera-frontend-staging.onrender.com`
- **管理画面ログイン**: `https://yadopera-frontend-staging.onrender.com/admin/login`
- **テストユーザー**: `test@example.com` / `testpassword123`（問題2解決済み）

---

## 2. Render.com Static Siteの作成

### 2.1 Static Site作成

1. Render.comダッシュボードにログイン: https://dashboard.render.com
2. 「New +」→「Static Site」を選択
3. GitHubリポジトリを接続（既に接続済みの場合は選択）
4. 以下の設定を行う:
   - **Name**: `yadopera-frontend-staging`
   - **Branch**: `develop`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist`

### 2.2 環境変数設定

1. Static Siteダッシュボードで「Environment」タブを開く
2. 以下の環境変数を追加:

```bash
# APIベースURL（Render.comバックエンド）
VITE_API_BASE_URL=https://yadopera-backend-staging.onrender.com

# 環境設定
VITE_ENVIRONMENT=staging
```

**重要**: 
- `VITE_API_BASE_URL`はバックエンドのURL（Render.com Web ServiceのURL）
- 環境変数はビルド時に埋め込まれるため、変更後は再デプロイが必要

---

## 3. バックエンドのCORS設定を更新

### 3.1 Render.comの環境変数を更新

1. Render.comダッシュボードで`yadopera-backend-staging`サービスの「Environment」タブを開く
2. `CORS_ORIGINS`環境変数を更新:

```bash
CORS_ORIGINS=https://yadopera-frontend-staging.onrender.com,http://localhost:5173
```

**注意**: 
- Static Siteの実際のURLに置き換える（デプロイ後に確認）
- 複数のオリジンをカンマ区切りで指定可能
- ローカル開発環境も含める

### 3.2 環境変数の確認

- `CORS_ORIGINS`が正しく設定されているか確認
- 変更後、バックエンドサービスを再デプロイ（自動的に再デプロイされる場合もある）

---

## 4. デプロイの実行

### 4.1 自動デプロイ（推奨）

1. `develop`ブランチにプッシュすると自動的にデプロイされる
2. Render.comダッシュボードでデプロイ状況を確認

### 4.2 手動デプロイ

1. Render.comダッシュボードでStatic Siteの「Manual Deploy」をクリック
2. ブランチを選択（`develop`）
3. デプロイを実行

---

## 5. デプロイ確認

### 5.1 フロントエンドのデプロイ確認

1. Render.comダッシュボードでデプロイ状況を確認
2. デプロイが成功したら、フロントエンドのURLを確認
   - 例: `https://yadopera-frontend-staging.onrender.com`
   - または: `https://yadopera-frontend-staging-[hash].onrender.com`

### 5.2 バックエンドのCORS設定確認

1. Render.comのバックエンドサービスの環境変数を確認
2. フロントエンドのURLが`CORS_ORIGINS`に含まれているか確認
3. 含まれていない場合は、追加して再デプロイ

### 5.3 動作確認

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

## 6. トラブルシューティング

### 6.1 ビルドエラー

**症状**: ビルドが失敗する

**対処法**:
1. ビルドログを確認
2. 環境変数が正しく設定されているか確認
3. `package.json`の依存関係を確認
4. ローカル環境で`npm run build`を実行して確認

### 6.2 CORSエラー

**症状**: ブラウザのコンソールにCORSエラーが表示される

**対処法**:
1. バックエンドの`CORS_ORIGINS`環境変数を確認
2. フロントエンドのURLが`CORS_ORIGINS`に含まれているか確認
3. バックエンドサービスを再デプロイ

### 6.3 404エラー

**症状**: ページが表示されない、または404エラーが表示される

**対処法**:
1. `vite.config.ts`のルーティング設定を確認
2. ビルド出力（`dist`ディレクトリ）を確認
3. Static Siteの設定（Publish Directory）を確認

### 6.4 環境変数が反映されない

**症状**: 環境変数を設定したが、ビルド時に反映されない

**対処法**:
1. 環境変数名が`VITE_`で始まっているか確認（Viteの要件）
2. 環境変数を変更後、再デプロイを実行
3. ビルドログで環境変数が正しく読み込まれているか確認

---

## 7. 完了条件

- ✅ フロントエンドのステージング環境がデプロイされている（2025-12-13完了）
- ✅ フロントエンドのURLが確認できる: `https://yadopera-frontend-staging.onrender.com`
- ✅ バックエンドのCORS設定が正しく設定されている
- ✅ フロントエンドからバックエンドへのAPI呼び出しが正常に動作する
- ✅ 管理画面のログインとダッシュボード表示が正常に動作する
- ✅ CORSエラーが発生していない
- ✅ テストユーザーが作成されている（問題2解決済み、2025-12-13）
- ✅ PWAアイコンとvite.svgが作成されている（問題3解決済み、2025-12-13）

## 7.1 解決済みの問題（2025-12-13更新）

### 問題2: ステージング環境でテストユーザーが存在しない ✅ **解決済み**

**解決日**: 2025年12月13日  
**解決方法**: `backend/create_staging_test_data.py`を実行してテストユーザーを作成

**テストユーザー情報**:
- メールアドレス: `test@example.com`
- パスワード: `testpassword123`
- ユーザーID: 87
- 施設ID: 347
- 施設slug: `test-facility`

**状態**: ✅ ログイン可能

### 問題3: PWAアイコンとvite.svgの404エラー ✅ **解決済み**

**解決日**: 2025年12月13日  
**解決方法**: `frontend/public`ディレクトリに以下のファイルを作成

**作成したファイル**:
- `frontend/public/pwa-192x192.png`
- `frontend/public/pwa-512x512.png`
- `frontend/public/vite.svg`
- `frontend/public/favicon.ico`

**状態**: ✅ 404エラー解消

---

## 8. 参考資料

- [Render.com Documentation](https://render.com/docs)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- `docs/Phase2/Phase2_ステージング環境テスト準備_完全調査分析.md`
- `docs/Phase2/Phase2_ステージング環境ログインエラー_完全調査分析レポート.md`
- `docs/Phase2/Phase2_引き継ぎ書_20251213.md`
- `docs/Deployment/Render_Railway_手動設定_実行手順.md`（ステップ5: フロントエンド設定）
- `docs/Phase1/Phase1_引き継ぎ書.md`（11.2節: Vercelは今後使用しない）

---

**状態**: ✅ **デプロイ完了（2025-12-13）。問題2と問題3は解決済み。**

