# Phase 2: 全問題解決ステップ計画

**作成日**: 2025年12月2日  
**実施者**: Auto (AI Assistant)  
**対象**: Phase 2 ステップ1（管理画面・ゲスト画面の動作確認）で発見された7つの課題  
**状態**: 🔴 **緊急対応が必要な問題が発生中**

**最新更新**: 2025年12月2日 - 緊急対応が必要な問題が発生。詳細は`Phase2_引き継ぎ書_20251202.md`を参照。

---

## 1. 調査分析の概要

### 1.1 課題の分類

7つの課題を以下の3つのカテゴリに分類：

1. **フロントエンドの状態管理・UI更新問題**（課題1, 2）
2. **バックエンドの未実装機能・データ取得問題**（課題3, 4, 5）
3. **環境設定・外部API接続問題**（課題6）

### 1.2 根本原因の特定

#### 課題1, 2: FAQ追加・削除後の画面反映問題

**調査結果**:
- バックエンドは正常に動作している（ログ確認済み）
- フロントエンドの`fetchFaqs()`は呼ばれている
- キャッシュキーの不一致が原因の可能性

**根本原因**:
- `cache_key()`関数の生成ロジックと`delete_cache_pattern()`のパターンが一致していない可能性
- フロントエンドの`fetchFaqs()`がキャッシュから古いデータを取得している可能性

**確認が必要な点**:
- `cache_key("faq:list", facility_id=2)`の実際の生成結果
- `delete_cache_pattern("faq:list:facility_id=2*")`のパターンマッチング

---

#### 課題3: 未解決質問リストからのFAQ追加エラー

**調査結果**:
- フロントエンドがモックデータ（`mockUnresolvedQuestions`）を使用している
- `FaqManagement.vue`の`handleAddFaqFromQuestion`が`generateSuggestion`を呼び出しているが、これはモック関数
- 実際のAPIエンドポイントが存在しない、または未実装

**根本原因**:
- 未解決質問リストのAPIエンドポイントが未実装
- フロントエンドがモックデータを使用しており、実際のデータベースと不一致

**確認が必要な点**:
- 未解決質問（エスカレーション済み）を取得するAPIエンドポイントの存在
- フロントエンドが実際のAPIを呼び出すように修正が必要

---

#### 課題4: ゲストフィードバック連動FAQからのFAQ改善提案エラー

**調査結果**:
- フロントエンドがモックデータ（`mockLowRatedAnswers`）を使用している
- `FeedbackLinkedFaqs.vue`の`handleImprove`が`faqSuggestionApi.generateSuggestion(message_id)`を呼び出している
- `message_id=201`が存在しない（データベースに該当するメッセージがない）

**根本原因**:
- ゲストフィードバック（低評価回答）を取得するAPIエンドポイントが未実装
- フロントエンドがモックデータを使用しており、実際のデータベースと不一致
- モックデータの`message_id`が実際のデータベースに存在しない

**確認が必要な点**:
- 低評価回答を取得するAPIエンドポイントの存在
- フロントエンドが実際のAPIを呼び出すように修正が必要

---

#### 課題5: よくある質問が表示されない問題

**調査結果**:
- `backend/app/services/facility_service.py`の`get_facility_public_info`メソッドで、`top_questions`が空リストのまま
- コメント: `# よくある質問TOP3（Week 1では空リスト、Week 2で実装）`

**根本原因**:
- `top_questions`の取得処理が未実装
- FAQからTOP3を取得する処理が必要

**実装が必要な処理**:
- `facility_id`に紐づくFAQから、`is_active=True`、`priority`の降順でTOP3を取得
- フロントエンドの`TopQuestion`型に合わせて変換（`id`, `question`, `answer`, `category`）

---

#### 課題6: フォールバックメッセージが表示される問題

**調査結果**:
- OpenAI APIキーが無効: `Incorrect API key provided: your_ope************here`
- `docker-compose.yml`に`OPENAI_API_KEY`環境変数が設定されていない
- `.env`ファイルの確認が必要

**根本原因**:
- Dockerコンテナに`OPENAI_API_KEY`環境変数が渡されていない
- `.env`ファイルが存在しない、または正しく設定されていない

**確認が必要な点**:
- `backend/.env`ファイルの存在と内容
- `docker-compose.yml`の`backend`サービスに`OPENAI_API_KEY`環境変数を追加する必要がある

