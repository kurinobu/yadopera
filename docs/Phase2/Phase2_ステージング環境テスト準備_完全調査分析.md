# Phase 2: ステージング環境テスト準備 完全調査分析レポート

**作成日**: 2025年12月13日  
**作成者**: Auto (AI Assistant)  
**目的**: ステージング環境のテストができるよう完全に調査分析を行い、準備を行う

---

## 1. 問題の概要

### 1.1 現在の状況

**バックエンド（Render.com）**:
- ✅ URL: `https://yadopera-backend-staging.onrender.com`
- ✅ ルートエンドポイント（`/`）は正常に動作: `{"message":"やどぺら API v0.3","status":"ok"}`
- ❌ `/admin/dashboard`にアクセスすると`{"detail":"Not Found"}`が返される

**フロントエンド**:
- ❓ ステージング環境のデプロイ状況が不明
- ❓ フロントエンドのURLが不明
- ❓ APIベースURL設定が不明

### 1.2 問題の根本原因

1. **APIルーティングの誤解**:
   - ユーザーが`/admin/dashboard`に直接アクセスしているが、正しいパスは`/api/v1/admin/dashboard`
   - バックエンドのAPIルーターは`/api/v1`プレフィックスで登録されている（`backend/app/main.py` 119行目）
   - 管理画面のAPIエンドポイントは`/api/v1/admin/dashboard`（`backend/app/api/v1/admin/dashboard.py` 13行目）

2. **フロントエンドのデプロイ状況が不明**:
   - ドキュメントによると、フロントエンドはVercelまたはRender.com Static Siteにデプロイされる予定
   - しかし、実際にデプロイされているかは不明
   - `.github/workflows/staging-deploy.yml`にVercelへのデプロイ設定があるが、実際に実行されているかは不明

3. **認証が必要なエンドポイント**:
   - `/api/v1/admin/dashboard`は認証が必要なエンドポイント（`get_current_user`依存）
   - 直接ブラウザでアクセスしても401エラーになる
   - フロントエンドからJWTトークン付きでアクセスする必要がある

---

## 2. 完全調査分析結果

### 2.1 バックエンドのAPIルーティング構造

**確認結果**:
- ✅ `backend/app/main.py` 119行目: `app.include_router(api_router, prefix="/api/v1")`
- ✅ `backend/app/api/v1/router.py` 27行目: `api_router.include_router(dashboard.router, tags=["admin"])`
- ✅ `backend/app/api/v1/admin/dashboard.py` 13行目: `router = APIRouter(prefix="/admin/dashboard", tags=["admin", "dashboard"])`
- ✅ 完全なパス: `/api/v1/admin/dashboard`

**結論**: バックエンドのAPIルーティングは正しく設定されている。

### 2.2 フロントエンドのAPI呼び出し構造

**確認結果**:
- ✅ `frontend/src/api/axios.ts` 10行目: `const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'`
- ✅ `frontend/src/api/axios.ts` 14行目: `baseURL: \`${API_BASE_URL}/api/v1\``
- ✅ `frontend/src/api/dashboard.ts` 13行目: `const response = await apiClient.get<DashboardData>('/admin/dashboard')`
- ✅ 実際のリクエストURL: `${API_BASE_URL}/api/v1/admin/dashboard`

**結論**: フロントエンドのAPI呼び出し構造は正しく設定されている。

### 2.3 ステージング環境のデプロイ設定

**確認結果**:

#### 2.3.1 バックエンド（Render.com）
- ✅ `render.yaml`に設定が記載されている
- ✅ サービス名: `yadopera-backend-staging`
- ✅ ブランチ: `develop`
- ✅ ビルドコマンド: `pip install -r requirements.txt && alembic upgrade head`
- ✅ 起動コマンド: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ CORS設定: `CORS_ORIGINS=https://yadopera-frontend-staging.vercel.app`

#### 2.3.2 フロントエンド（Vercel）
- ⚠️ `.github/workflows/staging-deploy.yml`にVercelへのデプロイ設定がある
- ⚠️ しかし、実際にデプロイされているかは不明
- ⚠️ フロントエンドのURLが不明

#### 2.3.3 フロントエンド（Render.com Static Site）
- ⚠️ ドキュメント（`docs/Deployment/ステージング環境構築手順.md`）にRender.com Static Siteへのデプロイ手順が記載されている
- ⚠️ しかし、実際にデプロイされているかは不明
- ⚠️ フロントエンドのURLが不明

**結論**: フロントエンドのステージング環境のデプロイ状況が不明確。

### 2.4 CORS設定

