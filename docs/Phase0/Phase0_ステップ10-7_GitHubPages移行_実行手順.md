# Phase 0 ステップ10-7: GitHub Pages移行 実行手順

**作成日**: 2025年11月27日  
**目的**: VercelからGitHub Pagesへの移行を実行  
**所要時間**: 約15分（DNS設定反映待ち含む）

---

## 前提条件

- ✅ Google Analytics 4プロパティ作成完了（測定ID: `G-BE9HZ0XGH4`）
- ✅ HTMLに測定ID設定完了（コミット: `4eddb00`）
- ✅ カスタムドメイン `yadopera.com` のDNS設定完了（Aレコード: `@` → `216.198.79.1`）
- ✅ `landing/index.html` が最新の状態でコミット済み
- ⚠️ **重要**: リポジトリがパブリック（Public）である必要があります
  - プライベートリポジトリの場合、まずリポジトリをパブリックに変更してください
  - 詳細は `Phase0_ステップ10-7_GitHubPages移行_リポジトリ公開手順.md` を参照

---

## バックアップ

### 作成済みバックアップ

- `landing/vercel.json.backup_YYYYMMDD_HHMMSS`: Vercel設定ファイルのバックアップ
- `landing/index.html.backup_20251127_090808`: Google Analytics設定前のバックアップ

---

## 移行手順

### ステップ0: リポジトリをパブリックに変更（必要な場合）

**重要**: もしSettings → Pagesで「Upgrade or make this repository public to enable Pages」というメッセージが表示されている場合、まずリポジトリをパブリックに変更する必要があります。

詳細な手順は `Phase0_ステップ10-7_GitHubPages移行_リポジトリ公開手順.md` を参照してください。

**簡単な手順**:
1. Settings → General → Danger Zone → Change repository visibility
2. 「Make this repository public」を選択
3. 確認ダイアログで `kurinobu/yadopera` と入力して確認

### ステップ1: GitHub Pages設定（ブラウザ作業）

#### 1-1. GitHubリポジトリにアクセス

1. ブラウザで以下のURLにアクセス:
   ```
   https://github.com/kurinobu/yadopera
   ```

2. GitHubアカウントでログイン（未ログインの場合）

#### 1-2. Settingsページを開く

1. リポジトリページの上部メニューから **「Settings」** をクリック
   - 場所: リポジトリ名の右側、メニューバーの最後

2. 左サイドバーから **「Pages」** をクリック
   - 場所: Settingsページの左サイドバー
   - **「Code and automation」** セクション内の **「Pages」** を探してください
   - もし見つからない場合は、左サイドバーを下にスクロールして探してください

#### 1-3. Build and deployment セクションでSource設定

1. **「Build and deployment」** セクションを探す
   - ページの上部または中央に表示されています
   - このセクション内に **「Source」** という項目があります

2. **「Source」** の設定:
   - **「Deploy from a branch」** を選択（デフォルトで選択されているはず）
   - もし選択されていない場合は、ドロップダウンから **「Deploy from a branch」** を選択

3. **「Branch」** の設定:
   - **「Branch」** ドロップダウンから `main` を選択
   - もし `main` が表示されない場合は、ブランチ名を確認してください

4. **「Folder」** の設定:
   - **「Folder」** ドロップダウンから `/ (root)` を選択
   - その後、テキストボックスに `/landing` と入力
   - または、ドロップダウンに `/landing` が表示されている場合は、それを選択

5. **「Save」** ボタンをクリック
   - 設定を保存します

#### 1-4. カスタムドメイン設定

1. **「Custom domain」** セクションで以下を設定:
   - テキストボックスに `yadopera.com` と入力
   - **「Save」** ボタンをクリック

2. 警告メッセージが表示される場合:
   - 「DNS設定が必要」という警告が表示されます
   - これは正常です。次のステップでDNS設定を行います

3. GitHub Pagesが提供するDNS設定情報を確認:
   - カスタムドメイン設定後、GitHub Pagesが推奨するDNS設定が表示されます
   - 通常は以下のいずれか:
     - **CNAMEレコード**: `@` → `kurinobu.github.io`
     - または **Aレコード**: `@` → GitHub PagesのIPアドレス（複数）