---

#### 課題7: フロントエンドとバックエンドのデータ不一致

**調査結果**:
- 課題3, 4の根本原因と重複
- フロントエンドがモックデータを使用しているため、データベースの状態と不一致

**根本原因**:
- フロントエンドがモックデータを使用している
- 実際のAPIエンドポイントが未実装、またはフロントエンドが呼び出していない

---

## 2. 全問題解決のステップ計画

### ステップ1: OpenAI APIキーの設定（課題6）

**優先度**: 🔴 **最優先**

**目的**: OpenAI APIキーを正しく設定し、AI機能を動作させる

**実施内容**:
1. `backend/.env`ファイルの確認・作成
2. `docker-compose.yml`の`backend`サービスに`OPENAI_API_KEY`環境変数を追加
3. Dockerコンテナの再起動
4. APIキーの動作確認

**期待される結果**:
- OpenAI APIが正常に動作する
- フォールバックメッセージが表示されなくなる
- 正常なAI応答が生成される

**推定時間**: 10分

---

### ステップ2: よくある質問TOP3の実装（課題5）

**優先度**: 🔴 **最優先**

**目的**: ゲスト画面にFAQのTOP3を表示する

**実施内容**:
1. `backend/app/services/facility_service.py`の`get_facility_public_info`メソッドを修正
2. FAQからTOP3を取得する処理を実装
   - `facility_id`に紐づくFAQを取得
   - `is_active=True`でフィルタ
   - `priority`の降順、`created_at`の降順でソート
   - 上位3件を取得
3. `TopQuestion`型に合わせて変換（`id`, `question`, `answer`, `category`）
4. フロントエンドの型定義を確認（`TopQuestion`）

**期待される結果**:
- ゲスト画面にFAQのTOP3が表示される
- 「よくある質問はありません」が表示されなくなる

**推定時間**: 30分

---

### ステップ3: 未解決質問リストAPIの実装（課題3）

**優先度**: 🟠 **高**

**目的**: 未解決質問リストを実際のデータベースから取得する

**実施内容**:
1. バックエンドAPIエンドポイントの確認・実装
   - エスカレーション済みで未解決の質問を取得するAPI
   - `/api/v1/admin/escalations`または`/api/v1/admin/unresolved-questions`
2. フロントエンドAPIクライアントの実装
   - `frontend/src/api/unresolvedQuestions.ts`を作成
3. `FaqManagement.vue`の修正
   - `mockUnresolvedQuestions`を削除
   - 実際のAPIからデータを取得するように修正
4. `UnresolvedQuestionsList.vue`の確認（既存の実装で問題ないか）

**期待される結果**:
- 未解決質問リストが実際のデータベースから取得される
- FAQ追加ボタンが正常に動作する

**推定時間**: 1時間

---

### ステップ4: ゲストフィードバック連動FAQ APIの実装（課題4）

**優先度**: 🟠 **高**

**目的**: 低評価回答を実際のデータベースから取得する

**実施内容**:
1. バックエンドAPIエンドポイントの確認・実装
   - 低評価回答（👎評価が2回以上）を取得するAPI
   - `/api/v1/admin/feedback/low-rated`または`/api/v1/admin/messages/low-rated`
2. フロントエンドAPIクライアントの実装
   - `frontend/src/api/feedback.ts`を作成
3. `FaqManagement.vue`の修正
   - `mockLowRatedAnswers`を削除
   - 実際のAPIからデータを取得するように修正
4. `FeedbackLinkedFaqs.vue`の確認（既存の実装で問題ないか）

**期待される結果**:
- 低評価回答が実際のデータベースから取得される
- FAQ改善提案ボタンが正常に動作する

**推定時間**: 1時間

---

### ステップ5: FAQ追加・削除後の画面反映問題の修正（課題1, 2）

**優先度**: 🟡 **中**

**目的**: FAQ追加・削除後に画面が即座に更新されるようにする

**実施内容**:
1. キャッシュキーの生成ロジックの確認
   - `cache_key("faq:list", facility_id=2)`の実際の生成結果を確認
   - `delete_cache_pattern("faq:list:facility_id=2*")`のパターンマッチングを確認
