# Phase 1 Week 3 ステップ15以降 実装準備

**作成日**: 2025年11月27日  
**フェーズ**: Phase 1 Week 3（フロントエンド）  
**対象ステップ**: ステップ15-20  
**目的**: ステップ15以降の実装準備と要件整理

---

## 現在の実装状況

### 完了済み（ステップ1-14）
- ✅ Vue.js プロジェクト構造完成
- ✅ Vue Router設定（admin.tsにルート定義済み）
- ✅ Pinia Store設定
- ✅ Axios設定
- ✅ PWA設定
- ✅ ダークモード設定
- ✅ 共通コンポーネント実装
- ✅ ゲスト側UI（言語選択、ウェルカム、チャット）
- ✅ セッション統合トークンUI
- ✅ ゲストレイアウト
- ✅ ログイン画面
- ✅ 管理画面レイアウト（AdminLayout.vue）

### 未実装（ステップ15-20）
- ⏳ ステップ15: ダッシュボードUI実装
- ⏳ ステップ16: FAQ管理UI実装
- ⏳ ステップ17: 夜間対応キューUI実装
- ⏳ ステップ18: QRコード発行UI実装
- ⏳ ステップ19: ルーティング統合・動作確認
- ⏳ ステップ20: エラーハンドリング・例外処理

---

## ステップ15: ダッシュボードUI実装

### 実装要件

#### 1. ファイル構成
```
frontend/src/
├── views/admin/
│   └── Dashboard.vue                    ⏳ 作成予定
└── components/admin/
    ├── StatsCard.vue                   ⏳ 作成予定
    ├── CategoryChart.vue               ⏳ 作成予定
    ├── ChatHistoryList.vue             ⏳ 作成予定
    ├── OvernightQueueList.vue          ⏳ 作成予定（v0.3新規）
    └── FeedbackStats.vue               ⏳ 作成予定（v0.3新規）
```

#### 2. Dashboard.vue 実装内容

**表示項目**:
1. **週次サマリー**
   - 総質問数（例: 127件）
   - 自動応答率（例: 88%）
   - カテゴリ別円グラフ（CategoryChartコンポーネント）
     - Basic: 35件
     - Facilities: 48件
     - Location: 25件
     - Trouble: 7件

2. **リアルタイムチャット履歴**（ChatHistoryListコンポーネント）
   - 最新10件の会話を表示
   - 表示項目: ゲスト言語、質問、AI回答、信頼度スコア、日時

3. **夜間対応キュー**（OvernightQueueListコンポーネント、v0.3新規）
   - 翌朝対応が必要な質問一覧
   - 表示項目: 質問内容、言語、日時、対応予定時刻

4. **ゲストフィードバック集計**（FeedbackStatsコンポーネント、v0.3新規）
   - 👍👎の比率
   - 低評価回答リスト（2回以上👎がついた回答）
   - 「FAQ改善提案」ボタン（モック、Week 4でAPI連携）

#### 3. モックデータ構造

```typescript
// 週次サマリー
interface WeeklySummary {
  total_questions: number
  auto_response_rate: number  // 0.0-1.0
  category_breakdown: {
    basic: number
    facilities: number
    location: number
    trouble: number
  }
  top_questions: Array<{
    question: string
    count: number
  }>
  unresolved_count: number
}

// リアルタイムチャット履歴
interface ChatHistory {
  session_id: string
  guest_language: string
  last_message: string
  ai_confidence: number  // 0.0-1.0
  created_at: string
}

// 夜間対応キュー
interface OvernightQueue {
  id: number
  guest_message: string
  language: string
  scheduled_notify_at: string
  created_at: string
}

// ゲストフィードバック統計
interface FeedbackStats {
  positive_count: number
  negative_count: number
  positive_rate: number  // 0.0-1.0
  low_rated_answers: Array<{
    message_id: number
    question: string
    answer: string
    negative_count: number
  }>
}
```

#### 4. コンポーネント詳細

**StatsCard.vue**
- 統計カードコンポーネント（再利用可能）
- Props: `title`, `value`, `icon`, `color`
- ダークモード対応

**CategoryChart.vue**
- カテゴリ別円グラフコンポーネント
- ライブラリ: Chart.js または vue-chartjs
- Props: `data` (category_breakdown)
- ダークモード対応

**ChatHistoryList.vue**
- チャット履歴リストコンポーネント
- Props: `conversations` (ChatHistory[])
- クリックで会話詳細表示（モック、Week 4で実装）

**OvernightQueueList.vue**（v0.3新規）
- 夜間対応キューリストコンポーネント
- Props: `queue` (OvernightQueue[])
- 「対応済み」マーク機能（モック、Week 4でAPI連携）

**FeedbackStats.vue**（v0.3新規）
- ゲストフィードバック統計コンポーネント
- Props: `stats` (FeedbackStats)
- 低評価回答の自動ハイライト
- 「FAQ改善提案」ボタン（モック、Week 4でAPI連携）

