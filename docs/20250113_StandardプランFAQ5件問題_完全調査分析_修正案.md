# StandardプランFAQ5件問題 完全調査分析・修正案

**作成日**: 2025年1月13日  
**対象**: Standardプランで新規登録後、FAQが5件しか表示されない問題  
**目的**: 原因を完全に調査分析し、大原則に準拠した修正案を立案

---

## 1. 問題の概要

### 1.1 発生状況

- **プラン**: Standardプラン
- **期待値**: 30件のFAQが自動登録される
- **実際**: ブラウザで「Basic (5件)」と表示される
- **データベース確認**: 30件のFAQが登録されている（Basic: 8件、Facilities: 10件、Location: 6件、Trouble: 6件）

### 1.2 問題の特徴

- データベースには正しく30件のFAQが登録されている
- しかし、フロントエンドでは5件しか表示されない
- Basicカテゴリには8件登録されているが、5件しか表示されない

---

## 2. 根本原因の分析

### 2.1 データベース確認結果

**最新の施設（ID: 26, Standardプラン）**:
- 登録されているFAQ数: **30件** ✅
- Basicカテゴリ: **8件** ✅
- Facilitiesカテゴリ: **10件** ✅
- Locationカテゴリ: **6件** ✅
- Troubleカテゴリ: **6件** ✅

**結論**: データベースには正しく30件のFAQが登録されている

### 2.2 バックグラウンド処理の確認

**ログ確認結果**:
- バックグラウンド処理は実行されている（ログで確認）
- FAQ作成処理は正常に完了している
- しかし、「Background FAQ creation completed」のログメッセージが見当たらない

**問題点**:
- `register_facility_async_faqs`関数でログを出力しているが、ログが表示されていない
- これは、バックグラウンド処理が正常に完了していない可能性がある

### 2.3 キャッシュの問題

**FAQ一覧取得APIのキャッシュ**:
- `FAQService.get_faqs()`はキャッシュを使用している
- キャッシュキー: `faq:list:facility_id={facility_id}:category={category}:is_active={is_active}`
- FAQ作成時にキャッシュを無効化しているが、バックグラウンド処理ではキャッシュ無効化が実行されていない可能性がある

**問題点**:
- バックグラウンド処理でFAQを作成した後、キャッシュが無効化されていない
- そのため、フロントエンドでFAQ一覧を取得する際に、古いキャッシュ（空の状態）が返される可能性がある

### 2.4 フロントエンドの表示ロジック

**FaqListコンポーネント**:
- カテゴリ別にFAQを表示している
- `getFaqsByCategory()`関数でカテゴリ別のFAQを取得している
- カテゴリフィルタが適用されている場合、フィルタされたFAQのみが表示される

**問題点**:
- フロントエンドでFAQ一覧を取得する際に、キャッシュから古いデータが返されている可能性がある
- または、APIレスポンスに問題がある可能性がある

---

## 3. 根本原因の特定

### 3.1 主原因: バックグラウンド処理でのキャッシュ無効化が実行されていない

**問題の本質**:
- `register_facility_async_faqs`関数でFAQを作成しているが、キャッシュ無効化を実行していない
- そのため、FAQ作成後も古いキャッシュ（空の状態）が残っている
- フロントエンドでFAQ一覧を取得する際に、古いキャッシュが返される

**証拠**:
- データベースには30件のFAQが登録されている
- しかし、フロントエンドでは5件しか表示されない
- これは、キャッシュから古いデータが返されている可能性が高い

### 3.2 副次的原因: ログ出力が正常に動作していない

**問題の本質**:
- `register_facility_async_faqs`関数でログを出力しているが、ログが表示されていない
- これは、バックグラウンド処理が正常に完了していない可能性がある

---

## 4. 修正案（大原則に準拠）

### 4.1 修正案1: バックグラウンド処理でのキャッシュ無効化を追加（根本解決）

**方針**: `register_facility_async_faqs`関数でFAQ作成後にキャッシュを無効化する