2. キャッシュ無効化の修正
   - `delete_cache_pattern()`のパターンを修正
   - または、`cache_key()`の生成ロジックを修正
3. フロントエンドの`fetchFaqs()`の確認
   - エラーハンドリングの確認
   - ローディング状態の確認
4. フロントエンドの状態管理の確認
   - Piniaストアの状態更新の確認
   - リアクティブな更新の確認

**期待される結果**:
- FAQ追加・削除後に画面が即座に更新される
- キャッシュの問題が解決される

**推定時間**: 1時間

---

### ステップ6: データ整合性の確認と修正（課題7）

**優先度**: 🟡 **中**

**目的**: フロントエンドとバックエンドのデータ不一致を解決する

**実施内容**:
1. ステップ3, 4の実施後に自動的に解決される可能性が高い
2. データベースの状態確認
   - `faq_suggestions`テーブルのデータ確認
   - `messages`テーブルのデータ確認
3. フロントエンドのモックデータの完全削除
   - すべてのモックデータを削除
   - 実際のAPIからデータを取得するように修正

**期待される結果**:
- フロントエンドとバックエンドのデータが一致する
- エラーが発生しなくなる

**推定時間**: 30分（ステップ3, 4の実施後に実施）

---

## 3. 実施順序と依存関係

### 3.1 実施順序

1. **ステップ1**: OpenAI APIキーの設定（課題6）
   - 他のステップに影響しない
   - 最優先で実施

2. **ステップ2**: よくある質問TOP3の実装（課題5）
   - ステップ1の完了後に実施可能
   - 独立した機能

3. **ステップ3**: 未解決質問リストAPIの実装（課題3）
   - ステップ1の完了後に実施可能
   - ステップ6の前提

4. **ステップ4**: ゲストフィードバック連動FAQ APIの実装（課題4）
   - ステップ1の完了後に実施可能
   - ステップ6の前提

5. **ステップ5**: FAQ追加・削除後の画面反映問題の修正（課題1, 2）
   - 他のステップに影響しない
   - 独立した修正

6. **ステップ6**: データ整合性の確認と修正（課題7）
   - ステップ3, 4の完了後に実施
   - 最終確認

### 3.2 依存関係図

```
ステップ1 (OpenAI APIキー)
  ├─> ステップ2 (よくある質問TOP3)
  ├─> ステップ3 (未解決質問リストAPI)
  └─> ステップ4 (ゲストフィードバック連動FAQ API)
        └─> ステップ6 (データ整合性)

ステップ5 (FAQ追加・削除後の画面反映)
  └─> (独立)

ステップ3 + ステップ4
  └─> ステップ6 (データ整合性)
```

---

## 4. 各ステップの詳細実装計画

### ステップ1: OpenAI APIキーの設定

#### 1.1 調査・確認

**実施内容**:
1. `backend/.env`ファイルの存在確認
2. `backend/.env`ファイルの内容確認（`OPENAI_API_KEY`の設定）
3. `docker-compose.yml`の`backend`サービスの環境変数設定確認

**確認コマンド**:
```bash
# .envファイルの確認
ls -la backend/.env
cat backend/.env | grep OPENAI_API_KEY

# docker-compose.ymlの確認
grep -A 10 "backend:" docker-compose.yml
```

#### 1.2 修正内容

**実施内容**:
1. `backend/.env`ファイルの作成（存在しない場合）
2. `OPENAI_API_KEY`の設定
3. `docker-compose.yml`の`backend`サービスに`OPENAI_API_KEY`環境変数を追加

**修正ファイル**:
- `docker-compose.yml`

**修正内容**:
```yaml
backend:
  environment:
    - DATABASE_URL=postgresql://yadopera_user:yadopera_password@postgres:5432/yadopera
    - REDIS_URL=redis://redis:6379/0
    - ENVIRONMENT=development
    - DEBUG=True
    - OPENAI_API_KEY=${OPENAI_API_KEY}  # 追加
```

#### 1.3 動作確認

**実施内容**:
1. Dockerコンテナの再起動
2. バックエンドログの確認（OpenAI APIエラーが発生しないか）
3. ゲスト画面でメッセージ送信テスト

**確認コマンド**:
```bash
# Dockerコンテナの再起動
docker-compose restart backend

# バックエンドログの確認
docker-compose logs backend --tail=50 | grep -i "openai\|api key\|error"
```

