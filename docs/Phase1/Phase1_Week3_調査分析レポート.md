# Phase 1 Week 3 調査分析レポート

**作成日**: 2025年11月27日  
**対象**: Phase 1 Week 3（フロントエンド）実装前調査分析  
**判断基準**: 要約定義書 v0.3.3 および アーキテクチャ設計書 v0.3

---

## 1. 調査サマリー

### 調査目的

Phase 1 Week 3で実装するフロントエンド（Vue.js 3）について、以下を調査・分析する：

1. 実装範囲の明確化
2. 技術的依存関係の確認
3. 実装上の課題・リスクの特定
4. 実装順序の最適化

### 調査結果サマリー

| カテゴリ | 状況 | 詳細 |
|---------|------|------|
| 実装範囲 | ✅ **明確** | 要約定義書・アーキテクチャ設計書で詳細化済み |
| 技術的依存関係 | ✅ **確認済み** | Week 1-2でバックエンドAPI実装完了、Week 3でフロントエンド実装 |
| 実装上の課題 | ⚠️ **軽微** | PWA設定、ダークモード実装、セッション管理 |
| 実装順序 | ✅ **最適化済み** | 基盤→ゲスト側→管理画面の順序 |

---

## 2. 実装範囲の明確化

### 2.1 Week 3で実装する機能

#### ゲスト側機能

1. **言語選択画面**
   - 英語のみ（MVP）
   - レスポンシブデザイン対応

2. **ウェルカム画面**
   - 施設情報表示
   - よくある質問TOP3表示
   - フリー入力フォーム
   - 緊急連絡先表示

3. **AI対話インターフェース（チャット形式）**
   - PWA対応
   - ダークモード対応
   - 固定フッター（メッセージ入力）
   - セッション管理（Cookie保存）
   - **セッション統合トークン表示・入力UI**（v0.3新規）
   - **ゲストフィードバックUI（👍👎）**（v0.3新規）

4. **セッション統合トークン機能**（v0.3新規）
   - 4桁英数字トークン表示（画面上部）
   - トークン入力UI（別デバイス統合用）
   - 会話履歴統合表示

#### 管理画面機能

1. **認証システム**
   - ログイン画面
   - JWT認証（localStorage保存）
   - パスワードリセット機能（Phase 2で実装予定、Week 3では準備のみ）

2. **ダッシュボード**
   - 更新方式: REST API + ポーリング（手動更新）
   - リアルタイムチャット履歴（最新10件）
   - 週次サマリー（総質問数、カテゴリ別円グラフ、TOP5、未解決数、自動応答率）
   - **夜間対応キュー**: 翌朝対応が必要な質問一覧（v0.3新規）
   - **ゲストフィードバック集計**: 👍👎の比率、低評価回答リスト（v0.3新規）

3. **FAQ管理（MVP強化版）**
   - 初期テンプレート20-30件提供
   - **FAQ自動学習UI（ワンクリック追加）**（v0.3新規）
     - 未解決質問リスト表示
     - 「FAQ追加」ボタン（ワンクリック）
     - 質問文自動入力
     - 回答文テンプレート自動生成（GPT-4o mini）
     - カテゴリ自動推定
     - スタッフが確認・編集
     - 保存時に埋め込みベクトル自動生成
   - **ゲストフィードバック連動**（v0.3新規）
     - 👎評価が2回以上ついた回答を自動ハイライト
     - 「FAQ改善提案」ボタンで回答文修正案を自動生成

4. **QRコード発行**
   - 施設専用QRコード生成
   - 設置場所別（entrance / room / kitchen / lounge / custom）
   - **セッション統合トークン埋め込みオプション**（v0.3新規）
   - PDF/PNG/SVG形式ダウンロード（A4印刷用）

5. **夜間対応キューUI**（v0.3新規）
   - 翌朝対応が必要な質問一覧表示
   - 手動実行ボタン（MVP期間中）
   - 解決済みマーク機能

### 2.2 Week 3で実装するコンポーネント構造

#### ゲスト側コンポーネント

