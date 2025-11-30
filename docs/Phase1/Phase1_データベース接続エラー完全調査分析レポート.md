# Phase 1 データベース接続エラー完全調査分析レポート

**作成日**: 2025年11月29日  
**対象**: ステージング環境でのテスト実行時のデータベース接続エラー  
**目的**: エラーの根本原因を特定し、解決策を提示

---

## 1. エラー概要

### 1.1 エラーメッセージ

```
ERROR at setup of TestLogin.test_login_success
asyncpg.exceptions.UniqueViolationError: duplicate key value violates unique constraint "idx_facilities_slug"
sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) 
<class 'asyncpg.exceptions.UniqueViolationError'>: duplicate key value violates unique constraint "idx_facilities_slug"
```

### 1.2 発生箇所

- **テストファイル**: `backend/tests/test_auth.py`
- **テスト関数**: `TestLogin.test_login_success`
- **フィクスチャ**: `test_facility`（`conftest.py`の175-193行目）

### 1.3 影響範囲

- **直接影響**: `test_auth.py`の全テスト（5テスト）
- **間接影響**: `test_facility`フィクスチャを使用する全テスト（多数）

---

## 2. 根本原因分析

### 2.1 エラーの直接原因

**問題**: `test_facility`フィクスチャが毎回同じ`slug="test-hotel"`でデータを挿入しようとしている

**エラー発生フロー**:
1. テスト実行開始
2. `test_facility`フィクスチャが実行される
3. `Facility`オブジェクトを作成（`slug="test-hotel"`）
4. `db_session.add(facility)`でセッションに追加
5. `await db_session.commit()`でコミット
6. **エラー**: `idx_facilities_slug`ユニーク制約違反

### 2.2 データベースの状態確認

**ステージング環境のデータベース状態**:
```
Test facilities found: 1
  ID: 1, Name: Test Hotel, Slug: test-hotel, Email: test@example.com
```

**確認結果**:
- ステージング環境には既に`slug="test-hotel"`の施設データが存在
- 前回のテスト実行で作成されたデータが残っている

### 2.3 現在の実装の問題点

#### 問題1: データクリーンアップの欠如

**現在の実装** (`conftest.py` 86-156行目):
```python
@pytest.fixture(scope="function")
async def db_session():
    # ... テーブル作成 ...
    
    session = TestSessionLocal()
    try:
        yield session
    finally:
        # ロールバックとクローズのみ
        await session.rollback()
        await session.close()
    
    # ステージング環境ではテーブル削除をスキップ
    if not os.getenv("TEST_DATABASE_URL"):
        # ローカル環境のみテーブル削除
        ...
```

**問題点**:
- ステージング環境では、テストデータのクリーンアップが行われていない
- `db_session.rollback()`は未コミットのトランザクションのみをロールバック
- コミット済みのデータ（`test_facility`で作成されたデータ）は残る

#### 問題2: 固定値の使用

**現在の実装** (`conftest.py` 175-193行目):
```python
@pytest.fixture
async def test_facility(db_session: AsyncSession):
    facility = Facility(
        name="Test Hotel",
        slug="test-hotel",  # ← 固定値
        email="test@example.com",  # ← 固定値
        ...
    )
    db_session.add(facility)
    await db_session.commit()  # ← コミット済みデータは残る
    await db_session.refresh(facility)
    return facility
```

**問題点**:
- `slug`と`email`が固定値のため、複数回のテスト実行で重複エラーが発生
- ユニーク制約があるカラム（`slug`）に固定値を使用している

#### 問題3: トランザクション管理の不備

**現在の実装**:
- `test_facility`フィクスチャは`await db_session.commit()`を実行
- コミット後、`db_session.rollback()`は効果がない
- テスト終了時にデータが削除されない

**期待される動作**:
- テスト終了時に、テストで作成したデータを削除
- または、トランザクション内でデータを作成し、ロールバックで削除

---

## 3. 詳細な問題分析

### 3.1 テストフィクスチャの実行順序

**現在の実行順序**:
1. `db_session`フィクスチャが実行される
   - テーブル作成（ステージング環境ではスキップ）
   - セッション作成
2. `test_facility`フィクスチャが実行される
   - 施設データを作成
   - **コミット**（データが永続化される）
3. テスト関数が実行される
4. `db_session`フィクスチャのクリーンアップが実行される
   - ロールバック（効果なし、既にコミット済み）
   - セッションクローズ

