# 新規登録時 自動登録FAQ — 埋め込みベクトル事前計算 実装計画

**作成日**: 2026年3月14日  
**目的**: 新規登録時のFAQ自動投入で、埋め込み（embedding）を毎回APIで生成するのではなく、**事前計算して保持し登録時はコピーする**方式に変更するための調査分析と、大原則に準拠した実装案の提示。  
**基準文書**: `docs/20260307_プロジェクト現況と今後の計画_総括.md`（大原則）、`docs/新規登録時_自動登録FAQ_精査・修正_実装計画.md`  
**状態**: Phase A 完了。Phase B は B1〜B11 の実装・テスト・手順整備を完了。B10 のステージング実確認は手順書に従い実施すること。

---

## 1. 目的・範囲

### 1.1 目的

- 新規登録のたびに **OpenAI 埋め込みAPI を呼ばない** ようにし、**コスト削減・登録時間短縮・レート制限リスク低減** を図る。
- 定型プリセットは同一テキストのため **同じベクトルでよい** という前提で、**事前に1回だけ計算して保存し、登録時はそれをコピーする**。

### 1.2 範囲

| 対象 | 内容 |
|------|------|
| **プリセット** | `backend/app/data/faq_presets.py` の全FAQ×全言語（30件×7言語＝最大210組み合わせ。プランで絞る前） |
| **事前計算** | 上記の (intent_key, language) ごとに `question + " " + answer` の埋め込みを生成し、ファイル等に保存 |
| **登録経路** | `auth_service.register_facility_async_faqs` → `filter_faq_presets_by_plan` → `FAQService.bulk_create_faqs` → `create_faq`。プリセット由来のときのみ「保存済み embedding を渡し、API を呼ばない」 |
| **対象外** | 管理画面からのFAQ追加・編集・CSV一括アップロードは従来どおりその場で `generate_embedding` を呼ぶ（変更しない） |

---

## 2. 現況（調査結果）

### 2.1 翻訳

- 各言語の文言は **faq_presets.py に事前定義** 済み。新規登録時に **翻訳API は呼んでいない**。

### 2.2 埋め込み（問題となっている部分）

- **生成箇所**: `backend/app/services/faq_service.py` の `create_faq`。各 `request.translations` について `generate_embedding(question + " " + answer)` を実行し、`FAQTranslation.embedding` に格納。
- **呼び出し元**: `register_facility_async_faqs` が `filter_faq_presets_by_plan` でプランに応じたプリセットを取得し、`FAQRequest` のリストに変換して `bulk_create_faqs` に渡す。`bulk_create_faqs` は各リクエストに対して `create_faq` を呼ぶため、**登録するFAQ数×言語数だけ** embedding API が呼ばれる。
- **モデル**: `app/ai/openai_client.py` で `text-embedding-3-small`（1536次元）を使用。
- **回数例**（現在20件投入時）: Free 20回、Mini 40回、Small 60回、Standard 80回、Premium 140回。30件化後は最大 30×7＝210 回/回。

### 2.3 データフロー（現状）

```
faq_presets.py（文言のみ）
  → filter_faq_presets_by_plan（件数・言語でフィルタ）
  → FAQRequest に変換（translations に question/answer のみ）
  → bulk_create_faqs → create_faq
  → 各 translation で generate_embedding() を実行 → API 呼び出し
  → FAQTranslation に embedding を格納
```

---

## 3. 大原則への準拠