---

### ステップ2: よくある質問TOP3の実装

#### 2.1 調査・確認

**実施内容**:
1. `backend/app/services/facility_service.py`の`get_facility_public_info`メソッドの確認
2. `backend/app/models/faq.py`のFAQモデルの確認
3. `frontend/src/types/facility.ts`の`TopQuestion`型の確認

**確認ファイル**:
- `backend/app/services/facility_service.py` (78-79行目)
- `frontend/src/types/facility.ts` (16-21行目)

#### 2.2 修正内容

**実施内容**:
1. `backend/app/services/facility_service.py`の`get_facility_public_info`メソッドを修正
2. FAQからTOP3を取得する処理を実装

**修正ファイル**:
- `backend/app/services/facility_service.py`

**修正内容**:
```python
# よくある質問TOP3を取得
from app.models.faq import FAQ
from sqlalchemy import select

# FAQからTOP3を取得
faq_query = select(FAQ).where(
    FAQ.facility_id == facility.id,
    FAQ.is_active == True
).order_by(
    FAQ.priority.desc(),
    FAQ.created_at.desc()
).limit(3)

faq_result = await db.execute(faq_query)
top_faqs = faq_result.scalars().all()

# TopQuestion型に変換
top_questions = [
    {
        "id": faq.id,
        "question": faq.question,
        "answer": faq.answer,
        "category": faq.category
    }
    for faq in top_faqs
]
```

#### 2.3 動作確認

**実施内容**:
1. バックエンドAPIの動作確認
2. ゲスト画面でFAQのTOP3が表示されることを確認

**確認コマンド**:
```bash
# APIの動作確認
curl http://localhost:8000/api/v1/facility/test-facility | jq '.top_questions'
```

---

### ステップ3: 未解決質問リストAPIの実装

#### 3.1 調査・確認

**実施内容**:
1. エスカレーション関連のAPIエンドポイントの確認
2. `backend/app/api/v1/admin/escalations.py`の存在確認
3. `backend/app/models/escalation.py`の確認

**確認ファイル**:
- `backend/app/api/v1/admin/escalations.py`（存在するか）
- `backend/app/models/escalation.py`

#### 3.2 修正内容

**実施内容**:
1. バックエンドAPIエンドポイントの実装（存在しない場合）
2. フロントエンドAPIクライアントの実装
3. `FaqManagement.vue`の修正

**修正ファイル**:
- `backend/app/api/v1/admin/escalations.py`（新規作成または修正）
- `frontend/src/api/unresolvedQuestions.ts`（新規作成）
- `frontend/src/views/admin/FaqManagement.vue`

**修正内容**:
1. バックエンド: 未解決質問（エスカレーション済み）を取得するAPIエンドポイント
2. フロントエンド: APIクライアントの実装
3. フロントエンド: `mockUnresolvedQuestions`を削除し、実際のAPIから取得

---

### ステップ4: ゲストフィードバック連動FAQ APIの実装

#### 4.1 調査・確認

**実施内容**:
1. ゲストフィードバック関連のAPIエンドポイントの確認
2. `backend/app/models/guest_feedback.py`の確認
3. 低評価回答を取得する処理の確認

**確認ファイル**:
- `backend/app/api/v1/admin/feedback.py`（存在するか）
- `backend/app/models/guest_feedback.py`

#### 4.2 修正内容

**実施内容**:
1. バックエンドAPIエンドポイントの実装（存在しない場合）
2. フロントエンドAPIクライアントの実装
3. `FaqManagement.vue`の修正

**修正ファイル**:
- `backend/app/api/v1/admin/feedback.py`（新規作成または修正）
- `frontend/src/api/feedback.ts`（新規作成）
- `frontend/src/views/admin/FaqManagement.vue`

**修正内容**:
1. バックエンド: 低評価回答（👎評価が2回以上）を取得するAPIエンドポイント
2. フロントエンド: APIクライアントの実装
3. フロントエンド: `mockLowRatedAnswers`を削除し、実際のAPIから取得

---

### ステップ5: FAQ追加・削除後の画面反映問題の修正

#### 5.1 調査・確認

**実施内容**:
1. `cache_key()`関数の生成ロジックの確認
2. `delete_cache_pattern()`のパターンマッチングの確認
3. 実際のキャッシュキーの生成結果の確認

