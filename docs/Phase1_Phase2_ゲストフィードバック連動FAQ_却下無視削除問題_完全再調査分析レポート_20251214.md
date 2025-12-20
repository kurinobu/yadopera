# Phase 1・Phase 2: ゲストフィードバック連動FAQ 却下・無視削除問題 完全再調査分析レポート

**作成日**: 2025年12月14日  
**実施者**: AI Assistant  
**対象**: ゲストフィードバック連動FAQの却下・無視削除問題の完全再調査分析  
**状態**: 🔍 **完全再調査分析完了**

---

## 1. 問題の概要

### 1.1 報告された問題

**問題**: 「却下」ボタンをクリックすると「却下しますか」というモーダルが表示され、OKしても表示も動作も変わらない。その後「FAQ改善提案」ボタンをクリックしても変わらず、普通に再度編集画面が表示される。また「無視」ボタンをクリックしても何も変わらない。結果、エラーは出なくなったが改善されていない。

**ユーザーの質問**:
- この動作は正しいのですか？
- 無視や却下しても削除されることなく永遠に表示されるのですか？

---

## 2. データベースの実際の状態

### 2.1 低評価フィードバックデータ

**message_id = 28**:
- **ID 1**: `feedback_type = "negative"`, `created_at = 2025-12-03 05:39:24`
- **ID 9**: `feedback_type = "negative"`, `created_at = 2025-12-04 00:48:23`
- **低評価数**: 2回

**message_id = 32**:
- **ID 3**: `feedback_type = "negative"`, `created_at = 2025-12-03 05:39:35`
- **ID 10**: `feedback_type = "negative"`, `created_at = 2025-12-04 00:48:24`
- **低評価数**: 2回

### 2.2 FAQ提案データ

**source_message_id = 28**:
- **ID 1**: `status = "approved"`
- **ID 2**: `status = "rejected"`
- **ID 15**: `status = "pending"`
- **ID 16**: `status = "pending"`

**source_message_id = 32**:
- **ID 14**: `status = "rejected"`

---

## 3. 現在の実装の動作分析

### 3.1 「却下」ボタンの動作フロー

**ステップ1**: ユーザーが「却下」ボタンをクリック
- `FaqSuggestionCard.vue`の`handleReject`関数が呼び出される
- `confirm('この提案を却下しますか？')`で確認モーダルが表示される

**ステップ2**: ユーザーがOKをクリック
- `faqSuggestionApi.rejectSuggestion(props.suggestion.id)`が呼び出される
- バックエンドでFAQ提案の`status`が`"rejected"`に更新される

**ステップ3**: `emit('reject', props.suggestion)`が発火
- 親コンポーネント（`FaqManagement.vue`）の`handleRejectSuggestion`関数が呼び出される
- `selectedSuggestion.value = null`が設定される（FAQ提案編集画面が閉じる）
- `fetchLowRatedAnswers()`が呼び出される（修正後）

**ステップ4**: `fetchLowRatedAnswers()`が実行される
- `/admin/feedback/negative`エンドポイントから低評価回答リストを取得
- `get_negative_feedbacks`関数が実行される
- **問題**: 低評価フィードバック自体は削除されていないため、同じ低評価回答が返される

**結果**: 
- ✅ FAQ提案は却下される（`status = "rejected"`）
- ✅ FAQ提案編集画面は閉じる（`selectedSuggestion.value = null`）
- ❌ **低評価回答は画面に残り続ける**（低評価フィードバックが削除されていないため）

### 3.2 「無視」ボタンの動作フロー

**ステップ1**: ユーザーが「無視」ボタンをクリック
- `FeedbackLinkedFaqs.vue`の`handleIgnore`関数が呼び出される
- `emit('ignore', answer)`が発火

**ステップ2**: 親コンポーネント（`FaqManagement.vue`）の`handleFeedbackIgnore`関数が呼び出される
- **現在の実装**: `console.log('Feedback ignore:', answer)`のみ
- **問題**: 何も処理されない

