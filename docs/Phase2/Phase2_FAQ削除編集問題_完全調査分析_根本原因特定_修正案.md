# Phase 2: FAQ削除・編集問題 完全調査分析・根本原因特定・修正案

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: FAQ削除・編集の問題の完全調査分析と根本原因特定、修正案  
**状態**: 🔍 **完全調査分析完了 → 根本原因特定完了 → 修正案提示**

---

## 1. 問題の説明と評価

### 1.1 報告された症状

**問題1: FAQ削除が反映されない**
- 「Q: ご近所ツアーなどのイベントはありますか？」を削除
- コンソールに「削除しました」と表示されるが、ブラウザには表示されたまま
- そのFAQを編集しようとすると「保存しようとしたFAQが見つかりませんでした。既に削除されている可能性があります。」というエラー

**問題2: FAQ編集が反映されない**
- 「Q: レンタルバイクはあります」を編集
- 何もエラーもないが、編集が反映されない

**コンソールエラー**:
```
FAQ「ご近所ツアーなどのイベントはありますか？」を削除しました
PUT http://localhost:8000/api/v1/admin/faqs/5 400 (Bad Request)
Failed to save FAQ: {code: 'BAD_REQUEST', message: 'FAQ not found: faq_id=5', details: {…}}
```

### 1.2 問題の評価

**重要度**: 🔴 **最優先（Critical）**

**影響範囲**:
- FAQ削除・編集が正常に動作しない
- ユーザー体験が低下する
- Phase 2の作業が停止している

**緊急度**: **即座に対応が必要**

---

## 2. ログの完全分析

### 2.1 バックエンドログの確認

**確認したログ**:
```bash
docker-compose logs backend --tail 100 | grep -i "faq\|delete\|update"
```

**発見された情報**:
1. **FAQ ID=5の削除は成功している**
   ```
   DELETE FROM faqs WHERE faqs.id = $1::INTEGER
   DELETE /api/v1/admin/faqs/5 HTTP/1.1" 204 No Content
   ```

2. **削除後にFAQ一覧を取得している**
   ```
   GET /api/v1/admin/faqs HTTP/1.1" 200 OK
   ```

3. **FAQ ID=5の編集を試みている**
   ```
   PUT /api/v1/admin/faqs/5 HTTP/1.1" 400 Bad Request
   ```

4. **FAQ ID=4の編集は成功している**
   ```
   UPDATE faqs SET answer=$1::VARCHAR, updated_at=now() WHERE faqs.id = $2::INTEGER
   PUT /api/v1/admin/faqs/4 HTTP/1.1" 200 OK
   ```

### 2.2 データベースの確認結果

**確認結果**:
```sql
SELECT id, facility_id, question, is_active FROM faqs ORDER BY id;
```

**結果**:
```
 id | facility_id |           question           | is_active 
----+-------------+------------------------------+-----------
  4 |           2 | レンタルバイクはありますか？ | t
(1 row)
```

**重要な発見**:
- ✅ データベースにはFAQ ID=4のみが存在する
- ❌ FAQ ID=5は削除されている（正常）
- ❌ FAQ ID=3は存在しない

### 2.3 APIレスポンスの確認

**確認結果**:
```json
{
    "faqs": [
        {
            "id": 5,
            "question": "ご近所ツアーなどのイベントはありますか？",
            ...
        },
        {
            "id": 4,
            "question": "レンタルバイクはありますか？",
            ...
        },
        {
            "id": 3,
            "question": "フロントはいつ開いてますか？",
            ...
        }
    ],
    "total": 3
}
```

**重要な発見**:
- ⚠️ APIレスポンスにはFAQ ID=3, 4, 5が含まれている
- ⚠️ しかし、データベースにはFAQ ID=4のみが存在する
- ⚠️ **これはキャッシュの問題である可能性が高い**

### 2.4 Redisキャッシュの確認

**確認結果**:
```bash
docker-compose exec redis redis-cli KEYS "faq:list:*"
```

**結果**:
```
faq:list:category=None:facility_id=2:is_active=None
```

**キャッシュの内容**:
```json
[
  {"id": 5, "question": "ご近所ツアーなどのイベントはありますか？", ...},
  {"id": 4, "question": "レンタルバイクはありますか？", ...},
  {"id": 3, "question": "フロントはいつ開いてますか？", ...}
]
```

**重要な発見**:
- ⚠️ キャッシュに古いデータ（FAQ ID=3, 4, 5）が残っている
- ⚠️ データベースにはFAQ ID=4のみが存在する
- ⚠️ **キャッシュが無効化されていない**

---

## 3. 根本原因の特定

### 3.1 根本原因1: キャッシュキーのパターンマッチが機能していない

**原因**:
- キャッシュキーは`faq:list:category=None:facility_id=2:is_active=None`という形式
- しかし、`delete_cache_pattern`で使用しているパターンは`faq:list:facility_id={facility_id}*`
- パターン`faq:list:facility_id=2*`は`faq:list:category=None:facility_id=2:is_active=None`にマッチしない

