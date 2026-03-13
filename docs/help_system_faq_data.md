# 宿泊事業者向けFAQデータ（48項目）

**プロジェクト**: YadOPERA Phase 2 統合ヘルプシステム  
**作成日**: 2025-12-26  
**最終更新日**: 2026年3月2日  
**言語**: 日本語・英語

**現行の定義**: 全48項目・11カテゴリ。データの正は `backend/scripts/insert_operator_faqs.py` の `OPERATOR_FAQ_DATA`。DB反映は `update_operator_faqs.py`。実施計画・ステップ実施記録・デプロイ時手順は `docs/施設管理者向けヘルプチャットFAQ_マニュアル水準化_調査と計画.md` を参照。

**カテゴリ（11）**: setup, qrcode, faq_management, ai_logic, logs, troubleshooting, billing, security, overnight_queue, guest, practice。フロントの表示ラベル（日本語）は `CategoryFilter.vue` および `FaqItem.vue` の `labels` で定義。

---

## Category: setup（初期設定） - 5項目

### FAQ 1: setup_account_creation

**intent_key**: `setup_account_creation`  
**display_order**: 100  
**category**: `setup`

#### 日本語 (ja)
- **質問**: アカウント作成の手順は？
- **回答**: 管理画面トップページから「新規登録」をクリックし、メールアドレス・パスワード・施設情報を入力してください。メール認証後、ログインできます。初回ログイン時に施設設定の入力をお願いします。
- **キーワード**: アカウント作成,新規登録,サインアップ,初期設定,アカウント開設
- **関連URL**: /admin/register

#### 英語 (en)
- **Question**: How to create an account?
- **Answer**: Click "Sign Up" from the top page, enter your email, password, and facility information. After email verification, you can log in. Please complete facility settings on first login.
- **Keywords**: account creation,sign up,registration,initial setup,account opening
- **Related URL**: /admin/register

---

### FAQ 2: setup_facility_info

**intent_key**: `setup_facility_info`  
**display_order**: 95  
**category**: `setup`

#### 日本語 (ja)
- **質問**: 施設情報はどこで登録しますか？
- **回答**: ログイン後、「設定」→「施設設定」から施設名、住所、チェックイン/アウト時間、WiFi情報、部屋数などを登録できます。これらの情報はゲストへの自動応答に使用されます。ゲストに表示するかは「ゲスト画面にメールアドレスを表示する」スイッチで変更できます。
- **キーワード**: 施設情報,施設設定,基本情報,WiFi設定,施設登録
- **関連URL**: /admin/facility

#### 英語 (en)
- **Question**: Where do I register facility information?
- **Answer**: After login, go to "Settings" → "Facility Settings" to register facility name, address, check-in/out times, WiFi info, room count, etc. This information is used for automatic guest responses. You can turn the "Show email on guest screen" switch on or off to show or hide the facility email to guests.
- **Keywords**: facility information,facility settings,basic info,WiFi settings,facility registration
- **Related URL**: /admin/facility

---

### FAQ 3: setup_first_login

**intent_key**: `setup_first_login`  
**display_order**: 90  
**category**: `setup`

#### 日本語 (ja)
- **質問**: 初回ログイン後にまずやるべきことは？
- **回答**: 以下の順番で設定を行ってください：1. 施設情報登録（WiFiパスワード、チェックアウト時間など）、2. FAQ初期テンプレート確認・編集、3. QRコード生成・印刷、4. テスト質問で動作確認。全て完了するまで約30分程度です。詳細はご利用マニュアルをご参照ください。
- **キーワード**: 初回ログイン,初期設定,はじめに,スタート,セットアップ
- **関連URL**: /admin/manual

