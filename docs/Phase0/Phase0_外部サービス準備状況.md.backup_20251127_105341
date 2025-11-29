# Phase 0 外部サービス準備状況

**作成日**: 2025年11月25日  
**バージョン**: v1.0  
**対象**: やどぺら Phase 0（準備期間）外部サービス準備

---

## 1. OpenAI API

### ステータス
✅ **準備完了**

### 設定状況
- **API キー**: `backend/.env`に設定済み
- **使用モデル**: 
  - GPT-4o-mini（チャット応答生成）
  - text-embedding-3-small（埋め込みベクトル生成）

### 確認事項
- [x] OpenAIアカウント作成
- [x] API キー生成
- [x] `backend/.env`に設定
- [ ] 使用量制限設定確認（OpenAIダッシュボードで確認推奨）
- [ ] API キーの有効性確認（Phase 1で実装時に確認）

### 参考リンク
- OpenAI Platform: https://platform.openai.com/
- API ドキュメント: https://platform.openai.com/docs

### 注意事項
- API キーは`.gitignore`で除外されていることを確認済み
- 本番環境では環境変数またはシークレット管理サービスを使用すること

---

## 2. メール送信サービス

### ステータス
⏳ **Phase 1で準備予定**

### 用途
- パスワードリセットメール送信
- エスカレーション通知（オプション）

### 候補サービス
- **SendGrid**: 無料枠あり（100通/日）
- **Mailgun**: 無料枠あり（5,000通/月）
- **AWS SES**: 従量課金

### 実装予定
Phase 1（MVP開発）Week 1-2で実装予定

---

## 3. その他外部サービス

### 分析ツール

**Google Analytics 4（ランディングページ用）**
- ステータス: ⚠️ **実装済み・測定ID未設定（Vercelデプロイ後に設定）**
- 用途: ランディングページのアクセス解析、コンバージョン追跡
- 実装状況:
  - ✅ HTMLにGoogle Analytics 4のgtag.js実装済み
  - ✅ イベントトラッキング実装済み（10種類のイベント）
  - ⏳ 測定ID（G-XXXXXXXXXX）未設定
  - ⏳ Google Analytics 4プロパティ未作成
- 実装時期: Phase 0 ステップ10（2025-11-25）
- **設定時期**: **Vercelデプロイ後**（Phase 0完了後、Phase 1開始前）
- **重要**: 
  - ランディングページは**Vercel**にデプロイ（Render.comではない）
  - Google Analytics設定には実際のURL（https://yadopera.com）が必要
  - Vercelデプロイ後にGoogle Analytics 4プロパティを作成し、測定IDを設定
- 注意事項:
  - 現在は測定IDがプレースホルダー（G-XXXXXXXXXX）のため、データは記録されない
  - デプロイ前でも一時的にlocalhostでプロパティ作成可能（後でURL更新）
  - 詳細は `landing/analytics-setup.md` および `docs/Phase0/Phase0_Render_GoogleAnalytics_設定時期.md` を参照

**Google Analytics（本番アプリ用）**
- ステータス: 未準備
- 用途: 本番アプリのユーザー行動分析、コンバージョン追跡
- 実装予定: Phase 2以降

### エラートラッキング（Phase 2以降）

**Sentry**
- ステータス: 未準備
- 用途: エラー監視、パフォーマンス追跡
- 実装予定: Phase 2以降

### 決済サービス（Phase 4）

**Stripe**
- ステータス: 未準備
- 用途: サブスクリプション決済、従量課金
- 実装予定: Phase 4（本格展開準備）

---

## 4. セキュリティ確認

### 環境変数管理
- ✅ `.env`ファイルは`.gitignore`で除外済み
- ✅ `.env.example`でテンプレート提供
- ⚠️ 本番環境では環境変数またはシークレット管理サービスを使用すること

### API キー管理
- ✅ 開発環境: `backend/.env`に設定
- ⚠️ 本番環境: Render.comの環境変数設定を使用（予定）

---

## 5. 次のステップ

### Phase 1開始前
- [ ] OpenAI API キーの使用量制限設定確認
- [ ] メール送信サービス選択・アカウント作成（Phase 1 Week 1-2）

### Phase 2以降
- [ ] Google Analytics設定
- [ ] Sentry設定
- [ ] Stripeアカウント作成・設定（Phase 4）

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-25  
**Status**: OpenAI API準備完了、その他はPhase 1以降で準備予定

