# Phase 1 ステージング環境テスト計画

**作成日**: 2025年11月29日  
**対象**: Phase 1（MVP開発）ステージング環境でのテスト実行  
**目的**: Phase 1完了のためのステージング環境でのテスト実行計画を立案  
**実施時期**: Phase 1 Week 4完了前（Phase 1完了の必須条件）

---

## 1. テストの目的と範囲

### 1.1 テストの目的

**Phase 1完了の必須条件を満たすため**、ステージング環境でテストを実行し、すべてのテストがパスすることを確認する。

**具体的な目的**:
1. ステージング環境（Railway PostgreSQL + Render.com）での動作確認
2. 本番環境に近い環境でのテスト実行
3. pgvector拡張を含むPostgreSQL環境でのテスト実行
4. すべてのテストが正常に動作することを確認
5. Phase 1完了判定のための証跡作成

### 1.2 テストの範囲

**対象テスト**:
- ✅ 既存の全テストファイル（12ファイル）
- ✅ 単体テスト（Unit Tests）
- ✅ 統合テスト（Integration Tests）
- ✅ APIテスト（API Tests）

**対象機能**:
- 認証機能（ログイン、ログアウト）
- AI対話エンジン（RAG統合型）
- 埋め込みベクトル生成
- pgvector検索
- 信頼度スコア計算
- 安全カテゴリ判定
- エスカレーション判定
- 夜間対応キュー処理
- チャットサービス
- チャットAPI
- セッション統合トークン
- 統合フロー（認証、チャット、管理画面）

**対象外**:
- E2Eテスト（フロントエンド連携、Phase 2で実装予定）
- パフォーマンステスト（別途実施予定）
- 負荷テスト（別途実施予定）

---

## 2. テスト環境の設定

### 2.1 ステージング環境の構成

**データベース**:
- **サービス**: Railway Hobby PostgreSQL（pgvector-pg18）
- **バージョン**: PostgreSQL 18.1
- **拡張**: pgvector 0.8.1（有効化済み）
- **接続URL**: Railwayダッシュボードから取得

**Redis**:
- **サービス**: Railway Hobby Redis
- **接続URL**: Railwayダッシュボードから取得

**バックエンド**:
- **サービス**: Render.com Web Service（`yadopera-backend-staging`）
- **URL**: `https://yadopera-backend-staging.onrender.com`
- **ブランチ**: `develop`
- **ステータス**: ✅ デプロイ成功（2025-11-29）

### 2.2 テスト実行環境

**実行方法**: ローカル環境からステージング環境のデータベースに接続（推奨）

**理由**:
- テスト実行の柔軟性が高い
- テスト結果の確認が容易
- デバッグが容易
- テスト実行時間の制御が可能

**代替方法**: Render.comのシェル機能を使用（オプション）

---

## 3. テスト環境の準備

### 3.1 前提条件の確認

**完了済み項目**:
- ✅ Railway PostgreSQL作成完了
- ✅ Railway pgvector拡張有効化完了（2025-11-29）
- ✅ Railway Redis作成完了
- ✅ Render.com Web Service作成完了
- ✅ Render.com 環境変数設定完了
- ✅ Render.com デプロイ成功（2025-11-29）
- ✅ ステージング環境動作確認完了（2025-11-29）

**確認が必要な項目**:
- [ ] Railway PostgreSQL接続情報の取得
- [ ] Railway Redis接続情報の取得
- [ ] ローカル環境での環境変数設定
- [ ] テスト用データベースの準備（オプション）

### 3.2 接続情報の取得手順

#### ステップ1: Railway PostgreSQL接続情報の取得

1. Railwayダッシュボードにアクセス: https://railway.app
2. プロジェクトを選択
3. PostgreSQLサービスを選択
4. 「Variables」タブで接続情報を確認:
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`
5. または、「Connect」タブで接続URLを取得:
   - `postgresql://user:password@host:port/database`

#### ステップ2: Railway Redis接続情報の取得