**詳細**:
- `cache_key`関数は`sorted(kwargs.items())`でソートしているため、キーの順序は：
  - `category=None`
  - `facility_id=2`
  - `is_active=None`
- パターン`faq:list:facility_id=2*`は、`facility_id=2`が最初に来ることを期待しているが、実際のキーでは`category=None`が最初に来る
- そのため、パターンマッチが機能せず、キャッシュが無効化されない

**確認**:
```bash
# パターンマッチのテスト
docker-compose exec redis redis-cli --scan --pattern "faq:list:facility_id=2*"
# 結果: 何も返されない（マッチしない）

docker-compose exec redis redis-cli --scan --pattern "faq:list:*facility_id=2*"
# 結果: faq:list:category=None:facility_id=2:is_active=None（マッチする）
```

**影響**:
- FAQ削除・編集・作成時にキャッシュが無効化されない
- 古いデータがキャッシュに残り続ける
- フロントエンドで古いデータが表示される

### 3.2 根本原因2: 編集時のキャッシュ無効化が不十分

**原因**:
- FAQ編集時にキャッシュを無効化しているが、パターンマッチが機能していない
- そのため、編集後も古いデータがキャッシュに残る

**影響**:
- 編集結果が反映されない
- フロントエンドで古いデータが表示される

---

## 4. 修正案（大原則に準拠）

### 4.1 修正案1: キャッシュキーのパターンを修正（根本解決）

**方針**: パターンを`faq:list:*facility_id={facility_id}*`に変更し、ワイルドカードを使用する

**修正内容**:

**ファイル**: `backend/app/services/faq_service.py`

**修正前**:
```python:162:163:backend/app/services/faq_service.py
        # キャッシュを無効化
        await delete_cache_pattern(f"faq:list:facility_id={facility_id}*")
```

**修正後**:
```python:162:163:backend/app/services/faq_service.py
        # キャッシュを無効化（ワイルドカードを使用して、すべてのパラメータ組み合わせを無効化）
        await delete_cache_pattern(f"faq:list:*facility_id={facility_id}*")
```

**同様に、他の箇所も修正**:
- `create_faq`メソッド（163行目）
- `update_faq`メソッド（266行目）
- `delete_faq`メソッド（315行目、322行目）

**メリット**:
- キャッシュキーのパターンマッチが機能する
- すべてのパラメータ組み合わせのキャッシュを無効化できる
- 根本的な解決

**デメリット**:
- パターンマッチが少し遅くなる可能性がある（影響は軽微）

**大原則への準拠**:
- ✅ 根本解決 > 暫定解決（根本原因を解決）
- ✅ シンプル構造 > 複雑構造（シンプルなパターン変更）
- ✅ 統一・同一化 > 特殊独自（既存のパターンに従う）
- ✅ 具体的 > 一般（具体的なパターン変更）
- ✅ 拙速 < 安全確実（バックアップ作成、テスト実施）

**推奨**: ✅ **この修正案を採用**

---

### 4.2 修正案2: キャッシュキーの生成方法を変更（根本解決）

**方針**: `cache_key`関数で`facility_id`を最初に配置する

**修正内容**:

**ファイル**: `backend/app/core/cache.py`

**修正前**:
```python:136:138:backend/app/core/cache.py
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_parts.append(":".join(f"{k}={v}" for k, v in sorted_kwargs))
```

**修正後**:
```python:136:145:backend/app/core/cache.py
    if kwargs:
        # facility_idを最初に配置（キャッシュ無効化のパターンマッチを容易にするため）
        sorted_kwargs = sorted(kwargs.items())
        facility_id_kwargs = [(k, v) for k, v in sorted_kwargs if k == 'facility_id']
        other_kwargs = [(k, v) for k, v in sorted_kwargs if k != 'facility_id']
        ordered_kwargs = facility_id_kwargs + other_kwargs
        key_parts.append(":".join(f"{k}={v}" for k, v in ordered_kwargs))
```

**メリット**:
- キャッシュキーの形式が統一される
- パターンマッチが容易になる

**デメリット**:
- 既存のキャッシュキーと互換性がなくなる（既存のキャッシュが無効になる）
- 実装が複雑になる

**大原則への準拠**:
- ⚠️ 統一・同一化 > 特殊独自（既存のキャッシュキーと互換性がない）
- ⚠️ シンプル構造 > 複雑構造（実装が複雑になる）

**推奨**: ⚠️ **この修正案は採用しない（修正案1の方がシンプルで効果的）**

---

### 4.3 修正案3: すべてのFAQキャッシュを無効化（根本解決）

**方針**: パターンを`faq:list:*`に変更し、すべてのFAQキャッシュを無効化する

**修正内容**:

**ファイル**: `backend/app/services/faq_service.py`

**修正前**:
```python:162:163:backend/app/services/faq_service.py
        # キャッシュを無効化
        await delete_cache_pattern(f"faq:list:facility_id={facility_id}*")
```

**修正後**:
```python:162:163:backend/app/services/faq_service.py
        # キャッシュを無効化（すべてのFAQキャッシュを無効化）
        await delete_cache_pattern(f"faq:list:*")
```

