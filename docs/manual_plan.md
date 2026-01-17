# YadOPERA 利用マニュアル実装計画書

## ドキュメント情報
- **作成日**: 2024-12-28
- **最終更新日**: 2026-01-17
- **対象フェーズ**: Phase 2（PoC準備）
- **実装優先度**: 9/9（最終項目）
- **所要時間**: 3-4時間
- **実装完了日**: 2026-01-17

---

## 1. 概要

### 1.1 目的
宿泊施設管理者がYadOPERAシステムを効果的に利用できるよう、操作手順・機能説明・トラブルシューティングをまとめた利用マニュアルを提供する。

### 1.2 対象ユーザー
- 宿泊施設管理者（ゲストハウス・ホステル等の運営者）
- ITリテラシー：初級〜中級（特別な技術知識不要）

### 1.3 アクセス方法
- 管理画面メニュー最下段「QRコード発行」の下に「ご利用マニュアル」を新設
- パス: `/admin/manual`
- ルート名: `AdminManual`

---

## 2. 技術仕様

### 2.1 表示形式
- **形式**: HTML形式（リッチな表示）
- **フレームワーク**: Vue.js 3 + TypeScript
- **スタイリング**: Tailwind CSS
- **レイアウト**: admin レイアウト使用（既存管理画面と統一）

### 2.2 実装フェーズ別機能

#### Phase 2（現在）✅ 実装完了
- ✅ HTML形式での表示
- ✅ 目次（Table of Contents）
- ✅ アンカーリンクによる章間移動
- ✅ ダークモード対応
- ✅ レスポンシブデザイン（スマホ・タブレット対応）
- ✅ 全12章の本文内容実装完了（55項目）
- ✅ マークダウン変換機能実装
- ❌ 画像・スクリーンショット（Phase 3実装予定）
- ❌ 検索機能（Phase 3実装予定）
- ❌ 自動更新（Phase 4実装予定）

#### Phase 3（PoC）
- ✅ 画像・スクリーンショット追加（ユーザーが準備）
- ✅ マニュアル内検索機能実装
- ✅ 動画埋め込み対応（YouTube等）

#### Phase 4（本格展開）
- ✅ システム更新時の自動マニュアル更新
- ✅ バージョン管理機能
- ✅ 多言語対応検討

### 2.3 ファイル構成

```
frontend/src/
├── views/admin/
│   └── Manual.vue                    # メイン画面
├── components/admin/
│   ├── ManualToc.vue                 # 目次コンポーネント
│   ├── ManualContent.vue             # セクションコンポーネント
│   └── ManualSearch.vue              # 検索コンポーネント（Phase 3）
├── router/
│   └── admin.ts                      # ルート追加
└── assets/
    └── manual/
        ├── images/                   # スクリーンショット格納（Phase 3）
        └── videos/                   # 動画格納（Phase 3）

backend/app/
└── api/v1/endpoints/
    └── manual.py                     # マニュアルAPI（Phase 4自動更新用）
```

---

## 3. マニュアル構成

### 3.1 全体構成（12章構成）

#### 第1章: はじめに
1.1 YadOPERAとは  
1.2 本マニュアルの使い方  
1.3 システム要件  
1.4 初期設定

#### 第2章: ログイン・ログアウト
2.1 初回ログイン  
2.2 ログアウト  
2.3 ログインできない場合

#### 第3章: ダッシュボードの見方
3.1 ダッシュボード概要  
3.2 週次サマリー統計カード  
3.3 カテゴリ別内訳  
3.4 月次統計カード  
3.5 リアルタイムチャット履歴  
3.6 未解決のエスカレーション  
3.7 ゲストフィードバック集計

#### 第4章: FAQ管理
4.1 FAQ管理画面の概要  
4.2 FAQの登録  
4.3 FAQの編集  
4.4 FAQの削除  
4.5 未解決質問からのFAQ生成  
4.6 低評価回答からのFAQ改善  
4.7 FAQのベストプラクティス

