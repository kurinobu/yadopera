# Dokploy Auto Deploy 不発 — ConoHa SG 修正・復旧証跡

**日付**: 2026-05-31  
**対象 VPS**: `160.251.199.237`（ConoHa VPS 12GB / Dokploy v0.29.4）  
**影響**: 同一 Dokploy（`air-edison` / `production`）上の **全 GitHub 連携 Application**  
**関連報告**: [20260531_会話詳細404とDokploy_AutoDeploy_SG復旧_作業報告.md](../reports/202605/20260531_会話詳細404とDokploy_AutoDeploy_SG復旧_作業報告.md)

---

## 1. 症状

| 項目 | 観測 |
|------|------|
| git push 後 | Dokploy **Deployments** に新行が出ない |
| Dokploy General | **Autodeploy = ON** |
| 最終 Deploy（本番例） | commit `2d8c43a`（2026-05-23）のまま 7 日以上停滞 |
| `GET /api/v1/health` | **200**（旧コンテナ稼働のため healthy のまま） |
| 会話詳細（本番） | `GET /api/v1/chat/history?...` → **404**（コード未反映） |

---

## 2. GitHub App Webhook 配信（確定）

**App**: `Dokploy-air-edison`  
**Webhook URL**（General タブ）:

```text
http://160.251.199.237:3000/api/deploy/github
```

**Recent Deliveries**（Advanced）: push イベントは **すべて赤三角（失敗）**。

代表 Delivery `2ad793f6-5c97-11f1-9914-e7ee76280d29`（2026-05-31 11:19:38）:

| 項目 | 値 |
|------|-----|
| Payload `ref` | `refs/heads/main` |
| Payload `after` | `f82ea19909604f0e2b728acc08411af0b8d8d78c` |
| Payload `installation.id` | `134291494` |
| 詳細画面 | **Response タブなし** |
| エラー | **`We couldn't deliver this payload: failed to connect to host`** |

※ 接続未到達のため Response 本文は記録されない（GitHub 仕様どおり）。

**Redeliver 後**（SG 修正・2026-05-31 11:58:35）: **緑チェック** + `redelivery` バッジ。

---

## 3. 原因（ConoHa セキュリティグループ）

**グループ名**: `air-edison-admin-3000`  
**修正前**（ConoHa 画面・2026-05-31 確認）:

| 通信方向 | プロトコル | ポート | IP/CIDR |
|----------|------------|--------|---------|
| In | TCP | 3000 | **`113.153.22.54/32` のみ** |

→ 自宅 IP からの Dokploy 管理画面（`:3000`）は開けるが、**GitHub Webhook 送信元 IP から port 3000 へ到達不可**。

**GitHub Webhook 送信元 CIDR**（`GET https://api.github.com/meta` の `hooks`・2026-05-31 取得）:

```text
192.30.252.0/22
185.199.108.0/22
140.82.112.0/20
143.55.64.0/20
```

参照: [GitHub Docs — Troubleshooting webhooks — Failed to connect to host](https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/troubleshooting-webhooks#failed-to-connect-to-host)

---

## 4. 実施した修正

### 4-A. ConoHa SG（`air-edison-admin-3000`）

既存ルール **`113.153.22.54/32` は削除せず維持**。以下 4 ルールを **追加**:

| # | In | IPv4 | TCP | 3000 | CIDR |
|---|-----|------|-----|------|------|
| 1 | In | IPv4 | TCP | 3000 | `192.30.252.0/22` |
| 2 | In | IPv4 | TCP | 3000 | `185.199.108.0/22` |
| 3 | In | IPv4 | TCP | 3000 | `140.82.112.0/20` |
| 4 | In | IPv4 | TCP | 3000 | `143.55.64.0/20` |

### 4-B. GitHub Redeliver

Advanced → 失敗 Delivery → **Redeliver** → 緑チェック確認。

### 4-C. コード反映（YadOPERA — 別件）

| 操作 | commit |
|------|--------|
| `develop` push | `5f46809` — admin 会話詳細 API |
| `main` merge + push | `f82ea19` |
| 本番 Auto Deploy（Redeliver 経由） | Backend / Frontend **`f82ea19` Done** |
| ステージング手動 Deploy | Backend / Frontend **`5f46809` Done** |

---

## 5. 復旧確認

| 確認 | 結果 | 日時 |
|------|------|------|
| GitHub Redeliver | 緑チェック | 2026-05-31 11:58:35 |
| 本番 Backend Deploy | `f82ea19` Done | 2026-05-31 |
| 本番 Frontend Deploy | `f82ea19` Done | 2026-05-31 |
| staging Backend Deploy | `5f46809` Done | 2026-05-31 |
| staging Frontend Deploy | `5f46809` Done | 2026-05-31 |
| `GET .../admin/conversations/test` 本番 | **403**（404 から変化） | 2026-05-31 |
| `GET .../admin/conversations/test` staging | **403** | 2026-05-31 |
| `https://app.yadopera.com/admin/login` | ログイン画面表示 OK | 2026-05-31 |
| 会話詳細（stg100・本番） | OK | 2026-05-31 |

---

## 6. 他 Application への影響

同一 Dokploy・同一 GitHub App Webhook のため、**InfluBerry / motivation_app 等も SG 修正前は Auto Deploy 不発の可能性がある**。

再デプロイ要否:

- Deployments の commit = 各 App の Branch 先端 → **不要**
- push 済みだが Deployments が古い → **Deploy または push で再トリガ**

---

## 7. 再発防止

- [Phase2 Step 0.2](../maintenance/20260521_Phase2_ConoHa初期設定_実施手順.md#02-ポート-3000-用の独自セキュリティグループを作る) に **GitHub hooks CIDR 追加**を追記済み
- `hooks` CIDR は GitHub が変更する場合がある → 月次または Auto Deploy 不発時に `GET /api.github.com/meta` で再確認