| 原則 | 本件での適用 |
|------|--------------|
| **根本解決 > 暫定解決** | 登録のたびのAPI呼び出しをやめ、事前計算＋コピーで根本的にコスト・時間を削減する。 |
| **シンプル構造 > 複雑構造** | プリセット由来かどうかは「リクエストに embedding が含まれるか」で判別し、分岐は1箇所にまとめる。保存形式は1ファイルに統一する。 |
| **統一・同一化 > 特殊独自** | 既存の `generate_embedding` を「事前計算スクリプト」でもそのまま使い、モデル・結合ルールを変えない。 |
| **具体的 > 一般** | 保存形式（キー・値・ファイルパス）、スキーマの拡張（Optional embedding）、スクリプトの入出力を明示する。 |
| **拙速 < 安全確実** | 事前計算ファイルのバージョン・モデル名を記録し、運用時の再計算条件を文書化する。テストで「プリセット登録時にAPIが呼ばれないこと」を検証する。 |
| **Docker環境必須** | 事前計算スクリプト・単体テストは Docker 上で実行できるようにする。 |

---

## 4. 実装案（方式概要）

### 4.1 考え方

1. **事前計算（一度だけ／プリセット変更時）**  
   全プリセット×全言語について、`question + " " + answer` で `generate_embedding` を実行し、結果を **キー (intent_key, language)** で保存する。
2. **登録時**  
   プリセットを `FAQRequest` に変換する段階で、**保存済み embedding を translations に付与**する。`create_faq` では、**embedding が渡されていれば API を呼ばずそのまま使う**。
3. **管理画面・CSV一括**  
   従来どおり embedding なしでリクエストが来るため、その場で `generate_embedding` を呼ぶ（変更なし）。

### 4.2 保存形式・置き場所

- **形式**: JSON 1ファイル。**ルート構造**は `{"meta": {...}, "embeddings": {...}}` とし、`meta` にモデル名・生成日時、`embeddings` にキー `"{intent_key}:{language}"`（例: `basic_quiet_hours:ja`）、値は 1536 次元の float 配列の辞書を格納する。メタと埋め込みを分けることで、キー競合を避け、運用時の判定に使う。
- **置き場所**: `backend/app/data/faq_presets_embeddings.json`（リポジトリにコミットする。サイズは 30×7×1536×4 バイト程度で数MB以内を想定）。
- **理由**: 既存の `faq_presets.py` は文言のみのままにして、embedding は別ファイルに分離する。モデル変更時やプリセット変更時に再生成するだけでよく、Python のソースに巨大な配列を書かなくてよい。

### 4.3 メタ情報（バージョン・モデル）

- 同一ファイルの先頭または別の小さいメタファイルで、**埋め込みモデル名**（例: `text-embedding-3-small`）と **生成日時またはプリセットバージョン** を記録する。
- 運用で「モデル変更時・プリセット文言変更時は再生成」と判断するための根拠にする。

---

## 5. 実装案（具体的な変更）

### 5.1 事前計算用スクリプト（新規）

- **パス**: `backend/scripts/generate_faq_presets_embeddings.py`
- **処理**:
  1. `faq_presets.py` の `FAQ_PRESETS` を読み込む。
  2. 各プリセットの各 `translations` について、`combined_text = question + " " + answer` で `generate_embedding(combined_text)` を実行（既存の `app.ai.embeddings.generate_embedding` を使用）。
  3. キー `intent_key:language`、値 `list[float]` の辞書を組み立て、メタ情報（model_embedding の値、生成日時）とともに JSON で保存。
  4. 出力先: `backend/app/data/faq_presets_embeddings.json`
- **実行**: Docker 上で、`OPENAI_API_KEY` を設定したうえで実行。`generate_embedding` が async のため、スクリプトは `asyncio.run(main())` 等で非同期実行する。初回またはプリセット変更後に手動またはCIで実行。
- **冪等**: 同じプリセット・同じモデルであれば上書きするだけなので、何度実行してもよい。

### 5.2 埋め込み読み込みモジュール（新規）

- **パス**: `backend/app/data/faq_presets_embeddings_loader.py`（または `faq_presets.py` 内の関数でも可）
- **役割**: `faq_presets_embeddings.json` を読み、`get_preset_embedding(intent_key: str, language: str) -> Optional[List[float]]` を提供。ファイルが無い・キーが無い場合は `None` を返す（その場合は登録経路で従来どおりAPIを呼ぶフォールバックにできるが、本方式採用時はプリセット登録では必ずファイルを用意する想定）。
- **読み込みタイミング**: モジュールロード時に JSON を1回読み、メモリ上の辞書を保持する。`get_preset_embedding` はその辞書を参照するだけとする（登録頻度は高くないため、都度ファイルを読む必要はない）。

