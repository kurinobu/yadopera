# やどぺら v4 要約定義書（サービス開始時点）

**作成日**: 2026年4月22日  
**最終更新日**: 2026年5月26日  
**バージョン**: v4.1.1  
**ステータス**: 現行正本（ConoHa 本番運用・サービス開始可能・**Phase 6 完了**）  
**旧版**: `docs/Summary/yadopera-v03-summary.md`（履歴として保持）

---

## 0. 文書の位置づけ（正本ルール）

本書は、やどぺらの「目的・経緯・現在地点・大原則・運用実態」を統合した最新版要約定義書である。

- 仕様の基準: 本書（v4）
- アーキテクチャ詳細の基準: `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`（§14.0 に **ConoHa 現行運用** を追記）
- インフラ移行の証跡: `docs/evidence/20260524_yadopera_conoha_migration_complete.md`
- サービス開始時系列の基準: `docs/20260415_サービス開始ロードマップ.md` と `docs/20260328_サービス開始ロードマップ_実行記録.md`（**ホスティング記述は本書・証跡を優先**）
- 実行証跡の基準: `docs/evidence/`

以後、旧文書に Render 前提の記述が残る場合は **履歴** とし、現行運用は本書および ConoHa 移行証跡を優先する。

---

## 1. 目的

やどぺら（YadOPERA）は、小規模宿泊施設向けの外国人ゲスト対応自動化SaaSである。  
QR導線でゲストが多言語質問を行い、施設側は管理画面でFAQ・運用・請求を管理する。  
開発目的は、宿泊現場の問い合わせ対応負荷を下げつつ、ホスピタリティ品質を維持した運営を実現することにある。

---

## 2. 経緯（サービス開始まで）

- Phase 0〜2で基盤機能（認証、FAQ、チャット、管理画面、開発者運用基盤）を構築。
- Phase 3で実運用に基づく改善（多言語、管理導線、LP改善、FAQ運用改善）を継続。
- Phase 4でStripe課金・請求機能を段階実装し、ステージング検証を完走。
- 2026-03末〜2026-04中旬でサービス開始ロードマップ（A〜F）を完了し、Go判定後に本番運用へ移行（当時ホスト: **Render**）。

### 2.1 インフラ移行（2026-05・ConoHa）

| 時期 | 内容 |
|------|------|
| 2026-05-19 頃 | Render 障害。本番 DB 復旧不可。手元・Railway ダンプで退避 |
| 2026-05-21〜23 | ConoHa VPS 契約・Dokploy・YadOPERA デプロイ準備・DB リストア（Phase 0〜4） |
| 2026-05-24 | DNS 切替・本番/ステージング公開（Phase 5）。同日、テストデータ公開等の重大課題を解消（DB 全削除・Stripe 設定） |
| 以降 | **SaaS 本体の正本ホストは ConoHa VPS**。Render 解約は移行計画 Phase 8（未実施） |

詳細: [ConoHa VPS 移転統合 引き継ぎ](../maintenance/20260521_ConoHaVPS_移転統合_引き継ぎ.md)・[移行完了証跡](../evidence/20260524_yadopera_conoha_migration_complete.md)

---

## 3. 現在地点（2026-05-24）

### 3.1 サービス状態

- **本番・ステージングとも ConoHa 上で稼働中。サービス開始（新規施設の受け入れ）に問題なし**（Owner 確認: 登録・ログイン・プラン・請求画面）。
- 2026-05-24 に本番 DB を **バックアップ後に全削除**し、クリーンな状態から再開（旧 Render リストアに含まれていたテスト施設 69 件等は解消）。
- エスカレーション改善トラックは A〜D を本番反映・実動確認済み。E（体験完成度向上）は残存課題として継続管理。

### 3.2 公開 URL（確定）

| 用途 | URL |
|------|-----|
| 本番 App | `https://app.yadopera.com` |
| 本番 API | `https://api.yadopera.com` |
| ステージング App | `https://staging-app.yadopera.com` |
| ステージング API | `https://staging-api.yadopera.com` |
| LP | `https://yadopera.com/`（GitHub Pages） |
| 管理・請求 | `https://app.yadopera.com/admin/billing`（**Stripe ダッシュボードではない**） |

### 3.3 Git / ブランチ運用の現況

