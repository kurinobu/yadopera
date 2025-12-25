# Phase 1 Week 3 ステップ計画

**作成日**: 2025年11月27日  
**フェーズ**: Phase 1 Week 3（フロントエンド）  
**期間**: 1週間  
**目的**: MVP開発のためのフロントエンド構築（Vue.js 3）

---

## Week 3 目標

フロントエンドを構築し、以下の機能を実装する：

1. Vue.js プロジェクト構造完成
2. ゲスト側UI（PWA、ダークモード）
3. ゲストフィードバックUI（👍👎）
4. セッション統合トークン表示・入力UI
5. 管理画面（ダッシュボード）
6. FAQ自動学習UI（ワンクリック追加）
7. 夜間対応キューUI

---

## 前提条件

### Phase 1 Week 1-2完了確認

- [x] FastAPI プロジェクト構造完成
- [x] PostgreSQL 接続（pgvector拡張対応）済み
- [x] Redis環境構築済み
- [x] JWT認証システム実装済み
- [x] 基本テーブル実装済み
- [x] RAG統合型AI対話エンジン実装済み
- [x] チャットAPI実装済み
- [x] セッション統合トークンAPI実装済み

### 必要な環境変数

`frontend/.env`に以下が設定されていること：
- `VITE_API_BASE_URL`: バックエンドAPI URL（例: `http://localhost:8000`）

### 必要なバックエンドAPI（実装済み）

- ✅ `GET /api/v1/facility/{slug}` - 施設情報取得
- ✅ `POST /api/v1/chat` - チャットメッセージ送信
- ✅ `GET /api/v1/chat/history/{session_id}` - 会話履歴取得
- ✅ `POST /api/v1/session/link` - セッション統合
- ✅ `GET /api/v1/session/token/{token}` - トークン検証
- ✅ `POST /api/v1/auth/login` - ログイン
- ✅ `POST /api/v1/auth/logout` - ログアウト

### 必要なバックエンドAPI（Week 4で実装予定、Week 3では準備のみ）

- ⏳ `POST /api/v1/chat/feedback` - ゲストフィードバック送信
- ⏳ `GET /api/v1/admin/dashboard` - ダッシュボードデータ取得
- ⏳ `GET/POST/PUT/DELETE /api/v1/admin/faqs` - FAQ管理
- ⏳ `GET /api/v1/admin/faq-suggestions` - FAQ追加提案一覧
- ⏳ `POST /api/v1/admin/faq-suggestions/{id}/approve` - 提案承認
- ⏳ `GET /api/v1/admin/overnight-queue` - 夜間対応キュー取得
- ⏳ `GET /api/v1/admin/feedback-stats` - フィードバック統計取得

---

## ステップ詳細

### ステップ1: Vue.js プロジェクト構造完成（3時間）

**目的**: Vue.js プロジェクトの基本構造を完成させる

**実装内容**:
1. `frontend/src/router/`ディレクトリ作成
   - `index.ts`: ルーター設定
   - `guest.ts`: ゲスト側ルート
   - `admin.ts`: 管理画面ルート

2. `frontend/src/stores/`ディレクトリ作成
   - `index.ts`: Pinia Store設定
   - `auth.ts`: 認証状態管理
   - `chat.ts`: チャット状態管理（セッション管理含む）
   - `facility.ts`: 施設情報状態管理
   - `theme.ts`: ダークモード状態管理

3. `frontend/src/api/`ディレクトリ作成
   - `axios.ts`: Axios設定
   - `auth.ts`: 認証API
   - `chat.ts`: チャットAPI
   - `facility.ts`: 施設情報API
   - `session.ts`: セッション統合トークンAPI

4. `frontend/src/composables/`ディレクトリ作成
   - `useAuth.ts`: 認証Composable
   - `useChat.ts`: チャットComposable
   - `useSession.ts`: セッション管理Composable
   - `useDarkMode.ts`: ダークモードComposable
   - `usePWA.ts`: PWA Composable