---

## ステップ16: FAQ管理UI実装

### 実装要件

#### 1. ファイル構成
```
frontend/src/
├── views/admin/
│   └── FaqManagement.vue               ⏳ 作成予定
└── components/admin/
    ├── FaqList.vue                     ⏳ 作成予定
    ├── FaqForm.vue                     ⏳ 作成予定
    ├── UnresolvedQuestionsList.vue     ⏳ 作成予定（v0.3新規）
    ├── FaqSuggestionCard.vue            ⏳ 作成予定（v0.3新規）
    └── FeedbackLinkedFaqs.vue          ⏳ 作成予定（v0.3新規）
```

#### 2. FaqManagement.vue 実装内容

**表示項目**:
1. **FAQ一覧**（FaqListコンポーネント）
   - カテゴリ別表示（Basic, Facilities, Location, Trouble）
   - 各FAQ: 質問文、回答文、優先度、編集・削除ボタン
   - 「新規FAQ追加」ボタン

2. **FAQ追加・編集フォーム**（FaqFormコンポーネント）
   - 質問文入力（200文字以内推奨）
   - 回答文入力（200文字以内推奨）
   - カテゴリ選択（basic, facilities, location, trouble）
   - 優先度設定（1-5）
   - 言語選択（MVPは英語のみ）

3. **未解決質問リスト**（UnresolvedQuestionsListコンポーネント、v0.3新規）
   - 未解決質問一覧表示
   - 表示項目: 日時、内容、言語、信頼度スコア
   - 「FAQ追加」ボタン（ワンクリック）

4. **FAQ自動学習UI**（FaqSuggestionCardコンポーネント、v0.3新規）
   - 未解決質問からFAQ提案を作成
   - 質問文自動入力
   - 回答文テンプレート自動生成（モック、Week 4でAPI連携）
   - カテゴリ自動推定（モック、Week 4でAPI連携）
   - スタッフが確認・編集可能

5. **ゲストフィードバック連動**（FeedbackLinkedFaqsコンポーネント、v0.3新規）
   - 👎評価が2回以上ついた回答の自動ハイライト
   - 「FAQ改善提案」ボタン（モック、Week 4でAPI連携）
   - 回答文修正案を自動生成（モック、Week 4でAPI連携）

#### 3. モックデータ構造

```typescript
// FAQ
interface FAQ {
  id: number
  category: 'basic' | 'facilities' | 'location' | 'trouble'
  language: string
  question: string
  answer: string
  priority: number  // 1-5
  is_active: boolean
  created_at: string
  updated_at: string
}

// 未解決質問
interface UnresolvedQuestion {
  id: number
  message_id: number
  question: string
  language: string
  confidence_score: number  // 0.0-1.0
  created_at: string
}

// FAQ提案
interface FaqSuggestion {
  id: number
  source_message_id: number
  suggested_question: string
  suggested_answer: string
  suggested_category: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}
```

#### 4. コンポーネント詳細

**FaqList.vue**
- FAQリストコンポーネント
- Props: `faqs` (FAQ[])
- カテゴリ別フィルタリング
- 編集・削除ボタン（モック、Week 4でAPI連携）

**FaqForm.vue**
- FAQ追加・編集フォームコンポーネント
- Props: `faq` (FAQ | null) - nullの場合は新規作成
- バリデーション（質問文・回答文200文字以内）
- カテゴリ選択ドロップダウン
- 優先度スライダー（1-5）

**UnresolvedQuestionsList.vue**（v0.3新規）
- 未解決質問リストコンポーネント
- Props: `questions` (UnresolvedQuestion[])
- 「FAQ追加」ボタンクリックでFaqSuggestionCardを表示

**FaqSuggestionCard.vue**（v0.3新規）
- FAQ追加提案カードコンポーネント
- Props: `suggestion` (FaqSuggestion)
- 質問文自動入力（編集可能）
- 回答文テンプレート自動生成（編集可能、モック）
- カテゴリ自動推定（編集可能、モック）
- 「承認」ボタン（モック、Week 4でAPI連携）
- 「却下」ボタン（モック、Week 4でAPI連携）

**FeedbackLinkedFaqs.vue**（v0.3新規）
- ゲストフィードバック連動FAQコンポーネント
- Props: `low_rated_faqs` (Array<{ message_id, question, answer, negative_count }>)
- 低評価回答の自動ハイライト
- 「FAQ改善提案」ボタン（モック、Week 4でAPI連携）

---

## ステップ17: 夜間対応キューUI実装

### 実装要件

#### 1. ファイル構成
```
frontend/src/
├── views/admin/
│   └── OvernightQueue.vue              ⏳ 作成予定
└── components/admin/
    └── ProcessButton.vue                ⏳ 作成予定
```

#### 2. OvernightQueue.vue 実装内容

