# 新規登録時 自動登録FAQの精査・修正 実装計画

**作成日**: 2026年3月14日  
**対象**: 今後の計画 総括 §7.1 項目10「新規登録時 自動登録FAQの精査・修正」  
**基準文書**: 要約定義書、アーキテクチャ設計書、`docs/20260307_プロジェクト現況と今後の計画_総括.md`（大原則）

---

## 1. 目的・範囲

- **目的**: 新規登録時に施設へ自動投入されるゲスト向けFAQの内容を精査・修正し、件数を20件から30件に拡張する。
- **範囲**:
  - データ定義: `backend/app/data/faq_presets.py`（FAQプリセット30件）
  - 投入件数制御: `backend/app/core/plan_limits.py`（`INITIAL_FAQ_COUNTS`, `filter_faq_presets_by_plan`）
  - 新規登録時の呼び出し: `backend/app/services/auth_service.py` の `register_facility_async_faqs`
  - 必要に応じて: マニュアル（初期設定・FAQ周り）、ヘルプチャット（事業者向けFAQで「初期テンプレート20件」等の記述）

※ 宿泊事業者向けヘルプチャットのFAQ（`backend/scripts/insert_operator_faqs.py` の48項目）は本件の対象外。

---

## 2. 大原則への準拠

| 原則 | 本件での適用 |
|------|--------------|
| 根本解決 > 暫定解決 | 文言・内容の不備はプリセット定義で修正し、運用で補正しない |
| シンプル構造 > 複雑構造 | 件数変更は定数とスライス変更のみ。新規テーブルや条件分岐を増やさない |
| 統一・同一化 > 特殊独自 | 既存のプリセット形式（category, intent_key, priority, translations）を維持 |
| 具体的 > 一般 | 修正は「どの intent_key のどの言語の question/answer をどう変えるか」を明示して反映 |
| 拙速 < 安全確実 | 精査→修正→20→30件変更→テスト→デプロイの順を守り、テストを省略しない |
| Docker環境必須 | ローカル検証・単体テストは Docker 上で実行する |

---

## 3. 現況

| 項目 | 内容 |
|------|------|
| プリセット定義 | `backend/app/data/faq_presets.py` に **30件** 定義（basic / facilities / location / trouble、7言語） |
| 現在の投入件数 | **20件**。`plan_limits.py` の `INITIAL_FAQ_COUNTS` が全プランで 20。`filter_faq_presets_by_plan()` が優先度順ソート後 `sorted_presets[:20]` で抽出 |
| 投入タイミング | 新規施設登録後、`auth_service.register_facility_async_faqs()` でバックグラウンド一括投入 |
| テスト | `backend/tests/test_faq_presets.py` が「全プラン20件」「30件の存在」「7言語」などを検証 |

精査用一覧は次で再生成できる。

```bash
cd backend && python scripts/export_faq_presets_for_review.py
```

出力: `docs/新規登録時_自動登録FAQ_精査用一覧.csv`（No, 投入区分, intent_key, category, priority, question_ja, answer_ja, 修正メモ）

---

## 4. 実施手順（順序）

### Step 1: 精査用一覧の提供（完了）

- **成果物**: `docs/新規登録時_自動登録FAQ_精査用一覧.csv`
- **内容**: 全30件を優先度順に一覧。1〜20が「現在投入中」、21〜30が「30件化で追加予定」。日本語の質問・回答と intent_key を記載。修正メモ列は空欄で利用者が記入可能。
- **再生成**: 上記スクリプトでいつでも再出力可能。

### Step 2: 利用者による目視精査と修正方針の決定

- 利用者が上記CSV（またはエディタで開いた内容）で全FAQを精査する。
- 修正したい場合は「修正メモ」列に記載するか、別ドキュメントで「intent_key / 言語 / 質問 or 回答 / 修正後文言」を指示する。
- **指示があるまで実装（Step 3 以降）は行わない。**

### Step 3: プリセット内容の修正反映（指示後に実施）

- 精査結果に基づき、`backend/app/data/faq_presets.py` の該当プリセットの `translations` 内の `question` / `answer` を修正する。
- 追加・削除するFAQがある場合は、プリセットの追加・削除と `filter_faq_presets_by_plan` の対象件数との整合を取る（通常は30件のまま内容のみ変更）。