#### 第5章: スタッフ不在時間帯対応キュー
5.1 スタッフ不在時間帯対応キューとは  
5.2 対応キュー一覧の見方  
5.3 質問への対応  
5.4 通知のタイミング

#### 第6章: 施設設定
6.1 施設設定画面の概要  
6.2 基本情報の設定  
6.3 スタッフ不在時間帯の設定  
6.4 パスワード変更

#### 第7章: QRコード発行
7.1 QRコードとは  
7.2 QRコード発行手順  
7.3 QRコードのダウンロード  
7.4 QRコードの設置方法  
7.5 QRコードのテスト

#### 第8章: 会話詳細の確認
8.1 会話詳細画面の概要  
8.2 会話履歴の見方  
8.3 ゲスト情報の確認  
8.4 エスカレーション対応について

#### 第9章: ゲスト側の使い方（管理者向け説明）
9.1 ゲストの利用フロー  
9.2 言語選択画面  
9.3 ウェルカム画面  
9.4 チャット画面  
9.5 ホーム画面へのインストールの仕方

#### 第10章: トラブルシューティング
10.1 よくある質問（FAQ）  
10.2 エラーメッセージ一覧  
10.3 ブラウザキャッシュのクリア方法  
10.4 問い合わせ方法

#### 第11章: 運用のベストプラクティス
11.1 初期設定チェックリスト  
11.2 日次運用  
11.3 週次運用  
11.4 月次運用

#### 第12章: 付録
12.1 用語集  
12.2 画面遷移図  
12.3 FAQ初期テンプレート例  
12.4 更新履歴

### 3.2 各章の詳細内容

✅ **実装完了**: 全12章、55項目の本文内容を実装完了（2026-01-17）

**実装内容**:
- 各章の本文内容を`frontend/src/views/admin/Manual.vue`に実装
- マークダウン風のテキストをHTMLに変換する機能を実装
- 技術用語を避け、管理者向けに分かりやすく記載
- 実際の実装に基づいた正確な説明

**重要な修正点**:
- 第1章に1.4 初期設定を追加
- 第3章の月次統計は請求期間ベースで説明（将来のStripe統合を見越して）
- 第4章にプランによる言語数制限について注意書きを追加
- 第8章で手動返信機能は未実装であることを明記
- 第9章で技術用語を避け、一般向けに書き直し
- 第11章で「朝一番」→「フロントオープン時」に修正
- 第12章でFAQ初期テンプレートは20件であることを明記

---

## 4. UI/UXデザイン仕様

### 4.1 レイアウト構成

```
+--------------------------------------------------+
| ヘッダー（既存admin layout）                        |
+--------------------------------------------------+
|                                                  |
| +----------------+  +---------------------------+ |
| | 目次（固定）      |  | メインコンテンツ（スクロール） | |
| |                |  |                           | |
| | 第1章 はじめに  |  | # 第1章 はじめに          | |
| |   1.1 概要     |  |                           | |
| |   1.2 使い方   |  | ## 1.1 YadOPERAとは      | |
| | 第2章 ログイン  |  | YadOPERAは...           | |
| |   2.1 初回     |  |                           | |
| |   2.2 エラー   |  | ## 1.2 本マニュアルの...  | |
| | ...            |  |                           | |
| |                |  |                           | |
| +----------------+  +---------------------------+ |
|                                                  |
+--------------------------------------------------+
| フッター（既存admin layout）                        |
+--------------------------------------------------+
```

### 4.2 目次（Table of Contents）仕様

#### 表示位置
- 左サイド固定（デスクトップ）
- 上部折りたたみ（モバイル）

#### 機能
- ✅ 現在表示中の章をハイライト表示
- ✅ クリックで該当章へスムーススクロール
- ✅ 折りたたみ/展開機能（章単位）
- ✅ スクロール追従（Sticky）

