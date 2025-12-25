# Phase 1: ステップ6 ログイン状態維持問題 完全調査分析・修正案

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: ブラウザの戻るボタンでログイン画面に戻ってしまう問題の完全調査分析と修正案  
**目的**: 大原則に準拠した根本解決方法を提示

---

## 1. 問題の詳細

### 1.1 現象

- ブラウザの戻るボタンをタップするとログイン画面に戻ってしまう
- ログイン状態を維持していないため、ログアウトしない限りログイン画面に戻ると面倒
- ページリロード時にも同様の問題が発生する可能性がある

### 1.2 発生条件

1. 管理画面でログイン後、他のページ（例: ダッシュボード、FAQ管理、QRコード発行など）に移動する
2. ブラウザの戻るボタンをタップしてログイン画面に戻る
3. または、ページをリロードする

### 1.3 期待される動作

- ログイン後、ページをリロードしてもログイン状態が維持される
- ブラウザの戻るボタンでログイン画面に戻った際、ログイン状態が維持され、自動的にダッシュボードにリダイレクトされる
- ログアウト後、ログイン画面が表示される

---

## 2. 根本原因の分析

### 2.1 現在の実装状況

#### 2.1.1 認証ストア（`frontend/src/stores/auth.ts`）

```typescript:39:45:frontend/src/stores/auth.ts
function initAuth() {
  const storedToken = localStorage.getItem('auth_token')
  if (storedToken) {
    token.value = storedToken
    // TODO: トークンからユーザー情報を取得（Week 4で実装）
  }
}
```

**問題点**:
- `initAuth()`は`localStorage`からトークンを読み込むだけで、ユーザー情報を取得していない
- `user.value`が`null`のままになる

#### 2.1.2 認証状態の判定（`frontend/src/stores/auth.ts`）

```typescript:13:13:frontend/src/stores/auth.ts
const isAuthenticated = computed(() => !!token.value && !!user.value)
```

**問題点**:
- `isAuthenticated`は`!!token.value && !!user.value`で判定される
- `user.value`が`null`の場合、`isAuthenticated`は`false`になる
- そのため、ページリロード時や戻るボタンでログイン画面に戻った際、`isAuthenticated`が`false`になり、ログイン画面が表示されてしまう

#### 2.1.3 ルーターガード（`frontend/src/router/index.ts`）

```typescript:39:55:frontend/src/router/index.ts
router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    // 認証が必要なページに未認証でアクセスした場合
    next({
      name: 'AdminLogin',
      query: { redirect: to.fullPath }
    })
  } else if (to.name === 'AdminLogin' && authStore.isAuthenticated) {
    // 既に認証済みの場合はダッシュボードにリダイレクト
    next({ name: 'AdminDashboard' })
  } else {
    next()
  }
})
```

**問題点**:
- `authStore.isAuthenticated`が`false`の場合、ログイン画面にリダイレクトされる
- `initAuth()`がユーザー情報を取得していないため、`isAuthenticated`が`false`になる

#### 2.1.4 アプリ起動時の初期化（`frontend/src/main.ts`）

```typescript:19:20:frontend/src/main.ts
const authStore = useAuthStore()
authStore.initAuth()
```

**問題点**:
- アプリ起動時に`initAuth()`が呼ばれるが、ユーザー情報を取得していない

### 2.2 根本原因の特定

**根本原因**:
1. `initAuth()`が`localStorage`からトークンを読み込むだけで、ユーザー情報を取得していない
2. `isAuthenticated`は`!!token.value && !!user.value`で判定されるため、`user.value`が`null`の場合、`isAuthenticated`が`false`になる
3. バックエンドには、現在のユーザー情報を取得するエンドポイント（`/api/v1/auth/me`）が存在しない

**影響範囲**:
- ページリロード時にログイン状態が維持されない
- ブラウザの戻るボタンでログイン画面に戻った際、ログイン状態が維持されない
- ユーザー体験が大幅に低下する

---

## 3. バックエンドの実装状況

### 3.1 認証APIエンドポイント

**現在のエンドポイント**:
- `POST /api/v1/auth/login`: ログイン
- `POST /api/v1/auth/logout`: ログアウト

**存在しないエンドポイント**:
- `GET /api/v1/auth/me`: 現在のユーザー情報を取得するエンドポイント

### 3.2 依存性注入（`get_current_user`）