#### 英語 (en)
- **Question**: What should I do after first login?
- **Answer**: Follow these steps: 1. Register facility info (WiFi password, check-out time, etc.), 2. Review/edit initial FAQ templates, 3. Generate/print QR codes, 4. Test with sample questions. Takes about 30 minutes total. See the user manual for details.
- **Keywords**: first login,initial setup,getting started,start,setup
- **Related URL**: /admin/manual

---

### FAQ 3.5: setup_facility_contact_email

**intent_key**: `setup_facility_contact_email`  
**display_order**: 88  
**category**: `setup`

#### 日本語 (ja)
- **質問**: ゲスト画面にメールアドレスを表示できますか？
- **回答**: 施設設定の基本情報で「ゲスト画面にメールアドレスを表示する」をONにすると表示されます。OFFにするとゲストには表示されません。表示する場合は、ログイン用とは別の施設用メールアドレスを設定してください。同じメールアドレスでは保存できません。
- **キーワード**: 施設設定,メールアドレス,ログイン,連絡先,ゲスト表示,専用メール
- **関連URL**: /admin/facility/settings

#### 英語 (en)
- **Question**: Can I show the facility email on the guest screen?
- **Answer**: In Facility Settings → Basic info, turn ON "Show email on guest screen" to display it. Turn OFF to hide it from guests. If you show it, set a facility or inquiry email different from your login email. You cannot save the same email as your login.
- **Keywords**: facility settings,email,login,contact,guest display,dedicated email
- **Related URL**: /admin/facility/settings

---

### FAQ 4: setup_staff_account

**intent_key**: `setup_staff_account`  
**display_order**: 85  
**category**: `setup`

#### 日本語 (ja)
- **質問**: スタッフアカウントを追加できますか？
- **回答**: 現在は追加できません。将来は「設定」→「スタッフ管理」から、スタッフのメールアドレスと権限レベル（オーナー/マネージャー/スタッフ）を設定してアカウントを追加できる予定です。スタッフには招待メールが送信されます。
- **キーワード**: スタッフ追加,複数ユーザー,アカウント追加,権限設定,チーム管理
- **関連URL**: なし

#### 英語 (en)
- **Question**: Can I add staff accounts?
- **Answer**: Currently not available. In the future, you will be able to add staff accounts from "Settings" → "Staff Management" by setting their email and permission level (Owner/Manager/Staff). Staff will receive an invitation email.
- **Keywords**: add staff,multiple users,add account,permissions,team management
- **Related URL**: なし

---

### FAQ 5: setup_password_reset

**intent_key**: `setup_password_reset`  
**display_order**: 80  
**category**: `setup`

#### 日本語 (ja)
- **質問**: パスワードを忘れた場合は？
- **回答**: 現在、パスワードリセット機能は実装されていません。パスワードを忘れた場合は、管理画面右下の「サポート」ボタンから、施設管理者専用問い合わせフォームにアクセスしてお問い合わせください。
- **キーワード**: パスワード忘れ,パスワードリセット,ログインできない,パスワード再設定
- **関連URL**: なし

#### 英語 (en)
- **Question**: What if I forget my password?
- **Answer**: Password reset functionality is currently not implemented. If you forget your password, please contact us via the support form accessible from the "Support" button at the bottom-right of the admin panel.
- **Keywords**: forgot password,password reset,cannot login,reset password
- **Related URL**: なし

---

## Category: qrcode（QRコード設置） - 4項目

### FAQ 6: qrcode_placement

**intent_key**: `qrcode_placement`  
**display_order**: 100  
**category**: `qrcode`

#### 日本語 (ja)
- **質問**: QRコードはどこに貼るのがベストですか？
- **回答**: おすすめの設置場所：1. エントランス（最優先、ゲストが最初に目にする場所）、2. 各部屋（ドア内側）、3. キッチン、4. ラウンジ。設置場所ごとに異なるQRコードを生成できます。目立つ場所に、目線の高さに貼るのがポイントです。
- **キーワード**: QRコード設置,設置場所,おすすめ場所,配置,どこに貼る
- **関連URL**: /admin/qr-code

