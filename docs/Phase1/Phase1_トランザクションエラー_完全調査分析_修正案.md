# Phase 1: トランザクションエラー 完全調査分析・修正案

**作成日**: 2025年12月3日  
**実施者**: Auto (AI Assistant)  
**対象**: トランザクションエラー（InFailedSQLTransactionError）の完全調査分析と修正案  
**状態**: ✅ **完全調査分析完了、修正案提示完了（修正は実施しません）**

---

## 1. エラーの概要

### 1.1 発生したエラー

**フロントエンドエラー**:
```
Error processing chat message: (sqlalchemy.dialects.postgresql.asyncpg.Error) <class 'asyncpg.exceptions.InFailedSQLTransactionError'>: current transaction is aborted, commands ignored until end of transaction block
[SQL: INSERT INTO messages ...]
```

**バックエンドログ**:
```
function cosine_distance(vector, character varying) does not exist
Error fetching facility info: (sqlalchemy.dialects.postgresql.asyncpg.Error) <class 'asyncpg.exceptions.InFailedSQLTransactionError'>: current transaction is aborted, commands ignored until end of transaction block
Facility not found: 2
Error processing message: Facility not found: 2
```

### 1.2 エラーの発生タイミング

**テスト実行日時**: 2025年12月3日 13:35頃

**エラーの発生フロー**:
1. ユーザーメッセージ送信
2. 埋め込み生成（成功）
3. pgvector検索（`cosine_distance`関数のエラー）← **最初のエラー**
4. トランザクションが失敗状態に
5. 施設情報取得（トランザクションエラーのため失敗）
6. `Facility not found: 2`エラー
7. エラーハンドリングでフォールバックメッセージを返そうとする
8. `INSERT INTO messages`（トランザクションエラーのため失敗）← **フロントエンドに表示されるエラー**

---

## 2. 根本原因の分析

### 2.1 最初のエラー: `cosine_distance`関数のエラー

**エラーメッセージ**:
```
function cosine_distance(vector, character varying) does not exist
```

**発生箇所**: `backend/app/ai/vector_search.py`の57行目

**問題のコード**:
```python
# ベクトルをPostgreSQL形式に変換
embedding_vector = f"[{','.join(map(str, embedding))}]"  # 文字列形式

# コサイン類似度で検索（1 - コサイン距離 = 類似度）
query = select(
    FAQ,
    (1 - func.cosine_distance(FAQ.embedding, embedding_vector)).label('similarity')
)
```

**問題点**:
1. `embedding_vector`が文字列形式（`character varying`）で作成されている
2. `FAQ.embedding`は`Vector(1536)`型（`pgvector.sqlalchemy.Vector`）
3. `cosine_distance`関数は、2つの`vector`型の引数を期待している
4. 文字列と`vector`型を比較しようとしてエラーが発生

**pgvectorの正しい使用方法**:
- `cosine_distance(vector1, vector2)` - 両方とも`vector`型である必要がある
- Pythonのリストを直接使用する場合は、`cast`関数や`type_coerce`関数を使用して`vector`型に変換する必要がある

### 2.2 トランザクションエラーの連鎖

**エラーの連鎖**:
1. `cosine_distance`関数のエラーが発生
2. PostgreSQLのトランザクションが失敗状態になる
3. トランザクションがロールバックされていない
4. その後のすべてのSQLコマンドが無視される（`InFailedSQLTransactionError`）
5. `_get_facility_info`で施設情報を取得しようとするが、トランザクションが失敗状態のためエラー
6. `process_message`で`ValueError`が発生
7. エラーハンドリングでフォールバックメッセージを返そうとするが、トランザクションが失敗状態のため`INSERT INTO messages`が失敗

**問題点**:
1. トランザクション管理が不適切（エラー発生時にロールバックされていない）
2. エラーハンドリングが不十分（トランザクションエラーを適切に処理していない）

---

## 3. コードの確認

### 3.1 `vector_search.py`の確認

**問題のコード**:
```python
# ベクトルをPostgreSQL形式に変換
embedding_vector = f"[{','.join(map(str, embedding))}]"  # 文字列形式

# コサイン類似度で検索（1 - コサイン距離 = 類似度）
query = select(
    FAQ,
    (1 - func.cosine_distance(FAQ.embedding, embedding_vector)).label('similarity')
)
```

**問題点**:
- `embedding_vector`が文字列形式で、`cosine_distance`関数に渡されている
- `FAQ.embedding`は`Vector(1536)`型
- `cosine_distance`関数は`vector`型を期待している

### 3.2 トランザクション管理の確認

**`chat_service.py`の確認**:
```python
async def process_chat_message(...):
    # ユーザーメッセージを保存
    self.db.add(user_message)
    await self.db.flush()  # トランザクション内
    
    # RAG統合型AI対話エンジンでメッセージ処理
    rag_response = await self.rag_engine.process_message(...)  # ここでエラーが発生
    
    # AI応答メッセージを保存
    self.db.add(ai_message)
    await self.db.flush()  # トランザクションが失敗状態のため失敗
    
    await self.db.commit()  # トランザクションが失敗状態のため失敗
```

**問題点**:
- エラー発生時にトランザクションがロールバックされていない
- エラーハンドリングが不十分

---

## 4. 修正案

### 4.1 修正案1: `cosine_distance`関数の使用方法を修正（最優先）

**問題点**:
- `embedding_vector`が文字列形式で、`cosine_distance`関数に渡されている
- `cosine_distance`関数は`vector`型を期待している

**修正内容**:
1. `embedding_vector`を`vector`型に変換する
2. pgvectorの`Vector`型を使用するか、`cast`関数を使用する