**結果**: 
- ❌ **何も処理されない**（TODOコメントのみ）
- ❌ **低評価回答は画面に残り続ける**

### 3.3 「FAQ改善提案」ボタンの動作フロー

**ステップ1**: ユーザーが「FAQ改善提案」ボタンをクリック
- `handleFeedbackImprove`関数が呼び出される
- `faqSuggestionApi.generateSuggestion(answer.message_id)`が呼び出される

**ステップ2**: バックエンドで既存の`pending`ステータスのFAQ提案を確認
- **修正後**: `order_by(created_at.desc()).limit(1)`を使用して最新の1件を取得
- 既存のFAQ提案（ID 15または16）が返される

**ステップ3**: 既存のFAQ提案が返される
- `selectedSuggestion.value`に既存のFAQ提案が設定される
- FAQ提案編集画面が表示される

**結果**: 
- ✅ エラーは発生しない（修正後）
- ✅ FAQ提案編集画面が表示される
- ⚠️ **既存のFAQ提案が表示される**（新規生成されない）

---

## 4. 根本原因の分析

### 4.1 問題1: 「却下」ボタンをクリックしても低評価回答が削除されない

#### 4.1.1 根本原因

**根本原因**: **FAQ提案を却下しても、低評価フィードバック自体は削除されない**

**詳細**:
1. **FAQ提案と低評価フィードバックの関係**:
   - FAQ提案（`faq_suggestions`）: 低評価回答から生成される提案
   - 低評価フィードバック（`guest_feedback`）: ゲストが実際に送信した低評価
   - **これらは独立したデータ**であり、FAQ提案を却下しても低評価フィードバックは削除されない

2. **低評価回答リストの取得ロジック**:
   - `/admin/feedback/negative`エンドポイントは、**「2回以上低評価がついたメッセージ」**を返す
   - 低評価フィードバックが存在する限り、低評価回答リストに含まれる
   - FAQ提案を却下しても、低評価フィードバックは削除されないため、同じ低評価回答が返される

3. **現在の修正の限界**:
   - `fetchLowRatedAnswers()`を呼び出しても、低評価フィードバックが削除されていないため、同じ低評価回答が返される
   - そのため、画面に低評価回答が残り続ける

#### 4.1.2 ユーザーの期待と実装のギャップ

**ユーザーの期待**:
- 「却下」をクリックしたら、その低評価回答が画面から削除される
- つまり、低評価回答を「処理済み」として扱い、画面から非表示にしたい

**現在の実装**:
- 「却下」はFAQ提案を却下するだけで、低評価回答自体は削除されない
- 低評価回答は「処理済み」として扱われない

**ギャップ**: 
- ユーザーの期待: 低評価回答を「処理済み」として非表示にする
- 現在の実装: FAQ提案を却下するだけで、低評価回答は非表示にならない

### 4.2 問題2: 「無視」ボタンをクリックしても何も変わらない

#### 4.2.1 根本原因

**根本原因**: **「無視」機能が実装されていない**

**詳細**:
1. **現在の実装**:
   - `handleFeedbackIgnore`関数は`console.log`のみ
   - TODOコメント: "Week 4でAPI連携を実装（ステップ4で実装予定）"

2. **必要な機能**:
   - 低評価回答を「無視」する機能
   - 無視した低評価回答を画面から非表示にする機能

### 4.3 問題3: 「FAQ改善提案」ボタンをクリックしても既存のFAQ提案が表示される

#### 4.3.1 根本原因

**根本原因**: **既存の`pending`ステータスのFAQ提案が存在するため、新規生成されずに既存の提案が返される**

**詳細**:
1. **`generate_suggestion`関数の動作**:
   - 既存の`pending`ステータスのFAQ提案を確認
   - 既存の提案が存在する場合、新規生成せずに既存の提案を返す

2. **ユーザーの期待**:
   - 「FAQ改善提案」ボタンをクリックしたら、新しいFAQ提案が生成される
   - または、既存のFAQ提案が表示される

3. **現在の動作**:
   - 既存のFAQ提案（ID 15または16）が返される
   - これは**正しい動作**（重複を防ぐため）

