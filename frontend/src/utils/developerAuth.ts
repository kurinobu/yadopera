/**
 * 開発者認証ユーティリティ
 */

/**
 * 開発者トークンの有効期限をチェック
 * JWTトークンから有効期限を取得して確認
 */
export const isDeveloperTokenExpired = (): boolean => {
  try {
    // ブラウザ環境でない場合（SSR等）は期限切れとみなす
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
      return true
    }

    const token = localStorage.getItem('developer_token')
    if (!token) {
      return true
    }

    // トークンの形式をチェック
    const tokenParts = token.split('.')
    if (tokenParts.length !== 3) {
      console.warn('Invalid JWT token format')
      return true
    }

    // JWTトークンをデコード（簡易版）
    // 実際の有効期限チェックはサーバー側で行われるが、クライアント側でも簡易チェック
    try {
      const payload = JSON.parse(atob(tokenParts[1]))
      const exp = payload.exp
      if (!exp || typeof exp !== 'number') {
        console.warn('Invalid or missing token expiration')
        return true
      }

      // 有効期限をチェック（秒単位のUnixタイムスタンプ）
      const expiryDate = new Date(exp * 1000)
      const now = new Date()
      
      // デバッグ情報をログ出力
      console.debug('Token expiry check:', {
        expiryDate: expiryDate.toISOString(),
        now: now.toISOString(),
        isExpired: expiryDate < now
      })
      
      return expiryDate < now
    } catch (decodeError) {
      // トークンのデコードに失敗した場合、期限切れとみなす
      console.warn('Failed to decode JWT token:', decodeError)
      return true
    }
  } catch (error) {
    // localStorageアクセスエラーやその他のエラーの場合、期限切れとみなす
    console.warn('Error checking token expiration:', error)
    return true
  }
}

/**
 * 開発者ログアウト処理
 */
export const logoutDeveloper = () => {
  try {
    // ブラウザ環境でない場合は何もしない
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
      console.warn('Cannot logout: not in browser environment')
      return
    }

    localStorage.removeItem('developer_token')
    
    // ログインページにリダイレクト
    // Vue Routerが利用可能な場合はそちらを優先
    if (window.location) {
      window.location.href = '/developer/login'
    }
  } catch (error) {
    console.warn('Failed to logout developer:', error)
    // エラーが発生してもリダイレクトを試行
    try {
      if (typeof window !== 'undefined' && window.location) {
        window.location.href = '/developer/login'
      }
    } catch (redirectError) {
      console.error('Failed to redirect to login page:', redirectError)
    }
  }
}

/**
 * 開発者トークンの有効期限を取得（表示用）
 */
export const getDeveloperTokenExpiry = (): Date | null => {
  try {
    // ブラウザ環境でない場合はnullを返す
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
      return null
    }

    const token = localStorage.getItem('developer_token')
    if (!token) {
      return null
    }

    // トークンの形式をチェック
    const tokenParts = token.split('.')
    if (tokenParts.length !== 3) {
      console.warn('Invalid JWT token format')
      return null
    }

    try {
      const payload = JSON.parse(atob(tokenParts[1]))
      const exp = payload.exp
      if (!exp || typeof exp !== 'number') {
        return null
      }

      return new Date(exp * 1000)
    } catch (decodeError) {
      console.warn('Failed to decode JWT token for expiry:', decodeError)
      return null
    }
  } catch (error) {
    console.warn('Error getting token expiry:', error)
    return null
  }
}

