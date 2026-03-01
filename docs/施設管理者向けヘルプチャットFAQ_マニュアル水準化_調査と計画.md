# 施設管理者向けヘルプチャットFAQ マニュアル水準化 — 調査分析と実施計画

**作成日**: 2026年3月1日  
**目的**: 要約定義書・アーキテクチャ設計書・Phase3計画書等を踏まえ、施設管理者向けヘルプチャットボットのFAQが「マニュアルレベル」に足りない現状を整理し、マニュアルと同等の網羅性・正確性に仕上げるための**方法**と**計画**を提示する。  
**前提**: マニュアルは実装機能・表示をほぼ網羅しているが、ヘルプチャットのFAQは項目数・内容ともに不足している。**指示があるまで実行しない。**

---

## 0. 目的・全体像・経緯・現況・大原則（参照）

### 0.1 目的・全体像

| 項目 | 内容 |
|------|------|
| **事業** | やどぺら = 小規模宿泊施設向け外国人ゲスト対応自動化SaaS。QRコードでAIが24時間多言語自動応答。 |
| **ヘルプの位置づけ** | Phase 2（PoC準備）で「宿泊事業者向けFAQ＋AIヘルプチャット」を実装。管理画面内フローティングチャットで、事業者向けFAQを参照して回答。サポート工数70%削減目標。 |
| **マニュアル** | 利用マニュアル（`/admin/manual`）は全**13章**・約**55以上の節**で、操作手順・機能説明・トラブルシューティングを網羅。実装している機能や表示に対してほぼ全て補完している。 |
| **ヘルプFAQの現状** | **30項目・8カテゴリ**のみ。マニュアルに比べて項目数が少なく、一部は古い記述・存在しない機能・誤ったリンクを含む。 |

### 0.2 経緯

- 要約定義書付録C: 宿泊事業者向けFAQテンプレート30項目（初期設定・QR・FAQ管理・AI・ログ・トラブル・料金・セキュリティ）を定義。
- 2026-01-18: FAQ全30項目修正・デプロイ後FAQ自動更新機能実装。
- 2026-01-20: 「統合ヘルプシステムFAQ精査」で**12項目に問題**を特定（誤記・存在しない機能・リンク404・マニュアルとの不整合）。修正案・修正計画を提示済み。**指示があるまで修正しない**と記載。
- マニュアルはその後も拡張（リードゲット・プラン・請求など）されており、FAQ側はその追従が十分でない。

### 0.3 現況（コード・データ）

| 項目 | 内容 |
|------|------|
| **FAQデータソース** | `backend/scripts/insert_operator_faqs.py` の `OPERATOR_FAQ_DATA`。定義書: `docs/help_system_faq_data.md`。 |
| **DB** | `operator_faqs`（id, category, intent_key, display_order, is_active 等）、`operator_faq_translations`（faq_id, language, question, answer, keywords, related_url）。マイグレーション 011。 |
| **API** | `GET /api/v1/help/faqs`（一覧）、`GET /api/v1/help/search?q=`（検索）、`POST /api/v1/help/chat`（AIチャット）。認証必須。 |
| **チャット動作** | `OperatorHelpChatService`: 全FAQを取得 → システムプロンプトにFAQ全文を埋め込み → GPT-4o-miniで回答。関連FAQはキーワード・部分一致で最大3件。関連URLは回答文から抽出。 |
| **キャッシュ** | `OperatorFaqService`: Redis で 5分 TTL（`operator_faqs:{language}:{category}:{is_active}`）。FAQ更新後はキャッシュ削除または再起動で反映。 |

### 0.4 大原則（要約定義書・Phase3計画書より）

1. **根本解決 > 暫定解決**  
2. **シンプル構造 > 複雑構造**  
3. **統一・同一化 > 特殊独自**（マニュアルとFAQの説明は一致させる）  
4. **具体的 > 一般**  
5. **拙速 < 安全確実**  
6. **Docker環境必須**（修正・テストは docker-compose で実施し、ステージングデプロイ前にDockerで検証する）

---

## 1. マニュアルとヘルプFAQの差分（なぜ「不足」か）

### 1.1 マニュアルのカバー範囲（Manual.vue の sections より）

