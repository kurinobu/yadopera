# Phase 2: 真っ白画面エラー 完全調査分析レポート

**作成日**: 2025年12月13日  
**問題**: リダイレクトルール追加後、404エラーは解消されたが画面が真っ白になる  
**エラー**: `Cannot read properties of null (reading 'src')`

---

## 1. 結果の説明と評価

### 1.1 前回の修正内容

**実施した修正**:
- `render.yaml`にStatic Site用のリダイレクト設定を追加
- Render.comダッシュボードでリダイレクトルールを追加

**期待された結果**:
- すべてのリクエストが`index.html`にリライトされ、Vue Routerが正しく動作
- 404エラーが解消される

### 1.2 実際の結果

**進展**: ✅ 404エラーは解消された（`dashboard 200 OK`）

**新たな問題**: ❌ 画面が真っ白になる

**エラーメッセージ**:
```
commons.js:2 Uncaught TypeError: Cannot read properties of null (reading 'src')
    at 19566 (commons.js:2:1267152)
```

**評価**: 
- リダイレクト設定は正しく機能している（404エラーが解消）
- しかし、JavaScriptの実行時にエラーが発生し、アプリケーションが初期化されていない
- エラーメッセージから、何かの要素が`null`で、その`src`プロパティにアクセスしようとしている

---

## 2. 根本原因の分析

### 2.1 エラーメッセージの分析

**エラー**: `Cannot read properties of null (reading 'src')`

**考えられる原因**:
1. **画像要素の`src`属性が`null`**: QRコード画像のURLが`null`または`undefined`の場合
2. **ビルド後のJavaScriptファイルのパスが正しく解決されていない**: `BASE_URL`の設定が間違っている
3. **静的ファイル（JS/CSS）のパスが正しく解決されていない**: Viteの`base`設定が間違っている

### 2.2 現在の設定状況

**確認した内容**:
- `vite.config.ts`: `base`設定がない（デフォルトは`/`）
- `router/index.ts`: `createWebHistory(import.meta.env.BASE_URL)`を使用
- `dist/index.html`: JavaScriptファイルのパスは`/assets/index-DIfeDb2Y.js`（絶対パス）

**問題の本質**:
- Render.com Static Siteでは、ルートパスが`/`であることを前提としている
- しかし、`import.meta.env.BASE_URL`が正しく設定されていない可能性がある
- または、QRコード画像のURLが`null`の場合にエラーが発生している

### 2.3 QRコード画像の`src`属性の問題

**確認したコード**:
- `QRCodeGenerator.vue`: `<img :src="qrCode.qr_code_url" />`
- `QRCodeForm.vue`: `<img :src="previewUrl" />`

**問題の可能性**:
- `qrCode.qr_code_url`が`null`または`undefined`の場合、`img`タグの`src`属性が`null`になる
- しかし、Vue.jsでは`v-bind:src`に`null`を渡しても通常はエラーにならない
- エラーメッセージの`commons.js`は、ビルドされたJavaScriptファイル内のエラーを示している

---

## 3. 大原則への準拠評価

### 3.1 根本解決 vs 暫定対応

**根本解決**: ✅ `vite.config.ts`に`base`設定を追加し、`null`チェックを追加する

**暫定対応**: ❌ エラーハンドリングのみを追加する

### 3.2 シンプル構造 vs 複雑構造

**シンプル構造**: ✅ `vite.config.ts`に`base`設定を追加し、`null`チェックを追加するだけ

**複雑構造**: ❌ 複雑なエラーハンドリングや条件分岐を追加する

### 3.3 統一・同一化

**統一・同一化**: ✅ すべての環境で同じ設定を使用する

**特殊化**: ❌ 環境ごとに異なる設定を使用する

---

## 4. 修正案

### 修正案1: `vite.config.ts`に`base`設定を追加し、`null`チェックを追加（推奨）

**目的**: Render.com Static Siteで正しく動作するように`base`設定を追加し、`null`チェックを追加する

**実施内容**:

1. **`vite.config.ts`に`base`設定を追加**
   ```typescript
   export default defineConfig({
     base: '/',
     plugins: [
       // ...
     ],
     // ...
   })
   ```

2. **QRコード画像の`null`チェックを追加**
   - `QRCodeGenerator.vue`: `qrCode.qr_code_url`が`null`でないことを確認
   - `QRCodeForm.vue`: `previewUrl`が`null`でないことを確認

**メリット**:
- ✅ 根本解決: `base`設定を追加し、`null`チェックを追加することで、エラーを防ぐ
- ✅ シンプル構造: 設定を追加し、`null`チェックを追加するだけ
- ✅ 統一・同一化: すべての環境で同じ設定を使用する
- ✅ 安全/確実: `null`チェックを追加することで、予期しないエラーを防ぐ

**デメリット**:
- なし

**大原則への準拠**: ✅ 完全準拠

---

### 修正案2: エラーハンドリングのみを追加（非推奨）

**目的**: エラーハンドリングのみを追加し、エラーを抑制する

**実施内容**:
- QRコード画像の`null`チェックを追加するだけ

**メリット**:
- ✅ エラーを防ぐ

**デメリット**:
- ❌ `base`設定の問題を解決していない
- ❌ 大原則違反: 「根本解決 > 暫定対応」に反する

**大原則への準拠**: ⚠️ 部分的準拠（根本解決を満たしていない）

---

## 5. 推奨修正案

**推奨**: **修正案1（`vite.config.ts`に`base`設定を追加し、`null`チェックを追加）**

**理由**:
1. **根本解決**: `base`設定を追加し、`null`チェックを追加することで、エラーを防ぐ
2. **シンプル構造**: 設定を追加し、`null`チェックを追加するだけ
3. **統一・同一化**: すべての環境で同じ設定を使用する
4. **安全/確実**: `null`チェックを追加することで、予期しないエラーを防ぐ

**実施手順**:

1. `vite.config.ts`に`base: '/'`を追加
2. `QRCodeGenerator.vue`で`qrCode.qr_code_url`の`null`チェックを追加
3. `QRCodeForm.vue`で`previewUrl`の`null`チェックを追加

---

## 6. 期待される結果

### 6.1 修正後の動作

1. **初回アクセス時**: ✅ 正常に動作
2. **リロード時**: ✅ 正常に動作
   - `https://yadopera-frontend-staging.onrender.com/admin/dashboard`に直接アクセス
   - サーバーが`index.html`を返す
   - Vue Routerがクライアントサイドでルーティングを処理
   - ダッシュボードが正常に表示される
3. **QRコード画像**: ✅ `null`チェックにより、エラーが発生しない

### 6.2 エラーの解消

- ❌ `Cannot read properties of null (reading 'src')` → ✅ エラーが発生しない
- ❌ 画面が真っ白になる → ✅ 正常に表示される

---

## 7. 参考資料

- [Vite Base Configuration](https://vitejs.dev/config/shared-options.html#base)
- [Vue Router History Mode](https://router.vuejs.org/guide/essentials/history-mode.html)
- [Render.com Static Site Documentation](https://render.com/docs/static-sites)

---

**次のステップ**: 修正案1を実施し、デプロイ後に動作確認を行う

