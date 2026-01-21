# Phase 2: 統合ヘルプシステム実装計画書

## ドキュメント情報
- **プロジェクト**: YadOPERA（宿泊施設管理システム）
- **フェーズ**: Phase 2 - 統合ヘルプシステム
- **作成日**: 2025年12月26日
- **バージョン**: 1.0
- **基準文書**: 
  - やどぺら v0.3.9 要約定義書
  - やどぺら v0.3.7 アーキテクチャ設計書

---

## 目次

1. [エグゼクティブサマリー](#1-エグゼクティブサマリー)
2. [システム概要](#2-システム概要)
3. [技術スタック](#3-技術スタック)
4. [データベース設計](#4-データベース設計)
5. [API設計](#5-api設計)
6. [フロントエンド設計](#6-フロントエンド設計)
7. [実装ステップ](#7-実装ステップ)
8. [テスト計画](#8-テスト計画)
9. [デプロイ計画](#9-デプロイ計画)
10. [セキュリティ対策](#10-セキュリティ対策)
11. [パフォーマンス最適化](#11-パフォーマンス最適化)
12. [監視・運用](#12-監視運用)
13. [コスト試算](#13-コスト試算)
14. [KPI・効果測定](#14-kpi効果測定)
15. [今後の拡張計画](#15-今後の拡張計画)
16. [付録](#16-付録)

---

## 1. エグゼクティブサマリー

### 1.1 目的

Phase 2では、宿泊施設管理者向けの統合ヘルプシステムを実装します。これにより、PoC期間中のサポート工数を**70%削減**し、管理者の初期操作つまずきによる解約率を低減します。

### 1.2 主要機能

1. **宿泊事業者向けFAQ管理**
   - 20-30項目の初期FAQデータ投入
   - カテゴリ別FAQ表示（初期設定、QRコード、FAQ管理、AI仕組み、ログ分析、トラブルシューティング、料金、セキュリティ）
   - 多言語対応（日本語・英語）

2. **管理画面内AIヘルプチャット**
   - OpenAI GPT-4o-miniを使用したリアルタイム回答
   - システムプロンプトにFAQ全文を埋め込み（pgvector不要）
   - 該当FAQ + 設定画面URLリンク自動返却
   - 管理画面右下にフローティングチャット

### 1.3 期待効果

| 指標 | 目標値 |
|------|--------|
| サポート工数削減 | 70% |
| 解約率低減 | 10%以上 |
| FAQ参照率 | 80%以上 |
| AIチャット利用率 | 50%以上 |

---

## 2. システム概要

### 2.1 システム構成

```
┌─────────────────────────────────────────┐
│     管理画面（Vue.js 3）                  │
│  ┌───────────────────────────────────┐  │
│  │  全ページ共通                      │  │
│  │  └─ HelpButton（右下固定）         │  │
│  │      └─ HelpModal                 │  │
│  │          ├─ FAQタブ               │  │
│  │          │   ├─ カテゴリ選択      │  │
│  │          │   ├─ FAQ検索           │  │
│  │          │   └─ FAQ一覧表示       │  │
│  │          └─ AIチャットタブ        │  │
│  │              ├─ チャット履歴      │  │
│  │              ├─ メッセージ入力    │  │
│  │              └─ 関連FAQ提案       │  │
│  └───────────────────────────────────┘  │
└────────┬────────────────────────────────┘
         │ HTTPS/REST
         ↓
┌─────────────────────────────────────────┐
│     FastAPI Backend                      │
│  ┌───────────────────────────────────┐  │
│  │  /api/v1/help/*                   │  │
│  │  ├─ GET /faqs                     │  │
│  │  ├─ GET /faqs/{category}          │  │
│  │  ├─ GET /search?q={query}         │  │
│  │  └─ POST /chat                    │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Services                         │  │
│  │  ├─ OperatorFaqService            │  │
│  │  └─ OperatorHelpChatService       │  │
│  └───────────────────────────────────┘  │
└────────┬────────────────────────────────┘
         │
         ├────────────────┬───────────────┐
         ↓                ↓               ↓
┌──────────────┐  ┌─────────────┐  ┌──────────────┐
│ PostgreSQL   │  │ OpenAI API  │  │    Redis     │
│ operator_faqs│  │ GPT-4o-mini │  │ (キャッシュ) │
│ operator_faq_│  │             │  │              │
│ translations │  │             │  │              │
└──────────────┘  └─────────────┘  └──────────────┘
```

### 2.2 データフロー

#### FAQ検索フロー

```
管理者がFAQ検索
    ↓
GET /api/v1/help/search?q={query}
    ↓
OperatorFaqService.search_faqs()
    ├─ operator_faq_translationsテーブル全文検索
    ├─ PostgreSQL LIKE検索（question, answer, keywords）
    └─ 関連度順にソート
    ↓
FAQ一覧 + 該当箇所ハイライト返却
```

#### AIチャットフロー

```
管理者が質問入力
    ↓
POST /api/v1/help/chat
    ├─ Request Body:
    │   {
    │     "message": "FAQの登録方法は？",
    │     "language": "ja"
    │   }
    ↓
OperatorHelpChatService.process_message()
    ├─ システムプロンプト構築
    │   ├─ 全FAQ（20-30項目）をMarkdown形式で埋め込み
    │   ├─ 管理画面URLマップ
    │   └─ 回答ガイドライン
    ↓
OpenAI GPT-4o-mini API呼び出し
    ├─ Model: gpt-4o-mini-2024-07-18
    ├─ Max tokens: 500
    ├─ Temperature: 0.7
    └─ System Prompt: FAQ全文 + URLマップ
    ↓
AI回答生成
    ├─ 回答文
    ├─ 関連FAQ ID配列
    └─ 設定画面URL
    ↓
Response:
    {
      "response": "FAQ登録は...",
      "related_faqs": [1, 3, 5],
      "related_url": "/admin/faqs"
    }
```

---

## 3. 技術スタック

### 3.1 Backend

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.11+ | 実行環境 |
| FastAPI | 0.109+ | APIフレームワーク |
| SQLAlchemy | 2.0+ | ORM（async対応） |
| Alembic | 1.13+ | マイグレーション |
| OpenAI SDK | 最新 | AI API連携 |
| python-jose | 3.3+ | JWT認証 |
| Redis | 7.2+ | キャッシュ |

### 3.2 Frontend

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Vue.js | 3.4+ | UIフレームワーク |
| TypeScript | 5.3+ | 型安全 |
| Tailwind CSS | 3.4+ | スタイリング |
| Axios | 1.6+ | HTTP通信 |
| Pinia | 2.1+ | 状態管理 |

### 3.3 AI/API

| サービス | モデル | 用途 |
|---------|--------|------|
| OpenAI | gpt-4o-mini-2024-07-18 | AIチャット回答生成 |

**重要**: pgvectorは**使用しない**（FAQ件数が少ないため、システムプロンプトに全文埋め込みで十分）

---

## 4. データベース設計

### 4.1 テーブル構造

#### operator_faqs（事業者向けFAQ）

```sql
CREATE TABLE operator_faqs (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    intent_key VARCHAR(100) NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(intent_key)
);

CREATE INDEX idx_operator_faqs_category ON operator_faqs(category);
CREATE INDEX idx_operator_faqs_is_active ON operator_faqs(is_active);
CREATE INDEX idx_operator_faqs_display_order ON operator_faqs(display_order);
```

#### operator_faq_translations（FAQ翻訳）

```sql
CREATE TABLE operator_faq_translations (
    id SERIAL PRIMARY KEY,
    faq_id INTEGER NOT NULL REFERENCES operator_faqs(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL DEFAULT 'ja',
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT,
    related_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(faq_id, language)
);

CREATE INDEX idx_operator_faq_translations_faq_id ON operator_faq_translations(faq_id);
CREATE INDEX idx_operator_faq_translations_language ON operator_faq_translations(language);
```

### 4.2 初期FAQデータ（30項目の一部抜粋）

```python
# Category: setup（初期設定） - 5項目
{
    'category': 'setup',
    'intent_key': 'setup_account_creation',
    'display_order': 100,
    'translations': {
        'ja': {
            'question': 'アカウント作成の手順は？',
            'answer': '管理画面トップページから「新規登録」をクリックし、メールアドレス・パスワード・施設情報を入力してください。メール認証後、ログインできます。',
            'keywords': 'アカウント作成,新規登録,サインアップ,初期設定',
            'related_url': '/admin/register'
        },
        'en': {
            'question': 'How to create an account?',
            'answer': 'Click "Sign Up" from the top page, enter your email, password, and facility information. After email verification, you can log in.',
            'keywords': 'account creation,sign up,registration,initial setup',
            'related_url': '/admin/register'
        }
    }
},
# ... 残り29項目（付録Aに全リスト記載）
```

---

## 5. API設計

### 5.1 エンドポイント一覧

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/api/v1/help/faqs` | 全FAQ取得 | 必要 |
| GET | `/api/v1/help/search` | FAQ検索 | 必要 |
| POST | `/api/v1/help/chat` | AIチャット | 必要 |

### 5.2 API詳細

#### GET /api/v1/help/faqs

**Query Parameters**:
- `category` (optional): カテゴリフィルタ
- `language` (optional, default: 'ja'): 言語

**Response**:
```json
{
  "faqs": [
    {
      "id": 1,
      "category": "setup",
      "question": "アカウント作成の手順は？",
      "answer": "管理画面トップページから...",
      "keywords": "アカウント作成,新規登録",
      "related_url": "/admin/register",
      "display_order": 100
    }
  ],
  "total": 30,
  "categories": ["setup", "qrcode", "faq_management", ...]
}
```

#### POST /api/v1/help/chat

**Request**:
```json
{
  "message": "FAQの登録方法を教えてください",
  "language": "ja"
}
```

**Response**:
```json
{
  "response": "FAQ登録は「FAQ管理」→「新規FAQ追加」から行えます...",
  "related_faqs": [
    {
      "id": 10,
      "question": "自分でFAQを追加する方法は？",
      "category": "faq_management"
    }
  ],
  "related_url": "/admin/faqs",
  "timestamp": "2025-12-26T10:30:00Z"
}
```

---

## 6. フロントエンド設計

### 6.1 コンポーネント構成

```
src/components/help/
├── HelpButton.vue          # 右下固定ボタン
├── HelpModal.vue           # モーダル本体
├── FaqList.vue             # FAQ一覧
├── FaqSearchBar.vue        # 検索バー
├── CategoryFilter.vue      # カテゴリフィルタ
└── AiChatPanel.vue         # チャットUI
```

### 6.2 State Management (Pinia)

```typescript
// src/stores/helpStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FAQ, ChatMessage } from '@/types/help'
import api from '@/api/client'

export const useHelpStore = defineStore('help', () => {
  const faqs = ref<FAQ[]>([])
  const isLoading = ref(false)
  
  const fetchFaqs = async (category?: string) => {
    isLoading.value = true
    try {
      const response = await api.get('/help/faqs', {
        params: { category }
      })
      faqs.value = response.data.faqs
    } finally {
      isLoading.value = false
    }
  }
  
  const searchFaqs = async (query: string) => {
    isLoading.value = true
    try {
      const response = await api.get('/help/search', {
        params: { q: query }
      })
      faqs.value = response.data.results
    } finally {
      isLoading.value = false
    }
  }
  
  const sendChatMessage = async (message: string) => {
    const response = await api.post('/help/chat', {
      message,
      language: 'ja'
    })
    return response.data
  }
  
  return {
    faqs,
    isLoading,
    fetchFaqs,
    searchFaqs,
    sendChatMessage
  }
})
```

---

## 7. 実装ステップ

### Step 1: データベースセットアップ（1日）

1. マイグレーションファイル作成
2. 初期FAQデータ投入（30項目）
3. データ確認

### Step 2: Backend API実装（2日）

**Day 1: Service Layer**
- OperatorFaqService
- OperatorHelpChatService

**Day 2: API Endpoints**
- GET /help/faqs
- GET /help/search
- POST /help/chat

### Step 3: Frontend実装（3日）

**Day 1**: HelpButton, HelpModal, Store作成  
**Day 2**: FAQ機能（FaqList, Search, Filter）  
**Day 3**: AIチャット機能（AiChatPanel）

### Step 4: 統合テスト（1日）

- FAQ閲覧・検索テスト
- AIチャット動作テスト
- エラーハンドリング確認

### Step 5: デプロイ（0.5日）

- Staging環境デプロイ
- Production環境デプロイ

---

## 8. テスト計画

### 8.1 単体テスト

```python
# Backend
@pytest.mark.asyncio
async def test_get_faqs(db_session):
    service = OperatorFaqService(db_session)
    faqs = await service.get_faqs(language='ja')
    assert len(faqs) > 0
```

```typescript
// Frontend
it('opens help modal', async () => {
  const wrapper = mount(HelpButton)
  await wrapper.find('button').trigger('click')
  expect(wrapper.findComponent(HelpModal).exists()).toBe(true)
})
```

### 8.2 統合テスト

```typescript
test('should search FAQs and display results', async ({ page }) => {
  await page.goto('/admin/dashboard')
  await page.click('[aria-label="ヘルプ"]')
  await page.fill('[placeholder="FAQを検索..."]', 'アカウント')
  await expect(page.locator('text=アカウント作成')).toBeVisible()
})
```

---

## 9. デプロイ計画

### 9.1 環境構成

- **Staging**: https://staging-admin.yadopera.com
- **Production**: https://admin.yadopera.com

### 9.2 デプロイ手順

1. データベースマイグレーション実行
2. Backend デプロイ（Docker）
3. Frontend デプロイ（S3/CloudFront）
4. 動作確認
5. ヘルスチェック

---

## 10. セキュリティ対策

### 10.1 認証・認可
- JWT認証（アクセストークン7日）
- 全APIエンドポイントで認証必須

### 10.2 入力バリデーション
```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    language: str = Field(default='ja', pattern='^(ja|en)$')
```

### 10.3 レート制限
- AIチャット: 10リクエスト/分
- FAQ検索: 20リクエスト/分

---

## 11. パフォーマンス最適化

### 11.1 データベース最適化
- インデックス活用
- JOIN最適化（N+1問題回避）

### 11.2 Redisキャッシュ
```python
# FAQ一覧キャッシュ（TTL: 5分）
cache_key = f"faqs:{language}:{category or 'all'}"
cached = await redis.get(cache_key)
if cached:
    return json.loads(cached)
```

### 11.3 フロントエンド最適化
- デバウンス処理（検索）
- 遅延ローディング

---

## 12. 監視・運用

### 12.1 ログ管理
```python
logger.info({
    'event': 'help_chat',
    'operator_id': operator_id,
    'message_length': len(message),
    'latency_ms': latency
})
```

### 12.2 メトリクス
- リクエスト数
- レイテンシ（P50, P95, P99）
- エラー率

### 12.3 アラート
- 高レイテンシ（> 5秒）
- OpenAI APIエラー率（> 5%）

---

## 13. コスト試算

### 13.1 OpenAI API コスト

| 月間チャット数 | 月額コスト |
|---------------|-----------|
| 1,000回 | ¥87 |
| 5,000回 | ¥432 |
| 10,000回 | ¥864 |

### 13.2 インフラコスト

| 項目 | 月額 |
|------|------|
| PostgreSQL | $15 |
| Redis | $12 |
| EC2 | $15 |
| **合計** | **$42 (¥6,300)** |

---

## 14. KPI・効果測定

| KPI | 目標値 | 測定方法 |
|-----|-------|---------|
| サポート工数削減率 | 70%以上 | 問い合わせ数（前月比） |
| FAQ参照率 | 80%以上 | モーダル開封率 |
| AIチャット利用率 | 50%以上 | チャットタブクリック率 |
| 平均解決時間 | 2分以内 | ログ分析 |

---

## 15. 今後の拡張計画

### Phase 3 追加機能
1. FAQ自動生成（ログ分析）
2. 多言語FAQ自動翻訳
3. ヘルプ動画チュートリアル
4. AIチャットストリーミングレスポンス

### Phase 4 高度な機能
1. コンテキスト保持型チャット
2. FAQ有効性スコアリング
3. インテリジェントFAQレコメンデーション

---

## 16. 付録

### A. 初期FAQデータ全30項目

#### カテゴリ: setup（5項目）
1. アカウント作成の手順は？
2. 施設情報はどこで登録しますか？
3. 初回ログイン後にまずやるべきことは？
4. スタッフアカウントを追加できますか？
5. パスワードを忘れた場合は？

#### カテゴリ: qrcode（4項目）
6. QRコードはどこに貼るのがベストですか？
7. 複数のQRコードを使い分けられますか？
8. QRコードの印刷サイズの推奨は？
9. QRコードを再発行したい場合は？

#### カテゴリ: faq_management（5項目）
10. FAQテンプレートの使い方は？
11. 自分でFAQを追加する方法は？
12. FAQの優先度とは何ですか？
13. カテゴリはどう分けるべきですか？
14. FAQを一括登録できますか？

#### カテゴリ: ai_logic（4項目）
15. AIはどうやって質問に答えていますか？
16. AIの回答精度を上げるには？
17. 対応言語は何語ですか？
18. AIが答えられない質問はありますか？

#### カテゴリ: logs（3項目）
19. ゲストの質問履歴はどこで見られますか？
20. AIが答えられなかった質問を確認するには？
21. よくある質問のランキングは？

#### カテゴリ: troubleshooting（5項目）
22. AIの応答が遅い場合は？
23. QRコードが読み取れない場合は？
24. FAQを更新したのに反映されない？
25. ログインできない場合は？
26. サポートへの問い合わせ方法は？

#### カテゴリ: billing（3項目）
27. 料金プランは？
28. 解約方法は？
29. 請求書の発行は？

#### カテゴリ: security（3項目）
30. ゲストのデータはどう管理されていますか？
31. スタッフの権限設定は？
32. データのバックアップは？

### B. 環境変数

```bash
# Backend .env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
```

```bash
# Frontend .env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### C. デプロイチェックリスト

#### Pre-deployment
- [ ] 全テスト通過
- [ ] コードレビュー完了
- [ ] マイグレーションファイル作成
- [ ] 環境変数設定確認

#### Deployment
- [ ] DBバックアップ
- [ ] Staging デプロイ
- [ ] Production デプロイ
- [ ] 動作確認

#### Post-deployment
- [ ] ログ監視開始
- [ ] メトリクス監視開始
- [ ] ユーザーフィードバック収集

---

**実装期間**: 7.5日間  
**完成日**: Phase 2完了時  
**次のステップ**: Phase 3（PoC実施）