# 3b | 宿泊施設名・メールアドレス一覧のCSVダウンロード機能 — 実装計画

**作成日**: 2026年3月10日  
**対象**: 計画「3b」開発者ダッシュボードから施設名・メールアドレス一覧をCSVでダウンロードする機能  
**基準**: 要約定義書 v0.3、アーキテクチャ設計書 v0.3、20260307_プロジェクト現況と今後の計画_総括、大原則、3a 実装計画

---

## 1. 目的・スコープ

- **目的**: 開発者管理ダッシュボードの「施設一覧」において、全施設の**施設名**と**メールアドレス**をCSVファイルとしてダウンロードできるようにする。
- **スコープ**: 3b のみ。開発者認証必須。出力項目は「施設名」「メールアドレス」の2列（必要に応じてIDやプラン等は拡張可能だが、まずは要件どおり2列とする）。
- **前提**: 3a により `GET /api/v1/developer/stats/facilities` は既に `email` を返却済み。データソースは同一（`facilities` テーブル）であり、DBマイグレーションは不要。

---

## 2. 大原則との対応

| 原則 | 対応 |
|------|------|
| 根本解決 > 暫定解決 | 施設マスタ（facilities）を正の情報源とし、既存APIと同一クエリで一貫性を保つ。 |
| シンプル構造 > 複雑構造 | 既存の「リードCSVエクスポート」パターン（StreamingResponse + CSV）を流用する。 |
| 統一・同一化 > 特殊独自 | バックエンドは `admin/leads.py` の `export_leads_csv`、フロントは `Leads.vue` + `leadsApi.exportCsv` のパターンに準拠する。 |
| 具体的 > 一般 | 変更対象ファイル・手順を本計画に明示する。 |
| 拙速 < 安全確実 | Docker で動作確認してからマージする。 |
| Docker環境必須 | すべての修正・テストは Docker 環境（docker-compose）で実行する。 |

---

## 3. コードベース調査結果

### 3.1 現状

- **バックエンド**
  - `GET /api/v1/developer/stats/facilities` が施設一覧を返す（`FacilitySummaryResponse`: id, name, email, is_active, plan_type, faq_count, chats_7d, errors_7d, last_admin_login）。
  - 開発者認証: `get_current_developer`（Deps）。ルーター: `backend/app/api/v1/developer/__init__.py` で `stats_router` が `prefix="/stats"` でマウント。よって施設一覧は `/api/v1/developer/stats/facilities`。
  - 既存CSVエクスポート: `backend/app/api/v1/admin/leads.py` の `GET /admin/leads/export` が `StreamingResponse` + `csv.writer` + `Content-Disposition: attachment; filename=leads.csv` で実装されている。
- **フロントエンド**
  - `DeveloperDashboard.vue`: 施設一覧テーブル表示、`developerApi.getFacilities()` で取得。施設名・メールアドレス列あり（3a 完了）。
  - 既存CSVダウンロード: `frontend/src/api/leads.ts` の `exportCsv()` が `responseType: 'blob'` で取得。`Leads.vue` で Blob → `URL.createObjectURL` → `<a download>.click()` でダウンロード。
- **Docker**
  - `docker-compose.yml`: backend (8000), frontend (5173), postgres, redis。検証は `docker-compose up -d` で実施（大原則・README準拠）。
- **ブランチ戦略**（要約定義書 v0.3.1）
  - `main`（本番）、`develop`（ステージング）、`feature/*`（開発）。本タスクは `develop` から `feature/developer-facilities-csv-export` を作成し、完了後に `develop` へマージする。

### 3.2 参照した既存実装

| ファイル | 参照内容 |
|----------|----------|
| `backend/app/api/v1/admin/leads.py` | CSV 出力（csv.writer, io.StringIO, StreamingResponse, Content-Disposition） |
| `backend/app/api/v1/developer/stats.py` | 施設一覧取得・get_current_developer・FacilitySummaryResponse |
| `frontend/src/api/leads.ts` | exportCsv(): responseType: 'blob' |
| `frontend/src/views/admin/Leads.vue` | handleExportCsv: blob → ダウンロードトリガー |

---

## 4. 実装ステップ

### Step 1: バックエンド — CSV エクスポートエンドポイント追加

| 項目 | 内容 |
|------|------|
| ファイル | `backend/app/api/v1/developer/stats.py` |
| 変更 | 新規エンドポイント `GET /stats/facilities/export` を追加。 |
| 仕様 | 開発者認証必須（`get_current_developer`）。施設一覧は既存の `get_facilities_summary` と同様のクエリで取得するが、レスポンスは JSON ではなく CSV（StreamingResponse）。 |
| CSV形式 | ヘッダー: `施設名,メールアドレス`（UTF-8）。2行目以降: `name, email`。BOM は付与する（Excel 等で文字化けしないよう）。 |
| ファイル名 | `Content-Disposition: attachment; filename="facilities_YYYY-MM-DD.csv"`（日付はサーバー日時で可）。 |

