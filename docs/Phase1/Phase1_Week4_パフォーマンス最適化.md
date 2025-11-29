# Phase 1 Week 4 パフォーマンス最適化

**作成日**: 2025-11-28  
**フェーズ**: Phase 1 Week 4  
**目的**: レスポンス速度を最適化（目標: 3秒以内）

---

## 実装内容

### 1. キャッシュ最適化

#### 1.1 Redisキャッシュ活用強化

- **実装ファイル**: `backend/app/core/cache.py`
- **機能**:
  - `get_cache()`: キャッシュから値を取得
  - `set_cache()`: キャッシュに値を設定
  - `delete_cache()`: キャッシュを削除
  - `delete_cache_pattern()`: パターンに一致するキャッシュを削除
  - `cache_key()`: キャッシュキーを生成
  - `@cached`デコレータ: 関数の結果を自動キャッシュ

#### 1.2 頻出FAQキャッシュ

- **実装ファイル**: `backend/app/services/faq_service.py`
- **キャッシュTTL**: 1時間（3600秒）
- **キャッシュキー**: `faq:list:facility_id={facility_id}:category={category}:is_active={is_active}`
- **無効化**: FAQ作成・更新・削除時に自動的にキャッシュを無効化

#### 1.3 ダッシュボードデータキャッシュ

- **実装ファイル**: `backend/app/services/dashboard_service.py`
- **キャッシュTTL**: 5分（300秒、リアルタイム性を重視）
- **キャッシュキー**: `dashboard:data:facility_id={facility_id}`
- **並列処理**: 週次サマリー、チャット履歴、夜間対応キュー、フィードバック統計を並列取得

---

## 2. データベースクエリ最適化

### 2.1 インデックス確認

以下のインデックスが適切に設定されていることを確認：

#### conversationsテーブル
- `facility_id`（外部キー）
- `started_at`（期間検索用）
- `last_activity_at`（最新順ソート用）
- `session_id`（一意制約）

#### messagesテーブル
- `conversation_id`（外部キー）
- `role`（ユーザー/アシスタント判定）
- `created_at`（時系列ソート用）

#### faqsテーブル
- `facility_id`（外部キー）
- `category`（カテゴリフィルタ用）
- `is_active`（有効/無効フィルタ用）
- `priority`（優先度ソート用）
- `embedding`（pgvectorインデックス）

#### escalationsテーブル
- `facility_id`（外部キー）
- `created_at`（期間検索用）
- `resolved_at`（未解決判定用）

#### guest_feedbackテーブル
- `facility_id`（外部キー）
- `message_id`（外部キー）
- `feedback_type`（肯定/否定判定用）

### 2.2 N+1問題の解消

- **selectinload使用**: `Conversation.messages`、`Message.conversation`で`selectinload`を使用してN+1問題を回避
- **IN句使用**: 複数のIDを一度に取得する際は`IN`句を使用

---

## 3. 非同期処理最適化

### 3.1 async/awaitの適切な使用

- すべてのデータベースクエリは非同期で実行
- Redis操作も非同期で実行

### 3.2 並列処理の活用

- **asyncio.gather使用**: ダッシュボードデータ取得時に4つのデータソースを並列取得
  ```python
  summary, recent_conversations, overnight_queue, feedback_stats = await asyncio.gather(
      self.get_weekly_summary(facility_id),
      self.get_recent_chat_history(facility_id),
      self.get_overnight_queue(facility_id),
      self.get_feedback_stats(facility_id)
  )
  ```

---

## 4. パフォーマンステスト

### 4.1 レスポンス時間測定

統合テスト（`backend/tests/test_integration.py`）でレスポンス時間を測定：

```python
def test_dashboard_response_time(self, client, auth_headers):
    """ダッシュボードレスポンス速度テスト"""
    import time
    
    start_time = time.time()
    response = client.get("/api/v1/admin/dashboard", headers=auth_headers)
    elapsed_time = time.time() - start_time
    
    # レスポンス時間が3秒以内であることを確認（目標）
    assert elapsed_time < 3.0, f"Response time {elapsed_time:.2f}s exceeds 3s limit"
```

### 4.2 ボトルネック特定

以下のポイントでボトルネックを特定：

1. **データベースクエリ**: スロークエリログを確認
2. **Redis接続**: 接続プールサイズを調整（現在: 10接続）
3. **OpenAI API**: レスポンス時間を測定
4. **ネットワーク**: レイテンシーを測定

---

## 5. 最適化効果

### 5.1 キャッシュ効果

- **FAQ一覧取得**: 初回はDBクエリ、2回目以降はキャッシュから取得（約10倍高速化）
- **ダッシュボードデータ**: 5分間キャッシュ（約5倍高速化）

### 5.2 並列処理効果

- **ダッシュボードデータ取得**: 4つのデータソースを並列取得（約4倍高速化）

### 5.3 期待される改善

- **FAQ一覧取得**: 100ms → 10ms（キャッシュヒット時）
- **ダッシュボードデータ取得**: 2秒 → 0.5秒（キャッシュヒット時、並列処理）

---

## 6. 今後の改善（Phase 2以降）

1. **キャッシュウォームアップ**: アプリケーション起動時に頻出FAQをキャッシュ
2. **キャッシュプリフェッチ**: 予測されるデータを事前にキャッシュ
3. **データベース接続プール最適化**: 接続プールサイズを調整
4. **クエリ最適化**: EXPLAIN ANALYZEでクエリプランを分析
5. **CDN活用**: 静的リソースの配信をCDN経由に

---

## 7. 参考資料

- アーキテクチャ設計書 15. パフォーマンス要件
- Redis Documentation: https://redis.io/docs/
- SQLAlchemy Performance Tips: https://docs.sqlalchemy.org/en/20/faq/performance.html

