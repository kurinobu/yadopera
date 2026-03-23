# ステップ2: 月次ダッシュボード統計実装 - 引き継ぎドキュメント

**作成日**: 2025年1月14日  
**目的**: 次のセッションで即座にステップ2の実装を開始できるよう、必要な情報を整理  
**ステータス**: 未着手（準備完了）

---

## 1. 実装概要

### 1.1 目的
施設管理者が最も気にする**コスト情報**を見える化する。具体的には：
- 「今月は従量課金でいくら使っているのか？」
- 「料金プランでの従量課金に切り替わるのは残りどれくらいか？」

これらの情報を明確に表示することで、PoC期間中の施設管理者の満足度向上を目指す。

### 1.2 実装するカード（Phase 2）

**月次統計カード（最優先表示エリア）**:
1. **カード1: 今月の質問数 / プラン上限**
   - プログレスバー表示
   - プラン別表示ロジック（Free/Mini/Small/Standard/Premium）
   - 使用率に応じた色分け・警告表示

2. **カード2: 今月のAI自動応答数**
   - AI自動応答数表示
   - 自動化率表示

3. **カード3: 今月のエスカレーション数**
   - エスカレーション総数表示
   - 未解決数・解決済み数表示

4. **カード8: 未解決のエスカレーション**
   - 未解決エスカレーションリスト表示（最新10件）

**Phase 3で実装予定**:
- カード4: 推定月額コスト
- カード5-7: 週次トレンド、平均信頼度、カテゴリ別内訳

### 1.3 所要時間
- **データベース拡張**: 0.5日
- **Backend API実装**: 1日
- **Frontend実装**: 1日
- **統合テスト**: 0.5日
- **合計**: 2-3日間

---

## 2. 参照ドキュメント

### 2.1 必須参照文書
- **`docs/monthly_dashboard_arch.md`**: 月次ダッシュボード統計設計書（詳細設計）
- **`docs/Phase2_実装ステップ計画_20250114.md`**: ステップ2の実装計画（セクション5.2参照）

### 2.2 既存実装の確認
- **`backend/app/api/v1/admin/dashboard.py`**: 既存のダッシュボードAPI（拡張対象）
- **`backend/app/services/dashboard_service.py`**: 既存のダッシュボードサービス（拡張対象）
- **`backend/app/schemas/dashboard.py`**: 既存のダッシュボードスキーマ（拡張対象）
- **`frontend/src/views/admin/DashboardView.vue`**: 既存のダッシュボード画面（拡張対象）

---

## 3. 実装ステップ詳細

### ステップ1: データベース拡張（0.5日）

#### 3.1 マイグレーションファイル作成
**ファイル**: `backend/alembic/versions/012_add_facility_plan_columns.py`

**追加カラム**:
```sql
ALTER TABLE facilities
ADD COLUMN plan_type VARCHAR(20) DEFAULT 'Free' 
  CHECK (plan_type IN ('Free', 'Mini', 'Small', 'Standard', 'Premium')),
ADD COLUMN monthly_question_limit INTEGER DEFAULT 30,
ADD COLUMN faq_limit INTEGER DEFAULT 20,
ADD COLUMN language_limit INTEGER DEFAULT 1,
ADD COLUMN plan_started_at TIMESTAMP DEFAULT NOW(),
ADD COLUMN plan_updated_at TIMESTAMP;
```

**注意事項**:
- 既存データの移行（デフォルト値設定）
- `plan_type`にCHECK制約を追加
- `monthly_question_limit`はMiniプランの場合はNULL（無制限）

#### 3.2 モデル更新
**ファイル**: `backend/app/models/facility.py`

**追加フィールド**:
```python
plan_type = Column(String(20), default='Free', nullable=False)
monthly_question_limit = Column(Integer, nullable=True)  # Miniの場合はNULL
faq_limit = Column(Integer, default=20, nullable=False)
language_limit = Column(Integer, default=1, nullable=False)
plan_started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
plan_updated_at = Column(DateTime, nullable=True)
```