---

### ステップ2: DNS設定変更（ブラウザ作業）

#### 2-1. ムームードメイン管理画面にアクセス

1. ブラウザで以下のURLにアクセス:
   ```
   https://muumuu-domain.com/
   ```

2. ムームードメインアカウントでログイン

#### 2-2. ドメイン管理画面を開く

1. ログイン後、**「ドメイン」** または **「ドメイン設定」** をクリック

2. `yadopera.com` を選択

3. **「DNS設定」** または **「DNSレコード設定」** をクリック

#### 2-3. 既存のAレコードを削除

1. 現在設定されているAレコードを確認:
   - レコードタイプ: `A`
   - ホスト名: `@`（または空欄）
   - 値: `216.198.79.1`（VercelのIPアドレス）

2. このAレコードを削除:
   - レコードの右側にある **「削除」** または **「×」** ボタンをクリック
   - 確認ダイアログで **「削除」** をクリック

#### 2-4. CNAMEレコードを追加

1. **「レコード追加」** または **「新規追加」** ボタンをクリック

2. 以下の情報を入力:
   - **レコードタイプ**: `CNAME` を選択
   - **ホスト名**: `@`（または空欄、ルートドメインを意味する）
   - **値**: `kurinobu.github.io` を入力
   - **TTL**: デフォルト値（通常は3600）のまま

3. **「保存」** または **「追加」** ボタンをクリック

#### 2-5. DNS設定の反映を待つ

1. DNS設定の反映には通常 **5-30分** かかります
2. 反映状況を確認する方法:
   - コマンドラインで確認:
     ```bash
     dig yadopera.com +short
     # または
     nslookup yadopera.com
     ```
   - オンラインツールで確認:
     - https://dnschecker.org/
     - https://www.whatsmydns.net/

---

### ステップ3: デプロイ確認（ブラウザ作業）

#### 3-1. GitHub Pagesのデプロイ状況を確認

1. GitHubリポジトリの **「Actions」** タブを開く
   - 場所: リポジトリページの上部メニュー

2. **「pages build and deployment」** ワークフローを確認
   - ステータスが **「✓」**（成功）になっていることを確認
   - 失敗している場合は、ログを確認してエラーを修正

#### 3-2. カスタムドメインのSSL証明書確認

1. GitHubリポジトリの **「Settings」** → **「Pages」** に戻る

2. カスタムドメイン設定セクションで以下を確認:
   - **「Enforce HTTPS」** チェックボックスが表示されている
   - チェックボックスにチェックを入れる（SSL証明書が自動で設定される）
   - SSL証明書の設定には **数分から数時間** かかる場合があります

#### 3-3. サイトアクセステスト

1. ブラウザで以下のURLにアクセス:
   ```
   https://yadopera.com
   ```

2. ページが正常に表示されることを確認:
   - ランディングページの全セクションが表示される
   - スタイリングが正しく適用されている
   - フォームが表示される

3. もしページが表示されない場合:
   - DNS設定の反映を待つ（最大30分）
   - ブラウザのキャッシュをクリア（Cmd+Shift+R または Ctrl+Shift+R）
   - 別のブラウザで試す

---

### ステップ4: Google Analytics動作確認（ブラウザ作業）

#### 4-1. 開発者ツールで確認

1. `https://yadopera.com` にアクセス

2. ブラウザの開発者ツールを開く:
   - **Chrome/Edge**: `F12` または `Cmd+Option+I`（Mac）/ `Ctrl+Shift+I`（Windows）
   - **Firefox**: `F12` または `Cmd+Option+I`（Mac）/ `Ctrl+Shift+I`（Windows）
   - **Safari**: `Cmd+Option+I`（開発者メニューを有効化する必要があります）

3. **「Network」** タブを開く

4. ページをリロード（`Cmd+R` または `Ctrl+R`）

5. ネットワークリクエストを確認:
   - フィルターに `gtag` または `google-analytics` と入力
   - `gtag/js?id=G-BE9HZ0XGH4` のリクエストが送信されていることを確認
   - ステータスが `200`（成功）であることを確認

