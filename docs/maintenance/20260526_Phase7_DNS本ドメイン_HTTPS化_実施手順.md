# Phase 7: DNS 本ドメイン化・HTTPS 化（InfluBerry / キャラまるわかり） — 実施手順

**作成日**: 2026-05-26  
**親文書**: [ConoHa VPS 移転統合 引き継ぎ](./20260521_ConoHaVPS_移転統合_引き継ぎ.md)  
**前提**: [Phase 6 完了](../evidence/20260526_phase6_motivation_app_complete.md)（2026-05-26）／[YadOPERA Phase 5 完了](../evidence/20260524_yadopera_conoha_migration_complete.md)（2026-05-24・**サービス稼働中**）

**Phase 8**（Render 解約）は **本 Phase 7 完了後**。本書は **InfluBerry / motivation_app の本ドメイン化・HTTPS 化** のみ。YadOPERA は触らない。

---

## 次会話引き継ぎ（Phase 7 即開始・2026-05-26）

### Phase 6 完了宣言（Phase 7 前提・事実）

| 項目 | 状態 |
|------|------|
| YadOPERA 本番・ステージング | ✅ ConoHa 稼働継続（Phase 5 完了・Phase 6 全期間 200 維持） |
| InfluBerry staging | ✅ Dokploy 稼働・`staging-influberry.local` 暫定ホストで 200 取得（commit `f6f8725`・2026-05-25） |
| キャラまるわかり (motivation_app) staging | ✅ Dokploy 稼働・`staging-motivation.local` 暫定ホストで 200 + 正規 title 取得（commit `604aefa`・Deploy 41s・2026-05-26） |
| Phase 6 完了証跡 | [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md) ／ [20260525_phase6_influberry_partial.md](../evidence/20260525_phase6_influberry_partial.md) |
| 事前調査・訂正履歴 | [20260525_motivation_app_事前調査_調査分析報告書.md](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md)（訂正版・C-1/C-2/C-3） |
| Phase 7 で触らない（凍結） | YadOPERA api/app の Dokploy env／Stripe Webhook／既存 Brevo Authorized IPs／motivation-app-staging の Environment Settings（DNS / Domain のみ変更） |

### 次会話に貼るプロンプト（推奨・このままコピー・2026-05-26 19:25 版）

```
Phase 7（DNS 本ドメイン化・HTTPS 化）を引き継ぎ再開します。
正本: docs/maintenance/20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md
親:   docs/maintenance/20260521_ConoHaVPS_移転統合_引き継ぎ.md §Phase 7
前提: docs/evidence/20260526_phase6_motivation_app_complete.md（Phase 6 完了）

正本「次会話引き継ぎ」§現在地点（Phase 7 着手前）から 1 Step ずつナビしてください。
最初に 7-A の Owner 確認（GitHub Visibility / ムームー DNS 現状 / Brevo 認可 IP /
C-1・C-2・C-3 ローテーション要否）を Owner と読み合わせてください。
憶測禁止。コピペ用ブロックは 1 つのコード欄にまとめる。Mac≠VPS。git は Mac のみ。
YadOPERA api/app・Stripe・既存 Brevo・既存 Dokploy env は触らない。
Phase 6 は完了済み（暫定 hostname 'staging-influberry.local' / 'staging-motivation.local'
で疎通確認済）。
```

### 現在地点（2026-05-26 19:25 時点・事実のみ）

| Step | 状態 | 根拠 |
|------|------|------|
| 7-A 着手前 Owner 確認 | 未 | 7-P1〜7-P6 を Owner と読み合わせ |
| 7-B DNS 現状の事実確認（ムームー画面） | 未 | Owner 提供情報を待つ |
| 7-C ローテーション判断（C-2 Brevo キー） | 未 | GitHub Visibility 確認後 |
| 7-D Dokploy Domains 切替（InfluBerry） | 未 | DNS 反映後 |
| 7-E Dokploy Domains 切替（motivation_app） | 未 | DNS 反映後 |
| 7-F TLS letsencrypt 有効化 | 未 | Domains 切替後 |
| 7-G 疎通確認 | 未 | TLS 有効化後 |
| 7-H 証跡作成・親引き継ぎ更新 | 未 | 全工程完了後 |