#### 3.3 マイグレーション実行
```bash
cd /Users/kurinobu/projects/yadopera
docker-compose exec backend alembic upgrade head
```

---

### ステップ2: Backend API実装（1日）

#### 4.1 サービス層実装
**ファイル**: `backend/app/services/dashboard_service.py`（既存ファイルを拡張）

**追加メソッド**:
1. `get_monthly_usage(facility_id: int) -> dict`
   - 今月の質問数/プラン上限を計算
   - プラン情報を取得
   - 使用率、残り質問数を計算
   - ステータス判定（normal/warning/overage/faq_only）

2. `get_ai_automation(facility_id: int) -> dict`
   - 今月のAI自動応答数を集計
   - 自動化率を計算（AI応答数 / 総質問数 * 100）

3. `get_escalations_summary(facility_id: int) -> dict`
   - 今月のエスカレーション数を集計
   - 未解決数・解決済み数を計算

4. `get_unresolved_escalations(facility_id: int, limit: int = 10) -> list`
   - 未解決エスカレーションを取得（最新10件）

**重要**: タイムゾーン処理は**日本時間（JST）**基準で実装
- データベースはUTC保存
- 取得時にJST変換（`pytz`ライブラリ使用）
- 月次集計期間: 毎月1日 00:00:00 〜 月末 23:59:59（JST基準）

#### 4.2 スキーマ定義
**ファイル**: `backend/app/schemas/dashboard.py`（既存ファイルを拡張）

**追加スキーマ**:
```python
class MonthlyUsageResponse(BaseModel):
    current_month_questions: int
    plan_type: str
    plan_limit: Optional[int]  # Miniの場合はNone
    usage_percentage: Optional[float]  # Miniの場合はNone
    remaining_questions: Optional[int]  # Miniの場合はNone
    overage_questions: int
    status: str  # "normal" | "warning" | "overage" | "faq_only"

class AiAutomationResponse(BaseModel):
    ai_responses: int
    total_questions: int
    automation_rate: float

class EscalationsSummaryResponse(BaseModel):
    total: int
    unresolved: int
    resolved: int

class UnresolvedEscalation(BaseModel):
    id: int
    conversation_id: int
    created_at: datetime
    message: str
```

#### 4.3 APIエンドポイント実装
**ファイル**: `backend/app/api/v1/admin/dashboard.py`（既存ファイルを拡張）

**既存エンドポイント**: `GET /api/v1/admin/dashboard`
- 既存の週次サマリー、リアルタイムチャット履歴などは維持
- 月次統計データをレスポンスに追加

**レスポンス構造**:
```python
class DashboardResponse(BaseModel):
    # 既存フィールド（維持）
    weekly_summary: WeeklySummary
    recent_conversations: List[ConversationSummary]
    overnight_queue: List[OvernightQueueItem]
    feedback_stats: FeedbackStats
    
    # 新規追加（月次統計）
    monthly_usage: MonthlyUsageResponse
    ai_automation: AiAutomationResponse
    escalations_summary: EscalationsSummaryResponse
    unresolved_escalations: List[UnresolvedEscalation]
```

#### 4.4 SQLクエリ例

**今月の質問数集計**:
```sql
SELECT COUNT(*) as current_month_questions
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.facility_id = :facility_id
  AND m.role = 'user'
  AND m.created_at >= DATE_TRUNC('month', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Tokyo')
  AND m.created_at < DATE_TRUNC('month', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Tokyo') + INTERVAL '1 month';
```

**プラン情報取得**:
```sql
SELECT plan_type, monthly_question_limit
FROM facilities
WHERE id = :facility_id;
```

**AI自動応答数集計**:
```sql
SELECT COUNT(*) as ai_responses
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.facility_id = :facility_id
  AND m.role = 'assistant'
  AND m.created_at >= DATE_TRUNC('month', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Tokyo')
  AND m.created_at < DATE_TRUNC('month', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Tokyo') + INTERVAL '1 month';
```

---

### ステップ3: Frontend実装（1日）

#### 5.1 コンポーネント作成

