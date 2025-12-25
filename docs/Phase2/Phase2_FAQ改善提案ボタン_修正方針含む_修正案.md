# Phase 2: FAQ改善提案ボタン 修正方針含む 修正案

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: FAQ改善提案ボタンの動作問題の修正方針と修正案  
**状態**: ✅ **修正方針検討完了 → 修正案提示**

---

## 1. 修正方針

### 1.1 方針の概要

**目的**: 同じ表示同じ動作の重複を排除し、シンプルにする

**内容**:
- ダッシュボードページの「FAQ改善提案」「無視」ボタンを削除
- 「対応する」ボタンを追加し、FAQ管理ページ（`/admin/faqs`）にジャンプするだけ
- これにより、重複を排除し、シンプルになる

**理由**:
- 同じ機能が2箇所に存在するのは無駄
- ダッシュボードページでは概要を表示し、詳細な操作はFAQ管理ページで行う方が自然
- シンプル構造 > 複雑構造（大原則に準拠）

---

## 2. 問題の調査分析結果

### 2.1 質問が「Question」になっている問題

**症状**:
- 低評価回答リストで「Q: Question」と表示される
- 実際の質問が表示されない

**調査結果**:
- データベースには質問が存在する（message_id=27: "アイロンは貸し出ししてますか？"、message_id=31: "ドリンカブルな水はありますか？"）
- `feedback_service.py`の実装では、会話履歴から質問を取得するロジックがある
- しかし、`dashboard_service.py`の古い実装では`question = "Question"`というハードコードされた値が使われている

**原因**:
- ダッシュボードページは`dashboard_service.py`の`get_feedback_stats`メソッドを使用
- このメソッドでは、質問の取得が不完全（`question = "Question"`というTODOがある）
- FAQページは`feedback_service.py`の`get_negative_feedbacks`メソッドを使用
- このメソッドでは、会話履歴から質問を正しく取得するロジックがある

**解決方法**:
- `dashboard_service.py`の`get_feedback_stats`メソッドを修正し、`feedback_service.py`と同じロジックを使用する
- または、`dashboard_service.py`から`feedback_service.py`の`get_negative_feedbacks`メソッドを呼び出す

---

## 3. 修正案（大原則に準拠）

### 3.1 修正案1: ダッシュボードページのUIをシンプルにする

**目的**: 同じ表示同じ動作の重複を排除し、シンプルにする

**実施内容**:
1. `FeedbackStats.vue`コンポーネントから「FAQ改善提案」「無視」ボタンを削除
2. 「対応する」ボタンを追加
3. 「対応する」ボタンをクリックすると、FAQ管理ページ（`/admin/faqs`）にジャンプする
4. `Dashboard.vue`から`handleFeedbackImprove`と`handleFeedbackIgnore`関数を削除（不要になる）

**ファイル**: `frontend/src/components/admin/FeedbackStats.vue`

**変更内容**:
```vue
<div class="flex items-center space-x-2 mt-3">
  <button
    @click="handleRespond"
    class="px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
  >
    対応する
  </button>
</div>
```

**スクリプト部分**:
```typescript
import { useRouter } from 'vue-router'

const router = useRouter()

const emit = defineEmits<{
  respond: [answer: FeedbackStats['low_rated_answers'][0]]
}>()

const handleRespond = (answer: FeedbackStats['low_rated_answers'][0]) => {
  // FAQ管理ページにジャンプ
  router.push('/admin/faqs')
  // 親コンポーネントに通知（必要に応じて）
  emit('respond', answer)
}
```

**ファイル**: `frontend/src/views/admin/Dashboard.vue`

**変更内容**:
```typescript
// handleFeedbackImproveとhandleFeedbackIgnore関数を削除（不要になる）
// @improveと@ignoreイベントハンドラーを削除
```

**テンプレート部分**:
```vue
<FeedbackStats
  :stats="feedbackStats"
  @respond="handleFeedbackRespond"
/>
```