**確認結果**:
- ✅ `backend/app/core/config.py` 25行目: `cors_origins: str = "http://localhost:5173,http://localhost:3000"`
- ✅ `backend/app/core/config.py` 28-30行目: `cors_origins_list`プロパティでリストに変換
- ✅ `backend/app/main.py` 18-24行目: CORSミドルウェアが設定されている
- ⚠️ `render.yaml` 22行目: `CORS_ORIGINS=https://yadopera-frontend-staging.vercel.app`
- ⚠️ しかし、フロントエンドの実際のURLが不明なため、CORS設定が正しいか確認できない

**結論**: CORS設定は正しく設定されているが、フロントエンドのURLが不明なため確認できない。

### 2.5 認証フロー

**確認結果**:
- ✅ `backend/app/api/v1/admin/dashboard.py` 18行目: `current_user: User = Depends(get_current_user)`
- ✅ `frontend/src/api/axios.ts` 26-35行目: リクエストインターセプターでJWTトークンを追加
- ✅ `frontend/src/api/axios.ts` 54-56行目: 401エラー時にログアウト処理

**結論**: 認証フローは正しく実装されている。

---

## 3. 根本原因の特定

### 3.1 主な問題

1. **フロントエンドのステージング環境がデプロイされていない**
   - フロントエンドのステージング環境のURLが不明
   - フロントエンドがデプロイされていない可能性が高い

2. **APIルーティングの誤解**
   - ユーザーが`/admin/dashboard`に直接アクセスしているが、正しいパスは`/api/v1/admin/dashboard`
   - しかし、これは認証が必要なエンドポイントなので、直接ブラウザでアクセスしても401エラーになる

3. **ステージング環境のテスト手順が不明確**
   - ステージング環境でのテスト手順が明確に定義されていない
   - フロントエンドとバックエンドの連携テストができない

### 3.2 大原則への準拠評価

**大原則**:
1. **根本解決 > 暫定解決**
2. **シンプル構造 > 複雑構造**
3. **統一・同一化 > 特殊独自**
4. **具体的 > 一般**
5. **急がば回れ < 安全/確実**

**評価**:
- ✅ 根本解決: フロントエンドのステージング環境をデプロイし、完全なテスト環境を構築する
- ✅ シンプル構造: 既存のデプロイ設定を活用し、追加の複雑な設定を避ける
- ✅ 統一・同一化: ローカル環境とステージング環境で同じAPI呼び出しパターンを使用
- ✅ 具体的: 明確なデプロイ手順とテスト手順を提示
- ✅ 安全/確実: 段階的にデプロイとテストを実施

---

## 4. 修正案

### 4.1 修正案1: フロントエンドのステージング環境をデプロイする（根本的解決）★推奨

**目的**: フロントエンドのステージング環境をデプロイし、完全なテスト環境を構築する

**実施内容**:

#### 4.1.1 フロントエンドのデプロイ先の選択

**選択肢1: Render.com Static Site（推奨）** ★修正
- 理由: バックエンドと同じプラットフォームで統一
- メリット: 同じダッシュボードで管理可能、Phase 1引き継ぎ書で決定済み
- デメリット: 追加の設定が必要（軽微）

**選択肢2: Vercel（使用しない）** ❌
- 理由: Phase 1引き継ぎ書で「Vercelは今後使用しない」と決定済み
- 問題: 過去にVercelで設定に失敗した経験がある（Phase 0）
- 結論: 使用しない

**推奨**: **選択肢1（Render.com Static Site）** - Phase 1引き継ぎ書で決定済み、大原則（統一・同一化）に準拠

#### 4.1.2 Vercelへのデプロイ手順

1. **Render.com Static Siteの作成**
   - Render.comダッシュボードで「New +」→「Static Site」を選択
   - GitHubリポジトリを接続（既に接続済みの場合は選択）
   - 以下の設定を行う:
     - **Name**: `yadopera-frontend-staging`
     - **Branch**: `develop`
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Publish Directory**: `dist`

2. **環境変数設定**
   - Static Siteダッシュボードで「Environment」タブを開く
   - 以下の環境変数を追加:
     ```bash
     VITE_API_BASE_URL=https://yadopera-backend-staging.onrender.com
     VITE_ENVIRONMENT=staging
     ```

3. **バックエンドのCORS設定を更新**
   - Render.comのバックエンドサービスの「Environment」タブを開く
   - `CORS_ORIGINS`環境変数を更新:
     ```bash
     CORS_ORIGINS=https://yadopera-frontend-staging.onrender.com,http://localhost:5173
     ```
     - 注: Static Siteの実際のURLに置き換える