**1. MonthlyUsageCard.vue**（カード1）
- **ファイル**: `frontend/src/components/admin/dashboard/MonthlyUsageCard.vue`
- **機能**:
  - プログレスバー表示（使用率に応じた色分け）
  - プラン別表示ロジック
    - **Freeプラン**: 30件超過後は「FAQのみ対応中」バッジ表示
    - **Miniプラン**: 「従量課金プラン」バッジ表示（プログレスバーなし）
    - **Small/Standard/Premium**: プログレスバー + 残数表示
  - 色分けルール:
    - 0-70%: 緑（`text-green-600`）
    - 71-90%: 黄色（`text-yellow-600`）
    - 91-99%: オレンジ（`text-orange-600`）
    - 100%+: 赤（`text-red-600`）

**2. AiAutomationCard.vue**（カード2）
- **ファイル**: `frontend/src/components/admin/dashboard/AiAutomationCard.vue`
- **機能**:
  - AI自動応答数表示
  - 自動化率表示（パーセンテージ + プログレスバー）

**3. EscalationsSummaryCard.vue**（カード3）
- **ファイル**: `frontend/src/components/admin/dashboard/EscalationsSummaryCard.vue`
- **機能**:
  - エスカレーション総数表示
  - 未解決数・解決済み数表示
  - 未解決数が1件以上の場合、赤バッジで強調

**4. UnresolvedListCard.vue**（カード8）
- **ファイル**: `frontend/src/components/admin/dashboard/UnresolvedListCard.vue`
- **機能**:
  - 未解決エスカレーションリスト表示（最新10件）
  - クリックで会話詳細ページに遷移

#### 5.2 ダッシュボード画面更新
**ファイル**: `frontend/src/views/admin/DashboardView.vue`

**変更内容**:
1. 月次統計セクションを追加（最優先表示エリア）
2. 既存の週次サマリーは維持（副次的な参考情報）
3. レイアウト:
   ```
   [月次統計セクション]
   - カード1: 今月の質問数 / プラン上限
   - カード2: 今月のAI自動応答数
   - カード3: 今月のエスカレーション数
   - カード8: 未解決のエスカレーション
   
   [週次サマリーセクション]（既存維持）
   [リアルタイム情報セクション]（既存維持）
   ```

#### 5.3 TypeScript型定義
**ファイル**: `frontend/src/types/dashboard.ts`（既存ファイルを拡張）

**追加型定義**:
```typescript
export interface MonthlyUsage {
  current_month_questions: number;
  plan_type: 'Free' | 'Mini' | 'Small' | 'Standard' | 'Premium';
  plan_limit: number | null;
  usage_percentage: number | null;
  remaining_questions: number | null;
  overage_questions: number;
  status: 'normal' | 'warning' | 'overage' | 'faq_only';
}

export interface AiAutomation {
  ai_responses: number;
  total_questions: number;
  automation_rate: number;
}

export interface EscalationsSummary {
  total: number;
  unresolved: number;
  resolved: number;
}

export interface UnresolvedEscalation {
  id: number;
  conversation_id: number;
  created_at: string;
  message: string;
}
```

---

### ステップ4: 統合テスト（0.5日）

#### 6.1 テスト項目

**各プランでの表示確認**:
- Freeプラン: 30件以内・30件超過
- Miniプラン: 従量課金表示
- Small/Standard/Premium: 上限内・警告範囲・超過

**月次集計の正確性確認**:
- SQLクエリ検証
- タイムゾーン処理確認（JST基準）
- 月次集計期間の境界値テスト（月末・月初）

**エラーハンドリング確認**:
- プラン情報が取得できない場合
- データが存在しない場合
- APIエラー時の表示

---

## 4. プラン別表示ロジック詳細

### 4.1 Freeプラン
- **30件以内**: プログレスバー表示（緑）
- **30件超過**: 「FAQのみ対応中」バッジ表示（赤）

### 4.2 Miniプラン
- 上限表示なし
- 「従量課金プラン」バッジ表示
- プログレスバーなし

