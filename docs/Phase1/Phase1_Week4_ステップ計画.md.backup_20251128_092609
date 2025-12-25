# Phase 1 Week 4 ステップ計画

**作成日**: 2025年11月27日  
**フェーズ**: Phase 1 Week 4（統合・テスト・ステージング環境構築）  
**期間**: 1週間  
**目的**: MVP開発の最終段階 - API連携、統合テスト、ステージング環境構築

---

## Week 4 目標

Phase 1 Week 4では、以下の目標を達成する：

1. **管理画面API実装**（Week 3でUI実装済み、API連携が必要）
2. **ゲストフィードバックAPI実装**（v0.3新規）
3. **FAQ自動学習API実装**（v0.3新規）
4. **QRコード生成API実装**
5. **Week 2のテストコード作成**（未実施、必須）
6. **統合テスト・E2Eテスト**
7. **ステージング環境構築・デプロイ**（Render.com Pro + Railway Hobby）

---

## 前提条件

### Phase 1 Week 1-3完了確認

- [x] Phase 1 Week 1: バックエンド基盤構築完了
- [x] Phase 1 Week 2: AI対話エンジン実装完了（テスト未実施）
- [x] Phase 1 Week 3: フロントエンド実装完了（API連携はモック）

### 必要な環境変数

`backend/.env`に以下が設定されていること：
- `DATABASE_URL`: PostgreSQL接続URL
- `REDIS_URL`: Redis接続URL
- `OPENAI_API_KEY`: OpenAI APIキー（必須）
- `SECRET_KEY`: JWT署名用シークレットキー

### 必要なバックエンドAPI（Week 4で実装）

- ⏳ `POST /api/v1/chat/feedback` - ゲストフィードバック送信（v0.3新規）
- ⏳ `GET /api/v1/admin/dashboard` - ダッシュボードデータ取得
- ⏳ `GET/POST/PUT/DELETE /api/v1/admin/faqs` - FAQ管理
- ⏳ `GET /api/v1/admin/faq-suggestions` - FAQ追加提案一覧（v0.3新規）
- ⏳ `POST /api/v1/admin/faq-suggestions/{id}/approve` - 提案承認（v0.3新規）
- ⏳ `POST /api/v1/admin/faq-suggestions/{id}/reject` - 提案却下（v0.3新規）
- ⏳ `GET /api/v1/admin/overnight-queue` - 夜間対応キュー取得（v0.3新規）
- ⏳ `GET /api/v1/admin/feedback-stats` - フィードバック統計取得（v0.3新規）
- ⏳ `POST /api/v1/admin/qr-code` - QRコード生成

---

## ステップ詳細

### ステップ1: ゲストフィードバックAPI実装（3時間）

**目的**: ゲストフィードバック送信APIを実装（v0.3新規）

**実装内容**:
1. `backend/app/api/v1/chat.py`更新
   - `POST /api/v1/chat/feedback`エンドポイント追加
   - リクエストバリデーション
   - フィードバック保存処理

2. `backend/app/services/chat_service.py`更新
   - `save_feedback()`: フィードバック保存処理
   - 低評価回答の自動ハイライト判定（2回以上）

3. `backend/app/schemas/chat.py`更新
   - `FeedbackRequest`: フィードバック送信リクエストスキーマ
   - `FeedbackResponse`: フィードバック送信レスポンススキーマ

4. `frontend/src/api/chat.ts`更新
   - `sendFeedback()`: フィードバック送信API呼び出し

5. `frontend/src/components/guest/FeedbackButtons.vue`更新
   - API連携実装（モックから実APIへ）

**確認項目**:
- [ ] フィードバック送信APIが正常に動作する
- [ ] 低評価回答の自動ハイライトが正しく動作する
- [ ] フロントエンドからAPI連携が正常に動作する

**参考**: 要約定義書 3.1 ゲスト側機能（回答後フィードバック）

---

### ステップ2: ダッシュボードAPI実装（4時間）

**目的**: ダッシュボードデータ取得APIを実装

**実装内容**:
1. `backend/app/api/v1/admin/dashboard.py`作成
   - `GET /api/v1/admin/dashboard`エンドポイント
   - JWT認証必須
   - 週次サマリー取得

