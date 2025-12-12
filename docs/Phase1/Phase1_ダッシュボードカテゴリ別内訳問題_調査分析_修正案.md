# Phase 1: ダッシュボードの「カテゴリ別内訳」セクションの数値が全部「0」の問題 調査分析・修正案

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: ダッシュボードの「カテゴリ別内訳」セクションがすべて「0」と表示される問題  
**状態**: ✅ **調査分析完了、修正案提示完了**

---

## 1. 問題の概要

### 1.1 現象

- **症状**: ダッシュボードの「カテゴリ別内訳」セクション（基本情報、設備・サービス、周辺情報、トラブル対応）の数値がすべて「0」と表示される
- **発生条件**: ダッシュボードを表示する際、常に発生
- **影響範囲**: ダッシュボードの週次サマリー統計

### 1.2 確認済み項目

- ✅ ダッシュボードは正常に表示される
- ✅ 総質問数、自動応答率、平均信頼度は正しく表示される
- ❌ カテゴリ別内訳がすべて「0」と表示される

---

## 2. 根本原因の調査分析

### 2.1 現在の実装

**ファイル**: `backend/app/services/dashboard_service.py`

**実装コード**:
```python:183:185:backend/app/services/dashboard_service.py
# カテゴリ別内訳（簡易実装、FAQカテゴリから推定）
category_breakdown = CategoryBreakdown()
# TODO: メッセージ内容からカテゴリを推定する実装（Phase 2で改善）
```

**確認事項**:
- ✅ `CategoryBreakdown()`をデフォルト値で作成しているため、すべての値が`0`になっている
- ⚠️ TODOコメントがあり、「メッセージ内容からカテゴリを推定する実装（Phase 2で改善）」と書かれている
- ❌ **実際のカテゴリ別内訳を計算する処理が実装されていない**

### 2.2 利用可能なデータ

**データモデルの関係**:
1. **メッセージ（Message）**: 
   - `matched_faq_ids` (ARRAY(Integer)): 使用したFAQ IDリスト
   - `role`: `user`（ユーザーメッセージ）または`assistant`（AI応答メッセージ）
   - `conversation_id`: 会話ID

2. **FAQ（FAQ）**:
   - `id`: FAQ ID
   - `category`: カテゴリ（`basic`, `facilities`, `location`, `trouble`）
   - `is_active`: アクティブかどうか

3. **会話（Conversation）**:
   - `facility_id`: 施設ID
   - `started_at`: 開始時刻

**データの流れ**:
- ユーザーメッセージが送信される
- RAGエンジンが処理し、類似FAQを検索（`matched_faq_ids`に保存）
- AI応答メッセージが生成され、`matched_faq_ids`が保存される（`chat_service.py`の104行目）

**確認事項**:
- ✅ `matched_faq_ids`はAI応答メッセージ（`role == MessageRole.ASSISTANT`）にのみ保存されている
- ✅ ユーザーメッセージ（`role == MessageRole.USER`）には保存されていない
- ✅ 過去7日間のメッセージを取得している（137-143行目）

### 2.3 根本原因の確定

**根本原因**: カテゴリ別内訳を計算する処理が実装されていない

**詳細**:
1. **実装不足**
   - `get_weekly_summary`メソッドで、`CategoryBreakdown()`をデフォルト値で作成している
   - 実際のカテゴリ別内訳を計算する処理がない

2. **利用可能なデータ**
   - AI応答メッセージの`matched_faq_ids`からFAQを取得できる
   - FAQの`category`を集計してカテゴリ別内訳を計算できる

3. **設計上の考慮事項**
   - ユーザーメッセージに対応するAI応答メッセージを取得する必要がある
   - `matched_faq_ids`が`NULL`または空の場合の処理が必要
   - 複数のFAQがマッチした場合、すべてのカテゴリをカウントするか、最初の1つだけをカウントするか？

---

## 3. 修正案（大原則準拠）

### 3.1 修正案1: `matched_faq_ids`からFAQカテゴリを集計する（根本解決・推奨）

**目的**: AI応答メッセージの`matched_faq_ids`からFAQを取得し、そのカテゴリを集計してカテゴリ別内訳を計算する