| 章 | 主な節（抜粋） | ヘルプFAQでの対応 |
|----|----------------|-------------------|
| 第1章 はじめに | 1.1〜1.4（概要・使い方・要件・初期設定） | setup で一部（初回ログイン・施設情報・アカウント作成・パスワード） |
| 第2章 ログイン・ログアウト | 2.1〜2.3 | 初回ログイン・パスワード・ログインできない場合に相当するFAQあり（内容は要修正） |
| 第3章 ダッシュボード | 3.1〜3.8（週次・月次・カテゴリ・リアルタイム・未解決・フィードバック・**クーポン発行数**） | logs 系で「ダッシュボードで統計」程度。**月次統計・クーポン発行数**の専用FAQなし |
| 第4章 FAQ管理 | 4.1〜4.8（概要・登録・編集・削除・未解決から生成・改善・ベストプラクティス・**CSV一括**） | faq_management でテンプレ・追加・優先度・カテゴリ・一括あり。**CSV手順・ベストプラクティス**は薄い |
| 第5章 スタッフ不在時間帯キュー | 5.1〜5.4 | **該当FAQなし** |
| 第6章 施設設定 | 6.1〜6.6（基本・不在時間帯・パスワード・**クーポン・公式サイトURL・リード一覧**） | setup の施設情報のみ。**クーポン設定・リード一覧**のFAQなし |
| 第7章 プラン・請求 | 7.1〜7.5（概要・現在プラン・プラン変更・解約・請求履歴・領収書） | billing で「料金体系・解約・請求書」3件のみ。**プラン変更手順・領収書の出し方**は不足 |
| 第8章 QRコード | 8.1〜8.5 | qrcode で4件。おおむね対応しているが、SVG記載漏れ等の修正あり |
| 第9章 会話詳細 | 9.1〜9.4 | logs で「質問履歴」程度。**会話詳細画面の見方・エスカレーション対応**は薄い |
| 第10章 ゲスト側の使い方 | 10.1〜10.6（フロー・言語・ウェルカム・チャット・PWA・**固定フッター・クーポン取得**） | **ゲスト側フロー・固定フッター・クーポン取得**のFAQなし |
| 第11章 トラブルシューティング | 11.1〜11.4 | troubleshooting で5件。問い合わせ方法は要修正（問い合わせフォーム統一） |
| 第12章 運用のベストプラクティス | 12.1〜12.4（チェックリスト・日次・週次・月次） | **該当FAQなし** |
| 第13章 付録 | 用語集・翻訳手引書・画面遷移・FAQテンプレ例・更新履歴 | なし（ヘルプでは不要としても可） |

### 1.2 結論：不足している主なトピック

- **プラン・請求**: プラン変更手順、解約手順、請求履歴・領収書の見方（現行は3項目で抽象的）。
- **スタッフ不在時間帯キュー**: キューとは何か、一覧の見方、対応の仕方、通知タイミング。
- **施設設定（拡張）**: クーポン設定・公式サイトURL、リード一覧の確認。
- **ダッシュボード**: 月次統計の見方、クーポン発行数。
- **FAQ管理（補強）**: CSV一括登録の対象プラン・手順・エラー時、ベストプラクティス（良い例・避けたい例）の要約。
- **ゲスト側**: ゲストの利用フロー、固定フッター・クーポン取得の説明（管理者向け説明として）。
- **運用**: 日次・週次・月次のベストプラクティス要約。
- **既存30件の正確性**: 2026-01-20 精査の12項目（パスワードリセット、問い合わせ先、スタッフ管理、TOP10ランキング、請求書、チェックアウト時間例など）の修正が未実施。

---

## 2. ブランチ戦略・Docker環境（コードベース確認結果）

### 2.1 ブランチ戦略（要約定義書・CSV計画書より）