2. `backend/app/services/dashboard_service.py`作成
   - `DashboardService`クラス実装
   - `get_weekly_summary()`: 週次サマリー取得
     - 総質問数
     - カテゴリ別円グラフデータ
     - TOP5質問
     - 未解決数
     - 自動応答率
   - `get_recent_chat_history()`: リアルタイムチャット履歴（最新10件）
   - `get_overnight_queue()`: 夜間対応キュー取得（v0.3新規）
   - `get_feedback_stats()`: フィードバック統計取得（v0.3新規）

3. `backend/app/schemas/dashboard.py`作成
   - `DashboardResponse`: ダッシュボードレスポンススキーマ

4. `frontend/src/api/dashboard.ts`作成
   - `getDashboard()`: ダッシュボードデータ取得API呼び出し

5. `frontend/src/views/admin/Dashboard.vue`更新
   - API連携実装（モックから実APIへ）

**確認項目**:
- [ ] ダッシュボードAPIが正常に動作する
- [ ] 週次サマリーが正しく取得される
- [ ] リアルタイムチャット履歴が正しく取得される
- [ ] 夜間対応キューが正しく取得される
- [ ] フィードバック統計が正しく取得される
- [ ] フロントエンドからAPI連携が正常に動作する

**参考**: 要約定義書 3.2 宿側機能（ダッシュボード）

---

### ステップ3: FAQ管理API実装（4時間）

**目的**: FAQ管理APIを実装

**実装内容**:
1. `backend/app/api/v1/admin/faqs.py`作成
   - `GET /api/v1/admin/faqs`: FAQ一覧取得
   - `POST /api/v1/admin/faqs`: FAQ作成
   - `PUT /api/v1/admin/faqs/{faq_id}`: FAQ更新
   - `DELETE /api/v1/admin/faqs/{faq_id}`: FAQ削除
   - JWT認証必須

2. `backend/app/services/faq_service.py`作成
   - `FAQService`クラス実装
   - `get_faqs()`: FAQ一覧取得
   - `create_faq()`: FAQ作成（埋め込みベクトル自動生成）
   - `update_faq()`: FAQ更新（埋め込みベクトル自動再生成）
   - `delete_faq()`: FAQ削除

3. `backend/app/schemas/faq.py`作成
   - `FAQRequest`: FAQ作成・更新リクエストスキーマ
   - `FAQResponse`: FAQレスポンススキーマ
   - `FAQListResponse`: FAQ一覧レスポンススキーマ

4. `frontend/src/api/faq.ts`作成
   - `getFaqs()`: FAQ一覧取得
   - `createFaq()`: FAQ作成
   - `updateFaq()`: FAQ更新
   - `deleteFaq()`: FAQ削除

5. `frontend/src/views/admin/FaqManagement.vue`更新
   - API連携実装（モックから実APIへ）

**確認項目**:
- [ ] FAQ管理APIが正常に動作する
- [ ] FAQ作成時に埋め込みベクトルが自動生成される
- [ ] FAQ更新時に埋め込みベクトルが自動再生成される
- [ ] フロントエンドからAPI連携が正常に動作する

**参考**: 要約定義書 3.2 宿側機能（FAQ管理）

---

### ステップ4: FAQ自動学習API実装（5時間）

**目的**: FAQ自動学習APIを実装（v0.3新規）

**実装内容**:
1. `backend/app/api/v1/admin/faq_suggestions.py`作成
   - `GET /api/v1/admin/faq-suggestions`: FAQ追加提案一覧取得
   - `POST /api/v1/admin/faq-suggestions/{id}/approve`: 提案承認
   - `POST /api/v1/admin/faq-suggestions/{id}/reject`: 提案却下
   - JWT認証必須

2. `backend/app/services/faq_suggestion_service.py`作成
   - `FAQSuggestionService`クラス実装
   - `get_suggestions()`: FAQ追加提案一覧取得
   - `generate_suggestion()`: FAQ追加提案生成（GPT-4o mini）
     - 質問文自動入力
     - 回答文テンプレート自動生成
     - カテゴリ自動推定
   - `approve_suggestion()`: 提案承認（FAQ作成）
   - `reject_suggestion()`: 提案却下