```
ゲスト側
├── GuestLayout.vue
│   ├── DarkModeToggle.vue
│   ├── PWAInstallPrompt.vue
│   ├── SessionTokenDisplay.vue（v0.3新規）
│   └── <router-view />
│
├── LanguageSelect.vue
│   └── LanguageCard.vue
│
├── Welcome.vue
│   ├── FacilityHeader.vue
│   ├── TopQuestions.vue
│   ├── MessageInput.vue
│   └── EmergencyContact.vue
│
└── Chat.vue
    ├── ChatMessageList.vue
    │   └── ChatMessage.vue (user/assistant)
    │       └── FeedbackButtons.vue（v0.3新規: 👍👎）
    ├── MessageInput.vue (固定フッター)
    ├── SessionTokenInput.vue（v0.3新規: トークン入力）
    └── EscalationButton.vue
```

#### 管理画面コンポーネント

```
管理側
├── AdminLayout.vue
│   ├── Sidebar.vue
│   │   └── NavItem.vue
│   ├── Header.vue
│   │   ├── UserMenu.vue
│   │   └── DarkModeToggle.vue
│   └── <router-view />
│
├── Login.vue
│   └── LoginForm.vue
│
├── Dashboard.vue
│   ├── StatsCard.vue
│   ├── CategoryChart.vue
│   ├── ChatHistoryList.vue
│   ├── OvernightQueueList.vue（v0.3新規）
│   └── FeedbackStats.vue（v0.3新規）
│
├── FaqManagement.vue
│   ├── FaqList.vue
│   ├── FaqForm.vue
│   ├── UnresolvedQuestionsList.vue（v0.3新規）
│   │   └── FaqSuggestionCard.vue（v0.3新規）
│   └── FeedbackLinkedFaqs.vue（v0.3新規）
│
├── OvernightQueue.vue（v0.3新規）
│   ├── OvernightQueueList.vue
│   └── ProcessButton.vue（手動実行）
│
└── QRCodeGenerator.vue
    └── QRCodeForm.vue
```

### 2.3 Week 3で実装するAPI連携

#### ゲスト側API

1. **GET `/api/v1/facility/{slug}`**
   - 施設情報取得
   - よくある質問TOP3取得

2. **POST `/api/v1/chat`**
   - チャットメッセージ送信
   - RAG統合型AI対話エンジン呼び出し
   - エスカレーション処理
   - 夜間対応キュー処理

3. **GET `/api/v1/chat/history/{session_id}`**
   - 会話履歴取得

4. **POST `/api/v1/chat/feedback`**（v0.3新規）
   - ゲストフィードバック送信（👍👎）

5. **POST `/api/v1/session/link`**（v0.3新規）
   - セッション統合

6. **GET `/api/v1/session/token/{token}`**（v0.3新規）
   - トークン検証

#### 管理画面API

1. **POST `/api/v1/auth/login`**
   - ログイン

2. **POST `/api/v1/auth/logout`**
   - ログアウト

3. **GET `/api/v1/admin/dashboard`**（Week 4で実装予定、Week 3では準備のみ）
   - ダッシュボードデータ取得

4. **GET/POST/PUT/DELETE `/api/v1/admin/faqs`**（Week 4で実装予定、Week 3では準備のみ）
   - FAQ管理

5. **GET `/api/v1/admin/faq-suggestions`**（v0.3新規、Week 4で実装予定、Week 3では準備のみ）
   - FAQ追加提案一覧

6. **POST `/api/v1/admin/faq-suggestions/{id}/approve`**（v0.3新規、Week 4で実装予定、Week 3では準備のみ）
   - 提案承認

7. **GET `/api/v1/admin/overnight-queue`**（v0.3新規、Week 4で実装予定、Week 3では準備のみ）
   - 夜間対応キュー取得

8. **GET `/api/v1/admin/feedback-stats`**（v0.3新規、Week 4で実装予定、Week 3では準備のみ）
   - フィードバック統計取得

---

## 3. 技術的依存関係の確認

### 3.1 Week 1-2で構築済みの基盤

- ✅ FastAPI プロジェクト構造
- ✅ PostgreSQL 接続（pgvector拡張対応）
- ✅ Redis環境構築
- ✅ JWT認証システム
- ✅ 基本テーブル（users, facilities, conversations, messages, session_tokens）
- ✅ RAG統合型AI対話エンジン
- ✅ チャットAPI実装完了
- ✅ セッション統合トークンAPI実装完了

