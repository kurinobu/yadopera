# YadOPERA 開発者管理ページ実装計画書
## フェーズ2: 開発者管理ページ実装

作成日: 2024年12月28日
対象フェーズ: フェーズ2
所要時間: 10-14時間（約2日間）
優先度: 実装順序7番目

---

## 1. 実装目的

宿泊施設管理者ページのトラブル、エラー、数値などを閲覧可能にし、システムのメンテナンスとトラブルシューティングを効率化する。

---

## 2. 現状システム分析（エビデンスベース）

### 2.1 既存データベーステーブル構成

**確認方法:**
```bash
cat ./database_backups/database_backup_faq_refactor_before_20251223_092717.sql | grep "CREATE TABLE"
```

**確認済みテーブル:**

#### users テーブル（管理者情報）
```sql
CREATE TABLE public.users (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(50) DEFAULT 'staff'::character varying,
    full_name character varying(255),
    is_active boolean DEFAULT true,
    last_login_at timestamp with time zone,
    password_reset_token character varying(255),
    password_reset_expires timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
```
**重要:** `role`フィールドが存在し、拡張可能

#### messages テーブル（チャットメッセージ）
```sql
CREATE TABLE public.messages (
    id integer NOT NULL,
    conversation_id integer NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    ai_confidence numeric(3,2),
    matched_faq_ids integer[],
    tokens_used integer,
    response_time_ms integer,
    created_at timestamp with time zone DEFAULT now()
);
```
**活用可能:** AIチャット利用統計の算出に使用

#### conversations テーブル（会話セッション）
```sql
CREATE TABLE public.conversations (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    session_id character varying(100) NOT NULL,
    guest_language character varying(10) DEFAULT 'en'::character varying,
    location character varying(50),
    user_agent text,
    ip_address inet,
    started_at timestamp with time zone DEFAULT now(),
    last_activity_at timestamp with time zone DEFAULT now(),
    ended_at timestamp with time zone,
    is_escalated boolean DEFAULT false,
    total_messages integer DEFAULT 0,
    auto_resolved boolean DEFAULT false
);
```
**活用可能:** 施設ごとの利用統計、言語別統計に使用

#### faqs テーブル（FAQ本体）
```sql
CREATE TABLE public.faqs (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    category character varying(50) NOT NULL,
    language character varying(10) DEFAULT 'en'::character varying,
    question text NOT NULL,
    answer text NOT NULL,
    priority integer DEFAULT 1,
    is_active boolean DEFAULT true,
    created_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    embedding public.vector(1536)
);
```

#### facilities テーブル（宿泊施設）
```sql
CREATE TABLE public.facilities (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    ...
    is_active boolean DEFAULT true,
    ...
);
```

#### 既存の関連テーブル
- `escalations`: エスカレーション記録
- `faq_suggestions`: FAQ提案（AIから生成）
- `guest_feedback`: 宿泊客フィードバック
- `session_tokens`: セッション管理

### 2.2 既存バックエンドAPI構造

**確認方法:**
```bash
ls -la ./backend/app/
find ./backend/app -name "*.py" | grep -E "(auth|api|route)"
```

**確認済み構成:**
- **フレームワーク:** FastAPI（`./backend/app/main.py`で確認）
- **APIバージョン:** v1 (`/api/v1`)
- **認証エンドポイント:** `./backend/app/api/v1/auth.py`
- **管理者APIディレクトリ:** `./backend/app/api/v1/admin/`
  - `escalations.py`
  - `feedback.py`
  - `overnight_queue.py`

**main.py の確認済みエラーハンドラー:**
```python
# ./backend/app/main.py より抜粋
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_code_map = {
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMIT_EXCEEDED",
        status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
    }
    # 標準エラーフォーマットで返却
```
**重要:** 既にエラーハンドラーが標準化済み、拡張してログ記録可能

### 2.3 既存フロントエンド構造

**確認方法:**
```bash
find ./frontend/src -type d | head -20
```

**確認済み構成:**
- `./frontend/src/api/`: API呼び出しモジュール
  - `auth.ts`: 認証API
- `./frontend/src/pages/`: ページコンポーネント
- React/TypeScriptベース

### 2.4 現在記録されていないデータ（新規実装必要）

1. **FAQ閲覧数** → 記録テーブルなし
2. **システムエラーログ** → 専用テーブルなし（エラーハンドラーはあるが記録なし）
3. **管理者アクティビティ詳細ログ** → `last_login_at`のみ、詳細ログなし
4. **開発者用認証機構** → `role='developer'`未実装

---

## 3. フェーズ2実装範囲

### 3.1 実装する機能（優先度順）

#### A. システムエラーログ（優先度1）
- エラーレベル別表示（error, warning, critical）
- 施設別フィルタリング
- 時系列表示
- スタックトレース表示

#### B. 宿泊施設ごとの利用統計（優先度1）
- FAQ閲覧数ランキング
- AIチャット利用回数（日別/週別/月別）
- 言語別利用統計
- エスカレーション発生率

#### D. 宿泊施設管理者のアクティビティ（優先度1）
- ログイン履歴
- FAQ編集履歴（作成/更新/削除）
- アクセス元IP、User-Agent記録

### 3.2 フェーズ3以降に延期する機能

- **C. パフォーマンスメトリクス** → 専用モニタリングツール連携が必要
- **E. 宿泊客の問い合わせ傾向分析** → 高度なデータ分析が必要
- **F. システム稼働状況** → インフラモニタリングツールが必要

---

## 4. 実装ステップ詳細

### ステップ1: データベース拡張（2-3時間）

#### 1.1 新規テーブル設計

**error_logs テーブル**
```sql
CREATE TABLE public.error_logs (
    id SERIAL PRIMARY KEY,
    error_level VARCHAR(20) NOT NULL,  -- 'error', 'warning', 'critical'
    error_code VARCHAR(50) NOT NULL,   -- 'UNAUTHORIZED', 'INTERNAL_ERROR' 等
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    request_path VARCHAR(500),
    request_method VARCHAR(10),
    facility_id INTEGER REFERENCES public.facilities(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_error_logs_level ON public.error_logs(error_level);
CREATE INDEX idx_error_logs_facility ON public.error_logs(facility_id);
CREATE INDEX idx_error_logs_created ON public.error_logs(created_at DESC);
```

**admin_activity_logs テーブル**
```sql
CREATE TABLE public.admin_activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    facility_id INTEGER NOT NULL REFERENCES public.facilities(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,  -- 'login', 'logout', 'faq_create', 'faq_update', 'faq_delete', 'developer_access'
    target_resource_type VARCHAR(50),  -- 'faq', 'user', 'facility'
    target_resource_id INTEGER,
    description TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_activity_logs_user ON public.admin_activity_logs(user_id);
CREATE INDEX idx_activity_logs_facility ON public.admin_activity_logs(facility_id);
CREATE INDEX idx_activity_logs_action ON public.admin_activity_logs(action_type);
CREATE INDEX idx_activity_logs_created ON public.admin_activity_logs(created_at DESC);
```

**faq_view_logs テーブル**
```sql
CREATE TABLE public.faq_view_logs (
    id SERIAL PRIMARY KEY,
    faq_id INTEGER NOT NULL REFERENCES public.faqs(id) ON DELETE CASCADE,
    facility_id INTEGER NOT NULL REFERENCES public.facilities(id) ON DELETE CASCADE,
    conversation_id INTEGER REFERENCES public.conversations(id) ON DELETE SET NULL,
    message_id INTEGER REFERENCES public.messages(id) ON DELETE SET NULL,
    guest_language VARCHAR(10),
    viewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_faq_view_logs_faq ON public.faq_view_logs(faq_id);
CREATE INDEX idx_faq_view_logs_facility ON public.faq_view_logs(facility_id);
CREATE INDEX idx_faq_view_logs_viewed ON public.faq_view_logs(viewed_at DESC);
```

#### 1.2 usersテーブル拡張

**role フィールドの制約変更**
```sql
-- 既存: role character varying(50) DEFAULT 'staff'
-- 'developer' 値を許可（既存の VARCHAR(50) で対応可能、制約追加不要）

-- 開発者ユーザー作成用の準備
-- フェーズ3で CHECK 制約を追加する場合:
-- ALTER TABLE public.users ADD CONSTRAINT check_user_role 
-- CHECK (role IN ('staff', 'admin', 'developer'));
```

#### 1.3 Alembicマイグレーションファイル作成

**ファイル名:** `./backend/alembic/versions/20241228_add_developer_management_tables.py`

**作成コマンド:**
```bash
cd backend
alembic revision -m "add_developer_management_tables"
```

**マイグレーション内容:**
- `error_logs` テーブル作成
- `admin_activity_logs` テーブル作成
- `faq_view_logs` テーブル作成
- 各種インデックス作成

**マイグレーション実行:**
```bash
alembic upgrade head
```

**ロールバック:**
```bash
alembic downgrade -1
```

---

### ステップ2: バックエンドAPI実装（4-5時間）

#### 2.1 開発者認証機能

**ファイル:** `./backend/app/api/v1/developer/auth.py`

**エンドポイント:**
- `POST /api/v1/developer/auth/login`
  - リクエスト: `{ "password": "開発者パスワード" }`
  - レスポンス: `{ "token": "session_token", "expires_at": "timestamp" }`
  - 環境変数 `DEVELOPER_PASSWORD` と照合
  - セッショントークン生成（`session_tokens`テーブル活用）
  - `admin_activity_logs` に 'developer_login' 記録

**環境変数設定:**
```bash
# ./backend/.env に追加
DEVELOPER_PASSWORD=your_secure_password_here
DEVELOPER_SESSION_EXPIRE_HOURS=24
```

**認証ミドルウェア:**
**ファイル:** `./backend/app/core/developer_auth.py`
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db
from sqlalchemy.orm import Session

security = HTTPBearer()