**大原則への準拠**:
- ✅ **根本解決 > 暫定解決**: 既存のデータ（`matched_faq_ids`）を活用してカテゴリ別内訳を計算（根本解決）
- ✅ **シンプル構造 > 複雑構造**: シンプルな実装（既存のデータを集計するだけ）
- ✅ **統一・同一化 > 特殊独自**: 既存のパターンに従う
- ✅ **具体的 > 一般**: 具体的な修正内容を明確にする
- ✅ **拙速 < 安全確実**: バックアップ作成、エラーハンドリング、リンター確認

**修正内容**:

**ファイル**: `backend/app/services/dashboard_service.py`

**修正箇所**: `get_weekly_summary`メソッド（183-185行目を置き換え）

**修正前**:
```python:183:185:backend/app/services/dashboard_service.py
# カテゴリ別内訳（簡易実装、FAQカテゴリから推定）
category_breakdown = CategoryBreakdown()
# TODO: メッセージ内容からカテゴリを推定する実装（Phase 2で改善）
```

**修正後**:
```python:183:230:backend/app/services/dashboard_service.py
# カテゴリ別内訳（matched_faq_idsからFAQカテゴリを集計）
category_breakdown = CategoryBreakdown()

# 過去7日間のAI応答メッセージを取得（matched_faq_idsがNULLでないもの）
ai_messages_with_faqs_result = await self.db.execute(
    select(Message)
    .where(Message.conversation_id.in_(conversation_ids))
    .where(Message.role == MessageRole.ASSISTANT.value)
    .where(Message.matched_faq_ids.isnot(None))
)
ai_messages_with_faqs = ai_messages_with_faqs_result.scalars().all()

# matched_faq_idsからFAQ IDを収集（重複を排除、空配列を除外）
faq_ids = set()
for msg in ai_messages_with_faqs:
    if msg.matched_faq_ids and len(msg.matched_faq_ids) > 0:
        faq_ids.update(msg.matched_faq_ids)

# FAQを取得してカテゴリを集計
if faq_ids:
    faqs_result = await self.db.execute(
        select(FAQ)
        .where(FAQ.id.in_(list(faq_ids)))
        .where(FAQ.facility_id == facility_id)
        .where(FAQ.is_active == True)
    )
    faqs = faqs_result.scalars().all()
    
    # カテゴリ別に集計（各メッセージの最初のマッチしたFAQのカテゴリをカウント）
    category_counts = {"basic": 0, "facilities": 0, "location": 0, "trouble": 0}
    faq_category_map = {faq.id: faq.category for faq in faqs}
    
    for msg in ai_messages_with_faqs:
        if msg.matched_faq_ids and len(msg.matched_faq_ids) > 0:
            # 最初のマッチしたFAQのカテゴリをカウント
            first_faq_id = msg.matched_faq_ids[0]
            if first_faq_id in faq_category_map:
                category = faq_category_map[first_faq_id]
                if category in category_counts:
                    category_counts[category] += 1
    
    category_breakdown = CategoryBreakdown(
        basic=category_counts["basic"],
        facilities=category_counts["facilities"],
        location=category_counts["location"],
        trouble=category_counts["trouble"]
    )
```

**変更点**:
- 過去7日間のAI応答メッセージを取得（`matched_faq_ids`が`NULL`でないもの）
- `matched_faq_ids`からFAQ IDを収集（重複を排除）
- FAQを取得してカテゴリを集計
- 各メッセージの最初のマッチしたFAQのカテゴリをカウント
- `CategoryBreakdown`を作成

**効果**:
- ✅ 既存のデータ（`matched_faq_ids`）を活用してカテゴリ別内訳を計算
- ✅ シンプルな実装（既存のデータを集計するだけ）
- ✅ コストがかからない（GPT-4o miniを呼び出さない）
- ✅ パフォーマンスが良い（データベースクエリのみ）

**注意点**:
- `matched_faq_ids`が`NULL`または空のメッセージは集計から除外される
- 複数のFAQがマッチした場合、最初の1つだけをカウントする（シンプルな実装）
- FAQが削除された場合、`faq_category_map`に含まれないため、集計から除外される

---