---

## 5. 設計上の問題

### 5.1 低評価回答の「処理済み」状態の管理

**現在の設計**:
- 低評価回答リストは「2回以上低評価がついたメッセージ」を返す
- 低評価回答を「処理済み」として扱う仕組みがない

**必要な設計**:
- 低評価回答を「処理済み」として扱う仕組み
- 処理済みの低評価回答を画面から非表示にする機能

### 5.2 「却下」と「無視」の意味の明確化

**現在の実装**:
- 「却下」: FAQ提案を却下する（低評価回答自体は削除されない）
- 「無視」: 実装されていない

**ユーザーの期待**:
- 「却下」: 低評価回答を処理済みとして非表示にする
- 「無視」: 低評価回答を処理済みとして非表示にする

**設計上の問題**:
- 「却下」と「無視」の意味が明確でない
- ユーザーの期待と実装が一致していない

---

## 6. 解決策の検討

### 6.1 解決策A: 低評価回答を「無視」する機能を実装（推奨）

**内容**:
1. **データベースに「無視」状態を保存する仕組みを追加**
   - オプション1: `guest_feedback`テーブルに`ignored`カラムを追加
   - オプション2: 新しいテーブル`ignored_feedbacks`を作成
   - オプション3: `faq_suggestions`テーブルに`ignored_at`カラムを追加（低評価回答を無視したことを記録）

2. **バックエンドAPIエンドポイントの追加**:
   - `POST /admin/feedback/{message_id}/ignore`: 低評価回答を無視する
   - `get_negative_feedbacks`関数で、無視された低評価回答を除外

3. **フロントエンドの実装**:
   - 「無視」ボタンの処理を実装
   - 無視した低評価回答を画面から削除

**メリット**:
- ユーザーの期待に沿った動作
- 低評価回答を「処理済み」として管理できる

**デメリット**:
- データベーススキーマの変更が必要
- 実装が複雑になる

### 6.2 解決策B: 「却下」ボタンの動作を変更（非推奨）

**内容**:
- FAQ提案を却下した際に、対応する低評価回答も「無視」として扱う

**メリット**:
- 既存の実装を活用できる

**デメリット**:
- 「却下」と「無視」の意味が曖昧になる
- ユーザーの期待と一致しない可能性がある

### 6.3 解決策C: 低評価フィードバックを削除する（非推奨）

**内容**:
- 「却下」や「無視」をクリックした際に、低評価フィードバックを削除

**メリット**:
- シンプルな実装

**デメリット**:
- **データの整合性の問題**: ゲストが実際に送信したフィードバックを削除するのは適切でない
- **統計データの損失**: 低評価フィードバックは統計データとして重要
- **大原則違反**: 根本解決ではなく、データを削除する暫定解決

---

## 7. 推奨される解決策

### 7.1 解決策A: 低評価回答を「無視」する機能を実装

**実装内容**:

#### 7.1.1 データベーススキーマの変更

**オプション1: `guest_feedback`テーブルに`ignored`カラムを追加（推奨）**

**マイグレーション**:
```python
# alembic/versions/XXX_add_ignored_to_guest_feedback.py
def upgrade():
    op.add_column('guest_feedback', sa.Column('ignored', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('guest_feedback', sa.Column('ignored_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('guest_feedback', sa.Column('ignored_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
```

**メリット**:
- シンプルな実装
- 既存のテーブルを拡張するだけ

**デメリット**:
- `guest_feedback`テーブルはゲストが送信したフィードバックを記録するテーブル
- 「無視」は管理者の操作であり、ゲストフィードバックテーブルに含めるのは設計上適切でない可能性がある

**オプション2: 新しいテーブル`ignored_feedbacks`を作成（推奨）**

**マイグレーション**:
```python
# alembic/versions/XXX_create_ignored_feedbacks_table.py
def upgrade():
    op.create_table(
        'ignored_feedbacks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('message_id', sa.Integer(), sa.ForeignKey('messages.id'), nullable=False),
        sa.Column('facility_id', sa.Integer(), sa.ForeignKey('facilities.id'), nullable=False),
        sa.Column('ignored_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ignored_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.UniqueConstraint('message_id', 'facility_id', name='uq_ignored_feedback_message_facility')
    )
```