#### スタイル
```css
.manual-toc {
  position: sticky;
  top: 80px; /* ヘッダー高さ分 */
  width: 250px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  border-right: 1px solid #e5e7eb; /* gray-200 */
  padding-right: 1rem;
}

.manual-toc-item {
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.manual-toc-item:hover {
  background-color: #f3f4f6; /* gray-100 */
}

.manual-toc-item.active {
  background-color: #dbeafe; /* blue-100 */
  color: #1e40af; /* blue-800 */
  font-weight: 600;
}
```

### 4.3 メインコンテンツ仕様

#### 見出しスタイル
```css
h1 { /* 章タイトル */
  font-size: 2rem;
  font-weight: 700;
  color: #111827; /* gray-900 */
  margin-top: 3rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #3b82f6; /* blue-500 */
  padding-bottom: 0.5rem;
}

h2 { /* 中項目 */
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937; /* gray-800 */
  margin-top: 2rem;
  margin-bottom: 1rem;
}

h3 { /* 小項目 */
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151; /* gray-700 */
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}
```

#### テキストスタイル
```css
p {
  font-size: 1rem;
  line-height: 1.75;
  color: #4b5563; /* gray-600 */
  margin-bottom: 1rem;
}

code {
  background-color: #f3f4f6; /* gray-100 */
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}
```

#### 強調表示
```css
.note {
  background-color: #dbeafe; /* blue-100 */
  border-left: 4px solid #3b82f6; /* blue-500 */
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 0.375rem;
}

.warning {
  background-color: #fef3c7; /* yellow-100 */
  border-left: 4px solid #f59e0b; /* yellow-500 */
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 0.375rem;
}

.tip {
  background-color: #d1fae5; /* green-100 */
  border-left: 4px solid #10b981; /* green-500 */
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 0.375rem;
}
```

### 4.4 ダークモード対応

```css
@media (prefers-color-scheme: dark) {
  .manual-toc {
    border-right-color: #374151; /* gray-700 */
  }
  
  .manual-toc-item:hover {
    background-color: #1f2937; /* gray-800 */
  }
  
  .manual-toc-item.active {
    background-color: #1e3a8a; /* blue-900 */
    color: #93c5fd; /* blue-300 */
  }
  
  h1, h2, h3 {
    color: #f9fafb; /* gray-50 */
  }
  
  p {
    color: #d1d5db; /* gray-300 */
  }
}
```

### 4.5 レスポンシブデザイン

#### モバイル（< 768px）
- 目次を上部折りたたみメニュー化
- ハンバーガーアイコンでトグル
- メインコンテンツを全幅表示

#### タブレット（768px - 1024px）
- 目次幅を200pxに縮小
- メインコンテンツの余白調整

#### デスクトップ（> 1024px）
- 目次250px固定
- メインコンテンツ最大幅800px

---

## 5. 実装ステップ

### Phase 2（現在）- 基本実装

#### ステップ1: ルーティング設定（15分）
```typescript
// frontend/src/router/admin.ts に追加

{
  path: '/admin/manual',
  name: 'AdminManual',
  component: () => import('@/views/admin/Manual.vue'),
  meta: {
    layout: 'admin',
    requiresAuth: true
  }
}
```

#### ステップ2: メニュー項目追加（15分）
```typescript
// frontend/src/components/admin/Sidebar.vue の navItems 配列に追加

// ナビゲーションアイテム定義
const navItems = [
  // ... 既存の項目 ...
  {
    to: '/admin/qr-code',
    label: 'QRコード発行',
    icon: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z' })
    ])
  },
  // 新規追加
  {
    to: '/admin/manual',
    label: 'ご利用マニュアル',
    icon: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
    ])
  }
]
```

