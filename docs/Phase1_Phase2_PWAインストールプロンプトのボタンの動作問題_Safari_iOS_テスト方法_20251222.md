# Phase 1・Phase 2: PWAインストールプロンプトのボタンの動作問題 Safari（iOS）テスト方法

**作成日時**: 2025年12月22日 10時05分03秒
**実施者**: AI Assistant  
**目的**: Safari（iOS）でのPWAインストールプロンプトのテスト方法を説明  
**状態**: 📋 **Safari（iOS）テスト方法説明完了**

---

## 1. Safari（iOS）でのPWAインストールの特徴

### 1.1 Safari（iOS）の制限事項

**重要な注意点**:
- ⚠️ **Safari（iOS）では`beforeinstallprompt`イベントが発火しない**
- ⚠️ **カスタムインストールプロンプトは表示されない**
- ✅ **Safari（iOS）では、手動で「ホーム画面に追加」機能を使用する必要がある**

### 1.2 Safari（iOS）でのPWAインストール方法

**標準的な方法**:
1. Safariでページを開く
2. 共有ボタン（□↑アイコン）をタップ
3. 「ホーム画面に追加」を選択
4. アイコン名を確認して「追加」をタップ

**カスタムプロンプトの動作**:
- `PWAInstallPrompt.vue`コンポーネントは表示されない（`beforeinstallprompt`イベントが発火しないため）
- しかし、手動で「ホーム画面に追加」機能を使用してPWAをインストールできる

---

## 2. Safari（iOS）でのテスト方法

### 2.1 開発者ツールの設定

**手順**:

1. **iPadの設定を変更**:
   - 「設定」→「Safari」→「詳細」
   - 「Webインスペクタ」を有効にする

2. **MacのSafariで開発者ツールを開く**:
   - MacのSafariで「開発」メニューを表示
   - メニューバーから「Safari」→「環境設定」→「詳細」
   - 「メニューバーに"開発"メニューを表示」にチェックを入れる
   - メニューバーから「開発」→ iPadのデバイス名を選択
   - 開いているページを選択

3. **開発者ツールが開く**:
   - MacのSafariで開発者ツールが開く
   - iPadのページが表示される

---

### 2.2 localStorageの削除方法

**手順**:

1. **MacのSafariの開発者ツールを開く**（上記の手順で開く）

2. **Storageタブを開く**:
   - 左側メニューから「Storage」を選択
   - 「Local Storage」を選択
   - 現在のドメイン（例: `https://yadopera-frontend-staging.onrender.com`）を選択

3. **`pwa_install_dismissed`キーを削除**:
   - `pwa_install_dismissed`キーを探す
   - キーを選択して「Delete」ボタンをクリック、または右クリック → 「Delete」を選択

4. **iPadでページをリロード**:
   - iPadのSafariでページをリロード

**注意**: Safari（iOS）では`beforeinstallprompt`イベントが発火しないため、カスタムプロンプトは表示されません。しかし、localStorageを削除することで、他の状態をリセットできます。

---

### 2.3 Service Workerの確認方法

**手順**:

1. **MacのSafariの開発者ツールを開く**

2. **Storageタブを開く**:
   - 左側メニューから「Storage」を選択
   - 「Service Workers」を選択

3. **Service Workerの状態を確認**:
   - 登録されているService Workerの状態を確認
   - 状態が「activated」または「waiting」の場合、Service Workerは正常に登録されている

4. **Service Workerを削除する場合**:
   - Service Workerを選択して「Unregister」ボタンをクリック

---

### 2.4 manifest.jsonの確認方法

**手順**:

1. **MacのSafariの開発者ツールを開く**

2. **Storageタブを開く**:
   - 左側メニューから「Storage」を選択
   - 「Manifest」を選択

3. **manifest.jsonの内容を確認**:
   - `start_url`、`scope`、`display`が正しく設定されているか確認
   - エラーメッセージが表示されていないか確認