### 5.3 プリセット→FAQRequest 変換で embedding を付与

- **箇所**: `auth_service.register_facility_async_faqs` 内。現在は `preset["translations"]` から `language`, `question`, `answer` のみで `FAQRequest` を組み立てている。
- **変更**: フィルタ後の各 preset について、各 `t in preset["translations"]` に対して、`get_preset_embedding(preset["intent_key"], t["language"])` を取得し、**embedding が取れた場合は**その translation に `embedding` を含めて `FAQRequest` に渡す。取れなかった場合は embedding なしで渡し、`create_faq` で従来どおり API が呼ばれる（キー欠損時は警告ログを出すとよい）。
- **スキーマ**: `FAQTranslationRequest` に `embedding: Optional[List[float]] = None` を追加。`create_faq` では `trans_request.embedding` が存在し None でなければそれを使い、そうでなければ `generate_embedding` を呼ぶ。

### 5.4 create_faq の変更

- **箇所**: `backend/app/services/faq_service.py` の `create_faq`。各 `trans_request` のループ内で、**`trans_request.embedding` が存在し長さが 1536 であれば**、それを使って `FAQTranslation(..., embedding=trans_request.embedding)` とする。そうでなければ従来どおり `generate_embedding(combined_text)` を実行する。
- **バリデーション**: `embedding` が渡された場合、長さが 1536 であることをチェックする（モデルと次元が変わった場合の検知）。

### 5.5 テスト

- **単体**: プリセット用 embedding 読み込みのテスト（キーが存在するとき正しくリストが返る、ファイルが無いとき None 等）。事前計算スクリプトは、テスト用に小さなプリセットで実行し、出力JSONのキー・次元数が期待どおりであることを確認する。
- **結合**: 新規登録フローで、**モックで OpenAI を叩かない** ようにしたうえで、プリセットから登録した施設の `faq_translations` に embedding が入っていること、かつ **embedding API が呼ばれていないこと**（モックの call_count が 0）を検証する。
- いずれも **Docker 上で実行** する。

---

## 6. 運用時の注意点（運用で気をつけること）

本機能は **一度の実装で終わりではなく、プリセットの修正・モデル変更・環境追加に伴い運用でメンテナンスする** ため、以下を文書として残し、運用時に参照する。

### 6.1 埋め込みモデルの変更

- **事象**: OpenAI の埋め込みモデルを変更した（例: `text-embedding-3-small` → 別モデル）、または同じモデルでも次元数が変わった。
- **対応**: `faq_presets_embeddings.json` は **全件再生成** が必要。`scripts/generate_faq_presets_embeddings.py` を、新しいモデルが設定された環境で実行し、生成されたファイルをコミット・デプロイする。
- **記録**: 本ドキュメントまたは `faq_presets_embeddings.json` のメタ情報に「使用モデル名」を明記し、モデル変更時に「再生成必須」であることを手順書に書いておく。

### 6.2 プリセット文言の追加・変更・削除

- **事象**: `faq_presets.py` の質問・回答を変更した、または新規プリセット・新言語を追加／削除した（例: 今回の「オンライン会議」→「自転車貸し出し」差し替え）。
- **対応**: 変更のあった **(intent_key, language)** について、**当該キーの embedding を再計算** し、`faq_presets_embeddings.json` を更新する。スクリプトを「全件再生成」で回してもよい。削除したプリセット・言語のキーは JSON からも削除する。
- **手順**: 1) `faq_presets.py` を編集、2) `generate_faq_presets_embeddings.py` を実行（変更分だけ再計算するオプションがあれば利用）、3) 生成ファイルをコミット、4) デプロイ。

