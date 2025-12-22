import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
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
        // 管理APIは常に最新を取得するため、キャッシュさせない
        runtimeCaching: [
          {
            // ナビゲーションリクエスト（HTMLの読み込み）に対する明示的なキャッシュ戦略
            // PWAインストール後の起動時にも確実にindex.htmlを返すため
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
          },
          {
            urlPattern: /\/api\/v1\/admin\/.*$/,
            handler: 'NetworkOnly',
            method: 'GET'
          },
          {
            // 施設情報APIはネットワーク優先、失敗時はキャッシュから取得
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