5. `frontend/src/utils/`ディレクトリ作成
   - `constants.ts`: 定数定義
   - `validators.ts`: バリデーション関数
   - `formatters.ts`: フォーマット関数
   - `cookies.ts`: Cookie操作関数

**確認項目**:
- [ ] ディレクトリ構造が正しく作成されている
- [ ] TypeScript設定が正しく動作する
- [ ] インポートエラーがない

**参考**: アーキテクチャ設計書 6.1 ディレクトリ構造（Frontend）

---

### ステップ2: Vue Router設定（2時間）

**目的**: Vue Routerを設定し、ルーティングを実装

**実装内容**:
1. `frontend/src/router/index.ts`作成
   - ルーターインスタンス作成
   - ゲスト側・管理画面ルートを統合

2. `frontend/src/router/guest.ts`作成
   - `/f/:facilityId`: 言語選択画面
   - `/f/:facilityId/welcome`: ウェルカム画面
   - `/f/:facilityId/chat`: AI対話インターフェース

3. `frontend/src/router/admin.ts`作成
   - `/admin/login`: ログイン画面
   - `/admin/dashboard`: ダッシュボード
   - `/admin/faqs`: FAQ管理
   - `/admin/overnight-queue`: 夜間対応キュー
   - `/admin/qr-code`: QRコード発行

4. `frontend/src/App.vue`更新
   - ルータービュー追加

**確認項目**:
- [ ] ルーティングが正常に動作する
- [ ] ゲスト側・管理画面ルートが正しく分離されている
- [ ] 404ページが正しく表示される

**参考**: アーキテクチャ設計書 4. Vue.js ページ遷移図

---

### ステップ3: Pinia Store設定（2時間）

**目的**: Pinia Storeを設定し、状態管理を実装

**実装内容**:
1. `frontend/src/stores/index.ts`作成
   - Piniaインスタンス作成

2. `frontend/src/stores/auth.ts`作成
   - 認証状態管理（ログイン状態、ユーザー情報）
   - ログイン・ログアウトアクション

3. `frontend/src/stores/chat.ts`作成
   - チャット状態管理（メッセージ履歴、セッションID）
   - セッション管理（Cookie保存）
   - セッション統合トークン管理

4. `frontend/src/stores/facility.ts`作成
   - 施設情報状態管理

5. `frontend/src/stores/theme.ts`作成
   - ダークモード状態管理

6. `frontend/src/main.ts`更新
   - Piniaインスタンスを登録

**確認項目**:
- [ ] Pinia Storeが正常に動作する
- [ ] 状態管理が正しく実装されている
- [ ] セッション管理が正しく実装されている

**参考**: アーキテクチャ設計書 6.1 ディレクトリ構造（stores）

---

### ステップ4: Axios設定（2時間）

**目的**: Axiosを設定し、API通信を実装

**実装内容**:
1. `frontend/src/api/axios.ts`作成
   - Axiosインスタンス作成
   - リクエストインターセプター（JWTトークン追加）
   - レスポンスインターセプター（エラーハンドリング）

2. `frontend/src/api/auth.ts`作成
   - `login()`: ログインAPI
   - `logout()`: ログアウトAPI

3. `frontend/src/api/chat.ts`作成
   - `sendMessage()`: チャットメッセージ送信
   - `getHistory()`: 会話履歴取得

4. `frontend/src/api/facility.ts`作成
   - `getFacility()`: 施設情報取得

5. `frontend/src/api/session.ts`作成
   - `linkSession()`: セッション統合
   - `verifyToken()`: トークン検証

**確認項目**:
- [x] Axios設定が正常に動作する
- [x] JWTトークンが正しく追加される
- [x] エラーハンドリングが正しく実装されている

**参考**: アーキテクチャ設計書 8.2 RESTful API エンドポイント一覧

---

### ステップ5: PWA設定（2時間）

**目的**: PWA設定を実装し、オフライン対応を実現

**実装内容**:
1. `frontend/vite.config.ts`更新
   - `vite-plugin-pwa`設定追加
   - マニフェストファイル設定
   - Service Worker設定

