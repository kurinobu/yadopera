# Phase 1・Phase 2: PWAインストールプロンプトのボタンの動作問題 テスト方法

**作成日時**: 2025年12月22日  
**実施者**: AI Assistant  
**目的**: PWAインストールプロンプトのテスト方法を説明  
**状態**: 📋 **テスト方法説明完了**

---

## 1. PWAインストールプロンプトが表示されない理由

### 1.1 プロンプトが表示される条件

PWAインストールプロンプトが表示されるには、以下の**すべての条件**を満たす必要があります：

1. ✅ `isInstallable.value === true`（`beforeinstallprompt`イベントが発火している）
2. ✅ `isInstalled.value === false`（PWAがインストールされていない）
3. ✅ `isDismissed.value === false`（プロンプトが「後で」で非表示にされていない）

### 1.2 プロンプトが表示されない理由

**理由1: プロンプトを「後で」で非表示にした**
- `localStorage`に`pwa_install_dismissed: 'true'`が保存されている
- この場合、プロンプトは表示されない

**理由2: 既にPWAがインストールされている**
- ホーム画面にアイコンが追加されている
- `isInstalled.value === true`になっている
- この場合、プロンプトは表示されない

**理由3: `beforeinstallprompt`イベントが発火していない**
- Service Workerが登録されていない
- manifest.jsonが正しく読み込まれていない
- ブラウザがPWAインストール可能と判断していない

**理由4: ブラウザのキャッシュ**
- 古いService Workerが登録されている
- 古いmanifest.jsonがキャッシュされている

---

## 2. テスト方法（推奨順）

### 方法1: localStorageを削除してテスト（最も簡単）

**手順**:

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **Applicationタブを開く**
3. **左側メニューから「Local Storage」を選択**
4. **現在のドメイン（例: `https://yadopera-frontend-staging.onrender.com`）を選択**
5. **`pwa_install_dismissed`キーを探す**
6. **`pwa_install_dismissed`キーを右クリック → 「Delete」を選択**
7. **ページをリロード**（F5キー）

**期待される結果**:
- プロンプトが表示される（`beforeinstallprompt`イベントが発火している場合）

**注意**: この方法では、`beforeinstallprompt`イベントが発火していない場合は、プロンプトは表示されません。

---

### 方法2: シークレットモード（プライベートモード）でテスト（推奨）

**手順**:

1. **シークレットモード（プライベートモード）でブラウザを開く**
   - Chrome: `Ctrl+Shift+N`（Windows/Linux）または `Cmd+Shift+N`（Mac）
   - Firefox: `Ctrl+Shift+P`（Windows/Linux）または `Cmd+Shift+P`（Mac）
   - Safari: `Cmd+Shift+N`（Mac）

2. **ステージング環境のURLにアクセス**
   - `https://yadopera-frontend-staging.onrender.com/f/test-facility?location=entrance`

3. **Service Workerが登録されるまで待つ**（数秒）

4. **プロンプトが表示されるか確認**

**期待される結果**:
- プロンプトが表示される（`beforeinstallprompt`イベントが発火している場合）
- localStorageに`pwa_install_dismissed`が保存されていないため、プロンプトが表示される

**メリット**:
- ✅ 既存のキャッシュやlocalStorageの影響を受けない
- ✅ クリーンな状態でテストできる
- ✅ 最も確実なテスト方法

---

### 方法3: Service WorkerとlocalStorageを削除してテスト

**手順**:

1. **ブラウザの開発者ツールを開く**（F12キー）

2. **Applicationタブを開く**

3. **Service Workerをアンインストール**:
   - 左側メニューから「Service Workers」を選択
   - 登録されているService Workerを探す
   - 「Unregister」ボタンをクリック

4. **localStorageを削除**:
   - 左側メニューから「Local Storage」を選択
   - 現在のドメインを選択
   - `pwa_install_dismissed`キーを削除

5. **キャッシュをクリア**:
   - 左側メニューから「Cache Storage」を選択
   - すべてのキャッシュを右クリック → 「Delete」を選択

6. **ページをリロード**（F5キー）

**期待される結果**:
- プロンプトが表示される（`beforeinstallprompt`イベントが発火している場合）

---

### 方法4: 既にPWAがインストールされている場合のテスト

**手順**:

1. **PWAをアンインストール**:
   - **Android（Chrome）**:
     - ホーム画面のアイコンを長押し
     - 「削除」または「アンインストール」を選択
   - **iOS（Safari）**:
     - ホーム画面のアイコンを長押し
     - 「削除」を選択
   - **デスクトップ（Chrome）**:
     - アドレスバーの右側のインストールアイコンをクリック
     - 「アンインストール」を選択

