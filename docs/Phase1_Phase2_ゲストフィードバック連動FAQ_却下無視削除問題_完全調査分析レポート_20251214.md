# Phase 1・Phase 2: ゲストフィードバック連動FAQ 却下・無視削除問題 完全調査分析レポート

**作成日**: 2025年12月14日  
**実施者**: AI Assistant  
**対象**: ゲストフィードバック連動FAQの却下・無視削除問題とFAQ改善提案エラー  
**状態**: 🔍 **調査分析完了**

---

## 1. 問題の概要

### 1.1 報告された問題

**問題1**: 「ゲストフィードバック連動FAQ」を「却下」しても「無視」をクリックしても削除されず画面に残っている

**問題2**: その後「FAQ改善提案」ボタンをクリックすると「Error generating FAQ suggestion: Multiple rows were found when one or none was required」とモーダル表示される

**問題3**: モーダルのOKをクリックしても何も表示も動作も変化無し

---

## 2. データベースの実際の状態

### 2.1 FAQ提案データ（source_message_id 28, 32）

**source_message_id = 28**:
- **ID 1**: `status = "approved"`, `created_at = 2025-12-04 00:51:07`
- **ID 2**: `status = "rejected"`, `created_at = 2025-12-04 01:47:34`
- **ID 15**: `status = "pending"`, `created_at = 2025-12-14 03:19:46`
- **ID 16**: `status = "pending"`, `created_at = 2025-12-14 03:19:48`

**source_message_id = 32**:
- **ID 14**: `status = "rejected"`, `created_at = 2025-12-14 02:23:36`

### 2.2 問題の確認

**問題2の原因**: `source_message_id = 28`に対して、**複数の`pending`ステータスのFAQ提案が存在**（ID 15, 16）

---

## 3. 根本原因の分析

### 3.1 問題1: 「却下」しても「無視」をクリックしても削除されず画面に残っている

#### 3.1.1 「却下」ボタンの動作

**フロントエンド実装** (`FaqSuggestionCard.vue`):
```typescript
const handleReject = async () => {
  if (loading.value) return
  
  if (!confirm('この提案を却下しますか？')) {
    return
  }
  
  try {
    loading.value = true
    await faqSuggestionApi.rejectSuggestion(props.suggestion.id)
    emit('reject', props.suggestion)
  } catch (err: any) {
    console.error('Failed to reject suggestion:', err)
    alert(err.response?.data?.detail || '提案の却下に失敗しました')
  } finally {
    loading.value = false
  }
}
```

**親コンポーネントの処理** (`FaqManagement.vue`):
```typescript
const handleRejectSuggestion = async (_suggestion: FaqSuggestion) => {
  // API連携はFaqSuggestionCard内で実装済み
  // ここでは提案をクリア
  selectedSuggestion.value = null
}
```

**問題点**:
1. ✅ FAQ提案は却下される（バックエンドで`status = "rejected"`に更新される）
2. ❌ **低評価回答リスト（`lowRatedFaqs`）を再取得していない**
3. ❌ そのため、画面に低評価回答が残り続ける

#### 3.1.2 「無視」ボタンの動作

**フロントエンド実装** (`FaqManagement.vue`):
```typescript
const handleFeedbackIgnore = (answer: LowRatedAnswer) => {
  // TODO: Week 4でAPI連携を実装（ステップ4で実装予定）
  console.log('Feedback ignore:', answer)
}
```

**問題点**:
1. ❌ **実装されていない**（TODOコメントのみ）
2. ❌ 低評価回答を無視するAPIエンドポイントが存在しない
3. ❌ そのため、何も処理されず画面に残り続ける

#### 3.1.3 根本原因

**根本原因**: 
1. **「却下」**: FAQ提案を却下しても、低評価回答リストを再取得していない
2. **「無視」**: 実装されていない（TODOコメントのみ）

**詳細**:
- 低評価回答リストは`/admin/feedback/negative`エンドポイントから取得される
- このエンドポイントは、低評価が2回以上ついたメッセージを返す
- FAQ提案を却下しても、低評価フィードバック自体は削除されない
- そのため、低評価回答リストから削除されない

---

### 3.2 問題2: 「FAQ改善提案」ボタンをクリックすると「Multiple rows were found when one or none was required」エラー

#### 3.2.1 エラーの原因