2. `frontend/src/composables/usePWA.ts`作成
   - PWAインストールプロンプト管理
   - インストール状態管理

3. `frontend/src/components/common/PWAInstallPrompt.vue`作成
   - PWAインストールプロンプト表示

**確認項目**:
- [x] PWA設定が正常に動作する
- [x] マニフェストファイルが正しく生成される
- [x] Service Workerが正しく生成される
- [x] PWAインストールプロンプトが正しく表示される

**参考**: アーキテクチャ設計書 6.1 ディレクトリ構造（PWA設定）

---

### ステップ6: ダークモード設定（2時間）

**目的**: ダークモード設定を実装し、テーマ切替を実現

**実装内容**:
1. `frontend/tailwind.config.js`更新
   - ダークモード設定追加（`darkMode: 'class'`）

2. `frontend/src/composables/useDarkMode.ts`作成
   - ダークモード状態管理
   - システム設定との連携（`@vueuse/core`の`useDark`）

3. `frontend/src/components/common/DarkModeToggle.vue`作成
   - ダークモード切替ボタン

4. `frontend/src/assets/styles/dark-mode.css`作成
   - ダークモードスタイル

**確認項目**:
- [x] ダークモード設定が正常に動作する
- [x] テーマ切替が即座に反映される
- [x] システム設定との連携が正しく動作する

**参考**: アーキテクチャ設計書 6.1 ディレクトリ構造（ダークモード設定）

---

### ステップ7: 共通コンポーネント実装（3時間）

**目的**: 再利用可能な共通コンポーネントを実装

**実装内容**:
1. `frontend/src/components/common/Button.vue`作成
   - ボタンコンポーネント（プライマリ、セカンダリ、アウトライン）

2. `frontend/src/components/common/Input.vue`作成
   - 入力コンポーネント（テキスト、パスワード、テキストエリア）

3. `frontend/src/components/common/Modal.vue`作成
   - モーダルコンポーネント

4. `frontend/src/components/common/Loading.vue`作成
   - ローディングコンポーネント

**確認項目**:
- [x] 共通コンポーネントが正しく実装されている
- [x] スタイルが適切に適用されている
- [x] ダークモード対応が正しく実装されている

**参考**: アーキテクチャ設計書 4.4 コンポーネント階層構造

---

### ステップ8: 言語選択画面実装（2時間）

**目的**: ゲスト側の言語選択画面を実装

**実装内容**:
1. `frontend/src/views/guest/LanguageSelect.vue`作成
   - 言語選択画面（英語のみ、MVP）
   - レスポンシブデザイン対応

2. `frontend/src/components/guest/LanguageCard.vue`作成
   - 言語カードコンポーネント

**確認項目**:
- [x] 言語選択画面が正常に表示される
- [x] レスポンシブデザインが正しく動作する
- [x] ルーティングが正しく動作する

**参考**: アーキテクチャ設計書 4. Vue.js ページ遷移図（ゲスト側）

---

### ステップ9: ウェルカム画面実装（3時間）

**目的**: ゲスト側のウェルカム画面を実装

**実装内容**:
1. `frontend/src/views/guest/Welcome.vue`作成
   - ウェルカム画面
   - 施設情報表示
   - よくある質問TOP3表示
   - フリー入力フォーム
   - 緊急連絡先表示

2. `frontend/src/components/guest/FacilityHeader.vue`作成
   - 施設情報ヘッダーコンポーネント

3. `frontend/src/components/guest/TopQuestions.vue`作成
   - よくある質問TOP3コンポーネント

4. `frontend/src/components/guest/MessageInput.vue`作成
   - メッセージ入力コンポーネント

5. `frontend/src/components/guest/EmergencyContact.vue`作成
   - 緊急連絡先コンポーネント

**確認項目**:
- [x] ウェルカム画面が正常に表示される
- [x] 施設情報が正しく取得される
- [x] よくある質問TOP3が正しく表示される
- [x] レスポンシブデザインが正しく動作する

