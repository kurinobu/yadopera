# 質問数・FAQ登録数カウント方法 設計調査分析レポート

**作成日時**: 2025年12月21日 10時47分00秒  
**調査目的**: 「今何時ですか？」と「what time is it now?」が質問数2件・FAQ登録数2件としてカウントされるか、システムの設計を調査分析

---

## 調査結果サマリー

✅ **質問数**: **2件としてカウントされる**（メッセージごとにカウント）  
✅ **FAQ登録数**: **2件としてカウントされる**（言語ごとに別レコードとして保存）

---

## 1. 質問数のカウント方法

### 1.1 データモデル

**`Message`モデル**（`backend/app/models/message.py`）:

```python
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)  # メッセージ内容（言語情報なし）
    ai_confidence = Column(DECIMAL(3, 2))
    matched_faq_ids = Column(ARRAY(Integer))
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
```

**重要なポイント**:
- ❌ **`language`カラムが存在しない**: `Message`モデルには言語情報を保存するカラムがない
- ✅ **`content`カラム**: メッセージ内容のみ保存（言語情報なし）
- ✅ **`role`カラム**: `'user'`（質問）、`'assistant'`（回答）、`'system'`（システム）を区別

### 1.2 質問数のカウントロジック

**`dashboard_service.py`の実装**（137-146行目）:

```python
# メッセージを取得
messages_result = await self.db.execute(
    select(Message)
    .where(Message.conversation_id.in_(conversation_ids))
    .where(Message.role == MessageRole.USER.value)  # 'user'ロールのみ
)
messages = messages_result.scalars().all()

# 総質問数
total_questions = len(messages)
```

**カウント方法**:
- ✅ **メッセージごとにカウント**: `role='user'`のメッセージをすべてカウント
- ✅ **言語を区別しない**: メッセージ内容の言語に関係なく、すべてのメッセージをカウント
- ✅ **重複を考慮しない**: 同じ内容のメッセージでも、別のメッセージレコードとしてカウント

### 1.3 質問数のカウント結果

**「今何時ですか？」と「what time is it now?」の場合**:

1. **「今何時ですか？」を送信**:
   - `messages`テーブルに1件のレコードが作成される
   - `role='user'`, `content='今何時ですか？'`

2. **「what time is it now?」を送信**:
   - `messages`テーブルに1件のレコードが作成される
   - `role='user'`, `content='what time is it now?'`

3. **質問数のカウント**:
   - `total_questions = len(messages)` = **2件**

**結論**: ✅ **質問数は2件としてカウントされる**

---

## 2. FAQ登録数のカウント方法

### 2.1 データモデル

**`FAQ`モデル**（`backend/app/models/faq.py`）:

```python
class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # 'basic', 'facilities', 'location', 'trouble'
    language = Column(String(10), default="en")  # 'en', 'ja', 'zh-TW', 'fr'  ← 言語情報あり
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small
    priority = Column(Integer, default=1)  # 1-5
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**重要なポイント**:
- ✅ **`language`カラムが存在する**: FAQには言語情報を保存するカラムがある
- ✅ **言語ごとに別レコード**: 同じ質問を異なる言語で登録した場合、別々のFAQレコードとして保存される
- ✅ **`is_active`カラム**: 有効/無効を区別（無効なFAQはカウントから除外される場合がある）

### 2.2 FAQ登録数のカウントロジック

**`faq_service.py`の実装**（41-87行目）:

```python
async def get_faqs(
    self,
    facility_id: int,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[FAQResponse]:
    query = select(FAQ).where(FAQ.facility_id == facility_id)
    
    if category:
        query = query.where(FAQ.category == category)
    
    if is_active is not None:
        query = query.where(FAQ.is_active == is_active)
    
    query = query.order_by(FAQ.priority.desc(), FAQ.created_at.desc())
    
    result = await self.db.execute(query)
    faqs = result.scalars().all()
    
    return [FAQResponse(**faq_dict) for faq_dict in faqs]
```

**カウント方法**:
- ✅ **レコードごとにカウント**: `faqs`テーブルのレコード数をカウント
- ✅ **言語を区別する**: 言語ごとに別レコードとして保存されるため、言語ごとにカウントされる
- ✅ **`is_active`フィルタ**: 有効なFAQのみをカウントする場合がある

### 2.3 FAQ登録数のカウント結果

**「今何時ですか？」と「what time is it now?」をFAQとして登録した場合**:

1. **「今何時ですか？」をFAQとして登録**:
   - `faqs`テーブルに1件のレコードが作成される
   - `language='ja'`, `question='今何時ですか？'`, `answer='現在の時刻は...'`

2. **「what time is it now?」をFAQとして登録**:
   - `faqs`テーブルに1件のレコードが作成される
   - `language='en'`, `question='what time is it now?', `answer='The current time is...'`

3. **FAQ登録数のカウント**:
   - `len(faqs)` = **2件**

**結論**: ✅ **FAQ登録数は2件としてカウントされる**

---

## 3. 設計思想の分析

### 3.1 メッセージ（質問）の設計

**設計思想**:
- ❌ **言語情報を保存しない**: `Message`モデルには`language`カラムがない
- ✅ **会話レベルで言語を管理**: `Conversation`モデルに`guest_language`カラムがある
- ✅ **メッセージごとにカウント**: 言語に関係なく、すべてのメッセージをカウント

**理由**:
- 質問数は「ゲストが送信したメッセージの総数」をカウントするため、言語を区別する必要がない
- 会話レベルで言語を管理することで、同じ会話内のメッセージは同じ言語として扱える

### 3.2 FAQの設計

**設計思想**:
- ✅ **言語情報を保存する**: `FAQ`モデルに`language`カラムがある
- ✅ **言語ごとに別レコード**: 同じ質問を異なる言語で登録した場合、別々のFAQレコードとして保存
- ✅ **言語ごとにカウント**: FAQ登録数は言語ごとにカウントされる

**理由**:
- FAQは多言語対応が必要なため、言語ごとに別レコードとして保存する
- ベクトル検索時に言語を考慮して検索できるようにするため
- 料金プランの「FAQ登録数」は、言語ごとに別レコードとしてカウントされる

### 3.3 料金プランとの関係

**料金プランの「FAQ登録数」**（要約定義書より）:

| プラン | 月額料金 | 質問数上限 | 超過料金 | FAQ登録数 |
|--------|----------|-----------|---------|-----------|
| Mini | ¥1,980 | 最初から従量課金 | ¥30/質問 | **20件** |
| Small | ¥3,980 | 200件/月 | ¥30/質問（超過分） | **50件** |
| Standard | ¥5,980 | 500件/月 | ¥30/質問（超過分） | **100件** |
| Premium | ¥7,980 | 1,000件/月 | ¥30/質問（超過分） | **無制限** |

**FAQ登録数のカウント方法**:
- ✅ **言語ごとに別レコードとしてカウント**: 「今何時ですか？」（日本語）と「what time is it now?」（英語）は2件としてカウントされる
- ✅ **`is_active=true`のFAQのみカウント**: 無効なFAQはカウントから除外される

**質問数上限との関係**:
- ✅ **質問数上限**: メッセージごとにカウントされるため、言語に関係なくすべてのメッセージをカウント
- ✅ **FAQ登録数上限**: 言語ごとに別レコードとしてカウントされるため、多言語対応にはより多くのFAQ登録数が必要

---

## 4. まとめ

### 4.1 質問数のカウント方法

✅ **「今何時ですか？」と「what time is it now?」は質問数2件としてカウントされる**

**理由**:
- `Message`モデルには`language`カラムがない
- メッセージごとにカウントされるため、言語に関係なくすべてのメッセージをカウント
- 質問数は「ゲストが送信したメッセージの総数」をカウントするため、言語を区別する必要がない

### 4.2 FAQ登録数のカウント方法

✅ **「今何時ですか？」と「what time is it now?」はFAQ登録数2件としてカウントされる**

**理由**:
- `FAQ`モデルに`language`カラムがある
- 言語ごとに別レコードとして保存されるため、言語ごとにカウントされる
- 料金プランの「FAQ登録数」は、言語ごとに別レコードとしてカウントされる

### 4.3 設計の一貫性

✅ **設計は一貫している**:
- 質問数: メッセージごとにカウント（言語を区別しない）
- FAQ登録数: 言語ごとに別レコードとしてカウント（言語を区別する）

**理由**:
- 質問数は「ゲストが送信したメッセージの総数」をカウントするため、言語を区別する必要がない
- FAQ登録数は「多言語対応のためのFAQの総数」をカウントするため、言語ごとに別レコードとしてカウントする必要がある

---

**調査完了日時**: 2025年12月21日 10時47分00秒


