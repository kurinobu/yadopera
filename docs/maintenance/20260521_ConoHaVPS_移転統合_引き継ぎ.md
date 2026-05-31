# ConoHa VPS へ移転・統合 — 引き継ぎ手順書

**作成日**: 2026-05-21  
**目的**: Render / Railway から ConoHa VPS（12GB）へ集約移行する。  
**次会話**: **三本柱 ①②③ 完了**（2026-05-29）。載せ替え・サービス再開の正本は [三本柱実施計画](./20260529_サービス再開_三本柱_実施計画.md)。全 URL 疎通記録は [証跡](../evidence/20260529_all_services_browser_path_check.md)。**2026-05-31 追記**: [Dokploy Auto Deploy 不発（SG 復旧）](./20260521_ConoHaVPS_移転統合_引き継ぎ.md#運用インシデント-dokploy-auto-deploy-不発2026-05-31)。**残**: Phase 8 カード削除（6/3・6/21 以降）／Phase 9 PublishDone／`www.*` DNS 後追い。
**前提**: サーバー知識は最小。Cursor による画面・コマンド単位のナビ。代行業者は不要。

**サービス再開 三本柱（次会話の正本）**: [20260529_サービス再開_三本柱_実施計画.md](./20260529_サービス再開_三本柱_実施計画.md)  
**Phase 8 実施手順**: [20260527_Phase8_Render_Railway_解約_実施手順.md](./20260527_Phase8_Render_Railway_解約_実施手順.md) ✅（2026-05-27）  
**Phase 7 実施手順（完了・staging）**: [20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md](./20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md) ✅（2026-05-29・[完了証跡](../evidence/20260529_phase7_dns_complete.md)）  
**Phase 6 実施手順（完了）**: [20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md](./20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md) ✅（2026-05-26）  
**Phase 5 実施手順（完了）**: [20260521_Phase5_YadOPERAサービス再開_実施手順.md](./20260521_Phase5_YadOPERAサービス再開_実施手順.md) ✅（2026-05-24）  
**Phase 4 実施手順（完了）**: [20260521_Phase4_DBリストア_実施手順.md](./20260521_Phase4_DBリストア_実施手順.md)  
**Phase 3 実施手順（完了）**: [20260521_Phase3_YadOPERAデプロイ準備_実施手順.md](./20260521_Phase3_YadOPERAデプロイ準備_実施手順.md)

---

## 全体ロードマップ（番号はそのまま）

**時間の見方**: あなたが画面操作・コピペを行い、Cursor がナビする前提。**1日 = 作業 2〜4 時間**くらいのペース想定。初めての作業は上限寄り。

| Phase | 名称 | 目安時間（作業） | カレンダー目安 | 状態 |
|-------|------|------------------|----------------|------|
| **0** | ダンプ・バックアップ | **3〜5 時間**（実績） | 1〜2 日（分割） | ✅ **完了**（2026-05-21） |
| **1** | ConoHa 契約（12GB） | **0.5〜1 時間** | 当日 | ✅ **完了**（2026-05-21） |
| **2** | ConoHa 初期設定 | **3〜6 時間** | 1〜2 日 | ✅ **完了**（2026-05-21・[実施手順](./20260521_Phase2_ConoHa初期設定_実施手順.md)） |
| **3** | YadOPERA 実装（デプロイ準備） | **4〜8 時間** | 2〜3 日 | ✅ **完了**（2026-05-22・[実施手順](./20260521_Phase3_YadOPERAデプロイ準備_実施手順.md)） |
| **4** | Railway 統合（DB リストア） | **1.5〜3 時間** | 半日 | ✅ **完了**（2026-05-23・[実施手順](./20260521_Phase4_DBリストア_実施手順.md)） |
| **5** | YadOPERA ConoHa 本番公開（**インフラ**） | **2〜5 時間** | 1 日 | ✅ **完了**（2026-05-24）+ ① サービス再開 ✅ |
| **6** | InfluBerry・キャラまるわかり **staging** 実装 | **3〜6 時間** | 1〜2 日 | ✅ **完了**（2026-05-26） |
| **7** | DNS 本ドメイン化・HTTPS 化（**staging**） | **1〜3 時間** | 半日 | ✅ **完了**（2026-05-29） |
| **SR** | **サービス再開 三本柱** ①→②→③ | **各 2〜5 時間** | 数日 | ✅ **完了**（2026-05-29・[正本](./20260529_サービス再開_三本柱_実施計画.md)・[全 URL 証跡](../evidence/20260529_all_services_browser_path_check.md)） |
| **8** | Render 解約・Railway クローズアウト | **0.5〜1 時間** | 当日 | ✅ **完了**（2026-05-27） |
| **9** | PublishDone 実装開始 | **着手 2〜4 時間**（以降は別計画） | 別トラック | 未 |

### 合計イメージ（Phase 1〜8・やどぺら再開まで）

| 区分 | 時間 |
|------|------|
| **作業時間の合計** | **約 16〜33 時間** |
| **カレンダー（副業ペース）** | **約 2〜4 週間**（1日 2〜3 時間） |
| **カレンダー（集中）** | **約 4〜7 営業日**（1日 4〜6 時間） |

※ Phase 9（PublishDone）は MVP 開発全体で **別途数週間〜数月**（[PublishDone 定義書](file:///Users/kurinobu/projects/PublishDone/publishdone_v0_172.md) 参照）。

### クリティカルパス（最優先で再開するまで）

```
Phase 1 → 2 → 3 → 4 → 5  ≒ 作業 11〜23 時間（カレンダー 3〜5 日〜2 週間）
```

Phase 6〜7 はやどぺら安定後でよい。**Phase 8 は 2026-05-27 に Phase 7 へ先回り完了**。

### サービス再開 三本柱（2026-05-29 正本・順序固定）

| 順 | プロダクト | 計画書 | 状態 |
|----|-----------|--------|------|
| **①** | YadOPERA サービス再開 | [計画](./20260529_YadOPERA_サービス再開_計画.md) | ✅ |
| **②** | InfluBerry 本番載せ替え + 再開 | [計画](./20260529_InfluBerry_本番載せ替え_サービス再開_計画.md) | ✅ |
| **③** | キャラまるわかり 本番載せ替え + 再開 | [計画](./20260529_キャラまるわかり_本番載せ替え_サービス再開_計画.md) | ✅ |

正本: [20260529_サービス再開_三本柱_実施計画.md](./20260529_サービス再開_三本柱_実施計画.md) · 全 URL 証跡: [20260529_all_services_browser_path_check.md](../evidence/20260529_all_services_browser_path_check.md)  
訂正根拠: [調査報告](../reports/202605/20260529_サービス再開_認識訂正_調査報告.md)

### 実施順の注意（Phase 3 と 4）

番号は **3 → 4** のまま進めるが、**技術的には Phase 4（DB リストア）を Phase 5 の直前までに完了**させる。

- **Phase 3**: Dokploy プロジェクト作成・Git 連携・`docker-compose` / 環境変数テンプレ・ビルド確認（DB 未接続でも可）
- **Phase 4**: Postgres（pgvector）へダンプリストア → `DATABASE_URL` 確定
- **Phase 5**: DNS・Stripe Webhook・ヘルス確認で公開

---

## 目標アーキテクチャ（1 台集約）

```
┌─────────────────────────────────────────────────────────┐
│ ConoHa VPS 12GB + Dokploy（1 契約）                      │
│                                                          │
│  [本番] YadOPERA    FastAPI + Vue(static) + DB yadopera   │
│  [stg]  YadOPERA    同上・DB yadopera_staging            │
│  [stg]  InfluBerry  Flask + Vue                         │
│  [stg]  キャラまるわかり motivation_app Flask           │
│  （将来）PublishDone  FastAPI API のみ追加                │
│                                                          │
│  Postgres (pgvector/pg15 or 18)  Redis                  │
│  本番/staging は DB 名・サブドメインで分離（別 VPS 不要）  │
└─────────────────────────────────────────────────────────┘

LP: yadopera.com → GitHub Pages（変更なし）
DNS: ムームー → api / app 等を ConoHa 向け
```

**Render**: 本番ワークスペース削除済み・**データ復旧不可**（サポート返信済み）。  
**Railway**: Postgres ダンプ取得済み。`soothing-acceptance` は**削除可**（未使用）。

---

## 関連文書（この会話・リポジトリ）

| 文書 | 内容 |
|------|------|
| [国内サーバー移行 検討メモ（セッション要約）](./20260519_国内サーバー移行_検討メモ_セッション要約.md) | Render 障害・ConoHa/さくら比較・費用・ブランチ戦略 |
| [Render 障害 バックアップ移行チェックリスト](./20260519_Render障害_バックアップ移行チェックリスト.md) | 退避・DNS・最優先アクション |
| [バックアップ確認結果（リポジトリ要約）](./20260521_バックアップ確認結果.md) | ダンプ一覧の短縮版 |
| [Phase4 DB リストア 実施手順](./20260521_Phase4_DBリストア_実施手順.md) | Phase 4 画面・コマンド ✅ |
| [Phase5 サービス再開 実施手順](./20260521_Phase5_YadOPERAサービス再開_実施手順.md) | Phase 5 ✅（2026-05-24） |
| [Phase6 InfluBerry・キャラまるわかり 実施手順](./20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md) | Phase 6 ✅ 完了（2026-05-26） |
| [サービス再開 三本柱 実施計画](./20260529_サービス再開_三本柱_実施計画.md) | **正本** ①②③ ✅ |
| [全サービス疎通証跡](../evidence/20260529_all_services_browser_path_check.md) | 本番・staging 9 URL 検証記録 |
| [check_service_resumption_all.sh](./scripts/check_service_resumption_all.sh) | 疎通再実行スクリプト |
| [Phase7 DNS staging 実施手順](./20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md) | Phase 7 ✅ staging 完了 |
| [Phase8 Render・Railway 解約 実施手順](./20260527_Phase8_Render_Railway_解約_実施手順.md) | Phase 8 主要作業完了（2026-05-27）+ カード削除残（6/3 / 6/21 以降） |
| [Phase 8 部分完了証跡](../evidence/20260527_phase8_render_railway_partial.md) | Render Hobby 化・Railway 全プロジェクト削除 + Plan Cancel・Final $102.35 / $0.00 確定 |
| [Phase 6 完了証跡](../evidence/20260526_phase6_motivation_app_complete.md) | motivation_app Deploy Done + Phase 6 全体完了宣言 |
| [motivation_app 事前調査報告書（訂正版）](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md) | C-1/C-2/C-3 + 誓約遵守記録 |
| [やどぺら v4 要約定義書](../Summary/yadopera-v04-summary.md) | 正本 v4.1.0・ConoHa 運用・ブランチ `develop→main` |
| [YadOPERA 移行完了証跡](../evidence/20260524_yadopera_conoha_migration_complete.md) | サービス開始可能判定 |
| [アーキテクチャ設計書 v0.3](../Architecture/やどぺら_v0.3_アーキテクチャ設計書.md) | API・DB・デプロイ詳細 |
| [maintenance README](./README.md) | 運用文書の置き場ルール |

### 手元のみ（Git 管理外・秘密情報あり）

| パス | 内容 |
|------|------|
| [/Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/BACKUP_STATUS_20260521.md](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/BACKUP_STATUS_20260521.md) | ダンプ最終一覧・本番 DB 選定 |
| [/Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/railway-dumps/](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/railway-dumps/) | 全 `.dump` / `.sql.gz` |
| [/Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/railway_dump_all.sh](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/railway_dump_all.sh) | Railway 再ダンプ用スクリプト |
| [/Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/RENDER_ENV_INVENTORY.md](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/RENDER_ENV_INVENTORY.md) | Render env 手動記入用（未記入） |

### コードベース参照

| パス | 用途 |
|------|------|
| [docker-compose.yml](../../docker-compose.yml) | ローカル開発・Postgres pgvector イメージ |
| [backend/Dockerfile](../../backend/Dockerfile) | 本番 Backend |
| [frontend/Dockerfile](../../frontend/Dockerfile) | 本番 Frontend |
| [render.yaml](../../render.yaml) | 旧ステージング定義（参考） |
| [backend/.env.example](../../backend/.env.example) | 環境変数テンプレ |

### PublishDone（Phase 9 以降）

| パス | 用途 |
|------|------|
| [/Users/kurinobu/projects/PublishDone/publishdone_v0_172.md](file:///Users/kurinobu/projects/PublishDone/publishdone_v0_172.md) | 統合定義・ConoHa 2GB/12GB 比較 |
| [/Users/kurinobu/projects/PublishDone/publishdone_summary_definition_v0.16.md](file:///Users/kurinobu/projects/PublishDone/publishdone_summary_definition_v0.16.md) | 要約定義 |

### 他リポジトリ

| サービス | パス |
|----------|------|
| InfluBerry | `/Users/kurinobu/projects/influberry_v2` |
| キャラまるわかり（motivation_app） | `/Users/kurinobu/motivation_app` |

---

# Phase 0: ダンプ・バックアップ ✅ 完了

**完了日**: 2026-05-21  
**目安時間**: 3〜5 時間（実績・Railway CLI ログイン含む）

## 0.1 実施結果

| 対象 | ファイル（`railway-dumps/` 内） | サイズ | 用途 |
|------|--------------------------------|--------|------|
| やどぺら **本番候補** | `yadopera_local_docker_20260521_114837.sql.gz` | 14 MB | 施設 **68**・**本番リストア第一候補** |
| やどぺら **staging** | `yadopera_18pgvector_20260521_120240.dump` | 12 MB | Railway `18pgvector`・PG 18 |
| やどぺら（旧 URL・参考） | `yadopera_railway_tramway_20260521_115100.dump` | 12 MB | 重複参考 |
| InfluBerry staging | `influberry_influberry-staging_20260521_120240.dump` | 41 KB | |
| キャラまるわかり DB | `influberry_motivation_app_db_20260521_120240.dump` | 165 KB | `motivation_app_db` |

## 0.2 取得不可・不要

| 対象 | 状態 |
|------|------|
| **Render 本番**（Postgres / Web / env） | ❌ ワークスペース削除・**復旧不可** |
| **yadopera-redis-staging** | 未ダンプ（空 Redis で再開可） |
| **soothing-acceptance**（Railway） | **削除可**（未使用） |
| Stripe live / Render 本番 env | Stripe ダッシュボード等から再取得 |

## 0.3 本番 DB の選定（ConoHa リストア時）

| DB 名（ConoHa 上で作成） | リストア元 |
|--------------------------|------------|
| `yadopera`（本番） | `yadopera_local_docker_*.sql.gz` |
| `yadopera_staging` | `yadopera_18pgvector_*.dump` |
| `influberry_staging` | `influberry_influberry-staging_*.dump` |
| `motivation_app` | `influberry_motivation_app_db_*.dump` |

## 0.4 Phase 0 チェックリスト

- [x] Railway Postgres 主要 DB ダンプ
- [x] ローカル Docker やどぺら ダンプ
- [x] Railway CLI ログイン・再ダンプ手順（`railway_dump_all.sh`）確保
- [ ] Stripe 本番キー・Webhook secret の整理（Phase 5 前に必須）
- [ ] Redis 退避（任意）

---

# Phase 1: ConoHa 契約（12GB） ✅ 完了

**完了日**: 2026-05-21  
**目安時間**: 0.5〜1 時間（実績）

## 1.0 実施結果（記録・秘密情報は Git 外に保管）

| 項目 | 値 |
|------|-----|
| ネームタグ | `air-edison_VPS` |
| グローバル IP | `160.251.199.237`（IPv6 あり） |
| OS | **Ubuntu 22.04.3 LTS**（SSH `uname` 確認済み） |
| プラン | 12GB / 6Core / SSD 100GB・まとめトク **1 ヶ月**（約 4,301 円/月） |
| 認証 | root パスワード（Phase 2 で SSH 鍵化可） |
| セキュリティグループ | **`IPv4v6-SSH`**（未設定時は SSH が **Operation timed out**） |

**補足**: 作成ウィザードにリージョン・ネームタグ入力が無い場合あり。リージョンは `conoha.jp` 申込で国内デフォルト想定。OS ホスト名は現状 `vm-98e00cd4-76` → Phase 2 で `hostnamectl set-hostname air-edison_VPS` 可。

## 1.1 推奨プラン

| 項目 | 内容 |
|------|------|
| サービス | [ConoHa VPS](https://www.conoha.jp/vps/) |
| プラン | **12GB**（まとめトク **1 ヶ月** から開始推奨・約 4,300 円/月目安） |
| 理由 | YadOPERA 本番+staging + InfluBerry + motivation + 将来 PublishDone を **1 契約に集約** |
| OS | **Ubuntu 22.04 LTS** |
| リージョン | 東京（国内向け） |

**避けるもの（初期）**: 36 ヶ月前払いまとめトク（途中解約不可）、512MB/1GB プラン。

## 1.2 契約時チェックリスト

- [x] ConoHa アカウント作成・支払い方法登録（国内カード）
- [x] VPS 12GB 作成・root パスワードを安全に保管
- [x] サーバー IP アドレスをメモ（ムームー DNS で使用）
- [x] 初期費用 0 円・初月課金を確認
- [x] セキュリティグループ **`IPv4v6-SSH`** をサーバーに適用（ネットワーク情報 → 編集 → 保存）

## 1.3 完了条件

- [x] 管理画面で VPS が **Running**
- [x] SSH でログイン可能（`ssh root@160.251.199.237`）

---

# Phase 2: ConoHa 初期設定 ✅ 完了（2026-05-21）

**実施手順（画面・コマンド単位）**: [20260521_Phase2_ConoHa初期設定_実施手順.md](./20260521_Phase2_ConoHa初期設定_実施手順.md)  
**本セッションの事実・手順ミス記録**: 同書 [§本セッションの記録（2026-05-21）](./20260521_Phase2_ConoHa初期設定_実施手順.md#本セッションの記録2026-05-21手順ナビの教訓)  
**確認スクリプト**: [scripts/phase2_verify.sh](./scripts/phase2_verify.sh)（VPS 上で実行）  
**目安時間**: 3〜6 時間（Dokploy 初回導入が最長になりやすい）

## 2.0 事前準備・スコープ（Phase 2 完了済み・次会話は Phase 4）

### 事前に読む・調査する必要があるか

| 対象 | Phase 2 前 | いつ必要か |
|------|------------|------------|
| 本引き継ぎ §2・Phase 1 実施結果（IP 等） | **必須**（Cursor が読む） | Phase 2 |
| [docker-compose.yml](../../docker-compose.yml)（Postgres / Redis イメージ参考） | 任意（§2.1 で方針済み） | Phase 2 |
| [やどぺら v0.3 アーキテクチャ設計書](../Architecture/やどぺら_v0.3_アーキテクチャ設計書.md) | **不要** | Phase 3〜5（API・DNS・CORS 等） |
| コードベース全体・`backend/.env.example` 精査 | **不要** | Phase 3（デプロイ・環境変数） |
| ダンプ・[BACKUP_STATUS](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/BACKUP_STATUS_20260521.md) | **不要**（PG18 選定理由は §2.1・Phase 0 で足りる） | Phase 4（リストア） |

**結論**: Phase 2 は「共通インフラの空の土台」構築。**アーキ設計書・YadOPERA コードの本格調査は Phase 3 に回してよい。**

### Phase 2 でやること / やらないこと

| Phase 2 でやる | Phase 2 ではやらない（後続 Phase） |
|----------------|-----------------------------------|
| Dokploy 導入・管理画面アクセス | YadOPERA Backend / Frontend の Dokploy デプロイ → **Phase 3** |
| Postgres（pgvector）・Redis の起動確認 | ダンプの SCP・リストア・4 DB 作成 → **Phase 4** |
| `CREATE EXTENSION vector;`・Redis `PING` | ムームー DNS 切替 → **Phase 5** |
| ファイアウォール（22, 80, 443） | Stripe Webhook・本番 env 全量 → **Phase 3〜5** |
| バックアップ方針のメモ（cron は別途手順化可） | InfluBerry / motivation_app → **Phase 6** |

### ConoHa セキュリティグループ（Phase 1 続き）

**重要（1 台集約・全アプリ共通）**

- 本 VPS は **YadOPERA だけではない**。上記 [目標アーキテクチャ（1 台集約）](#目標アーキテクチャ1-台集約) のとおり、**YadOPERA 本番/staging・InfluBerry・キャラまるわかり・将来 PublishDone** を **同一 ConoHa 12GB + Dokploy** に載せる。
- セキュリティグループは **VPS（NIC）単位のポート開閉**であり、**アプリ別の専用グループは原則不要**（InfluBerry 用に別グループを増やす必要はない）。
- Phase 2 で付けるのは次の **3 種類だけ**（名前は **アプリ名を入れない** 中立名推奨）:

| グループ（推奨名） | 役割 | 対象 |
|--------------------|------|------|
| `IPv4v6-SSH`（既製） | 22 | サーバー管理 |
| `IPv4v6-Web`（既製） | 80, 443 | **全サービス**の HTTP/HTTPS（Traefik/Dokploy 経由） |
| 独自（正本）: **`air-edison-admin-3000`** | 3000（自宅 IP 等） | **Dokploy 管理画面のみ**（VPS ネームタグ `air-edison` に合わせた **VPS 共通**名） |

- **命名規則**: **`{ネームタグの接頭辞}-admin-3000`**（例: ネームタグ `air-edison_VPS` → `air-edison-admin-3000`）。**アプリ名（yadopera 等）は入れない。**
- **避ける命名**: `yadopera-*` など単一アプリ名 — 他アプリ統合と矛盾し誤解を招く。
- **誤名で作成済みの場合**: 上記正本名へ **リネームまたは作り直しは必須**。[Phase2 Step 0.4](./20260521_Phase2_ConoHa初期設定_実施手順.md#04-誤ったグループ名の修正必須)。

Phase 1 で **`IPv4v6-SSH`** を適用済み（port 22）。Phase 2 では **`IPv4v6-Web`** と **3000 用の独自グループ（上表）** を追加する。

| タイミング | 作業 |
|------------|------|
| Phase 1 済 | `IPv4v6-SSH` → SSH（22） |
| **Phase 2** | **`IPv4v6-Web`**（80/443）+ **3000 用独自グループ（IN/TCP）** をサーバーに付与 |

未設定のままだと Dokploy 画面がブラウザから開けない（タイムアウト）ことがある。OS 内 `ufw` は Ubuntu 新規では多く `inactive` — **ConoHa 側のセキュリティグループが主因**になりやすい。

ConoHa 画面に **「Inbound」という語は無い**。ルール作成では **通信方向 = `IN`**。サーバー詳細のドロップダウンは **既製グループの選択**のみ。詳細は [Phase2 実施手順](./20260521_Phase2_ConoHa初期設定_実施手順.md) Step 0。

### 次会話の開始プロンプト（これだけで可）

```
Phase 2 を開始
```

または（明示版）:

```
docs/maintenance/20260521_ConoHaVPS_移転統合_引き継ぎ.md を読んで、
Phase 2（ConoHa 初期設定・Dokploy）から画面操作単位でナビしてください。
```

**手元**: `ssh root@160.251.199.237`、root パスワード（Git 外のパスワード管理ツール）。

## 2.1 方針

- **Dokploy** で Git デプロイ（Render に近い運用）
- Postgres: **`pgvector/pgvector:pg15`** または PG18（18pgvector ダンプ互換のため **18 推奨**）
- Redis: 公式 `redis:7-alpine`
- HTTPS: Dokploy / Traefik + Let's Encrypt

## 2.2 作業一覧（ナビで実施）

詳細は [Phase2 実施手順](./20260521_Phase2_ConoHa初期設定_実施手順.md) の Step 0〜7 に対応。

1. [x] **Step 0** ConoHa セキュリティグループ（`IPv4v6-SSH` + `IPv4v6-Web` + **`air-edison-admin-3000`**）
2. [x] **Step 2** Dokploy 導入（v0.29.4・2026-05-21）
3. [x] **Step 3** Dokploy 管理者アカウント・`http://160.251.199.237:3000` アクセス
4. [x] **Step 4** Postgres — `pgvector/pg18`・`vector 0.8.2` 確認済み（2026-05-21）
5. [x] **Step 5** Redis — `redis:7`・`PING` → `PONG`（要 `-a`）
6. [x] **Step 6** 動作確認（vector・PING — Step 4・5 で実施済み）
7. [x] **Step 7** バックアップ方針メモ（[Phase2 §Step 7](./20260521_Phase2_ConoHa初期設定_実施手順.md#step-7-バックアップ方針メモcron-は-phase-4-後)。**cron / 初回 dump は Phase 4 後**）

## 2.3 完了条件

- Dokploy 管理画面にブラウザアクセス可能
- 空の Postgres に `CREATE EXTENSION vector;` 成功
- Redis `PING` 成功

**参照**: [国内サーバー移行 検討メモ](./20260519_国内サーバー移行_検討メモ_セッション要約.md) § ConoHa + Dokploy

---

# Phase 3: YadOPERA 実装（デプロイ準備）✅ 完了（2026-05-22）

**実施手順（画面・コマンド・Phase 2 完了状態）**: [20260521_Phase3_YadOPERAデプロイ準備_実施手順.md](./20260521_Phase3_YadOPERAデプロイ準備_実施手順.md)  
**目安時間**: 4〜8 時間（環境変数・Stripe キー整理・staging Backend/Frontend の Dokploy 設定）

### Phase 3 進捗（2026-05-22）

| Step | 内容 | 状態 |
|------|------|------|
| 1 | staging Backend `yadopera-backend-staging`・health **200** | ✅ **完了** |
| 2 | staging Frontend（Dockerfile.staging・Context `frontend`） | ✅ **完了** — `/admin/login` 管理ログイン UI（ブラウザ 2026-05-22） |
| 3 | ドメイン（任意） | 未（Phase 3 完了に必須ではない） |
| 4 | Phase 3 完了確認 | ✅ **完了** — health 200・DB/Redis connected |

**実績**: [Phase3 §Step 4 実績](./20260521_Phase3_YadOPERAデプロイ準備_実施手順.md#step-4-実績2026-05-22)・[完了チェックリスト](./20260521_Phase3_YadOPERAデプロイ準備_実施手順.md#phase-3-完了チェックリスト)

### Phase 4 完了サマリ（2026-05-23）

| 項目 | 実績 |
|------|------|
| DB | `yadopera_staging`（30 施設）・`yadopera`（68 施設） |
| staging | `DATABASE_URL` → `yadopera_staging`・health OK |
| ログイン | curl **200**・ブラウザ `/admin/dashboard`（Build Time Arguments + サイトデータ消去） |
| Frontend JS | `index-BqOvmiT1.js`・`160.251.199.237`（`localhost:8000` なし） |
| 任意 4-E | 未（`/tmp/` に influberry ダンプあり） |

※ 詳細は [Phase4 実施手順](./20260521_Phase4_DBリストア_実施手順.md)

### Phase 5 完了サマリ（2026-05-24）

| 項目 | 実績 |
|------|------|
| 本番 API / App | `https://api.yadopera.com` / `https://app.yadopera.com` |
| Stripe Webhook | `charming-bliss` → ConoHa API |
| Brevo | Authorized IPs に `160.251.199.237` 追加（401 復旧） |
| 5-G | health・`/f/68`・LP・管理ログイン OK |

※ 詳細は [Phase5 実施手順 §Phase 5 完了](./20260521_Phase5_YadOPERAサービス再開_実施手順.md#phase-5-完了2026-05-24)・[証跡](../evidence/20260524_conoha_phase5_service_resume.md)

### Phase 7 次会話プロンプト（推奨・2026-05-26 19:25 版）

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

※ 詳細は [Phase7 実施手順 §次会話引き継ぎ](./20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md#次会話引き継ぎphase-7-即開始2026-05-26)

### Phase 2 完了サマリ（次会話用）

| 項目 | 状態 |
|------|------|
| Dokploy | v0.29.4・`http://160.251.199.237:3000` |
| プロジェクト | **`air-edison`** / **`production`** |
| Postgres | `air-edison-postgres`・`pgvector/pg18`・vector **0.8.2**・`1/1` |
| Redis | `air-edison-redis`・`redis:7`・**PONG**（`-a`）・`1/1` |
| 接続情報 | Dokploy **Internal** → **Git 外メモ**（パスワードは文書に書かない） |

### Phase 3 でやる / やらない

| やる | やらない |
|------|----------|
| staging Backend/Frontend（`develop`）・health 200 | DB リストア（**Phase 4**） |
| `DATABASE_URL` / `REDIS_URL` を Internal 向けに設定 | 本番 DNS・Stripe Webhook（**Phase 5**） |

## 3.1 Git / ブランチ（変更なし）

```
feature/* → develop → staging 検証 → main → 本番
```

- LP: `main` の `landing/**` → **GitHub Pages**（ConoHa 不要）
- 正本: [yadopera-v04-summary.md](../Summary/yadopera-v04-summary.md)

## 3.2 Dokploy プロジェクト（案）

| プロジェクト | ブランチ | ドメイン例 |
|--------------|----------|------------|
| yadopera-backend-staging | develop | `staging-api.yadopera.com` |
| yadopera-frontend-staging | develop | `staging-app.yadopera.com` |
| yadopera-backend-production | main | `api.yadopera.com` |
| yadopera-frontend-production | main | `app.yadopera.com` |

## 3.3 環境変数（Backend 必須項目）

`backend/.env.example` および [RENDER_ENV_INVENTORY](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/RENDER_ENV_INVENTORY.md) を参照。

| 区分 | 主なキー |
|------|----------|
| DB | `DATABASE_URL`（asyncpg 形式） |
| Cache | `REDIS_URL` |
| App | `SECRET_KEY`, `ENVIRONMENT`, `CORS_ORIGINS`, `FRONTEND_URL` |
| AI | `OPENAI_API_KEY` |
| Mail | `BREVO_API_KEY`, `BREVO_SENDER_*` |
| 課金 | `STRIPE_*`（**Stripe ダッシュボードから再取得**） |

## 3.4 デプロイ手順の要点

1. [x] Backend staging: `yadopera-backend-staging`・Deploy・health **200**（2026-05-21）
2. [x] Frontend: Dockerfile.staging・`/admin/login` 管理 UI（2026-05-22）
3. [x] ヘルス staging Backend: `GET /api/v1/health` → **200**
4. [x] **DB 実データ・ログイン** — **Phase 4 完了**（2026-05-23・staging）

## 3.5 完了条件

- [x] staging URL でビルド・起動成功（Phase 3 完了・2026-05-22）

---

# Phase 4: Railway 統合（DB リストア）✅ 完了（2026-05-23）

**目安時間**: 1.5〜3 時間（ダンプ SCP・リストア 4 DB・件数確認）  
**実施手順（正本・画面単位）**: [20260521_Phase4_DBリストア_実施手順.md](./20260521_Phase4_DBリストア_実施手順.md)

## 4.0 進捗（2026-05-23）

| Step | 内容 | 状態 |
|------|------|------|
| 4-A | ダンプ SCP → VPS `/tmp/` | ✅ |
| 4-B | DB 4 つ + `vector` | ✅ |
| 4-C | `yadopera_staging` リストア（facilities **30**） | ✅ |
| 4-D | `yadopera` リストア（facilities **68**） | ✅ |
| 4-E | influberry / motivation（任意） | 未（Phase 6 前でも可） |
| 4-F | staging `DATABASE_URL` → `yadopera_staging` | ✅ |
| 4-G | 再 Deploy・health・**管理ログイン**（ブラウザ `/admin/dashboard`） | ✅ |

## 4.1 Postgres 上の DB 作成

```sql
CREATE DATABASE yadopera;
CREATE DATABASE yadopera_staging;
CREATE DATABASE influberry_staging;
CREATE DATABASE motivation_app;
-- 各 DB で
CREATE EXTENSION IF NOT EXISTS vector;
```

## 4.2 リストアコマンド例（ConoHa 上で実行・ナビ付き）

```bash
# 本番候補（ローカル docker）
gunzip -c yadopera_local_docker_*.sql.gz | psql -U ... -d yadopera

# staging（18pgvector・PG18）
pg_restore -U ... -d yadopera_staging --no-owner yadopera_18pgvector_*.dump

# influberry / motivation
pg_restore -U ... -d influberry_staging --no-owner influberry_influberry-staging_*.dump
pg_restore -U ... -d motivation_app --no-owner influberry_motivation_app_db_*.dump
```

ダンプファイルは [railway-dumps](file:///Users/kurinobu/Documents/yadopera-disaster-recovery-20260519/railway-dumps/) から SCP。

## 4.3 Dokploy の `DATABASE_URL` 更新

- staging → `yadopera_staging`
- production → `yadopera`

## 4.4 完了条件

- 施設数等の spot 確認（本番: 68 前後、staging: ダンプ内容と一致）
- staging でログイン・ゲスト導線の疎通

---

# Phase 5: YadOPERA サービス再開 ✅ 完了（2026-05-24）

**目安時間**: 2〜5 時間（実績: 2026-05-23〜24）  
**実施手順（正本）**: [20260521_Phase5_YadOPERAサービス再開_実施手順.md](./20260521_Phase5_YadOPERAサービス再開_実施手順.md)  
**証跡**: [20260524_conoha_phase5_service_resume.md](../evidence/20260524_conoha_phase5_service_resume.md)  
**作業報告**: [20260524_Phase5_サービス再開_作業報告.md](../reports/202605/20260524_Phase5_サービス再開_作業報告.md)

## 5.0 進捗（2026-05-24 完了）

| Step | 内容 | 状態 |
|------|------|------|
| 5-A | 事前確認 | ✅ |
| 5-B | staging サブドメイン + HTTPS | ✅ |
| 5-C | 本番 Backend / Frontend（`main` `2d8c43a`） | ✅ |
| 5-D | DNS `api` / `app` → ConoHa | ✅ |
| 5-E | Stripe Webhook → `api.yadopera.com` | ✅ |
| 5-F | 本番 VITE / CORS | ✅ |
| 5-G | 品質ゲート | ✅ |
| 5-H | 証跡・完了 | ✅ |

## 5.1 本番 URL（確定）

| 用途 | URL |
|------|-----|
| API | `https://api.yadopera.com` |
| App | `https://app.yadopera.com` |
| LP | `https://yadopera.com/`（GitHub Pages・無変更） |

## 5.2 外部連携（2026-05-24 実績）

| サービス | 作業 | 状態 |
|----------|------|------|
| **Stripe** | Webhook `charming-bliss` → `https://api.yadopera.com/api/v1/webhooks/stripe` | ✅ |
| **Brevo** | **Authorized IPs** に `160.251.199.237` 追加（401 障害復旧）・SPF/DKIM 維持 | ✅ |
| **OpenAI** | 既存キー流用 | ✅ |

## 5.3 品質ゲート（2026-05-24）

- [x] `/api/v1/health` 200
- [x] 管理画面ログイン（`info@yadobito.com`・やどびとホステル）
- [x] ゲスト `/f/68` 疎通
- [x] 証跡: [20260524_conoha_phase5_service_resume.md](../evidence/20260524_conoha_phase5_service_resume.md)

## 5.4 完了条件

- [x] 本番 URL でサービス利用可能
- [x] 重大課題（P0）解消・Stripe・DB クリーン再開（2026-05-24）
- [x] **YadOPERA サービス開始可能** — [移行完了証跡](../evidence/20260524_yadopera_conoha_migration_complete.md)
- [ ] 利用者へ障害・復旧の必要な連絡（Owner 判断・未記録）

## 5.5 Phase 5 完了後の重大課題（2026-05-24 発見 → 同日復旧）

**正本**: [20260524_Phase5完了後_本番公開状態_重大課題_発見記録.md](../reports/202605/20260524_Phase5完了後_本番公開状態_重大課題_発見記録.md)  
**復旧証跡**: [20260524_conoha_stripe_and_db_remediation.md](../evidence/20260524_conoha_stripe_and_db_remediation.md)

- ✅ DB 全削除・クリーン再開・本番/ステージング Stripe・`/admin/billing`（2026-05-24）
- ⏳ P0-5: 5-G 拡張チェックリストの文書化（任意）
- **Phase 6 へ進行可**（下記）

---

# Phase 6: InfluBerry・キャラまるわかり実装 ✅ 完了（2026-05-26）

**目安時間**: 3〜6 時間（2 アプリ × Dokploy・env・ビルド）  
**実施手順（正本）**: [20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md](./20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md)  
**完了証跡**: [20260525_phase6_influberry_partial.md](../evidence/20260525_phase6_influberry_partial.md)（InfluBerry 部分完了）／ [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md)（motivation_app 完了 + Phase 6 全体完了宣言）  
**事前調査**: [20260525_motivation_app_事前調査_調査分析報告書.md](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md)（2026-05-26 訂正版・C-1/C-2/C-3 / 誓約遵守記録）

## 6.0 進捗（2026-05-26 19:08 時点・全完了）

| Step | 内容 | 状態 |
|------|------|------|
| 6-A | 事前確認 | ✅ |
| 6-B | Phase 4-E リストア（InfluBerry / motivation_app・各 9 テーブル） | ✅ |
| 6-C | InfluBerry Dokploy（Dockerfile push `f6f8725` / Application / Provider / Build / Domain / Env） | ✅ |
| 6-E ステップ 1 | InfluBerry Deploy Done（29s）・Swarm 1/1 | ✅ |
| 6-E ステップ 2 | InfluBerry 疎通（Host: `staging-influberry.local` 偽装で 200 + title 取得・YadOPERA 全 200 維持） | ✅ |
| **6-D-0** | motivation_app 事前調査（C-1/C-2/C-3 発見・Owner 方針確定・調査報告書を 2026-05-26 訂正版に） | ✅ |
| **6-D-1** | Dockerfile 作成（Python 3.12.6-slim-bookworm・PORT 5002・gunicorn 1 worker / 4 threads / 120s） | ✅ |
| **6-D-3** | Mac から push — commit **`604aefa`**（full: `604aefa88851478911589aa5a449fe133d99e7fc`） | ✅ |
| **6-D-5** | Dokploy `motivation-app-staging` 作成（Swarm `airedison-motivationappstaging-rex1my`・Domain `staging-motivation.local` / Port 5002） | ✅ |
| **6-D-6** | Environment Settings **17 行** Save Successful（dotenv パーサー版テンプレ・C-3 のみ意図的未設定で Render 時代と同じ fallback 動作維持） | ✅ |
| **6-D-8** | Deploy Done・所要 **41 秒** | ✅ |
| **6-D-9** | 疎通確認 — Mac curl で YadOPERA `healthy` / app 200 / staging-app 200 / InfluBerry 200 + title / **motivation_app `Host: staging-motivation.local` で 200 + `<title>キャラまるわかり - 3つの心理学理論で自己診断</title>`** 取得（2026-05-26 19:07 実測） | ✅ |
| **6-D-10** | 証跡 [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md) 作成 | ✅ |
| 6-F | 証跡・Phase 6 完了チェックリスト・親引き継ぎ更新・事前調査報告書訂正履歴追記 | ✅ |

## 6.0.1 6-E ステップ 2 解消記録（2026-05-25 17:00 完了・InfluBerry）

Dokploy Domains 画面確認で `yadopera-frontend-staging` / `yadopera-frontend-production` が **`Host: 160.251.199.237`** を保持していたため、Traefik が YadOPERA Frontend を先勝ち配信していたことが判明。**YadOPERA Domains は一切触らず**、**InfluBerry 側のみ** Host を `staging-influberry.local`（外部 DNS 非登録の暫定 hostname）に変更し、Mac から `curl -H "Host: staging-influberry.local" http://160.251.199.237/` の **Host ヘッダ偽装** で InfluBerry に到達することを確認。詳細は [部分完了証跡 §2](../evidence/20260525_phase6_influberry_partial.md#2-6-e-ステップ-2-ブロッカー解消記録2026-05-25-1700-完了)。

## 6.0.2 motivation_app 6-D 完了記録（2026-05-26 19:07 完了）

InfluBerry と同流派の暫定 hostname 戦略を踏襲し、Dokploy Application `motivation-app-staging` の Domain を **`staging-motivation.local`**（Port 5002 / HTTP / Cert none）で Save。Provider GitHub `kurinobu/motivation_app` `main` Branch・Build Type Dockerfile・Build Path `/` で Deploy 実行 → **Done / 41 秒**。Mac から `curl -H "Host: staging-motivation.local" http://160.251.199.237/` で **200 + `<title>キャラまるわかり - 3つの心理学理論で自己診断</title>`** 取得・**YadOPERA / InfluBerry 全 200 維持**を同時確認。事前調査の訂正版（C-1/C-2/C-3 + 環境変数 A/B/C 分類）に基づき、Environment Settings は `python-dotenv==1.0.1` の `dotenv_values()` を使った **dotenv パーサー版テンプレ**で 17 行を生成・Dokploy 投入（bash grep + echo 方式の `# コメント` / クォート破損リスクを根本解決・大原則 1）。**C-3（`app.py:138` 管理者パスワード `'kurikuri'` コード固定）** のみ Owner 方針「Render と同じ状態で載せ替え」に従い `ADMIN_PASSWORD_HASH` を意図的未設定で起動。詳細は [motivation_app 完了証跡](../evidence/20260526_phase6_motivation_app_complete.md)。  
**Phase 7 申し送り**: `staging.influberry.jp` の DNS 確定後 `influberry-staging` Domain を切替＋ TLS letsencrypt・motivation_app 本ドメインも同様。**C-2 Brevo キー ローテーション**は GitHub `kurinobu/motivation_app` Visibility 確認後に Owner 判断（Public なら即時必須）・**C-3 管理者パスワード変更**は Phase 7+ Owner 判断。

## 6.1 対象

| サービス | Mac パス | GitHub | DB | Dokploy Application |
|----------|----------|--------|-----|--------------------|
| InfluBerry | `/Users/kurinobu/projects/influberry_v2` | `kurinobu/influberry` | **`influberry_staging`**（4-B 作成済・4-E 済・Phase 6 完了） | `influberry-staging`（Swarm `airedison-influberrystaging-qqn2hl`・Domain `staging-influberry.local` Port 5001） |
| キャラまるわかり | `/Users/kurinobu/motivation_app` | `kurinobu/motivation_app` | **`motivation_app`**（4-B 作成済・4-E 済・Phase 6 完了） | `motivation-app-staging`（Swarm `airedison-motivationappstaging-rex1my`・Domain `staging-motivation.local` Port 5002） |

## 6.2 作業（実績）

1. [x] Phase 4-E リストア（InfluBerry / motivation_app 各 9 テーブル）
2. [x] Dockerfile 等ビルド方針確定（**両リポジトリに新規 Dockerfile push** — InfluBerry `f6f8725` / motivation_app `604aefa`）
3. [x] Dokploy Application 追加・`DATABASE_URL` Internal 向け
4. [x] Deploy・暫定 hostname 疎通（DNS 本ドメイン化は **Phase 7**）

## 6.3 完了条件（達成）

- [x] 両アプリ **Deploy Done**・DB 接続エラーなし（ログ・疎通で確認）
- [x] Phase 6 証跡・チェックリスト `[x]`
- [x] 親引き継ぎ Phase 6 ✅ 化

**Phase 6 に含めなかった（Phase 7+ 対象）**:
- `influberry.jp` / `staging.influberry.jp` / motivation_app 本ドメイン等の **DNS 切替**（Phase 7）
- TLS letsencrypt 化（Phase 7）
- C-1 / C-2 / **C-3** のコード修正（Phase 7+ Owner 判断）
- Brevo API キー ローテーション（Phase 7 着手前推奨）
- GitHub `kurinobu/motivation_app` Visibility 確認（Phase 7 着手前必須）
- 管理者パスワード `'kurikuri'` の変更（Phase 7+ Owner 判断）
- Render 解約（Phase 8）

---

---

# サービス再開 三本柱 ✅ 完了（2026-05-29）

**正本**: [20260529_サービス再開_三本柱_実施計画.md](./20260529_サービス再開_三本柱_実施計画.md)  
**全 URL 疎通記録**: [20260529_all_services_browser_path_check.md](../evidence/20260529_all_services_browser_path_check.md)  
**再検証スクリプト**: [`scripts/check_service_resumption_all.sh`](./scripts/check_service_resumption_all.sh)

| 順 | 計画書 | 状態 |
|----|--------|------|
| ① | [YadOPERA サービス再開](./20260529_YadOPERA_サービス再開_計画.md) | ✅ [証跡](../evidence/20260529_yadopera_service_resumption_complete.md) |
| ② | [InfluBerry 本番 + 再開](./20260529_InfluBerry_本番載せ替え_サービス再開_計画.md) | ✅ [証跡](../evidence/20260529_influberry_prod_service_resumption_complete.md) |
| ③ | [キャラまるわかり 本番 + 再開](./20260529_キャラまるわかり_本番載せ替え_サービス再開_計画.md) | ✅ [証跡](../evidence/20260529_motivation_prod_service_resumption_complete.md) |

**任意残**: `www.influberry.jp` / `www.olovolo.online`（ルート URL で運用中）

---

# Phase 7: DNS 本ドメイン化・HTTPS 化（InfluBerry / キャラまるわかり） ✅ staging 完了（2026-05-29）

**目安時間**: 1〜3 時間（DNS 反映待ちを含めると半日〜1 日）  
**前提**: Phase 6 完了  
**実施手順（正本）**: [20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md](./20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md)  
**完了証跡**: [20260529_phase7_dns_complete.md](../evidence/20260529_phase7_dns_complete.md)

## 7.0 完了サマリ（2026-05-29）

| 区分 | URL | 状態 |
|------|-----|------|
| staging InfluBerry | `https://staging.influberry.jp/` | HTTPS 200 ✅ |
| staging motivation_app | `https://staging.olovolo.online/` | HTTPS 200 ✅ |
| **本番** InfluBerry | `influberry.jp` | ⏳ A = `216.24.57.1`（未切替） |
| **本番** motivation_app | `olovolo.online` | ⏳ A = `216.24.57.1`（未切替） |
| YadOPERA | api/app / staging | 無影響 ✅ |

**C-2 / C-3**: Owner 判断で据え置き（後日対応可）。

## 7.1 Phase 7 実施項目（手順書 §3 実施順序）

- [x] 7-0 安全復帰ゲート（責務マトリクス承認・YadOPERA 凍結ルール確認）
- [x] 7-A Owner 確認（7-P1〜7-P6）→ 手順書 §11 に Owner 記入
- [x] 7-B DNS 現状記録 + 事前ベースライン curl
- [x] 7-C C-2 / C-3 ローテーション判断（据え置き）
- [x] 7-D InfluBerry Dokploy Domains 切替（`staging.influberry.jp`）
- [x] 7-E motivation_app Dokploy Domains 切替（`staging.olovolo.online`）
- [x] 7-F TLS letsencrypt 発行確認
- [x] 7-G staging 本ドメインで HTTPS 疎通確認（全 7 行 OK）
- [x] 7-H 完了証跡 [20260529_phase7_dns_complete.md](../evidence/20260529_phase7_dns_complete.md) 作成・親引き継ぎ Phase 7 ✅ 化

## 7.2 本番載せ替え + サービス再開（②③ — ① 完了後）

| 順 | 計画書 |
|----|--------|
| ② InfluBerry | [20260529_InfluBerry_本番載せ替え_サービス再開_計画.md](./20260529_InfluBerry_本番載せ替え_サービス再開_計画.md) |
| ③ キャラまるわかり | [20260529_キャラまるわかり_本番載せ替え_サービス再開_計画.md](./20260529_キャラまるわかり_本番載せ替え_サービス再開_計画.md) |

着手条件: [① YadOPERA サービス再開](./20260529_YadOPERA_サービス再開_計画.md) 完了 → ② → ③（順序固定）

## 7.3 Phase 7 で触らなかった（凍結遵守）

- YadOPERA api/app の Dokploy env／Stripe Webhook／既存 Brevo Authorized IPs（流用するが新規追加なし）
- influberry-staging / motivation-app-staging の Environment Settings（**DNS / Domain のみ変更**・他 env は変更しない）
- C-1（旧 Render DB ハードコード）のコード修正（Phase 8 解約で自動消滅）
- C-2 / C-3 のコード fail-fast 化（別 PR・別 Phase）
- Render 解約（Phase 8）

## 7.4 Phase 7 失敗時のロールバック（参考・完了済）

万一 7-D / 7-E で本ドメイン化失敗または letsencrypt 発行不可の場合、Dokploy Domains を暫定 hostname に戻す（Phase 6 完了状態に復帰）。YadOPERA は触っていないため影響なし。

---

# Phase 8: Render 解約・Railway クローズアウト ✅ 完了（2026-05-27）

**目安時間**: 主要作業 0.5〜1 時間（実績 30〜45 分・2026-05-27）／カード削除は別途各社請求サイクル後  
**実施手順（正本）**: [20260527_Phase8_Render_Railway_解約_実施手順.md](./20260527_Phase8_Render_Railway_解約_実施手順.md)  
**部分完了証跡**: [20260527_phase8_render_railway_partial.md](../evidence/20260527_phase8_render_railway_partial.md)  
**Owner 方針**: **Phase 7（DNS 本ドメイン化）に先行して Phase 8 を実施・コスト即時停止優先・Free 化（Hobby 化）でワークスペースは残置**（過去請求書閲覧用）

## 8.0 進捗（2026-05-27）

| Step | 内容 | 状態 |
|------|------|------|
| 8-A | Render Pro → Hobby（Free 相当）Downgrade | ✅（2026-05-27） |
| 8-D-R1 | ローカルダンプ存在確認（5 ファイル必須） | ✅ |
| 8-D-R2 | Railway 全プロジェクト削除（soothing-acceptance / yadopera-postgres-staging / supportive-surprise） | ✅（48h ソフト削除中） |
| 8-D-R3 | Railway Hobby Plan Cancel（Final $0.00 確定） | ✅ |
| 8-B | Render カード削除（5月分 $102.35 Paid 確認後・6/3 以降） | 🔜 |
| 8-D-R4 | Railway カード削除（Free 落ち確認後・6/21 以降） | 🔜 |
| 8-Z | Phase 8 完全完了証跡更新 | 🔜（カード削除完了後） |

## 8.1 確定金額・スケジュール

| 月 | Render | Railway | 合計 | 備考 |
|----|--------|---------|------|------|
| 2026-05 | **$102.35**（Services $94.08 + Datastores $8.27・Team Members $19 は遡及除外）／**6/1〜6/3 のいずれかに JCB 4178 へ自動課金予定** | $5.00（5/20 既払・以降ゼロ） | $107.35 | Render 全削除済・Railway クローズ操作日 |
| 2026-06 以降 | **$0** | **$0**（6/20 で完全停止 → 6/21 以降 Free 落ち） | **$0** | Phase 8 効果開始・**永久ゼロ** |

## 8.2 完了確認の作業フロー（残）

1. **2026-06-01〜06-03 頃**: Render `Billing → Invoice History` で「May 2026 / Paid / $102.35」確認
2. **2026-06-03〜06-05 頃**: Render `Billing → Payment Method` でカード `Edit payment details → Remove`
3. **2026-06-21 以降**: Railway `https://railway.com/workspace/plans` で Plan が Free / Trial 切替確認
4. **2026-06-21 以降**: Railway カード削除（`Replace` 経由）
5. **完全完了後**: 部分完了証跡を最終版へ更新・親引き継ぎ Phase 8 ✅ 化

## 8.3 触っていないこと（運用無影響）

- ConoHa VPS（`160.251.199.237`）の Dokploy 設定・Postgres・Redis（YadOPERA / InfluBerry / motivation_app 全て稼働継続）
- `api.yadopera.com` / `app.yadopera.com` / `staging-app.yadopera.com` の DNS・Stripe Webhook・Brevo Authorized IPs
- InfluBerry / motivation_app の Dokploy `Domain` 設定（Phase 6 暫定 `*.local`・Phase 7 で本ドメイン化予定）
- ローカル `~/Documents/yadopera-disaster-recovery-20260519/railway-dumps/` ダンプファイル群（無変更・残置）
- 各リポジトリのコード（YadOPERA / InfluBerry / motivation_app すべて無変更）

## 8.4 Phase 7 復帰時の前提更新

- C-1（旧 Render DB ハードコード `motivation_app/app.py:50-52`）: **Render DB 削除済 + Render プラン Hobby 化済 → 接続不可・実質的な脅威消滅**（Workspace 残置中も DB 復元は不可）
- C-2 / C-3: Phase 7+ で Owner 判断（変化なし）

→ Phase 7 着手前 Owner 確認（7-P1〜7-P6）の判断材料に **C-1 は Phase 8 で実質処理済** を反映。

---

# 運用インシデント: Dokploy Auto Deploy 不発（2026-05-31）

**正本証跡**: [20260531_dokploy_autodeploy_security_group_remediation.md](../evidence/20260531_dokploy_autodeploy_security_group_remediation.md)  
**作業報告**: [20260531_会話詳細404とDokploy_AutoDeploy_SG復旧_作業報告.md](../reports/202605/20260531_会話詳細404とDokploy_AutoDeploy_SG復旧_作業報告.md)

## 概要（2 件）

| # | 事象 | 原因 | 復旧 |
|---|------|------|------|
| A | 本番 管理画面 会話詳細 404 | ゲスト API + JWT 施設不一致（コード） | `5f46809` / `f82ea19` デプロイ |
| B | git push 後 Dokploy 未更新 | ConoHa SG `air-edison-admin-3000` が port **3000** を自宅 IP のみ許可 → GitHub Webhook **`failed to connect to host`** | SG に GitHub `hooks` CIDR 4 件追加 + Redeliver |

## B の要点（インフラ・全 App 共通）

| 項目 | 値 |
|------|-----|
| 誤解しやすい点 | Autodeploy **ON**・`health` **200** でも **コード未反映**になりうる |
| Webhook URL | `http://160.251.199.237:3000/api/deploy/github`（正しいが GitHub から到達不可だった） |
| SG 修正前 | `113.153.22.54/32` のみ（port 3000 In） |
| SG 修正 | 上記に加え `192.30.252.0/22` 等 **4 CIDR**（[Phase2 Step 0.2](./20260521_Phase2_ConoHa初期設定_実施手順.md#02-ポート-3000-用の独自セキュリティグループを作る)） |
| 確認 | GitHub Advanced → Redeliver **緑チェック** → Deployments に `f82ea19` |

## 他 Application

InfluBerry / motivation_app 等も **同一 SG・同一 GitHub App** のため、SG 修正前の push は Auto Deploy されていない可能性あり。**Deployments commit と Git 先端を突合**し、ずれていれば Deploy。

---

# Phase 9: PublishDone 実装開始

**目安時間**: 着手 **2〜4 時間**（リポジトリ・Dokploy プロジェクト追加まで）。MVP 全体は **数週間〜**（別計画）

- 同一 ConoHa 12GB に **FastAPI API** を追加（別 VPS 不要）
- 定義: [publishdone_v0_172.md](file:///Users/kurinobu/projects/PublishDone/publishdone_v0_172.md)
- YadOPERA 本番安定後に着手（初期整備パック営業と並行可）

---

## 次会話の開始プロンプト例

**推奨（次会話）**: Phase 8 カード削除（[Phase 8 手順](./20260527_Phase8_Render_Railway_解約_実施手順.md)）または Phase 9 PublishDone。全 URL 再確認は [`check_service_resumption_all.sh`](./scripts/check_service_resumption_all.sh)。

**済**: Phase 2〜6 [実施手順](./20260521_Phase2_ConoHa初期設定_実施手順.md) / [Phase3](./20260521_Phase3_YadOPERAデプロイ準備_実施手順.md) / [Phase4](./20260521_Phase4_DBリストア_実施手順.md) / [Phase5](./20260521_Phase5_YadOPERAサービス再開_実施手順.md) / [Phase6](./20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md)

---

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-05-21 | 初版（Phase 0 完了反映・引き継ぎ用） |
| 2026-05-21 | 各 Phase の目安時間・合計イメージを追加 |
| 2026-05-21 | Phase 1 完了反映（IP・IPv4v6-SSH・Ubuntu 22.04.3 確認） |
| 2026-05-21 | Phase 2 §2.0 追加（事前調査不要・スコープ外・80/443・開始プロンプト） |
| 2026-05-21 | Phase 2 開始・[実施手順](./20260521_Phase2_ConoHa初期設定_実施手順.md)・`phase2_verify.sh` 追加 |
| 2026-05-21 | §2.0 追記: セキュリティグループは VPS 共通・1 台集約・命名はアプリ名を入れない |
| 2026-05-21 | 誤名グループのリネームは必須と明記（§2.0・Phase2 Step 0.4） |
| 2026-05-21 | セキュリティグループ正本名を **`air-edison-admin-3000`**（ネームタグ準拠）に確定 |
| 2026-05-21 | Phase2 実施手順に本セッションの事実・ナビ誤り記録を追加 |
| 2026-05-21 | Phase 2 完了（Dokploy・PG18+vector・Redis PONG） |
| 2026-05-21 | Phase 3 引き継ぎ [実施手順](./20260521_Phase3_YadOPERAデプロイ準備_実施手順.md)・次会話プロンプト更新 |
| 2026-05-21 | Phase 3 **Step 1 完了**（Backend staging・health 200）— Step 2 へ。Phase 3 全体は未完了 |
| 2026-05-22 | Phase 3 **完了**（Frontend・管理ログイン UI・Step 4 確認） |
| 2026-05-22 | [Phase4 DB リストア 実施手順](./20260521_Phase4_DBリストア_実施手順.md) 追加・次会話正本を Phase 4 に |
| 2026-05-23 | Phase 4 完了・[Phase5 サービス再開 実施手順](./20260521_Phase5_YadOPERAサービス再開_実施手順.md) 追加・次会話正本を Phase 5 に |
| 2026-05-24 | **Phase 5 完了** — 本番 `api`/`app`・Stripe Webhook・Brevo IP 許可・5-G ログイン・[証跡](../evidence/20260524_conoha_phase5_service_resume.md) |
| 2026-05-24 | [Phase6 InfluBerry・キャラまるわかり 実施手順](./20260521_Phase6_InfluBerry_キャラまるわかり_実施手順.md) 追加・次会話正本を Phase 6 に |
| 2026-05-25 | Phase 6 部分完了：6-A〜6-E ステップ 1（InfluBerry Deploy Done）／6-E ステップ 2 ブロッカー記録（[部分完了証跡](../evidence/20260525_phase6_influberry_partial.md)） |
| 2026-05-25 17:02 | Phase 6 **InfluBerry 完了**（6-E ステップ 2 解消・`staging-influberry.local` 経由で疎通確認・YadOPERA 全 200 維持／詳細は [部分完了証跡 §2.4〜2.6](../evidence/20260525_phase6_influberry_partial.md#24-解消後の実測2026-05-25-1700mac)）・次は **6-D（motivation_app）** |
| 2026-05-25 17:32 | Phase 6 6-D 事前調査完了・[調査分析報告書](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md) 作成。C-1（app.py:52 旧 Render DB ハードコード）・C-2（services.py Brevo キー ハードコード）を発見。Owner 方針「Render と同じ状態で載せ替え／コード修正なし／問題は証跡」確定。 |
| 2026-05-26 19:10 | **Phase 6 全体完了**：motivation_app Deploy Done（commit `604aefa`・41 秒）・疎通 200 + `<title>キャラまるわかり - 3つの心理学理論で自己診断</title>` 取得・YadOPERA / InfluBerry 全 200 維持。事前調査報告書を 2026-05-26 訂正版に更新（M-1〜M-4 誓約遵守記録・**C-3 app.py:138 管理者パスワード 'kurikuri' コード固定**を新規発見として追加）。6-D-6 のテンプレを **dotenv パーサー版**に置換（大原則 1 根本解決）。証跡 [20260526_phase6_motivation_app_complete.md](../evidence/20260526_phase6_motivation_app_complete.md) を新規作成。**Phase 7（DNS 切替・HTTPS 化）次会話プロンプト**を冒頭に提示。 |
| 2026-05-26 19:25 | **Phase 7 専用手順書**を新規作成 — [20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md](./20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md)。7-A 着手前 Owner 確認（7-P1〜7-P6）・7-B〜7-H Step・§11 Owner 記入欄・§12 完了チェックリスト・誓約継承を明記。本書を Phase 7 手順書リンクで強化、§Phase 7 セクションを手順書参照型に更新。索引文書 3 件（`docs/Summary/yadopera-v04-summary.md` を v4.1.1 / `docs/README.md` を v1.5 / `docs/maintenance/README.md`）を Phase 6 完了 + Phase 7 手順書追加で更新。 |
| 2026-05-27 09:44 | **Phase 8 主要作業完了**（Phase 7 に先行実施・Owner 方針）。Render Pro → Hobby（Free 相当）Downgrade で 6 月以降課金ゼロ確定・5月分 Final **$102.35**（Team Members $19 遡及除外）。Railway 全プロジェクト 3 件削除（48h ソフト削除）+ Hobby Plan Cancel で Final **$0.00**・6/20 で完全停止 → 6/21 以降 Free 落ち。**Phase 8 専用手順書**を新規作成 — [20260527_Phase8_Render_Railway_解約_実施手順.md](./20260527_Phase8_Render_Railway_解約_実施手順.md)。**部分完了証跡**を新規作成 — [20260527_phase8_render_railway_partial.md](../evidence/20260527_phase8_render_railway_partial.md)。残作業はカード削除のみ（Render 6/3 以降・Railway 6/21 以降）。本書 §Phase 8 を手順書参照型 + 進捗表 + 確定金額表に更新・ロードマップ 8 行を 🟡 主要作業完了に変更・C-1 脅威消滅を Phase 7 復帰前提に追記。 |
| 2026-05-29 | **サービス再開 三本柱** 正本 [20260529_サービス再開_三本柱_実施計画.md](./20260529_サービス再開_三本柱_実施計画.md) 新設。① YadOPERA / ② InfluBerry / ③ キャラまるわかりを分離。順序 ①→②→③ 固定。Phase 5/6 の「完了」をインフラ層とサービス再開で訂正。[認識訂正 調査報告](../reports/202605/20260529_サービス再開_認識訂正_調査報告.md)。 |
| 2026-05-29 | **三本柱 ①②③ 完了**・[全サービス疎通証跡](../evidence/20260529_all_services_browser_path_check.md)・[`check_service_resumption_all.sh`](./scripts/check_service_resumption_all.sh)。引き継ぎの「次会話 ①」表記を完了に更新。 |
| 2026-05-31 | **運用インシデント** — 会話詳細 admin API 修正（`f82ea19`）+ Dokploy Auto Deploy 不発（ConoHa SG `air-edison-admin-3000` に GitHub hooks CIDR 追加で復旧）。[証跡](../evidence/20260531_dokploy_autodeploy_security_group_remediation.md)・[作業報告](../reports/202605/20260531_会話詳細404とDokploy_AutoDeploy_SG復旧_作業報告.md)・[Phase2 Step 0.2 追記](./20260521_Phase2_ConoHa初期設定_実施手順.md#02-ポート-3000-用の独自セキュリティグループを作る)。 |