3. `backend/app/schemas/faq_suggestion.py`作成
   - `FAQSuggestionResponse`: FAQ追加提案レスポンススキーマ
   - `ApproveSuggestionRequest`: 提案承認リクエストスキーマ

4. `frontend/src/api/faqSuggestion.ts`作成
   - `getSuggestions()`: FAQ追加提案一覧取得
   - `approveSuggestion()`: 提案承認
   - `rejectSuggestion()`: 提案却下

5. `frontend/src/components/admin/FaqSuggestionCard.vue`更新
   - API連携実装（モックから実APIへ）

6. `frontend/src/components/admin/FeedbackLinkedFaqs.vue`更新
   - 「FAQ改善提案」ボタンAPI連携実装

**確認項目**:
- [ ] FAQ自動学習APIが正常に動作する
- [ ] 回答文テンプレート自動生成が正常に動作する
- [ ] カテゴリ自動推定が正常に動作する
- [ ] 提案承認・却下が正常に動作する
- [ ] フロントエンドからAPI連携が正常に動作する

**参考**: 要約定義書 3.2 宿側機能（FAQ自動学習機能）

---

### ステップ5: 夜間対応キューAPI実装（3時間）

**目的**: 夜間対応キューAPIを実装（v0.3新規）

**実装内容**:
1. `backend/app/api/v1/admin/overnight_queue.py`作成
   - `GET /api/v1/admin/overnight-queue`: 夜間対応キュー取得
   - `POST /api/v1/admin/overnight-queue/{id}/process`: 手動実行処理（MVP期間中）
   - JWT認証必須

2. `backend/app/services/overnight_queue_service.py`更新
   - `get_overnight_queue()`: 夜間対応キュー取得
   - `process_scheduled_notifications()`: 翌朝8:00の一括通知処理（手動実行）

3. `backend/app/schemas/overnight_queue.py`更新
   - `OvernightQueueResponse`: 夜間対応キューレスポンススキーマ

4. `frontend/src/api/overnightQueue.ts`作成
   - `getOvernightQueue()`: 夜間対応キュー取得
   - `processNotifications()`: 手動実行処理

5. `frontend/src/views/admin/OvernightQueue.vue`更新
   - API連携実装（モックから実APIへ）

**確認項目**:
- [ ] 夜間対応キューAPIが正常に動作する
- [ ] 手動実行処理が正常に動作する
- [ ] フロントエンドからAPI連携が正常に動作する

**参考**: 要約定義書 3.2 宿側機能（ダッシュボード - 夜間対応キュー）

---

### ステップ6: QRコード生成API実装（4時間）

**目的**: QRコード生成APIを実装

**実装内容**:
1. `backend/app/api/v1/admin/qr_code.py`作成
   - `POST /api/v1/admin/qr-code`: QRコード生成
   - JWT認証必須

2. `backend/app/services/qr_code_service.py`作成
   - `QRCodeService`クラス実装
   - `generate_qr_code()`: QRコード生成
     - 設置場所別URL生成
     - セッション統合トークン埋め込みオプション対応（v0.3新規）
     - PDF/PNG/SVG形式生成
     - S3保存（Phase 2で実装、MVP期間中はローカル保存）

3. `backend/app/schemas/qr_code.py`作成
   - `QRCodeRequest`: QRコード生成リクエストスキーマ
   - `QRCodeResponse`: QRコード生成レスポンススキーマ

4. `frontend/src/api/qrcode.ts`作成
   - `generateQRCode()`: QRコード生成API呼び出し

5. `frontend/src/views/admin/QRCodeGenerator.vue`更新
   - API連携実装（モックから実APIへ）

**確認項目**:
- [ ] QRコード生成APIが正常に動作する
   - [ ] セッション統合トークン埋め込みオプションが正常に動作する
   - [ ] PDF/PNG/SVG形式生成が正常に動作する
   - [ ] フロントエンドからAPI連携が正常に動作する

**参考**: 要約定義書 3.2 宿側機能（QRコード発行）

---

### ステップ7: Week 2のテストコード作成（8-12時間）⚠️ 必須

