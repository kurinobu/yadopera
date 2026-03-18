# CSV代行申し込み 送信先修正 — 実行計画（どこから・どのように）

**目的**: Formspree（添付不可）→ 自前API + Brevo（添付対応）に切り替える。  
**参照**: `docs/CSV一括登録_マニュアル・有料オプション・フロート申し込み_実装計画.md` §9  
**再発防止**: 第三者サービス選定・フォーム送信設計時は `docs/20260313_CSV一括登録_代行申し込み_Formspree選定事故_原因と再発防止策.md` の手順（R1〜R4）とルールに従うこと。

---

## ロールバック後ゼロから実装する場合の実行順序

ロールバック後は **CsvBulkRequest.vue・ルート・サイドバー・導線が存在しない**。以下を **この順** で実施する。

| 順 | Phase | 対象 | 内容 |
|----|--------|------|------|
| 1 | バックエンド | EmailService | § Phase 1 のとおりメソッド1つ追加 |
| 2 | バックエンド | 新規 | csv_bulk_request.py ルーター + 1エンドポイント（§ Phase 2） |
| 3 | バックエンド | router.py | ルーター登録（§ Phase 3） |
| 4a | フロント | CsvBulkRequest.vue | **新規作成**。フォーム項目・バリデーション・送信は **最初から** `apiClient.post('/admin/csv-bulk-request', formData)`。Formspree は一切使わない。 |
| 4b | フロント | admin.ts | `/admin/csv-bulk-request` ルート（name: CsvBulkRequest）を追加 |
| 4c | フロント | Sidebar.vue | navItems に「CSV代行の申し込み」→ `/admin/csv-bulk-request` を追加 |
| 4d | フロント | FaqManagement.vue | `canUseCsvBulkUpload` が true のとき「代行をご希望の方はこちら」→ `/admin/csv-bulk-request` を追加 |
| 4e | フロント | HelpModal.vue | 「CSV一括登録の代行をお申し込みの方はこちら」→ `/admin/csv-bulk-request` を追加 |
| 5 | ドキュメント | 運用チェックリスト | `docs/CSV_bulk_registration_function_implementation_plan/` 配下の運用開始チェックリストがロールバックで消えていれば**新規作成**し、§ Phase 5 のとおり ADMIN_NOTIFICATION_EMAIL 必須を記載する。 |

**CsvBulkRequest.vue のフォーム項目（新規作成時の仕様）**: 施設名・プラン・希望登録件数・希望言語（複数チェックボックス: ja, en, zh-TW, zh-CN, fr, ko, es）・連絡メール・担当者名・FAQ内容ファイル（任意、.xlsx/.csv/.txt/.md）・その他要望。施設名・プラン・メール・担当者名は施設APIから自動入力。送信は `apiClient.post('/admin/csv-bulk-request', formData)` のみ。503 時は「申し込み受付は一時的に利用できません。お問い合わせフォームからご連絡ください。」を表示。

---

## 実行順序（既に CsvBulkRequest.vue 等がある場合＝ Formspree 版を修正する場合）

| 順 |  Phase  | 対象 | 内容 |
|----|--------|------|------|
| 1 | バックエンド | EmailService | メソッド1つ追加 |
| 2 | バックエンド | 新規ファイル | ルーター + 1エンドポイント |
| 3 | バックエンド | router.py | ルーター登録 |
| 4 | フロント | CsvBulkRequest.vue | 送信先をAPIに変更 |
| 5 | ドキュメント | 運用チェックリスト | ADMIN_NOTIFICATION_EMAIL 必須を追記 |

---

## Phase 1: EmailService にメソッド追加

**ファイル**: `backend/app/services/email_service.py`

**やること**: クラス `EmailService` の末尾（他メソッドの後）に、次のメソッドを追加する。

- **メソッド名**: `send_csv_bulk_request_email`
- **引数**: `self`, `form_data: dict`, `file_bytes: Optional[bytes] = None`, `filename: Optional[str] = None`
- **戻り**: `bool`（送信成功時 True）
- **処理**:
  1. `settings.admin_notification_email` が空なら `ValueError` を raise（呼び出し元で 503 に変換する想定）。
  2. `form_data` のキー: `csv_facility_name`, `csv_plan`, `csv_desired_count`, `csv_languages`, `csv_email`, `csv_contact_name`, `csv_notes` を HTML の表形式で本文に組み立てる。
  3. 件名: `【YadOPERA】CSV一括登録代行の申し込み`
  4. 宛先: `settings.admin_notification_email`
  5. 添付: `file_bytes` と `filename` が渡されていれば、`attachment=[{"name": filename, "content": base64.b64encode(file_bytes).decode()}]` を `SendSmtpEmail` に渡す。
  6. 既存の `send_verification_email` 等と同様に `self.api_instance.send_transac_email(send_smtp_email)` で送信。

**参照**: 既存の `send_password_reset_email` の構造。Brevo 添付は `SendSmtpEmail(..., attachment=[{"name": "...", "content": "<base64>"}])`。

---

## Phase 2: 新規ルーター + エンドポイント

**新規ファイル**: `backend/app/api/v1/admin/csv_bulk_request.py`

**やること**:

