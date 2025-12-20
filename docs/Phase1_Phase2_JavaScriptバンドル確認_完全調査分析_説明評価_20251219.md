# Phase 1・Phase 2: JavaScriptバンドル確認 完全調査分析と説明評価

**作成日時**: 2025年12月19日 23時30分00秒
**実施者**: AI Assistant
**目的**: デプロイ後のJavaScriptバンドル確認方法の完全な調査分析と説明評価

---

## 1. 問題の概要

### 1.1 ユーザー様からの報告

**問題**:
- デプロイ後のJavaScriptバンドルをcurlコマンドで確認しようとした
- `Welcome-*.js`というファイル名が見つからない
- `Welcome-`で始まるJavaScriptファイルも見つからない
- 404エラーが発生している

### 1.2 調査結果

**HTMLの内容確認**:
```html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>やどぺら</title>
    <script type="module" crossorigin src="/assets/index-iHuDpMpx.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-BWPcFWvR.css">
  </head>
  <body>
    <div id="app"></div>
  </body>
</html>
```

**重要な発見**:
1. ✅ HTMLには`/assets/index-iHuDpMpx.js`というメインのJavaScriptファイルが含まれている
2. ✅ メインのJavaScriptバンドル（`index-iHuDpMpx.js`）には、`__vite__mapDeps`という関数があり、その中に`Welcome-K6zHy5qi.js`というファイル名が含まれている
3. ✅ これは、Viteがコード分割を行い、`Welcome.vue`が別のチャンクファイル（`Welcome-K6zHy5qi.js`）として生成されていることを示している

---

## 2. 根本原因の分析

### 2.1 Viteのコード分割の理解

**Viteのコード分割**:
- Viteは、デフォルトでコード分割（code splitting）を実施する
- 各ルートやコンポーネントが別々のチャンクファイルとして生成される
- メインの`index-*.js`ファイルには、アプリケーションのエントリーポイントとルーティング設定が含まれる
- 各コンポーネント（`Welcome.vue`など）は、個別のチャンクファイル（`Welcome-*.js`）として生成される

**今回のケース**:
- メインのJavaScriptバンドル（`index-iHuDpMpx.js`）には、`__vite__mapDeps`という関数があり、その中に`Welcome-K6zHy5qi.js`というファイル名が含まれている
- したがって、`Welcome.vue`のコードは`Welcome-K6zHy5qi.js`という個別のチャンクファイルに含まれている

### 2.2 正しい確認方法

**誤った方法**:
- HTMLから直接`Welcome-*.js`を探す（HTMLには含まれていない）
- `/assets/Welcome-*.js`に直接アクセスする（ファイル名のハッシュが不明）

**正しい方法**:
1. HTMLからメインのJavaScriptファイル名（`index-*.js`）を取得
2. メインのJavaScriptバンドルから、`__vite__mapDeps`関数内の`Welcome-*.js`のファイル名を抽出
3. そのファイル（`Welcome-K6zHy5qi.js`）の内容を確認
4. その中に`Welcome.vue`のコードと新しいデバッグログが含まれているか確認

---

## 3. 正しい確認手順

### 3.1 ステップ1: HTMLからメインのJavaScriptファイル名を取得

```bash
# HTMLを取得して、JavaScriptファイル名を抽出
curl -s "https://yadopera-frontend-staging.onrender.com/" | grep -o 'src="[^"]*\.js"'
```

**結果**: `/assets/index-iHuDpMpx.js`

### 3.2 ステップ2: メインのJavaScriptバンドルからWelcome.vueのチャンクファイル名を抽出

```bash
# メインのJavaScriptバンドルから、Welcome-*.jsのファイル名を抽出
curl -s "https://yadopera-frontend-staging.onrender.com/assets/index-iHuDpMpx.js" | grep -o 'Welcome-[^"]*\.js' | head -1
```

**結果**: `Welcome-K6zHy5qi.js`

### 3.3 ステップ3: Welcome.vueのチャンクファイルの内容を確認

