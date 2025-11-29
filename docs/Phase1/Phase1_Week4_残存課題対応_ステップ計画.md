# Phase 1 Week 4 残存課題対応ステップ計画

**作成日**: 2025年11月28日  
**対象**: Phase 1 Week 4の残存課題対応  
**目的**: Render.comデプロイエラー解決、Railway pgvector拡張有効化、ステージング環境動作確認、テスト実行・パス確認

---

## 1. 現状分析

### 1.1 エラーログ分析

**エラー内容**: `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.`

**エラー発生箇所**:
```
File "/opt/render/project/src/backend/alembic/env.py", line 79, in run_migrations_online
    with connectable.connect() as connection:
         ^^^^^^^^^^^^^^^^^^^^^
```

**根本原因**:
1. `alembic/env.py`の`get_url()`関数が`postgresql+asyncpg://`形式のURLを返している
2. `engine_from_config()`は同期エンジンを作成する関数
3. 同期エンジンで`postgresql+asyncpg://`形式のURLを使用しようとすると、`MissingGreenlet`エラーが発生

**確認事項**:
- ✅ `asyncpg==0.29.0`は`requirements.txt`に含まれている（10行目）
- ✅ パッケージのインストールは成功している
- ❌ Alembicが同期エンジンで非同期URLを使用しようとしている

### 1.2 残存課題

#### 課題1: Render.comデプロイエラー（最優先）

**現状**:
- ✅ Web Service作成完了
- ✅ 環境変数設定完了
- ✅ `asyncpg==0.29.0`は`requirements.txt`に含まれている
- ❌ **デプロイ失敗**: `MissingGreenlet`エラー

**原因**:
- `alembic/env.py`で`postgresql+asyncpg://`形式のURLを同期エンジンで使用している

**優先度**: **最高**（Phase 1完了に必須）

#### 課題2: Railway PostgreSQLのpgvector拡張有効化（最優先）

**現状**:
- ✅ PostgreSQLサービス作成完了（pgvector-pg17テンプレート使用）
- ❌ **pgvector拡張が有効化されていない**

**優先度**: **最高**（Phase 1完了に必須）

#### 課題3: ステージング環境での動作確認（最優先）

**現状**:
- ❌ デプロイが失敗しているため、動作確認ができない

**優先度**: **最高**（Phase 1完了に必須）

**前提条件**: 課題1、課題2の解決が必要

#### 課題4: ステージング環境でのテスト実行・パス確認（最優先）

**現状**:
- ❌ デプロイが失敗しているため、テストが実行できない

**優先度**: **最高**（Phase 1完了に必須）

**前提条件**: 課題1、課題2、課題3の解決が必要

---

## 2. ステップ計画

### ステップ1: Render.comデプロイエラー解決（1時間）

**目的**: Alembicが同期エンジンで`postgresql://`形式のURLを使用できるようにする

**実装内容**:
1. `backend/alembic/env.py`の`get_url()`関数を修正
   - `postgresql+asyncpg://`形式のURLを`postgresql://`形式に変換
   - アプリケーション側は`app/database.py`で非同期形式に変換済み（問題なし）

**修正内容**:
```python
def get_url():
    """環境変数からデータベースURLを取得（Alembic用に同期形式に変換）"""
    url = settings.database_url
    # postgresql+asyncpg:// -> postgresql:// に変換（Alembicは同期エンジンを使用）
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url
```

**確認項目**:
- [ ] `alembic/env.py`の`get_url()`関数を修正完了
- [ ] 変更をコミット・プッシュ
- [ ] Render.comで再デプロイ
- [ ] デプロイが成功することを確認
- [ ] Alembicマイグレーションが正常に実行されることを確認

**参考**: `docs/Deployment/Render_デプロイエラー_完全分析レポート.md`

---

### ステップ2: Railway PostgreSQLのpgvector拡張有効化（15分）

**目的**: Railway PostgreSQLにpgvector拡張を有効化する

**実装内容**:
1. Railway CLIを使用してPostgreSQLサービスに接続
2. `CREATE EXTENSION IF NOT EXISTS vector;`を実行
3. 拡張が有効化されたか確認

