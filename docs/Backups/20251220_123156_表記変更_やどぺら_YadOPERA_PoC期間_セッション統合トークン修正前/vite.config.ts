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
        // 管理APIは常に最新を取得するため、キャッシュさせない
        runtimeCaching: [
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
        name: 'やどぺら',
        short_name: 'やどぺら',
        description: '小規模宿泊施設向けAI多言語自動案内システム',
        theme_color: '#ffffff',
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


