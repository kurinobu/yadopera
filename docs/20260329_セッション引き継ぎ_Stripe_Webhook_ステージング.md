# セッション引き継ぎ: Stripe Webhook（ステージング）2026-03-29

**目的**: 次セッションで憶測なく再開するため、**観測された事実・確定した原因・未完了**だけを記録する。  
**対象**: `yadopera-backend-staging`（Render）× Stripe **テスト／サンドボックス** × Webhook `/api/v1/webhooks/stripe`。

---

## 1. 確定した事実（観測ベース）

### 1.1 Render ステージングの Stripe キーが属するアカウント

- **環境変数 `STRIPE_SECRET_KEY`**（利用者が Render で表示した値）は  
  `sk_test_51T4aV5LnkMufdVqu...` で始まる。
- Stripe の規則上、`sk_test_51` の直後の断片 `T4aV5LnkMufdVqu` は **アカウント ID `acct_1T4aV5LnkMufdVqu`** に対応する。
- **結論**: API（Customer / Subscription 作成）は **`acct_1T4aV5LnkMufdVqu`** 上で動いている。

### 1.2 別 Stripe コンテキスト（会話前半で混在したもの）

- 別のスクショ・URL では **`acct_1T4aUMPw8Sx3ll4T`** 上の Webhook 送信先名 **`adventurous-splendor`** が使われていた。
- **`acct_1T4aUMPw8Sx3ll4T` と `acct_1T4aV5LnkMufdVqu` は別アカウント（別 `acct_...`）**である。
- **`adventurous-splendor` の署名シークレット（`whsec_...`）を `STRIPE_WEBHOOK_SECRET` に入れた場合、`acct_1T4aV5LnkMufdVqu` から飛ぶ Webhook の署名と一致しない**ため、**400（署名検証失敗）**になりうる。

### 1.3 `acct_1T4aV5LnkMufdVqu` 側の Webhook（利用者スクショ）

- 送信先名の例: **`empowering-euphoria`**
- 送信先 URL: `https://yadopera-backend-staging.onrender.com/api/v1/webhooks/stripe`
- ダッシュボード表示: **「YadOPERA サンドボックス」**（サンドボックス／テスト系 UI）
- **Stripe ワークベンチの「イベント」**で `test2@air-edison.com` の `customer.subscription.created` 等を確認。**「Webhook エンドポイントへの配信」が `400 ERR`** と表示された事例あり。

### 1.4 バックエンドログで確認されたこと（過去・共有ログ）

- `POST /api/v1/auth/register` 成功後、Stripe API へ `customers` / `subscriptions` が **HTTP 200**。
- ログに **`Stripe Customer and Subscription created for facility_id=387, plan_type=Mini`**（`test1@air-edison.com` 登録時系列）。
- 続けて **`Stripe Webhook signature verification failed`** と **`POST .../webhooks/stripe` 400** の記録あり。
- **`GET .../webhooks/stripe` が 405** は、ブラウザ等での GET が仕様どおり拒否されたもの（Webhook は POST のみ）。

### 1.5 環境変数の正しい対応（コード・ドキュメント上の定義）