### 3.2 Week 3で追加する依存関係

#### フロントエンドライブラリ

- `vue`: Vue.js 3.4+（既にインストール済み）
- `vue-router`: 4.3+（既にインストール済み）
- `pinia`: 2.1+（既にインストール済み）
- `axios`: 1.6+（既にインストール済み）
- `@vueuse/core`: 10.9+（既にインストール済み）
- `vite-plugin-pwa`: 0.19+（既にインストール済み）
- `tailwindcss`: 3.4+（既にインストール済み）

#### 追加で必要な設定

- PWA設定（`vite.config.ts`）
- ダークモード設定（`tailwind.config.js`）
- Vue Router設定（`src/router/`）
- Pinia Store設定（`src/stores/`）
- Axios設定（`src/api/`）

### 3.3 依存関係の確認結果

| 依存関係 | 状況 | 備考 |
|---------|------|------|
| Vue.js 3 | ✅ **準備済み** | package.jsonに記載済み |
| Vue Router | ✅ **準備済み** | package.jsonに記載済み |
| Pinia | ✅ **準備済み** | package.jsonに記載済み |
| Axios | ✅ **準備済み** | package.jsonに記載済み |
| Tailwind CSS | ✅ **準備済み** | package.jsonに記載済み |
| PWA Plugin | ✅ **準備済み** | package.jsonに記載済み |
| バックエンドAPI | ✅ **実装済み** | Week 1-2で実装完了 |
| 管理画面API | ⚠️ **一部未実装** | Week 4で実装予定、Week 3では準備のみ |

---

## 4. 実装上の課題・リスクの特定

### 4.1 技術的課題

#### 課題1: PWA設定の複雑性

**問題**:
- PWA設定には複数の設定ファイルが必要
- Service Workerの設定が必要
- マニフェストファイルの設定が必要

**対策**:
- `vite-plugin-pwa`を使用して自動設定
- マニフェストファイルを自動生成
- Service Workerを自動生成

**実装方針**:
- `vite.config.ts`でPWA設定を追加
- マニフェストファイルを自動生成
- Service Workerを自動生成

#### 課題2: ダークモード実装の複雑性

**問題**:
- ダークモードの状態管理が必要
- Tailwind CSSのダークモード設定が必要
- システム設定との連携が必要

**対策**:
- Pinia Storeでダークモード状態管理
- Tailwind CSSの`dark:`クラスを使用
- `@vueuse/core`の`useDark`を使用

**実装方針**:
- `src/stores/theme.ts`でダークモード状態管理
- `tailwind.config.js`でダークモード設定
- `src/composables/useDarkMode.ts`でダークモードComposable実装

#### 課題3: セッション管理の複雑性

**問題**:
- Cookie保存が必要
- セッションIDの生成・管理が必要
- セッション統合トークンの管理が必要

**対策**:
- `js-cookie`ライブラリを使用（または`@vueuse/core`の`useCookies`）
- UUID生成ライブラリを使用
- Pinia Storeでセッション状態管理

**実装方針**:
- `src/composables/useSession.ts`でセッション管理
- `src/stores/chat.ts`でセッション状態管理
- Cookie操作は`@vueuse/core`の`useCookies`を使用

#### 課題4: ゲストフィードバックUIの実装

**問題**:
- フィードバック送信APIが未実装（Week 4で実装予定）
- フィードバック状態管理が必要

**対策**:
- Week 3ではUIのみ実装
- API連携はWeek 4で実装
- モックデータで動作確認

**実装方針**:
- `src/components/guest/FeedbackButtons.vue`でUI実装
- API連携はWeek 4で実装
- モックデータで動作確認

#### 課題5: FAQ自動学習UIの実装

**問題**:
- FAQ追加提案APIが未実装（Week 4で実装予定）
- GPT-4o miniによる回答テンプレート自動生成が必要

**対策**:
- Week 3ではUIのみ実装
- API連携はWeek 4で実装
- モックデータで動作確認

**実装方針**:
- `src/views/admin/FaqManagement.vue`でUI実装
- `src/components/admin/FaqSuggestionCard.vue`で提案カード実装
- API連携はWeek 4で実装