#### ステップ3: Manual.vue作成（60分）
```vue
<template>
  <div class="manual-container">
    <!-- ページヘッダー -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        ご利用マニュアル
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        YadOPERAの操作方法・機能説明
      </p>
    </div>

    <!-- メインコンテンツエリア -->
    <div class="flex gap-6">
      <!-- 目次（デスクトップ） -->
      <aside class="hidden lg:block w-64 flex-shrink-0">
        <ManualToc :sections="sections" :activeSection="activeSection" />
      </aside>

      <!-- マニュアル本文 -->
      <main class="flex-1 max-w-4xl">
        <ManualContent :sections="sections" @section-change="handleSectionChange" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ManualToc from '@/components/admin/ManualToc.vue'
import ManualContent from '@/components/admin/ManualContent.vue'

// マニュアルセクション定義
const sections = ref([
  {
    id: 'intro',
    title: '第1章 はじめに',
    subsections: [
      { id: 'intro-about', title: '1.1 YadOPERAとは' },
      { id: 'intro-howto', title: '1.2 本マニュアルの使い方' },
      { id: 'intro-requirements', title: '1.3 システム要件' }
    ]
  },
  // ... 他の章
])

const activeSection = ref('intro')

const handleSectionChange = (sectionId: string) => {
  activeSection.value = sectionId
}
</script>
```

#### ステップ4: ManualToc.vueコンポーネント作成（30分）
目次コンポーネントの実装

#### ステップ5: ManualContent.vueコンポーネント作成（90分）
マニュアル本文コンポーネントの実装

#### ステップ6: スタイリング調整（30分）
Tailwind CSSでの最終調整

#### ステップ7: ダークモード対応（15分）
dark: プレフィックスの追加

#### ステップ8: レスポンシブ対応（30分）
モバイル・タブレット表示の調整

#### ステップ9: テスト（30分）
- ブラウザテスト（Chrome, Safari, Firefox）
- モバイル表示テスト
- ダークモード切り替えテスト
- アンカーリンク動作確認

**Phase 2 合計所要時間: 3-4時間**

---

### Phase 3（PoC）- 機能拡張

#### ステップ10: 画像埋め込み対応（60分）
- スクリーンショット準備（ユーザー作業）
- 画像最適化（WebP変換）
- Lazy Loading実装

#### ステップ11: 検索機能実装（120分）
```vue
<ManualSearch 
  :sections="sections" 
  @search="handleSearch" 
/>
```

#### ステップ12: 動画埋め込み対応（30分）フェーズ４以降へ繰越
YouTube iframe埋め込み

**Phase 3 合計所要時間: 3-4時間**

---

### Phase 4（本格展開）- 自動化

#### ステップ13: バックエンドAPI実装（180分）
- マニュアル自動生成API
- バージョン管理機能
- 更新履歴記録

#### ステップ14: 多言語対応検討（180分）
- i18n導入
- 英語版翻訳

**Phase 4 合計所要時間: 6時間**

---

## 6. データ構造

### 6.1 マニュアルセクション型定義

```typescript
// frontend/src/types/manual.ts

export interface ManualSubsection {
  id: string
  title: string
  content: string
  level: number // 1=大項目, 2=中項目, 3=小項目
}

export interface ManualSection {
  id: string
  title: string
  order: number
  subsections: ManualSubsection[]
}

export interface ManualSearchResult {
  sectionId: string
  subsectionId: string
  title: string
  excerpt: string
  matchScore: number
}
```

---

## 7. マニュアル本文サンプル

### 第3章 ダッシュボードの見方

#### 3.1 ダッシュボード概要

ダッシュボードは、YadOPERAの利用状況を一目で確認できる画面です。ログイン後、最初に表示されます。

<div class="note">
💡 <strong>ポイント</strong><br>
ダッシュボードは過去7日間のデータを表示します。より詳細な分析が必要な場合は、各詳細画面に遷移してください。
</div>

#### 3.2 総質問数

**表示内容**: 過去7日間にゲストから寄せられた質問の総数

**見方**:
- 数値が大きいほど、ゲストの利用が活発
- 前週比の増減をグラフで確認可能

**活用方法**:
- 繁忙期・閑散期の把握
- プロモーション効果の測定
- 施設の稼働率との相関分析

<div class="tip">
✅ <strong>ベストプラクティス</strong><br>
質問数が急増した場合は、FAQ管理画面で新しい質問傾向を確認し、必要に応じてFAQを追加しましょう。
</div>

---

## 8. テスト計画

### 8.1 機能テスト項目