**目的**: Week 2で実装した機能のテストコードを作成（未実施、必須）

**実装内容**:
1. `backend/tests/test_ai_engine.py`作成
   - RAG統合型AI対話エンジンテスト
   - 埋め込みベクトル生成テスト
   - pgvector検索テスト
   - 信頼度スコア計算テスト

2. `backend/tests/test_embeddings.py`作成
   - 埋め込みベクトル生成テスト
   - FAQ埋め込み生成テスト

3. `backend/tests/test_vector_search.py`作成
   - pgvector検索テスト
   - 類似FAQ検索テスト
   - 類似パターン検索テスト

4. `backend/tests/test_confidence.py`作成
   - 信頼度スコア計算テスト
   - v0.3改善版の全要素テスト

5. `backend/tests/test_safety_check.py`作成
   - 安全カテゴリ判定テスト
   - 医療・安全キーワード検出テスト

6. `backend/tests/test_chat.py`作成
   - チャットメッセージ送信テスト
   - 会話履歴取得テスト

7. `backend/tests/test_chat_service.py`作成
   - チャットサービス統合テスト
   - セッション管理テスト
   - エスカレーション処理テスト
   - 夜間対応キュー処理テスト

8. `backend/tests/test_escalation.py`作成
   - エスカレーション判定テスト
   - エスカレーションスケジュール連動テスト
   - タイムゾーン処理テスト

9. `backend/tests/test_overnight_queue.py`作成
   - 夜間対応キュー処理テスト
   - タイムゾーン基準の翌朝8:00計算テスト

10. `backend/tests/test_chat_api.py`作成
    - チャットAPIエンドポイントテスト
    - 会話履歴取得APIテスト

**確認項目**:
- [ ] テストが正常に実行される
- [ ] テストカバレッジが適切である（最低60%以上）
- [ ] 全テストが通過する
- [ ] エッジケースもテストされている

**参考**: 
- `docs/Phase1/Phase1_Week2_テスト実施計画.md`
- `docs/Phase1/Phase1_Week2_引き継ぎ事項.md`

---

### ステップ8: 統合テスト・E2Eテスト（6時間）

**目的**: フロントエンド・バックエンド統合テストとE2Eテストを実施

**実装内容**:
1. `backend/tests/test_integration.py`作成
   - フロントエンド・バックエンド統合テスト
   - 認証フローテスト
   - チャットフローテスト
   - 管理画面フローテスト

2. `frontend/tests/e2e/`ディレクトリ作成（オプション）
   - E2Eテスト（Playwright等を使用）
   - ゲスト側フローテスト
   - 管理画面フローテスト

3. 手動テスト実施
   - 全機能の動作確認
   - エラーハンドリング確認
   - レスポンス速度確認

**確認項目**:
- [ ] 統合テストが正常に実行される
- [ ] E2Eテストが正常に実行される（オプション）
- [ ] 全機能が正常に動作する
- [ ] エラーハンドリングが適切に動作する
- [ ] レスポンス速度が適切である（目標: 3秒以内）

**参考**: アーキテクチャ設計書 15. パフォーマンス要件

---

### ステップ9: ステージング環境構築・デプロイ（6時間）

**目的**: ステージング環境を構築し、デプロイする（Render.com Pro + Railway Hobby）

**実装内容**:
1. `develop`ブランチ作成
   ```bash
   git checkout -b develop
   git push -u origin develop
   ```

2. Render.com Pro設定
   - Web Service作成（ステージング）
   - 環境変数設定
   - 自動デプロイ設定（`develop`ブランチ）

3. Railway Hobby設定
   - PostgreSQLサービス追加（既存契約、追加料金なし）
   - Redisサービス追加（既存契約、追加料金なし）
   - 接続設定確認

4. 環境変数設定
   - `DATABASE_URL`: Railway Hobby PostgreSQL接続URL
   - `REDIS_URL`: Railway Hobby Redis接続URL
   - `OPENAI_API_KEY`: OpenAI APIキー
   - `SECRET_KEY`: JWT署名用シークレットキー
   - `CORS_ORIGINS`: フロントエンドURL