### 3.2 修正案2: メッセージ内容からGPT-4o miniでカテゴリを推定する（暫定解決・非推奨）

**目的**: メッセージ内容からGPT-4o miniでカテゴリを推定する

**大原則への準拠**:
- ⚠️ **根本解決 > 暫定解決**: GPT-4o miniを呼び出すため、コストがかかる（暫定解決）
- ⚠️ **シンプル構造 > 複雑構造**: 複雑な実装（GPT-4o miniを呼び出す必要がある）
- ⚠️ **拙速 < 安全確実**: コストとパフォーマンスの問題がある

**評価**: ❌ **非推奨**（修正案1の方が優れている）

**理由**:
- コストがかかる（GPT-4o miniを呼び出す必要がある）
- パフォーマンスが悪い（API呼び出しが必要）
- 既存のデータ（`matched_faq_ids`）を活用できるため、修正案1の方が優れている

---

## 4. 大原則への準拠確認

### 4.1 根本解決 > 暫定解決

**評価**: ✅ **準拠**

**理由**:
- 既存のデータ（`matched_faq_ids`）を活用してカテゴリ別内訳を計算（根本解決）
- GPT-4o miniを呼び出す必要がない（コストがかからない）

### 4.2 シンプル構造 > 複雑構造

**評価**: ✅ **準拠**

**理由**:
- シンプルな実装（既存のデータを集計するだけ）
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
- エラーハンドリングを実装（`matched_faq_ids`が`NULL`または空の場合の処理）
- リンター確認を推奨

**総合評価**: ✅ **大原則に完全準拠**

---

## 5. 実装の詳細

### 5.1 データフロー

1. **過去7日間の会話を取得**
   - `conversation_ids`を取得（112-122行目）

2. **AI応答メッセージを取得**
   - `matched_faq_ids`が`NULL`でないAI応答メッセージを取得
   - `array_length(Message.matched_faq_ids, 1) > 0`で空配列を除外

3. **FAQ IDを収集**
   - `matched_faq_ids`からFAQ IDを収集（重複を排除）

4. **FAQを取得**
   - FAQ IDからFAQを取得（`facility_id`と`is_active`でフィルタ）

5. **カテゴリを集計**
   - 各メッセージの最初のマッチしたFAQのカテゴリをカウント
   - `CategoryBreakdown`を作成

### 5.2 エラーハンドリング

- `matched_faq_ids`が`NULL`または空の場合: 集計から除外
- FAQが削除された場合: `faq_category_map`に含まれないため、集計から除外
- カテゴリが存在しない場合: `category_counts`に含まれないため、集計から除外

### 5.3 パフォーマンス考慮

- **インデックス**: `Message.conversation_id`、`Message.role`、`Message.matched_faq_ids`にインデックスがあることを確認
- **クエリ最適化**: `IN`句を使用して効率的にFAQを取得
- **メモリ使用**: `faq_ids`を`set`で管理して重複を排除

---

## 6. まとめ

### 6.1 根本原因

**根本原因**: カテゴリ別内訳を計算する処理が実装されていない

**詳細**:
- `get_weekly_summary`メソッドで、`CategoryBreakdown()`をデフォルト値で作成している
- 実際のカテゴリ別内訳を計算する処理がない

### 6.2 推奨修正案

**修正案1**: `matched_faq_ids`からFAQカテゴリを集計する（根本解決・推奨）

**修正内容**:
1. 過去7日間のAI応答メッセージを取得（`matched_faq_ids`が`NULL`でないもの）
2. `matched_faq_ids`からFAQ IDを収集（重複を排除）
3. FAQを取得してカテゴリを集計
4. 各メッセージの最初のマッチしたFAQのカテゴリをカウント
5. `CategoryBreakdown`を作成

### 6.3 次のステップ

1. **修正の実施**（ユーザーの指示を待つ）
   - バックアップを作成
   - 修正案1を実施
   - 動作確認

2. **動作確認**
   - ダッシュボードを表示
   - カテゴリ別内訳が正しい数値を表示することを確認
   - ブラウザの開発者ツールでエラーがないことを確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ✅ **調査分析完了、修正案提示完了（修正待ち）**

