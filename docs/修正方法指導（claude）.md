この問題を詳細に分析しました。スマートフォンで画面が真っ白になり、タブレットで「test-facility.txt」がダウンロードされる現象から、\*\*Render.comが\`index.html\`を正しく配信していない\*\*ことが根本原因と判断されます。調査結果に基づき、根本原因と修正方法を提示します。

\#\# 🔍 根本原因の特定

\#\#\# 判明した問題点

1\. \*\*Render.comは\`\_headers\`ファイルをサポートしていない\*\*  
   \- Render.comの公式ドキュメントによると、静的サイトにはカスタムHTTPヘッダーをダッシュボードから設定する必要があります  
   \- \`\_headers\`ファイルは無視される（NetlifyやCloudflareの形式）

2\. \*\*Rewrite Ruleが正しく設定されていない可能性\*\*  
   \- Render.comではリダイレクト/リライトルールをダッシュボードから設定する必要があります  
   \- \`\_redirects\`ファイルの\`/\* /index.html 200\`は機能するはずですが、一部のケースで問題が発生する可能性があります

3\. \*\*\`test-facility.txt\`ダウンロード問題の原因\*\*  
   \- URLパス\`/f/test-facility\`が実際のファイルとして解釈されている  
   \- SPAのルーティングが機能していない  
   \- \`index.html\`へのフォールバックが失敗している

\#\# 🛠️ 修正方法（優先順位順）

\#\#\# 修正案A: Render.comダッシュボードでRewrite Ruleを正しく設定 ⭐ 最優先

\*\*手順\*\*:

1\. \*\*Render.comダッシュボードにアクセス\*\*  
   \- \`yadopera-frontend-staging\`を選択  
   \- 「Redirects/Rewrites」タブを開く

2\. \*\*既存のルールをすべて削除\*\*

3\. \*\*新しいRewrite Ruleを追加\*\*  
   \- \*\*Source\*\*: \`/\*\`  
   \- \*\*Destination\*\*: \`/index.html\`  
   \- \*\*Action\*\*: \`Rewrite\` (Redirectではない)  
   \- \*\*Status Code\*\*: 200

\*\*重要\*\*: SPAでクライアントサイドルーティングを使用する場合、すべてのルーティングリクエストをindex.htmlにリライトする必要があります

\*\*検証方法\*\*:  
\`\`\`bash  
\# 再デプロイ後、以下のURLで確認  
\# スマートフォン/タブレットでアクセス  
https://yadopera-frontend-staging.onrender.com/f/test-facility?location=entrance  
\`\`\`

\---

\#\#\# 修正案B: \_redirectsファイルの形式を確認・修正

\*\*現在の\`\_redirects\`\*\*:  
\`\`\`  
/\*    /index.html   200  
\`\`\`

\*\*推奨される形式\*\*（Render.com用）:  
\`\`\`  
/\*  /index.html  200  
\`\`\`

\*\*修正箇所\*\*: \`frontend/public/\_redirects\`

\*\*理由\*\*:  
\- タブの数やスペースの違いでパースエラーが発生する可能性  
\- Render.comの仕様に完全に準拠させる

\---

\#\#\# 修正案C: Content-Typeヘッダーをダッシュボードから設定（\_headersファイルの代替）

\*\*手順\*\*:

1\. \*\*Render.comダッシュボードにアクセス\*\*  
   \- \`yadopera-frontend-staging\`を選択  
   \- 「Headers」タブを開く

2\. \*\*既存のヘッダーをすべて削除\*\*

3\. \*\*新しいヘッダーを追加\*\*（重要度順）:

\*\*ヘッダー1: HTMLファイル用\*\*  
\- \*\*Path\*\*: \`/\`  
\- \*\*Header Name\*\*: \`Content-Type\`  
\- \*\*Header Value\*\*: \`text/html; charset=utf-8\`

\*\*ヘッダー2: JavaScriptファイル用\*\*  
\- \*\*Path\*\*: \`/assets/\*.js\`  
\- \*\*Header Name\*\*: \`Content-Type\`  
\- \*\*Header Value\*\*: \`application/javascript; charset=utf-8\`

\*\*ヘッダー3: CSSファイル用\*\*  
\- \*\*Path\*\*: \`/assets/\*.css\`  
\- \*\*Header Name\*\*: \`Content-Type\`  
\- \*\*Header Value\*\*: \`text/css; charset=utf-8\`

\*\*重要\*\*: \`\_headers\`ファイルは削除する（Render.comでは機能しないため）

\---

\#\#\# 修正案D: index.htmlにフォールバック用の基本スクリプトを追加

\*\*問題\*\*: JavaScriptファイルの読み込みに失敗した場合のフォールバック

\*\*修正箇所\*\*: \`frontend/index.html\`

\`\`\`html  
\<\!DOCTYPE html\>  
\<html lang="ja"\>  
  \<head\>  
    \<meta charset="UTF-8" /\>  
    \<link rel="icon" type="image/svg+xml" href="/vite.svg" /\>  
    \<meta name="viewport" content="width=device-width, initial-scale=1.0" /\>  
    \<meta name="description" content="小規模宿泊施設向けAI多言語自動案内システム" /\>  
    \<title\>やどぺら\</title\>  
    \<\!-- 基本スタイル: JavaScriptが読み込まれない場合の表示 \--\>  
    \<style\>  
      \#app:empty::after {  
        content: '読み込み中...';  
        display: flex;  
        justify-content: center;  
        align-items: center;  
        height: 100vh;  
        font-size: 1.5rem;  
        color: \#666;  
      }  
    \</style\>  
  \</head\>  
  \<body\>  
    \<div id="app"\>\</div\>  
    \<script type="module" src="/src/main.ts"\>\</script\>  
    \<\!-- エラーハンドリング: JavaScriptが読み込まれない場合 \--\>  
    \<script\>  
      window.addEventListener('error', function(e) {  
        if (e.filename && e.filename.includes('/src/main')) {  
          const app \= document.getElementById('app');  
          if (app && app.innerHTML \=== '') {  
            app.innerHTML \= '\<div style="padding: 2rem; text-align: center; font-family: sans-serif;"\>\<h1\>アプリケーションの読み込みに失敗しました\</h1\>\<p\>ページを再読み込みしてください。\</p\>\</div\>';  
          }  
        }  
      }, true);  
    \</script\>  
  \</body\>  
\</html\>  
\`\`\`

\---

\#\#\# 修正案E: Vite設定でベースパスとビルドオプションを明示的に設定

\*\*修正箇所\*\*: \`frontend/vite.config.ts\`

\`\`\`typescript  
import { defineConfig } from 'vite'  
import vue from '@vitejs/plugin-vue'  
import { VitePWA } from 'vite-plugin-pwa'  
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({  
  base: '/', // 明示的に設定  
  plugins: \[  
    vue(),  
    VitePWA({  
      registerType: 'autoUpdate',  
      workbox: {  
        globPatterns: \['\*\*/\*.{js,css,html,ico,png,svg}'\],  
        runtimeCaching: \[  
          {  
            urlPattern: /\\/api\\/v1\\/admin\\/.\*$/,  
            handler: 'NetworkOnly',  
            method: 'GET'  
          }  
        \]  
      },  
      manifest: {  
        name: 'やどぺら',  
        short\_name: 'やどぺら',  
        description: '小規模宿泊施設向けAI多言語自動案内システム',  
        theme\_color: '\#ffffff',  
        icons: \[  
          {  
            src: 'pwa-192x192.png',  
            sizes: '192x192',  
            type: 'image/png'  
          },  
          {  
            src: 'pwa-512x512.png',  
            sizes: '512x512',  
            type: 'image/png'  
          }  
        \]  
      }  
    })  
  \],  
  resolve: {  
    alias: {  
      '@': fileURLToPath(new URL('./src', import.meta.url))  
    }  
  },  
  build: {  
    // 静的リソースの配置を明確にする  
    assetsDir: 'assets',  
    // ソースマップを生成（デバッグ用）  
    sourcemap: true,  
    // チャンクサイズの警告を調整  
    chunkSizeWarningLimit: 1000  
  },  
  server: {  
    host: '0.0.0.0',  
    port: 5173,  
    watch: {  
      usePolling: true  
    }  
  }  
})  
\`\`\`

\---

\#\# 📋 実施手順（推奨順序）

\#\#\# ステップ1: Render.comダッシュボード設定（最優先）⭐

1\. \*\*Rewrite Ruleを設定\*\* (修正案A)  
2\. \*\*Content-Typeヘッダーを設定\*\* (修正案C)  
3\. \*\*手動で再デプロイ\*\*

\#\#\# ステップ2: コード修正

1\. \*\*\`\_redirects\`ファイルを修正\*\* (修正案B)  
2\. \*\*\`\_headers\`ファイルを削除\*\* (Render.comでは不要)  
3\. \*\*\`index.html\`を修正\*\* (修正案D)  
4\. \*\*\`vite.config.ts\`を修正\*\* (修正案E)

\#\#\# ステップ3: ビルド・デプロイ

\`\`\`bash  
\# ローカルDocker環境で確認  
cd frontend  
npm run build

\# distディレクトリの内容を確認  
ls \-la dist/

\# Gitにコミット・プッシュ  
git add .  
git commit \-m "fix: Render.com static site configuration for mobile devices"  
git push origin develop  
\`\`\`

\#\#\# ステップ4: 検証

1\. \*\*デプロイ完了を確認\*\*  
2\. \*\*スマートフォンでアクセス\*\*:  
   \`\`\`  
   https://yadopera-frontend-staging.onrender.com/f/test-facility?location=entrance  
   \`\`\`  
3\. \*\*タブレットでアクセス\*\*  
4\. \*\*デスクトップブラウザでも再確認\*\*

\---

\#\# 🔧 追加デバッグ方法

もし上記の修正で解決しない場合:

\#\#\# デバッグ案1: Render.comのログを確認

1\. Render.comダッシュボードで「Logs」タブを開く  
2\. デプロイログとランタイムログを確認  
3\. 404エラーや静的リソースの読み込みエラーを探す

\#\#\# デバッグ案2: 簡易テストページを作成

\*\*\`frontend/public/test.html\`\*\*を作成:

\`\`\`html  
\<\!DOCTYPE html\>  
\<html\>  
\<head\>  
    \<meta charset="UTF-8"\>  
    \<meta name="viewport" content="width=device-width, initial-scale=1.0"\>  
    \<title\>Test Page\</title\>  
\</head\>  
\<body\>  
    \<h1\>Test Page\</h1\>  
    \<p\>If you can see this, static files are being served correctly.\</p\>  
    \<script\>  
        document.body.innerHTML \+= '\<p\>JavaScript is working\!\</p\>';  
    \</script\>  
\</body\>  
\</html\>  
\`\`\`

アクセス: \`https://yadopera-frontend-staging.onrender.com/test.html\`

\#\#\# デバッグ案3: Chrome Remote Debuggingを使用

Android端末の場合:  
1\. 開発者オプションを有効化  
2\. USBデバッグを有効化  
3\. PCとUSB接続  
4\. Chrome DevToolsで\`chrome://inspect\`を開く  
5\. 実機のブラウザでコンソールエラーを確認

\---

\#\# 💡 根本原因のまとめ

1\. \*\*Render.comは\`\_headers\`ファイルをサポートしていない\*\*  
   \- ダッシュボードから設定が必要

2\. \*\*SPAのルーティングが正しく設定されていない\*\*  
   \- Rewrite Ruleをダッシュボードから設定する必要がある  
   \- \`\_redirects\`ファイルだけでは不十分な可能性

3\. \*\*モバイルブラウザでの制約\*\*  
   \- デスクトップブラウザよりも厳密なContent-Type検証  
   \- JavaScriptの読み込み失敗に対するフォールバックが必要

\*\*最優先で実施すべき\*\*: 修正案A（Render.comダッシュボードでRewrite Rule設定）

この修正により、スマートフォンとタブレットでの画面真っ白問題が解決すると考えられます。