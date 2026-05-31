# 会話詳細 404 と Dokploy Auto Deploy 不発 — 調査・復旧 作業報告

**日付**: 2026-05-31  
**環境**: ConoHa VPS `160.251.199.237` / Dokploy `air-edison` / production  
**証跡**: [20260531_dokploy_autodeploy_security_group_remediation.md](../../evidence/20260531_dokploy_autodeploy_security_group_remediation.md)

---

## 1. 報告された事象（2 件）

### 1-A. 管理画面 — 会話詳細 404

| 項目 | 内容 |
|------|------|
| URL | 本番 `app.yadopera.com` — 未解決エスカレーション → 会話詳細 |
| API | `GET /api/v1/chat/history/{session_id}?facility_id=1` → **404** |
| 前提 | エスカレーションは施設 2・ログインアカウントは施設 1（stg102） |

**DB 確認**: エスカレーション id=1 は `escalation.facility_id=2`・`conversation.facility_id=2` で整合。**データ不整合ではない**。

**原因（アプリ）**: 管理画面 `ConversationDetail.vue` がゲスト向け `chat/history`（JWT 施設でフィルタ）を使用。別施設アカウントでメール URL を開くと 404。

### 1-B. git push 後も本番が更新されない

| 項目 | 内容 |
|------|------|
| 操作 | `develop` → `main` merge + push（`f82ea19`） |
| Dokploy | Autodeploy ON だが Deployments は **7 日前**（`2d8c43a`）のまま |
| health | **200**（旧 Backend コンテナ継続） |

---

## 2. コード修正（1-A）

**commit**: `5f46809`（develop）→ `f82ea19`（main merge）

| 変更 | 内容 |
|------|------|
| Backend | `GET /api/v1/admin/conversations/{session_id}` 追加（JWT 施設で認可） |
| Frontend | `ConversationDetail.vue` が admin API を使用 |
| その他 | 未解決一覧を `Conversation.facility_id` 基準に統一 |

**テスト**: `test_admin_get_conversation_success` / `test_admin_get_conversation_forbidden_other_facility` — 2 passed（Docker PG）。

---

## 3. Auto Deploy 不発の調査（1-B）

### 3.1 除外した仮説

| 仮説 | 判定 |
|------|------|
| Autodeploy OFF | ❌ ON（Dokploy General スクショ） |
| push 漏れ | ❌ `origin/main` に `f82ea19` 存在 |
| Branch 不一致（Payload） | ❌ `ref: refs/heads/main` |
| Webhook URL 誤り | ❌ `http://160.251.199.237:3000/api/deploy/github`（General 確認） |

### 3.2 確定原因

GitHub App `Dokploy-air-edison` → Advanced → Recent Deliveries:

**`We couldn't deliver this payload: failed to connect to host`**

ConoHa SG **`air-edison-admin-3000`**: port **3000** / In / TCP / **`113.153.22.54/32` のみ**（Phase 2 当時の自宅 IP 限定）。

GitHub Webhook は `https://api.github.com/meta` の `hooks` CIDR から送信されるため、**port 3000 へ接続できなかった**。

### 3.3 修正

`air-edison-admin-3000` に GitHub `hooks` IPv4 CIDR **4 件**を追加（自宅 IP ルールは維持）。  
詳細は [証跡 §4](../../evidence/20260531_dokploy_autodeploy_security_group_remediation.md#4-実施した修正)。

GitHub **Redeliver** → 緑チェック（2026-05-31 11:58:35）。

---

## 4. デプロイ結果

| App | 手段 | commit | 状態 |
|-----|------|--------|------|
| yadopera-backend-production | Redeliver → Auto Deploy | `f82ea19` | Done |
| yadopera-frontend-production | 同上 | `f82ea19` | Done |
| yadopera-backend-staging | 手動 Deploy（main Redeliver は develop 非対象） | `5f46809` | Done |
| yadopera-frontend-staging | 手動 Deploy | `5f46809` | Done |

**本番確認**:

- `https://app.yadopera.com/admin/login` — 表示 OK
- 会話詳細（stg100）— OK
- `GET /api/v1/admin/conversations/...` — **403**（未認証 curl）/ ブラウザ **200**

---

## 5. 他 Application（InfluBerry / motivation_app）

SG 修正は **VPS 共通**。Auto Deploy 不発期間中に push があった App は、Deployments と Git 先端 commit を突合し、ずれていれば Deploy すること。

---

## 6. 関連文書更新

| 文書 | 更新内容 |
|------|----------|
| [Phase2 Step 0.2](../../maintenance/20260521_Phase2_ConoHa初期設定_実施手順.md) | GitHub hooks CIDR 必須追記 |
| [ConoHa 引き継ぎ §運用インシデント](../../maintenance/20260521_ConoHaVPS_移転統合_引き継ぎ.md#運用インシデント-dokploy-auto-deploy-不発2026-05-31) | 本件サマリ |
| [maintenance README](../../maintenance/README.md) | 証跡・報告リンク |
