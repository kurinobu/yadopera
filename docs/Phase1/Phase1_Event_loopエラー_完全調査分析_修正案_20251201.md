# Phase 1 Event loopエラー完全調査分析・修正案

**作成日**: 2025年12月1日  
**対象**: Event loopエラーの完全調査分析と修正案の立案  
**目的**: `RuntimeError: Task got Future attached to a different loop`エラーの根本原因を特定し、大原則に基づく修正案を立案

---

## 1. エラーの概要

### 1.1 エラーメッセージ

**主要なエラーメッセージ**:
```
RuntimeError: Task <Task pending name='anyio.from_thread.BlockingPortal._call_func' coro=<BlockingPortal._call_func() running at ...> cb=[TaskGroup._spawn.<locals>.task_done() at ...]> got Future <Future pending cb=[Protocol._on_waiter_completed()]> attached to a different loop
```

**補助的なエラーメッセージ**:
```
RuntimeError: Event loop is closed
```

### 1.2 発生状況

**影響範囲**:
- **失敗したテスト**: 22テスト
- **エラーが発生したテスト**: 8テスト
- **合計影響**: 30テスト（42.3%）

**影響を受けたテストファイル**:
1. `test_auth.py` - 5テスト失敗（認証APIテスト）
2. `test_integration.py` - 8テストエラー（統合テスト）
3. `test_session_token.py` - 6テスト失敗（セッション統合トークンテスト）
4. `test_chat_api.py` - 2テスト失敗（チャットAPIテスト）
5. `test_chat_service.py` - 1テスト失敗（チャットサービステスト）
6. `test_escalation.py` - 1テスト失敗（エスカレーションテスト）
7. `test_overnight_queue.py` - 1テスト失敗（夜間対応キュー処理テスト）
8. `test_vector_search.py` - 2テスト失敗（pgvector検索テスト）

---

## 2. 根本原因の分析

### 2.1 技術的な根本原因

#### 原因1: TestClientとイベントループの競合（最優先）

**問題の本質**:
- `TestClient`は同期的なクライアントで、内部的に`anyio.BlockingPortal`を使用して非同期アプリケーションを呼び出します
- `BlockingPortal`は新しいイベントループを作成します
- SQLAlchemyの非同期接続（`asyncpg`）は、元のイベントループ（pytest-asyncioが作成したループ）にバインドされています
- 異なるイベントループ間でFutureを共有しようとすると、`RuntimeError: Task got Future attached to a different loop`エラーが発生します

**エラーの発生フロー**:
```
1. pytest-asyncioがイベントループを作成（ループA）
2. SQLAlchemyの非同期接続（asyncpg）がループAにバインド
3. TestClientがFastAPIアプリケーションを呼び出す
4. TestClient内部でanyio.BlockingPortalが新しいイベントループを作成（ループB）
5. FastAPIアプリケーションがSQLAlchemyセッションを使用
6. asyncpgがループAのFutureをループBで使用しようとする
7. → RuntimeError: Task got Future attached to a different loop
```

**証拠**:
- エラートレースバックで`anyio.from_thread.BlockingPortal._call_func`が確認される
- `TestClient`を使用するテストでのみ発生
- 非同期テスト（`@pytest.mark.asyncio`）で`TestClient`を使用する場合に特に発生しやすい

#### 原因2: イベントループのライフサイクル管理の問題

**問題の本質**:
- pytest-asyncioの`asyncio_mode = auto`設定により、イベントループが自動的に管理されます
- テスト終了時にイベントループが閉じられる前に、非同期接続のクリーンアップが実行されない場合があります
- 閉じられたイベントループでFutureを作成しようとすると、`RuntimeError: Event loop is closed`エラーが発生します

**証拠**:
- エラートレースバックで`RuntimeError: Event loop is closed`が確認される
- セッションのクローズ処理（`conftest.py`の`db_session`フィクスチャ）で発生

#### 原因3: 非同期接続のクリーンアップタイミングの問題

**問題の本質**:
- `db_session`フィクスチャの`finally`ブロックでセッションをクローズする際、イベントループが既に閉じられている可能性があります
- `await session.close()`が実行される時点で、イベントループが閉じられているとエラーが発生します

