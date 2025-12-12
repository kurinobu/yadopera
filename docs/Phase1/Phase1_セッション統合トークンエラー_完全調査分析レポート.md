# Phase 1: セッション統合トークンエラー 完全調査分析レポート

**作成日**: 2025年12月3日  
**実施者**: Auto (AI Assistant)  
**対象**: セッション統合トークン取得時の404エラーハンドリング問題  
**状態**: ⚠️ **根本原因特定完了（修正は実施しません）**

---

## 1. エラー結果の説明と評価

### 1.1 エラーログの確認

**エラーログ**:
```
GET http://localhost:8000/api/v1/session/session/37dee6e7-1df1-4226-aa5a-06fbf3ba5b64/token 404 (Not Found)
[Chat.vue] onMounted: トークン取得エラー 
{code: 'NOT_FOUND', message: 'Token not found for this session', details: {…}}
```

### 1.2 エラーの説明

**発生したエラー**:
1. **HTTPステータス**: 404 (Not Found)
2. **エラーコード**: `NOT_FOUND`
3. **エラーメッセージ**: `Token not found for this session`
4. **発生箇所**: `Chat.vue`の`onMounted`内のトークン取得処理

**エラーの意味**:
- セッションID `37dee6e7-1df1-4226-aa5a-06fbf3ba5b64`に関連する既存のトークンが存在しない
- これは**正常な動作**（新規セッションの場合、トークンが存在しないのは正常）
- しかし、404エラーの場合に新規生成する処理が実行されていない

### 1.3 エラーの評価

**問題の評価**:
- 🔴 **高**: トークンが表示されない（機能が動作しない）
- ⚠️ **中**: エラーハンドリングのロジックに問題がある
- ✅ **低**: チャット機能自体は継続できる（エラーハンドリングで保護されている）

**影響範囲**:
- セッション統合トークンが表示されない
- ユーザーが他のデバイスでセッションを統合できない

---

## 2. 完全調査分析

### 2.1 エラーハンドリングの流れ

**エラーハンドリングの流れ**:

1. **APIリクエスト**: `sessionApi.getTokenBySessionId(currentSessionId)`
2. **バックエンド**: 404エラーを返す（トークンが存在しない）
3. **Axiosインターセプター**: `handleApiError`でエラーを`AppError`形式に変換
4. **Chat.vue**: `err?.response?.status === 404`でチェック
5. **問題**: `AppError`形式のエラーには`response.status`が存在しない

### 2.2 コード調査結果

#### 2.2.1 Axiosインターセプターの実装

**ファイル**: `frontend/src/api/axios.ts`

**実装コード**:

```47:61:frontend/src/api/axios.ts
  async (error: AxiosError) => {
    const authStore = useAuthStore()

    if (error.response) {
      const { status } = error.response

      // 401 Unauthorized: トークン無効または期限切れ
      if (status === 401) {
        authStore.logout()
        // TODO: ログイン画面にリダイレクト（Week 4で実装）
      }

      // エラーを処理して返す
      const appError = handleApiError(error)
      return Promise.reject(appError)
    }
```

**確認事項**:
- ✅ Axiosエラーを`handleApiError`で処理している
- ✅ `AppError`形式（`{code, message, details}`）に変換している
- ❌ 変換後のエラーには`response.status`が存在しない

#### 2.2.2 エラーハンドラーの実装

**ファイル**: `frontend/src/utils/errorHandler.ts`

**実装コード**:

```44:48:frontend/src/utils/errorHandler.ts
      case 404:
        return {
          code: 'NOT_FOUND',
          message: 'リソースが見つかりません。'
        }
```

**確認事項**:
- ✅ 404エラーを`NOT_FOUND`コードに変換している
- ✅ `AppError`形式（`{code, message, details}`）を返している
- ❌ `response.status`は含まれていない

#### 2.2.3 Chat.vueのエラーハンドリング

**ファイル**: `frontend/src/views/guest/Chat.vue`

**実装コード**:

```238:259:frontend/src/views/guest/Chat.vue
        } catch (err: any) {
          // 404エラー（トークンが存在しない）の場合は新規生成
          if (err?.response?.status === 404) {
            console.log('[Chat.vue] onMounted: 既存トークンなし - 新規生成', {
              sessionId: currentSessionId,
              facilityId: facilityId.value
            })
            const newToken = await sessionApi.generateToken({
              facility_id: facilityId.value,
              session_id: currentSessionId
            })
            console.log('[Chat.vue] onMounted: トークン生成成功', {
              token: newToken.token,
              expiresAt: newToken.expires_at
            })
            chatStore.setSessionToken(newToken.token)
            tokenExpiresAt.value = newToken.expires_at
          } else {
            // その他のエラーはログに記録するが、チャット機能は継続できる
            console.error('[Chat.vue] onMounted: トークン取得エラー', err)
          }
        }
```

**確認事項**:
- ❌ `err?.response?.status === 404`でチェックしている
- ❌ しかし、`AppError`形式のエラーには`response.status`が存在しない
- ❌ そのため、404エラーの場合でも`else`節で処理されている

### 2.3 根本原因の特定

**根本原因**: エラーハンドリングのロジックがAxiosインターセプターのエラー変換と一致していない

**詳細**:
1. **Axiosインターセプター**: エラーを`AppError`形式（`{code, message, details}`）に変換している
2. **Chat.vue**: `err?.response?.status === 404`でチェックしている
3. **問題**: `AppError`形式のエラーには`response.status`が存在しないため、404チェックが失敗している
4. **結果**: 404エラーの場合でも新規生成の処理が実行されず、`else`節で「トークン取得エラー」として処理されている

**エラーログの確認**:
- `{code: 'NOT_FOUND', message: 'Token not found for this session', details: {…}}`
- `code`が`'NOT_FOUND'`になっている
- `response.status`は存在しない

---

## 3. 修正案

### 3.1 修正方針

**目的**: エラーハンドリングのロジックをAxiosインターセプターのエラー変換と一致させる

**修正方針**:
1. **オプション1**: `err?.code === 'NOT_FOUND'`でチェックする（推奨）
2. **オプション2**: 両方をチェックする（`err?.code === 'NOT_FOUND' || err?.response?.status === 404`）

### 3.2 修正案1: エラーコードでチェックする（推奨）

**修正内容**:
- `err?.response?.status === 404`の代わりに、`err?.code === 'NOT_FOUND'`を使用する

**メリット**:
- Axiosインターセプターのエラー変換と一致している
- シンプルで理解しやすい
- 既存のエラーハンドリングパターンに準拠している

**デメリット**:
- なし

**実装例**:

```typescript
// 修正前
if (err?.response?.status === 404) {
  // 新規生成処理
}

// 修正後
if (err?.code === 'NOT_FOUND') {
  // 新規生成処理
}
```

### 3.3 修正案2: 両方をチェックする

**修正内容**:
- `err?.code === 'NOT_FOUND' || err?.response?.status === 404`でチェックする

**メリット**:
- より安全（両方のケースに対応）
- 将来の変更に対応しやすい

**デメリット**:
- 少し複雑

**実装例**:

```typescript
// 修正後
if (err?.code === 'NOT_FOUND' || err?.response?.status === 404) {
  // 新規生成処理
}
```

### 3.4 推奨修正案

**推奨**: **修正案1（エラーコードでチェックする）**

**理由**:
1. **シンプル**: より理解しやすい
2. **一貫性**: Axiosインターセプターのエラー変換と一致している
3. **保守性**: 既存のエラーハンドリングパターンに準拠している

**実装コード**:

```typescript
} catch (err: any) {
  // 404エラー（トークンが存在しない）の場合は新規生成
  if (err?.code === 'NOT_FOUND') {
    console.log('[Chat.vue] onMounted: 既存トークンなし - 新規生成', {
      sessionId: currentSessionId,
      facilityId: facilityId.value
    })
    const newToken = await sessionApi.generateToken({
      facility_id: facilityId.value,
      session_id: currentSessionId
    })
    console.log('[Chat.vue] onMounted: トークン生成成功', {
      token: newToken.token,
      expiresAt: newToken.expires_at
    })
    chatStore.setSessionToken(newToken.token)
    tokenExpiresAt.value = newToken.expires_at
  } else {
    // その他のエラーはログに記録するが、チャット機能は継続できる
    console.error('[Chat.vue] onMounted: トークン取得エラー', err)
  }
}
```

---

## 4. 大原則準拠評価

### 4.1 大原則の確認

