# FAQ登録数カウント方法修正 - スクリーンショット分析・問題特定

**作成日時**: 2025年12月23日  
**目的**: スクリーンショットから発見された問題の特定と原因分析

---

## 🔍 発見された問題

### 問題1: 言語コードと質問・回答の内容が一致しない

**症状**:
- FAQ ID 14: `language='en'`（英語）と表示されているが、質問と回答は日本語
  - 質問: 「国際電話できる電話はありますか？」
  - 回答: 「当施設にはありません。」

**データベース確認結果**:
```sql
SELECT f.id, f.category, ft.language, ft.question, ft.answer 
FROM faqs f 
JOIN faq_translations ft ON f.id = ft.faq_id 
WHERE f.id = 14;

-- 結果:
-- id | category | language | question | answer
-- 14 | basic    | en       | 国際電話できる電話はありますか？ | 当施設にはありません。
```

**根本原因**:
- データベースに保存されている言語コード（`language='en'`）と、実際の質問・回答の言語（日本語）が一致していない
- これは既存データの移行時またはテストデータ作成時に発生したデータ不整合

### 問題2: 複数言語の翻訳が1つのFAQエントリの下に表示されていない

**症状**:
- スクリーンショットでは、1つのFAQエントリの下に1つの翻訳のみが表示されている
- FAQ ID 22には2つの翻訳（en, ja）があるはずだが、1つしか表示されていない

**期待される表示**:
```
FAQ ID 22:
  英語
  Q: Do you have WiFi?
  A: Yes, we have free WiFi.
  
  日本語
  Q: WiFiはありますか？
  A: はい、無料WiFiをご利用いただけます。
```

**実際の表示**:
- 1つの翻訳のみが表示されている（言語が1つしか表示されていない）

**データベース確認結果**:
```sql
SELECT f.id, f.category, COUNT(ft.id) as translation_count, 
       STRING_AGG(ft.language || ':' || LEFT(ft.question, 30), ' | ' ORDER BY ft.language) as translations 
FROM faqs f 
LEFT JOIN faq_translations ft ON f.id = ft.faq_id 
WHERE f.id = 22 
GROUP BY f.id, f.category;

-- 結果:
-- id | category  | translation_count | translations
-- 22 | facilities | 2                 | en:Do you have WiFi? | ja:WiFiはありますか？
```

**Redisキャッシュ確認結果**:
- Redisキャッシュには正しいデータが含まれている（FAQ ID 22に2つの翻訳が含まれている）
- キャッシュのJSON構造は正しい

**フロントエンド実装確認結果**:
- `FaqList.vue`の実装は正しい（`v-for="translation in faq.translations"`でループしている）
- `getLanguageLabel()`関数も正しく実装されている

---

## 🔍 原因分析

### 原因1: データベースの言語コード不整合

**問題のFAQ**:
- FAQ ID 14: `language='en'`だが質問・回答は日本語
- FAQ ID 6: `language='en'`だが質問・回答は日本語
- FAQ ID 7: `language='en'`だが質問・回答は日本語

**影響範囲**:
- これらのFAQは、言語ラベルが「英語」と表示されるが、実際の質問・回答は日本語
- ユーザーにとって混乱を招く

### 原因2: フロントエンドの表示ロジックの問題（可能性）

**仮説**:
1. APIレスポンスが正しく取得されていない
2. フロントエンドで`faq.translations`が正しく処理されていない
3. Vueのリアクティビティの問題（`faq.translations`が配列として認識されていない）

**確認が必要な項目**:
- ブラウザの開発者ツールでAPIレスポンスを確認
- Vue DevToolsで`faqs`データの構造を確認
- コンソールで`faq.translations`の内容を確認

---

## 📋 修正が必要な項目

### 修正1: データベースの言語コード修正（高優先度）

**対象FAQ**:
- FAQ ID 14: `language='en'` → `language='ja'`に修正
- FAQ ID 6: `language='en'` → `language='ja'`に修正
- FAQ ID 7: `language='en'` → `language='ja'`に修正

**修正方法**:
```sql
-- FAQ ID 14の言語コードを修正
UPDATE faq_translations 
SET language = 'ja' 
WHERE faq_id = 14 AND language = 'en' AND question LIKE '%国際電話%';

-- FAQ ID 6の言語コードを修正
UPDATE faq_translations 
SET language = 'ja' 
WHERE faq_id = 6 AND language = 'en' AND question LIKE '%レンタルバイク%';

-- FAQ ID 7の言語コードを修正
UPDATE faq_translations 
SET language = 'ja' 
WHERE faq_id = 7 AND language = 'en' AND question LIKE '%アイロン%';
```

### 修正2: フロントエンドの表示ロジック確認（中優先度）

**確認項目**:
1. APIレスポンスに`translations`が含まれているか
2. `faq.translations`が配列として正しく処理されているか
3. Vueのリアクティビティが正しく動作しているか

**デバッグ方法**:
```javascript
// FaqList.vueにデバッグコードを追加
console.log('FAQ data:', faq)
console.log('Translations:', faq.translations)
console.log('Translations length:', faq.translations?.length)
```

### 修正3: テストデータ作成スクリプトの修正（低優先度）

**問題**:
- `create_test_data.py`や`create_staging_test_data.py`で、言語コードと質問・回答の言語が一致していないデータが作成されている可能性

**修正方法**:
- テストデータ作成時に、質問・回答の言語を自動検出して正しい言語コードを設定する
- または、テストデータ作成時に明示的に言語コードを指定する

---

## 🎯 期待される表示

### 正しい表示例（FAQ ID 22）

```
[Basic] 優先度: 3

英語
Q: Do you have WiFi?
A: Yes, we have free WiFi.

日本語
Q: WiFiはありますか？
A: はい、無料WiFiをご利用いただけます。

[編集] [削除]
```

### 現在の表示（問題あり）

```
[Basic] 優先度: 3

英語
Q: 国際電話できる電話はありますか？
A: 当施設にはありません。

[編集] [削除]
```

**問題点**:
1. 言語ラベルが「英語」だが、質問・回答は日本語
2. 複数言語の翻訳が表示されていない（1つの翻訳のみ）

---

## 📝 次のステップ

1. **データベースの言語コード修正**
   - FAQ ID 14, 6, 7の言語コードを`'ja'`に修正
   - 修正後、データベースの整合性を確認

2. **フロントエンドの表示ロジック確認**
   - ブラウザの開発者ツールでAPIレスポンスを確認
   - Vue DevToolsでデータ構造を確認
   - 必要に応じてデバッグコードを追加

3. **キャッシュのクリア**
   - Redisキャッシュをクリアして、最新のデータを取得

4. **再テスト**
   - 修正後、ブラウザでFAQ一覧を再確認
   - FAQ ID 22に2つの翻訳が表示されることを確認

---

**注意**: 指示があるまで修正しないでください。調査・分析・提案のみを行います。

