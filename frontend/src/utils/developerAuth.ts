/**
 * 開発者認証ユーティリティ
 */

/**
 * 開発者トークンの有効期限をチェック
 * JWTトークンから有効期限を取得して確認
 */
export const isDeveloperTokenExpired = (): boolean => {
  try {
    const token = localStorage.getItem('developer_token')
    if (!token) {
      return true
    }

    // JWTトークンをデコード（簡易版）
    // 実際の有効期限チェックはサーバー側で行われるが、クライアント側でも簡易チェック
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp
      if (!exp) {
        return true
      }

      // 有効期限をチェック（秒単位のUnixタイムスタンプ）
      const expiryDate = new Date(exp * 1000)
      return expiryDate < new Date()
    } catch (e) {
      // トークンのデコードに失敗した場合、期限切れとみなす
      return true
    }
  } catch (error) {
    // localStorageアクセスエラーの場合、期限切れとみなす
    return true
  }
}

/**
 * 開発者ログアウト処理
 */
export const logoutDeveloper = () => {
  try {
    localStorage.removeItem('developer_token')
    // ログインページにリダイレクト
    window.location.href = '/developer/login'
  } catch (error) {
    console.warn('Failed to logout developer:', error)
    // エラーが発生してもリダイレクト
    window.location.href = '/developer/login'
  }
}

/**
 * 開発者トークンの有効期限を取得（表示用）
 */
export const getDeveloperTokenExpiry = (): Date | null => {
  try {
    const token = localStorage.getItem('developer_token')
    if (!token) {
      return null
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp
      if (!exp) {
        return null
      }

      return new Date(exp * 1000)
    } catch (e) {
      return null
    }
  } catch (error) {
    return null
  }
}