**手順**:
```bash
# 1. Railway CLIでログイン（未ログインの場合）
railway login

# 2. プロジェクトをリンク
railway link

# 3. PostgreSQLサービスに接続
railway connect postgres

# 4. pgvector拡張を有効化
CREATE EXTENSION IF NOT EXISTS vector;

# 5. 確認
SELECT * FROM pg_extension WHERE extname = 'vector';

# 6. psqlを終了
\q
```

**確認項目**:
- [ ] Railway CLIでログイン完了
- [ ] プロジェクトをリンク完了
- [ ] PostgreSQLサービスに接続完了
- [ ] `CREATE EXTENSION IF NOT EXISTS vector;`実行完了
- [ ] 拡張が有効化されたことを確認（`SELECT * FROM pg_extension WHERE extname = 'vector';`で結果が返る）
- [ ] Alembicマイグレーション（`001_enable_pgvector.py`）が正常に実行されることを確認

**参考**: `docs/Deployment/pgvector拡張有効化_実行手順.md`

---

### ステップ3: Render.comデプロイ再実行・確認（30分）

**目的**: 修正後のコードでデプロイが成功することを確認

**実装内容**:
1. ステップ1の修正をコミット・プッシュ
2. Render.comで自動デプロイが実行されるのを待つ
3. デプロイログを確認
4. デプロイが成功することを確認

**確認項目**:
- [ ] 修正をコミット・プッシュ完了
- [ ] Render.comで自動デプロイが実行される
- [ ] デプロイログでエラーがないことを確認
- [ ] Alembicマイグレーションが正常に実行されることを確認
- [ ] ビルドが成功することを確認

---

### ステップ4: ステージング環境での動作確認（30分）

**目的**: ステージング環境でバックエンドが正常に動作していることを確認

**実装内容**:
1. ヘルスチェックエンドポイントにアクセス
   - `https://yadopera-backend-staging.onrender.com/api/v1/health`
2. 主要なAPIエンドポイントが正常に動作していることを確認
   - `GET /api/v1/health`
   - `GET /api/v1/facility/{slug}`（テスト用施設が必要）
   - `POST /api/v1/chat`（テスト用データが必要）

**確認項目**:
- [ ] ヘルスチェックエンドポイントが正常に応答する（`{"status": "ok"}`）
- [ ] 主要なAPIエンドポイントが正常に動作している
- [ ] エラーログがないことを確認（Render.comのログ画面で確認）

---

### ステップ5: ステージング環境でのテスト実行・パス確認（1時間）

**目的**: ステージング環境でテストを実行し、すべてパスすることを確認

**実装内容**:
1. ステージング環境のデータベース接続情報を取得
2. ローカル環境でステージング環境のデータベースに接続してテストを実行
   - または、Render.comのシェル機能を使用してテストを実行
3. 全テストがパスすることを確認

**確認項目**:
- [ ] ステージング環境のデータベース接続情報を取得完了
- [ ] テストを実行完了
- [ ] 全テストがパスすることを確認
- [ ] テスト結果を記録

**注意**: 
- ステージング環境のデータベースを使用するため、既存データに影響を与えないよう注意
- テスト用のデータベースを作成するか、テスト後にデータをクリーンアップする

---

### ステップ6: ドキュメント更新（1時間）

**目的**: Phase 1完了を反映したドキュメント更新

**実装内容**:
1. `docs/Phase1/Phase1_Week4_実装状況.md`を更新
   - ステージング環境構築・デプロイ完了を反映
   - 動作確認完了を反映
   - テスト実行・パス確認完了を反映
2. `docs/Phase1/Phase1_Week4_引き継ぎ書.md`を作成（または更新）
   - Phase 1完了を反映
   - ステージング環境の情報を記載
   - 次のフェーズ（Phase 2）への準備事項を記載

**確認項目**:
- [ ] Phase 1 Week 4実装状況ドキュメント更新完了
- [ ] Phase 1引き継ぎ書作成（または更新）完了
- [ ] ステージング環境の情報を記載完了

---

## 3. 完了基準