### 4.2 ビジネスロジック上の課題

#### 課題1: セッション統合トークンのUX

**問題**:
- 4桁英数字トークンの入力が煩雑
- トークンの有効期限（24時間）の表示が必要

**対策**:
- トークン入力UIを分かりやすく実装
- 有効期限を視覚的に表示
- トークン入力のガイダンスを追加

**実装方針**:
- `src/components/guest/SessionTokenInput.vue`でUI実装
- 有効期限をカウントダウン表示
- トークン入力のガイダンスを追加

#### 課題2: ゲストフィードバックのタイミング

**問題**:
- フィードバック送信のタイミングが不明確
- フィードバック送信後のフィードバックが必要

**対策**:
- 回答表示後にフィードバックボタンを表示
- フィードバック送信後に「ありがとうございます」メッセージを表示

**実装方針**:
- `src/components/guest/FeedbackButtons.vue`でUI実装
- 回答表示後にフィードバックボタンを表示
- フィードバック送信後に感謝メッセージを表示

### 4.3 パフォーマンス上の課題

#### 課題1: チャット履歴の表示

**問題**:
- 会話履歴が長くなると表示が重くなる
- スクロール位置の管理が必要

**対策**:
- 仮想スクロールを実装（必要に応じて）
- 最新メッセージに自動スクロール
- メッセージの遅延読み込み

**実装方針**:
- 最新メッセージに自動スクロール
- メッセージの遅延読み込み（必要に応じて）
- 仮想スクロールはPhase 2で検討

#### 課題2: ダッシュボードのポーリング

**問題**:
- ポーリングによるAPI呼び出しが増加
- サーバー負荷が増加する可能性

**対策**:
- ポーリング間隔を適切に設定（30秒-1分）
- 手動更新ボタンを追加
- Phase 2でWebSocketに移行検討

**実装方針**:
- ポーリング間隔を30秒に設定
- 手動更新ボタンを追加
- Phase 2でWebSocketに移行検討

---

## 5. 実装順序の最適化

### 5.1 推奨実装順序

1. **基盤構築フェーズ**（ステップ1-3）
   - Vue.js プロジェクト構造完成
   - Vue Router設定
   - Pinia Store設定
   - Axios設定
   - PWA設定
   - ダークモード設定

2. **共通コンポーネントフェーズ**（ステップ4-5）
   - 共通コンポーネント実装（Button, Input, Modal, Loading）
   - ダークモードToggle実装
   - PWA Install Prompt実装

3. **ゲスト側UIフェーズ**（ステップ6-9）
   - 言語選択画面実装
   - ウェルカム画面実装
   - AI対話インターフェース実装
   - セッション統合トークンUI実装（v0.3新規）
   - ゲストフィードバックUI実装（v0.3新規）

4. **管理画面UIフェーズ**（ステップ10-13）
   - 認証システム実装（ログイン画面）
   - ダッシュボード実装（UIのみ、API連携はWeek 4）
   - FAQ管理実装（UIのみ、API連携はWeek 4）
   - FAQ自動学習UI実装（v0.3新規、UIのみ）
   - 夜間対応キューUI実装（v0.3新規、UIのみ）

5. **統合フェーズ**（ステップ14-15）
   - ルーティング統合
   - 動作確認

### 5.2 実装順序の根拠

1. **基盤→機能の順序**: プロジェクト構造・設定を先に構築し、その後に機能を実装
2. **共通コンポーネント→ページコンポーネントの順序**: 再利用可能なコンポーネントを先に実装し、その後にページコンポーネントで使用
3. **ゲスト側→管理画面の順序**: ゲスト側の方がシンプルなため、先に実装してから管理画面を実装
4. **UI→API連携の順序**: UIを先に実装し、その後にAPI連携を実装（Week 4で実装予定のAPIは準備のみ）

---

## 6. 実装上の注意事項

### 6.1 Vue.js 3 Composition API

- Composition APIを使用
- `<script setup>`構文を使用
- TypeScriptを使用

### 6.2 状態管理（Pinia）

- Pinia Storeで状態管理
- セッション管理は`chat.ts`で実装
- ダークモード管理は`theme.ts`で実装

