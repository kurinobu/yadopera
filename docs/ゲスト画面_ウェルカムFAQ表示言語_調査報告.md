# ゲスト画面 — ウェルカム「よくある質問」表示言語の調査報告

**作成日**: 2026年3月11日  
**対象**: 「FAQを多言語登録すれば、ゲストが選択した言語のFAQが表示されるか」の確認  
**結論**: **表示される。** ただし (1) 施設がその言語の翻訳を登録していること、(2) 見出し「よくある質問 / Frequently Asked Questions」は現状で言語切り替え対象外。

---

## 1. 調査結果サマリ

| 項目 | 結果 |
|------|------|
| **FAQ本文（3件の質問テキスト）** | ゲストの選択言語で表示される。API が `language` パラメータを受け取り、その言語の翻訳を返している。 |
| **表示の条件** | 施設が当該言語の FAQ 翻訳を DB（`faq_translations`）に登録していること。未登録の言語はバックエンドで **英語（en）にフォールバック** する。 |
| **セクション見出し** | 「よくある質問 / Frequently Asked Questions」は **TopQuestions.vue に固定** で、選択言語に応じた切り替えはしていない。 |

---

## 2. 根拠（コード上の流れ）

### 2.1 フロントエンド

- **Welcome.vue**（65行目）  
  - `language = route.query.lang`（未指定時は `'en'`）。
- **Welcome.vue**（85行目）  
  - `facilityApi.getFacility(slug, location.value, language.value)` で **選択言語を API に渡している**。
- **facility.ts**（16–22行目）  
  - `getFacility(slug, location?, language?)` で `language` をクエリ `params.language` として送信。
- **TopQuestions.vue**（14–16行目）  
  - 表示しているのは API から受け取った `question.question`（および answer）のみ。  
  - 見出し「よくある質問 / Frequently Asked Questions」は 4 行目で固定表示。

### 2.2 バックエンド

- **facility.py**（17–21行目）  
  - `GET /facility/{slug}?language=...` で `language` を取得（省略時は `"en"`）。
- **facility_service.py**（44–47行目）  
  - `get_facility_public_info(db, slug, language="en")` に `language` を渡している。
- **facility_service.py**（98–136行目）  
  - 施設の FAQ を優先度・作成日で上位3件取得。  
  - 各 FAQ について **選択言語の翻訳を優先**（119–128行目）:  
    1. `t.language == language` の翻訳を使用  
    2. なければ `t.language == "en"`  
    3. それもなければ `faq.translations[0]`  
  - その結果を `top_questions` として返却。

したがって、**API は「ゲストの選択言語」に合わせた FAQ 本文を返す実装になっており、フロントもそのまま表示している。**

---

## 3. スクショで「3件とも英語」だった理由として考えられること

1. **URL が `?lang=en` だった**  
   - 英語を指定しているため、API も英語の FAQ を返し、表示は英語になる。
2. **施設の FAQ にその言語の翻訳がない**  
   - 例: ゲストが zh-CN を選択していても、該当施設の TOP3 の FAQ に zh-CN の `faq_translations` が無い場合、バックエンドのフォールバックで **en** が選ばれ、英語で表示される。

どちらの場合も「選択言語で返す」仕様どおりの動作。**多言語で登録されていれば、その言語で表示される**。

---

## 4. 補足：見出しの多言語化（別課題）

- 「よくある質問 / Frequently Asked Questions」および「よくある質問はありません」は、`TopQuestions.vue` に日本語・英語で固定されている。
- ゲストの選択言語に合わせて見出しも切り替える場合は、  
  - 選択言語用のコピー（例: `couponCopy.ts` と同様の仕組み）を用意し、  
  - `TopQuestions` に `lang` を渡して見出し文言を切り替える対応が必要。  
  本調査の「FAQ本文が選択言語で表示されるか」とは別の改善項目。

---

## 5. 結論

- **FAQを多言語登録すれば、ゲストが選択した言語のFAQが表示される。**  
  - フロントは `route.query.lang` を API に渡しており、バックエンドはその `language` で `faq_translations` を選び、`top_questions` を返している。
- 表示が英語になるのは、(1) `lang=en` で開いている、(2) その施設の TOP3 FAQ に選択言語の翻訳が無く、en にフォールバックしている、のいずれか（または両方）で説明できる。
- 見出し「よくある質問 / Frequently Asked Questions」は現状、選択言語に依存せず固定表示。多言語化する場合は上記のとおり別対応が必要。

**指示があるまで修正は行わない。**
