# Phase 1・Phase 2: FAQ追加提案 質問文・回答文マッピング 完全調査分析レポート

**作成日**: 2025年12月14日  
**実施者**: AI Assistant  
**対象**: FAQ追加提案編集ページの質問文・回答文マッピング問題の完全調査分析  
**状態**: 🔍 **調査分析完了**

---

## 1. 問題の概要

### 1.1 報告された問題

**1件目**:
- **質問文**: 「申し訳ありませんが、アイロンの貸し出しについての情報はありません。スタッフにお問い合わせください。」（これは回答）
- **回答文（テンプレート）**: 「We apologize for the inconvenience, but we currently do not have information available regarding iron rentals. Please feel free to reach out to our staff, and they will be happy to assist you with any inquiries you may have.」（これも回答）

**2件目**:
- **質問文**: 「ドリンカブルな水はありますか？」（正しい質問）
- **回答文（テンプレート）**: 「Yes, we do provide drinkable water for our guests. You can find it available in the common areas, and if you have any specific requests or need assistance, our staff would be more than happy to help you. Please feel free to reach out to them at any time!」（英語の回答、質問は日本語）

---

## 2. データベースの実際の状態

### 2.1 メッセージデータ（message_id 28, 32）

**メッセージID 28（アシスタントメッセージ）**:
- **role**: `assistant`
- **content**: 「申し訳ありませんが、アイロンの貸し出しについての情報はありません。スタッフにお問い合わせください。」
- **conversation_id**: 3
- **created_at**: 2025-12-03 04:49:25

**メッセージID 32（アシスタントメッセージ）**:
- **role**: `assistant`
- **content**: 「申し訳ありませんが、ドリンカブルな水についての情報はありません。スタッフにお問い合わせください。」
- **conversation_id**: 3
- **created_at**: 2025-12-03 05:39:12

### 2.2 会話内のメッセージ順序（conversation_id 3）

**メッセージID 28の直前のUSERメッセージ**:
- **メッセージID 27**: `role = user`, `content = "アイロンは貸し出ししてますか？"`, `created_at = 2025-12-03 04:49:25`

**メッセージID 32の直前のUSERメッセージ**:
- **メッセージID 31**: `role = user`, `content = "ドリンカブルな水はありますか？"`, `created_at = 2025-12-03 05:39:12`

### 2.3 会話の言語設定

**conversation_id 3**:
- **guest_language**: `"en"`（英語）

### 2.4 FAQ提案データ

**FAQ提案ID 2（1件目）**:
- **source_message_id**: 28
- **suggested_question**: 「申し訳ありませんが、アイロンの貸し出しについての情報はありません。スタッフにお問い合わせください。」（**回答が質問文に入っている**）
- **suggested_answer**: 「We apologize for the inconvenience, but we currently do not have information available regarding iron rentals. Please feel free to reach out to our staff, and they will be happy to assist you with any inquiries you may have.」
- **language**: `"en"`
- **created_at**: 2025-12-04 01:47:34（**修正前の古いデータ**）

**FAQ提案ID 14（2件目）**:
- **source_message_id**: 32
- **suggested_question**: 「ドリンカブルな水はありますか？」（**正しい質問**）
- **suggested_answer**: 「Yes, we do provide drinkable water for our guests. You can find it available in the common areas, and if you have any specific requests or need assistance, our staff would be more than happy to help you. Please feel free to reach out to them at any time!」（**英語の回答、質問は日本語**）
- **language**: `"en"`
- **created_at**: 2025-12-14 02:23:36（**修正後の新しいデータ**）

---

## 3. 根本原因の分析

### 3.1 問題1: FAQ提案ID 2（1件目）の質問文が回答になっている

**根本原因**: **既存のFAQ提案が修正前のロジックで作成されている**

**詳細**:
1. **作成日時**: 2025-12-04 01:47:34（修正前）
2. **修正前のロジック**: アシスタントメッセージの場合、メッセージの`content`をそのまま質問文として使用していた
3. **結果**: `suggested_question`に回答（アシスタントメッセージの内容）が入ってしまった

