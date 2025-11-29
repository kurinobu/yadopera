# Phase 1 Week 4 ステップ3: Railway PostgreSQL接続情報確認完了 次のステップ

**作成日**: 2025年11月29日  
**対象**: Railway PostgreSQLサービス（pgvector-pg18）の接続情報確認完了  
**現在の状態**: 接続情報取得完了、次のステップ（psqlで直接接続）

---

## 1. 確認結果の説明

### 1.1 確認した内容

**確認場所**: Railwayダッシュボード

**確認項目**:
1. ✅ **Variablesタブ**: `DATABASE_URL`と`DATABASE_PUBLIC_URL`を確認完了
2. ❌ **Settingsタブ**: 「Service Name」が見当たらない

### 1.2 取得した接続情報

**DATABASE_PUBLIC_URL**（公開エンドポイント）:
```
postgresql://postgres:uhk62qgfrro7wu2s4et6dgd84563qg1k@tramway.proxy.rlwy.net:50673/railway
```

**DATABASE_URL**（内部エンドポイント）:
```
postgresql://postgres:uhk62qgfrro7wu2s4et6dgd84563qg1k@pgvector.railway.internal:5432/railway
```

**重要な確認事項**:
- ✅ 接続情報が正常に取得できた
- ✅ `DATABASE_PUBLIC_URL`は外部接続用（Render.comから接続する場合に使用）
- ✅ `DATABASE_URL`はRailway内部サービス間接続用（Render.comからは使用不可）
- ✅ 外部接続にはegress feesが発生する可能性がある

---

## 2. 評価

### 2.1 確認結果の評価

**評価**: ✅ **接続情報の取得は成功**

**理由**:
1. **接続情報が正常に取得できた**
   - `DATABASE_PUBLIC_URL`と`DATABASE_URL`の両方が確認できた
   - 接続URLの形式が正しい（`postgresql://...`形式）

2. **次のステップに進める状態**
   - 接続情報を取得できたので、psqlで直接接続できる
   - pgvector拡張の確認に進める

### 2.2 Settingsタブの「Service Name」が見当たらない件

**評価**: ⚠️ **問題なし**（接続情報が取得できたため）

**理由**:
- 接続情報が取得できたので、サービス名を確認する必要はない
- psqlで直接接続する場合は、サービス名は不要
- 接続URLがあれば、直接接続できる

---

## 3. 次のステップ

### ステップ1: psqlで直接接続

**目的**: 取得した接続情報を使って、psqlで直接接続する

**実行方法**: ローカルのpsqlを使用

**手順**:
```bash
# 1. プロジェクトルートディレクトリに移動（既にいる場合はスキップ）
cd /Users/kurinobu/projects/yadopera

# 2. psqlで直接接続（DATABASE_PUBLIC_URLを使用）
psql "postgresql://postgres:uhk62qgfrro7wu2s4et6dgd84563qg1k@tramway.proxy.rlwy.net:50673/railway"
```

**期待される結果**:
- psqlが起動する
- psqlのプロンプト（例: `railway=#`）が表示される

**確認事項**:
- [ ] `psql`コマンドで接続できた
- [ ] psqlのプロンプトが表示された

---

### ステップ2: pgvector拡張が利用可能か確認

**目的**: 新しいPostgreSQLサービス（pgvector-pg18）にpgvector拡張がインストールされているか確認

**実行方法**: psqlでSQLを実行

**手順**:
```sql
-- 1. PostgreSQLバージョン確認
SELECT version();

-- 2. 利用可能な拡張一覧を確認
SELECT * FROM pg_available_extensions WHERE name LIKE '%vector%';
```

**期待される結果（成功の場合）**:
```
   name   | default_version | installed_version | comment
----------+-----------------+-------------------+---------
 vector   | 0.5.0           |                   | vector data type and ivfflat access method
```

**期待される結果（失敗の場合）**:
```
 name | default_version | installed_version | comment 
------+-----------------+-------------------+---------
(0 行)
```

**確認事項**:
- [ ] `vector`拡張が一覧に表示される（成功）
- [ ] `vector`拡張が一覧に表示されない（失敗、以前と同じ問題）

---

### ステップ3: pgvector拡張を有効化（拡張が利用可能な場合のみ）

**前提条件**: ステップ2で`vector`拡張が一覧に表示された場合のみ実行

**目的**: pgvector拡張を有効化する

**実行方法**: psqlでSQLを実行

**手順**:
```sql
-- pgvector拡張を有効化
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

### ステップ4: 拡張が有効化されたか確認

**前提条件**: ステップ3を実行した場合のみ

**目的**: pgvector拡張が正常に有効化されたか確認

**実行方法**: psqlでSQLを実行

**手順**:
```sql
-- 有効化された拡張を確認
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

