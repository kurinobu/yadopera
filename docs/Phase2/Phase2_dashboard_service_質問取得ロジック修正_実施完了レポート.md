# Phase 2: dashboard_service 質問取得ロジック修正 実施完了レポート

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: 修正案4（`dashboard_service.py`の質問取得ロジック修正）  
**状態**: ✅ **実施完了**

---

## 1. 実施概要

### 1.1 実施内容

**修正内容**: `dashboard_service.py`の`get_feedback_stats`メソッドで、`feedback_service.py`の`get_negative_feedbacks`メソッドを使用するように修正

**目的**: ダッシュボードページで「Q: Question」ではなく、実際の質問が表示されるようにする

### 1.2 実施日時

- **開始時刻**: 2025年12月4日 10:40
- **完了時刻**: 2025年12月4日 10:42

---

## 2. バックアップ作成

### 2.1 バックアップファイル

- ✅ `backend/app/services/dashboard_service.py.backup_YYYYMMDD_HHMMSS`を作成

---

## 3. 修正内容

### 3.1 `dashboard_service.py`の修正

**ファイル**: `backend/app/services/dashboard_service.py`

**修正内容**:
1. `FeedbackService`をインポート
2. `get_feedback_stats`メソッドで、`feedback_service.py`の`get_negative_feedbacks`メソッドを使用するように修正
3. 重複コードを削除（統一 > 特殊・独自の大原則に準拠）

**修正前**:
```python:315:346:backend/app/services/dashboard_service.py
# 低評価回答（2回以上）を取得
# メッセージIDごとに低評価数を集計
message_negative_count: dict[int, int] = {}
for feedback in feedbacks:
    if feedback.feedback_type == "negative":
        message_negative_count[feedback.message_id] = message_negative_count.get(feedback.message_id, 0) + 1

# 2回以上低評価がついたメッセージを取得
low_rated_message_ids = [msg_id for msg_id, count in message_negative_count.items() if count >= 2]

low_rated_answers: List[LowRatedAnswer] = []
if low_rated_message_ids:
    # メッセージを取得
    messages_result = await self.db.execute(
        select(Message)
        .where(Message.id.in_(low_rated_message_ids))
        .options(selectinload(Message.conversation))
    )
    messages = messages_result.scalars().all()
    
    for message in messages:
        # 質問と回答を取得（簡易実装）
        # 実際には会話履歴から質問と回答を抽出する必要がある
        question = "Question"  # TODO: 会話履歴から質問を抽出
        answer = message.content[:200]  # 回答は200文字まで
        
        low_rated_answers.append(LowRatedAnswer(
            message_id=message.id,
            question=question,
            answer=answer,
            negative_count=message_negative_count[message.id]
        ))
```

**修正後**:
```python:315:318:backend/app/services/dashboard_service.py
# 低評価回答（2回以上）を取得
# feedback_serviceを使用して重複を排除（統一 > 特殊・独自）
feedback_service = FeedbackService(self.db)
low_rated_answers = await feedback_service.get_negative_feedbacks(facility_id)
```

**インポート追加**:
```python:30:31:backend/app/services/dashboard_service.py
from app.core.cache import get_cache, set_cache, cache_key
from app.services.feedback_service import FeedbackService
```

---

## 4. 改善点

### 4.1 重複コードの排除

- **修正前**: `dashboard_service.py`と`feedback_service.py`で同じロジックが重複していた
- **修正後**: `feedback_service.py`の`get_negative_feedbacks`メソッドを再利用することで、重複を排除

### 4.2 質問取得ロジックの修正

- **修正前**: `question = "Question"`というハードコードされた値が使用されていた
- **修正後**: `feedback_service.py`の`get_negative_feedbacks`メソッドを使用することで、会話履歴から実際の質問を取得

### 4.3 コードの統一

- **修正前**: ダッシュボードページとFAQページで異なるロジックを使用していた
- **修正後**: 両方とも`feedback_service.py`の`get_negative_feedbacks`メソッドを使用することで、統一された

---

## 5. 動作確認方法

### 5.1 動作確認項目

1. **ダッシュボードページの確認**
   - [ ] ダッシュボードページにアクセス
   - [ ] 「ゲストフィードバック集計」セクションを確認
   - [ ] 低評価回答リストが表示されることを確認
   - [ ] 「Q: Question」ではなく、実際の質問が表示されることを確認

2. **FAQページの確認**
   - [ ] FAQ管理ページにアクセス
   - [ ] 「ゲストフィードバック連動FAQ」セクションを確認
   - [ ] 低評価回答リストが表示されることを確認
   - [ ] 実際の質問が表示されることを確認

3. **データの整合性確認**
   - [ ] ダッシュボードページとFAQページで同じデータが表示されることを確認
   - [ ] 質問と回答が正しく対応していることを確認

---

## 6. 大原則への準拠

### 6.1 大原則の評価

1. **根本原因 > 一時的解決**
   - ✅ ハードコードされた「Question」を修正し、実際の質問を取得するように修正

2. **シンプルな構造 > 複雑な構造**
   - ✅ 重複コードを削除し、`feedback_service.py`を再利用することで、シンプルな構造に

3. **統一 > 特殊・独自**
   - ✅ ダッシュボードページとFAQページで同じロジックを使用することで、統一された

4. **具体的 > 一般的**
   - ✅ 具体的な`feedback_service.py`の`get_negative_feedbacks`メソッドを使用

5. **遅くても安全 > 急いで危険**
   - ✅ バックアップを作成してから修正を実施

---

## 7. まとめ

### 7.1 実施完了項目

- ✅ バックアップファイルの作成
- ✅ `FeedbackService`をインポート
- ✅ `get_feedback_stats`メソッドで`feedback_service.py`の`get_negative_feedbacks`メソッドを使用
- ✅ 重複コードを削除
- ✅ リンターエラーの確認

### 7.2 期待される効果

1. **質問の正しい表示**
   - ダッシュボードページで「Q: Question」ではなく、実際の質問が表示される

2. **コードの統一**
   - ダッシュボードページとFAQページで同じロジックを使用することで、保守性が向上

3. **重複の排除**
   - 重複コードを削除することで、コードの保守性が向上

### 7.3 次のアクション

1. **動作確認の実施**（ユーザーによる確認が必要）
   - ダッシュボードページで実際の質問が表示されることを確認
   - FAQページで実際の質問が表示されることを確認
   - データの整合性を確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ✅ **実施完了**


