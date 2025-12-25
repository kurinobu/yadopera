# Phase 1: 未解決質問リストから削除されない問題 調査分析・修正案

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: FAQ提案を承認した後、未解決質問リストから削除されない問題  
**状態**: ✅ **調査分析完了、修正案提示完了**

---

## 1. 問題の概要

### 1.1 現象

- **症状**: FAQ提案を承認してFAQが正常に作成された後、「未解決質問リスト」から削除されずに残っている
- **発生条件**: 管理画面のFAQ管理画面で未解決質問リストからFAQ提案を生成し、承認してFAQを作成する

### 1.2 確認済み項目

- ✅ FAQ提案が生成される
- ✅ FAQ提案が表示される
- ✅ FAQ提案を承認してFAQが正常に作成される
- ✅ FAQ一覧に表示される
- ❌ 未解決質問リストから削除されない

---

## 2. 根本原因の調査分析

### 2.1 未解決質問リストの取得条件

**ファイル**: `backend/app/services/escalation_service.py`

**実装コード**:
```python:343:349:backend/app/services/escalation_service.py
# 未解決のエスカレーションを取得（conversationをeager load）
query = select(Escalation).options(
    joinedload(Escalation.conversation)
).where(
    Escalation.facility_id == facility_id,
    Escalation.resolved_at.is_(None)
).order_by(Escalation.created_at.desc())
```

**確認事項**:
- ✅ 未解決質問リストは`Escalation.resolved_at.is_(None)`でフィルタしている
- ✅ `resolved_at`が`NULL`のエスカレーションのみが表示される

### 2.2 FAQ提案承認時の処理

**ファイル**: `backend/app/services/faq_suggestion_service.py`

**実装コード**:
```python:398:412:backend/app/services/faq_suggestion_service.py
# 提案を更新
logger.info(
    f"Updating FAQ suggestion: suggestion_id={suggestion_id}, faq_id={faq.id}",
    extra={
        "suggestion_id": suggestion_id,
        "faq_id": faq.id
    }
)
suggestion.status = FAQSuggestionStatus.APPROVED.value
suggestion.reviewed_at = datetime.utcnow()
suggestion.reviewed_by = user_id
suggestion.created_faq_id = faq.id

await self.db.commit()
await self.db.refresh(suggestion)
```

**確認事項**:
- ⚠️ FAQ提案のステータスを`APPROVED`に更新している
- ❌ **エスカレーションを解決済みにする処理がない**（`resolved_at`を設定していない）

### 2.3 データモデルの関係

**関係性**:
1. **FAQ提案（FAQSuggestion）**: `source_message_id`を持つ
2. **メッセージ（Message）**: `conversation_id`を持つ
3. **エスカレーション（Escalation）**: `conversation_id`を持つ
4. **未解決質問リスト**: `Escalation.resolved_at.is_(None)`でフィルタ

**問題**:
- FAQ提案を承認しても、エスカレーションの`resolved_at`が設定されない
- そのため、未解決質問リストから削除されない

### 2.4 根本原因の確定

**根本原因**: FAQ提案を承認してFAQを作成した際、エスカレーションを解決済みにする処理が実装されていない

**詳細**:
1. **FAQ提案承認時の処理不足**
   - `approve_suggestion`メソッドでFAQを作成しているが、エスカレーションを解決済みにする処理がない
   - エスカレーションの`resolved_at`が`NULL`のまま

2. **データモデルの関係**
   - FAQ提案の`source_message_id`からメッセージを取得
   - メッセージの`conversation_id`からエスカレーションを取得
   - エスカレーションの`resolved_at`を設定する必要がある

3. **設計上の考慮事項**
   - 1つの会話に複数のエスカレーションがある可能性がある
   - その場合、どのエスカレーションを解決済みにするか？
   - **推奨**: FAQ提案の`source_message_id`に対応するエスカレーションを解決済みにする（`conversation_id`が一致し、`resolved_at IS NULL`のもの）

---

## 3. 修正案（大原則準拠）

### 3.1 修正案1: FAQ提案承認時にエスカレーションを解決済みにする（根本解決）

**目的**: FAQ提案を承認してFAQを作成した際、対応するエスカレーションを解決済みにする

**大原則への準拠**:
- ✅ **根本解決 > 暫定解決**: エスカレーションを解決済みにする処理を追加（根本解決）
- ✅ **シンプル構造 > 複雑構造**: シンプルな実装（エスカレーションの更新のみ）
- ✅ **統一・同一化 > 特殊独自**: 既存のパターンに従う
- ✅ **具体的 > 一般**: 具体的な修正内容を明確にする
- ✅ **拙速 < 安全確実**: バックアップ作成、エラーハンドリング、リンター確認

**修正内容**:

**ファイル**: `backend/app/services/faq_suggestion_service.py`

**修正箇所**: `approve_suggestion`メソッド（FAQ作成後、提案を更新する前に追加）

**修正前**:
```python:397:412:backend/app/services/faq_suggestion_service.py
# 提案を更新
logger.info(
    f"Updating FAQ suggestion: suggestion_id={suggestion_id}, faq_id={faq.id}",
    extra={
        "suggestion_id": suggestion_id,
        "faq_id": faq.id
    }
)
suggestion.status = FAQSuggestionStatus.APPROVED.value
suggestion.reviewed_at = datetime.utcnow()
suggestion.reviewed_by = user_id
suggestion.created_faq_id = faq.id

await self.db.commit()
await self.db.refresh(suggestion)
```

