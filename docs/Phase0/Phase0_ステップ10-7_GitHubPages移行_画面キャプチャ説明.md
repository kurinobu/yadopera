# Phase 0 ステップ10-7: GitHub Pages移行 画面説明

**作成日**: 2025年11月27日  
**目的**: GitHub Pages設定画面の具体的な見つけ方と操作方法

---

## GitHub Pages設定画面の見つけ方

### ステップ1: Settingsページにアクセス

1. リポジトリページ（`https://github.com/kurinobu/yadopera`）を開く

2. 上部のタブメニューから **「Settings」** をクリック
   ```
   [Code] [Issues] [Pull requests] [Actions] [Projects] [Wiki] [Security] [Insights] [Settings]
                                                                                        ↑ここ
   ```

### ステップ2: Pagesセクションを見つける

Settingsページの左サイドバーを確認します。以下のいずれかの場所にあります：

#### パターン1: 「Code and automation」セクション内
```
左サイドバー:
├─ General
├─ Access
├─ Secrets and variables
├─ Actions
├─ Code and automation
│  ├─ Actions
│  ├─ Pages          ← ここ
│  └─ Environments
└─ ...
```

#### パターン2: 直接表示されている場合
```
左サイドバー:
├─ General
├─ Access
├─ Secrets and variables
├─ Actions
├─ Pages             ← ここ（直接表示）
└─ ...
```

**見つからない場合**:
- 左サイドバーを下にスクロールしてください
- ブラウザの検索機能（Cmd+F または Ctrl+F）で「Pages」を検索してください

### ステップ3: Build and deployment セクションを確認

Pagesページを開くと、以下のような構成になっています：

```
┌─────────────────────────────────────────┐
│  GitHub Pages                            │
├─────────────────────────────────────────┤
│                                          │
│  Build and deployment                    │ ← このセクションを探す
│  ┌───────────────────────────────────┐  │
│  │ Source                            │  │ ← ここにSourceがある
│  │ [Deploy from a branch ▼]          │  │
│  │                                    │  │
│  │ Branch: [main ▼]                   │  │
│  │ Folder: [/ (root) ▼]              │  │
│  │                                    │  │
│  │ [Save]                             │  │
│  └───────────────────────────────────┘  │
│                                          │
│  Custom domain                           │
│  ┌───────────────────────────────────┐  │
│  │ [yadopera.com]                    │  │
│  │ [Save]                             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 具体的な操作手順

### 1. Source設定の見つけ方

**「Build and deployment」** セクションを探してください：

1. ページの上部または中央に **「Build and deployment」** という見出しがあります
2. その下に **「Source」** という項目があります
3. もし見つからない場合：
   - ページを下にスクロールしてください
   - ブラウザの検索機能（Cmd+F または Ctrl+F）で「Source」を検索してください

### 2. Source設定の操作方法

1. **「Source」** のドロップダウンをクリック
   - デフォルトで **「Deploy from a branch」** が選択されているはずです
   - もし選択されていない場合は、ドロップダウンから選択してください

2. **「Branch」** のドロップダウンをクリック
   - `main` を選択してください
   - もし `main` が表示されない場合は、利用可能なブランチを確認してください

3. **「Folder」** の設定：
   - ドロップダウンから `/ (root)` を選択
   - その後、テキストボックスに `/landing` と入力
   - または、ドロップダウンに `/landing` が表示されている場合は、それを選択

4. **「Save」** ボタンをクリック
   - 設定が保存されます
   - 保存後、デプロイが開始されます

---

## もし「Source」セクションが見つからない場合

### 確認事項

1. **権限の確認**:
   - リポジトリの管理者権限が必要です
   - 権限が不足している場合、設定項目が表示されないことがあります

2. **GitHub Pagesが有効になっているか確認**:
   - もしGitHub Pagesが初めて設定する場合、まず有効化する必要があるかもしれません

3. **ブラウザのキャッシュをクリア**:
   - ブラウザのキャッシュをクリアして、ページを再読み込みしてください

4. **別のブラウザで試す**:
   - 別のブラウザ（Chrome、Firefox、Safari等）で試してください

### 代替方法: GitHub Actionsを使用

もし「Source」セクションが見つからない場合、GitHub Actionsを使用してデプロイすることもできます：

1. `.github/workflows/pages.yml` ファイルを作成
2. 以下の内容を記述：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'landing/**'

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Pages
        uses: actions/configure-pages@v2
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v1
        with:
          path: './landing'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v1
```

---

## 画面のスクリーンショット例

### 期待される画面構成

```
GitHub Pages Settings
├─ Build and deployment
│  └─ Source
│     ├─ Deploy from a branch
│     ├─ Branch: main
│     └─ Folder: /landing
│
└─ Custom domain
   └─ yadopera.com
```

---

## トラブルシューティング

### 問題: 「Build and deployment」セクションが見つからない

**解決策**:
1. ページを下にスクロールしてください
2. ブラウザの検索機能（Cmd+F または Ctrl+F）で「Build」を検索してください
3. 別のブラウザで試してください

### 問題: 「Source」ドロップダウンが表示されない

**解決策**:
1. ページを再読み込みしてください（Cmd+R または Ctrl+R）
2. ブラウザのキャッシュをクリアしてください
3. 別のブラウザで試してください

### 問題: 「Folder」に `/landing` が設定できない

**解決策**:
1. ドロップダウンから `/ (root)` を選択
2. その後、テキストボックスに `/landing` と直接入力してください
3. 保存後、正しく設定されているか確認してください

---

## 参考資料

- **GitHub Pages公式ドキュメント**: https://docs.github.com/ja/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- **GitHub Pages設定**: https://docs.github.com/ja/pages

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27  
**Status**: 画面説明完成