- 基本戦略: `feature/* -> develop -> main`
- LP本番公開は `main` の `landing/**` が唯一の配信ソース（GitHub Pages）。
- コード変更のデプロイ: **Dokploy が GitHub 連携でビルド・Deploy**（VPS 上。`render.yaml` は **レガシー**参照用にリポジトリに残存しうる）。

### 3.4 配信・デプロイ運用の現況（As-Is）

| コンポーネント | ホスト | 備考 |
|----------------|--------|------|
| 本番 Backend / Frontend | **ConoHa VPS + Dokploy** | Project `air-edison` / Env `production` |
| ステージング Backend / Frontend | **同上** | DB 名 `yadopera_staging` |
| PostgreSQL / Redis | **VPS 上 Swarm** | pgvector・Internal URL |
| LP | **GitHub Pages** | 変更なし |
| CI | `staging-deploy.yml` | `develop` 向け pytest（**デプロイ先は Dokploy ステージング**） |
| ~~Render~~ | **DNS 切替済み・解約は Phase 8** | 2026-03〜04 までの本番ホスト（履歴） |

**VPS IP**: `160.251.199.237`  
**Dokploy**: `http://160.251.199.237:3000`

### 3.5 外部連携（本番）

| サービス | 状態（2026-05-24） |
|----------|-------------------|
| Stripe Live | Webhook `charming-bliss` → 本番 API・Dokploy `STRIPE_*` 設定済 |
| Stripe Test | Webhook `conoha-staging-api` → ステージング API |
| Brevo | Authorized IPs に VPS IP 追加済み |
| OpenAI | 既存キー流用 |

---

## 4. 大原則（継続拘束）

以下を実装・運用の共通原則として固定する。

1. 根本解決 > 暫定解決
2. シンプル構造 > 複雑構造
3. 統一・同一化 > 特殊独自
4. 具体的 > 一般
5. 安全確実 > 拙速
6. Docker環境必須
7. LP本番公開は `main` + GitHub Pages（Vercel不使用）
8. 品質ゲートと証跡を満たさない本番操作は行わない

---

## 5. 現行アーキテクチャ（As-Is要約）

### 5.1 システム構成

- Frontend: Vue 3 + TypeScript + Vite + PWA
- Backend: FastAPI + SQLAlchemy + Alembic
- Database: PostgreSQL（pgvector）— **VPS 上 1 インスタンス、DB 名で本番/ステージング分離**
- Cache/Session: Redis — **VPS 上**
- 外部連携: OpenAI, Stripe, Brevo

### 5.2 主要導線

- ゲスト導線: `/f/:facilityId` 系（welcome/chat）
- 管理導線: `/admin/*`（FAQ、CSV、請求、設定、マニュアル、サポート）
- 開発者導線: `/developer/*`（統計、障害ログ、ヘルス）

### 5.3 実装上の重要現況

- Backend APIルーターに guest/admin/developer/webhook が統合済み。
- 課金ロジックは `create_subscription` / `update_subscription_price` の両方で税率設定を明示。
- `ENVIRONMENT=production` では `GET /__debug_env` を無効化。
- Stripe 設定判定: `is_stripe_configured()` = `bool(stripe_secret_key)` → 未設定時は管理画面に「Stripe 未設定」。

---

## 6. サービス開始ロードマップの評価（計画 vs 実績）

- A1/A2（税率反映・コード経路確認）: 完了
- B1/B2（品質ゲート・ステージング6.5）: 完了
- B3（本番導線）: 実課金リスクに対する許容例外を記録して完了扱い
- C0/C1（本番インフラ設計・本番起動）: 完了（**2026-04 Render → 2026-05 ConoHa へ移行完了**）
- D（Stripe本番）: 完了（ConoHa 本番で再設定済み 2026-05-24）
- E（カットオーバー）: 完了（Go）
- F（LP公開）: 完了（`https://yadopera.com/`）

---

## 7. 直近の運用課題（開始後フェーズ）

### 7.1 優先度高

- 請求書・領収書の表示運用（インボイス整合、税表示確認）の継続精査
- 証跡文書と運用手順文書の整合維持（**Render 記述の残置は履歴扱い**）
- エスカレーション改善 E（体験完成度向上）の段階実施

### 7.1.1 移行計画上の残（YadOPERA 本体以外）

