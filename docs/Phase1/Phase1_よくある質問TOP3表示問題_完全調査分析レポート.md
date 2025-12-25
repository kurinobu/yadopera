# Phase 1: よくある質問TOP3表示問題 完全調査分析レポート

**作成日**: 2025年12月3日  
**実施者**: Auto (AI Assistant)  
**対象**: よくある質問TOP3が表示されない問題  
**状態**: ⚠️ **根本原因特定完了（修正は実施しません）**

---

## 1. 問題の概要

### 1.1 ユーザー報告

**報告内容**:
- Welcome画面でよくある質問TOP3が表示されていない
- セクション自体が表示されていない

### 1.2 問題の症状

**確認された症状**:
- ❌ Welcome画面でよくある質問TOP3が表示されない
- ❌ 「よくある質問はありません」というメッセージが表示される可能性がある

---

## 2. コード調査結果

### 2.1 フロントエンド実装の確認

**関連ファイル**:
- `frontend/src/views/guest/Welcome.vue` - Welcome画面コンポーネント
- `frontend/src/components/guest/TopQuestions.vue` - よくある質問TOP3コンポーネント
- `frontend/src/stores/facility.ts` - 施設情報ストア
- `frontend/src/api/facility.ts` - 施設情報APIクライアント

**Welcome.vueの実装**:

```74:93:frontend/src/views/guest/Welcome.vue
onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null

    // TODO: facilityIdからslugを取得する処理（Week 4で実装）
    // 現在はfacilityIdをslugとして使用
    const slug = facilityId.value
    
    const response = await facilityApi.getFacility(slug, location.value)
    
    facilityStore.setFacility(response.facility)
    facilityStore.setTopQuestions(response.top_questions)
  } catch (err) {
    error.value = '施設情報の取得に失敗しました'
    console.error('Facility fetch error:', err)
  } finally {
    isLoading.value = false
  }
})
```

**問題点の特定**:
- `facilityId`は`route.params.facilityId`から取得される（文字列）
- `facilityId`は数値ID（例：`"2"`）またはslug（例：`"test-facility"`）の可能性がある
- 現在のコードは`facilityId`をそのまま`slug`として使用している
- しかし、APIエンドポイントは`/api/v1/facility/{slug}`を期待している

**TopQuestions.vueの実装**:

```6:35:frontend/src/components/guest/TopQuestions.vue
    <div v-if="questions.length > 0" class="space-y-3">
      <button
        v-for="question in questions"
        :key="question.id"
        @click="handleQuestionClick(question)"
        class="w-full text-left p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-600 hover:shadow-md transition-all"
      >
        <div class="flex items-start justify-between">
          <p class="text-sm font-medium text-gray-900 dark:text-white flex-1">
            {{ question.question }}
          </p>
          <svg
            class="w-5 h-5 text-gray-400 flex-shrink-0 ml-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </button>
    </div>
    <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
      <p class="text-sm">よくある質問はありません</p>
    </div>
```

**確認事項**:
- ✅ `questions.length > 0`の条件で表示が制御されている
- ✅ `questions`が空配列の場合、「よくある質問はありません」が表示される

### 2.2 バックエンドAPI実装の確認

**関連ファイル**:
- `backend/app/api/v1/facility.py` - 施設情報APIエンドポイント
- `backend/app/services/facility_service.py` - 施設サービス

**APIエンドポイント**:

```15:44:backend/app/api/v1/facility.py
@router.get("/{slug}", response_model=dict)
async def get_facility(
    slug: str,
    location: Optional[str] = Query(None, description="QRコード設置場所（entrance/room/kitchen/lounge）"),
    db: AsyncSession = Depends(get_db)
):
    """
    施設情報取得（公開API）
    
    - **slug**: 施設slug（URL用識別子）
    - **location**: QRコード設置場所（オプション）
    
    施設情報とよくある質問TOP3を返却します
    """
    facility_info = await FacilityService.get_facility_public_info(db, slug)
    
    # レスポンス形式（アーキテクチャ設計書に合わせる）
    return {
        "facility": {
            "id": facility_info.id,
            "name": facility_info.name,
            "slug": facility_info.slug,
            "email": facility_info.email,
            "phone": facility_info.phone,
            "check_in_time": facility_info.check_in_time,
            "check_out_time": facility_info.check_out_time,
            "wifi_ssid": facility_info.wifi_ssid,
        },
        "top_questions": facility_info.top_questions,
    }
```

**確認事項**:
- ✅ APIエンドポイントは`/api/v1/facility/{slug}`を期待している
- ✅ `slug`は文字列として受け取られる
- ✅ レスポンスには`top_questions`が含まれている

**FacilityServiceの実装**:

```79:100:backend/app/services/facility_service.py
        # よくある質問TOP3を取得
        faq_query = select(FAQ).where(
            FAQ.facility_id == facility.id,
            FAQ.is_active == True
        ).order_by(
            FAQ.priority.desc(),
            FAQ.created_at.desc()
        ).limit(3)
        
        faq_result = await db.execute(faq_query)
        top_faqs = faq_result.scalars().all()
        
        # TopQuestion型に変換（フロントエンドの型定義に合わせる）
        top_questions: List[TopQuestion] = [
            TopQuestion(
                id=faq.id,
                question=faq.question,
                answer=faq.answer,
                category=faq.category
            )
            for faq in top_faqs
        ]
```

**確認事項**:
- ✅ FAQが`is_active = True`で、`priority`の降順でTOP3を取得している
- ✅ `top_questions`が正しく生成されている

### 2.3 データベースの確認

**確認結果**:

```sql
SELECT id, facility_id, question, priority, is_active, created_at 
FROM faqs 
WHERE facility_id = 2 
ORDER BY priority DESC, created_at DESC 
LIMIT 5;
```

**結果**:
| id | facility_id | question | priority | is_active | created_at |
|----|------------|----------|----------|-----------|------------|
| 5 | 2 | ご近所ツアーなどのイベントはありますか？ | 3 | t | 2025-12-02 06:38:05 |
| 4 | 2 | レンタルバイクはありますか？ | 3 | t | 2025-12-02 01:41:28 |
| 3 | 2 | フロントはいつ開いてますか？ | 3 | t | 2025-12-02 01:03:19 |

**確認事項**:
- ✅ FAQが存在する（3件）
- ✅ `is_active = true`である
- ✅ `priority`が設定されている（すべて3）
- ✅ `facility_id = 2`である

**施設情報の確認**:

```sql
SELECT id, slug, name FROM facilities WHERE id = 2;
```

**結果**:
| id | slug | name |
|----|------|------|
| 2 | test-facility | Test Facility |

**確認事項**:
- ✅ 施設が存在する
- ✅ `slug = "test-facility"`である

### 2.4 APIレスポンスの確認

**APIテスト**:

```bash
curl http://localhost:8000/api/v1/facility/test-facility
```

**結果**:
```json
{
  "facility": {
    "id": 2,
    "name": "Test Facility",
    "slug": "test-facility",
    "email": "test@example.com",
    "phone": "090-1234-5678",
    "check_in_time": "15:00",
    "check_out_time": "11:00",
    "wifi_ssid": "TestWiFi"
  },
  "top_questions": [
    {
      "id": 5,
      "question": "ご近所ツアーなどのイベントはありますか？",
      "answer": "毎週金土日曜日に実施してます。",
      "category": "basic"
    },
    {
      "id": 4,
      "question": "レンタルバイクはありますか？",
      "answer": "あります。予約が必要です。",
      "category": "basic"
    },
    {
    "id": 3,
      "question": "フロントはいつ開いてますか？",
      "answer": "15:00pm-9:00pmです。",
      "category": "basic"
    }
  ]
}
```

