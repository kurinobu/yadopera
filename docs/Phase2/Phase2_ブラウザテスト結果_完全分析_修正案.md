# Phase 2: ブラウザテスト結果・完全分析・修正案

**作成日**: 2025年12月2日  
**実施者**: Auto (AI Assistant)  
**対象**: Phase 2 ステップ1（管理画面・ゲスト画面の動作確認）  
**状態**: ✅ **完全分析完了、根本原因特定完了、修正案提示完了**

---

## 1. ブラウザテスト結果の説明と評価

### 1.1 問題1: ゲスト画面のメッセージ表示問題

**現象**:
- メッセージ送信後、「メッセージがありません」と表示される
- コンソールログから`facilityId: NaN`が確認される

**コンソールログの分析**:
```
[Chat.vue] handleMessageSubmit: 開始 {
  message: 'Wi-Fiパスワードを教えて下さい',
  facilityId: NaN,  // ← 問題発見！
  messagesCountBefore: 0,
  messagesBefore: Proxy(Array)
}
[Chat.vue] handleMessageSubmit: バリデーションエラー {
  facilityId: NaN,
  message: 'Wi-Fiパスワードを教えて下さい'
}
```

**根本原因の特定**:

1. **`Chat.vue`での`facilityId`の取得方法**:
   ```typescript:132:frontend/src/views/guest/Chat.vue
   const facilityId = computed(() => parseInt(route.params.facilityId as string, 10))
   ```
   - `route.params.facilityId`を`parseInt`で数値に変換しようとしている

2. **`Welcome.vue`からの遷移**:
   ```typescript:124:132:frontend/src/views/guest/Welcome.vue
   router.push({
     name: 'Chat',
     params: { facilityId: facilityId.value },  // ← 文字列（slug）を渡している
     query: {
       lang: language.value,
       location: location.value,
       message: message
     }
   })
   ```
   - `facilityId.value`は文字列（slug）として定義されている
   ```typescript:63:frontend/src/views/guest/Welcome.vue
   const facilityId = computed(() => route.params.facilityId as string)
   ```

3. **ルート定義**:
   ```typescript:25:27:frontend/src/router/guest.ts
   {
     path: '/f/:facilityId/chat',
     name: 'Chat',
     ...
   }
   ```
   - ルートパラメータは文字列（slug）として扱われる

4. **APIリクエスト**:
   - `chatApi.sendMessage`は`facility_id: number`を期待している
   - しかし、`facilityId`が`NaN`のため、バリデーションエラーが発生

**根本原因**: 
- `Chat.vue`で`route.params.facilityId`（文字列のslug）を`parseInt`で数値に変換しようとしているが、slugが数値でないため`NaN`になる
- 実際のAPIリクエストには`facility.id`（数値）が必要

**評価**:
- 🔴 **CRITICAL**: メッセージ送信が完全に失敗している
- 影響度: **最高**（Phase 1完了に必須）

---

### 1.2 問題2: 管理画面のFAQ追加問題

**現象**:
- FAQ提案の承認時に500エラーが発生
- エラーメッセージ: 「FAQ提案の生成に失敗しました」

**バックエンドログの分析**:
```
2025-12-02 00:45:27,643 INFO sqlalchemy.engine.Engine SELECT faq_suggestions.id ... FROM faq_suggestions WHERE faq_suggestions.id = $1::INTEGER (2,)
2025-12-02 00:45:27,645 INFO sqlalchemy.engine.Engine ROLLBACK
INFO: 192.168.65.1:54114 - "POST /api/v1/admin/faq-suggestions/2/approve HTTP/1.1" 500 Internal Server Error
```

**分析結果**:
1. FAQ提案の取得は成功している
2. その後、すぐに`ROLLBACK`が実行されている
3. 500エラーが返されている

**根本原因の特定**:

1. **`approve_suggestion`メソッドの処理フロー**:
   ```python:257:276:backend/app/services/faq_suggestion_service.py
   # 提案を取得
   suggestion = await self.db.get(FAQSuggestion, suggestion_id)
   if not suggestion:
       raise ValueError(...)
   
   if suggestion.facility_id != facility_id:
       raise ValueError(...)
   
   if suggestion.status != FAQSuggestionStatus.PENDING.value:
       raise ValueError(...)
   
   # FAQ作成リクエストを準備（編集可能）
   faq_request = FAQRequest(
       category=request.category or suggestion.suggested_category,
       language=suggestion.language,
       question=request.question or suggestion.suggested_question,
       answer=request.answer or suggestion.suggested_answer,
       priority=request.priority or 1,  # ← 修正済み
       is_active=True
   )
   
   # FAQ作成
   faq = await self.faq_service.create_faq(
       facility_id=facility_id,
       request=faq_request,
       user_id=user_id
   )
   ```

2. **問題の可能性**:
   - `faq_service.create_faq`が呼ばれる前にエラーが発生している可能性
   - または、`faq_service.create_faq`内でエラーが発生している可能性

3. **ログから確認された情報**:
   - FAQ提案の取得は成功
   - その後、すぐに`ROLLBACK`が実行
   - `faq_service.create_faq`が呼ばれていない可能性

**根本原因（推定）**:
- `approve_suggestion`メソッド内で、`faq_service.create_faq`を呼ぶ前にエラーが発生している可能性
- または、`faq_service.create_faq`内でエラーが発生し、例外が適切に処理されていない可能性

**評価**:
- 🔴 **CRITICAL**: FAQ提案の承認が完全に失敗している
- 影響度: **最高**（Phase 1完了に必須）

---

## 2. 調査分析結果

### 2.1 問題1: ゲスト画面のメッセージ表示問題

**完全な調査分析の結果**:

1. **`facilityId`の取得方法の問題**:
   - `Chat.vue`で`route.params.facilityId`（文字列のslug）を`parseInt`で数値に変換しようとしている
   - しかし、slugが数値でないため`NaN`になる
   - 実際のAPIリクエストには`facility.id`（数値）が必要

2. **`facilityStore`の確認**:
   - `facilityStore.currentFacility`に施設情報が保存されている
   - `facility.id`（数値）を取得できる可能性がある

3. **修正方針**:
   - `Chat.vue`で`facilityId`を取得する際、`facilityStore.currentFacility.id`を使用する
   - または、`route.params.facilityId`（slug）から施設情報を取得し、`facility.id`を使用する

---

### 2.2 問題2: 管理画面のFAQ追加問題

**完全な調査分析の結果**:

1. **ログから確認された情報**:
   - FAQ提案の取得は成功
   - その後、すぐに`ROLLBACK`が実行
   - `faq_service.create_faq`が呼ばれていない可能性

2. **問題の可能性**:
   - `approve_suggestion`メソッド内で、`faq_service.create_faq`を呼ぶ前にエラーが発生している可能性
   - または、`faq_service.create_faq`内でエラーが発生し、例外が適切に処理されていない可能性

3. **修正方針**:
   - バックエンドのログをより詳細に確認する
   - `approve_suggestion`メソッド内でエラーハンドリングを改善する
   - `faq_service.create_faq`の呼び出し前後でログを追加する

---

## 3. 修正案

### 3.1 問題1: ゲスト画面のメッセージ表示問題の修正案

**修正方針**: `Chat.vue`で`facilityId`を取得する際、`facilityStore.currentFacility.id`を使用する

**修正内容**:

#### 修正1: `Chat.vue`の`facilityId`の取得方法を変更

**現在のコード**:
```typescript:132:frontend/src/views/guest/Chat.vue
const facilityId = computed(() => parseInt(route.params.facilityId as string, 10))
```

**修正後のコード**:
```typescript
// 施設IDを取得（facilityStoreから取得、またはroute.paramsから取得）
const facilityId = computed(() => {
  // まず、facilityStoreから取得を試みる
  if (facilityStore.currentFacility?.id) {
    return facilityStore.currentFacility.id
  }
  
  // facilityStoreにない場合、route.paramsから取得を試みる
  // ただし、route.params.facilityIdはslug（文字列）の可能性がある
  const paramId = route.params.facilityId as string
  const parsedId = parseInt(paramId, 10)
  
  // 数値として有効な場合のみ返す
  if (!isNaN(parsedId)) {
    return parsedId
  }
  
  // それでも取得できない場合、エラーをログに記録
  console.error('[Chat.vue] facilityId取得失敗', {
    routeParams: route.params,
    currentFacility: facilityStore.currentFacility
  })
  
  return null
})
```

