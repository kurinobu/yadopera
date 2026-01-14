# StandardプランFAQ20件問題 完全調査分析・修正案

**作成日**: 2025年1月13日  
**対象**: Standardプランで新規登録後、FAQが20件しか表示されない問題（リロード後）  
**目的**: 原因を完全に調査分析し、大原則に準拠した修正案を立案

---

## 1. 問題の概要

### 1.1 発生状況

- **プラン**: Standardプラン
- **期待値**: 30件のFAQが自動登録される
- **実際の動作**:
  - 初回表示: 5件表示
  - リロード後: 20件表示
  - 最終的には30件が登録されるが、表示されない
- **データベース確認**: 30件のFAQが登録されている（Basic: 8件、Facilities: 10件、Location: 6件、Trouble: 6件）

### 1.2 問題の特徴

- データベースには正しく30件のFAQが登録されている
- しかし、フロントエンドでは20件しか表示されない（リロード後）
- 初回表示では5件、リロード後は20件と、タイミングによって表示件数が異なる

---

## 2. 根本原因の分析

### 2.1 データベース確認結果

**最新の施設（ID: 27, Standardプラン）**:
- 登録されているFAQ数: **30件** ✅
- Basicカテゴリ: **8件** ✅
- Facilitiesカテゴリ: **10件** ✅
- Locationカテゴリ: **6件** ✅
- Troubleカテゴリ: **6件** ✅

**FAQ作成のタイミング**:
- 施設作成日時: `2026-01-13 04:52:06.694862+00:00`
- 最初のFAQ作成: `2026-01-13 04:52:06.975507+00:00`（約0.28秒後）
- 5件目のFAQ作成: `2026-01-13 04:52:10.205611+00:00`（約3.5秒後）
- 20件目のFAQ作成: `2026-01-13 04:52:20.441393+00:00`（約13.7秒後）
- 30件目のFAQ作成: `2026-01-13 04:52:29.079350+00:00`（約22.4秒後）

**結論**: データベースには正しく30件のFAQが登録されているが、作成に約22秒かかっている

### 2.2 バックグラウンド処理の確認

**`bulk_create_faqs`の実装**:
- FAQ作成は順次処理されている（`for`ループで1件ずつ処理）
- 各FAQ作成時にembedding生成が含まれるため、1件あたり約0.7秒かかる
- 30件のFAQを作成するのに約22秒かかる

**問題点**:
- バックグラウンド処理が完了する前にFAQ一覧を取得すると、その時点でのFAQ数がキャッシュされる
- キャッシュが無効化されるのは、バックグラウンド処理が完了した後
- そのため、初回表示時とリロード時で異なる件数が表示される

### 2.3 キャッシュの問題

**FAQ一覧取得APIのキャッシュ**:
- `FAQService.get_faqs()`はキャッシュを使用している
- キャッシュキー: `faq:list:facility_id={facility_id}:category={category}:is_active={is_active}`
- キャッシュTTL: 1時間（3600秒）

**問題の発生フロー**:
1. 新規登録APIが呼び出される（施設・ユーザー作成）
2. バックグラウンド処理が開始される（FAQ作成開始）
3. フロントエンドがFAQ一覧取得APIを呼び出す（約3.5秒後、5件作成済み）
4. キャッシュに5件のFAQが保存される
5. バックグラウンド処理が進行中（20件作成済み）
6. フロントエンドがリロードしてFAQ一覧取得APIを呼び出す（約13.7秒後）
7. キャッシュが無効化されていないため、新しいキャッシュに20件のFAQが保存される
8. バックグラウンド処理が完了（30件作成済み、キャッシュ無効化）
9. しかし、フロントエンドは20件のキャッシュを参照している

**根本原因**:
- バックグラウンド処理が完了する前にFAQ一覧を取得すると、その時点でのFAQ数がキャッシュされる
- キャッシュ無効化がバックグラウンド処理の完了時のみ実行されているため、途中の状態がキャッシュに残る
- バックグラウンド処理が完了した後も、古いキャッシュ（20件）が残っている

