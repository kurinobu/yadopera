# Render.com環境変数設定 詳細

**SECRET_KEY生成完了**: `aff4ec2b7acd42726b52e838454a7453b8ba8492b437023d005395897b2c3dd6`

---

## 設定する環境変数一覧

### Render.comダッシュボードで設定

1. Web Service（`yadopera-backend-staging`）を選択
2. 「**Environment**」タブを開く
3. 「**Add Environment Variable**」をクリック
4. 以下の環境変数を追加:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:q2qvotspe3muf84hanuy5lw6eascqt82@yamanote.proxy.rlwy.net:15647/railway` |
| `REDIS_URL` | `redis://default:QIpOCNjyhqyHYoaGBUWWaALyuWmVGYjd@shuttle.proxy.rlwy.net:28858` |
| `OPENAI_API_KEY` | 既存のOpenAI APIキー |
| `SECRET_KEY` | `aff4ec2b7acd42726b52e838454a7453b8ba8492b437023d005395897b2c3dd6` |
| `CORS_ORIGINS` | `https://yadopera-frontend-staging.onrender.com` |
| `ENVIRONMENT` | `staging` |
| `DEBUG` | `False` |
| `LOG_LEVEL` | `INFO` |

---

## 重要事項

1. **DATABASE_URL**: `postgresql://`を`postgresql+asyncpg://`に変更済み
2. **CORS_ORIGINS**: フロントエンドURL（後でStatic Site作成後に更新）
3. 環境変数を追加すると、自動的にデプロイが再実行されます

---

## 次のステップ

環境変数の設定が完了したら:
1. デプロイの完了を待つ
2. ヘルスチェックで動作確認
3. フロントエンドの設定に進む

