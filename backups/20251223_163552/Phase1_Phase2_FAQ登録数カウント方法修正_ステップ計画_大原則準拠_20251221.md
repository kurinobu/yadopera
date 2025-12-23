# FAQ登録数カウント方法修正 ステップ計画（大原則準拠）

**作成日時**: 2025年12月21日 10時47分00秒  
**目的**: FAQ登録数を「意味（インテント）」単位で1件としてカウントするように修正  
**大原則**: 根本解決 > 暫定解決、具体的 > 一般、拙速 < 安全確実、Docker環境必須、バックアップ必須

---

## 修正概要

### 現状（問題あり）
- FAQは言語ごとに別レコードとして保存
- FAQ登録数は言語ごとにカウント（「今何時ですか？」と「what time is it now?」は2件）

### 修正後（目標）
- FAQは「意味（インテント）」単位で1件
- 言語は`FAQ_translation`テーブルに分離
- FAQ登録数は「意味（インテント）」単位で1件としてカウント（「今何時ですか？」と「what time is it now?」は1件）

---

## 影響範囲

### データベーススキーマ
- `faqs`テーブル: 構造変更（`language`, `question`, `answer`, `embedding`を削除、`intent_key`を追加）
- `faq_translations`テーブル: 新規作成（`faq_id`, `language`, `question`, `answer`, `embedding`）

### バックエンド（影響ファイル数: 約10ファイル）
1. `backend/app/models/faq.py`: FAQモデル修正
2. `backend/app/models/faq_translation.py`: 新規作成（FAQ翻訳モデル）
3. `backend/app/services/faq_service.py`: FAQサービス修正（CRUD操作）
4. `backend/app/api/v1/admin/faqs.py`: FAQ APIエンドポイント修正
5. `backend/app/schemas/faq.py`: FAQスキーマ修正
6. `backend/app/ai/vector_search.py`: ベクトル検索修正（FAQ検索）
7. `backend/app/ai/embeddings.py`: 埋め込み生成修正（FAQ埋め込み）
8. `backend/app/services/dashboard_service.py`: ダッシュボードサービス修正（FAQカウント）
9. `backend/app/services/faq_suggestion_service.py`: FAQ提案サービス修正
10. `backend/app/ai/engine.py`: RAGエンジン修正（FAQ使用）

### フロントエンド（影響ファイル数: 約10ファイル）
1. `frontend/src/types/faq.ts`: FAQ型定義修正
2. `frontend/src/api/faq.ts`: FAQ APIクライアント修正
3. `frontend/src/views/admin/FaqManagement.vue`: FAQ管理画面修正
4. `frontend/src/components/admin/FaqList.vue`: FAQリストコンポーネント修正
5. `frontend/src/components/admin/FaqForm.vue`: FAQフォームコンポーネント修正
6. その他のFAQ関連コンポーネント

### テストデータスクリプト
1. `backend/create_staging_test_data.py`: テストデータ作成スクリプト修正
2. `backend/create_test_data.py`: テストデータ作成スクリプト修正

### ドキュメント
1. `docs/Summary/yadopera-v03-summary.md`: 要約定義書修正（料金プラン説明）
2. `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`: アーキテクチャ設計書修正
3. `landing/index.html`: ランディングページ修正（料金プラン説明）

---

## 修正ステップ計画

### ステップ0: 準備・調査（完了）

✅ **完了**: 現状の調査分析、外部評価の評価分析、影響範囲の特定

---

### ステップ1: バックアップ作成

**目的**: 修正前の状態を完全にバックアップ

**実施内容**:
1. Gitコミット（現在の状態をコミット）
2. データベースバックアップ（既存FAQデータのエクスポート）
3. コードバックアップ（影響を受けるファイルのコピー）

**確認事項**:
- ✅ Gitコミット完了
- ✅ データベースバックアップ完了
- ✅ コードバックアップ完了

**所要時間**: 約30分

---

### ステップ2: データベーススキーマ設計・マイグレーション準備

**目的**: 新しいデータベーススキーマを設計し、Alembicマイグレーションファイルを作成