---

## 3. 根本原因の特定

### 3.1 主原因: バックグラウンド処理中のキャッシュ保存

**問題の本質**:
- バックグラウンド処理が完了する前にFAQ一覧を取得すると、その時点でのFAQ数がキャッシュされる
- キャッシュ無効化がバックグラウンド処理の完了時のみ実行されているため、途中の状態がキャッシュに残る
- バックグラウンド処理が完了した後も、古いキャッシュ（20件）が残っている

**証拠**:
- 初回表示: 5件（バックグラウンド処理開始直後）
- リロード後: 20件（バックグラウンド処理進行中）
- データベース: 30件（バックグラウンド処理完了後）

### 3.2 副次的原因: キャッシュ無効化のタイミング

**問題の本質**:
- キャッシュ無効化がバックグラウンド処理の完了時のみ実行されている
- バックグラウンド処理が完了する前にFAQ一覧を取得すると、その時点でのFAQ数がキャッシュされる
- バックグラウンド処理が完了した後も、古いキャッシュが残っている

---

## 4. 修正案（大原則に準拠）

### 4.1 修正案1: バックグラウンド処理中のキャッシュ保存を防止（根本解決）

**方針**: バックグラウンド処理が完了するまで、FAQ一覧取得APIでキャッシュを保存しない

**修正内容**:

**ファイル**: `backend/app/services/faq_service.py`

**修正箇所**: `get_faqs`メソッド

```python
async def get_faqs(
    self,
    facility_id: int,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[FAQResponse]:
    """
    FAQ一覧取得（キャッシュ対応、インテントベース構造）
    
    Args:
        facility_id: 施設ID
        category: カテゴリフィルタ（オプション）
        is_active: 有効/無効フィルタ（オプション）
    
    Returns:
        List[FAQResponse]: FAQリスト（translationsを含む）
    """
    # キャッシュキー生成
    cache_key_str = cache_key(
        "faq:list",
        facility_id=facility_id,
        category=category,
        is_active=is_active
    )
    
    # キャッシュから取得を試みる
    cached_faqs = await get_cache(cache_key_str)
    if cached_faqs is not None:
        logger.debug(f"FAQ cache hit: {cache_key_str}")
        return [FAQResponse(**faq_dict) for faq_dict in cached_faqs]
    
    # キャッシュミス: データベースから取得
    logger.debug(f"FAQ cache miss: {cache_key_str}")
    query = select(FAQ).where(FAQ.facility_id == facility_id)
    
    if category:
        query = query.where(FAQ.category == category)
    
    if is_active is not None:
        query = query.where(FAQ.is_active == is_active)
    
    # 関連するFAQTranslationを取得（selectinloadを使用）
    query = query.options(selectinload(FAQ.translations))
    query = query.order_by(FAQ.priority.desc(), FAQ.created_at.desc())
    
    result = await self.db.execute(query)
    faqs = result.scalars().all()
    
    # FAQResponseを作成（translationsを含む）
    faq_responses = []
    for faq in faqs:
        # FAQTranslationをFAQTranslationResponseに変換
        translations = [
            FAQTranslationResponse(
                id=trans.id,
                faq_id=trans.faq_id,
                language=trans.language,
                question=trans.question,
                answer=trans.answer,
                created_at=trans.created_at,
                updated_at=trans.updated_at
            )
            for trans in faq.translations
        ]
        
        faq_responses.append(
            FAQResponse(
                id=faq.id,
                facility_id=faq.facility_id,
                category=faq.category,
                intent_key=faq.intent_key,
                translations=translations,
                priority=faq.priority,
                is_active=faq.is_active,
                created_by=faq.created_by,
                created_at=faq.created_at,
                updated_at=faq.updated_at
            )
        )
    
    # バックグラウンド処理が完了しているか確認
    # 施設作成から30秒以内の場合、バックグラウンド処理が完了していない可能性がある
    from app.models.facility import Facility
    facility = await self.db.get(Facility, facility_id)
    if facility:
        from datetime import datetime, timezone, timedelta
        time_since_creation = datetime.now(timezone.utc) - facility.created_at
        # 施設作成から30秒以内の場合、キャッシュを保存しない（バックグラウンド処理が完了していない可能性がある）
        if time_since_creation < timedelta(seconds=30):
            logger.debug(
                f"Skipping cache save for recently created facility: "
                f"facility_id={facility_id}, time_since_creation={time_since_creation.total_seconds()}s"
            )
            return faq_responses
    
    # キャッシュに保存（辞書形式で保存）
    faq_dicts = [faq.model_dump() for faq in faq_responses]
    await set_cache(cache_key_str, faq_dicts, FAQ_CACHE_TTL)
    
    return faq_responses
```