### Step 4: 自動登録件数を 20件 → 30件 に変更（指示後に実施）

- **4.1** `backend/app/core/plan_limits.py`
  - `INITIAL_FAQ_COUNTS`: 各プランの値を `20` → `30` に変更。
  - `filter_faq_presets_by_plan()`: コメントおよび `sorted_presets[:20]` を `sorted_presets[:30]` に変更。
- **4.2** `backend/tests/test_faq_presets.py`
  - 「20件」を前提にしているテストを「30件」に更新（`assert len(result) == 20` → `assert len(result) == 30`、`get_initial_faq_count(plan) == 20` → `== 30` など）。

### Step 5: マニュアル・ヘルプチャットの必要反映（指示後に実施）

- **マニュアル**: `frontend/src/views/admin/Manual.vue` などで「20件の初期デフォルトFAQ」と書かれている箇所があれば「30件の初期デフォルトFAQ」に変更。必読: `docs/マニュアル更新・改訂_必読.md`。
- **ヘルプチャット（事業者向けFAQ）**: `docs/help_system_faq_data.md` および `backend/scripts/insert_operator_faqs.py` 内に「20件」「20-30件」等の記述があれば、必要に応じて「30件」に統一。

### Step 6: ローカルでのテスト（Docker必須）

- `backend` で pytest を実行し、FAQプリセット関連テストが通ることを確認。
  - 例: `cd backend && docker compose run --rm backend pytest tests/test_faq_presets.py -v`
- 必要なら新規登録フローをローカルで実行し、該当施設に30件のFAQが投入されることを確認。

### Step 7: ステージングへのデプロイとテスト

- 変更を `develop` にコミットし、プッシュ（認証都合で利用者が手動実行の場合あり）。
- ステージングで新規登録またはテスト施設でFAQ件数・内容をブラウザおよびAPIで確認。

### Step 8: 関連文書の更新

- **総括** `docs/20260307_プロジェクト現況と今後の計画_総括.md`: 残存課題一覧の「新規登録時 自動登録FAQの精査・修正」を完了にし、§1 現況に実施結果を追記。
- **要約定義書** `docs/Summary/yadopera-v03-summary.md`: 変更履歴に「新規登録時 自動登録FAQ 精査・修正、30件化」を追記。
- 必要に応じてアーキテクチャ設計書の「FAQ初期テンプレート 20-30件」等の記述を「30件」に更新。

---

## 5. 成果物・参照一覧

| 成果物 | パス |
|--------|------|
| 埋め込み事前計算 実装計画 | `docs/新規登録時_自動登録FAQ_埋め込み事前計算_実装計画.md`（登録時のAPI呼び出しをやめ、事前計算したembeddingをコピーする方式。運用時の注意点含む） |
| 精査用一覧CSV | `docs/新規登録時_自動登録FAQ_精査用一覧.csv` |
| 一覧生成スクリプト | `backend/scripts/export_faq_presets_for_review.py` |
| FAQプリセット定義 | `backend/app/data/faq_presets.py` |
| 件数・フィルタ定義 | `backend/app/core/plan_limits.py` |
| 単体テスト | `backend/tests/test_faq_presets.py` |
| マニュアル必読 | `docs/マニュアル更新・改訂_必読.md` |
| 総括（大原則・残存課題） | `docs/20260307_プロジェクト現況と今後の計画_総括.md` |

---

## 6. Status

- **Step 1〜8**: **✅ 完了（2026-03-14）**。精査用CSV・修正版CSVに基づくプリセット修正、20→30件化、マニュアル・ヘルプ表記統一、テスト、デプロイ・ステージング確認、関連文書更新まで実施。Phase A として `docs/新規登録時_自動登録FAQ_埋め込み事前計算_実装計画.md` §9 に沿って A1〜A7 完了。develop コミット 2ae5ad1。
- **Phase B（埋め込み事前計算）**: **✅ 完了（2026-03-14）**。同実装計画 §9 Phase B・§10 に実施結果と B10 ステージング確認（FAQ30件・埋め込みAPI未使用・ゲスト画面RAG）を記録済み。

---

**Document Version**: 1.1  
**Last Updated**: 2026年3月14日
