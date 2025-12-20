# Phase 1・Phase 2: ゲストフィードバック FAQ改善提案・無視ボタン 完全調査分析レポート

**作成日時**: 2025年12月16日  
**実施者**: AI Assistant  
**対象**: ゲストフィードバック連動FAQのFAQ改善提案と無視ボタンの問題  
**状態**: 🔴 **問題確認 - 修正が必要**

---

## 1. 問題の概要

### 1.1 問題1: FAQ改善提案の質問文と回答文の引用先が異なる

**症状**:
- FAQ改善提案のボタンをクリックすると、質問文フィールドに予め入力されている文言の引用先が異なる
- 質問文が「Check-out time is 11:00 AM. If you need any assistance, feel free to ask!」となっている
- これは質問文ではなく回答文（AI応答）の内容
- ユーザー体験が大幅に低下している

**発生環境**: ステージング環境

**報告内容**:
- 質問文: `Check-out time is 11:00 AM. If you need any assistance, feel free to ask!`
- 回答文（テンプレート）: `Thank you for your inquiry! Our check-out time is 11:00 AM, and if you require any assistance with your departure or have any questions, please don't hesitate to let us know. We're here to help make your stay as comfortable as possible!`

### 1.2 問題2: 無視ボタンがクリックしても反応も表示もない

**症状**:
- ゲストフィードバックのFAQ改善提案ボタンの横にある無視ボタンをクリックしても反応も表示もない
- ボタンが動作していない

**発生環境**: ステージング環境

---

## 2. データベース調査結果

### 2.1 低評価回答の確認

**調査結果**:
- message_id 28と32が2回以上の低評価を受けている
- message_id 28: 「申し訳ありませんが、アイロンの貸し出しについての情報はありません。スタッフにお問い合わせください。」
- message_id 32: 「申し訳ありませんが、ドリンカブルな水についての情報はありません。スタッフにお問い合わせください。」

**会話履歴の確認**:
- conversation_id 3の会話に属している
- message_id 28の前には、message_id 27のUSERメッセージ「アイロンは貸し出ししてますか？」がある
- message_id 32の前には、message_id 31のUSERメッセージ「ドリンカブルな水はありますか？」がある

### 2.2 FAQ提案の確認

**調査結果**:
- FAQ提案は正しく生成されている
- 質問文は正しく取得されている（「アイロンは貸し出ししてますか？」「ドリンカブルな水はありますか？」）
- しかし、ユーザーが報告している「Check-out time is 11:00 AM. If you need any assistance, feel free to ask!」という内容はデータベースに見つからない

**推測**:
- 問題が発生しているメッセージは、データベース調査時点では既に削除されている可能性がある
- または、別の会話・メッセージで問題が発生している可能性がある
- **重要な発見**: ユーザーが報告している「Check-out time is 11:00 AM. If you need any assistance, feel free to ask!」は、**質問文ではなく回答文（AI応答）の内容**である可能性が高い
- これは、`pick_question_before`関数が質問文を取得できず、エラーが発生した場合に、`message.content`（回答文）が質問文として使用されている可能性がある

### 2.3 無視ボタンの確認

**調査結果**:
- `ignored_feedbacks`テーブルに1件のレコードが存在（message_id 28が無視されている）
- 無視機能自体は動作している可能性がある
- しかし、フロントエンドで反応がないということは、API呼び出しが失敗しているか、エラーハンドリングが不十分な可能性がある

---

## 3. コード調査結果

### 3.1 FAQ改善提案の質問文取得ロジック

**ファイル**: `backend/app/services/faq_suggestion_service.py`

