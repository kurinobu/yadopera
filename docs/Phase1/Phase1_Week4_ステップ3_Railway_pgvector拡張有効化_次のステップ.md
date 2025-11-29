# Phase 1 Week 4 ステップ3: Railway PostgreSQLのpgvector拡張有効化 次のステップ

**作成日**: 2025年11月29日  
**対象**: 新しいPostgreSQLサービス（pgvector-pg17）のpgvector拡張有効化  
**現在の状態**: 接続情報取得完了

---

## 1. 現在の状態

### 1.1 完了したステップ

✅ **新しいPostgreSQLサービス作成完了**
- テンプレート: `pgvector-pg17`
- サービス名: `yadopera-postgres-staging`（推測）

✅ **接続情報取得完了**

**DATABASE_PUBLIC_URL**（公開エンドポイント）:
```
postgresql://postgres:xwi3baosq58bmmph6itzmg8mtizu07cu@crossover.proxy.rlwy.net:46227/railway
```

**DATABASE_URL**（内部エンドポイント）:
```
postgresql://postgres:xwi3baosq58bmmph6itzmg8mtizu07cu@pgvector-9gte.railway.internal:5432/railway
```

**注意事項**:
- `DATABASE_PUBLIC_URL`は外部接続用（Render.comから接続する場合に使用）
- `DATABASE_URL`はRailway内部サービス間接続用（Render.comからは使用不可）
- 外部接続にはegress feesが発生する可能性がある

---

## 2. 次のステップ

### ステップ1: pgvector拡張が利用可能か確認

**目的**: 新しいPostgreSQLサービスにpgvector拡張がインストールされているか確認

**実行方法**: Railway CLIを使用

**手順**:
```bash
# 1. プロジェクトルートディレクトリに移動
cd /Users/kurinobu/projects/yadopera

# 2. Railway CLIで接続（既にリンク済みの場合）
railway connect postgres

# 3. 利用可能な拡張を確認
SELECT * FROM pg_available_extensions WHERE name LIKE '%vector%';
```

**期待される結果**:
```
   name   | default_version | installed_version | comment
----------+-----------------+-------------------+----------
 vector   | 0.5.0           |                   | vector data type and ivfflat access method
```

**確認事項**:
- [ ] `vector`拡張が一覧に表示される
- [ ] `default_version`が表示される（例: `0.5.0`）
- [ ] `installed_version`は空（まだ有効化されていない）

---

### ステップ2: pgvector拡張を有効化

**目的**: pgvector拡張を有効化する

**実行方法**: Railway CLIを使用

**手順**:
```bash
# 1. Railway CLIで接続（既に接続済みの場合はスキップ）
railway connect postgres

# 2. pgvector拡張を有効化
CREATE EXTENSION IF NOT EXISTS vector;
```

**期待される結果**:
```
CREATE EXTENSION
```

**確認事項**:
- [ ] エラーが発生しない
- [ ] 「CREATE EXTENSION」というメッセージが表示される

---

### ステップ3: 拡張が有効化されたか確認

**目的**: pgvector拡張が正常に有効化されたか確認

**実行方法**: Railway CLIを使用

**手順**:
```bash
# 1. Railway CLIで接続（既に接続済みの場合はスキップ）
railway connect postgres

# 2. 有効化された拡張を確認
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**期待される結果**:
```
 extname | extowner | extnamespace | extrelocatable | extversion | extconfig | extcondition 
---------+----------+--------------+----------------+------------+-----------+--------------
 vector  |    16384 |         2200 | t              | 0.5.0      |           | 
