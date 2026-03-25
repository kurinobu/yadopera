# Backend スクリプト一覧

開発・運用で使用するスクリプトの概要と実行例。

---

## CSV一括登録 代行履行用（方法C・バックアップ）

**第一選択（2026-03-21〜）**: 開発者管理画面からの投入（**方法D**）。`POST /api/v1/developer/facilities/{facility_id}/faqs/bulk-upload` および UI。詳細は `docs/FAQ_CSV一括登録_翻訳生成_必須ルール_AIと運営向け.md` §5.3.0、`docs/20260321_CSV一括登録_開発者管理画面からの実行_実装計画.md`。

**スクリプト**: `bulk_upload_faq_csv_for_facility.py`  
**用途**: 指定施設にCSVからFAQを一括登録する（有料代行サービス履行用）。**方法D が使えない場合・障害時・緊急時・オフライン検証**のバックアップ。`uploaded_by` は **`--user-email` 指定時はそのユーザー**、**`--facility-id` のみのときは施設に紐づく先頭1ユーザー**。

**実行例**

- **Docker（推奨・リポジトリルートで）**
  ```bash
  # CSVをコンテナから読める場所へ（例: backend/tmp に置き ./backend が /app にマウントされている場合）
  docker compose exec backend python scripts/bulk_upload_faq_csv_for_facility.py --user-email user@example.com --csv /app/tmp/faq.csv
  # または施設ID指定
  docker compose exec backend python scripts/bulk_upload_faq_csv_for_facility.py --facility-id <施設ID> --csv /app/tmp/faq.csv
  ```
- **ドライラン**: 上記の末尾に `--dry-run` を付与
- **ローカル**（`DATABASE_URL` 等が設定されている場合）
  ```bash
  cd backend
  python scripts/bulk_upload_faq_csv_for_facility.py --user-email user@example.com --csv /path/to/faq.csv
  ```

**詳細**: 料金表・受注〜履行の流れ・CSVフォーマットは以下を参照。

- `docs/CSV_bulk_registration_function_implementation_plan/開発者によるCSV一括登録代行_手順と方法_20260212.md`
- `docs/CSV_bulk_registration_function_implementation_plan/CSV一括登録_有料オプション_運用開始チェックリスト.md`
- `docs/CSV_bulk_registration_function_implementation_plan/files/FAQ_CSV_format_guide.md`

---

## その他のスクリプト

| スクリプト | 用途 |
|------------|------|
| `apply_faq_presets.py` | 指定施設にFAQプリセットを一括投入（`--facility-id`, `--dry-run`） |
| その他 | 検証・テスト用スクリプト（必要に応じて実行） |