**実施内容**:

#### 2.1 新しいデータモデル設計

**`FAQ`テーブル（修正後）**:
```sql
CREATE TABLE faqs (
    id SERIAL PRIMARY KEY,
    facility_id INTEGER NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,  -- 'basic', 'facilities', 'location', 'trouble'
    intent_key VARCHAR(100) NOT NULL,  -- インテント識別キー（例: 'checkout_time'）
    priority INTEGER DEFAULT 1,  -- 1-5
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(facility_id, intent_key)  -- 同じ施設内で同じインテントは1つだけ
);
```

**`faq_translations`テーブル（新規）**:
```sql
CREATE TABLE faq_translations (
    id SERIAL PRIMARY KEY,
    faq_id INTEGER NOT NULL REFERENCES faqs(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL DEFAULT 'en',  -- 'en', 'ja', 'zh-TW', 'fr'
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(faq_id, language)  -- 同じFAQの同じ言語は1つだけ
);
```

#### 2.2 Alembicマイグレーションファイル作成

**ファイル名**: `backend/alembic/versions/009_refactor_faq_to_intent_based.py`

**マイグレーション内容**:
1. `faq_translations`テーブル作成
2. 既存`faqs`テーブルのデータ移行（`language`, `question`, `answer`, `embedding`を`faq_translations`に移動）
3. `faqs`テーブルの構造変更（`language`, `question`, `answer`, `embedding`を削除、`intent_key`を追加）
4. インデックス作成・削除

**確認事項**:
- ✅ マイグレーションファイル作成完了
- ✅ マイグレーションロールバック手順確認完了

**所要時間**: 約2時間

---

### ステップ3: 既存データ移行スクリプト作成

**目的**: 既存のFAQデータを新しい構造に移行

**実施内容**:

#### 3.1 データ移行ロジック

1. **既存FAQデータの分析**:
   - 同じ`facility_id`、同じ`category`、同じ`question`（意味的に同じ）のFAQをグループ化
   - 各グループから`intent_key`を生成（例: `basic_checkout_time`）

2. **データ移行**:
   - 各グループから1つの`FAQ`レコードを作成（`intent_key`を設定）
   - 各グループの各言語のFAQを`faq_translations`テーブルに移動

3. **インテントキー生成ルール**:
   - `{category}_{normalized_question}`形式
   - 例: `basic_checkout_time`, `facilities_wifi_password`

**確認事項**:
- ✅ データ移行スクリプト作成完了
- ✅ データ移行スクリプトのテスト完了

**所要時間**: 約2時間

---

### ステップ4: バックエンドモデル修正

**目的**: SQLAlchemyモデルを新しい構造に修正

**実施内容**:

#### 4.1 `backend/app/models/faq.py`修正

- `FAQ`モデルから`language`, `question`, `answer`, `embedding`を削除
- `intent_key`を追加
- `faq_translations`リレーションシップを追加

#### 4.2 `backend/app/models/faq_translation.py`新規作成

- `FAQTranslation`モデルを作成
- `faq_id`, `language`, `question`, `answer`, `embedding`を含む
- `faq`リレーションシップを追加

**確認事項**:
- ✅ モデル修正完了
- ✅ リレーションシップ確認完了

**所要時間**: 約1時間

---

### ステップ5: バックエンドスキーマ修正

**目的**: Pydanticスキーマを新しい構造に修正

**実施内容**:

#### 5.1 `backend/app/schemas/faq.py`修正

- `FAQRequest`: `intent_key`を追加、`language`, `question`, `answer`を削除
- `FAQTranslationRequest`: 新規作成（`language`, `question`, `answer`を含む）
- `FAQResponse`: `intent_key`を追加、`language`, `question`, `answer`を削除、`translations`を追加
- `FAQTranslationResponse`: 新規作成

**確認事項**:
- ✅ スキーマ修正完了
- ✅ バリデーション確認完了

**所要時間**: 約1時間

---

### ステップ6: バックエンドサービス修正

