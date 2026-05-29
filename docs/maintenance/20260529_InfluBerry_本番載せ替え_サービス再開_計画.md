# ② InfluBerry — 本番載せ替え + サービス再開 計画

**作成日**: 2026-05-29  
**順序**: **三本柱 ②**（[正本](./20260529_サービス再開_三本柱_実施計画.md)）  
**状態**: ✅ **完了（2026-05-29）**  
**証跡**: [20260529_influberry_prod_service_resumption_complete.md](../evidence/20260529_influberry_prod_service_resumption_complete.md)  
**プロダクト**: InfluBerry **のみ**

---

## 0. 現状（完了後）

| 項目 | 値 |
|------|-----|
| 本番 | `https://influberry.jp/` ConoHa HTTPS ✅・TikTok ログイン ✅ |
| staging | `https://staging.influberry.jp/` ✅ 維持 |
| Dokploy 本番 | `influberry-production` / Branch **`main`** / `2314abb` |
| DB 本番 | `influberry` |

---

## 1. タスク

| ID | 内容 | 状態 |
|----|------|------|
| IB-0〜4 | 載せ替え・DNS・HTTPS | ✅ |
| IB-5 | TikTok ログイン復旧（`main` + Dockerfile `2314abb`） | ✅ |
| IB-6 | 本番・staging 疎通 | ✅ |
| IB-7 | 証跡 | ✅ |
| **IB-8** | **`main` / `staging` 分支統** | ✅ `472ce9b`・staging/prod TikTok **302** |

**実施手順**: [20260529_InfluBerry_本番載せ替え_実施手順.md](./20260529_InfluBerry_本番載せ替え_実施手順.md)

---

## 2. 完了定義

- [x] `https://influberry.jp/` HTTPS 200 + title
- [x] TikTok ログイン（UI + `/api/auth/tiktok/login` 302）
- [x] 証跡作成

---

## 3. `main` と `staging`（IB-8 完了）

- **HEAD 同一**: `472ce9b`（2026-05-29・Mac merge + push）
- 本番 = Branch `main`、staging 環境 = Branch `staging`（名前は分離、中身は同期）
- Dokploy: 両 App を `472ce9b` で Redeploy 確認 → [証跡 §5](../evidence/20260529_influberry_prod_service_resumption_complete.md)

---

## 4. 次 Step

→ **③ 完了**。次会話: [キャラまるわかり 実施手順 MO-0](./20260529_キャラまるわかり_本番載せ替え_実施手順.md#mo-0--凍結確認ベースライン-curl次会話最初の-1-step)