1. RailwayダッシュボードでRedisサービスを選択
2. 「Variables」タブで接続情報を確認:
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `REDIS_PASSWORD`
3. または、「Connect」タブで接続URLを取得:
   - `redis://default:password@host:port`

### 3.3 環境変数の設定

**ローカル環境での環境変数設定**:

```bash
cd /Users/kurinobu/projects/yadopera/backend

# ステージング環境のデータベース接続情報を設定
export DATABASE_URL="postgresql://postgres:password@host:port/database"
export REDIS_URL="redis://default:password@host:port"

# その他の環境変数（既存の値を使用）
export OPENAI_API_KEY="your_openai_api_key"
export SECRET_KEY="your_secret_key"
export CORS_ORIGINS="http://localhost:5173"

# PostgreSQLテスト環境を有効化
export USE_POSTGRES_TEST="true"

# OpenAI APIモックを使用（高速・低コスト）
export USE_OPENAI_MOCK="true"
```

**注意事項**:
- `DATABASE_URL`は`postgresql://`形式を使用（`postgresql+asyncpg://`ではない）
- `USE_POSTGRES_TEST=true`を設定することで、PostgreSQL + pgvectorテスト環境が有効化される
- `USE_OPENAI_MOCK=true`を設定することで、OpenAI APIのモックが使用される（高速・低コスト）

---

## 4. 実行するテストの種類と内容

### 4.1 テストファイル一覧

**既存のテストファイル（12ファイル）**:

1. **`test_auth.py`** - 認証APIテスト
   - ログイン成功テスト
   - ログイン失敗テスト（無効なメールアドレス、無効なパスワード）
   - 非アクティブユーザーのログインテスト

2. **`test_ai_engine.py`** - RAG統合型AI対話エンジンテスト
   - メッセージ処理成功テスト
   - 埋め込みベクトル生成統合テスト
   - pgvector検索統合テスト
   - エラーハンドリングテスト

3. **`test_confidence.py`** - 信頼度スコア計算テスト
   - 基本信頼度スコアテスト
   - FAQ類似度ボーナス計算テスト
   - 回答長ペナルティ計算テスト
   - 不確実性ワード検出テスト
   - 質問具体性スコア計算テスト（v0.3新規）
   - 過去解決率計算テスト（v0.3新規）
   - 施設カスタムFAQヒット判定テスト（v0.3新規）

4. **`test_embeddings.py`** - 埋め込みベクトル生成テスト
   - `generate_embedding()`の正常動作テスト
   - `generate_faq_embedding()`の正常動作テスト
   - エラーハンドリングテスト（OpenAI API障害時）

5. **`test_vector_search.py`** - pgvector検索テスト
   - `search_similar_faqs()`の正常動作テスト
   - `search_similar_patterns()`の正常動作テスト
   - コサイン類似度計算の正確性テスト
   - 類似度閾値フィルタリングテスト
   - Top K取得の正確性テスト
   - **注意**: PostgreSQL環境でのみ実行可能（SQLiteではスキップ）

6. **`test_escalation.py`** - エスカレーション判定テスト
   - `check_escalation_needed()`の正常動作テスト
   - 信頼度 < 閾値判定テスト
   - 緊急キーワード検出テスト
   - 3往復以上未解決チェックテスト
   - 安全カテゴリ即エスカレーションテスト
   - エスカレーションスケジュール連動テスト

7. **`test_overnight_queue.py`** - 夜間対応キュー処理テスト
   - `add_to_overnight_queue()`の正常動作テスト
   - `send_overnight_auto_reply()`の正常動作テスト
   - `process_scheduled_notifications()`の正常動作テスト
   - 施設タイムゾーン基準の翌朝8:00計算テスト
   - 夜間時間帯判定テスト（22:00-8:00）

8. **`test_safety_check.py`** - 安全カテゴリ判定テスト
   - `check_safety_category()`の正常動作テスト
   - 医療関連キーワード検出テスト
   - 安全・避難関連キーワード検出テスト
   - 大文字小文字を区別しない検出テスト
   - 多言語対応テスト（英語・日本語）