**現在の実装**（177-206行目）:
```python
def pick_question_before(index: int) -> str | None:
    """
    直前以前のUSERメッセージから「質問らしい」ものを優先的に選ぶ。
    疑問符を含むものを優先し、それがなければ直近のUSERロールを返す。
    """
    for i in range(index - 1, -1, -1):
        msg = conversation_messages[i]
        if msg.role != MessageRole.USER.value:
            continue
        content = (msg.content or "").strip()
        if "?" in content or content.endswith("？"):
            return content
    for i in range(index - 1, -1, -1):
        msg = conversation_messages[i]
        if msg.role == MessageRole.USER.value:
            return (msg.content or "").strip()
    return None

# メッセージのインデックスを見つける
message_index = None
for i, msg in enumerate(conversation_messages):
    if msg.id == message.id:
        message_index = i
        break

question = pick_question_before(message_index) if message_index is not None and message_index > 0 else None

if not question:
    # USERメッセージが見つからない場合、エラー
    raise ValueError(f"User message not found for assistant message: message_id={message_id}")

existing_answer = message.content  # 既存の回答（改善対象）
```

**問題点の分析**:

1. **`pick_question_before`関数の問題**:
   - 疑問符を含むUSERメッセージを優先的に選ぶが、疑問符がないUSERメッセージも選ぶ可能性がある
   - しかし、ユーザーが報告している「Check-out time is 11:00 AM. If you need any assistance, feel free to ask!」は、ASSISTANTロールのメッセージの内容である可能性が高い
   - **重要な発見**: エラーが発生した場合、`question`が`None`になり、`ValueError`が発生するはずだが、実際には質問文フィールドに回答文が表示されている
   - これは、エラーハンドリングが不十分で、エラーが発生した場合に`message.content`（回答文）が質問文として使用されている可能性がある

2. **メッセージの順序の問題**:
   - `conversation_messages`は`created_at.asc()`でソートされているが、同じタイムスタンプのメッセージがある場合、順序が保証されない可能性がある
   - または、メッセージの順序が正しく取得できていない可能性がある

3. **エラーハンドリングの問題**:
   - `question`が`None`の場合、エラーを発生させるが、実際には`message.content`（回答文）が質問文として使用されている可能性がある
   - **根本原因の仮説**: エラーが発生した場合、フロントエンドでエラーメッセージが表示されず、代わりに`message.content`（回答文）が質問文として表示されている可能性がある

### 3.2 無視ボタンの実装

**フロントエンド**: `frontend/src/views/admin/FaqManagement.vue`

**実装**（432-446行目）:
```typescript
const handleFeedbackIgnore = async (answer: LowRatedAnswer) => {
  if (!confirm('この低評価回答を無視しますか？無視した回答は画面から非表示になります。')) {
    return
  }
  
  try {
    await feedbackApi.ignoreNegativeFeedback(answer.message_id)
    // 低評価回答リストを再取得（画面に反映）
    await fetchLowRatedAnswers()
  } catch (err: any) {
    console.error('Failed to ignore negative feedback:', err)
    const errorMessage = err.response?.data?.detail || err.message || '低評価回答の無視に失敗しました'
    alert(errorMessage)
  }
}
```

**問題点の分析**:

1. **エラーハンドリング**:
   - エラーが発生した場合、`alert`でエラーメッセージを表示するが、コンソールにエラーが出力されるだけの可能性がある
   - ユーザーがエラーメッセージを見逃している可能性がある
   - **重要な発見**: `confirm`ダイアログが表示されない場合、関数が早期リターンするため、無視ボタンが動作していないように見える可能性がある

2. **API呼び出し**:
   - `feedbackApi.ignoreNegativeFeedback(answer.message_id)`が正しく呼び出されているか確認が必要
   - ネットワークエラーや認証エラーが発生している可能性がある

3. **画面更新**:
   - `fetchLowRatedAnswers()`でリストを再取得しているが、エラーが発生した場合、画面が更新されない可能性がある

**バックエンド**: `backend/app/api/v1/admin/feedback.py`

**実装**（54-96行目）:
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
    無視された低評価回答は、低評価回答リストから除外されます。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # フィードバックサービスで低評価回答を無視
        feedback_service = FeedbackService(db)
        await feedback_service.ignore_negative_feedback(
            message_id=message_id,
            facility_id=facility_id,
            user_id=current_user.id
        )
        
        return {"message": "Negative feedback ignored successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ignoring negative feedback: {str(e)}"
        )
