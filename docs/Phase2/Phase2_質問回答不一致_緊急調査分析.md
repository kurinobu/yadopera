# Phase 2: 質問回答不一致 緊急調査分析

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: 質問と回答が一致しない重大なデータ整合性問題  
**状態**: 🔴 **緊急調査中**

---

## 1. 問題の報告

### 1.1 報告された問題

**症状**:
- 質問: 「アイロンは貸し出ししてますか？」
- 回答: 「申し訳ありませんが、ドリンカブルな水についての情報はありません。スタッフにお問い合わせください。」

**問題の深刻度**: 🔴 **重大** - 質問と回答が完全に一致していない

---

## 2. 調査分析

### 2.1 コードロジックの確認

**`feedback_service.py`の`get_negative_feedbacks`メソッド**:

```python:88:95:backend/app/services/feedback_service.py
# このメッセージ（AI応答）の前にあるユーザーメッセージ（質問）を取得
question = None
for msg in reversed(conversation_messages):
    if msg.id == message.id:
        break
    if msg.role == MessageRole.USER.value:
        question = msg.content
        break
```

**問題の可能性**:
1. **逆順走査の問題**: `reversed(conversation_messages)`で逆順に走査しているが、`message.id`に到達するまで、その前にある最初の`USER`ロールのメッセージを取得している
2. **複数質問の問題**: 会話に複数の質問が含まれている場合、間違った質問を取得する可能性がある
3. **順序の問題**: `created_at`でソートしているが、タイムスタンプが同じ場合や、順序が正しくない場合、間違った質問を取得する可能性がある

### 2.2 データベースの確認が必要

**確認すべきデータ**:
1. `guest_feedback`テーブル: `message_id`と`facility_id`の対応
2. `messages`テーブル: `message_id`に対応する`content`と`role`
3. `messages`テーブル: 同じ`conversation_id`内のメッセージの順序
4. 会話履歴: 質問と回答の対応関係

---

## 3. 調査手順

### 3.1 データベースクエリ

以下のクエリを実行して、実際のデータを確認する必要があります：

```sql
-- 1. 低評価が2回以上ついたメッセージIDを確認
SELECT message_id, COUNT(*) as negative_count 
FROM guest_feedback 
WHERE feedback_type = 'negative' AND facility_id = 2 
GROUP BY message_id 
HAVING COUNT(*) >= 2;

-- 2. そのメッセージIDの詳細を確認
SELECT id, conversation_id, role, content, created_at 
FROM messages 
WHERE id IN (上記のmessage_id);

-- 3. 同じ会話内のメッセージを確認（順序付き）
SELECT id, conversation_id, role, content, created_at 
FROM messages 
WHERE conversation_id IN (上記のconversation_id)
ORDER BY conversation_id, created_at ASC;

-- 4. 質問と回答の対応を確認
-- 各メッセージIDについて、その前にあるUSERロールのメッセージを確認
```

---

## 4. 考えられる原因

### 4.1 ロジックの問題

1. **逆順走査の問題**
   - `reversed(conversation_messages)`で逆順に走査しているが、`message.id`に到達するまで、その前にある最初の`USER`ロールのメッセージを取得している
   - しかし、会話に複数の質問が含まれている場合、間違った質問を取得する可能性がある

2. **順序の問題**
   - `created_at`でソートしているが、タイムスタンプが同じ場合や、順序が正しくない場合、間違った質問を取得する可能性がある

### 4.2 データの問題

1. **リレーションの問題**
   - `message_id`と実際のメッセージの対応が間違っている
   - `conversation_id`が間違っている

2. **データの不整合**
   - 会話履歴の順序が正しくない
   - メッセージの`created_at`が正しくない

---

## 5. 次のステップ

1. **データベースの実際のデータを確認**
   - 上記のSQLクエリを実行
   - 実際のデータを確認

2. **ロジックの修正**
   - 問題が特定されたら、ロジックを修正

3. **テスト**
   - 修正後、正しい質問と回答が表示されることを確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: 🔴 **緊急調査中**