#### 英語 (en)
- **Question**: Where is the best place to put QR codes?
- **Answer**: Recommended locations: 1. Entrance (highest priority, first place guests see), 2. Each room (inside door), 3. Kitchen, 4. Lounge. You can generate different QR codes for each location. Key is to place at eye level in visible spots.
- **Keywords**: QR code placement,location,recommended spots,positioning,where to place
- **Related URL**: /admin/qr-code

---

### FAQ 7: qrcode_multiple

**intent_key**: `qrcode_multiple`  
**display_order**: 95  
**category**: `qrcode`

#### 日本語 (ja)
- **質問**: 複数のQRコードを使い分けられますか？
- **回答**: はい。設置場所ごとにQRコードを生成できます。各QRコードには設置場所情報が紐付けられるため、どこから質問が来たか追跡できます。例：「エントランス」「部屋101」「キッチン」など。ログ分析で場所別の質問傾向がわかります。
- **キーワード**: 複数QRコード,QRコード使い分け,場所別QRコード,QR分類
- **関連URL**: /admin/qr-code

#### 英語 (en)
- **Question**: Can I use multiple QR codes?
- **Answer**: Yes. You can generate QR codes for each location. Each QR code includes location info, so you can track where questions come from. Examples: "Entrance", "Room 101", "Kitchen". Log analysis shows question trends by location.
- **Keywords**: multiple QR codes,QR code variation,location-specific codes,QR classification
- **Related URL**: /admin/qr-code

---

### FAQ 8: qrcode_print_size

**intent_key**: `qrcode_print_size`  
**display_order**: 90  
**category**: `qrcode`

#### 日本語 (ja)
- **質問**: QRコードの印刷サイズの推奨は？
- **回答**: A4用紙1枚に1つのQRコードが推奨です。最小サイズは5cm×5cm、推奨サイズは10cm×10cm以上です。小さすぎるとスマホで読み取りにくくなります。光沢紙よりマット紙の方が読み取りやすいです。PDF/PNG/SVG形式でダウンロードできます。
- **キーワード**: QRコード印刷,印刷サイズ,推奨サイズ,最小サイズ,QRサイズ
- **関連URL**: /admin/qr-code

#### 英語 (en)
- **Question**: What is the recommended QR code print size?
- **Answer**: One QR code per A4 sheet is recommended. Minimum size is 5cm×5cm, recommended size is 10cm×10cm or larger. Too small makes it hard to scan with smartphones. Matte paper is better than glossy. Available in PDF/PNG/SVG format.
- **Keywords**: QR code printing,print size,recommended size,minimum size,QR size
- **Related URL**: /admin/qr-code

---

### FAQ 9: qrcode_regenerate

**intent_key**: `qrcode_regenerate`  
**display_order**: 85  
**category**: `qrcode`

#### 日本語 (ja)
- **質問**: QRコードを再発行したい場合は？
- **回答**: 「QRコード管理」から既存のQRコードを削除し、新しいQRコードを生成してください。古いQRコードは自動的に無効化されます。セキュリティ上、定期的な再発行（3-6ヶ月ごと）を推奨します。
- **キーワード**: QRコード再発行,QRコード更新,QRコード削除,QR再生成
- **関連URL**: なし

#### 英語 (en)
- **Question**: How do I regenerate a QR code?
- **Answer**: From "QR Code Management", delete the existing QR code and generate a new one. The old QR code will be automatically invalidated. For security, periodic regeneration (every 3-6 months) is recommended.
- **Keywords**: regenerate QR code,update QR code,delete QR code,QR regeneration
- **Related URL**: なし

---

## Category: faq_management（FAQ管理） - 5項目

### FAQ 10: faq_template_usage

**intent_key**: `faq_template_usage`  
**display_order**: 100  
**category**: `faq_management`

