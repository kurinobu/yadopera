# ローカル環境でのブラウザテスト手順

Docker とビルドを確認し、即座にブラウザテストできる状態にする手順です。

## 前提

- **Docker Desktop** が起動していること
- **backend/.env** が存在し、少なくとも以下が設定されていること（未設定時は `backend/.env.example` をコピーして編集）:
  - `OPENAI_API_KEY`
  - `SECRET_KEY`
  - その他 `backend/.env.example` 参照

## 1. 起動（初回または再起動時）

プロジェクトルートで:

```bash
docker compose up -d --build
```

または既存スクリプトを使う場合:

```bash
./scripts/docker-build-and-test.sh
```

## 2. マイグレーション（DB を新規作成した場合のみ）

初回や DB を作り直した場合は、マイグレーションを実行します:

```bash
docker compose exec backend alembic upgrade head
```

## 3. アクセスURL

| 用途           | URL                      |
|----------------|--------------------------|
| フロント（SPA） | http://localhost:5173    |
| API（Swagger）  | http://localhost:8000/docs |
| API（ヘルス）   | http://localhost:8000/api/v1/health |

## 4. ブラウザテストの開始

1. ブラウザで **http://localhost:5173** を開く
2. ゲスト: 言語選択 → 施設ページ → チャット／クーポンなど
3. 管理: `/admin/login` でログイン → ダッシュボード・施設設定・リード一覧など

## 5. 状態確認

```bash
# コンテナ一覧
docker compose ps

# バックエンドログ（確認用）
docker compose logs -f backend
```

## 6. 停止

```bash
docker compose down
```

---

## ビルド確認（Docker を使わない場合）

- **フロント**: `cd frontend && npm run build`  
  - `vue-tsc` と `vite build` が通れば OK（PWA Service Worker の警告は既知で、開発時は `npm run dev` で問題なし）
- **バックエンド**: Docker 内で `uvicorn` が起動しているため、ローカル単体ビルドは通常不要

## トラブルシューティング

| 現象 | 対処 |
|------|------|
| 5173 で接続できない | `docker compose ps` で frontend が Up か確認。`docker compose up -d` で再起動 |
| 8000 で API が返らない | `docker compose logs backend` でエラー確認。`.env` と DB 接続を確認 |
| マイグレーションエラー | `docker compose exec backend alembic upgrade head` を実行。既に適用済みの場合はスキップされる |
| ポート競合 | `docker compose down` のうえ、他アプリが 5173 / 8000 / 5433 / 6379 を使っていないか確認 |