### Phase 1 Week 4完了基準（再定義）

Week 4完了の基準：

- [x] ゲストフィードバックAPIが正常に動作する（ローカル環境）
- [x] ダッシュボードAPIが正常に動作する（ローカル環境）
- [x] FAQ管理APIが正常に動作する（ローカル環境）
- [x] FAQ自動学習APIが正常に動作する（ローカル環境）
- [x] 夜間対応キューAPIが正常に動作する（ローカル環境）
- [x] QRコード生成APIが正常に動作する（ローカル環境）
- [x] Week 2のテストコードが作成され、全テストが通過する（ローカル環境）
- [x] 統合テスト・E2Eテストが正常に実行される（ローカル環境）
- [ ] **ステージング環境が構築され、デプロイが完了している** ❌
  - [ ] Railway PostgreSQLのpgvector拡張有効化完了
  - [ ] Render.comデプロイ成功
  - [ ] ステージング環境で動作確認完了
  - [ ] ステージング環境でテスト実行・パス確認完了
- [x] レスポンス速度が3秒以内である（ローカル環境）
- [x] エラーハンドリングが適切に実装されている
- [⏳] ドキュメントが更新されている（実装中）

**完了率**: **9/12項目（75.0%）**

### Phase 1完了基準（再定義）

Phase 1が100%完了するためには、以下がすべて完了している必要があります：

1. Week 1-3完了 ✅
2. Week 4 API実装完了 ✅
3. Week 4テストコード作成完了 ✅
4. Week 4最適化・エラーハンドリング完了 ✅
5. **ステージング環境構築・デプロイ完了** ❌
   - Railway PostgreSQLのpgvector拡張有効化完了 ❌
   - Render.comデプロイ成功 ❌
   - ステージング環境動作確認完了 ❌
   - テスト実行・パス確認完了 ❌
6. ドキュメント更新完了 ⏳

**Phase 1完了率**: **約90%**（ステージング環境構築・デプロイが未完了のため100%ではない）

---

## 4. 推奨実施順序

### 最優先フロー（約3時間）

```
1. ステップ1: Render.comデプロイエラー解決（1時間）
   ↓
2. ステップ2: Railway PostgreSQLのpgvector拡張有効化（15分）
   ↓
3. ステップ3: Render.comデプロイ再実行・確認（30分）
   ↓
4. ステップ4: ステージング環境での動作確認（30分）
   ↓
5. ステップ5: ステージング環境でのテスト実行・パス確認（1時間）
   ↓
6. ステップ6: ドキュメント更新（1時間）
```

**合計**: 約4時間15分

### 並行実施可能項目

- ステップ2（Railway pgvector拡張有効化）とステップ1（Render.comエラー解決）は並行実施可能
  - ただし、ステップ3（デプロイ再実行）はステップ1完了後

---

## 5. 各ステップの詳細

### ステップ1: Render.comデプロイエラー解決（詳細）

**ファイル**: `backend/alembic/env.py`

**修正前**:
```python
def get_url():
    """環境変数からデータベースURLを取得"""
    return settings.database_url
```

**修正後**:
```python
def get_url():
    """環境変数からデータベースURLを取得（Alembic用に同期形式に変換）"""
    url = settings.database_url
    # postgresql+asyncpg:// -> postgresql:// に変換（Alembicは同期エンジンを使用）
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url
```

**理由**:
- Alembicは同期エンジン（`engine_from_config`）を使用する
- 同期エンジンでは`postgresql://`形式のURLが必要
- アプリケーション側（`app/database.py`）は非同期エンジンを使用するため、`postgresql+asyncpg://`形式が必要
- `app/database.py`では既に`postgresql://`を`postgresql+asyncpg://`に変換する処理が実装されている

**確認方法**:
1. 修正をコミット・プッシュ
2. Render.comで自動デプロイが実行される
3. デプロイログで以下を確認:
   - `alembic upgrade head`が正常に実行される
   - `MissingGreenlet`エラーが発生しない
   - ビルドが成功する

---

### ステップ2: Railway PostgreSQLのpgvector拡張有効化（詳細）