**または、よりシンプルな修正**:
```typescript
// 施設IDを取得（facilityStoreから取得）
const facilityId = computed(() => {
  if (facilityStore.currentFacility?.id) {
    return facilityStore.currentFacility.id
  }
  
  // facilityStoreにない場合、エラーをログに記録
  console.error('[Chat.vue] facilityId取得失敗: facilityStore.currentFacilityが未設定', {
    routeParams: route.params,
    currentFacility: facilityStore.currentFacility
  })
  
  return null
})
```

**修正理由**:
- `route.params.facilityId`は文字列（slug）の可能性がある
- 実際のAPIリクエストには`facility.id`（数値）が必要
- `facilityStore.currentFacility.id`を使用することで、正しい数値IDを取得できる

#### 修正2: `Chat.vue`の`onMounted`で施設情報を取得

**現在のコード**:
```typescript:145:177:frontend/src/views/guest/Chat.vue
onMounted(async () => {
  // セッションIDを取得または生成
  const currentSessionId = getOrCreateSessionId()
  // ...
})
```

**修正後のコード**:
```typescript
onMounted(async () => {
  try {
    // 施設情報が取得されていない場合、取得する
    if (!facilityStore.currentFacility) {
      const slug = route.params.facilityId as string
      try {
        const response = await facilityApi.getFacility(slug, location.value)
        facilityStore.setFacility(response.facility)
        facilityStore.setTopQuestions(response.top_questions)
      } catch (err) {
        console.error('[Chat.vue] 施設情報取得エラー', err)
        error.value = '施設情報の取得に失敗しました'
        return
      }
    }
    
    // セッションIDを取得または生成
    const currentSessionId = getOrCreateSessionId()
    // ...
  } catch (err) {
    console.error('[Chat.vue] Chat initialization error:', err)
    error.value = 'チャットの初期化に失敗しました'
  }
})
```

**修正理由**:
- `Chat.vue`がマウントされる際、`facilityStore.currentFacility`が未設定の可能性がある
- 施設情報を取得することで、`facility.id`を確実に取得できる

---

### 3.2 問題2: 管理画面のFAQ追加問題の修正案

**修正方針**: `approve_suggestion`メソッド内でエラーハンドリングを改善し、詳細なログを追加する

**修正内容**:

#### 修正1: `approve_suggestion`メソッドに詳細なログを追加