async def require_developer_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """開発者認証チェック"""
    token = credentials.credentials
    
    # session_tokensテーブルからトークン検証
    # users.role = 'developer' チェック
    # 有効期限チェック
    
    # エラー時: HTTPException(status_code=401, detail="Invalid developer token")
    return user  # 認証成功時、ユーザー情報返却
```

#### 2.2 統計取得API

**ファイル:** `./backend/app/api/v1/developer/stats.py`

**エンドポイント:**

##### GET /api/v1/developer/stats/overview
システム全体概要
```json
{
  "total_facilities": 10,
  "active_facilities": 8,
  "total_faqs": 250,
  "errors_24h": {
    "critical": 2,
    "error": 15,
    "warning": 30
  },
  "chats_7d": 1450,
  "escalations_7d": 23
}
```

**SQLクエリ例:**
```python
# 施設数
total_facilities = db.query(Facility).count()
active_facilities = db.query(Facility).filter(Facility.is_active == True).count()

# エラー数（過去24時間）
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(hours=24)
errors_24h = db.query(
    ErrorLog.error_level, 
    func.count(ErrorLog.id)
).filter(
    ErrorLog.created_at >= yesterday
).group_by(ErrorLog.error_level).all()

# チャット数（過去7日）
week_ago = datetime.now() - timedelta(days=7)
chats_7d = db.query(Message).filter(
    Message.created_at >= week_ago,
    Message.role == 'user'  # ユーザーメッセージのみカウント
).count()
```

##### GET /api/v1/developer/stats/facilities
全施設一覧と基本統計
```json
{
  "facilities": [
    {
      "id": 1,
      "name": "施設名",
      "is_active": true,
      "faq_count": 25,
      "chats_7d": 120,
      "errors_7d": 3,
      "last_admin_login": "2024-12-27T10:30:00Z"
    }
  ]
}
```

**SQLクエリ例:**
```python
# サブクエリでFAQ数を取得
faq_count_subq = db.query(
    FAQ.facility_id,
    func.count(FAQ.id).label('faq_count')
).group_by(FAQ.facility_id).subquery()

# サブクエリでチャット数を取得（過去7日）
week_ago = datetime.now() - timedelta(days=7)
chat_count_subq = db.query(
    Conversation.facility_id,
    func.count(Message.id).label('chat_count')
).join(Message).filter(
    Message.created_at >= week_ago,
    Message.role == 'user'
).group_by(Conversation.facility_id).subquery()

# メインクエリ
facilities = db.query(
    Facility,
    faq_count_subq.c.faq_count,
    chat_count_subq.c.chat_count
).outerjoin(faq_count_subq).outerjoin(chat_count_subq).all()
```

##### GET /api/v1/developer/stats/facility/{facility_id}
特定施設の詳細統計
```json
{
  "facility": {
    "id": 1,
    "name": "施設名"
  },
  "faq_stats": {
    "total": 25,
    "by_language": {"ja": 15, "en": 10},
    "top_viewed": [
      {"faq_id": 5, "question": "質問内容", "view_count": 45}
    ]
  },
  "chat_stats": {
    "total_conversations": 150,
    "total_messages": 600,
    "avg_messages_per_conversation": 4.0,
    "by_language": {"ja": 100, "en": 50},
    "daily_trend": [
      {"date": "2024-12-21", "count": 20},
      {"date": "2024-12-22", "count": 25}
    ]
  },
  "admin_activity": {
    "last_login": "2024-12-27T10:30:00Z",
    "recent_actions": [
      {
        "action": "faq_create",
        "timestamp": "2024-12-26T14:20:00Z",
        "user": "admin@example.com"
      }
    ]
  }
}
```

**SQLクエリ例（FAQ閲覧ランキング）:**
```python
top_viewed_faqs = db.query(
    FAQ.id,
    FAQ.question,
    func.count(FAQViewLog.id).label('view_count')
).join(FAQViewLog).filter(
    FAQ.facility_id == facility_id
).group_by(FAQ.id, FAQ.question).order_by(
    desc('view_count')
).limit(10).all()
```

**SQLクエリ例（日別チャット数）:**
```python
from sqlalchemy import func, cast, Date