**目的**: FAQサービスのCRUD操作を新しい構造に修正

**実施内容**:

#### 6.1 `backend/app/services/faq_service.py`修正

**`get_faqs`メソッド**:
- `FAQ`を取得し、関連する`FAQTranslation`を取得
- `FAQResponse`に`translations`を含める

**`create_faq`メソッド**:
- `FAQ`を作成（`intent_key`を設定）
- `FAQTranslation`を作成（`language`, `question`, `answer`, `embedding`を含む）

**`update_faq`メソッド**:
- `FAQ`を更新
- `FAQTranslation`を更新または作成

**`delete_faq`メソッド**:
- `FAQ`を削除（CASCADEで`FAQTranslation`も削除）

**FAQ登録数カウント**:
- `FAQ.id`をカウント（言語に関係なく、インテント単位で1件）

**確認事項**:
- ✅ サービス修正完了
- ✅ CRUD操作確認完了

**所要時間**: 約3時間

---

### ステップ7: ベクトル検索修正

**目的**: ベクトル検索を新しい構造に修正

**実施内容**:

#### 7.1 `backend/app/ai/vector_search.py`修正

**`search_similar_faqs`関数**:
- `faq_translations`テーブルから検索
- 検索結果の`FAQTranslation`から`FAQ`を取得
- 同じ`faq_id`の`FAQTranslation`をグループ化して返す

**確認事項**:
- ✅ ベクトル検索修正完了
- ✅ 検索結果確認完了

**所要時間**: 約2時間

---

### ステップ8: 埋め込み生成修正

**目的**: 埋め込み生成を新しい構造に修正

**実施内容**:

#### 8.1 `backend/app/ai/embeddings.py`修正

**`generate_faq_embedding`関数**:
- `FAQTranslation`を受け取るように修正
- `FAQTranslation.question`と`FAQTranslation.answer`を結合して埋め込み生成

**確認事項**:
- ✅ 埋め込み生成修正完了
- ✅ 埋め込み生成確認完了

**所要時間**: 約1時間

---

### ステップ9: ダッシュボードサービス修正

**目的**: ダッシュボードサービスのFAQカウントを修正

**実施内容**:

#### 9.1 `backend/app/services/dashboard_service.py`修正

**FAQ登録数カウント**:
- `FAQ.id`をカウント（言語に関係なく、インテント単位で1件）

**確認事項**:
- ✅ ダッシュボードサービス修正完了
- ✅ FAQカウント確認完了

**所要時間**: 約1時間

---

### ステップ10: FAQ提案サービス修正

**目的**: FAQ提案サービスを新しい構造に修正

**実施内容**:

#### 10.1 `backend/app/services/faq_suggestion_service.py`修正

**FAQ作成**:
- `FAQ`を作成（`intent_key`を生成）
- `FAQTranslation`を作成（提案された言語で）

**確認事項**:
- ✅ FAQ提案サービス修正完了
- ✅ FAQ作成確認完了

**所要時間**: 約2時間

---

### ステップ11: RAGエンジン修正

**目的**: RAGエンジンを新しい構造に修正

**実施内容**:

#### 11.1 `backend/app/ai/engine.py`修正

**`process_message`メソッド**:
- `search_similar_faqs`の結果から`FAQTranslation`を取得
- `FAQTranslation`から`FAQ`を取得してコンテキスト構築

**確認事項**:
- ✅ RAGエンジン修正完了
- ✅ コンテキスト構築確認完了

**所要時間**: 約2時間

---

### ステップ12: APIエンドポイント修正

**目的**: FAQ APIエンドポイントを新しい構造に修正

**実施内容**:

#### 12.1 `backend/app/api/v1/admin/faqs.py`修正

**`get_faqs`エンドポイント**:
- `FAQResponse`に`translations`を含める

**`create_faq`エンドポイント**:
- `FAQRequest`に`intent_key`と`translations`を含める

**`update_faq`エンドポイント**:
- `FAQUpdateRequest`に`intent_key`と`translations`を含める

