# ③ キャラまるわかり — 本番載せ替え + サービス再開 完了証跡

**実施日**: 2026-05-29  
**正本**: [キャラまるわかり 本番載せ替え + サービス再開 計画](../maintenance/20260529_キャラまるわかり_本番載せ替え_サービス再開_計画.md)  
**親**: [サービス再開 三本柱](../maintenance/20260529_サービス再開_三本柱_実施計画.md)  
**関連**: [Phase 6 motivation 証跡](./20260526_phase6_motivation_app_complete.md) / [事前調査](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md)

---

## 1. 完了サマリ

| 項目 | 結果 |
|------|------|
| 本番 URL | `https://olovolo.online/` HTTPS **200** + キャラまるわかり title |
| staging | `https://staging.olovolo.online/` **200** 維持 |
| Dokploy 本番 | `motivation-app-production` / Branch **`main`** / Deploy commit **`604aefa`** Done |
| DNS | `olovolo.online` A → **`160.251.199.237`**（ムームー・`dig @8.8.8.8` 実測） |
| 三本柱 | **① YadOPERA ✅ ② InfluBerry ✅ ③ キャラまるわかり ✅** |

---

## 2. 本番構成（確定値）

| 項目 | 値 |
|------|-----|
| Application | `motivation-app-production` |
| Swarm | `airedison-motivationappproduction-bloxme` |
| GitHub | `kurinobu/motivation_app` / Branch **`main`** |
| Deploy commit | **`604aefa`**（Dockerfile 追加・Phase 6 実績） |
| Domain | `olovolo.online` / Port **`5004`** / letsencrypt |
| DB | **`olovolo`**（`motivation_app` staging から pg_dump コピー・MO-2a・9 テーブル） |
| VPS IP | `160.251.199.237` |
| `BASE_URL` | `https://olovolo.online` |
| `ADMIN_PASSWORD_HASH` | 意図的未設定（C-3 fallback・Render 同型） |

---

## 3. タスク完了

| ID | 結果 |
|----|------|
| MO-0 | ✅ 凍結・ベースライン curl |
| MO-1 | ✅（推奨値で確定） |
| MO-2 | ✅（2a DB / 2b App / 2c env 17 行 / 2d Deploy / 2e 疎通） |
| MO-3 | ✅ ムームー A → ConoHa |
| MO-4 | ✅ Domains + letsencrypt |
| MO-5 | ✅ `BASE_URL` 等（MO-2c 投入済・確認のみ） |
| MO-6 | ⏭ スキップ（C-2/C-3・非ブロッカー） |
| MO-7 | ✅ 下記実測 |
| MO-8 | ✅ 本書 |

---

## 4. MO-7 疎通（Mac 実測・2026-05-29）

### 実行コマンド

```bash
curl -sS "https://api.yadopera.com/api/v1/health"; echo
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "influberry_prod=%{http_code}\n" "https://influberry.jp/"
curl -sS -o /dev/null -w "influberry_tiktok=%{http_code}\n" "https://influberry.jp/api/auth/tiktok/login"
curl -sS -o /dev/null -w "influberry_stg=%{http_code}\n" "https://staging.influberry.jp/"
curl -sS -o /dev/null -w "motivation_stg=%{http_code}\n" "https://staging.olovolo.online/"
curl -sSk -o /dev/null -w "olovolo_root=%{http_code}\n" --resolve olovolo.online:443:160.251.199.237 "https://olovolo.online/"
curl -sSk --resolve olovolo.online:443:160.251.199.237 "https://olovolo.online/" | grep -o '<title>[^<]*</title>' | head -1
dig @8.8.8.8 +short olovolo.online A
```

### 出力（そのまま）

```text
{"status":"healthy","database":"connected","redis":"connected"}
yadopera_app=200
influberry_prod=200
influberry_tiktok=302
influberry_stg=200
motivation_stg=200
olovolo_root=200
<title>キャラまるわかり - 3つの心理学理論で自己診断</title>
160.251.199.237
```

### 判定

| 観点 | 結果 |
|------|------|
| YadOPERA 本番 | health `healthy`・app **200** ✅ |
| InfluBerry 本番・staging | **200** / TikTok **302** ✅ |
| motivation staging | **200** ✅ |
| **motivation 本番** | **200** + 正規 title ✅ |
| DNS（Google） | **160.251.199.237** ✅ |

※ MO-7 時点で Mac ローカル `dig olovolo.online` は TTL キャッシュにより **`216.24.57.1`** のままの場合あり。権威 DNS・`@8.8.8.8` は **`160.251.199.237`**。本番 HTTPS は VPS 上で letsencrypt 発行済み。

---

## 5. MO-2a DB 実測（VPS・2026-05-29）

| 項目 | 値 |
|------|-----|
| Postgres コンテナ | `airedison-airedisonpostgres-wsxrdk.1.u4sww14dlpycjo7m804ztty3e` |
| `CREATE DATABASE olovolo` | 成功 |
| `\dt` | **9 テーブル**（Phase 6 `motivation_app` と同型） |

---

## 8. セッション教訓（2026-05-29 実施時）

| # | 事象 | 原因 | 対処（手順書に反映済） |
|---|------|------|------------------------|
| 1 | `This node is not a swarm manager` | SSH 切断後、DB ブロックが **Mac 側**で実行された | MO-2a は VPS ログイン**後**に DB ブロックのみ貼る |
| 2 | `ModuleNotFoundError: dotenv` | MO-2c スクリプトを **VPS** で実行 | **Mac ターミナル**のみ。`pip3 install python-dotenv` |
| 3 | `[プロセスが完了しました]` | ナビに `exit` 含むブロックを貼り、ターミナルが終了 | **`exit` をナビに含めない** |
| 4 | Dokploy が変わらない | ターミナル出力を Dokploy に貼付・Save していない | スクリプト出力 → Environment **貼付 → Save** を明示 |
| 5 | `curl https://olovolo.online/` SSL 失敗 | Mac ローカル DNS が旧 IP `216.24.57.1` | `dig @8.8.8.8` / `--resolve` で確認 |

---

## 9. 既知の残課題（非ブロッカー）

| 項目 | 事実 |
|------|------|
| `www.olovolo.online` | CNAME → `motivation-app.onrender.com`（旧 Render・任意後追い） |
| Mac ローカル DNS | TTL 満了まで `216.24.57.1` キャッシュの可能性 |
| MO-6 C-2 / C-3 | Brevo キーローテーション・管理者 PW（[事前調査](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md) 申し送り） |
| 本番 DB | staging コピー（旧 Render 本番 DB は Phase 8 削除済） |

---

## 10. 三本柱完了

→ [サービス再開 三本柱](../maintenance/20260529_サービス再開_三本柱_実施計画.md) **①②③ すべて ✅**
