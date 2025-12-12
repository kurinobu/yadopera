# Phase 1: ステップ9 会話詳細画面実装 計画

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: 会話詳細画面の実装（ステップ9）  
**状態**: ⏳ **計画作成完了、実装待ち**

---

## 1. 実施概要

### 1.1 目的

**目的**: カテゴリ確認方法の質問への回答として、会話詳細画面を実装する

**背景**:
- ユーザーからの質問: 「過去7日間のメッセージで使用されたFAQのカテゴリ集計」の各カテゴリを確認する術はありますか？
- 現在、直接的な確認方法は実装されていない
- 会話詳細画面を実装することで、各メッセージの`matched_faq_ids`からFAQのカテゴリを確認できるようになる

### 1.2 優先度

**優先度**: ⚠️ **中優先度**（Phase 1完了の必須条件ではない）

**理由**:
- Phase 1 Week 4は既に完了しているが、この機能は未実装のまま
- カテゴリ確認方法の質問への回答として必要
- Phase 1完了の必須条件ではないが、ユーザビリティ向上のために実装する

### 1.3 所要時間

**予定工数**: 2-3時間

---

## 2. 実装内容

### 2.1 必要な実装

1. **会話詳細画面の作成**
   - `frontend/src/views/admin/ConversationDetail.vue`を作成
   - 会話の全メッセージを表示
   - 各メッセージの`matched_faq_ids`からFAQのカテゴリを表示

2. **ルーティングの追加**
   - `frontend/src/router/admin.ts`に会話詳細画面のルートを追加
   - パス: `/admin/conversations/:session_id`

3. **`handleConversationClick`の実装**
   - `frontend/src/views/admin/Dashboard.vue`の`handleConversationClick`を修正
   - 会話詳細画面への遷移を実装

### 2.2 実装詳細

#### 2.2.1 会話詳細画面の作成

**ファイル**: `frontend/src/views/admin/ConversationDetail.vue`

**表示項目**:
1. **会話情報**
   - セッションID
   - ゲストの言語
   - 開始時刻
   - 最終活動時刻

2. **メッセージ一覧**
   - 各メッセージの内容
   - メッセージのロール（user/assistant）
   - 作成日時
   - AI信頼度（assistantのみ）
   - 使用したFAQ（`matched_faq_ids`からFAQのカテゴリを表示）

3. **FAQカテゴリの表示**
   - 各メッセージで使用されたFAQのカテゴリを表示
   - カテゴリ別に色分けして表示

#### 2.2.2 ルーティングの追加

**ファイル**: `frontend/src/router/admin.ts`

**追加するルート**:
```typescript
{
  path: '/conversations/:session_id',
  name: 'ConversationDetail',
  component: () => import('@/views/admin/ConversationDetail.vue'),
  meta: { requiresAuth: true }
}
```

#### 2.2.3 `handleConversationClick`の実装

**ファイル**: `frontend/src/views/admin/Dashboard.vue`

**修正内容**:
```typescript
const handleConversationClick = (conversation: ChatHistory) => {
  router.push({
    name: 'ConversationDetail',
    params: { session_id: conversation.session_id }
  })
}
```

---

## 3. 大原則の適用

### 3.1 大原則への準拠

- ✅ **根本解決 > 暫定解決**: 会話詳細画面を実装することで、カテゴリ確認方法の質問に根本的に回答する
- ✅ **シンプル構造 > 複雑構造**: シンプルな会話詳細画面を実装する
- ✅ **統一・同一化 > 特殊独自**: 既存のパターンに従い、統一された実装を維持する
- ✅ **具体的 > 一般**: 具体的な実装内容を明確にする
- ✅ **拙速 < 安全確実**: 十分な検証を行い、安全に実装する

---

## 4. 実施手順

### 4.1 ステップ1: 会話詳細画面の作成（1-1.5時間）

1. **`ConversationDetail.vue`を作成**
   - 会話情報を表示
   - メッセージ一覧を表示
   - FAQカテゴリを表示

2. **API呼び出しの実装**
   - `GET /api/v1/chat/history/{session_id}`を呼び出す
   - 会話履歴を取得

3. **FAQカテゴリの取得**
   - `matched_faq_ids`からFAQを取得
   - FAQのカテゴリを表示

### 4.2 ステップ2: ルーティングの追加（10分）

1. **`admin.ts`にルートを追加**
   - 会話詳細画面のルートを追加
   - 認証ガードを設定

### 4.3 ステップ3: `handleConversationClick`の実装（10分）

1. **`Dashboard.vue`の`handleConversationClick`を修正**
   - 会話詳細画面への遷移を実装

### 4.4 ステップ4: 動作確認（30分）

1. **ブラウザで動作確認**
   - ダッシュボードでチャットをタップ
   - 会話詳細画面に遷移することを確認
   - メッセージ一覧が表示されることを確認
   - FAQカテゴリが表示されることを確認

---

## 5. 確認項目

### 5.1 実装確認

- [ ] 会話詳細画面が作成される
- [ ] ルーティングが追加される
- [ ] `handleConversationClick`が実装される
- [ ] ブラウザの開発者ツールでエラーがない

### 5.2 動作確認

- [ ] ダッシュボードでチャットをタップすると会話詳細画面に遷移する
- [ ] 会話の全メッセージが表示される
- [ ] 各メッセージの`matched_faq_ids`からFAQのカテゴリが表示される
- [ ] カテゴリ別に色分けして表示される

---

## 6. 完了条件

- ✅ 会話詳細画面が作成される
- ✅ ルーティングが追加される
- ✅ `handleConversationClick`が実装される
- ✅ ブラウザで動作確認が完了する
- ✅ カテゴリ確認方法の質問に回答できるようになる

---

## 7. 参考資料

### 7.1 関連ドキュメント

- **質問回答レポート**: `docs/Phase1/Phase1_ダッシュボードカテゴリ確認方法_質問回答レポート.md`
- **質問回答完全版**: `docs/Phase1/Phase1_質問回答_完全版_20251204.md`
- **アーキテクチャ設計書**: `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`

### 7.2 関連API

- **会話履歴取得API**: `GET /api/v1/chat/history/{session_id}`
- **FAQ取得API**: `GET /api/v1/faqs`

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: ⏳ **計画作成完了、実装待ち**