**確認事項**:
- ✅ APIエンドポイント修正完了
- ✅ API動作確認完了

**所要時間**: 約2時間

---

### ステップ13: フロントエンド型定義修正

**目的**: フロントエンドの型定義を新しい構造に修正

**実施内容**:

#### 13.1 `frontend/src/types/faq.ts`修正

- `FAQ`型に`intent_key`を追加、`language`, `question`, `answer`を削除、`translations`を追加
- `FAQTranslation`型を新規作成
- `FAQCreate`型を修正
- `FAQUpdate`型を修正

**確認事項**:
- ✅ 型定義修正完了
- ✅ 型チェック確認完了

**所要時間**: 約1時間

---

### ステップ14: フロントエンドAPIクライアント修正

**目的**: フロントエンドのAPIクライアントを新しい構造に修正

**実施内容**:

#### 14.1 `frontend/src/api/faq.ts`修正

- APIリクエスト・レスポンスを新しい構造に修正

**確認事項**:
- ✅ APIクライアント修正完了
- ✅ API動作確認完了

**所要時間**: 約1時間

---

### ステップ15: フロントエンドコンポーネント修正

**目的**: フロントエンドのコンポーネントを新しい構造に修正

**実施内容**:

#### 15.1 `frontend/src/views/admin/FaqManagement.vue`修正

- FAQ一覧表示を修正（`translations`を表示）
- FAQ作成フォームを修正（`intent_key`と`translations`を入力）
- FAQ更新フォームを修正

#### 15.2 `frontend/src/components/admin/FaqList.vue`修正

- FAQリスト表示を修正（`translations`を表示）

#### 15.3 `frontend/src/components/admin/FaqForm.vue`修正

- FAQフォームを修正（`intent_key`と`translations`を入力）

**確認事項**:
- ✅ コンポーネント修正完了
- ✅ UI動作確認完了

**所要時間**: 約4時間

---

### ステップ16: テストデータスクリプト修正

**目的**: テストデータ作成スクリプトを新しい構造に修正

**実施内容**:

#### 16.1 `backend/create_staging_test_data.py`修正

- FAQ作成を新しい構造に修正（`FAQ`と`FAQTranslation`を作成）

#### 16.2 `backend/create_test_data.py`修正

- FAQ作成を新しい構造に修正（`FAQ`と`FAQTranslation`を作成）

**確認事項**:
- ✅ テストデータスクリプト修正完了
- ✅ テストデータ作成確認完了

**所要時間**: 約2時間

---

### ステップ17: ドキュメント修正

**目的**: ドキュメントを新しい構造に修正

**実施内容**:

#### 17.1 `docs/Summary/yadopera-v03-summary.md`修正

- 料金プランの「FAQ登録数」の説明を修正（「意味（インテント）」単位で1件としてカウント）

#### 17.2 `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`修正

- データベーススキーマの説明を修正（`FAQ`と`FAQTranslation`テーブル）

#### 17.3 `landing/index.html`修正

- 料金プランの説明を修正（「FAQ登録数」の説明）

**確認事項**:
- ✅ ドキュメント修正完了
- ✅ 説明確認完了

**所要時間**: 約2時間

---

### ステップ18: Docker環境でのテスト

**目的**: Docker環境で修正をテスト

**実施内容**:

1. **データベースマイグレーション実行**:
   - Alembicマイグレーションを実行
   - 既存データ移行スクリプトを実行

2. **バックエンドテスト**:
   - FAQ CRUD操作のテスト
   - ベクトル検索のテスト
   - ダッシュボードのFAQカウントのテスト

3. **フロントエンドテスト**:
   - FAQ管理画面のテスト
   - FAQ作成・更新・削除のテスト

**確認事項**:
- ✅ データベースマイグレーション成功
- ✅ 既存データ移行成功
- ✅ バックエンドテスト成功
- ✅ フロントエンドテスト成功

**所要時間**: 約4時間

---

### ステップ19: ブラウザテスト

**目的**: ブラウザで修正をテスト

**実施内容**:

1. **FAQ管理画面のテスト**:
   - FAQ一覧表示
   - FAQ作成（複数言語）
   - FAQ更新（複数言語）
   - FAQ削除

2. **ダッシュボードのテスト**:
   - FAQ登録数のカウント確認（言語に関係なく、インテント単位で1件）

**確認事項**:
- ✅ FAQ管理画面動作確認完了
- ✅ ダッシュボードFAQカウント確認完了

**所要時間**: 約2時間

---

### ステップ20: コミット・プッシュ

**目的**: 修正をコミット・プッシュ

**実施内容**:

1. **Gitコミット**:
   - すべての修正をコミット
   - コミットメッセージ: "refactor: FAQ登録数をインテント単位でカウントするように修正"

2. **Gitプッシュ**:
   - `develop`ブランチにプッシュ

**確認事項**:
- ✅ Gitコミット完了
- ✅ Gitプッシュ完了

**所要時間**: 約30分

---

## 総所要時間見積もり

| ステップ | 所要時間 |
|---------|---------|
| ステップ1: バックアップ作成 | 30分 |
| ステップ2: データベーススキーマ設計・マイグレーション準備 | 2時間 |
| ステップ3: 既存データ移行スクリプト作成 | 2時間 |
| ステップ4: バックエンドモデル修正 | 1時間 |
| ステップ5: バックエンドスキーマ修正 | 1時間 |
| ステップ6: バックエンドサービス修正 | 3時間 |
| ステップ7: ベクトル検索修正 | 2時間 |
| ステップ8: 埋め込み生成修正 | 1時間 |
| ステップ9: ダッシュボードサービス修正 | 1時間 |
| ステップ10: FAQ提案サービス修正 | 2時間 |
| ステップ11: RAGエンジン修正 | 2時間 |
| ステップ12: APIエンドポイント修正 | 2時間 |
| ステップ13: フロントエンド型定義修正 | 1時間 |
| ステップ14: フロントエンドAPIクライアント修正 | 1時間 |
| ステップ15: フロントエンドコンポーネント修正 | 4時間 |
| ステップ16: テストデータスクリプト修正 | 2時間 |
| ステップ17: ドキュメント修正 | 2時間 |
| ステップ18: Docker環境でのテスト | 4時間 |
| ステップ19: ブラウザテスト | 2時間 |
| ステップ20: コミット・プッシュ | 30分 |
| **合計** | **約35時間** |

---

## リスクと対策

### リスク1: データ移行の失敗

**リスク**: 既存FAQデータの移行に失敗する可能性

**対策**:
- データ移行スクリプトを十分にテスト
- データ移行前にデータベースバックアップを作成
- データ移行後にデータ整合性を確認

### リスク2: ベクトル検索の精度低下

**リスク**: 新しい構造でベクトル検索の精度が低下する可能性

**対策**:
- ベクトル検索のテストを十分に実施
- 検索結果の精度を確認
- 必要に応じて閾値や検索ロジックを調整

### リスク3: フロントエンドUIの複雑化

**リスク**: 複数言語対応でフロントエンドUIが複雑になる可能性

**対策**:
- UI設計を十分に検討
- ユーザビリティテストを実施
- 必要に応じてUIを改善

---

## 確認事項チェックリスト

### 修正前
- [ ] バックアップ作成完了
- [ ] 影響範囲の確認完了

### 修正中
- [ ] データベーススキーマ設計完了
- [ ] Alembicマイグレーションファイル作成完了
- [ ] 既存データ移行スクリプト作成完了
- [ ] バックエンド修正完了
- [ ] フロントエンド修正完了
- [ ] テストデータスクリプト修正完了
- [ ] ドキュメント修正完了

### 修正後
- [ ] Docker環境でのテスト完了
- [ ] ブラウザテスト完了
- [ ] データ整合性確認完了
- [ ] FAQ登録数カウント確認完了（言語に関係なく、インテント単位で1件）
- [ ] Gitコミット・プッシュ完了

---

**計画作成完了日時**: 2025年12月21日 10時47分00秒