### 6.3 ルーティング（Vue Router）

- ゲスト側と管理画面でルートを分離
- 認証ガードを実装（管理画面）
- 404ページを実装

### 6.4 API通信（Axios）

- Axiosインスタンスを作成
- リクエストインターセプターでJWTトークン追加
- レスポンスインターセプターでエラーハンドリング

### 6.5 PWA設定

- `vite-plugin-pwa`を使用
- マニフェストファイルを自動生成
- Service Workerを自動生成

### 6.6 ダークモード

- Pinia Storeでダークモード状態管理
- Tailwind CSSの`dark:`クラスを使用
- システム設定との連携

### 6.7 セッション管理

- Cookie保存（`@vueuse/core`の`useCookies`）
- セッションID生成（UUID）
- セッション統合トークン管理

### 6.8 レスポンシブデザイン

- Tailwind CSSのレスポンシブクラスを使用
- モバイルファーストで実装
- 375px-428pxのスマホ画面に対応

---

## 7. 実装完了基準

### 7.1 機能完了基準

- [ ] Vue.js プロジェクト構造が完成している
- [ ] Vue Router設定が正常に動作する
- [ ] Pinia Store設定が正常に動作する
- [ ] Axios設定が正常に動作する
- [ ] PWA設定が正常に動作する
- [ ] ダークモード設定が正常に動作する
- [ ] 言語選択画面が正常に動作する
- [ ] ウェルカム画面が正常に動作する
- [ ] AI対話インターフェースが正常に動作する
- [ ] セッション統合トークンUIが正常に動作する
- [ ] ゲストフィードバックUIが正常に動作する
- [ ] ログイン画面が正常に動作する
- [ ] ダッシュボードUIが正常に表示される（API連携はWeek 4）
- [ ] FAQ管理UIが正常に表示される（API連携はWeek 4）
- [ ] FAQ自動学習UIが正常に表示される（API連携はWeek 4）
- [ ] 夜間対応キューUIが正常に表示される（API連携はWeek 4）

### 7.2 パフォーマンス基準

- [ ] ページ読み込み時間: 3秒以内（目標）
- [ ] チャットメッセージ送信: 3秒以内（目標）
- [ ] ダークモード切替: 即座に反映

### 7.3 品質基準

- [ ] レスポンシブデザインが適切に実装されている
- [ ] ダークモードが適切に実装されている
- [ ] PWAが適切に実装されている
- [ ] エラーハンドリングが適切に実装されている
- [ ] コード品質が適切である（リントエラーなし）

---

## 8. 次のステップ（Week 4）

Week 3完了後、Week 4（統合・テスト・ステージング環境構築）に進む：

- エンドツーエンドテスト
- レスポンス速度最適化
- エラーハンドリング
- QRコード生成機能
- 管理画面API実装（ダッシュボード、FAQ管理、FAQ自動学習、夜間対応キュー）
- ゲストフィードバックAPI実装
- ステージング環境構築・デプロイ（Render.com Pro + Railway Hobby）

---

## 9. 参考資料

### 主要ドキュメント

- **要約定義書**: `docs/Summary/yadopera-v03-summary.md`
- **アーキテクチャ設計書**: `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`
- **Phase 0引き継ぎ書**: `docs/Phase0_引き継ぎ書.md`
- **Phase 1 Week 1ステップ計画**: `docs/Phase1/Phase1_Week1_ステップ計画.md`
- **Phase 1 Week 2ステップ計画**: `docs/Phase1/Phase1_Week2_ステップ計画.md`
- **Phase 1 Week 2引き継ぎ事項**: `docs/Phase1/Phase1_Week2_引き継ぎ事項.md`

### 実装参考セクション

- アーキテクチャ設計書 4. Vue.js ページ遷移図
- アーキテクチャ設計書 4.4 コンポーネント階層構造
- アーキテクチャ設計書 6.1 ディレクトリ構造（Frontend）
- アーキテクチャ設計書 8.2 RESTful API エンドポイント一覧
- アーキテクチャ設計書 8.3 APIリクエスト・レスポンス詳細

---

**レポート作成者**: AI Assistant  
**最終更新日**: 2025年11月27日


