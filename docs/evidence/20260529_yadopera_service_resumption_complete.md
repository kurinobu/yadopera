# ① YadOPERA — サービス再開 完了証跡

**実施日**: 2026-05-29  
**正本**: [YadOPERA サービス再開 計画](../maintenance/20260529_YadOPERA_サービス再開_計画.md)  
**親**: [サービス再開 三本柱 実施計画](../maintenance/20260529_サービス再開_三本柱_実施計画.md)  
**区別**: [Phase 5 証跡](./20260524_conoha_phase5_service_resume.md) は **インフラ載せ替え**。本書は **利用者導線（LP→app）を含むサービス再開**。

---

## 1. 完了タスク（Y-1 〜 Y-5）

| ID | 内容 | 結果 | 確認者 |
|----|------|------|--------|
| Y-1 | LP CTA を `app.yadopera.com` へ | ✅ | AI（コード） |
| Y-2 | `landing/` Render URL grep | ✅ 残存なし | AI |
| Y-3 | `main` へ反映・GitHub Pages | ✅ | AI（cherry-pick） |
| Y-4 | `yadopera.com` CTA → 登録画面 | ✅ | Owner（2026-05-29） |
| Y-5 | health / 新規登録 / `/admin/billing` | ✅ | Owner + AI（health） |

---

## 2. Git（LP 反映）

| ブランチ | コミット | 備考 |
|----------|----------|------|
| `develop` | `d8efe32` | `fix(lp): point register/login CTAs to app.yadopera.com` |
| `main` | `068cf49` | 上記 cherry-pick（`develop` 全体マージは未実施・LP のみ） |

**Pages ワークフロー**: `.github/workflows/pages.yml`（`main` push・`landing/**`）

---

## 3. 本番 LP（Y-3 後・curl 実測）

```bash
curl -sL https://yadopera.com/ | grep -E 'admin/(register|login)'
```

→ すべて `https://app.yadopera.com/admin/register` / `admin/login`（`onrender.com` なし）

---

## 4. API・App スモーク

### 自動（2026-05-29）

```bash
curl -sS https://api.yadopera.com/api/v1/health
# {"status":"healthy","database":"connected","redis":"connected"}
```

| URL | HTTP |
|-----|------|
| `https://app.yadopera.com/` | 200 |
| `https://app.yadopera.com/admin/register` | 200 |
| `https://app.yadopera.com/admin/login` | 200 |
| `https://app.yadopera.com/admin/billing` | 200 |

### Owner（Y-5・詳細は Git 外）

- 新規登録（確認メール・ログイン・ダッシュボード）: ✅
- ログイン後 `/admin/billing` 表示: ✅

---

## 5. 変更しなかったもの（凍結遵守）

- InfluBerry / motivation の Dokploy・DNS
- YadOPERA api/app の Dokploy env
- ②③ 本番載せ替え

---

## 6. 次 Step

**② InfluBerry** 着手可 — [InfluBerry 本番載せ替え + サービス再開 計画](../maintenance/20260529_InfluBerry_本番載せ替え_サービス再開_計画.md)（IB-0 から・1 Step ずつ）