**前提条件**:
- Railway CLIがインストールされていること
- Railwayアカウントでログイン済みであること

**手順**:
1. プロジェクトルートディレクトリで以下を実行:
   ```bash
   railway login
   railway link
   railway connect postgres
   ```

2. psqlが起動したら、以下のSQLを実行:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. 拡張が有効化されたか確認:
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```
   - 結果が1行返れば、拡張は有効化されている

4. psqlを終了:
   ```sql
   \q
   ```

**確認方法**:
- `SELECT * FROM pg_extension WHERE extname = 'vector';`で結果が返る
- Alembicマイグレーション（`001_enable_pgvector.py`）が正常に実行される

**参考**: `docs/Deployment/pgvector拡張有効化_実行手順.md`

---

### ステップ3: Render.comデプロイ再実行・確認（詳細）

**前提条件**:
- ステップ1の修正がコミット・プッシュ済み
- Railway pgvector拡張有効化完了（ステップ2）

**確認項目**:
1. Render.comダッシュボードでデプロイログを確認
2. 以下を確認:
   - `pip install -r requirements.txt`が成功
   - `alembic upgrade head`が成功
   - `MissingGreenlet`エラーが発生しない
   - ビルドが成功する
   - Web Serviceが起動する

**エラーが発生した場合**:
- デプロイログを確認
- エラー内容を分析
- 必要に応じて追加の修正を実施

---

### ステップ4: ステージング環境での動作確認（詳細）

**確認するエンドポイント**:
1. **ヘルスチェック**: `GET /api/v1/health`
   - 期待値: `{"status": "ok"}`
   - ステータスコード: `200 OK`

2. **ルートエンドポイント**: `GET /`
   - 期待値: `{"message": "やどぺら API v0.3", "status": "ok"}`
   - ステータスコード: `200 OK`

3. **Swagger UI**: `GET /docs`
   - 期待値: Swagger UIが表示される
   - ステータスコード: `200 OK`

**確認方法**:
- ブラウザでアクセス
- curlコマンドで確認
- Postman等のツールで確認

**エラーが発生した場合**:
- Render.comのログ画面でエラーログを確認
- エラー内容を分析
- 必要に応じて修正を実施

---

### ステップ5: ステージング環境でのテスト実行・パス確認（詳細）

**方法1: ローカル環境からステージング環境のデータベースに接続**

1. ステージング環境のデータベース接続情報を取得（Railwayダッシュボード）
2. ローカル環境で環境変数を設定:
   ```bash
   export DATABASE_URL="postgresql://user:password@railway-host:port/database"
   ```
3. テストを実行:
   ```bash
   cd backend
   pytest tests/
   ```

**方法2: Render.comのシェル機能を使用**

1. Render.comダッシュボードで「Shell」を開く
2. テストを実行:
   ```bash
   cd backend
   pytest tests/
   ```

**確認項目**:
- 全テストがパスする
- エラーがない
- テスト結果を記録

**注意**:
- ステージング環境のデータベースを使用するため、既存データに影響を与えないよう注意
- テスト用のデータベースを作成するか、テスト後にデータをクリーンアップする

---

### ステップ6: ドキュメント更新（詳細）

**更新するドキュメント**:
1. `docs/Phase1/Phase1_Week4_実装状況.md`
   - ステージング環境構築・デプロイ完了を反映
   - 動作確認完了を反映
   - テスト実行・パス確認完了を反映

2. `docs/Phase1/Phase1_Week4_引き継ぎ書.md`（新規作成または更新）
   - Phase 1完了を反映
   - ステージング環境の情報を記載
     - Railway PostgreSQL接続情報
     - Railway Redis接続情報
     - Render.com Web Service URL
   - 次のフェーズ（Phase 2）への準備事項を記載

**記載内容**:
- Phase 1完了日
- ステージング環境URL
- データベース接続情報（機密情報は環境変数参照を記載）
- テスト結果サマリー
- 既知の問題点（あれば）
- 次のフェーズへの準備事項

---

## 6. 完了基準チェックリスト

### Phase 1 Week 4完了基準

- [x] ゲストフィードバックAPIが正常に動作する（ローカル環境）
- [x] ダッシュボードAPIが正常に動作する（ローカル環境）
- [x] FAQ管理APIが正常に動作する（ローカル環境）
- [x] FAQ自動学習APIが正常に動作する（ローカル環境）
- [x] 夜間対応キューAPIが正常に動作する（ローカル環境）
- [x] QRコード生成APIが正常に動作する（ローカル環境）
- [x] Week 2のテストコードが作成され、全テストが通過する（ローカル環境）
- [x] 統合テスト・E2Eテストが正常に実行される（ローカル環境）
- [ ] **ステージング環境が構築され、デプロイが完了している**
  - [ ] Railway PostgreSQLのpgvector拡張有効化完了
  - [ ] Render.comデプロイ成功
  - [ ] ステージング環境で動作確認完了
  - [ ] ステージング環境でテスト実行・パス確認完了
- [x] レスポンス速度が3秒以内である（ローカル環境）
- [x] エラーハンドリングが適切に実装されている
- [ ] ドキュメントが更新されている

**完了率**: **9/12項目（75.0%）**

### Phase 1完了基準

- [x] Week 1-3完了
- [x] Week 4 API実装完了
- [x] Week 4テストコード作成完了
- [x] Week 4最適化・エラーハンドリング完了
- [ ] **ステージング環境構築・デプロイ完了**
  - [ ] Railway PostgreSQLのpgvector拡張有効化完了
  - [ ] Render.comデプロイ成功
  - [ ] ステージング環境動作確認完了
  - [ ] テスト実行・パス確認完了
- [ ] ドキュメント更新完了

**Phase 1完了率**: **約90%**（ステージング環境構築・デプロイが未完了のため100%ではない）

---

## 7. 次のアクション（推奨順序）

### 最優先（Phase 1完了に必須）

1. **ステップ1: Render.comデプロイエラー解決**（1時間）
   - `backend/alembic/env.py`の`get_url()`関数を修正
   - `postgresql+asyncpg://`を`postgresql://`に変換