| 変数名 | 中身の種類 | 先頭の例 |
|--------|------------|----------|
| `STRIPE_SECRET_KEY` | API 用シークレットキー | `sk_test_...` / `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Endpoint 署名シークレットのみ | `whsec_...` |

**`whsec_...` を `STRIPE_SECRET_KEY` に入れてはならない**（逆も同様）。

### 1.6 リポジトリに入れたコード変更（2026-03-29）

- ファイル: `backend/app/api/v1/webhooks/stripe.py`
- 内容: `STRIPE_WEBHOOK_SECRET` と `Stripe-Signature` ヘッダを **`strip()`** してから `construct_event` に渡す（Render 等で環境変数末尾に改行が混入するケースの緩和）。
- **注意**: **アカウント取り違えによる署名不一致の根本解決にはならない**。正しい `whsec` と **同一 `acct`** が必須。

---

## 2. 確定した原因（上記事実からの論理）

- **主因**: **`STRIPE_SECRET_KEY` が属する Stripe アカウント（`acct_1T4aV5LnkMufdVqu`）と、`STRIPE_WEBHOOK_SECRET` を取得した Webhook Endpoint が属するアカウントが一致していなかった期間があった**（別 `acct` の `adventurous-splendor` の `whsec` を参照していた可能性が高い）。
- **正しい組み合わせ**:  
  **`sk_test_51T4aV5LnkMufdVqu...` と、同一ダッシュボード（URL の `acct_1T4aV5LnkMufdVqu`）上の、staging URL 向け Endpoint の `whsec_...` を `STRIPE_WEBHOOK_SECRET` に設定する。**

---

## 3. 利用者が実施した対応（会話上の報告）

- **`acct_1T4aV5LnkMufdVqu` の `empowering-euphoria`（同一 staging URL）の署名シークレットを `STRIPE_WEBHOOK_SECRET` に設定**し、**Save → デプロイ完了**まで実施した、との報告あり。

---

## 4. Webhook 署名検証の確認手順と実施結果

### 4.1 実施結果（2026-03-29 追記・証跡）

**環境**: Render → `yadopera-backend-staging` → **Logs** → 検索語 **`webhooks/stripe`**、期間 **Last 4 hours**（「Last hour」だけだと修正後の行が見えないことがある）。

| 時刻（ログ表示・ローカル） | メソッド | 結果 |
|----------------------------|----------|------|
| 10:23〜11:43 頃（複数行） | POST | **400**（署名不一致だった期間の記録として残存） |
| 10:47 頃 | GET | **405**（ブラウザ等の GET。仕様どおり） |
| **2026-03-29 12:42:54** | POST | **200 OK** ← **同一エンドポイントで署名検証通過** |

**結論**: `acct_1T4aV5LnkMufdVqu` 側 Endpoint の `whsec_...` を **`STRIPE_WEBHOOK_SECRET` に合わせた後**、**新しい `POST .../webhooks/stripe` が 200** であることを確認済み。

### 4.2 参考（同種トラブル時の切り分け）

**秘密鍵修正・デプロイ後も、Render Logs の「Last hour」には古い `POST 400` だけが残ることがある。**  
環境変数更新は **過去のログ行を書き換えない**。

新しい `POST` 行を発生させる例:

1. **Stripe**（同一 `acct_...`・ワークベンチ **イベント**）で該当イベントを開き、**「Webhook エンドポイントへの配信」に「再送」がある場合のみ**実行する。
2. **別メールで新規登録（有料プラン）**を 1 回行う。

**成功の定義**: 新しい POST が **200** かつ **`signature verification failed` が出ない**。

---

## 5. Stripe UI に関する事実（手戻りの記録）

- **ワークベンチの「ログ」（`/test/workbench/logs`）**は、**Webhook 配信専用の一覧ではない**ことがあり、フィルタ次第で **0 件**になりやすい。
- **送信先詳細の「イベントの配信」**も、利用者環境では **0 件表示**だった一方、**「イベント」タブの個別イベント詳細内の「Webhook エンドポイントへの配信」**では **400 ERR** が見えた。**画面によってログの出方が違う**。
- **「テストイベントを送信する」**は、利用者環境では **Stripe CLI 利用案内のモーダル**になり、ブラウザだけでイベントを選んで送る UI とは限らない。

→ **次セッションでは「画面名と URL」をセットで書く**こと。憶測で「必ずここに出る」と書かない。

---

## 6. セキュリティ（事実）

- 会話・スクショ経由で **`sk_test_...` が外部に露出した可能性**がある。運用上問題なければ **Stripe ダッシュボードでテスト用シークレットキーをローテーション**し、Render の `STRIPE_SECRET_KEY` を差し替えることを推奨。

---

## 7. 実装計画・Runbook との関係

- **§6.5** の Webhook 確認は **ステージングで実施する必要がある**方針は変わらない（ローカルのみでは代替にならない）。
- **技術的主因**は §2 のとおり **`acct` / `whsec` の不一致**。あわせて **対話アシスタントの誘導ミス**が時間損失を増幅した。失敗の一覧は **§9**。
- 対策は **Runbook §3.4.1.1** および本引き継ぎ書への集約。

---

## 8. 参照リンク（リポジトリ内）

| ファイル | 内容 |
|----------|------|
| `docs/サービス開始までの手順_Runbook.md` | §3.4.1.1（アカウント整合・検証手順） |
| `docs/サービス開始までの手順整理_実装計画.md` | §6.4 / §6.5 から本書への参照 |
| `backend/app/api/v1/webhooks/stripe.py` | Webhook 受信・署名検証・`strip()` |
| `docs/README.md` | 本引き継ぎ書への索引 |

---

## 9. 対話アシスタント（AI）側の失敗・再発防止（セッション事実）

以下は **当該セッションの会話・共有物から特定できる失敗**である。利用者の操作ミスではなく、**誘導・説明の欠陥**として記録する。

| # | 失敗内容 | 結果・影響 | 再発防止（文書・運用） |
|---|----------|------------|------------------------|
| 1 | **Render の `STRIPE_SECRET_KEY`（`sk_test_...`）から `acct_...` を突き合わせず**、別 URL の **`acct_1T4aUMPw8Sx3ll4T` / `adventurous-splendor` を前提に手順を書いた** | 合わない `whsec` を貼るループ、400 が長く続く | **先に `sk_test_51` 直後の断片 ⇔ `acct_1` + 同一断片を確認**してから Webhook 画面の URL を指定する（Runbook §3.4.1.1） |
| 2 | 上記と独立に、**同一 `whsec` の貼り直し・デプロイを繰り返す指示**が続いた | 利用者の時間浪費、不信感 | **文字列が同じでも acct が違えば直らない**ことを最初に検証。貼り直しは「acct 整合確認後」の 1 回に限定 |
| 3 | スクショ OCR／読み取りに基づき **`whsec` の 1 文字違いを指摘**したが、利用者が貼った 2 行は同一だった | 混乱・「憶測」との指摘 | **秘密値の照合は人間がコピペした平文を正**とし、画像 OCR だけで断定しない |
| 4 | **「顧客一覧に必ず出る」「イベントの配信タブに行が並ぶ」**など、Stripe UI を**断定**した | 実画面と食い違い、強いストレス | **画面名・URL をセットで書く**。「0 件になりうる」と Runbook 同様に注記 |
| 5 | **「テストイベントを送信」→ ブラウザでイベントを選ぶ**と説明したが、利用者環境では **Stripe CLI 案内モーダル**だった | 手順と画面が噛み合わない | **実際の UI（CLI 案内）を前提に**、代替は「再送」「新規登録」等と明示 |
| 6 | **ワークベンチ「ログ」**を Webhook 配信確認先として扱いがちだった | フィルタで 0 件、手戻り | **配信の一次確認は Render Logs の `POST` 行**、またはイベント詳細内の配信ブロック |
| 7 | **「フィルタを触れるなら」「あれば」**など条件だらけの次手 | 「次の一手」にならない | **命令形 1 手ずつ**、または **URL 直打ち 1 本** |
| 8 | Stripe と Render を**同じ返信内で行き来**させ、利用者がどちらの製品画面か迷う | 混乱 | **製品名（Stripe / Render）を見出しで分ける** |
| 9 | 利用者が **`whsec` を `STRIPE_SECRET_KEY` に貼ったのでは**と誤解しうるほど、**変数名の言い回しが紛らわしい**場面があった | 不信感 | 本書 §1.5 と Runbook で **`sk_` / `whsec_` / 変数名を表で固定** |

**注**: 上記は **特定セッションの反省用**であり、将来の AI 利用時は **本節と §5 を読んでから**手順を書くこと。

---

**記録者**: セッション終了時点の会話・共有ログ・スクショ説明に基づく整理。  
**次アクション（2026-03-30 更新）**: Webhook **`acct` / `whsec` 整合**・**POST 200** は当セッション〜追記で収束。**実装計画 §6.5** のステージングチェックリスト **1〜6** は `docs/20260328_サービス開始ロードマップ_実行記録.md` で証跡付き完走（うち 6 は **イベント再送 → 200** まで確認。「意図的 5xx」は未実施）。**以降**: 必要なら **テスト鍵ローテーション**（本書 **§6. セキュリティ**）、**残存課題**（請求履歴 JPY `/100`、領収・請求の消費税表示）、**ロードマップ段3以降**（`docs/サービス開始までの手順整理_実装計画.md` §6）。