### 次会話の最初の作業

**7-A 着手前 Owner 確認**（**変更なし・全て読み取り or Owner 画面確認**）:

1. GitHub `kurinobu/motivation_app` Visibility（Public / Private）→ 7-P3 判断材料
2. GitHub `kurinobu/influberry` Visibility（Public / Private）→ 同上
3. ムームードメイン現状（`influberry.jp` / `staging.influberry.jp` / motivation_app 本ドメインの現向き先）
4. Brevo Authorized IPs（YadOPERA Phase 5 で `160.251.199.237` 追加済・流用可能性確認）
5. C-1 / C-2 / **C-3** のローテーション要否を Owner 判断（[Phase 7 申し送り](#9-phase-7-着手前-owner-必須確認7-p1-7-p6) 参照）

**やらないこと**:
- YadOPERA の Domains 編集・`yadopera-backend-*` の env 変更・本番 Stripe / Brevo / DNS 操作
- influberry-staging / motivation-app-staging の Environment Settings 変更（DNS / Domain のみ変更）
- C-1 / C-2 / C-3 のコード修正（Owner 判断で別 PR・別 Phase）
- Render 解約（Phase 8）

---

## 1. Phase 7 の目的とスコープ

### 1.1 目的

- InfluBerry / motivation_app を **暫定 hostname（`*.local`）→ 本ドメイン**に切替
- **HTTPS 化**（letsencrypt 経由）
- **YadOPERA は触らない**・**Phase 6 で確立した動作を本ドメインで再確認**

### 1.2 スコープに **含むこと**

- ムームードメインの DNS A レコード設定（Owner が画面操作）
- Dokploy `influberry-staging` / `motivation-app-staging` の Domain Host を本ドメインに切替
- Dokploy 側の letsencrypt 有効化（Certificate provider をデフォルトに）
- Mac から本ドメインでの疎通確認（HTTPS）

### 1.3 スコープに **含まないこと**

- C-1（`app.py:50-52` 旧 Render DB ハードコード）・C-2（`services.py` Brevo キー ハードコード）・**C-3（`app.py:138` 管理者パスワード `'kurikuri'` コード固定）** のコード修正 → Phase 7+ Owner 判断で別 PR
- Brevo API キー ローテーション → Owner 判断（GitHub Visibility 次第で 7-C で要否判定）
- 管理者パスワード `'kurikuri'` 変更 → Owner 判断・別 PR
- Render 解約 → Phase 8
- YadOPERA api/app の Dokploy 設定変更・Stripe Webhook 変更

### 1.4 大原則照合（着手前）

| 大原則 | Phase 7 での扱い |
|--------|-----------------|
| 1 根本解決 > 暫定 | 暫定 hostname `*.local` → 本ドメイン化 = 根本解決 ✅ |
| 2 シンプル構造 > 複雑 | Dokploy 画面操作のみ・新規コンテナ追加なし ✅ |
| 3 統一・同一化 | YadOPERA と同じ運用パターン（Dokploy Domains + letsencrypt） ✅ |
| 4 具体的 > 一般 | 本書および 7-A 確認結果で具体的に明記 ✅ |
| 5 安全確実 > 拙速 | YadOPERA 無影響を各 Step で確認・凍結対象を明示 ✅ |
| 6 Docker 環境必須 | Phase 6 で既に Docker 化済・Phase 7 は変更なし ✅ |
| 7 LP は `main` + GitHub Pages | 該当なし — |
| 8 品質ゲートと証跡 | 各 Step で実測コマンド・本書末尾で完了証跡 ✅ |

---

## 2. 確定値（コピペ用・秘密なし）

| 項目 | 値 |
|------|-----|
| VPS IP | `160.251.199.237` |
| SSH | `ssh root@160.251.199.237` |
| Dokploy | `http://160.251.199.237:3000` |
| Project / Environment | `air-edison` / `production` |
| InfluBerry Application 名 | `influberry-staging`（Swarm `airedison-influberrystaging-qqn2hl`） |
| motivation_app Application 名 | `motivation-app-staging`（Swarm `airedison-motivationappstaging-rex1my`） |
| InfluBerry 現 Domain（Phase 6 暫定） | `staging-influberry.local` / Port 5001 / HTTP / Cert none |
| motivation_app 現 Domain（Phase 6 暫定） | `staging-motivation.local` / Port 5002 / HTTP / Cert none |
| Brevo Authorized IPs | **`160.251.199.237`** 追加済み（Phase 5・2026-05-24） |
| YadOPERA 本番 | `https://api.yadopera.com` / `https://app.yadopera.com`（**Phase 7 では変更しない**） |

### 本ドメイン（候補・Owner 確認待ち）

| 環境 | URL（候補） | 状態 |
|------|-------------|------|
| InfluBerry staging | `staging.influberry.jp` | DNS 現状を Owner 画面確認待ち（7-A） |
| InfluBerry 本番 | `influberry.jp`（Phase 7 では切替しない可能性） | DNS 現状を Owner 画面確認待ち（7-A） |
| motivation_app staging | **未確定** | ドメイン所有有無を Owner 画面確認待ち（7-A） |

→ **DNS の最終確定値は 7-B で Owner 画面確認後に本書に追記する**（憶測で書かない）。

---

## 3. 実施順序（概要）

```
7-A  着手前 Owner 確認（7-P1〜7-P6）
7-B  DNS 現状の事実記録（ムームー画面）
7-C  C-2 / C-3 ローテーション判断（GitHub Visibility 次第）
7-D  Dokploy Domains 切替（InfluBerry）→ TLS 待機
7-E  Dokploy Domains 切替（motivation_app）→ TLS 待機
7-F  TLS letsencrypt 有効化（Dokploy 側設定）
7-G  本ドメインで疎通確認（HTTPS）
7-H  証跡・親引き継ぎ更新 → Phase 8 へ
```

**目安時間**: 1〜3 時間（DNS 反映待ちを含めると半日〜1 日。**作業時間自体は短い**）

---

## 4. Step 7-A: 着手前 Owner 確認（読み取り・画面確認のみ）

### 4.1 7-P1: GitHub `kurinobu/motivation_app` Visibility

Owner が Web UI で確認:

- URL: `https://github.com/kurinobu/motivation_app`
- 画面右上の Public / Private 表示
- 判定:
  - **Public** → **C-2 Brevo キー 即時ローテーション必須**（漏洩確定）／**C-3 管理者パスワード 'kurikuri' 即時変更必須**（コード経由で漏洩）／**C-1 DB パスワードは Phase 8 解約で自動消滅だが、念のため記録**
  - **Private** → 7-P3 で Owner 判断

### 4.2 7-P2: GitHub `kurinobu/influberry` Visibility

同上。InfluBerry に Brevo / 機密ハードコードがあるかは [Phase 6 実施手順 §6-C](20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md#step-6-c-influberrydokploy) で未追跡。Owner が今回確認するなら同時に GitHub Visibility だけ記録。

### 4.3 7-P3: C-2 Brevo API キー ローテーション要否

| 7-P1 結果 | 判断 |
|----------|------|
| Public | **必須**・Phase 7 着手前に実施（Brevo 管理画面で旧キー無効化 → 新キー発行 → Dokploy `motivation-app-staging` Env `BREVO_API_KEY` を新値に更新 → Deploy 再実行 → メール送信疎通） |
| Private | **Owner 判断**（運用ローテーション の良いタイミング） |

### 4.4 7-P4: C-3 管理者パスワード `'kurikuri'` の取扱

| 選択肢 | 内容 | 推奨度 |
|--------|------|--------|
| (A) 据え置き（fallback 動作維持） | 何もしない・本 Phase 7 のスコープ外 | △（Public なら NG） |
| (B) Dokploy Env で `ADMIN_PASSWORD_HASH` を新値で設定 | コード非変更・即時反映可（Owner が新パスワード生成 → `generate_password_hash()` 実行 → Dokploy Env Save → Deploy） | ◯（Phase 7 内で実施可能） |
| (C) コード修正で fail-fast 化 + Env 必須化 | コード変更 PR が必要・別 Phase | △（Phase 7+ 推奨） |

→ Owner 判断。(B) なら本 Phase で同時実施可。

### 4.5 7-P5: ムームードメイン現状

Owner がムームー画面で確認:

- `influberry.jp` Aレコード現向き先（Render IP 残置の有無）
- `staging.influberry.jp` の有無・現向き先
- motivation_app 本ドメインの所有有無
- 上記の **現在の TTL**（300s 推奨・切替時の反映時間に影響）

### 4.6 7-P6: Phase 7 専用手順書の完成方針

本書（本ドキュメント）は **7-A 確認待ちで枠組みのみ**。Owner 提供情報を 7-B で本書に追記し、7-D 以降の具体的なナビ（コマンド・画面手順）を確定する。

### 4.7 7-A 完了条件

- [ ] 7-P1〜7-P5 の事実が Owner から本書 §11 にメモされている
- [ ] 7-P3 / 7-P4 の Owner 判断が記録されている
- [ ] **YadOPERA 全 200 / Phase 6 暫定 hostname 全 200** の事前ベースライン取得済（次の §5 Step 7-B 冒頭）

---

## 5. Step 7-B: DNS 現状の事実記録（ムームー画面 + 事前ベースライン curl）

### 5.1 事前ベースライン（Phase 7 着手前の正常状態を実測・Mac）

```bash
echo "=== Phase 7 着手前ベースライン (Mac) ==="
date
curl -sS "https://api.yadopera.com/api/v1/health"; echo
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "yadopera_staging_app=%{http_code}\n" "https://staging-app.yadopera.com/"
curl -sS -o /dev/null -w "influberry_local=%{http_code}\n" -H "Host: staging-influberry.local" "http://160.251.199.237/"
curl -sS -o /dev/null -w "motivation_local=%{http_code}\n" -H "Host: staging-motivation.local" "http://160.251.199.237/"
echo "=== END ==="
```

期待値: YadOPERA health `healthy` / app・staging-app 200 / influberry_local 200 / motivation_local 200

→ **失敗時は Phase 7 に進まず、Phase 6 完了状態を再確認**。

### 5.2 ムームー画面の事実記録（Owner が記録 → 本書末尾 §11 に貼り付け）

Owner がムームー DNS 画面を開き、以下を箇条書きで本書 §11 に記録:

- ドメイン名
- サブドメインの一覧
- 各レコード（A / CNAME / TXT）の現値と TTL
- 削除すべき旧 Render IP（あれば）

→ **記録のみ・変更は 7-D まで保留**。

### 5.3 7-B 完了条件

- [ ] §5.1 ベースライン全期待値クリア
- [ ] §11 に DNS 現状が事実記録されている

---

## 6. Step 7-C: C-2 / C-3 ローテーション判断・実施（Owner 判断）

### 6.1 C-2 Brevo API キー（7-P3 の結果に従う）

#### 6.1.1 ローテーション実施（Public または Owner 判断 = YES の場合）

1. Brevo 管理画面 → 旧キー（`xkeysib-ae0b...`）を **無効化**
2. 新キー発行・**チャットには貼らない**・Mac の安全な場所に一時保管
3. Dokploy `motivation-app-staging` → Environment Settings → `BREVO_API_KEY` を新値に更新 → Save
4. Deploy 実行 → ログで起動成功確認
5. メール疎通: motivation_app の任意のメール送信機能（パスワード再設定など）でメール到達確認 → Brevo 管理画面で送信ログ確認

#### 6.1.2 据え置き（Private + Owner 判断 = NO の場合）

- 何もしない・本書 §11 に「7-C 据え置き理由」を Owner 名義で記録

### 6.2 C-3 管理者パスワード（7-P4 の結果に従う）

#### 6.2.1 Dokploy Env で `ADMIN_PASSWORD_HASH` を新値設定（推奨 = B 案）

Mac で新パスワードハッシュ生成:

```bash
python3 -c "from werkzeug.security import generate_password_hash; import getpass; pw=getpass.getpass('new admin password: '); print(generate_password_hash(pw))"
```

→ 出力されたハッシュ文字列を Dokploy `motivation-app-staging` → Env で `ADMIN_PASSWORD_HASH` として **新規追加** → Save → Deploy。

#### 6.2.2 据え置き（A 案 = fallback 維持）

- 何もしない・本書 §11 に「7-C 据え置き理由」を Owner 名義で記録

### 6.3 7-C 完了条件

- [ ] 7-P3 / 7-P4 の Owner 判断が実施または据え置きで明確
- [ ] 実施した場合 Deploy Done を確認・据え置きの場合は理由が記録

---

## 7. Step 7-D / 7-E: Dokploy Domains 切替

### 7.1 前提（事前 DNS 設定 = Owner 作業）

7-B で確認した DNS を Owner がムームー画面で以下に設定:

| サブドメイン | 種別 | 値 | TTL |
|--------------|------|-----|-----|
| `staging.influberry.jp`（または Owner 指定） | A | `160.251.199.237` | 300（反映加速） |
| motivation_app 本ドメイン（Owner 確定値） | A | `160.251.199.237` | 300 |

DNS 反映待ち（5〜30 分）。Mac で `dig` 確認:

```bash
dig +short staging.influberry.jp
dig +short ＜motivation-app の本ドメイン＞
```

→ 両方とも `160.251.199.237` を返すまで待つ。

### 7.2 7-D: InfluBerry Domains 切替

1. Dokploy `influberry-staging` → Domains
2. 既存 `staging-influberry.local` → **Edit**
   - Host: `staging.influberry.jp`（または Owner 確定値）
   - Path: `/`
   - Port: `5001`
   - HTTPS: **ON**
   - Certificate provider: **letsencrypt**
   - Save
3. Dokploy が Traefik 設定を更新・letsencrypt が証明書発行
4. **YadOPERA / motivation_app に影響していない**ことを Mac から即確認:
   ```bash
   curl -sS "https://api.yadopera.com/api/v1/health"; echo
   curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
   curl -sS -o /dev/null -w "motivation_local=%{http_code}\n" -H "Host: staging-motivation.local" "http://160.251.199.237/"
   ```

### 7.3 7-E: motivation_app Domains 切替

1. Dokploy `motivation-app-staging` → Domains
2. 既存 `staging-motivation.local` → **Edit**
   - Host: Owner 確定値（例: `staging.motifinder.jp` 等・**7-A で確定**）
   - Path: `/`
   - Port: `5002`
   - HTTPS: **ON**
   - Certificate provider: **letsencrypt**
   - Save
3. **YadOPERA / InfluBerry に影響していない**ことを即確認

### 7.4 7-D / 7-E 完了条件

- [ ] Dokploy Save Successful（両 Application）
- [ ] letsencrypt 証明書発行ログを Dokploy で確認
- [ ] YadOPERA health `healthy` / app 200 / staging-app 200 維持

---

## 8. Step 7-F / 7-G: TLS 有効化と疎通確認

### 8.1 letsencrypt 発行待ち

Dokploy 画面の Domains 行に **緑チェック** または **Certificate active** が出るまで 1〜10 分待つ。失敗した場合は **DNS 未反映の可能性**が高い（§7.1 の `dig` を再確認）。

### 8.2 7-G 疎通確認（1 ブロック・Mac）

```bash
echo "=== Phase 7 完了疎通 (Mac) ==="
date
curl -sS "https://api.yadopera.com/api/v1/health"; echo
curl -sS -o /dev/null -w "yadopera_app=%{http_code}\n" "https://app.yadopera.com/"
curl -sS -o /dev/null -w "yadopera_staging_app=%{http_code}\n" "https://staging-app.yadopera.com/"
curl -sS -o /dev/null -w "influberry_https=%{http_code}\n" "https://staging.influberry.jp/"
curl -sS "https://staging.influberry.jp/" | grep -o '<title>[^<]*</title>' | head -1
curl -sS -o /dev/null -w "motivation_https=%{http_code}\n" "https://＜motivation 本ドメイン＞/"
curl -sS "https://＜motivation 本ドメイン＞/" | grep -o '<title>[^<]*</title>' | head -1
echo "=== END ==="
```

### 8.3 期待値

| 行 | 期待値 |
|----|--------|
| 1 | `{"status":"healthy",...}` |
| 2 | `yadopera_app=200` |
| 3 | `yadopera_staging_app=200` |
| 4 | `influberry_https=200`（HTTPS で 200） |
| 5 | `<title>InfluBerry - ...` |
| 6 | `motivation_https=200`（HTTPS で 200） |
| 7 | `<title>キャラまるわかり - ...` |

→ **失敗時は Domains 切替を元に戻す（暫定 `*.local` に戻す）**・本書 §11 に失敗事象を記録。

### 8.4 7-G 完了条件

- [ ] 全 7 行が期待値クリア
- [ ] Owner が画面で実際にログイン・主要機能を試して問題なし

---

## 9. Phase 7 着手前 Owner 必須確認（7-P1〜7-P6）

| # | 項目 | 結果記入欄 | 担当 |
|---|------|----------|------|
| 7-P1 | GitHub `kurinobu/motivation_app` Visibility | □ Public / □ Private（記入: ） | Owner |
| 7-P2 | GitHub `kurinobu/influberry` Visibility | □ Public / □ Private（記入: ） | Owner |
| 7-P3 | C-2 Brevo キー ローテーション | □ 実施 / □ 据え置き（理由: ） | Owner |
| 7-P4 | C-3 管理者パスワード `'kurikuri'` 対応 | □ A 据え置き / □ B Env で再設定 / □ C コード PR | Owner |
| 7-P5 | DNS 現状（§5.2 §11 にメモ） | □ 記録済 | Owner |
| 7-P6 | DNS 切替先（本ドメイン）の確定値 | InfluBerry: `_________` / motivation_app: `_________` | Owner |

---

## 10. Step 7-H: 証跡・親引き継ぎ更新

### 10.1 証跡作成

`docs/evidence/20260527_phase7_dns_complete.md`（仮）を新規作成し、以下を記録:

- 7-A〜7-G の実測値
- DNS 切替前後の `dig` 結果
- letsencrypt 発行ログ
- YadOPERA 無影響の証跡
- C-2 / C-3 の対応結果

### 10.2 親引き継ぎ更新

[ConoHa VPS 移転統合 引き継ぎ](./20260521_ConoHaVPS_移転統合_引き継ぎ.md) を更新:

- 冒頭プロンプトを Phase 8 用に
- 全体ロードマップ §Phase 7 を ✅ に
- §Phase 7 セクションを完了状態に
- 変更履歴に 2026-05-27（仮）を追加

### 10.3 Phase 6 / 7 関連文書の整理

- 本書（Phase 7 手順書）に「Phase 7 完了」セクションを追加
- v4 要約定義書（`docs/Summary/yadopera-v04-summary.md`）に Phase 7 完了を反映（v4.1.2 を追加）
- `docs/README.md` ConoHa 本番移行 § の次 Phase を Phase 8 に
- `docs/maintenance/README.md` の Phase 6 / Phase 7 を完了状態に

---

## 11. Phase 7 Owner 記入欄（事実の記録・憶測禁止）

> Owner が 7-A / 7-B 完了時にここに事実を記入。本書を更新する Cursor は、ここに書かれた事実のみを引用すること。

### 11.1 GitHub Visibility（7-P1 / 7-P2）

- `kurinobu/motivation_app`: （未記入）
- `kurinobu/influberry`: （未記入）

### 11.2 DNS 現状（7-B 時点・ムームー画面）

- ドメイン: （未記入）
- 既存サブドメイン一覧: （未記入）
- 既存 A レコード: （未記入）
- 旧 Render IP 残置: （未記入）

### 11.3 DNS 切替先確定値（7-P6）

- InfluBerry staging: （未記入）
- motivation_app staging: （未記入）

### 11.4 ローテーション判断（7-P3 / 7-P4）

- C-2 Brevo: （未記入）
- C-3 管理者パスワード: （未記入）

### 11.5 Phase 7 着手前ベースライン curl（§5.1 実測）

- 日時: （未記入）
- 結果: （未記入）

---

## 12. Phase 7 完了チェックリスト

**必須**

- [ ] 7-A: Owner 確認 §11 記入済（7-P1〜7-P6）
- [ ] 7-B: 事前ベースライン curl 全期待値クリア・DNS 現状を §11 に記録
- [ ] 7-C: C-2 / C-3 の Owner 判断と実施／据え置きを §11 に記録
- [ ] 7-D: InfluBerry Domains 切替 Save Successful・letsencrypt 発行
- [ ] 7-E: motivation_app Domains 切替 Save Successful・letsencrypt 発行
- [ ] 7-G: 全 7 行疎通期待値クリア（HTTPS で 200 + title）
- [ ] 7-H: 証跡 `docs/evidence/202605xx_phase7_dns_complete.md` 作成
- [ ] 親引き継ぎ Phase 7 ✅ 化

**Phase 7 完了宣言の条件**: 上記必須すべて `[x]` → **Phase 8**（Render 解約）着手可。

**Phase 7 に含めない（Phase 8 以降 / 別 PR）**:
- C-1（旧 Render DB ハードコード）コード修正 → Phase 8 解約で自動消滅・据え置き可
- Render 解約 → Phase 8
- C-2 / C-3 のコード fail-fast 化 → 別 PR
- git history から旧 Brevo キー削除（git filter-repo・別 PR）
- motivation_app の APScheduler 分離 → 運用負荷次第・別 Phase

---

## 13. ナビ原則（Phase 2〜6 継承）

1. **Owner のスクショ・ターミナル出力が正**
2. **プレースホルダ禁止** — 確定したホスト名・Application 名だけ。未確定は §11 に「未記入」と明示し、確定後に本書を更新
3. **Step 完了のたびに** 本書と [親引き継ぎ](./20260521_ConoHaVPS_移転統合_引き継ぎ.md) を更新
4. **YadOPERA 本番を壊さない** — 共有 Postgres / Traefik / Dokploy 操作は影響範囲を確認
5. **DNS** — ムームー画面を見てから書く・反映待ちは `dig` で確認
6. **誓約**: Cursor は未確認の事実を「ある」「無い」と断言しない・憶測ナビ禁止（Phase 6 6-D-6 で確認した方針を継承）

---

## 14. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-05-26 19:25 | 初版（Phase 6 完了を受けて Phase 7 専用手順書を新規作成。7-A 着手前 Owner 確認・7-B〜7-H Step 構成・§11 Owner 記入欄・§12 完了チェックリスト・誓約継承を明記。本ドメイン候補は Owner 確認待ちでプレースホルダで記述。） |