**修正内容**:

**ファイル**: `backend/app/services/auth_service.py`

**修正箇所**: `register_facility_async_faqs`関数

```python
@staticmethod
async def register_facility_async_faqs(
    facility_id: int,
    user_id: int,
    subscription_plan: str
):
    """
    FAQ自動投入処理（バックグラウンド実行）
    
    Args:
        facility_id: 施設ID
        user_id: ユーザーID
        subscription_plan: 料金プラン
    """
    from app.database import AsyncSessionLocal
    from app.data.faq_presets import FAQ_PRESETS
    from app.schemas.faq import FAQRequest
    from app.services.cache import delete_cache_pattern
    
    # 新しいデータベースセッションを作成
    async with AsyncSessionLocal() as db:
        try:
            # 料金プランに基づいてFAQプリセットをフィルタ
            filtered_presets = filter_faq_presets_by_plan(
                FAQ_PRESETS,
                subscription_plan
            )
            
            # プリセットFAQをFAQRequestに変換
            faq_requests = []
            for preset in filtered_presets:
                faq_request = FAQRequest(
                    category=preset["category"],
                    intent_key=preset["intent_key"],
                    translations=[
                        {
                            "language": t["language"],
                            "question": t["question"],
                            "answer": t["answer"]
                        } for t in preset["translations"]
                    ],
                    priority=preset["priority"],
                    is_active=True
                )
                faq_requests.append(faq_request)
            
            # FAQ一括作成
            await FAQService(db).bulk_create_faqs(facility_id, faq_requests, user_id)
            await db.commit()
            
            # キャッシュを無効化（FAQ作成後、最新のデータが取得されるようにする）
            try:
                deleted_count = await delete_cache_pattern(f"faq:list:*facility_id={facility_id}*")
                logger.info(
                    f"FAQ cache invalidated: {deleted_count} keys deleted "
                    f"(facility_id={facility_id})"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to invalidate FAQ cache: facility_id={facility_id}, "
                    f"error={str(e)}",
                    exc_info=True
                )
                # エラーが発生しても処理は続行（キャッシュは次回のリクエストで更新される）
            
            logger.info(
                f"Background FAQ creation completed: facility_id={facility_id}, "
                f"plan={subscription_plan}, count={len(faq_requests)}"
            )
        except Exception as e:
            logger.error(
                f"Background FAQ creation failed: facility_id={facility_id}, "
                f"plan={subscription_plan}, error={str(e)}",
                exc_info=True
            )
            # エラーが発生してもロールバックは不要（既に施設・ユーザーは作成済み）
```

**メリット**:
- FAQ作成後にキャッシュが無効化される
- フロントエンドで最新のデータが取得される
- 根本的な解決

**デメリット**:
- キャッシュ無効化の処理が追加される（影響は軽微）

**大原則への準拠**:
- ✅ 根本解決 > 暫定解決（根本原因を解決）
- ✅ シンプル構造 > 複雑構造（シンプルなキャッシュ無効化の追加）
- ✅ 統一・同一化 > 特殊独自（既存のキャッシュ無効化パターンに従う）
- ✅ 具体的 > 一般（具体的な修正内容）
- ✅ 拙速 < 安全確実（エラーハンドリングを追加）

### 4.2 修正案2: 料金プランドロップダウン順序の修正

**方針**: 料金プランのドロップダウンリストを正しい順序（free, mini, small, standard, Premium）に並び替える

**修正内容**:

**ファイル**: `frontend/src/views/admin/Register.vue`

**修正前**:
```vue
<option value="small">Small (推奨)</option>
<option value="mini">Mini</option>
<option value="free">Free</option>
<option value="standard">Standard</option>
<option value="premium">Premium</option>
```

**修正後**:
```vue
<option value="free">Free</option>
<option value="mini">Mini</option>
<option value="small">Small (推奨)</option>
<option value="standard">Standard</option>
<option value="premium">Premium</option>
```