**参考**: アーキテクチャ設計書 4. Vue.js ページ遷移図（ゲスト側）

---

### ステップ10: AI対話インターフェース実装（5時間）

**目的**: ゲスト側のAI対話インターフェースを実装

**実装内容**:
1. `frontend/src/views/guest/Chat.vue`作成
   - AI対話インターフェース（チャット形式）
   - 固定フッター（メッセージ入力）
   - セッション管理（Cookie保存）

2. `frontend/src/components/guest/ChatMessageList.vue`作成
   - チャットメッセージリストコンポーネント

3. `frontend/src/components/guest/ChatMessage.vue`作成
   - チャットメッセージコンポーネント（user/assistant）
   - **FeedbackButtons.vue統合**（v0.3新規）

4. `frontend/src/components/guest/FeedbackButtons.vue`作成（v0.3新規）
   - ゲストフィードバックボタン（👍👎）
   - フィードバック送信（API連携はWeek 4、Week 3ではモック）

5. `frontend/src/components/guest/EscalationButton.vue`作成
   - エスカレーションボタン

6. `frontend/src/composables/useChat.ts`更新
   - チャットメッセージ送信ロジック
   - 会話履歴取得ロジック
   - セッション管理ロジック

**確認項目**:
- [x] AI対話インターフェースが正常に動作する
- [x] チャットメッセージが正しく表示される
- [x] セッション管理が正しく動作する
- [x] ゲストフィードバックUIが正しく表示される（API連携はWeek 4）
- [x] レスポンシブデザインが正しく動作する

**参考**: アーキテクチャ設計書 4. Vue.js ページ遷移図（ゲスト側）

---

### ステップ11: セッション統合トークンUI実装（3時間）

**目的**: セッション統合トークンUIを実装（v0.3新規）

**実装内容**:
1. `frontend/src/components/guest/SessionTokenDisplay.vue`作成
   - セッション統合トークン表示（画面上部）
   - 4桁英数字トークン表示
   - 有効期限表示（カウントダウン）

2. `frontend/src/components/guest/SessionTokenInput.vue`作成
   - セッション統合トークン入力UI
   - トークン入力フォーム
   - トークン検証・統合処理

3. `frontend/src/views/guest/Chat.vue`更新
   - SessionTokenDisplay統合
   - SessionTokenInput統合

4. `frontend/src/composables/useSession.ts`更新
   - セッション統合トークン管理
   - トークン生成・検証ロジック

**確認項目**:
- [x] セッション統合トークンが正しく表示される
- [x] トークン入力UIが正しく動作する
- [x] セッション統合が正しく動作する
- [x] 有効期限が正しく表示される

**参考**: 
- 要約定義書 3.1 ゲスト側機能（セッション管理）
- アーキテクチャ設計書 5.4 セッション管理フロー（セッション統合フロー）

---

### ステップ12: ゲストレイアウト実装（2時間）

**目的**: ゲスト側のレイアウトコンポーネントを実装

**実装内容**:
1. `frontend/src/layouts/GuestLayout.vue`作成
   - ゲスト側レイアウト
   - DarkModeToggle統合
   - PWAInstallPrompt統合
   - SessionTokenDisplay統合

2. `frontend/src/router/guest.ts`更新
   - GuestLayoutを適用

**確認項目**:
- [x] ゲストレイアウトが正常に表示される
- [x] ダークモード切替が正しく動作する
- [x] PWAインストールプロンプトが正しく表示される

**参考**: アーキテクチャ設計書 4.4 コンポーネント階層構造

---

### ステップ13: ログイン画面実装（2時間）

**目的**: 管理画面のログイン画面を実装

**実装内容**:
1. `frontend/src/views/admin/Login.vue`作成
   - ログイン画面
   - メールアドレス・パスワード入力
   - ログインボタン

2. `frontend/src/components/admin/LoginForm.vue`作成
   - ログインフォームコンポーネント

3. `frontend/src/composables/useAuth.ts`更新
   - ログイン処理
   - JWTトークン保存（localStorage）