### 6.3 次元数・形式の一致

- **事象**: DB の `faq_translations.embedding`（pgvector）は 1536 次元で定義されている。モデルや実装の変更で次元が変わると不整合になる。
- **対応**: 埋め込みモデルや次元数を変更する場合は、DB のカラム定義・マイグレーションと、`faq_presets_embeddings.json` の再生成、および `create_faq` の 1536 チェックの更新をセットで行う。本ドキュメントに「現在の次元数: 1536」「モデル: text-embedding-3-small」を記載し、変更時はここを更新する。

### 6.4 事前計算スクリプトの実行タイミングと実行者

- **タイミング**: (1) 初回導入時、(2) `faq_presets.py` の内容変更後、(3) 埋め込みモデル変更後。
- **実行者**: 開発者またはCI。実行には **OPENAI_API_KEY** が必要なため、CI で回す場合はシークレットに設定する。ローカルで手動実行する場合は、手順を README または本ドキュメントに書いておく。
- **本番**: 本番環境ではスクリプトを実行せず、**事前に生成した JSON をリポジトリに含めデプロイする**。これにより本番で API を叩かずに済む。

### 6.5 ファイルが無い・キーが無い場合の挙動

- **設計**: `get_preset_embedding` が None を返す場合、現状案では「プリセット登録時は必ずファイルとキーを用意する」想定。万が一キー欠損があっても、`create_faq` の既存ロジックにフォールバックすれば、その translation だけその場で API が呼ばれる。運用では、**新規プリセット追加時に embedding の追加を忘れない** ようにチェックリストに含める。

### 6.6 バージョン管理とデプロイ

- **faq_presets_embeddings.json** はリポジトリにコミットし、`faq_presets.py` と **同時に更新** する。`faq_presets.py` だけ更新して embedding を更新し忘れると、登録時に古いベクトルがコピーされ、検索精度がずれる。デプロイ前チェックリストに「プリセット変更時は embedding 再生成・コミット」を入れておく。

### 6.7 本実装と「精査・修正」「30件化」の関係

- 「新規登録時 自動登録FAQ 精査・修正」で、プリセット文言の修正・30件化・自転車貸し出しへの差し替えを行う。
- **推奨順序**: (1) プリセット文言の修正と30件化を反映、(2) その後で **埋め込み事前計算の仕組み** を導入し、全プリセット×全言語の embedding を一度生成して JSON をコミット、(3) 登録経路でその JSON を参照するように変更。これにより、最初から「登録時にAPIを呼ばない」状態でリリースできる。
- 運用後、文言を変えたときは上記 6.2 に従い、該当部分の再計算と JSON 更新を行う。

---

## 7. 成果物・参照一覧

| 成果物 | パス・内容 |
|--------|------------|
| 本実装計画 | `docs/新規登録時_自動登録FAQ_埋め込み事前計算_実装計画.md` |
| 精査・修正 実装計画 | `docs/新規登録時_自動登録FAQ_精査・修正_実装計画.md` |
| プリセット定義 | `backend/app/data/faq_presets.py` |
| 埋め込み生成（現行） | `backend/app/ai/embeddings.py`（`generate_embedding`） |
| 埋め込みクライアント | `backend/app/ai/openai_client.py`（`model_embedding`） |
| FAQ作成 | `backend/app/services/faq_service.py`（`create_faq`） |
| 新規登録時FAQ投入 | `backend/app/services/auth_service.py`（`register_facility_async_faqs`） |
| 大原則 | `docs/20260307_プロジェクト現況と今後の計画_総括.md` §0.1 |

---

## 8. 計画の抜け・矛盾の確認

### 8.1 抜けの補足（反映済み・要反映）