**実装・修正の大原則**:
1. **根本解決 > 暫定解決**: 一時的な回避策ではなく、根本原因を解決する
2. **シンプル構造 > 複雑構造**: 過度に複雑な実装を避け、理解しやすく保守しやすい構造を選択
3. **統一・同一化 > 特殊独自**: 既存のパターンや規約に従い、統一された実装を優先
4. **具体的 > 一般**: 抽象的な説明ではなく、具体的な実装方法や手順を明確にする
5. **拙速 < 安全確実**: 速度よりも安全性と確実性を優先

### 4.2 修正案の大原則準拠評価

**推奨修正案**: エラーコードでチェックする（`err?.code === 'NOT_FOUND'`）

**評価結果**:

1. **根本解決 > 暫定解決**: ✅ **完全準拠**
   - 問題の根本原因（エラーハンドリングのロジックがAxiosインターセプターのエラー変換と一致していない）を解決している
   - 一時的な回避策ではなく、設計レベルでの解決

2. **シンプル構造 > 複雑構造**: ✅ **完全準拠**
   - `err?.code === 'NOT_FOUND'`でチェックするシンプルな実装
   - 過度に複雑な実装を避けている

3. **統一・同一化 > 特殊独自**: ✅ **完全準拠**
   - Axiosインターセプターのエラー変換と一致している
   - 既存のエラーハンドリングパターンに準拠している

4. **具体的 > 一般**: ✅ **完全準拠**
   - 実装方法が明確で具体的
   - 実行可能な具体的な内容

5. **拙速 < 安全確実**: ✅ **完全準拠**
   - 既存のエラーハンドリングパターンを活用し、安全性を確保
   - エラーハンドリングが適切

**結論**: ✅ **大原則に完全準拠している**

---

## 5. 修正時の注意事項

### 5.1 他の箇所の確認

**確認が必要な箇所**:
- `Chat.vue`内の他の404エラーチェック（会話履歴取得など）

**確認結果**:
- `Chat.vue`の286行目: `if (err?.response?.status !== 404)` - こちらも修正が必要

**修正内容**:
- `err?.response?.status !== 404` → `err?.code !== 'NOT_FOUND'`

**実装コード**:

```typescript
// 修正前
if (err?.response?.status !== 404) {
  console.error('[Chat.vue] onMounted: 会話履歴読み込みエラー', err)
} else {
  console.log('[Chat.vue] onMounted: 会話履歴なし（404）- 正常', {
    messagesCount: messages.value.length,
    messages: messages.value
  })
}

// 修正後
if (err?.code !== 'NOT_FOUND') {
  console.error('[Chat.vue] onMounted: 会話履歴読み込みエラー', err)
} else {
  console.log('[Chat.vue] onMounted: 会話履歴なし（404）- 正常', {
    messagesCount: messages.value.length,
    messages: messages.value
  })
}
```

### 5.2 テスト項目

**確認項目**:
- [ ] 404エラーの場合、新規生成の処理が実行される
- [ ] トークンが正しく表示される
- [ ] その他のエラーの場合、適切にログに記録される
- [ ] チャット機能は継続できる

---

## 6. まとめ

### 6.1 問題の要約

**根本原因**: エラーハンドリングのロジックがAxiosインターセプターのエラー変換と一致していない

**詳細**:
- Axiosインターセプターがエラーを`AppError`形式（`{code, message, details}`）に変換している
- `Chat.vue`では`err?.response?.status === 404`でチェックしている
- `AppError`形式のエラーには`response.status`が存在しないため、404チェックが失敗している
- 結果として、404エラーの場合でも新規生成の処理が実行されない

### 6.2 修正方針

**推奨修正案**: エラーコードでチェックする（`err?.code === 'NOT_FOUND'`）

**理由**:
- Axiosインターセプターのエラー変換と一致している
- シンプルで理解しやすい
- 既存のエラーハンドリングパターンに準拠している
- 大原則に完全準拠している

### 6.3 次のステップ

**修正実施時の手順**:
1. `Chat.vue`の240行目: トークン取得エラーハンドリングを修正（`err?.code === 'NOT_FOUND'`）
2. `Chat.vue`の286行目: 会話履歴読み込みエラーハンドリングを修正（`err?.code !== 'NOT_FOUND'`）
3. 動作確認を実施
4. ブラウザテストを実施

**重要**: 修正は実施しません。ユーザーからの指示があるまで、調査分析と評価のみを行います。

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-03  
**Status**: ⚠️ **根本原因特定完了（修正は実施しません）**

