# Phase 1・Phase 2: FAQ承認後 ゲストフィードバック連動FAQ削除問題 完全調査分析・大原則準拠修正案

**作成日時**: 2025年12月16日  
**実施者**: AI Assistant  
**対象**: FAQ承認後に「ゲストフィードバック連動FAQ」から削除されない問題の完全調査分析と大原則準拠修正案  
**状態**: 🔴 **調査分析完了 - 修正案提示**

---

## 1. 問題の詳細

### 1.1 問題の発生状況

**症状**:
- 「承認してFAQへ追加」ボタンを押すと「FAQ一覧」に表示される
- しかし、「ゲストフィードバック連動FAQ」から削除されない
- リロードしても削除されていない
- 処理しても残ってしまう

**ユーザー体験への影響**:
- 同じ低評価回答が繰り返し表示される
- ユーザーが混乱する
- データの整合性が保たれない

### 1.2 問題の流れ

1. ユーザーが「FAQ改善提案」ボタンをクリック
2. FAQ提案が生成される
3. ユーザーが「承認してFAQへ追加」ボタンをクリック
4. FAQが作成される（`faq_suggestion_service.py`の`approve_suggestion`メソッド）
5. **問題**: 「ゲストフィードバック連動FAQ」から削除されない

---

## 2. 根本原因の調査分析

### 2.1 フロントエンドの処理確認

**`FaqManagement.vue`の`handleApproveSuggestion`メソッド**:
```typescript
const handleApproveSuggestion = async (_suggestion: FaqSuggestion) => {
  // API連携はFaqSuggestionCard内で実装済み
  // ここでは提案をクリアしてFAQ一覧と未解決質問リストを再取得
  selectedSuggestion.value = null
  await fetchFaqs()
  await fetchUnresolvedQuestions()
}
```

**問題点**:
- `fetchLowRatedAnswers()`が呼び出されていない
- 低評価回答リストが再取得されていない

### 2.2 バックエンドの処理確認

**`faq_suggestion_service.py`の`approve_suggestion`メソッド**:
- FAQを作成している
- エスカレーションを解決している
- **問題**: 対応するメッセージを無視リストに追加していない

**`feedback_service.py`の`get_negative_feedbacks`メソッド**:
- 無視されたメッセージIDを除外している
- しかし、FAQ承認時に無視リストに追加されていないため、削除されない

### 2.3 根本原因の確定

**原因1: フロントエンドで低評価回答リストを再取得していない**
- `handleApproveSuggestion`で`fetchLowRatedAnswers()`が呼び出されていない
- 画面に反映されない

**原因2: バックエンドでFAQ承認時に無視リストに追加していない（根本原因）**
- FAQ承認時に、対応するメッセージを無視リストに追加していない
- リロードしても削除されない（データベースに無視状態が記録されていない）

---

## 3. 大原則準拠修正案

### 3.1 大原則の確認

1. **根本解決 > 暫定解決**: バックエンドでFAQ承認時に無視リストに追加する（根本解決）
2. **シンプル構造 > 複雑構造**: シンプルな処理追加
3. **統一・同一化 > 特殊独自**: 既存の無視処理と同じパターンを使用
4. **具体的 > 一般**: 具体的な処理を追加
5. **安全確実**: エラーハンドリングを追加

### 3.2 修正案

**修正1: バックエンドでFAQ承認時に無視リストに追加する（根本解決）**
- `faq_suggestion_service.py`の`approve_suggestion`メソッドで、FAQ承認時に`FeedbackService.ignore_negative_feedback`を呼び出す
- 対応するメッセージ（`source_message_id`）を無視リストに追加する
- エラーハンドリングを追加（無視処理の失敗はFAQ作成を妨げない）

**修正2: フロントエンドで低評価回答リストを再取得する（暫定対応）**
- `handleApproveSuggestion`で`fetchLowRatedAnswers()`を呼び出す
- 画面に反映される

**推奨**: 修正1（根本解決）を実施し、修正2（暫定対応）も併用する

---

## 4. 修正内容の詳細

### 4.1 バックエンドの修正（`faq_suggestion_service.py`）

**修正内容**:
- `approve_suggestion`メソッドで、FAQ承認時に`FeedbackService.ignore_negative_feedback`を呼び出す
- 対応するメッセージ（`source_message_id`）を無視リストに追加する
- エラーハンドリングを追加（無視処理の失敗はFAQ作成を妨げない）

**実装例**:
```python
# FAQ承認時に、対応するメッセージを無視リストに追加
try:
    from app.services.feedback_service import FeedbackService
    feedback_service = FeedbackService(self.db)
    await feedback_service.ignore_negative_feedback(
        message_id=suggestion.source_message_id,
        facility_id=facility_id,
        user_id=user_id
    )
    logger.info(
        f"Negative feedback ignored after FAQ approval: message_id={suggestion.source_message_id}, "
        f"suggestion_id={suggestion_id}, faq_id={faq.id}"
    )
except ValueError as e:
    # 既に無視されている場合や、メッセージが見つからない場合は警告のみ（FAQ作成は続行）
    logger.warning(
        f"Could not ignore negative feedback after FAQ approval: message_id={suggestion.source_message_id}, "
        f"error={str(e)}"
    )
except Exception as e:
    # その他のエラーも警告のみ（FAQ作成は続行）
    logger.error(
        f"Error ignoring negative feedback after FAQ approval: message_id={suggestion.source_message_id}, "
        f"error={str(e)}",
        exc_info=True
    )
```

### 4.2 フロントエンドの修正（`FaqManagement.vue`）

**修正内容**:
- `handleApproveSuggestion`で`fetchLowRatedAnswers()`を呼び出す
- 画面に反映される

**実装例**:
```typescript
const handleApproveSuggestion = async (_suggestion: FaqSuggestion) => {
  // API連携はFaqSuggestionCard内で実装済み
  // ここでは提案をクリアしてFAQ一覧と未解決質問リストを再取得
  selectedSuggestion.value = null
  await fetchFaqs()
  await fetchUnresolvedQuestions()
  // 低評価回答リストを再取得（画面に反映）
  await fetchLowRatedAnswers()
}
```

---

## 5. 修正実施計画

1. **バックアップの作成**
   - `backend/app/services/faq_suggestion_service.py.backup_YYYYMMDD_HHMMSS`
   - `frontend/src/views/admin/FaqManagement.vue.backup_YYYYMMDD_HHMMSS`

2. **修正の実施**
   - `faq_suggestion_service.py`の修正（根本解決）
   - `FaqManagement.vue`の修正（暫定対応）

3. **コミット・プッシュ**
   - 修正内容をコミット
   - プッシュしてデプロイ

---

**調査分析完了日時**: 2025年12月16日  
**状態**: 🔴 **調査分析完了 - 修正案提示**

**重要**: 指示があるまで修正を実施しません。調査分析のみです。

