# Phase 0 ステップ10-7: GitHub Pages移行 - リポジトリ公開手順

**作成日**: 2025年11月27日  
**目的**: プライベートリポジトリをパブリックに変更してGitHub Pagesを有効化  
**背景**: GitHub Pagesは無料アカウントの場合、パブリックリポジトリでのみ利用可能

---

## 問題の状況

現在、GitHub Pagesの設定画面に以下のメッセージが表示されています：

```
Upgrade or make this repository public to enable Pages
```

これは、リポジトリがプライベート（Private）であるため、GitHub Pagesが有効化されていないことを示しています。

---

## 解決策

### オプション1: リポジトリをパブリックに変更（推奨）

**メリット**:
- ✅ 無料でGitHub Pagesが利用可能
- ✅ ランディングページは公開情報なので問題なし

**デメリット**:
- ⚠️ コードが公開される（ただし、ランディングページは公開情報なので問題なし）

### オプション2: GitHub Proにアップグレード

**メリット**:
- ✅ プライベートリポジトリでもGitHub Pagesが利用可能

**デメリット**:
- ❌ 有料（月額$4）

---

## リポジトリをパブリックに変更する手順

### ステップ1: Settingsページを開く

1. リポジトリページ（`https://github.com/kurinobu/yadopera`）を開く

2. 上部のタブメニューから **「Settings」** をクリック

### ステップ2: Generalセクションを開く

1. 左サイドバーから **「General」** をクリック
   - 通常、一番上に表示されています

2. ページを下にスクロールして **「Danger Zone」** セクションを探す
   - ページの最下部にあります
   - 赤い背景色で表示されています

### ステップ3: Change repository visibility

1. **「Danger Zone」** セクション内で **「Change repository visibility」** を探す

2. **「Change visibility」** ボタンをクリック

3. 確認ダイアログが表示されます：
   ```
   Change repository visibility
   
   Make this repository public
   
   Anyone on the internet can see this repository. You choose who can commit.
   
   [Cancel] [I understand, change repository visibility]
   ```

4. **「I understand, change repository visibility」** ボタンをクリック

5. さらに確認ダイアログが表示されます：
   ```
   Type kurinobu/yadopera to confirm
   
   [Cancel] [I understand, change repository visibility]
   ```

6. テキストボックスに `kurinobu/yadopera` と入力

7. **「I understand, change repository visibility」** ボタンをクリック

### ステップ4: リポジトリがパブリックになったことを確認

1. リポジトリページの上部に **「Public」** というバッジが表示されることを確認

2. Settings → Pages に戻る

3. 今度は **「Build and deployment」** セクションが表示されることを確認

---

## 機密情報の確認

リポジトリをパブリックに変更する前に、以下を確認してください：

### ✅ 確認済み（問題なし）

- `.env` ファイル: `.gitignore` で除外されているため、公開されません
- APIキー: `.env` ファイルに保存されているため、公開されません
- パスワード: `.env` ファイルに保存されているため、公開されません

### ⚠️ 確認が必要

- `landing/index.html`: 公開情報なので問題なし
- `docs/`: ドキュメントなので問題なし（機密情報が含まれていないことを確認）
- `backend/`: コードが公開されます（通常は問題なし）
- `frontend/`: コードが公開されます（通常は問題なし）

---

## リポジトリをパブリックに変更した後の手順

リポジトリをパブリックに変更した後、以下の手順でGitHub Pagesを設定してください：

### ステップ1: GitHub Pages設定

1. Settings → Pages に戻る

2. **「Build and deployment」** セクションが表示されていることを確認

3. **「Source」** の設定：
   - **「Deploy from a branch」** を選択
   - **「Branch」**: `main` を選択
   - **「Folder」**: `/landing` を選択

4. **「Save」** ボタンをクリック

### ステップ2: カスタムドメイン設定

1. **「Custom domain」** セクションで `yadopera.com` を入力

2. **「Save」** ボタンをクリック

3. DNS設定の指示に従って、ムームードメインでDNS設定を変更

---

## 代替案: GitHub Actionsを使用（プライベートリポジトリのまま）

もしリポジトリをパブリックにしたくない場合、GitHub Actionsを使用してGitHub Pagesにデプロイすることもできます。ただし、この方法でもGitHub Pagesはパブリックリポジトリでのみ利用可能です。

---

## 推奨事項

**ランディングページは公開情報なので、リポジトリをパブリックに変更することを推奨します。**

理由：
1. 無料でGitHub Pagesが利用可能
2. ランディングページは公開情報なので問題なし
3. コードが公開されても、機密情報（APIキー等）は `.env` ファイルに保存されており、`.gitignore` で除外されているため安全

---

## 次のステップ

リポジトリをパブリックに変更した後：

1. Settings → Pages で **「Build and deployment」** セクションが表示されることを確認
2. Source設定を実施（`main` ブランチ、`/landing` フォルダ）
3. カスタムドメイン設定を実施（`yadopera.com`）
4. DNS設定を変更（CNAMEレコード: `@` → `kurinobu.github.io`）

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27  
**Status**: リポジトリ公開手順完成


