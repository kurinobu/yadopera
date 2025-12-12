# Phase 1: APIレスポンススキーマ不一致 調査分析レポート

**作成日**: 2025年12月1日  
**実施者**: Auto (AI Assistant)  
**環境**: ローカル環境  
**対象**: APIレスポンススキーマの不一致の調査と分析

---

## 1. 調査実施概要

### 1.1 調査実施日時

- **実施日時**: 2025年12月1日 18:30頃
- **調査環境**: ローカル環境（Docker Compose）

### 1.2 調査対象

- **バックエンド**: `backend/app/schemas/chat.py`
- **フロントエンド**: `frontend/src/types/chat.ts`
- **バックエンド実装**: `backend/app/services/chat_service.py`
- **フロントエンド実装**: `frontend/src/composables/useChat.ts`

---

## 2. 調査結果

### 2.1 バックエンドの`ChatResponse`スキーマ

**ファイル**: `backend/app/schemas/chat.py`

```python
class ChatResponse(BaseModel):
    message_id: int = Field(..., description="メッセージID")
    session_id: str = Field(..., description="セッションID")
    response: str = Field(..., description="AI応答")
    ai_confidence: Optional[Decimal] = Field(None, description="AI信頼度（0.0-1.0）")
    source: str = Field(..., description="応答ソース（rag_generated/escalation_needed）")
    matched_faq_ids: Optional[List[int]] = Field(None, description="使用したFAQ IDリスト")
    response_time_ms: Optional[int] = Field(None, description="レスポンス時間（ミリ秒）")
    escalation: EscalationInfo = Field(..., description="エスカレーション情報")
```

**特徴**:
- `message`フィールドは存在しない
- `response`フィールド（文字列）でAI応答を返す
- `message_id`フィールドでメッセージIDを返す
- `escalation`フィールドでエスカレーション情報を返す

### 2.2 フロントエンドの`ChatResponse`型

**ファイル**: `frontend/src/types/chat.ts`

```typescript
export interface ChatResponse {
  message: ChatMessage
  session_id: string
  ai_confidence?: number
  is_escalated: boolean
  escalation_id?: number
}
```

**特徴**:
- `message`フィールド（`ChatMessage`オブジェクト）を期待している
- `is_escalated`フィールドを期待している
- `escalation_id`フィールドを期待している

### 2.3 バックエンドの`MessageResponse`スキーマ

**ファイル**: `backend/app/schemas/chat.py`

```python
class MessageResponse(BaseModel):
    id: int
    role: str  # 'user', 'assistant', 'system'
    content: str
    ai_confidence: Optional[Decimal] = None
    matched_faq_ids: Optional[List[int]] = None
    response_time_ms: Optional[int] = None
    created_at: datetime
```

**特徴**:
- `ChatMessage`型とほぼ同じ構造
- `created_at`フィールドが`datetime`型

### 2.4 フロントエンドの`ChatMessage`型

**ファイル**: `frontend/src/types/chat.ts`

```typescript
export interface ChatMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  ai_confidence?: number
  matched_faq_ids?: number[]
  created_at: string
}
```

**特徴**:
- `MessageResponse`とほぼ同じ構造
- `created_at`フィールドが`string`型（ISO形式）

### 2.5 バックエンドの実装

**ファイル**: `backend/app/services/chat_service.py`

```python
# AI応答メッセージを保存
ai_message = Message(
    conversation_id=conversation.id,
    role=MessageRole.ASSISTANT.value,
    content=chat_response.response,
    ai_confidence=chat_response.ai_confidence,
    matched_faq_ids=chat_response.matched_faq_ids,
    response_time_ms=chat_response.response_time_ms
)
self.db.add(ai_message)
await self.db.flush()

# レスポンスに実際のメッセージIDを設定
chat_response.message_id = ai_message.id

return chat_response
```

**特徴**:
- `ChatResponse`オブジェクトを返している
- `ai_message`オブジェクトは作成されているが、レスポンスには含まれていない

---

## 3. 問題の分析

### 3.1 スキーマの不一致

| フィールド | バックエンド | フロントエンド | 不一致 |
|-----------|------------|--------------|--------|
| `message` | ❌ 存在しない | ✅ `ChatMessage` | ✅ 不一致 |
| `response` | ✅ `str` | ❌ 存在しない | ✅ 不一致 |
| `message_id` | ✅ `int` | ❌ 存在しない | ✅ 不一致 |
| `session_id` | ✅ `str` | ✅ `string` | ✅ 一致 |
| `ai_confidence` | ✅ `Optional[Decimal]` | ✅ `number?` | ✅ 一致 |
| `is_escalated` | ❌ 存在しない | ✅ `boolean` | ✅ 不一致 |
| `escalation` | ✅ `EscalationInfo` | ❌ 存在しない | ✅ 不一致 |
| `escalation_id` | ❌ 存在しない | ✅ `number?` | ✅ 不一致 |

### 3.2 問題の影響

1. **フロントエンドで`response.message`を参照しているが、存在しない**
   - `useChat.ts`の23行目: `if (response.message) { chatStore.addMessage(response.message) }`
   - この条件が常に`false`になり、メッセージがストアに追加されない

2. **フロントエンドで`response.is_escalated`を参照しているが、存在しない**
   - `Chat.vue`の210行目: `if (response.is_escalated) { ... }`
   - この条件が常に`false`になり、エスカレーション処理が実行されない

---

## 4. 修正方針の検討

### 4.1 方針1: バックエンドのスキーマを変更（根本解決）

**内容**:
- `ChatResponse`スキーマに`message: MessageResponse`フィールドを追加
- `is_escalated: bool`フィールドを追加（`escalation.needed`から取得）
- `escalation_id: Optional[int]`フィールドを追加