```python:19:84:backend/app/api/deps.py
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    現在のユーザー取得（JWT認証）
    
    Args:
        credentials: HTTPBearer認証情報
        db: データベースセッション
        
    Returns:
        認証されたユーザー
        
    Raises:
        HTTPException: 認証失敗時
    """
    token = credentials.credentials
    
    # トークンデコード
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ユーザーID取得
    sub_value = payload.get("sub")
    if sub_value is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 文字列から整数に変換
    try:
        user_id = int(sub_value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ユーザー取得
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user
```

**確認事項**:
- `get_current_user`は依存性注入として使用されているが、直接呼び出せるエンドポイントではない
- 新しいエンドポイント（`/api/v1/auth/me`）を作成する必要がある

### 3.3 ユーザーレスポンススキーマ

```python:18:30:backend/app/schemas/auth.py
class UserResponse(BaseModel):
    """
    ユーザー情報レスポンス
    """
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    facility_id: int
    is_active: bool

    class Config:
        from_attributes = True
```

**確認事項**:
- `UserResponse`スキーマは既に存在する
- 新しいエンドポイントで使用できる

---

## 4. 修正案

### 4.1 修正方針（大原則に準拠）

#### 4.1.1 根本解決 > 暫定解決

- ✅ **根本解決**: `initAuth()`でトークンからユーザー情報を取得するAPIを呼び出す
- ❌ **暫定解決**: JWTトークンをデコードしてユーザー情報を取得（トークンの有効性を確認できない）

#### 4.1.2 シンプル構造 > 複雑構造

- ✅ **シンプル構造**: 既存の`get_current_user`を使用して新しいエンドポイントを作成
- ❌ **複雑構造**: フロントエンドでJWTトークンをデコードする

#### 4.1.3 統一・同一化 > 特殊独自

- ✅ **統一・同一化**: 既存の認証パターンに従い、`get_current_user`を使用
- ❌ **特殊独自**: フロントエンドで独自のJWTデコード処理を実装

#### 4.1.4 具体的 > 一般

- ✅ **具体的**: 具体的な実装手順を明確にする

#### 4.1.5 拙速 < 安全確実

- ✅ **安全確実**: バックエンドでトークンの有効性を確認し、ユーザー情報を取得する

### 4.2 推奨修正案: オプション1（バックエンドAPIエンドポイント追加）

#### 4.2.1 修正内容

**ステップ1: バックエンドに`/api/v1/auth/me`エンドポイントを追加**

**ファイル**: `backend/app/api/v1/auth.py`

```python
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    現在のユーザー情報取得
    
    JWTトークンから現在のユーザー情報を返却
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        facility_id=current_user.facility_id,
        is_active=current_user.is_active
    )
```

**ステップ2: フロントエンドの認証APIクライアントに`getCurrentUser`メソッドを追加**

**ファイル**: `frontend/src/api/auth.ts`

```typescript
export const authApi = {
  /**
   * ログイン
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  /**
   * ログアウト
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  },

  /**
   * 現在のユーザー情報取得
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  }
}
```

**ステップ3: 認証ストアの`initAuth`関数を修正**

**ファイル**: `frontend/src/stores/auth.ts`

```typescript
import { authApi } from '@/api/auth'

function initAuth() {
  const storedToken = localStorage.getItem('auth_token')
  if (storedToken) {
    token.value = storedToken
    // トークンからユーザー情報を取得
    authApi.getCurrentUser()
      .then((userData) => {
        setUser(userData)
      })
      .catch((error) => {
        // トークンが無効な場合、ログアウト
        console.error('Failed to get current user:', error)
        logout()
      })
  }
}
```

**ステップ4: 非同期処理の考慮**

`initAuth()`が非同期処理を含むため、ルーターガードで適切に処理する必要があります。

**オプションA: `initAuth()`を非同期関数に変更**

```typescript
async function initAuth() {
  const storedToken = localStorage.getItem('auth_token')
  if (storedToken) {
    token.value = storedToken
    try {
      const userData = await authApi.getCurrentUser()
      setUser(userData)
    } catch (error) {
      // トークンが無効な場合、ログアウト
      console.error('Failed to get current user:', error)
      logout()
    }
  }
}
```

**オプションB: ルーターガードで非同期処理を待機**