**修正例1: `cast`関数を使用**:
```python
from sqlalchemy import cast
from pgvector.sqlalchemy import Vector

# ベクトルをvector型に変換
embedding_vector = cast(embedding, Vector(1536))

# コサイン類似度で検索
query = select(
    FAQ,
    (1 - func.cosine_distance(FAQ.embedding, embedding_vector)).label('similarity')
)
```

**修正例2: `type_coerce`関数を使用**:
```python
from sqlalchemy import type_coerce
from pgvector.sqlalchemy import Vector

# ベクトルをvector型に変換
embedding_vector = type_coerce(embedding, Vector(1536))

# コサイン類似度で検索
query = select(
    FAQ,
    (1 - func.cosine_distance(FAQ.embedding, embedding_vector)).label('similarity')
)
```

**修正例3: pgvectorの演算子を使用（推奨）**:
```python
from pgvector.sqlalchemy import Vector

# ベクトルをvector型に変換
embedding_vector = Vector(embedding)

# コサイン類似度で検索（pgvectorの演算子を使用）
# 1 - (embedding <=> embedding_vector) = コサイン類似度
query = select(
    FAQ,
    (1 - (FAQ.embedding <=> embedding_vector)).label('similarity')
).where(
    FAQ.facility_id == facility_id,
    FAQ.is_active == True,
    FAQ.embedding.isnot(None)
).order_by(
    (FAQ.embedding <=> embedding_vector).asc()
).limit(top_k)
```

**実装場所**:
- `backend/app/ai/vector_search.py`の`search_similar_faqs`関数（57行目、63行目）
- `backend/app/ai/vector_search.py`の`search_similar_patterns`関数（152行目、156行目）

### 4.2 修正案2: トランザクション管理の改善

**問題点**:
- エラー発生時にトランザクションがロールバックされていない
- トランザクションエラーを適切に処理していない

**修正内容**:
1. エラー発生時にトランザクションをロールバック
2. トランザクションエラーを適切に処理

**修正例**:
```python
async def process_chat_message(...):
    try:
        # ユーザーメッセージを保存
        self.db.add(user_message)
        await self.db.flush()
        
        # RAG統合型AI対話エンジンでメッセージ処理
        rag_response = await self.rag_engine.process_message(...)
        
        # AI応答メッセージを保存
        self.db.add(ai_message)
        await self.db.flush()
        
        await self.db.commit()
        
    except Exception as e:
        await self.db.rollback()  # エラー発生時にロールバック
        raise
```

**実装場所**:
- `backend/app/services/chat_service.py`の`process_chat_message`関数
- `backend/app/api/v1/chat.py`の`send_chat_message`関数

### 4.3 修正案3: エラーハンドリングの改善

**問題点**:
- トランザクションエラーを適切に処理していない
- エラー発生時にトランザクションがロールバックされていない

**修正内容**:
1. トランザクションエラーを検出してロールバック
2. エラーハンドリングを改善

**修正例**:
```python
from sqlalchemy.exc import DBAPIError

async def process_message(...):
    try:
        # ...
    except DBAPIError as e:
        # トランザクションエラーを検出
        if "InFailedSQLTransactionError" in str(e) or "transaction is aborted" in str(e):
            await self.db.rollback()  # トランザクションをロールバック
        raise
    except Exception as e:
        logger.error(...)
        return RAGEngineResponse(...)  # フォールバックレスポンスを返す
```

**実装場所**:
- `backend/app/ai/engine.py`の`process_message`関数
- `backend/app/services/chat_service.py`の`process_chat_message`関数

---

## 5. 修正の優先順位

### 5.1 最優先: 修正案1（`cosine_distance`関数の使用方法を修正）

**理由**:
1. これが最初のエラーの根本原因
2. このエラーが修正されれば、トランザクションエラーの連鎖も解消される
3. 最も根本的な解決策

**実施内容**:
1. `embedding_vector`を`vector`型に変換
2. `cosine_distance`関数に正しい型で渡す

### 5.2 高優先: 修正案2（トランザクション管理の改善）

**理由**:
1. エラー発生時にトランザクションをロールバックすることで、エラーの連鎖を防ぐ
2. データベースの整合性を保つ

**実施内容**:
1. エラー発生時にトランザクションをロールバック
2. トランザクションエラーを適切に処理

### 5.3 中優先: 修正案3（エラーハンドリングの改善）

**理由**:
1. トランザクションエラーを適切に処理することで、エラーメッセージを改善
2. デバッグが容易になる

**実施内容**:
1. トランザクションエラーを検出してロールバック
2. エラーハンドリングを改善

---

## 6. まとめ

### 6.1 エラーの根本原因

**根本原因**: ✅ **`cosine_distance`関数の使用方法が間違っている**

**詳細**:
1. `embedding_vector`が文字列形式で、`cosine_distance`関数に渡されている
2. `cosine_distance`関数は`vector`型を期待している
3. このエラーが発生した後、トランザクションが失敗状態になり、その後のすべてのSQLコマンドが無視される

### 6.2 修正すべき点

**最優先**:
1. **`cosine_distance`関数の使用方法を修正**（`embedding_vector`を`vector`型に変換）

**高優先**:
2. **トランザクション管理の改善**（エラー発生時にロールバック）

**中優先**:
3. **エラーハンドリングの改善**（トランザクションエラーを適切に処理）

### 6.3 期待される効果

1. ✅ `cosine_distance`関数のエラーが解消される
2. ✅ トランザクションエラーの連鎖が解消される
3. ✅ 正常にメッセージが処理される

**重要**: 修正は実施しません。ユーザーからの指示があるまで、調査分析と修正案の提示のみを行います。

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-03  
**Status**: ✅ **完全調査分析完了、修正案提示完了（修正は実施しません）**


