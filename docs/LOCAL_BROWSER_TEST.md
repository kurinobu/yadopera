# ローカル環境でのブラウザテスト手順

Docker とビルドを確認し、即座にブラウザテストできる状態にする手順です。

## 前提

- **Docker Desktop** が起動していること
- **backend/.env** が存在し、少なくとも以下が設定されていること（未設定時は `backend/.env.example` をコピーして編集）:
  - `OPENAI_API_KEY`
  - `SECRET_KEY`
  - その他 `backend/.env.example` 参照

**CSV一括登録 代行申し込み**で**メール送信まで含めた完全なテスト**をする場合、以下が必須（未設定だと送信されず準備完了とは言えない）:
- `BREVO_API_KEY` … 未設定だと申し込み送信時に EmailService 初期化でエラーになる
- `ADMIN_NOTIFICATION_EMAIL` … 申し込みメールの**送信先**。未設定だと申し込みAPIが 503 を返し、メールは送られない

※ 503 の表示確認だけする場合は未設定のままで可。送信先は `backend/.env.example` の `ADMIN_NOTIFICATION_EMAIL` を参照。

## 1. 起動（初回または再起動時）

プロジェクトルートで:

```bash
docker compose up -d --build
```

または既存スクリプトを使う場合:

```bash
./scripts/docker-build-and-test.sh
```

**起動確認**: バックエンドのヘルスとCSV申し込み用ルートの存在確認（認証必須のため 401 で正常）:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health
# → 200 が返ればOK

curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/v1/admin/csv-bulk-request
# → 401（Unauthorized）が返ればルート登録済み
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
| 管理ログイン    | http://localhost:5173/admin/login |
| CSV代行申し込み | http://localhost:5173/admin/csv-bulk-request（要ログイン・Standard/Premium） |
| API（Swagger）  | http://localhost:8000/docs |
| API（ヘルス）   | http://localhost:8000/api/v1/health |

## 4. ブラウザテストの開始

1. ブラウザで **http://localhost:5173** を開く
2. ゲスト: 言語選択 → 施設ページ → チャット／クーポンなど
3. 管理: `/admin/login` でログイン → ダッシュボード・施設設定・リード一覧など

---

## 5a. CSV一括登録 代行申し込み ブラウザテスト（ローカル）

### 準備（送信まで確認する場合＝完全なテスト）

1. **backend/.env** に次を**必ず**設定する（どちらか未設定だとメールは送られない）:
   - `BREVO_API_KEY` … Brevo の API キー（[Brevo](https://app.brevo.com/settings/keys/api) で取得）
   - `ADMIN_NOTIFICATION_EMAIL` … 申し込みメールの**送信先**（届けて確認したいメールアドレス）。`backend/.env.example` にも記載あり
   - **設定手順の詳細**（ローカル・ステージング/本番）: [CSV一括登録_有料オプション_運用開始チェックリスト](CSV_bulk_registration_function_implementation_plan/CSV一括登録_有料オプション_運用開始チェックリスト.md) の「環境・設定」→ **「設定方法（運営が手動で行う）」** を参照。
2. **Standard または Premium プランの施設ユーザー**でログインできるアカウントを用意する（CSV一括登録・代行申し込みは Standard/Premium のみ表示）。

上記 1 が未設定のままでは「送信されるか」のテストはできず、503 表示の確認のみとなる。

### 手順

| 順 | 操作 | 期待する表示・動作 |
|----|------|-------------------|
| 1 | `docker compose up -d --build` で起動 | 全コンテナが Up |
| 2 | ブラウザで http://localhost:5173 を開く | トップまたはログイン画面 |
| 3 | Standard/Premium の施設ユーザーで `/admin/login` からログイン | ダッシュボード等が表示される |
| 4 | 左メニューで「**CSV代行の申し込み**」をクリック | 申し込みページ（CSV一括登録 代行の申し込み）が開く |
| 5 | または「FAQ管理」を開き「**代行をご希望の方はこちら**」をクリック | 上記と同じ申し込みページへ遷移 |
| 6 | 施設名・プラン・希望件数・希望言語・メール・担当者を入力し「申し込む」をクリック（ファイルは任意） | 「申し込みを受け付けました。」と表示される |
| 7 | （ADMIN_NOTIFICATION_EMAIL を設定している場合）受信メールを確認 | 件名「【YadOPERA】CSV一括登録代行の申し込み」で、入力内容の表と添付（付けた場合）が届く |
| 8 | ヘルプ（？）ボタン → FAQ タブ → 「**CSV一括登録の代行をお申し込みの方はこちら**」をクリック | 申し込みページへ遷移する |

### 503 の確認（ADMIN_NOTIFICATION_EMAIL 未設定時）

- `ADMIN_NOTIFICATION_EMAIL` を空のまま、上記のとおり申し込み送信を行う。
- 期待: 「申し込み受付は一時的に利用できません。お問い合わせフォームからご連絡ください。」と表示される。

### 403 の確認（Standard/Premium 以外）

- Free / Mini / Small プランの施設ユーザーでログインし、URL を直接 `/admin/csv-bulk-request` にしてアクセスし、送信を試す。
- 期待: 403 エラーまたは「CSV一括登録代行の申し込みはStandardプランまたはPremiumプランのみ利用可能です」のメッセージが返る。

## 5. 状態確認

```bash
# コンテナ一覧
docker compose ps

# バックエンドログ（確認用）
docker compose logs -f backend
```

## 6. 停止（共通）

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