### 4.3 Small/Standard/Premiumプラン
- プログレスバー表示
- 残数表示（「あと○○件で上限です」）
- 使用率に応じた色分け

---

## 5. タイムゾーン処理

### 5.1 重要事項
- **すべての統計は日本時間（JST）基準**
- データベースはUTC保存
- 取得時にJST変換

### 5.2 実装方法
```python
import pytz
from datetime import datetime

# JSTタイムゾーン取得
jst = pytz.timezone('Asia/Tokyo')

# 今月の開始時刻（JST）
now_jst = datetime.now(jst)
month_start_jst = now_jst.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

# UTCに変換してSQLクエリで使用
month_start_utc = month_start_jst.astimezone(pytz.UTC)
```

---

## 6. 次のセッションで最初にやるべきこと

### 6.1 環境確認
```bash
# Dockerコンテナの状態確認
cd /Users/kurinobu/projects/yadopera
docker-compose ps

# データベースバックアップ（重要！）
docker-compose exec postgres pg_dump -U yadopera_user yadopera > database_backup_step2_$(date +%Y%m%d_%H%M%S).sql
```

### 6.2 実装開始
1. **ステップ1（データベース拡張）から開始**
   - Alembicマイグレーションファイル作成
   - モデル更新
   - マイグレーション実行
   - 動作確認

2. **ステップ2（Backend API実装）**
   - サービス層実装
   - スキーマ定義
   - APIエンドポイント実装
   - 動作確認（curl等でテスト）

3. **ステップ3（Frontend実装）**
   - コンポーネント作成
   - ダッシュボード画面更新
   - 動作確認（ブラウザテスト）

4. **ステップ4（統合テスト）**
   - 各プランでの表示確認
   - 月次集計の正確性確認
   - エラーハンドリング確認

---

## 7. 注意事項

### 7.1 データベースバックアップ
- **実装前には必ずデータベースバックアップを取得**
- マイグレーション失敗時のロールバック手順を確認

### 7.2 既存機能の維持
- 既存のダッシュボードAPI（週次サマリー等）は維持
- 既存のダッシュボード画面レイアウトは維持
- 月次統計は**追加**する形で実装

### 7.3 パフォーマンス
- Phase 2: リアルタイム集計（ポーリング5分間隔）
- Phase 3以降: 日次バッチで`monthly_usage_cache`テーブル更新（パフォーマンス最適化）

### 7.4 テストデータ
- 各プランでのテストデータを準備
- 月次集計の境界値テスト（月末・月初）を実施

---

## 8. 成功基準

### 8.1 Phase 2完了条件
- ✅ 月次統計カード（カード1-3、カード8）が正常に表示される
- ✅ プラン別表示ロジックが正しく動作する（Free/Mini/Small/Standard/Premium）
- ✅ 使用率に応じた色分け・警告表示が正しく動作する
- ✅ 月次集計が正確（JST基準）
- ✅ 「従量課金でいくら使っているか」「残りどれくらいで上限か」が明確に表示される

---

## 9. 関連ファイル一覧

### 9.1 Backend
- `backend/alembic/versions/012_add_facility_plan_columns.py`（新規作成）
- `backend/app/models/facility.py`（更新）
- `backend/app/services/dashboard_service.py`（更新）
- `backend/app/schemas/dashboard.py`（更新）
- `backend/app/api/v1/admin/dashboard.py`（更新）

### 9.2 Frontend
- `frontend/src/components/admin/dashboard/MonthlyUsageCard.vue`（新規作成）
- `frontend/src/components/admin/dashboard/AiAutomationCard.vue`（新規作成）
- `frontend/src/components/admin/dashboard/EscalationsSummaryCard.vue`（新規作成）
- `frontend/src/components/admin/dashboard/UnresolvedListCard.vue`（新規作成）
- `frontend/src/views/admin/DashboardView.vue`（更新）
- `frontend/src/types/dashboard.ts`（更新）

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025年1月14日  
**Status**: 準備完了、次のセッションで実装開始可能

