# QRコード読み取りエラー（GitHub Pages 404）完全調査分析・修正案

**作成日時**: 2026年01月20日  
**実施者**: AI Assistant  
**目的**: ステージング環境で生成されたQRコードをスマートフォンで読み取った際に発生する「GitHub Pages 404エラー」の原因を完全に調査分析し、大原則に準拠した修正案を提示  
**状態**: 📋 **完全調査分析完了・修正案提示完了**

**重要**: 指示があるまで修正を実施しません。調査分析と修正案提示のみです。

---

## 1. 問題の概要

### 1.1 発生状況

**環境**: ステージング環境（`https://yadopera-frontend-staging.onrender.com`）  
**ユーザー**: `test31@example.com`（freeプラン）  
**操作**: QRコード生成 → スマートフォンで読み取り → アクセス

**エラーメッセージ**:
```
File not found

The site configured at this address does not contain the requested file.

If this is your site, make sure that the filename case matches the URL as well as any file permissions.
For root URLs (like http://example.com/) you must provide an index.html file.

Read the full documentation for more information about using GitHub Pages.

GitHub Status — @githubstatus
```

### 1.2 気になる点

**「GitHub Status — @githubstatus」という記述**:
- エラーメッセージに「GitHub Pages」と「GitHub Status — @githubstatus」が含まれている
- これは、QRコードに埋め込まれたURLが存在しないため、GitHub Pagesの404エラーページが表示されている可能性が高い

### 1.3 テスト方法の確認

**テスト方法**: ✅ **正しい**
- QRコード生成 → スマートフォンで読み取り → アクセスという流れは正しい
- 問題はQRコードに埋め込まれたURLにある

---

## 2. 根本原因の調査分析

### 2.1 QRコード生成処理の確認

**ファイル**: `backend/app/services/qr_code_service.py`

**問題箇所（60行目）**:
```python
def _generate_url(
    self,
    facility_slug: str,
    location: str,
    custom_location_name: Optional[str] = None,
    session_token: Optional[str] = None,
    base_url: str = "https://yadopera.com"  # ❌ ハードコードされている
) -> str:
```

**問題点**:
1. **base_urlがハードコードされている**: `"https://yadopera.com"`がデフォルト値としてハードコードされている
2. **環境変数を使用していない**: ステージング環境と本番環境で異なるURLを使用すべきだが、環境変数から取得していない
3. **ステージング環境では間違ったURLが生成される**: ステージング環境でQRコードを生成すると、`https://yadopera.com/f/{facility_slug}?location={location}`というURLが生成されるが、これは本番環境のURLであり、ステージング環境では存在しない

### 2.2 環境変数の確認

**ファイル**: `backend/app/core/config.py`

**現在の設定**:
```python
class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # OpenAI
    openai_api_key: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    
    # App
    environment: str = "development"
    debug: bool = True
    
    # CORS (comma-separated string to List[str])
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
```

**問題点**:
- ❌ **FRONTEND_URL環境変数が定義されていない**: QRコード生成時に使用するフロントエンドURLを環境変数から取得できない

### 2.3 ステージング環境の設定確認

**ファイル**: `render.yaml`

**現在の設定**:
```yaml
services:
  - type: web
    name: yadopera-backend-staging
    envVars:
      - key: CORS_ORIGINS
        value: https://yadopera-frontend-staging.onrender.com,http://localhost:5173
      - key: ENVIRONMENT
        value: staging
```

**問題点**:
- ❌ **FRONTEND_URL環境変数が設定されていない**: ステージング環境でFRONTEND_URLが設定されていない

### 2.4 エラーメッセージの分析

**「GitHub Status — @githubstatus」の意味**:
- これは、QRコードに埋め込まれたURL（`https://yadopera.com/f/{facility_slug}?location={location}`）が存在しないため、GitHub Pagesの404エラーページが表示されている
- `https://yadopera.com`がGitHub Pagesでホスティングされている場合、存在しないパスにアクセスするとGitHub Pagesの404エラーページが表示される
- または、`https://yadopera.com`が存在しないドメインの場合、DNS解決に失敗し、GitHub Pagesの404エラーページが表示される可能性がある

**実際の動作**:
1. QRコードに`https://yadopera.com/f/{facility_slug}?location={location}`が埋め込まれる
2. スマートフォンでQRコードを読み取る
3. ブラウザが`https://yadopera.com/f/{facility_slug}?location={location}`にアクセスしようとする
4. このURLが存在しない（またはGitHub Pagesでホスティングされているが、該当パスが存在しない）
5. GitHub Pagesの404エラーページが表示される

---

## 3. 大原則への準拠評価

### 3.1 根本解決 > 暫定解決

**根本解決**: ✅ 環境変数からbase_urlを取得するように修正する
- `FRONTEND_URL`環境変数を追加
- `qr_code_service.py`で環境変数からbase_urlを取得
- ステージング環境と本番環境で異なるURLを使用

