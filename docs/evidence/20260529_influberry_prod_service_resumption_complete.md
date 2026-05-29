# ② InfluBerry — 本番載せ替え + サービス再開 完了証跡

**実施日**: 2026-05-29  
**正本**: [InfluBerry 本番載せ替え + サービス再開 計画](../maintenance/20260529_InfluBerry_本番載せ替え_サービス再開_計画.md)  
**親**: [サービス再開 三本柱](../maintenance/20260529_サービス再開_三本柱_実施計画.md)  
**関連**: [TikTok OAuth branch 差分 調査](../reports/202605/20260529_influberry_tiktok_oauth_branch_gap_調査報告.md)

---

## 1. 完了サマリ

| 項目 | 結果 |
|------|------|
| 本番 URL | `https://influberry.jp/` HTTPS 200 + InfluBerry title |
| TikTok ログイン UI | ✅ 表示（Owner 画面確認） |
| `/api/auth/tiktok/login` | **302**（VPS curl） |
| staging | `https://staging.influberry.jp/` 200 維持 |
| Dokploy 本番 | `influberry-production` / Branch **`main`** / Deploy **`2314abb`** Done |

---

## 2. 本番構成（確定値）

| 項目 | 値 |
|------|-----|
| Application | `influberry-production` |
| GitHub | `kurinobu/influberry` / Branch **`main`** |
| Deploy commit | **`2314abb`**（Dockerfile + `main` 系 TikTok 含む） |
| Domain | `influberry.jp` / Port `5003` / letsencrypt |
| DB | `influberry`（`influberry_staging` からコピー・IB-2a） |
| VPS IP | `160.251.199.237` |

---

## 3. タスク完了

| ID | 結果 |
|----|------|
| IB-0 | ✅ |
| IB-1 | ✅（Branch `main`・DB `influberry`・Port `5003`） |
| IB-2 | ✅ |
| IB-3 | ✅ DNS A → ConoHa |
| IB-4 | ✅ |
| IB-5 | ✅ TikTok UI + API 302 |
| IB-6 | ✅（本番・staging 200・下記） |
| IB-7 | ✅ 本書 |

---

## 4. IB-6 疎通（実測）

| URL | 結果 |
|-----|------|
| `https://influberry.jp/` | 200・InfluBerry title |
| `https://staging.influberry.jp/` | 200 |
| `https://influberry.jp/api/auth/tiktok/login` | 302 |

---

## 5. IB-8 — `main` / `staging` 分支統（2026-05-29）

**実施場所**: Mac `/Users/kurinobu/projects/influberry_v2`（git push のみ・VPS では実行しない）

| Step | 内容 | 結果 |
|------|------|------|
| 8-1 | `main` に `staging` を merge | merge commit `472ce9b`（コンフリクトなし） |
| 8-2 | `staging` に `main` を merge | fast-forward → **同一 HEAD** |
| 8-3 | `git push origin main` / `staging` | ✅ |

| | 統合前 | 統合後 |
|--|--------|--------|
| `main` | `2314abb` | **`472ce9b`** |
| `staging` | `f6f8725` | **`472ce9b`**（`main` と同一） |
| TikTok OAuth | `main` のみ | **両 branch** |
| staging 改善（請求書遅延・絵文字削除等） | `staging` のみ | **両 branch** |

### 運用ルール（固定）

| 環境 | Branch | Dokploy Application |
|------|--------|---------------------|
| 本番 | `main` | `influberry-production` |
| staging | `staging` | `influberry-staging` |

→ branch 名は分けるが、**コミットは揃える**（以降は `main` に入れたら `staging` へ merge または同一 PR で両方更新）。

### IB-8 残作業（Owner・Dokploy）

push 後、各 Application で **Redeploy**（または自動 Deploy 完了待ち）:

1. `influberry-production`（Branch `main`）→ `472ce9b` が **Done**
2. `influberry-staging`（Branch `staging`）→ `472ce9b` が **Done**（**staging に TikTok UI が載る**）

### IB-8 疎通確認（VPS curl・Owner 実測）

| URL | 結果 | 解釈 |
|-----|------|------|
| `https://influberry.jp/api/auth/tiktok/login` | **302** | ✅ `influberry-production` は `472ce9b` 相当で稼働 |
| `https://staging.influberry.jp/api/auth/tiktok/login` | **404** + `{"error":"API endpoint not found"}` | ❌ **`influberry-staging` が旧イメージのまま**（TikTok ルート未デプロイ） |