### ステップ5: psqlを終了

**手順**:
```sql
\q
```

または `Ctrl+D`

**確認事項**:
- [ ] psqlを終了
- [ ] ターミナルに戻る

---

## 4. Render.comの環境変数更新

### 4.1 更新が必要な環境変数

**DATABASE_URL**:
- **現在の値**: 古いPostgreSQLサービスの接続URL
- **新しい値**: `postgresql://postgres:uhk62qgfrro7wu2s4et6dgd84563qg1k@tramway.proxy.rlwy.net:50673/railway`
- **重要**: `postgresql://`形式のまま（`postgresql+asyncpg://`に変更しない）

**理由**:
- `app/database.py`が`postgresql://`を`postgresql+asyncpg://`に自動変換する
- Alembicは`postgresql://`形式を使用する

### 4.2 更新手順

1. Render.comダッシュボードにアクセス: https://dashboard.render.com
2. Web Service `yadopera-backend-staging`を選択
3. 「Environment」タブを開く
4. `DATABASE_URL`環境変数を編集
5. 新しい値を設定: `postgresql://postgres:uhk62qgfrro7wu2s4et6dgd84563qg1k@tramway.proxy.rlwy.net:50673/railway`
6. 「Save Changes」をクリック
7. 自動デプロイが実行されるのを待つ

**確認事項**:
- [ ] `DATABASE_URL`が新しい接続URLに更新されている
- [ ] `postgresql://`形式のまま（`postgresql+asyncpg://`に変更していない）
- [ ] デプロイが正常に完了する
- [ ] Alembicマイグレーションが正常に実行される

---

## 5. 結果に応じた次のアクション

### 5.1 成功した場合（pgvector拡張が利用可能）

**次のステップ**:
1. ✅ 新しいPostgreSQLサービス（pgvector-pg18）の接続情報を取得（完了）
2. ✅ Render.comの環境変数`DATABASE_URL`を更新
3. ✅ 古いPostgreSQLサービス（pgvector-pg17）を削除（オプション）

---

### 5.2 失敗した場合（pgvector拡張が利用可能でない）

**次のアクション**:

**最優先（推奨）**: Railwayサポートに問い合わせ

**問い合わせ内容**:
1. `pgvector-pg17`テンプレートと`pgvector-pg18`テンプレートの両方を使用してPostgreSQLサービスを作成した
2. しかし、どちらのテンプレートでもpgvector拡張が利用可能な拡張一覧に表示されない
3. `SELECT * FROM pg_available_extensions WHERE name LIKE '%vector%';`で結果が返らない
4. 解決方法を確認したい

**期待される結果**:
- Railwayサポートから解決方法が提供される
- または、テンプレートの問題が修正される

---

## 6. 確認チェックリスト

### 6.1 接続情報確認

- [x] `DATABASE_PUBLIC_URL`を取得完了
- [x] `DATABASE_URL`を取得完了
- [ ] 接続情報が正しい形式であることを確認

### 6.2 psql接続とpgvector拡張確認

- [ ] psqlで直接接続完了
- [ ] PostgreSQLバージョンを確認完了
- [ ] 利用可能な拡張を確認完了（`vector`拡張が表示されるか確認）
- [ ] pgvector拡張を有効化完了（拡張が利用可能な場合のみ）
- [ ] 拡張が有効化されたことを確認完了（拡張が利用可能な場合のみ）
- [ ] psqlを終了完了

### 6.3 Render.com環境変数更新

- [ ] `DATABASE_URL`が新しい接続URLに更新されている
- [ ] `postgresql://`形式のまま（`postgresql+asyncpg://`に変更していない）
- [ ] デプロイが正常に完了する
- [ ] Alembicマイグレーションが正常に実行される
- [ ] `/api/v1/health`エンドポイントが正常に動作する

---

## 7. まとめ

### 7.1 現在の状態

**完了したステップ**:
- ✅ Railwayダッシュボードで接続情報を確認完了
- ✅ `DATABASE_PUBLIC_URL`と`DATABASE_URL`を取得完了

**次のステップ**:
1. ✅ psqlで直接接続
2. ✅ pgvector拡張が利用可能か確認
3. ✅ 拡張が利用可能な場合、有効化

### 7.2 推奨アクション

**最優先**:
1. ✅ `psql "postgresql://postgres:uhk62qgfrro7wu2s4et6dgd84563qg1k@tramway.proxy.rlwy.net:50673/railway"`を実行
2. ✅ psqlが起動することを確認
3. ✅ pgvector拡張が利用可能か確認
4. ✅ 結果に応じた対応を実行

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-11-29  
**Status**: 接続情報確認完了、次のステップ提示完了