5. デプロイ確認
   - バックエンドデプロイ確認
   - フロントエンドデプロイ確認（Vercel等）
   - 動作確認

**確認項目**:
- [ ] `develop`ブランチが作成されている
- [ ] Render.com Pro Web Serviceが作成されている
- [ ] Railway Hobby PostgreSQL・Redisが設定されている
- [ ] 環境変数が正しく設定されている
- [ ] デプロイが正常に完了している
- [ ] ステージング環境で動作確認が完了している

**参考**: 
- 要約定義書 7. 開発スケジュール（Phase 1 Week 4）
- アーキテクチャ設計書 14. デプロイメント

---

### ステップ10: レスポンス速度最適化（3時間）

**目的**: レスポンス速度を最適化（目標: 3秒以内）

**実装内容**:
1. キャッシュ最適化
   - Redisキャッシュ活用強化
   - 頻出FAQキャッシュ

2. データベースクエリ最適化
   - インデックス確認
   - N+1問題の解消

3. 非同期処理最適化
   - async/awaitの適切な使用
   - 並列処理の活用

4. パフォーマンステスト
   - レスポンス時間測定
   - ボトルネック特定

**確認項目**:
- [ ] レスポンス速度が3秒以内である
- [ ] キャッシュが適切に動作している
- [ ] データベースクエリが最適化されている
- [ ] 非同期処理が適切に実装されている

**参考**: アーキテクチャ設計書 15. パフォーマンス要件

---

### ステップ11: エラーハンドリング強化（2時間）

**目的**: エラーハンドリングを強化し、ユーザー体験を向上

**実装内容**:
1. フロントエンドエラーハンドリング強化
   - APIエラーの適切な表示
   - ネットワークエラーの処理
   - タイムアウト処理

2. バックエンドエラーハンドリング強化
   - 統一されたエラーレスポンス形式
   - 適切なHTTPステータスコード
   - エラーログ記録

3. ユーザーフレンドリーなエラーメッセージ
   - 多言語対応（英語・日本語）
   - 分かりやすいエラーメッセージ

**確認項目**:
- [ ] エラーハンドリングが適切に実装されている
- [ ] エラーメッセージが分かりやすい
- [ ] エラーログが適切に記録されている

**参考**: アーキテクチャ設計書 13. エラーハンドリング

---

### ステップ12: ドキュメント更新（2時間）

**目的**: 実装完了後のドキュメントを更新

**実装内容**:
1. `README.md`更新
   - セットアップ手順更新
   - デプロイ手順追加

2. API仕様書更新
   - Swagger UI確認
   - 新規APIエンドポイント追加

3. 引き継ぎ書作成
   - `docs/Phase1/Phase1_Week4_引き継ぎ書.md`作成
   - 実装完了状況
   - 次のステップ（Phase 2）

**確認項目**:
- [ ] README.mdが更新されている
- [ ] API仕様書が更新されている
- [ ] 引き継ぎ書が作成されている

---

## 実装順序の推奨

1. **ステップ1**: ゲストフィードバックAPI実装（基盤）
2. **ステップ2**: ダッシュボードAPI実装（管理画面基盤）
3. **ステップ3**: FAQ管理API実装（FAQ機能基盤）
4. **ステップ4**: FAQ自動学習API実装（v0.3新規機能）
5. **ステップ5**: 夜間対応キューAPI実装（v0.3新規機能）
6. **ステップ6**: QRコード生成API実装（QRコード機能）
7. **ステップ7**: Week 2のテストコード作成（品質保証、必須）
8. **ステップ8**: 統合テスト・E2Eテスト（品質保証）
9. **ステップ9**: ステージング環境構築・デプロイ（デプロイ）
10. **ステップ10**: レスポンス速度最適化（パフォーマンス）
11. **ステップ11**: エラーハンドリング強化（品質向上）
12. **ステップ12**: ドキュメント更新（ドキュメント）

---

## 各ステップの工数見積もり