**修正後のロジック**（2025-12-14修正）:
- アシスタントメッセージの場合、直前のUSERメッセージを取得して質問文として使用
- しかし、**既存のFAQ提案は修正されない**（データベースに保存済み）

### 3.2 問題2: FAQ提案ID 14（2件目）の回答が英語になっている

**根本原因**: **会話の言語設定（`guest_language`）が英語（`"en"`）になっているため、GPT-4o miniが英語で回答を生成している**

**詳細**:
1. **会話の言語設定**: `conversation_id 3`の`guest_language = "en"`（英語）
2. **質問文の言語**: 日本語（「ドリンカブルな水はありますか？」）
3. **現在のロジック**:
   ```python
   language = message.conversation.guest_language or "en"
   ```
   - 会話の`guest_language`を取得してGPT-4o miniのプロンプトに使用
   - プロンプトに`Language: {language}`を指定
   - そのため、GPT-4o miniが英語で回答を生成

4. **問題点**:
   - 質問文が日本語なのに、回答が英語になっている
   - ユーザー体験が悪い（質問と回答の言語が一致しない）

### 3.3 追加の問題: 質問文の言語検出が行われていない

**現在の実装**:
- `language = message.conversation.guest_language or "en"`
- 会話の言語設定を使用しているが、**実際の質問文の言語を検出していない**

**期待される動作**:
- 質問文の言語を検出（日本語、英語など）
- 検出した言語で回答を生成
- または、質問文の言語と会話の言語設定の両方を考慮

---

## 4. コードの確認

### 4.1 現在の実装（修正後）

**ファイル**: `backend/app/services/faq_suggestion_service.py`

**質問文取得ロジック**（146-181行目）:
```python
# 質問文を取得（ユーザーメッセージから）
# メッセージがASSISTANTの場合は、同じ会話のUSERメッセージを取得
if message.role == MessageRole.ASSISTANT.value:
    # 同じ会話の全メッセージを時系列順で取得
    conversation_messages_result = await self.db.execute(
        select(Message)
        .where(Message.conversation_id == message.conversation_id)
        .order_by(Message.created_at.asc())
    )
    conversation_messages = conversation_messages_result.scalars().all()
    
    # このメッセージ（AI応答）の前にあるユーザーメッセージ（質問）を取得
    question = None
    # メッセージのインデックスを見つける
    message_index = None
    for i, msg in enumerate(conversation_messages):
        if msg.id == message.id:
            message_index = i
            break
    
    if message_index is not None and message_index > 0:
        # インデックスの前にある最後のUSERロールのメッセージを取得
        for i in range(message_index - 1, -1, -1):
            if conversation_messages[i].role == MessageRole.USER.value:
                question = conversation_messages[i].content
                break
    
    if not question:
        # USERメッセージが見つからない場合、エラー
        raise ValueError(f"User message not found for assistant message: message_id={message_id}")
    
    existing_answer = message.content  # 既存の回答（改善対象）
else:
    # USERメッセージの場合
    question = message.content
    existing_answer = None  # 新規FAQ提案

# 会話の言語を取得
language = message.conversation.guest_language or "en"
```

**問題点**:
1. ✅ 質問文の取得ロジックは正しい（修正後）
2. ❌ 言語設定が会話の`guest_language`のみを使用している
3. ❌ 質問文の実際の言語を検出していない

### 4.2 GPT-4o miniプロンプト

**ゲストフィードバック連動の場合**（187-202行目）:
```python
if existing_answer:
    # ゲストフィードバック連動の場合：既存の回答を改善
    prompt = f"""You are an AI assistant helping a guesthouse improve FAQ entries.

Guest question: {question}
Current answer (needs improvement): {existing_answer}

Please generate:
1. An improved answer template (2-3 sentences, professional and friendly, addressing the guest's concern better)
2. A category from: basic, facilities, location, trouble

Format your response as:
ANSWER: [your improved answer template]
CATEGORY: [category]

Language: {language}"""
```

**問題点**:
- `Language: {language}`で会話の言語設定（`"en"`）を指定
- しかし、質問文（`question`）が日本語の場合、回答も日本語で生成すべき

---