**確認項目**:
- [x] ログイン画面が正常に表示される
- [x] ログイン処理が正しく動作する
- [x] JWTトークンが正しく保存される
- [x] エラーハンドリングが正しく実装されている

**参考**: アーキテクチャ設計書 4. Vue.js ページ遷移図（管理側）

---

### ステップ14: 管理画面レイアウト実装（3時間）

**目的**: 管理画面のレイアウトコンポーネントを実装

**実装内容**:
1. `frontend/src/layouts/AdminLayout.vue`作成
   - 管理画面レイアウト
   - Sidebar統合
   - Header統合

2. `frontend/src/components/admin/Sidebar.vue`作成
   - サイドバーコンポーネント
   - ナビゲーションメニュー

3. `frontend/src/components/admin/NavItem.vue`作成
   - ナビゲーションアイテムコンポーネント

4. `frontend/src/components/admin/Header.vue`作成
   - ヘッダーコンポーネント
   - UserMenu統合
   - DarkModeToggle統合

5. `frontend/src/components/admin/UserMenu.vue`作成
   - ユーザーメニューコンポーネント

6. `frontend/src/router/admin.ts`更新
   - AdminLayoutを適用
   - 認証ガード実装

**確認項目**:
- [x] 管理画面レイアウトが正常に表示される
- [x] サイドバーが正しく動作する
- [x] ヘッダーが正しく動作する
- [x] 認証ガードが正しく動作する

**参考**: アーキテクチャ設計書 4. Vue.js ページ遷移図（管理側）

---

### ステップ15: ダッシュボードUI実装（4時間）

**目的**: 管理画面のダッシュボードUIを実装（API連携はWeek 4）

**実装内容**:
1. `frontend/src/views/admin/Dashboard.vue`作成
   - ダッシュボード画面
   - 週次サマリー表示（モックデータ）
   - リアルタイムチャット履歴（モックデータ）
   - **夜間対応キュー表示**（v0.3新規、モックデータ）
   - **ゲストフィードバック集計表示**（v0.3新規、モックデータ）

2. `frontend/src/components/admin/StatsCard.vue`作成
   - 統計カードコンポーネント

3. `frontend/src/components/admin/CategoryChart.vue`作成
   - カテゴリ別円グラフコンポーネント

4. `frontend/src/components/admin/ChatHistoryList.vue`作成
   - チャット履歴リストコンポーネント

5. `frontend/src/components/admin/OvernightQueueList.vue`作成（v0.3新規）
   - 夜間対応キューリストコンポーネント

6. `frontend/src/components/admin/FeedbackStats.vue`作成（v0.3新規）
   - ゲストフィードバック統計コンポーネント

**確認項目**:
- [ ] ダッシュボードUIが正常に表示される
- [ ] モックデータが正しく表示される
- [ ] レスポンシブデザインが正しく動作する
- [ ] API連携準備が整っている（Week 4で実装）

**参考**: アーキテクチャ設計書 4. Vue.js ページ遷移図（管理側）

---

### ステップ16: FAQ管理UI実装（4時間）

**目的**: 管理画面のFAQ管理UIを実装（API連携はWeek 4）

**実装内容**:
1. `frontend/src/views/admin/FaqManagement.vue`作成
   - FAQ管理画面
   - FAQ一覧表示（モックデータ）
   - FAQ追加・編集フォーム
   - **未解決質問リスト表示**（v0.3新規、モックデータ）
   - **FAQ自動学習UI**（v0.3新規、モックデータ）

2. `frontend/src/components/admin/FaqList.vue`作成
   - FAQリストコンポーネント

3. `frontend/src/components/admin/FaqForm.vue`作成
   - FAQ追加・編集フォームコンポーネント

4. `frontend/src/components/admin/UnresolvedQuestionsList.vue`作成（v0.3新規）
   - 未解決質問リストコンポーネント