```typescript
router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore()
  
  // トークンが存在するが、ユーザー情報が取得されていない場合、取得を試みる
  if (authStore.token && !authStore.user) {
    try {
      await authStore.initAuth()
    } catch (error) {
      console.error('Failed to initialize auth:', error)
    }
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    // 認証が必要なページに未認証でアクセスした場合
    next({
      name: 'AdminLogin',
      query: { redirect: to.fullPath }
    })
  } else if (to.name === 'AdminLogin' && authStore.isAuthenticated) {
    // 既に認証済みの場合はダッシュボードにリダイレクト
    next({ name: 'AdminDashboard' })
  } else {
    next()
  }
})
```

#### 4.2.2 メリット

- ✅ **根本解決**: トークンの有効性をバックエンドで確認し、ユーザー情報を取得する
- ✅ **安全確実**: トークンが無効な場合、適切にログアウトする
- ✅ **シンプル構造**: 既存のパターンに従い、統一された実装
- ✅ **統一・同一化**: 既存の`get_current_user`を使用

#### 4.2.3 デメリット

- ⚠️ アプリ起動時にAPI呼び出しが発生する（ただし、これは必要な処理）
- ⚠️ 非同期処理の考慮が必要

### 4.3 代替案: オプション2（JWTトークンデコード）

#### 4.3.1 修正内容

フロントエンドでJWTトークンをデコードしてユーザー情報を取得する方法です。

**問題点**:
- トークンの有効性を確認できない（期限切れのトークンでもデコードできる）
- ユーザー情報がトークンに含まれていない可能性がある
- セキュリティ上の懸念がある

**推奨しません**。

---

## 5. 推奨修正案の詳細実装手順

### 5.1 バックエンド修正

#### ステップ1: 認証APIエンドポイントに`/me`を追加

**ファイル**: `backend/app/api/v1/auth.py`

```python
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    現在のユーザー情報取得
    
    JWTトークンから現在のユーザー情報を返却
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        facility_id=current_user.facility_id,
        is_active=current_user.is_active
    )
```

### 5.2 フロントエンド修正

#### ステップ1: 認証APIクライアントに`getCurrentUser`メソッドを追加

**ファイル**: `frontend/src/api/auth.ts`

```typescript
export const authApi = {
  /**
   * ログイン
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  /**
   * ログアウト
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  },

  /**
   * 現在のユーザー情報取得
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  }
}
```

#### ステップ2: 認証ストアの`initAuth`関数を修正

**ファイル**: `frontend/src/stores/auth.ts`

```typescript
import { authApi } from '@/api/auth'

async function initAuth() {
  const storedToken = localStorage.getItem('auth_token')
  if (storedToken) {
    token.value = storedToken
    try {
      // トークンからユーザー情報を取得
      const userData = await authApi.getCurrentUser()
      setUser(userData)
    } catch (error) {
      // トークンが無効な場合、ログアウト
      console.error('Failed to get current user:', error)
      logout()
    }
  }
}
```

#### ステップ3: `main.ts`で非同期処理を待機

**ファイル**: `frontend/src/main.ts`

```typescript
// 初期化処理
const themeStore = useThemeStore()
themeStore.initTheme()

const authStore = useAuthStore()
await authStore.initAuth()

app.mount('#app')
```

**注意**: `main.ts`はトップレベルで`await`を使用できないため、以下のように修正する必要があります：

```typescript
// 初期化処理
const themeStore = useThemeStore()
themeStore.initTheme()

const authStore = useAuthStore()
authStore.initAuth().then(() => {
  app.mount('#app')
}).catch((error) => {
  console.error('Failed to initialize auth:', error)
  app.mount('#app')
})
```

#### ステップ4: ルーターガードで非同期処理を考慮

**ファイル**: `frontend/src/router/index.ts`

```typescript
router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore()
  
  // トークンが存在するが、ユーザー情報が取得されていない場合、取得を試みる
  if (authStore.token && !authStore.user) {
    try {
      await authStore.initAuth()
    } catch (error) {
      console.error('Failed to initialize auth:', error)
      // エラーが発生した場合、ログアウト
      authStore.logout()
    }
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    // 認証が必要なページに未認証でアクセスした場合
    next({
      name: 'AdminLogin',
      query: { redirect: to.fullPath }
    })
  } else if (to.name === 'AdminLogin' && authStore.isAuthenticated) {
    // 既に認証済みの場合はダッシュボードにリダイレクト
    next({ name: 'AdminDashboard' })
  } else {
    next()
  }
})
```

