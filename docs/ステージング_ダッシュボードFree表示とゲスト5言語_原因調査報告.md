# ステージング環境：ダッシュボード Free 表示・ゲスト 5 言語のみ表示 — 原因調査報告

**日付**: 2026-03-11  
**対象**: デプロイ完了後のステージング（yadopera-frontend-staging.onrender.com）  
**指示**: 原因の調査分析の上報告。修正は行わない。

---

## 1. 現象の整理

| 現象 | 内容 |
|------|------|
| **A. ダッシュボードのプラン表示** | プラン・請求ページで Free → Premium に変更済みで「(現在)」は Premium と表示されるが、ダッシュボードの「利用状況」では「Freeプラン」のまま。強制リロード・サイトデータ消去でも変わらない。 |
| **B. ゲスト画面の言語カード** | 5 枚の言語カードのみ表示（日本語・英語・繁体中文・フランス語・韓国語）。ドイツ語・ベトナム語は表示されていない（想定通り）。簡体中国語・スペイン語が表示されていない（多言語_5 では追加想定）。 |

---

## 2. 現象 A：ダッシュボードが Free のままになる原因

### 2.1 データの流れ

- **プラン・請求ページ（/admin/billing）**  
  - `GET /admin/plans` を呼ぶ。  
  - バックエンドは **DB の `facility.plan_type` をその場で読んで** `current_plan_type` を返す。  
  - キャッシュは使っていない。  
  - そのため、プラン変更後はすぐ「Premium（現在）」と表示される。

- **ダッシュボード（/admin/dashboard）**  
  - `GET /admin/dashboard` を呼ぶ。  
  - バックエンドは **Redis にキャッシュしたダッシュボード全体**（`monthly_usage` 含む）を返す。  
  - キャッシュ TTL は **300 秒（5 分）**（`dashboard_service.py` の `DASHBOARD_CACHE_TTL`）。  
  - キャッシュヒット時は DB を読まず、**古い `plan_type`（例: Free）のまま** `monthly_usage` が返る。

### 2.2 根本原因

- **ダッシュボード API が 5 分間キャッシュしており、プラン変更時にそのキャッシュを破棄していない。**
  - 実装: `backend/app/services/dashboard_service.py` の `get_dashboard_data()` で、`cache_key("dashboard:data", facility_id=facility_id)` をキーに Redis へキャッシュ。
  - プラン変更: `backend/app/api/v1/admin/billing.py` の `change_plan()` で `facility.plan_type` 等を更新して `db.commit()` しているが、**ダッシュボード用キャッシュの削除・無効化は行っていない**。
- その結果、
  - プラン変更直後: DB は Premium、プラン・請求は DB 参照のため Premium 表示。
  - ダッシュボード: キャッシュに古い「Free」入りレスポンスが残っているため、最大 5 分間は「Freeプラン」のまま。
- 強制リロードやサイトデータ消去では **サーバー側（Redis）のキャッシュは消えない**ため、現象が続く。

### 2.3 結論（現象 A）

| 項目 | 内容 |
|------|------|
| 原因 | ダッシュボード API の 5 分キャッシュを、プラン変更 API が無効化していないため。 |
| 参照コード | `dashboard_service.py` 74–81 行（キャッシュ取得）、`billing.py` の `change_plan`（キャッシュ削除なし） |
| 補足 | 同一施設・同一 DB の `facility.plan_type` を両方とも参照しているが、プラン API は常に DB、ダッシュボード API はキャッシュ優先。 |

---

## 3. 現象 B：ゲスト画面で 5 言語のみ表示される原因

### 3.1 データの流れ

- ゲストの言語選択画面で表示する言語カードは、**バックエンドの公開 API**  
  `GET /api/v1/facility/{slug}` のレスポンスの **`available_languages`** で決まる。
- フロントは `SUPPORTED_LANGUAGES`（定数）を、この `available_languages` でフィルタして表示している（`LanguageSelect.vue`）。
- `available_languages` は **施設の `plan_type` に応じて** `backend/app/services/facility_service.py` で組み立てられる。

### 3.2 現行コード（feature/multilingual-5 適用後）の挙動

- Premium の場合、`facility_service.py` で次を返すように実装されている。  
  `["ja", "en", "zh-TW", "zh-CN", "fr", "ko", "es"]`（7 言語、zh-CN・es 含む）。
- バックアップ（`facility_service.py.bak_20260117_215613`）では、**旧実装の Premium** は  
  `["ja", "en", "zh-TW", "fr", "ko"]` の **5 言語** だった。

### 3.3 根本原因

- ステージングの **バックエンド** が、**多言語_5 対応後のコード**（Premium で 7 言語を返す版）にまだ更新されていないと判断できる。
- そのため、ステージングの `GET /api/v1/facility/{slug}` は、**旧ロジック**に従い Premium 施設に対しても  
  `available_languages = ["ja", "en", "zh-TW", "fr", "ko"]` の 5 言語を返している。
- 結果として、
  - ドイツ語・ベトナム語が無い → 旧仕様でも含まれておらず、フロントの `SUPPORTED_LANGUAGES` からも削除済みのため表示されない（想定通り）。
  - 簡体中国語・スペイン語が無い → 旧バックエンドはこれらを `available_languages` に含めておらず、7 言語に拡張した新バックエンドがステージングにデプロイされていないため。

### 3.4 結論（現象 B）

| 項目 | 内容 |
|------|------|
| 原因 | ステージングにデプロイされているバックエンドが、多言語_5（zh-CN・es 追加）対応前のコードのままであるため。Premium の `available_languages` が 5 言語のまま返っている。 |
| 参照コード | `facility_service.py` 146–152 行（現行は Premium で 7 言語）、旧実装バックアップ（5 言語） |
| 補足 | フロントは `available_languages` をそのまま使っているため、バックエンドのレスポンスが 5 言語なら 5 枚のカードになる。 |

---

## 4. まとめ

| 現象 | 原因 | 修正の方向性（参考・指示があるまで実装しない） |
|------|------|-----------------------------------------------|
| **A. ダッシュボードが Free のまま** | ダッシュボード API の 5 分キャッシュを、プラン変更時に無効化していない。 | プラン変更 API（`change_plan`）実行時に、当該施設のダッシュボードキャッシュ（`dashboard:data`, facility_id）を削除する。既存の `delete_cache` / `delete_cache_pattern` を利用可能。 |
| **B. ゲストで 5 言語のみ** | ステージングのバックエンドが多言語_5 対応前のコードのため、Premium でも 5 言語の `available_languages` を返している。 | `feature/multilingual-5-zhcn-es-remove-de-vi` を `develop` にマージし、ステージングのバックエンドをそのブランチ（またはマージ後の develop）で再デプロイする。 |

---

## 5. 追記（2026-03-11 解消）

**現象 B（ゲストで 5 言語のみ）** は、同日に多言語_5 を develop にマージしステージングを再デプロイしたことで **解消済み**。ステージングで `RENDER_GIT_COMMIT=7a828ca...` を確認し、Premium 施設の `available_languages` が 7 言語で返ること、ゲスト画面で 7 枚の言語カードが表示されることをブラウザ検証済み。現象 A（ダッシュボードのプラン表示不整合）は残存課題のまま。

**追記（2026-03-17）**: 現象 A は、修正計画 Phase 1 実施後に利用者がステージングでプラン変更→表示一致を確認したことで **解消**。総括 §3.1 を「✅ 完了（2026-03-17）」に更新済み。参照: `docs/プランページとダッシュボード_プラン表示不整合_修正計画.md` §7・§8。

以上。