5. `frontend/src/components/admin/FaqSuggestionCard.vue`作成（v0.3新規）
   - FAQ追加提案カードコンポーネント
   - 「FAQ追加」ボタン（ワンクリック）
   - 質問文自動入力
   - 回答文テンプレート自動生成（モック、Week 4でAPI連携）
   - カテゴリ自動推定（モック、Week 4でAPI連携）

6. `frontend/src/components/admin/FeedbackLinkedFaqs.vue`作成（v0.3新規）
   - ゲストフィードバック連動FAQコンポーネント
   - 👎評価が2回以上ついた回答の自動ハイライト
   - 「FAQ改善提案」ボタン（モック、Week 4でAPI連携）

**確認項目**:
- [ ] FAQ管理UIが正常に表示される
- [ ] モックデータが正しく表示される
- [ ] FAQ自動学習UIが正しく表示される（API連携はWeek 4）
- [ ] レスポンシブデザインが正しく動作する

**参考**: 
- 要約定義書 3.2 宿側機能（FAQ管理）
- アーキテクチャ設計書 4. Vue.js ページ遷移図（管理側）

---

### ステップ17: 夜間対応キューUI実装（2時間）

**目的**: 管理画面の夜間対応キューUIを実装（v0.3新規、API連携はWeek 4）

**実装内容**:
1. `frontend/src/views/admin/OvernightQueue.vue`作成
   - 夜間対応キュー画面
   - 翌朝対応が必要な質問一覧表示（モックデータ）
   - 手動実行ボタン（MVP期間中）

2. `frontend/src/components/admin/OvernightQueueList.vue`作成
   - 夜間対応キューリストコンポーネント

3. `frontend/src/components/admin/ProcessButton.vue`作成
   - 手動実行ボタンコンポーネント（モック、Week 4でAPI連携）

**確認項目**:
- [ ] 夜間対応キューUIが正常に表示される
- [ ] モックデータが正しく表示される
- [ ] レスポンシブデザインが正しく動作する
- [ ] API連携準備が整っている（Week 4で実装）

**参考**: 
- 要約定義書 3.2 宿側機能（ダッシュボード）
- アーキテクチャ設計書 4. Vue.js ページ遷移図（管理側）

---

### ステップ18: QRコード発行UI実装（3時間）

**目的**: 管理画面のQRコード発行UIを実装（API連携はWeek 4）

**実装内容**:
1. `frontend/src/views/admin/QRCodeGenerator.vue`作成
   - QRコード発行画面
   - 設置場所選択
   - **セッション統合トークン埋め込みオプション**（v0.3新規）
   - PDF/PNG/SVG形式ダウンロード（モック、Week 4でAPI連携）

2. `frontend/src/components/admin/QRCodeForm.vue`作成
   - QRコード発行フォームコンポーネント

**確認項目**:
- [ ] QRコード発行UIが正常に表示される
- [ ] セッション統合トークン埋め込みオプションが正しく表示される
- [ ] レスポンシブデザインが正しく動作する
- [ ] API連携準備が整っている（Week 4で実装）

**参考**: 
- 要約定義書 3.2 宿側機能（QRコード発行）
- アーキテクチャ設計書 4. Vue.js ページ遷移図（管理側）

---

### ステップ19: ルーティング統合・動作確認（2時間）

**目的**: 実装したルーティングを統合し、動作確認を行う

**実装内容**:
1. `frontend/src/router/index.ts`更新
   - 全ルートを統合

2. `frontend/src/App.vue`更新
   - ルータービュー確認

3. 動作確認:
   - 各ページの動作確認
   - ルーティング確認
   - 認証ガード確認
   - レスポンシブデザイン確認
   - ダークモード確認
   - PWA確認

**確認項目**:
- [ ] 全ページが正常に表示される
- [ ] ルーティングが正しく動作する
- [ ] 認証ガードが正しく動作する
- [ ] レスポンシブデザインが正しく動作する
- [ ] ダークモードが正しく動作する
- [ ] PWAが正しく動作する

**参考**: アーキテクチャ設計書 4. Vue.js ページ遷移図

---