2. **ステップ2: Railway PostgreSQLのpgvector拡張有効化**（15分）
   - Railway CLIを使用してSQLを実行

3. **ステップ3: Render.comデプロイ再実行・確認**（30分）
   - 修正をコミット・プッシュ
   - デプロイが成功することを確認

4. **ステップ4: ステージング環境での動作確認**（30分）
   - ヘルスチェックエンドポイントにアクセス
   - 主要なAPIエンドポイントが正常に動作していることを確認

5. **ステップ5: ステージング環境でのテスト実行・パス確認**（1時間）
   - ステージング環境でテストを実行
   - 全テストがパスすることを確認

### 高優先度

6. **ステップ6: ドキュメント更新**（1時間）
   - Phase 1完了を反映したドキュメント更新

---

## 8. まとめ

### 現在の状況

**Phase 1 Week 4完了率**: **75.0%**（9/12項目完了）

**未完了項目**:
- ステージング環境構築・デプロイ（4項目）
- ドキュメント更新（1項目）

### 残存課題

**最優先課題（Phase 1完了に必須）**:
1. Render.comデプロイエラー解決（1時間）
2. Railway PostgreSQLのpgvector拡張有効化（15分）
3. ステージング環境での動作確認（30分）
4. ステージング環境でのテスト実行・パス確認（1時間）

**高優先度課題**:
5. ドキュメント更新（1時間）

### Phase 1完了の定義

**Phase 1が100%完了するためには**:
1. Week 1-3完了 ✅
2. Week 4 API実装完了 ✅
3. Week 4テストコード作成完了 ✅
4. Week 4最適化・エラーハンドリング完了 ✅
5. **ステージング環境構築・デプロイ完了** ❌
6. **ステージング環境での動作確認完了** ❌
7. **ステージング環境でのテスト実行・パス確認完了** ❌
8. ドキュメント更新完了 ⏳

**これらすべてが完了し、テストを実行してパスして初めてPhase 1は100%完了です。**

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-11-28  
**Status**: 残存課題対応ステップ計画立案完了

