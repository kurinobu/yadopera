# Phase 2: ステップ4 低評価回答リストAPI 完全調査分析・実装計画

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: ステップ4 - 低評価回答リストAPIの実装  
**状態**: ✅ **完全調査分析完了 → 実装計画提示**

---

## 1. 調査分析結果

### 1.1 既存の実装状況

#### 1.1.1 データベースモデル

**`GuestFeedback`モデル** (`backend/app/models/guest_feedback.py`):
- `id`: フィードバックID
- `message_id`: メッセージID（外部キー）
- `facility_id`: 施設ID（外部キー）
- `feedback_type`: フィードバックタイプ（'positive'/'negative'）
- `created_at`: 作成日時

**`Message`モデル** (`backend/app/models/message.py`):
- `id`: メッセージID
- `conversation_id`: 会話ID（外部キー）
- `role`: メッセージロール（'user'/'assistant'/'system'）
- `content`: メッセージ内容
- `ai_confidence`: AI信頼度
- `created_at`: 作成日時

**`Conversation`モデル** (`backend/app/models/conversation.py`):
- `id`: 会話ID
- `facility_id`: 施設ID
- `session_id`: セッションID
- `messages`: メッセージリスト（リレーションシップ）

#### 1.1.2 既存のサービス実装

**`dashboard_service.py`の`get_feedback_stats`メソッド**:
- 低評価回答を取得するロジックが既に存在
- ただし、質問の取得が不完全（`question = "Question"`というTODOがある）
- メッセージIDごとに低評価数を集計し、2回以上低評価がついたメッセージを取得

**問題点**:
- 質問の取得が不完全（会話履歴から質問を取得する必要がある）
- ダッシュボード用の実装であり、管理画面用のAPIエンドポイントが存在しない

#### 1.1.3 既存のスキーマ

**`LowRatedAnswer`スキーマ** (`backend/app/schemas/dashboard.py`):
```python
class LowRatedAnswer(BaseModel):
    message_id: int
    question: str
    answer: str
    negative_count: int
```

**`FeedbackStats`スキーマ** (`backend/app/schemas/dashboard.py`):
```python
class FeedbackStats(BaseModel):
    positive_count: int
    negative_count: int
    positive_rate: Decimal
    low_rated_answers: List[LowRatedAnswer]
```

#### 1.1.4 フロントエンドの現状

**`FaqManagement.vue`**:
- `lowRatedAnswers`が定義されているが、空配列（モックデータなし）
- コメント: `// 低評価回答リスト（ステップ4でAPI実装予定）`

**`FeedbackStats.vue`**:
- `FeedbackStats`型の`low_rated_answers`を表示
- ダッシュボード用のコンポーネント

**`FeedbackLinkedFaqs.vue`**:
- 低評価回答を表示するコンポーネント
- `lowRatedFaqs`プロップを受け取る

**型定義** (`frontend/src/types/faq.ts`):
```typescript
export interface LowRatedAnswer {
  message_id: number
  question: string
  answer: string
  negative_count: number
}
```

#### 1.1.5 既存のAPIパターン

**`backend/app/api/v1/admin/faqs.py`**:
- JWT認証必須（`get_current_user`）
- 施設IDは`current_user.facility_id`から取得
- エラーハンドリング: `ValueError` → `400 Bad Request`, その他 → `500 Internal Server Error`

**`backend/app/services/faq_service.py`**:
- サービスクラスパターン
- データベースセッションを`__init__`で受け取る
- ログ出力を実装

---

## 2. 実装計画

### 2.1 バックエンド実装

#### 2.1.1 サービスメソッドの実装

**ファイル**: `backend/app/services/feedback_service.py`（新規作成）

**実装内容**:
1. `FeedbackService`クラスを作成
2. `get_negative_feedbacks`メソッドを実装
   - 施設IDを引数に受け取る
   - 低評価フィードバック（`feedback_type='negative'`）を取得
   - メッセージIDごとに低評価数を集計
   - 2回以上低評価がついたメッセージを取得
   - 会話履歴から質問を取得（メッセージの前にある`role='user'`のメッセージ）
   - `LowRatedAnswer`リストを返却

**質問の取得方法**:
- メッセージの`conversation_id`から会話を取得
- 会話内のメッセージを`created_at`でソート
- 特定のメッセージ（AI応答）の前にある`role='user'`のメッセージを取得
- 複数のユーザーメッセージがある場合は、最も近いものを取得

**参考実装**: `escalation_service.py`の`get_unresolved_questions`メソッド

#### 2.1.2 APIエンドポイントの実装

**ファイル**: `backend/app/api/v1/admin/feedback.py`（新規作成）

**実装内容**:
1. `GET /api/v1/admin/feedback/negative`エンドポイントを作成
2. JWT認証必須（`get_current_user`）
3. 施設IDは`current_user.facility_id`から取得
4. `FeedbackService`を使用して低評価回答リストを取得
5. `List[LowRatedAnswer]`を返却

**エラーハンドリング**:
- `ValueError` → `400 Bad Request`
- その他 → `500 Internal Server Error`

#### 2.1.3 スキーマの確認・追加

**ファイル**: `backend/app/schemas/feedback.py`（新規作成、または既存のスキーマに追加）

**実装内容**:
1. `LowRatedAnswer`スキーマを確認（既に`dashboard.py`に存在）
2. 必要に応じて`feedback.py`に移動またはインポート

**注意**: `LowRatedAnswer`は既に`dashboard.py`に定義されているため、重複を避ける

#### 2.1.4 ルーターの登録

**ファイル**: `backend/app/api/v1/admin/__init__.py`または`backend/app/main.py`