1. **import**: `FastAPI` の `APIRouter`, `Depends`, `File`, `Form`, `HTTPException`, `status`, `UploadFile`。`get_db`, `get_current_user`。`User`, `Facility`。`settings`。`EmailService`。`Optional`。
2. **ルーター**: `router = APIRouter(prefix="/admin/csv-bulk-request", tags=["admin"])`
3. **定数**: `MAX_FILE_SIZE = 10 * 1024 * 1024`（10MB）、`ALLOWED_EXTENSIONS = (".xlsx", ".csv", ".txt", ".md")`
4. **1本のエンドポイント**: `@router.post("", status_code=200)`
   - **認証**: `current_user: User = Depends(get_current_user)`
   - **Form パラメータ**（すべて `Form("")` または `Form(None)`）:  
     `csv_facility_name`, `csv_plan`, `csv_desired_count`, `csv_languages`, `csv_email`, `csv_contact_name`, `csv_notes`
   - **ファイル**: `csv_faq_file: Optional[UploadFile] = File(None)`
   - **処理**:
     1. `admin_notification_email` が空 → `HTTPException(503, detail="申し込み受付は現在利用できません。")`
     2. `current_user.facility_id` が無い → 403
     3. 施設を取得し `plan_type not in ("Standard", "Premium")` → 403
     4. ファイルがある場合: `await csv_faq_file.read()` で読み、サイズ > 10MB → 400。ファイル名の拡張子が `ALLOWED_EXTENSIONS` に無い → 400。
     5. `form_data = { "csv_facility_name": ..., "csv_plan": ..., ... }` を組み立て。
     6. `EmailService()` を生成し、`await email_service.send_csv_bulk_request_email(form_data, file_bytes=読んだbytes or None, filename=元のファイル名 or None)` を呼ぶ。
     7. 成功時 `return {"message": "申し込みを受け付けました。"}`。`EmailService` が `ValueError` を投げたら 503、Brevo API 例外は 500 で返す。

**参照**: `backend/app/api/v1/admin/faqs.py` の `bulk_upload_faqs`（`UploadFile`, `Form`, `get_current_user`, 施設・プランチェック）。

---

## Phase 3: ルーター登録

**ファイル**: `backend/app/api/v1/router.py`

**やること**:

1. 先頭付近の import に追加:  
   `from app.api.v1.admin import ..., csv_bulk_request`  
   （既存の `billing` の後などに `csv_bulk_request` を追加）
2. `api_router.include_router(billing.router, tags=["admin"])` の直後に追加:  
   `api_router.include_router(csv_bulk_request.router, tags=["admin"])`

---

## Phase 4: フロント送信先を API に変更

**ファイル**: `frontend/src/views/admin/CsvBulkRequest.vue`

**やること**:

1. **import 追加**: `import apiClient from '@/api/axios'`（既に他で api を import していればそのクライアントを使用）。
2. **handleSubmit 内**:
   - `fetch('https://formspree.io/f/mvzzapae', ...)` を**削除**。
   - 代わりに:  
     `const response = await apiClient.post('/admin/csv-bulk-request', formData)`  
     （`formData` は既存の `FormData` の組み立てのまま。キー: `csv_facility_name`, `csv_plan`, `csv_desired_count`, `csv_languages`, `csv_email`, `csv_contact_name`, `csv_notes`, およびファイルがあれば `csv_faq_file`。**`_subject` は不要**なので付けなくてよい。）
   - 成功時: `response.status === 200` なら `showSuccessMessage.value = true` 等、既存の成功処理。
   - エラー時: `response.response?.status === 503` なら `submitError.value = '申し込み受付は一時的に利用できません。お問い合わせフォームからご連絡ください。'`、それ以外は `response.response?.data?.detail` またはメッセージを `submitError` に表示。
3. **form タグ**: `action="https://formspree.io/f/mvzzapae"` を削除するか空にする（送信は JavaScript のみ）。

**注意**: `FormData` を `apiClient.post` に渡すときは、Content-Type を設定しない（axios が multipart を自動設定）。

---

## Phase 5: ドキュメント（運用チェックリスト）

**ファイル**: `docs/CSV_bulk_registration_function_implementation_plan/CSV一括登録_有料オプション_運用開始チェックリスト.md`

**やること**: 「環境・設定」または「申し込み受付」の節に以下を追記。

- **CSV代行申し込みフォーム**を利用する場合、バックエンドの環境変数 **`ADMIN_NOTIFICATION_EMAIL`**（運営あてメールアドレス）の設定が**必須**。未設定時は申し込みAPIが 503 を返す。

---

## 確認チェックリスト（修正後）

- [ ] バックエンド: `POST /api/v1/admin/csv-bulk-request` に FormData（項目 + 任意でファイル）を送ると 200 が返る。
- [ ] バックエンド: `admin_notification_email` 未設定時は 503。
- [ ] バックエンド: Standard/Premium 以外の施設ユーザーでは 403。
- [ ] バックエンド: 添付が 10MB 超または拡張子が .xlsx/.csv/.txt/.md 以外なら 400。
- [ ] 運営メールボックス（admin_notification_email）に、申し込み内容のメールと添付ファイル（付けた場合）が届く。
- [ ] フロント: 申し込み画面で送信 → 「申し込みを受け付けました」と表示される。
- [ ] フロント: 503 のとき「申し込み受付は一時的に利用できません…」と表示される。

---

**この順で実施すれば、Formspree に依存せず添付付きで申し込みが運営に届く。**
