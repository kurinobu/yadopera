# A5 ローカルテスト手順（新規登録時 自動登録FAQ 30件化）

**目的**: Phase A Step A5 をローカルで実施するための環境準備・実行手順と、新規登録画面URL。

---

## 1. 前提

- Docker Desktop が起動していること
- `backend/.env` が存在し、少なくとも `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY` が設定されていること（新規登録でメール送信を行う場合は `OPENAI_API_KEY` も必要）

---

## 2. 環境準備（Docker ビルド・起動）

**プロジェクトルート（`yadopera`）で、ローカル端末から**実行する。Docker のビルドはホスト環境での実行が必要です。

```bash
cd /Users/kurinobu/projects/yadopera
docker-compose up -d --build
```

- 初回またはコード変更後は `--build` でイメージを再ビルドする。
- 起動確認:
  - Backend: http://localhost:8000 （Swagger: http://localhost:8000/docs ）
  - Frontend: http://localhost:5173
  - DB・Redis はコンテナ内で利用され、ポートは docker-compose の通り（postgres 5433, redis 6379）。

---

## 3. 単体テスト（FAQ プリセット・30件）

Backend コンテナ内で pytest を実行する。

```bash
cd /Users/kurinobu/projects/yadopera
docker-compose run --rm backend pytest tests/test_faq_presets.py -v
```

- 18 件すべて PASS であれば、30件化・プラン別フィルタ・初期登録件数の変更は問題なし。

---

## 4. 新規登録画面の URL

**新規登録画面**（施設の初回登録）は次の URL で開く。

- **http://localhost:5173/admin/register**

- ルート: `frontend/src/router/admin.ts` の `path: '/admin/register'`、コンポーネント: `Register.vue`。
- 登録完了後、当該施設には **30件の初期FAQ** が自動投入される（`auth_service.register_facility_async_faqs`）。

---

## 5. 新規登録〜30件投入の確認（任意）

1. 上記 URL で新規登録を完了する（メール認証が必要な場合は認証まで実施）。
2. ログイン後、管理画面の「FAQ管理」で、該当施設の FAQ が **30件** 登録されていることを確認する。
3. または API で確認: 施設トークンで `GET /api/v1/admin/faqs` を叩き、件数が 30 であることを確認する。

---

## 6. 参照

- Phase A ステップ一覧: `docs/新規登録時_自動登録FAQ_埋め込み事前計算_実装計画.md` §9
- 全体の開発手順: リポジトリルート `README.md` の「開発環境セットアップ」「サービス起動」
