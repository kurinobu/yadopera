# Phase 1: テスト環境整備 - 未解決質問リスト作成手順書

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: 未解決質問リストのテスト環境整備  
**目的**: FAQ自動学習UIのテストを実施するために、未解決質問リストに表示されるテストデータを作成する

---

## 1. 概要

### 1.1 問題

- 「未解決質問リストからFAQ提案を生成」のテストができない
- 現在「未解決質問リスト」は「未解決質問はありません」となっている

### 1.2 解決方法

未解決質問を作成するために、以下のテストデータを作成する必要があります：

1. **会話（Conversation）**: ゲストとの会話セッション
2. **メッセージ（Message）**: ユーザーからの質問メッセージ
3. **エスカレーション（Escalation）**: 未解決のエスカレーション（`resolved_at IS NULL`）

---

## 2. テストデータ作成方法

### 2.1 方法1: テストデータ作成スクリプトを拡張（推奨）

**ファイル**: `backend/create_test_data.py`

**追加する内容**:

```python
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.escalation import Escalation
from decimal import Decimal
from datetime import datetime, timedelta

# 会話を作成
conversation = Conversation(
    facility_id=test_facility.id,
    session_id="test-session-unresolved-1",
    guest_language="en",
    started_at=datetime.utcnow() - timedelta(days=1),
    last_activity_at=datetime.utcnow() - timedelta(hours=2),
    is_escalated=True
)
session.add(conversation)
await session.flush()

# ユーザーメッセージを作成
user_message = Message(
    conversation_id=conversation.id,
    role=MessageRole.USER.value,
    content="What time is check-in?",
    created_at=datetime.utcnow() - timedelta(days=1)
)
session.add(user_message)
await session.flush()

# アシスタントメッセージを作成
assistant_message = Message(
    conversation_id=conversation.id,
    role=MessageRole.ASSISTANT.value,
    content="Check-in is from 3pm to 10pm.",
    created_at=datetime.utcnow() - timedelta(days=1) + timedelta(minutes=1)
)
session.add(assistant_message)
await session.flush()

# 未解決のエスカレーションを作成
escalation = Escalation(
    facility_id=test_facility.id,
    conversation_id=conversation.id,
    trigger_type="low_confidence",
    ai_confidence=Decimal("0.5"),
    escalation_mode="normal",
    notification_channels=["email"],
    resolved_at=None  # 未解決
)
session.add(escalation)
await session.flush()

print(f"✅ 未解決質問を作成しました: escalation_id={escalation.id}, message_id={user_message.id}")
```

### 2.2 方法2: データベースに直接SQLで挿入

**PostgreSQLに接続**:
```bash
docker-compose exec postgres psql -U yadopera -d yadopera
```

**SQL実行**:
```sql
-- 会話を作成
INSERT INTO conversations (facility_id, session_id, guest_language, started_at, last_activity_at, is_escalated)
VALUES (
    (SELECT id FROM facilities WHERE slug = 'test-facility' LIMIT 1),
    'test-session-unresolved-1',
    'en',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '2 hours',
    true
)
RETURNING id;

-- メッセージを作成（会話IDを上記の結果に置き換える）
INSERT INTO messages (conversation_id, role, content, created_at)
VALUES (
    (SELECT id FROM conversations WHERE session_id = 'test-session-unresolved-1' LIMIT 1),
    'user',
    'What time is check-in?',
    NOW() - INTERVAL '1 day'
)
RETURNING id;

-- エスカレーションを作成（会話IDを上記の結果に置き換える）
INSERT INTO escalations (facility_id, conversation_id, trigger_type, ai_confidence, escalation_mode, notification_channels, resolved_at)
VALUES (
    (SELECT id FROM facilities WHERE slug = 'test-facility' LIMIT 1),
    (SELECT id FROM conversations WHERE session_id = 'test-session-unresolved-1' LIMIT 1),
    'low_confidence',
    0.5,
    'normal',
    ARRAY['email'],
    NULL  -- 未解決
)
RETURNING id;
```