| ブランチ | 用途 | デプロイ先 |
|----------|------|------------|
| **main** | 本番 | Render.com 本番 |
| **develop** | ステージング | Railway Hobby（または現行ステージング） |
| **feature/*** | 開発 | ローカル → PR で develop にマージ |

- FAQ追加・修正は **feature/operator-faq-manual-level** 等で実施し、Dockerで動作・表示確認後に **develop** へマージする運用を推奨。
- 直接 develop で作業する場合は、コミット単位を分け、必要なら `update_operator_faqs.py` で既存レコード更新。

### 2.2 Docker環境（docker-compose.yml より）

- **構成**: postgres（pgvector:pg15, 5433:5432）、redis（6379）、backend（uvicorn 8000）、frontend（Vite 5173）。
- **バックエンド**: `backend/.env` および `OPENAI_API_KEY` が必要。DBは `alembic upgrade head` でマイグレーション適用。
- **FAQ投入**: 初回は `python backend/scripts/insert_operator_faqs.py`（プロジェクトルートで `backend` をカレントにした実行または `docker-compose exec backend` 内で実行）。既存データ更新は `update_operator_faqs.py`。
- **キャッシュ**: FAQ更新後は Redis の `operator_faqs:*` を削除するか、backend 再起動で反映。`OperatorFaqService.clear_faq_cache()` が利用可能。

### 2.3 関連ファイル一覧

| 種別 | パス | 役割 |
|------|------|------|
| FAQデータ定義 | `backend/scripts/insert_operator_faqs.py` | OPERATOR_FAQ_DATA（30件）。追加・修正はここに反映。 |
| FAQ定義書 | `docs/help_system_faq_data.md` | 日本語・英語の質問・回答・キーワード・関連URLのドキュメント。 |
| 更新スクリプト | `backend/scripts/update_operator_faqs.py` | 既存 intent_key の上書き更新用。 |
| FAQサービス | `backend/app/services/operator_faq_service.py` | 取得・検索・キャッシュ・キャッシュ削除。 |
| チャットサービス | `backend/app/services/operator_help_chat_service.py` | 全FAQをプロンプトに埋め込み、GPTで回答。 |
| API | `backend/app/api/v1/help.py` | /help/faqs, /help/search, /help/chat。 |
| マニュアル本文 | `frontend/src/views/admin/Manual.vue` | sections 配列。FAQの「正解」の参照元。 |
| 精査・修正計画 | `docs/20260120_統合ヘルプシステムFAQ精査_調査分析_修正案_修正計画.md` | 12項目の修正内容・ステップ。 |

---

## 3. ヘルプFAQをマニュアルレベルに仕上げる「方法」

### 3.1 基本方針

1. **マニュアルを正とする**: 説明内容・用語・手順は `Manual.vue` の該当章節に合わせる（大原則「統一・同一化」）。
2. **実装と一致させる**: 存在しない機能は「現在はできません」「将来予定」と明記。関連URLは実在するパスのみ（`/admin/plan-billing` 等）。
3. **段階的に拡充**: まず既存30件の誤りを直し、その後に「不足トピック」を追加する。

### 3.2 既存30件の修正（2026-01-20 精査の実施）

- **対象**: 同文書「2. 各問題点の詳細調査分析」「3. 修正計画」の12項目。
- **作業**: `docs/help_system_faq_data.md` と `backend/scripts/insert_operator_faqs.py` の OPERATOR_FAQ_DATA を修正。その後 `update_operator_faqs.py` でDB更新（intent_key で既存レコード更新）、または一時的に operator_faqs を truncate して insert_operator_faqs.py で再投入。
- **確認**: Docker で backend 起動 → GET /api/v1/help/faqs、POST /api/v1/help/chat で回答文・related_url が期待通りか確認。

### 3.3 不足トピックの追加設計

- **カテゴリ**: 既存の setup, qrcode, faq_management, ai_logic, logs, troubleshooting, billing, security に加え、必要なら **plan_billing**（第7章専用）、**overnight_queue**（第5章）、**facility_advanced**（クーポン・リード）などを検討。既存 billing を「プラン・請求」に拡張してもよい。
- **intent_key 例**（マニュアル節と対応）:
  - プラン・請求: `plan_billing_overview`, `plan_billing_change`, `plan_billing_cancel`, `plan_billing_invoices_receipt`
  - スタッフ不在キュー: `overnight_queue_overview`, `overnight_queue_list`, `overnight_queue_respond`
  - 施設設定拡張: `facility_coupon_settings`, `facility_leads_list`
  - ダッシュボード: `dashboard_monthly_stats`, `dashboard_coupon_count`
  - FAQ: `faq_csv_bulk_usage`, `faq_best_practices_summary`
  - ゲスト側: `guest_flow`, `guest_coupon_footer`
  - 運用: `practice_daily_weekly_monthly`
- **本文**: マニュアルの該当節の `content` を要約し、300文字前後で answer を作成。質問文は管理者がよくしそうな自然な疑問形に。

### 3.4 運用フロー（追加・修正のたびに）

1. `help_system_faq_data.md` に項目を追記（日本語・英語・キーワード・related_url）。
2. `insert_operator_faqs.py` の OPERATOR_FAQ_DATA に追加（新規）または既存を修正。
3. 既存のみ修正なら `update_operator_faqs.py` を実行。新規追加がある場合は insert スクリプトを実行（重複は intent_key でスキップする実装になっている）。
4. Redis の operator_faqs キャッシュを削除、または backend 再起動。
5. Docker で API・チャット動作確認。
6. develop にマージ → ステージングでヘルプチャットをブラウザテスト。

---

## 4. 実施計画（ステップと優先度）

| 順序 | 内容 | 予測工数 | 依存 |
|------|------|----------|------|
| **1** | **既存12項目の修正**（2026-01-20 精査） | 0.5〜1日 | なし |
| | help_system_faq_data.md と insert_operator_faqs.py を修正。update_operator_faqs.py でDB反映。DockerでAPI・チャット確認。 | | |
| **2** | **マニュアルとの差分一覧の確定** | 0.5日 | 1 |
| | Manual.vue の全節を一覧化し、各節に対応するFAQの有無・要追加を表にまとめる。 | | |
| **3** | **プラン・請求まわりFAQ追加**（第7章） | 0.5日 | 2 |
| | 7.1〜7.5 に対応する4〜5件（概要・現在プラン・プラン変更・解約・請求履歴・領収書）。billing カテゴリ拡張または plan_billing 新設。 | | |
| **4** | **スタッフ不在時間帯キューFAQ追加**（第5章） | 0.25日 | 2 |
| | 3〜4件。overnight_queue カテゴリ。 | | |
| **5** | **施設設定・ダッシュボード・FAQ・ゲスト・運用の不足分追加** | 1〜1.5日 | 2 |
| | クーポン・リード、月次統計・クーポン発行数、CSV一括・ベストプラクティス、ゲスト側フロー・固定フッター、日週月運用の要約。 | | |
| **6** | **英語翻訳の追加・更新** | 0.5日 | 1〜5 |
| | 新規・修正したFAQの operator_faq_translations に en を投入。 | | |
| **7** | **ステージングデプロイ・ブラウザテスト** | 0.25日 | 1〜6 |
| | ヘルプチャットで各トピックを質問し、マニュアルと矛盾しないか・リンクが正しいか確認。 | | |

**合計目安**: 約 3.5〜4.5 日（28〜36時間）。並行や省略により短縮可能。

---

## 5. まとめ

- **目的**: 施設管理者向けヘルプチャットのFAQを、利用マニュアルと同等の網羅性・正確性にすること。
- **現状**: FAQは30項目・8カテゴリのみで、マニュアルの13章・55節以上に比べて不足。さらに12項目に誤記・存在しない機能・リンク不備がある。
- **方法**: （1）マニュアルを正として内容を統一、（2）既存12項目を修正、（3）不足トピックをマニュアル章節に沿って追加、（4）データ定義・スクリプト・キャッシュ・Docker・ステージングで検証。
- **環境**: ブランチは feature/* → develop。テストは Docker 必須。FAQ更新後は Redis キャッシュ削除または backend 再起動。
- **実行**: 指示があるまで実装は行わず、本計画に基づき準備・設計のみ完了とする。

---

## 6. ステップ1 実施記録（2026-03-01）

### 6.1 バックアップ

- **保存先**: `backups/20260301_operator_faq_step1/`
- **対象**: `backend/scripts/insert_operator_faqs.py`, `docs/help_system_faq_data.md`

### 6.2 実施した修正（既存12項目）

| No | intent_key | 修正内容 |
|----|------------|----------|
| 1 | setup_password_reset | 回答を「実装されていない→問い合わせフォームへ」に変更、related_url なし |
| 2 | faq_bulk_import | 回答を Standard・Premium でCSV一括利用可能に更新、related_url → None |
| 3 | trouble_contact_support | 既に問い合わせフォーム案内・related_url None（スクリプト側は変更なし） |
| 4 | setup_staff_account | 既に「現在は追加できません」・related_url None（スクリプト側は変更なし） |
| 5 | qrcode_regenerate | related_url → None（スクリプト・md 両方） |
| 6 | trouble_cannot_login | 既に問い合わせフォーム案内・related_url None（スクリプト側は変更なし） |
| 7 | setup_first_login | 回答の「チェックイン」→「チェックアウト」、related_url → /admin/manual（md のみ。スクリプトは既に /admin/manual#login-first） |
| 8 | qrcode_print_size | 回答に SVG 追加（スクリプトは既に PDF/PNG/SVG、md を修正） |
| 9 | faq_priority | 例を「チェックイン時間」→「チェックアウト時間」に変更（md。スクリプトは既に修正済み） |
| 10 | ai_languages | 対応言語を「日本語・英語・繁体中国語・フランス語・韓国語」に修正、related_url → /admin/manual（md。スクリプトは既に修正済み） |
| 11 | logs_analytics | 回答を「TOP10は将来追加予定」に変更、related_url なし（md。スクリプトは既に修正済み） |
| 12 | billing_invoice | 請求書は原則非発行・領収書はダウンロード可能の旨に変更（スクリプトは既に修正済み。md は FAQ 25–30 が未記載のため対象外） |

- **help_system_faq_data.md**: 上記のうち FAQ 1–24 に相当する箇所を修正。trouble_ai_slow・trouble_faq_not_updated の問い合わせ先を「問い合わせフォーム」に統一、関連URLを「なし」または正しいURLに変更。
- **insert_operator_faqs.py**: faq_bulk_import の回答・related_url、qrcode_regenerate の related_url を修正。その他は既に修正済みのため変更なし。

### 6.3 DB反映

- **実施済み（2026-03-01）**: Docker で postgres・redis を起動し、`docker compose run --rm -e DATABASE_URL=postgresql://yadopera_user:yadopera_password@postgres:5432/yadopera backend python scripts/update_operator_faqs.py` を実行。30件の FAQ 翻訳（ja/en）を更新し、DB 反映完了。
- ステージング・本番で反映する場合は、各環境の DATABASE_URL を指定して同スクリプトを実行してください。反映後は Redis の `operator_faqs:*` キャッシュを削除するか、backend を再起動してください。

### 6.4 Docker環境・ブランチ・コミット・プッシュ

- **Docker**: `docker-compose.yml` の postgres（port 5433）, redis, backend, frontend 構成。DB 更新は backend コンテナ内で `DATABASE_URL=postgresql://yadopera_user:yadopera_password@postgres:5432/yadopera` を指定して実行。
- **ブランチ戦略**: main＝本番、develop＝ステージング、feature/*＝開発。今回の作業は **develop** で実施。
- **コミット**: `9b85a5b` — 「Fix: 施設管理者向けヘルプチャットFAQ 12項目修正（ステップ1）とマニュアル水準化計画」（3ファイル変更）。
- **プッシュ**: 認証の都合で自動プッシュは未実施。お手元のターミナルで `git push origin develop` を実行してください。

---

**参照文書**

- [yadopera-v03-summary.md](Summary/yadopera-v03-summary.md)（要約定義書・付録C 宿泊事業者向けFAQ）
- [Phase3_現況と残存課題_実装計画_20260209.md](Phase3/Phase3_現況と残存課題_実装計画_20260209.md)
- [manual_plan.md](manual_plan.md)（マニュアル構成・目的）
- [20260120_統合ヘルプシステムFAQ精査_調査分析_修正案_修正計画.md](20260120_統合ヘルプシステムFAQ精査_調査分析_修正案_修正計画.md)
- [help_system_faq_data.md](help_system_faq_data.md)
- [Stripe実装_宿泊施設管理者マニュアル反映_計画_20260228.md](Phase4/Stripe実装_宿泊施設管理者マニュアル反映_計画_20260228.md)
- [ブランチ戦略確認とコミットプッシュ_20260211.md](CSV_bulk_registration_function_implementation_plan/ブランチ戦略確認とコミットプッシュ_20260211.md)