**スクリプト部分**:
```typescript
const handleFeedbackRespond = (answer: FeedbackStatsType['low_rated_answers'][0]) => {
  // FAQ管理ページにジャンプ（FeedbackStatsコンポーネント内で既に処理されている）
  // 必要に応じて、追加の処理をここに記述
  console.log('Navigate to FAQ management page for:', answer)
}
```

---

### 3.2 修正案2: `FaqSuggestionCard`コンポーネントに「キャンセル」ボタンを追加

**目的**: ユーザーが提案を簡単に閉じることができるようにする

**実施内容**:
1. `FaqSuggestionCard`コンポーネントに「キャンセル」ボタンを追加
2. `cancel`イベントをemitする処理を追加

**ファイル**: `frontend/src/components/admin/FaqSuggestionCard.vue`

**変更内容**:
```typescript
// emit定義に追加
const emit = defineEmits<{
  approve: [suggestion: FaqSuggestion]
  reject: [suggestion: FaqSuggestion]
  cancel: []
}>()

// handleCancel関数を追加
const handleCancel = () => {
  emit('cancel')
}
```

**テンプレート部分**:
```vue
<div class="flex items-center justify-end space-x-3 mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
  <button
    @click="handleCancel"
    class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
  >
    キャンセル
  </button>
  <button
    @click="handleReject"
    :disabled="loading || suggestion.status !== 'pending'"
    class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
  >
    {{ loading ? '処理中...' : '却下' }}
  </button>
  <button
    @click="handleApprove"
    :disabled="loading || suggestion.status !== 'pending'"
    class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
  >
    {{ loading ? '処理中...' : '承認してFAQ追加' }}
  </button>
</div>
```

---

### 3.3 修正案3: `FaqManagement.vue`で`cancel`イベントをハンドル

**目的**: FAQページでキャンセルボタンが正常に動作するようにする

**実施内容**:
1. `FaqManagement.vue`で`handleCancelSuggestion`関数を実装
2. `FaqSuggestionCard`コンポーネントに`@cancel`イベントハンドラーを追加

**ファイル**: `frontend/src/views/admin/FaqManagement.vue`

**変更内容**:
```typescript
// handleCancelSuggestion関数を追加
const handleCancelSuggestion = () => {
  selectedSuggestion.value = null
}
```

**テンプレート部分**:
```vue
<FaqSuggestionCard
  :suggestion="selectedSuggestion"
  @approve="handleApproveSuggestion"
  @reject="handleRejectSuggestion"
  @cancel="handleCancelSuggestion"
/>
```

---

### 3.4 修正案4: `dashboard_service.py`の質問取得ロジックを修正

**目的**: ダッシュボードページで質問が正しく表示されるようにする

**実施内容**:
1. `dashboard_service.py`の`get_feedback_stats`メソッドを修正
2. `feedback_service.py`の`get_negative_feedbacks`メソッドと同じロジックを使用する
3. または、`dashboard_service.py`から`feedback_service.py`の`get_negative_feedbacks`メソッドを呼び出す

**ファイル**: `backend/app/services/dashboard_service.py`

**変更内容（方法1: 同じロジックを実装）**:
```python
# 既存のロジックを修正
for message in messages:
    # 会話内のメッセージを取得（質問を取得するため）
    conversation_messages_result = await self.db.execute(
        select(Message)
        .where(Message.conversation_id == message.conversation_id)
        .order_by(Message.created_at.asc())
    )
    conversation_messages = conversation_messages_result.scalars().all()
    
    # このメッセージ（AI応答）の前にあるユーザーメッセージ（質問）を取得
    question = None
    for msg in reversed(conversation_messages):
        if msg.id == message.id:
            break
        if msg.role == MessageRole.USER.value:
            question = msg.content
            break
    
    # 質問が見つからない場合はデフォルト値を設定
    if not question:
        question = "質問が見つかりませんでした"
    
    # 回答はメッセージの内容（200文字まで）
    answer = message.content[:200] if len(message.content) > 200 else message.content
    
    low_rated_answers.append(LowRatedAnswer(
        message_id=message.id,
        question=question,
        answer=answer,
        negative_count=message_negative_count[message.id]
    ))
```