### ステップ20: エラーハンドリング・例外処理（2時間）

**目的**: エラーハンドリングと例外処理を実装

**実装内容**:
1. `frontend/src/utils/errorHandler.ts`作成
   - エラーハンドリング関数
   - エラーメッセージ表示

2. `frontend/src/api/axios.ts`更新
   - レスポンスインターセプターでエラーハンドリング強化

3. `frontend/src/views/Error404.vue`作成
   - 404ページ

4. `frontend/src/views/Error500.vue`作成
   - 500ページ

**確認項目**:
- [ ] エラーハンドリングが適切に実装されている
- [ ] エラーメッセージが正しく表示される
- [ ] 404ページが正しく表示される
- [ ] 500ページが正しく表示される

**参考**: アーキテクチャ設計書 13. エラーハンドリング

---

## 実装順序の推奨

1. **ステップ1**: Vue.js プロジェクト構造完成（基盤）
2. **ステップ2**: Vue Router設定（ルーティング）
3. **ステップ3**: Pinia Store設定（状態管理）
4. **ステップ4**: Axios設定（API通信）
5. **ステップ5**: PWA設定（オフライン対応）
6. **ステップ6**: ダークモード設定（テーマ切替）
7. **ステップ7**: 共通コンポーネント実装（再利用可能コンポーネント）
8. **ステップ8**: 言語選択画面実装（ゲスト側）
9. **ステップ9**: ウェルカム画面実装（ゲスト側）
10. **ステップ10**: AI対話インターフェース実装（ゲスト側）
11. **ステップ11**: セッション統合トークンUI実装（v0.3新規）
12. **ステップ12**: ゲストレイアウト実装（ゲスト側）
13. **ステップ13**: ログイン画面実装（管理画面）
14. **ステップ14**: 管理画面レイアウト実装（管理画面）
15. **ステップ15**: ダッシュボードUI実装（管理画面）
16. **ステップ16**: FAQ管理UI実装（管理画面）
17. **ステップ17**: 夜間対応キューUI実装（v0.3新規）
18. **ステップ18**: QRコード発行UI実装（管理画面）
19. **ステップ19**: ルーティング統合・動作確認（統合）
20. **ステップ20**: エラーハンドリング・例外処理（品質向上）

---

## 各ステップの工数見積もり

| ステップ | 工数 | 累計工数 |
|---------|------|---------|
| ステップ1: Vue.js プロジェクト構造完成 | 3時間 | 3時間 |
| ステップ2: Vue Router設定 | 2時間 | 5時間 |
| ステップ3: Pinia Store設定 | 2時間 | 7時間 |
| ステップ4: Axios設定 | 2時間 | 9時間 |
| ステップ5: PWA設定 | 2時間 | 11時間 |
| ステップ6: ダークモード設定 | 2時間 | 13時間 |
| ステップ7: 共通コンポーネント実装 | 3時間 | 16時間 |
| ステップ8: 言語選択画面実装 | 2時間 | 18時間 |
| ステップ9: ウェルカム画面実装 | 3時間 | 21時間 |
| ステップ10: AI対話インターフェース実装 | 5時間 | 26時間 |
| ステップ11: セッション統合トークンUI実装 | 3時間 | 29時間 |
| ステップ12: ゲストレイアウト実装 | 2時間 | 31時間 |
| ステップ13: ログイン画面実装 | 2時間 | 33時間 |
| ステップ14: 管理画面レイアウト実装 | 3時間 | 36時間 |
| ステップ15: ダッシュボードUI実装 | 4時間 | 40時間 |
| ステップ16: FAQ管理UI実装 | 4時間 | 44時間 |
| ステップ17: 夜間対応キューUI実装 | 2時間 | 46時間 |
| ステップ18: QRコード発行UI実装 | 3時間 | 49時間 |
| ステップ19: ルーティング統合・動作確認 | 2時間 | 51時間 |
| ステップ20: エラーハンドリング・例外処理 | 2時間 | 53時間 |

**合計**: 約53時間（1週間で実装可能）