| 項目 | 内容 | 対応 |
|------|------|------|
| **JSON ルート構造** | メタ情報と埋め込みを同一ファイルに含める場合、キー競合を避けるためルートを `meta` / `embeddings` に分ける必要がある。 | §4.2 に `{"meta": {...}, "embeddings": {...}}` を明記済み。 |
| **事前計算スクリプトの非同期** | `generate_embedding` は async のため、スクリプトは `asyncio.run` 等で実行する必要がある。 | §5.1 に「asyncio.run(main()) 等で非同期実行」を追記済み。 |
| **ローダーの読み込みタイミング** | JSON を毎回読むか、起動時1回か。登録は頻度が高くないが、一貫して「モジュールロード時1回読み、辞書を保持」とすると実装が明確になる。 | §5.2 に「モジュールロード時に1回読み、get_preset_embedding は辞書を参照」を追記済み。 |
| **キー欠損時の扱い** | embedding が取れなかった translation は embedding なしで FAQRequest に渡し、create_faq で API が呼ばれる。警告ログを出すと運用で気づきやすい。 | §5.3 に「取れなかった場合は embedding なしで渡す」「キー欠損時は警告ログ」を追記済み。 |
| **バックアップ** | 実装前に変更対象ファイルのバックアップを取る手順が計画に無い。 | §10 ステップ計画に「バックアップ」を明示した。 |
| **次元数の定数化** | 1536 をマジックナンバーにせず、1箇所で定義するか既存の openai_client 等と揃えると変更時に漏れが少ない。 | §10 ステップ計画に「次元数定数の参照・検討」を入れた。 |

### 8.2 矛盾の有無

- **5.3 と 6.5**: 「embedding が取れた場合のみ付与」と「None のときは create_faq で API が呼ばれるフォールバック」は一致している。矛盾なし。
- **精査・修正との順序**: 6.7 で「(1) プリセット文言・30件化 (2) 埋め込み事前計算の導入」とある。プリセットの intent_key 変更（例: 自転車貸し出し）を先に反映したうえで、その内容で事前計算スクリプトを回すため、順序は正しい。矛盾なし。
- **管理画面・CSV一括**: embedding を渡さないため、create_faq で従来どおり generate_embedding が呼ばれる。対象外のまま変更なしで一貫している。

---

## 9. ステップ計画（実施順）

全体を **Phase A（精査・修正・30件化）** と **Phase B（埋め込み事前計算）** に分け、実施順に記載する。**指示があるまで実装しない。**

### Phase A: 新規登録時 自動登録FAQ 精査・修正 および 30件化

（参照: `docs/新規登録時_自動登録FAQ_精査・修正_実装計画.md`）

| Step | 内容 | 成果物・確認 |
|------|------|----------------|
| A1 | バックアップ | 変更対象（`faq_presets.py`, `plan_limits.py`, `test_faq_presets.py` 等）を `backups/YYYYMMDD_*` にコピー。 |
| A2 | プリセット内容の修正 | 修正版CSVに基づき `faq_presets.py` を更新（自転車貸し出しへの差し替えは intent_key を `facilities_bicycle_rental` に変更し、全7言語の文言を追加・整合）。 |
| A3 | 自動登録件数 20→30 | `plan_limits.py` の `INITIAL_FAQ_COUNTS` と `filter_faq_presets_by_plan` のスライスを 30 に変更。`test_faq_presets.py` の 20→30 に更新。 |
| A4 | マニュアル・ヘルプの反映 | 「20件」→「30件」の表記を `Manual.vue` 等・ヘルプFAQに反映。必読: `docs/マニュアル更新・改訂_必読.md`。 |
| A5 | テスト（Docker） | `pytest tests/test_faq_presets.py -v` が通ること、必要なら新規登録→30件投入をローカルで確認。 |
| A6 | デプロイ・ステージング確認 | develop にコミット・プッシュ後、ステージングで新規登録またはFAQ件数・内容を確認。 |
| A7 | 関連文書の更新 | 総括・要約定義書の残存課題・変更履歴を更新。 |

