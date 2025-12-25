# ⚠️ 危険！重要！ PWAインストール後の起動時404エラー 調査依頼書

**⚠️ 危険！重要！**: この文書にはAI Assistantの誤った認識が反映されている可能性があります。必ず`docs/Phase1_Phase2_PWAインストール後の起動時404エラー_期待動作_誤認識警告_20251222.md`を参照してください。

**作成日時**: 2025年12月22日  
**依頼先**: ChatGPT / Claude  
**目的**: PWAインストール後の起動時404エラーの根本原因を特定し、確実な解決策を提案する  
**緊急度**: 🔴 **最高（ユーザー価値が暴落している状態）**

---

## 1. プロジェクト概要

### 1.1 プロジェクト名
**YadOPERA** - 小規模宿泊施設向けAI多言語自動案内システム

### 1.2 プロジェクトの目的
- 小規模宿泊施設向けのSaaSサービス
- QRコードを介してゲストが24時間365日多言語でAIチャットボットと対話可能
- 管理者はダッシュボードで会話履歴を確認し、必要に応じてエスカレーション

### 1.3 現在のフェーズ
- **Phase 2（PoC準備）**: ステージング環境でのテスト中
- 本番環境への移行前の最終調整段階

---

## 2. 問題の詳細

### 2.1 問題の概要
**PWAインストール後の起動時に404エラーが発生し、アプリが起動しない**

### 2.2 症状
- **発生率**: 100%（全端末で発生）
- **発生端末**: 
  - iPad（Safari iOS）
  - Pixel（Chrome Android）
- **発生タイミング**: PWAをインストール後、ホーム画面のアイコンをタップしてアプリを起動した際
- **エラー内容**: 404エラー（Not Found）

### 2.3 エラーログ
```
[Error] Failed to load resource: the server responded with a status of 404 (Not Found) (token, line 0)
[Error] Failed to load resource: the server responded with a status of 500 (Internal Server Error) (431bf1e3-7816-4d23-846a-08376ec491d3, line 0)
```

### 2.4 発生条件
1. ブラウザでPWAをインストール（ホーム画面にアイコンを追加）
2. ホーム画面のアイコンをタップ
3. `start_url: '/'`にアクセス
4. **404エラーが発生**

### 2.5 影響
- **ユーザー体験**: 致命的 - PWAとして使用できない
- **ビジネス影響**: ユーザー価値が暴落
- **緊急度**: 最高 - 即座に解決が必要

### 2.6 通常のブラウザアクセス時の動作
- **正常に動作**: ブラウザで直接URLにアクセスした場合は正常に動作
- **問題なし**: Service Workerの登録、ルーティング、API通信すべて正常

---

## 3. 技術スタック

### 3.1 フロントエンド
- **フレームワーク**: Vue.js 3.4.21
- **言語**: TypeScript
- **ビルドツール**: Vite 5.0.12
- **ルーティング**: Vue Router 4.3.0
- **PWAプラグイン**: vite-plugin-pwa 0.19.8
- **Service Worker**: Workbox（vite-plugin-pwa経由）
- **スタイリング**: Tailwind CSS 3.4.1
- **状態管理**: Pinia 2.1.7

### 3.2 バックエンド
- **フレームワーク**: FastAPI（Python）
- **データベース**: PostgreSQL with pgvector
- **キャッシュ**: Redis

### 3.3 デプロイ環境
- **フロントエンド**: Render.com Static Site
- **バックエンド**: Render.com Web Service
- **リージョン**: Tokyo

### 3.4 開発環境
- **Docker / Docker Compose**: 必須（大原則）
- **Node.js**: >=18.0.0 <23.0.0
- **npm**: >=9.0.0

---

## 4. 現在の実装状況

### 4.1 PWA設定ファイル