#### 日本語 (ja)
- **質問**: FAQテンプレートの使い方は？
- **回答**: システムが20-30件の初期テンプレートを提供しています。「FAQ管理」から各テンプレートを確認し、施設に合わせて編集してください。不要なFAQは非アクティブ化できます。WiFiパスワードやチェックイン時間など、施設固有の情報を必ず更新してください。
- **キーワード**: FAQテンプレート,初期FAQ,テンプレート編集,FAQ雛形
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: How to use FAQ templates?
- **Answer**: The system provides 20-30 initial templates. From "FAQ Management", review each template and edit to match your facility. Unwanted FAQs can be deactivated. Be sure to update facility-specific info like WiFi password and check-in time.
- **Keywords**: FAQ templates,initial FAQs,template editing,FAQ templates
- **Related URL**: /admin/faqs

---

### FAQ 11: faq_add_custom

**intent_key**: `faq_add_custom`  
**display_order**: 95  
**category**: `faq_management`

#### 日本語 (ja)
- **質問**: 自分でFAQを追加する方法は？
- **回答**: 「FAQ管理」→「新規FAQ追加」から、質問・回答・カテゴリ・優先度を入力して保存してください。質問は具体的に、回答は簡潔に（200文字以内推奨）。複数言語対応する場合は、各言語で登録が必要です。
- **キーワード**: FAQ追加,カスタムFAQ,FAQ作成,新規FAQ,FAQ登録
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: How to add custom FAQs?
- **Answer**: From "FAQ Management" → "Add New FAQ", enter question, answer, category, and priority, then save. Make questions specific and answers concise (under 200 characters recommended). For multilingual support, register in each language.
- **Keywords**: add FAQ,custom FAQ,create FAQ,new FAQ,register FAQ
- **Related URL**: /admin/faqs

---

### FAQ 12: faq_priority

**intent_key**: `faq_priority`  
**display_order**: 90  
**category**: `faq_management`

#### 日本語 (ja)
- **質問**: FAQの優先度とは何ですか？
- **回答**: 優先度（1-5）は、AI検索時のランキングに影響します。優先度5が最高で、よくある質問には高い優先度を設定してください。例：WiFiパスワード（5）、チェックアウト時間（5）、周辺観光（3）。ログ分析で質問頻度を確認し、優先度を調整しましょう。
- **キーワード**: FAQ優先度,優先順位,ランキング,FAQ重要度
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: What is FAQ priority?
- **Answer**: Priority (1-5) affects ranking in AI search. Priority 5 is highest. Set high priority for frequently asked questions. Examples: WiFi password (5), Check-out time (5), Local tourism (3). Check log analysis for question frequency and adjust priority accordingly.
- **Keywords**: FAQ priority,ranking,priority level,FAQ importance
- **Related URL**: /admin/faqs

---

### FAQ 13: faq_category

**intent_key**: `faq_category`  
**display_order**: 85  
**category**: `faq_management`

#### 日本語 (ja)
- **質問**: カテゴリはどう分けるべきですか？
- **回答**: カテゴリは4種類：基本情報（チェックイン/WiFi等）、設備（キッチン/シャワー等）、周辺情報（駅/コンビニ等）、トラブル（鍵紛失/故障等）。質問内容に最も近いカテゴリを選んでください。カテゴリ別にログ分析できるので、適切な分類が重要です。
- **キーワード**: FAQカテゴリ,カテゴリ分類,カテゴリ選択,FAQ分類
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: How should I categorize FAQs?
- **Answer**: 4 categories: Basic (check-in/WiFi), Facilities (kitchen/shower), Location (station/convenience store), Trouble (lost key/malfunction). Choose the category closest to the question content. Proper categorization is important for category-based log analysis.
- **Keywords**: FAQ categories,categorization,category selection,FAQ classification
- **Related URL**: /admin/faqs

---

### FAQ 14: faq_bulk_import