9. **`test_chat_service.py`** - チャットサービス統合テスト
   - `process_chat_message()`の正常動作テスト
   - セッション管理の統合テスト
   - RAG統合型AI対話エンジン呼び出しテスト
   - エスカレーション処理の統合テスト
   - 夜間対応キュー処理の統合テスト

10. **`test_chat_api.py`** - チャットAPIエンドポイントテスト
    - `POST /api/v1/chat`の正常動作テスト
    - `GET /api/v1/chat/history/{session_id}`の正常動作テスト
    - リクエストバリデーションテスト
    - エラーハンドリングテスト

11. **`test_session_token.py`** - セッション統合トークンテスト
    - トークン生成テスト
    - トークン検証テスト
    - セッション統合テスト

12. **`test_integration.py`** - 統合テスト
    - 認証フローテスト
    - チャットフローテスト
    - 管理画面フローテスト（ダッシュボード、FAQ、FAQ提案、夜間対応キュー、QRコード）
    - エラーハンドリングテスト
    - レスポンス速度テスト

### 4.2 テスト実行の順序

**推奨実行順序**:

1. **単体テスト（Unit Tests）** - 基盤機能のテスト
   - `test_embeddings.py` - 埋め込みベクトル生成
   - `test_vector_search.py` - pgvector検索（PostgreSQL環境必須）
   - `test_confidence.py` - 信頼度スコア計算
   - `test_safety_check.py` - 安全カテゴリ判定
   - `test_escalation.py` - エスカレーション判定
   - `test_overnight_queue.py` - 夜間対応キュー処理

2. **統合テスト（Integration Tests）** - 機能統合のテスト
   - `test_ai_engine.py` - RAG統合型AI対話エンジン
   - `test_chat_service.py` - チャットサービス統合

3. **APIテスト（API Tests）** - APIエンドポイントのテスト
   - `test_auth.py` - 認証API
   - `test_chat_api.py` - チャットAPI
   - `test_session_token.py` - セッション統合トークンAPI

4. **統合フローテスト（Integration Flow Tests）** - エンドツーエンドフローのテスト
   - `test_integration.py` - 統合フローテスト

**理由**:
- 単体テストから統合テストへ段階的に実行することで、問題の特定が容易
- 基盤機能のテストが成功してから、上位レイヤーのテストを実行
- エンドツーエンドフローテストは最後に実行し、全体の動作確認を行う

---

## 5. テスト実行方法

### 5.1 全テスト実行

**コマンド**:
```bash
cd /Users/kurinobu/projects/yadopera/backend

# 環境変数を設定（上記の「3.3 環境変数の設定」を参照）
export DATABASE_URL="postgresql://..."
export REDIS_URL="redis://..."
export USE_POSTGRES_TEST="true"
export USE_OPENAI_MOCK="true"

# 全テスト実行（詳細出力）
pytest tests/ -v
```

**期待される結果**:
- すべてのテストがパスする
- エラーがない
- 警告が最小限である

### 5.2 カテゴリ別テスト実行

**単体テストのみ実行**:
```bash
pytest tests/test_embeddings.py tests/test_vector_search.py tests/test_confidence.py tests/test_safety_check.py tests/test_escalation.py tests/test_overnight_queue.py -v
```

**統合テストのみ実行**:
```bash
pytest tests/test_ai_engine.py tests/test_chat_service.py -v
```

**APIテストのみ実行**:
```bash
pytest tests/test_auth.py tests/test_chat_api.py tests/test_session_token.py -v
```

**統合フローテストのみ実行**:
```bash
pytest tests/test_integration.py -v
```

### 5.3 特定のテストファイル実行

**例: pgvector検索テストのみ実行**:
```bash
pytest tests/test_vector_search.py -v
```

**例: 認証APIテストのみ実行**:
```bash
pytest tests/test_auth.py -v
```

### 5.4 テスト結果の記録

