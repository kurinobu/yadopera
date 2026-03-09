# Step 3: Docker での動作確認 — 実行手順とブラウザテスト即実行用準備

**対象**: 実装計画 3a「開発者ダッシュボードにメールアドレス表示を追加」  
**作成日**: 2026年3月9日

---

## 1. Docker 起動（ローカルで実行）

```bash
cd /Users/kurinobu/projects/yadopera
docker-compose up -d
```

初回またはビルド後は 1〜2 分かかることがあります。起動確認:

```bash
docker-compose ps
```

期待: `yadopera-backend`（8000）、`yadopera-frontend`（5173）、`yadopera-postgres`、`yadopera-redis` が **Up** または **running**。

---

## 2. 動作確認コマンド（ローカルで実行）

| 確認項目 | コマンド | 期待 |
|----------|----------|------|
| バックエンドヘルス | `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health` | **200** |
| フロント応答 | `curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/` | **200** |
| API ドキュメント | ブラウザで http://localhost:8000/docs を開く | Swagger UI が表示される |

---

## 3. 開発者パスワードの準備（ブラウザテスト前に必須）

開発者ダッシュボードは **環境変数 `DEVELOPER_PASSWORD`** でログインします。

1. `backend/.env` に以下を設定（未設定の場合）:
   ```bash
   # 例（ローカルテスト用）
   DEVELOPER_PASSWORD=testpass123
   ```
2. 設定確認（Docker 内）:
   ```bash
   docker-compose exec backend python -c "from app.core.config import settings; print('DEVELOPER_PASSWORD:', 'SET' if settings.developer_password else 'NOT SET')"
   ```
   期待: `DEVELOPER_PASSWORD: SET`
3. パスワードを変更した場合はバックエンドの再起動:
   ```bash
   docker-compose restart backend
   ```

詳細: `docs/20260209_Docker環境_開発者パスワード設定手順.md`

---

## 4. ブラウザテスト即実行用 URL 一覧

**まず開く URL（開発者ログイン）**: **http://localhost:5173/developer/login**

| 用途 | URL |
|------|-----|
| **開発者ログイン** | **http://localhost:5173/developer/login** |
| **開発者ダッシュボード（施設一覧・メールアドレス列）** | http://localhost:5173/developer/dashboard |
| フロントトップ | http://localhost:5173 |
| バックエンドヘルス | http://localhost:8000/api/v1/health |
| API ドキュメント（Swagger） | http://localhost:8000/docs |

---

## 5. 3a ブラウザテスト チェックリスト（メールアドレス表示）

- [ ] **1.** 上記 §1〜§3 を実施し、Docker 起動・ヘルス 200・`DEVELOPER_PASSWORD` 設定済みである
- [ ] **2.** ブラウザで **http://localhost:5173/developer/login** を開く
- [ ] **3.** `backend/.env` に設定した開発者パスワードを入力してログイン
- [ ] **4.** 開発者ダッシュボード（施設一覧）が表示される
- [ ] **5.** 施設一覧テーブルに **「メールアドレス」列** が施設名の右隣に表示されている
- [ ] **6.** 各施設の行に、施設のメールアドレス（または未設定時は `-`）が表示されている

### オプション: API で email を確認

開発者トークン取得後、施設一覧 API のレスポンスに `email` が含まれることを確認する場合:

1. http://localhost:8000/docs を開く
2. `POST /api/v1/developer/auth/login` で `{"password": "あなたのDEVELOPER_PASSWORD"}` を実行し `access_token` をコピー
3. **Authorize** で `Bearer <access_token>` を設定
4. `GET /api/v1/developer/stats/facilities` を実行
5. レスポンスの各施設オブジェクトに **`email`** フィールドが含まれていることを確認

---

## 6. トラブルシューティング

| 現象 | 対処 |
|------|------|
| ログインできない | `backend/.env` の `DEVELOPER_PASSWORD` を確認。未設定なら「Developer password is not configured」になる。 |
| 施設一覧が空 | DB に施設データがあるか確認。新規登録で施設を作成するか、シードデータを投入する。 |
| メールアドレス列が表示されない | フロントのビルドキャッシュを消して再起動: `docker-compose up -d --build frontend` |
| ネットワークエラー | フロントは **http://localhost:5173** で開く（VITE_API_BASE_URL が localhost:8000 向け）。 |

---

## 7. Step 3 実行報告の記録

Docker 起動・上記チェックリストおよびオプション確認まで実施したら、以下を記録してください。

- 実施日:
- Docker 起動: 成功 / 失敗
- バックエンド 200: 是 / 否
- フロント 200: 是 / 否
- 開発者ログイン: 成功 / 失敗
- 施設一覧にメールアドレス列表示: 是 / 否
- API `GET /api/v1/developer/stats/facilities` に `email` 含む: 是 / 否 / 未実施

---

**参照**: `docs/開発者ダッシュボード_メールアドレス表示追加_実装計画_3a.md` Step 3