### Phase B: 埋め込み事前計算の導入

| Step | 内容 | 成果物・確認 |
|------|------|----------------|
| B1 | バックアップ | 変更対象（`schemas/faq.py`, `faq_service.py`, `auth_service.py`、新規追加するファイル）を `backups/YYYYMMDD_*` にコピー。 |
| B2 | スキーマ拡張 | `FAQTranslationRequest` に `embedding: Optional[List[float]] = None` を追加。 |
| B3 | JSON 構造の確定 | 出力形式を `{"meta": {"model": "...", "generated_at": "..."}, "embeddings": {"intent_key:lang": [...]}}` とし、ローダー・スクリプトで共通利用する。 |
| B4 | 埋め込みローダー（新規） | `backend/app/data/faq_presets_embeddings_loader.py` を追加。モジュールロード時に JSON を読み、`get_preset_embedding(intent_key, language)` を提供。ファイルが無い・キーが無い場合は `None`。 |
| B5 | 事前計算スクリプト（新規） | `backend/scripts/generate_faq_presets_embeddings.py` を追加。`FAQ_PRESETS` を走査し、各 (intent_key, language) で `generate_embedding(question + " " + answer)` を呼び、B3 の形式で JSON 出力。`asyncio.run` で実行。 |
| B6 | 事前計算の実行と JSON のコミット | Docker 上で `OPENAI_API_KEY` を設定しスクリプトを実行。`backend/app/data/faq_presets_embeddings.json` を生成し、リポジトリにコミットする。 |
| B7 | auth_service の変更 | `register_facility_async_faqs` 内で、プリセット→FAQRequest に変換する際に `get_preset_embedding(preset["intent_key"], t["language"])` を取得し、取れた場合にのみ各 translation に `embedding` を付与。取れない場合は警告ログ。 |
| B8 | create_faq の変更 | 各 `trans_request` について、`trans_request.embedding` が存在し長さが 1536 ならそれをそのまま使用。そうでなければ `generate_embedding(combined_text)` を実行。次元数は定数または既存定義の参照を検討。 |
| B9 | テスト | ローダー単体（キー存在時・ファイル無し・キー無し）。可能であれば、プリセット登録経路で `generate_embedding` が呼ばれないことをモックで検証。いずれも Docker 上で実行。 |
| B10 | デプロイ・ステージング確認 | 新規登録でFAQが投入され、RAG検索が期待どおり動くこと、および（ログ等で）埋め込みAPIが登録時に呼ばれていないことを確認。手順: `docs/新規登録時_自動登録FAQ_B10_デプロイとステージング確認手順.md`。 |
| B11 | 文書更新 | 本計画の Status・実施結果、運用注意点（§6）を「実施手順」として参照しやすいよう必要に応じて追記。 |

### 実施順序のまとめ

- **Phase A を先に完了**し、その後に **Phase B** を実施する。これにより、自転車貸し出しを含む確定したプリセット内容で embedding を1回だけ計算し、登録時はコピーのみにできる。
- 両方の指示をいただいた場合、A1→A7 ののち B1→B11 の順で進める。

---

## 10. Status

