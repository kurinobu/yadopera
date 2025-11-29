# Render.com Web Service設定 正確な手順

**注意**: Render.comのUIは変更される可能性があります。実際の画面に合わせて設定してください。

---

## 設定項目の説明

### Language/Runtime

- **選択**: `Python 3` を選択
- Dockerがデフォルトになっている場合、`Python 3`に変更してください

### Build Command

- **場所**: Build Commandという専用のフィールドがあるはずです
- **値**: `pip install -r requirements.txt && alembic upgrade head`
- **注意**: Environment Variablesではありません

### Start Command

- **場所**: Start Commandという専用のフィールドがあるはずです
- **値**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **注意**: Environment Variablesではありません

### Environment Variables

- **用途**: 環境変数（DATABASE_URL、REDIS_URL等）を設定する場所
- **注意**: Build CommandやStart Commandを入力する場所ではありません

---

## 確認事項

現在のRender.comの設定画面で、以下を確認してください:

1. **Language/Runtime**の選択肢に`Python 3`があるか
2. **Build Command**というフィールドがあるか（どこにあるか）
3. **Start Command**というフィールドがあるか（どこにあるか）
4. **Environment Variables**セクションがあるか

---

## 次のステップ

現在の設定画面の状態を教えてください。具体的に:
- Language/Runtimeの選択肢一覧
- 表示されているフィールド名
- Build CommandやStart Commandを入力できる場所があるか

それに基づいて、正確な手順を案内します。