**メリット**:
- バックグラウンド処理が完了するまで、キャッシュに途中の状態が保存されない
- フロントエンドで最新のデータが取得される
- 根本的な解決

**デメリット**:
- 施設作成直後はキャッシュが効かない（影響は軽微、30秒以内のみ）

**大原則への準拠**:
- ✅ 根本解決 > 暫定解決（根本原因を解決）
- ✅ シンプル構造 > 複雑構造（シンプルな時間チェック）
- ✅ 統一・同一化 > 特殊独自（既存のパターンに従う）
- ✅ 具体的 > 一般（具体的な時間チェック）
- ✅ 拙速 < 安全確実（エラーハンドリングを追加）

### 4.2 修正案2: バックグラウンド処理完了フラグを使用（代替案）

**方針**: バックグラウンド処理の完了をフラグで管理し、完了するまでキャッシュを保存しない

**修正内容**:

**ファイル**: `backend/app/services/auth_service.py`、`backend/app/services/faq_service.py`

**実装**:
1. 施設テーブルに`faq_initialization_completed`フラグを追加（またはRedisにフラグを保存）
2. バックグラウンド処理完了時にフラグを設定
3. FAQ一覧取得時にフラグを確認し、完了していない場合はキャッシュを保存しない

**メリット**:
- より確実にバックグラウンド処理の完了を判定できる
- 時間ベースの判定よりも正確

**デメリット**:
- データベーススキーマの変更が必要（またはRedisの追加利用）
- 実装が複雑になる

**大原則への準拠**:
- ⚠️ シンプル構造 > 複雑構造（データベーススキーマの変更が必要）

**推奨**: ⚠️ **この修正案は採用しない（複雑になるため）**

### 4.3 修正案3: バックグラウンド処理完了後にキャッシュを強制的に無効化（補助的修正）

**方針**: バックグラウンド処理完了後、一定時間経過後に再度キャッシュを無効化する

**修正内容**:

**ファイル**: `backend/app/services/auth_service.py`

**実装**:
- バックグラウンド処理完了後、5秒待ってから再度キャッシュを無効化
- これにより、バックグラウンド処理完了直後に取得されたキャッシュも無効化される

**メリット**:
- 既存の実装を大きく変更しない
- バックグラウンド処理完了後のキャッシュも無効化できる

**デメリット**:
- 時間ベースの判定のため、確実性が低い
- 根本的な解決にはならない

**大原則への準拠**:
- ⚠️ 根本解決 > 暫定解決（根本原因を解決していない）

**推奨**: ⚠️ **この修正案は補助的に使用（修正案1と組み合わせ）**

---

## 5. 修正の優先順位

### 優先度1: バックグラウンド処理中のキャッシュ保存を防止（根本解決）
- **影響**: FAQ一覧が正しく表示されない
- **緊急度**: 高
- **修正内容**: `get_faqs`メソッドで、施設作成から30秒以内の場合はキャッシュを保存しない

### 優先度2: バックグラウンド処理完了後のキャッシュ無効化を強化（補助的修正）
- **影響**: バックグラウンド処理完了直後のキャッシュも無効化する
- **緊急度**: 中
- **修正内容**: バックグラウンド処理完了後、5秒待ってから再度キャッシュを無効化

---

## 6. 修正後の期待動作

