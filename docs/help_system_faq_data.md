# 宿泊事業者向けFAQ初期データ（30項目）

**プロジェクト**: YadOPERA Phase 2 統合ヘルプシステム  
**作成日**: 2025-12-26  
**言語**: 日本語・英語

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
- **回答**: ログイン後、「設定」→「施設設定」から施設名、住所、チェックイン/アウト時間、WiFi情報、部屋数などを登録できます。これらの情報はゲストへの自動応答に使用されます。
- **キーワード**: 施設情報,施設設定,基本情報,WiFi設定,施設登録
- **関連URL**: /admin/facility

#### 英語 (en)
- **Question**: Where do I register facility information?
- **Answer**: After login, go to "Settings" → "Facility Settings" to register facility name, address, check-in/out times, WiFi info, room count, etc. This information is used for automatic guest responses.
- **Keywords**: facility information,facility settings,basic info,WiFi settings,facility registration
- **Related URL**: /admin/facility

---

### FAQ 3: setup_first_login

**intent_key**: `setup_first_login`  
**display_order**: 90  
**category**: `setup`

#### 日本語 (ja)
- **質問**: 初回ログイン後にまずやるべきことは？
- **回答**: 以下の順番で設定を行ってください：1. 施設情報登録（WiFiパスワード、チェックイン時間など）、2. FAQ初期テンプレート確認・編集、3. QRコード生成・印刷、4. テスト質問で動作確認。全て完了するまで約30分程度です。
- **キーワード**: 初回ログイン,初期設定,はじめに,スタート,セットアップ
- **関連URL**: /admin/dashboard

#### 英語 (en)
- **Question**: What should I do after first login?
- **Answer**: Follow these steps: 1. Register facility info (WiFi password, check-in time, etc.), 2. Review/edit initial FAQ templates, 3. Generate/print QR codes, 4. Test with sample questions. Takes about 30 minutes total.
- **Keywords**: first login,initial setup,getting started,start,setup
- **Related URL**: /admin/dashboard

---

### FAQ 4: setup_staff_account

**intent_key**: `setup_staff_account`  
**display_order**: 85  
**category**: `setup`

#### 日本語 (ja)
- **質問**: スタッフアカウントを追加できますか？
- **回答**: はい。「設定」→「スタッフ管理」から、スタッフのメールアドレスと権限レベル（オーナー/マネージャー/スタッフ）を設定してアカウントを追加できます。スタッフには招待メールが送信されます。
- **キーワード**: スタッフ追加,複数ユーザー,アカウント追加,権限設定,チーム管理
- **関連URL**: /admin/staff

#### 英語 (en)
- **Question**: Can I add staff accounts?
- **Answer**: Yes. From "Settings" → "Staff Management", you can add staff accounts by setting their email and permission level (Owner/Manager/Staff). Staff will receive an invitation email.
- **Keywords**: add staff,multiple users,add account,permissions,team management
- **Related URL**: /admin/staff

---

### FAQ 5: setup_password_reset

**intent_key**: `setup_password_reset`  
**display_order**: 80  
**category**: `setup`

#### 日本語 (ja)
- **質問**: パスワードを忘れた場合は？
- **回答**: ログイン画面の「パスワードを忘れた場合」リンクをクリックし、登録メールアドレスを入力してください。パスワードリセット用のリンクが送信されます。リンクの有効期限は1時間です。
- **キーワード**: パスワード忘れ,パスワードリセット,ログインできない,パスワード再設定
- **関連URL**: /admin/login

#### 英語 (en)
- **Question**: What if I forget my password?
- **Answer**: Click "Forgot password?" on the login screen, enter your registered email address, and you will receive a password reset link. The link expires in 1 hour.
- **Keywords**: forgot password,password reset,cannot login,reset password
- **Related URL**: /admin/login

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
- **回答**: A4用紙1枚に1つのQRコードが推奨です。最小サイズは5cm×5cm、推奨サイズは10cm×10cm以上です。小さすぎるとスマホで読み取りにくくなります。光沢紙よりマット紙の方が読み取りやすいです。PDF/PNG形式でダウンロードできます。
- **キーワード**: QRコード印刷,印刷サイズ,推奨サイズ,最小サイズ,QRサイズ
- **関連URL**: /admin/qr-code

#### 英語 (en)
- **Question**: What is the recommended QR code print size?
- **Answer**: One QR code per A4 sheet is recommended. Minimum size is 5cm×5cm, recommended size is 10cm×10cm or larger. Too small makes it hard to scan with smartphones. Matte paper is better than glossy. Available in PDF/PNG format.
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
- **関連URL**: /admin/qr-code