**確認ファイル**:
- `backend/app/core/cache.py`
- `backend/app/services/faq_service.py`

**確認コマンド**:
```bash
# キャッシュキーの生成結果を確認
docker-compose exec backend python -c "
from app.core.cache import cache_key
print(cache_key('faq:list', facility_id=2))
"
```

#### 5.2 修正内容

**実施内容**:
1. キャッシュキーの生成ロジックとパターンマッチングの一致確認
2. 必要に応じて修正

**修正ファイル**:
- `backend/app/services/faq_service.py`（キャッシュ無効化のパターン修正）

**修正内容**:
- `delete_cache_pattern()`のパターンを`cache_key()`の生成結果と一致させる

---

### ステップ6: データ整合性の確認と修正

#### 6.1 調査・確認

**実施内容**:
1. データベースの状態確認
2. フロントエンドのモックデータの完全削除確認

**確認コマンド**:
```bash
# データベースの状態確認
docker-compose exec postgres psql -U yadopera_user -d yadopera -c "SELECT id, facility_id, status FROM faq_suggestions LIMIT 10;"
docker-compose exec postgres psql -U yadopera_user -d yadopera -c "SELECT id, facility_id FROM messages LIMIT 10;"
```

#### 6.2 修正内容

**実施内容**:
1. フロントエンドのモックデータの完全削除
2. 実際のAPIからデータを取得するように修正

**修正ファイル**:
- `frontend/src/views/admin/FaqManagement.vue`

---

## 5. 実施スケジュール

### 5.1 推定時間

| ステップ | 課題 | 推定時間 |
|---------|------|---------|
| ステップ1 | 課題6: OpenAI APIキーの設定 | 10分 |
| ステップ2 | 課題5: よくある質問TOP3の実装 | 30分 |
| ステップ3 | 課題3: 未解決質問リストAPIの実装 | 1時間 |
| ステップ4 | 課題4: ゲストフィードバック連動FAQ APIの実装 | 1時間 |
| ステップ5 | 課題1, 2: FAQ追加・削除後の画面反映問題の修正 | 1時間 |
| ステップ6 | 課題7: データ整合性の確認と修正 | 30分 |
| **合計** | | **約4時間10分** |

### 5.2 実施順序

1. **ステップ1** (10分) - 最優先
2. **ステップ2** (30分) - ステップ1完了後
3. **ステップ3** (1時間) - ステップ1完了後、並行実施可能
4. **ステップ4** (1時間) - ステップ1完了後、並行実施可能
5. **ステップ5** (1時間) - 独立、いつでも実施可能
6. **ステップ6** (30分) - ステップ3, 4完了後

---

## 6. リスクと対策

### 6.1 リスク

1. **OpenAI APIキーの設定ミス**
   - 対策: `.env`ファイルの内容を確認し、正しいAPIキーを設定

2. **キャッシュの問題が解決しない**
   - 対策: キャッシュを完全にクリアし、再テスト

3. **APIエンドポイントの実装が複雑**
   - 対策: 既存のAPIエンドポイントを参考に実装

4. **フロントエンドの型定義の不一致**
   - 対策: 型定義を確認し、必要に応じて修正

### 6.2 対策

1. **各ステップの実施前にバックアップを作成**
2. **各ステップの実施後に動作確認を実施**
3. **問題が発生した場合は、ロールバックを実施**

---

## 7. 完了条件

### 7.1 各ステップの完了条件

- **ステップ1**: OpenAI APIが正常に動作し、フォールバックメッセージが表示されない
- **ステップ2**: ゲスト画面にFAQのTOP3が表示される
- **ステップ3**: 未解決質問リストが実際のデータベースから取得され、FAQ追加が正常に動作する
- **ステップ4**: 低評価回答が実際のデータベースから取得され、FAQ改善提案が正常に動作する
- **ステップ5**: FAQ追加・削除後に画面が即座に更新される
- **ステップ6**: フロントエンドとバックエンドのデータが一致し、エラーが発生しない

### 7.2 全体の完了条件

- すべてのステップが完了している
- すべての課題が解決されている
- ブラウザテストでエラーが発生しない
- すべての機能が正常に動作している

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-02  
**Status**: ✅ **調査分析完了 → ステップ計画策定完了**