- ~~Phase 6: InfluBerry・キャラまるわかり（ConoHa デプロイ）~~ ✅ **完了**（2026-05-26・[完了証跡](../evidence/20260526_phase6_motivation_app_complete.md)）
- Phase 7: InfluBerry / motivation_app の DNS 本ドメイン化・HTTPS 化（[実施手順](../maintenance/20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md)）
- Phase 8: Render 解約

**Phase 7 着手前 Owner 必須確認**（[Phase 7 §9](../maintenance/20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md#9-phase-7-着手前-owner-必須確認7-p1-7-p6)）:
- GitHub `kurinobu/motivation_app` / `kurinobu/influberry` の Visibility（Public なら C-2 Brevo キー / C-3 管理者パスワード `'kurikuri'` の即時ローテーション必須）
- ムームードメイン現状（`influberry.jp` 系・motivation_app 本ドメイン所有有無）
- Brevo Authorized IPs（`160.251.199.237` は YadOPERA Phase 5 で追加済・流用可）

**Phase 6 完了で確認されたハードコード機密情報**（[事前調査報告書](../reports/202605/20260525_motivation_app_事前調査_調査分析報告書.md) §0.3 / §4）:
- C-1: `motivation_app/app.py:50-52` 旧 Render DB URL ハードコード（Phase 8 解約で自動消滅）
- C-2: `motivation_app/blueprints/mail/services.py:457,554` Brevo API キー ハードコード（Phase 7 着手前要対応・Public なら必須）
- C-3: `motivation_app/app.py:138` 管理者パスワード `'kurikuri'` コード固定（Phase 7 で Dokploy Env 化または別 PR）

### 7.2 優先度中

- LPのコンバージョン改善（AB改善、計測運用）
- 運営・法務ページの継続改修
- 利用者向け障害・復旧連絡（Owner 判断）

---

## 8. リリース・運用規律（固定）

- 変更は `develop` で検証後、`main` へ昇格。
- LP公開判定は `main` 反映と公開URL確認までを1セットで完了判定する。
- 重要変更は `docs/evidence/` に証跡を残し、関連ロードマップへ相互参照を記載する。
- 本番操作は秘密情報を文書に平文記録しない。
- **本番デプロイ**: Dokploy で Save → Deploy（環境変数変更時も再デプロイ）。

---

## 9. 参照ドキュメント（v4策定根拠）

- `docs/Summary/yadopera-v03-summary.md`
- `docs/Architecture/やどぺら_v0.3_アーキテクチャ設計書.md`
- `docs/maintenance/20260521_ConoHaVPS_移転統合_引き継ぎ.md`
- `docs/evidence/20260524_yadopera_conoha_migration_complete.md`
- `docs/evidence/20260524_conoha_phase5_service_resume.md`
- `docs/evidence/20260524_conoha_stripe_and_db_remediation.md`
- `docs/20260307_プロジェクト現況と今後の計画_総括.md`
- `docs/20260415_サービス開始ロードマップ.md`
- `docs/20260328_サービス開始ロードマップ_実行記録.md`
- `docs/サービス開始までの手順_Runbook.md`（**冒頭に現行ホスト注記**）

---

## 10. v4 変更履歴

### v4.1.1（2026-05-26）

- **Phase 6（InfluBerry・キャラまるわかり）完了**を §7.1.1 に反映（ConoHa Dokploy デプロイ完了・暫定 hostname で疎通確認済）。
- Phase 7 専用手順書 `docs/maintenance/20260526_Phase7_DNS本ドメイン_HTTPS化_実施手順.md` を新設し相互参照。
- §7.1.1 に **C-1 / C-2 / C-3 ハードコード機密情報の Phase 7 着手前申し送り**を明記（YadOPERA 本体には影響なし・motivation_app 側の Phase 7+ 課題）。

### v4.1.0（2026-05-24）

- **ConoHa VPS 本番移行完了**を反映（Render は履歴・Phase 8 で解約予定）。
- 公開 URL・Dokploy・Stripe/Brevo・DB クリーン再開の現況を §2.1・§3 に追記。
- 移行完了証跡への相互参照を追加。

### v4.0.0（2026-04-22）

- `v0.3` 系の仕様要約を、サービス開始後の実運用状態に合わせて再定義。
- ロードマップ（A〜F）完了結果を反映し、現時点を「開始後運用フェーズ」として明文化。
- ブランチ戦略、CI/CD、LP公開経路、証跡運用ルールを現況に合わせて統合。
- 旧版要約定義書を履歴として保持し、本書を現行正本へ昇格。