**メリット**:
- 確実にすべてのキャッシュを無効化できる
- パターンマッチの問題を回避できる

**デメリット**:
- 他の施設のキャッシュも無効化される（マルチテナント環境では問題になる可能性がある）
- パフォーマンスへの影響がある

**大原則への準拠**:
- ⚠️ 統一・同一化 > 特殊独自（他の施設のキャッシュも無効化される）

**推奨**: ⚠️ **この修正案は採用しない（マルチテナント環境では問題になる）**

---

### 4.4 修正案4: フロントエンドで強制的にキャッシュを回避（補助的修正）

**方針**: FAQ一覧取得時にキャッシュを回避するパラメータを追加する

**修正内容**:

**ファイル**: `frontend/src/views/admin/FaqManagement.vue`

**修正前**:
```typescript:150:162:frontend/src/views/admin/FaqManagement.vue
const fetchFaqs = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await faqApi.getFaqs()
    faqs.value = data
  } catch (err: any) {
    console.error('Failed to fetch FAQs:', err)
    error.value = err.response?.data?.detail || 'FAQ一覧の取得に失敗しました'
  } finally {
    loading.value = false
  }
}
```

**修正後**:
```typescript:150:162:frontend/src/views/admin/FaqManagement.vue
const fetchFaqs = async () => {
  try {
    loading.value = true
    error.value = null
    // キャッシュを回避するため、タイムスタンプを追加
    const timestamp = Date.now()
    const data = await faqApi.getFaqs(undefined, undefined, timestamp)
    faqs.value = data
  } catch (err: any) {
    console.error('Failed to fetch FAQs:', err)
    error.value = err.response?.data?.detail || 'FAQ一覧の取得に失敗しました'
  } finally {
    loading.value = false
  }
}
```

**注意**: この修正案は、バックエンドAPIも変更する必要があるため、実装が複雑になる

**推奨**: ⚠️ **この修正案は採用しない（実装が複雑になる）**

---

## 5. 推奨される修正方針

### 5.1 最優先修正

**修正案1: キャッシュキーのパターンを修正**（根本解決）

**理由**:
- キャッシュキーのパターンマッチが機能していない根本原因を解決
- シンプルで効果的な修正
- 大原則に完全準拠

**実施内容**:
1. `create_faq`メソッドのパターンを修正
2. `update_faq`メソッドのパターンを修正
3. `delete_faq`メソッドのパターンを修正（2箇所）

---

## 6. 修正実施計画

### 6.1 修正の優先順位

1. **最優先**: 修正案1（キャッシュキーのパターンを修正）
   - キャッシュの問題を根本的に解決

### 6.2 修正実施手順

#### ステップ1: 修正案1の実施

1. **バックアップ作成**
   - `backend/app/services/faq_service.py.backup_YYYYMMDD_HHMMSS`

2. **パターンの修正**
   - `create_faq`メソッド: `faq:list:facility_id={facility_id}*` → `faq:list:*facility_id={facility_id}*`
   - `update_faq`メソッド: `faq:list:facility_id={facility_id}*` → `faq:list:*facility_id={facility_id}*`
   - `delete_faq`メソッド: `faq:list:facility_id={facility_id}*` → `faq:list:*facility_id={facility_id}*`（2箇所）

3. **動作確認**
   - FAQ削除後にキャッシュが無効化されることを確認
   - FAQ一覧が最新の状態になることを確認

### 6.3 修正後の動作確認

1. **FAQ削除のテスト**
   - FAQ削除後にFAQ一覧が更新されることを確認
   - 削除されたFAQが一覧から消えることを確認

2. **FAQ編集のテスト**
   - FAQ編集後にFAQ一覧が更新されることを確認
   - 編集内容が反映されることを確認

3. **キャッシュの確認**
   - FAQ削除後にキャッシュが無効化されることを確認
   - FAQ一覧が最新の状態になることを確認

---

## 7. まとめ

### 7.1 根本原因の特定

1. **キャッシュキーのパターンマッチが機能していない**
   - キャッシュキーは`faq:list:category=None:facility_id=2:is_active=None`という形式
   - パターン`faq:list:facility_id=2*`は`faq:list:category=None:facility_id=2:is_active=None`にマッチしない
   - そのため、キャッシュが無効化されない

2. **編集時のキャッシュ無効化が不十分**
   - パターンマッチが機能していないため、編集後も古いデータがキャッシュに残る

### 7.2 修正方針

1. **修正案1: キャッシュキーのパターンを修正**（根本解決）
   - パターンを`faq:list:*facility_id={facility_id}*`に変更
   - ワイルドカードを使用して、すべてのパラメータ組み合わせを無効化

### 7.3 期待される結果

- ✅ キャッシュキーのパターンマッチが機能する
- ✅ FAQ削除・編集・作成時にキャッシュが無効化される
- ✅ FAQ一覧が最新の状態になる
- ✅ 編集結果が反映される

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ✅ **完全調査分析完了 → 根本原因特定完了 → 修正案提示完了**