**証拠**:
- `conftest.py`の`db_session`フィクスチャの`finally`ブロックでエラーが発生
- `RuntimeError`をキャッチしているが、根本的な解決にはなっていない

---

## 3. 大原則に基づく修正案の立案

### 3.1 大原則の確認

**実装や修正の基本原則**:
1. **根本解決 > 暫定解決**: 一時的な対処よりも根本的な解決を優先
2. **シンプル構造 > 複雑構造**: 複雑な実装よりもシンプルで理解しやすい構造を優先
3. **統一・同一化 > 特殊独自**: 特殊な実装よりも統一されたパターンを優先
4. **具体的 > 一般**: 抽象的な実装よりも具体的で明確な実装を優先
5. **拙速 < 安全確実**: MVPアプローチと安全性のバランスを取る。安全を確保しながら迅速に進める

**準拠基準**:
- 要約定義書・アーキテクチャ設計書を準拠
- 方向性: 根本解決 > 暫定解決、シンプル構造 > 複雑構造、統一・同一化 > 特殊独自、具体的 > 一般、拙速 < 安全確実

### 3.2 修正案の評価

#### 修正案1: AsyncClientの使用（根本解決・推奨）

**内容**:
- `TestClient`の代わりに`httpx.AsyncClient`を使用
- すべてのテストを非同期テスト（`@pytest.mark.asyncio`）に統一
- 同じイベントループを使用することで、イベントループの競合を回避

**実装方法**:
```python
# conftest.py
from httpx import AsyncClient

@pytest.fixture(scope="function")
async def client(db_session):
    """
    テスト用FastAPIクライアント（非同期）
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
```

**テストコードの変更例**:
```python
# test_auth.py
@pytest.mark.asyncio
async def test_login_success(self, client, test_user):
    """正常なログイン"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
```

**大原則評価**:
- ✅ **根本解決**: イベントループの競合を根本的に解決
- ✅ **シンプル構造**: 非同期テストを統一し、シンプルな構造
- ✅ **統一・同一化**: すべてのテストを非同期テストに統一
- ✅ **具体的**: 具体的な実装方法を提示
- ✅ **安全確実**: 既存の非同期テストパターンに準拠

**メリット**:
- イベントループの競合を完全に回避
- 非同期テストの統一により、コードの一貫性が向上
- FastAPIの非同期アプリケーションに適したテスト方法

**デメリット**:
- すべてのテストコードを非同期に変更する必要がある（約30テスト）
- テストコードの変更量が多い（約500-1000行）

**影響範囲**:
- テストコード: 約30テストファイル、約500-1000行の変更
- テストフィクスチャ: `conftest.py`の`client`フィクスチャを変更
- 依存関係: 追加の依存関係は不要（`httpx`は既に`requirements.txt`に含まれている）

#### 修正案2: pytest-asyncioの設定調整（暫定解決）

**内容**:
- `pytest.ini`の`asyncio_mode`を`auto`から`strict`に変更
- イベントループの管理を明示的に制御
- `TestClient`を使用するテストを同期テストに統一

**実装方法**:
```ini
# pytest.ini
[pytest]
asyncio_mode = strict
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**大原則評価**:
- ⚠️ **暫定解決**: 根本的な解決ではなく、エラーの回避
- ⚠️ **複雑構造**: 同期テストと非同期テストが混在し、複雑になる
- ❌ **特殊独自**: 特殊な設定が必要
- ⚠️ **一般**: 一般的な対処法
- ✅ **安全確実**: 既存のテストコードを大きく変更せずに実装可能

**メリット**:
- テストコードの変更量が少ない
- 既存のテストコードを大きく変更せずに実装可能

**デメリット**:
- 根本的な解決にならない（イベントループの競合は残る可能性がある）
- 同期テストと非同期テストが混在し、コードの一貫性が低下
- 将来的に問題が再発する可能性がある

**影響範囲**:
- テストコード: 最小限の変更（`@pytest.mark.asyncio`の追加・削除）
- テストフィクスチャ: 変更不要
- 設定ファイル: `pytest.ini`のみ変更

#### 修正案3: イベントループの明示的な管理（暫定解決）

**内容**:
- `conftest.py`でイベントループを明示的に管理
- `TestClient`を使用する前にイベントループを確認
- セッションのクローズ処理を改善

**実装方法**:
```python
# conftest.py
@pytest.fixture(scope="function")
async def db_session():
    """
    テスト用データベースセッション
    """
    # ... 既存のコード ...
    
    session = None
    try:
        session = TestSessionLocal()
        yield session
    finally:
        if session:
            # イベントループが閉じられていないことを確認
            try:
                loop = asyncio.get_running_loop()
                if loop.is_closed():
                    # イベントループが閉じられている場合はスキップ
                    return
            except RuntimeError:
                # イベントループが存在しない場合はスキップ
                return
            
            try:
                await session.rollback()
            except (Exception, RuntimeError):
                pass
            finally:
                try:
                    await session.close()
                except (Exception, RuntimeError):
                    pass