**intent_key**: `faq_bulk_import`  
**display_order**: 80  
**category**: `faq_management`

#### 日本語 (ja)
- **質問**: FAQを一括登録できますか？
- **回答**: Standard・Premiumプランでは「FAQ管理」からCSV一括登録（追加モード）が利用できます。現在は個別登録のみのプランでは、大量のFAQがある場合はサポートへご相談ください。
- **キーワード**: FAQ一括登録,CSV登録,大量登録,インポート,バルク登録
- **関連URL**: なし

#### 英語 (en)
- **Question**: Can I bulk import FAQs?
- **Answer**: Standard and Premium plans can use CSV bulk registration (add mode) from "FAQ Management". For plans with individual registration only, please contact support for large FAQ volumes.
- **Keywords**: bulk import FAQ,CSV import,mass registration,import,bulk registration
- **Related URL**: なし

---

## Category: ai_logic（AI仕組み） - 4項目

### FAQ 15: ai_how_it_works

**intent_key**: `ai_how_it_works`  
**display_order**: 100  
**category**: `ai_logic`

#### 日本語 (ja)
- **質問**: AIはどうやって質問に答えていますか？
- **回答**: OpenAI GPT-4o-miniを使用しています。登録されたFAQをシステムプロンプトに埋め込み、ゲストの質問に最適な回答を生成します。FAQ内容が充実しているほど、精度の高い回答ができます。
- **キーワード**: AI仕組み,どうやって,GPT-4o-mini,仕組み,AIの仕組み
- **関連URL**: /admin/dashboard

#### 英語 (en)
- **Question**: How does AI answer questions?
- **Answer**: We use OpenAI GPT-4o-mini. Registered FAQs are embedded in the system prompt to generate optimal responses to guest questions. The more comprehensive your FAQs, the more accurate the responses.
- **Keywords**: how AI works,mechanism,GPT-4o-mini,how it works,AI mechanism
- **Related URL**: /admin/dashboard

---

### FAQ 16: ai_accuracy

**intent_key**: `ai_accuracy`  
**display_order**: 95  
**category**: `ai_logic`

#### 日本語 (ja)
- **質問**: AIの回答精度を上げるには？
- **回答**: FAQ登録時のポイント：1. 質問文は具体的に（「WiFiは？」より「WiFiパスワードは？」）、2. 回答は簡潔に（200文字以内）、3. キーワードを適切に設定、4. 優先度を調整。FAQが充実するほど精度が向上します。週次でログを確認し、答えられなかった質問をFAQに追加しましょう。
- **キーワード**: AI精度,精度向上,回答精度,改善,正確性
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: How to improve AI response accuracy?
- **Answer**: FAQ registration tips: 1. Make questions specific ("WiFi password?" vs "WiFi?"), 2. Keep answers concise (under 200 characters), 3. Set keywords properly, 4. Adjust priority. More FAQs improve accuracy. Check logs weekly and add unanswered questions to FAQs.
- **Keywords**: AI accuracy,improve accuracy,response quality,improvement,accuracy
- **Related URL**: /admin/faqs

---

### FAQ 17: ai_languages

**intent_key**: `ai_languages`  
**display_order**: 90  
**category**: `ai_logic`

#### 日本語 (ja)
- **質問**: 対応言語は何語ですか？
- **回答**: 現在は日本語、英語、繁体中国語、簡体中国語、フランス語、韓国語、スペイン語の7言語に対応しています。ゲスト画面の言語選択で選べます。ドイツ語・ベトナム語は選択肢からは削除しています。FAQは各言語で登録が必要です。
- **キーワード**: 対応言語,多言語,言語設定,何語,サポート言語
- **関連URL**: /admin/manual