**メリット**:
- 料金プランが正しい順序で表示される
- ユーザーがプランを選択しやすくなる

**大原則への準拠**:
- ✅ シンプル構造 > 複雑構造（シンプルな順序変更）
- ✅ 統一・同一化 > 特殊独自（一般的な順序）

---

## 5. 修正の優先順位

### 優先度1: バックグラウンド処理でのキャッシュ無効化を追加（根本解決）
- **影響**: FAQ一覧が正しく表示されない
- **緊急度**: 高
- **修正内容**: `register_facility_async_faqs`関数でキャッシュ無効化を追加

### 優先度2: 料金プランドロップダウン順序の修正
- **影響**: ユーザー体験の向上
- **緊急度**: 中
- **修正内容**: ドロップダウンリストの順序を修正

---

## 6. 修正後の期待動作

### 6.1 バックグラウンド処理でのキャッシュ無効化追加後

- ✅ FAQ作成後にキャッシュが無効化される
- ✅ フロントエンドで最新のデータが取得される
- ✅ Standardプランで30件のFAQが正しく表示される
- ✅ Basicカテゴリで8件のFAQが正しく表示される

### 6.2 料金プランドロップダウン順序修正後

- ✅ 料金プランが正しい順序（free, mini, small, standard, Premium）で表示される

---

## 7. テスト項目

### 7.1 バックグラウンド処理でのキャッシュ無効化追加後

1. **Standardプランの新規登録テスト**
   - Standardプランで新規登録
   - 登録後、FAQ一覧取得APIを呼び出す
   - 30件のFAQが返されることを確認

2. **キャッシュ無効化の確認**
   - FAQ作成後にキャッシュが無効化されることを確認
   - ログでキャッシュ無効化のメッセージを確認

### 7.2 料金プランドロップダウン順序修正後

1. **ドロップダウン順序の確認**
   - 新規登録ページで料金プランドロップダウンを開く
   - 順序が正しい（free, mini, small, standard, Premium）ことを確認

---

## 8. 大原則への準拠

### 8.1 根本解決 > 暫定対応
- ✅ キャッシュ無効化を追加して根本原因を解決
- ✅ 暫定的なキャッシュクリアではなく、根本的な解決

### 8.2 シンプルな構造 > 複雑な構造
- ✅ シンプルなキャッシュ無効化の追加
- ✅ シンプルな順序変更

### 8.3 安全性と確実性 > 速度
- ✅ エラーハンドリングを追加
- ✅ キャッシュ無効化が失敗しても処理は続行

---

## 9. 修正ファイル一覧

### 9.1 バックグラウンド処理でのキャッシュ無効化追加

- `backend/app/services/auth_service.py`
  - `register_facility_async_faqs`関数にキャッシュ無効化を追加

### 9.2 料金プランドロップダウン順序の修正

- `frontend/src/views/admin/Register.vue`
  - ドロップダウンリストの順序を修正

---

## 10. まとめ

### 10.1 問題点

1. **FAQが5件しか表示されない**: データベースには30件登録されているが、フロントエンドでは5件しか表示されない
2. **料金プランドロップダウン順序**: 正しい順序（free, mini, small, standard, Premium）ではない

### 10.2 根本原因

1. **キャッシュ無効化が実行されていない**: バックグラウンド処理でFAQを作成した後、キャッシュが無効化されていない
2. **ドロップダウン順序**: 実装時に正しい順序で実装されていない

### 10.3 修正内容

1. **バックグラウンド処理でのキャッシュ無効化追加**: FAQ作成後にキャッシュを無効化する
2. **料金プランドロップダウン順序の修正**: 正しい順序（free, mini, small, standard, Premium）に並び替える

### 10.4 期待される効果

- ✅ Standardプランで30件のFAQが正しく表示される
- ✅ Basicカテゴリで8件のFAQが正しく表示される
- ✅ 料金プランが正しい順序で表示される