2. **ブラウザのキャッシュをクリア**:
   - 開発者ツールを開く（F12キー）
   - Applicationタブ → Service Workers → 「Unregister」
   - Applicationタブ → Local Storage → `pwa_install_dismissed`を削除
   - Applicationタブ → Cache Storage → すべてのキャッシュを削除

3. **ページをリロード**（F5キー）

**期待される結果**:
- プロンプトが表示される（`beforeinstallprompt`イベントが発火している場合）

---

## 3. ブラウザ別の詳細手順

### 3.1 Chrome（デスクトップ）

**手順**:

1. **開発者ツールを開く**: `F12`キーまたは`Ctrl+Shift+I`（Windows/Linux） / `Cmd+Option+I`（Mac）

2. **Applicationタブを開く**

3. **Service Workerを確認**:
   - 左側メニューから「Service Workers」を選択
   - 登録されているService Workerの状態を確認
   - 状態が「activated」または「waiting」の場合、Service Workerは正常に登録されている

4. **localStorageを確認**:
   - 左側メニューから「Local Storage」を選択
   - 現在のドメインを選択
   - `pwa_install_dismissed`キーが存在する場合、削除する

5. **ページをリロード**: `F5`キー

**期待される結果**:
- プロンプトが表示される（`beforeinstallprompt`イベントが発火している場合）

---

### 3.2 Chrome（Android）

**手順**:

1. **開発者ツールを開く**:
   - Chromeで`chrome://inspect`にアクセス（PCのChrome）
   - 「Remote devices」を選択
   - Androidデバイスを接続
   - デバイスを選択して「inspect」をクリック

2. **Applicationタブを開く**

3. **Service Workerを確認**:
   - 左側メニューから「Service Workers」を選択
   - 登録されているService Workerの状態を確認

4. **localStorageを確認**:
   - 左側メニューから「Local Storage」を選択
   - 現在のドメインを選択
   - `pwa_install_dismissed`キーが存在する場合、削除する

5. **ページをリロード**: デバイス上でリロード

**期待される結果**:
- プロンプトが表示される（`beforeinstallprompt`イベントが発火している場合）

---

### 3.3 Safari（iOS）

**手順**:

1. **Safariの設定を変更**:
   - iOSデバイスの「設定」→「Safari」→「詳細」
   - 「Webインスペクタ」を有効にする

2. **MacのSafariで開発者ツールを開く**:
   - MacのSafariで「開発」メニューを表示
   - iOSデバイス名を選択
   - ページを選択

3. **Storageタブを開く**:
   - 左側メニューから「Storage」を選択
   - 「Local Storage」を選択
   - `pwa_install_dismissed`キーが存在する場合、削除する

4. **ページをリロード**: デバイス上でリロード

**期待される結果**:
- プロンプトが表示される（`beforeinstallprompt`イベントが発火している場合）

**注意**: iOSのSafariでは、`beforeinstallprompt`イベントが発火しない場合があります。この場合、プロンプトは表示されません。

---

## 4. プロンプトが表示されない場合の確認事項

### 4.1 `beforeinstallprompt`イベントが発火しているか確認

**確認方法**:

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **Consoleタブを開く**
3. **以下のコードを実行**:
   ```javascript
   window.addEventListener('beforeinstallprompt', (e) => {
     console.log('beforeinstallprompt event fired!', e);
   });
   ```
4. **ページをリロード**（F5キー）
5. **Consoleに「beforeinstallprompt event fired!」が表示されるか確認**

**期待される結果**:
- Consoleに「beforeinstallprompt event fired!」が表示される
- 表示されない場合、`beforeinstallprompt`イベントが発火していない

**考えられる原因**:
- Service Workerが登録されていない
- manifest.jsonが正しく読み込まれていない
- ブラウザがPWAインストール可能と判断していない

---

### 4.2 Service Workerが登録されているか確認

**確認方法**:

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **Applicationタブを開く**
3. **左側メニューから「Service Workers」を選択**
4. **登録されているService Workerの状態を確認**

**期待される結果**:
- Service Workerが登録されている
- 状態が「activated」または「waiting」

**問題がある場合**:
- Service Workerが登録されていない → ビルドが正しく完了していない可能性
- 状態が「redundant」または「error」 → Service Workerの登録に失敗している

---