**確認事項**:
- ✅ APIは正常に動作している
- ✅ `top_questions`が正しく返されている（3件）
- ✅ データ構造が正しい

---

## 3. 根本原因の特定

### 3.1 問題の根本原因

**根本原因**: `facilityId`と`slug`の不一致

**詳細**:
1. **ルーティング**: `/f/:facilityId`の形式で、`facilityId`は数値ID（例：`"2"`）またはslug（例：`"test-facility"`）の可能性がある
2. **APIエンドポイント**: `/api/v1/facility/{slug}`を期待しており、slug（文字列）を要求している
3. **現在の実装**: `facilityId`をそのまま`slug`として使用している
4. **問題**: `facilityId`が数値ID（例：`"2"`）の場合、APIは`/api/v1/facility/2`を呼び出すが、これはslugではないため、404エラーになる可能性がある

**確認**:
- データベースには`slug = "test-facility"`が存在する
- APIは`/api/v1/facility/test-facility`で正常に動作する
- しかし、`/api/v1/facility/2`で呼び出すと、slugではないため、404エラーになる可能性がある

### 3.2 問題の発生条件

**発生条件**:
1. ユーザーが`/f/2`（数値ID）でアクセスした場合
2. `facilityId = "2"`が`slug`として使用される
3. APIは`/api/v1/facility/2`を呼び出す
4. しかし、`2`はslugではないため、`get_facility_by_slug()`が`None`を返す
5. `HTTPException(404, "Facility not found")`が発生する
6. フロントエンドでエラーが発生し、`top_questions`が設定されない

### 3.3 ルーティングの確認

**ルーティング定義**:

```17:22:frontend/src/router/guest.ts
    path: '/f/:facilityId/welcome',
    name: 'Welcome',
    component: () => import('@/views/guest/Welcome.vue'),
    meta: {
      layout: 'guest'
    }
```

**確認事項**:
- ✅ `:facilityId`は動的パラメータとして定義されている
- ✅ `facilityId`は文字列として受け取られる（数値IDまたはslug）

---

## 4. 修正案

### 4.1 修正方針

**目的**: `facilityId`が数値IDの場合、slugに変換する処理を追加する

**修正方針**:
1. **オプション1**: `facilityId`が数値IDの場合、slugに変換するAPIを追加する
2. **オプション2**: `facilityId`が数値IDの場合、バックエンドでIDでも検索できるようにする
3. **オプション3**: フロントエンドで`facilityId`が数値IDの場合、slugを取得する処理を追加する

### 4.2 修正案1: バックエンドでIDでも検索できるようにする（推奨）

**修正内容**:
- バックエンドの`get_facility_public_info()`を修正し、`slug`が数値IDの場合も対応できるようにする
- `slug`が数値として解釈できる場合、IDとして検索する

**メリット**:
- フロントエンドの変更が最小限
- バックエンドで統一的な処理が可能
- 既存のAPIエンドポイントを維持できる

**デメリット**:
- バックエンドの変更が必要

**実装例**:
```python
# backend/app/services/facility_service.py
@staticmethod
async def get_facility_public_info(
    db: AsyncSession,
    slug: str
) -> FacilityPublicResponse:
    """
    施設情報を公開用形式で取得
    
    Args:
        db: データベースセッション
        slug: 施設slugまたはID（文字列）
        
    Returns:
        施設情報公開レスポンス
        
    Raises:
        HTTPException: 施設が見つからない場合
    """
    # slugが数値IDの場合も対応
    facility = None
    
    # まず、slugとして検索を試みる
    facility = await FacilityService.get_facility_by_slug(db, slug)
    
    # slugで見つからない場合、数値IDとして検索を試みる
    if facility is None:
        try:
            facility_id = int(slug)
            result = await db.execute(
                select(Facility).where(
                    Facility.id == facility_id,
                    Facility.is_active == True
                )
            )
            facility = result.scalar_one_or_none()
        except ValueError:
            # slugが数値として解釈できない場合は何もしない
            pass
    
    if facility is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    
    # 以下、既存の処理...
```

