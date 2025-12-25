/**
 * 動的Web App Manifest生成ユーティリティ
 * 
 * PWAインストール時に現在の施設URLをstart_urlに設定することで、
 * PWA起動時に直接施設URLにアクセスし、localStorageへの依存を排除する
 */

export interface DynamicManifest {
  name: string
  short_name: string
  description: string
  theme_color: string
  start_url: string
  scope: string
  display: string
  icons: Array<{
    src: string
    sizes: string
    type: string
  }>
}

/**
 * 動的manifestを生成
 * @param facilityId - 施設ID（nullの場合は'/'をstart_urlに設定）
 * @returns DynamicManifest
 */
export function generateManifest(facilityId: string | null): DynamicManifest {
  const startUrl = facilityId ? `/f/${facilityId}` : '/'
  
  return {
    name: 'YadOPERA',
    short_name: 'YadOPERA',
    description: '小規模宿泊施設向けAI多言語自動案内システム',
    theme_color: '#ffffff',
    start_url: startUrl,
    scope: '/',
    display: 'standalone',
    icons: [
      {
        src: '/pwa-192x192.png',
        sizes: '192x192',
        type: 'image/png'
      },
      {
        src: '/pwa-512x512.png',
        sizes: '512x512',
        type: 'image/png'
      }
    ]
  }
}

/**
 * manifest linkタグを動的に更新
 * @param facilityId - 施設ID
 */
export function updateManifestLink(facilityId: string | null): void {
  try {
    // 既存のmanifest linkタグを削除
    const existingLink = document.querySelector('link[rel="manifest"]')
    if (existingLink) {
      existingLink.remove()
    }
    
    // 動的manifestを生成
    const manifest = generateManifest(facilityId)
    const manifestBlob = new Blob([JSON.stringify(manifest)], { type: 'application/json' })
    const manifestUrl = URL.createObjectURL(manifestBlob)
    
    // 新しいmanifest linkタグを追加
    const link = document.createElement('link')
    link.rel = 'manifest'
    link.href = manifestUrl
    document.head.appendChild(link)
    
    console.log('[PWA] manifestを動的に更新しました:', { facilityId, startUrl: manifest.start_url })
  } catch (error) {
    console.error('[PWA] manifestの更新に失敗しました:', error)
  }
}

