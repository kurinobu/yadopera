# Phase 7 — InfluBerry / motivation_app staging 本ドメイン化・HTTPS 化 完了証跡（2026-05-29）

**記録日**: 2026-05-29 09:18 JST  
**判定**: **Phase 7 staging 切替完了**（本番 URL 切替は Phase 7 スコープ外）  
**2026-05-29 追記**: 本番 `influberry.jp` / `olovolo.online` は **サービス再開 三本柱 ②③** で同日完了 — [InfluBerry 証跡](./20260529_influberry_prod_service_resumption_complete.md) / [motivation 証跡](./20260529_motivation_prod_service_resumption_complete.md)  
**親文書**: [20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md](../maintenance/20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md)  
**関連証跡**:
- [20260528_phase7_safety_recovery_prechange_backup.md](./20260528_phase7_safety_recovery_prechange_backup.md)
- [20260528_phase7_safety_recovery_checks.md](./20260528_phase7_safety_recovery_checks.md)
- [20260526_phase6_motivation_app_complete.md](./20260526_phase6_motivation_app_complete.md)

---

## 1. 結論サマリ

| 区分 | 状態 | 備考 |
|------|------|------|
| **staging** InfluBerry | ✅ | `https://staging.influberry.jp/` HTTPS 200 + 正規 title |
| **staging** motivation_app | ✅ | `https://staging.olovolo.online/` HTTPS 200 + 正規 title |
| **本番** `influberry.jp` | ⏳ 未切替 | ルート A は `216.24.57.1`（旧 Render 向き先のまま） |
| **本番** `olovolo.online` | ⏳ 未切替 | ルート A は `216.24.57.1`（旧 Render 向き先のまま） |
| YadOPERA 本番 / staging | ✅ 無影響 | 全工程で health / 200 維持 |

→ **Phase 7 のスコープ（staging アプリの Domains + DNS + HTTPS）は完了**。本番ドメイン切替は今後の別作業。

---

## 2. 確定 URL 責務（7-0）

| URL | 用途 | Dokploy Application | 状態 |
|-----|------|---------------------|------|
| `api.yadopera.com` | YadOPERA prod | `yadopera-backend-production` | 変更なし |
| `app.yadopera.com` | YadOPERA prod | `yadopera-frontend-production` | 変更なし |
| `staging-api.yadopera.com` | YadOPERA stg | `yadopera-backend-staging` | 変更なし |
| `staging-app.yadopera.com` | YadOPERA stg | `yadopera-frontend-staging` | 変更なし |
| `staging.influberry.jp` | InfluBerry stg | `influberry-staging` | **Phase 7 で切替完了** |
| `staging.olovolo.online` | motivation stg | `motivation-app-staging` | **Phase 7 で切替完了** |
| `influberry.jp` | InfluBerry prod（将来） | （未作成） | **未切替** |
| `olovolo.online` | motivation prod（将来） | （未作成） | **未切替** |

---

## 3. DNS（dig 実測）

```text
staging.influberry.jp  → 160.251.199.237
staging.olovolo.online → 160.251.199.237
```

**本番ルート（切替していない・事実）**:
- `influberry.jp` A = `216.24.57.1`（ムームー画面・Owner スクショ）
- `olovolo.online` A = `216.24.57.1`（ムームー画面・Owner スクショ）

---

## 4. Phase 7 完了疎通（7-G・Mac・2026-05-29 09:18 JST）

```bash
curl -sS "https://api.yadopera.com/api/v1/health"
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "yadopera_staging_app=%{http_code}\n" "https://staging-app.yadopera.com/"
curl -sS -o /dev/null -w "influberry_https=%{http_code}\n" "https://staging.influberry.jp/"
curl -sS "https://staging.influberry.jp/" | grep -o '<title>[^<]*</title>' | head -1
curl -sS -o /dev/null -w "motivation_https=%{http_code}\n" "https://staging.olovolo.online/"
curl -sS "https://staging.olovolo.online/" | grep -o '<title>[^<]*</title>' | head -1
```

```text
{"status":"healthy","database":"connected","redis":"connected"}
yadopera_app=200
yadopera_staging_app=200
influberry_https=200
<title>InfluBerry - インフルエンサー案件管理・請求書自動生成SaaS</title>
motivation_https=200
<title>キャラまるわかり - 3つの心理学理論で自己診断</title>
```

---

## 5. C-2 / C-3（Owner 判断・据え置き）

| ID | 判断 | 備考 |
|----|------|------|
| C-2 Brevo キー | 据え置き | Owner「後でする」・`motivation_app` は Private |
| C-3 管理者パスワード | A 据え置き | Dokploy `ADMIN_PASSWORD_HASH` 未設定のまま |

---

## 6. 触っていないこと

- YadOPERA api/app の Dokploy env / Domains
- Stripe Webhook / Brevo Authorized IPs
- `influberry.jp` / `olovolo.online` **本番** DNS（ルート A 未変更）
- 本番用 Dokploy Application（未作成）
- motivation-app-staging / influberry-staging の Environment Settings（Domains のみ変更）

---

## 7. 7-D 障害メモ（解消済）

- 初回 Save 後も Host が `staging-influberry.local` のまま → Validate で `queryA ENOTFOUND staging-influberry.local`
- Host を `staging.influberry.jp` に Edit 後、HTTPS 200 + letsencrypt 正常化

---

## 8. 次 Phase 申し送り（2026-05-29 更新）

| 項目 | 状態 |
|------|------|
| **サービス再開 三本柱** | ✅ [正本](../maintenance/20260529_サービス再開_三本柱_実施計画.md) ①②③ 完了 |
| 本番 `influberry.jp` | ✅ [② 証跡](./20260529_influberry_prod_service_resumption_complete.md) |
| 本番 `olovolo.online` | ✅ [③ 証跡](./20260529_motivation_prod_service_resumption_complete.md) |