```bash
# 1. 完全なエラーオブジェクト構造のログを検索
curl -s "https://yadopera-frontend-staging.onrender.com/assets/Welcome-K6zHy5qi.js" | grep -o "完全なエラーオブジェクト構造" | head -3

# 2. 検出されたerrorCodeのログを検索
curl -s "https://yadopera-frontend-staging.onrender.com/assets/Welcome-K6zHy5qi.js" | grep -o "検出されたerrorCode" | head -3

# 3. NETWORK_ERROR検出のログを検索
curl -s "https://yadopera-frontend-staging.onrender.com/assets/Welcome-K6zHy5qi.js" | grep -o "NETWORK_ERROR検出" | head -3

# 4. Facility fetch errorのログを検索
curl -s "https://yadopera-frontend-staging.onrender.com/assets/Welcome-K6zHy5qi.js" | grep -o "Facility fetch error" | head -3
```

---

## 4. 説明と評価

### 4.1 問題の説明

**なぜ`Welcome-*.js`が見つからないのか**:
- HTMLには、メインのJavaScriptファイル（`index-*.js`）のみが含まれている
- `Welcome-*.js`は、コード分割により個別のチャンクファイルとして生成されているが、HTMLには直接含まれていない
- メインのJavaScriptバンドル内の`__vite__mapDeps`関数に、動的に読み込まれるチャンクファイルのリストが含まれている

**なぜ404エラーが発生するのか**:
- `/assets/Welcome-*.js`というファイル名のハッシュ部分（`*`）が不明なため、直接アクセスできない
- 正しいファイル名（`Welcome-K6zHy5qi.js`）をメインのJavaScriptバンドルから抽出する必要がある

### 4.2 正しい確認方法の評価

**推奨される確認方法**:
1. ✅ HTMLからメインのJavaScriptファイル名（`index-*.js`）を取得
2. ✅ メインのJavaScriptバンドルから、`Welcome-*.js`のファイル名を抽出
3. ✅ そのファイル（`Welcome-K6zHy5qi.js`）の内容を確認
4. ✅ 新しいデバッグログが含まれているか確認

**確認すべきファイル**:
- `/assets/index-iHuDpMpx.js`（メインのJavaScriptバンドル）
- `/assets/Welcome-K6zHy5qi.js`（Welcome.vueのチャンクファイル）

**確認すべき文字列**:
- `完全なエラーオブジェクト構造`
- `検出されたerrorCode`
- `NETWORK_ERROR検出`
- `エラーオブジェクト構造確認終了`

---

## 5. 修正が必要な手順書

**修正が必要な箇所**:
- `/Users/kurinobu/projects/yadopera/docs/Phase1_Phase2_ビルドキャッシュクリア_再デプロイ_バンドル確認手順_20251219.md`の「ステップ2: JavaScriptバンドルのURLを特定」セクション

**修正内容**:
1. HTMLから直接`Welcome-*.js`を探すのではなく、メインのJavaScriptバンドルから抽出する方法に変更
2. メインのJavaScriptバンドル（`index-*.js`）から、`Welcome-*.js`のファイル名を抽出する手順を追加
3. 抽出したファイル名を使用して、`Welcome.vue`のチャンクファイルの内容を確認する手順を追加

---

## 6. 次のステップ

1. **メインのJavaScriptバンドルからWelcome.vueのチャンクファイル名を抽出**: `Welcome-K6zHy5qi.js`
2. **Welcome.vueのチャンクファイルの内容を確認**: 上記の確認コマンドを実行
3. **新しいデバッグログが含まれているか確認**: 結果を評価
4. **必要に応じて手順書を修正**: 正しい確認方法を手順書に反映

---

## 7. まとめ

**問題の根本原因**:
- `Welcome-*.js`は、コード分割により個別のチャンクファイルとして生成されている
- HTMLには直接含まれていないため、メインのJavaScriptバンドルから抽出する必要がある

**正しい確認方法**:
1. HTMLからメインのJavaScriptファイル名（`index-*.js`）を取得
2. メインのJavaScriptバンドルから、`Welcome-*.js`のファイル名を抽出
3. そのファイルの内容を確認
4. 新しいデバッグログが含まれているか確認

**次のアクション**:
- `Welcome-K6zHy5qi.js`の内容を確認
- 新しいデバッグログが含まれているか検証