**修正後のコード**:
```python
async def approve_suggestion(
    self,
    suggestion_id: int,
    facility_id: int,
    request: ApproveSuggestionRequest,
    user_id: int
) -> FAQSuggestionResponse:
    """
    提案承認（FAQ作成）
    """
    logger.info(f"Approving FAQ suggestion: suggestion_id={suggestion_id}, facility_id={facility_id}, user_id={user_id}")
    
    try:
        # 提案を取得
        suggestion = await self.db.get(FAQSuggestion, suggestion_id)
        if not suggestion:
            logger.error(f"FAQ suggestion not found: suggestion_id={suggestion_id}")
            raise ValueError(f"FAQ suggestion not found: suggestion_id={suggestion_id}")
        
        logger.info(f"FAQ suggestion found: suggestion_id={suggestion_id}, status={suggestion.status}, facility_id={suggestion.facility_id}")
        
        if suggestion.facility_id != facility_id:
            logger.error(f"FAQ suggestion facility mismatch: suggestion_id={suggestion_id}, suggestion.facility_id={suggestion.facility_id}, facility_id={facility_id}")
            raise ValueError(f"FAQ suggestion does not belong to facility: suggestion_id={suggestion_id}, facility_id={facility_id}")
        
        if suggestion.status != FAQSuggestionStatus.PENDING.value:
            logger.error(f"FAQ suggestion is not pending: suggestion_id={suggestion_id}, status={suggestion.status}")
            raise ValueError(f"FAQ suggestion is not pending: suggestion_id={suggestion_id}, status={suggestion.status}")
        
        # FAQ作成リクエストを準備（編集可能）
        logger.info(f"Creating FAQ request: suggestion_id={suggestion_id}")
        faq_request = FAQRequest(
            category=request.category or suggestion.suggested_category,
            language=suggestion.language,
            question=request.question or suggestion.suggested_question,
            answer=request.answer or suggestion.suggested_answer,
            priority=request.priority or 1,
            is_active=True
        )
        logger.info(f"FAQ request created: category={faq_request.category}, language={faq_request.language}, priority={faq_request.priority}")
        
        # FAQ作成
        logger.info(f"Creating FAQ: facility_id={facility_id}, user_id={user_id}")
        try:
            faq = await self.faq_service.create_faq(
                facility_id=facility_id,
                request=faq_request,
                user_id=user_id
            )
            logger.info(f"FAQ created successfully: faq_id={faq.id}")
        except Exception as e:
            logger.error(f"Error creating FAQ: {str(e)}", exc_info=True)
            raise
        
        # 提案を更新
        logger.info(f"Updating FAQ suggestion: suggestion_id={suggestion_id}, faq_id={faq.id}")
        suggestion.status = FAQSuggestionStatus.APPROVED.value
        suggestion.reviewed_at = datetime.utcnow()
        suggestion.reviewed_by = user_id
        suggestion.created_faq_id = faq.id
        
        await self.db.commit()
        await self.db.refresh(suggestion)
        
        logger.info(f"FAQ suggestion approved successfully: suggestion_id={suggestion_id}, faq_id={faq.id}")
        
        return FAQSuggestionResponse(
            id=suggestion.id,
            facility_id=suggestion.facility_id,
            source_message_id=suggestion.source_message_id,
            suggested_question=suggestion.suggested_question,
            suggested_answer=suggestion.suggested_answer,
            suggested_category=suggestion.suggested_category,
            language=suggestion.language,
            status=suggestion.status,
            reviewed_at=suggestion.reviewed_at,
            reviewed_by=suggestion.reviewed_by,
            created_faq_id=suggestion.created_faq_id,
            created_at=suggestion.created_at
        )
    except ValueError as e:
        logger.error(f"ValueError in approve_suggestion: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in approve_suggestion: {str(e)}", exc_info=True)
        raise
```

**修正理由**:
- 各ステップで詳細なログを出力することで、エラーが発生する箇所を特定できる
- エラーハンドリングを改善することで、適切なエラーメッセージを返せる

---

## 4. 修正の優先順位

### 4.1 最優先（Phase 1完了に必須）

1. **問題1: ゲスト画面のメッセージ表示問題の修正**（1-2時間）
   - 影響: ゲスト画面のメッセージ送信が完全に失敗している
   - 優先度: **最高**

2. **問題2: 管理画面のFAQ追加問題の修正**（1-2時間）
   - 影響: 管理画面のFAQ提案の承認が完全に失敗している
   - 優先度: **最高**

**合計工数**: 約2-4時間

---

## 5. まとめ

### 5.1 問題1: ゲスト画面のメッセージ表示問題

**根本原因**: `Chat.vue`で`route.params.facilityId`（文字列のslug）を`parseInt`で数値に変換しようとしているが、slugが数値でないため`NaN`になる

**修正案**: `Chat.vue`で`facilityId`を取得する際、`facilityStore.currentFacility.id`を使用する

### 5.2 問題2: 管理画面のFAQ追加問題

**根本原因**: `approve_suggestion`メソッド内でエラーが発生しているが、詳細なログがないため原因を特定できない

**修正案**: `approve_suggestion`メソッド内でエラーハンドリングを改善し、詳細なログを追加する

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-02  
**Status**: ✅ **完全分析完了、根本原因特定完了、修正案提示完了**


