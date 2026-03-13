import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'
import { readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'

// アイコン版番号（index.html の __ICON_VERSION__ をビルド時に置換するため）
function getIconVersion(): string {
  try {
    const p = resolve(dirname(fileURLToPath(import.meta.url)), 'src/utils/icon-version.json')
    const { version } = JSON.parse(readFileSync(p, 'utf-8'))
    return String(version)
  } catch {
    return '1'
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  base: '/',
  plugins: [
    vue(),
    {
      name: 'html-inject-icon-version',
      transformIndexHtml(html) {
        return html.replace(/__ICON_VERSION__/g, getIconVersion())
      }
    },
    VitePWA({
      registerType: 'manual',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/faq-csv-template\//],
        navigationPreload: false,
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
      manifest: false  // 静的manifestの生成を無効化（動的manifestのみを使用）
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