**暫定解決**: ❌ QRコード生成時にbase_urlを手動で指定する
- 環境ごとに異なる処理が必要になる
- 保守性が低下する

### 3.2 シンプル構造 > 複雑構造

**シンプル構造**: ✅ 環境変数からbase_urlを取得するだけ
- `Settings`クラスに`FRONTEND_URL`を追加
- `qr_code_service.py`で`settings.FRONTEND_URL`を使用

**複雑構造**: ❌ 環境ごとに異なる処理を追加する
- 条件分岐が増える
- 保守性が低下する

### 3.3 統一・同一化 > 特殊独自

**統一・同一化**: ✅ すべての環境で同じロジックを使用
- 環境変数からbase_urlを取得するロジックを統一
- 環境ごとに異なる処理を追加しない

**特殊独自**: ❌ 環境ごとに異なる処理を追加する
- ステージング環境と本番環境で異なる処理が必要になる

### 3.4 具体的 > 一般

**具体的**: ✅ 環境変数名とデフォルト値を明確に定義
- `FRONTEND_URL`環境変数を使用
- デフォルト値は`https://yadopera.com`（本番環境用）

**一般**: ❌ 抽象的な説明のみ
- 「環境変数を使用する」という説明だけでは不十分

### 3.5 拙速 < 安全確実

**安全確実**: ✅ 環境変数のバリデーションとエラーハンドリングを追加
- `FRONTEND_URL`が設定されていない場合のエラーハンドリング
- デフォルト値の設定（本番環境用）

**拙速**: ❌ エラーハンドリングなしで実装する
- 環境変数が設定されていない場合にエラーが発生する可能性がある

---

## 4. 修正案

### 修正案1: 環境変数からbase_urlを取得するように修正（推奨・根本解決）

**目的**: QRコード生成時に環境変数からbase_urlを取得し、ステージング環境と本番環境で異なるURLを使用できるようにする

**実施内容**:

#### ステップ1: `backend/app/core/config.py`に`FRONTEND_URL`環境変数を追加

**修正前**:
```python
class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # OpenAI
    openai_api_key: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    
    # App
    environment: str = "development"
    debug: bool = True
    
    # CORS (comma-separated string to List[str])
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
```

**修正後**:
```python
class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # OpenAI
    openai_api_key: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    
    # App
    environment: str = "development"
    debug: bool = True
    
    # Frontend URL (QRコード生成用)
    frontend_url: str = "https://yadopera.com"  # デフォルトは本番環境用
    
    # CORS (comma-separated string to List[str])
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
```

#### ステップ2: `backend/app/services/qr_code_service.py`で環境変数からbase_urlを取得

**修正前**:
```python
def _generate_url(
    self,
    facility_slug: str,
    location: str,
    custom_location_name: Optional[str] = None,
    session_token: Optional[str] = None,
    base_url: str = "https://yadopera.com"  # ❌ ハードコード
) -> str:
```

**修正後**:
```python
from app.core.config import settings

def _generate_url(
    self,
    facility_slug: str,
    location: str,
    custom_location_name: Optional[str] = None,
    session_token: Optional[str] = None,
    base_url: Optional[str] = None  # ✅ オプショナル、デフォルトは環境変数から取得
) -> str:
    """
    QRコードURL生成
    
    Args:
        facility_slug: 施設slug
        location: 設置場所
        custom_location_name: カスタム設置場所名（オプション）
        session_token: 会話引き継ぎコード（オプション）
        base_url: ベースURL（オプション、未指定の場合は環境変数から取得）
    
    Returns:
        str: QRコードURL
    """
    # base_urlが指定されていない場合は環境変数から取得
    if base_url is None:
        base_url = settings.frontend_url
    
    url = f"{base_url}/f/{facility_slug}?location={location}"
    
    if custom_location_name:
        url += f"&custom={custom_location_name}"
    
    if session_token:
        url += f"&token={session_token}"
    
    return url
```

#### ステップ3: `render.yaml`に`FRONTEND_URL`環境変数を追加

**修正前**:
```yaml
services:
  - type: web
    name: yadopera-backend-staging
    envVars:
      - key: CORS_ORIGINS
        value: https://yadopera-frontend-staging.onrender.com,http://localhost:5173
      - key: ENVIRONMENT
        value: staging
```

**修正後**:
```yaml
services:
  - type: web
    name: yadopera-backend-staging
    envVars:
      - key: CORS_ORIGINS
        value: https://yadopera-frontend-staging.onrender.com,http://localhost:5173
      - key: ENVIRONMENT
        value: staging
      - key: FRONTEND_URL
        value: https://yadopera-frontend-staging.onrender.com  # ✅ ステージング環境用
```

#### ステップ4: Render.comダッシュボードで環境変数を設定

