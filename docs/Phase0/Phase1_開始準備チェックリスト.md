# Phase 1 開始準備チェックリスト

**作成日**: 2025年11月27日  
**目的**: Phase 1（MVP開発）開始前の準備確認

---

## Phase 0完了確認

### ✅ Phase 0完了（16/16ステップ、100%）

- [x] ステップ1-9: 環境構築、外部サービス準備（9ステップ）
- [x] ステップ10-1: ランディングページ実装・改善
- [x] ステップ10-2: Vercelデプロイ（後にGitHub Pagesに移行）
- [x] ステップ10-3: カスタムドメイン設定
- [x] ステップ10-4: Google Analytics設定
- [x] ステップ10-5: HTMLに測定ID設定
- [x] ステップ10-6: 動作確認
- [x] ステップ10-7: GitHub Pages移行
- [x] ステップ11: やどびと多言語優先度アンケート実施

---

## Phase 1開始前の準備事項

### 必須項目

- [x] ランディングページ公開完了（`https://yadopera.com`）
- [x] やどびと多言語優先度アンケート配信完了（結果集計はPhase 1中）
- [ ] `develop`ブランチ作成（Phase 1 Week 4でステージング環境構築のため）

### 推奨項目

- [ ] Vercelプロジェクト削除（`docs/Phase0/Phase0_ステップ10-7_Vercel後処理手順.md`参照）
- [ ] Google Analyticsデータ収集確認（48時間経過後）

---

## `develop`ブランチ作成手順

### ステップ1: ブランチ作成

```bash
cd /Users/kurinobu/projects/yadopera
git checkout -b develop
git push -u origin develop
```

### ステップ2: 確認

```bash
git branch -a
# develop ブランチが表示されることを確認
```

---

## Phase 1概要

### 期間: 4週間

### Week 1: バックエンド基盤

- FastAPI プロジェクト初期化
- PostgreSQL 接続（pgvector拡張）
- JWT認証システム
- 基本テーブル実装
- セッション統合トークンAPI実装

### Week 2: AI対話エンジン

- OpenAI API 統合
- RAG実装
- 信頼度スコア改善版実装
- 安全カテゴリ強制エスカレーション実装
- 夜間対応キュー実装
- フォールバック文言実装

### Week 3: フロントエンド

- Vue.js プロジェクト初期化
- ゲスト側UI（PWA、ダークモード）
- ゲストフィードバックUI（👍👎）
- セッション統合トークン表示・入力UI
- 管理画面（ダッシュボード）
- FAQ自動学習UI（ワンクリック追加）
- 夜間対応キューUI

### Week 4: 統合・テスト・ステージング環境構築

- エンドツーエンドテスト
- レスポンス速度最適化
- エラーハンドリング
- QRコード生成機能
- ステージング環境構築・デプロイ（Render.com Pro + Railway Hobby）
  - `develop`ブランチ作成
  - Render.com Pro Web Service作成（ステージング）
  - Railway Hobby PostgreSQLサービス追加（既存契約）
  - Railway Hobby Redisサービス追加（既存契約）
  - Render.com ProからRailway Hobbyへの接続設定
  - 環境変数設定
  - ステージング環境デプロイ確認

---

## 参考資料

- **Phase 0引き継ぎ書**: `docs/Phase0/Phase0_引き継ぎ書.md`
- **Phase 0進捗状況**: `docs/Phase0/Phase0_進捗状況.md`
- **Phase 0完了報告書**: `docs/Phase0/Phase0_完了報告書.md`
- **要約定義書**: `docs/Summary/yadopera-v03-summary.md`
- **アーキテクチャ設計書**: `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27  
**Status**: Phase 1開始準備完了