- **本ドキュメント**: 調査分析・実装案・運用注意点・抜け矛盾の確認・ステップ計画を記載済み。Phase B 実施後、§10.1 実施結果・§10.2 運用時の参照を追記済み。
- **Phase A（精査・修正・30件化）**: **✅ 完了（2026-03-14）**。A1 バックアップ〜A7 関連文書更新まで実施。develop にコミット・デプロイ済み。ステージングで FAQ 30件・マニュアル表示確認済み。
- **Phase B（埋め込み事前計算）**: **✅ 完了（2026-03-14）**。
  - **B1〜B8**: スキーマ拡張・定数・ローダー・スクリプト・auth_service・create_faq の変更を実施。B6 にて事前計算 JSON（210件）を生成・コミット（2b0df2d）。リポジトリに含まれることを確認済み。
  - **B9**: ローダー単体3件＋create_faq 経路（事前計算時は `generate_embedding` 未呼出）1件の計4テストを追加。Docker 上でパス（PostgreSQL 使用時は4件とも実行）。
  - **B10**: 手順書を整備。**2026-03-14 にステージングで実確認完了**。デプロイ後、test4@air-edison.com で新規登録（facility_id=384）→ ブラウザでFAQ 30件確認。Render Logs で登録処理中に「Generating FAQ translation embedding」が無いことを確認（埋め込みAPI未使用）。ゲスト画面（https://yadopera-frontend-staging.onrender.com/f/384/chat）でRAG動作確認（変換プラグ・自転車貸し出しの質問にFAQに基づく回答、信頼度表示）完了。
  - **B11**: 本節（Status・実施結果・運用時の参照）の文書更新で完了。本セッションで全関連文書（本計画・総括・要約定義書・B10手順書）へ実施結果を記録済み。

**Phase B を「完了」とするためのチェックリスト**

| 項目 | 状態 |
|------|------|
| B1〜B8 のコードが develop にコミット・push されている | ✅ 完了（a412cf5） |
| B6 で生成した `faq_presets_embeddings.json` がリポジトリに含まれている | ✅ 確認済み（2b0df2d） |
| B9 のテストファイルがコミットされている | ✅ 完了（a412cf5） |
| B10 手順書に従い、ステージングで新規登録→30件・RAG・ログ確認を実施した | ✅ 完了（2026-03-14） |
| B11 文書更新（本ドキュメント）がコミットされている | ✅ 完了 |

---

### 10.1 Phase B 実施結果（概要）

| Step | 内容 | 成果物・結果 |
|------|------|----------------|
| B1 | バックアップ | 変更対象を `backups/20260314_faq_embedding_precompute_B1/` 等にコピー。 |
| B2 | スキーマ拡張 | `FAQTranslationRequest` に `embedding: Optional[List[float]] = None` を追加。 |
| B3 | JSON 構造 | `faq_presets_embeddings_constants.py` で形式・パス・次元数を定義。 |
| B4 | ローダー | `faq_presets_embeddings_loader.py` を追加。`get_preset_embedding(intent_key, language)` を提供。 |
| B5 | 事前計算スクリプト | `scripts/generate_faq_presets_embeddings.py` を追加。`asyncio.run` で全プリセット×全言語の embedding を生成。 |
| B6 | 事前計算実行 | Docker 上でスクリプト実行。`faq_presets_embeddings.json`（210件）を生成しコミット。 |
| B7 | auth_service | `register_facility_async_faqs` で `get_preset_embedding` を取得し、取れた場合のみ translation に `embedding` を付与。 |
| B8 | create_faq | `trans_request.embedding` が存在し長さ 1536 ならそれを使用。そうでなければ `generate_embedding` を実行。 |
| B9 | テスト | `tests/test_faq_presets_embeddings_loader.py` にローダー3件＋create_faq 経路1件の計4テストを追加。 |
| B10 | デプロイ・ステージング確認 | 手順書を整備。2026-03-14 に実確認完了（デプロイ・FAQ30件・ログで埋め込みAPI未使用・ゲスト画面RAG確認）。 |
| B11 | 文書更新 | 本ドキュメントの Status・実施結果・運用時の参照を更新。全関連文書へ本セッションの作業・結果を記録済み。 |

---

### 10.2 運用時の参照

- **運用注意点（プリセット変更・モデル変更・再生成手順）**: 本ドキュメント **§6 運用時の注意点** を参照すること。
- **embedding 再生成（B6）**: `docs/新規登録時_自動登録FAQ_B6_事前計算実行とコミット手順.md`
- **ステージング確認（B10）**: `docs/新規登録時_自動登録FAQ_B10_デプロイとステージング確認手順.md`

---

**Document Version**: 1.3  
**Last Updated**: 2026年3月14日