#### 4.1.1 `frontend/vite.config.ts`
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  base: '/',
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//],
        navigationPreload: false,
        runtimeCaching: [
          {
            urlPattern: /\/api\/v1\/admin\/.*$/,
            handler: 'NetworkOnly',
            method: 'GET'
          },
          {
            urlPattern: /\/api\/v1\/facility\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'facility-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 // 24時間
              }
            }
          }
        ]
      },
      manifest: {
        name: 'YadOPERA',
        short_name: 'YadOPERA',
        description: '小規模宿泊施設向けAI多言語自動案内システム',
        theme_color: '#ffffff',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        icons: [
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
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true
    }
  }
})
```

#### 4.1.2 `frontend/dist/manifest.webmanifest`（生成されたファイル）
```json
{
  "name": "YadOPERA",
  "short_name": "YadOPERA",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "lang": "en",
  "scope": "/",
  "description": "小規模宿泊施設向けAI多言語自動案内システム",
  "theme_color": "#ffffff",
  "icons": [
    {
      "src": "pwa-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "pwa-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

#### 4.1.3 `frontend/dist/index.html`（生成されたファイル）
```html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>YadOPERA</title>
    <script type="module" crossorigin src="/assets/index-BIL2B6qr.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-BWPcFWvR.css">
    <link rel="manifest" href="/manifest.webmanifest">
    <script id="vite-plugin-pwa:register-sw" src="/registerSW.js"></script>
  </head>
  <body>
    <div id="app"></div>
  </body>
</html>
```

### 4.2 Service Worker設定

#### 4.2.1 生成されたService Worker（`frontend/dist/sw.js`）
- **ファイルサイズ**: 約3KB（minified）
- **登録されているルート**:
  1. `NavigationRoute`（`navigateFallback`から生成）
     - `new s.NavigationRoute(s.createHandlerBoundToURL("/index.html"),{denylist:[/^\/api\//]})`
  2. APIリクエストに対するキャッシュ戦略
     - `/api/v1/admin/*` → `NetworkOnly`
     - `/api/v1/facility/*` → `NetworkFirst`

**重要な点**: 修正案1実施後、ナビゲーションリクエストに対する`NetworkFirst`戦略は削除されている

### 4.3 デプロイ設定

#### 4.3.1 `render.yaml`
```yaml
services:
  - type: static
    name: yadopera-frontend-staging
    rootDir: frontend
    buildCommand: npx vite build
    staticPublishPath: dist
    envVars:
      - key: VITE_API_BASE_URL
        value: https://yadopera-backend-staging.onrender.com
      - key: VITE_ENVIRONMENT
        value: staging
    routes:
      - type: rewrite
        source: /assets/*
        destination: /assets/*
      - type: rewrite
        source: /registerSW.js
        destination: /registerSW.js
      - type: rewrite
        source: /manifest.webmanifest
        destination: /manifest.webmanifest
      - type: rewrite
        source: /sw.js
        destination: /sw.js
      - type: rewrite
        source: /*
        destination: /index.html
```

### 4.4 Vue Router設定

#### 4.4.1 `frontend/src/router/index.ts`
```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { guestRoutes } from './guest'
import { adminRoutes } from './admin'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  ...guestRoutes,
  ...adminRoutes,
  {
    path: '/500',
    name: 'Error500',
    component: () => import('@/views/Error500.vue'),
    meta: {
      layout: undefined
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/Error404.vue'),
    meta: {
      layout: undefined
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 認証ガード
router.beforeEach(async (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore()
  
  // トークンが存在するが、ユーザー情報が取得されていない場合、取得を試みる
  if (authStore.token && !authStore.user) {
    try {
      await authStore.initAuth()
    } catch (error) {
      console.error('Failed to initialize auth:', error)
      authStore.logout()
      
      const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
      if (requiresAuth) {
        return next({
          name: 'AdminLogin',
          query: { redirect: to.fullPath }
        })
      }
    }
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    return next({
      name: 'AdminLogin',
      query: { redirect: to.fullPath }
    })
  }
  
  if (to.name === 'AdminLogin' && authStore.isAuthenticated) {
    return next({ name: 'AdminDashboard' })
  }
  
  next()
})

export default router
```

#### 4.4.2 `frontend/src/main.ts`
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { useThemeStore } from './stores/theme'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初期化処理（すべて非同期で実行）
async function initializeApp() {
  try {
    const themeStore = useThemeStore()
    themeStore.initTheme()

    const authStore = useAuthStore()
    await authStore.initAuth()
  } catch (error) {
    console.error('Failed to initialize app:', error)
  } finally {
    app.mount('#app')
  }
}

initializeApp()
```

### 4.5 ゲストルート設定

#### 4.5.1 `frontend/src/router/guest.ts`
```typescript
import type { RouteRecordRaw } from 'vue-router'

export const guestRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Welcome',
    component: () => import('@/views/guest/Welcome.vue'),
    meta: {
      layout: 'guest'
    }
  },
  {
    path: '/f/:facilitySlug',
    name: 'GuestChat',
    component: () => import('@/views/guest/Chat.vue'),
    meta: {
      layout: 'guest'
    }
  }
]
```

---

## 5. これまで実施した修正とその結果

### 5.1 修正履歴

#### 修正1: Manifest.jsonの設定追加（2025年12月22日）
**実施内容**:
- `start_url: '/'`を明示的に設定
- `scope: '/'`を明示的に設定
- `display: 'standalone'`を明示的に設定

**結果**: ❌ **失敗** - 404エラーが継続

#### 修正2: ナビゲーションリクエストに対する明示的なキャッシュ戦略追加（2025年12月22日）
**実施内容**:
- `navigationPreload: false`を追加
- ナビゲーションリクエストに対する`NetworkFirst`戦略を追加
  ```typescript
  {
    urlPattern: ({ request }) => request.mode === 'navigate',
    handler: 'NetworkFirst',
    options: {
      cacheName: 'html-cache',
      expiration: {
        maxEntries: 50,
        maxAgeSeconds: 60 * 60 * 24 * 7 // 7日間
      },
      networkTimeoutSeconds: 3
    }
  }
  ```

**結果**: ❌ **失敗** - 404エラーが継続

#### 修正3: NavigationRouteとNetworkFirstの競合解消（2025年12月22日）
**実施内容**:
- ナビゲーションリクエストに対する`NetworkFirst`戦略を削除
- `NavigationRoute`（`navigateFallback`から生成）のみを使用

**結果**: ❌ **失敗** - 404エラーが継続

### 5.2 調査分析結果

#### 調査1: 全端末共通問題の完全調査分析（2025年12月22日）
**結論**:
- PWAインストール後の起動時に、Service Workerが登録されていない状態で`start_url: '/'`にアクセス
- Service Workerが登録されていない場合、`navigateFallback`は動作しない
- Render.comのリライト設定（`/*` → `/index.html`）に依存する必要がある
- しかし、Render.comのリライト設定が正しく動作していない可能性がある

#### 調査2: 多角的調査分析（2025年12月22日）
**結論**:
- `NavigationRoute`と`NetworkFirst`の競合の可能性
- Service Workerが登録されていない状態での動作の問題
- Render.comのリライト設定の問題

**修正案**: `NetworkFirst`を削除し、`NavigationRoute`のみを使用（修正3として実施）

**結果**: ❌ **失敗** - 404エラーが継続

---

## 6. 開発環境

### 6.1 Docker環境
- **必須**: 大原則により、すべての修正・テストはDocker環境で実行
- **構成**: `docker-compose.yml`を使用

### 6.2 ビルドコマンド
```bash
docker-compose exec frontend npm run build
```

### 6.3 ビルド結果
- ✅ **成功**: ビルドは正常に完了
- ✅ **Service Worker生成**: `dist/sw.js`が正常に生成される
- ✅ **Manifest生成**: `dist/manifest.webmanifest`が正常に生成される

---

## 7. デプロイ環境

### 7.1 Render.com Static Site
- **サービス名**: `yadopera-frontend-staging`
- **URL**: `https://yadopera-frontend-staging.onrender.com`
- **ビルドコマンド**: `npx vite build`
- **公開パス**: `dist`

### 7.2 リライト設定
- `/*` → `/index.html`（SPA用）
- `/assets/*` → `/assets/*`
- `/registerSW.js` → `/registerSW.js`
- `/manifest.webmanifest` → `/manifest.webmanifest`
- `/sw.js` → `/sw.js`

### 7.3 デプロイプロセス
1. `develop`ブランチにプッシュ
2. Render.comが自動的にビルドを開始
3. ビルド完了後、自動的にデプロイ
4. 通常2-5分で完了

---

## 8. 期待する動作

**⚠️ 危険！重要！**: 以下の期待動作の記述には誤りが含まれている可能性があります。正しい期待動作については、`docs/Phase1_Phase2_PWAインストール後の起動時404エラー_期待動作_誤認識警告_20251222.md`を参照してください。

### 8.1 PWAインストール後の起動時（正しい期待動作）
1. ゲストがPWAアイコンをタップ
2. `start_url: '/'`にアクセス
3. **`index.html`が返される**
4. Vue Routerが正しく初期化される
5. **localStorageから最後にアクセスした施設URLを取得**
6. **保存された施設URLにリダイレクト**
7. **施設独自の画面が表示される**
8. **⚠️ 誤った認識**: 「404エラーページを表示する」という動作は期待されていません。この状況は発生してはいけません。

### 8.2 通常のブラウザアクセス時
1. ブラウザでURLにアクセス
2. `index.html`が読み込まれる
3. `registerSW.js`が実行される
4. Service Workerが登録される
5. `NavigationRoute`が動作する
6. アプリが正常に起動する

---

## 9. 現況

### 9.1 現在の状態
- **問題**: PWAインストール後の起動時に404エラーが発生
- **発生率**: 100%（全端末で発生）
- **修正試行回数**: 3回
- **修正結果**: すべて失敗

### 9.2 確認済みの項目
- ✅ Manifest.jsonの設定は正しい
- ✅ Service Workerの設定は正しい
- ✅ Render.comのリライト設定は正しい
- ✅ ビルドは正常に完了
- ✅ 通常のブラウザアクセス時は正常に動作

### 9.3 未解決の項目
- ❌ PWAインストール後の起動時に404エラーが発生
- ❌ Service Workerが登録されていない状態での動作
- ❌ Render.comのリライト設定がPWA起動時に正しく動作していない可能性

---

## 10. 関連ファイルのパス

### 10.1 設定ファイル
- `frontend/vite.config.ts` - Vite設定（PWA設定含む）
- `render.yaml` - Render.comデプロイ設定
- `frontend/package.json` - 依存関係

### 10.2 生成されたファイル
- `frontend/dist/index.html` - エントリーポイントHTML
- `frontend/dist/sw.js` - Service Worker
- `frontend/dist/manifest.webmanifest` - PWAマニフェスト
- `frontend/dist/registerSW.js` - Service Worker登録スクリプト

### 10.3 ソースコード
- `frontend/src/main.ts` - アプリケーションエントリーポイント
- `frontend/src/router/index.ts` - Vue Router設定
- `frontend/src/router/guest.ts` - ゲストルート設定
- `frontend/src/App.vue` - ルートコンポーネント

### 10.4 ドキュメント
- `docs/Phase1_Phase2_PWAインストール後の起動時404エラー_全端末共通問題_完全調査分析_根本原因確定_20251222.md`
- `docs/Phase1_Phase2_PWAインストール後の起動時404エラー_デプロイ後再発_多角的調査分析_20251222.md`
- `docs/Phase1_Phase2_PWAインストール後の起動時404エラー_修正案1実施完了_20251222.md`

---

## 11. 調査すべき観点

### 11.1 Service Workerの登録タイミング
- PWAインストール後の起動時に、Service Workerが登録されているか
- Service Workerが登録されていない場合、どのように`index.html`を返すべきか

### 11.2 Render.comのリライト設定
- Render.comのリライト設定（`/*` → `/index.html`）がPWA起動時に正しく動作しているか
- PWA起動時のリクエストがRender.comのリライト設定に到達しているか

### 11.3 WorkboxのNavigationRoute
- `NavigationRoute`がPWA起動時に正しく動作しているか
- Service Workerが登録されていない状態で`NavigationRoute`が動作するか

### 11.4 ブラウザのPWA起動動作
- ブラウザがPWA起動時にどのようなリクエストを送信するか
- `start_url: '/'`へのアクセスがどのように処理されるか

### 11.5 キャッシュの状態
- PWAインストール後の起動時に、キャッシュが空の状態か
- キャッシュが空の場合、どのように`index.html`を返すべきか

### 11.6 ネットワークリクエスト
- PWA起動時に実際にどのようなネットワークリクエストが発生しているか
- 404エラーが発生しているリクエストの詳細

---

## 12. 追加情報

### 12.1 大原則（開発・実装の基本方針）
1. **根本解決 > 暫定解決**: 一時的な対処よりも根本的な解決を優先
2. **シンプル構造 > 複雑構造**: 複雑な実装よりもシンプルで理解しやすい構造を優先
3. **統一・同一化 > 特殊独自**: 特殊な実装よりも統一されたパターンを優先
4. **具体的 > 一般**: 抽象的な実装よりも具体的で明確な実装を優先
5. **拙速 < 安全確実**: 速度よりも安全性と確実性を優先
6. **Docker環境必須 > ローカル直接実行**: すべての修正・テストはDocker環境で実行

### 12.2 プロジェクトの重要度
- **ユーザー価値**: 致命的な問題 - PWAとして使用できない
- **ビジネス影響**: ユーザー価値が暴落
- **緊急度**: 最高 - 即座に解決が必要

### 12.3 テスト環境
- **ステージング環境**: `https://yadopera-frontend-staging.onrender.com`
- **テスト端末**: iPad（Safari iOS）、Pixel（Chrome Android）

---

## 13. 調査依頼事項

### 13.1 根本原因の特定
1. PWAインストール後の起動時に404エラーが発生する根本原因を特定してください
2. これまでの修正が失敗した理由を分析してください
3. Service Workerが登録されていない状態での動作を考慮してください

### 13.2 解決策の提案
1. 確実に動作する解決策を提案してください
2. 大原則に準拠した解決策を提案してください
3. 複数の解決策がある場合、優先順位を付けてください

### 13.3 実装手順
1. 解決策の実装手順を詳細に記載してください
2. テスト方法を記載してください
3. 期待される結果を記載してください

---

## 14. 補足情報

### 14.1 プロジェクトのGitHubリポジトリ
- **リポジトリ**: `https://github.com/kurinobu/yadopera`
- **ブランチ**: `develop`（ステージング環境）

### 14.2 関連技術ドキュメント
- **Vite PWA Plugin**: https://vite-pwa-org.netlify.app/
- **Workbox**: https://developers.google.com/web/tools/workbox
- **Render.com Static Site**: https://render.com/docs/static-sites

### 14.3 連絡先
- 調査結果は、このドキュメントに基づいて実施してください
- 追加の情報が必要な場合は、このドキュメントの内容を参照してください

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025年12月22日  
**Status**: 📋 **調査依頼書作成完了**

**重要**: この問題はユーザー価値に直結する致命的な問題です。確実な解決策の提案をお願いします。