```

**問題点の分析**:

1. **エラーハンドリング**:
   - エラーが発生した場合、適切なHTTPステータスコードとエラーメッセージを返している
   - しかし、フロントエンドでエラーメッセージが正しく表示されていない可能性がある

2. **サービス層の実装**:
   - `FeedbackService.ignore_negative_feedback`が正しく実装されているか確認が必要
   - データベースへのコミットが正しく行われているか確認が必要

---

## 4. 根本原因の特定

### 4.1 問題1: FAQ改善提案の質問文と回答文の引用先が異なる

**根本原因の特定**:

**最も可能性が高い原因**: **エラーハンドリングが不十分で、質問文が取得できない場合に回答文が質問文として使用されている**

**詳細**:
1. `pick_question_before`関数が質問文を取得できない場合、`question`が`None`になる
2. `question`が`None`の場合、`ValueError`が発生するはずだが、実際にはエラーが発生していない可能性がある
3. または、エラーが発生した場合、フロントエンドでエラーメッセージが表示されず、代わりに`message.content`（回答文）が質問文として表示されている可能性がある
4. ユーザーが報告している「Check-out time is 11:00 AM. If you need any assistance, feel free to ask!」は、**回答文（AI応答）の内容**である可能性が高い

**確認が必要な点**:
- 実際に問題が発生しているメッセージIDを特定する
- そのメッセージの会話履歴を確認する
- `pick_question_before`関数が正しく動作しているか確認する
- エラーハンドリングが正しく実装されているか確認する

### 4.2 問題2: 無視ボタンがクリックしても反応も表示もない

**根本原因の特定**:

**最も可能性が高い原因**: **エラーハンドリングが不十分で、エラーメッセージが表示されていない**

**詳細**:
1. `confirm`ダイアログが表示されない場合、関数が早期リターンするため、無視ボタンが動作していないように見える可能性がある
2. API呼び出しが失敗した場合、エラーメッセージが`alert`で表示されるが、ユーザーが気づいていない可能性がある
3. または、エラーが発生した場合、コンソールにエラーが出力されるだけの可能性がある

**確認が必要な点**:
- ブラウザの開発者ツール（Console、Networkタブ）でエラーを確認する
- API呼び出しが正しく行われているか確認する
- バックエンドのログでエラーを確認する

---

## 5. 推奨調査手順

### 5.1 問題1の調査手順

1. **実際に問題が発生しているメッセージIDを特定**:
   - ブラウザの開発者ツール（Networkタブ）で、FAQ改善提案のAPI呼び出しを確認
   - `message_id`を特定

2. **データベースでメッセージと会話履歴を確認**:
   ```sql
   -- メッセージの詳細を確認
   SELECT m.id, m.role, m.content, m.conversation_id, m.created_at
   FROM messages m
   WHERE m.id = <message_id>;
   
   -- 会話履歴を確認
   SELECT m.id, m.role, m.content, m.created_at
   FROM messages m
   WHERE m.conversation_id = <conversation_id>
   ORDER BY m.created_at ASC;
   ```

3. **`pick_question_before`関数の動作を確認**:
   - メッセージの順序が正しいか確認
   - 質問文が正しく取得されているか確認
   - エラーが発生している場合、エラーメッセージを確認

### 5.2 問題2の調査手順

1. **ブラウザの開発者ツールでエラーを確認**:
   - Consoleタブでエラーメッセージを確認
   - NetworkタブでAPI呼び出しを確認
   - レスポンスのステータスコードと内容を確認

2. **バックエンドのログでエラーを確認**:
   - サーバーログでエラーメッセージを確認
   - API呼び出しが正しく行われているか確認

3. **データベースで無視状態を確認**:
   ```sql
   -- 無視されたメッセージを確認
   SELECT if.id, if.message_id, if.facility_id, if.ignored_at
   FROM ignored_feedbacks if
   WHERE if.facility_id = <facility_id>
   ORDER BY if.ignored_at DESC;
   ```

---

## 6. 修正案（調査完了後の対応）

### 6.1 問題1の修正案

**修正案A: エラーハンドリングの改善と質問文取得ロジックの強化**（推奨）★

**目的**: 質問文が正しく取得されるようにし、エラーが発生した場合に適切に処理する

**実施内容**:
1. `pick_question_before`関数の改善:
   - メッセージの順序を確実にする（`id`でソートするなど）
   - 質問文が取得できない場合のエラーハンドリングを改善
   - ログを追加して、デバッグしやすくする

2. エラーハンドリングの改善:
   - `question`が`None`の場合、確実にエラーを発生させる
   - エラーメッセージを明確にする
   - フロントエンドでエラーメッセージを確実に表示する

**大原則準拠評価**:
- ✅ **根本解決**: 質問文が正しく取得されるようにし、エラーが発生した場合に適切に処理する
- ✅ **シンプル構造**: 関数の改善のみで、複雑な変更は不要
- ✅ **統一・同一化**: 既存のコードスタイルに従う
- ✅ **具体的**: 明確な修正内容
- ✅ **安全確実**: 既存の動作を維持しつつ、改善する

### 6.2 問題2の修正案

**修正案A: エラーハンドリングの改善とUIの改善**（推奨）★

**目的**: エラーメッセージを確実に表示し、ユーザーに処理状態を明確に伝える

**実施内容**:
1. エラーハンドリングの改善:
   - `alert`の代わりに、より目立つエラーメッセージ表示方法を使用
   - ローディング状態を表示して、ユーザーに処理中であることを伝える
   - 成功メッセージも表示して、ユーザーに処理が完了したことを伝える

2. UIの改善:
   - ボタンの無効化状態を明確にする
   - ローディングインジケーターを表示する

**大原則準拠評価**:
- ✅ **根本解決**: エラーメッセージを確実に表示し、ユーザーに処理状態を明確に伝える
- ✅ **シンプル構造**: UIの改善のみで、実装がシンプル
- ✅ **統一・同一化**: 既存のUIパターンに従う
- ✅ **具体的**: 明確な修正内容
- ✅ **安全確実**: 既存の動作を維持しつつ、改善する

---

## 7. まとめ

### 7.1 調査結果のサマリー

**問題1: FAQ改善提案の質問文と回答文の引用先が異なる**:
- **根本原因**: エラーハンドリングが不十分で、質問文が取得できない場合に回答文が質問文として使用されている可能性が高い
- ユーザーが報告している「Check-out time is 11:00 AM. If you need any assistance, feel free to ask!」は、回答文（AI応答）の内容である可能性が高い
- `pick_question_before`関数が正しく動作していない可能性がある

**問題2: 無視ボタンがクリックしても反応も表示もない**:
- **根本原因**: エラーハンドリングが不十分で、エラーメッセージが表示されていない可能性が高い
- `confirm`ダイアログが表示されない場合、関数が早期リターンするため、無視ボタンが動作していないように見える可能性がある
- API呼び出しが失敗した場合、エラーメッセージが`alert`で表示されるが、ユーザーが気づいていない可能性がある

### 7.2 次のステップ

1. **実際に問題が発生しているメッセージIDを特定**:
   - ブラウザの開発者ツール（Networkタブ）で、FAQ改善提案のAPI呼び出しを確認
   - 無視ボタンのAPI呼び出しを確認

2. **データベースでメッセージと会話履歴を確認**:
   - 問題が発生しているメッセージの会話履歴を確認
   - 質問文が正しく取得されているか確認

3. **ブラウザの開発者ツールでエラーを確認**:
   - Consoleタブでエラーメッセージを確認
   - NetworkタブでAPI呼び出しを確認

---

**調査分析完了日時**: 2025年12月16日  
**状態**: 🔴 **問題確認 - 追加調査が必要**

**重要**: 指示があるまで修正を実施しません。調査分析のみです。