#### 英語 (en)
- **Question**: What languages are supported?
- **Answer**: Currently we support 7 languages: Japanese, English, Traditional Chinese, Simplified Chinese, French, Korean, and Spanish. Guests can choose their language on the language selection screen. German and Vietnamese are no longer offered in the guest language options. FAQs must be registered in each language.
- **Keywords**: supported languages,multilingual,language settings,what languages,supported languages
- **Related URL**: /admin/manual

---

### FAQ 18: ai_limitations

**intent_key**: `ai_limitations`  
**display_order**: 85  
**category**: `ai_logic`

#### 日本語 (ja)
- **質問**: AIが答えられない質問はありますか？
- **回答**: はい。FAQに登録されていない内容や、リアルタイム情報（天気、在庫状況等）には答えられません。その場合は「スタッフに確認してください」と案内されます。信頼度スコアが低い回答は自動的にスタッフへエスカレーションされます。
- **キーワード**: AI限界,答えられない,できないこと,制限,対応不可
- **関連URL**: /admin/dashboard

#### 英語 (en)
- **Question**: Are there questions AI cannot answer?
- **Answer**: Yes. AI cannot answer content not registered in FAQs or real-time information (weather, inventory status, etc.). In such cases, it will suggest "Please check with staff." Low confidence responses are automatically escalated to staff.
- **Keywords**: AI limitations,cannot answer,what it cannot do,restrictions,cannot handle
- **Related URL**: /admin/dashboard

---

## Category: logs（ログ分析） - 3項目

### FAQ 19: logs_view_questions

**intent_key**: `logs_view_questions`  
**display_order**: 100  
**category**: `logs`

#### 日本語 (ja)
- **質問**: ゲストの質問履歴はどこで見られますか？
- **回答**: 「ログ管理」→「質問履歴」から、日付・カテゴリ・キーワードで検索できます。各質問のAI信頼度スコア、ゲストの言語、設置場所も確認できます。CSVエクスポート機能もあります。
- **キーワード**: 質問履歴,ログ確認,履歴閲覧,チャットログ,ログ表示
- **関連URL**: /admin/logs

#### 英語 (en)
- **Question**: Where can I view guest question history?
- **Answer**: From "Log Management" → "Question History", you can search by date, category, and keywords. AI confidence scores, guest language, and location are also visible. CSV export function available.
- **Keywords**: question history,view logs,history access,chat logs,log display
- **Related URL**: /admin/logs

---

### FAQ 20: logs_unanswered

**intent_key**: `logs_unanswered`  
**display_order**: 95  
**category**: `logs`

#### 日本語 (ja)
- **質問**: AIが答えられなかった質問を確認するには？
- **回答**: 「ログ管理」で信頼度スコア0.5以下の質問をフィルタリングできます。これらの質問は新しいFAQ作成の参考になります。週次でチェックし、頻出する質問はFAQに追加しましょう。
- **キーワード**: 答えられなかった質問,低信頼度,FAQ作成参考,未回答
- **関連URL**: /admin/logs

#### 英語 (en)
- **Question**: How to check questions AI couldn't answer?
- **Answer**: In "Log Management", filter questions with confidence score 0.5 or below. These questions can be used as references for creating new FAQs. Check weekly and add frequently asked questions to FAQs.
- **Keywords**: unanswered questions,low confidence,FAQ creation reference,unanswered
- **Related URL**: /admin/logs

---

### FAQ 21: logs_analytics

**intent_key**: `logs_analytics`  
**display_order**: 90  
**category**: `logs`

#### 日本語 (ja)
- **質問**: よくある質問のランキングは？
- **回答**: 「ダッシュボード」で質問カテゴリ別の統計を確認できます。よく聞かれる質問のランキング機能は将来的に追加予定です。週次・月次で傾向を分析できるようになる予定です。ランキング上位の質問はFAQ優先度を高めに設定しましょう。
- **キーワード**: ランキング,統計,よくある質問,分析,TOP10
- **関連URL**: なし