#### 4-2. Google Analyticsリアルタイムレポートで確認

1. [Google Analytics](https://analytics.google.com/) にアクセス

2. プロパティ **「やどぺら LP」** を選択

3. 左サイドバーから **「レポート」** → **「リアルタイム」** → **「概要」** をクリック

4. 別のブラウザまたはタブで `https://yadopera.com` にアクセス

5. リアルタイムレポートで以下を確認:
   - **「現在のユーザー数」** が `1` 以上になっている
   - **「ページビュー」** が記録されている
   - **「ページ」** セクションに `/` が表示されている

---

## 完了基準

- [ ] GitHub Pages設定完了（Source: `main` ブランチ、`/landing` フォルダ）
- [ ] カスタムドメイン設定完了（`yadopera.com`）
- [ ] DNS設定変更完了（CNAMEレコード: `@` → `kurinobu.github.io`）
- [ ] `https://yadopera.com` でページが正常に表示される
- [ ] SSL証明書が有効（HTTPSでアクセス可能）
- [ ] Google Analyticsのリクエストが送信されている（開発者ツールで確認）
- [ ] Google Analyticsのリアルタイムレポートでアクセスが記録されている

---

## トラブルシューティング

### 問題1: GitHub Pagesがデプロイされない

**症状**: Actionsタブでワークフローが失敗している

**解決策**:
1. Actionsタブで失敗したワークフローのログを確認
2. よくある原因:
   - `/landing` フォルダが存在しない
   - `index.html` が存在しない
   - ファイルのパーミッション問題
3. ログを確認してエラーを修正

### 問題2: カスタムドメインが設定できない

**症状**: GitHub Pagesでカスタムドメインを設定してもエラーが表示される

**解決策**:
1. DNS設定が正しく行われているか確認
2. DNS設定の反映を待つ（最大30分）
3. GitHub Pagesのカスタムドメイン設定画面でDNS設定を再確認

### 問題3: DNS設定が反映されない

**症状**: `https://yadopera.com` にアクセスしてもページが表示されない

**解決策**:
1. DNS設定の反映を待つ（最大30分）
2. オンラインツール（https://dnschecker.org/）でDNS設定を確認
3. ブラウザのキャッシュをクリア
4. 別のブラウザまたはデバイスで試す

### 問題4: SSL証明書が設定されない

**症状**: HTTPSでアクセスできない、または警告が表示される

**解決策**:
1. GitHub PagesのSettings → Pagesで **「Enforce HTTPS」** チェックボックスを確認
2. SSL証明書の設定には数分から数時間かかる場合があります
3. しばらく待ってから再度確認

### 問題5: Google Analyticsが動作しない

**症状**: 開発者ツールで `gtag` のリクエストが送信されていない

**解決策**:
1. `landing/index.html` の測定IDが正しく設定されているか確認（`G-BE9HZ0XGH4`）
2. ブラウザの拡張機能（広告ブロッカー等）を無効化して試す
3. 別のブラウザで試す
4. Google Analyticsのリアルタイムレポートで確認（数分遅延する場合があります）

---

## 次のステップ

移行完了後、以下を実施:

1. **ステップ10-6: 動作確認**（約10分）
   - `https://yadopera.com` でアクセス確認
   - Google Analyticsのリアルタイムレポートで確認
   - 測定ID `G-BE9HZ0XGH4` が正しく動作しているか確認

2. **Phase 0完了確認**
   - すべてのステップが完了したことを確認
   - Phase 1（MVP開発）の準備を開始

---

## 参考資料

- **GitHub Pages公式ドキュメント**: https://docs.github.com/ja/pages
- **カスタムドメイン設定**: https://docs.github.com/ja/pages/configuring-a-custom-domain-for-your-github-pages-site
- **Vercel代替案検討**: `docs/Phase0/Phase0_Vercel代替案検討.md`
- **GitHub Pagesデプロイ手順**: `docs/Phase0/Phase0_ランディングページ_デプロイ手順_GitHubPages.md`

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27  
**Status**: 実行手順完成、バックアップ作成済み