## 5. 問題の整理

### 5.1 問題1: 既存のFAQ提案が古いロジックで作成されている

**症状**: FAQ提案ID 2の質問文に回答が入っている

**原因**: 修正前（2025-12-04）のロジックで作成されたデータ

**解決方法**:
1. **既存のFAQ提案を削除して再生成**（推奨）
2. または、既存のFAQ提案を手動で修正

### 5.2 問題2: 質問文の言語と回答文の言語が一致しない

**症状**: FAQ提案ID 14の質問文が日本語なのに、回答文が英語

**原因**: 
1. 会話の`guest_language`が`"en"`（英語）に設定されている
2. 質問文の実際の言語（日本語）を検出していない
3. GPT-4o miniのプロンプトに`Language: en`を指定しているため、英語で回答を生成

**解決方法**:
1. **質問文の言語を検出**（日本語、英語など）
2. 検出した言語で回答を生成
3. または、質問文の言語と会話の言語設定の両方を考慮

---

## 6. 修正方針

### 6.1 既存のFAQ提案の処理

**推奨**: 既存のFAQ提案（ID 2）を削除して再生成

**理由**:
- 修正前のロジックで作成されたデータは修正できない
- 再生成することで、正しい質問文が取得される

### 6.2 言語検出の実装

**修正内容**:
1. **質問文の言語を検出**（簡易的な方法）:
   - 日本語文字（ひらがな、カタカナ、漢字）が含まれているかチェック
   - 含まれていれば`"ja"`、そうでなければ`"en"`（デフォルト）

2. **言語の優先順位**:
   - 質問文の言語 > 会話の言語設定
   - または、質問文の言語と会話の言語設定の両方を考慮

3. **GPT-4o miniプロンプトの修正**:
   - 検出した言語で回答を生成するようにプロンプトを修正

### 6.3 実装の詳細

**言語検出関数の追加**:
```python
def detect_language(text: str) -> str:
    """
    テキストの言語を検出（簡易版）
    - 日本語文字（ひらがな、カタカナ、漢字）が含まれていれば "ja"
    - そうでなければ "en"
    """
    import re
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
    if japanese_pattern.search(text):
        return "ja"
    return "en"
```

**言語設定の修正**:
```python
# 会話の言語を取得
conversation_language = message.conversation.guest_language or "en"

# 質問文の言語を検出
question_language = detect_language(question)

# 言語の優先順位: 質問文の言語 > 会話の言語設定
language = question_language if question_language else conversation_language
```

---

## 7. テストデータの問題

### 7.1 テストデータの確認

**問題**: テストデータの問題ではない

**理由**:
1. データベースのメッセージデータは正しい
   - メッセージID 28の直前のUSERメッセージ（ID 27）: 「アイロンは貸し出ししてますか？」（正しい質問）
   - メッセージID 32の直前のUSERメッセージ（ID 31）: 「ドリンカブルな水はありますか？」（正しい質問）

2. 問題は**ロジック**と**既存データ**にある
   - FAQ提案ID 2: 修正前のロジックで作成されたデータ
   - FAQ提案ID 14: 修正後のロジックで作成されたが、言語設定の問題

### 7.2 テストデータの影響

**テストデータの状態**:
- ✅ メッセージデータは正しい
- ✅ 会話の言語設定は`"en"`（これはテストデータの問題ではなく、実際の会話の設定）
- ❌ 既存のFAQ提案（ID 2）が古いロジックで作成されている

---

## 8. まとめ

### 8.1 問題の原因

1. **問題1（FAQ提案ID 2）**: 既存のFAQ提案が修正前のロジックで作成されている
2. **問題2（FAQ提案ID 14）**: 質問文の言語を検出せず、会話の言語設定（`"en"`）で回答を生成している

### 8.2 修正が必要な箇所

1. **既存のFAQ提案の処理**: 削除して再生成
2. **言語検出の実装**: 質問文の言語を検出して回答を生成

### 8.3 テストデータの問題

**結論**: テストデータの問題ではない。ロジックと既存データの問題。

---

**調査完了日**: 2025年12月14日  
**次回**: 修正指示を待つ