**修正後**:
```python:397:440:backend/app/services/faq_suggestion_service.py
# エスカレーションを解決済みにする
try:
    # メッセージを取得（conversationを事前にロード）
    from app.models.message import Message
    from app.models.escalation import Escalation
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    
    message_query = select(Message).options(joinedload(Message.conversation)).where(Message.id == suggestion.source_message_id)
    message_result = await self.db.execute(message_query)
    message = message_result.scalar_one_or_none()
    
    if message and message.conversation_id:
        # 対応するエスカレーションを取得（未解決のもの）
        escalation_query = select(Escalation).where(
            Escalation.conversation_id == message.conversation_id,
            Escalation.facility_id == facility_id,
            Escalation.resolved_at.is_(None)
        ).order_by(Escalation.created_at.desc()).limit(1)
        
        escalation_result = await self.db.execute(escalation_query)
        escalation = escalation_result.scalar_one_or_none()
        
        if escalation:
            # エスカレーションを解決済みにする
            escalation.resolved_at = datetime.utcnow()
            escalation.resolved_by = user_id
            escalation.resolution_notes = f"FAQ created from suggestion {suggestion_id}"
            await self.db.flush()
            
            logger.info(
                f"Escalation resolved: escalation_id={escalation.id}, suggestion_id={suggestion_id}",
                extra={
                    "escalation_id": escalation.id,
                    "suggestion_id": suggestion_id,
                    "faq_id": faq.id
                }
            )
        else:
            logger.warning(
                f"No unresolved escalation found for conversation_id={message.conversation_id}, suggestion_id={suggestion_id}",
                extra={
                    "conversation_id": message.conversation_id,
                    "suggestion_id": suggestion_id
                }
            )
    else:
        logger.warning(
            f"Message not found or conversation_id is None: source_message_id={suggestion.source_message_id}, suggestion_id={suggestion_id}",
            extra={
                "source_message_id": suggestion.source_message_id,
                "suggestion_id": suggestion_id
            }
        )
except Exception as e:
    # エスカレーション解決の失敗はFAQ作成を妨げない（ログのみ記録）
    logger.error(
        f"Error resolving escalation: {str(e)}",
        exc_info=True,
        extra={
            "suggestion_id": suggestion_id,
            "source_message_id": suggestion.source_message_id,
            "error": str(e)
        }
    )

# 提案を更新
logger.info(
    f"Updating FAQ suggestion: suggestion_id={suggestion_id}, faq_id={faq.id}",
    extra={
        "suggestion_id": suggestion_id,
        "faq_id": faq.id
    }
)
suggestion.status = FAQSuggestionStatus.APPROVED.value
suggestion.reviewed_at = datetime.utcnow()
suggestion.reviewed_by = user_id
suggestion.created_faq_id = faq.id

await self.db.commit()
await self.db.refresh(suggestion)
```

**変更点**:
- FAQ作成後、提案を更新する前に、エスカレーションを解決済みにする処理を追加
- `source_message_id`からメッセージを取得
- メッセージの`conversation_id`からエスカレーションを取得（`resolved_at IS NULL`のもの）
- エスカレーションの`resolved_at`を設定
- エラーハンドリングを追加（エスカレーション解決の失敗はFAQ作成を妨げない）

**効果**:
- ✅ FAQ提案を承認してFAQを作成した際、対応するエスカレーションが解決済みになる
- ✅ 未解決質問リストから削除される
- ✅ エラーハンドリングにより、エスカレーション解決の失敗がFAQ作成を妨げない

---

## 4. 大原則への準拠確認

### 4.1 根本解決 > 暫定解決

**評価**: ✅ **準拠**

**理由**:
- エスカレーションを解決済みにする処理を追加（根本解決）
- 一時的な回避策ではなく、恒久的な解決方法

### 4.2 シンプル構造 > 複雑構造

**評価**: ✅ **準拠**

**理由**:
- シンプルな実装（エスカレーションの更新のみ）
- 過度に複雑な実装ではない

### 4.3 統一・同一化 > 特殊独自

**評価**: ✅ **準拠**

**理由**:
- 既存のパターンに従っている
- 標準的なアプローチを採用

### 4.4 具体的 > 一般

**評価**: ✅ **準拠**

**理由**:
- 具体的な修正内容を明確にする
- 実行可能なコードが提示されている

### 4.5 拙速 < 安全確実

**評価**: ✅ **準拠**

**理由**:
- バックアップ作成を推奨
- エラーハンドリングを実装
- リンター確認を推奨

**総合評価**: ✅ **大原則に完全準拠**

---

## 5. まとめ

### 5.1 根本原因

**根本原因**: FAQ提案を承認してFAQを作成した際、エスカレーションを解決済みにする処理が実装されていない

**詳細**:
- 未解決質問リストは`Escalation.resolved_at.is_(None)`でフィルタしている
- FAQ提案を承認しても、エスカレーションの`resolved_at`が設定されない
- そのため、未解決質問リストから削除されない

### 5.2 推奨修正案

**修正案1**: FAQ提案承認時にエスカレーションを解決済みにする

**修正内容**:
1. FAQ作成後、提案を更新する前に、エスカレーションを解決済みにする処理を追加
2. `source_message_id`からメッセージを取得
3. メッセージの`conversation_id`からエスカレーションを取得（`resolved_at IS NULL`のもの）
4. エスカレーションの`resolved_at`を設定
5. エラーハンドリングを追加

### 5.3 次のステップ

1. **修正の実施**（ユーザーの指示を待つ）
   - バックアップを作成
   - 修正案1を実施
   - 動作確認

2. **動作確認**
   - FAQ提案を承認してFAQを作成
   - 未解決質問リストから削除されることを確認
   - ブラウザの開発者ツールでエラーがないことを確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ✅ **調査分析完了、修正案提示完了（修正待ち）**


