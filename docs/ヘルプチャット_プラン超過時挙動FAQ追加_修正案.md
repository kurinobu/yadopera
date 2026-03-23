# ヘルプチャット「プラン超過時の停止」回答ずれ — 調査・修正案

**作成日**: 2026年3月13日  
**目的**: 「質問数上限が超過したら停止できますか?」に対するヘルプチャットの回答を、実装済みの「プラン超過時の挙動（管理者選択制）」と一致させる。  
**方針**: 指示があるまで**実行しない**。修正案の提示のみ。

---

## 1. 概要・原因

### 1.1 事象

- **ユーザー質問**: 「質問数上限が超過したら停止できますか?」
- **ヘルプチャットの回答**: 「現在、質問数の上限を超過した場合の**自動停止機能はありません**が、利用状況を定期的に確認し、プラン変更や解約を行うことができます。詳細は「プラン・請求」ページでご確認ください。」
- **問題**: 実装では「プラン超過時の挙動」で**「AI停止・FAQのみ対応」**を選ぶと、上限超過後は**自動で**AIを止めFAQ検索のみで応答するため、「自動停止機能はありません」は誤り。

### 1.2 原因

- ヘルプの**AIチャット**は `OperatorHelpChatService` で、**DBの operator_faqs / operator_faq_translations に登録されたFAQ全文**をシステムプロンプトに埋め込み、OpenAI で回答している。
- **データの正**: `backend/scripts/insert_operator_faqs.py` の `OPERATOR_FAQ_DATA`。定義書: `docs/help_system_faq_data.md`。
- 「質問数上限超過時の停止」「プラン超過時の挙動」に直接答える**FAQ項目が存在しない**ため、AIが既存の料金・プラン系FAQから推論し、古い説明（停止機能なし）を返している。

---

## 2. 大原則との対応（docs/20260307_プロジェクト現況と今後の計画_総括.md §0.1 参照）

| 大原則 | 本修正での対応 |
|--------|----------------|
| 根本解決 > 暫定解決 | FAQデータに「プラン超過時・AI停止」の正しい説明を**1項目追加**し、チャットがそれを参照して回答するようにする。暫定的なプロンプト修正は行わない。 |
| シンプル構造 > 複雑構造 | 既存の「billing」カテゴリに1件追加するだけとし、サービスコードは変更しない。 |
| 統一・同一化 > 特殊独自 | ご利用マニュアル「7.3 プラン超過時の挙動の設定」および要約定義書・実装計画書の説明と**文言・意味を一致**させる。 |
| 具体的 > 一般 | 回答文で「プラン・請求」ページの「プラン超過時の挙動」セクション、「AI停止・FAQのみ対応」選択時の挙動を具体的に記載する。 |
| 拙速 < 安全確実 | 修正後はDockerでヘルプAPI・チャット応答を確認し、期待する表示・動作になってから反映とする。 |
| Docker環境必須 | DB反映・動作確認は docker-compose 上の backend で行う。 |

---

## 3. 修正内容

### 3.1 追加するFAQ（1件）

- **intent_key**: `plan_billing_overage_behavior`
- **category**: `billing`
- **display_order**: 84（既存の plan_billing_invoices が 85 のため、その前）

#### 日本語 (ja)

- **質問**: 質問数が上限を超過したらAIを止められますか？ / 超過したら停止できますか？
- **回答**: はい、止められます。「プラン・請求」ページの「プラン超過時の挙動」で**「AI停止・FAQのみ対応」**を選んで「設定を保存」すると、月間質問数がプラン上限を超えたあとは、AIは自動で使われず、登録したFAQの検索結果だけでゲストに応答します。超過分の課金はありません。もう一方の「通常継続（従量課金）」を選ぶと、超過後もAI応答を続け、超過分は1質問あたり¥30で請求されます。Free・Small・Standard・Premiumでこの設定が表示されます（Miniは質問数上限がないため表示されません）。詳細はご利用マニュアル「7.3 プラン超過時の挙動の設定」をご覧ください。
- **キーワード**: 質問数上限,超過,停止,AI停止,FAQのみ,プラン超過時の挙動,従量課金
- **関連URL**: /admin/billing

#### 英語 (en)