**テスト結果をファイルに保存**:
```bash
# テキスト形式で保存
pytest tests/ -v > test_results.txt 2>&1

# JSON形式で保存（pytest-json-reportプラグインが必要）
pytest tests/ --json-report --json-report-file=test_results.json

# HTML形式で保存（pytest-htmlプラグインが必要）
pytest tests/ --html=test_results.html --self-contained-html
```

**テストカバレッジの確認**:
```bash
# カバレッジレポート生成
pytest tests/ --cov=app --cov-report=html --cov-report=term

# カバレッジレポートをブラウザで開く
open htmlcov/index.html
```

---

## 6. 成功基準

### 6.1 Phase 1完了のための成功基準

**必須条件**:
1. ✅ **すべてのテストがパスする**
   - エラーがない
   - 失敗がない
   - スキップされたテストが最小限である

2. ✅ **テストカバレッジが適切である**
   - 最低カバレッジ: 60%以上
   - 推奨カバレッジ: 80%以上
   - 重要機能: 100%カバレッジ（RAGエンジン、エスカレーション判定等）

3. ✅ **pgvector検索テストが正常に動作する**
   - PostgreSQL環境でのみ実行可能なテストが正常に動作する
   - pgvector拡張が正しく機能していることを確認

4. ✅ **統合テストが正常に動作する**
   - エンドツーエンドフローが正常に動作する
   - 複数の機能が連携して正常に動作する

### 6.2 テスト結果の評価基準

**合格基準**:
- ✅ すべてのテストがパスする
- ✅ テストカバレッジが60%以上
- ✅ エラーがない
- ✅ 警告が最小限である

**不合格基準**:
- ❌ 1つ以上のテストが失敗する
- ❌ テストカバレッジが60%未満
- ❌ 重大なエラーが発生する
- ❌ pgvector検索テストが失敗する（PostgreSQL環境の問題）

---

## 7. リスクと対策

### 7.1 想定されるリスク

#### リスク1: データベース接続エラー

**内容**: ステージング環境のデータベースに接続できない

**対策**:
- Railwayダッシュボードで接続情報を再確認
- ネットワーク接続を確認
- ファイアウォール設定を確認
- 接続URLの形式を確認（`postgresql://`形式）

#### リスク2: pgvector拡張が有効化されていない

**内容**: pgvector拡張が有効化されていないため、ベクトル検索テストが失敗する

**対策**:
- Railway PostgreSQLでpgvector拡張が有効化されていることを確認
- `SELECT * FROM pg_extension WHERE extname = 'vector';`で確認
- 必要に応じて拡張を有効化: `CREATE EXTENSION IF NOT EXISTS vector;`

#### リスク3: テストデータの競合

**内容**: 複数のテストが同じデータを使用して競合する

**対策**:
- 各テスト関数ごとに新しいセッションを作成（`conftest.py`で実装済み）
- テスト後にデータをクリーンアップ（`conftest.py`で実装済み）
- テスト用のデータベースを作成（オプション）

#### リスク4: OpenAI APIモックの不具合

**内容**: OpenAI APIモックが正しく動作しない

**対策**:
- `USE_OPENAI_MOCK=true`を設定してモックを使用
- モックフィクスチャが正しく動作していることを確認
- 必要に応じてモックの動作を調整

#### リスク5: テスト実行時間の超過

**内容**: テスト実行に時間がかかりすぎる

**対策**:
- テストをカテゴリ別に実行
- 並列実行を検討（`pytest-xdist`プラグイン）
- 不要なテストをスキップ

### 7.2 エラー発生時の対応

**エラー発生時の手順**:
1. エラーメッセージを確認
2. エラーが発生したテストファイルを特定
3. エラーの原因を分析
4. 必要に応じて修正を実施
5. 修正後にテストを再実行
6. テスト結果を記録

**よくあるエラーと対処法**:

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `Connection refused` | データベース接続エラー | 接続情報を確認、ネットワーク接続を確認 |
| `Extension "vector" does not exist` | pgvector拡張が有効化されていない | `CREATE EXTENSION IF NOT EXISTS vector;`を実行 |
| `Table does not exist` | テーブルが作成されていない | Alembicマイグレーションを実行 |
| `ImportError` | モジュールが見つからない | 依存関係を確認、`pip install -r requirements.txt`を実行 |

