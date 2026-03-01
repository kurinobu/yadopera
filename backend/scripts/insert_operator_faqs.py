#!/usr/bin/env python3
"""
宿泊事業者向けFAQ初期データ投入スクリプト
30項目のFAQデータをoperator_faqsテーブルに投入します。
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Pythonパスにbackendディレクトリを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

from app.models.operator_help import OperatorFaq, OperatorFaqTranslation

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初期FAQデータ（30項目）
# 参照: docs/help_system_faq_data.md
OPERATOR_FAQ_DATA = [
    # Category: setup（初期設定） - 5項目
    {
        'intent_key': 'setup_account_creation',
        'category': 'setup',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'アカウント作成の手順は？',
                'answer': '管理画面トップページから「新規登録」をクリックし、メールアドレス・パスワード・施設情報を入力してください。メール認証後、ログインできます。初回ログイン時に施設設定の入力をお願いします。',
                'keywords': 'アカウント作成,新規登録,サインアップ,初期設定,アカウント開設',
                'related_url': None
            },
            'en': {
                'question': 'How to create an account?',
                'answer': 'Click "Sign Up" from the top page, enter your email, password, and facility information. After email verification, you can log in. Please complete facility settings on first login.',
                'keywords': 'account creation,sign up,registration,initial setup,account opening',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'setup_facility_info',
        'category': 'setup',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '施設情報はどこで登録しますか？',
                'answer': 'ログイン後、「設定」→「施設設定」から施設名、住所、チェックイン/アウト時間、WiFi情報、部屋数などを登録できます。これらの情報はゲストへの自動応答に使用されます。',
                'keywords': '施設情報,施設設定,基本情報,WiFi設定,施設登録',
                'related_url': '/admin/facility/settings'
            },
            'en': {
                'question': 'Where do I register facility information?',
                'answer': 'After login, go to "Settings" → "Facility Settings" to register facility name, address, check-in/out times, WiFi info, room count, etc. This information is used for automatic guest responses.',
                'keywords': 'facility information,facility settings,basic info,WiFi settings,facility registration',
                'related_url': '/admin/facility/settings'
            }
        }
    },
    {
        'intent_key': 'setup_first_login',
        'category': 'setup',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '初回ログイン後にまずやるべきことは？',
                'answer': '以下の順番で設定を行ってください：1. 施設情報登録（WiFiパスワード、チェックアウト時間など）、2. FAQ初期テンプレート確認・編集、3. QRコード生成・印刷、4. テスト質問で動作確認。全て完了するまで約30分程度です。',
                'keywords': '初回ログイン,初期設定,はじめに,スタート,セットアップ',
                'related_url': '/admin/manual#login-first'
            },
            'en': {
                'question': 'What should I do after first login?',
                'answer': 'Follow these steps: 1. Register facility info (WiFi password, check-out time, etc.), 2. Review/edit initial FAQ templates, 3. Generate/print QR codes, 4. Test with sample questions. Takes about 30 minutes total.',
                'keywords': 'first login,initial setup,getting started,start,setup',
                'related_url': '/admin/manual#login-first'
            }
        }
    },
    {
        'intent_key': 'setup_staff_account',
        'category': 'setup',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'スタッフアカウントを追加できますか？',
                'answer': '現在は追加できません。将来は「設定」→「スタッフ管理」から、スタッフのメールアドレスと権限レベル（オーナー/マネージャー/スタッフ）を設定してアカウントを追加できる予定です。',
                'keywords': 'スタッフ追加,複数ユーザー,アカウント追加,権限設定,チーム管理',
                'related_url': None
            },
            'en': {
                'question': 'Can I add staff accounts?',
                'answer': 'Currently not available. In the future, you will be able to add staff accounts from "Settings" → "Staff Management" by setting their email and permission level (Owner/Manager/Staff).',
                'keywords': 'add staff,multiple users,add account,permissions,team management',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'setup_password_reset',
        'category': 'setup',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'パスワードを忘れた場合は？',
                'answer': '現在、パスワードリセット機能は実装されていません。パスワードを忘れた場合は、管理画面右下の「サポート」ボタンから、施設管理者専用問い合わせフォームにアクセスしてお問い合わせください。',
                'keywords': 'パスワード忘れ,パスワードリセット,ログインできない,パスワード再設定',
                'related_url': None
            },
            'en': {
                'question': 'What if I forget my password?',
                'answer': 'Password reset functionality is currently not implemented. If you forget your password, please contact us via the support form accessible from the "Support" button at the bottom-right of the admin panel.',
                'keywords': 'forgot password,password reset,cannot login,reset password',
                'related_url': None
            }
        }
    },
    # Category: qrcode（QRコード設置） - 4項目
    {
        'intent_key': 'qrcode_placement',
        'category': 'qrcode',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'QRコードはどこに貼るのがベストですか？',
                'answer': 'おすすめの設置場所：1. エントランス（最優先、ゲストが最初に目にする場所）、2. 各部屋（ドア内側）、3. キッチン、4. ラウンジ。設置場所ごとに異なるQRコードを生成できます。目立つ場所に、目線の高さに貼るのがポイントです。',
                'keywords': 'QRコード設置,設置場所,おすすめ場所,配置,どこに貼る',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'Where is the best place to put QR codes?',
                'answer': 'Recommended locations: 1. Entrance (highest priority, first place guests see), 2. Each room (inside door), 3. Kitchen, 4. Lounge. You can generate different QR codes for each location. Key is to place at eye level in visible spots.',
                'keywords': 'QR code placement,location,recommended spots,positioning,where to place',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'intent_key': 'qrcode_multiple',
        'category': 'qrcode',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '複数のQRコードを使い分けられますか？',
                'answer': 'はい。設置場所ごとにQRコードを生成できます。各QRコードには設置場所情報が紐付けられるため、どこから質問が来たか追跡できます。例：「エントランス」「部屋101」「キッチン」など。ログ分析で場所別の質問傾向がわかります。',
                'keywords': '複数QRコード,QRコード使い分け,場所別QRコード,QR分類',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'Can I use multiple QR codes?',
                'answer': 'Yes. You can generate QR codes for each location. Each QR code includes location info, so you can track where questions come from. Examples: "Entrance", "Room 101", "Kitchen". Log analysis shows question trends by location.',
                'keywords': 'multiple QR codes,QR code variation,location-specific codes,QR classification',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'intent_key': 'qrcode_print_size',
        'category': 'qrcode',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'QRコードの印刷サイズの推奨は？',
                'answer': 'A4用紙1枚に1つのQRコードが推奨です。最小サイズは5cm×5cm、推奨サイズは10cm×10cm以上です。小さすぎるとスマホで読み取りにくくなります。光沢紙よりマット紙の方が読み取りやすいです。PDF/PNG/SVG形式でダウンロードできます。',
                'keywords': 'QRコード印刷,印刷サイズ,推奨サイズ,最小サイズ,QRサイズ',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'What is the recommended QR code print size?',
                'answer': 'One QR code per A4 sheet is recommended. Minimum size is 5cm×5cm, recommended size is 10cm×10cm or larger. Too small makes it hard to scan with smartphones. Matte paper is better than glossy. Available in PDF/PNG/SVG format.',
                'keywords': 'QR code printing,print size,recommended size,minimum size,QR size',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'intent_key': 'qrcode_regenerate',
        'category': 'qrcode',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'QRコードを再発行したい場合は？',
                'answer': '「QRコード管理」から既存のQRコードを削除し、新しいQRコードを生成してください。古いQRコードは自動的に無効化されます。セキュリティ上、定期的な再発行（3-6ヶ月ごと）を推奨します。',
                'keywords': 'QRコード再発行,QRコード更新,QRコード削除,QR再生成',
                'related_url': None
            },
            'en': {
                'question': 'How do I regenerate a QR code?',
                'answer': 'From "QR Code Management", delete the existing QR code and generate a new one. The old QR code will be automatically invalidated. For security, periodic regeneration (every 3-6 months) is recommended.',
                'keywords': 'regenerate QR code,update QR code,delete QR code,QR regeneration',
                'related_url': None
            }
        }
    },
    # Category: faq_management（FAQ管理） - 5項目
    {
        'intent_key': 'faq_template_usage',
        'category': 'faq_management',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'FAQテンプレートの使い方は？',
                'answer': 'システムが20-30件の初期テンプレートを提供しています。「FAQ管理」から各テンプレートを確認し、施設に合わせて編集してください。不要なFAQは非アクティブ化できます。WiFiパスワードやチェックアウト時間など、施設固有の情報を必ず更新してください。',
                'keywords': 'FAQテンプレート,初期FAQ,テンプレート編集,FAQ雛形',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to use FAQ templates?',
                'answer': 'The system provides 20-30 initial templates. From "FAQ Management", review each template and edit to match your facility. Unwanted FAQs can be deactivated. Be sure to update facility-specific info like WiFi password and check-out time.',
                'keywords': 'FAQ templates,initial FAQs,template editing,FAQ templates',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'intent_key': 'faq_add_custom',
        'category': 'faq_management',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '自分でFAQを追加する方法は？',
                'answer': '「FAQ管理」→「新規FAQ追加」から、質問・回答・カテゴリ・優先度を入力して保存してください。質問は具体的に、回答は簡潔に（200文字以内推奨）。複数言語対応する場合は、各言語で登録が必要です。',
                'keywords': 'FAQ追加,カスタムFAQ,FAQ作成,新規FAQ,FAQ登録',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to add custom FAQs?',
                'answer': 'From "FAQ Management" → "Add New FAQ", enter question, answer, category, and priority, then save. Make questions specific and answers concise (under 200 characters recommended). For multilingual support, register in each language.',
                'keywords': 'add FAQ,custom FAQ,create FAQ,new FAQ,register FAQ',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'intent_key': 'faq_priority',
        'category': 'faq_management',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'FAQの優先度とは何ですか？',
                'answer': '優先度（1-5）は、AI検索時のランキングに影響します。優先度5が最高で、よくある質問には高い優先度を設定してください。例：WiFiパスワード（5）、チェックアウト時間（5）、周辺観光（3）。ログ分析で質問頻度を確認し、優先度を調整しましょう。',
                'keywords': 'FAQ優先度,優先順位,ランキング,FAQ重要度',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'What is FAQ priority?',
                'answer': 'Priority (1-5) affects ranking in AI search. Priority 5 is highest. Set high priority for frequently asked questions. Examples: WiFi password (5), Check-out time (5), Local tourism (3). Check log analysis for question frequency and adjust priority accordingly.',
                'keywords': 'FAQ priority,ranking,priority level,FAQ importance',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'intent_key': 'faq_category',
        'category': 'faq_management',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'カテゴリはどう分けるべきですか？',
                'answer': 'カテゴリは4種類：基本情報（チェックイン/WiFi等）、設備（キッチン/シャワー等）、周辺情報（駅/コンビニ等）、トラブル（鍵紛失/故障等）。質問内容に最も近いカテゴリを選んでください。カテゴリ別にログ分析できるので、適切な分類が重要です。',
                'keywords': 'FAQカテゴリ,カテゴリ分類,カテゴリ選択,FAQ分類',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How should I categorize FAQs?',
                'answer': '4 categories: Basic (check-in/WiFi), Facilities (kitchen/shower), Location (station/convenience store), Trouble (lost key/malfunction). Choose the category closest to the question content. Proper categorization is important for category-based log analysis.',
                'keywords': 'FAQ categories,categorization,category selection,FAQ classification',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'intent_key': 'faq_bulk_import',
        'category': 'faq_management',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'FAQを一括登録できますか？',
                'answer': 'Standard・Premiumプランでは「FAQ管理」からCSV一括登録（追加モード）が利用できます。現在は個別登録のみのプランでは、大量のFAQがある場合はサポートへご相談ください。',
                'keywords': 'FAQ一括登録,CSV登録,大量登録,インポート,バルク登録',
                'related_url': None
            },
            'en': {
                'question': 'Can I bulk import FAQs?',
                'answer': 'Standard and Premium plans can use CSV bulk registration (add mode) from "FAQ Management". For plans with individual registration only, please contact support for large FAQ volumes.',
                'keywords': 'bulk import FAQ,CSV import,mass registration,import,bulk registration',
                'related_url': None
            }
        }
    },
    # Category: ai_logic（AI仕組み） - 4項目
    {
        'intent_key': 'ai_how_it_works',
        'category': 'ai_logic',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'AIはどうやって質問に答えていますか？',
                'answer': 'OpenAI GPT-4o-miniを使用しています。登録されたFAQをシステムプロンプトに埋め込み、ゲストの質問に最適な回答を生成します。FAQ内容が充実しているほど、精度の高い回答ができます。',
                'keywords': 'AI仕組み,どうやって,GPT-4o-mini,仕組み,AIの仕組み',
                'related_url': None
            },
            'en': {
                'question': 'How does AI answer questions?',
                'answer': 'We use OpenAI GPT-4o-mini. Registered FAQs are embedded in the system prompt to generate optimal responses to guest questions. The more comprehensive your FAQs, the more accurate the responses.',
                'keywords': 'how AI works,mechanism,GPT-4o-mini,how it works,AI mechanism',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'ai_accuracy',
        'category': 'ai_logic',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'AIの回答精度を上げるには？',
                'answer': 'FAQ登録時のポイント：1. 質問文は具体的に（「WiFiは？」より「WiFiパスワードは？」）、2. 回答は簡潔に（200文字以内）、3. キーワードを適切に設定、4. 優先度を調整。FAQが充実するほど精度が向上します。週次でログを確認し、答えられなかった質問をFAQに追加しましょう。',
                'keywords': 'AI精度,精度向上,回答精度,改善,正確性',
                'related_url': None
            },
            'en': {
                'question': 'How to improve AI response accuracy?',
                'answer': 'FAQ registration tips: 1. Make questions specific ("WiFi password?" vs "WiFi?"), 2. Keep answers concise (under 200 characters), 3. Set keywords properly, 4. Adjust priority. More FAQs improve accuracy. Check logs weekly and add unanswered questions to FAQs.',
                'keywords': 'AI accuracy,improve accuracy,response quality,improvement,accuracy',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'ai_languages',
        'category': 'ai_logic',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '対応言語は何語ですか？',
                'answer': '現在は日本語、英語、繁体中国語、フランス語、韓国語の5言語に対応しています。ゲストが選択した言語で自動的に回答します。FAQは各言語で登録が必要です。翻訳支援機能も今後追加予定です。',
                'keywords': '対応言語,多言語,言語設定,何語,サポート言語',
                'related_url': '/admin/manual'
            },
            'en': {
                'question': 'What languages are supported?',
                'answer': 'Currently supports 5 languages: Japanese, English, Traditional Chinese, French, and Korean. Responses are automatically provided in the guest\'s selected language. FAQs must be registered in each language. Translation assistance feature coming soon.',
                'keywords': 'supported languages,multilingual,language settings,what languages,supported languages',
                'related_url': '/admin/manual'
            }
        }
    },
    {
        'intent_key': 'ai_limitations',
        'category': 'ai_logic',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'AIが答えられない質問はありますか？',
                'answer': 'はい。FAQに登録されていない内容や、リアルタイム情報（天気、在庫状況等）には答えられません。その場合は「スタッフに確認してください」と案内されます。信頼度スコアが低い回答は自動的にスタッフへエスカレーションされます。',
                'keywords': 'AI限界,答えられない,できないこと,制限,対応不可',
                'related_url': None
            },
            'en': {
                'question': 'Are there questions AI cannot answer?',
                'answer': 'Yes. AI cannot answer content not registered in FAQs or real-time information (weather, inventory status, etc.). In such cases, it will suggest "Please check with staff." Low confidence responses are automatically escalated to staff.',
                'keywords': 'AI limitations,cannot answer,what it cannot do,restrictions,cannot handle',
                'related_url': None
            }
        }
    },
    # Category: logs（ログ分析） - 3項目
    {
        'intent_key': 'logs_view_questions',
        'category': 'logs',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'ゲストの質問履歴はどこで見られますか？',
                'answer': '現在、ログ管理機能は実装されていません。将来的には「ログ管理」→「質問履歴」から、日付・カテゴリ・キーワードで検索できる予定です。',
                'keywords': '質問履歴,ログ確認,履歴閲覧,チャットログ,ログ表示',
                'related_url': None
            },
            'en': {
                'question': 'Where can I view guest question history?',
                'answer': 'Log management functionality is currently not implemented. In the future, you will be able to search by date, category, and keywords from "Log Management" → "Question History".',
                'keywords': 'question history,view logs,history access,chat logs,log display',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'logs_unanswered',
        'category': 'logs',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'AIが答えられなかった質問を確認するには？',
                'answer': '現在、ログ管理機能は実装されていません。将来的には「ログ管理」で信頼度スコア0.5以下の質問をフィルタリングできる予定です。',
                'keywords': '答えられなかった質問,低信頼度,FAQ作成参考,未回答',
                'related_url': None
            },
            'en': {
                'question': 'How to check questions AI couldn\'t answer?',
                'answer': 'Log management functionality is currently not implemented. In the future, you will be able to filter questions with confidence score 0.5 or below in "Log Management".',
                'keywords': 'unanswered questions,low confidence,FAQ creation reference,unanswered',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'logs_analytics',
        'category': 'logs',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'よくある質問のランキングは？',
                'answer': '「ダッシュボード」で質問カテゴリ別の統計を確認できます。よく聞かれる質問TOP10のランキング機能は、将来的には追加予定です。ランキング上位の質問はFAQ優先度を高めに設定しましょう。',
                'keywords': 'ランキング,統計,よくある質問,分析,TOP10',
                'related_url': None
            },
            'en': {
                'question': 'Where is the FAQ ranking?',
                'answer': 'On the "Dashboard", you can view statistics by question category. The TOP 10 frequently asked questions ranking feature will be added in the future. Set higher FAQ priority for top-ranking questions.',
                'keywords': 'ranking,statistics,frequently asked,analysis,TOP10',
                'related_url': None
            }
        }
    },
    # Category: troubleshooting（トラブルシューティング） - 5項目
    {
        'intent_key': 'trouble_ai_slow',
        'category': 'troubleshooting',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'AIの応答が遅い場合は？',
                'answer': '通常3-5秒以内に応答します。10秒以上かかる場合は、ネットワーク状況を確認するか、ブラウザをリフレッシュしてください。問題が続く場合は、管理画面右下の「サポート」ボタンから、施設管理者専用問い合わせフォームにアクセスしてお問い合わせください。',
                'keywords': 'AI遅い,応答遅延,遅延,速度,レスポンス遅い',
                'related_url': None
            },
            'en': {
                'question': 'What if AI response is slow?',
                'answer': 'Normal response time is 3-5 seconds. If it takes over 10 seconds, check network conditions or refresh the browser. If the problem persists, please contact us via the support form accessible from the "Support" button at the bottom-right of the admin panel.',
                'keywords': 'AI slow,response delay,delay,speed,slow response',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'trouble_qr_not_working',
        'category': 'troubleshooting',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'QRコードが読み取れない場合は？',
                'answer': '原因：1. QRコードが小さすぎる（5cm未満）、2. 印刷が不鮮明、3. カメラの焦点が合っていない、4. 光沢紙で反射している。対処法：大きめのQRコードをマット紙で再印刷してください。それでも解決しない場合はQRコードを再生成してみてください。',
                'keywords': 'QRコード読み取れない,スキャンできない,QRエラー,認識しない',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'What if QR code doesn\'t scan?',
                'answer': 'Causes: 1. QR code too small (under 5cm), 2. Unclear printing, 3. Camera out of focus, 4. Reflection on glossy paper. Solution: Reprint a larger QR code on matte paper. If still not working, try regenerating the QR code.',
                'keywords': 'QR code not scanning,cannot scan,QR error,not recognized',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'intent_key': 'trouble_faq_not_updated',
        'category': 'troubleshooting',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'FAQを更新したのに反映されない？',
                'answer': 'FAQ更新後、システムプロンプトの再構築に最大5分かかります。5分待ってもダメな場合は、ブラウザキャッシュをクリアしてください（Ctrl+Shift+R または Cmd+Shift+R）。それでも解決しない場合は、管理画面右下の「サポート」ボタンから、施設管理者専用問い合わせフォームにアクセスしてお問い合わせください。',
                'keywords': 'FAQ反映されない,更新されない,変更されない,反映遅い',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'FAQ update not reflected?',
                'answer': 'After FAQ update, system prompt reconstruction takes up to 5 minutes. If still not working after 5 minutes, clear browser cache (Ctrl+Shift+R or Cmd+Shift+R). If still unresolved, please contact us via the support form accessible from the "Support" button at the bottom-right of the admin panel.',
                'keywords': 'FAQ not reflected,not updated,not changed,slow reflection',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'intent_key': 'trouble_cannot_login',
        'category': 'troubleshooting',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'ログインできない場合は？',
                'answer': 'パスワードリセットをお試しください。それでも解決しない場合、メールアドレスの登録ミスの可能性があります。管理画面右下の「サポート」ボタンから、施設管理者専用問い合わせフォームにアクセスしてお問い合わせください。',
                'keywords': 'ログインできない,パスワード,エラー',
                'related_url': None
            },
            'en': {
                'question': 'Cannot login?',
                'answer': 'Try password reset. If issue persists, email may be incorrect. Please contact us via the support form accessible from the "Support" button at the bottom-right of the admin panel.',
                'keywords': 'cannot login,password,error',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'trouble_contact_support',
        'category': 'troubleshooting',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'サポートへの問い合わせ方法は？',
                'answer': '管理画面右下の「サポート」ボタンから、施設管理者専用問い合わせフォームにアクセスできます。平日9-18時対応です。',
                'keywords': 'サポート,問い合わせ,ヘルプ,連絡先',
                'related_url': None
            },
            'en': {
                'question': 'How to contact support?',
                'answer': 'Access the facility manager inquiry form from the "Support" button at the bottom-right of the admin panel. Available weekdays 9am-6pm.',
                'keywords': 'support,contact,help,inquiry',
                'related_url': None
            }
        }
    },
    # Category: billing（料金） - 3項目
    {
        'intent_key': 'billing_plans',
        'category': 'billing',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': '料金プランは？',
                'answer': 'Freeプラン（無料、30質問限定）、Miniプラン（¥1,980/月+¥30/質問）、Smallプラン（¥3,980/月、200件/月）、Standardプラン（¥5,980/月、500件/月）、Premiumプラン（¥7,980/月、1,000件/月）があります。詳細は料金ページをご確認ください。',
                'keywords': '料金,プラン,価格,費用,従量課金',
                'related_url': None
            },
            'en': {
                'question': 'Pricing plans?',
                'answer': 'Free Plan (free, 30 questions limit), Mini Plan (¥1,980/month + ¥30/question), Small Plan (¥3,980/month, 200/month), Standard Plan (¥5,980/month, 500/month), Premium Plan (¥7,980/month, 1,000/month). See pricing page for details.',
                'keywords': 'pricing,plans,cost,fee,pay-as-you-go',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'billing_cancellation',
        'category': 'billing',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '解約方法は？',
                'answer': '左メニュー「プラン・請求」ページで「解約する」ボタンから手続きできます。期間末解約（請求期間終了後にFreeへ）または即時解約を選べます。有料プランかつ決済（Stripe）設定済みの施設にのみ解約ブロックが表示されます。解約後もデータは保持され、再度有料プランへはプラン変更から変更できます。',
                'keywords': '解約,退会,キャンセル,停止',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How to cancel?',
                'answer': 'On the left menu "Plan & Billing" page, use the "Cancel" button. You can choose cancel at period end (move to Free after current period) or cancel immediately. The cancel block is shown only for paid plans with Stripe set up. Data is retained after cancellation; you can resubscribe via Plan change.',
                'keywords': 'cancel,unsubscribe,terminate',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'intent_key': 'billing_invoice',
        'category': 'billing',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '請求書の発行は？',
                'answer': '当サービスはクレジットカード決済（Stripe）による月次利用確定後の自動決済を前提としたサブスクリプションサービスのため、原則として請求書の発行には対応しておりません。なお、領収書（電子）は管理画面よりいつでもダウンロード可能ですので、経費精算や会計処理にはそちらをご利用ください。※ 一部の法人・年額契約をご検討の場合に限り、事前のご相談により対応可能な場合があります。',
                'keywords': '請求書,領収書,インボイス,ダウンロード',
                'related_url': None
            },
            'en': {
                'question': 'Invoice issuance?',
                'answer': 'As this service is a subscription service based on automatic monthly payment via credit card (Stripe) after usage confirmation, we generally do not issue invoices. However, electronic receipts are available for download from the admin panel at any time for expense reimbursement and accounting purposes. * For some corporate or annual contract cases, we may be able to accommodate upon prior consultation.',
                'keywords': 'invoice,receipt,download',
                'related_url': None
            }
        }
    },
    # Category: billing（プラン・請求・第7章） - 5項目追加
    {
        'intent_key': 'plan_billing_overview',
        'category': 'billing',
        'display_order': 89,
        'translations': {
            'ja': {
                'question': 'プラン・請求ページでは何ができますか？',
                'answer': '左メニュー「プラン・請求」で、料金プランの確認・変更、解約、請求履歴・領収書の確認ができます。現在のプラン確認、プラン変更、解約、請求履歴・領収書の表示が可能です。Stripe未設定の施設では「プラン変更・解約は利用できません」と表示されます。',
                'keywords': 'プラン・請求,料金,解約,請求履歴,領収書',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'What can I do on the Plan & Billing page?',
                'answer': 'From the left menu "Plan & Billing" you can check and change your plan, cancel, and view billing history and receipts. If Stripe is not set up, "Plan change and cancellation are not available" is displayed.',
                'keywords': 'plan,billing,pricing,cancel,invoice,receipt',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'intent_key': 'plan_billing_current_list',
        'category': 'billing',
        'display_order': 88,
        'translations': {
            'ja': {
                'question': '現在のプランとプラン一覧の見方は？',
                'answer': 'ページ上部「現在のプラン」でプラン名・月額を確認できます。プラン一覧の表でFree/Mini/Small/Standard/Premiumの月額・月間質問数・FAQ数・言語数を確認できます。現在契約中のプランには「（現在）」と表示されます。料金はFree無料、Mini¥1,980/月+従量、Small¥3,980/月、Standard¥5,980/月、Premium¥7,980/月です。',
                'keywords': '現在のプラン,プラン一覧,料金,月額,FAQ数',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How do I view my current plan and plan list?',
                'answer': 'Check plan name and monthly rate at "Current plan" at the top. The plan table shows Free/Mini/Small/Standard/Premium with monthly rate, question limit, FAQ limit, and language count. Your current plan is marked "(Current)".',
                'keywords': 'current plan,plan list,pricing,monthly,FAQ limit',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'intent_key': 'plan_billing_change',
        'category': 'billing',
        'display_order': 87,
        'translations': {
            'ja': {
                'question': 'プラン変更の手順は？',
                'answer': 'プラン・請求ページで、変更したいプラン行の「プラン変更」ボタンをクリック→確認モーダルでプラン名・月額を確認→「変更する」で実行。変更後は画面上の現在プラン表示が更新されます。既存のQRコード・FAQ・施設設定はそのまま利用できます。Stripe設定済みで現在と異なるプランの場合のみボタンが表示されます。',
                'keywords': 'プラン変更,アップグレード,ダウングレード,手順',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How do I change my plan?',
                'answer': 'On the Plan & Billing page, click "Change plan" for the desired plan→confirm in the modal→click "Change" to apply. Your current plan display updates. Existing QR codes, FAQs, and facility settings remain. The button appears only when Stripe is set up and the plan is different from current.',
                'keywords': 'plan change,upgrade,downgrade,procedure',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'intent_key': 'plan_billing_cancel',
        'category': 'billing',
        'display_order': 86,
        'translations': {
            'ja': {
                'question': '解約の手順は？',
                'answer': 'プラン・請求ページで「解約する」→解約確認モーダルで「期間末で解約」（請求期間終了後にFreeへ）または「即時解約」を選択→「解約する」で完了。解約後はFreeプランになります。再度有料プランへ変更する場合はプラン変更から選択できます。有料プランかつStripe設定済みの施設にのみ解約ブロックが表示されます。',
                'keywords': '解約,キャンセル,期間末,即時解約,Freeプラン',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How do I cancel my subscription?',
                'answer': 'On Plan & Billing page click "Cancel"→in the modal choose "Cancel at period end" (move to Free after current period) or "Cancel immediately"→click "Cancel" to confirm. After cancellation you are on the Free plan. To resubscribe, use Plan change. Cancel block is shown only for paid plans with Stripe set up.',
                'keywords': 'cancel,subscription,end of period,immediate,Free plan',
                'related_url': '/admin/billing'
            }
        }
    },
    {
        'intent_key': 'plan_billing_invoices',
        'category': 'billing',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': '請求履歴と領収書の見方は？',
                'answer': 'プラン・請求ページの「請求履歴・領収書」の表で、請求日・金額・ステータスを確認できます。各行の「領収書を表示」をクリックすると領収書ページが別タブで開きます。印刷・保存はその画面から行えます。請求がまだない場合は「請求履歴はありません。」と表示されます。',
                'keywords': '請求履歴,領収書,インボイス,ダウンロード,経費精算',
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'How do I view billing history and receipts?',
                'answer': 'On the Plan & Billing page, the "Billing history & receipts" table shows request date, amount, and status. Click "View receipt" on each row to open the receipt in a new tab. Print or save from that screen. If there are no invoices yet, "No billing history" is displayed.',
                'keywords': 'billing history,receipt,invoice,download,expense',
                'related_url': '/admin/billing'
            }
        }
    },
    # Category: security（セキュリティ） - 2項目
    {
        'intent_key': 'security_data_management',
        'category': 'security',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'ゲストのデータはどう管理されていますか？',
                'answer': 'AWS上で暗号化して保存し、GDPR・個人情報保護法に準拠しています。ゲストの個人情報は収集しません（質問内容とIPアドレスのみ記録）。',
                'keywords': 'データ管理,セキュリティ,個人情報,プライバシー',
                'related_url': None
            },
            'en': {
                'question': 'How is guest data managed?',
                'answer': 'Encrypted storage on AWS, GDPR and privacy law compliant. No personal info collected (only questions and IP addresses).',
                'keywords': 'data management,security,privacy,GDPR',
                'related_url': None
            }
        }
    },
    {
        'intent_key': 'security_staff_permissions',
        'category': 'security',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': 'スタッフの権限設定は？',
                'answer': '現在、スタッフ権限設定機能は実装されていません。将来的には「設定」→「スタッフ管理」から、管理者: 全機能、編集者: FAQ編集・ログ閲覧、閲覧者: ログ閲覧のみの権限を設定できる予定です。',
                'keywords': 'スタッフ権限,アクセス制御,ロール,設定',
                'related_url': None
            },
            'en': {
                'question': 'Staff permission settings?',
                'answer': 'Staff permission settings functionality is currently not implemented. In the future, you will be able to set permissions from "Settings" → "Staff Management": Admin: All features, Editor: FAQ editing & log viewing, Viewer: Log viewing only.',
                'keywords': 'staff permissions,access control,roles,settings',
                'related_url': None
            }
        }
    }
]


async def insert_operator_faqs():
    """
    宿泊事業者向けFAQ初期データ投入
    """
    # DB接続（環境変数DATABASE_URLから取得、なければsettingsから取得）
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        try:
            from app.core.config import settings
            database_url = settings.database_url
        except Exception as e:
            print(f"❌ エラー: DATABASE_URLが設定されていません: {e}")
            print("環境変数DATABASE_URLを設定してください:")
            print("  export DATABASE_URL='postgresql://postgres:password@host:port/database'")
            sys.exit(1)
    
    if database_url.startswith("postgresql://"):
        async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        async_database_url = database_url
    
    engine = create_async_engine(async_database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            created_count = 0
            skipped_count = 0

            for faq_data in OPERATOR_FAQ_DATA:
                # 既存チェック
                result = await db.execute(
                    select(OperatorFaq).where(OperatorFaq.intent_key == faq_data['intent_key'])
                )
                existing_faq = result.scalar_one_or_none()

                if existing_faq:
                    logger.info(f"FAQ already exists: {faq_data['intent_key']}, skipping...")
                    skipped_count += 1
                    continue

                # FAQマスター作成
                operator_faq = OperatorFaq(
                    category=faq_data['category'],
                    intent_key=faq_data['intent_key'],
                    display_order=faq_data['display_order'],
                    is_active=True
                )
                db.add(operator_faq)
                await db.flush()  # IDを取得するためにflush

                # 翻訳データ作成
                for lang, translation_data in faq_data['translations'].items():
                    translation = OperatorFaqTranslation(
                        faq_id=operator_faq.id,
                        language=lang,
                        question=translation_data['question'],
                        answer=translation_data['answer'],
                        keywords=translation_data.get('keywords'),
                        related_url=translation_data.get('related_url')
                    )
                    db.add(translation)

                created_count += 1
                logger.info(f"Created FAQ: {faq_data['intent_key']} ({faq_data['category']})")

            await db.commit()

            logger.info(f"Operator FAQ insertion completed: created={created_count}, skipped={skipped_count}")
            print(f"✅ 宿泊事業者向けFAQ初期データ投入完了")
            print(f"   作成成功数: {created_count}")
            print(f"   スキップ数: {skipped_count}")

            # カテゴリ別集計
            result = await db.execute(
                select(OperatorFaq.category, func.count(OperatorFaq.id))
                .group_by(OperatorFaq.category)
            )
            categories = {row[0]: row[1] for row in result.all()}
            print(f"   カテゴリ別: {categories}")

        except Exception as e:
            logger.error(f"Error inserting operator FAQs: {str(e)}", exc_info=True)
            await db.rollback()
            print(f"❌ エラー発生: {str(e)}")
            raise
        finally:
            await engine.dispose()


def main():
    """メイン関数"""
    print("🚀 宿泊事業者向けFAQ初期データ投入を開始します...")
    print(f"   投入予定数: {len(OPERATOR_FAQ_DATA)}件")
    asyncio.run(insert_operator_faqs())


if __name__ == "__main__":
    main()