```

**大原則評価**:
- ❌ **暫定解決**: 根本的な解決ではなく、エラーの回避
- ❌ **複雑構造**: 複雑なエラーハンドリングが必要
- ❌ **特殊独自**: 特殊な処理が必要
- ⚠️ **一般**: 一般的な対処法
- ⚠️ **安全確実**: エラーを回避できるが、根本的な解決ではない

**メリット**:
- テストコードの変更が不要
- 既存のテストコードを変更せずに実装可能

**デメリット**:
- 根本的な解決にならない（イベントループの競合は残る可能性がある）
- 複雑なエラーハンドリングが必要
- 将来的に問題が再発する可能性がある

**影響範囲**:
- テストコード: 変更不要
- テストフィクスチャ: `conftest.py`の`db_session`フィクスチャのみ変更
- 設定ファイル: 変更不要

---

## 4. 推奨修正案の詳細

### 4.1 修正案1: AsyncClientの使用（推奨）

**理由**:
- 大原則に最も適合（根本解決、シンプル構造、統一・同一化、具体的、安全確実）
- イベントループの競合を根本的に解決
- FastAPIの非同期アプリケーションに適したテスト方法

**実装ステップ**:

#### ステップ1: conftest.pyの修正

```python
# conftest.py
from httpx import AsyncClient
from fastapi.testclient import TestClient  # 後方互換性のため残す

@pytest.fixture(scope="function")
async def client(db_session):
    """
    テスト用FastAPIクライアント（非同期）
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

# 後方互換性のため、同期クライアントも提供（非推奨）
@pytest.fixture(scope="function")
def sync_client(db_session):
    """
    テスト用FastAPIクライアント（同期・非推奨）
    後方互換性のため残すが、新規テストでは使用しない
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
```

#### ステップ2: テストコードの修正

**修正が必要なテストファイル**:
1. `test_auth.py` - 5テスト
2. `test_integration.py` - 8テスト
3. `test_session_token.py` - 6テスト
4. `test_chat_api.py` - 2テスト
5. `test_chat_service.py` - 1テスト
6. `test_escalation.py` - 1テスト
7. `test_overnight_queue.py` - 1テスト
8. `test_vector_search.py` - 2テスト

**修正例**:
```python
# test_auth.py（修正前）
def test_login_success(self, client, test_user):
    """正常なログイン"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK

# test_auth.py（修正後）
@pytest.mark.asyncio
async def test_login_success(self, client, test_user):
    """正常なログイン"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
