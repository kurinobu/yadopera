# 固定フッターまわりの表示言語をゲスト選択言語にする機能 — 調査分析と修正計画案

**作成日**: 2026年2月22日  
**準拠**: リードゲットオプション実装計画書・大原則（要約定義書 v0.3.18）  
**目的**: 固定フッター・クーポンエントリーモーダルの表示を、ゲストが選択した言語（`?lang=ja` 等）に合わせて切り替える。

---

## 1. 調査結果

### 1.1 現状の言語の扱い（ゲスト側）

| 項目 | 内容 |
|------|------|
| **言語の決定** | URL クエリ `lang`（例: `/f/{slug}/welcome?lang=ja`）。ゲストは言語選択画面で言語を選ぶと `query: { lang: language.code }` で Welcome に遷移し、以降も同じ `lang` が引き継がれる。 |
| **参照方法** | 各画面で `const language = computed(() => (route.query.lang as string) \|\| 'en')` としている（Welcome.vue, Chat.vue）。共通 composable や store の「ゲスト言語」はない。 |
| **文言の出し分け** | vue-i18n は未使用。`language.value === 'ja' ? '日本語' : 'English'` のようなインライン分岐が Chat.vue 等で使われている。 |
| **対応言語** | `frontend/src/utils/constants.ts` の `SUPPORTED_LANGUAGES` で定義: ja, en, zh-TW, fr, es, de, ko, th, vi。施設の `available_languages` でフィルタされ、言語選択に表示される。 |

### 1.2 固定フッター・モーダルの現状

| コンポーネント | 言語対応 | 備考 |
|----------------|----------|------|
| **GuestLayout.vue** | なし | `route` は参照しているが、子に `lang` を渡していない。固定フッターはここでレンダリング。 |
| **GuestOptionFooter.vue** | なし | ボタン文言「🎁 オトクなクーポン」が日本語でハードコード。`lang` 未受け取り。 |
| **CouponEntryModal.vue** | なし | タイトル・説明・ラベル・ボタン・プレースホルダ・成功/エラーメッセージがすべて日本語でハードコード。`lang` 未受け取り。 |

### 1.3 既存パターンとの整合

- **統一・同一化**: ゲスト画面では「`route.query.lang` をデフォルト `'en'` で取得し、文言を言語別に切り替える」パターンが既に使われている。固定フッターまわりも同じルールに揃える。
- **シンプル構造**: 固定フッターは 1 コンポーネントに集約したまま、内部で「渡された `lang` に応じた文言」を使う形にすればよい。
- **具体的 > 一般**: 多言語キーは「どこに何を定義するか」を計画書で明示する（後述の「文言定義」）。

---

## 2. 大原則との対応

| 原則 | 本機能での適用 |
|------|----------------|
| 根本解決 > 暫定解決 | ゲストの選択言語（`route.query.lang`）を正しく参照し、フッター・モーダルで一貫してその言語で表示する。暫定的な「常に日本語」にしない。 |
| シンプル構造 > 複雑構造 | 文言は 1 か所（共有の文言マップまたは定数）にまとめ、フッターとモーダルから参照する。各コンポーネントに散らさない。 |
| 統一・同一化 > 特殊独自 | 既存の「`route.query.lang` + 言語別文言」パターンに合わせる。vue-i18n 等の新規導入は行わない。 |
| 具体的 > 一般 | 文言キー一覧と、対応する言語コード（ja, en, zh-TW 等）、フォールバック（未定義時は en）を計画書で明示する。 |
| 拙速 < 安全確実 | 実装後は Docker 環境でブラウザテストし、`?lang=ja` / `?lang=en` 等で表示が切り替わることを確認する。 |
| Docker環境必須 | 修正・テストは docker-compose で実行する。 |

---

## 3. 修正計画案

### 3.1 方針

1. **言語の受け渡し**  
   - `GuestLayout` で `route.query.lang` を取得（デフォルト `'en'`）。  
   - `GuestOptionFooter` に `lang` を props で渡す。  
   - `CouponEntryModal` に `lang` を props で渡す（Footer が Modal を利用しているため、Footer が同じ `lang` を渡す）。

2. **文言の定義**  
   - 固定フッター・クーポンモーダル専用の文言を、**1 つのモジュール**に集約する（例: `frontend/src/utils/couponCopy.ts` または `frontend/src/constants/couponCopy.ts`）。  
   - キーは「ボタン」「モーダルタイトル」「説明文」「ラベル」「ボタン」「エラー」等を明示。  
   - 言語コードごとにオブジェクトで保持し、未定義の言語は `en` にフォールバックする。

3. **対応言語**  
   - まずは **ja / en** を明示的に定義し、他言語（zh-TW, fr, es, de, ko, th, vi）は未定義時は **en** を使う（既存の Chat 等と同様のフォールバック）。  
   - 必要に応じて後から他言語を追加する。