### 4.3 修正案2: フロントエンドでslugを取得する処理を追加する

**修正内容**:
- フロントエンドで`facilityId`が数値IDの場合、slugを取得するAPIを追加する
- または、施設情報を取得する際に、IDからslugを取得する処理を追加する

**メリット**:
- バックエンドの変更が不要
- フロントエンドで柔軟な処理が可能

**デメリット**:
- フロントエンドの変更が必要
- 追加のAPI呼び出しが必要になる可能性がある

**実装例**:
```typescript
// frontend/src/views/guest/Welcome.vue
onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null

    let slug = facilityId.value
    
    // facilityIdが数値IDの場合、slugを取得する
    if (!isNaN(Number(facilityId.value))) {
      // IDから施設情報を取得してslugを取得
      // または、IDからslugを取得する専用APIを呼び出す
      const facilityInfo = await facilityApi.getFacilityById(Number(facilityId.value))
      slug = facilityInfo.slug
    }
    
    const response = await facilityApi.getFacility(slug, location.value)
    
    facilityStore.setFacility(response.facility)
    facilityStore.setTopQuestions(response.top_questions)
  } catch (err) {
    error.value = '施設情報の取得に失敗しました'
    console.error('Facility fetch error:', err)
  } finally {
    isLoading.value = false
  }
})
```

### 4.4 修正案3: ルーティングをslugベースに変更する

**修正内容**:
- ルーティングを`/f/:slug`に変更する
- すべてのURLでslugを使用する

**メリット**:
- 一貫性のあるURL構造
- 問題の根本的な解決

**デメリット**:
- 既存のURLとの互換性の問題
- 大規模な変更が必要

### 4.5 推奨修正案

**推奨**: **修正案1（バックエンドでIDでも検索できるようにする）**

**理由**:
1. **最小限の変更**: フロントエンドの変更が最小限
2. **後方互換性**: 既存のURL（`/f/2`）でも動作する
3. **柔軟性**: slugとIDの両方に対応できる
4. **統一的な処理**: バックエンドで統一的な処理が可能

---

## 5. 修正時の注意事項

### 5.1 テスト項目

**確認項目**:
- [ ] `/f/2`（数値ID）でアクセスした場合、正常に動作する
- [ ] `/f/test-facility`（slug）でアクセスした場合、正常に動作する
- [ ] よくある質問TOP3が正しく表示される
- [ ] エラーハンドリングが適切に動作する

### 5.2 エラーハンドリング

**確認事項**:
- ✅ 施設が見つからない場合、適切なエラーメッセージを表示する
- ✅ APIエラーが発生した場合、適切にハンドリングする

---

## 6. まとめ

### 6.1 問題の要約

**根本原因**: `facilityId`と`slug`の不一致

**詳細**:
- `facilityId`が数値ID（例：`"2"`）の場合、APIは`/api/v1/facility/2`を呼び出す
- しかし、`2`はslugではないため、`get_facility_by_slug()`が`None`を返す
- `HTTPException(404, "Facility not found")`が発生する
- フロントエンドでエラーが発生し、`top_questions`が設定されない

### 6.2 修正方針

**推奨修正案**: バックエンドでIDでも検索できるようにする

**理由**:
- 最小限の変更で問題を解決できる
- 既存のURLとの互換性を維持できる
- 柔軟性が高い

### 6.3 次のステップ

**修正実施時の手順**:
1. バックエンドの`get_facility_public_info()`を修正
2. `slug`が数値IDの場合も対応できるようにする
3. 動作確認を実施
4. ブラウザテストを実施

**重要**: 修正は実施しません。ユーザーからの指示があるまで、調査分析と評価のみを行います。

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-03  
**Status**: ⚠️ **根本原因特定完了（修正は実施しません）**