#### 英語 (en)
- **Question**: How do I regenerate a QR code?
- **Answer**: From "QR Code Management", delete the existing QR code and generate a new one. The old QR code will be automatically invalidated. For security, periodic regeneration (every 3-6 months) is recommended.
- **Keywords**: regenerate QR code,update QR code,delete QR code,QR regeneration
- **Related URL**: /admin/qr-code

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
- **回答**: 優先度（1-5）は、AI検索時のランキングに影響します。優先度5が最高で、よくある質問には高い優先度を設定してください。例：WiFiパスワード（5）、チェックイン時間（5）、周辺観光（3）。ログ分析で質問頻度を確認し、優先度を調整しましょう。
- **キーワード**: FAQ優先度,優先順位,ランキング,FAQ重要度
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: What is FAQ priority?
- **Answer**: Priority (1-5) affects ranking in AI search. Priority 5 is highest. Set high priority for frequently asked questions. Examples: WiFi password (5), Check-in time (5), Local tourism (3). Check log analysis for question frequency and adjust priority accordingly.
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
- **回答**: 現在は個別登録のみですが、Phase 2でCSV一括インポート機能を追加予定です。大量のFAQがある場合は、サポートチーム（support@yadopera.com）にご相談ください。一時的に代行登録のサポートも可能です。
- **キーワード**: FAQ一括登録,CSV登録,大量登録,インポート,バルク登録
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: Can I bulk import FAQs?
- **Answer**: Currently only individual registration is supported, but CSV bulk import will be added in Phase 2. For large FAQ volumes, please contact our support team (support@yadopera.com). Temporary registration assistance is available.
- **Keywords**: bulk import FAQ,CSV import,mass registration,import,bulk registration
- **Related URL**: /admin/faqs

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
- **回答**: 現在は日本語、英語、中国語（簡体字・繁体字）、韓国語の5言語に対応しています。ゲストが選択した言語で自動的に回答します。FAQは各言語で登録が必要です。翻訳支援機能も今後追加予定です。
- **キーワード**: 対応言語,多言語,言語設定,何語,サポート言語
- **関連URL**: /admin/facility

#### 英語 (en)
- **Question**: What languages are supported?
- **Answer**: Currently supports 5 languages: Japanese, English, Chinese (Simplified/Traditional), and Korean. Responses are automatically provided in the guest's selected language. FAQs must be registered in each language. Translation assistance feature coming soon.
- **Keywords**: supported languages,multilingual,language settings,what languages,supported languages
- **Related URL**: /admin/facility

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
- **回答**: 「ダッシュボード」で質問カテゴリ別の統計と、よく聞かれる質問TOP10を確認できます。週次・月次で傾向を分析できます。ランキング上位の質問はFAQ優先度を高めに設定しましょう。
- **キーワード**: ランキング,統計,よくある質問,分析,TOP10
- **関連URL**: /admin/dashboard

#### 英語 (en)
- **Question**: Where is the FAQ ranking?
- **Answer**: On the "Dashboard", you can view statistics by question category and TOP 10 frequently asked questions. Analyze trends weekly/monthly. Set higher FAQ priority for top-ranking questions.
- **Keywords**: ranking,statistics,frequently asked,analysis,TOP10
- **Related URL**: /admin/dashboard

---

## Category: troubleshooting（トラブルシューティング） - 5項目

### FAQ 22: trouble_ai_slow

**intent_key**: `trouble_ai_slow`  
**display_order**: 100  
**category**: `troubleshooting`

#### 日本語 (ja)
- **質問**: AIの応答が遅い場合は？
- **回答**: 通常3-5秒以内に応答します。10秒以上かかる場合は、ネットワーク状況を確認するか、ブラウザをリフレッシュしてください。問題が続く場合はサポート（support@yadopera.com）にお問い合わせください。
- **キーワード**: AI遅い,応答遅延,遅延,速度,レスポンス遅い
- **関連URL**: /admin/dashboard

#### 英語 (en)
- **Question**: What if AI response is slow?
- **Answer**: Normal response time is 3-5 seconds. If it takes over 10 seconds, check network conditions or refresh the browser. If the problem persists, contact support (support@yadopera.com).
- **Keywords**: AI slow,response delay,delay,speed,slow response
- **Related URL**: /admin/dashboard

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
- **回答**: FAQ更新後、システムプロンプトの再構築に最大5分かかります。5分待ってもダメな場合は、ブラウザキャッシュをクリアしてください（Ctrl+Shift+R または Cmd+Shift+R）。それでも解決しない場合はサポートにご連絡ください。
- **キーワード**: FAQ反映されない,更新されない,変更されない,反映遅い
- **関連URL**: /admin/faqs

#### 英語 (en)
- **Question**: FAQ update not reflected?
- **Answer**: After FAQ update, system prompt reconstruction takes up to 5 minutes. If still not working after 5 minutes, clear browser cache (Ctrl+Shift+R or Cmd+Shift+R). If still unresolved, contact support.
- **Keywords**: FAQ not reflected,not updated,not changed,slow reflection
- **Related URL**: /