### 2.3 方法3: ゲスト画面から実際にエスカレーションを発生させる

**手順**:
1. ゲスト画面で低信頼度の質問を送信する（例: 曖昧な質問）
2. AIの信頼度が低い場合、自動的にエスカレーションが作成される
3. 管理画面で未解決質問リストを確認する

**注意**: この方法は「スタッフに連絡」ボタンの問題が解決されていないため、現在は使用できない可能性がある

---

## 3. 確認方法

### 3.1 管理画面で確認

1. 管理画面にログイン: `http://localhost:5173/admin/login`
2. FAQ管理画面に移動: `http://localhost:5173/admin/faqs`
3. 「未解決質問リスト」セクションを確認
4. 未解決質問が表示されることを確認

### 3.2 APIで確認

```bash
# 認証トークンを取得（ログイン後）
TOKEN="your_jwt_token"

# 未解決質問リストを取得
curl -X GET "http://localhost:8000/api/v1/admin/escalations/unresolved-questions" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 3.3 データベースで確認

```sql
-- 未解決のエスカレーションを確認
SELECT 
    e.id AS escalation_id,
    e.conversation_id,
    e.trigger_type,
    e.ai_confidence,
    e.resolved_at,
    c.session_id,
    m.content AS question
FROM escalations e
JOIN conversations c ON e.conversation_id = c.id
JOIN messages m ON m.conversation_id = c.id AND m.role = 'user'
WHERE e.resolved_at IS NULL
ORDER BY e.created_at DESC;
```

---

## 4. 複数の未解決質問を作成する場合

### 4.1 スクリプトで複数作成

```python
# 複数の未解決質問を作成
for i in range(3):
    conversation = Conversation(
        facility_id=test_facility.id,
        session_id=f"test-session-unresolved-{i+1}",
        guest_language="en",
        started_at=datetime.utcnow() - timedelta(days=i+1),
        last_activity_at=datetime.utcnow() - timedelta(hours=i+2),
        is_escalated=True
    )
    session.add(conversation)
    await session.flush()
    
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER.value,
        content=f"Test question {i+1}",
        created_at=datetime.utcnow() - timedelta(days=i+1)
    )
    session.add(user_message)
    await session.flush()
    
    escalation = Escalation(
        facility_id=test_facility.id,
        conversation_id=conversation.id,
        trigger_type="low_confidence",
        ai_confidence=Decimal("0.5"),
        escalation_mode="normal",
        notification_channels=["email"],
        resolved_at=None
    )
    session.add(escalation)
    await session.flush()
    
    print(f"✅ 未解決質問 {i+1} を作成しました: escalation_id={escalation.id}")
```

---

## 5. トラブルシューティング

### 5.1 未解決質問が表示されない場合

**確認項目**:
1. エスカレーションの`resolved_at`が`NULL`であることを確認
2. エスカレーションの`facility_id`が正しいことを確認
3. 会話にユーザーメッセージが存在することを確認
4. APIエンドポイントが正常に動作していることを確認（ログを確認）

### 5.2 エラーメッセージが表示される場合

**確認項目**:
1. データベース接続が正常であることを確認
2. 外部キー制約が満たされていることを確認（`facility_id`, `conversation_id`）
3. 必須フィールドがすべて設定されていることを確認

---

## 6. まとめ

### 6.1 推奨方法

**方法1（テストデータ作成スクリプトを拡張）**を推奨します：
- 再現性が高い
- 他の開発者も同じデータを作成できる
- バージョン管理できる

### 6.2 次のステップ

1. `backend/create_test_data.py`を拡張して未解決質問を作成する機能を追加
2. スクリプトを実行してテストデータを作成
3. 管理画面で未解決質問リストを確認
4. FAQ提案の生成と承認のテストを実施

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ✅ **手順書作成完了**