**変更内容（方法2: feedback_serviceを使用）**:
```python
from app.services.feedback_service import FeedbackService

# get_feedback_statsメソッド内で
feedback_service = FeedbackService(self.db)
low_rated_answers = await feedback_service.get_negative_feedbacks(facility_id)
```

**推奨**: 方法2（`feedback_service`を使用）を推奨
- 重複を排除できる
- メンテナンスが容易
- 統一・同一化 > 特殊独自（大原則に準拠）

---

## 4. 大原則への準拠確認

### 4.1 根本解決 > 暫定解決

**評価**: ✅ **準拠**

**理由**:
- 重複を排除し、シンプルな構造にする（根本解決）
- 質問取得ロジックを正しく実装する（根本解決）

### 4.2 シンプル構造 > 複雑構造

**評価**: ✅ **準拠**

**理由**:
- 同じ機能を2箇所に実装するのではなく、1箇所に集約する（シンプル）
- ダッシュボードページでは「対応する」ボタンでFAQ管理ページにジャンプするだけ（シンプル）

### 4.3 統一・同一化 > 特殊独自

**評価**: ✅ **準拠**

**理由**:
- `feedback_service.py`のロジックを`dashboard_service.py`でも使用する（統一）
- 既存の実装パターンに従う（統一）

### 4.4 具体的 > 一般

**評価**: ✅ **準拠**

**理由**:
- 具体的なボタンを追加する
- 具体的な関数を実装する

### 4.5 拙速 < 安全確実

**評価**: ✅ **準拠**

**理由**:
- バックアップを作成してから実装
- 既存の実装パターンに従う（安全）
- 十分な検証を行う

**総合評価**: ✅ **大原則に完全準拠**

---

## 5. 修正案の詳細

### 5.1 修正案1: ダッシュボードページのUIをシンプルにする

**ファイル**: `frontend/src/components/admin/FeedbackStats.vue`

**実施内容**:
1. 「FAQ改善提案」「無視」ボタンを削除
2. 「対応する」ボタンを追加
3. `useRouter`を使用してFAQ管理ページにジャンプ
4. `respond`イベントをemit（必要に応じて）

### 5.2 修正案2: `FaqSuggestionCard`コンポーネントに「キャンセル」ボタンを追加

**ファイル**: `frontend/src/components/admin/FaqSuggestionCard.vue`

**実施内容**:
1. `cancel`イベントをemit定義に追加
2. `handleCancel`関数を追加
3. 「キャンセル」ボタンを追加（「却下」ボタンの前に配置）

### 5.3 修正案3: `FaqManagement.vue`で`cancel`イベントをハンドル

**ファイル**: `frontend/src/views/admin/FaqManagement.vue`

**実施内容**:
1. `handleCancelSuggestion`関数を追加
2. `FaqSuggestionCard`コンポーネントに`@cancel`イベントハンドラーを追加

### 5.4 修正案4: `dashboard_service.py`の質問取得ロジックを修正

**ファイル**: `backend/app/services/dashboard_service.py`

**実施内容**:
1. `feedback_service.py`の`get_negative_feedbacks`メソッドを使用するように修正
2. または、同じロジックを実装

**推奨**: `feedback_service.py`を使用する方法を推奨（重複を排除できる）

---

## 6. まとめ

### 6.1 修正方針

- ダッシュボードページの「FAQ改善提案」「無視」ボタンを削除
- 「対応する」ボタンを追加し、FAQ管理ページにジャンプするだけ
- これにより、重複を排除し、シンプルになる

### 6.2 修正案

**修正案1**: ダッシュボードページのUIをシンプルにする
**修正案2**: `FaqSuggestionCard`コンポーネントに「キャンセル」ボタンを追加
**修正案3**: `FaqManagement.vue`で`cancel`イベントをハンドル
**修正案4**: `dashboard_service.py`の質問取得ロジックを修正

### 6.3 大原則への準拠

✅ **すべての修正案は大原則に完全準拠**

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ✅ **修正方針検討完了 → 修正案提示完了**


