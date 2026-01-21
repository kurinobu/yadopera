})
</script>
```

### 6.3 State Management (Pinia)

**ファイル**: `src/stores/helpStore.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FAQ, ChatMessage, ChatResponse } from '@/types/help'
import api from '@/api/client'

export const useHelpStore = defineStore('help', () => {
  const faqs = ref<FAQ[]>([])
  const categories = ref<string[]>([])
  const selectedCategory = ref<string | null>(null)
  const searchQuery = ref('')
  const isLoading = ref(false)
  const activeFaqId = ref<number | null>(null)
  
  // FAQ取得
  const fetchFaqs = async (category?: string) => {
    isLoading.value = true
    try {
      const params = category ? { category } : {}
      const response = await api.get('/help/faqs', { params })
      faqs.value = response.data.faqs
      categories.value = response.data.categories
    } catch (error) {
      console.error('Failed to fetch FAQs:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  // FAQ検索
  const searchFaqs = async (query: string) => {
    if (!query.trim()) {
      await fetchFaqs()
      return
    }
    
    isLoading.value = true
    try {
      const response = await api.get('/help/search', {
        params: { q: query }
      })
      faqs.value = response.data.results
    } catch (error) {
      console.error('Failed to search FAQs:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  // AIチャット
  const sendChatMessage = async (message: string): Promise<ChatResponse> => {
    try {
      const response = await api.post('/help/chat', {
        message,
        language: 'ja'
      })
      return response.data
    } catch (error) {
      console.error('Failed to send chat message:', error)
      throw error
    }
  }
  
  // カテゴリフィルタ設定
  const setCategory = (category: string | null) => {
    selectedCategory.value = category
    fetchFaqs(category || undefined)
  }
  
  // 検索クエリ設定
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
    searchFaqs(query)
  }
  
  // アクティブFAQ設定
  const setActiveFaq = (faqId: number) => {
    activeFaqId.value = faqId
  }
  
  return {
    faqs,
    categories,
    selectedCategory,
    searchQuery,
    isLoading,
    activeFaqId,
    fetchFaqs,
    searchFaqs,
    sendChatMessage,
    setCategory,
    setSearchQuery,
    setActiveFaq
  }
})
```

### 6.4 Type Definitions

**ファイル**: `src/types/help.ts`

```typescript
export interface FAQ {
  id: number
  category: string
  question: string
  answer: string
  keywords: string
  related_url: string
  display_order: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  related_faqs?: FAQ[]
  related_url?: string
  timestamp: Date
}

export interface ChatResponse {
  response: string
  related_faqs: FAQ[]
  related_url: string
  timestamp: string
}

export type Category = 
  | 'setup'
  | 'qrcode'
  | 'faq_management'
  | 'ai_logic'
  | 'logs'
  | 'troubleshooting'
  | 'billing'
  | 'security'
```

---

## 7. 実装ステップ

### Step 1: データベースセットアップ（1日）

**担当**: Backend Developer

**タスク**:
1. マイグレーションファイル作成
   - `20251225_create_operator_help_tables.py`
   - `20251225_insert_initial_operator_faqs.py`
2. マイグレーション実行
   ```bash
   cd backend
   alembic upgrade head
   ```
3. データ確認
   ```sql
   SELECT COUNT(*) FROM operator_faqs;  -- 30件
   SELECT COUNT(*) FROM operator_faq_translations;  -- 60件（日英）
   ```

**成果物**:
- マイグレーションファイル × 2
- 初期FAQデータ30項目（日英）

---

### Step 2: Backend API実装（2日）

**担当**: Backend Developer

**Day 1: Service Layer**

1. **OperatorFaqService** (`backend/app/services/operator_faq_service.py`)
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select, and_, or_
   from app.models import OperatorFaq, OperatorFaqTranslation
   
   class OperatorFaqService:
       def __init__(self, db: AsyncSession):
           self.db = db
       
       async def get_faqs(
           self,
           language: str = 'ja',
           category: str | None = None
       ) -> list[dict]:
           """FAQ一覧取得"""
           query = (
               select(OperatorFaq, OperatorFaqTranslation)
               .join(OperatorFaqTranslation)
               .where(
                   and_(
                       OperatorFaq.is_active == True,
                       OperatorFaqTranslation.language == language
                   )
               )
           )
           
           if category:
               query = query.where(OperatorFaq.category == category)
           
           query = query.order_by(OperatorFaq.display_order.desc())
           
           result = await self.db.execute(query)
           rows = result.all()
           
           return [
               {
                   'id': faq.id,
                   'category': faq.category,
                   'question': trans.question,
                   'answer': trans.answer,
                   'keywords': trans.keywords,
                   'related_url': trans.related_url,
                   'display_order': faq.display_order
               }
               for faq, trans in rows
           ]
       
       async def search_faqs(
           self,
           query: str,
           language: str = 'ja'
       ) -> list[dict]:
           """FAQ全文検索"""
           search_pattern = f'%{query}%'
           
           stmt = (
               select(OperatorFaq, OperatorFaqTranslation)
               .join(OperatorFaqTranslation)
               .where(
                   and_(
                       OperatorFaq.is_active == True,
                       OperatorFaqTranslation.language == language,
                       or_(
                           OperatorFaqTranslation.question.ilike(search_pattern),
                           OperatorFaqTranslation.answer.ilike(search_pattern),
                           OperatorFaqTranslation.keywords.ilike(search_pattern)
                       )
                   )
               )
               .order_by(OperatorFaq.display_order.desc())
           )
           
           result = await self.db.execute(stmt)
           rows = result.all()
           
           return [
               {
                   'id': faq.id,
                   'category': faq.category,
                   'question': trans.question,
                   'answer': trans.answer,
                   'related_url': trans.related_url,
                   'relevance_score': self._calculate_relevance(query, trans)
               }
               for faq, trans in rows
           ]
       
       def _calculate_relevance(self, query: str, trans) -> float:
           """関連度スコア計算"""
           score = 0.0
           query_lower = query.lower()
           
           if query_lower in trans.question.lower():
               score += 1.0
           if query_lower in trans.answer.lower():
               score += 0.5
           if trans.keywords and query_lower in trans.keywords.lower():
               score += 0.7
           
           return min(score, 1.0)
   ```

2. **OperatorHelpChatService** (`backend/app/services/operator_help_chat_service.py`)
   ```python
   import openai
   from typing import Dict, List
   from app.services.operator_faq_service import OperatorFaqService
   from app.core.config import settings
   
   class OperatorHelpChatService:
       def __init__(self, faq_service: OperatorFaqService):
           self.faq_service = faq_service
           self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
       
       async def process_message(
           self,
           message: str,
           language: str = 'ja'
       ) -> Dict:
           """AIチャット処理"""
           # 全FAQ取得
           all_faqs = await self.faq_service.get_faqs(language=language)
           
           # システムプロンプト構築
           system_prompt = self._build_system_prompt(all_faqs, language)
           
           # OpenAI API呼び出し
           response = await self.client.chat.completions.create(
               model="gpt-4o-mini-2024-07-18",
               messages=[
                   {"role": "system", "content": system_prompt},
                   {"role": "user", "content": message}
               ],
               max_tokens=500,
               temperature=0.7
           )
           
           ai_response = response.choices[0].message.content
           
           # 関連FAQ抽出
           related_faqs = self._extract_related_faqs(message, all_faqs)
           
           # 関連URL取得
           related_url = self._extract_related_url(ai_response, all_faqs)
           
           return {
               'response': ai_response,
               'related_faqs': related_faqs[:3],  # Top 3
               'related_url': related_url
           }
       
       def _build_system_prompt(self, faqs: List[Dict], language: str) -> str:
           """システムプロンプト構築"""
           faq_text = "\n\n".join([
               f"## {faq['category']}\n"
               f"Q: {faq['question']}\n"
               f"A: {faq['answer']}\n"
               f"URL: {faq['related_url']}"
               for faq in faqs
           ])
           
           if language == 'ja':
               prompt = f"""あなたは「やどぺら」という宿泊施設管理システムのヘルプアシスタントです。
管理者からの質問に、以下のFAQを参考に回答してください。

【FAQデータベース】
{faq_text}

【回答ガイドライン】
1. FAQに該当する内容があれば、それをベースに分かりやすく回答
2. 該当するFAQがない場合は、「申し訳ございません。該当するFAQが見つかりませんでした。サポートチームにお問い合わせください。」と案内
3. 回答には必ず設定画面のURLを含める
4. 簡潔かつ丁寧な日本語で回答"""
           else:
               prompt = f"""You are a help assistant for "YadOPERA", an accommodation management system.
Please answer questions from administrators based on the following FAQs.

【FAQ Database】
{faq_text}

【Response Guidelines】
1. If there's a matching FAQ, provide a clear answer based on it
2. If no matching FAQ exists, say "I'm sorry, I couldn't find a matching FAQ. Please contact our support team."
3. Always include the settings page URL in your response
4. Answer concisely and politely in English"""
           
           return prompt
       
       def _extract_related_faqs(
           self,
           message: str,
           all_faqs: List[Dict]
       ) -> List[Dict]:
           """関連FAQ抽出（簡易的なキーワードマッチング）"""
           message_lower = message.lower()
           scored_faqs = []
           
           for faq in all_faqs:
               score = 0
               keywords = faq.get('keywords', '').lower().split(',')
               
               for keyword in keywords:
                   if keyword.strip() in message_lower:
                       score += 1
               
               if score > 0:
                   scored_faqs.append((score, faq))
           
           scored_faqs.sort(key=lambda x: x[0], reverse=True)
           return [faq for _, faq in scored_faqs[:3]]
       
       def _extract_related_url(
           self,
           ai_response: str,
           all_faqs: List[Dict]
       ) -> str:
           """関連URL抽出"""
           for faq in all_faqs:
               if faq['related_url'] in ai_response:
                   return faq['related_url']
           
           return '/admin/dashboard'  # デフォルト
   ```

**Day 2: API Endpoints**

3. **API Router** (`backend/app/api/v1/endpoints/help.py`)
   ```python
   from fastapi import APIRouter, Depends, Query
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.api.deps import get_db, get_current_operator
   from app.services.operator_faq_service import OperatorFaqService
   from app.services.operator_help_chat_service import OperatorHelpChatService
   from app.schemas.help import (
       FaqListResponse,
       FaqSearchResponse,
       ChatRequest,
       ChatResponse
   )
   
   router = APIRouter(prefix="/help", tags=["operator-help"])
   
   @router.get("/faqs", response_model=FaqListResponse)
   async def get_faqs(
       category: str | None = None,
       language: str = 'ja',
       db: AsyncSession = Depends(get_db),
       current_operator = Depends(get_current_operator)
   ):
       """FAQ一覧取得"""
       faq_service = OperatorFaqService(db)
       faqs = await faq_service.get_faqs(language=language, category=category)
       
       categories = list(set(faq['category'] for faq in faqs))
       
       return {
           'faqs': faqs,
           'total': len(faqs),
           'categories': categories
       }
   
   @router.get("/search", response_model=FaqSearchResponse)
   async def search_faqs(
       q: str = Query(..., min_length=1),
       language: str = 'ja',
       db: AsyncSession = Depends(get_db),
       current_operator = Depends(get_current_operator)
   ):
       """FAQ検索"""
       faq_service = OperatorFaqService(db)
       results = await faq_service.search_faqs(query=q, language=language)
       
       return {
           'results': results,
           'total': len(results),
           'query': q
       }
   
   @router.post("/chat", response_model=ChatResponse)
   async def chat(
       request: ChatRequest,
       db: AsyncSession = Depends(get_db),
       current_operator = Depends(get_current_operator)
   ):
       """AIヘルプチャット"""
       faq_service = OperatorFaqService(db)
       chat_service = OperatorHelpChatService(faq_service)
       
       result = await chat_service.process_message(
           message=request.message,
           language=request.language
       )
       
       return result
   ```

**成果物**:
- Service Layer × 2
- API Endpoints × 3
- Pydantic Schemas

---

### Step 3: Frontend実装（3日）

**担当**: Frontend Developer

**Day 1: コンポーネント基盤**

1. 型定義作成 (`src/types/help.ts`)
2. HelpButton.vue 実装
3. HelpModal.vue 実装
4. Pinia Store (helpStore.ts) 実装

**Day 2: FAQ機能**

5. FaqList.vue 実装
6. FaqSearchBar.vue 実装
7. CategoryFilter.vue 実装
8. FAQ検索・フィルタリング機能

**Day 3: AIチャット機能**

9. AiChatPanel.vue 実装
10. チャット履歴表示
11. メッセージ送信・受信
12. 関連FAQ表示・リンク

**成果物**:
- Vue コンポーネント × 7
- Pinia Store × 1
- 型定義ファイル

---

### Step 4: 統合テスト（1日）

**担当**: Full Team

**テストシナリオ**:

1. **FAQ閲覧テスト**
   - カテゴリフィルタリング
   - FAQ検索
   - 多言語切り替え

2. **AIチャットテスト**
   - 基本的な質問
   - FAQ外の質問
   - 関連FAQ提案
   - 関連URL表示

3. **エラーハンドリングテスト**
   - OpenAI API エラー
   - ネットワークエラー
   - 不正なリクエスト

**成果物**:
- テストレポート
- バグ修正リスト

---

### Step 5: デプロイ（0.5日）

**担当**: DevOps

**タスク**:
1. Staging環境デプロイ
2. 動作確認
3. Production環境デプロイ

**成果物**:
- デプロイ完了レポート

---

## 8. テスト計画

### 8.1 単体テスト

#### Backend (pytest)

**ファイル**: `backend/tests/test_operator_faq_service.py`

```python
import pytest
from app.services.operator_faq_service import OperatorFaqService

@pytest.mark.asyncio
async def test_get_faqs(db_session):
    """FAQ取得テスト"""
    service = OperatorFaqService(db_session)
    faqs = await service.get_faqs(language='ja')
    
    assert len(faqs) > 0
    assert all('question' in faq for faq in faqs)
    assert all('answer' in faq for faq in faqs)

@pytest.mark.asyncio
async def test_search_faqs(db_session):
    """FAQ検索テスト"""
    service = OperatorFaqService(db_session)
    results = await service.search_faqs(query='アカウント', language='ja')
    
    assert len(results) > 0
    assert any('アカウント' in result['question'].lower() for result in results)

@pytest.mark.asyncio
async def test_search_faqs_no_results(db_session):
    """FAQ検索テスト（結果なし）"""
    service = OperatorFaqService(db_session)
    results = await service.search_faqs(query='存在しないキーワード', language='ja')
    
    assert len(results) == 0
```

**ファイル**: `backend/tests/test_operator_help_chat_service.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.operator_help_chat_service import OperatorHelpChatService

@pytest.mark.asyncio
async def test_process_message(faq_service_mock):
    """AIチャット処理テスト"""
    chat_service = OperatorHelpChatService(faq_service_mock)
    
    with patch.object(chat_service.client.chat.completions, 'create', new=AsyncMock()) as mock_create:
        mock_create.return_value.choices = [
            type('obj', (object,), {
                'message': type('obj', (object,), {
                    'content': 'アカウント作成は...'
                })()
            })()
        ]
        
        result = await chat_service.process_message(
            message='アカウント作成の手順は？',
            language='ja'
        )
        
        assert 'response' in result
        assert 'related_faqs' in result
        assert 'related_url' in result
        assert len(result['related_faqs']) <= 3
```

#### Frontend (Vitest)

**ファイル**: `frontend/tests/unit/HelpModal.spec.ts`

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import HelpModal from '@/components/help/HelpModal.vue'

describe('HelpModal.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  
  it('renders FAQ tab by default', () => {
    const wrapper = mount(HelpModal)
    expect(wrapper.find('[data-testid="faq-tab"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('FAQ')
  })
  
  it('switches to chat tab', async () => {
    const wrapper = mount(HelpModal)
    const chatTabButton = wrapper.find('button:nth-child(2)')
    
    await chatTabButton.trigger('click')
    
    expect(wrapper.find('[data-testid="chat-panel"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('AIチャット')
  })
  
  it('emits close event', async () => {
    const wrapper = mount(HelpModal)
    const closeButton = wrapper.find('[aria-label="閉じる"]')
    
    await closeButton.trigger('click')
    
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
```

### 8.2 統合テスト

#### E2E Test (Playwright)

**ファイル**: `frontend/e2e/help-system.spec.ts`

```typescript
import { test, expect } from '@playwright/test'

test.describe('Help System', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/admin/dashboard')
    await page.waitForLoadState('networkidle')
  })
  
  test('should open help modal from button', async ({ page }) => {
    // ヘルプボタンをクリック
    await page.click('[aria-label="ヘルプ"]')
    
    // モーダルが表示される
    await expect(page.locator('text=ヘルプ')).toBeVisible()
    await expect(page.locator('text=FAQ')).toBeVisible()
  })
  
  test('should search FAQs', async ({ page }) => {
    // ヘルプモーダルを開く
    await page.click('[aria-label="ヘルプ"]')
    
    // FAQ検索
    await page.fill('[placeholder="FAQを検索..."]', 'アカウント')
    await page.press('[placeholder="FAQを検索..."]', 'Enter')
    
    // 検索結果が表示される
    await expect(page.locator('text=アカウント作成')).toBeVisible()
  })
  
  test('should send chat message and receive response', async ({ page }) => {
    // ヘルプモーダルを開く
    await page.click('[aria-label="ヘルプ"]')
    
    // AIチャットタブに切り替え
    await page.click('text=AIチャット')
    
    // メッセージ送信
    await page.fill('[placeholder="質問を入力してください..."]', 'FAQの登録方法は？')
    await page.click('button:has-text("送信")')
    
    // AI応答を待つ
    await page.waitForSelector('text=FAQ登録は', { timeout: 10000 })
    
    // 応答が表示される
    await expect(page.locator('text=FAQ管理')).toBeVisible()
  })
})
```

### 8.3 パフォーマンステスト

#### Load Test (Locust)

**ファイル**: `backend/tests/load/locustfile.py`

```python
from locust import HttpUser, task, between

class OperatorHelpUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """ログイン"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_faqs(self):
        """FAQ一覧取得"""
        self.client.get("/api/v1/help/faqs", headers=self.headers)
    
    @task(2)
    def search_faqs(self):
        """FAQ検索"""
        self.client.get(
            "/api/v1/help/search?q=アカウント",
            headers=self.headers
        )
    
    @task(1)
    def chat(self):
        """AIチャット"""
        self.client.post(
            "/api/v1/help/chat",
            json={
                "message": "FAQの登録方法は？",
                "language": "ja"
            },
            headers=self.headers
        )
```

**実行コマンド**:
```bash
locust -f backend/tests/load/locustfile.py --host=http://localhost:8000 --users=50 --spawn-rate=5
```

**目標パフォーマンス**:
- FAQ取得: 平均レスポンス < 100ms
- FAQ検索: 平均レスポンス < 200ms
- AIチャット: 平均レスポンス < 3000ms (OpenAI API含む)
- エラー率: < 1%

---

## 9. デプロイ計画

### 9.1 環境構成

#### Staging環境

- **URL**: https://staging-admin.yadopera.com
- **用途**: QA・統合テスト
- **デプロイトリガー**: `develop` ブランチへのマージ

#### Production環境

- **URL**: https://admin.yadopera.com
- **用途**: 本番サービス
- **デプロイトリガー**: `main` ブランチへのマージ（手動承認）

### 9.2 デプロイ手順

#### Step 1: データベースマイグレーション

```bash
# Staging
alembic upgrade head

# Production（慎重に）
alembic upgrade head
```

#### Step 2: Backend デプロイ

```bash
# Docker イメージビルド
docker build -t yadopera-backend:v0.3.9 ./backend

# コンテナ起動
docker-compose up -d backend
```

#### Step 3: Frontend デプロイ

```bash
# ビルド
cd frontend
npm run build

# S3/CloudFront デプロイ
aws s3 sync dist/ s3://yadopera-frontend/
aws cloudfront create-invalidation --distribution-id XXX --paths "/*"
```

#### Step 4: 動作確認

1. ヘルスチェック
   ```bash
   curl https://api.yadopera.com/health
   ```

2. FAQ取得テスト
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
        https://api.yadopera.com/api/v1/help/faqs
   ```

3. AIチャットテスト（手動）
   - 管理画面ログイン
   - ヘルプボタンクリック
   - AIチャットで質問送信

### 9.3 ロールバック計画

#### 問題発生時の対処

1. **データベース問題**
   ```bash
   alembic downgrade -1
   ```

2. **Backend問題**
   ```bash
   docker-compose down
   docker-compose up -d --scale backend=0
   # 前バージョンのコンテナを起動
   docker run -d yadopera-backend:v0.3.8
   ```

3. **Frontend問題**
   ```bash
   # S3から前バージョンを復元
   aws s3 sync s3://yadopera-frontend-backup/ s3://yadopera-frontend/
   aws cloudfront create-invalidation --distribution-id XXX --paths "/*"
   ```

---

## 10. セキュリティ対策

### 10.1 認証・認可

#### JWT認証

- アクセストークン有効期限: 7日
- リフレッシュトークン有効期限: 30日
- トークン更新エンドポイント: `/api/v1/auth/refresh`

#### APIエンドポイント保護

```python
from fastapi import Depends
from app.api.deps import get_current_operator

@router.get("/help/faqs")
async def get_faqs(
    current_operator = Depends(get_current_operator)  # JWT認証必須
):
    ...
```

### 10.2 入力バリデーション

#### Pydantic Schemas

```python
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    language: str = Field(default='ja', pattern='^(ja|en)# Phase 2: 統合ヘルプシステム実装計画書

## ドキュメント情報
- **プロジェクト**: YadOPERA（宿泊施設管理システム）
- **フェーズ**: Phase 2 - 統合ヘルプシステム
- **作成日**: 2025年12月25日
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
    category VARCHAR(100) NOT NULL,  -- 'setup', 'qrcode', 'faq_management', 'ai_logic', 'logs', 'troubleshooting', 'billing', 'security'
    intent_key VARCHAR(100) NOT NULL,  -- 'setup_account_creation', 'qrcode_placement' など
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
    language VARCHAR(10) NOT NULL DEFAULT 'ja',  -- 'ja', 'en'
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT,  -- 検索用キーワード（カンマ区切り）
    related_url TEXT,  -- 管理画面内リンク（例: '/admin/faqs'）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(faq_id, language)
);

CREATE INDEX idx_operator_faq_translations_faq_id ON operator_faq_translations(faq_id);
CREATE INDEX idx_operator_faq_translations_language ON operator_faq_translations(language);
```

### 4.2 マイグレーション

#### マイグレーション1: テーブル作成

**ファイル**: `backend/alembic/versions/20251225_create_operator_help_tables.py`

```python
"""create operator help tables

Revision ID: xxx
Revises: xxx
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # operator_faqs
    op.create_table(
        'operator_faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('intent_key', sa.String(100), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('intent_key')
    )
    
    op.create_index('idx_operator_faqs_category', 'operator_faqs', ['category'])
    op.create_index('idx_operator_faqs_is_active', 'operator_faqs', ['is_active'])
    op.create_index('idx_operator_faqs_display_order', 'operator_faqs', ['display_order'])
    
    # operator_faq_translations
    op.create_table(
        'operator_faq_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('faq_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(10), nullable=False, server_default='ja'),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('keywords', sa.Text()),
        sa.Column('related_url', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['faq_id'], ['operator_faqs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('faq_id', 'language')
    )
    
    op.create_index('idx_operator_faq_translations_faq_id', 'operator_faq_translations', ['faq_id'])
    op.create_index('idx_operator_faq_translations_language', 'operator_faq_translations', ['language'])

def downgrade():
    op.drop_index('idx_operator_faq_translations_language')
    op.drop_index('idx_operator_faq_translations_faq_id')
    op.drop_table('operator_faq_translations')
    
    op.drop_index('idx_operator_faqs_display_order')
    op.drop_index('idx_operator_faqs_is_active')
    op.drop_index('idx_operator_faqs_category')
    op.drop_table('operator_faqs')
```

#### マイグレーション2: 初期FAQデータ投入

**ファイル**: `backend/alembic/versions/20251225_insert_initial_operator_faqs.py`

```python
"""insert initial operator faqs

Revision ID: xxx
Revises: xxx
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

# 初期FAQデータ（30項目）
INITIAL_FAQS = [
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
    {
        'category': 'setup',
        'intent_key': 'setup_facility_info',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '施設情報はどこで登録しますか？',
                'answer': 'ログイン後、「設定」→「施設設定」から施設名、住所、チェックイン/アウト時間、WiFi情報などを登録できます。',
                'keywords': '施設情報,施設設定,基本情報,WiFi設定',
                'related_url': '/admin/facility'
            },
            'en': {
                'question': 'Where do I register facility information?',
                'answer': 'After login, go to "Settings" → "Facility Settings" to register facility name, address, check-in/out times, WiFi info, etc.',
                'keywords': 'facility information,facility settings,basic info,WiFi settings',
                'related_url': '/admin/facility'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_first_login',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '初回ログイン後にまずやるべきことは？',
                'answer': '以下の順番で設定を行ってください：1. 施設情報登録、2. FAQ初期テンプレート確認・編集、3. QRコード生成・印刷、4. テスト質問で動作確認。',
                'keywords': '初回ログイン,初期設定,はじめに,スタート',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'What should I do after first login?',
                'answer': 'Follow these steps: 1. Register facility info, 2. Review/edit initial FAQ templates, 3. Generate/print QR codes, 4. Test with sample questions.',
                'keywords': 'first login,initial setup,getting started,start',
                'related_url': '/admin/dashboard'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_staff_account',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'スタッフアカウントを追加できますか？',
                'answer': 'はい。「設定」→「スタッフ管理」から、スタッフのメールアドレスと権限レベルを設定してアカウントを追加できます。',
                'keywords': 'スタッフ追加,複数ユーザー,アカウント追加,権限設定',
                'related_url': '/admin/staff'
            },
            'en': {
                'question': 'Can I add staff accounts?',
                'answer': 'Yes. From "Settings" → "Staff Management", you can add staff accounts by setting their email and permission level.',
                'keywords': 'add staff,multiple users,add account,permissions',
                'related_url': '/admin/staff'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_password_reset',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'パスワードを忘れた場合は？',
                'answer': 'ログイン画面の「パスワードを忘れた場合」リンクをクリックし、メールアドレスを入力してください。パスワードリセット用のリンクが送信されます。',
                'keywords': 'パスワード忘れ,パスワードリセット,ログインできない',
                'related_url': '/admin/login'
            },
            'en': {
                'question': 'What if I forget my password?',
                'answer': 'Click "Forgot password?" on the login screen, enter your email, and you will receive a password reset link.',
                'keywords': 'forgot password,password reset,cannot login',
                'related_url': '/admin/login'
            }
        }
    },
    
    # Category: qrcode（QRコード設置） - 4項目
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_placement',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'QRコードはどこに貼るのがベストですか？',
                'answer': 'おすすめの設置場所：1. エントランス（最優先）、2. 各部屋、3. キッチン、4. ラウンジ。設置場所ごとに異なるQRコードを生成できます。',
                'keywords': 'QRコード設置,設置場所,おすすめ場所,配置',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'Where is the best place to put QR codes?',
                'answer': 'Recommended locations: 1. Entrance (highest priority), 2. Each room, 3. Kitchen, 4. Lounge. You can generate different QR codes for each location.',
                'keywords': 'QR code placement,location,recommended spots,positioning',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_multiple',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '複数のQRコードを使い分けられますか？',
                'answer': 'はい。設置場所ごとにQRコードを生成できます。各QRコードは設置場所情報を含むため、どこから質問が来たか追跡できます。',
                'keywords': '複数QRコード,QRコード使い分け,場所別QRコード',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'Can I use multiple QR codes?',
                'answer': 'Yes. You can generate QR codes for each location. Each QR code includes location info, so you can track where questions come from.',
                'keywords': 'multiple QR codes,QR code variation,location-specific codes',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_print_size',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'QRコードの印刷サイズの推奨は？',
                'answer': 'A4用紙1枚に1つのQRコードが推奨です。最小サイズは5cm×5cm、推奨サイズは10cm×10cm以上です。小さすぎるとスマホで読み取りにくくなります。',
                'keywords': 'QRコード印刷,印刷サイズ,推奨サイズ,最小サイズ',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'What is the recommended QR code print size?',
                'answer': 'One QR code per A4 sheet is recommended. Minimum size is 5cm×5cm, recommended size is 10cm×10cm or larger. Too small makes it hard to scan with smartphones.',
                'keywords': 'QR code printing,print size,recommended size,minimum size',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_regenerate',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'QRコードを再発行したい場合は？',
                'answer': '「QRコード管理」から既存のQRコードを削除し、新しいQRコードを生成してください。古いQRコードは自動的に無効化されます。',
                'keywords': 'QRコード再発行,QRコード更新,QRコード削除',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'How do I regenerate a QR code?',
                'answer': 'From "QR Code Management", delete the existing QR code and generate a new one. The old QR code will be automatically invalidated.',
                'keywords': 'regenerate QR code,update QR code,delete QR code',
                'related_url': '/admin/qr-code'
            }
        }
    },
    
    # Category: faq_management（FAQ管理） - 5項目
    {
        'category': 'faq_management',
        'intent_key': 'faq_template_usage',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'FAQテンプレートの使い方は？',
                'answer': 'システムが20-30件の初期テンプレートを提供しています。「FAQ管理」から各テンプレートを確認し、施設に合わせて編集してください。不要なFAQは非アクティブ化できます。',
                'keywords': 'FAQテンプレート,初期FAQ,テンプレート編集',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to use FAQ templates?',
                'answer': 'The system provides 20-30 initial templates. From "FAQ Management", review each template and edit to match your facility. Unwanted FAQs can be deactivated.',
                'keywords': 'FAQ templates,initial FAQs,template editing',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_add_custom',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '自分でFAQを追加する方法は？',
                'answer': '「FAQ管理」→「新規FAQ追加」から、質問・回答・カテゴリ・優先度を入力して保存してください。保存時に埋め込みベクトルが自動生成されます。',
                'keywords': 'FAQ追加,カスタムFAQ,FAQ作成,新規FAQ',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to add custom FAQs?',
                'answer': 'From "FAQ Management" → "Add New FAQ", enter question, answer, category, and priority, then save. Embedding vectors are automatically generated on save.',
                'keywords': 'add FAQ,custom FAQ,create FAQ,new FAQ',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_priority',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'FAQの優先度とは何ですか？',
                'answer': '優先度（1-5）は、AI検索時のランキングに影響します。優先度5が最高で、よくある質問には高い優先度を設定してください。',
                'keywords': 'FAQ優先度,優先順位,ランキング',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'What is FAQ priority?',
                'answer': 'Priority (1-5) affects ranking in AI search. Priority 5 is highest. Set high priority for frequently asked questions.',
                'keywords': 'FAQ priority,ranking,priority level',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_category',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'カテゴリはどう分けるべきですか？',
                'answer': 'カテゴリは4種類：基本情報（チェックイン/WiFi等）、設備（キッチン/シャワー等）、周辺情報（駅/コンビニ等）、トラブル（鍵紛失/故障等）。質問内容に最も近いカテゴリを選んでください。',
                'keywords': 'FAQカテゴリ,カテゴリ分類,カテゴリ選択',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How should I categorize FAQs?',
                'answer': '4 categories: Basic (check-in/WiFi), Facilities (kitchen/shower), Location (station/convenience store), Trouble (lost key/malfunction). Choose the category closest to the question content.',
                'keywords': 'FAQ categories,categorization,category selection',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_bulk_import',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'FAQを一括登録できますか？',
                'answer': '現在は個別登録のみですが、Phase 2でCSV一括インポート機能を追加予定です。大量のFAQがある場合は、サポートチームにご相談ください。',
                'keywords': 'FAQ一括登録,CSV登録,大量登録,インポート',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'Can I bulk import FAQs?',
                'answer': 'Currently only individual registration is supported, but CSV bulk import will be added in Phase 2. For large FAQ volumes, please contact our support team.',
                'keywords': 'bulk import FAQ,CSV import,mass registration,import',
                'related_url': '/admin/faqs'
            }
        }
    },
    
    # Category: ai_logic（AI仕組み） - 4項目
    {
        'category': 'ai_logic',
        'intent_key': 'ai_how_it_works',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'AIはどうやって質問に答えていますか？',
                'answer': 'OpenAI GPT-4o-miniを使用しています。登録されたFAQをシステムプロンプトに埋め込み、ゲストの質問に最適な回答を生成します。',
                'keywords': 'AI仕組み,どうやって,GPT-4o-mini,仕組み',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'How does AI answer questions?',
                'answer': 'We use OpenAI GPT-4o-mini. Registered FAQs are embedded in the system prompt to generate optimal responses to guest questions.',
                'keywords': 'how AI works,mechanism,GPT-4o-mini,how it works',
                'related_url': '/admin/dashboard'
            }
        }
    },
    {
        'category': 'ai_logic',
        'intent_key': 'ai_accuracy',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'AIの回答精度を上げるには？',
                'answer': 'FAQ登録時のポイント：1. 質問文は具体的に、2. 回答は簡潔に、3. キーワードを適切に設定、4. 優先度を調整。FAQが充実するほど精度が向上します。',
                'keywords': 'AI精度,精度向上,回答精度,改善',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to improve AI response accuracy?',
                'answer': 'FAQ registration tips: 1. Make questions specific, 2. Keep answers concise, 3. Set keywords properly, 4. Adjust priority. More FAQs improve accuracy.',
                'keywords': 'AI accuracy,improve accuracy,response quality,improvement',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'ai_logic',
        'intent_key': 'ai_languages',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '対応言語は何語ですか？',
                'answer': '現在は日本語、英語、中国語（簡体字・繁体字）、韓国語の5言語に対応しています。ゲストが選択した言語で自動的に回答します。',
                'keywords': '対応言語,多言語,言語設定,何語',
                'related_url': '/admin/facility'
            },
            'en': {
                'question': 'What languages are supported?',
                'answer': 'Currently supports 5 languages: Japanese, English, Chinese (Simplified/Traditional), and Korean. Responses are automatically provided in the guest\'s selected language.',
                'keywords': 'supported languages,multilingual,language settings,what languages',
                'related_url': '/admin/facility'
            }
        }
    },
    {
        'category': 'ai_logic',
        'intent_key': 'ai_limitations',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'AIが答えられない質問はありますか？',
                'answer': 'はい。FAQに登録されていない内容や、リアルタイム情報（天気、在庫状況等）には答えられません。その場合は「スタッフに確認してください」と案内されます。',
                'keywords': 'AI限界,答えられない,できないこと,制限',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'Are there questions AI cannot answer?',
                'answer': 'Yes. AI cannot answer content not registered in FAQs or real-time information (weather, inventory status, etc.). In such cases, it will suggest "Please check with staff."',
                'keywords': 'AI limitations,cannot answer,what it cannot do,restrictions',
                'related_url': '/admin/dashboard'
            }
        }
    },
    
    # Category: logs（ログ分析） - 3項目
    {
        'category': 'logs',
        'intent_key': 'logs_view_questions',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'ゲストの質問履歴はどこで見られますか？',
                'answer': '「ログ管理」→「質問履歴」から、日付・カテゴリ・キーワードで検索できます。各質問のAI信頼度スコアも確認できます。',
                'keywords': '質問履歴,ログ確認,履歴閲覧,チャットログ',
                'related_url': '/admin/logs'
            },
            'en': {
                'question': 'Where can I view guest question history?',
                'answer': 'From "Log Management" → "Question History", you can search by date, category, and keywords. AI confidence scores for each question are also visible.',
                'keywords': 'question history,view logs,history access,chat logs',
                'related_url': '/admin/logs'
            }
        }
    },
    {
        'category': 'logs',
        'intent_key': 'logs_unanswered',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'AIが答えられなかった質問を確認するには？',
                'answer': '「ログ管理」で信頼度スコア0.5以下の質問をフィルタリングできます。これらの質問は新しいFAQ作成の参考になります。',
                'keywords': '答えられなかった質問,低信頼度,FAQ作成参考',
                'related_url': '/admin/logs'
            },
            'en': {
                'question': 'How to check questions AI couldn\'t answer?',
                'answer': 'In "Log Management", filter questions with confidence score 0.5 or below. These questions can be used as references for creating new FAQs.',
                'keywords': 'unanswered questions,low confidence,FAQ creation reference',
                'related_url': '/admin/logs'
            }
        }
    },
    {
        'category': 'logs',
        'intent_key': 'logs_analytics',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'よくある質問のランキングは？',
                'answer': '「ダッシュボード」で質問カテゴリ別の統計と、よく聞かれる質問TOP10を確認できます。週次・月次で傾向を分析できます。',
                'keywords': 'ランキング,統計,よくある質問,分析',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'Where is the FAQ ranking?',
                'answer': 'On the "Dashboard", you can view statistics by question category and TOP 10 frequently asked questions. Analyze trends weekly/monthly.',
                'keywords': 'ranking,statistics,frequently asked,analysis',
                'related_url': '/admin/dashboard'
            }
        }
    },
    
    # Category: troubleshooting（トラブルシューティング） - 5項目
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_ai_slow',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'AIの応答が遅い場合は？',
                'answer': '通常3-5秒以内に応答します。10秒以上かかる場合は、ネットワーク状況を確認するか、ブラウザをリフレッシュしてください。',
                'keywords': 'AI遅い,応答遅延,遅延,速度',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'What if AI response is slow?',
                'answer': 'Normal response time is 3-5 seconds. If it takes over 10 seconds, check network conditions or refresh the browser.',
                'keywords': 'AI slow,response delay,delay,speed',
                'related_url': '/admin/dashboard'
            }
        }
    },
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_qr_not_working',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'QRコードが読み取れない場合は？',
                'answer': '原因：1. QRコードが小さすぎる（5cm未満）、2. 印刷が不鮮明、3. カメラの焦点が合っていない。対処法：大きめのQRコードを再印刷してください。',
                'keywords': 'QRコード読み取れない,スキャンできない,QRエラー',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'What if QR code doesn\'t scan?',
                'answer': 'Causes: 1. QR code too small (under 5cm), 2. Unclear printing, 3. Camera out of focus. Solution: Reprint a larger QR code.',
                'keywords': 'QR code not scanning,cannot scan,QR error',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_faq_not_updated',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'FAQを更新したのに反映されない？',
                'answer': 'FAQ更新後、システムプロンプトの再構築に最大5分かかります。5分待ってもダメな場合は、ブラウザキャッシュをクリアしてください。',
                'keywords': 'FAQ反映されない,更新されない,変更されない',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'FAQ update not reflected?',
                'answer': 'After FAQ update, system prompt reconstruction takes up to 5 minutes. If still not working after 5 minutes, clear browser cache.',
                'keywords': 'FAQ not reflected,not updated,not changed',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_login_failed',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'ログインできない場合は？',
                'answer': '原因：1. メールアドレス/パスワード間違い、2. アカウント未認証、3. セッション期限切れ。対処法：パスワードリセットを試すか、サポートにお問い合わせください。',
                'keywords': 'ログインできない,ログイン失敗,アクセスできない',
                'related_url': '/admin/login'
            },
            'en': {
                'question': 'Cannot login?',
                'answer': 'Causes: 1. Wrong email/password, 2. Account not verified, 3. Session expired. Solution: Try password reset or contact support.',
                'keywords': 'cannot login,login failed,cannot access',
                'related_url': '/admin/login'
            }
        }
    },
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_contact_support',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'サポートへの問い合わせ方法は？',
                'answer': '画面右下のヘルプボタン→「サポートに連絡」から、問い合わせフォームにアクセスできます。または support@yadopera.com にメールしてください。',
                'keywords': 'サポート,問い合わせ,連絡先,ヘルプ',
                'related_url': '/admin/support'
            },
            'en': {
                'question': 'How to contact support?',
                'answer': 'Click help button at bottom right → "Contact Support" to access inquiry form. Or email support@yadopera.com directly.',
                'keywords': 'support,contact,inquiry,help',
                'related_url': '/admin/support'
            }
        }
    },
    
    # Category: billing（料金） - 3項目
    {
        'category': 'billing',
        'intent_key': 'billing_pricing',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': '料金プランは？',
                'answer': 'PoC期間（3ヶ月）は無料です。その後：ライトプラン ¥3,000/月（FAQ50件まで）、スタンダードプラン ¥8,000/月（FAQ無制限）、エンタープライズ 要相談。',
                'keywords': '料金,プラン,価格,費用',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'What are the pricing plans?',
                'answer': 'PoC period (3 months) is free. After: Light ¥3,000/month (up to 50 FAQs), Standard ¥8,000/month (unlimited FAQs), Enterprise (contact us).',
                'keywords': 'pricing,plans,price,cost',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'category': 'billing',
        'intent_key': 'billing_cancel',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '解約方法は？',
                'answer': '「設定」→「契約情報」→「解約手続き」から、いつでも解約できます。解約月の末日までサービスが利用可能です。',
                'keywords': '解約,キャンセル,退会,辞める',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How to cancel subscription?',
                'answer': 'From "Settings" → "Subscription" → "Cancel", you can cancel anytime. Service remains available until end of cancellation month.',
                'keywords': 'cancel,cancellation,unsubscribe,quit',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'category': 'billing',
        'intent_key': 'billing_invoice',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '請求書の発行は？',
                'answer': '「契約情報」→「請求書履歴」から、過去の請求書をPDFダウンロードできます。領収書の発行も同じ画面から可能です。',
                'keywords': '請求書,領収書,インボイス,ダウンロード',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How to get invoices?',
                'answer': 'From "Subscription" → "Invoice History", you can download past invoices as PDFs. Receipts can also be issued from the same screen.',
                'keywords': 'invoice,receipt,billing,download',
                'related_url': '/admin/billing'
            }
        }
    },
    
    # Category: security（セキュリティ） - 3項目
    {
        'category': 'security',
        'intent_key': 'security_data_privacy',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'ゲストのデータはどう管理されていますか？',
                'answer': '全データはAWS東京リージョンに保存され、SSL/TLS暗号化通信で保護されています。個人情報は7日後に自動削除されます。',
                'keywords': 'データ管理,プライバシー,個人情報,セキュリティ',
                'related_url': '/admin/security'
            },
            'en': {
                'question': 'How is guest data managed?',
                'answer': 'All data is stored in AWS Tokyo region and protected by SSL/TLS encryption. Personal information is automatically deleted after 7 days.',
                'keywords': 'data management,privacy,personal info,security',
                'related_url': '/admin/security'
            }
        }
    },
    {
        'category': 'security',
        'intent_key': 'security_access_control',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'スタッフの権限設定は？',
                'answer': '3つの権限レベル：オーナー（全権限）、マネージャー（FAQ管理・ログ閲覧）、スタッフ（ログ閲覧のみ）。各スタッフに適切な権限を付与してください。',
                'keywords': '権限設定,アクセス制御,スタッフ権限,ロール',
                'related_url': '/admin/staff'
            },
            'en': {
                'question': 'How to set staff permissions?',
                'answer': '3 permission levels: Owner (full access), Manager (FAQ management/log viewing), Staff (log viewing only). Assign appropriate permissions to each staff member.',
                'keywords': 'permissions,access control,staff rights,roles',
                'related_url': '/admin/staff'
            }
        }
    },
    {
        'category': 'security',
        'intent_key': 'security_backup',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'データのバックアップは？',
                'answer': 'データベースは毎日自動バックアップされ、30日間保管されます。万が一のデータ消失時も、前日の状態に復元可能です。',
                'keywords': 'バックアップ,復元,データ保護,復旧',
                'related_url': '/admin/security'
            },
            'en': {
                'question': 'How is data backed up?',
                'answer': 'Database is automatically backed up daily and stored for 30 days. In case of data loss, restoration to previous day\'s state is possible.',
                'keywords': 'backup,restore,data protection,recovery',
                'related_url': '/admin/security'
            }
        }
    }
]

def upgrade():
    conn = op.get_bind()
    
    for faq_data in INITIAL_FAQS:
        # operator_faqs insert
        result = conn.execute(
            sa.text(
                """
                INSERT INTO operator_faqs (category, intent_key, display_order, is_active)
                VALUES (:category, :intent_key, :display_order, true)
                RETURNING id
                """
            ),
            {
                'category': faq_data['category'],
                'intent_key': faq_data['intent_key'],
                'display_order': faq_data['display_order']
            }
        )
        faq_id = result.fetchone()[0]
        
        # operator_faq_translations insert
        for lang, translation in faq_data['translations'].items():
            conn.execute(
                sa.text(
                    """
                    INSERT INTO operator_faq_translations 
                    (faq_id, language, question, answer, keywords, related_url)
                    VALUES (:faq_id, :language, :question, :answer, :keywords, :related_url)
                    """
                ),
                {
                    'faq_id': faq_id,
                    'language': lang,
                    'question': translation['question'],
                    'answer': translation['answer'],
                    'keywords': translation['keywords'],
                    'related_url': translation['related_url']
                }
            )

def downgrade():
    # FAQsの削除（cascadeで翻訳も削除される）
    op.execute("DELETE FROM operator_faqs")
```

---

## 5. API設計

### 5.1 エンドポイント一覧

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/api/v1/help/faqs` | 全FAQ取得（カテゴリフィルタ可） | 必要 |
| GET | `/api/v1/help/faqs/{category}` | カテゴリ別FAQ取得 | 必要 |
| GET | `/api/v1/help/search` | FAQ検索 | 必要 |
| POST | `/api/v1/help/chat` | AIチャット | 必要 |

### 5.2 API詳細仕様

#### GET /api/v1/help/faqs

**説明**: 全FAQ取得（オペレーター向け）

**Query Parameters**:
- `category` (optional): カテゴリフィルタ
- `language` (optional, default: 'ja'): 言語

**Response** (200 OK):
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

#### GET /api/v1/help/search

**説明**: FAQ全文検索

**Query Parameters**:
- `q` (required): 検索クエリ
- `language` (optional, default: 'ja'): 言語

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": 1,
      "question": "アカウント作成の手順は？",
      "answer": "管理画面トップページから...",
      "category": "setup",
      "related_url": "/admin/register",
      "relevance_score": 0.95
    }
  ],
  "total": 5,
  "query": "アカウント作成"
}
```

#### POST /api/v1/help/chat

**説明**: AIヘルプチャット

**Request Body**:
```json
{
  "message": "FAQの登録方法を教えてください",
  "language": "ja"
}
```

**Response** (200 OK):
```json
{
  "response": "FAQ登録は「FAQ管理」→「新規FAQ追加」から行えます。質問・回答・カテゴリ・優先度を入力して保存してください。",
  "related_faqs": [
    {
      "id": 10,
      "question": "自分でFAQを追加する方法は？",
      "category": "faq_management"
    }
  ],
  "related_url": "/admin/faqs",
  "timestamp": "2025-12-25T10:30:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Message is required and must be non-empty"
}
```

---

## 6. フロントエンド設計

### 6.1 コンポーネント構成

```
src/
├── components/
│   └── help/
│       ├── HelpButton.vue          # 右下固定ヘルプボタン
│       ├── HelpModal.vue           # ヘルプモーダル（FAQタブ + チャットタブ）
│       ├── FaqList.vue             # FAQ一覧表示
│       ├── FaqSearchBar.vue        # FAQ検索バー
│       ├── CategoryFilter.vue      # カテゴリフィルタ
│       └── AiChatPanel.vue         # AIチャットパネル
├── stores/
│   └── helpStore.ts                # ヘルプストア（Pinia）
└── types/
    └── help.ts                     # 型定義
```

### 6.2 主要コンポーネント詳細

#### HelpButton.vue

**説明**: 全ページ共通の右下固定ヘルプボタン

```vue
<template>
  <div class="fixed bottom-6 right-6 z-50">
    <button
      @click="openHelpModal"
      class="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all"
      aria-label="ヘルプ"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </button>
    
    <HelpModal v-if="isHelpModalOpen" @close="closeHelpModal" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HelpModal from './HelpModal.vue'

const isHelpModalOpen = ref(false)

const openHelpModal = () => {
  isHelpModalOpen.value = true
}

const closeHelpModal = () => {
  isHelpModalOpen.value = false
}
</script>
```

#### HelpModal.vue

**説明**: FAQタブとAIチャットタブを切り替え可能なモーダル

```vue
<template>
  <teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b">
          <h2 class="text-2xl font-semibold">ヘルプ</h2>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Tabs -->
        <div class="flex border-b">
          <button
            @click="activeTab = 'faq'"
            :class="['flex-1 py-4 text-center font-medium transition-colors',
                     activeTab === 'faq' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-gray-900']"
          >
            FAQ
          </button>
          <button
            @click="activeTab = 'chat'"
            :class="['flex-1 py-4 text-center font-medium transition-colors',
                     activeTab === 'chat' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-gray-900']"
          >
            AIチャット
          </button>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <FaqList v-if="activeTab === 'faq'" />
          <AiChatPanel v-else />
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FaqList from './FaqList.vue'
import AiChatPanel from './AiChatPanel.vue'

defineEmits(['close'])

const activeTab = ref<'faq' | 'chat'>('faq')
</script>
```

#### AiChatPanel.vue

**説明**: AIチャットインターフェース

```vue
<template>
  <div class="flex flex-col h-full">
    <!-- Chat Messages -->
    <div class="flex-1 overflow-y-auto space-y-4 mb-4">
      <div v-for="msg in messages" :key="msg.id" 
           :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
        <div :class="['max-w-[70%] rounded-lg p-4',
                      msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900']">
          <p class="whitespace-pre-wrap">{{ msg.content }}</p>
          
          <!-- Related FAQs -->
          <div v-if="msg.related_faqs && msg.related_faqs.length > 0" class="mt-3 space-y-2">
            <p class="text-sm font-medium">関連FAQ:</p>
            <div v-for="faq in msg.related_faqs" :key="faq.id" 
                 class="text-sm bg-white bg-opacity-20 rounded p-2 cursor-pointer hover:bg-opacity-30"
                 @click="viewFaq(faq.id)">
              {{ faq.question }}
            </div>
          </div>
          
          <!-- Related URL -->
          <div v-if="msg.related_url" class="mt-3">
            <a :href="msg.related_url" 
               class="text-sm underline hover:no-underline"
               target="_blank">
              設定画面を開く →
            </a>
          </div>
        </div>
      </div>
      
      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-start">
        <div class="bg-gray-100 rounded-lg p-4">
          <div class="flex space-x-2">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Input Form -->
    <form @submit.prevent="sendMessage" class="flex gap-2">
      <input
        v-model="inputMessage"
        type="text"
        placeholder="質問を入力してください..."
        class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
        :disabled="isLoading"
      />
      <button
        type="submit"
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="isLoading || !inputMessage.trim()"
      >
        送信
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useHelpStore } from '@/stores/helpStore'
import type { ChatMessage } from '@/types/help'

const helpStore = useHelpStore()
const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const isLoading = ref(false)

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date()
  }
  
  messages.value.push(userMessage)
  const query = inputMessage.value
  inputMessage.value = ''
  isLoading.value = true
  
  try {
    const response = await helpStore.sendChatMessage(query)
    
    messages.value.push({
      id: Date.now().toString(),
      role: 'assistant',
      content: response.response,
      related_faqs: response.related_faqs,
      related_url: response.related_url,
      timestamp: new Date()
    })
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({
      id: Date.now().toString(),
      role: 'assistant',
      content: '申し訳ございません。エラーが発生しました。もう一度お試しください。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
  }
}

const viewFaq = (faqId: number) => {
  // FAQ詳細を表示する処理
  helpStore.setActiveFaq(faqId)
}

onMounted(() => {
  // 初期メッセージ
  messages.value.push({
    id: '0',
    role: 'assistant',
    content: 'こんにちは！やどぺらのヘルプチャットです。ご質問をお気軽にどうぞ。',
    timestamp: new Date()
  })
})
                      )
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
```

### 10.3 レート制限

#### Redis ベースのレート制限

```python
from fastapi_limiter.depends import RateLimiter

@router.post(
    "/help/chat",
    dependencies=[Depends(RateLimiter(times=10, minutes=1))]
)
async def chat(...):
    # 1分あたり10リクエストまで
    ...
```

**設定ファイル**: `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # Rate Limiting
    RATE_LIMIT_CHAT_PER_MINUTE: int = 10
    RATE_LIMIT_FAQ_PER_MINUTE: int = 30
    RATE_LIMIT_SEARCH_PER_MINUTE: int = 20
```

### 10.4 XSS対策

#### フロントエンド

- Vue.jsのデフォルトエスケープを使用
- v-html は使用しない
- ユーザー入力は常にサニタイズ

```typescript
// 安全な表示
<template>
  <p>{{ message.content }}</p>  <!-- 自動エスケープ -->
</template>

// 危険な表示（使用禁止）
<template>
  <p v-html="message.content"></p>  <!-- XSSリスク -->
</template>
```

### 10.5 CSRF対策

#### Backend

```python
from fastapi.middleware.csrf import CSRFMiddleware

app.add_middleware(
    CSRFMiddleware,
    secret_key=settings.SECRET_KEY
)
```

#### Frontend

```typescript
// Axios interceptor
axios.interceptors.request.use((config) => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken
  }
  return config
})
```

### 10.6 OpenAI APIキー保護

#### 環境変数管理

```bash
# .env (Gitにコミットしない)
OPENAI_API_KEY=sk-...

# .env.example (Gitにコミット)
OPENAI_API_KEY=your-openai-api-key-here
```

#### Backend での使用

```python
from app.core.config import settings

client = openai.AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY  # 環境変数から取得
)
```

---

## 11. パフォーマンス最適化

### 11.1 データベース最適化

#### インデックス戦略

```sql
-- 既存インデックス
CREATE INDEX idx_operator_faqs_category ON operator_faqs(category);
CREATE INDEX idx_operator_faqs_is_active ON operator_faqs(is_active);
CREATE INDEX idx_operator_faq_translations_language ON operator_faq_translations(language);

-- 複合インデックス（よく使われるクエリ用）
CREATE INDEX idx_operator_faqs_active_category 
ON operator_faqs(is_active, category) 
WHERE is_active = true;

CREATE INDEX idx_operator_faq_translations_faq_language 
ON operator_faq_translations(faq_id, language);

-- 全文検索用（PostgreSQL）
CREATE INDEX idx_operator_faq_translations_search 
ON operator_faq_translations 
USING gin(to_tsvector('japanese', question || ' ' || answer || ' ' || keywords));
```

#### クエリ最適化

```python
# Before: N+1問題
faqs = await db.execute(select(OperatorFaq))
for faq in faqs:
    translation = await db.execute(
        select(OperatorFaqTranslation).where(
            OperatorFaqTranslation.faq_id == faq.id
        )
    )

# After: JOIN で一度に取得
result = await db.execute(
    select(OperatorFaq, OperatorFaqTranslation)
    .join(OperatorFaqTranslation)
    .where(OperatorFaq.is_active == True)
)
```

### 11.2 キャッシング戦略

#### Redis キャッシュ

**FAQ一覧キャッシュ** (TTL: 5分)

```python
import redis.asyncio as redis
import json

class OperatorFaqService:
    def __init__(self, db: AsyncSession, cache: redis.Redis):
        self.db = db
        self.cache = cache
    
    async def get_faqs(self, language: str = 'ja', category: str | None = None):
        # キャッシュキー生成
        cache_key = f"faqs:{language}:{category or 'all'}"
        
        # キャッシュ確認
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # DB から取得
        faqs = await self._fetch_from_db(language, category)
        
        # キャッシュに保存（5分）
        await self.cache.setex(
            cache_key,
            300,  # 5分
            json.dumps(faqs)
        )
        
        return faqs
```

**システムプロンプトキャッシュ** (TTL: 10分)

```python
class OperatorHelpChatService:
    async def _get_system_prompt(self, language: str) -> str:
        cache_key = f"system_prompt:{language}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached.decode('utf-8')
        
        # FAQ取得してプロンプト構築
        faqs = await self.faq_service.get_faqs(language=language)
        prompt = self._build_system_prompt(faqs, language)
        
        # キャッシュに保存（10分）
        await self.cache.setex(cache_key, 600, prompt)
        
        return prompt
```

### 11.3 OpenAI API最適化

#### トークン数削減

```python
def _build_system_prompt(self, faqs: List[Dict], language: str) -> str:
    """トークン数を削減したシステムプロンプト"""
    # 簡潔なフォーマット
    faq_text = "\n".join([
        f"{i+1}. {faq['question']} → {faq['answer'][:100]}..."  # 回答を100文字に制限
        for i, faq in enumerate(faqs)
    ])
    
    if language == 'ja':
        return f"FAQ:\n{faq_text}\n\n上記FAQを参考に簡潔に回答。"
    else:
        return f"FAQ:\n{faq_text}\n\nAnswer briefly based on FAQs above."
```

#### レスポンスストリーミング（将来対応）

```python
# Phase 3 で実装予定
async def process_message_stream(self, message: str):
    """ストリーミングレスポンス"""
    response = await self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[...],
        stream=True  # ストリーミング有効
    )
    
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### 11.4 フロントエンド最適化

#### 遅延ローディング

```typescript
// Vue Router の lazy loading
const routes = [
  {
    path: '/admin/help',
    component: () => import('@/views/admin/HelpPage.vue')  // 必要時のみロード
  }
]
```

#### デバウンス処理

```typescript
import { debounce } from 'lodash-es'

// FAQ検索のデバウンス（300ms）
const debouncedSearch = debounce(async (query: string) => {
  await helpStore.searchFaqs(query)
}, 300)

const onSearchInput = (event: Event) => {
  const query = (event.target as HTMLInputElement).value
  debouncedSearch(query)
}
```

#### Virtual Scrolling（将来対応）

```vue
<!-- FAQ一覧が100件以上になった場合 -->
<template>
  <RecycleScroller
    :items="faqs"
    :item-size="80"
    key-field="id"
    v-slot="{ item }"
  >
    <FaqItem :faq="item" />
  </RecycleScroller>
</template>
```

---

## 12. 監視・運用

### 12.1 ログ管理

#### Structured Logging

**Backend** (`backend/app/core/logging.py`)

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_help_chat(
        self,
        operator_id: str,
        message: str,
        response: str,
        latency_ms: float,
        related_faqs: list
    ):
        self.logger.info(json.dumps({
            'event': 'help_chat',
            'timestamp': datetime.utcnow().isoformat(),
            'operator_id': operator_id,
            'message_length': len(message),
            'response_length': len(response),
            'latency_ms': latency_ms,
            'related_faq_count': len(related_faqs)
        }))
    
    def log_faq_search(
        self,
        operator_id: str,
        query: str,
        result_count: int,
        latency_ms: float
    ):
        self.logger.info(json.dumps({
            'event': 'faq_search',
            'timestamp': datetime.utcnow().isoformat(),
            'operator_id': operator_id,
            'query': query,
            'result_count': result_count,
            'latency_ms': latency_ms
        }))
```

#### ログ使用例

```python
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)

@router.post("/chat")
async def chat(request: ChatRequest, current_operator = Depends(...)):
    start_time = time.time()
    
    result = await chat_service.process_message(request.message)
    
    latency_ms = (time.time() - start_time) * 1000
    
    logger.log_help_chat(
        operator_id=current_operator.id,
        message=request.message,
        response=result['response'],
        latency_ms=latency_ms,
        related_faqs=result['related_faqs']
    )
    
    return result
```

### 12.2 メトリクス収集

#### Prometheus メトリクス

**設定** (`backend/app/core/metrics.py`)

```python
from prometheus_client import Counter, Histogram, Gauge

# カウンター
help_chat_requests = Counter(
    'help_chat_requests_total',
    'Total help chat requests',
    ['operator_id', 'language']
)

faq_search_requests = Counter(
    'faq_search_requests_total',
    'Total FAQ search requests',
    ['language']
)

# ヒストグラム（レイテンシ）
help_chat_latency = Histogram(
    'help_chat_latency_seconds',
    'Help chat response latency',
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

openai_api_latency = Histogram(
    'openai_api_latency_seconds',
    'OpenAI API response latency',
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

# ゲージ（現在値）
active_help_sessions = Gauge(
    'active_help_sessions',
    'Number of active help sessions'
)
```

#### メトリクス記録

```python
@router.post("/chat")
async def chat(request: ChatRequest, current_operator = Depends(...)):
    help_chat_requests.labels(
        operator_id=current_operator.id,
        language=request.language
    ).inc()
    
    with help_chat_latency.time():
        result = await chat_service.process_message(request.message)
    
    return result
```

### 12.3 アラート設定

#### Grafana アラート

**高レイテンシアラート**

```yaml
# grafana/alerts/help_chat_latency.yml
alert: HighHelpChatLatency
expr: histogram_quantile(0.95, help_chat_latency_seconds) > 5
for: 5m
labels:
  severity: warning
annotations:
  summary: "Help chat latency is high"
  description: "95th percentile latency is {{ $value }}s (threshold: 5s)"
```

**OpenAI APIエラーアラート**

```yaml
# grafana/alerts/openai_errors.yml
alert: HighOpenAIErrorRate
expr: rate(openai_api_errors_total[5m]) > 0.05
for: 5m
labels:
  severity: critical
annotations:
  summary: "High OpenAI API error rate"
  description: "Error rate is {{ $value }} (threshold: 5%)"
```

### 12.4 ダッシュボード

#### Grafana ダッシュボード構成

**パネル1: リクエスト数**
- FAQ取得リクエスト数（時系列）
- FAQ検索リクエスト数（時系列）
- AIチャットリクエスト数（時系列）

**パネル2: レイテンシ**
- FAQ取得レイテンシ（P50, P95, P99）
- FAQ検索レイテンシ（P50, P95, P99）
- AIチャットレイテンシ（P50, P95, P99）
- OpenAI APIレイテンシ（P50, P95, P99）

**パネル3: エラー率**
- 全体エラー率
- OpenAI APIエラー率
- データベースエラー率

**パネル4: ビジネスメトリクス**
- アクティブヘルプセッション数
- FAQカテゴリ別利用率
- AIチャット利用率
- 関連FAQ提案のクリック率

---

## 13. コスト試算

### 13.1 OpenAI API コスト

#### 前提条件

- **モデル**: GPT-4o-mini
- **入力トークン**: $0.150 / 1M tokens
- **出力トークン**: $0.600 / 1M tokens
- **平均システムプロンプトトークン**: 3,000 tokens（FAQ 30件）
- **平均ユーザーメッセージトークン**: 50 tokens
- **平均AI応答トークン**: 200 tokens

#### 月間コスト試算

| 項目 | 値 | 計算 |
|------|-----|------|
| 想定月間チャット数 | 1,000回 | PoC期間中の施設数×利用率 |
| 入力トークン/回 | 3,050 tokens | システムプロンプト + ユーザーメッセージ |
| 出力トークン/回 | 200 tokens | AI応答 |
| 月間入力トークン | 3,050,000 tokens | 3,050 × 1,000 |
| 月間出力トークン | 200,000 tokens | 200 × 1,000 |
| 入力コスト | $0.46 | 3.05M × $0.150 |
| 出力コスト | $0.12 | 0.2M × $0.600 |
| **月間合計** | **$0.58** | **約¥87（$1=¥150換算）** |

#### スケーリング試算

| 月間チャット数 | 月間コスト（$） | 月間コスト（¥） |
|---------------|----------------|----------------|
| 1,000回 | $0.58 | ¥87 |
| 5,000回 | $2.88 | ¥432 |
| 10,000回 | $5.76 | ¥864 |
| 50,000回 | $28.80 | ¥4,320 |

**結論**: OpenAI APIコストは非常に低く、スケールしても月額数千円程度。

### 13.2 インフラコスト

| 項目 | スペック | 月額コスト |
|------|---------|-----------|
| PostgreSQL RDS | db.t3.micro | $15 |
| Redis ElastiCache | cache.t3.micro | $12 |
| EC2 (Backend) | t3.small | $15 |
| S3 (Frontend) | 5GB | $0.12 |
| CloudFront | 10GB転送 | $1.00 |
| **合計** | - | **$43.12 (約¥6,468)** |

### 13.3 総コスト

| 項目 | 月額コスト（¥） |
|------|----------------|
| インフラ | ¥6,468 |
| OpenAI API（10,000回/月） | ¥864 |
| **合計** | **¥7,332** |

**ユーザー単価**: ¥7,332 ÷ 10施設 = **¥733/施設/月**

---

## 14. KPI・効果測定

### 14.1 主要KPI

| KPI | 目標値 | 測定方法 |
|-----|-------|---------|
| **サポート工数削減率** | 70%以上 | サポート問い合わせ数（前月比） |
| **FAQ参照率** | 80%以上 | ヘルプモーダル開封率 |
| **AIチャット利用率** | 50%以上 | チャットタブクリック率 |
| **AI回答満足度** | 4.0以上（5段階） | チャット後のフィードバック |
| **平均解決時間** | 2分以内 | ログタイムスタンプ分析 |
| **解約率低減** | 10%以上改善 | 月次解約率比較 |

### 14.2 測定ダッシュボード

#### 週次レポート

```sql
-- ヘルプ利用状況（週次）
SELECT 
    DATE_TRUNC('week', created_at) as week,
    COUNT(DISTINCT operator_id) as unique_operators,
    COUNT(*) as total_help_opens,
    SUM(CASE WHEN action = 'chat_used' THEN 1 ELSE 0 END) as chat_usages,
    SUM(CASE WHEN action = 'faq_viewed' THEN 1 ELSE 0 END) as faq_views,
    AVG(session_duration_seconds) as avg_session_duration
FROM help_usage_logs
WHERE created_at >= NOW() - INTERVAL '4 weeks'
GROUP BY week
ORDER BY week DESC;
```

#### 月次レポート

```sql
-- AIチャット効果測定（月次）
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_chats,
    AVG(response_length) as avg_response_length,
    AVG(ARRAY_LENGTH(related_faqs, 1)) as avg_related_faqs,
    COUNT(CASE WHEN feedback_rating >= 4 THEN 1 END)::float / COUNT(*) as satisfaction_rate
FROM help_chat_logs
WHERE created_at >= NOW() - INTERVAL '6 months'
GROUP BY month
ORDER BY month DESC;
```

### 14.3 A/Bテスト（Phase 3）

#### テストシナリオ

**テストA**: FAQ検索結果の表示順序
- パターン1: 関連度順
- パターン2: カテゴリ別グループ化

**テストB**: AIチャット初期メッセージ
- パターン1: 「ご質問をお気軽にどうぞ」
- パターン2: 「よくある質問: アカウント作成、QRコード設置...」

**測定指標**:
- クリック率
- 平均セッション時間
- 問題解決率

---

## 15. 今後の拡張計画

### 15.1 Phase 3 追加機能

#### 1. FAQ自動生成機能

**概要**: ログ分析から新しいFAQを自動提案

```python
class FaqAutoGenerator:
    async def analyze_unanswered_questions(self):
        """未回答質問を分析"""
        # 信頼度0.5以下の質問を集計
        low_confidence_questions = await self.get_low_confidence_logs()
        
        # 類似質問をクラスタリング
        clusters = self.cluster_similar_questions(low_confidence_questions)
        
        # クラスタごとにFAQ案を生成
        faq_suggestions = []
        for cluster in clusters:
            suggestion = await self.generate_faq_from_cluster(cluster)
            faq_suggestions.append(suggestion)
        
        return faq_suggestions
```

#### 2. 多言語FAQ自動翻訳

**概要**: 日本語FAQを英語・中国語・韓国語に自動翻訳

```python
class FaqTranslationService:
    async def auto_translate_faq(self, faq_id: int, target_languages: list):
        """FAQ自動翻訳"""
        # 日本語FAQ取得
        ja_faq = await self.get_faq(faq_id, language='ja')
        
        translations = {}
        for lang in target_languages:
            # GPT-4o-miniで翻訳
            translated = await self.translate_with_gpt(ja_faq, target_lang=lang)
            translations[lang] = translated
        
        return translations
```

#### 3. ヘルプ動画チュートリアル

**概要**: FAQ項目に動画説明を追加

- 動画ホスティング: YouTube or Vimeo
- 動画埋め込み: FAQ回答に動画リンク追加
- 視聴分析: 動画再生回数・完視率トラッキング

#### 4. AIチャットストリーミングレスポンス

**概要**: リアルタイムでAI回答を表示

```python
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """ストリーミングレスポンス"""
    async def generate():
        async for chunk in chat_service.process_message_stream(request.message):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 15.2 Phase 4 高度な機能

#### 1. コンテキスト保持型チャット

**概要**: 過去の会話を考慮した応答

```python
class ContextAwareChatService:
    async def process_with_context(
        self,
        message: str,
        session_id: str
    ):
        # セッション履歴取得
        history = await self.get_chat_history(session_id)
        
        # コンテキスト付きプロンプト構築
        messages = [
            {"role": "system", "content": system_prompt},
            *[{"role": msg.role, "content": msg.content} for msg in history],
            {"role": "user", "content": message}
        ]
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        return response
```

#### 2. FAQ有効性スコアリング

**概要**: FAQの有効性を自動評価

```python
class FaqEffectivenessAnalyzer:
    def calculate_effectiveness_score(self, faq_id: int) -> float:
        """FAQ有効性スコア計算"""
        # 参照回数
        view_count = self.get_view_count(faq_id)
        
        # 問題解決率
        resolution_rate = self.get_resolution_rate(faq_id)
        
        # フィードバック評価
        feedback_score = self.get_avg_feedback(faq_id)
        
        # 総合スコア
        score = (
            view_count * 0.3 +
            resolution_rate * 0.5 +
            feedback_score * 0.2
        )
        
        return score
```

#### 3. インテリジェントFAQレコメンデーション

**概要**: 管理者の行動に基づいたFAQ提案

```python
class FaqRecommender:
    async def recommend_faqs(self, operator_id: str) -> list:
        """パーソナライズドFAQ推薦"""
        # 管理者の行動履歴取得
        behavior = await self.get_operator_behavior(operator_id)
        
        # 類似管理者の参照FAQ取得
        similar_operators = self.find_similar_operators(operator_id)
        popular_faqs = self.get_popular_faqs_among(similar_operators)
        
        # 未読FAQをフィルタリング
        unread_faqs = self.filter_unread(operator_id, popular_faqs)
        
        return unread_faqs[:5]
```

---

## 16. まとめ

### 16.1 実装タイムライン

| フェーズ | 期間 | タスク |
|---------|------|--------|
| **Step 1** | 1日 | データベースセットアップ |
| **Step 2** | 2日 | Backend API実装 |
| **Step 3** | 3日 | Frontend実装 |
| **Step 4** | 1日 | 統合テスト |
| **Step 5** | 0.5日 | デプロイ |
| **合計** | **7.5日** | **Phase 2 完了** |

### 16.2 リスクと対策

| リスク | 影響度 | 発生確率 | 対策 |
|-------|-------|---------|------|
| OpenAI API障害 | 高 | 低 | フォールバックメッセージ表示 |
| FAQ件数増加によるトークン超過 | 中 | 中 | FAQ要約・優先度フィルタリング |
| レスポンス遅延 | 中 | 中 | Redis キャッシング強化 |
| 多言語翻訳品質 | 低 | 低 | 人手によるレビュー |

### 16.3 成功基準

Phase 2は以下の条件を満たした場合、成功とみなす：

1. **機能要件**
   - ✅ FAQ一覧・検索機能が正常動作
   - ✅ AIチャットが3秒以内に応答
   - ✅ 関連FAQ提案が適切
   - ✅ 多言語対応（日英）

2. **パフォーマンス**
   - ✅ FAQ取得 < 100ms
   - ✅ FAQ検索 < 200ms
   - ✅ AIチャット < 3000ms
   - ✅ エラー率 < 1%

3. **ビジネス指標**
   - ✅ サポート工数削減 70%以上
   - ✅ FAQ参照率 80%以上
   - ✅ AIチャット利用率 50%以上
   - ✅ 解約率低減 10%以上

### 16.4 次のステップ

Phase 2完了後、以下を実施：

1. **効果測定**（2週間）
   - KPI収集・分析
   - ユーザーフィードバック収集
   - 改善点洗い出し

2. **Phase 3 計画**（1週間）
   - FAQ自動生成機能設計
   - 多言語自動翻訳設計
   - ヘルプ動画チュートリアル設計

3. **Phase 3 実装**（2-3週間）
   - 高度な機能追加
   - UX改善
   - パフォーマンス最適化

---

## 付録

### A. 環境変数一覧

#### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/yadopera
POSTGRES_USER=yadopera
POSTGRES_PASSWORD=your_password
POSTGRES_DB=yadopera

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_DB=1

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini-2024-07-18
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Rate Limiting
RATE_LIMIT_CHAT_PER_MINUTE=10
RATE_LIMIT_FAQ_PER_MINUTE=30
RATE_LIMIT_SEARCH_PER_MINUTE=20

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

#### Frontend (.env)

```bash
# API
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000

# Feature Flags
VITE_FEATURE_HELP_CHAT=true
VITE_FEATURE_FAQ_SEARCH=true

# Environment
VITE_ENVIRONMENT=development
```

### B. API仕様書（OpenAPI）

```yaml
openapi: 3.0.0
info:
  title: YadOPERA Operator Help API
  version: 1.0.0
  description: 宿泊事業者向けヘルプシステムAPI

servers:
  - url: https://api.yadopera.com/api/v1
    description: Production
  - url: https://staging-api.yadopera.com/api/v1
    description: Staging

paths:
  /help/faqs:
    get:
      summary: FAQ一覧取得
      tags:
        - Help
      security:
        - BearerAuth: []
      parameters:
        - name: category
          in: query
          schema:
            type: string
            enum: [setup, qrcode, faq_management, ai_logic, logs, troubleshooting, billing, security]
        - name: language
          in: query
          schema:
            type: string
            default: ja
            enum: [ja, en]
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  faqs:
                    type: array
                    items:
                      $ref: '#/components/schemas/FAQ'
                  total:
                    type: integer
                  categories:
                    type: array
                    items:
                      type: string
        '401':
          description: 未認証

  /help/search:
    get:
      summary: FAQ検索
      tags:
        - Help
      security:
        - BearerAuth: []
      parameters:
        - name: q
          in: query
          required: true
          schema:
            type: string
            minLength: 1
        - name: language
          in: query
          schema:
            type: string
            default: ja
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      $ref: '#/components/schemas/FAQSearchResult'
                  total:
                    type: integer
                  query:
                    type: string

  /help/chat:
    post:
      summary: AIヘルプチャット
      tags:
        - Help
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  minLength: 1
                  maxLength: 500
                language:
                  type: string
                  default: ja
                  enum: [ja, en]
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
        '400':
          description: 不正なリクエスト
        '429':
          description: レート制限超過

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    FAQ:
      type: object
      properties:
        id:
          type: integer
        category:
          type: string
        question:
          type: string
        answer:
          type: string
        keywords:
          type: string
        related_url:
          type: string
        display_order:
          type: integer

    FAQSearchResult:
      allOf:
        - $ref: '#/components/schemas/FAQ'
        - type: object
          properties:
            relevance_score:
              type: number
              format: float
              minimum: 0
              maximum: 1

    ChatResponse:
      type: object
      properties:
        response:
          type: string
        related_faqs:
          type: array
          items:
            $ref: '#/components/schemas/FAQ'
        related_url:
          type: string
        timestamp:
          type: string
          format: date-time
```

### C. データベーススキーマ図

```
┌─────────────────────────────────────┐
│        operator_faqs                │
├─────────────────────────────────────┤
│ PK  id              SERIAL          │
│     category        VARCHAR(100)    │
│     intent_key      VARCHAR(100)    │ UNIQUE
│     display_order   INTEGER         │
│     is_active       BOOLEAN         │
│     created_at      TIMESTAMP       │
│     updated_at      TIMESTAMP       │
└─────────────────┬───────────────────┘
                  │
                  │ 1:N
                  │
┌─────────────────▼───────────────────┐
│   operator_faq_translations         │
├─────────────────────────────────────┤
│ PK  id              SERIAL          │
│ FK  faq_id          INTEGER         │ → operator_faqs(id)
│     language        VARCHAR(10)     │
│     question        TEXT            │
│     answer          TEXT            │
│     keywords        TEXT            │
│     related_url     TEXT            │
│     created_at      TIMESTAMP       │
│     updated_at      TIMESTAMP       │
│                                     │
│ UNIQUE(faq_id, language)            │
└─────────────────────────────────────┘

Indexes:
- idx_operator_faqs_category (category)
- idx_operator_faqs_is_active (is_active)
- idx_operator_faqs_display_order (display_order)
- idx_operator_faq_translations_faq_id (faq_id)
- idx_operator_faq_translations_language (language)
```

### D. フロントエンド ディレクトリ構造

```
frontend/
├── src/
│   ├── components/
│   │   └── help/
│   │       ├── HelpButton.vue
│   │       ├── HelpModal.vue
│   │       ├── FaqList.vue
│   │       ├── FaqSearchBar.vue
│   │       ├── CategoryFilter.vue
│   │       ├── AiChatPanel.vue
│   │       └── __tests__/
│   │           ├── HelpButton.spec.ts
│   │           ├── HelpModal.spec.ts
│   │           └── AiChatPanel.spec.ts
│   ├── stores/
│   │   ├── helpStore.ts
│   │   └── __tests__/
│   │       └── helpStore.spec.ts
│   ├── types/
│   │   └── help.ts
│   ├── api/
│   │   └── help.ts
│   └── App.vue
├── public/
├── tests/
│   └── e2e/
│       └── help-system.spec.ts
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### E. Backend ディレクトリ構造

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── help.py
│   ├── services/
│   │   ├── operator_faq_service.py
│   │   └── operator_help_chat_service.py
│   ├── models/
│   │   ├── operator_faq.py
│   │   └── operator_faq_translation.py
│   ├── schemas/
│   │   └── help.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── metrics.py
│   └── main.py
├── alembic/
│   └── versions/
│       ├── 20251225_create_operator_help_tables.py
│       └── 20251225_insert_initial_operator_faqs.py
├── tests/
│   ├── unit/
│   │   ├── test_operator_faq_service.py
│   │   └── test_operator_help_chat_service.py
│   ├── integration/
│   │   └── test_help_api.py
│   └── load/
│       └── locustfile.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### F. デプロイチェックリスト

#### Pre-deployment

- [ ] すべての単体テストが通過
- [ ] すべての統合テストが通過
- [ ] E2Eテストが通過
- [ ] セキュリティスキャン完了（Bandit, npm audit）
- [ ] コードレビュー完了
- [ ] マイグレーションファイル作成完了
- [ ] 環境変数設定確認（.env.production）
- [ ] OpenAI APIキー確認
- [ ] Redisキャッシュクリア

#### Deployment

- [ ] データベースバックアップ実施
- [ ] Staging環境デプロイ
- [ ] Staging環境動作確認
- [ ] マイグレーション実行（Staging）
- [ ] 初期FAQデータ投入確認
- [ ] Production環境デプロイ承認
- [ ] Production環境デプロイ
- [ ] マイグレーション実行（Production）
- [ ] ヘルスチェック確認
- [ ] 動作確認（手動テスト）

#### Post-deployment

- [ ] ログ監視開始
- [ ] メトリクス監視開始
- [ ] エラーアラート確認
- [ ] パフォーマンス測定
- [ ] ユーザーフィードバック収集開始
- [ ] デプロイ完了報告
- [ ] ロールバック手順確認

---

## 完成

この実装計画書に従って、Phase 2の統合ヘルプシステムを7.5日間で実装できます。

**重要ポイント**:

1. **pgvectorは不要**: FAQ件数が30件程度なので、システムプロンプトに全文埋め込みで十分
2. **コストは非常に低い**: OpenAI API月額約¥1,000以下
3. **段階的な拡張**: Phase 3, 4で高度な機能を追加
4. **効果測定重視**: KPIダッシュボードで常に効果を可視化

---

**ドキュメント作成日**: 2025年12月25日  
**最終更新日**: 2025年12月25日  
**バージョン**: 1.0  
**作成者**: YadOPERA開発チーム# Phase 2: 統合ヘルプシステム実装計画書

## ドキュメント情報
- **プロジェクト**: YadOPERA（宿泊施設管理システム）
- **フェーズ**: Phase 2 - 統合ヘルプシステム
- **作成日**: 2025年12月25日
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
    category VARCHAR(100) NOT NULL,  -- 'setup', 'qrcode', 'faq_management', 'ai_logic', 'logs', 'troubleshooting', 'billing', 'security'
    intent_key VARCHAR(100) NOT NULL,  -- 'setup_account_creation', 'qrcode_placement' など
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
    language VARCHAR(10) NOT NULL DEFAULT 'ja',  -- 'ja', 'en'
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT,  -- 検索用キーワード（カンマ区切り）
    related_url TEXT,  -- 管理画面内リンク（例: '/admin/faqs'）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(faq_id, language)
);

CREATE INDEX idx_operator_faq_translations_faq_id ON operator_faq_translations(faq_id);
CREATE INDEX idx_operator_faq_translations_language ON operator_faq_translations(language);
```

### 4.2 マイグレーション

#### マイグレーション1: テーブル作成

**ファイル**: `backend/alembic/versions/20251225_create_operator_help_tables.py`

```python
"""create operator help tables

Revision ID: xxx
Revises: xxx
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # operator_faqs
    op.create_table(
        'operator_faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('intent_key', sa.String(100), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('intent_key')
    )
    
    op.create_index('idx_operator_faqs_category', 'operator_faqs', ['category'])
    op.create_index('idx_operator_faqs_is_active', 'operator_faqs', ['is_active'])
    op.create_index('idx_operator_faqs_display_order', 'operator_faqs', ['display_order'])
    
    # operator_faq_translations
    op.create_table(
        'operator_faq_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('faq_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(10), nullable=False, server_default='ja'),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('keywords', sa.Text()),
        sa.Column('related_url', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['faq_id'], ['operator_faqs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('faq_id', 'language')
    )
    
    op.create_index('idx_operator_faq_translations_faq_id', 'operator_faq_translations', ['faq_id'])
    op.create_index('idx_operator_faq_translations_language', 'operator_faq_translations', ['language'])

def downgrade():
    op.drop_index('idx_operator_faq_translations_language')
    op.drop_index('idx_operator_faq_translations_faq_id')
    op.drop_table('operator_faq_translations')
    
    op.drop_index('idx_operator_faqs_display_order')
    op.drop_index('idx_operator_faqs_is_active')
    op.drop_index('idx_operator_faqs_category')
    op.drop_table('operator_faqs')
```

#### マイグレーション2: 初期FAQデータ投入

**ファイル**: `backend/alembic/versions/20251225_insert_initial_operator_faqs.py`

```python
"""insert initial operator faqs

Revision ID: xxx
Revises: xxx
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

# 初期FAQデータ（30項目）
INITIAL_FAQS = [
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
    {
        'category': 'setup',
        'intent_key': 'setup_facility_info',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '施設情報はどこで登録しますか？',
                'answer': 'ログイン後、「設定」→「施設設定」から施設名、住所、チェックイン/アウト時間、WiFi情報などを登録できます。',
                'keywords': '施設情報,施設設定,基本情報,WiFi設定',
                'related_url': '/admin/facility'
            },
            'en': {
                'question': 'Where do I register facility information?',
                'answer': 'After login, go to "Settings" → "Facility Settings" to register facility name, address, check-in/out times, WiFi info, etc.',
                'keywords': 'facility information,facility settings,basic info,WiFi settings',
                'related_url': '/admin/facility'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_first_login',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '初回ログイン後にまずやるべきことは？',
                'answer': '以下の順番で設定を行ってください：1. 施設情報登録、2. FAQ初期テンプレート確認・編集、3. QRコード生成・印刷、4. テスト質問で動作確認。',
                'keywords': '初回ログイン,初期設定,はじめに,スタート',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'What should I do after first login?',
                'answer': 'Follow these steps: 1. Register facility info, 2. Review/edit initial FAQ templates, 3. Generate/print QR codes, 4. Test with sample questions.',
                'keywords': 'first login,initial setup,getting started,start',
                'related_url': '/admin/dashboard'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_staff_account',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'スタッフアカウントを追加できますか？',
                'answer': 'はい。「設定」→「スタッフ管理」から、スタッフのメールアドレスと権限レベルを設定してアカウントを追加できます。',
                'keywords': 'スタッフ追加,複数ユーザー,アカウント追加,権限設定',
                'related_url': '/admin/staff'
            },
            'en': {
                'question': 'Can I add staff accounts?',
                'answer': 'Yes. From "Settings" → "Staff Management", you can add staff accounts by setting their email and permission level.',
                'keywords': 'add staff,multiple users,add account,permissions',
                'related_url': '/admin/staff'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_password_reset',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'パスワードを忘れた場合は？',
                'answer': 'ログイン画面の「パスワードを忘れた場合」リンクをクリックし、メールアドレスを入力してください。パスワードリセット用のリンクが送信されます。',
                'keywords': 'パスワード忘れ,パスワードリセット,ログインできない',
                'related_url': '/admin/login'
            },
            'en': {
                'question': 'What if I forget my password?',
                'answer': 'Click "Forgot password?" on the login screen, enter your email, and you will receive a password reset link.',
                'keywords': 'forgot password,password reset,cannot login',
                'related_url': '/admin/login'
            }
        }
    },
    
    # Category: qrcode（QRコード設置） - 4項目
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_placement',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'QRコードはどこに貼るのがベストですか？',
                'answer': 'おすすめの設置場所：1. エントランス（最優先）、2. 各部屋、3. キッチン、4. ラウンジ。設置場所ごとに異なるQRコードを生成できます。',
                'keywords': 'QRコード設置,設置場所,おすすめ場所,配置',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'Where is the best place to put QR codes?',
                'answer': 'Recommended locations: 1. Entrance (highest priority), 2. Each room, 3. Kitchen, 4. Lounge. You can generate different QR codes for each location.',
                'keywords': 'QR code placement,location,recommended spots,positioning',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_multiple',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '複数のQRコードを使い分けられますか？',
                'answer': 'はい。設置場所ごとにQRコードを生成できます。各QRコードは設置場所情報を含むため、どこから質問が来たか追跡できます。',
                'keywords': '複数QRコード,QRコード使い分け,場所別QRコード',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'Can I use multiple QR codes?',
                'answer': 'Yes. You can generate QR codes for each location. Each QR code includes location info, so you can track where questions come from.',
                'keywords': 'multiple QR codes,QR code variation,location-specific codes',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_print_size',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'QRコードの印刷サイズの推奨は？',
                'answer': 'A4用紙1枚に1つのQRコードが推奨です。最小サイズは5cm×5cm、推奨サイズは10cm×10cm以上です。小さすぎるとスマホで読み取りにくくなります。',
                'keywords': 'QRコード印刷,印刷サイズ,推奨サイズ,最小サイズ',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'What is the recommended QR code print size?',
                'answer': 'One QR code per A4 sheet is recommended. Minimum size is 5cm×5cm, recommended size is 10cm×10cm or larger. Too small makes it hard to scan with smartphones.',
                'keywords': 'QR code printing,print size,recommended size,minimum size',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_regenerate',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'QRコードを再発行したい場合は？',
                'answer': '「QRコード管理」から既存のQRコードを削除し、新しいQRコードを生成してください。古いQRコードは自動的に無効化されます。',
                'keywords': 'QRコード再発行,QRコード更新,QRコード削除',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'How do I regenerate a QR code?',
                'answer': 'From "QR Code Management", delete the existing QR code and generate a new one. The old QR code will be automatically invalidated.',
                'keywords': 'regenerate QR code,update QR code,delete QR code',
                'related_url': '/admin/qr-code'
            }
        }
    },
    
    # Category: faq_management（FAQ管理） - 5項目
    {
        'category': 'faq_management',
        'intent_key': 'faq_template_usage',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'FAQテンプレートの使い方は？',
                'answer': 'システムが20-30件の初期テンプレートを提供しています。「FAQ管理」から各テンプレートを確認し、施設に合わせて編集してください。不要なFAQは非アクティブ化できます。',
                'keywords': 'FAQテンプレート,初期FAQ,テンプレート編集',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to use FAQ templates?',
                'answer': 'The system provides 20-30 initial templates. From "FAQ Management", review each template and edit to match your facility. Unwanted FAQs can be deactivated.',
                'keywords': 'FAQ templates,initial FAQs,template editing',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_add_custom',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '自分でFAQを追加する方法は？',
                'answer': '「FAQ管理」→「新規FAQ追加」から、質問・回答・カテゴリ・優先度を入力して保存してください。保存時に埋め込みベクトルが自動生成されます。',
                'keywords': 'FAQ追加,カスタムFAQ,FAQ作成,新規FAQ',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to add custom FAQs?',
                'answer': 'From "FAQ Management" → "Add New FAQ", enter question, answer, category, and priority, then save. Embedding vectors are automatically generated on save.',
                'keywords': 'add FAQ,custom FAQ,create FAQ,new FAQ',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_priority',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'FAQの優先度とは何ですか？',
                'answer': '優先度（1-5）は、AI検索時のランキングに影響します。優先度5が最高で、よくある質問には高い優先度を設定してください。',
                'keywords': 'FAQ優先度,優先順位,ランキング',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'What is FAQ priority?',
                'answer': 'Priority (1-5) affects ranking in AI search. Priority 5 is highest. Set high priority for frequently asked questions.',
                'keywords': 'FAQ priority,ranking,priority level',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_category',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'カテゴリはどう分けるべきですか？',
                'answer': 'カテゴリは4種類：基本情報（チェックイン/WiFi等）、設備（キッチン/シャワー等）、周辺情報（駅/コンビニ等）、トラブル（鍵紛失/故障等）。質問内容に最も近いカテゴリを選んでください。',
                'keywords': 'FAQカテゴリ,カテゴリ分類,カテゴリ選択',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How should I categorize FAQs?',
                'answer': '4 categories: Basic (check-in/WiFi), Facilities (kitchen/shower), Location (station/convenience store), Trouble (lost key/malfunction). Choose the category closest to the question content.',
                'keywords': 'FAQ categories,categorization,category selection',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_bulk_import',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'FAQを一括登録できますか？',
                'answer': '現在は個別登録のみですが、Phase 2でCSV一括インポート機能を追加予定です。大量のFAQがある場合は、サポートチームにご相談ください。',
                'keywords': 'FAQ一括登録,CSV登録,大量登録,インポート',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'Can I bulk import FAQs?',
                'answer': 'Currently only individual registration is supported, but CSV bulk import will be added in Phase 2. For large FAQ volumes, please contact our support team.',
                'keywords': 'bulk import FAQ,CSV import,mass registration,import',
                'related_url': '/admin/faqs'
            }
        }
    },
    
    # Category: ai_logic（AI仕組み） - 4項目
    {
        'category': 'ai_logic',
        'intent_key': 'ai_how_it_works',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'AIはどうやって質問に答えていますか？',
                'answer': 'OpenAI GPT-4o-miniを使用しています。登録されたFAQをシステムプロンプトに埋め込み、ゲストの質問に最適な回答を生成します。',
                'keywords': 'AI仕組み,どうやって,GPT-4o-mini,仕組み',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'How does AI answer questions?',
                'answer': 'We use OpenAI GPT-4o-mini. Registered FAQs are embedded in the system prompt to generate optimal responses to guest questions.',
                'keywords': 'how AI works,mechanism,GPT-4o-mini,how it works',
                'related_url': '/admin/dashboard'
            }
        }
    },
    {
        'category': 'ai_logic',
        'intent_key': 'ai_accuracy',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'AIの回答精度を上げるには？',
                'answer': 'FAQ登録時のポイント：1. 質問文は具体的に、2. 回答は簡潔に、3. キーワードを適切に設定、4. 優先度を調整。FAQが充実するほど精度が向上します。',
                'keywords': 'AI精度,精度向上,回答精度,改善',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to improve AI response accuracy?',
                'answer': 'FAQ registration tips: 1. Make questions specific, 2. Keep answers concise, 3. Set keywords properly, 4. Adjust priority. More FAQs improve accuracy.',
                'keywords': 'AI accuracy,improve accuracy,response quality,improvement',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'ai_logic',
        'intent_key': 'ai_languages',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '対応言語は何語ですか？',
                'answer': '現在は日本語、英語、中国語（簡体字・繁体字）、韓国語の5言語に対応しています。ゲストが選択した言語で自動的に回答します。',
                'keywords': '対応言語,多言語,言語設定,何語',
                'related_url': '/admin/facility'
            },
            'en': {
                'question': 'What languages are supported?',
                'answer': 'Currently supports 5 languages: Japanese, English, Chinese (Simplified/Traditional), and Korean. Responses are automatically provided in the guest\'s selected language.',
                'keywords': 'supported languages,multilingual,language settings,what languages',
                'related_url': '/admin/facility'
            }
        }
    },
    {
        'category': 'ai_logic',
        'intent_key': 'ai_limitations',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'AIが答えられない質問はありますか？',
                'answer': 'はい。FAQに登録されていない内容や、リアルタイム情報（天気、在庫状況等）には答えられません。その場合は「スタッフに確認してください」と案内されます。',
                'keywords': 'AI限界,答えられない,できないこと,制限',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'Are there questions AI cannot answer?',
                'answer': 'Yes. AI cannot answer content not registered in FAQs or real-time information (weather, inventory status, etc.). In such cases, it will suggest "Please check with staff."',
                'keywords': 'AI limitations,cannot answer,what it cannot do,restrictions',
                'related_url': '/admin/dashboard'
            }
        }
    },
    
    # Category: logs（ログ分析） - 3項目
    {
        'category': 'logs',
        'intent_key': 'logs_view_questions',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'ゲストの質問履歴はどこで見られますか？',
                'answer': '「ログ管理」→「質問履歴」から、日付・カテゴリ・キーワードで検索できます。各質問のAI信頼度スコアも確認できます。',
                'keywords': '質問履歴,ログ確認,履歴閲覧,チャットログ',
                'related_url': '/admin/logs'
            },
            'en': {
                'question': 'Where can I view guest question history?',
                'answer': 'From "Log Management" → "Question History", you can search by date, category, and keywords. AI confidence scores for each question are also visible.',
                'keywords': 'question history,view logs,history access,chat logs',
                'related_url': '/admin/logs'
            }
        }
    },
    {
        'category': 'logs',
        'intent_key': 'logs_unanswered',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'AIが答えられなかった質問を確認するには？',
                'answer': '「ログ管理」で信頼度スコア0.5以下の質問をフィルタリングできます。これらの質問は新しいFAQ作成の参考になります。',
                'keywords': '答えられなかった質問,低信頼度,FAQ作成参考',
                'related_url': '/admin/logs'
            },
            'en': {
                'question': 'How to check questions AI couldn\'t answer?',
                'answer': 'In "Log Management", filter questions with confidence score 0.5 or below. These questions can be used as references for creating new FAQs.',
                'keywords': 'unanswered questions,low confidence,FAQ creation reference',
                'related_url': '/admin/logs'
            }
        }
    },
    {
        'category': 'logs',
        'intent_key': 'logs_analytics',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'よくある質問のランキングは？',
                'answer': '「ダッシュボード」で質問カテゴリ別の統計と、よく聞かれる質問TOP10を確認できます。週次・月次で傾向を分析できます。',
                'keywords': 'ランキング,統計,よくある質問,分析',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'Where is the FAQ ranking?',
                'answer': 'On the "Dashboard", you can view statistics by question category and TOP 10 frequently asked questions. Analyze trends weekly/monthly.',
                'keywords': 'ranking,statistics,frequently asked,analysis',
                'related_url': '/admin/dashboard'
            }
        }
    },
    
    # Category: troubleshooting（トラブルシューティング） - 5項目
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_ai_slow',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'AIの応答が遅い場合は？',
                'answer': '通常3-5秒以内に応答します。10秒以上かかる場合は、ネットワーク状況を確認するか、ブラウザをリフレッシュしてください。',
                'keywords': 'AI遅い,応答遅延,遅延,速度',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'What if AI response is slow?',
                'answer': 'Normal response time is 3-5 seconds. If it takes over 10 seconds, check network conditions or refresh the browser.',
                'keywords': 'AI slow,response delay,delay,speed',
                'related_url': '/admin/dashboard'
            }
        }
    },
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_qr_not_working',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'QRコードが読み取れない場合は？',
                'answer': '原因：1. QRコードが小さすぎる（5cm未満）、2. 印刷が不鮮明、3. カメラの焦点が合っていない。対処法：大きめのQRコードを再印刷してください。',
                'keywords': 'QRコード読み取れない,スキャンできない,QRエラー',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'What if QR code doesn\'t scan?',
                'answer': 'Causes: 1. QR code too small (under 5cm), 2. Unclear printing, 3. Camera out of focus. Solution: Reprint a larger QR code.',
                'keywords': 'QR code not scanning,cannot scan,QR error',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_faq_not_updated',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'FAQを更新したのに反映されない？',
                'answer': 'FAQ更新後、システムプロンプトの再構築に最大5分かかります。5分待ってもダメな場合は、ブラウザキャッシュをクリアしてください。',
                'keywords': 'FAQ反映されない,更新されない,変更されない',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'FAQ update not reflected?',
                'answer': 'After FAQ update, system prompt reconstruction takes up to 5 minutes. If still not working after 5 minutes, clear browser cache.',
                'keywords': 'FAQ not reflected,not updated,not changed',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_login_failed',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'ログインできない場合は？',
                'answer': '原因：1. メールアドレス/パスワード間違い、2. アカウント未認証、3. セッション期限切れ。対処法：パスワードリセットを試すか、サポートにお問い合わせください。',
                'keywords': 'ログインできない,ログイン失敗,アクセスできない',
                'related_url': '/admin/login'
            },
            'en': {
                'question': 'Cannot login?',
                'answer': 'Causes: 1. Wrong email/password, 2. Account not verified, 3. Session expired. Solution: Try password reset or contact support.',
                'keywords': 'cannot login,login failed,cannot access',
                'related_url': '/admin/login'
            }
        }
    },
    {
        'category': 'troubleshooting',
        'intent_key': 'trouble_contact_support',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'サポートへの問い合わせ方法は？',
                'answer': '画面右下のヘルプボタン→「サポートに連絡」から、問い合わせフォームにアクセスできます。または support@yadopera.com にメールしてください。',
                'keywords': 'サポート,問い合わせ,連絡先,ヘルプ',
                'related_url': '/admin/support'
            },
            'en': {
                'question': 'How to contact support?',
                'answer': 'Click help button at bottom right → "Contact Support" to access inquiry form. Or email support@yadopera.com directly.',
                'keywords': 'support,contact,inquiry,help',
                'related_url': '/admin/support'
            }
        }
    },
    
    # Category: billing（料金） - 3項目
    {
        'category': 'billing',
        'intent_key': 'billing_pricing',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': '料金プランは？',
                'answer': 'PoC期間（3ヶ月）は無料です。その後：ライトプラン ¥3,000/月（FAQ50件まで）、スタンダードプラン ¥8,000/月（FAQ無制限）、エンタープライズ 要相談。',
                'keywords': '料金,プラン,価格,費用',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'What are the pricing plans?',
                'answer': 'PoC period (3 months) is free. After: Light ¥3,000/month (up to 50 FAQs), Standard ¥8,000/month (unlimited FAQs), Enterprise (contact us).',
                'keywords': 'pricing,plans,price,cost',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'category': 'billing',
        'intent_key': 'billing_cancel',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '解約方法は？',
                'answer': '「設定」→「契約情報」→「解約手続き」から、いつでも解約できます。解約月の末日までサービスが利用可能です。',
                'keywords': '解約,キャンセル,退会,辞める',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How to cancel subscription?',
                'answer': 'From "Settings" → "Subscription" → "Cancel", you can cancel anytime. Service remains available until end of cancellation month.',
                'keywords': 'cancel,cancellation,unsubscribe,quit',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'category': 'billing',
        'intent_key': 'billing_invoice',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '請求書の発行は？',
                'answer': '「契約情報」→「請求書履歴」から、過去の請求書をPDFダウンロードできます。領収書の発行も同じ画面から可能です。',
                'keywords': '請求書,領収書,インボイス,ダウンロード',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How to get invoices?',
                'answer': 'From "Subscription" → "Invoice History", you can download past invoices as PDFs. Receipts can also be issued from the same screen.',
                'keywords': 'invoice,receipt,billing,download',
                'related_url': '/admin/billing'
            }
        }
    },
    
    # Category: security（セキュリティ） - 3項目
    {
        'category': 'security',
        'intent_key': 'security_data_privacy',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'ゲストのデータはどう管理されていますか？',
                'answer': '全データはAWS東京リージョンに保存され、SSL/TLS暗号化通信で保護されています。個人情報は7日後に自動削除されます。',
                'keywords': 'データ管理,プライバシー,個人情報,セキュリティ',
                'related_url': '/admin/security'
            },
            'en': {
                'question': 'How is guest data managed?',
                'answer': 'All data is stored in AWS Tokyo region and protected by SSL/TLS encryption. Personal information is automatically deleted after 7 days.',
                'keywords': 'data management,privacy,personal info,security',
                'related_url': '/admin/security'
            }
        }
    },
    {
        'category': 'security',
        'intent_key': 'security_access_control',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'スタッフの権限設定は？',
                'answer': '3つの権限レベル：オーナー（全権限）、マネージャー（FAQ管理・ログ閲覧）、スタッフ（ログ閲覧のみ）。各スタッフに適切な権限を付与してください。',
                'keywords': '権限設定,アクセス制御,スタッフ権限,ロール',
                'related_url': '/admin/staff'
            },
            'en': {
                'question': 'How to set staff permissions?',
                'answer': '3 permission levels: Owner (full access), Manager (FAQ management/log viewing), Staff (log viewing only). Assign appropriate permissions to each staff member.',
                'keywords': 'permissions,access control,staff rights,roles',
                'related_url': '/admin/staff'
            }
        }
    },
    {
        'category': 'security',
        'intent_key': 'security_backup',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'データのバックアップは？',
                'answer': 'データベースは毎日自動バックアップされ、30日間保管されます。万が一のデータ消失時も、前日の状態に復元可能です。',
                'keywords': 'バックアップ,復元,データ保護,復旧',
                'related_url': '/admin/security'
            },
            'en': {
                'question': 'How is data backed up?',
                'answer': 'Database is automatically backed up daily and stored for 30 days. In case of data loss, restoration to previous day\'s state is possible.',
                'keywords': 'backup,restore,data protection,recovery',
                'related_url': '/admin/security'
            }
        }
    }
]

def upgrade():
    conn = op.get_bind()
    
    for faq_data in INITIAL_FAQS:
        # operator_faqs insert
        result = conn.execute(
            sa.text(
                """
                INSERT INTO operator_faqs (category, intent_key, display_order, is_active)
                VALUES (:category, :intent_key, :display_order, true)
                RETURNING id
                """
            ),
            {
                'category': faq_data['category'],
                'intent_key': faq_data['intent_key'],
                'display_order': faq_data['display_order']
            }
        )
        faq_id = result.fetchone()[0]
        
        # operator_faq_translations insert
        for lang, translation in faq_data['translations'].items():
            conn.execute(
                sa.text(
                    """
                    INSERT INTO operator_faq_translations 
                    (faq_id, language, question, answer, keywords, related_url)
                    VALUES (:faq_id, :language, :question, :answer, :keywords, :related_url)
                    """
                ),
                {
                    'faq_id': faq_id,
                    'language': lang,
                    'question': translation['question'],
                    'answer': translation['answer'],
                    'keywords': translation['keywords'],
                    'related_url': translation['related_url']
                }
            )

def downgrade():
    # FAQsの削除（cascadeで翻訳も削除される）
    op.execute("DELETE FROM operator_faqs")
```

---

## 5. API設計

### 5.1 エンドポイント一覧

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/api/v1/help/faqs` | 全FAQ取得（カテゴリフィルタ可） | 必要 |
| GET | `/api/v1/help/faqs/{category}` | カテゴリ別FAQ取得 | 必要 |
| GET | `/api/v1/help/search` | FAQ検索 | 必要 |
| POST | `/api/v1/help/chat` | AIチャット | 必要 |

### 5.2 API詳細仕様

#### GET /api/v1/help/faqs

**説明**: 全FAQ取得（オペレーター向け）

**Query Parameters**:
- `category` (optional): カテゴリフィルタ
- `language` (optional, default: 'ja'): 言語

**Response** (200 OK):
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

#### GET /api/v1/help/search

**説明**: FAQ全文検索

**Query Parameters**:
- `q` (required): 検索クエリ
- `language` (optional, default: 'ja'): 言語

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": 1,
      "question": "アカウント作成の手順は？",
      "answer": "管理画面トップページから...",
      "category": "setup",
      "related_url": "/admin/register",
      "relevance_score": 0.95
    }
  ],
  "total": 5,
  "query": "アカウント作成"
}
```

#### POST /api/v1/help/chat

**説明**: AIヘルプチャット

**Request Body**:
```json
{
  "message": "FAQの登録方法を教えてください",
  "language": "ja"
}
```

**Response** (200 OK):
```json
{
  "response": "FAQ登録は「FAQ管理」→「新規FAQ追加」から行えます。質問・回答・カテゴリ・優先度を入力して保存してください。",
  "related_faqs": [
    {
      "id": 10,
      "question": "自分でFAQを追加する方法は？",
      "category": "faq_management"
    }
  ],
  "related_url": "/admin/faqs",
  "timestamp": "2025-12-25T10:30:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Message is required and must be non-empty"
}
```

---

## 6. フロントエンド設計

### 6.1 コンポーネント構成

```
src/
├── components/
│   └── help/
│       ├── HelpButton.vue          # 右下固定ヘルプボタン
│       ├── HelpModal.vue           # ヘルプモーダル（FAQタブ + チャットタブ）
│       ├── FaqList.vue             # FAQ一覧表示
│       ├── FaqSearchBar.vue        # FAQ検索バー
│       ├── CategoryFilter.vue      # カテゴリフィルタ
│       └── AiChatPanel.vue         # AIチャットパネル
├── stores/
│   └── helpStore.ts                # ヘルプストア（Pinia）
└── types/
    └── help.ts                     # 型定義
```

### 6.2 主要コンポーネント詳細

#### HelpButton.vue

**説明**: 全ページ共通の右下固定ヘルプボタン

```vue
<template>
  <div class="fixed bottom-6 right-6 z-50">
    <button
      @click="openHelpModal"
      class="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all"
      aria-label="ヘルプ"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </button>
    
    <HelpModal v-if="isHelpModalOpen" @close="closeHelpModal" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HelpModal from './HelpModal.vue'

const isHelpModalOpen = ref(false)

const openHelpModal = () => {
  isHelpModalOpen.value = true
}

const closeHelpModal = () => {
  isHelpModalOpen.value = false
}
</script>
```

#### HelpModal.vue

**説明**: FAQタブとAIチャットタブを切り替え可能なモーダル

```vue
<template>
  <teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b">
          <h2 class="text-2xl font-semibold">ヘルプ</h2>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Tabs -->
        <div class="flex border-b">
          <button
            @click="activeTab = 'faq'"
            :class="['flex-1 py-4 text-center font-medium transition-colors',
                     activeTab === 'faq' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-gray-900']"
          >
            FAQ
          </button>
          <button
            @click="activeTab = 'chat'"
            :class="['flex-1 py-4 text-center font-medium transition-colors',
                     activeTab === 'chat' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-gray-900']"
          >
            AIチャット
          </button>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <FaqList v-if="activeTab === 'faq'" />
          <AiChatPanel v-else />
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FaqList from './FaqList.vue'
import AiChatPanel from './AiChatPanel.vue'

defineEmits(['close'])

const activeTab = ref<'faq' | 'chat'>('faq')
</script>
```

#### AiChatPanel.vue

**説明**: AIチャットインターフェース

```vue
<template>
  <div class="flex flex-col h-full">
    <!-- Chat Messages -->
    <div class="flex-1 overflow-y-auto space-y-4 mb-4">
      <div v-for="msg in messages" :key="msg.id" 
           :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
        <div :class="['max-w-[70%] rounded-lg p-4',
                      msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900']">
          <p class="whitespace-pre-wrap">{{ msg.content }}</p>
          
          <!-- Related FAQs -->
          <div v-if="msg.related_faqs && msg.related_faqs.length > 0" class="mt-3 space-y-2">
            <p class="text-sm font-medium">関連FAQ:</p>
            <div v-for="faq in msg.related_faqs" :key="faq.id" 
                 class="text-sm bg-white bg-opacity-20 rounded p-2 cursor-pointer hover:bg-opacity-30"
                 @click="viewFaq(faq.id)">
              {{ faq.question }}
            </div>
          </div>
          
          <!-- Related URL -->
          <div v-if="msg.related_url" class="mt-3">
            <a :href="msg.related_url" 
               class="text-sm underline hover:no-underline"
               target="_blank">
              設定画面を開く →
            </a>
          </div>
        </div>
      </div>
      
      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-start">
        <div class="bg-gray-100 rounded-lg p-4">
          <div class="flex space-x-2">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Input Form -->
    <form @submit.prevent="sendMessage" class="flex gap-2">
      <input
        v-model="inputMessage"
        type="text"
        placeholder="質問を入力してください..."
        class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
        :disabled="isLoading"
      />
      <button
        type="submit"
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="isLoading || !inputMessage.trim()"
      >
        送信
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useHelpStore } from '@/stores/helpStore'
import type { ChatMessage } from '@/types/help'

const helpStore = useHelpStore()
const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const isLoading = ref(false)

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date()
  }
  
  messages.value.push(userMessage)
  const query = inputMessage.value
  inputMessage.value = ''
  isLoading.value = true
  
  try {
    const response = await helpStore.sendChatMessage(query)
    
    messages.value.push({
      id: Date.now().toString(),
      role: 'assistant',
      content: response.response,
      related_faqs: response.related_faqs,
      related_url: response.related_url,
      timestamp: new Date()
    })
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({
      id: Date.now().toString(),
      role: 'assistant',
      content: '申し訳ございません。エラーが発生しました。もう一度お試しください。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
  }
}

const viewFaq = (faqId: number) => {
  // FAQ詳細を表示する処理
  helpStore.setActiveFaq(faqId)
}

onMounted(() => {
  // 初期メッセージ
  messages.value.push({
    id: '0',
    role: 'assistant',
    content: 'こんにちは！やどぺらのヘルプチャットです。ご質問をお気軽にどうぞ。',
    timestamp: new Date()
  })
})
                      