```

**修正パターン**:
1. テスト関数に`@pytest.mark.asyncio`デコレータを追加
2. テスト関数を`async def`に変更
3. `client.post()`を`await client.post()`に変更
4. `client.get()`を`await client.get()`に変更
5. `client.put()`を`await client.put()`に変更
6. `client.delete()`を`await client.delete()`に変更

#### ステップ3: テスト実行と確認

**確認項目**:
- すべてのテストがパスすることを確認
- イベントループエラーが発生しないことを確認
- テスト実行時間が適切であることを確認

---

## 5. 他の機能やUIへの影響調査

### 5.1 影響範囲の分析

#### 影響を受けるファイル

**テストファイル（約30ファイル）**:
1. `backend/tests/test_auth.py` - 5テスト
2. `backend/tests/test_integration.py` - 8テスト
3. `backend/tests/test_session_token.py` - 6テスト
4. `backend/tests/test_chat_api.py` - 2テスト
5. `backend/tests/test_chat_service.py` - 1テスト
6. `backend/tests/test_escalation.py` - 1テスト
7. `backend/tests/test_overnight_queue.py` - 1テスト
8. `backend/tests/test_vector_search.py` - 2テスト

**テストフィクスチャ**:
- `backend/tests/conftest.py` - `client`フィクスチャを変更

**設定ファイル**:
- 変更不要（`pytest.ini`は変更不要）

#### 影響を受けないファイル

**本番コード**:
- ✅ すべての本番コード（`app/`ディレクトリ）は影響を受けない
- ✅ APIエンドポイント、サービス、モデルなどは変更不要

**フロントエンド**:
- ✅ フロントエンドコードは影響を受けない
- ✅ UIの動作は変更されない

**データベース**:
- ✅ データベーススキーマは変更不要
- ✅ マイグレーションファイルは変更不要

**外部サービス**:
- ✅ OpenAI API、Redis、PostgreSQLなどの外部サービスは影響を受けない

### 5.2 競合・干渉リスクの評価

#### リスク1: テストコードの変更による回帰

**リスク内容**:
- テストコードの変更により、既存のテストが失敗する可能性

**リスク評価**: **低**
- テストコードのみの変更であり、本番コードは変更しない
- テストの動作は変更されるが、テストの目的（APIの動作確認）は変わらない

**対策**:
- 段階的に修正を実施（1ファイルずつ修正・確認）
- 修正後にすべてのテストを実行して確認
- バックアップを作成してから修正

#### リスク2: テスト実行時間の増加

**リスク内容**:
- 非同期テストへの変更により、テスト実行時間が増加する可能性

**リスク評価**: **低**
- `AsyncClient`は`TestClient`と同等のパフォーマンス
- 非同期テストの実行時間は同期テストと同等または高速

**対策**:
- テスト実行時間を測定して確認
- 必要に応じてテストの最適化を実施

#### リスク3: テストコードの複雑化

**リスク内容**:
- 非同期テストへの変更により、テストコードが複雑になる可能性

**リスク評価**: **低**
- 非同期テストは既に使用されている（約40テストが既に非同期）
- 統一されたパターンにより、コードの一貫性が向上

**対策**:
- 統一されたパターンを使用
- テストコードのドキュメント化

#### リスク4: 後方互換性の問題

**リスク内容**:
- 既存のテストコードとの互換性の問題

**リスク評価**: **低**
- 段階的に修正を実施することで、互換性を維持
- 後方互換性のため、`sync_client`フィクスチャも提供

**対策**:
- 段階的に修正を実施
- 後方互換性のため、`sync_client`フィクスチャも提供

### 5.3 影響を受けない機能の確認

#### 本番コード

**APIエンドポイント**:
- ✅ すべてのAPIエンドポイントは影響を受けない
- ✅ リクエスト・レスポンスの処理は変更されない

**サービス層**:
- ✅ すべてのサービス（認証、チャット、FAQ等）は影響を受けない
- ✅ ビジネスロジックは変更されない

**データベース層**:
- ✅ データベース接続、セッション管理は影響を受けない
- ✅ モデル、スキーマは変更されない

**AIエンジン**:
- ✅ RAG統合型AI対話エンジンは影響を受けない
- ✅ OpenAI APIとの連携は変更されない

#### フロントエンド

**UIコンポーネント**:
- ✅ すべてのUIコンポーネントは影響を受けない
- ✅ ユーザーインターフェースは変更されない

**API通信**:
- ✅ フロントエンドとバックエンドのAPI通信は影響を受けない
- ✅ リクエスト・レスポンスの形式は変更されない

#### 外部サービス

**OpenAI API**:
- ✅ OpenAI APIとの連携は影響を受けない
- ✅ APIキー、エンドポイントは変更されない

**Redis**:
- ✅ Redisとの連携は影響を受けない
- ✅ セッション管理、キャッシュは変更されない

**PostgreSQL**:
- ✅ PostgreSQLとの連携は影響を受けない
- ✅ データベース接続、クエリは変更されない

---

## 6. 修正案の比較

### 6.1 修正案の比較表

| 項目 | 修正案1: AsyncClient | 修正案2: pytest-asyncio設定 | 修正案3: イベントループ管理 |
|------|---------------------|---------------------------|-------------------------|
| **根本解決** | ✅ 完全に解決 | ⚠️ 部分的に回避 | ❌ 回避のみ |
| **シンプル構造** | ✅ 統一された構造 | ⚠️ 混在する構造 | ❌ 複雑な構造 |
| **統一・同一化** | ✅ 完全に統一 | ❌ 混在 | ❌ 特殊処理 |
| **具体的** | ✅ 具体的な実装 | ⚠️ 一般的な設定 | ⚠️ 一般的な処理 |
| **安全確実** | ✅ 安全確実 | ⚠️ 暫定的 | ⚠️ 暫定的 |
| **テストコード変更量** | 約500-1000行 | 最小限 | 不要 |
| **実装工数** | 中（2-3時間） | 小（30分） | 小（30分） |
| **将来のリスク** | 低 | 中 | 高 |
| **推奨度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |

### 6.2 推奨修正案

**推奨**: **修正案1: AsyncClientの使用**

**理由**:
1. **根本解決**: イベントループの競合を根本的に解決
2. **大原則に適合**: 根本解決 > 暫定解決、シンプル構造 > 複雑構造、統一・同一化 > 特殊独自
3. **将来のリスクが低い**: 根本的な解決により、将来的な問題の再発を防止
4. **FastAPIに適した方法**: 非同期アプリケーションに適したテスト方法

---

## 7. 実装計画

### 7.1 実装ステップ（修正案1: AsyncClientの使用）

#### ステップ1: バックアップ作成（5分）
- `backend/tests/conftest.py`のバックアップ作成
- 影響を受けるテストファイルのバックアップ作成

#### ステップ2: conftest.pyの修正（15分）
- `client`フィクスチャを`AsyncClient`を使用するように修正
- 後方互換性のため、`sync_client`フィクスチャも提供

#### ステップ3: テストコードの修正（段階的、2-3時間）
- 1ファイルずつ修正・確認
- 修正順序:
  1. `test_auth.py`（5テスト）
  2. `test_chat_api.py`（2テスト）
  3. `test_session_token.py`（6テスト）
  4. `test_integration.py`（8テスト）
  5. その他のテストファイル

#### ステップ4: テスト実行と確認（30分）
- すべてのテストを実行
- イベントループエラーが発生しないことを確認
- すべてのテストがパスすることを確認

#### ステップ5: ドキュメント更新（15分）
- テスト実行手順の更新
- 修正内容の記録

**合計所要時間**: 約3-4時間

---

## 8. まとめ

### 8.1 根本原因

**Event loopエラーの根本原因**:
1. `TestClient`が`anyio.BlockingPortal`を使用して新しいイベントループを作成
2. SQLAlchemyの非同期接続（`asyncpg`）が元のイベントループにバインドされている
3. 異なるイベントループ間でFutureを共有しようとするとエラーが発生

### 8.2 推奨修正案

**修正案1: AsyncClientの使用**（推奨）
- 根本解決: ✅
- シンプル構造: ✅
- 統一・同一化: ✅
- 具体的: ✅
- 安全確実: ✅

### 8.3 影響範囲

**影響を受けるファイル**:
- テストファイル: 約30テスト（約500-1000行の変更）
- テストフィクスチャ: `conftest.py`の`client`フィクスチャ

**影響を受けないファイル**:
- 本番コード: すべて影響を受けない
- フロントエンド: 影響を受けない
- 外部サービス: 影響を受けない

### 8.4 競合・干渉リスク

**リスク評価**: **低**
- テストコードのみの変更であり、本番コードは変更しない
- 段階的に修正を実施することで、リスクを最小化
- 後方互換性のため、`sync_client`フィクスチャも提供

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-01  
**Status**: 完全調査分析完了、修正案立案完了、指示待ち