### 5.3 エラーハンドリング

#### 5.3.1 トークンが無効な場合

- 401エラーが返された場合、`logout()`を呼び出してログアウトする
- 既に`apiClient`のレスポンスインターセプターで401エラー時に`logout()`が呼ばれているため、追加の処理は不要

#### 5.3.2 ネットワークエラーの場合

- ネットワークエラーが発生した場合、ユーザー情報の取得に失敗する
- この場合、`isAuthenticated`が`false`になり、ログイン画面にリダイレクトされる
- これは期待される動作（ネットワークエラー時はログイン画面に戻る）

---

## 6. 確認項目

### 6.1 実装確認

- [ ] バックエンドに`/api/v1/auth/me`エンドポイントが追加されている
- [ ] フロントエンドの認証APIクライアントに`getCurrentUser`メソッドが追加されている
- [ ] 認証ストアの`initAuth`関数が修正されている
- [ ] `main.ts`で非同期処理が適切に処理されている
- [ ] ルーターガードで非同期処理が適切に処理されている

### 6.2 動作確認

- [ ] ログイン後、ページをリロードしてログイン状態が維持される
- [ ] ブラウザの戻るボタンでログイン画面に戻った際、ログイン状態が維持される
- [ ] ログアウト後、ログイン画面が表示される
- [ ] トークンが無効な場合、適切にログアウトされる
- [ ] ブラウザの開発者ツールでエラーがない
- [ ] ネットワークリクエストが正常に送信されている

### 6.3 テスト実行

- [ ] 関連するテストを実行
- [ ] すべてのテストがパスすることを確認

---

## 7. 大原則への準拠

### 7.1 根本解決 > 暫定解決

- ✅ **根本解決**: `initAuth()`でトークンからユーザー情報を取得するAPIを呼び出す
- ✅ トークンの有効性をバックエンドで確認し、ユーザー情報を取得する

### 7.2 シンプル構造 > 複雑構造

- ✅ **シンプル構造**: 既存の`get_current_user`を使用して新しいエンドポイントを作成
- ✅ 既存のパターンに従い、統一された実装

### 7.3 統一・同一化 > 特殊独自

- ✅ **統一・同一化**: 既存の認証パターンに従い、`get_current_user`を使用
- ✅ 他のエンドポイントと同じパターンで実装

### 7.4 具体的 > 一般

- ✅ **具体的**: 具体的な実装手順を明確にする
- ✅ コード例を提示

### 7.5 拙速 < 安全確実

- ✅ **安全確実**: バックエンドでトークンの有効性を確認し、ユーザー情報を取得する
- ✅ エラーハンドリングを適切に実装

---

## 8. まとめ

### 8.1 根本原因

1. `initAuth()`が`localStorage`からトークンを読み込むだけで、ユーザー情報を取得していない
2. `isAuthenticated`は`!!token.value && !!user.value`で判定されるため、`user.value`が`null`の場合、`isAuthenticated`が`false`になる
3. バックエンドには、現在のユーザー情報を取得するエンドポイントが存在しない

### 8.2 推奨修正案

**オプション1: バックエンドAPIエンドポイント追加（推奨）**

1. バックエンドに`/api/v1/auth/me`エンドポイントを追加
2. フロントエンドの認証APIクライアントに`getCurrentUser`メソッドを追加
3. 認証ストアの`initAuth`関数を修正（非同期関数に変更）
4. `main.ts`で非同期処理を適切に処理
5. ルーターガードで非同期処理を考慮

### 8.3 実装手順

1. **バックエンド修正**:
   - `backend/app/api/v1/auth.py`に`/me`エンドポイントを追加

2. **フロントエンド修正**:
   - `frontend/src/api/auth.ts`に`getCurrentUser`メソッドを追加
   - `frontend/src/stores/auth.ts`の`initAuth`関数を修正
   - `frontend/src/main.ts`で非同期処理を適切に処理
   - `frontend/src/router/index.ts`で非同期処理を考慮

### 8.4 期待される効果

- ✅ ログイン後、ページをリロードしてもログイン状態が維持される
- ✅ ブラウザの戻るボタンでログイン画面に戻った際、ログイン状態が維持される
- ✅ トークンが無効な場合、適切にログアウトされる
- ✅ ユーザー体験が向上する

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ✅ **完全調査分析完了、修正案提示完了**


