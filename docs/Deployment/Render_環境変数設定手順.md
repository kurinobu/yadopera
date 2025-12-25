# Render.com環境変数設定手順

**現在の状態**: Web Service作成・デプロイ完了

---

## 設定する環境変数

### ステップ1: Render.comダッシュボードで環境変数を設定

1. 作成したWeb Service（`yadopera-backend-staging`）を選択
2. 「**Environment**」タブを開く
3. 「**Add Environment Variable**」をクリック
4. 以下の環境変数を追加:

### 必須環境変数

#### 1. DATABASE_URL
- **Key**: `DATABASE_URL`
- **Value**: `postgresql+asyncpg://postgres:q2qvotspe3muf84hanuy5lw6eascqt82@yamanote.proxy.rlwy.net:15647/railway`
- **重要**: `postgresql://`を`postgresql+asyncpg://`に変更

#### 2. REDIS_URL
- **Key**: `REDIS_URL`
- **Value**: `redis://default:QIpOCNjyhqyHYoaGBUWWaALyuWmVGYjd@shuttle.proxy.rlwy.net:28858`

#### 3. OPENAI_API_KEY
- **Key**: `OPENAI_API_KEY`
- **Value**: 既存のOpenAI APIキー（既に取得済み）

#### 4. SECRET_KEY
- **Key**: `SECRET_KEY`
- **Value**: 32文字以上のランダム文字列（生成が必要）

#### 5. CORS_ORIGINS
- **Key**: `CORS_ORIGINS`
- **Value**: `https://yadopera-frontend-staging.onrender.com`（フロントエンドURL、後で設定）

#### 6. ENVIRONMENT
- **Key**: `ENVIRONMENT`
- **Value**: `staging`

#### 7. DEBUG
- **Key**: `DEBUG`
- **Value**: `False`

#### 8. LOG_LEVEL
- **Key**: `LOG_LEVEL`
- **Value**: `INFO`

---

## SECRET_KEYの生成

ターミナルで以下を実行:

```bash
openssl rand -hex 32
```

生成されたキーを`SECRET_KEY`の値として使用してください。

---

## 次のステップ

環境変数の設定が完了したら:
1. デプロイが自動的に再実行される
2. ヘルスチェックで動作確認
3. フロントエンドの設定に進む