**問題点**:
- コミット済みデータが残る
- 次のテスト実行時に重複エラーが発生

### 3.2 ステージング環境とローカル環境の違い

| 項目 | ローカル環境 | ステージング環境 |
|------|------------|----------------|
| テーブル作成 | 毎回作成 | スキップ（既に存在） |
| テーブル削除 | 毎回削除 | スキップ |
| データクリーンアップ | テーブル削除で自動削除 | **なし** |
| データの永続化 | なし（メモリDBまたは毎回削除） | **あり** |

**問題点**:
- ステージング環境では、データが永続化される
- データクリーンアップが行われていない

### 3.3 ユニーク制約の確認

**`facilities`テーブルの定義** (`app/models/facility.py` 20行目):
```python
slug = Column(String(100), unique=True, nullable=False, index=True)
```

**制約**:
- `slug`カラムにはユニーク制約がある
- 同じ`slug`値を持つレコードは複数存在できない

**影響**:
- `test_facility`フィクスチャが毎回同じ`slug="test-hotel"`でデータを作成しようとする
- 前回のテストで作成されたデータが残っている場合、重複エラーが発生

---

## 4. 影響範囲の分析

### 4.1 直接影響を受けるテスト

**`test_facility`フィクスチャを使用するテスト**:
- `test_auth.py`: 5テスト（`test_login_success`, `test_login_invalid_email`, `test_login_invalid_password`, `test_login_inactive_user`, `test_logout_success`）
- `test_integration.py`: 複数テスト
- `test_escalation.py`: 複数テスト
- `test_overnight_queue.py`: 複数テスト
- `test_session_token.py`: 複数テスト
- その他、`test_facility`を使用する全テスト

**推定影響範囲**: 30-50テスト

### 4.2 間接影響

**`test_user`フィクスチャを使用するテスト**:
- `test_user`は`test_facility`に依存しているため、間接的に影響を受ける

**推定影響範囲**: 追加で10-20テスト

### 4.3 エラーの種類

**主なエラー**:
1. **`IntegrityError: duplicate key value violates unique constraint "idx_facilities_slug"`**
   - `test_facility`フィクスチャで発生
2. **`IntegrityError: duplicate key value violates unique constraint "ix_users_email"`**
   - `test_user`フィクスチャで発生する可能性（`email`も固定値）

---

## 5. 解決策の提案

### 5.1 解決策1: テストデータのクリーンアップ（推奨）

**概要**: テスト終了時に、テストで作成したデータを削除

**実装方法**:
1. `test_facility`フィクスチャのクリーンアップを追加
2. テスト終了時に、作成した施設データを削除
3. 関連データ（ユーザー、会話など）も削除

**メリット**:
- ステージング環境でも安全にテストを実行できる
- データの永続化を防ぐ
- テスト間の独立性を保つ

**デメリット**:
- クリーンアップ処理が複雑になる可能性
- 外部キー制約により、削除順序に注意が必要

### 5.2 解決策2: ユニークな値の生成

**概要**: テストデータにユニークな値（UUID、タイムスタンプ）を使用

**実装方法**:
1. `test_facility`フィクスチャで、`slug`と`email`にユニークな値を生成
2. UUIDまたはタイムスタンプを使用

**メリット**:
- 重複エラーを防ぐ
- 実装が簡単

**デメリット**:
- テストデータが蓄積される（ステージング環境）
- データベースのクリーンアップが必要になる可能性

### 5.3 解決策3: トランザクションのロールバック（推奨）

**概要**: テストデータをトランザクション内で作成し、ロールバックで削除

**実装方法**:
1. `test_facility`フィクスチャで、`commit()`を実行しない
2. テスト終了時に、`db_session.rollback()`でデータを削除

**メリット**:
- データの永続化を防ぐ
- 実装が簡単
- テスト間の独立性を保つ

**デメリット**:
- 一部のテストで`commit()`が必要な場合、対応が必要

### 5.4 解決策4: 既存データの削除（推奨）

**概要**: テスト開始前に、既存のテストデータを削除

**実装方法**:
1. `test_facility`フィクスチャの開始時に、既存データを削除
2. `slug="test-hotel"`または`email="test@example.com"`のデータを削除

**メリット**:
- 重複エラーを防ぐ
- 実装が簡単

