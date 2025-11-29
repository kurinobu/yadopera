# Phase 0 ステップ10-7: GitHub Pages移行 - GitHub Actions設定手順

**作成日**: 2025年11月27日  
**目的**: GitHub Actionsを使用して `/landing` フォルダをGitHub Pagesにデプロイ  
**背景**: GitHub Pagesは標準で `/` と `/docs` のみをサポート。`/landing` は認識されないため、GitHub Actionsを使用

---

## 問題の状況

GitHub Pagesの設定画面で「Folder」に `/landing` を入力しても「見つからない」とエラーが表示されます。

これは、GitHub Pagesが標準でサポートしているフォルダが以下のみであるためです：
- `/` (root)
- `/docs`

`/landing` は標準的なフォルダではないため、GitHub Pagesが認識しません。

---

## 解決策: GitHub Actionsを使用

GitHub Actionsを使用して、`/landing` フォルダをGitHub Pagesにデプロイします。

### ステップ1: GitHub Actionsワークフローファイルの作成

既に以下のファイルが作成されています：
- `.github/workflows/pages.yml`

このファイルは、`landing` フォルダの内容をGitHub Pagesにデプロイする設定です。

### ステップ2: ファイルをコミット・プッシュ

1. ターミナルで以下のコマンドを実行：

```bash
cd /Users/kurinobu/projects/yadopera
git add .github/workflows/pages.yml
git commit -m "Add GitHub Actions workflow for Pages deployment from /landing folder"
git push origin main
```

### ステップ3: GitHub Pages設定（ブラウザ作業）

1. GitHubリポジトリの **Settings → Pages** にアクセス

2. **「Build and deployment」** セクションで以下を設定：
   - **「Source」**: **「GitHub Actions」** を選択
     - ドロップダウンから **「GitHub Actions」** を選択
     - これにより、GitHub Actionsワークフローがデプロイを担当します

3. **「Save」** ボタンをクリック

### ステップ4: デプロイの確認

1. GitHubリポジトリの **「Actions」** タブを開く

2. **「Deploy to GitHub Pages」** ワークフローを確認
   - ステータスが **「✓」**（成功）になっていることを確認
   - 失敗している場合は、ログを確認してエラーを修正

3. デプロイが完了すると、GitHub PagesのURLが表示されます：
   - 通常は `https://kurinobu.github.io/yadopera/` のような形式

### ステップ5: カスタムドメイン設定

1. Settings → Pages に戻る

2. **「Custom domain」** セクションで `yadopera.com` を入力

3. **「Save」** ボタンをクリック

4. DNS設定の指示に従って、ムームードメインでDNS設定を変更

---

## GitHub Actionsワークフローの動作

### トリガー条件

- `main` ブランチにプッシュされたとき
- `landing/**` パスのファイルが変更されたとき

### デプロイプロセス

1. **Checkout**: リポジトリのコードを取得
2. **Setup Pages**: GitHub Pagesの設定
3. **Upload artifact**: `landing` フォルダの内容をアップロード
4. **Deploy to GitHub Pages**: GitHub Pagesにデプロイ

---

## トラブルシューティング

### 問題1: GitHub Actionsワークフローが実行されない

**解決策**:
1. Actionsタブでワークフローが表示されているか確認
2. ワークフローが表示されない場合、ファイルが正しくコミット・プッシュされているか確認
3. `.github/workflows/pages.yml` の構文エラーを確認

### 問題2: デプロイが失敗する

**解決策**:
1. Actionsタブで失敗したワークフローのログを確認
2. よくある原因：
   - `landing` フォルダが存在しない
   - `index.html` が存在しない
   - ファイルのパーミッション問題

### 問題3: GitHub PagesのSource設定で「GitHub Actions」が表示されない

**解決策**:
1. ワークフローファイルが正しくコミット・プッシュされているか確認
2. ワークフローが少なくとも1回実行されているか確認
3. ブラウザのキャッシュをクリアして、ページを再読み込み

---

## メリット

### GitHub Actionsを使用するメリット

1. ✅ **柔軟性**: 任意のフォルダからデプロイ可能
2. ✅ **自動デプロイ**: `landing` フォルダの変更を検知して自動デプロイ
3. ✅ **カスタマイズ可能**: デプロイプロセスをカスタマイズ可能
4. ✅ **標準的な方法**: GitHub Pagesの推奨される方法

---

## 次のステップ

GitHub Actionsワークフローを設定した後：

1. ファイルをコミット・プッシュ
2. Settings → Pages で **「Source」** を **「GitHub Actions」** に変更
3. カスタムドメイン設定（`yadopera.com`）
4. DNS設定変更（CNAMEレコード: `@` → `kurinobu.github.io`）

---

## 参考資料

- **GitHub Actions公式ドキュメント**: https://docs.github.com/ja/actions
- **GitHub Pages with Actions**: https://docs.github.com/ja/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27  
**Status**: GitHub Actions設定手順完成