#### 4.1.3 デプロイ確認

1. **フロントエンドのデプロイ確認**
   - Render.comのダッシュボードでデプロイ状況を確認
   - フロントエンドのURLを確認（例: `https://yadopera-frontend-staging.onrender.com`）

2. **バックエンドのCORS設定確認**
   - Render.comのバックエンドサービスの環境変数を確認
   - フロントエンドのURLがCORS設定に含まれているか確認

3. **動作確認**
   - フロントエンドのURLにアクセス
   - 管理画面のログイン画面が表示されることを確認
   - ログイン後、ダッシュボードが表示されることを確認

**完了条件**:
- ✅ フロントエンドのステージング環境がデプロイされている
- ✅ フロントエンドのURLが確認できる
- ✅ バックエンドのCORS設定が正しく設定されている
- ✅ フロントエンドからバックエンドへのAPI呼び出しが正常に動作する
- ✅ 管理画面のログインとダッシュボード表示が正常に動作する

**所要時間**: 約1時間

**大原則への準拠**: ✅ 根本解決、シンプル構造、統一・同一化、具体的、安全/確実

---

### 4.2 修正案2: Render.com Static Siteへのデプロイ（代替案）

**目的**: バックエンドと同じプラットフォームで統一する

**実施内容**:

1. **Render.com Static Siteの作成**
   - Render.comダッシュボードで「New +」→「Static Site」を選択
   - GitHubリポジトリを接続
   - 以下の設定を行う:
     - **Name**: `yadopera-frontend-staging`
     - **Branch**: `develop`
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Publish Directory**: `dist`

2. **環境変数設定**
   - Static Siteダッシュボードで「Environment」タブを開く
   - 以下の環境変数を追加:
     ```bash
     VITE_API_BASE_URL=https://yadopera-backend-staging.onrender.com
     VITE_ENVIRONMENT=staging
     ```

3. **バックエンドのCORS設定を更新**
   - Render.comのバックエンドサービスの「Environment」タブを開く
   - `CORS_ORIGINS`環境変数を更新:
     ```bash
     CORS_ORIGINS=https://yadopera-frontend-staging.onrender.com,http://localhost:5173
     ```

**完了条件**: 修正案1と同じ

**所要時間**: 約1時間

**大原則への準拠**: ✅ 根本解決、統一・同一化、具体的、安全/確実

---

## 5. ステージング環境のテスト手順

### 5.1 テスト環境の確認

1. **バックエンドの確認**
   - URL: `https://yadopera-backend-staging.onrender.com`
   - ルートエンドポイント: `GET /` → `{"message":"やどぺら API v0.3","status":"ok"}`
   - ヘルスチェック: `GET /health` → `{"status":"ok"}`
   - APIヘルスチェック: `GET /api/v1/health` → `{"status":"ok","database":"ok","redis":"ok"}`

2. **フロントエンドの確認**
   - URL: `https://yadopera-frontend-staging.vercel.app`（またはRender.comのURL）
   - ルートページが表示されることを確認
   - 管理画面のログイン画面が表示されることを確認

### 5.2 認証フローのテスト

1. **ログイン**
   - フロントエンドの管理画面にアクセス
   - ログイン画面が表示されることを確認
   - テストユーザーでログイン（`test@example.com` / `testpassword123`）
   - ログインが成功することを確認

2. **ダッシュボード表示**
   - ログイン後、ダッシュボードが表示されることを確認
   - API呼び出しが正常に動作することを確認（ブラウザの開発者ツールで確認）

### 5.3 機能テスト

1. **管理画面の機能テスト**
   - ダッシュボード表示
   - FAQ管理（追加、編集、削除）
   - QRコード生成
   - スタッフ不在時間帯対応キュー
   - 施設設定

2. **ゲスト画面の機能テスト**
   - 言語選択
   - ウェルカム画面表示
   - AI対話
   - フィードバック送信

### 5.4 エラーハンドリングのテスト

1. **認証エラーのテスト**
   - 無効なトークンでAPI呼び出し
   - 401エラーが返されることを確認
   - ログアウト処理が実行されることを確認

2. **ネットワークエラーのテスト**
   - バックエンドが停止している場合のエラーハンドリング
   - タイムアウトエラーのハンドリング

---

## 6. 必須の課題

### 6.1 最優先課題

1. **フロントエンドのステージング環境のデプロイ**（必須）
   - 現状: フロントエンドのステージング環境がデプロイされていない
   - 影響: ステージング環境でのテストができない
   - 解決方法: 修正案1を実施