**デメリット**:
- 他のテストで使用中のデータを誤って削除する可能性
- テスト間の独立性が損なわれる可能性

---

## 6. 推奨される解決策

### 6.1 ハイブリッドアプローチ（推奨）

**組み合わせ**:
1. **解決策3（トランザクションのロールバック）**: 基本方針として採用
2. **解決策2（ユニークな値の生成）**: フォールバックとして採用
3. **解決策4（既存データの削除）**: ステージング環境での追加対策として採用

**実装の優先順位**:
1. **最優先**: 解決策3（トランザクションのロールバック）
2. **次優先**: 解決策2（ユニークな値の生成）
3. **追加対策**: 解決策4（既存データの削除）

### 6.2 実装の詳細

#### 実装1: トランザクションのロールバック

**変更箇所**: `conftest.py`の`test_facility`フィクスチャ

**変更内容**:
- `await db_session.commit()`を削除または条件付きに変更
- テスト終了時に、`db_session.rollback()`でデータを削除

#### 実装2: ユニークな値の生成

**変更箇所**: `conftest.py`の`test_facility`フィクスチャ

**変更内容**:
- `slug`と`email`にユニークな値を生成（UUIDまたはタイムスタンプ）

#### 実装3: 既存データの削除

**変更箇所**: `conftest.py`の`test_facility`フィクスチャ

**変更内容**:
- フィクスチャの開始時に、既存のテストデータを削除
- ステージング環境でのみ実行

---

## 7. 実装の影響分析

### 7.1 変更が必要なファイル

1. **`backend/tests/conftest.py`**
   - `test_facility`フィクスチャの修正
   - `test_user`フィクスチャの修正（必要に応じて）

### 7.2 影響を受けるテスト

**修正後、すべてのテストが正常に実行できるようになる**:
- `test_auth.py`: 5テスト
- `test_integration.py`: 複数テスト
- `test_escalation.py`: 複数テスト
- `test_overnight_queue.py`: 複数テスト
- `test_session_token.py`: 複数テスト
- その他、`test_facility`を使用する全テスト

### 7.3 パフォーマンスへの影響

**最小限**:
- トランザクションのロールバックは高速
- ユニークな値の生成も高速
- 既存データの削除は、データ量に応じて時間がかかる可能性がある

---

## 8. リスク分析

### 8.1 リスク1: データの誤削除

**リスク**: 既存データの削除処理で、他のテストで使用中のデータを誤って削除する可能性

**対策**:
- 削除対象を明確に定義（`slug="test-hotel"`など）
- テスト専用のプレフィックスを使用

### 8.2 リスク2: トランザクションの不整合

**リスク**: 一部のテストで`commit()`が必要な場合、ロールバックが機能しない

**対策**:
- テストごとにトランザクション管理を確認
- 必要に応じて、個別の対応を実施

### 8.3 リスク3: パフォーマンスの低下

**リスク**: 既存データの削除処理で、テスト実行時間が長くなる可能性

**対策**:
- 削除処理を最適化
- 必要に応じて、バッチ削除を実施

---

## 9. 次のステップ

### 9.1 実装の優先順位

1. **最優先**: 解決策3（トランザクションのロールバック）
2. **次優先**: 解決策2（ユニークな値の生成）
3. **追加対策**: 解決策4（既存データの削除）

### 9.2 実装の確認事項

1. ✅ エラーの根本原因を特定
2. ✅ 解決策を提案
3. ⏳ 実装の実施（指示待ち）
4. ⏳ テストの再実行
5. ⏳ 結果の確認

---

## 10. まとめ

### 10.1 エラーの根本原因

1. **直接原因**: `test_facility`フィクスチャが毎回同じ`slug="test-hotel"`でデータを挿入しようとしている
2. **根本原因**: ステージング環境で、テストデータのクリーンアップが行われていない
3. **影響範囲**: `test_facility`を使用する全テスト（30-50テスト）

### 10.2 推奨される解決策

**ハイブリッドアプローチ**:
1. **トランザクションのロールバック**: 基本方針として採用
2. **ユニークな値の生成**: フォールバックとして採用
3. **既存データの削除**: ステージング環境での追加対策として採用

### 10.3 期待される効果

- ✅ データベース接続エラーの解決
- ✅ テスト間の独立性の確保
- ✅ ステージング環境での安全なテスト実行

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-11-29  
**Status**: 調査分析完了、解決策提案完了、実装待ち