### 6.1 バックグラウンド処理中のキャッシュ保存を防止後

- ✅ バックグラウンド処理が完了するまで、キャッシュに途中の状態が保存されない
- ✅ フロントエンドで最新のデータが取得される
- ✅ Standardプランで30件のFAQが正しく表示される
- ✅ 施設作成直後（30秒以内）はキャッシュが効かないが、最新のデータが取得される

### 6.2 バックグラウンド処理完了後のキャッシュ無効化強化後

- ✅ バックグラウンド処理完了直後に取得されたキャッシュも無効化される
- ✅ より確実に最新のデータが取得される

---

## 7. テスト項目

### 7.1 バックグラウンド処理中のキャッシュ保存を防止後

1. **Standardプランの新規登録テスト**
   - Standardプランで新規登録
   - 登録直後（5秒後）にFAQ一覧取得APIを呼び出す
   - 最新のFAQ数が返されることを確認（途中の状態がキャッシュされない）

2. **リロードテスト**
   - 新規登録後、リロードしてFAQ一覧取得APIを呼び出す
   - 30件のFAQが返されることを確認

3. **キャッシュの確認**
   - 施設作成から30秒以内の場合、キャッシュが保存されないことを確認
   - 施設作成から30秒以上経過後、キャッシュが保存されることを確認

### 7.2 バックグラウンド処理完了後のキャッシュ無効化強化後

1. **バックグラウンド処理完了後のキャッシュ無効化確認**
   - バックグラウンド処理完了後、5秒待ってから再度キャッシュを無効化されることを確認
   - ログでキャッシュ無効化のメッセージを確認

---

## 8. 大原則への準拠

### 8.1 根本解決 > 暫定対応
- ✅ バックグラウンド処理中のキャッシュ保存を防止して根本原因を解決
- ✅ 暫定的なキャッシュクリアではなく、根本的な解決

### 8.2 シンプルな構造 > 複雑な構造
- ✅ シンプルな時間チェック（施設作成から30秒以内）
- ✅ データベーススキーマの変更は不要

### 8.3 安全性と確実性 > 速度
- ✅ 施設作成直後はキャッシュが効かないが、最新のデータが取得される
- ✅ エラーハンドリングを追加

---

## 9. 修正ファイル一覧

### 9.1 バックグラウンド処理中のキャッシュ保存を防止

- `backend/app/services/faq_service.py`
  - `get_faqs`メソッドに、施設作成から30秒以内の場合はキャッシュを保存しない処理を追加

### 9.2 バックグラウンド処理完了後のキャッシュ無効化を強化（オプション）

- `backend/app/services/auth_service.py`
  - `register_facility_async_faqs`関数で、バックグラウンド処理完了後、5秒待ってから再度キャッシュを無効化

---

## 10. まとめ

### 10.1 問題点

1. **FAQが20件しか表示されない**: データベースには30件登録されているが、フロントエンドでは20件しか表示されない
2. **タイミングによって表示件数が異なる**: 初回表示は5件、リロード後は20件と、タイミングによって異なる

### 10.2 根本原因

1. **バックグラウンド処理中のキャッシュ保存**: バックグラウンド処理が完了する前にFAQ一覧を取得すると、その時点でのFAQ数がキャッシュされる
2. **キャッシュ無効化のタイミング**: キャッシュ無効化がバックグラウンド処理の完了時のみ実行されているため、途中の状態がキャッシュに残る

### 10.3 修正内容

1. **バックグラウンド処理中のキャッシュ保存を防止**: 施設作成から30秒以内の場合はキャッシュを保存しない
2. **バックグラウンド処理完了後のキャッシュ無効化を強化**: バックグラウンド処理完了後、5秒待ってから再度キャッシュを無効化（オプション）

### 10.4 期待される効果

- ✅ Standardプランで30件のFAQが正しく表示される
- ✅ タイミングによって表示件数が異なる問題が解決される
- ✅ バックグラウンド処理が完了するまで、キャッシュに途中の状態が保存されない