**実装内容**:
1. `feedback.py`のルーターを`main.py`に登録
2. 既存のパターンに従う

---

### 2.2 フロントエンド実装

#### 2.2.1 APIクライアントの実装

**ファイル**: `frontend/src/api/feedback.ts`（新規作成）

**実装内容**:
1. `getNegativeFeedbacks`関数を実装
2. `GET /api/v1/admin/feedback/negative`を呼び出す
3. `LowRatedAnswer[]`を返却
4. 既存のAPIクライアントパターンに従う（`faq.ts`を参考）

#### 2.2.2 コンポーネントの修正

**ファイル**: `frontend/src/views/admin/FaqManagement.vue`

**実装内容**:
1. `feedbackApi`をインポート
2. `fetchLowRatedAnswers`関数を実装
3. `onMounted`で`fetchLowRatedAnswers`を呼び出す
4. モックデータのコメントを削除（既にモックデータは使用されていない）

**ファイル**: `frontend/src/components/admin/FeedbackLinkedFaqs.vue`（必要に応じて）

**実装内容**:
1. 親コンポーネントから`lowRatedFaqs`を受け取る（既に実装済み）
2. 修正不要（親コンポーネントでデータを取得する）

---

## 3. 大原則への準拠確認

### 3.1 根本解決 > 暫定解決

**評価**: ✅ **準拠**

**理由**:
- モックデータを削除し、実際のAPIからデータを取得する
- 質問の取得を正しく実装する（既存のTODOを解決）

### 3.2 シンプル構造 > 複雑構造

**評価**: ✅ **準拠**

**理由**:
- 既存のAPIパターンに従う
- 既存のサービスパターンに従う
- モックデータを削除してシンプルに

### 3.3 統一・同一化 > 特殊独自

**評価**: ✅ **準拠**

**理由**:
- 既存のAPIエンドポイントパターンに従う（`/api/v1/admin/faqs`を参考）
- 既存のサービスパターンに従う（`FAQService`を参考）
- 既存のAPIクライアントパターンに従う（`faq.ts`を参考）

### 3.4 具体的 > 一般

**評価**: ✅ **準拠**

**理由**:
- 具体的なAPIエンドポイントを実装
- 具体的なサービスメソッドを実装
- 具体的な型定義を使用

### 3.5 拙速 < 安全確実

**評価**: ✅ **準拠**

**理由**:
- バックアップを作成してから実装
- 既存のパターンに従う
- エラーハンドリングを実装
- ログ出力を実装

**総合評価**: ✅ **大原則に完全準拠**

---

## 4. 実装手順

### 4.1 バックエンド実装

1. **バックアップ作成**
   - 関連ファイルのバックアップを作成

2. **サービスメソッドの実装**
   - `backend/app/services/feedback_service.py`を作成
   - `get_negative_feedbacks`メソッドを実装

3. **APIエンドポイントの実装**
   - `backend/app/api/v1/admin/feedback.py`を作成
   - `GET /api/v1/admin/feedback/negative`エンドポイントを実装

4. **ルーターの登録**
   - `backend/app/main.py`にルーターを登録

5. **動作確認**
   - APIエンドポイントが正常に動作することを確認

### 4.2 フロントエンド実装

1. **バックアップ作成**
   - 関連ファイルのバックアップを作成

2. **APIクライアントの実装**
   - `frontend/src/api/feedback.ts`を作成
   - `getNegativeFeedbacks`関数を実装

3. **コンポーネントの修正**
   - `frontend/src/views/admin/FaqManagement.vue`を修正
   - `fetchLowRatedAnswers`関数を実装

4. **動作確認**
   - フロントエンドで低評価回答リストが正常に表示されることを確認

---

## 5. 実装の詳細

### 5.1 質問の取得方法（詳細）

**問題**: メッセージ（AI応答）に対応する質問を取得する必要がある

**解決方法**:
1. メッセージの`conversation_id`から会話を取得
2. 会話内のメッセージを`created_at`でソート
3. 特定のメッセージ（AI応答）の前にある`role='user'`のメッセージを取得
4. 複数のユーザーメッセージがある場合は、最も近いものを取得（`created_at`が最も近いもの）

**実装例**:
```python
# 会話内のメッセージを取得
messages_result = await self.db.execute(
    select(Message)
    .where(Message.conversation_id == message.conversation_id)
    .order_by(Message.created_at.asc())
)
messages = messages_result.scalars().all()

# 特定のメッセージ（AI応答）の前にあるユーザーメッセージを取得
question = None
for msg in reversed(messages):
    if msg.id == message.id:
        break
    if msg.role == MessageRole.USER.value:
        question = msg.content
        break
```

### 5.2 エラーハンドリング

**バックエンド**:
- `ValueError` → `400 Bad Request`
- その他 → `500 Internal Server Error`
- ログ出力を実装

**フロントエンド**:
- エラーメッセージを適切に表示
- エラー時は空配列を返す（既存のパターンに従う）

---

## 6. まとめ

### 6.1 実装内容

1. **バックエンド**:
   - `backend/app/services/feedback_service.py`を作成
   - `backend/app/api/v1/admin/feedback.py`を作成
   - `backend/app/main.py`にルーターを登録

2. **フロントエンド**:
   - `frontend/src/api/feedback.ts`を作成
   - `frontend/src/views/admin/FaqManagement.vue`を修正

### 6.2 大原則への準拠

✅ **すべての実装は大原則に完全準拠**

### 6.3 次のステップ

1. バックアップを作成
2. バックエンド実装
3. フロントエンド実装
4. 動作確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ✅ **完全調査分析完了 → 実装計画提示完了**