#### 英語 (en)
- **Question**: Where is the FAQ ranking?
- **Answer**: On the "Dashboard", you can view statistics by question category. The frequently asked questions ranking feature will be added in the future. Weekly/monthly trend analysis is planned. Set higher FAQ priority for top-ranking questions.
- **Keywords**: ranking,statistics,frequently asked,analysis,TOP10
- **Related URL**: なし

---

## Category: troubleshooting（トラブルシューティング） - 5項目

### FAQ 22: trouble_ai_slow

**intent_key**: `trouble_ai_slow`  
**display_order**: 100  
**category**: `troubleshooting`

#### 日本語 (ja)
- **質問**: AIの応答が遅い場合は？
- **回答**: 通常3-5秒以内に応答します。10秒以上かかる場合は、ネットワーク状況を確認するか、ブラウザをリフレッシュしてください。問題が続く場合は、管理画面右下の「サポート」ボタンから施設管理者専用問い合わせフォームにアクセスしてお問い合わせください。
- **キーワード**: AI遅い,応答遅延,遅延,速度,レスポンス遅い
- **関連URL**: なし

#### 英語 (en)
- **Question**: What if AI response is slow?
- **Answer**: Normal response time is 3-5 seconds. If it takes over 10 seconds, check network conditions or refresh the browser. If the problem persists, please contact us via the support form accessible from the "Support" button at the bottom-right of the admin panel.
- **Keywords**: AI slow,response delay,delay,speed,slow response
- **Related URL**: なし

---

### FAQ 23: trouble_qr_not_working

**intent_key**: `trouble_qr_not_working`  
**display_order**: 95  
**category**: `troubleshooting`

#### 日本語 (ja)
- **質問**: QRコードが読み取れない場合は？
- **回答**: 原因：1. QRコードが小さすぎる（5cm未満）、2. 印刷が不鮮明、3. カメラの焦点が合っていない、4. 光沢紙で反射している。対処法：大きめのQRコードをマット紙で再印刷してください。それでも解決しない場合はQRコードを再生成してみてください。
- **キーワード**: QRコード読み取れない,スキャンできない,QRエラー,認識しない
- **関連URL**: /admin/qr-code

#### 英語 (en)
- **Question**: What if QR code doesn't scan?
- **Answer**: Causes: 1. QR code too small (under 5cm), 2. Unclear printing, 3. Camera out of focus, 4. Reflection on glossy paper. Solution: Reprint a larger QR code on matte paper. If still not working, try regenerating the QR code.
- **Keywords**: QR code not scanning,cannot scan,QR error,not recognized
- **Related URL**: /admin/qr-code

---

### FAQ 24: trouble_faq_not_updated

**intent_key**: `trouble_faq_not_updated`  
**display_order**: 90  
**category**: `troubleshooting`

#### 日本語 (ja)
- **質問**: FAQを更新したのに反映されない？
- **回答**: FAQ更新後、システムプロンプトの再構築に最大5分かかります。5分待ってもダメな場合は、ブラウザキャッシュをクリアしてください（Ctrl+Shift+R または Cmd+Shift+R）。それでも解決しない場合は、管理画面右下の「サポート」ボタンから施設管理者専用問い合わせフォームにアクセスしてお問い合わせください。
- **キーワード**: FAQ反映されない,更新されない,変更されない,反映遅い
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: FAQ update not reflected?
- **Answer**: After FAQ update, system prompt reconstruction takes up to 5 minutes. If still not working after 5 minutes, clear browser cache (Ctrl+Shift+R or Cmd+Shift+R). If still unresolved, please contact us via the support form accessible from the "Support" button at the bottom-right of the admin panel.
- **Keywords**: FAQ not reflected,not updated,not changed,slow reflection
- **Related URL**: /admin/faqs

---

## Category: billing（料金・プラン・請求）

### FAQ: plan_billing_overage_behavior

**intent_key**: `plan_billing_overage_behavior`  
**display_order**: 84  
**category**: `billing`

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