---

## 3. Safari（iOS）でのPWAインストールテスト

### 3.1 手動インストールのテスト

**手順**:

1. **iPadのSafariでステージング環境のURLにアクセス**
   - `https://yadopera-frontend-staging.onrender.com/f/test-facility?location=entrance`

2. **Service Workerが登録されるまで待つ**（数秒）

3. **手動で「ホーム画面に追加」を実行**:
   - 共有ボタン（□↑アイコン）をタップ
   - 「ホーム画面に追加」を選択
   - アイコン名を確認して「追加」をタップ

4. **ホーム画面にアイコンが追加されることを確認**

5. **アイコンをタップしてアプリを起動**:
   - ホーム画面のアイコンをタップ
   - アプリが起動することを確認
   - **404エラーが発生しないことを確認**

6. **QRコードで読み取ったURLへのアクセスの確認**:
   - QRコードを読み取る（例: `/f/test-facility?location=entrance`）
   - 施設独自の画面が正常に表示されることを確認

---

### 3.2 インストール後の動作確認

**確認項目**:

1. **ホーム画面のアイコンをタップ**:
   - ✅ アプリが起動する
   - ✅ 404エラーが発生しない
   - ✅ `start_url: '/'`にアクセスする
   - ✅ Vue Routerが正しく初期化される
   - ✅ アプリが正常に起動する

2. **QRコードで読み取ったURLへのアクセス**:
   - ✅ QRコードを読み取る（例: `/f/test-facility?location=entrance`）
   - ✅ 施設独自の画面が正常に表示される
   - ✅ PWAインストール済みでも、QRコードで読み取ったURLに正常にアクセスできる

---

## 4. Safari（iOS）でのトラブルシューティング

### 4.1 プロンプトが表示されない場合

**原因**: Safari（iOS）では`beforeinstallprompt`イベントが発火しないため、カスタムプロンプトは表示されません。

**対処法**:
- ✅ **正常な動作**: Safari（iOS）では、手動で「ホーム画面に追加」機能を使用する必要があります
- ✅ **カスタムプロンプトは不要**: Safari（iOS）では、標準の「ホーム画面に追加」機能を使用します

---

### 4.2 インストール後に404エラーが発生する場合

**確認事項**:

1. **manifest.jsonの`start_url`が正しく設定されているか**:
   - MacのSafariの開発者ツール → Storage → Manifest
   - `start_url: "/"`が正しく設定されているか確認

2. **Service Workerの`navigateFallback`が正しく設定されているか**:
   - Service Workerが登録されているか確認
   - `navigateFallback: '/index.html'`が設定されているか確認

3. **Render.comのリライト設定が正しく設定されているか**:
   - `render.yaml`の`routes`セクションで`/*` → `/index.html`が設定されているか確認

**対処法**:
- ブラウザの開発者ツールで、リクエストのステータスコードを確認
- Service Workerの登録状態を確認
- manifest.jsonの内容を確認

---

### 4.3 Service Workerが登録されない場合

**確認事項**:

1. **ビルドが正しく完了しているか**:
   - `frontend/dist/sw.js`が存在するか確認
   - `frontend/dist/manifest.webmanifest`が存在するか確認

2. **HTTPSでアクセスしているか**:
   - Safari（iOS）では、Service WorkerはHTTPSでのみ動作します
   - `https://yadopera-frontend-staging.onrender.com`でアクセスしているか確認

3. **デプロイが正しく完了しているか**:
   - Render.comのデプロイログを確認
   - デプロイが正常に完了しているか確認

**対処法**:
- ビルドを再実行
- デプロイを再実行
- ブラウザのキャッシュをクリア

---

## 5. Safari（iOS）でのテスト手順（まとめ）

### 5.1 推奨テスト手順

**手順**:

1. **iPadのSafariでステージング環境のURLにアクセス**
   - `https://yadopera-frontend-staging.onrender.com/f/test-facility?location=entrance`

2. **Service Workerが登録されるまで待つ**（数秒）

3. **MacのSafariの開発者ツールで確認**:
   - Storage → Service Workers → Service Workerが登録されているか確認
   - Storage → Manifest → manifest.jsonが正しく読み込まれているか確認
   - Storage → Local Storage → `pwa_install_dismissed`が存在する場合は削除

4. **手動で「ホーム画面に追加」を実行**:
   - 共有ボタン（□↑アイコン）をタップ
   - 「ホーム画面に追加」を選択
   - アイコン名を確認して「追加」をタップ

5. **ホーム画面にアイコンが追加されることを確認**

6. **アイコンをタップしてアプリを起動**:
   - ✅ アプリが起動する
   - ✅ 404エラーが発生しない
   - ✅ アプリが正常に起動する

7. **QRコードで読み取ったURLへのアクセスの確認**:
   - ✅ QRコードを読み取る（例: `/f/test-facility?location=entrance`）
   - ✅ 施設独自の画面が正常に表示される

---

### 5.2 テスト項目チェックリスト

**インストール前**:
- [ ] Service Workerが登録されている
- [ ] manifest.jsonが正しく読み込まれている
- [ ] `start_url`、`scope`、`display`が正しく設定されている

**インストール時**:
- [ ] 手動で「ホーム画面に追加」を実行できる
- [ ] ホーム画面にアイコンが追加される

**インストール後**:
- [ ] ホーム画面のアイコンをタップすると、アプリが起動する
- [ ] 404エラーが発生しない
- [ ] アプリが正常に起動する
- [ ] QRコードで読み取ったURLに正常にアクセスできる

---

## 6. Safari（iOS）とChromeの違い

### 6.1 インストールプロンプトの違い

| 項目 | Chrome | Safari（iOS） |
|------|--------|--------------|
| **`beforeinstallprompt`イベント** | ✅ 発火する | ❌ 発火しない |
| **カスタムプロンプト** | ✅ 表示される | ❌ 表示されない |
| **手動インストール** | ✅ 可能 | ✅ 可能（共有ボタン → 「ホーム画面に追加」） |

### 6.2 テスト方法の違い

**Chrome**:
- カスタムプロンプトが表示される
- 「インストール」ボタンをクリックしてインストール

**Safari（iOS）**:
- カスタムプロンプトは表示されない
- 手動で「ホーム画面に追加」機能を使用してインストール

---

## 7. まとめ

### 7.1 Safari（iOS）でのテストの重要なポイント

1. **`beforeinstallprompt`イベントが発火しない**:
   - カスタムプロンプトは表示されない
   - これは正常な動作です

2. **手動で「ホーム画面に追加」機能を使用**:
   - 共有ボタン（□↑アイコン）→「ホーム画面に追加」
   - これがSafari（iOS）での標準的なPWAインストール方法です

3. **インストール後の動作確認が重要**:
   - ホーム画面のアイコンをタップして、404エラーが発生しないことを確認
   - QRコードで読み取ったURLに正常にアクセスできることを確認

### 7.2 推奨テスト手順

1. **iPadのSafariでステージング環境のURLにアクセス**
2. **MacのSafariの開発者ツールで確認**（Service Worker、manifest.json）
3. **手動で「ホーム画面に追加」を実行**
4. **アイコンをタップしてアプリを起動**
5. **404エラーが発生しないことを確認**
6. **QRコードで読み取ったURLへのアクセスを確認**

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025年12月22日  
**Status**: 📋 **Safari（iOS）テスト方法説明完了**

**重要**: Safari（iOS）では`beforeinstallprompt`イベントが発火しないため、カスタムプロンプトは表示されません。手動で「ホーム画面に追加」機能を使用してPWAをインストールし、インストール後の動作（404エラーが発生しない）を確認してください。