---

## 実装時の注意事項

### 1. Vue.js 3 Composition API

- Composition APIを使用
- `<script setup>`構文を使用
- TypeScriptを使用

### 2. 状態管理（Pinia）

- Pinia Storeで状態管理
- セッション管理は`chat.ts`で実装
- ダークモード管理は`theme.ts`で実装

### 3. ルーティング（Vue Router）

- ゲスト側と管理画面でルートを分離
- 認証ガードを実装（管理画面）
- 404ページを実装

### 4. API通信（Axios）

- Axiosインスタンスを作成
- リクエストインターセプターでJWTトークン追加
- レスポンスインターセプターでエラーハンドリング

### 5. PWA設定

- `vite-plugin-pwa`を使用
- マニフェストファイルを自動生成
- Service Workerを自動生成

### 6. ダークモード

- Pinia Storeでダークモード状態管理
- Tailwind CSSの`dark:`クラスを使用
- システム設定との連携

### 7. セッション管理

- Cookie保存（`@vueuse/core`の`useCookies`）
- セッションID生成（UUID）
- セッション統合トークン管理

### 8. レスポンシブデザイン

- Tailwind CSSのレスポンシブクラスを使用
- モバイルファーストで実装
- 375px-428pxのスマホ画面に対応

### 9. Week 4で実装予定のAPI連携

- Week 3ではUIのみ実装
- モックデータで動作確認
- API連携はWeek 4で実装

---

## 完了基準

Week 3完了の基準：

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
- [ ] ゲストフィードバックUIが正常に表示される（API連携はWeek 4）
- [ ] ログイン画面が正常に動作する
- [ ] ダッシュボードUIが正常に表示される（API連携はWeek 4）
- [ ] FAQ管理UIが正常に表示される（API連携はWeek 4）
- [ ] FAQ自動学習UIが正常に表示される（API連携はWeek 4）
- [ ] 夜間対応キューUIが正常に表示される（API連携はWeek 4）
- [ ] QRコード発行UIが正常に表示される（API連携はWeek 4）
- [ ] レスポンシブデザインが適切に実装されている
- [ ] ダークモードが適切に実装されている
- [ ] PWAが適切に実装されている
- [ ] エラーハンドリングが適切に実装されている

---

## 次のステップ（Week 4）

Week 3完了後、Week 4（統合・テスト・ステージング環境構築）に進む：

- エンドツーエンドテスト
- レスポンス速度最適化
- エラーハンドリング
- QRコード生成機能
- 管理画面API実装（ダッシュボード、FAQ管理、FAQ自動学習、夜間対応キュー）
- ゲストフィードバックAPI実装
- ステージング環境構築・デプロイ（Render.com Pro + Railway Hobby）

---

## 参考資料

### 主要ドキュメント

- **要約定義書**: `docs/Summary/yadopera-v03-summary.md`
- **アーキテクチャ設計書**: `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`
- **Phase 0引き継ぎ書**: `docs/Phase0_引き継ぎ書.md`
- **Phase 1 Week 1ステップ計画**: `docs/Phase1/Phase1_Week1_ステップ計画.md`
- **Phase 1 Week 2ステップ計画**: `docs/Phase1/Phase1_Week2_ステップ計画.md`
- **Phase 1 Week 2引き継ぎ事項**: `docs/Phase1/Phase1_Week2_引き継ぎ事項.md`
- **Phase 1 Week 3調査分析レポート**: `docs/Phase1/Phase1_Week3_調査分析レポート.md`

### 実装参考セクション

- アーキテクチャ設計書 4. Vue.js ページ遷移図
- アーキテクチャ設計書 4.4 コンポーネント階層構造
- アーキテクチャ設計書 6.1 ディレクトリ構造（Frontend）
- アーキテクチャ設計書 8.2 RESTful API エンドポイント一覧
- アーキテクチャ設計書 8.3 APIリクエスト・レスポンス詳細

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025-11-27  
**Status**: Phase 1 Week 3 ステップ計画完了