### 4.3 manifest.jsonが正しく読み込まれているか確認

**確認方法**:

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **Applicationタブを開く**
3. **左側メニューから「Manifest」を選択**
4. **manifest.jsonの内容を確認**

**期待される結果**:
- manifest.jsonが読み込まれている
- `start_url`、`scope`、`display`が正しく設定されている
- エラーメッセージが表示されていない

**問題がある場合**:
- manifest.jsonが読み込まれていない → ビルドが正しく完了していない可能性
- エラーメッセージが表示されている → manifest.jsonの設定に問題がある

---

## 5. テスト手順のまとめ（推奨）

### 5.1 最も確実なテスト方法

**手順**:

1. **シークレットモード（プライベートモード）でブラウザを開く**
2. **ステージング環境のURLにアクセス**
   - `https://yadopera-frontend-staging.onrender.com/f/test-facility?location=entrance`
3. **Service Workerが登録されるまで待つ**（数秒）
4. **プロンプトが表示されるか確認**
5. **「インストール」ボタンをクリック**
6. **ホーム画面にアイコンが追加されることを確認**
7. **アイコンをタップしてアプリを起動**
8. **404エラーが発生しないことを確認**

---

### 5.2 既にアクセスしている場合のテスト方法

**手順**:

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **Applicationタブを開く**
3. **Local Storageから`pwa_install_dismissed`を削除**
4. **Service WorkersからService Workerをアンインストール**（必要に応じて）
5. **ページをリロード**（F5キー）
6. **プロンプトが表示されるか確認**

---

## 6. テスト項目チェックリスト

### 6.1 プロンプトの表示確認

- [ ] プロンプトが表示される
- [ ] 「インストール」ボタンが表示される
- [ ] 「後で」ボタンが表示される
- [ ] 「閉じる」ボタン（×アイコン）が表示される

### 6.2 インストール機能の確認

- [ ] 「インストール」ボタンをクリックすると、PWAインストールダイアログが表示される
- [ ] インストールを承認すると、ホーム画面にアイコンが追加される
- [ ] インストールを拒否すると、プロンプトが非表示になる

### 6.3 インストール後の動作確認

- [ ] ホーム画面のアイコンをタップすると、アプリが起動する
- [ ] 404エラーが発生しない
- [ ] アプリが正常に起動する

### 6.4 QRコードで読み取ったURLへのアクセスの確認

- [ ] QRコードで読み取ったURL（例: `/f/test-facility?location=entrance`）に正常にアクセスできる
- [ ] 施設独自の画面が正常に表示される

---

## 7. トラブルシューティング

### 7.1 プロンプトが表示されない場合

**確認事項**:
1. Service Workerが登録されているか
2. manifest.jsonが正しく読み込まれているか
3. `beforeinstallprompt`イベントが発火しているか
4. localStorageに`pwa_install_dismissed`が保存されていないか
5. 既にPWAがインストールされていないか

**対処法**:
- シークレットモードでテストする（推奨）
- Service WorkerとlocalStorageを削除してテストする
- ブラウザのキャッシュをクリアしてテストする

---

### 7.2 インストール後に404エラーが発生する場合

**確認事項**:
1. manifest.jsonの`start_url`が正しく設定されているか
2. Service Workerの`navigateFallback`が正しく設定されているか
3. Render.comのリライト設定が正しく設定されているか

**対処法**:
- ブラウザの開発者ツールで、リクエストのステータスコードを確認
- Service Workerの登録状態を確認
- manifest.jsonの内容を確認

---

## 8. まとめ

### 8.1 推奨テスト方法

**最も確実な方法**: **シークレットモード（プライベートモード）でテスト**

**理由**:
- 既存のキャッシュやlocalStorageの影響を受けない
- クリーンな状態でテストできる
- 最も確実にプロンプトが表示される

### 8.2 既にアクセスしている場合の対処法

1. **localStorageから`pwa_install_dismissed`を削除**
2. **Service Workerをアンインストール**（必要に応じて）
3. **ページをリロード**

### 8.3 テスト項目

- ✅ プロンプトの表示確認
- ✅ インストール機能の確認
- ✅ インストール後の動作確認（404エラーが発生しない）
- ✅ QRコードで読み取ったURLへのアクセスの確認

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025年12月22日  
**Status**: 📋 **テスト方法説明完了**

**重要**: シークレットモード（プライベートモード）でのテストが最も確実です。既にアクセスしている場合は、localStorageから`pwa_install_dismissed`を削除してからテストしてください。