**表示項目**:
1. **夜間対応キュー一覧**
   - 翌朝対応が必要な質問一覧表示（モックデータ）
   - 表示項目: 質問内容、言語、日時、対応予定時刻（翌朝8:00）
   - 「対応済み」マーク機能（モック、Week 4でAPI連携）

2. **手動実行ボタン**（ProcessButtonコンポーネント）
   - MVP期間中は手動実行
   - モック、Week 4でAPI連携

#### 3. モックデータ構造

```typescript
// 夜間対応キュー
interface OvernightQueue {
  id: number
  facility_id: number
  escalation_id: number
  guest_message: string
  language: string
  scheduled_notify_at: string  // 翌朝8:00
  notified_at: string | null
  resolved_at: string | null
  resolved_by: number | null
  created_at: string
}
```

---

## ステップ18: QRコード発行UI実装

### 実装要件

#### 1. ファイル構成
```
frontend/src/
├── views/admin/
│   └── QRCodeGenerator.vue              ⏳ 作成予定
└── components/admin/
    └── QRCodeForm.vue                    ⏳ 作成予定
```

#### 2. QRCodeGenerator.vue 実装内容

**表示項目**:
1. **QRコード発行フォーム**（QRCodeFormコンポーネント）
   - 設置場所選択（entrance, room, kitchen, lounge, custom）
   - **セッション統合トークン埋め込みオプション**（v0.3新規）
   - カスタム設置場所名入力（custom選択時）

2. **QRコードプレビュー**
   - 生成されたQRコードのプレビュー表示（モック、Week 4でAPI連携）

3. **ダウンロードボタン**
   - PDF/PNG/SVG形式ダウンロード（モック、Week 4でAPI連携）
   - A4印刷用サイズ

#### 3. モックデータ構造

```typescript
// QRコード生成リクエスト
interface QRCodeRequest {
  facility_id: number
  location: 'entrance' | 'room' | 'kitchen' | 'lounge' | 'custom'
  custom_location_name?: string
  include_session_token: boolean  // v0.3新規
}

// QRコード生成レスポンス
interface QRCodeResponse {
  qr_code_url: string
  download_urls: {
    pdf: string
    png: string
    svg: string
  }
}
```

---

## ステップ19: ルーティング統合・動作確認

### 実装要件

#### 1. ルーティング確認
- `frontend/src/router/admin.ts`のルート定義確認
- 各ページのルーティング動作確認
- 認証ガード動作確認

#### 2. 動作確認項目
- [ ] 各ページが正常に表示される
- [ ] ルーティングが正しく動作する
- [ ] 認証ガードが正しく動作する
- [ ] レスポンシブデザインが正しく動作する
- [ ] ダークモードが正しく動作する
- [ ] PWAが正しく動作する

---

## ステップ20: エラーハンドリング・例外処理

### 実装要件

#### 1. ファイル構成
```
frontend/src/
├── utils/
│   └── errorHandler.ts                  ⏳ 作成予定
└── views/
    ├── Error404.vue                    ⏳ 作成予定
    └── Error500.vue                     ⏳ 作成予定
```

#### 2. 実装内容

**errorHandler.ts**
- エラーハンドリング関数
- エラーメッセージ表示
- APIエラーの統一処理

**Error404.vue**
- 404ページ
- ダークモード対応

**Error500.vue**
- 500ページ
- ダークモード対応

**api/axios.ts更新**
- レスポンスインターセプターでエラーハンドリング強化
- 統一エラーレスポンス形式の処理

---

## 実装時の注意事項

### 1. モックデータ
- Week 3ではモックデータを使用
- API連携はWeek 4で実装
- モックデータは`frontend/src/utils/mockData.ts`に定義（作成予定）

### 2. ダークモード対応
- 全コンポーネントでダークモード対応
- Tailwind CSSの`dark:`クラスを使用

### 3. レスポンシブデザイン
- モバイルファーストで実装
- 375px-428pxのスマホ画面に対応

### 4. TypeScript型定義
- 全データ構造にTypeScript型定義を追加
- `frontend/src/types/`に型定義ファイルを作成（必要に応じて）

### 5. コンポーネント設計
- 再利用可能なコンポーネント設計
- Props/Emitsの型定義
- コンポーネントの責務分離

---

## 参考資料

### 主要ドキュメント
- **要約定義書**: `docs/Summary/yadopera-v03-summary.md`
- **アーキテクチャ設計書**: `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`
- **Phase 1 Week 3ステップ計画**: `docs/Phase1/Phase1_Week3_ステップ計画.md`
- **Phase 0引き継ぎ書**: `docs/Phase0/Phase0_引き継ぎ書.md`

### 実装参考セクション
- アーキテクチャ設計書 4. Vue.js ページ遷移図（管理側）
- アーキテクチャ設計書 8.2 RESTful API エンドポイント一覧
- アーキテクチャ設計書 8.3 APIリクエスト・レスポンス詳細

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025-11-27  
**Status**: 実装準備完了、指示待ち