daily_chats = db.query(
    cast(Message.created_at, Date).label('date'),
    func.count(Message.id).label('count')
).join(Conversation).filter(
    Conversation.facility_id == facility_id,
    Message.role == 'user',
    Message.created_at >= datetime.now() - timedelta(days=30)
).group_by('date').order_by('date').all()
```

#### 2.3 エラーログAPI

**ファイル:** `./backend/app/api/v1/developer/errors.py`

##### GET /api/v1/developer/errors/list
```
クエリパラメータ:
- page: int (default: 1)
- per_page: int (default: 50, max: 100)
- level: str (optional) ['critical', 'error', 'warning']
- facility_id: int (optional)
- start_date: datetime (optional)
- end_date: datetime (optional)
```

**レスポンス:**
```json
{
  "errors": [
    {
      "id": 123,
      "level": "error",
      "code": "VALIDATION_ERROR",
      "message": "エラーメッセージ",
      "request_path": "/api/v1/chat/send",
      "facility_name": "施設名",
      "created_at": "2024-12-27T15:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 230,
    "total_pages": 5
  }
}
```

**SQLクエリ例:**
```python
query = db.query(ErrorLog).order_by(ErrorLog.created_at.desc())

if level:
    query = query.filter(ErrorLog.error_level == level)
if facility_id:
    query = query.filter(ErrorLog.facility_id == facility_id)
if start_date:
    query = query.filter(ErrorLog.created_at >= start_date)
if end_date:
    query = query.filter(ErrorLog.created_at <= end_date)

total = query.count()
errors = query.offset((page - 1) * per_page).limit(per_page).all()
```

##### GET /api/v1/developer/errors/{error_id}
```json
{
  "id": 123,
  "level": "error",
  "code": "VALIDATION_ERROR",
  "message": "詳細メッセージ",
  "stack_trace": "スタックトレース全文",
  "request_path": "/api/v1/chat/send",
  "request_method": "POST",
  "facility": {
    "id": 1,
    "name": "施設名"
  },
  "user": {
    "id": 5,
    "email": "user@example.com"
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2024-12-27T15:30:00Z"
}
```

#### 2.4 アクティビティログAPI

**ファイル:** `./backend/app/api/v1/developer/activity.py`

##### GET /api/v1/developer/activity/admins
```
クエリパラメータ:
- page, per_page
- action_type: str (optional)
- facility_id: int (optional)
- user_id: int (optional)
- start_date, end_date
```

**レスポンス:**
```json
{
  "activities": [
    {
      "id": 456,
      "user_email": "admin@example.com",
      "facility_name": "施設名",
      "action_type": "faq_update",
      "target_resource_type": "faq",
      "target_resource_id": 10,
      "description": "FAQ ID 10を更新",
      "ip_address": "192.168.1.50",
      "created_at": "2024-12-27T14:00:00Z"
    }
  ],
  "pagination": {...}
}
```

##### GET /api/v1/developer/activity/facility/{facility_id}
特定施設のアクティビティ履歴

#### 2.5 システムヘルスAPI

**ファイル:** `./backend/app/api/v1/developer/health.py`

##### GET /api/v1/developer/health/system
```json
{
  "database": {
    "status": "ok",
    "response_time_ms": 5
  },
  "redis": {
    "status": "ok",
    "response_time_ms": 2
  },
  "openai_api": {
    "status": "ok",
    "last_check": "2024-12-27T16:00:00Z"
  }
}
```

**実装例:**
```python
import time
from app.database import engine
from app.redis_client import redis_client

@router.get("/system")
async def system_health(current_user = Depends(require_developer_auth)):
    health_status = {}
    
    # データベースチェック
    try:
        start = time.time()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_time = (time.time() - start) * 1000
        health_status["database"] = {"status": "ok", "response_time_ms": round(db_time, 2)}
    except Exception as e:
        health_status["database"] = {"status": "error", "error": str(e)}
    
    # Redisチェック
    try:
        start = time.time()
        redis_client.ping()
        redis_time = (time.time() - start) * 1000
        health_status["redis"] = {"status": "ok", "response_time_ms": round(redis_time, 2)}
    except Exception as e:
        health_status["redis"] = {"status": "error", "error": str(e)}
    
    return health_status
```

#### 2.6 エラーログ自動記録機能

**ファイル:** `./backend/app/main.py` 拡張

**既存のエラーハンドラーにログ記録を追加:**
```python
from app.models.error_log import ErrorLog
from app.database import SessionLocal

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # 既存のエラーレスポンス生成処理
    error_code_map = {...}
    error_code = error_code_map.get(exc.status_code, "INTERNAL_ERROR")
    
    # データベースにエラーログ記録
    try:
        db = SessionLocal()
        error_log = ErrorLog(
            error_level="error",
            error_code=error_code,
            error_message=exc.detail,
            request_path=str(request.url.path),
            request_method=request.method,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(error_log)
        db.commit()
        db.close()
    except Exception as log_error:
        logger.error(f"Failed to log error: {log_error}")
    
    return JSONResponse(...)
```

**criticalレベルのエラーも同様に記録:**
```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # エラーログ記録（error_level='critical'）
    try:
        db = SessionLocal()
        error_log = ErrorLog(
            error_level="critical",
            error_code="INTERNAL_ERROR",
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
            request_path=str(request.url.path),
            request_method=request.method,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(error_log)
        db.commit()
        db.close()
    except Exception as log_error:
        logger.error(f"Failed to log critical error: {log_error}")
    
    return JSONResponse(...)
```

#### 2.7 SQLAlchemyモデル定義

**ファイル:** `./backend/app/models/error_log.py`
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ErrorLog(Base):
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True)
    error_level = Column(String(20), nullable=False)
    error_code = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    request_path = Column(String(500))
    request_method = Column(String(10))
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    facility = relationship("Facility")
    user = relationship("User")
```

**ファイル:** `./backend/app/models/admin_activity_log.py`
```python
class AdminActivityLog(Base):
    __tablename__ = "admin_activity_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_resource_type = Column(String(50))
    target_resource_id = Column(Integer)
    description = Column(Text)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")
    facility = relationship("Facility")
```

**ファイル:** `./backend/app/models/faq_view_log.py`
```python
class FAQViewLog(Base):
    __tablename__ = "faq_view_logs"
    
    id = Column(Integer, primary_key=True)
    faq_id = Column(Integer, ForeignKey("faqs.id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="SET NULL"))
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"))
    guest_language = Column(String(10))
    viewed_at = Column(DateTime, default=datetime.now)
    
    faq = relationship("FAQ")
    facility = relationship("Facility")
    conversation = relationship("Conversation")
    message = relationship("Message")
```

#### 2.8 APIルーター統合

**ファイル:** `./backend/app/api/v1/developer/__init__.py`
```python
from fastapi import APIRouter
from .auth import router as auth_router
from .stats import router as stats_router
from .errors import router as errors_router
from .activity import router as activity_router
from .health import router as health_router

developer_router = APIRouter(prefix="/developer", tags=["developer"])

developer_router.include_router(auth_router, prefix="/auth")
developer_router.include_router(stats_router, prefix="/stats")
developer_router.include_router(errors_router, prefix="/errors")
developer_router.include_router(activity_router, prefix="/activity")
developer_router.include_router(health_router, prefix="/health")
```

**メインルーターへの登録:**
`./backend/app/api/v1/router.py` に追加
```python
from app.api.v1.developer import developer_router

api_router.include_router(developer_router)
```

---

### ステップ3: フロントエンド実装（4-5時間）

#### 3.1 ディレクトリ構造

```
frontend/src/
├── pages/
│   └── developer/
│       ├── DeveloperLogin.tsx          # 開発者ログインページ
│       ├── DeveloperDashboard.tsx      # ダッシュボード（概要）
│       ├── FacilityList.tsx            # 施設一覧
│       ├── FacilityDetail.tsx          # 施設詳細統計
│       ├── ErrorLogs.tsx               # エラーログ閲覧
│       └── ActivityLogs.tsx            # アクティビティログ閲覧
├── api/
│   └── developer.ts                    # 開発者API呼び出し
├── components/
│   └── developer/
│       ├── StatCard.tsx                # 統計カードコンポーネント
│       ├── ErrorLogTable.tsx           # エラーログテーブル
│       ├── ActivityLogTable.tsx        # アクティビティログテーブル
│       ├── FacilityStatsChart.tsx      # チャート表示
│       └── DeveloperNav.tsx            # ナビゲーションメニュー
└── types/
    └── developer.ts                    # TypeScript型定義
```

#### 3.2 TypeScript型定義

**ファイル:** `./frontend/src/types/developer.ts`
```typescript
export interface SystemOverview {
  total_facilities: number;
  active_facilities: number;
  total_faqs: number;
  errors_24h: {
    critical: number;
    error: number;
    warning: number;
  };
  chats_7d: number;
  escalations_7d: number;
}

export interface FacilitySummary {
  id: number;
  name: string;
  is_active: boolean;
  faq_count: number;
  chats_7d: number;
  errors_7d: number;
  last_admin_login: string | null;
}

export interface ErrorLog {
  id: number;
  level: 'critical' | 'error' | 'warning';
  code: string;
  message: string;
  request_path?: string;
  facility_name?: string;
  created_at: string;
}

export interface ErrorLogDetail extends ErrorLog {
  stack_trace?: string;
  request_method?: string;
  facility?: {
    id: number;
    name: string;
  };
  user?: {
    id: number;
    email: string;
  };
  ip_address?: string;
  user_agent?: string;
}

export interface ActivityLog {
  id: number;
  user_email: string;
  facility_name: string;
  action_type: string;
  target_resource_type?: string;
  target_resource_id?: number;
  description?: string;
  ip_address?: string;
  created_at: string;
}

export interface FacilityDetail {
  facility: {
    id: number;
    name: string;
  };
  faq_stats: {
    total: number;
    by_language: Record<string, number>;
    top_viewed: Array<{
      faq_id: number;
      question: string;
      view_count: number;
    }>;
  };
  chat_stats: {
    total_conversations: number;
    total_messages: number;
    avg_messages_per_conversation: number;
    by_language: Record<string, number>;
    daily_trend: Array<{
      date: string;
      count: number;
    }>;
  };
  admin_activity: {
    last_login: string | null;
    recent_actions: Array<{
      action: string;
      timestamp: string;
      user: string;
    }>;
  };
}
```

#### 3.3 API呼び出しモジュール

**ファイル:** `./frontend/src/api/developer.ts`
```typescript
import apiClient from './client';
import type {
  SystemOverview,
  FacilitySummary,
  FacilityDetail,
  ErrorLog,
  ErrorLogDetail,
  ActivityLog
} from '@/types/developer';

const DEVELOPER_API_BASE = '/api/v1/developer';

export const developerApi = {
  // 認証
  login: async (password: string): Promise<{ token: string; expires_at: string }> => {
    const response = await apiClient.post(`${DEVELOPER_API_BASE}/auth/login`, { password });
    return response.data;
  },

  // 統計
  getOverview: async (): Promise<SystemOverview> => {
    const response = await apiClient.get(`${DEVELOPER_API_BASE}/stats/overview`);
    return response.data;
  },

  getFacilities: async (): Promise<{ facilities: FacilitySummary[] }> => {
    const response = await apiClient.get(`${DEVELOPER_API_BASE}/stats/facilities`);
    return response.data;
  },

  getFacilityDetail: async (facilityId: number): Promise<FacilityDetail> => {
    const response = await apiClient.get(`${DEVELOPER_API_BASE}/stats/facility/${facilityId}`);
    return response.data;
  },

  // エラーログ
  getErrors: async (params: {
    page?: number;
    per_page?: number;
    level?: string;
    facility_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<{ errors: ErrorLog[]; pagination: any }> => {
    const response = await apiClient.get(`${DEVELOPER_API_BASE}/errors/list`, { params });
    return response.data;
  },

  getErrorDetail: async (errorId: number): Promise<ErrorLogDetail> => {
    const response = await apiClient.get(`${DEVELOPER_API_BASE}/errors/${errorId}`);
    return response.data;
  },

  // アクティビティログ
  getActivityLogs: async (params: {
    page?: number;
    per_page?: number;
    action_type?: string;
    facility_id?: number;
    user_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<{ activities: ActivityLog[]; pagination: any }> => {
    const response = await apiClient.get(`${DEVELOPER_API_BASE}/activity/admins`, { params });
    return response.data;
  },

  // ヘルスチェック
  getSystemHealth: async () => {
    const response = await apiClient.get(`${DEVELOPER_API_BASE}/health/system`);
    return response.data;
  },
};
```

**認証トークン管理:**
`./frontend/src/api/client.ts` にインターセプター追加
```typescript
// 開発者トークンをヘッダーに追加
apiClient.interceptors.request.use((config) => {
  const devToken = localStorage.getItem('developer_token');
  if (devToken && config.url?.includes('/developer/')) {
    config.headers.Authorization = `Bearer ${devToken}`;
  }
  return config;
});
```

#### 3.4 開発者ログインページ

**ファイル:** `./frontend/src/pages/developer/DeveloperLogin.tsx`

**主要機能:**
- パスワード入力フォーム
- ログイン処理
- トークンをlocalStorageに保存
- ダッシュボードへリダイレクト

**UI要素:**
- タイトル: "開発者管理ページ"
- パスワード入力フィールド（type="password"）
- ログインボタン
- エラーメッセージ表示エリア

**実装のポイント:**
```typescript
const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault();
  try {
    const { token, expires_at } = await developerApi.login(password);
    localStorage.setItem('developer_token', token);
    localStorage.setItem('developer_token_expires', expires_at);
    navigate('/developer/dashboard');
  } catch (error) {
    setError('ログインに失敗しました。パスワードを確認してください。');
  }
};
```

#### 3.5 ダッシュボードページ

**ファイル:** `./frontend/src/pages/developer/DeveloperDashboard.tsx`

**表示内容:**

1. **システム概要カード（4枚）**
   - 総施設数 / アクティブ施設数
   - 総FAQ数
   - 過去24時間のエラー数（重大度別）
   - 過去7日間のチャット総数

2. **施設一覧テーブル（上位10件）**
   - 施設名
   - FAQ数
   - 過去7日間のチャット数
   - 最終ログイン
   - エラー数
   - 詳細リンク

3. **最近のエラーログ（最新10件）**
   - タイムスタンプ
   - エラーレベル（色分け: critical=赤, error=オレンジ, warning=黄）
   - エラーコード
   - 施設名
   - 詳細リンク

**レイアウト:**
```
+------------------+------------------+------------------+------------------+
|  総施設数        |  総FAQ数         |  エラー24h       |  チャット7d      |
|  10 / 8 active  |  250             |  2 / 15 / 30     |  1,450          |
+------------------+------------------+------------------+------------------+

+-----------------------------------------------------------------------+
|  施設一覧                                              [すべて表示 >] |
+-----------------------------------------------------------------------+
| 施設名    | FAQ数 | チャット7d | 最終ログイン        | エラー7d | 詳細 |
|-----------|-------|-----------|-------------------|---------|------|
| 施設A     | 25    | 120       | 2024-12-27 10:30  | 3       | 表示 |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
|  最近のエラー                                          [すべて表示 >] |
+-----------------------------------------------------------------------+
| 時刻              | レベル   | コード            | 施設    | 詳細 |
|-------------------|---------|-------------------|---------|------|
| 2024-12-27 15:30  | error   | VALIDATION_ERROR  | 施設A   | 表示 |
+-----------------------------------------------------------------------+
```

#### 3.6 施設一覧ページ

**ファイル:** `./frontend/src/pages/developer/FacilityList.tsx`

**機能:**
- 全施設の一覧表示（ページネーション）
- フィルタリング（アクティブ/非アクティブ）
- ソート機能（FAQ数、チャット数、エラー数）
- 検索機能（施設名）
- 詳細ページへのリンク

**テーブルカラム:**
- ID
- 施設名
- ステータス（アクティブ/非アクティブ）
- FAQ数
- 過去7日間チャット数
- 過去7日間エラー数
- 最終管理者ログイン
- アクション（詳細ボタン）

#### 3.7 施設詳細ページ

**ファイル:** `./frontend/src/pages/developer/FacilityDetail.tsx`

**表示内容:**

1. **施設情報ヘッダー**
   - 施設名
   - ステータス
   - 戻るボタン

2. **FAQタブ**
   - FAQ総数
   - 言語別内訳（円グラフ）
   - 閲覧数ランキング（Top 10）

3. **チャット統計タブ**
   - 総会話数、総メッセージ数
   - 平均メッセージ数/会話
   - 言語別内訳（棒グラフ）
   - 日別トレンドグラフ（過去30日）

4. **管理者アクティビティタブ**
   - 最終ログイン時刻
   - 最近のアクション（直近20件）
     - アクションタイプ
     - タイムスタンプ
     - 実行ユーザー
     - 対象リソース

**チャート実装:**
- ライブラリ: Recharts または Chart.js
- 日別トレンド: LineChart
- 言語別内訳: BarChart / PieChart

#### 3.8 エラーログページ

**ファイル:** `./frontend/src/pages/developer/ErrorLogs.tsx`

**機能:**
- エラーログ一覧表示（ページネーション）
- フィルタリング
  - エラーレベル（critical / error / warning）
  - 施設選択（ドロップダウン）
  - 日付範囲（カレンダー）
- ソート（時刻降順/昇順）
- エラー詳細モーダル

**テーブルカラム:**
- ID
- 時刻
- レベル（色分けバッジ）
- エラーコード
- メッセージ（省略表示）
- リクエストパス
- 施設名
- 詳細ボタン

**エラー詳細モーダル:**
- 全フィールド表示
- スタックトレース（折りたたみ可能）
- コピーボタン（デバッグ用）

#### 3.9 アクティビティログページ

**ファイル:** `./frontend/src/pages/developer/ActivityLogs.tsx`

**機能:**
- アクティビティログ一覧（ページネーション）
- フィルタリング
  - アクションタイプ（ドロップダウン）
  - 施設選択
  - ユーザー選択
  - 日付範囲
- ソート（時刻降順/昇順）

**テーブルカラム:**
- ID
- 時刻
- ユーザー（email）
- 施設名
- アクションタイプ
- 対象リソース
- 説明
- IPアドレス

#### 3.10 ナビゲーションメニュー

**ファイル:** `./frontend/src/components/developer/DeveloperNav.tsx`

**メニュー項目:**
- ダッシュボード
- 施設一覧
- エラーログ
- アクティビティログ
- システムヘルス
- ログアウト

**実装:**
- React Router Link コンポーネント
- アクティブメニューのハイライト
- ログアウト処理（localStorage クリア + ログインページへリダイレクト）

---

### ステップ4: ログ収集機能追加（2時間）

#### 4.1 FAQ閲覧ログ記録

**対象ファイル:** `./backend/app/services/chat_service.py`

**実装箇所:** FAQがチャットで返却される際

**追加コード例:**
```python
from app.models.faq_view_log import FAQViewLog

async def process_chat_message(...):
    # 既存のチャット処理
    chat_response = await self.rag_engine.process_message(...)
    
    # マッチしたFAQのログ記録
    if chat_response.matched_faq_ids:
        for faq_id in chat_response.matched_faq_ids:
            faq_view_log = FAQViewLog(
                faq_id=faq_id,
                facility_id=conversation.facility_id,
                conversation_id=conversation.id,
                message_id=ai_message.id,
                guest_language=conversation.guest_language
            )
            db.add(faq_view_log)
        db.commit()
```

#### 4.2 管理者ログインログ記録

**対象ファイル:** `./backend/app/api/v1/auth.py`

**実装箇所:** ログイン成功時

**追加コード例:**
```python
from app.models.admin_activity_log import AdminActivityLog

@router.post("/login")
async def login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    # 既存の認証処理
    user = authenticate_user(db, credentials.email, credentials.password)
    
    # アクティビティログ記録
    activity_log = AdminActivityLog(
        user_id=user.id,
        facility_id=user.facility_id,
        action_type="login",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(activity_log)
    db.commit()
    
    return {...}
```

#### 4.3 FAQ編集ログ記録

**対象ファイル:** `./backend/app/api/v1/admin/faq.py` （新規作成または既存を拡張）

**実装箇所:** FAQ作成/更新/削除API

**追加コード例:**
```python
@router.post("/")
async def create_faq(
    faq_data: FAQCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # FAQ作成処理
    new_faq = FAQ(**faq_data.dict(), created_by=current_user.id)
    db.add(new_faq)
    db.flush()  # IDを取得
    
    # アクティビティログ記録
    activity_log = AdminActivityLog(
        user_id=current_user.id,
        facility_id=current_user.facility_id,
        action_type="faq_create",
        target_resource_type="faq",
        target_resource_id=new_faq.id,
        description=f"FAQ作成: {faq_data.question[:50]}...",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(activity_log)
    db.commit()
    
    return new_faq

@router.put("/{faq_id}")
async def update_faq(...):
    # 更新処理
    # action_type="faq_update" でログ記録

@router.delete("/{faq_id}")
async def delete_faq(...):
    # 削除処理
    # action_type="faq_delete" でログ記録
```

---

### ステップ5: アクセス制限とセキュリティ（1-2時間）

#### 5.1 環境変数設定

**ファイル:** `./backend/.env`

**追加項目:**
```env
# 開発者認証
DEVELOPER_PASSWORD=Change_This_Secure_Password_2024!
DEVELOPER_SESSION_EXPIRE_HOURS=24
```

**本番環境での推奨:**
- 20文字以上のランダム文字列
- 大文字、小文字、数字、記号を含む
- 定期的にローテーション

#### 5.2 開発者アクセスログ記録

**対象ファイル:** `./backend/app/core/developer_auth.py`

**実装:**
```python
from app.models.admin_activity_log import AdminActivityLog

async def require_developer_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
    db: Session = Depends(get_db)
):
    # 既存の認証処理
    user = verify_developer_token(credentials.credentials, db)
    
    # 開発者アクセスログ記録
    activity_log = AdminActivityLog(
        user_id=user.id,
        facility_id=user.facility_id,  # 開発者の場合はNULL許可
        action_type="developer_access",
        target_resource_type="page",
        description=f"開発者ページアクセス: {request.url.path}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(activity_log)
    db.commit()
    
    return user
```

#### 5.3 セッショントークン有効期限管理

**実装:**
```python
from datetime import datetime, timedelta

def create_developer_session(user_id: int, db: Session) -> str:
    expires_hours = int(os.getenv("DEVELOPER_SESSION_EXPIRE_HOURS", "24"))
    expires_at = datetime.now() + timedelta(hours=expires_hours)
    
    token = secrets.token_urlsafe(32)
    session = SessionToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    
    return token
```

#### 5.4 フロントエンドでのトークン期限チェック

**ファイル:** `./frontend/src/utils/auth.ts`
```typescript
export const isDeveloperTokenExpired = (): boolean => {
  const expiresAt = localStorage.getItem('developer_token_expires');
  if (!expiresAt) return true;
  
  const expiryDate = new Date(expiresAt);
  return expiryDate < new Date();
};

export const logoutDeveloper = () => {
  localStorage.removeItem('developer_token');
  localStorage.removeItem('developer_token_expires');
  window.location.href = '/developer/login';
};
```

**全開発者ページでのチェック:**
```typescript
// DeveloperDashboard.tsx 等
useEffect(() => {
  if (isDeveloperTokenExpired()) {
    logoutDeveloper();
  }
}, []);
```

#### 5.5 将来の拡張ポイント（フェーズ3）

**IPアドレスホワイトリスト:**
```python
DEVELOPER_ALLOWED_IPS = os.getenv("DEVELOPER_ALLOWED_IPS", "").split(",")

async def require_developer_auth(...):
    if DEVELOPER_ALLOWED_IPS and request.client.host not in DEVELOPER_ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="IP not allowed")
```

**2要素認証（TOTP）:**
- PyOTP ライブラリ使用
- QRコード生成
- 認証コード検証

**監査ログエクスポート:**
- CSV/JSON形式でダウンロード
- 日付範囲指定
- 定期的な自動バックアップ

---

## 5. 実装スケジュール

### Day 1（3-4時間）

**午前:**
- [ ] Alembicマイグレーションファイル作成
- [ ] マイグレーション実行・動作確認
- [ ] SQLAlchemyモデル定義（error_logs, admin_activity_logs, faq_view_logs）

**午後:**
- [ ] 開発者認証API実装（login エンドポイント）
- [ ] 認証ミドルウェア実装
- [ ] 環境変数設定

### Day 2（4-5時間）

**午前:**
- [ ] 統計取得API実装（overview, facilities, facility detail）
- [ ] エラーログAPI実装（list, detail）

**午後:**
- [ ] アクティビティログAPI実装
- [ ] システムヘルスAPI実装
- [ ] APIルーター統合

### Day 3（3-4時間）

**午前:**
- [ ] TypeScript型定義作成
- [ ] API呼び出しモジュール実装
- [ ] 開発者ログインページ実装

**午後:**
- [ ] ダッシュボードページ実装
- [ ] 施設一覧ページ実装

### Day 4（2-3時間）

**午前:**
- [ ] 施設詳細ページ実装
- [ ] エラーログページ実装

**午後:**
- [ ] アクティビティログページ実装
- [ ] ナビゲーションメニュー実装

### Day 5（1-2時間）

**午前:**
- [ ] FAQ閲覧ログ記録機能追加
- [ ] 管理者アクティビティログ記録機能追加

**午後:**
- [ ] 開発者アクセスログ記録
- [ ] セキュリティ設定確認

### Day 6（1-2時間）

**統合テスト:**
- [ ] 開発者ログイン → ダッシュボード表示
- [ ] 施設詳細統計表示
- [ ] エラーログ一覧・フィルタリング
- [ ] アクティビティログ一覧・フィルタリング
- [ ] FAQ閲覧ログが正しく記録されるか
- [ ] 管理者アクションログが正しく記録されるか

**デバッグ・調整:**
- [ ] エラーハンドリング確認
- [ ] レスポンシブデザイン調整
- [ ] パフォーマンス確認

---

## 6. テスト計画

### 6.1 ユニットテスト

**バックエンド:**
- `test_developer_auth.py`: 開発者認証のテスト
- `test_developer_stats.py`: 統計取得APIのテスト
- `test_error_logging.py`: エラーログ記録のテスト
- `test_activity_logging.py`: アクティビティログ記録のテスト

**テストケース例:**
```python
# test_developer_auth.py
async def test_developer_login_success(client, db_session):
    response = await client.post(
        "/api/v1/developer/auth/login",
        json={"password": "correct_password"}
    )
    assert response.status_code == 200
    assert "token" in response.json()

async def test_developer_login_failure(client, db_session):
    response = await client.post(
        "/api/v1/developer/auth/login",
        json={"password": "wrong_password"}
    )
    assert response.status_code == 401
```

### 6.2 統合テスト

**テストシナリオ:**
1. 開発者ログイン → トークン取得
2. トークンを使ってダッシュボードデータ取得
3. 施設詳細データ取得
4. エラーログ取得（フィルタリング）
5. アクティビティログ取得（ページネーション）

### 6.3 手動テスト

**チェックリスト:**
- [ ] 開発者ログインページが表示される
- [ ] 正しいパスワードでログインできる
- [ ] 誤ったパスワードでログインできない
- [ ] ダッシュボードに統計が表示される
- [ ] 施設一覧が表示される
- [ ] 施設詳細ページでチャートが表示される
- [ ] エラーログ一覧が表示される
- [ ] エラーログをフィルタリングできる
- [ ] エラー詳細モーダルが開く
- [ ] アクティビティログ一覧が表示される
- [ ] アクティビティログをフィルタリングできる
- [ ] ログアウトできる
- [ ] トークン期限切れで自動ログアウトされる

---

## 7. データベースバックアップ

**実装前バックアップ:**
```bash
cd backend
python backup_staging_database.py
# または
./backup_staging_database.sh
```

**バックアップファイル:**
`./database_backups/database_backup_developer_page_before_YYYYMMDD_HHMMSS.sql`

---

## 8. リスク管理

### 8.1 想定されるリスク

**技術的リスク:**
1. **マイグレーション失敗**
   - 影響: データベース破損
   - 対策: 実装前バックアップ、ロールバック手順確認
   - 対応: `alembic downgrade -1` でロールバック

2. **大量ログによるストレージ圧迫**
   - 影響: データベース容量不足
   - 対策: ログ保持期間設定（90日）、定期的なアーカイブ
   - 対応: クリーンアップスクリプト作成（フェーズ3）

3. **統計クエリのパフォーマンス低下**
   - 影響: ダッシュボード表示遅延
   - 対策: 適切なインデックス設定、キャッシング導入
   - 対応: Redis キャッシュで統計データを5分間キャッシュ

4. **認証トークン漏洩**
   - 影響: 不正アクセス
   - 対策: HTTPS必須、短い有効期限（24時間）
   - 対応: 即座にパスワード変更、セッション無効化

**スケジュールリスク:**
1. **予期しないバグ発生**
   - 影響: 実装遅延
   - 対策: 各ステップでの動作確認、段階的実装
   - バッファ: 合計2時間の余裕あり（10-14時間）

### 8.2 ロールバック手順

**マイグレーション失敗時:**
```bash
# データベースロールバック
alembic downgrade -1

# バックアップから復元
psql -U yadopera_user -d yadopera_db < ./database_backups/database_backup_developer_page_before_YYYYMMDD_HHMMSS.sql
```

**APIデプロイ失敗時:**
```bash
# Gitで前のコミットに戻す
git revert HEAD
git push origin main
```

---

## 9. セキュリティ考慮事項

### 9.1 認証セキュリティ

**パスワード管理:**
- 環境変数に保存（コードにハードコードしない）
- `.env` ファイルは `.gitignore` に含める
- 本番環境では環境変数管理サービス使用（Railway/Render）

**セッション管理:**
- トークンは暗号学的に安全な乱数生成（`secrets.token_urlsafe`）
- 有効期限: 24時間（環境変数で調整可能）
- ログアウト時にトークン無効化

### 9.2 データアクセス制御

**開発者のみアクセス可能:**
- `/api/v1/developer/*` エンドポイントは `require_developer_auth` で保護
- フロントエンドルートも保護（トークンなしでアクセス不可）

**監査ログ:**
- すべての開発者アクセスを記録
- IP アドレス、User-Agent 保存
- 定期的にログレビュー

### 9.3 データ保護

**個人情報:**
- エラーログに個人情報を含めない
- スタックトレースから機密情報を除外
- 宿泊客のメッセージ内容は直接表示しない（統計のみ）

**データ保持:**
- エラーログ: 90日後自動削除（フェーズ3で実装）
- アクティビティログ: 1年後アーカイブ
- FAQ閲覧ログ: 無期限保持（統計用）

### 9.4 HTTPS強制

**本番環境:**
- すべての開発者ページアクセスは HTTPS 必須
- HTTP → HTTPS リダイレクト
- HSTS ヘッダー設定

---

## 10. モニタリングとメンテナンス

### 10.1 ログローテーション

**データベーステーブルサイズ監視:**
```sql
-- テーブルサイズ確認クエリ
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**古いログの削除（フェーズ3で実装）:**
```python
# 90日以上前のエラーログを削除
from datetime import datetime, timedelta

def cleanup_old_logs(db: Session):
    cutoff_date = datetime.now() - timedelta(days=90)
    
    deleted_errors = db.query(ErrorLog).filter(
        ErrorLog.created_at < cutoff_date
    ).delete()
    
    deleted_activities = db.query(AdminActivityLog).filter(
        AdminActivityLog.created_at < cutoff_date,
        AdminActivityLog.action_type != 'developer_access'  # 開発者アクセスログは保持
    ).delete()
    
    db.commit()
    return deleted_errors, deleted_activities
```

### 10.2 パフォーマンス監視

**統計クエリ実行時間:**
```python
import time

@router.get("/stats/overview")
async def get_overview(current_user = Depends(require_developer_auth)):
    start_time = time.time()
    
    # 統計取得処理
    overview = calculate_overview_stats(db)
    
    execution_time = (time.time() - start_time) * 1000
    logger.info(f"Overview stats calculated in {execution_time:.2f}ms")
    
    return overview
```

**スロークエリ検出:**
- 500ms 以上かかるクエリをログ出力
- 定期的にインデックスの見直し

### 10.3 定期メンテナンスタスク

**週次:**
- [ ] エラーログ件数確認
- [ ] critical エラーのレビュー
- [ ] データベースサイズ確認

**月次:**
- [ ] アクティビティログの異常パターン検出
- [ ] 統計データの整合性確認
- [ ] パフォーマンスメトリクス確認

**四半期:**
- [ ] 開発者パスワードローテーション
- [ ] セキュリティ監査
- [ ] 古いログのアーカイブ

---

## 11. ドキュメント

### 11.1 開発者向けドキュメント

**README 追加セクション:**
```markdown
## 開発者管理ページ

### アクセス方法
1. `/developer/login` にアクセス
2. 開発者パスワードを入力（環境変数 `DEVELOPER_PASSWORD`）
3. ダッシュボードにリダイレクト

### 機能
- システム全体の統計表示
- 施設ごとの利用状況分析
- エラーログ閲覧
- 管理者アクティビティ監視

### 環境変数
- `DEVELOPER_PASSWORD`: 開発者ログインパスワード（必須）
- `DEVELOPER_SESSION_EXPIRE_HOURS`: セッション有効期限（デフォルト: 24）

### API エンドポイント
- `POST /api/v1/developer/auth/login`: ログイン
- `GET /api/v1/developer/stats/overview`: システム概要
- `GET /api/v1/developer/stats/facilities`: 施設一覧
- `GET /api/v1/developer/errors/list`: エラーログ一覧
- `GET /api/v1/developer/activity/admins`: アクティビティログ
```

### 11.2 運用マニュアル

**ファイル:** `docs/developer_page_manual.md`

**内容:**
- ログインからダッシュボード閲覧までの手順
- 各機能の使い方（スクリーンショット付き）
- よくあるトラブルシューティング
- エラーログの読み方
- アクティビティログの解釈方法

### 11.3 API仕様書

**ファイル:** `docs/developer_api_spec.md`

**内容:**
- 各エンドポイントの詳細仕様
- リクエスト/レスポンス例
- エラーコード一覧
- 認証方法
- レート制限（将来実装時）

---

## 12. 成果物チェックリスト

### 12.1 バックエンド

**データベース:**
- [ ] `error_logs` テーブル作成
- [ ] `admin_activity_logs` テーブル作成
- [ ] `faq_view_logs` テーブル作成
- [ ] 各テーブルのインデックス作成
- [ ] Alembic マイグレーションファイル作成

**API:**
- [ ] 開発者認証 API（login）
- [ ] 統計取得 API（overview, facilities, facility detail）
- [ ] エラーログ API（list, detail）
- [ ] アクティビティログ API（admins, facility）
- [ ] システムヘルス API
- [ ] 認証ミドルウェア実装
- [ ] API ルーター統合

**ログ記録:**
- [ ] エラーハンドラーへのログ記録追加
- [ ] FAQ 閲覧ログ記録機能
- [ ] 管理者ログインログ記録
- [ ] FAQ 編集ログ記録（作成/更新/削除）
- [ ] 開発者アクセスログ記録

**モデル:**
- [ ] ErrorLog モデル定義
- [ ] AdminActivityLog モデル定義
- [ ] FAQViewLog モデル定義

### 12.2 フロントエンド

**ページ:**
- [ ] 開発者ログインページ
- [ ] ダッシュボードページ
- [ ] 施設一覧ページ
- [ ] 施設詳細ページ
- [ ] エラーログページ
- [ ] アクティビティログページ

**コンポーネント:**
- [ ] StatCard（統計カード）
- [ ] ErrorLogTable（エラーログテーブル）
- [ ] ActivityLogTable（アクティビティログテーブル）
- [ ] FacilityStatsChart（統計チャート）
- [ ] DeveloperNav（ナビゲーションメニュー）

**API:**
- [ ] TypeScript 型定義
- [ ] API 呼び出しモジュール
- [ ] 認証トークン管理
- [ ] トークン期限チェック

**ルーティング:**
- [ ] `/developer/login` ルート
- [ ] `/developer/dashboard` ルート
- [ ] `/developer/facilities` ルート
- [ ] `/developer/facility/:id` ルート
- [ ] `/developer/errors` ルート
- [ ] `/developer/activity` ルート
- [ ] 認証保護ルート実装

### 12.3 設定・ドキュメント

**環境設定:**
- [ ] `DEVELOPER_PASSWORD` 環境変数設定
- [ ] `DEVELOPER_SESSION_EXPIRE_HOURS` 環境変数設定
- [ ] `.env.example` 更新

**ドキュメント:**
- [ ] README に開発者ページセクション追加
- [ ] 運用マニュアル作成
- [ ] API 仕様書作成
- [ ] セキュリティガイドライン作成

### 12.4 テスト

**バックエンドテスト:**
- [ ] 開発者認証テスト
- [ ] 統計取得 API テスト
- [ ] エラーログ API テスト
- [ ] アクティビティログ API テスト
- [ ] ログ記録機能テスト

**フロントエンドテスト:**
- [ ] ログイン機能テスト
- [ ] ダッシュボード表示テスト
- [ ] ページ遷移テスト
- [ ] フィルタリング機能テスト

**統合テスト:**
- [ ] エンドツーエンドテストシナリオ実行
- [ ] 手動テストチェックリスト完了

---

## 13. 実装後の確認事項

### 13.1 動作確認

**開発者認証:**
- [ ] 正しいパスワードでログインできる
- [ ] 誤ったパスワードで拒否される
- [ ] セッショントークンが発行される
- [ ] トークンで保護されたエンドポイントにアクセスできる

**ダッシュボード:**
- [ ] システム概要統計が表示される
- [ ] 施設一覧が表示される
- [ ] 最近のエラーが表示される
- [ ] 数値が正確（手動計算と照合）

**施設詳細:**
- [ ] FAQ 統計が表示される
- [ ] チャート（日別トレンド）が描画される
- [ ] 言語別内訳が正しい
- [ ] 管理者アクティビティが表示される

**エラーログ:**
- [ ] エラーログ一覧が表示される
- [ ] フィルタリングが動作する
- [ ] ページネーションが動作する
- [ ] エラー詳細モーダルが開く
- [ ] スタックトレースが表示される

**アクティビティログ:**
- [ ] アクティビティログ一覧が表示される
- [ ] フィルタリングが動作する
- [ ] ページネーションが動作する

**ログ記録:**
- [ ] エラー発生時に error_logs テーブルに記録される
- [ ] FAQ 表示時に faq_view_logs に記録される
- [ ] 管理者ログイン時に admin_activity_logs に記録される
- [ ] FAQ 編集時に admin_activity_logs に記録される
- [ ] 開発者アクセス時に admin_activity_logs に記録される

### 13.2 パフォーマンス確認

**レスポンス時間:**
- [ ] ダッシュボード表示: 2秒以内
- [ ] 施設詳細表示: 3秒以内
- [ ] エラーログ一覧: 1秒以内
- [ ] アクティビティログ一覧: 1秒以内

**データベースクエリ:**
- [ ] N+1 問題がない
- [ ] インデックスが有効に使われている
- [ ] スロークエリがない（>500ms）

### 13.3 セキュリティ確認

**認証:**
- [ ] トークンなしで保護エンドポイントにアクセスできない
- [ ] 期限切れトークンが拒否される
- [ ] ログアウト後にアクセスできない

**データ保護:**
- [ ] エラーログに個人情報が含まれていない
- [ ] スタックトレースから機密情報が除外されている
- [ ] 開発者パスワードがコードに含まれていない

**監査:**
- [ ] すべての開発者アクセスがログ記録される
- [ ] IP アドレスが記録される
- [ ] User-Agent が記録される

---

## 14. デプロイ手順

### 14.1 本番環境デプロイ前

**チェックリスト:**
- [ ] すべての自動テストがパス
- [ ] 手動テストチェックリストが完了
- [ ] データベースバックアップ取得
- [ ] デプロイ計画書レビュー
- [ ] ロールバック手順確認

### 14.2 デプロイ手順

**ステップ1: データベースマイグレーション**
```bash
# 本番環境にSSH接続
ssh production-server

# バックアップ取得
cd /path/to/yadopera
python backend/backup_staging_database.py

# マイグレーション実行
cd backend
alembic upgrade head

# マイグレーション確認
alembic current
```

**ステップ2: 環境変数設定**
```bash
# Railway/Render の環境変数設定画面で追加
DEVELOPER_PASSWORD=<strong_random_password>
DEVELOPER_SESSION_EXPIRE_HOURS=24
```

**ステップ3: バックエンドデプロイ**
```bash
# Git push（Railway/Renderは自動デプロイ）
git add .
git commit -m "feat: 開発者管理ページ実装"
git push origin main
```

**ステップ4: デプロイ確認**
- [ ] ヘルスチェックエンドポイント確認（`/health`）
- [ ] ログでエラーがないか確認
- [ ] 開発者ログインページにアクセス
- [ ] ログインしてダッシュボード表示確認

**ステップ5: フロントエンドデプロイ**
```bash
# フロントエンドビルド・デプロイ
cd frontend
npm run build
# Netlify/Vercelへデプロイ
```

### 14.3 デプロイ後確認

**即時確認（5分以内）:**
- [ ] 開発者ログインが動作する
- [ ] ダッシュボードが表示される
- [ ] エラーログが正しく記録される

**24時間以内確認:**
- [ ] システムエラーが発生していない
- [ ] パフォーマンス劣化がない
- [ ] ログが正しく蓄積されている

---

## 15. トラブルシューティング

### 15.1 よくある問題

**問題: マイグレーション失敗**
```
症状: alembic upgrade head でエラー
原因: テーブル定義の競合、既存データとの不整合
対処:
1. エラーメッセージ確認
2. バックアップからロールバック
3. マイグレーションファイル修正
4. 再実行
```

**問題: 開発者ログインできない**
```
症状: 正しいパスワードでも 401 エラー
原因: 環境変数が設定されていない、パスワード不一致
対処:
1. 環境変数 DEVELOPER_PASSWORD 確認
2. バックエンドログ確認
3. パスワードの特殊文字エスケープ確認
```

**問題: ダッシュボードが表示されない**
```
症状: 空のページまたはエラー
原因: API エラー、認証トークン問題
対処:
1. ブラウザコンソールのエラー確認
2. ネットワークタブで API レスポンス確認
3. localStorage のトークン確認
4. バックエンドログ確認
```

**問題: 統計データが不正確**
```
症状: 数値が明らかにおかしい
原因: SQL クエリのバグ、データの不整合
対処:
1. データベースで直接クエリ実行
2. 手動計算と照合
3. SQL クエリのロジック確認
4. テストデータで検証
```

**問題: パフォーマンスが遅い**
```
症状: ダッシュボード表示に 10秒以上かかる
原因: インデックス不足、N+1 問題、大量データ
対処:
1. スロークエリログ確認
2. EXPLAIN ANALYZE でクエリ分析
3. インデックス追加
4. キャッシング導入検討
```

### 15.2 緊急時対応

**重大エラー発生時:**
1. 即座にロールバック実行
2. エラーログ収集
3. バックアップから復元
4. ユーザーへの影響確認
5. 原因調査・修正
6. 再デプロイ

**データ整合性問題:**
1. 該当テーブルのバックアップ取得
2. データ修正スクリプト作成
3. テスト環境で検証
4. 本番環境で実行
5. 整合性確認

---

## 16. 将来の拡張（フェーズ3以降）

### 16.1 機能拡張

**高度な統計:**
- 宿泊客の問い合わせ傾向分析（E機能）
- FAQ 推奨機能（AI による自動提案）
- チャットボット改善提案（よくある失敗パターン分析）

**パフォーマンスメトリクス:**
- ページ読み込み時間計測（C機能）
- API 応答時間分布
- リソース使用率モニタリング

**システム稼働状況:**
- アップタイムモニタリング（F機能）
- アラート設定（critical エラー発生時にメール通知）
- 自動復旧機能

### 16.2 セキュリティ強化

**IP アドレス制限:**
- ホワイトリスト設定
- 地理的制限（国単位）

**2要素認証:**
- TOTP（Time-based One-Time Password）
- SMS 認証
- バックアップコード

**監査ログ強化:**
- 改ざん検知
- 暗号化保存
- 定期的な外部バックアップ

### 16.3 自動化

**定期タスク:**
- 古いログ自動削除（90日以上）
- レポート自動生成（週次/月次）
- 異常検知アラート

**CI/CD パイプライン:**
- 自動テスト実行
- 自動デプロイ
- カナリアデプロイ

---

## 17. 成功基準

### 17.1 機能要件

- [ ] 開発者が認証してログインできる
- [ ] システム全体の統計が表示される
- [ ] 施設ごとの詳細統計が表示される
- [ ] エラーログが閲覧・検索できる
- [ ] 管理者アクティビティが記録・閲覧できる
- [ ] FAQ 閲覧数が記録される
- [ ] すべてのエラーが自動記録される

### 17.2 非機能要件

**パフォーマンス:**
- [ ] ダッシュボード表示: 2秒以内
- [ ] 施設詳細表示: 3秒以内
- [ ] エラーログ一覧: 1秒以内

**可用性:**
- [ ] エラーログ記録が失敗してもメインシステムに影響なし
- [ ] 開発者ページがダウンしても宿泊客向けシステムは稼働

**セキュリティ:**
- [ ] 認証なしでアクセス不可
- [ ] すべてのアクセスがログ記録される
- [ ] 個人情報が保護されている

**保守性:**
- [ ] コードが適切にコメントされている
- [ ] ドキュメントが整備されている
- [ ] テストが書かれている

### 17.3 運用要件

- [ ] 実装後 1週間、critical エラーが発生しない
- [ ] 月次メンテナンス手順が確立されている
- [ ] トラブルシューティングガイドが利用可能
- [ ] ロールバック手順が文書化されている

---

## 18. まとめ

### 18.1 実装内容サマリー

**新規データベーステーブル: 3**
- error_logs
- admin_activity_logs
- faq_view_logs

**新規 API エンドポイント: 9**
- 開発者認証 API (1)
- 統計取得 API (3)
- エラーログ API (2)
- アクティビティログ API (2)
- システムヘルス API (1)

**新規フロントエンドページ: 6**
- 開発者ログイン
- ダッシュボード
- 施設一覧
- 施設詳細
- エラーログ
- アクティビティログ

**新規コンポーネント: 5**
- StatCard
- ErrorLogTable
- ActivityLogTable
- FacilityStatsChart
- DeveloperNav

### 18.2 所要時間見積もり

**合計: 10-14時間**
- ステップ1: データベース拡張 (2-3h)
- ステップ2: バックエンド API (4-5h)
- ステップ3: フロントエンド (4-5h)
- ステップ4: ログ収集機能 (2h)
- ステップ5: セキュリティ (1-2h)

### 18.3 次のステップ

**実装開始前:**
1. この計画書のレビュー
2. 不明点の確認
3. データベースバックアップ取得
4. 開発ブランチ作成

**実装中:**
1. 各ステップの完了確認
2. こまめなコミット
3. テストの実行
4. ドキュメント更新

**実装完了後:**
1. 統合テスト実行
2. デプロイ準備
3. 本番環境デプロイ
4. 動作確認
5. フェーズ2 他項目へ移行

---

## 付録A: 参照ファイル一覧

### 既存ファイル（確認済み）

**データベース:**
- `./database_backups/database_backup_faq_refactor_before_20251223_092717.sql`

**バックエンド:**
- `./backend/app/main.py`
- `./backend/app/database.py`
- `./backend/app/api/v1/auth.py`
- `./backend/app/api/v1/admin/escalations.py`
- `./backend/app/api/v1/admin/feedback.py`
- `./backend/app/api/v1/admin/overnight_queue.py`
- `./backend/app/services/chat_service.py`

**フロントエンド:**
- `./frontend/src/api/auth.ts`
- `./frontend/src/types/dashboard.ts`

### 新規ファイル（作成予定）

**バックエンド:**
- `./backend/alembic/versions/20241228_add_developer_management_tables.py`
- `./backend/app/models/error_log.py`
- `./backend/app/models/admin_activity_log.py`
- `./backend/app/models/faq_view_log.py`
- `./backend/app/core/developer_auth.py`
- `./backend/app/api/v1/developer/__init__.py`
- `./backend/app/api/v1/developer/auth.py`
- `./backend/app/api/v1/developer/stats.py`
- `./backend/app/api/v1/developer/errors.py`
- `./backend/app/api/v1/developer/activity.py`
- `./backend/app/api/v1/developer/health.py`

**フロントエンド:**
- `./frontend/src/types/developer.ts`
- `./frontend/src/api/developer.ts`
- `./frontend/src/pages/developer/DeveloperLogin.tsx`
- `./frontend/src/pages/developer/DeveloperDashboard.tsx`
- `./frontend/src/pages/developer/FacilityList.tsx`
- `./frontend/src/pages/developer/FacilityDetail.tsx`
- `./frontend/src/pages/developer/ErrorLogs.tsx`
- `./frontend/src/pages/developer/ActivityLogs.tsx`
- `./frontend/src/components/developer/StatCard.tsx`
- `./frontend/src/components/developer/ErrorLogTable.tsx`
- `./frontend/src/components/developer/ActivityLogTable.tsx`
- `./frontend/src/components/developer/FacilityStatsChart.tsx`
- `./frontend/src/components/developer/DeveloperNav.tsx`
- `./frontend/src/utils/auth.ts`

**ドキュメント:**
- `docs/developer_page_manual.md`
- `docs/developer_api_spec.md`
- `docs/developer_security_guide.md`

---

## 付録B: SQL クエリ例

### 施設ごとのチャット統計
```sql
SELECT 
    f.id AS facility_id,
    f.name AS facility_name,
    COUNT(DISTINCT c.id) AS total_conversations,
    COUNT(m.id) AS total_messages,
    ROUND(AVG(c.total_messages), 2) AS avg_messages_per_conversation
FROM facilities f
LEFT JOIN conversations c ON f.id = c.facility_id
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE m.created_at >= NOW() - INTERVAL '7 days'
  AND m.role = 'user'
GROUP BY f.id, f.name
ORDER BY total_conversations DESC;
```

### FAQ閲覧ランキング
```sql
SELECT 
    faq.id,
    faq.question,
    COUNT(fvl.id) AS view_count
FROM faqs faq
LEFT JOIN faq_view_logs fvl ON faq.id = fvl.faq_id
WHERE faq.facility_id = :facility_id
  AND fvl.viewed_at >= NOW() - INTERVAL '30 days'
GROUP BY faq.id, faq.question
ORDER BY view_count DESC
LIMIT 10;
```

### 日別チャット数推移
```sql
SELECT 
    DATE(m.created_at) AS date,
    COUNT(DISTINCT c.id) AS conversation_count,
    COUNT(m.id) AS message_count
FROM conversations c
JOIN messages m ON c.id = m.conversation_id
WHERE c.facility_id = :facility_id
  AND m.created_at >= NOW() - INTERVAL '30 days'
  AND m.role = 'user'
GROUP BY DATE(m.created_at)
ORDER BY date;
```

### エラー発生件数（重大度別、過去24時間）
```sql
SELECT 
    error_level,
    COUNT(*) AS count
FROM error_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY error_level
ORDER BY 
    CASE error_level
        WHEN 'critical' THEN 1
        WHEN 'error' THEN 2
        WHEN 'warning' THEN 3
    END;
```

### 管理者アクティビティサマリー（施設別）
```sql
SELECT 
    f.id AS facility_id,
    f.name AS facility_name,
    u.email AS admin_email,
    MAX(aal.created_at) AS last_activity,
    COUNT(CASE WHEN aal.action_type = 'login' THEN 1 END) AS login_count,
    COUNT(CASE WHEN aal.action_type LIKE 'faq_%' THEN 1 END) AS faq_actions
FROM facilities f
JOIN users u ON f.id = u.facility_id
LEFT JOIN admin_activity_logs aal ON u.id = aal.user_id
WHERE aal.created_at >= NOW() - INTERVAL '7 days'
GROUP BY f.id, f.name, u.email
ORDER BY last_activity DESC;
```

---

## 付録C: 環境変数テンプレート

### .env.example（バックエンド）
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/yadopera_db

# OpenAI
OPENAI_API_KEY=sk-...

# Redis
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# 開発者管理ページ（追加）
DEVELOPER_PASSWORD=Change_This_Secure_Password_2024!
DEVELOPER_SESSION_EXPIRE_HOURS=24

# Optional: IP制限（フェーズ3）
# DEVELOPER_ALLOWED_IPS=192.168.1.100,10.0.0.50
```

### .env.local.example（フロントエンド）
```bash
VITE_API_BASE_URL=http://localhost:8000
# または本番環境
# VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## 付録D: Git コミットメッセージ例

### フィーチャーブランチ作成
```bash
git checkout -b feature/developer-management-page
```

### コミット例
```bash
# ステップ1: データベース
git add backend/alembic/versions/20241228_add_developer_management_tables.py
git add backend/app/models/error_log.py backend/app/models/admin_activity_log.py backend/app/models/faq_view_log.py
git commit -m "feat(db): 開発者管理ページ用テーブル追加

- error_logs テーブル作成
- admin_activity_logs テーブル作成
- faq_view_logs テーブル作成
- 各テーブルのインデックス設定"

# ステップ2: バックエンドAPI
git add backend/app/api/v1/developer/
git add backend/app/core/developer_auth.py
git commit -m "feat(api): 開発者管理API実装

- 開発者認証API追加
- 統計取得API追加（overview, facilities, facility detail）
- エラーログAPI追加
- アクティビティログAPI追加
- システムヘルスAPI追加"

# ステップ3: エラーログ記録
git add backend/app/main.py
git commit -m "feat(logging): エラー自動記録機能追加

- HTTPExceptionハンドラーにログ記録追加
- 一般例外ハンドラーにログ記録追加
- スタックトレース保存機能"

# ステップ4: アクティビティログ記録
git add backend/app/services/chat_service.py
git add backend/app/api/v1/auth.py
git add backend/app/api/v1/admin/faq.py
git commit -m "feat(logging): アクティビティログ記録機能追加

- FAQ閲覧ログ記録
- 管理者ログインログ記録
- FAQ編集ログ記録（作成/更新/削除）"

# ステップ5: フロントエンド
git add frontend/src/pages/developer/
git add frontend/src/components/developer/
git add frontend/src/api/developer.ts
git add frontend/src/types/developer.ts
git commit -m "feat(ui): 開発者管理ページUI実装

- ログインページ実装
- ダッシュボードページ実装
- 施設一覧・詳細ページ実装
- エラーログページ実装
- アクティビティログページ実装"

# ステップ6: ドキュメント
git add README.md docs/
git commit -m "docs: 開発者管理ページドキュメント追加

- README更新
- 運用マニュアル作成
- API仕様書作成"
```

### マージ
```bash
git checkout main
git merge feature/developer-management-page
git push origin main
```

---

## 付録E: テストデータ生成スクリプト

### エラーログのテストデータ
```python
# backend/create_test_error_logs.py
from app.database import SessionLocal
from app.models.error_log import ErrorLog
from datetime import datetime, timedelta
import random

db = SessionLocal()

error_levels = ['critical', 'error', 'warning']
error_codes = ['VALIDATION_ERROR', 'UNAUTHORIZED', 'NOT_FOUND', 'INTERNAL_ERROR']
request_paths = ['/api/v1/chat/send', '/api/v1/faq/list', '/api/v1/auth/login']

# 過去7日間のエラーログを生成
for i in range(100):
    created_at = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
    
    error_log = ErrorLog(
        error_level=random.choice(error_levels),
        error_code=random.choice(error_codes),
        error_message=f"Test error message {i}",
        request_path=random.choice(request_paths),
        request_method='POST',
        facility_id=random.randint(1, 5) if random.random() > 0.3 else None,
        created_at=created_at
    )
    db.add(error_log)

db.commit()
print("✅ 100件のエラーログテストデータを作成しました")
```

### FAQ閲覧ログのテストデータ
```python
# backend/create_test_faq_view_logs.py
from app.database import SessionLocal
from app.models.faq_view_log import FAQViewLog
from datetime import datetime, timedelta
import random

db = SessionLocal()

# 既存のFAQ IDとfacility IDを取得
faqs = db.execute("SELECT id, facility_id FROM faqs LIMIT 20").fetchall()

# 過去30日間の閲覧ログを生成
for i in range(500):
    faq = random.choice(faqs)
    viewed_at = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    
    view_log = FAQViewLog(
        faq_id=faq[0],
        facility_id=faq[1],
        guest_language=random.choice(['ja', 'en', 'zh', 'ko']),
        viewed_at=viewed_at
    )
    db.add(view_log)

db.commit()
print("✅ 500件のFAQ閲覧ログテストデータを作成しました")
```

### 管理者アクティビティログのテストデータ
```python
# backend/create_test_activity_logs.py
from app.database import SessionLocal
from app.models.admin_activity_log import AdminActivityLog
from datetime import datetime, timedelta
import random

db = SessionLocal()

# 既存のuser IDとfacility IDを取得
users = db.execute("SELECT id, facility_id FROM users LIMIT 10").fetchall()

action_types = ['login', 'logout', 'faq_create', 'faq_update', 'faq_delete']

# 過去14日間のアクティビティログを生成
for i in range(200):
    user = random.choice(users)
    created_at = datetime.now() - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
    
    activity_log = AdminActivityLog(
        user_id=user[0],
        facility_id=user[1],
        action_type=random.choice(action_types),
        target_resource_type='faq' if 'faq' in action_types[i % len(action_types)] else None,
        target_resource_id=random.randint(1, 100) if random.random() > 0.5 else None,
        description=f"Test activity {i}",
        created_at=created_at
    )
    db.add(activity_log)

db.commit()
print("✅ 200件のアクティビティログテストデータを作成しました")
```

---

## 付録F: パフォーマンス最適化Tips

### 1. データベースクエリ最適化

**問題: 施設一覧取得が遅い**
```python
# ❌ 悪い例（N+1問題）
facilities = db.query(Facility).all()
for facility in facilities:
    facility.faq_count = db.query(FAQ).filter(FAQ.facility_id == facility.id).count()
    facility.chat_count = db.query(Message).join(Conversation).filter(
        Conversation.facility_id == facility.id
    ).count()
```

**解決策: JOINとサブクエリ**
```python
# ✅ 良い例
from sqlalchemy import func

faq_count_sq = db.query(
    FAQ.facility_id,
    func.count(FAQ.id).label('faq_count')
).group_by(FAQ.facility_id).subquery()

chat_count_sq = db.query(
    Conversation.facility_id,
    func.count(Message.id).label('chat_count')
).join(Message).group_by(Conversation.facility_id).subquery()

facilities = db.query(
    Facility,
    func.coalesce(faq_count_sq.c.faq_count, 0).label('faq_count'),
    func.coalesce(chat_count_sq.c.chat_count, 0).label('chat_count')
).outerjoin(faq_count_sq, Facility.id == faq_count_sq.c.facility_id
).outerjoin(chat_count_sq, Facility.id == chat_count_sq.c.facility_id
).all()
```

### 2. キャッシング戦略

**Redis キャッシュ実装例**
```python
import json
from app.redis_client import redis_client
from datetime import timedelta

async def get_overview_stats_cached(db: Session):
    cache_key = "developer:stats:overview"
    
    # キャッシュチェック
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # キャッシュなし→計算
    stats = calculate_overview_stats(db)
    
    # 5分間キャッシュ
    redis_client.setex(
        cache_key,
        timedelta(minutes=5),
        json.dumps(stats)
    )
    
    return stats
```

### 3. ページネーション最適化

**カーソルベースページネーション**
```python
# オフセットベース（大きなオフセットで遅い）
# SELECT * FROM error_logs ORDER BY created_at DESC LIMIT 50 OFFSET 10000;

# カーソルベース（高速）
# SELECT * FROM error_logs WHERE created_at < :last_seen_timestamp ORDER BY created_at DESC LIMIT 50;

@router.get("/errors/list")
async def get_errors(
    cursor: datetime = None,
    per_page: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(ErrorLog).order_by(ErrorLog.created_at.desc())
    
    if cursor:
        query = query.filter(ErrorLog.created_at < cursor)
    
    errors = query.limit(per_page).all()
    
    next_cursor = errors[-1].created_at if errors else None
    
    return {
        "errors": errors,
        "next_cursor": next_cursor
    }
```

---

## 付録G: セキュリティチェックリスト

### デプロイ前チェック

- [ ] **パスワード管理**
  - [ ] DEVELOPER_PASSWORD が環境変数に設定されている
  - [ ] パスワードが20文字以上
  - [ ] パスワードがコードにハードコードされていない
  - [ ] .env ファイルが .gitignore に含まれている

- [ ] **認証・認可**
  - [ ] すべての開発者エンドポイントが認証保護されている
  - [ ] トークン有効期限が設定されている（24時間）
  - [ ] 期限切れトークンが拒否される

- [ ] **データ保護**
  - [ ] エラーログに個人情報が含まれていない
  - [ ] スタックトレースから機密情報が除外されている
  - [ ] SQL インジェクション対策（ORM 使用）
  - [ ] XSS 対策（フロントエンドで適切なエスケープ）

- [ ] **通信セキュリティ**
  - [ ] 本番環境で HTTPS 必須
  - [ ] CORS 設定が適切
  - [ ] セキュリティヘッダー設定（CSP, X-Frame-Options 等）

- [ ] **監査**
  - [ ] すべての開発者アクセスがログ記録される
  - [ ] IP アドレスが記録される
  - [ ] User-Agent が記録される

- [ ] **依存関係**
  - [ ] 使用ライブラリが最新版
  - [ ] 既知の脆弱性がない（npm audit, pip check）

---

## 付録H: よくある質問（FAQ）

### Q1: 開発者パスワードを忘れた場合は？
**A:** 
1. サーバーの環境変数を確認
2. Railway/Render のダッシュボードから確認
3. 変更する場合は、環境変数を更新して再デプロイ

### Q2: 複数の開発者でアクセスを共有できますか？
**A:** 
フェーズ2では1つのパスワードを共有します。フェーズ3で個別アカウント機能を実装予定です。

### Q3: エラーログはどのくらいの期間保存されますか？
**A:** 
フェーズ2では無期限保存。フェーズ3で90日後の自動削除機能を実装予定です。

### Q4: ダッシュボードの統計はリアルタイムですか？
**A:** 
5分間のキャッシュがあります。最新データを見たい場合はページをリロードしてください。

### Q5: エラーログが大量に記録されてデータベースが圧迫されたら？
**A:** 
一時的な対処として、古いログを手動削除できます：
```sql
DELETE FROM error_logs WHERE created_at < NOW() - INTERVAL '30 days';
```

### Q6: 特定の施設のデータだけを見たい場合は？
**A:** 
施設一覧から該当施設を選択して詳細ページへ。または、エラーログ・アクティビティログページでフィルタリング機能を使用してください。

### Q7: モバイルからアクセスできますか？
**A:** 
アクセス可能ですが、PCでの利用を推奨します。レスポンシブデザインは最低限の実装です。

### Q8: 他の開発者にアクセス権を付与したい
**A:** 
開発者パスワードを共有してください。個別アカウント機能はフェーズ3で実装予定です。

---

## 付録I: 用語集

| 用語 | 説明 |
|------|------|
| **開発者管理ページ** | システムの統計・エラー・アクティビティを閲覧する管理画面 |
| **宿泊施設管理者** | 各宿泊施設のスタッフ・運営者（FAQ管理等を行う） |
| **宿泊客（ゲスト）** | 宿泊施設に泊まる一般のお客様 |
| **エラーログ** | システムで発生したエラーの記録 |
| **アクティビティログ** | 管理者の操作履歴（ログイン、FAQ編集等） |
| **FAQ閲覧ログ** | チャットでFAQが表示された回数の記録 |
| **セッショントークン** | 認証後に発行される一時的なアクセストークン |
| **ダッシュボード** | システム全体の概要を表示するページ |
| **エスカレーション** | チャットボットで解決できず人間対応が必要な状態 |
| **Alembic** | Pythonのデータベースマイグレーションツール |
| **FastAPI** | Python製の高速なWebフレームワーク |
| **SQLAlchemy** | PythonのORMライブラリ |

---

## 付録J: 連絡先・サポート

### 開発者
- 担当: 栗延信之（kurinobu）

### 緊急時連絡
- システムダウン時の対応フロー参照（別ドキュメント）

### ドキュメント更新履歴
- 2024-12-28: 初版作成

---

**文書終了**

この実装計画書は、エビデンスベースで作成されました。
すべてのテーブル構造、API構造、ファイルパスは実際のシステムから確認済みです。
実装時にはこの計画書を参照しながら、段階的に進めてください。