2. **バックエンドのCORS設定の更新**（必須）
   - 現状: フロントエンドのURLが不明なため、CORS設定が正しいか確認できない
   - 影響: フロントエンドからバックエンドへのAPI呼び出しが失敗する可能性がある
   - 解決方法: フロントエンドのURLを確認後、CORS設定を更新

### 6.2 高優先度課題

3. **ステージング環境のテスト手順の明確化**（推奨）
   - 現状: ステージング環境でのテスト手順が明確に定義されていない
   - 影響: テストの実施が困難
   - 解決方法: 本レポートの「5. ステージング環境のテスト手順」を参照

4. **GitHub Actionsの設定確認**（推奨）
   - 現状: `.github/workflows/staging-deploy.yml`にVercelへのデプロイ設定があるが、実際に実行されているかは不明
   - 影響: 自動デプロイが機能しない可能性がある
   - 解決方法: GitHub Actionsの実行履歴を確認し、必要に応じて修正

---

## 7. まとめ

### 7.1 調査結果の要約（2025-12-13更新）

1. **バックエンド**: ✅ 正常にデプロイされている
   - URL: `https://yadopera-backend-staging.onrender.com`
2. **フロントエンド**: ✅ ステージング環境がデプロイされている
   - URL: `https://yadopera-frontend-staging.onrender.com`
3. **APIルーティング**: ✅ 正しく設定されている
4. **CORS設定**: ✅ 正しく設定されている
   - `CORS_ORIGINS=https://yadopera-frontend-staging.onrender.com,http://localhost:5173`
5. **認証フロー**: ✅ 正しく実装されている
6. **テストユーザー**: ✅ 作成済み（問題2解決済み）
   - メールアドレス: `test@example.com`
   - パスワード: `testpassword123`
   - ユーザーID: 87
7. **PWAアイコンとvite.svg**: ✅ 作成済み（問題3解決済み）
   - `frontend/public/pwa-192x192.png`
   - `frontend/public/pwa-512x512.png`
   - `frontend/public/vite.svg`
   - `frontend/public/favicon.ico`

### 7.2 解決済みの問題（2025-12-13）

#### 問題2: ステージング環境でテストユーザーが存在しない ✅ **解決済み**

**解決日**: 2025年12月13日  
**解決方法**: `backend/create_staging_test_data.py`を実行してテストユーザーを作成

**テストユーザー情報**:
- メールアドレス: `test@example.com`
- パスワード: `testpassword123`
- ユーザーID: 87
- 施設ID: 347
- 施設slug: `test-facility`

**状態**: ✅ ログイン可能

#### 問題3: PWAアイコンとvite.svgの404エラー ✅ **解決済み**

**解決日**: 2025年12月13日  
**解決方法**: `frontend/public`ディレクトリに以下のファイルを作成

**作成したファイル**:
- `frontend/public/pwa-192x192.png`
- `frontend/public/pwa-512x512.png`
- `frontend/public/vite.svg`
- `frontend/public/favicon.ico`

**状態**: ✅ 404エラー解消

### 7.3 推奨される次のステップ

1. **ステージング環境のテスト手順を実施**
   - 認証フローのテスト
   - 機能テスト
   - エラーハンドリングのテスト

2. **ドキュメントの更新**
   - ステージング環境のURLを記録
   - テスト手順を明確化

### 7.4 大原則への準拠

- ✅ **根本解決**: フロントエンドのステージング環境をデプロイし、完全なテスト環境を構築
- ✅ **シンプル構造**: 既存のデプロイ設定を活用し、追加の複雑な設定を避ける
- ✅ **統一・同一化**: ローカル環境とステージング環境で同じAPI呼び出しパターンを使用
- ✅ **具体的**: 明確なデプロイ手順とテスト手順を提示
- ✅ **安全/確実**: 段階的にデプロイとテストを実施

---

## 8. 参考資料

- `docs/Deployment/ステージング環境構築手順.md`
- `docs/Deployment/Render_Railway_手動設定_実行手順.md`
- `docs/Deployment/Render_Static_Site_ステージング環境デプロイ手順.md`
- `docs/Phase2/Phase2_引き継ぎ書_20251213.md`
- `docs/Phase2/Phase2_ステージング環境ログインエラー_完全調査分析レポート.md`
- `.github/workflows/staging-deploy.yml`
- `render.yaml`
- `backend/app/main.py`
- `backend/app/api/v1/admin/dashboard.py`
- `frontend/src/api/axios.ts`
- `frontend/src/api/dashboard.ts`

---

**状態**: ✅ **問題2と問題3は解決済み（2025-12-13）。フロントエンドのステージング環境はデプロイ済み。**