**ステージング環境**:
- `FRONTEND_URL=https://yadopera-frontend-staging.onrender.com`

**本番環境**（将来）:
- `FRONTEND_URL=https://yadopera.com`

**実施手順**:
1. Render.comダッシュボードにログイン
2. `yadopera-backend-staging`サービスの「Environment」タブを開く
3. 「Add Environment Variable」をクリック
4. `FRONTEND_URL`を追加し、値に`https://yadopera-frontend-staging.onrender.com`を設定
5. サービスを再デプロイ

---

## 5. 修正後の動作確認

### 5.1 ステージング環境での確認

**期待される動作**:
1. QRコード生成時に`https://yadopera-frontend-staging.onrender.com/f/{facility_slug}?location={location}`が生成される
2. スマートフォンでQRコードを読み取る
3. ブラウザが`https://yadopera-frontend-staging.onrender.com/f/{facility_slug}?location={location}`にアクセスする
4. ステージング環境のフロントエンドが正常に表示される
5. GitHub Pagesの404エラーページが表示されない

### 5.2 本番環境での確認（将来）

**期待される動作**:
1. QRコード生成時に`https://yadopera.com/f/{facility_slug}?location={location}`が生成される
2. スマートフォンでQRコードを読み取る
3. ブラウザが`https://yadopera.com/f/{facility_slug}?location={location}`にアクセスする
4. 本番環境のフロントエンドが正常に表示される

---

## 6. 影響範囲

### 6.1 影響を受けるファイル

1. **`backend/app/core/config.py`**: `FRONTEND_URL`環境変数を追加
2. **`backend/app/services/qr_code_service.py`**: 環境変数からbase_urlを取得するように修正
3. **`render.yaml`**: `FRONTEND_URL`環境変数を追加（オプション、コードとして管理する場合）

### 6.2 影響を受ける機能

- **QRコード生成機能**: すべてのQRコード生成処理が影響を受ける
- **既存のQRコード**: 既に生成されたQRコードは影響を受けない（新しいQRコードのみ影響を受ける）

### 6.3 後方互換性

- ✅ **後方互換性あり**: `base_url`パラメータをオプショナルにすることで、既存のコードとの互換性を維持
- ✅ **デフォルト値**: 環境変数が設定されていない場合は`https://yadopera.com`（本番環境用）を使用

---

## 7. テスト計画

### 7.1 ユニットテスト

**テストケース**:
1. 環境変数`FRONTEND_URL`が設定されている場合、その値が使用されることを確認
2. 環境変数`FRONTEND_URL`が設定されていない場合、デフォルト値`https://yadopera.com`が使用されることを確認
3. `base_url`パラメータが指定されている場合、その値が優先されることを確認

### 7.2 統合テスト

**テストケース**:
1. ステージング環境でQRコードを生成し、正しいURLが生成されることを確認
2. 生成されたQRコードをスマートフォンで読み取り、正常にアクセスできることを確認
3. GitHub Pagesの404エラーページが表示されないことを確認

### 7.3 ブラウザテスト

**テストケース**:
1. ステージング環境でQRコードを生成
2. スマートフォンでQRコードを読み取り
3. 正常にアクセスできることを確認
4. GitHub Pagesの404エラーページが表示されないことを確認

---

## 8. まとめ

### 8.1 根本原因

**根本原因**: QRコード生成時の`base_url`がハードコードされており、ステージング環境と本番環境で異なるURLを使用できない

**証拠**:
1. `qr_code_service.py`の60行目で`base_url: str = "https://yadopera.com"`がハードコードされている
2. 環境変数`FRONTEND_URL`が定義されていない
3. ステージング環境でQRコードを生成すると、本番環境のURL（`https://yadopera.com`）が生成される
4. このURLが存在しないため、GitHub Pagesの404エラーページが表示される

### 8.2 修正案

**修正案1（推奨）**: 環境変数からbase_urlを取得するように修正
- `FRONTEND_URL`環境変数を追加
- `qr_code_service.py`で環境変数からbase_urlを取得
- ステージング環境と本番環境で異なるURLを使用

**大原則への準拠**:
- ✅ 根本解決 > 暫定解決
- ✅ シンプル構造 > 複雑構造
- ✅ 統一・同一化 > 特殊独自
- ✅ 具体的 > 一般
- ✅ 拙速 < 安全確実

### 8.3 次のステップ

1. **修正案の承認**: ユーザーから修正案の承認を得る
2. **修正実施**: 修正案1を実施
3. **環境変数設定**: Render.comダッシュボードで`FRONTEND_URL`環境変数を設定
4. **再デプロイ**: バックエンドサービスを再デプロイ
5. **動作確認**: ステージング環境でQRコードを生成し、スマートフォンで読み取って正常にアクセスできることを確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2026年01月20日  
**Status**: 📋 **完全調査分析完了・修正案提示完了（修正実施待ち）**