**メリット**:
- 設計上適切（管理者の操作を別テーブルで管理）
- ゲストフィードバックテーブルを汚染しない

**デメリット**:
- 新しいテーブルを作成する必要がある

#### 7.1.2 バックエンドAPIエンドポイントの追加

**ファイル**: `backend/app/api/v1/admin/feedback.py`

**追加内容**:
```python
@router.post("/{message_id}/ignore")
async def ignore_negative_feedback(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    低評価回答を無視
    
    JWT認証必須。指定されたメッセージIDの低評価回答を無視します。
    """
    # 実装
```

#### 7.1.3 バックエンドサービスの実装

**ファイル**: `backend/app/services/feedback_service.py`

**追加内容**:
```python
async def ignore_negative_feedback(
    self,
    message_id: int,
    facility_id: int,
    user_id: int
) -> None:
    """
    低評価回答を無視
    
    Args:
        message_id: メッセージID
        facility_id: 施設ID
        user_id: 無視したユーザーID
    """
    # 実装
```

#### 7.1.4 `get_negative_feedbacks`関数の修正

**修正内容**:
- 無視された低評価回答を除外する処理を追加

#### 7.1.5 フロントエンドの実装

**ファイル**: `frontend/src/views/admin/FaqManagement.vue`

**修正内容**:
```typescript
const handleFeedbackIgnore = async (answer: LowRatedAnswer) => {
  if (!confirm('この低評価回答を無視しますか？')) {
    return
  }
  
  try {
    await feedbackApi.ignoreNegativeFeedback(answer.message_id)
    // 低評価回答リストを再取得
    await fetchLowRatedAnswers()
  } catch (err: any) {
    console.error('Failed to ignore negative feedback:', err)
    alert(err.response?.data?.detail || '低評価回答の無視に失敗しました')
  }
}
```

### 7.2 「却下」ボタンの動作の明確化

**現在の動作**:
- FAQ提案を却下する
- 低評価回答は削除されない

**推奨される動作**:
- FAQ提案を却下する
- オプション: 対応する低評価回答も「無視」として扱う（ユーザーの期待に沿う）

**実装方法**:
- `reject_suggestion`関数で、対応する低評価回答も「無視」として扱う処理を追加

---

## 8. まとめ

### 8.1 問題の原因

1. **「却下」ボタン**: FAQ提案を却下しても、低評価フィードバック自体は削除されないため、低評価回答が画面に残り続ける
2. **「無視」ボタン**: 実装されていない（TODOコメントのみ）
3. **「FAQ改善提案」ボタン**: 既存の`pending`ステータスのFAQ提案が存在するため、新規生成されずに既存の提案が返される（これは正しい動作）

### 8.2 ユーザーの期待と実装のギャップ

**ユーザーの期待**:
- 「却下」や「無視」をクリックしたら、その低評価回答が画面から削除される
- 低評価回答を「処理済み」として扱い、画面から非表示にしたい

**現在の実装**:
- 「却下」: FAQ提案を却下するだけで、低評価回答は削除されない
- 「無視」: 実装されていない

**ギャップ**: 
- ユーザーの期待: 低評価回答を「処理済み」として非表示にする
- 現在の実装: 低評価回答を「処理済み」として扱う仕組みがない

### 8.3 修正が必要な箇所

1. **「無視」機能の実装**: 低評価回答を無視する機能を実装（データベーススキーマの変更、APIエンドポイントの追加、フロントエンドの実装）
2. **「却下」ボタンの動作の明確化**: FAQ提案を却下した際に、対応する低評価回答も「無視」として扱う（オプション）
3. **`get_negative_feedbacks`関数の修正**: 無視された低評価回答を除外する処理を追加

---

**調査完了日**: 2025年12月14日  
**次回**: 修正指示を待つ