(1 row)
```

**確認事項**:
- [ ] 結果が1行返る
- [ ] `extname`が`vector`であることを確認
- [ ] `extversion`が表示される（例: `0.5.0`）

---

### ステップ4: psqlを終了

**手順**:
```sql
\q
```

または `Ctrl+D`

**確認事項**:
- [ ] psqlを終了
- [ ] ターミナルに戻る

---

## 3. Render.comの環境変数更新

### 3.1 更新が必要な環境変数

**DATABASE_URL**:
- **現在の値**: 古いPostgreSQLサービスの接続URL
- **新しい値**: `postgresql://postgres:xwi3baosq58bmmph6itzmg8mtizu07cu@crossover.proxy.rlwy.net:46227/railway`
- **重要**: `postgresql://`形式のまま（`postgresql+asyncpg://`に変更しない）

**理由**:
- `app/database.py`が`postgresql://`を`postgresql+asyncpg://`に自動変換する
- Alembicは`postgresql://`形式を使用する

### 3.2 更新手順

1. Render.comダッシュボードにアクセス: https://dashboard.render.com
2. Web Service `yadopera-backend-staging`を選択
3. 「Environment」タブを開く
4. `DATABASE_URL`環境変数を編集
5. 新しい値を設定: `postgresql://postgres:xwi3baosq58bmmph6itzmg8mtizu07cu@crossover.proxy.rlwy.net:46227/railway`
6. 「Save Changes」をクリック
7. 自動デプロイが実行されるのを待つ

**確認事項**:
- [ ] `DATABASE_URL`が新しい接続URLに更新されている
- [ ] `postgresql://`形式のまま（`postgresql+asyncpg://`に変更していない）
- [ ] デプロイが正常に完了する
- [ ] Alembicマイグレーションが正常に実行される

---

## 4. 確認チェックリスト

### 4.1 pgvector拡張有効化

- [ ] Railway CLIで接続完了
- [ ] 利用可能な拡張を確認完了（`vector`拡張が表示される）
- [ ] `CREATE EXTENSION IF NOT EXISTS vector;`実行完了
- [ ] 拡張が有効化されたことを確認完了（`SELECT * FROM pg_extension WHERE extname = 'vector';`で結果が返る）
- [ ] psqlを終了完了

### 4.2 Render.com環境変数更新

- [ ] `DATABASE_URL`が新しい接続URLに更新されている
- [ ] `postgresql://`形式のまま（`postgresql+asyncpg://`に変更していない）
- [ ] デプロイが正常に完了する
- [ ] Alembicマイグレーションが正常に実行される
- [ ] `/api/v1/health`エンドポイントが正常に動作する

---

## 5. トラブルシューティング

### 5.1 pgvector拡張が見つからない場合

**症状**: `SELECT * FROM pg_available_extensions WHERE name LIKE '%vector%';`で結果が返らない

**原因**: `pgvector-pg17`テンプレートを使用しているにもかかわらず、pgvector拡張がインストールされていない

**対策**:
1. Railwayサポートに問い合わせ
2. または、別のPostgreSQLサービスを作成（pgvector-pg18テンプレートを試す）

---

### 5.2 拡張の有効化に失敗する場合

**症状**: `CREATE EXTENSION IF NOT EXISTS vector;`でエラーが発生する

**原因**: 権限エラー、または拡張がインストールされていない

**対策**:
1. エラーメッセージを確認
2. Railwayサポートに問い合わせ

---

### 5.3 Render.comデプロイエラー

**症状**: Render.comでデプロイが失敗する

**原因**: 環境変数`DATABASE_URL`の形式が正しくない、または接続URLが間違っている

**対策**:
1. `DATABASE_URL`が`postgresql://`形式であることを確認
2. 接続URLが正しいか確認
3. パスワードに特殊文字が含まれている場合はURLエンコードが必要

---

## 6. 次のステップ（完了後）

pgvector拡張の有効化とRender.comの環境変数更新が完了したら:

1. **ステップ4: ステージング環境での動作確認**
   - ヘルスチェックエンドポイントにアクセス
   - 主要なAPIエンドポイントが正常に動作していることを確認

2. **ステップ5: ステージング環境でのテスト実行・パス確認**
   - テストを実行
   - すべてのテストがパスすることを確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-11-29  
**Status**: 次のステップ提示完了