**実装メモ**:
- `import csv`, `import io` を追加。
- 既存の施設取得ロジック（Facility 一覧＋email）を流用するため、同じサブクエリ・メインクエリで Facility の id, name, email を取得し、CSV に name, email のみ書き出す。
- 既存 `get_facilities_summary` のクエリを共通化するか、export 用に簡易クエリ（select Facility.id, Facility.name, Facility.email order_by Facility.id）のみで十分。シンプルに「全 Facility の name, email を取得」するクエリでよい。

### Step 2: フロントエンド — API クライアントに CSV 取得を追加

| 項目 | 内容 |
|------|------|
| ファイル | `frontend/src/api/developer.ts` |
| 変更 | `developerApi` に `exportFacilitiesCsv(): Promise<Blob>` を追加。`getDeveloperApiClient().get('/stats/facilities/export', { responseType: 'blob' })` で Blob を返す。 |

### Step 3: フロントエンド — 開発者ダッシュボードに CSV ダウンロードボタン追加

| 項目 | 内容 |
|------|------|
| ファイル | `frontend/src/views/developer/DeveloperDashboard.vue` |
| 変更 | 「施設一覧」セクションの見出し横（またはテーブル上）に「CSVダウンロード」ボタンを追加。クリックで `developerApi.exportFacilitiesCsv()` を呼び、Blob から `facilities_YYYY-MM-DD.csv` でダウンロード（Leads.vue と同様のパターン）。ローディング中はボタン無効または「ダウンロード中...」表示。 |

### Step 4: Docker での動作確認

1. `docker-compose up -d` で起動。
2. 開発者ログイン → ダッシュボードで「CSVダウンロード」をクリックし、CSV がダウンロードされることを確認。
3. CSV の内容: 1行目が `施設名,メールアドレス`、2行目以降に施設名・メールが並ぶことを確認。文字化けなし（UTF-8 BOM 確認）。
4. 必要に応じて Swagger (`/docs`) で `GET /api/v1/developer/stats/facilities/export` のレスポンスが CSV であることを確認。

### Step 5: マージ

- `feature/developer-facilities-csv-export` を `develop` にマージ。
- ステージングデプロイ後、開発者ダッシュボードで CSV ダウンロードを再確認推奨。

---

## 5. 変更ファイル一覧（予定）

| レイヤー | ファイル | 変更内容 |
|----------|----------|----------|
| Backend | `backend/app/api/v1/developer/stats.py` | GET /stats/facilities/export 追加（CSV StreamingResponse）、csv/io 利用 |
| Frontend | `frontend/src/api/developer.ts` | exportFacilitiesCsv(): Promise<Blob> 追加 |
| Frontend | `frontend/src/views/developer/DeveloperDashboard.vue` | 「CSVダウンロード」ボタンと handleExportFacilitiesCsv 追加 |

---

## 6. CSV 仕様（確定）

- **文字コード**: UTF-8（BOM 付き推奨、Excel での文字化け防止）。
- **ヘッダー**: `施設名,メールアドレス`。
- **データ行**: 各施設の `name`, `email`。`email` が空の場合は空文字列。
- **ファイル名**: `facilities_YYYY-MM-DD.csv`（クライアントで日付生成で可、またはサーバーで Content-Disposition に含めても可）。

---

## 7. リスク・注意

- **個人情報**: 開発者画面は開発者認証必須のため、メールアドレスを含むCSVは認証済み運用者のみが取得する。3a と同様に扱う。
- **件数**: 施設数は現状数十規模の想定のため、メモリ上に全件展開してCSV生成で問題ない。将来施設数が大幅に増えた場合はストリーミング生成を検討可能。
- **認証**: 既存の開発者JWT（Bearer）で保護する。フロントは既存の `getDeveloperApiClient()` によりトークンを付与する。

---

## 8. 参照

- `docs/20260307_プロジェクト現況と今後の計画_総括.md` §3.1 残存課題（3b）、§7.1 短期計画
- `docs/Summary/yadopera-v03-summary.md` 大原則・ブランチ戦略
- `docs/開発者ダッシュボード_メールアドレス表示追加_実装計画_3a.md` 3a 計画・ブランチ・Docker 方針
- `docs/開発者ダッシュボード_メールアドレス表示_Step3_Docker動作確認とブラウザテスト準備.md` Docker 起動・ブラウザテスト手順
- `backend/app/api/v1/admin/leads.py`（CSV エクスポートパターン）
- `backend/app/api/v1/developer/stats.py`（施設一覧API）
- `frontend/src/api/leads.ts`, `frontend/src/views/admin/Leads.vue`（CSV ダウンロードUI パターン）

---

**Document Version**: 1.0  
**Last Updated**: 2026年3月10日  
**Status**: 実装計画のみ。指示があるまで実装しない。