**404 の意味**: Flask の catch-all（`app/__init__.py`）— **ルートが存在しない旧コード**の典型。git は統合済みだが **staging Application の Redeploy 未完了**。

### IB-8b（Owner・1 Step）

1. Dokploy → **`influberry-staging`** のみ（本番は触らない）
2. Branch **`staging`** のまま **Deploy / Redeploy**
3. Deploy ログで commit **`472ce9b`**・**Done**
4. VPS で再実行:

```bash
curl -sS -o /dev/null -w "stg=%{http_code}\n" "https://staging.influberry.jp/api/auth/tiktok/login"
```

→ **`stg=302`** で IB-8 完了。

（任意）staging で TikTok ログインまで試す場合は env に `TIKTOK_REDIRECT_URI=https://staging.influberry.jp/api/auth/tiktok/callback` 等が必要。ルート確認だけなら Redeploy のみで可。

### IB-8b 再試行後も `stg=404`（2026-05-29・事実）

| 観測 | 本番 | staging |
|------|------|---------|
| `/api/auth/tiktok/login` | 302 | 404 + `API endpoint not found` |
| フロント JS | `index-BdV3acjy.js` | `index-Bjx1Qa8O.js`（**別ビルド＝旧イメージ**） |
| `/api/auth/me` | — | 401（アプリは生きている） |

**結論**: git `staging` @ `472ce9b` は GitHub 上で揃っているが、**Swarm `airedison-influberrystaging-qqn2hl` がまだ `f6f8725` 時代のコンテナ**。

#### IB-8c — Dokploy 確認（Owner・画面）

`influberry-staging`（**production ではない**）→ **Deployments** 最新行:

| 確認 | 期待 |
|------|------|
| Commit / SHA | **`472ce9b`**（短縮表示でも可） |
| Status | **Done**（Error ならログ全文を控える） |
| Branch | **`staging`** |

- 最新が **`f6f8725`** または Deploy 無し → **Deploy** を押す（Build Type Dockerfile・Branch `staging`）
- **Error**（例: Dockerfile 無し）→ ログ貼付で再ナビ
- Done なのに 404 継続 → **Rebuild / Clear cache** 相当があれば実行 → 再度 Deploy

#### IB-8d — VPS 実測（Deploy Done 後）

```bash
docker service ls | grep -i influberry
docker service ps airedison-influberrystaging-qqn2hl --no-trunc 2>/dev/null | head -5
CID=$(docker ps --format '{{.ID}} {{.Names}}' | grep -i influberrystaging | awk '{print $1}' | head -1)
echo "CID=$CID"
docker exec "$CID" grep -c 'tiktok/login' /app/app/blueprints/auth.py 2>/dev/null || \
  docker exec "$CID" sh -c 'grep -r tiktok/login /app 2>/dev/null | head -1'
curl -sS -o /dev/null -w "stg=%{http_code}\n" "https://staging.influberry.jp/api/auth/tiktok/login"
```

| `grep` 結果 | 意味 |
|-------------|------|
| `1` 以上 | 新コード入り → curl **302** になるはず |
| 空 / ファイル無し | 旧コンテナのまま → Dokploy Deploy が反映されていない |

**③ キャラまるわかり**: 本番 InfluBerry は 302 のため **ブロックしない**。staging 404 は IB-8c〜d で並行解消可。

### IB-8 完了（2026-05-29・Deploy #1 `472ce9b` Done 21s 後）

| 確認 | 結果 |
|------|------|
| Dokploy `influberry-staging` | commit `472ce9b`・Build Done |
| `curl …/api/auth/tiktok/login` staging | **302** |
| 本番 | **302**（維持） |
| フロント JS | 両方 `index-BdV3acjy.js`（同一ビルド） |

→ **IB-8 クローズ**。② InfluBerry 完全完了。

**次会話**: ~~[③ 実施手順 MO-0](../maintenance/20260529_キャラまるわかり_本番載せ替え_実施手順.md)~~ → **③ 完了**（[証跡](./20260529_motivation_prod_service_resumption_complete.md)）

---

## 6. 既知の残課題（非ブロッカー）

- `www.influberry.jp` CNAME が Render 向きの可能性（ルート `influberry.jp` は ConoHa）
- 本番 DB が staging コピー（旧 Render 本番データとは限らない）

---

## 7. 次 Step

**③ キャラまるわかり** — ✅ 完了（[証跡](../evidence/20260529_motivation_prod_service_resumption_complete.md)・[三本柱正本](../maintenance/20260529_サービス再開_三本柱_実施計画.md)）