**バックエンド実装** (`faq_suggestion_service.py`):
```python
# 既存の提案を確認
existing_result = await self.db.execute(
    select(FAQSuggestion).where(
        FAQSuggestion.source_message_id == message_id,
        FAQSuggestion.status == FAQSuggestionStatus.PENDING.value
    )
)
existing = existing_result.scalar_one_or_none()
```

**問題点**:
1. `source_message_id = 28`に対して、**複数の`pending`ステータスのFAQ提案が存在**（ID 15, 16）
2. `scalar_one_or_none()`は、1行または0行を期待しているが、複数の行が存在するためエラーが発生

#### 3.2.2 なぜ複数の`pending`ステータスのFAQ提案が存在するのか

**原因**:
1. ユーザーが「FAQ改善提案」ボタンを複数回クリックした
2. 既存の`pending`ステータスのFAQ提案を確認する処理があるが、**複数の`pending`ステータスのFAQ提案が存在する場合の処理がない**
3. そのため、同じ`message_id`に対して複数の`pending`ステータスのFAQ提案が作成される

**データベースの状態**:
- `source_message_id = 28`に対して、ID 15とID 16の2つの`pending`ステータスのFAQ提案が存在

#### 3.2.3 根本原因

**根本原因**: 
1. **既存の`pending`ステータスのFAQ提案を確認する処理が不十分**
   - `scalar_one_or_none()`を使用しているが、複数の行が存在する場合の処理がない
2. **重複チェックが不十分**
   - 同じ`message_id`に対して複数の`pending`ステータスのFAQ提案が作成されることを防いでいない

---

### 3.3 問題3: モーダルのOKをクリックしても何も表示も動作も変化無し

#### 3.3.1 エラーハンドリング

**フロントエンド実装** (`FaqManagement.vue`):
```typescript
const handleFeedbackImprove = async (answer: LowRatedAnswer) => {
  try {
    // FAQ提案を生成（GPT-4o mini）
    selectedSuggestion.value = await faqSuggestionApi.generateSuggestion(answer.message_id)
  } catch (err: any) {
    console.error('Failed to generate FAQ suggestion:', err)
    const errorMessage = err.response?.data?.detail || err.message || 'FAQ提案の生成に失敗しました'
    alert(errorMessage)
  }
}
```

**問題点**:
1. ✅ エラーメッセージは`alert`で表示される
2. ❌ **エラー後の処理がない**（`selectedSuggestion.value`が設定されない）
3. ❌ そのため、モーダルが表示されない（`selectedSuggestion.value`が`null`のまま）

#### 3.3.2 根本原因

**根本原因**: エラーハンドリングで`alert`を表示するだけで、エラー後の処理（リトライ、ログ出力、ユーザーへの案内など）がない

---

## 4. コードの確認

### 4.1 既存の提案を確認する処理

**ファイル**: `backend/app/services/faq_suggestion_service.py`

**現在の実装**（140-147行目）:
```python
# 既存の提案を確認
existing_result = await self.db.execute(
    select(FAQSuggestion).where(
        FAQSuggestion.source_message_id == message_id,
        FAQSuggestion.status == FAQSuggestionStatus.PENDING.value
    )
)
existing = existing_result.scalar_one_or_none()
```

**問題点**:
- `scalar_one_or_none()`は、1行または0行を期待しているが、複数の行が存在する場合にエラーが発生

### 4.2 低評価回答リストの取得

**ファイル**: `frontend/src/views/admin/FaqManagement.vue`

**現在の実装**（183-192行目）:
```typescript
const fetchLowRatedAnswers = async () => {
  try {
    const data = await feedbackApi.getNegativeFeedbacks()
    lowRatedAnswers.value = data
  } catch (err: any) {
    console.error('Failed to fetch low-rated answers:', err)
    // エラーは表示しない（低評価回答はオプション機能のため）
    lowRatedAnswers.value = []
  }
}
```

**問題点**:
- FAQ提案を却下した後、`fetchLowRatedAnswers()`を呼び出していない

### 4.3 「無視」ボタンの実装

**ファイル**: `frontend/src/views/admin/FaqManagement.vue`

**現在の実装**（428-431行目）:
```typescript
const handleFeedbackIgnore = (answer: LowRatedAnswer) => {
  // TODO: Week 4でAPI連携を実装（ステップ4で実装予定）
  console.log('Feedback ignore:', answer)
}
```