---

## 8. テスト結果の記録

### 8.1 記録する情報

**必須記録項目**:
1. **テスト実行日時**
2. **テスト実行環境**
   - データベース: Railway PostgreSQL（pgvector-pg18）
   - Redis: Railway Hobby Redis
   - バックエンド: Render.com Web Service
3. **テスト実行結果**
   - 実行したテスト数
   - 成功したテスト数
   - 失敗したテスト数
   - スキップされたテスト数
   - エラー数
4. **テストカバレッジ**
   - 全体カバレッジ率
   - カテゴリ別カバレッジ率
5. **エラー詳細**（エラーが発生した場合）
   - エラーメッセージ
   - エラーが発生したテストファイル
   - エラーの原因と対処法

### 8.2 記録方法

**テスト結果をドキュメントに記録**:
- `docs/Phase1/Phase1_ステージング環境テスト結果.md`を作成
- テスト実行結果を記録
- エラーが発生した場合は、エラー詳細を記録

**テスト結果をファイルに保存**:
```bash
# テキスト形式で保存
pytest tests/ -v > test_results.txt 2>&1

# 日時付きで保存
pytest tests/ -v > test_results_$(date +%Y%m%d_%H%M%S).txt 2>&1
```

---

## 9. テスト実行チェックリスト

### 9.1 テスト実行前の確認

- [ ] Railway PostgreSQL接続情報を取得完了
- [ ] Railway Redis接続情報を取得完了
- [ ] ローカル環境で環境変数を設定完了
- [ ] `USE_POSTGRES_TEST=true`を設定完了
- [ ] `USE_OPENAI_MOCK=true`を設定完了
- [ ] テスト実行環境の準備完了

### 9.2 テスト実行中

- [ ] 単体テストを実行
- [ ] 統合テストを実行
- [ ] APIテストを実行
- [ ] 統合フローテストを実行
- [ ] テスト結果を確認
- [ ] エラーが発生した場合は、エラー詳細を記録

### 9.3 テスト実行後

- [ ] すべてのテストがパスすることを確認
- [ ] テストカバレッジを確認
- [ ] テスト結果を記録
- [ ] エラーが発生した場合は、エラー詳細を記録
- [ ] テスト結果をドキュメントに反映

---

## 10. 次のステップ

### 10.1 テスト実行完了後

**Phase 1完了判定**:
- ✅ すべてのテストがパスすることを確認
- ✅ テスト結果を記録
- ✅ Phase 1完了条件を満たしていることを確認

**ドキュメント更新**:
- `docs/Phase1/Phase1_Week4_実装状況.md`を更新
- `docs/Phase1/Phase1_引き継ぎ書.md`を作成（または更新）
- テスト結果を反映

### 10.2 Phase 2への準備

**Phase 2開始前の準備**:
- Phase 1完了の確認
- PoC準備の開始
- やどびとユーザーリストの準備

---

## 11. まとめ

### 11.1 テスト計画の要点

**目的**: Phase 1完了の必須条件を満たすため、ステージング環境でテストを実行し、すべてのテストがパスすることを確認する。

**実行方法**: ローカル環境からステージング環境のデータベースに接続してテストを実行（推奨）

**成功基準**: 
- すべてのテストがパスする
- テストカバレッジが60%以上
- pgvector検索テストが正常に動作する

**所要時間**: 約1時間（テスト実行 + 結果確認 + 記録）

### 11.2 実行順序

1. **テスト環境の準備**（15分）
   - Railway接続情報の取得
   - 環境変数の設定

2. **テスト実行**（30分）
   - 全テスト実行
   - 結果確認

3. **テスト結果の記録**（15分）
   - テスト結果を記録
   - ドキュメントに反映

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-11-29  
**Status**: Phase 1ステージング環境テスト計画立案完了

