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
                'related_url': '/admin/register'
            },
            'en': {
                'question': 'How to create an account?',
                'answer': 'Click "Sign Up" from the top page, enter your email, password, and facility information. After email verification, you can log in. Please complete facility settings on first login.',
                'keywords': 'account creation,sign up,registration,initial setup,account opening',
                'related_url': '/admin/register'
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
                'related_url': '/admin/facility'
            },
            'en': {
                'question': 'Where do I register facility information?',
                'answer': 'After login, go to "Settings" → "Facility Settings" to register facility name, address, check-in/out times, WiFi info, room count, etc. This information is used for automatic guest responses.',
                'keywords': 'facility information,facility settings,basic info,WiFi settings,facility registration',
                'related_url': '/admin/facility'
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
                'answer': '以下の順番で設定を行ってください：1. 施設情報登録（WiFiパスワード、チェックイン時間など）、2. FAQ初期テンプレート確認・編集、3. QRコード生成・印刷、4. テスト質問で動作確認。全て完了するまで約30分程度です。',
                'keywords': '初回ログイン,初期設定,はじめに,スタート,セットアップ',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'What should I do after first login?',
                'answer': 'Follow these steps: 1. Register facility info (WiFi password, check-in time, etc.), 2. Review/edit initial FAQ templates, 3. Generate/print QR codes, 4. Test with sample questions. Takes about 30 minutes total.',
                'keywords': 'first login,initial setup,getting started,start,setup',
                'related_url': '/admin/dashboard'
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
                'answer': 'はい。「設定」→「スタッフ管理」から、スタッフのメールアドレスと権限レベル（オーナー/マネージャー/スタッフ）を設定してアカウントを追加できます。スタッフには招待メールが送信されます。',
                'keywords': 'スタッフ追加,複数ユーザー,アカウント追加,権限設定,チーム管理',
                'related_url': '/admin/staff'
            },
            'en': {
                'question': 'Can I add staff accounts?',
                'answer': 'Yes. From "Settings" → "Staff Management", you can add staff accounts by setting their email and permission level (Owner/Manager/Staff). Staff will receive an invitation email.',
                'keywords': 'add staff,multiple users,add account,permissions,team management',
                'related_url': '/admin/staff'
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
                'answer': 'ログイン画面の「パスワードを忘れた場合」リンクをクリックし、登録メールアドレスを入力してください。パスワードリセット用のリンクが送信されます。リンクの有効期限は1時間です。',
                'keywords': 'パスワード忘れ,パスワードリセット,ログインできない,パスワード再設定',
                'related_url': '/admin/login'
            },
            'en': {
                'question': 'What if I forget my password?',
                'answer': 'Click "Forgot password?" on the login screen, enter your registered email address, and you will receive a password reset link. The link expires in 1 hour.',
                'keywords': 'forgot password,password reset,cannot login,reset password',
                'related_url': '/admin/login'
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
                'answer': 'A4用紙1枚に1つのQRコードが推奨です。最小サイズは5cm×5cm、推奨サイズは10cm×10cm以上です。小さすぎるとスマホで読み取りにくくなります。光沢紙よりマット紙の方が読み取りやすいです。PDF/PNG形式でダウンロードできます。',
                'keywords': 'QRコード印刷,印刷サイズ,推奨サイズ,最小サイズ,QRサイズ',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'What is the recommended QR code print size?',
                'answer': 'One QR code per A4 sheet is recommended. Minimum size is 5cm×5cm, recommended size is 10cm×10cm or larger. Too small makes it hard to scan with smartphones. Matte paper is better than glossy. Available in PDF/PNG format.',
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
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'How do I regenerate a QR code?',
                'answer': 'From "QR Code Management", delete the existing QR code and generate a new one. The old QR code will be automatically invalidated. For security, periodic regeneration (every 3-6 months) is recommended.',
                'keywords': 'regenerate QR code,update QR code,delete QR code,QR regeneration',
                'related_url': '/admin/qr-code'
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
                'answer': 'システムが20-30件の初期テンプレートを提供しています。「FAQ管理」から各テンプレートを確認し、施設に合わせて編集してください。不要なFAQは非アクティブ化できます。WiFiパスワードやチェックイン時間など、施設固有の情報を必ず更新してください。',
                'keywords': 'FAQテンプレート,初期FAQ,テンプレート編集,FAQ雛形',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to use FAQ templates?',
                'answer': 'The system provides 20-30 initial templates. From "FAQ Management", review each template and edit to match your facility. Unwanted FAQs can be deactivated. Be sure to update facility-specific info like WiFi password and check-in time.',
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
                'answer': '優先度（1-5）は、AI検索時のランキングに影響します。優先度5が最高で、よくある質問には高い優先度を設定してください。例：WiFiパスワード（5）、チェックイン時間（5）、周辺観光（3）。ログ分析で質問頻度を確認し、優先度を調整しましょう。',
                'keywords': 'FAQ優先度,優先順位,ランキング,FAQ重要度',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'What is FAQ priority?',
                'answer': 'Priority (1-5) affects ranking in AI search. Priority 5 is highest. Set high priority for frequently asked questions. Examples: WiFi password (5), Check-in time (5), Local tourism (3). Check log analysis for question frequency and adjust priority accordingly.',
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
                'answer': '現在は個別登録のみですが、Phase 2でCSV一括インポート機能を追加予定です。大量のFAQがある場合は、サポートチーム（support@yadopera.com）にご相談ください。一時的に代行登録のサポートも可能です。',
                'keywords': 'FAQ一括登録,CSV登録,大量登録,インポート,バルク登録',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'Can I bulk import FAQs?',
                'answer': 'Currently only individual registration is supported, but CSV bulk import will be added in Phase 2. For large FAQ volumes, please contact our support team (support@yadopera.com). Temporary registration assistance is available.',
                'keywords': 'bulk import FAQ,CSV import,mass registration,import,bulk registration',
                'related_url': '/admin/faqs'
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
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'How does AI answer questions?',
                'answer': 'We use OpenAI GPT-4o-mini. Registered FAQs are embedded in the system prompt to generate optimal responses to guest questions. The more comprehensive your FAQs, the more accurate the responses.',
                'keywords': 'how AI works,mechanism,GPT-4o-mini,how it works,AI mechanism',
                'related_url': '/admin/dashboard'
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
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to improve AI response accuracy?',
                'answer': 'FAQ registration tips: 1. Make questions specific ("WiFi password?" vs "WiFi?"), 2. Keep answers concise (under 200 characters), 3. Set keywords properly, 4. Adjust priority. More FAQs improve accuracy. Check logs weekly and add unanswered questions to FAQs.',
                'keywords': 'AI accuracy,improve accuracy,response quality,improvement,accuracy',
                'related_url': '/admin/faqs'
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
                'answer': '現在は日本語、英語、中国語（簡体字・繁体字）、韓国語の5言語に対応しています。ゲストが選択した言語で自動的に回答します。FAQは各言語で登録が必要です。翻訳支援機能も今後追加予定です。',
                'keywords': '対応言語,多言語,言語設定,何語,サポート言語',
                'related_url': '/admin/facility'
            },
            'en': {
                'question': 'What languages are supported?',
                'answer': 'Currently supports 5 languages: Japanese, English, Chinese (Simplified/Traditional), and Korean. Responses are automatically provided in the guest\'s selected language. FAQs must be registered in each language. Translation assistance feature coming soon.',
                'keywords': 'supported languages,multilingual,language settings,what languages,supported languages',
                'related_url': '/admin/facility'
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
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'Are there questions AI cannot answer?',
                'answer': 'Yes. AI cannot answer content not registered in FAQs or real-time information (weather, inventory status, etc.). In such cases, it will suggest "Please check with staff." Low confidence responses are automatically escalated to staff.',
                'keywords': 'AI limitations,cannot answer,what it cannot do,restrictions,cannot handle',
                'related_url': '/admin/dashboard'
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
                'answer': '「ログ管理」→「質問履歴」から、日付・カテゴリ・キーワードで検索できます。各質問のAI信頼度スコア、ゲストの言語、設置場所も確認できます。CSVエクスポート機能もあります。',
                'keywords': '質問履歴,ログ確認,履歴閲覧,チャットログ,ログ表示',
                'related_url': '/admin/logs'
            },
            'en': {
                'question': 'Where can I view guest question history?',
                'answer': 'From "Log Management" → "Question History", you can search by date, category, and keywords. AI confidence scores, guest language, and location are also visible. CSV export function available.',
                'keywords': 'question history,view logs,history access,chat logs,log display',
                'related_url': '/admin/logs'
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
                'answer': '「ログ管理」で信頼度スコア0.5以下の質問をフィルタリングできます。これらの質問は新しいFAQ作成の参考になります。週次でチェックし、頻出する質問はFAQに追加しましょう。',
                'keywords': '答えられなかった質問,低信頼度,FAQ作成参考,未回答',
                'related_url': '/admin/logs'
            },
            'en': {
                'question': 'How to check questions AI couldn\'t answer?',
                'answer': 'In "Log Management", filter questions with confidence score 0.5 or below. These questions can be used as references for creating new FAQs. Check weekly and add frequently asked questions to FAQs.',
                'keywords': 'unanswered questions,low confidence,FAQ creation reference,unanswered',
                'related_url': '/admin/logs'
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
                'answer': '「ダッシュボード」で質問カテゴリ別の統計と、よく聞かれる質問TOP10を確認できます。週次・月次で傾向を分析できます。ランキング上位の質問はFAQ優先度を高めに設定しましょう。',
                'keywords': 'ランキング,統計,よくある質問,分析,TOP10',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'Where is the FAQ ranking?',
                'answer': 'On the "Dashboard", you can view statistics by question category and TOP 10 frequently asked questions. Analyze trends weekly/monthly. Set higher FAQ priority for top-ranking questions.',
                'keywords': 'ranking,statistics,frequently asked,analysis,TOP10',
                'related_url': '/admin/dashboard'
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
                'answer': '通常3-5秒以内に応答します。10秒以上かかる場合は、ネットワーク状況を確認するか、ブラウザをリフレッシュしてください。問題が続く場合はサポート（support@yadopera.com）にお問い合わせください。',
                'keywords': 'AI遅い,応答遅延,遅延,速度,レスポンス遅い',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'What if AI response is slow?',
                'answer': 'Normal response time is 3-5 seconds. If it takes over 10 seconds, check network conditions or refresh the browser. If the problem persists, contact support (support@yadopera.com).',
                'keywords': 'AI slow,response delay,delay,speed,slow response',
                'related_url': '/admin/dashboard'
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
                'answer': 'FAQ更新後、システムプロンプトの再構築に最大5分かかります。5分待ってもダメな場合は、ブラウザキャッシュをクリアしてください（Ctrl+Shift+R または Cmd+Shift+R）。それでも解決しない場合はサポートにご連絡ください。',
                'keywords': 'FAQ反映されない,更新されない,変更されない,反映遅い',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'FAQ update not reflected?',
                'answer': 'After FAQ update, system prompt reconstruction takes up to 5 minutes. If still not working after 5 minutes, clear browser cache (Ctrl+Shift+R or Cmd+Shift+R). If still unresolved, contact support.',
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
                'answer': 'パスワードリセットをお試しください。それでも解決しない場合、メールアドレスの登録ミスの可能性があります。サポート（support@yadopera.com）にお問い合わせください。',
                'keywords': 'ログインできない,パスワード,エラー',
                'related_url': '/admin/login'
            },
            'en': {
                'question': 'Cannot login?',
                'answer': 'Try password reset. If issue persists, email may be incorrect. Contact support (support@yadopera.com).',
                'keywords': 'cannot login,password,error',
                'related_url': '/admin/login'
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
                'answer': '管理画面右下の「サポート」ボタン、またはメール（support@yadopera.com）でお問い合わせください。平日9-18時対応です。',
                'keywords': 'サポート,問い合わせ,ヘルプ,連絡先',
                'related_url': '/admin/support'
            },
            'en': {
                'question': 'How to contact support?',
                'answer': 'Click "Support" button at bottom-right, or email support@yadopera.com. Available weekdays 9am-6pm.',
                'keywords': 'support,contact,help,inquiry',
                'related_url': '/admin/support'
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
                'related_url': '/admin/billing'
            },
            'en': {
                'question': 'Pricing plans?',
                'answer': 'Free Plan (free, 30 questions limit), Mini Plan (¥1,980/month + ¥30/question), Small Plan (¥3,980/month, 200/month), Standard Plan (¥5,980/month, 500/month), Premium Plan (¥7,980/month, 1,000/month). See pricing page for details.',
                'keywords': 'pricing,plans,cost,fee,pay-as-you-go',
                'related_url': '/admin/billing'
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
                'answer': '「設定」→「アカウント」→「解約する」から手続きできます。解約後もデータは30日間保持されます。',
                'keywords': '解約,退会,キャンセル,停止',
                'related_url': '/admin/settings/account'
            },
            'en': {
                'question': 'How to cancel?',
                'answer': 'Go to "Settings" → "Account" → "Cancel". Data is retained for 30 days after cancellation.',
                'keywords': 'cancel,unsubscribe,terminate',
                'related_url': '/admin/settings/account'
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
                'answer': '「設定」→「請求情報」から過去の請求書をダウンロードできます。PDF形式で発行されます。',
                'keywords': '請求書,領収書,インボイス,ダウンロード',
                'related_url': '/admin/billing/invoices'
            },
            'en': {
                'question': 'Invoice issuance?',
                'answer': 'Go to "Settings" → "Billing Info" to download past invoices in PDF format.',
                'keywords': 'invoice,receipt,download',
                'related_url': '/admin/billing/invoices'
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
                'related_url': '/admin/settings/security'
            },
            'en': {
                'question': 'How is guest data managed?',
                'answer': 'Encrypted storage on AWS, GDPR and privacy law compliant. No personal info collected (only questions and IP addresses).',
                'keywords': 'data management,security,privacy,GDPR',
                'related_url': '/admin/settings/security'
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
                'answer': '管理者: 全機能、編集者: FAQ編集・ログ閲覧、閲覧者: ログ閲覧のみ。権限は「設定」→「スタッフ管理」で変更できます。',
                'keywords': 'スタッフ権限,アクセス制御,ロール,設定',
                'related_url': '/admin/settings/staff'
            },
            'en': {
                'question': 'Staff permission settings?',
                'answer': 'Admin: All features, Editor: FAQ editing & log viewing, Viewer: Log viewing only. Permissions can be changed from "Settings" → "Staff Management".',
                'keywords': 'staff permissions,access control,roles,settings',
                'related_url': '/admin/settings/staff'
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

