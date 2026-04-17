# 証跡: ステージング「プラン・請求」障害の調査・修正チェーン（2026-04-16〜17）

**作成日**: 2026-04-17  
**対象環境**: Render `yadopera-backend-staging` / `yadopera-frontend-staging`  
**関連ロードマップ**: `docs/20260415_サービス開始ロードマップ.md`（運用・品質ゲートの文脈）

---

## 0. 記録の所在（Owner が即判断するための前提）

| 種類 | 所在 | 備考 |
|------|------|------|
| **変更の正本** | Git `develop` のコミット・差分 | いつでも `git log` / `git show` で復元可能 |
| **会話上の経緯** | Cursor のチャット履歴 | リポジトリ外。設計判断の「なぜ」は主にここ |
| **本ファイル** | `docs/evidence/20260417_staging_plan_billing_remediation.md` | **本インシデント用の証跡に今回初めて集約**（以前の修正を逐次ここへ自動追記していたわけではない） |

**AI エージェントは、ユーザーの明示依頼なしに「ロードマップ本体」や「実行記録」を自動更新していない。**  
以後、同種のインシデントは **本証跡ディレクトリに `YYYYMMDD_...md` を追加する**運用を推奨する。

---

## 1. コミット時系列（新しい順）

| コミット | 概要 |
|----------|------|
| `4628b4f` | `stripe.util` 廃止。`to_dict_recursive` / `to_dict` で dict 化（Render で `ModuleNotFoundError: stripe.util` により起動不能になっていたため） |
| `a212ea8` | 請求一覧: `dict.get("id","")` の罠（値が `None` のとき `None` が返る）を正規化し Pydantic 500 を防止 |
| `227746b` | `convert_to_dict` 導入（後に `stripe.util` 不在で障害化 → `4628b4f` で是正） |
| `07403fb` | プラン言語の明示（API/UI/FAQ）、Stripe `ListObject.data` 修正、`PlanBilling` の `allSettled` 分離 |

**ロールバックを「請求周りだけ」戻したい場合**: 上記を個別 `git revert` するより、**障害直前のコミット**（例: `d01d9d6`）へ Render で **Manual Deploy** する方が Owner 判断は速い（言語表示なども巻き戻る点に注意）。

---

## 2. 症状 → 原因 → 対処の対応表

| 症状 | 原因 | 対処コミット |
|------|------|----------------|
| Stripe API 200 の直後 `Stripe Invoice list failed: get` | stripe-python 7+ の `ListObject` に対し `.get("data")` を使用 | `07403fb` |
| プラン・請求が真っ赤なネットワークエラー / CORS 表示 | バックエンド 500・502 等で **ブラウザが応答を正しく解釈できない**場合に併発し得る | 根本原因は下段 |
| `GET /admin/invoices` が **500** | `InvoiceItemResponse(id=None)` となり **Pydantic ValidationError**（`dict.get("id","")` の仕様） | `a212ea8` |
| デプロイが health check で長時間停滞 | **`ModuleNotFoundError: stripe.util`** でプロセスが import 段階で終了 | `4628b4f` |
| Render Events で「古いデプロイがキャンセル」 | **短時間に複数 push** → Render の重複デプロイ方針 | 運用: push の間隔 / [Overlapping deploy policy](https://render.com/docs/deploys#overlapping-deploys) の確認 |

---

## 3. 触れた主なファイル（`07403fb`〜`4628b4f` の範囲）

- **Backend**: `app/services/stripe_service.py`, `app/api/v1/admin/billing.py`, `app/core/plan_limits.py`, `app/schemas/billing.py`
- **Frontend**: `src/views/admin/PlanBilling.vue`, `Register.vue`, `Manual.vue`, `src/api/billing.ts`
- **LP**: `landing/legal/faq.html`

（言語ラベル系は `07403fb` に含まれる。請求の安定化は `07403fb`〜`4628b4f`。）

---

## 4. Owner が「今すぐ」やるべき確認（デプロイ `4628b4f` Live 後）

1. **管理画面** → **プラン・請求**を開く（ハードリロード推奨）。
2. ブラウザ DevTools **Network**:
   - `.../api/v1/admin/plans` → **200**
   - `.../api/v1/admin/invoices` → **200**、本文に `invoices` 配列
3. Render **Logs**（backend）で起動直後に **import エラーが無い**こと。
4. 問題なしなら本証跡に **「2026-04-17 実測 OK」** と一行追記する（Owner または編集者）。

---

## 5. 再発時の優先順（短く）

1. **Network のステータスコード**（200 / 4xx / 5xx）と **レスポンス JSON の有無**
2. **Backend Logs** の先頭 traceback（import 失敗は数十秒で確定）
3. **直近の `git log develop`** と Render Events の **コミット SHA が一致しているか**（フロントだけ新しくバックが古い、等）

---

## 6. 収束確認ログ（2026-04-17）

### 6.1 実測結果（Owner 共有スクリーンショット反映）

- 実測時刻: 2026-04-17 10:38 JST 前後
- 画面: `https://yadopera-frontend-staging.onrender.com/admin/billing`
- 結果:
  - `GET .../api/v1/admin/plans` → **200**
  - `GET .../api/v1/admin/invoices` → **200**
  - プラン一覧表示正常（言語列の表示含む）
  - Console に請求 API の 4xx/5xx は観測されず

判定: **本インシデントはステージングで収束**。

### 6.2 監視（30〜60分）記録欄

> 注: Render Logs の最終確認は Owner 画面アクセスが必要なため、ここではチェック項目のみ記録する。

- [ ] Render backend logs で `Stripe Invoice list failed` の再発なし
- [ ] Render backend logs で `ModuleNotFoundError` の再発なし
- [ ] `/admin/invoices` の 500 再発なし（Spot-check）
- 監視開始:
- 監視終了:
- 備考:

---

**Document Version**: 1.1