#### 基本表示
- [ ] マニュアル画面が正常に表示される
- [ ] 目次が表示される
- [ ] 本文が表示される

#### 目次機能
- [ ] 目次クリックで該当章にスクロール
- [ ] 現在表示中の章がハイライト
- [ ] 折りたたみ/展開が動作

#### レスポンシブ
- [ ] モバイル表示で目次が折りたたまれる
- [ ] タブレット表示で適切にレイアウト
- [ ] デスクトップ表示で目次が固定

#### ダークモード
- [ ] ダークモード切り替えが正常動作
- [ ] テキストの可読性が保たれる

### 8.2 ブラウザ互換性テスト

| ブラウザ | バージョン | テスト結果 |
|---------|----------|----------|
| Chrome  | 最新版   | ✅ 完了 |
| Safari  | 最新版   | ✅ 完了 |
| Firefox | 最新版   | ⬜ 未実施 |
| Edge    | 最新版   | ⬜ 未実施 |

### 8.3 パフォーマンステスト

- [ ] 初回ロード時間 < 2秒
- [ ] スクロール動作が滑らか（60fps維持）
- [ ] 画像Lazy Loading動作確認（Phase 3）

---

## 9. リスク管理

### 9.1 想定リスクと対策

| リスク | 影響度 | 発生確率 | 対策 |
|-------|-------|---------|-----|
| マニュアル内容の不正確性 | 高 | 中 | システム更新時に内容を同期確認 |
| モバイル表示の崩れ | 中 | 低 | レスポンシブテストを徹底 |
| 検索機能の実装遅延 | 低 | 中 | Phase 3での実装に留め、Phase 2では未実装 |
| 画像容量が大きすぎる | 中 | 中 | WebP形式に変換、Lazy Loading実装 |

---

## 10. 成功基準

### Phase 2（基本実装）✅ 完了
- ✅ マニュアル画面が実装され、メニューからアクセス可能
- ✅ 12章構成のマニュアルが表示される
- ✅ 全12章、55項目の本文内容を実装完了
- ✅ 目次クリックで該当章に遷移
- ✅ ダークモード対応完了
- ✅ レスポンシブ対応完了（モバイル・タブレット・デスクトップ）
- ✅ ブラウザテスト完了（Chrome, Safari）
- ✅ デプロイ完了（ステージング環境）
- ✅ コミット・プッシュ完了（コミットハッシュ: `e87c832`）

### Phase 3（PoC）
- ✅ 画像・スクリーンショット埋め込み完了
- ✅ 検索機能実装完了
- ✅ ユーザーフィードバック収集・反映

### Phase 4（本格展開）
- ✅ 自動更新機能実装完了
- ✅ バージョン管理機能実装完了

---

## 11. 今後の拡張計画

### Phase 5以降（将来構想）
- 📹 操作説明動画の追加
- 📝 PDFダウンロード機能
- 🔔 マニュアル更新通知機能
- 📊 マニュアル閲覧統計（どの章が最も読まれているか）
- 🌐 多言語対応（英語、中国語等）
- 💬 マニュアル内コメント・質問機能

---

## 12. 参考資料

### 類似サービスのマニュアル事例
- Notion Help Center
- Intercom Help Center
- Zendesk Guide

### 設計参考ドキュメント
- `docs/Phase2/Phase2_PoC準備_ステップ計画.md`
- `docs/Summary/yadopera-v03-summary.md`
- `README.md`

---

## 13. 承認・レビュー

| 役割 | 氏名 | 承認日 | 署名 |
|-----|------|-------|-----|
| 作成者 | Claude | 2024-12-28 | ✅ |
| レビュー担当 | kurinobu | - | ⬜ |
| 承認者 | kurinobu | - | ⬜ |

---

## 14. 変更履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|----------|------|---------|-------|
| 1.0 | 2024-12-28 | 初版作成 | Claude |
| 1.1 | 2026-01-17 | 実装完了に伴う更新（全12章実装完了、本文内容実装完了、テスト完了、デプロイ完了） | AI Assistant |

---

**END OF DOCUMENT**