**問題点**:
- 実装されていない（TODOコメントのみ）

---

## 5. 問題の整理

### 5.1 問題1: 「却下」しても「無視」をクリックしても削除されず画面に残っている

**症状**: 
- 「却下」ボタンをクリックしても、低評価回答が画面に残る
- 「無視」ボタンをクリックしても、低評価回答が画面に残る

**原因**:
1. **「却下」**: FAQ提案は却下されるが、低評価回答リストを再取得していない
2. **「無視」**: 実装されていない（TODOコメントのみ）

**解決方法**:
1. **「却下」**: FAQ提案を却下した後、`fetchLowRatedAnswers()`を呼び出して低評価回答リストを再取得
2. **「無視」**: 低評価回答を無視する機能を実装（APIエンドポイントの追加が必要）

### 5.2 問題2: 「FAQ改善提案」ボタンをクリックすると「Multiple rows were found when one or none was required」エラー

**症状**: 
- 「FAQ改善提案」ボタンをクリックすると、エラーモーダルが表示される
- エラーメッセージ: "Error generating FAQ suggestion: Multiple rows were found when one or none was required"

**原因**:
1. `source_message_id = 28`に対して、複数の`pending`ステータスのFAQ提案が存在（ID 15, 16）
2. `scalar_one_or_none()`が複数の行を返したためエラーが発生

**解決方法**:
1. **既存の`pending`ステータスのFAQ提案を確認する処理を修正**
   - `scalar_one_or_none()`の代わりに、最新の1件を取得する処理に変更
   - または、複数の`pending`ステータスのFAQ提案が存在する場合、古いものを`rejected`に更新

### 5.3 問題3: モーダルのOKをクリックしても何も表示も動作も変化無し

**症状**: 
- エラーモーダルのOKをクリックしても、何も表示も動作も変化無し

**原因**:
1. エラーハンドリングで`alert`を表示するだけで、エラー後の処理がない
2. `selectedSuggestion.value`が`null`のままのため、モーダルが表示されない

**解決方法**:
1. エラーハンドリングを改善（エラーメッセージの表示、ログ出力、ユーザーへの案内など）

---

## 6. データベースの整合性問題

### 6.1 複数の`pending`ステータスのFAQ提案が存在する問題

**データベースの状態**:
- `source_message_id = 28`に対して、ID 15とID 16の2つの`pending`ステータスのFAQ提案が存在

**問題点**:
1. **データ整合性の問題**: 同じ`message_id`に対して複数の`pending`ステータスのFAQ提案が存在する
2. **ビジネスロジックの問題**: 1つの`message_id`に対して1つの`pending`ステータスのFAQ提案のみが存在すべき

**解決方法**:
1. **既存の`pending`ステータスのFAQ提案を確認する処理を修正**
   - 最新の1件を取得する処理に変更
   - または、複数の`pending`ステータスのFAQ提案が存在する場合、古いものを`rejected`に更新
2. **データベースの整合性を確保**
   - 既存の`pending`ステータスのFAQ提案を確認する処理を修正
   - 重複チェックを強化

---

## 7. まとめ

### 7.1 問題の原因

1. **問題1（却下・無視削除問題）**: 
   - 「却下」: FAQ提案を却下しても、低評価回答リストを再取得していない
   - 「無視」: 実装されていない（TODOコメントのみ）

2. **問題2（Multiple rowsエラー）**: 
   - `source_message_id = 28`に対して、複数の`pending`ステータスのFAQ提案が存在
   - `scalar_one_or_none()`が複数の行を返したためエラーが発生

3. **問題3（モーダル表示問題）**: 
   - エラーハンドリングで`alert`を表示するだけで、エラー後の処理がない

### 7.2 修正が必要な箇所

1. **「却下」ボタンの処理**: FAQ提案を却下した後、`fetchLowRatedAnswers()`を呼び出して低評価回答リストを再取得
2. **「無視」ボタンの実装**: 低評価回答を無視する機能を実装（APIエンドポイントの追加が必要）
3. **既存の`pending`ステータスのFAQ提案を確認する処理**: `scalar_one_or_none()`の代わりに、最新の1件を取得する処理に変更
4. **エラーハンドリング**: エラーメッセージの表示、ログ出力、ユーザーへの案内などを改善

---

**調査完了日**: 2025年12月14日  
**次回**: 修正指示を待つ


