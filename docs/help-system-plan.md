# Phase 2: 統合ヘルプシステム実装計画書

## ドキュメント情報
- **プロジェクト**: YadOPERA（宿泊施設管理システム）
- **フェーズ**: Phase 2 - 統合ヘルプシステム
- **作成日**: 2025年12月25日
- **バージョン**: 1.0
- **基準文書**: 
  - やどぺら v0.3.9 要約定義書
  - やどぺら v0.3.7 アーキテクチャ設計書

---

## 目次

1. [エグゼクティブサマリー](#1-エグゼクティブサマリー)
2. [システム概要](#2-システム概要)
3. [技術スタック](#3-技術スタック)
4. [データベース設計](#4-データベース設計)
5. [API設計](#5-api設計)
6. [フロントエンド設計](#6-フロントエンド設計)
7. [実装ステップ](#7-実装ステップ)
8. [テスト計画](#8-テスト計画)
9. [デプロイ計画](#9-デプロイ計画)

---

## 1. エグゼクティブサマリー

### 1.1 目的

Phase 2では、宿泊施設管理者向けの統合ヘルプシステムを実装します。これにより、PoC期間中のサポート工数を**70%削減**し、管理者の初期操作つまずきによる解約率を低減します。

### 1.2 主要機能

1. **宿泊事業者向けFAQ管理**
   - 20-30項目の初期FAQデータ投入
   - カテゴリ別FAQ表示（初期設定、QRコード、FAQ管理、AI仕組み、ログ分析、トラブルシューティング、料金、セキュリティ）
   - 多言語対応（日本語・英語）

2. **管理画面内AIヘルプチャット**
   - OpenAI GPT-4o-miniを使用したリアルタイム回答
   - システムプロンプトにFAQ全文を埋め込み（pgvector不要）
   - 該当FAQ + 設定画面URLリンク自動返却
   - 管理画面右下にフローティングチャット

### 1.3 期待効果

| 指標 | 目標値 |
|------|--------|
| サポート工数削減 | 70% |
| 解約率低減 | 10%以上 |
| FAQ参照率 | 80%以上 |
| AIチャット利用率 | 50%以上 |

---

## 2. システム概要

### 2.1 システム構成

```
┌─────────────────────────────────────────┐
│     管理画面（Vue.js 3）                  │
│  ┌───────────────────────────────────┐  │
│  │  全ページ共通                      │  │
│  │  └─ HelpButton（右下固定）         │  │
│  │      └─ HelpModal                 │  │
│  │          ├─ FAQタブ               │  │
│  │          │   ├─ カテゴリ選択      │  │
│  │          │   ├─ FAQ検索           │  │
│  │          │   └─ FAQ一覧表示       │  │
│  │          └─ AIチャットタブ        │  │
│  │              ├─ チャット履歴      │  │
│  │              ├─ メッセージ入力    │  │
│  │              └─ 関連FAQ提案       │  │
│  └───────────────────────────────────┘  │
└────────┬────────────────────────────────┘
         │ HTTPS/REST
         ↓
┌─────────────────────────────────────────┐
│     FastAPI Backend                      │
│  ┌───────────────────────────────────┐  │
│  │  /api/v1/help/*                   │  │
│  │  ├─ GET /faqs                     │  │
│  │  ├─ GET /faqs/{category}          │  │
│  │  ├─ GET /search?q={query}         │  │
│  │  └─ POST /chat                    │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Services                         │  │
│  │  ├─ OperatorFaqService            │  │
│  │  └─ OperatorHelpChatService       │  │
│  └───────────────────────────────────┘  │
└────────┬────────────────────────────────┘
         │
         ├────────────────┬───────────────┐
         ↓                ↓               ↓
┌──────────────┐  ┌─────────────┐  ┌──────────────┐
│ PostgreSQL   │  │ OpenAI API  │  │    Redis     │
│ operator_faqs│  │ GPT-4o-mini │  │ (キャッシュ) │
│ operator_faq_│  │             │  │              │
│ translations │  │             │  │              │
└──────────────┘  └─────────────┘  └──────────────┘
```

### 2.2 データフロー

#### FAQ検索フロー

```
管理者がFAQ検索
    ↓
GET /api/v1/help/search?q={query}
    ↓
OperatorFaqService.search_faqs()
    ├─ operator_faq_translationsテーブル全文検索
    ├─ PostgreSQL LIKE検索（question, answer, keywords）
    └─ 関連度順にソート
    ↓
FAQ一覧 + 該当箇所ハイライト返却
```

#### AIチャットフロー

```
管理者が質問入力
    ↓
POST /api/v1/help/chat
    ├─ Request Body:
    │   {
    │     "message": "FAQの登録方法は？",
    │     "language": "ja"
    │   }
    ↓
OperatorHelpChatService.process_message()
    ├─ システムプロンプト構築
    │   ├─ 全FAQ（20-30項目）をMarkdown形式で埋め込み
    │   ├─ 管理画面URLマップ
    │   └─ 回答ガイドライン
    ↓
OpenAI GPT-4o-mini API呼び出し
    ├─ Model: gpt-4o-mini-2024-07-18
    ├─ Max tokens: 500
    ├─ Temperature: 0.7
    └─ System Prompt: FAQ全文 + URLマップ
    ↓
AI回答生成
    ├─ 回答文
    ├─ 関連FAQ ID配列
    └─ 設定画面URL
    ↓
Response:
    {
      "response": "FAQ登録は...",
      "related_faqs": [1, 3, 5],
      "related_url": "/admin/faqs"
    }
```

---

## 3. 技術スタック

### 3.1 Backend

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.11+ | 実行環境 |
| FastAPI | 0.109+ | APIフレームワーク |
| SQLAlchemy | 2.0+ | ORM（async対応） |
| Alembic | 1.13+ | マイグレーション |
| OpenAI SDK | 最新 | AI API連携 |
| python-jose | 3.3+ | JWT認証 |
| Redis | 7.2+ | キャッシュ |

### 3.2 Frontend

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Vue.js | 3.4+ | UIフレームワーク |
| TypeScript | 5.3+ | 型安全 |
| Tailwind CSS | 3.4+ | スタイリング |
| Axios | 1.6+ | HTTP通信 |
| Pinia | 2.1+ | 状態管理 |

### 3.3 AI/API

| サービス | モデル | 用途 |
|---------|--------|------|
| OpenAI | gpt-4o-mini-2024-07-18 | AIチャット回答生成 |

**重要**: pgvectorは**使用しない**（FAQ件数が少ないため、システムプロンプトに全文埋め込みで十分）

---

## 4. データベース設計

### 4.1 テーブル構造

#### operator_faqs（事業者向けFAQ）

```sql
CREATE TABLE operator_faqs (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,  -- 'setup', 'qrcode', 'faq_management', 'ai_logic', 'logs', 'troubleshooting', 'billing', 'security'
    intent_key VARCHAR(100) NOT NULL,  -- 'setup_account_creation', 'qrcode_placement' など
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(intent_key)
);

CREATE INDEX idx_operator_faqs_category ON operator_faqs(category);
CREATE INDEX idx_operator_faqs_is_active ON operator_faqs(is_active);
CREATE INDEX idx_operator_faqs_display_order ON operator_faqs(display_order);
```

#### operator_faq_translations（FAQ翻訳）

```sql
CREATE TABLE operator_faq_translations (
    id SERIAL PRIMARY KEY,
    faq_id INTEGER NOT NULL REFERENCES operator_faqs(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL DEFAULT 'ja',  -- 'ja', 'en'
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT,  -- 検索用キーワード（カンマ区切り）
    related_url TEXT,  -- 管理画面内リンク（例: '/admin/faqs'）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(faq_id, language)
);

CREATE INDEX idx_operator_faq_translations_faq_id ON operator_faq_translations(faq_id);
CREATE INDEX idx_operator_faq_translations_language ON operator_faq_translations(language);
```

### 4.2 マイグレーション

#### マイグレーション1: テーブル作成

**ファイル**: `backend/alembic/versions/YYYYMMDD_create_operator_help_tables.py`

```python
"""create operator help tables

Revision ID: xxx
Revises: xxx
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # operator_faqs
    op.create_table(
        'operator_faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('intent_key', sa.String(100), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('intent_key')
    )
    
    op.create_index('idx_operator_faqs_category', 'operator_faqs', ['category'])
    op.create_index('idx_operator_faqs_is_active', 'operator_faqs', ['is_active'])
    op.create_index('idx_operator_faqs_display_order', 'operator_faqs', ['display_order'])
    
    # operator_faq_translations
    op.create_table(
        'operator_faq_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('faq_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(10), nullable=False, server_default='ja'),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('keywords', sa.Text()),
        sa.Column('related_url', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['faq_id'], ['operator_faqs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('faq_id', 'language')
    )
    
    op.create_index('idx_operator_faq_translations_faq_id', 'operator_faq_translations', ['faq_id'])
    op.create_index('idx_operator_faq_translations_language', 'operator_faq_translations', ['language'])

def downgrade():
    op.drop_index('idx_operator_faq_translations_language')
    op.drop_index('idx_operator_faq_translations_faq_id')
    op.drop_table('operator_faq_translations')
    
    op.drop_index('idx_operator_faqs_display_order')
    op.drop_index('idx_operator_faqs_is_active')
    op.drop_index('idx_operator_faqs_category')
    op.drop_table('operator_faqs')
```

#### マイグレーション2: 初期FAQデータ投入

**ファイル**: `backend/alembic/versions/YYYYMMDD_insert_initial_operator_faqs.py`

```python
"""insert initial operator faqs

Revision ID: xxx
Revises: xxx
Create Date: 2025-12-25
"""
from alembic import op
import sqlalchemy as sa

# 初期FAQデータ（30項目）
INITIAL_FAQS = [
    # Category: setup（初期設定） - 5項目
    {
        'category': 'setup',
        'intent_key': 'setup_account_creation',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'アカウント作成の手順は？',
                'answer': '管理画面トップページから「新規登録」をクリックし、メールアドレス・パスワード・施設情報を入力してください。メール認証後、ログインできます。',
                'keywords': 'アカウント作成,新規登録,サインアップ,初期設定',
                'related_url': '/admin/register'
            },
            'en': {
                'question': 'How to create an account?',
                'answer': 'Click "Sign Up" from the top page, enter your email, password, and facility information. After email verification, you can log in.',
                'keywords': 'account creation,sign up,registration,initial setup',
                'related_url': '/admin/register'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_facility_info',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '施設情報はどこで登録しますか？',
                'answer': 'ログイン後、「設定」→「施設設定」から施設名、住所、チェックイン/アウト時間、WiFi情報などを登録できます。',
                'keywords': '施設情報,施設設定,基本情報,WiFi設定',
                'related_url': '/admin/facility'
            },
            'en': {
                'question': 'Where do I register facility information?',
                'answer': 'After login, go to "Settings" → "Facility Settings" to register facility name, address, check-in/out times, WiFi info, etc.',
                'keywords': 'facility information,facility settings,basic info,WiFi settings',
                'related_url': '/admin/facility'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_first_login',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': '初回ログイン後にまずやるべきことは？',
                'answer': '以下の順番で設定を行ってください：1. 施設情報登録、2. FAQ初期テンプレート確認・編集、3. QRコード生成・印刷、4. テスト質問で動作確認。',
                'keywords': '初回ログイン,初期設定,はじめに,スタート',
                'related_url': '/admin/dashboard'
            },
            'en': {
                'question': 'What should I do after first login?',
                'answer': 'Follow these steps: 1. Register facility info, 2. Review/edit initial FAQ templates, 3. Generate/print QR codes, 4. Test with sample questions.',
                'keywords': 'first login,initial setup,getting started,start',
                'related_url': '/admin/dashboard'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_staff_account',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'スタッフアカウントを追加できますか？',
                'answer': 'はい。「設定」→「スタッフ管理」から、スタッフのメールアドレスと権限レベルを設定してアカウントを追加できます。',
                'keywords': 'スタッフ追加,複数ユーザー,アカウント追加,権限設定',
                'related_url': '/admin/staff'
            },
            'en': {
                'question': 'Can I add staff accounts?',
                'answer': 'Yes. From "Settings" → "Staff Management", you can add staff accounts by setting their email and permission level.',
                'keywords': 'add staff,multiple users,add account,permissions',
                'related_url': '/admin/staff'
            }
        }
    },
    {
        'category': 'setup',
        'intent_key': 'setup_password_reset',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'パスワードを忘れた場合は？',
                'answer': 'ログイン画面の「パスワードを忘れた場合」リンクをクリックし、メールアドレスを入力してください。パスワードリセット用のリンクが送信されます。',
                'keywords': 'パスワード忘れ,パスワードリセット,ログインできない',
                'related_url': '/admin/login'
            },
            'en': {
                'question': 'What if I forget my password?',
                'answer': 'Click "Forgot password?" on the login screen, enter your email, and you will receive a password reset link.',
                'keywords': 'forgot password,password reset,cannot login',
                'related_url': '/admin/login'
            }
        }
    },
    
    # Category: qrcode（QRコード設置） - 4項目
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_placement',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'QRコードはどこに貼るのがベストですか？',
                'answer': 'おすすめの設置場所：1. エントランス（最優先）、2. 各部屋、3. キッチン、4. ラウンジ。設置場所ごとに異なるQRコードを生成できます。',
                'keywords': 'QRコード設置,設置場所,おすすめ場所,配置',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'Where is the best place to put QR codes?',
                'answer': 'Recommended locations: 1. Entrance (highest priority), 2. Each room, 3. Kitchen, 4. Lounge. You can generate different QR codes for each location.',
                'keywords': 'QR code placement,location,recommended spots,positioning',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_multiple',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '複数のQRコードを使い分けられますか？',
                'answer': 'はい。設置場所ごとにQRコードを生成できます。各QRコードは設置場所情報を含むため、どこから質問が来たか追跡できます。',
                'keywords': '複数QRコード,QRコード使い分け,場所別QRコード',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'Can I use multiple QR codes?',
                'answer': 'Yes. You can generate QR codes for each location. Each QR code includes location info, so you can track where questions come from.',
                'keywords': 'multiple QR codes,QR code variation,location-specific codes',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_print_size',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'QRコードの印刷サイズの推奨は？',
                'answer': 'A4用紙1枚に1つのQRコードが推奨です。最小サイズは5cm×5cm、推奨サイズは10cm×10cm以上です。小さすぎるとスマホで読み取りにくくなります。',
                'keywords': 'QRコード印刷,印刷サイズ,推奨サイズ,最小サイズ',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'What is the recommended QR code print size?',
                'answer': 'One QR code per A4 sheet is recommended. Minimum size is 5cm×5cm, recommended size is 10cm×10cm or larger. Too small makes it hard to scan with smartphones.',
                'keywords': 'QR code printing,print size,recommended size,minimum size',
                'related_url': '/admin/qr-code'
            }
        }
    },
    {
        'category': 'qrcode',
        'intent_key': 'qrcode_regenerate',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'QRコードを再発行したい場合は？',
                'answer': '「QRコード管理」から既存のQRコードを削除し、新しいQRコードを生成してください。古いQRコードは自動的に無効化されます。',
                'keywords': 'QRコード再発行,QRコード更新,QRコード削除',
                'related_url': '/admin/qr-code'
            },
            'en': {
                'question': 'How do I regenerate a QR code?',
                'answer': 'From "QR Code Management", delete the existing QR code and generate a new one. The old QR code will be automatically invalidated.',
                'keywords': 'regenerate QR code,update QR code,delete QR code',
                'related_url': '/admin/qr-code'
            }
        }
    },
    
    # Category: faq_management（FAQ管理） - 5項目
    {
        'category': 'faq_management',
        'intent_key': 'faq_template_usage',
        'display_order': 100,
        'translations': {
            'ja': {
                'question': 'FAQテンプレートの使い方は？',
                'answer': 'システムが20-30件の初期テンプレートを提供しています。「FAQ管理」から各テンプレートを確認し、施設に合わせて編集してください。不要なFAQは非アクティブ化できます。',
                'keywords': 'FAQテンプレート,初期FAQ,テンプレート編集',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to use FAQ templates?',
                'answer': 'The system provides 20-30 initial templates. From "FAQ Management", review each template and edit to match your facility. Unwanted FAQs can be deactivated.',
                'keywords': 'FAQ templates,initial FAQs,template editing',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_add_custom',
        'display_order': 95,
        'translations': {
            'ja': {
                'question': '自分でFAQを追加する方法は？',
                'answer': '「FAQ管理」→「新規FAQ追加」から、質問・回答・カテゴリ・優先度を入力して保存してください。保存時に埋め込みベクトルが自動生成されます。',
                'keywords': 'FAQ追加,カスタムFAQ,FAQ作成,新規FAQ',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How to add custom FAQs?',
                'answer': 'From "FAQ Management" → "Add New FAQ", enter question, answer, category, and priority, then save. Embedding vectors are automatically generated on save.',
                'keywords': 'add FAQ,custom FAQ,create FAQ,new FAQ',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_priority',
        'display_order': 90,
        'translations': {
            'ja': {
                'question': 'FAQの優先度とは何ですか？',
                'answer': '優先度（1-5）は、AI検索時のランキングに影響します。優先度5が最高で、よくある質問には高い優先度を設定してください。',
                'keywords': 'FAQ優先度,優先順位,ランキング',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'What is FAQ priority?',
                'answer': 'Priority (1-5) affects ranking in AI search. Priority 5 is highest. Set high priority for frequently asked questions.',
                'keywords': 'FAQ priority,ranking,priority level',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_category',
        'display_order': 85,
        'translations': {
            'ja': {
                'question': 'カテゴリはどう分けるべきですか？',
                'answer': 'カテゴリは4種類：基本情報（チェックイン/WiFi等）、設備（キッチン/シャワー等）、周辺情報（駅/コンビニ等）、トラブル（鍵紛失/故障等）。質問内容に最も近いカテゴリを選んでください。',
                'keywords': 'FAQカテゴリ,カテゴリ分類,カテゴリ選択',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'How should I categorize FAQs?',
                'answer': '4 categories: Basic (check-in/WiFi), Facilities (kitchen/shower), Location (station/convenience store), Trouble (lost key/malfunction). Choose the category closest to the question content.',
                'keywords': 'FAQ categories,categorization,category selection',
                'related_url': '/admin/faqs'
            }
        }
    },
    {
        'category': 'faq_management',
        'intent_key': 'faq_bulk_import',
        'display_order': 80,
        'translations': {
            'ja': {
                'question': 'FAQを一括登録できますか？',
                'answer': '現在は個別登録のみですが、Phase 2でCSV一括インポート機能を追加予定です。大量のFAQがある場合は、サポートチームにご相談ください。',
                'keywords': 'FAQ一括登録,CSV登録,大量登録,インポート',
                'related_url': '/admin/faqs'
            },
            'en': {
                'question': 'Can I bulk import FAQs?',
                'answer': 'Currently only individual registration is supported, but CSV bulk import will be added in Phase 2. For large FAQ volumes, please