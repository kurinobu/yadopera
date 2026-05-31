# docs/maintenance 運用ガイド

`docs/maintenance` は、仕様正本とは分離した**運用整理メモ**と**移行レビュー資料**の保管場所です。

---

## 1. 配置対象（短縮版）

- 置く: 参照統一メモ、影響範囲チェック結果、分割レビュー資料
- 置かない: 正式仕様/設計（`docs/Summary/`, `docs/Architecture/`）、証跡（`docs/evidence/`）

---

## 2. 命名規則

- フォルダ: `YYYYMMDD_テーマ名`
- ファイル: `目的が分かる短い日本語名.md`

例: `docs/maintenance/20260422_v4参照統一/レビュー整理.md`

---

## 3. 更新責任者と保管期限

- 更新責任者: 変更を実施した担当者（AI作業時は実行者が記録）
- 保管期限: 90日（延長が必要なものだけ継続保管）
- 期限超過ファイルは月次で見直し、不要なら削除または `docs/reports/` へ移管

---

## 4. 現行の重要手順書

| 文書 | 内容 |
|------|------|
| [20260521_ConoHaVPS_移転統合_引き継ぎ.md](./20260521_ConoHaVPS_移転統合_引き継ぎ.md) | Render/Railway → ConoHa 移行（Phase 0〜9） |
| [20260521_Phase2_ConoHa初期設定_実施手順.md](./20260521_Phase2_ConoHa初期設定_実施手順.md) | Phase 2 画面・コマンド手順（Dokploy / PG / Redis）✅ |
| [20260521_Phase3_YadOPERAデプロイ準備_実施手順.md](./20260521_Phase3_YadOPERAデプロイ準備_実施手順.md) | Phase 3 staging Backend/Frontend ✅ 完了（2026-05-22） |
| [20260521_Phase4_DBリストア_実施手順.md](./20260521_Phase4_DBリストア_実施手順.md) | Phase 4 DB リストア ✅（2026-05-23） |
| [20260521_Phase5_YadOPERAサービス再開_実施手順.md](./20260521_Phase5_YadOPERAサービス再開_実施手順.md) | Phase 5 ✅（2026-05-24） |
| [20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md](./20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md) | Phase 6 ✅ 完了（2026-05-26・InfluBerry + motivation_app 両者 Deploy + 暫定 hostname 疎通確認済） |
| [20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md](./20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md) | Phase 7 ✅ staging 完了（2026-05-29） |
| [20260529_サービス再開_三本柱_実施計画.md](./20260529_サービス再開_三本柱_実施計画.md) | **サービス再開正本** — ①②③ **すべて ✅**（2026-05-29） |
| [20260529_YadOPERA_サービス再開_計画.md](./20260529_YadOPERA_サービス再開_計画.md) | ① YadOPERA ✅ |
| [20260529_InfluBerry_本番載せ替え_サービス再開_計画.md](./20260529_InfluBerry_本番載せ替え_サービス再開_計画.md) | ② InfluBerry ✅ |
| [20260529_キャラまるわかり_本番載せ替え_サービス再開_計画.md](./20260529_キャラまるわかり_本番載せ替え_サービス再開_計画.md) | ③ キャラまるわかり ✅ |
| [20260529_キャラまるわかり_本番載せ替え_実施手順.md](./20260529_キャラまるわかり_本番載せ替え_実施手順.md) | ③ 実施手順 ✅（MO-0〜MO-8 記録） |
| [../evidence/20260529_influberry_prod_service_resumption_complete.md](../evidence/20260529_influberry_prod_service_resumption_complete.md) | ② 完了証跡（IB-8 含む） |
| [../evidence/20260529_motivation_prod_service_resumption_complete.md](../evidence/20260529_motivation_prod_service_resumption_complete.md) | ③ 完了証跡（MO-0〜MO-8） |
| [20260527_Phase8_Render_Railway_解約_実施手順.md](./20260527_Phase8_Render_Railway_解約_実施手順.md) | Phase 8 ✅ 完了（2026-05-27） |
| [../evidence/20260524_yadopera_conoha_migration_complete.md](../evidence/20260524_yadopera_conoha_migration_complete.md) | **YadOPERA 移行完了・サービス開始可能**（2026-05-24） |
| [../evidence/20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md) | **Phase 6 完了**（2026-05-26・motivation_app Deploy Done + Phase 6 全体完了宣言） |
| [../evidence/20260529_phase7_dns_complete.md](../evidence/20260529_phase7_dns_complete.md) | **Phase 7 staging 完了**（2026-05-29） |
| [../evidence/20260529_all_services_browser_path_check.md](../evidence/20260529_all_services_browser_path_check.md) | **全サービス疎通**（本番・staging 9 URL・2026-05-29） |
| [scripts/check_service_resumption_all.sh](./scripts/check_service_resumption_all.sh) | 上記の再実行スクリプト |
| [../evidence/20260527_phase8_render_railway_partial.md](../evidence/20260527_phase8_render_railway_partial.md) | **Phase 8 部分完了**（2026-05-27・Final $102.35 / $0.00 確定・6 月以降課金ゼロ） |
| [../evidence/20260531_dokploy_autodeploy_security_group_remediation.md](../evidence/20260531_dokploy_autodeploy_security_group_remediation.md) | **Dokploy Auto Deploy 不発** — ConoHa SG + GitHub hooks CIDR 復旧（2026-05-31） |
| [../reports/202605/20260531_会話詳細404とDokploy_AutoDeploy_SG復旧_作業報告.md](../reports/202605/20260531_会話詳細404とDokploy_AutoDeploy_SG復旧_作業報告.md) | 会話詳細 404 修正 + SG 復旧 作業報告 |

---

## 5. 新規運用文書の配置先（固定）

- 運用手順/チェックリスト: `docs/operations/YYYYMM/`
- 調査報告/実施報告: `docs/reports/YYYYMM/`
- `docs/` 直下へ新規運用文書を増やさない

---

## 6. 変更ガード（既存差分を触らない）

1. 開始時に `git status -sb` を記録
2. 終了時に `git status -sb` を再取得
3. 既存差分の増減を照合し、意図外変更は `git restore` で戻す

---

## 7. 参照更新チェック（先行自動化）

移動・置換の前に以下を実行して旧参照を列挙する。

```bash
rg "yadopera-v03-summary\\.md" docs --glob "*.md"
```

完了条件:
- 意図した残置（`旧版履歴`、`docs/Backups/**`、`*.backup*`）以外が0件
- 自動チェックは `docs/maintenance/scripts/check_v03_reference_residue.sh` を使用

---

## 8. コミット分割ルール

- Commit 1: 正本・参照の意味変更（`v4`統一）
- Commit 2: フォルダ整理（配置変更）

この2分割を守り、レビュー/ロールバックを容易にする。