**メリット**:
- ✅ 根本解決（大原則: 根本解決 > 暫定解決）
- ✅ フロントエンドのコードを変更する必要がない
- ✅ スキーマが明確になる

**デメリット**:
- ❌ バックエンドの実装を変更する必要がある
- ❌ 他の部分への影響が大きい可能性がある
- ❌ テストコードの修正が必要

**影響範囲**:
- `backend/app/schemas/chat.py`
- `backend/app/services/chat_service.py`
- バックエンドのテストコード

### 4.2 方針2: フロントエンドで`response.response`から`ChatMessage`オブジェクトを構築（暫定解決）

**内容**:
- `useChat.ts`で`response.response`から`ChatMessage`オブジェクトを構築
- `response.escalation.needed`から`is_escalated`を取得
- `response.escalation`から`escalation_id`を取得（必要に応じて）

**メリット**:
- ✅ バックエンドのコードを変更する必要がない
- ✅ 影響範囲が小さい
- ✅ 実装が簡単

**デメリット**:
- ❌ 暫定解決（大原則: 根本解決 > 暫定解決）
- ❌ スキーマの不一致が残る
- ❌ 将来的に問題が発生する可能性がある

**影響範囲**:
- `frontend/src/composables/useChat.ts`
- `frontend/src/types/chat.ts`（型定義の更新）

### 4.3 推奨方針

**推奨**: **方針1（バックエンドのスキーマを変更）**

**理由**:
1. **大原則に準拠**: 根本解決 > 暫定解決
2. **シンプル構造**: スキーマが明確になり、コードがシンプルになる
3. **統一・同一化**: バックエンドとフロントエンドのスキーマが一致する
4. **具体的**: 明確なスキーマ定義により、実装が明確になる

**ただし、時間的制約がある場合は方針2も検討可能**

---

## 5. 修正内容の詳細（方針1の場合）

### 5.1 バックエンドの`ChatResponse`スキーマの変更

**変更前**:
```python
class ChatResponse(BaseModel):
    message_id: int = Field(..., description="メッセージID")
    session_id: str = Field(..., description="セッションID")
    response: str = Field(..., description="AI応答")
    ai_confidence: Optional[Decimal] = Field(None, description="AI信頼度（0.0-1.0）")
    source: str = Field(..., description="応答ソース（rag_generated/escalation_needed）")
    matched_faq_ids: Optional[List[int]] = Field(None, description="使用したFAQ IDリスト")
    response_time_ms: Optional[int] = Field(None, description="レスポンス時間（ミリ秒）")
    escalation: EscalationInfo = Field(..., description="エスカレーション情報")
```

**変更後**:
```python
class ChatResponse(BaseModel):
    message: MessageResponse = Field(..., description="AI応答メッセージ")
    session_id: str = Field(..., description="セッションID")
    ai_confidence: Optional[Decimal] = Field(None, description="AI信頼度（0.0-1.0）")
    is_escalated: bool = Field(..., description="エスカレーションが必要か")
    escalation_id: Optional[int] = Field(None, description="エスカレーションID")
    escalation: EscalationInfo = Field(..., description="エスカレーション情報")
```

### 5.2 バックエンドの`chat_service.py`の変更

**変更内容**:
- `ChatResponse`オブジェクトを作成する際に、`message`フィールドに`MessageResponse`オブジェクトを設定
- `is_escalated`フィールドに`escalation.needed`を設定
- `escalation_id`フィールドにエスカレーションIDを設定（存在する場合）

---

## 6. 修正内容の詳細（方針2の場合）

### 6.1 フロントエンドの`useChat.ts`の変更

**変更前**:
```typescript
// メッセージを追加
if (response.message) {
  chatStore.addMessage(response.message)
}
```

**変更後**:
```typescript
// メッセージを追加（response.responseからChatMessageオブジェクトを構築）
if (response.response) {
  const chatMessage: ChatMessage = {
    id: response.message_id,
    role: 'assistant',
    content: response.response,
    ai_confidence: response.ai_confidence ? Number(response.ai_confidence) : undefined,
    matched_faq_ids: response.matched_faq_ids,
    created_at: new Date().toISOString()
  }
  chatStore.addMessage(chatMessage)
}
```

### 6.2 フロントエンドの`Chat.vue`の変更

**変更前**:
```typescript
// エスカレーションが必要な場合
if (response.is_escalated) {
  // TODO: エスカレーション処理（Week 4で実装）
  console.log('Escalation needed:', response.escalation_id)
}
```

**変更後**:
```typescript
// エスカレーションが必要な場合
if (response.escalation?.needed) {
  // TODO: エスカレーション処理（Week 4で実装）
  console.log('Escalation needed:', response.escalation)
}
```

---

## 7. 結論

### 7.1 推奨修正方針

**方針1（バックエンドのスキーマを変更）を推奨**

**理由**:
1. 大原則に準拠（根本解決 > 暫定解決）
2. シンプル構造（スキーマが明確）
3. 統一・同一化（バックエンドとフロントエンドのスキーマが一致）
4. 具体的（明確なスキーマ定義）

### 7.2 修正の工数見積もり

**方針1（推奨）**:
- バックエンドのスキーマ変更: 15分
- バックエンドの実装変更: 15分
- テスト: 10分
- **合計: 約40分**

**方針2**:
- フロントエンドの実装変更: 15分
- テスト: 10分
- **合計: 約25分**

---

**Document Version**: v1.0  
**Last Updated**: 2025-12-01  
**Status**: 調査分析完了、修正方針決定待ち