- **Question**: Can I stop AI when the question limit is exceeded? / Can it stop after exceeding the limit?
- **Answer**: Yes. On the "Plan & Billing" page, under "Plan overage behavior", select **"AI stop & FAQ only"** and click "Save settings". After your monthly question count exceeds the plan limit, AI will not be used and only registered FAQ search results will be shown to guests. No charge for overage. If you choose "Normal continuation (usage-based billing)" instead, AI continues and overage is billed at ¥30 per question. This setting is shown for Free, Small, Standard, and Premium (Mini has no question limit, so the setting is not shown). See the user manual section "7.3 Plan overage behavior settings" for details.
- **Keywords**: question limit,overage,stop,AI stop,FAQ only,plan overage behavior,usage billing
- **Related URL**: /admin/billing

### 3.2 変更対象ファイル

| ファイル | 変更内容 |
|----------|----------|
| `docs/help_system_faq_data.md` | billing カテゴリに上記1件の定義を追記（形式は既存の「FAQ ○○: intent_key」に合わせる）。※ 同ファイルに「## Category: billing」が無い場合は、logs や troubleshooting の後など適宜に「## Category: billing（料金・プラン・請求）」見出しと本FAQ 1件を追加する。 |
| `backend/scripts/insert_operator_faqs.py` | `OPERATOR_FAQ_DATA` の billing ブロック内、`plan_billing_invoices`（display_order 85）の**前**に、上記の `plan_billing_overage_behavior`（display_order 84）を1件追加する。 |

### 3.3 変更しないもの

- `OperatorHelpChatService` 等のサービス・API・フロント: 変更不要（FAQ追加のみでシステムプロンプトに自動で含まれる）。
- 既存FAQの文言変更: 行わない（新規1件追加のみ）。

---

## 4. 実施手順（実行は指示があるまで行わない）

1. **バックアップ**  
   - `docs/help_system_faq_data.md` と `backend/scripts/insert_operator_faqs.py` を `backups/YYYYMMDD_help_overage_faq/` にコピーする。

2. **定義書の更新**  
   - `docs/help_system_faq_data.md` の billing カテゴリに、上記「3.1 追加するFAQ」を既存形式で追記する。

3. **スクリプトの更新**  
   - `backend/scripts/insert_operator_faqs.py` の `OPERATOR_FAQ_DATA` に、`plan_billing_overage_behavior` の辞書を1件追加する（`plan_billing_invoices` の直前に挿入）。

4. **DB反映**  
   - Docker 内で次のいずれかを実行する。  
     - **新規1件のみ追加する場合**:  
       `docker compose run --rm -e DATABASE_URL=postgresql://yadopera_user:yadopera_password@postgres:5432/yadopera backend python scripts/update_operator_faqs.py`  
       （`update_operator_faqs.py` は intent_key が無い場合は新規作成するため、これで1件追加される。）  
     - または:  
       `docker compose run --rm -e DATABASE_URL=... backend python scripts/insert_operator_faqs.py`  
       （既存はスキップされ、新規分のみ作成される。）

5. **キャッシュ**  
   - FAQ 更新後、Redis の `operator_faqs:*` を削除するか、backend を再起動してから確認する。

6. **動作確認**  
   - 管理画面でヘルプを開き、AIチャットで「質問数上限が超過したら停止できますか?」と送信する。  
   - 回答に「AI停止・FAQのみ対応」を選べば超過後はAIが使われずFAQのみで応答すること、設定は「プラン・請求」の「プラン超過時の挙動」で行うことが含まれることを確認する。  
   - 必要に応じて「プラン超過時の挙動」「超過したら停止」など別表現でも質問し、同様の内容が返ることを確認する。

7. **ステージング・本番**  
   - デプロイ後、該当環境の DB に対して上記と同じく `update_operator_faqs.py`（または手順に従ったFAQ反映）を1回実行する。手順は `docs/施設管理者向けヘルプチャットFAQ_マニュアル水準化_調査と計画.md` の「デプロイ時のDB反映」に従う。

---

## 5. 参照

- 実装仕様: `docs/プラン超過時の挙動_管理者選択制_実装計画.md`
- マニュアル: `frontend/src/views/admin/Manual.vue` 第7章 7.3 プラン超過時の挙動の設定
- ヘルプFAQデータ運用: `docs/施設管理者向けヘルプチャットFAQ_マニュアル水準化_調査と計画.md`
- 要約定義書: `docs/Summary/yadopera-v03-summary.md`（プラン超過時の挙動 実装済みの記述）

---

**Document Version**: 1.0  
**Status**: 2026-03-13 実施済み。バックアップ `backups/20260313_help_overage_faq/`。DB反映は `update_operator_faqs.py` で完了（plan_billing_overage_behavior 追加）。確認時は Redis の operator_faqs キャッシュ削除または backend 再起動を推奨。