### 3.2 対象ファイルと変更内容

| ファイル | 変更内容 |
|----------|----------|
| **新規: `frontend/src/utils/couponCopy.ts`**（または `constants/couponCopy.ts`） | 言語コードをキーとした文言オブジェクト。`getCouponCopy(lang: string)` のような関数を export し、未対応 `lang` のときは `en` を返す。 |
| **GuestLayout.vue** | `route.query.lang \|\| 'en'` を算出し、`GuestOptionFooter` に `:lang="guestLang"` で渡す。 |
| **GuestOptionFooter.vue** | props に `lang: string` を追加。`couponCopy` から「クーポンボタン」文言を取得し表示。`CouponEntryModal` に `:lang="lang"` を渡す。 |
| **CouponEntryModal.vue** | props に `lang: string` を追加。タイトル・説明・ラベル・ボタン・プレースホルダ・成功/エラーメッセージをすべて `couponCopy` から取得して表示。 |

### 3.3 文言キー一覧（案）

以下を `couponCopy` の 1 言語オブジェクトのキーとして定義する。

| キー | 用途 | 例（ja） |
|------|------|----------|
| `couponButton` | フッターのクーポンボタン | オトクなクーポン |
| `modalTitle` | モーダル見出し | オトクなクーポンを受け取る |
| `successTitle` | 送信完了メッセージ | クーポンを送信しました。 |
| `successDescription` | 送信完了の説明 | ご登録のメールアドレスにクーポンを送信しました。ご確認ください。 |
| `closeButton` | 閉じるボタン | 閉じる |
| `introText` | モーダル冒頭の説明 | 次回のご予約でご利用いただけるクーポンをお送りします。… |
| `privacyNote` | 利用目的・プライバシー注意 | 利用目的：次回予約のご案内のため。… |
| `labelName` | お名前ラベル | お名前（任意） |
| `labelEmail` | メールアドレスラベル | メールアドレス |
| `placeholderName` | お名前プレースホルダ | 山田 太郎 |
| `placeholderEmail` | メールアドレスプレースホルダ | example@email.com |
| `cancelButton` | キャンセルボタン | キャンセル |
| `submitButton` | 送信ボタン | クーポンを受け取る |
| `submittingButton` | 送信中ボタン | 送信中... |
| `errorSendFailed` | 送信失敗時のメッセージ | 送信に失敗しました。しばらくしてから再度お試しください。 |

英語（en）は上記と同キーで英文を定義。他言語を追加する場合は同じキーでオブジェクトを増やす。

### 3.4 実装順序（案）

1. **文言モジュールの追加**  
   - `couponCopy.ts` を新規作成し、`ja` / `en` のオブジェクトと `getCouponCopy(lang)` を実装。未対応は `en` にフォールバック。
2. **GuestLayout**  
   - `guestLang` を算出し、`GuestOptionFooter` に `:lang="guestLang"` を渡す。
3. **GuestOptionFooter**  
   - props に `lang` を追加。ボタン文言を `getCouponCopy(lang).couponButton` で表示。`CouponEntryModal` に `:lang="lang"` を渡す。
4. **CouponEntryModal**  
   - props に `lang` を追加。全表示文言を `getCouponCopy(lang)` のキーで差し替え（成功時・エラー時のメッセージも同様）。
5. **動作確認**  
   - Docker で起動し、`?lang=ja` と `?lang=en` で固定フッター・モーダルの表示が切り替わることを確認。必要なら zh-TW 等を追加。

### 3.5 注意点

- **言語選択画面（/f/:facilityId）**  
   - この画面ではまだ `lang` が URL にないため、フッターが出る場合はデフォルト `en` とするか、または言語選択画面ではフッターを出さない仕様のままでもよい（現状、フッターは Welcome/Chat で主に表示される想定）。
- **API・メール**  
   - 本件は「表示言語」のみ。リード登録 API やクーポン送付メールの言語は変更しない（従来どおり日本語で送る等、別仕様のままとする）。

---

## 4. まとめ

- **原因**: 固定フッターとクーポンモーダルが `route.query.lang` を参照しておらず、文言が日本語でハードコードされている。
- **方針**: 既存の「`route.query.lang` + 言語別文言」に合わせ、Layout → Footer → Modal へ `lang` を渡し、文言を 1 モジュール（`couponCopy`）で管理する。
- **範囲**: 新規 `couponCopy.ts`、`GuestLayout.vue`、`GuestOptionFooter.vue`、`CouponEntryModal.vue` の 4 ファイル。まず ja/en を明示し、他は en にフォールバックする形で大原則に準拠した修正が可能。

実施する場合は、上記順序でバックアップを取得したうえで実装し、Docker 環境でブラウザテストを行うことを推奨する。