| ステップ | 工数 | 累計工数 |
|---------|------|---------|
| ステップ1: ゲストフィードバックAPI実装 | 3時間 | 3時間 |
| ステップ2: ダッシュボードAPI実装 | 4時間 | 7時間 |
| ステップ3: FAQ管理API実装 | 4時間 | 11時間 |
| ステップ4: FAQ自動学習API実装 | 5時間 | 16時間 |
| ステップ5: 夜間対応キューAPI実装 | 3時間 | 19時間 |
| ステップ6: QRコード生成API実装 | 4時間 | 23時間 |
| ステップ7: Week 2のテストコード作成 | 8-12時間 | 31-35時間 |
| ステップ8: 統合テスト・E2Eテスト | 6時間 | 37-41時間 |
| ステップ9: ステージング環境構築・デプロイ | 6時間 | 43-47時間 |
| ステップ10: レスポンス速度最適化 | 3時間 | 46-50時間 |
| ステップ11: エラーハンドリング強化 | 2時間 | 48-52時間 |
| ステップ12: ドキュメント更新 | 2時間 | 50-54時間 |

**合計**: 約50-54時間（1週間で実装可能）

---

## 実装時の注意事項

### 1. API連携

- Week 3で実装済みのUIコンポーネントにAPI連携を追加
- モックデータから実APIへの移行
- エラーハンドリングの実装

### 2. テストコード

- Week 2のテスト未実施は重大なリスク
- 必ず実施すること（ステップ7）
- テストカバレッジ60%以上を目標

### 3. ステージング環境

- Render.com Pro + Railway Hobby構成
- `develop`ブランチで自動デプロイ
- 環境変数の適切な設定

### 4. パフォーマンス

- レスポンス速度3秒以内を目標
- キャッシュ活用
- データベースクエリ最適化

### 5. エラーハンドリング

- 統一されたエラーレスポンス形式
- ユーザーフレンドリーなエラーメッセージ
- 適切なログ記録

---

## 完了基準

Week 4完了の基準：

- [ ] ゲストフィードバックAPIが正常に動作する
- [ ] ダッシュボードAPIが正常に動作する
- [ ] FAQ管理APIが正常に動作する
- [ ] FAQ自動学習APIが正常に動作する
- [ ] 夜間対応キューAPIが正常に動作する
- [ ] QRコード生成APIが正常に動作する
- [ ] Week 2のテストコードが作成され、全テストが通過する
- [ ] 統合テスト・E2Eテストが正常に実行される
- [ ] ステージング環境が構築され、デプロイが完了している
- [ ] レスポンス速度が3秒以内である
- [ ] エラーハンドリングが適切に実装されている
- [ ] ドキュメントが更新されている

---

## 次のステップ（Phase 2）

Week 4完了後、Phase 2（PoC準備）に進む：

- やどびとユーザーへのメールDM作成・送信
- オンライン説明会準備
- PoC施設選定（3施設、品質重視）
- 初期FAQ作成支援
- 利用マニュアル作成
- 専用Slackチャンネル作成

---

## 参考資料

### 主要ドキュメント

- **要約定義書**: `docs/Summary/yadopera-v03-summary.md`
- **アーキテクチャ設計書**: `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`
- **Phase 0引き継ぎ書**: `docs/Phase0_引き継ぎ書.md`
- **Phase 1 Week 1ステップ計画**: `docs/Phase1/Phase1_Week1_ステップ計画.md`
- **Phase 1 Week 2ステップ計画**: `docs/Phase1/Phase1_Week2_ステップ計画.md`
- **Phase 1 Week 2テスト実施計画**: `docs/Phase1/Phase1_Week2_テスト実施計画.md`
- **Phase 1 Week 3ステップ計画**: `docs/Phase1/Phase1_Week3_ステップ計画.md`
- **Phase 1 Week 3実装整合性レポート**: `docs/Phase1/Phase1_Week3_実装整合性レポート.md`

### 実装参考セクション

- アーキテクチャ設計書 8.2 RESTful API エンドポイント一覧
- アーキテクチャ設計書 8.3 APIリクエスト・レスポンス詳細
- アーキテクチャ設計書 14. デプロイメント
- アーキテクチャ設計書 15. パフォーマンス要件

---

**Document Version**: v1.0  
**Author**: AI Assistant  
**Last Updated**: 2025-11-27  
**Status**: Phase 1 Week 4 ステップ計画完了

