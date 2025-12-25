--
-- PostgreSQL database dump
--

\restrict GNnEed842mKbOe1nhoSomuhM0VZxKPZ3TD8Awb2uG7wNrmX15DPeBwkwUUd7a9C

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg12+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: faq_category; Type: TYPE; Schema: public; Owner: yadopera_user
--

CREATE TYPE public.faq_category AS ENUM (
    'basic',
    'facilities',
    'location',
    'trouble'
);


ALTER TYPE public.faq_category OWNER TO yadopera_user;

--
-- Name: faq_suggestion_status; Type: TYPE; Schema: public; Owner: yadopera_user
--

CREATE TYPE public.faq_suggestion_status AS ENUM (
    'pending',
    'approved',
    'rejected'
);


ALTER TYPE public.faq_suggestion_status OWNER TO yadopera_user;

--
-- Name: check_forbidden_patterns(); Type: FUNCTION; Schema: public; Owner: yadopera_user
--

CREATE FUNCTION public.check_forbidden_patterns() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        DECLARE
            forbidden_patterns TEXT[] := ARRAY[
                'check-in', 'チェックイン', 'checkin',
                'Check-in', 'Check-In', 'CHECK-IN',
                'check in', 'Check In', 'CHECK IN'
            ];
            content_lower TEXT;
            pattern TEXT;
            is_test_facility BOOLEAN := FALSE;
        BEGIN
            -- messagesテーブルの場合: テスト施設かどうかをチェック
            IF TG_TABLE_NAME = 'messages' THEN
                SELECT EXISTS (
                    SELECT 1 FROM conversations c
                    JOIN facilities f ON c.facility_id = f.id
                    WHERE c.id = NEW.conversation_id
                    AND f.slug = 'test-facility'
                ) INTO is_test_facility;
                
                IF is_test_facility THEN
                    content_lower := LOWER(NEW.content);
                    FOREACH pattern IN ARRAY forbidden_patterns LOOP
                        IF content_lower LIKE '%' || LOWER(pattern) || '%' THEN
                            -- 「checkout」「checking」などは除外
                            IF content_lower NOT LIKE '%checkout%' 
                               AND content_lower NOT LIKE '%checking%' THEN
                                RAISE EXCEPTION '禁止用語が検出されました: % (パターン: %). このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない', NEW.content, pattern;
                            END IF;
                        END IF;
                    END LOOP;
                END IF;
            END IF;
            
            -- faq_translationsテーブルの場合: テスト施設かどうかをチェック
            IF TG_TABLE_NAME = 'faq_translations' THEN
                SELECT EXISTS (
                    SELECT 1 FROM faqs f
                    JOIN facilities fac ON f.facility_id = fac.id
                    WHERE f.id = NEW.faq_id
                    AND fac.slug = 'test-facility'
                ) INTO is_test_facility;
                
                IF is_test_facility THEN
                    content_lower := LOWER(NEW.question || ' ' || COALESCE(NEW.answer, ''));
                    FOREACH pattern IN ARRAY forbidden_patterns LOOP
                        IF content_lower LIKE '%' || LOWER(pattern) || '%' THEN
                            IF content_lower NOT LIKE '%checkout%' 
                               AND content_lower NOT LIKE '%checking%' THEN
                                RAISE EXCEPTION '禁止用語が検出されました: % (パターン: %). このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない', NEW.question, pattern;
                            END IF;
                        END IF;
                    END LOOP;
                END IF;
            END IF;
            
            -- faq_suggestionsテーブルの場合: テスト施設かどうかをチェック
            IF TG_TABLE_NAME = 'faq_suggestions' THEN
                SELECT EXISTS (
                    SELECT 1 FROM facilities f
                    WHERE f.id = NEW.facility_id
                    AND f.slug = 'test-facility'
                ) INTO is_test_facility;
                
                IF is_test_facility THEN
                    content_lower := LOWER(COALESCE(NEW.suggested_question, ''));
                    FOREACH pattern IN ARRAY forbidden_patterns LOOP
                        IF content_lower LIKE '%' || LOWER(pattern) || '%' THEN
                            IF content_lower NOT LIKE '%checkout%' 
                               AND content_lower NOT LIKE '%checking%' THEN
                                RAISE EXCEPTION '禁止用語が検出されました: % (パターン: %). このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない', NEW.suggested_question, pattern;
                            END IF;
                        END IF;
                    END LOOP;
                END IF;
            END IF;
            
            RETURN NEW;
        END;
        $$;


ALTER FUNCTION public.check_forbidden_patterns() OWNER TO yadopera_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO yadopera_user;

--
-- Name: conversations; Type: TABLE; Schema: public; Owner: yadopera_user
--

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


ALTER TABLE public.conversations OWNER TO yadopera_user;

--
-- Name: conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.conversations_id_seq OWNER TO yadopera_user;

--
-- Name: conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.conversations_id_seq OWNED BY public.conversations.id;


--
-- Name: escalation_schedules; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.escalation_schedules (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    day_of_week character varying[] NOT NULL,
    time_start time without time zone NOT NULL,
    time_end time without time zone NOT NULL,
    mode character varying(50) DEFAULT 'normal'::character varying,
    threshold numeric(3,2) DEFAULT 0.70,
    languages character varying[] DEFAULT ARRAY['en'::text, 'ja'::text],
    notify_channels character varying[] DEFAULT ARRAY['email'::text],
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.escalation_schedules OWNER TO yadopera_user;

--
-- Name: escalation_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.escalation_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.escalation_schedules_id_seq OWNER TO yadopera_user;

--
-- Name: escalation_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.escalation_schedules_id_seq OWNED BY public.escalation_schedules.id;


--
-- Name: escalations; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.escalations (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    conversation_id integer NOT NULL,
    trigger_type character varying(50) NOT NULL,
    ai_confidence numeric(3,2),
    escalation_mode character varying(50) DEFAULT 'normal'::character varying,
    notified_at timestamp with time zone,
    notification_channels character varying[] DEFAULT ARRAY['email'::text],
    resolved_at timestamp with time zone,
    resolved_by integer,
    resolution_notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.escalations OWNER TO yadopera_user;

--
-- Name: escalations_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.escalations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.escalations_id_seq OWNER TO yadopera_user;

--
-- Name: escalations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.escalations_id_seq OWNED BY public.escalations.id;


--
-- Name: facilities; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.facilities (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(50),
    address text,
    wifi_ssid character varying(100),
    wifi_password character varying(100),
    check_in_time time without time zone DEFAULT '15:00:00'::time without time zone,
    check_out_time time without time zone DEFAULT '11:00:00'::time without time zone,
    house_rules text,
    local_info text,
    languages character varying[] DEFAULT ARRAY['en'::text],
    timezone character varying(50) DEFAULT 'Asia/Tokyo'::character varying,
    subscription_plan character varying(50) DEFAULT 'small'::character varying,
    monthly_question_limit integer DEFAULT 200,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    staff_absence_periods json DEFAULT '[]'::json,
    icon_url character varying(255)
);


ALTER TABLE public.facilities OWNER TO yadopera_user;

--
-- Name: facilities_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.facilities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.facilities_id_seq OWNER TO yadopera_user;

--
-- Name: facilities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.facilities_id_seq OWNED BY public.facilities.id;


--
-- Name: faq_suggestions; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.faq_suggestions (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    source_message_id integer NOT NULL,
    suggested_question text NOT NULL,
    suggested_answer text NOT NULL,
    suggested_category character varying(50) NOT NULL,
    language character varying(10) DEFAULT 'en'::character varying,
    status character varying(20) DEFAULT 'pending'::character varying,
    reviewed_at timestamp with time zone,
    reviewed_by integer,
    created_faq_id integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.faq_suggestions OWNER TO yadopera_user;

--
-- Name: faq_suggestions_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.faq_suggestions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faq_suggestions_id_seq OWNER TO yadopera_user;

--
-- Name: faq_suggestions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.faq_suggestions_id_seq OWNED BY public.faq_suggestions.id;


--
-- Name: faq_translations; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.faq_translations (
    id integer NOT NULL,
    faq_id integer NOT NULL,
    language character varying(10) DEFAULT 'en'::character varying NOT NULL,
    question text NOT NULL,
    answer text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    embedding public.vector(1536)
);


ALTER TABLE public.faq_translations OWNER TO yadopera_user;

--
-- Name: faq_translations_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.faq_translations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faq_translations_id_seq OWNER TO yadopera_user;

--
-- Name: faq_translations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.faq_translations_id_seq OWNED BY public.faq_translations.id;


--
-- Name: faqs; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.faqs (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    category character varying(50) NOT NULL,
    priority integer DEFAULT 1,
    is_active boolean DEFAULT true,
    created_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    intent_key character varying(100) NOT NULL
);


ALTER TABLE public.faqs OWNER TO yadopera_user;

--
-- Name: faqs_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.faqs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faqs_id_seq OWNER TO yadopera_user;

--
-- Name: faqs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.faqs_id_seq OWNED BY public.faqs.id;


--
-- Name: guest_feedback; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.guest_feedback (
    id integer NOT NULL,
    message_id integer NOT NULL,
    facility_id integer NOT NULL,
    feedback_type character varying(10) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.guest_feedback OWNER TO yadopera_user;

--
-- Name: guest_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.guest_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.guest_feedback_id_seq OWNER TO yadopera_user;

--
-- Name: guest_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.guest_feedback_id_seq OWNED BY public.guest_feedback.id;


--
-- Name: ignored_feedbacks; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.ignored_feedbacks (
    id integer NOT NULL,
    message_id integer NOT NULL,
    facility_id integer NOT NULL,
    ignored_at timestamp with time zone DEFAULT now() NOT NULL,
    ignored_by integer
);


ALTER TABLE public.ignored_feedbacks OWNER TO yadopera_user;

--
-- Name: ignored_feedbacks_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.ignored_feedbacks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ignored_feedbacks_id_seq OWNER TO yadopera_user;

--
-- Name: ignored_feedbacks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.ignored_feedbacks_id_seq OWNED BY public.ignored_feedbacks.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: yadopera_user
--

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


ALTER TABLE public.messages OWNER TO yadopera_user;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO yadopera_user;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: overnight_queue; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.overnight_queue (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    escalation_id integer NOT NULL,
    guest_message text NOT NULL,
    scheduled_notify_at timestamp with time zone NOT NULL,
    notified_at timestamp with time zone,
    resolved_at timestamp with time zone,
    resolved_by integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.overnight_queue OWNER TO yadopera_user;

--
-- Name: overnight_queue_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.overnight_queue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.overnight_queue_id_seq OWNER TO yadopera_user;

--
-- Name: overnight_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.overnight_queue_id_seq OWNED BY public.overnight_queue.id;


--
-- Name: processed_feedbacks; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.processed_feedbacks (
    id integer NOT NULL,
    message_id integer NOT NULL,
    facility_id integer NOT NULL,
    faq_suggestion_id integer,
    processed_at timestamp with time zone DEFAULT now() NOT NULL,
    processed_by integer
);


ALTER TABLE public.processed_feedbacks OWNER TO yadopera_user;

--
-- Name: processed_feedbacks_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.processed_feedbacks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.processed_feedbacks_id_seq OWNER TO yadopera_user;

--
-- Name: processed_feedbacks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.processed_feedbacks_id_seq OWNED BY public.processed_feedbacks.id;


--
-- Name: qr_codes; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.qr_codes (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    location character varying(50) NOT NULL,
    custom_location_name character varying(50),
    qr_code_url text NOT NULL,
    qr_code_data text NOT NULL,
    format character varying(10) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.qr_codes OWNER TO yadopera_user;

--
-- Name: qr_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.qr_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.qr_codes_id_seq OWNER TO yadopera_user;

--
-- Name: qr_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.qr_codes_id_seq OWNED BY public.qr_codes.id;


--
-- Name: question_patterns; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.question_patterns (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    total_count integer DEFAULT 0,
    resolved_count integer DEFAULT 0,
    last_asked_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    pattern_embedding public.vector(1536) NOT NULL,
    resolution_rate numeric(3,2) GENERATED ALWAYS AS (
CASE
    WHEN (total_count > 0) THEN ((resolved_count)::numeric / (total_count)::numeric)
    ELSE 0.0
END) STORED
);


ALTER TABLE public.question_patterns OWNER TO yadopera_user;

--
-- Name: question_patterns_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.question_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.question_patterns_id_seq OWNER TO yadopera_user;

--
-- Name: question_patterns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.question_patterns_id_seq OWNED BY public.question_patterns.id;


--
-- Name: session_tokens; Type: TABLE; Schema: public; Owner: yadopera_user
--

CREATE TABLE public.session_tokens (
    id integer NOT NULL,
    facility_id integer NOT NULL,
    token character varying(10) NOT NULL,
    primary_session_id character varying(100) NOT NULL,
    linked_session_ids text[] DEFAULT ARRAY[]::text[],
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL
);


ALTER TABLE public.session_tokens OWNER TO yadopera_user;

--
-- Name: session_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.session_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.session_tokens_id_seq OWNER TO yadopera_user;

--
-- Name: session_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.session_tokens_id_seq OWNED BY public.session_tokens.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: yadopera_user
--

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


ALTER TABLE public.users OWNER TO yadopera_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: yadopera_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO yadopera_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yadopera_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: conversations id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.conversations ALTER COLUMN id SET DEFAULT nextval('public.conversations_id_seq'::regclass);


--
-- Name: escalation_schedules id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.escalation_schedules ALTER COLUMN id SET DEFAULT nextval('public.escalation_schedules_id_seq'::regclass);


--
-- Name: escalations id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.escalations ALTER COLUMN id SET DEFAULT nextval('public.escalations_id_seq'::regclass);


--
-- Name: facilities id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.facilities ALTER COLUMN id SET DEFAULT nextval('public.facilities_id_seq'::regclass);


--
-- Name: faq_suggestions id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_suggestions ALTER COLUMN id SET DEFAULT nextval('public.faq_suggestions_id_seq'::regclass);


--
-- Name: faq_translations id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_translations ALTER COLUMN id SET DEFAULT nextval('public.faq_translations_id_seq'::regclass);


--
-- Name: faqs id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faqs ALTER COLUMN id SET DEFAULT nextval('public.faqs_id_seq'::regclass);


--
-- Name: guest_feedback id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.guest_feedback ALTER COLUMN id SET DEFAULT nextval('public.guest_feedback_id_seq'::regclass);


--
-- Name: ignored_feedbacks id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.ignored_feedbacks ALTER COLUMN id SET DEFAULT nextval('public.ignored_feedbacks_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: overnight_queue id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.overnight_queue ALTER COLUMN id SET DEFAULT nextval('public.overnight_queue_id_seq'::regclass);


--
-- Name: processed_feedbacks id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.processed_feedbacks ALTER COLUMN id SET DEFAULT nextval('public.processed_feedbacks_id_seq'::regclass);


--
-- Name: qr_codes id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.qr_codes ALTER COLUMN id SET DEFAULT nextval('public.qr_codes_id_seq'::regclass);


--
-- Name: question_patterns id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.question_patterns ALTER COLUMN id SET DEFAULT nextval('public.question_patterns_id_seq'::regclass);


--
-- Name: session_tokens id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.session_tokens ALTER COLUMN id SET DEFAULT nextval('public.session_tokens_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.alembic_version (version_num) FROM stdin;
010
\.


--
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.conversations (id, facility_id, session_id, guest_language, location, user_agent, ip_address, started_at, last_activity_at, ended_at, is_escalated, total_messages, auto_resolved) FROM stdin;
24	2	c157e2e9-0891-4b57-8e20-eef3b77bc0cf	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-10 04:48:36.703007+00	2025-12-10 04:48:53.28961+00	\N	f	2	f
11	2	test-session-category-basic-1	en	entrance	\N	\N	2025-12-03 08:55:33.235418+00	2025-12-04 06:55:33.235421+00	\N	f	2	f
12	2	test-session-category-basic-2	en	entrance	\N	\N	2025-12-02 08:55:33.238434+00	2025-12-04 04:55:33.238436+00	\N	f	2	f
13	2	test-session-category-facilities-1	en	entrance	\N	\N	2025-12-01 08:55:33.240339+00	2025-12-04 02:55:33.240341+00	\N	f	2	f
14	2	test-session-category-location-1	en	entrance	\N	\N	2025-11-30 08:55:33.241991+00	2025-12-04 00:55:33.241993+00	\N	f	2	f
2	2	1ac4e038-7fb8-4b52-abc1-e797c3a103bf	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-02 00:58:52.179407+00	2025-12-02 07:45:36.044011+00	\N	f	8	f
15	2	test-session-category-trouble-1	en	entrance	\N	\N	2025-11-29 08:55:33.243518+00	2025-12-03 22:55:33.243519+00	\N	f	2	f
16	2	test-session-overnight-1	en	entrance	\N	\N	2025-12-03 08:55:33.245112+00	2025-12-04 06:55:33.245113+00	\N	t	2	f
17	2	test-session-overnight-2	ja	entrance	\N	\N	2025-12-02 08:55:33.314609+00	2025-12-04 04:55:33.314612+00	\N	t	2	f
28	2	0d7e0287-3694-49fd-ae98-4dfda77168fb	en	\N	\N	\N	2025-12-18 09:00:06.371356+00	2025-12-18 22:17:44.368691+00	\N	f	10	f
29	2	39a3c5b5-f21b-4d3e-9146-2639e04e8efd	en	\N	\N	\N	2025-12-20 02:45:56.408556+00	2025-12-20 02:46:00.478286+00	\N	f	2	f
30	2	df5438fc-28c9-4bd0-94e9-2106922ae6b0	en	\N	\N	\N	2025-12-20 06:27:30.308692+00	2025-12-20 06:27:38.384688+00	\N	f	2	f
31	2	f0c9580a-3f73-4a58-851f-ef54eebc6358	en	\N	\N	\N	2025-12-22 01:19:13.40994+00	2025-12-22 01:19:13.409941+00	\N	f	0	f
25	2	f6b13d95-3492-46ec-95af-118a8bcf5f5e	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-12 12:39:21.166425+00	2025-12-13 07:23:35.553646+00	\N	f	66	f
5	2	test-session-unresolved-1	en	entrance	\N	\N	2025-12-03 04:32:45.655802+00	2025-12-04 02:32:45.655805+00	\N	t	2	f
6	2	test-session-unresolved-2	en	entrance	\N	\N	2025-12-02 04:32:45.664629+00	2025-12-04 00:32:45.664631+00	\N	t	2	f
7	2	test-session-unresolved-3	ja	entrance	\N	\N	2025-12-01 04:32:45.6661+00	2025-12-03 22:32:45.666101+00	\N	t	2	f
18	2	94debf7e-f607-43c5-bc13-a9f2ca16016f	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.32 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	192.168.65.1	2025-12-05 09:30:35.866205+00	2025-12-06 06:10:01.574151+00	\N	f	20	f
19	2	ac95eda5-e94b-43c3-afbe-c7b247c4fadd	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-05 09:30:36.485614+00	2025-12-06 06:10:02.119207+00	\N	f	22	f
20	2	23744f70-941e-4cbd-8e57-a51dceb25806	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.32 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	192.168.65.1	2025-12-06 14:07:27.753084+00	2025-12-06 14:07:30.831406+00	\N	f	2	f
4	2	18e17582-653e-446d-8a86-1993b8a9f37a	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.32 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	192.168.65.1	2025-12-03 07:21:05.950228+00	2025-12-04 06:59:27.12217+00	\N	f	14	f
3	2	37dee6e7-1df1-4226-aa5a-06fbf3ba5b64	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-02 12:58:50.601021+00	2025-12-04 06:59:27.968286+00	\N	f	68	f
9	2	ad59235f-490f-42f9-9e52-003b454624ae	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.32 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	192.168.65.1	2025-12-04 08:01:26.47454+00	2025-12-05 02:56:40.820281+00	\N	f	26	f
10	2	6951a3d9-8cbd-42d3-a3c9-b252523407b5	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-04 08:01:28.266239+00	2025-12-05 02:56:41.104561+00	\N	t	30	f
21	2	168d0fce-1f6d-47a1-9830-dcaa98db2b28	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-06 14:07:28.263996+00	2025-12-07 08:32:55.165515+00	\N	f	10	f
22	2	e836303f-2202-412e-8f82-25ecfdca4c2e	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-07 14:22:21.968024+00	2025-12-08 14:18:22.012608+00	\N	f	4	f
23	2	5a87e680-6ef6-461a-aafb-6116e0683c46	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	192.168.65.1	2025-12-09 09:07:45.503272+00	2025-12-09 20:30:19.000926+00	\N	f	6	f
26	2	30ca8bc5-b7c0-4e98-8f32-06f18eb24991	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	192.168.65.1	2025-12-14 06:02:52.692833+00	2025-12-15 01:55:29.14331+00	\N	f	32	f
27	2	6eb0d2ad-2ec4-4ada-86e4-2da5e0f9ec1b	en	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	192.168.65.1	2025-12-17 07:25:21.219156+00	2025-12-18 06:26:59.151906+00	\N	f	18	f
\.


--
-- Data for Name: escalation_schedules; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.escalation_schedules (id, facility_id, day_of_week, time_start, time_end, mode, threshold, languages, notify_channels, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: escalations; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.escalations (id, facility_id, conversation_id, trigger_type, ai_confidence, escalation_mode, notified_at, notification_channels, resolved_at, resolved_by, resolution_notes, created_at) FROM stdin;
2	2	6	low_confidence	0.40	normal	\N	{email}	\N	\N	\N	2025-12-04 04:32:45.64569+00
1	2	5	low_confidence	0.50	normal	\N	{email}	2025-12-04 05:05:13.984695+00	1	FAQ created from suggestion 4	2025-12-04 04:32:45.64569+00
4	2	5	low_confidence	0.50	normal	\N	{email}	2025-12-04 07:34:29.036324+00	1	FAQ created from suggestion 5	2025-12-04 07:20:48.976729+00
5	2	10	staff_mode	0.00	normal	\N	{email}	\N	\N	\N	2025-12-04 08:06:24.369221+00
9	2	17	low_confidence	0.50	normal	\N	{email}	2025-12-05 12:49:21.238807+00	1	FAQ created from suggestion 6	2025-12-04 08:55:33.21179+00
8	2	16	low_confidence	0.50	normal	\N	{email}	2025-12-14 00:54:33.701867+00	1	FAQ created from suggestion 7	2025-12-04 08:55:33.21179+00
3	2	7	keyword	0.60	normal	\N	{email}	2025-12-14 00:56:30.513779+00	1	FAQ created from suggestion 11	2025-12-04 04:32:45.64569+00
11	2	16	low_confidence	0.50	normal	\N	{email}	\N	\N	\N	2025-12-14 01:21:40.164084+00
12	2	17	low_confidence	0.50	normal	\N	{email}	2025-12-14 01:53:49.760528+00	1	FAQ created from suggestion 13	2025-12-14 01:21:40.164084+00
13	2	17	low_confidence	0.50	normal	\N	{email}	\N	\N	\N	2025-12-15 00:46:58.112527+00
10	2	7	keyword	0.60	normal	\N	{email}	2025-12-17 05:30:47.24378+00	1	FAQ created from suggestion 22	2025-12-14 01:21:40.164084+00
\.


--
-- Data for Name: facilities; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.facilities (id, name, slug, email, phone, address, wifi_ssid, wifi_password, check_in_time, check_out_time, house_rules, local_info, languages, timezone, subscription_plan, monthly_question_limit, is_active, created_at, updated_at, staff_absence_periods, icon_url) FROM stdin;
2	やどぺらゲストハウス	test-facility	test@example.com	090-1234-5679	Test Address, Test City	TestWiFi	testtesttesttest111111111	15:00:00	10:00:00	禁煙（中庭の喫煙エリアのみ可）、門限23:00、静粛時間22:00-8:00、キッチン使用可能時間~22:00	最寄り駅: 京都駅（徒歩10分）、コンビニ: セブンイレブン（徒歩3分）、レストラン: 多数あり	{en,ja}	Asia/Tokyo	small	200	t	2025-12-01 07:31:02.85344+00	2025-12-14 02:04:44.011903+00	[{"start_time": "22:00", "end_time": "07:30", "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]}, {"start_time": "11:00", "end_time": "15:00", "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]}]	\N
\.


--
-- Data for Name: faq_suggestions; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.faq_suggestions (id, facility_id, source_message_id, suggested_question, suggested_answer, suggested_category, language, status, reviewed_at, reviewed_by, created_faq_id, created_at) FROM stdin;
1	2	28	申し訳ありませんが、アイロンの貸し出しについての情報はありません。スタッフにお問い合わせください。	We apologize for any inconvenience, but we currently do not have information regarding the availability of iron rentals. Please feel free to contact our staff, and they will be happy to assist you further.	facilities	en	approved	2025-12-04 00:51:41.138392+00	1	7	2025-12-04 00:51:07.262649+00
6	2	142	朝食の時間は何時ですか？	朝食は毎日午前7時から午前10時までご用意しております。お好きな時間にお越しいただき、ぜひお楽しみください。ご不明な点がございましたら、お気軽にお尋ねください。	basic	ja	approved	2025-12-05 12:49:21.241371+00	1	15	2025-12-05 12:28:44.453187+00
9	2	106	レンタルバイクはありますか？	Yes, we offer rental bikes for our guests! You can easily rent one at the reception desk, and our staff will be happy to assist you with any information you need to enjoy your ride.	facilities	en	pending	\N	\N	\N	2025-12-05 12:54:35.00744+00
7	2	141	What time is breakfast?	Breakfast is served daily from 7:30 AM to 10:00 AM in our dining area. We offer a variety of options to suit different tastes, so be sure to join us to start your day off right! If you have any dietary restrictions, please let us know in advance.	facilities	en	approved	2025-12-14 00:54:33.704266+00	1	16	2025-12-05 12:28:50.613999+00
12	2	141	What time is breakfast?	Breakfast is served daily from 7:00 AM to 10:00 AM. We offer a variety of options to ensure a delightful start to your day. If you have any dietary preferences or restrictions, please let us know, and we’ll be happy to accommodate you!	facilities	en	pending	\N	\N	\N	2025-12-14 01:43:46.712004+00
13	2	142	朝食の時間は何時ですか？	朝食の時間は毎日午前7時から午前10時までとなっております。お客様のご都合に合わせてお楽しみいただけるよう、幅広いメニューをご用意しておりますので、ぜひお越しください。	basic	ja	approved	2025-12-14 01:53:49.761824+00	1	19	2025-12-14 01:53:34.470237+00
2	2	28	申し訳ありませんが、アイロンの貸し出しについての情報はありません。スタッフにお問い合わせください。	We apologize for the inconvenience, but we currently do not have information available regarding iron rentals. Please feel free to reach out to our staff, and they will be happy to assist you with any inquiries you may have.	facilities	en	rejected	2025-12-14 03:19:26.239731+00	1	\N	2025-12-04 01:47:34.754504+00
14	2	32	ドリンカブルな水はありますか？	Yes, we do provide drinkable water for our guests. You can find it available in the common areas, and if you have any specific requests or need assistance, our staff would be more than happy to help you. Please feel free to reach out to them at any time!	facilities	en	rejected	2025-12-14 03:19:36.311512+00	1	\N	2025-12-14 02:23:36.671704+00
16	2	28	アイロンは貸し出ししてますか？	アイロンの貸し出しについてですが、当ゲストハウスではアイロンをご用意しております。必要な場合は、スタッフにお声がけください。快適なご滞在をお手伝いできるよう努めますので、お気軽にご相談ください。	facilities	ja	rejected	2025-12-14 03:36:32.46691+00	1	\N	2025-12-14 03:19:48.39701+00
15	2	28	アイロンは貸し出ししてますか？	ありがとうございます。アイロンの貸し出しは行っておりませんが、近くのランドリーサービスをご利用いただけます。何か他にお困りのことがございましたら、スタッフにお気軽にお声がけください。	facilities	ja	rejected	2025-12-14 03:36:44.508274+00	1	\N	2025-12-14 03:19:46.367832+00
17	2	28	アイロンは貸し出ししてますか？	当ゲストハウスではアイロンの貸し出しを行っております。ご利用希望の場合は、フロントスタッフにお声がけいただければ、すぐにお手配いたします。お気軽にお問い合わせください。	facilities	ja	rejected	2025-12-14 03:38:42.506577+00	1	\N	2025-12-14 03:38:35.617928+00
18	2	28	アイロンは貸し出ししてますか？	ご質問ありがとうございます。当ゲストハウスではアイロンの貸し出しを行っておりますので、必要な際はお気軽にフロントスタッフにお声がけください。お手伝いできることがあれば、どうぞお知らせください。	facilities	ja	rejected	2025-12-14 03:39:06.55376+00	1	\N	2025-12-14 03:38:56.683597+00
19	2	28	アイロンは貸し出ししてますか？	はい、アイロンを貸し出しております。必要な場合は、フロントまでお気軽にお声がけください。スタッフが喜んでお手伝いいたします。	facilities	ja	rejected	2025-12-14 05:36:39.199717+00	1	\N	2025-12-14 05:36:24.538735+00
20	2	32	ドリンカブルな水はありますか？	はい、当ゲストハウスではドリンカブルな水をご用意しております。お部屋や共用スペースに設置された水サーバーをご利用いただけますので、いつでも安心してお飲みいただけます。何かご不明な点がございましたら、スタッフまでお気軽にお尋ねください。	facilities	ja	rejected	2025-12-14 05:37:09.033562+00	1	\N	2025-12-14 05:36:53.922101+00
21	2	32	ドリンカブルな水はありますか？	はい、当ゲストハウスではドリンカブルな水をご用意しております。お部屋や共用スペースに設置された水のボトルを自由にご利用いただけますので、ぜひご活用ください。また、追加の水が必要な場合は、スタッフにお声掛けいただければお手伝いします。	facilities	ja	pending	\N	\N	\N	2025-12-15 09:01:31.054242+00
\.


--
-- Data for Name: faq_translations; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.faq_translations (id, faq_id, language, question, answer, created_at, updated_at, embedding) FROM stdin;
1	14	en	国際電話できる電話はありますか？	当施設にはありません。	2025-12-05 09:09:35.599463+00	2025-12-05 09:13:21.734041+00	[-0.023867702,0.027478106,0.0135243805,0.021076957,-0.005239966,-0.006005957,-0.03862157,-0.010050586,0.01730067,-0.08376139,-0.028492924,-0.017964203,0.011319106,0.008001437,-0.020315845,-0.026072977,-0.039285105,0.03444521,-0.012070461,0.030424979,0.010762909,0.05210692,-0.0048325756,-0.046642527,0.0072256885,-0.01134838,-0.012275376,0.013085278,0.007391572,0.013914695,0.015007574,-0.040709753,-0.032532673,0.03286444,-0.013602444,0.021174535,0.04316873,0.0018857046,-0.009479752,-0.026756026,-0.017242122,-0.02519477,-0.018354516,-0.018256938,-0.05815679,0.039226558,-0.008147805,0.02492155,0.021076957,-0.0048447726,-0.026541354,0.0136805065,0.025097191,-0.08953804,-0.013016973,-0.011094676,-0.011299591,-0.011514263,-0.035538092,0.00052265485,-0.0016685924,0.026580384,0.0060937777,-0.0032225302,0.0116216,0.03555761,0.012792542,-0.027185371,-0.0289613,0.025643632,-0.046993807,0.027478106,0.011494748,0.022989497,-0.00088735454,0.07923374,-0.025155738,-0.004259302,-0.021896617,-0.0048545306,0.02841486,0.02755617,-0.0360455,0.020413423,0.0010209151,0.037255473,-0.031108027,0.012021672,-0.0099627655,0.061357364,-0.0005705293,-0.008255142,0.0023662788,0.02310659,0.027712295,0.015905296,0.024531236,0.05206789,-0.010606783,0.027321981,0.0116313575,-0.045276426,0.011436201,-0.035518575,0.006132809,0.003032252,0.016334642,0.015495467,-0.020784222,0.04422258,-0.018442338,-0.056751657,-0.04734509,0.014041547,0.015944328,-0.034620855,0.04004622,-0.03994864,-0.0023967721,-0.02060858,0.06506535,0.025175255,0.01384639,-0.000930655,0.040787816,0.019769406,-0.030112727,0.02269676,-0.041412316,-0.016285853,0.0034615975,-0.0313227,0.00563028,0.015271036,-0.010597026,0.037021287,-0.05679069,0.0134365605,-0.007864827,-0.034698915,0.056439407,0.0110751605,0.048477,-0.0021808797,0.017232364,-0.037099347,-0.0017015252,-0.014822175,0.025565568,0.033606037,-0.02937113,-0.022208868,-0.009889581,-0.044847082,-0.042231977,0.017837351,-0.034484245,0.050584696,0.0005278387,0.0498431,0.00019820634,0.0109190345,-0.027321981,-0.01411961,-0.0065475176,0.017076239,0.03963639,-0.002078422,-0.014022031,0.00078245765,0.013817117,-0.027029246,-0.024218986,0.02950774,-0.030171273,-0.0050155353,0.08422977,0.027009731,-0.042505197,0.04531546,-0.01230465,0.01525152,0.007186657,-0.002193077,-0.0171543,-0.052145954,0.00871376,0.014168399,-0.010684846,0.009391931,-0.003712862,-0.035674702,0.032922987,0.06479213,-0.04843797,-0.014822175,-0.0185204,-0.034659885,-0.0040129162,-0.057024878,-0.052224018,-0.07006136,0.025565568,-0.013495107,-0.0007422065,-0.037606757,-0.027517138,0.00026315704,0.013007215,-0.037353054,-0.0046252212,-0.019310785,-0.0068256166,0.004054387,0.020979378,0.0026175433,0.04871119,0.050311476,-0.025624115,-0.028219704,-0.004488611,0.008484451,-0.03327427,-0.0032810771,0.0066841277,0.0113874115,-0.011904578,0.020393908,-0.012109493,0.032571707,-0.025175255,-0.013465834,0.008918676,0.0024675163,-0.010470173,-0.031947203,-0.019174177,0.011826515,-0.0015917494,0.0060498673,0.033801194,-0.0026882878,0.04531546,0.027790358,0.004698405,-0.046681557,0.059600953,-0.013016973,0.024589783,-0.03296202,0.0057229795,0.037060317,0.0046471762,-0.061708648,-0.056010064,-0.016061421,0.0242385,0.0020149963,0.007093957,-0.00685489,0.0058644684,-0.023887219,-0.024394626,-0.018666768,0.027497623,-0.054761056,-0.0116313575,0.03344991,-0.046720587,0.01884241,-0.07150553,-0.020725675,0.050467603,-0.011094676,-0.019954804,-0.013670749,-0.005923015,-0.02396528,0.038875278,0.00045221538,-0.08805484,0.032708313,-0.08095113,-0.051443387,-0.019603522,-0.019759648,-0.04231004,0.026775543,-0.013016973,0.055229433,0.06529953,0.046252213,-0.036299203,-0.020335361,-0.015046606,0.023223685,0.026521837,0.006752433,-0.02015972,-0.017027449,0.024648331,0.0061474456,0.012431501,-0.028590502,-0.04000719,0.06428472,0.023731092,0.06955396,0.070529744,-0.048242815,-0.044105485,0.01293891,0.027458591,0.0002550763,0.030288368,-0.027751327,0.037801914,0.0047471942,-0.0066841277,-0.026404744,0.04562771,-0.029878538,-0.044144515,-0.017222606,-0.04172457,-0.011972883,0.001592969,-0.011885062,-0.050194383,0.0099627655,0.010343322,-0.025565568,0.062528305,0.01175821,-0.01652004,0.06916364,-0.037157893,0.033645067,-0.013719538,-0.019252239,0.04445677,0.049374722,-0.006059625,-0.0059961993,0.014949027,-0.029898055,0.0038031223,-0.002065005,0.007977043,0.028863722,-0.0135243805,-0.020530518,-0.00726472,0.0014234264,0.026112009,-0.023087075,0.0021845389,-0.0023943326,0.0065670335,-0.040163312,-0.04734509,-0.017544616,-0.0072012935,0.013221888,0.003881185,0.039148495,-0.036572423,0.011728937,-0.00435932,-0.036611456,-0.009021133,0.021037925,0.04453483,-0.01802275,0.044847082,-0.0087381555,-0.010557994,0.03454279,0.041334257,0.003886064,0.025507022,-0.020862285,-0.0011593546,-0.004259302,-0.017944688,0.02905888,-0.0246093,0.012792542,0.026775543,-0.06689982,0.030385947,0.010187196,0.0013648793,-0.042427134,-0.010597026,0.0008312469,-0.049647942,0.059639983,-0.08930385,-0.05741519,-0.011377654,0.0034128083,-0.049999226,0.02855147,0.042388104,-0.025819272,-0.01211925,0.002583391,0.019603522,-0.008108774,0.013973242,-0.02519477,0.014168399,0.0145489555,0.015446678,-0.010323806,-0.015554014,-0.01448065,-0.0010794622,-0.071973905,0.036513876,0.010450658,-0.006001078,0.010948309,-0.016383432,0.008201473,-0.03690419,-0.012216829,0.02810261,0.0022174716,-0.021037925,-0.02673651,-0.0054497593,0.04402742,-0.022891918,0.07513545,0.025994914,0.026658447,-0.007874586,0.008469814,-0.01071412,-9.658747e-05,-0.031478826,-0.031342216,0.024316564,0.029390646,0.017944688,0.054331712,0.05628328,0.019183934,-0.0022174716,0.007303751,0.04063169,-0.0128120575,-0.035577122,-0.0064450605,0.0043056514,-0.0094943885,-0.048086688,-0.03590889,0.00080685224,0.010382353,0.007986801,0.0037518935,-0.0069378316,0.02855147,-0.07119328,0.0293321,-0.00885525,0.05901548,-0.03317669,-0.050779853,-0.0022138124,-0.012636417,0.041022003,-0.02369206,0.015583287,0.016159,-0.037821427,-0.050818887,0.023555452,0.004230028,-0.009528541,-0.07131037,0.02015972,0.031108027,0.043285824,0.020784222,-0.0444958,-0.017612921,0.007454998,-0.008704003,0.026853604,-0.0033688978,0.021057442,0.04675962,-0.036748067,0.003854351,-0.0538243,-4.497759e-05,-0.022423541,-0.043793235,-0.024082376,-0.025721693,0.054682996,0.0002828252,-0.043793235,-0.03046401,-0.012372955,-0.046642527,0.014802659,0.011699663,-0.047852498,0.006010836,0.004344683,0.014870964,0.01965231,0.018315485,-0.012607143,-0.013124309,0.0064401813,-0.01929127,0.044378705,-0.024062859,-0.0022052743,-0.010382353,-0.028707596,-0.077008955,0.021135503,0.011777726,0.023009012,-0.014470892,-0.019301029,0.032766864,0.04289551,-0.025370412,0.038348354,0.0187058,0.031303186,0.009196774,0.0055717328,0.023848187,-0.052692395,-0.021994196,-0.045471583,-0.020589065,0.008406389,0.0039616874,0.003137149,0.013797601,-0.018217906,-0.0058547105,-0.024941066,-0.04262229,0.016246822,0.0039226557,0.024941066,0.0025297229,-0.02201371,0.014724596,0.04145135,0.025994914,0.0048057414,0.012626658,0.019837711,0.023223685,0.00017884311,0.0023809155,0.01098734,-0.003854351,0.009587089,0.0058986205,-0.005308271,0.05542459,0.0014673368,0.031908173,0.024823971,-0.033196207,-0.02129163,0.010909277,0.018178876,0.0011459376,0.017827593,0.042427134,-0.0142367035,-0.0034420819,-0.004108055,-0.0077379756,0.008235626,0.020042624,0.016041907,0.025702178,0.011563053,-0.012753511,-0.0132121295,0.0036494362,-0.023477389,0.032337517,0.014812417,0.0068988004,-0.006654854,0.007508666,0.012538838,0.01552474,0.00058486115,0.004847212,-0.017242122,-0.0001448431,0.0007916056,-0.003237167,0.0124998065,0.015192973,0.009196774,-0.020218266,0.012421744,0.0057083424,-0.033079114,0.003954369,0.00046014364,0.03827029,-0.021311145,0.043832265,-0.017730014,0.025409443,0.01244126,0.007113473,0.007533061,-0.0350502,0.004571553,-0.0019125387,-0.013192614,0.0052350867,0.01080194,-0.019222965,0.01252908,-0.01189482,-0.017007934,-0.012763268,-0.00019271755,-0.03077626,0.0065182443,-0.038153194,0.014197673,-0.06791464,0.05152145,0.026287649,-0.022852886,-0.008303931,0.03875818,0.0067475536,0.014744112,-0.011270317,0.0065865493,0.0028492925,-0.0032127723,-0.002895642,0.016285853,0.018188633,0.0005022244,-0.004378835,-0.0015954085,0.06287959,0.015719898,0.027263435,-0.0027248797,-0.018403307,0.003137149,-0.019525459,-0.0022967542,-0.0015258839,-0.001230099,0.015017332,0.016627377,-0.038387384,0.0030395705,0.02728295,-0.007523303,-0.04621318,0.0009184577,-0.0014331843,0.0108312145,-0.015436919,-0.031400762,-0.014139125,0.014265978,0.0059864414,0.01987674,0.010850729,-0.0047862255,-4.486324e-05,0.009874945,-0.0063669975,0.03050304,0.029800477,-0.00011091932,-0.0011843591,0.02265773,-0.01929127,-0.033879258,0.05261433,-0.020198751,-0.036240656,-0.004661813,0.019457154,-0.01316334,0.009557814,0.0012404667,0.016803019,0.019779162,0.003332306,-0.03487456,0.014539197,-0.019330302,-0.03186914,0.03300105,0.013251161,-0.004227589,0.004898441,0.016061421,-0.00031118395,0.013700022,0.054917183,0.019349817,-0.0095382985,0.0104409,0.011133707,-0.009826155,0.02501913,0.029819991,-0.0018698481,-0.056439407,-0.015768686,-0.026502322,-0.0025638752,0.010860488,0.016198032,-0.0040617054,0.026873121,-0.022423541,-0.04539352,0.015319825,0.018120328,-0.004888683,-0.03690419,-0.027048761,-0.019964563,-0.010479932,0.0047447546,-0.0444958,0.016588345,0.0077282176,0.0014392829,-0.036025986,-0.0011502067,0.03586986,-0.017056722,0.022404024,0.01978892,-0.012743752,-0.03385974,-0.017720256,-0.007176899,0.0081722,0.010099376,0.036982253,0.0064304234,-0.032200906,-0.01057751,0.005230208,0.036104046,-0.037255473,-0.0146367755,0.005762011,0.016227305,0.005610764,0.0022869962,0.0039031403,-0.06678273,-0.016237063,-0.03454279,0.032922987,0.004534961,0.033567008,0.01766171,0.008435662,-0.014783144,0.003890943,0.010616542,0.0047252392,-0.032747347,-0.028024547,0.00962124,-0.009362658,-0.014002516,0.0062352666,0.011494748,0.017681224,-0.01888144,0.018130086,-0.030112727,-0.0056058853,0.008133168,0.00640115,-0.005557096,0.02591685,-0.012519322,0.00036195526,0.018803379,-0.012041188,-0.0064157867,0.026209587,0.043598074,0.00626454,-0.016588345,-0.029898055,0.016890839,0.027009731,0.012782784,-0.008591787,0.01793493,0.020706158,-0.010177438,0.0076696705,0.0054497593,0.0016795701,-0.04094394,0.004666692,-0.0055131856,0.01738849,-0.012831573,0.030542072,0.02937113,-0.023477389,-0.010138406,-0.021623397,-0.041685537,0.0061474456,0.011280076,0.011514263,-0.00681098,0.019642552,-0.04765734,0.020784222,-0.0024309244,0.008016074,0.03183011,-0.04789153,-0.005859589,0.032708313,-0.030756745,0.009787124,-0.015183215,0.01993529,-0.011738694,0.036260173,0.038816728,-0.021681944,0.02474591,0.025409443,-0.04199779,0.0143928295,-0.005171661,0.0076989443,-0.020393908,-0.00027947093,0.02351642,0.005830316,-0.020530518,0.00076965045,-0.04418355,-0.009684667,0.0129681835,0.005801042,0.0031834987,-0.030444494,0.013582928,0.021642912,0.0111434655,-0.026853604,-0.07657961,-0.004556916,0.0003659194,-0.017827593,0.026775543,0.015368614,0.00626454,0.001866189,-0.00081051147,0.04262229,-0.02382867,0.015866265,0.017778805,0.011241044,-0.017964203,-0.039675422,-0.041919727,-0.0021345299,0.013358497,0.024023827,-0.008445419,-0.053629145,0.0031347096,0.039285105,-0.009065043,-0.002510207,-0.0022223506,-0.0037640908,0.012421744,0.048320875,0.0020015792,-0.015310068,-0.032747347,0.025409443,0.008450299,0.011182496,-0.01620779,-0.041841663,0.009601725,-0.023067558,0.040475566,-0.002820019,0.013417045,0.018266696,0.01692987,0.0002229059,-0.018959504,-0.017895898,0.051365327,-0.04851603,-0.055580717,-0.0017368974,0.022579666,0.023984797,-0.009382173,0.016490767,-0.0012032649,-0.022345478,-0.0029712655,0.039421715,-0.003422566,-0.015300309,0.009616362,-0.027458591,-0.018315485,-0.002169902,-0.046018023,0.005069203,0.017642194,-0.0010428702,-0.03159592,-0.02029633,0.04418355,0.004581311,-0.02310659,0.015153942,0.026482806,0.04149038,-0.038816728,0.012558354,0.056673598,0.009099196,0.030698197,-0.018042266,-0.029410161,-0.01793493,0.020706158,0.030795777,0.033332817,-0.026521837,-0.015319825,-0.021369692,0.017046966,-0.019213207,0.018110571,0.008962586,-0.005620522,-0.01843258,0.0065475176,0.009265079,0.039285105,0.031088512,0.0035786917,-0.012714479,-0.014002516,-0.013651233,0.066119194,0.021994196,0.036201626,0.021818554,-0.011309349,-0.023009012,-0.00028145302,0.009548057,-0.009709061,0.014246462,-0.027263435,0.021779522,-0.030834807,-0.004112934,0.026619416,-0.0142367035,-0.020452455,-0.029039362,-0.021623397,-0.0026882878,-0.022404024,0.0049277144,0.031264152,0.040202346,0.011972883,-0.004608145,-0.007567213,0.021818554,-0.015905296,-0.040553626,-0.047462184,0.013114551,0.013807358,-0.025253316,-0.009318748,0.033469427,0.041334257,-0.0049960194,0.008557635,-0.017222606,0.004339804,0.016685924,-0.017769046,0.046915747,0.0036104047,-0.019135145,-0.0055131856,-0.0061572036,0.032513157,0.0038714272,0.005937652,-0.020218266,0.015963843,0.020081656,0.0038787455,0.02396528,0.036748067,0.02782939,0.03104948,0.019398607,0.039929125,0.02919549,0.010323806,-0.02437511,-0.020940347,0.00028023327,0.008059985,0.038094647,0.014412345,0.012890121,0.029156458,0.01920345,-0.0071183518,0.020062141,0.00016634086,0.011065402,-0.012733995,0.01448065,-0.00758185,-0.018452095,0.0011678927,-0.079428904,-0.019096114,-0.03104948,-0.004666692,-0.044847082,0.009435842,0.006454818,0.01665665,0.038641088,-0.05323883,0.024199469,0.006391392,0.010762909,0.03403538,-0.003690907,0.030717714,-0.015534498,0.032337517,-0.04539352,0.0038153196,0.019135145,-0.004317849,0.022735791,-0.02060858,0.00503993,-0.0051862975,0.00018646642,0.010060344,-0.014275735,-0.004486172,-0.009011375,0.007640397,0.038348354,-0.005225329,0.012372955,-0.019418122,-0.007142747,0.012929152,0.032337517,-0.011972883,0.029995633,-0.025077676,0.010587268,0.035128262,-0.016285853,0.0020052383,0.014763628,-0.014705081,-0.0316935,-0.012958425,0.0075281817,-0.016695682,0.013085278,-0.0057668895,-0.025311865,-0.024960581,0.018559432,0.012792542,0.01679326,-0.008347841,0.016510284,0.016402947,-0.03700177,0.01738849,0.0110751605,-0.018910713,-0.011582568,0.011709421,0.04004622,-0.0070207734,-0.005557096,-0.01721285,0.009357778,-0.0013099915,0.0051423875,0.008874765,-0.03614308,-0.011963124,-0.021760007,0.01643222,-0.0059571676,0.022852886,-0.018149601,0.03501117,0.00839663,0.008835734,0.029097911,0.027868422,-0.038153194,0.020179234,-0.010958066,-0.036260173,0.012236345,0.024902035,-0.036709033,-0.025799757,0.020081656,0.0123436805,-0.0053668176,-0.01184603,-0.0040348712,-0.02433608,-0.021584366,0.013631717,0.0046471762,-0.002778548,-0.021311145,0.026404744,0.040670723,-0.00417636,0.0072793565,-0.026892636,0.006137688,0.026346197,-0.024179954,-0.032532673,-0.00563028,-0.016002875,0.010733635,0.03019079,0.0019479109,-0.01198264,-0.002810261,0.009552936,0.014256219,-0.013387771,0.014822175,-0.04867216,-0.007176899,0.03304008,-0.011211771,0.037470147,-0.0208818,-0.011572811,-0.031634953,-0.03916801,-0.027068278,-0.045003206,0.006596307,0.014870964,-0.016461493,-0.04843797,-0.007103715,0.054956213,0.005883984,0.021447755,0.0023235881,0.008542998,0.00082453835,-0.009913976,0.02447269,-0.011231286,-0.020725675,-0.028356314,0.0081136525,-0.021096474,-0.008918676,-0.025038645,-0.015915055,-0.014451377,-0.01779832,0.039792515,-0.029976116,0.029117426,-0.02060858,-0.015690623,-0.028005032,-0.0045008087,-0.022033226,0.01007986,-0.031537373,0.018861925,0.0034737948,-0.016012633,-0.04004622,-0.027848905,-0.005669311,0.019896258,0.019593764,-0.027204888,0.010470173,0.051014043,-0.0038616695,-0.022618698,0.01774953,0.034523275,-0.024589783,-0.022169836,-0.019144902,0.0062499032,-0.0028322162,0.005542459,-0.018803379,0.025487505,-0.012860847,0.015895538,-0.013563412,-0.00703541,-0.023809155,0.0006940271,-0.0054643964,0.03559664,0.049023442,-0.01730067,0.0022943146,-0.015622319,0.0031517858,0.0009202873,0.010606783,0.03183011,0.017329942,0.032708313,-0.01525152,0.010509205,-0.004939912,0.01579796,0.014139125,-0.0042056334,-0.015690623,0.008494209,-0.020862285,0.026931668,-0.00043208982,0.021252599,-0.0036396782,-0.012899878,0.007313509,-0.036611456,0.011524022,0.0123436805,0.007254962,-0.034698915,0.01579796,-0.02937113,0.0042519835,-0.022150321,0.008777186,0.019105872,0.017232364,-0.06518244,0.012909636,-0.049140535,0.022599181,0.023711577,0.055892967,-0.009426083,-0.014851448,-0.02283337,0.020511001,-0.03186914,0.01692987,-0.026404744,0.022618698,-0.038816728,-0.0053863334,0.0374116,-0.04738412,-0.027848905,-0.042271007,0.0115435375,-0.015358857,-0.026033945,0.04293454,0.014461135,0.036357753,0.0014551395,-0.0028932027,-0.04348098,-0.00030645748,-0.01742752,-0.029800477,-0.023223685,0.012890121,0.0027883057,0.0004662423,-0.014275735,-0.028356314,0.008118532,0.032981534,0.013719538,-0.016949387,-0.013202372,0.03358652,0.0011313008,0.04535449,0.011328865,-0.010284775,-0.018608222,0.01915466,-0.029976116,-0.005278997,-0.019593764,-0.0032444852,0.0064353026,0.024394626,-0.01874483,0.016061421,0.007191536,0.01244126,-0.010265259,-0.032259453,-0.008723519,0.013153583,-0.006001078,-0.028629534,-0.0028248976,-0.00921629,0.02447269,0.019623037,0.00063487014,-0.008845491,0.029976116,-0.0015100273,-0.00021269065,-0.004276378,-0.0512092,0.016734714,-0.011524022,0.017085996,0.0065767914,0.029624835,0.0068890424,0.034211025,0.020511001,-0.04703284,0.0041104946,-0.027614716,-0.0043641985,-0.004108055,-0.010665331,0.0032786378,-0.010909277,-0.020062141,-0.019496186,-0.0038153196,0.005615643,-0.015427162,0.006659733,-0.047540247,-0.024492204,-0.0066938857,-0.0022869962,0.01692987,-0.021076957,0.009972523,0.01489048,0.00622063,0.0009019913,0.011016613,0.023731092,0.02587782,0.02351642,0.0033518216,-0.0032396063,0.008884523,0.030893356,0.02101841,-0.025507022,-0.002079642,0.044573862,0.009826155,-0.003927535,0.008889402,0.021681944,-0.0022211308,-0.049608912,0.0038372746,-0.0028127003,0.016178517,0.031537373,0.0081819575,-0.011836273,-0.030990934,0.003068844,-0.014012273,0.04426161,1.749552e-05,0.0064304234,0.023067558,0.05035051,-0.034952622,-0.014100094,-0.042778417,-0.0036835885,-0.01216804,-0.003295714,-0.009104075,0.0018149602,-0.0246093,-0.017466553,0.030171273,0.007484271,0.012197313,0.011953367,0.04059266,0.02351642,-0.00567419,0.034328118,0.03655291,0.005532701,-0.0028224583,-0.020315845,0.02683409,-0.031127544,-0.005308271,0.047149934,-0.0049423515,-0.02433608,-0.01942788,-0.0026882878,-0.0015649153,0.017125027,-0.04086588,-0.008874765,0.0025077676,0.014383072,-0.029097911,0.023594482,-0.0020357317,0.011172739,0.0005327177,0.016627377,-0.056322314,-0.007176899,0.0028248976,-0.023672545,0.012929152,-0.033430398,0.016539557,0.020550033,0.015817476,-0.021369692,0.005542459,-0.019720616,0.0010727537,0.018042266,0.018315485,-0.022891918,-0.016461493,0.007303751,-0.0067768274,0.0052643605,0.027497623,0.0063182083,0.015417404,0.022852886,0.019086355,-0.0041617234,0.015036847,0.0049228356,0.0008891841,-0.016695682,-0.028805174,-0.010928793,0.023145622,0.01956449,0.018735074,0.050155353,-0.011026371,-0.031166574,-0.003010297,0.019418122,-0.02310659,0.014402587,-0.015778445,-0.03214236,0.010928793,-0.0015990677,-0.02146727,0.013202372]
2	15	ja	朝食の時間は何時ですか？	朝食は毎日午前7時から午前10時までご用意しております。お好きな時間にお越しいただき、ぜひお楽しみください。ご不明な点がございましたら、お気軽にお尋ねください。	2025-12-05 12:49:20.530065+00	2025-12-05 12:49:20.530065+00	[0.009092536,-0.027449474,-0.0010659791,-0.017039297,0.008347783,0.03285098,0.03149242,0.04180439,0.01757945,-0.03951284,-0.01648278,0.0063017574,0.02676201,-0.013430109,-0.007705331,0.033063766,0.0027703182,-0.0074434397,0.046649374,0.078501895,0.008626042,0.0040797745,-0.0052296403,-0.0136183435,-0.01874159,0.037614126,0.023275582,0.023782996,0.010917591,-0.0526074,-0.03394765,-0.011776921,-0.021851549,-0.001953954,0.017710393,-0.006850092,0.015958996,0.0025473014,-0.07365691,-0.026336437,-0.04095324,0.01985463,0.0380397,-0.044914346,-0.051003315,-0.026009072,-0.040724088,0.00260459,-0.021671498,0.020427516,0.005200996,-0.025239768,-0.006899197,-0.02530524,0.08053155,-0.011760553,-0.014354913,0.070383266,0.0052214563,0.084852755,0.01901985,0.02484693,-0.036468353,0.051036052,-0.027940521,-0.010639331,-0.02147508,0.011212219,-0.036697507,0.013904788,-0.05833627,-0.01820144,0.004873632,-0.0140193645,0.03294919,0.02995381,-0.004044992,-0.006817356,0.037908755,-0.012169758,-0.0045871884,-0.012439833,-0.04949744,0.061577175,0.014043917,-0.0038444814,-0.037908755,0.02039478,0.015836235,-0.021786077,0.026369173,-0.009092536,0.005516084,-0.01584442,0.0021790168,-0.022408068,-0.010622963,0.046878528,0.045863703,0.045732755,0.037286762,-0.036730245,-0.039185476,0.043015633,-0.032065306,-0.039905675,-0.012718093,0.027433107,-0.04393225,0.021998864,-0.01560708,0.021704236,-0.07876378,0.011588687,0.011326795,0.021262294,0.005855724,-0.026270963,0.020067416,-0.007537557,-0.01069662,0.0067232386,-0.035715416,0.024961507,-0.08033513,-0.032703668,-0.014477674,0.023930311,-0.052312773,0.035453524,0.004443967,-0.051756255,0.059351098,-0.022686327,0.034995217,-0.007885382,-0.0039406447,0.028529776,-0.07686508,-0.0003296658,0.066225745,0.034733325,-0.01428944,-0.02648375,0.0019365628,0.011105825,-0.027875047,-0.037843283,-0.04887545,0.053654965,0.009092536,-0.04039672,-0.019707315,-0.011948788,0.009288955,0.06769888,-0.04059314,-0.045078028,-0.02093493,0.08675147,0.010917591,-0.005180536,-0.021687867,-0.018168705,-0.012898143,-0.0070792474,-0.054866213,0.01574621,-0.0231119,-0.0062199165,0.023422897,0.023897575,0.007852645,0.028513407,0.016269993,0.021164084,-0.0027089373,-0.0266638,0.0259436,0.03813791,-0.0037012596,0.018823432,-0.034438696,-0.008847013,0.039840203,-0.013356453,-0.06612753,0.0063631386,0.04841714,-0.0116459755,0.0009478212,-0.018463332,0.029888336,-0.037352238,0.0035027952,-0.026090914,-0.010082812,0.0062894817,0.01055749,-0.0037524102,-0.016973825,0.014461306,0.015484319,-0.03203257,0.02941366,0.03758139,-0.006952394,-0.0026025441,0.03961105,0.023422897,0.027318528,0.005331942,0.041346077,-0.0053278496,-0.034176804,0.019985573,0.020492988,-0.018250545,-0.028955348,-0.032098044,-0.022555381,-0.0065309126,0.03967652,0.007979498,0.046452958,-0.026467383,-0.016613726,0.0046772137,0.022506278,-0.0116132395,0.008879749,0.0072470214,-0.021736972,0.014796854,-0.017743131,-0.016810143,-0.04314658,-0.036632035,-0.025501657,-0.0048286193,0.0015764624,0.0072756656,-0.016122678,0.032736402,0.024012152,-0.0021728787,-0.0040879585,-0.06200275,-0.01802139,0.017055666,0.045536336,-0.007545741,0.017710393,-0.045470864,9.667469e-05,-0.018987114,0.01105672,-0.008478728,0.036566563,0.0064859,0.0048408955,0.0070506027,0.024159465,0.023422897,0.032605458,0.030985005,-0.0007232699,-0.0059416573,-0.02722032,-0.007697147,-0.017595816,-0.049824804,0.023619315,-0.0036378328,0.012677172,-0.029446395,-0.042099014,-0.013839315,0.019183533,-0.024503198,-0.078109056,-0.027367633,0.016597357,-0.05306571,0.03358755,0.022228017,0.09133457,0.0056347535,0.061511703,0.020345675,-0.02812057,-0.0045830966,0.049137343,-0.0042680087,0.012071549,-0.0376796,0.011506846,-0.035879098,-0.020312939,0.0029810588,0.06737152,0.0044153226,0.027875047,0.0077421595,0.02704027,-0.0014168725,0.012169758,0.032212622,-0.021344135,0.0019723682,-0.0054874397,-0.0021319583,0.012398913,-0.004836804,0.009591767,-0.050086696,0.004333481,0.0522473,0.0049800253,-0.0061544436,0.058761843,0.0061994563,-0.013176402,0.073395014,-0.01642549,-0.007795356,-0.006404059,-0.0607915,-0.028971717,-0.024323147,0.010647515,-0.082495734,0.0016490964,-0.018938009,-0.032376304,0.029691918,0.023439264,-0.012955432,0.021409608,0.03486427,-0.012742645,-0.040298514,-0.028038729,-0.025010612,-0.037384972,0.007062879,0.015852604,-0.015443399,0.00071866636,0.037614126,0.013143666,-0.0029053558,-0.021196822,-0.047565993,0.045012556,-0.022719065,-0.006264929,-0.05070869,-0.04023304,0.011744184,0.0129718,-0.04969386,0.0074393474,-0.01800502,0.010426545,-0.0035068872,-0.019510897,-0.03121416,-0.045536336,-0.04150976,-0.0060603265,0.0061462596,-0.025665341,-0.005184628,-0.02656559,0.032900084,-0.029970177,0.029086294,0.010009156,0.07411522,-0.013004536,-0.028840771,0.0056061093,-0.0110158,0.0526074,-0.019690946,-0.011531398,0.0021728787,0.085049175,-0.02995381,-0.020591198,0.027711365,0.07143083,-0.009960051,-0.02821878,0.030068386,0.03506069,0.013757474,-0.05087237,-0.07503184,0.06462166,0.035191633,-0.030101122,0.00860149,0.007566201,0.005761607,-0.017595816,0.016163599,-0.04285195,0.03265456,0.017170243,-0.015672553,-0.0032409038,0.00042480597,0.00778308,0.019560002,0.013773842,-0.008094076,0.00068541843,-0.04288469,-0.015582528,-0.056372087,-0.014191231,0.03748318,-0.0016071527,-0.0040961425,0.034078594,-0.039087266,-0.021098612,-0.025076086,0.060726028,-0.06544007,0.015672553,0.009534477,-0.0054096906,-0.029708287,-0.014837774,-0.05561915,0.013225507,0.03568268,-0.04324479,0.029020822,0.008576938,-0.0070055905,-0.044488773,0.01642549,0.011318612,0.06580017,0.043113843,-0.020181993,0.06200275,-0.00040306698,0.0255835,-0.005704318,0.008986142,0.025632603,-0.04661664,-0.02139324,0.022228017,-0.03496248,-0.0094199,-0.019494528,-0.004149339,0.017874077,-0.007660318,0.027400369,-0.017153876,-0.0034230002,0.026876587,0.03633741,-0.049071867,0.05070869,0.022506278,-0.025239768,-0.06291937,0.014551331,0.025665341,-0.0007079247,0.008912486,0.027007533,0.008196377,-0.016761038,0.03486427,-0.010303783,0.01766129,0.009575398,0.039840203,0.041215133,0.012660804,0.018528804,-0.005917105,0.002447046,-0.037745073,0.004939105,0.026140017,0.07025232,-0.008388704,-0.018168705,-0.00048286194,0.019527264,-0.018381491,-0.029282713,0.007840369,-0.010950327,0.0053728623,0.011097641,-0.016114494,-0.027056638,0.052280035,0.015206059,-0.016351834,0.02502698,-0.012979984,0.018381491,-0.0063631386,0.021131348,-0.0032409038,-0.008945222,-0.037810545,0.030428488,-0.029249977,0.0060316822,0.008634226,-0.016302729,0.014125758,0.009575398,0.023373792,-0.029249977,-0.013757474,-0.010721172,0.025518026,-0.027351266,-0.051658046,-0.0065554646,0.025616236,-0.007128352,0.005127339,0.025141558,0.033391133,-0.020492988,0.0026148201,-0.017939549,-0.037941493,-0.007791264,-0.006395875,-0.0050659585,-0.015811684,0.007848552,-0.028627984,-0.0518872,0.0046526613,0.020100152,0.005106879,0.021655131,0.00973908,0.017710393,-0.01985463,-0.037876017,0.021655131,-0.009837289,-0.033112872,0.010017339,-0.042721007,-0.00033222334,-0.015819866,-0.023242846,-0.01496872,-0.004881816,-0.018381491,-0.018905273,-0.019150795,0.03506069,0.018152336,-0.030772218,0.031901624,0.0070997076,0.042000804,0.035551734,-0.030101122,-0.01009918,0.0050373143,0.0101237325,0.0044275983,-0.013421926,-0.030903164,0.015435214,0.042099014,0.036075518,-0.019429056,0.025648972,0.016122678,-0.0075948457,0.02466688,0.0067641595,0.009501741,-0.009976419,-0.062133692,0.026254596,-0.022064336,-0.02648375,0.012857222,0.013135482,0.027171215,-0.021917023,-0.0054587955,-0.042491853,-0.025288872,0.01279175,0.009027063,-0.023046428,0.03059217,0.036468353,0.003803561,0.023733892,-0.017644921,0.018888906,0.0028582972,-0.010614779,-0.053458545,0.009763632,0.009542662,0.034602378,0.017415766,-0.009256218,-0.007930393,-0.039152738,-0.04033125,-0.022637224,-0.0067846198,-0.014903247,0.0033084229,0.0032327198,0.001535542,0.0037912847,0.009714528,0.006498176,0.017694026,-0.03365302,-0.012022444,0.0047385944,0.040429458,0.025812654,0.018725222,-0.04524171,0.009960051,0.03394765,-0.0005148311,0.018185072,-0.045569073,-0.00060204294,0.0263037,-0.024601407,0.024977876,-0.058139853,0.008065431,0.029462762,-0.008642411,-0.0019785063,0.010164653,0.003079268,-0.005115063,-0.069401175,0.017874077,0.015394294,0.012906327,0.01546795,-0.0015150816,0.0035212093,-0.011343163,0.01910169,-0.0014311946,0.029249977,0.01187513,-0.02175334,0.0071160756,-0.010663884,0.01856154,-0.0061298916,0.02484693,0.009125273,-0.019036219,0.023472002,0.020869456,0.019527264,0.054407902,-0.004595373,0.030444855,-0.01187513,0.022604486,-0.010164653,-0.019068955,0.006727331,0.003723766,-0.046452958,0.062657475,0.009665423,0.021196822,0.059842147,0.02494514,0.074704476,-0.037646864,-0.026696537,-0.00087262975,-0.0068623684,0.008069524,0.04069135,0.022293491,0.021917023,0.019281741,0.00053861615,-0.008855197,0.003887448,0.0034393684,-0.009043432,0.002273134,0.022719065,-0.028447935,-0.0034966571,-0.021180453,-0.013143666,0.045863703,0.011163114,-0.048024304,0.018135967,-0.014575884,-0.003981565,0.047926094,0.0045258077,-0.009747264,0.027269425,0.008016326,0.014158495,0.0065104524,0.0038547115,-0.011457741,0.0004235272,-0.037188556,0.020984035,-0.017824972,-0.032736402,0.033014663,0.016711934,-0.012636252,-0.016310913,0.0024981967,-0.0165237,0.031459685,-0.003154971,-0.06269021,0.0522473,0.041542497,-0.004317113,-0.024437726,-0.0046690297,0.0097227115,-0.02903719,0.023799365,0.019772789,0.0048122513,-0.019379951,0.010721172,0.011228587,-0.0067027784,0.01087667,-0.017350294,0.034897007,-0.016073573,0.012881774,-0.009149825,0.0023017784,-0.027138479,-0.027089374,0.013209139,0.01974005,0.023946678,-0.00016841345,-0.029659182,0.035977308,-0.034013122,-0.013659264,-0.007361599,-0.012668988,-0.00423118,-0.01865975,0.009804552,0.0035437157,0.0062976656,0.005364678,-0.02530524,0.013127298,0.028071465,0.0033779875,-0.015271532,0.0048490795,0.017595816,-0.027269425,0.0155416075,-0.00910072,0.0011007616,0.03601004,-0.031967096,0.0077503435,-0.016777407,-0.0037667325,-0.0029605986,0.03394765,-0.029102663,-0.00034322072,0.027531315,0.036173727,-0.0069319336,0.02375026,-0.01428944,-0.011965156,0.01756308,-0.007799448,0.0101401005,0.00066649274,0.021917023,0.030019281,0.03961105,0.009329875,0.026189122,-0.0050618662,0.018790696,-0.017333925,0.0013350315,0.0047590546,-0.01911806,-0.026892954,0.011916051,-0.0053155734,-0.022522645,0.01746487,0.005835264,0.021442344,-0.026778378,-0.021998864,-0.017072035,0.042328168,-0.008503281,0.011506846,-0.000262147,-0.0067150546,-0.041837122,0.03849801,-0.037352238,0.00059743936,0.002684385,0.0006751883,-0.023193741,0.024617774,0.028153308,0.007774896,-0.0060603265,0.020984035,0.023995783,-0.006408151,0.018332386,-0.008732435,-0.011269507,0.006391783,0.015386109,0.029004453,-0.033096503,0.022915483,0.0019273558,-0.02494514,-0.012668988,-0.027744101,0.0050946027,-0.025157927,0.009215297,0.0009841381,0.031836152,0.02676201,-0.030723115,0.009035247,-0.012922695,-0.0003680288,0.023095533,-0.02429041,0.016188152,0.04167344,0.032065306,-0.008765172,-0.008863381,0.016859248,0.020427516,0.004443967,0.006408151,0.017153876,0.016540067,0.0026946152,0.045372654,0.012889959,0.0120469965,-0.03404586,-0.013192771,0.009649055,-0.045078028,0.040920503,-0.016392754,-0.004959565,0.018365122,0.0014373327,0.02212981,0.0054096906,0.031050479,-0.0056470297,-0.032228988,0.008405072,0.0026230044,-0.01757945,0.034242276,0.037941493,-0.020722143,-0.0016675106,-0.024224939,0.041018713,0.02029657,0.017170243,-0.032147147,0.026401909,-0.017317558,-0.007873105,-0.0013953892,0.012865406,-0.0039406447,-0.0015324729,0.03483153,-0.0034700588,-0.022047969,-0.029544605,0.027171215,-0.03303103,-0.0017094541,-0.02766226,0.012120653,-0.0019948746,0.025878128,-0.03951284,-0.05879458,-0.025878128,-0.045863703,0.008200469,-0.019445423,0.0015713474,-0.011637791,-0.008396887,0.03712308,0.047042213,0.006383599,-0.04740231,-0.002833745,0.022522645,0.003406632,0.020280201,-0.051756255,0.016351834,-0.0018076632,0.0054015066,0.013135482,-0.014485858,0.01975642,0.009018879,-0.0031140503,0.019870996,0.033456605,0.016646462,0.002931954,0.041477025,-0.044390563,0.033325657,0.0026598328,-0.016294545,0.027907783,-0.035617206,0.0023652052,-0.0040838663,0.023602948,0.040920503,-0.0036173726,-0.028644353,-0.034111332,-0.02530524,0.018414227,0.021425975,-0.010778461,0.005597925,0.02722032,-0.017513976,-0.00043401308,0.029691918,-0.0060398662,0.00846236,-0.0050782347,-0.017350294,0.03167247,-0.036075518,-0.03378397,-0.036075518,-0.033080135,0.010000971,-0.007541649,0.005769791,-0.012267967,0.003318653,-0.051265206,-0.030330278,0.029479131,-0.028251516,-0.007950854,0.03584636,0.01584442,-0.004595373,0.051036052,0.0075089126,-0.0050864187,0.024715984,0.0013994812,0.0018700671,-0.0010097134,0.04023304,0.008024511,-0.017350294,0.040985975,0.020149257,0.0030465315,0.008470545,-0.0040122555,0.0011028076,-0.008159549,0.022309858,0.004554452,0.018168705,0.0015478181,0.014755934,-0.011261323,-0.00038797752,-0.014862327,-0.039250948,-0.009771816,-0.0058761844,-0.003811745,0.02893898,-0.0047508706,0.004967749,-0.02366842,0.0063140336,-0.011997892,-0.071758196,0.04141155,-0.01247257,0.025861759,0.0075702933,0.011776921,-0.0073370463,0.04861356,-0.00075140275,0.023439264,-0.020181993,0.047827885,-0.022358963,0.01351195,-0.00923985,-0.017317558,0.0010997385,-0.03758139,-0.012857222,-0.0046567535,0.021655131,0.0010782552,0.022506278,0.017137507,0.007991774,0.009526294,-0.031230528,-0.0040204395,0.035518996,-0.011048536,0.013503767,0.023291951,-0.0042680087,-0.009223482,0.017628552,-0.048384406,0.013119114,0.00292377,-0.0266638,0.021818813,-0.014240336,-0.011752369,0.008609674,0.0020848997,-0.047009476,0.028366093,0.019592738,0.006731423,0.034275014,-0.023619315,-0.010017339,-0.0076112137,-0.0066209375,0.02211344,0.037712336,0.024224939,0.01947816,0.014584067,0.019412687,0.015230612,0.02047662,-0.005585649,0.0003166224,0.038105175,0.042360906,0.04959565,-0.0017790189,0.0061380756,-0.015386109,0.028808035,-0.0076112137,0.007054695,-0.002027611,0.0048245275,0.016106311,-0.024372252,0.00095753977,-0.014174863,-0.007398427,-0.0067641595,0.012709908,0.007455716,0.013520135,0.007418887,0.019641843,0.03348934,0.0022240295,0.023095533,-0.021687867,0.04497982,0.011367716,-0.028709825,0.02785868,-0.008756988,-0.020525726,-0.014354913,0.009804552,-0.03938189,0.0043457574,0.024797825,0.00518872,0.018316017,-0.017726762,-0.04733684,-0.014837774,-0.0043212054,0.022178913,-0.0041616154,-0.012325256,0.025419816,-0.009886394,-0.0060562347,0.0023897574,-0.011711448,-0.0037258118,0.00584754,-0.013724737,0.035649944,0.022800906,0.018414227,-0.0017964102,-0.027105741,-0.02839883,-0.014084837,0.009820921,-0.0071529043,-0.011850578,0.008204561,0.0074066115,-0.015197875,1.9437239e-05,-0.04733684,-0.011883315,0.012235231,0.006469532,-0.001864952,-0.00021854107,-0.008576938,-0.012104285,0.00987821,-0.009452636,0.013724737,-0.00928077,0.003903816,-0.027203951,0.014256704,0.041902598,0.007991774,0.005536544,-0.007733975,-0.009321691,-0.027875047,0.005900737,0.013102746,0.004632201,-0.0052050883,0.004771331,-0.03175431,-0.002031703,0.017743131,0.021736972,0.004202536,-0.031967096,-0.02676201,0.01648278,0.002359067,0.032981925,-0.0034966571,-0.012145205,-0.003895632,0.0255835,0.0076193977,-0.046813056,-0.023062795,-0.00013324739,-0.04743505,-0.012554411,0.017055666,0.0022219834,0.006162628,-0.0054587955,-0.017432135,-0.070383266,0.020820353,-0.023161005,0.018774327,-0.005041406,0.020132888,-0.0069933143,0.044194143,-0.01365108,-0.01183421,-0.023193741,-0.02466688,0.01632728,-0.029004453,0.0021585566,0.008544201,-0.002442954,0.025910864,0.020460252,-0.03131237,0.016728302,0.028775299,-0.03095227,-0.045830965,0.016687382,0.0011406591,0.006244469,0.014461306,-0.010721172,0.018512435,-0.011776921,-0.009027063,0.028382462,-0.0048327115,0.024339516,0.0075743855,0.003318653,-0.0056715817,0.005434243,-0.002181063,-0.023782996,0.012546226,0.0155416075,0.025419816,0.0030485776,0.018627014,-0.0074229795,-0.0047222264,0.04069135,0.011621423,0.00035089333,0.018348753,0.0052623767,0.0065268204,-0.050086696,0.024781458,0.009501741,-0.0259436,0.035355315,-0.011007615,-0.038792636,-0.00138209,0.03483153,0.018037759,0.032458145,0.0052337325,0.027384002,-0.02366842,0.019592738,-0.011686896,0.011981524,-0.019707315,0.0023426989,-0.007058787,0.014453122,-0.015181507,-0.038105175,0.0070178662,-0.011179482,-0.0024736444,-0.009051615,-0.027416738,0.009747264,0.03286735,0.006502268,0.0066945944,0.00085114647,-0.0270239,0.0026496027,-0.007705331,-0.01648278,0.0006255722,-0.023079164,0.010041892,-0.019772789,-0.0073370463,-0.007688963,0.038727164,0.04275374,-0.009984603,-0.042197224,-0.020280201,0.03748318,-0.00730431,-0.0054956237,-0.035879098,0.017186612,0.030117491,0.0041861674,0.01856154,0.037450444,0.0039304146,-0.017644921,0.039120004,-0.024552302,-0.00822093,-0.008977959,0.004460335,-0.034275014,0.018708855,-0.021442344,-0.013724737,-0.013757474,0.027645893,0.0077626198,0.0022178914,-0.041215133,0.011318612,0.011343163,-0.008896118,0.009780001,0.048220724,0.00044705652,0.021998864,0.0071733645,0.014068469,-0.003484381,-0.035486262,0.016736487,-0.005274653,-0.005413783,-0.014199415,-0.035748154,-0.022309858,0.018234177,0.027956888,0.028431566,0.012939064,-0.0006444979,-0.007705331,0.014273072,0.010827566,0.02103314,0.010958511,-0.030706747,0.011572318,-0.010860302,-0.018708855,-0.012988168,0.034536906,-0.013479214,0.0058229878,-0.03620646,0.010017339,-0.014575884,-0.016130863,0.011997892,-0.019232636,0.021900654,-0.0047222264,-0.021917023,-0.012570779,-0.0029401383,0.015418846,-0.021245927,0.003249088,-0.026270963,-0.008716067,0.018872537,-0.005675674,-0.0012634206,0.0010347773,0.007832184,-0.009272587,-0.0037810546,0.029626446,0.0028767115,0.0043539414,0.0031877072,0.00012710932,-0.021196822,-0.009346243,0.0029831047,0.045372654,0.012488938,0.034111332,0.010631147,0.022358963,-0.038792636,0.015337005,-6.560068e-05,0.038727164,-0.022522645,-0.032539986,0.018086864,0.01265262,0.021802444,-0.00014130362,-0.00973908,0.010860302,-0.012006076,0.0021258201,-0.020067416,-0.01792318,0.03722129,-0.012611699,-0.037352238,-0.0021278663,0.001219431,0.0044030463,-0.0031099583,-0.02957734,0.00846236,0.04867903,-0.01929811,0.030461224,-0.0056388453,-0.023357423,-0.0033657115,-0.026287332,-0.0024020337,-0.001948839,0.010213758,0.045012556,0.012660804,0.016891984,0.01632728,-0.044456035,0.052410983,0.012799934,-0.013847498,-0.047893357,0.0042761927,-0.03712308,-0.030215701,0.011899683,0.00010409153,0.006019406,0.031459685,0.044652455,0.00842144,0.018316017,-0.028038729,0.01073754,-0.01582805,-0.042262696,-0.015459767,-0.0001143856,-0.017333925,-0.015337005,-0.052018143,-0.013397373,-0.01474775,0.041084185,0.07359143,-0.016220888,0.008904302,-0.028840771,-0.017072035,-0.025665341,0.023439264,-0.015353373,0.0034352762,0.03213078,0.014526779,-0.04049493,0.0020337491,-0.0057738833,0.019870996,0.005859816,-0.019003483,0.007627582,0.004619925,-0.020951299,-0.005851632,-0.017432135,-0.026270963,-0.02265359,0.017726762,0.03849801,0.032278094,0.044848874,-0.010295599,-0.01985463,-0.01415031,0.024224939,0.006563649,0.028333357,0.018234177,-0.017153876,0.021409608,-0.004836804,-0.043572154]
3	7	en	アイロンは無料貸し出ししてますか？	アイロンはフロントで貸し出しています。スタッフにお尋ねください。	2025-12-04 00:51:40.800779+00	2025-12-14 00:53:30.629087+00	[0.0021289012,0.009982876,-0.025910916,-0.026258713,0.054430313,-0.036649164,-0.05543023,-0.0078471815,0.01948753,-0.05838651,0.0048773168,-0.003910005,0.027693378,0.002891067,0.041322693,-0.009602472,-0.052821748,0.020117912,-0.08155852,0.06221228,0.035823144,0.06477729,-0.0050811046,-0.038779423,-0.026932571,0.028606346,0.016879048,-0.059864648,0.00023928062,-0.013716265,0.017618118,-0.031584363,0.012270732,0.012216388,-0.014064062,0.021606922,0.012575055,-0.01843327,0.053908616,-0.03940981,0.007863484,-0.03962718,0.019128865,-0.015726969,-0.0081786765,0.027802065,0.0028068346,-0.005591932,0.016824706,0.029062832,-0.0026139158,-0.0042414996,-0.039083745,-0.085166916,0.0006555168,0.024519725,0.03588836,0.0064559914,0.033931997,0.0037714294,-0.015074849,-3.568406e-05,0.00998831,0.061647113,-0.024367563,0.047300465,-0.054256413,0.07816749,-0.034497168,-0.0033095109,0.023063324,-0.029454103,0.02161779,-0.05708227,-0.007173324,0.0077439295,0.044952832,-0.02047658,-0.028845457,0.04167049,-0.005765831,0.03219301,-0.048691653,0.03219301,-0.0003668177,-0.016944261,-0.05921253,0.037062176,-0.0015881849,-0.01998749,-0.028258549,0.0053229323,0.00013314123,-0.027889013,0.018215895,0.01794418,0.006026679,0.017357271,-0.0023571434,0.027802065,0.0299758,-0.03236691,0.02441104,-0.0028231377,-0.0087384125,0.039822817,-0.021606922,-0.013053276,-0.015172667,0.014911819,-0.06308178,-0.013379336,0.017042078,0.0044317013,0.023280697,0.0218569,-0.022259042,0.03136699,-0.015487859,-0.048865553,0.002793249,0.057343118,0.043670326,0.029671477,-0.004328449,0.029519316,-0.02767164,0.0032035413,-0.011390369,-0.016226929,0.023628494,-0.037714295,-0.017400745,0.008754716,0.0021913962,0.046735294,-0.00096051896,-0.048083007,-0.028106388,-0.024845786,0.020574398,0.0055973665,-0.04332253,-0.026758673,-0.05495201,0.017357271,-0.012194651,0.007499384,0.015542202,0.020270074,0.011477319,-0.052778274,-0.058169138,-0.07073332,-0.010673037,0.036497004,-0.016433433,0.012455499,0.013661922,0.047300465,-0.0076461113,0.02710647,-0.054691162,0.019911408,-0.020183126,-0.007999343,0.028780246,-0.022074275,0.0059505985,0.03258428,-0.0015080284,0.046474446,-0.015031374,0.050517593,0.044431135,-0.008662332,0.031584363,0.036497004,0.047648262,0.02530227,-0.03825773,-0.005472377,0.021106962,0.015487859,-0.029932324,-0.07182019,-0.03734476,0.007923262,-0.046387494,0.054039042,0.006961385,0.038192514,-0.012944589,0.024345826,-0.009819846,0.008113464,-0.029758425,-0.037866455,-0.038953323,0.029410629,0.046735294,-0.0014292304,0.020172257,0.037844718,0.034671064,0.011988146,0.009472048,-0.013466286,0.03236691,-0.029128043,0.031823475,-0.022009062,-0.01612911,0.0053039123,-0.022237305,-0.014770526,0.03178,0.024845786,-0.023541545,0.063038304,-0.0071298494,0.008711241,0.00087628677,0.01941145,0.029280204,0.05003937,0.03301903,0.004475176,0.036975224,-0.051169712,-0.020835245,0.01768333,-0.031453937,-0.018781066,0.015411778,0.01833545,-0.04143138,-0.027802065,-0.0017308361,-0.050082844,0.0041300957,-0.035236236,0.03186695,0.00080835755,0.02488926,-0.044409398,0.036583953,0.01060239,0.06077762,0.0014645536,0.011770773,-0.022074275,-0.0010501855,-0.052604377,0.017585512,-0.014618365,-0.0100861285,-0.0014278719,0.025280533,-0.031649575,0.06342957,-0.030149698,-0.03269297,-0.002328613,-0.0038882676,0.011825116,0.03430153,0.054343365,0.0069505163,0.015585677,-0.037844718,0.0091948975,0.026389137,-0.013466286,-0.00778197,-0.027780328,-0.012966326,0.022476416,0.0110806115,0.011194733,0.0034345007,0.004312146,-0.0017974067,-0.07425477,0.00937423,0.004896337,-0.025041422,0.00019767399,0.010053522,0.066342376,-0.0021356943,-0.008667766,-0.0010610542,-0.021824295,0.02031355,-0.006510335,0.033497248,-0.0027823802,0.0029589962,0.010461098,0.05338692,0.04275736,0.020574398,-0.02111783,-0.030823557,-0.005749528,-0.02169387,0.050474115,0.03447543,-0.013281518,-0.006461426,0.04595275,-0.0037822982,-0.008472131,0.023715444,0.034258056,0.02964974,-0.017226847,0.06725535,-0.040735785,0.060255922,0.027084732,-0.0069233445,-0.011509924,-0.012292469,-0.03554056,0.057821337,-0.011357763,0.017835492,0.03710565,-0.0016914372,-0.01849848,0.029106306,-0.05412599,0.019998359,0.06251661,-0.0067766174,-0.01092845,0.005458791,-0.05682142,0.003342117,-0.0070048594,-0.041366167,-0.004219762,-0.011086046,-0.031475674,0.026519561,0.0127815595,0.00087696605,0.033214662,0.026563035,0.042626936,-0.004602883,-0.022030799,0.03904027,0.0193245,0.03586662,-0.0229329,-0.04608317,0.01645517,-0.044952832,0.013064144,-0.03577967,-0.044126812,-0.020780902,-0.0022797042,0.038127303,0.044496346,0.03488844,-0.022172092,0.040018454,0.020943932,0.020672215,-0.0122816,0.022824213,0.009640513,0.026606511,-0.0025636482,0.05873431,-0.05329997,0.017009472,0.021356942,-0.025345745,0.02488926,0.039757606,-0.019617954,-0.0042605195,-0.007934131,0.045213677,-0.016944261,0.032714706,-0.023302434,-0.011499056,-0.031649575,0.012835902,0.010624127,0.01392277,0.040931422,-0.04421376,-0.006651628,-0.023476332,0.0036817628,-0.0044833273,0.026476087,-0.0033692885,0.016911656,-0.017237715,0.0247371,-0.042322613,-0.019270157,0.06569026,-0.031910423,0.041300956,0.070298575,-0.028388973,-0.03167131,0.028236812,-0.0060049416,-0.011912066,0.020433106,0.017292058,-0.007836313,0.041496594,-0.030845294,-0.0065538096,-0.005608235,0.006673365,-0.0067277085,-0.023476332,-0.0736896,0.046822242,-0.013564103,-0.047648262,0.019041914,-0.04486588,-0.0039779344,0.061212365,0.035257973,-0.0020052702,-0.037562132,0.018357188,-0.008542777,-0.023758918,0.0054044477,-0.014292304,-0.0073635257,-0.002116674,0.08216716,-0.05747354,0.017476825,0.013172831,-0.014270567,-0.011368631,0.030258385,-0.007314617,0.014009719,4.0545245e-05,0.046648342,-0.028388973,-0.0067222742,-0.009156857,-0.005154468,-0.006363608,0.007118981,0.040800996,0.002054179,-0.035323188,0.053604294,0.0068092234,0.042322613,-0.034910176,0.019509267,-0.020367892,-0.0099611385,-0.009428574,-0.061038464,0.022237305,-0.026084814,-0.044822406,-0.05477811,-0.03456238,0.02194385,-0.018639773,-0.023563283,0.013987982,0.10381756,0.016748624,0.018205026,-0.04290952,-0.04299647,0.01670515,0.019096257,0.03495365,-0.00736896,-0.00491264,0.036953487,-0.005994073,-0.028562872,-0.032214746,-0.034823228,-0.0019903257,-0.044735458,-0.022954637,-0.008314535,-0.102774166,0.014922688,0.010906713,-0.0017743108,0.018357188,-0.012846771,-0.009428574,0.021737345,-0.014433597,-0.03391026,-0.03373636,0.0059179924,0.016639939,-0.003890985,-0.01874846,-0.00810803,0.005901689,-0.028541135,0.04560495,-0.042192187,0.0060810223,0.005586498,-0.045474526,0.004488762,0.00015428421,0.021106962,0.021519972,-0.021324337,-0.012227257,0.045822322,0.011901197,-0.013107619,0.018944096,-0.01997662,0.027693378,-0.00827106,-0.03193216,0.010319805,0.01793331,-0.0016941543,-0.04325732,-0.017042078,-0.020520054,0.0035785106,-0.009107947,0.02482405,0.038279466,0.04512673,-0.008216716,-0.019041914,0.03193216,0.0024902846,0.016618202,-0.030171435,0.04299647,0.0041463985,-0.046952665,0.031497415,-0.010923016,0.010548047,0.016031293,-0.0034834095,0.007885222,-0.033062503,-0.049517673,-0.028432447,-0.012977195,0.07377655,-0.018455006,0.032888602,0.0034345007,-0.008966655,-0.008075424,-0.012890246,0.027954226,-0.0121185705,-0.0011391727,-0.031736523,0.003964348,0.05551718,0.018237634,0.004184439,0.008809059,0.014031457,-0.028041176,-0.02645435,0.0046789637,0.0071950615,0.0030894203,-0.0055022654,-0.023389384,-0.0045648427,0.02743253,0.05169141,0.027780328,0.034345005,0.0039154394,-0.03660569,0.0010569785,0.03334509,-0.0021737346,0.006803789,-0.0036545913,-0.035236236,-0.003007905,0.014629234,0.014096669,-0.016683413,-0.015466121,0.005722356,-0.019367974,0.053604294,-0.027823802,0.049082927,-0.023802394,-0.015292223,-0.015346566,0.03380157,0.026584774,0.014890081,-0.0023992595,-0.027367318,0.036453526,-0.027236894,-0.006075588,0.002093578,-0.012379418,-0.041474856,0.021313468,0.018574562,0.007950434,-0.0018300128,-0.025476169,-0.02243294,0.006830961,0.0039235908,-0.017389877,-0.04486588,-0.006651628,-0.010450229,0.035670985,0.039279383,0.01424883,0.025671804,-0.025128372,0.015900869,-0.0053908615,-0.027541216,0.008205848,-0.025019685,0.0043012775,0.01753117,-0.008890574,0.012542448,-0.014759658,-0.0015555788,-0.020172257,0.02325896,0.00055022654,0.013259781,-0.03178,-0.023737181,-0.005328367,0.04960462,0.0283455,0.007200496,-0.007173324,0.0368448,-0.01035241,-0.024302352,-0.013314124,-0.006738577,-0.004252368,-0.011901197,-0.024845786,0.016444301,-0.001388473,-0.020161388,-0.0017892553,-0.04273562,0.012944589,0.0033665714,0.0419096,-0.007086375,0.011901197,0.010162209,-0.0068581323,0.026063077,0.047474362,-0.04625707,0.0118685905,0.0052550035,-0.0029970366,-0.027149944,0.008292797,0.0152270105,0.0024440929,-0.04856123,0.012248994,-0.037736032,0.011977278,-0.009580735,-0.015531333,0.022498153,0.022998111,0.010004614,-0.01981359,-0.018031128,0.007086375,-0.0016479625,0.0027674357,0.017096423,0.028584609,0.025345745,0.010993662,-0.009428574,-0.014487941,0.031258304,0.03495365,-0.002344916,-0.0184224,-0.0025079462,0.006363608,0.00520066,-0.03314945,-0.00014086819,-0.0011235491,0.016194323,-0.023498071,-0.0018300128,0.01818329,0.00017347421,-0.028562872,0.028475923,-0.07034205,-0.04690919,0.027084732,0.0026438045,0.016444301,0.030823557,0.008553646,-0.0033964603,-0.0193245,0.060690667,-0.022954637,0.012194651,0.026497824,0.006026679,-0.03128004,-0.0052522863,0.050778437,-0.0070646373,0.010412188,-0.0022022647,-0.00026407477,-0.010634996,-0.0031600667,-0.02146563,0.011064309,0.03178,-0.009488352,0.013553235,-0.017009472,-0.024454514,-0.00021261841,-0.0066190218,0.015324828,-0.00552672,0.009977441,-0.011814247,-0.041561805,-0.0059505985,-0.020617872,0.006336436,-0.019802721,-0.039648917,0.035823144,-0.0047034184,-0.023976292,-0.04006193,-0.003937177,-0.021389548,-0.005173488,0.023476332,0.009602472,-0.00018867337,0.014227092,-0.062168807,0.00030720982,-0.05856041,-0.012738084,0.012314206,-0.03430153,0.031584363,-0.027628167,0.013466286,0.007499384,-0.012618529,-0.0007771101,0.0054696593,0.017465957,-0.0040349946,0.039605442,0.015542202,-0.014194487,-0.039279383,-0.0049207914,0.025758754,0.009167725,0.040409725,0.0060647195,0.017400745,0.01589,-0.030106224,-0.027802065,0.0023761636,0.012401155,-0.0075645964,-0.03436674,-0.0031627838,0.010993662,0.0113795,0.011477319,-0.0100861285,0.006483163,0.030475758,-0.017802887,0.026019603,0.044996306,-0.023780655,0.015009637,0.026563035,0.04938725,-0.036257893,0.0073580914,-0.0035594904,0.011944671,0.01260766,0.043779016,0.01359671,0.011662086,0.024389302,-0.0061951433,-0.0021370528,0.028280286,-0.01858543,0.00038108285,-0.011037137,-0.00017389876,-0.010096997,0.018074602,0.00782001,-0.033997208,0.011672954,-0.018346319,-0.0034372178,0.010591522,0.014400992,-0.015063981,-0.0095263915,0.008189545,0.037388235,0.0026682592,0.041322693,0.0020229318,-0.01383582,-0.01695513,0.03030186,-0.038649,0.00049690215,-0.044952832,0.031084403,-0.009232937,0.04030104,-0.0029535617,-0.004488762,0.0057169218,-0.023845868,-0.013140226,-0.010743683,0.01883541,-0.010776289,0.025976127,0.028302023,0.011651217,0.034040682,-0.0109773595,-0.0062060123,0.020335287,-0.030693132,0.012216388,0.0004918074,0.019454924,-0.010999097,0.003426349,0.025367482,-0.02071569,0.034605853,-0.009004695,-0.028671559,-0.03643179,0.019824458,0.007912394,-0.01359671,-0.003988803,0.023367647,0.02882372,-0.020009227,0.025432695,-0.04069231,0.013466286,0.0043556206,-0.0007540142,0.008439524,0.0029698648,0.033671148,-0.051604457,0.065559834,0.018531088,-0.0037198032,-0.040583625,-0.010569784,-0.03178,0.023693707,0.0014170032,0.020215731,-0.0049669836,0.0020473863,0.010015482,0.030584445,0.01052631,-0.0075048185,0.01564002,-0.01997662,-0.0366709,-0.013738003,-0.016335616,-0.012879377,-0.019628823,0.002188679,0.016835574,-0.04677877,0.004347469,0.0023544263,-0.024171928,-0.012585923,0.011303419,-0.0033339653,0.015987817,-0.022074275,0.00868407,0.03512755,0.033866785,0.0017688764,0.054647688,0.051604457,-0.028888931,0.006135366,0.00040893382,0.052387003,0.007146152,0.028519398,-0.023650233,0.029997537,0.008564514,0.03193216,-0.019346237,0.006570113,-0.040996633,-0.010961057,0.019291895,-0.0048881858,0.03169305,-0.01621606,0.032236483,0.05560413,0.012998933,0.007749364,-0.029214993,-0.0131837,-0.003602965,0.0017403462,0.004714287,0.017465957,-0.036453526,0.0064722947,-0.0071026776,0.05182183,0.04397465,0.037736032,-0.004776782,-0.019367974,0.00047788196,-0.0056462754,0.020509185,0.017911572,-0.0025011534,-0.04734394,-0.003149198,-0.04019235,0.00019699469,0.0016099222,0.011835985,-0.009814411,-0.009232937,0.03438848,0.015074849,0.0026111987,0.004458873,-0.046604868,0.004021409,0.012705479,-0.0005159223,-0.020900458,-0.0043719234,0.045344103,0.006238618,0.022867687,-0.03986629,-0.0061734063,0.016444301,0.0049561146,0.028867194,0.030323597,0.012085964,-0.0026573904,0.014096669,0.060690667,0.027019521,0.04030104,0.025367482,-0.0050321952,-0.006445123,-0.02482405,0.047865633,0.020411367,0.021704739,0.009711159,-0.003135612,0.016335616,0.042518247,0.023780655,0.026106551,-0.007689586,0.008211282,0.0076189395,0.01244463,-0.020672215,0.0006388742,0.019041914,-0.0050811046,0.011944671,0.010803461,-0.013607578,0.0014835738,0.007629808,-0.0019251136,3.128989e-05,0.0016751342,-0.023606757,-0.017215978,-0.027736852,-0.007428738,0.03749692,-0.023628494,-0.04338774,0.029497577,0.03527971,0.032866865,-0.004890903,0.022389466,-0.0013952658,0.038170777,-0.017542038,-0.006042982,-0.0016180737,0.008966655,-0.011194733,-0.0067548803,0.039779343,0.00888514,-0.015922606,0.035171025,0.018607168,0.001881639,-0.010759986,0.0021941133,-0.0022729111,0.0016737756,0.0037442578,-0.01399885,-0.031236565,0.031975634,0.012879377,-0.013270649,0.043865964,-0.008249323,-0.020302681,-0.023302434,-0.01416188,0.013944507,0.010553481,0.02415019,0.025671804,0.011835985,-0.03021491,0.02784554,-0.0017539321,-0.022976374,-0.020107044,0.004510499,9.713876e-05,0.049908943,-0.0026302189,0.008694938,0.020204863,0.002586744,0.040735785,0.010629562,-0.017498564,0.0046789637,0.025041422,-0.015346566,0.0070374655,0.0074559096,0.001453685,0.03732302,-0.017705068,-0.027041258,-0.01035241,0.03219301,-0.017487694,0.031975634,0.019911408,0.0080536865,0.008401484,-0.001365377,0.03136699,0.0009238372,0.02162866,-0.0045268023,0.031519152,0.010846935,0.058125664,0.00953726,0.04903945,-0.016096504,-0.026476087,0.0012757104,-0.0043175803,-0.025367482,0.021737345,-0.014846607,-0.014357517,-0.02604134,-0.008667766,0.010776289,-0.0061462345,-0.021498235,0.02956279,-0.0028475923,-0.024997948,0.017085554,0.010135037,0.002198189,-0.0038040355,0.020498317,0.00039670654,-0.0209548,0.010580653,-0.007189627,0.017313795,0.01556394,0.026171764,0.007428738,-0.0007010294,-0.01416188,0.00029498257,-0.006477729,-0.00018561655,-0.018455006,-0.017063817,-0.012162045,-0.03217127,0.00055837806,-0.057951763,-0.00018663549,-0.04160528,0.018813673,-0.013129356,-0.020628741,-0.0018612602,-0.040648837,0.03030186,0.0010929808,-0.010374148,-0.026432613,0.025171846,-0.007825444,-0.0050838217,0.039105486,-0.012911983,0.0051925085,0.001541993,-0.02832376,0.0489525,0.0034806924,0.04408334,0.023454595,-0.027889013,0.010042653,0.01833545,0.008385181,-0.004344752,0.010080694,-0.014716183,0.0020854266,0.0036083993,0.016194323,0.0074070003,0.02194385,0.022215568,-0.04143138,0.014542284,-0.014183618,0.009270978,-0.002593537,-0.002535118,-0.05373472,-0.01874846,-0.010781723,0.010531744,-0.024780573,-0.011303419,-0.01899844,-0.00041029238,0.008086292,-0.007385263,0.024910998,0.010450229,0.004627337,0.010787157,-0.0213026,0.019954883,-0.00446159,-0.008477565,-0.026584774,0.023411121,-0.009819846,0.03136699,-0.015976949,0.025367482,-0.017237715,0.009814411,-0.025106633,0.036649164,0.010145906,-0.021519972,-0.012585923,0.0012206878,-0.012075095,0.028562872,-0.004168136,0.031562626,-0.0056517096,-0.025019685,0.007993909,-0.0031165918,0.017009472,-0.0040947725,0.037562132,0.031062666,0.0048447107,-0.0033692885,0.010553481,0.0088471,-0.003230713,-0.015357435,0.0062603555,0.00042319894,0.013661922,0.036062256,-0.023867605,0.0014292304,-0.0279977,-0.015248748,-0.025997866,0.018954964,0.0149879,-0.022498153,-0.01612911,0.012825034,0.013618447,-0.008298231,0.009982876,-0.0069505163,0.042844307,-0.024606675,-0.022911161,0.0024128454,-0.012064227,-0.01645517,-0.027149944,-0.021802558,-0.03251907,-0.032453857,-0.025063159,0.01818329,-0.008765585,-0.01424883,0.03677959,0.00050980865,0.00868407,0.008607989,0.024128454,-0.016813837,0.009607906,-0.025737017,-0.010330673,-0.021259123,-0.017476825,-9.3997034e-05,-0.018194158,-0.028975882,0.01416188,-0.017389877,0.026171764,0.003456238,0.010265461,-0.0229329,-0.015466121,-0.0035893791,0.01556394,-0.016085636,-0.015466121,0.0036573084,-0.01923755,-0.016922524,-0.022009062,-0.010374148,0.015368303,-0.027280368,0.0033964603,0.0030568142,0.033931997,0.014281436,-0.012585923,-0.012705479,-0.002988885,0.003912722,0.024867523,0.012911983,0.013151094,0.010167643,-0.01703121,-0.0064722947,-0.025432695,0.018868016,-0.04717004,0.010488269,0.033627674,0.023324171,0.024519725,0.02391108,0.015259616,-0.038018618,-0.0017389876,-0.0026764106,-0.009368796,0.03838815,0.0017593664,-0.012064227,0.032453857,0.007113546,-0.046691816,-0.012640267,-0.0040920554,-0.02121565,0.02204167,0.005700619,0.00041334922,0.040496673,0.04256172,-0.0041762874,0.023345908,-0.027236894,0.010884976,0.0010175795,-0.009254674,0.017052947,-0.026476087,-0.018346319,0.019400582,0.03301903,0.00033149452,-0.039192434,0.0049017714,-0.014118406,-0.031149616,0.019378843,-0.023541545,-0.0026098401,-0.0019332651,0.0067005367,0.005956033,0.017237715,0.002256608,-0.02399803,0.022117749,-0.0013701321,-0.016074767,0.008732978,-0.001907452,-0.008732978,-0.010510007,0.029454103,-0.003573076,-0.009504654,-0.014227092,-0.012727216,0.0069016074,0.016531251,0.024237141,0.016607331,0.044409398,-0.023345908,-0.012270732,-0.019748379,0.034997128,0.038301203,0.023498071,0.009874189,0.00016922863,0.019389711,-0.016346484,0.014759658,0.0057766996,0.020520054,-0.01236855,-0.0034317835,-0.02055266,-0.010515441,-0.016716018,-0.0049289432,-0.05086539,0.035257973,-0.023867605,0.01794418,-0.018541956,-0.020052701,-0.0026261432,-0.005874518,-7.709965e-05,0.012455499,-0.038931586,-0.04612665,0.024432776,0.031714786,-0.024128454,0.013161963,0.012716347,0.014183618,0.014933556,-0.008211282,0.022802476,0.0044371355,0.010966491,0.0420835,-0.014683577,0.020998275,0.011575136,-0.014868344,0.01162948,0.0022498153,-0.034105893,0.004100207,-0.002188679,-0.011238208,-0.03128004,0.03438848,-0.018770197,-0.021422153,0.0067222742,0.004168136,-0.022259042,-0.03373636,0.015596545,0.008705807,-0.010412188,-0.01825937,0.004246934,-0.039431546,0.0014360234,-0.012944589,0.029106306,-0.020693952,0.009417705,0.0068744356,0.027910752,0.008265626,-0.0054044477,-0.0006195143,-0.012966326,0.04051841,0.00023333682,0.009428574,0.007086375,0.051387083,0.009309018,-0.00017814434,0.07090722,-0.008841665,-0.015748708,-0.02070482,-0.031214828,-0.011705561,-0.03506234,0.0045186505,0.00080767827,0.027128207,0.03643179,0.006396214,-0.029062832,0.009395967,-0.021889508,0.0245632,0.009129685,0.014031457,-0.027149944,-0.020683084,0.0018952248,0.034997128]
4	11	en	Do you have WiFi?	Yes, we have free WiFi. The password is in your room.	2025-12-04 08:55:33.21179+00	2025-12-04 08:55:33.21179+00	\N
5	12	en	Where is the nearest convenience store?	There is a convenience store about 5 minutes walk from here.	2025-12-04 08:55:33.21179+00	2025-12-04 08:55:33.21179+00	\N
6	13	en	I lost my room key.	Please contact the front desk. We will help you immediately.	2025-12-04 08:55:33.21179+00	2025-12-04 08:55:33.21179+00	\N
7	16	en	What time is breakfast?	Breakfast is served daily from 6:30 AM to 10:00 AM in our dining area.	2025-12-14 00:54:33.235579+00	2025-12-14 00:55:52.682119+00	[-0.013291283,-0.016546879,0.05239685,-0.011802736,-0.026928293,0.015067936,0.06365219,0.045520723,0.043676846,-0.025948733,0.010410224,0.016489258,-0.014443707,-0.0016217958,-0.008211017,0.080131836,-0.01755525,0.026659394,0.019360712,0.020916484,0.03497605,-0.031173052,-0.0411031,0.010218154,0.016594896,0.04456037,-0.02406644,-0.0059877997,0.0021535913,-0.040680546,-0.018477188,-0.027312433,-0.025161244,0.011303352,0.007942118,-0.024085648,0.018986175,-0.002085166,-0.02316371,0.03960495,-0.008667184,-0.0035509046,0.00968996,-0.040411647,-0.07287157,0.025756663,-0.014549345,-0.053587686,0.010554277,-0.0027177983,-0.00851833,0.007634805,-0.01399234,-0.055546805,0.07544532,0.036512613,0.03824125,0.024508204,0.025449349,0.040334817,0.02180001,-0.013973134,0.032901686,0.060194913,-0.014606967,0.0005918174,0.017958598,0.028215166,-0.012667053,-0.016806174,0.0031883714,0.009584321,0.01937992,-0.007716435,0.037280895,0.0015149566,0.0074811485,-0.015778597,0.0022784371,0.023259746,-0.0020515537,-0.03126909,-0.0223186,0.06987527,0.021761594,-0.02297164,-0.00036253317,0.044329885,0.00851833,0.004864187,0.021070141,0.0140883755,0.049938347,-0.028388029,-0.0082734395,-0.035533056,0.016786966,0.017804941,-0.028368821,0.03215261,-0.017017452,-0.046020105,-0.023106089,0.011476216,0.017497629,-0.060271744,0.0073082848,0.006285509,-0.038721424,-0.018275514,-0.034476668,-0.0044752443,-0.035456225,-0.014213221,0.019879304,0.007836479,0.0010041689,-0.027850231,0.014309257,-0.06580337,0.050975528,0.012542208,-0.038375698,-0.0022400229,-0.051398084,-0.023586266,-0.042178694,0.039720193,-0.07755809,0.016460447,0.019821681,-0.058812007,0.02471948,-0.011965996,0.0031187457,0.004153526,0.034265388,-0.0076252013,-0.075906284,-0.0009249398,0.02648653,0.056545574,0.023048468,-0.00944507,-0.022721948,-0.043100633,-0.0473646,-0.0069721616,-0.036839135,0.0440994,0.023663092,-0.03764583,-0.002308448,0.024892345,-0.016844587,0.040104333,-0.013108816,0.014520534,-0.019879304,0.06392109,-0.0070345844,0.021915251,-0.021896044,-0.03086574,-0.0359364,-0.033439483,-0.047326185,0.053357203,-0.050745044,0.0066456413,0.058082137,0.052358434,-0.021703973,0.031864505,-0.018803708,0.056391917,-0.057429098,0.0018006616,0.042754907,-0.03875984,-0.008374277,-0.0015125556,0.003438063,0.0002628966,0.062192447,0.032613583,-0.03693517,-0.027677368,-0.034572702,0.011111282,0.004801764,-0.0076588136,-0.012186877,-0.037357725,-0.0032411907,-0.013060798,0.015538508,0.01761287,0.0041991426,0.0037285697,-0.00062723045,0.01921666,0.041256756,-0.024296926,0.023106089,0.0059877997,0.025987146,0.016729346,0.010823176,0.008268638,0.0010954024,0.0055460376,0.008499122,-0.034687944,-0.025026795,-0.022395428,-0.008551942,0.0032531952,0.0045304643,-0.013569785,0.009113749,0.010803969,0.021454282,0.009795599,0.047556672,0.0058965664,-0.0050898697,-0.0019771263,0.025948733,-0.007245862,0.03295931,-0.01657569,0.014683794,0.005939782,-0.045443896,-0.029117897,-0.044060986,-0.010602295,0.011533837,-0.002705794,0.01445331,0.020878071,-0.044483542,0.081437916,-0.0004969826,-0.028234372,0.012052428,-0.008902471,-0.00028345414,0.0013324895,0.0204171,-0.01151463,0.030692875,-0.054624867,0.029386796,0.04932372,0.032229442,-0.008936083,0.031691644,-0.007874893,-0.0017382386,-0.038644597,0.013915512,0.03870222,0.02675543,-0.004535266,-0.0056180637,-0.018736484,-0.005190707,-0.0045856847,-0.06772408,-0.0050178436,-0.0019675228,0.011562648,0.04352319,-0.041371997,-0.043292705,-0.009257801,0.019178245,0.031211466,-0.0024969173,-0.032056578,0.019072607,-0.024873137,0.00043425953,-0.021588732,0.07705871,0.009113749,0.011610665,0.024296926,0.011120886,0.036128473,0.05958029,0.0014105182,0.012791899,-0.027715782,0.06964479,-0.010803969,0.03601323,6.981315e-05,-0.012609432,0.02406644,0.0011170104,-0.021415867,-0.012878331,0.01995613,-0.009713968,0.035917196,0.051628567,-0.013099212,-9.175871e-05,-0.004477645,-0.0045424686,-0.042716492,0.0018642849,0.025679834,0.015538508,-0.007817272,-0.047863983,0.0068713245,0.05247368,-0.001556972,-0.014837451,0.006083835,0.021742387,-0.04678839,0.06787774,0.015644148,-0.015183178,-0.080669634,0.040872615,-0.08159158,0.037031204,-0.0044752443,-0.02498838,0.015260006,0.024565825,-0.014789433,-0.021492695,-0.023394195,-0.02466186,-0.015010314,-0.05754434,-0.028925827,-0.0100164795,0.005680487,-0.03328583,0.02662098,0.013925116,0.021281417,-0.0029890982,0.009176171,-0.024028027,-0.0353794,0.009978065,0.011063265,0.06100161,-0.020321066,-0.030327942,0.012311723,0.00024293925,-0.03835649,0.014885468,0.023989614,0.02844565,-0.006112646,-0.047556672,0.010179739,-0.032344684,-0.020609172,-0.0107559515,-0.015087143,-0.0018054633,0.01311842,-0.015605733,0.038068384,-0.008100576,0.0085903555,0.043139048,0.013224058,0.021896044,0.011927582,0.03217182,0.011572251,0.07352461,-0.006655245,0.021896044,0.01203322,0.05247368,-0.060847953,-0.009829211,0.020858863,0.05427914,0.006376743,-0.032402303,0.010775158,-0.016258772,0.011581855,0.004069495,-0.018554017,0.00046457068,0.004158328,-0.014866262,0.0045880857,0.014923883,-0.018381152,-0.021358246,0.011370577,-0.050207246,-0.026966708,0.025238072,-0.033689175,0.01543287,0.008014144,0.009656347,0.04801764,-0.042831734,0.024834724,-0.025103623,-0.0023396595,-0.04828654,-0.0072794743,-0.029713316,0.06883809,-0.030039836,-0.012062031,0.0013348904,-0.031595606,-0.06810822,0.044137817,-0.005411588,0.0049170065,0.03895191,0.026505737,-0.03269041,0.0071546286,0.023605471,0.026371289,-0.0076540117,0.036301337,0.019581594,0.0055268304,-0.00813899,-0.0044872486,-0.052281607,0.02577587,0.035072085,0.0473646,0.04951579,-0.008441501,0.06357536,-0.013358507,-0.011207317,-0.0037861909,-0.03933605,-0.007346699,-0.028003888,-0.026121596,-0.00655921,-0.038663805,-0.03464953,-0.03342028,-0.023720715,-0.053280372,0.01331049,0.005848549,-0.013406525,0.033439483,-0.016037893,0.032575168,-0.059465047,0.024277719,0.02773499,0.034092523,-0.014520534,0.005757315,-0.01943754,-0.028426442,0.012244498,0.020609172,-0.0072218534,-0.012811107,0.010717537,-0.04248601,0.05312672,-0.029079484,0.005574848,0.01712309,0.019725647,-0.010957626,0.021377454,0.016556483,-0.012503793,-0.0025737456,-0.012369344,0.05696813,-0.028407237,-0.020186616,0.032728825,-0.0065015885,0.025718248,0.0147222085,0.044714026,0.019274281,0.035994023,-0.006876126,-0.04594328,-0.027907852,0.027197191,0.0032700014,-0.048901167,0.03053922,-0.023432609,0.008945687,-0.025122829,0.025718248,-0.011428199,-0.008599959,-0.039720193,0.04717253,-0.023144502,0.029982215,0.0020839656,-0.017459214,0.01807384,-0.013406525,0.012801503,-0.019744854,0.0031091422,0.029194726,0.04494451,-0.05381817,-0.04398416,0.032978516,0.009243396,-0.02180001,0.0049170065,0.029559659,0.012014014,-0.0253149,0.017670492,0.022606704,-0.01758406,0.0031979748,-0.0005257932,-0.027773403,0.0152504025,-0.014501328,-0.005142689,-0.0066072275,0.013905909,0.039950676,0.0028834592,-0.010928815,0.009137757,0.01859243,0.033900455,-0.05220478,0.031922128,-0.015932253,-0.021319833,0.011447405,-0.015711373,-0.0069673597,-0.0039038341,-0.03126909,0.015634544,-0.04840178,0.0070489896,0.015413662,-0.021166176,0.03914398,-0.010342999,0.03522574,0.062730245,-0.004520861,-0.018352343,0.066379584,-0.01399234,0.018870933,0.008575951,-0.029079484,0.059004076,-0.0064871833,-0.035513848,0.02610239,0.030942567,0.025084415,0.0029746927,0.054624867,0.004960222,-0.009661149,0.02251067,-0.0058053327,0.040065918,-0.014943089,-0.0036973583,0.023855165,-0.021281417,0.006957756,0.023336573,0.02283719,0.028560892,-0.002869054,-0.0052675353,0.0064199585,-0.006026214,0.0051618963,0.012887935,-0.021070141,0.0137138385,0.008076567,-0.00655921,0.0030707282,-0.014001944,0.01622036,-0.0049890326,-0.002520926,-0.040757373,0.000470873,0.040027507,-0.007932514,0.017209522,-0.016162738,-0.010285378,-0.031403538,-0.00069865666,-0.026524944,0.046365835,-0.03445746,-0.0091713695,0.0078941,0.036435787,-0.002430893,0.01717111,0.016508466,-0.0042087464,-0.0033684375,-0.04567438,-0.015538508,0.020032959,0.008849652,0.030289527,-0.024239305,-0.018966967,0.022664327,0.041371997,-0.01731516,-0.007711633,0.0017214324,0.01679657,-0.007841281,-0.020935692,-0.060771126,-0.0030011025,0.0034932834,-0.017795337,0.041756142,0.031345915,0.009978065,-0.011428199,-0.029790144,0.003622931,0.012993573,0.025238072,0.018025823,-0.002708195,0.0059974035,0.013396922,0.010506259,0.003980662,-0.022222564,0.028887413,-0.016316393,-0.022952432,-0.0042879754,0.006386346,0.016105117,0.035264157,0.02022503,-0.01622036,0.0039518517,0.0114954235,0.0069241435,0.036320545,0.008047757,0.02218415,-0.029674903,0.03874063,-0.008969695,0.015173574,0.041371997,0.004511257,0.0054644076,0.014779829,-0.020282652,-0.0016301989,0.037165653,0.016162738,-0.03589799,-0.015135161,-0.0054500024,-0.010784762,0.006391148,0.032056578,0.05016883,0.024585033,-0.026870672,-0.014635777,-0.029213933,-0.007327492,0.0046433057,-0.017488025,0.022683533,0.03987385,0.0033636356,-0.06284549,0.007072998,-0.028599307,-0.00067824917,0.0064391657,0.007922911,0.0052531296,0.006189474,-0.014741416,0.0049986364,0.049362134,-0.019101417,-0.03307455,0.036704686,-0.0070489896,0.012388552,0.021108555,0.011697098,-0.011687494,-0.00083070516,-0.02022503,0.009099343,-0.023471022,-0.022875603,0.020359479,-0.006434364,-0.02316371,-0.023567058,0.008912074,0.0006047222,0.018928554,0.017824149,-0.025257278,0.059004076,0.023067674,0.0015089543,-0.006112646,0.025871905,0.033958074,-0.030020628,0.06296073,0.03397728,-0.009891634,0.0020815646,0.013425732,0.008340664,0.016489258,0.004513658,-0.011216921,0.003663746,-0.00066564453,-0.012119653,0.019783268,-0.020724414,-0.02166556,-0.0016674126,0.0568913,-0.003378041,0.00699617,-0.013877098,-0.03705041,0.022549083,-0.01820829,-0.015029522,0.005594055,-0.010679123,0.016105117,0.0008120983,-0.008734409,-0.027293228,0.030116664,0.02708195,0.01706547,-0.009104145,0.024585033,-0.0026817853,-0.005469209,-0.018054632,0.0012856723,-0.05278099,0.024047235,0.021031726,0.0024681068,0.052742578,-0.029386796,-0.03860618,-0.026121596,-0.0062230863,0.0269475,-0.0031283493,-0.018544413,-0.007514761,0.047787156,0.0204171,0.0025737456,0.002525728,-0.020532344,0.0028858602,0.033746798,-0.008921677,0.015836218,-0.008974497,0.005305949,-0.008451105,0.03386204,-0.007284276,-0.004074297,-0.02218415,0.015077539,0.005512425,0.03831808,-0.008950489,0.01216767,-0.01793939,0.018294722,-0.014703002,-0.013733045,0.017728113,-0.015855424,-0.016806174,0.03486081,0.00018771896,-0.012974367,0.028945034,0.012580622,-0.0021007718,0.014424499,0.010323793,-0.026390495,0.036704686,0.025622213,-0.026697809,0.018045029,-0.0055076233,0.030808117,-0.0057044956,0.011034454,-0.014530138,0.010429432,0.013685027,0.014424499,0.034361422,0.006818505,-0.011005643,-0.0072362586,0.004429627,0.0036373362,0.017046262,0.0043816096,0.03574433,-0.008311854,0.00794692,0.018650051,-0.018563619,0.003971059,-0.037415344,-0.0009741579,0.018361947,0.028925827,0.0010149729,-0.020109788,-0.013502561,0.004619297,-0.0063383286,0.004237557,0.020628378,-0.0054836147,-0.004945817,-0.02153111,0.002520926,-0.010006877,-0.0058917645,-0.037434552,-0.005248328,0.0010461843,0.011226525,0.0353794,0.009411458,0.016383618,0.034803186,0.009373044,-0.03843332,-0.005718901,0.029194726,-0.04671156,0.035840366,-0.0669558,-0.006295113,0.026736222,0.009901238,-0.01186996,-0.008124584,0.03384283,-0.032920893,-0.027293228,-0.0089841,-0.012743882,-0.019120624,-0.0014477319,0.021070141,-0.034092523,-0.009041722,-0.019264678,-0.00083310605,0.030039836,0.011226525,-0.050284073,0.010035687,-0.009939652,0.000971757,-0.0062518967,0.017948994,-0.0065880204,-0.0005675085,-0.0094882855,0.03655103,0.0030227106,0.015711373,0.029828558,-0.040488474,-0.023759129,-0.008542338,-0.009252999,-0.02354785,0.020839656,-0.036685478,-0.022817982,-0.058043722,-0.039835434,-0.02577587,-0.019840889,0.0021932058,-0.005478813,-0.020455515,0.04529024,0.029041069,0.003975861,-0.042524423,0.017027056,0.029963007,-0.003053922,0.0021211794,-0.044521958,0.0042663673,0.011687494,0.034783978,0.003277204,0.023067674,0.03315138,-0.015336835,0.05043773,0.05377976,0.045328654,0.027197191,0.008782427,0.05289623,-0.01311842,-0.004969826,0.013723441,0.0008156997,0.020628378,-0.0013997143,0.003089935,0.02362468,-0.005656478,0.017142298,-0.010342999,0.0050994735,-0.020762827,-0.033266623,-0.012369344,0.04467561,0.016479654,0.02466186,-0.0039350456,-0.019687233,-0.020628378,0.08481836,0.013588992,0.009176171,0.024815517,0.020032959,0.032191027,-0.014097979,-0.024104856,-0.043292705,-0.023086881,0.014664588,0.001701025,-0.013108816,0.016162738,-0.02779261,-0.044790857,-0.017756924,0.016825382,-0.02420089,0.01589384,0.032267854,0.0012460578,-0.007956523,0.06488144,-0.010986436,-0.002031146,-0.0051714997,0.0056468747,0.012590226,0.01717111,0.009425863,-0.004175134,-0.022088114,0.07110452,0.07655933,0.021492695,-0.010150929,0.015413662,0.009569916,0.034303803,0.0449061,0.014069169,-0.029905386,-0.01935111,0.016393222,-0.019312695,0.0014717407,-0.002825838,0.005838945,0.027062742,-0.01200441,0.005776522,0.022587499,-0.033554725,0.00988203,0.0018654853,0.03244072,0.014184411,-0.04360002,0.032997724,0.003995068,-0.010544674,0.011985203,0.009800401,-0.021454282,-0.0068713245,-0.01976406,0.047518257,-0.007841281,0.021070141,-0.03073129,-0.012609432,-0.014760623,0.0010599894,-0.0013240865,-0.007822074,-0.0011110081,-0.011620269,0.0011056062,0.007673219,0.017728113,-0.02623684,0.013224058,0.002003536,-0.036474198,-0.025430143,0.014443707,-0.014395689,0.021127762,-0.008753615,-0.008158197,-0.011418595,0.00022298192,-0.033516314,-0.011601062,0.040219575,-0.03345869,0.014683794,0.027619747,-0.036301337,0.024623446,-0.010602295,-0.03693517,0.037223276,0.001483745,0.0051570944,0.01731516,-0.0050082398,-0.0033252216,-0.021742387,0.0019603202,-0.0023576661,-0.00566128,-0.0034548691,0.029943801,-0.016719742,0.013483354,0.008715202,0.031096224,-0.025276486,0.0038630192,0.015048728,-0.010496656,0.01820829,0.041410413,-0.027638953,0.0043816096,0.032018162,0.02133904,-0.00833106,0.036781512,-0.0061318525,0.00835507,-0.0068281083,-0.014962297,-0.020685999,-0.011937185,-0.0353794,-0.004357601,0.04079579,-0.027754197,0.027542919,-0.0030395167,0.014818244,-0.028810585,0.006823307,-0.0060358173,0.050898697,-0.031806886,-0.016047496,0.03680072,0.006799298,-0.0036157283,-0.019821681,0.050860286,-0.01565375,-0.025430143,-0.011505026,-0.00089492876,0.021723181,-0.052435264,-0.023125296,-0.04306222,-0.0070970072,0.018323531,-0.06192355,-0.019063003,0.017814545,-0.0040334817,0.0088016335,0.0022340207,0.014232429,0.002787424,-0.030500805,0.005776522,0.0083790785,0.038394906,-0.011466612,-0.03587878,0.00939225,-0.014501328,-0.038126007,0.028560892,-0.016566087,-0.029694108,-0.019130228,0.011802736,0.003802997,-0.003113944,-0.037991557,-0.0032507943,0.0076203994,0.019312695,0.0039350456,-0.014414895,-0.0023444614,-0.015308023,0.008508726,-0.024969174,-0.0040046712,-0.017833753,-0.0070393863,-0.039681777,-0.017411197,0.021723181,0.0010984035,-0.0036133274,-0.0075819856,-0.0036685478,-0.014875865,0.0025689437,0.0012352538,-0.011178507,0.015308023,0.007634805,0.0031907721,-0.011005643,-0.010448638,0.013128023,-0.018429171,-0.039047945,-0.009709167,-0.0074187256,0.03100019,0.05723703,-0.021703973,-0.023720715,-0.019658422,0.027696574,0.009464277,-0.026966708,0.0119179785,-0.0046505085,-0.032459926,-0.02316371,0.014011548,-0.0072890776,0.008215819,0.022433842,0.006650443,-0.051013943,0.01265745,-0.0016145932,-0.0029026663,-0.0070778,0.020032959,0.01347375,0.01066952,-0.007596391,0.021396661,-0.018640447,0.0064247604,0.03770345,-0.010410224,0.005397183,0.025161244,-0.029252347,0.0039782617,0.029406004,-0.024450583,0.011082471,-0.004674517,-0.032363888,-0.029924594,-0.009387448,0.020897277,-0.015980272,-0.033266623,-0.0025689437,-0.02354785,-0.023797542,0.0004921808,0.045904864,0.0021932058,0.02961728,-0.0022604305,0.037242483,-0.03772266,-0.012772692,-0.010794366,-0.011245731,0.03952812,-0.011418595,0.0037741866,-0.0046433057,-0.0044656405,0.012839917,-0.009872427,0.0064439676,-0.010506259,-0.0034932834,0.019504765,0.029367588,0.011889168,-0.005104275,0.032325476,0.015961064,-0.019879304,0.021223797,-0.02283719,-0.050745044,0.0130319875,0.023835957,-0.012868728,-0.03138433,0.021089347,0.00672247,0.0253149,-0.006122249,-0.0018930954,0.037857108,-0.015260006,0.033362657,0.003992667,0.016133927,-0.025218865,-0.038068384,0.004271169,-0.012619036,0.0026169615,0.015528905,0.0023204524,0.010592692,0.017132694,0.028618515,0.012503793,0.0020107387,-0.026256045,0.0095267,-0.014962297,-0.016229963,-0.007999739,-0.028925827,-0.0028954637,-0.004007072,0.014549345,0.021415867,0.022260979,0.054701697,0.001282071,0.024700275,-0.00037483772,0.03607085,-0.004477645,-0.004456037,-0.053971827,-0.0056084604,0.004398416,0.0020611573,-0.010535071,0.036051646,0.022068908,-0.007817272,0.035321776,0.008772823,-0.035475433,-0.0065063904,-0.011889168,-0.019466352,0.017516835,-0.002969891,0.025660627,0.029636487,0.018323531,0.020148203,-0.024585033,-0.008158197,-0.032210235,0.038471732,-0.0026409703,0.002027545,0.027370054,0.020801242,0.015423266,0.013166437,0.02850327,-0.0033444287,-0.01690221,0.00049308117,0.020685999,-0.000808497,-0.015740182,-0.033305034,-0.027638953,0.018947762,0.02452741,0.021223797,0.05354927,0.011360974,-0.011072868,-0.002300045,0.004705729,-0.007706831,0.027005121,-0.026198424,0.0065784166,-0.04913165,-0.06764725,-0.020148203,0.025161244,-0.026409702,0.024796309,-0.059196148,-0.00082950474,-0.011956393,-0.013348904,0.027907852,-0.013339301,-0.008455906,0.007970928,-0.020148203,0.003663746,0.0011656282,0.00025239273,-0.042447593,0.010198947,0.0024176883,-0.0034548691,0.030961774,0.0069913683,0.00094354665,-0.0042999797,0.011937185,0.009185774,-0.013060798,-0.011303352,0.0334779,0.014597363,-0.0187845,-0.0103333965,-0.04398416,-0.021742387,0.018582826,0.014424499,-0.013483354,0.006271104,0.0020707608,0.0004768752,-0.0058053327,-0.00045826836,0.009022514,-4.9143055e-05,-0.041794553,-0.03856777,0.010304586,0.031096224,-0.010736745,0.012119653,-0.00041175127,0.020666793,-0.006007007,0.007183439,-0.0067272712,-0.0008661182,0.005776522,-0.02329816,-0.032114197,-0.022721948,-0.016374016,-0.0019687233,-0.024047235,0.0073082848,-0.003358834,-0.033055343,-0.00010503859,0.023182917,-0.043830503,-0.0063239234,-0.008225421,-0.0059877997,0.0035268958,0.020052167,0.00075927895,0.045635965,-0.035129707,0.0025713446,-0.028925827,-0.020897277,-0.016095513,0.007341897,0.016431637,-0.02180001,-0.01764168,-0.03464953,-0.036128473,-0.02471948,-0.005032249,-0.023048468,0.030827325,0.0021944062,-0.018496396,-0.0047177332,-0.012993573,0.0061990772,-0.003889429,-0.0073370957,-0.0013060798,-0.04398416,-0.0027922257,0.0056084604,-0.037011996,-0.03476477,0.052435264,0.02452741,0.031499572,-0.0024032828,0.013905909,0.024604239,0.014770227,-0.016364412,0.005594055,-0.044829268,0.009478683,0.051666982,0.00922899,-0.03405411,-0.04352319,0.031672437,0.013809874,0.010083704,-0.028330408,0.011053661,0.0012652648,-0.018246703,0.00988203,-0.01976406,-0.021627145,-0.01761287,0.017814545,0.019668026,0.046634734,0.0114954235,-0.011562648,-0.015845822,-0.004880993,-0.0449061,-0.0051666982,0.045328654,0.018189082,0.017411197,0.021723181,0.020340273,-0.0075195627]
8	6	en	レンタルバイクはありますか？	予約が必要です。フロントで予約してください。	2025-12-04 00:17:22.309197+00	2025-12-05 08:52:49.89369+00	[-0.00159866,0.0024422568,-0.05370688,-0.025801158,0.016887112,-0.01880955,-0.055244833,0.014549829,0.02238124,-0.031831548,-0.0071636154,0.004656856,0.023453759,-0.017382897,-0.018445298,-0.007856705,-0.027480762,-0.013254712,-0.0037335793,0.05653995,0.0074570407,0.016846638,0.015723528,-0.029140132,-0.013204122,0.0076745795,0.03958201,-0.034826506,-0.0023423403,-0.020742107,0.022421712,-0.035251465,0.004436787,-0.026630843,0.0054435385,0.0042369547,0.04051288,0.0081501305,0.015703293,-0.005716727,-0.04970011,-0.06074908,0.040148627,0.018546479,-0.0017946982,0.0357169,-0.0057420223,-0.051845152,-0.02173368,-0.0029216018,-0.025922576,-0.041929413,-0.061922777,-0.05415208,-0.011109675,0.054637745,-0.01886014,0.02642848,0.05751129,0.023696592,-0.01039129,0.009126527,-0.020286793,0.062003724,-0.012161958,0.013285067,-0.016188962,0.04662421,-0.055568613,-0.029443674,-0.033227846,-0.02600352,-0.015855065,-0.028836587,-0.009632432,0.046543267,0.048404995,0.0031897314,0.013406484,0.024586987,-0.021834861,-0.0063592265,-0.012829753,-0.0004708079,-0.00894946,0.0026939444,-0.041524686,0.014590302,0.008008477,-0.0181114,0.030394776,0.022522893,-0.03031383,0.023514466,0.053747352,-5.383146e-05,-0.009293476,0.024222733,-0.0064755846,0.031973198,0.025275016,-0.03138635,-0.00021200583,-0.050428618,0.007340682,0.008210839,-0.020691518,0.035150282,-0.02903895,0.03814524,-0.04577429,-0.010072569,0.027237928,-0.00852956,0.009293476,0.011322156,0.012870225,-0.008347433,-0.046340905,-0.035676423,0.046907518,-0.004816216,0.01945711,-0.023453759,-0.008681331,0.0069865487,-0.02675226,-0.0062175733,0.007861764,-0.015652703,-0.011261446,-0.060830023,0.0205701,0.0036475754,-0.0077605834,0.00836767,0.0065868837,-0.017301952,-0.011514399,-0.024708403,0.024202498,-0.0016113076,0.011382864,0.004150951,-0.03931894,0.06022294,0.009339008,-0.012900579,0.021308722,-0.030597137,-0.010674597,-0.014256405,-0.055568613,-0.034381308,-0.043022167,-0.017706677,-0.028856825,-0.006683006,-0.004444376,0.018212583,-0.021268249,0.0047656256,0.012930933,-0.01166617,0.052249875,-0.030334067,0.0133154215,0.047555074,-0.021146832,-0.0016277495,0.036303747,0.012000068,-0.025942812,0.033430208,0.0140338065,0.0317506,0.052614126,-0.0068651317,0.05354499,0.021328958,-0.02169321,0.021814626,-0.030232886,0.020640926,-0.054840107,0.0021349194,-0.0039991797,0.019942777,0.0020565041,-0.008301902,-0.01945711,0.02312998,-0.016553214,0.053787827,-0.009829735,-0.028310448,-0.03181131,-0.042455554,0.008716744,-0.045288622,0.001529098,-0.002499171,-0.012809516,-0.0015619819,0.041686576,-0.0064351126,-0.032054145,-0.0007341947,0.04346736,-0.042010356,0.011079321,0.0064553483,0.000689928,0.012748808,0.008423319,-0.011362627,-0.013234477,0.0141147515,-0.035049103,0.018050693,-0.0479598,-0.032539815,-0.020529628,0.00591403,-0.014620656,0.0401891,0.052087985,0.04387209,-0.026893914,-0.036263276,-0.012313729,0.022421712,0.0010668273,-0.042981695,-0.026408244,0.01406416,-0.008489087,-0.0010857987,0.031649422,-0.029504383,0.00730021,-0.030678082,-0.004484848,-0.044722006,0.058684986,-0.05403066,-0.00017864772,-0.0296258,0.03363257,0.072283715,0.00932383,-0.0004199012,-0.033551622,-0.036526345,0.019811243,-0.0031669657,0.0007955357,-0.010988258,0.0020109727,-0.057956483,0.025355961,-0.006303577,-0.022745492,-0.021430138,-0.025983283,0.0006703242,0.039561775,-0.00932889,-0.0035565125,0.017079355,-0.031649422,-0.018748842,0.0029443675,0.012253021,-0.035089575,0.00064819085,0.031305406,-0.0054233023,0.045045786,-0.014145105,-0.0045759114,0.019851714,0.027622417,-0.046907518,0.014661129,0.02920084,0.04294122,0.0029342494,-0.0437102,0.045410037,0.032418396,0.017565023,-0.033065956,-0.041383035,0.054071132,0.0073760957,0.009546428,-0.04439823,-0.005686373,0.00932889,0.029504383,0.026772495,0.029909108,0.022907382,-0.030334067,0.06499868,-0.030839972,-0.0026281767,-0.00021532584,-0.035534773,0.006597002,0.073821664,-0.05386877,-0.0693697,0.008853339,-0.009935975,0.007841528,-0.042698387,0.059534907,-0.045005314,-0.002914013,-0.00761893,-0.0009346596,0.022138406,-0.030880446,-0.031305406,0.0105329435,-0.030172179,-0.018708369,-0.004965458,0.0042015417,-0.010644242,0.028735407,-0.0046290313,0.06856025,0.027581943,0.009829735,0.01732219,0.016563332,-0.03523123,0.03158871,0.035352647,-0.03755839,0.0105329435,-0.02153132,-0.006688065,0.0019135859,-0.0065514706,-0.0069511356,-0.01641156,-0.025052419,-0.03395635,0.003371857,0.03154824,7.4818614e-05,0.002957015,0.06564624,0.008903929,-0.064593956,0.0005618708,-0.004454494,0.014762309,-0.037214376,-0.007942709,-0.032175563,0.0437102,0.027379582,0.0033162076,-0.044681534,-0.0032099676,0.05702562,-0.011959596,-0.011069203,0.0048389817,0.0090253465,-0.02574045,0.048404995,0.019841596,0.041807994,-0.013325539,0.0128398705,-0.0533831,-0.0058583803,-0.0047833323,0.011281683,-0.01784833,-0.0024498452,0.023190688,0.013699909,-0.021490848,-0.021814626,-0.03478603,0.011817942,-0.036000203,0.012657745,0.00077656424,0.04310311,0.055123415,-0.06989584,-0.00841826,-0.04759555,0.009956212,-0.0039840024,0.02600352,0.031447057,0.0038904098,-0.00841826,-0.0028431865,-0.028978242,-6.6755754e-05,0.023959663,-0.026792731,0.0020059135,0.02675226,0.017443607,0.029362729,-0.0029190723,-0.03846902,-0.0026560016,-0.020367738,0.016006837,-0.002482729,-0.038489256,0.0045582047,-0.058361206,-0.029504383,-0.0026838263,0.024647694,-0.020843288,-0.013042232,-0.029909108,-0.040958073,-0.012485737,0.01998325,-0.08147095,0.027905723,0.014428413,0.029706744,-0.03719414,-0.016148489,0.016138371,-0.017281717,0.0022361004,0.05941349,-3.1085496e-05,0.014165342,0.052452236,0.08483016,-0.011575107,0.011170384,-0.03745721,0.038125005,-0.009779145,-0.034866977,0.0067588915,0.04698846,-0.014124869,0.010937667,-0.021065887,0.02456675,-0.016684748,0.01502538,0.018607188,0.026023757,0.051359482,-0.012293493,-0.009763967,0.0072496193,-0.017089473,-0.0035716898,-0.055082943,0.024890529,0.00420913,-0.045248147,0.005691432,0.021915806,-0.014580184,-0.010522826,-0.09251992,-0.0069511356,-0.011514399,0.026468953,-0.01220243,0.0331469,-0.0141956955,0.095352985,0.06046577,0.039339177,-0.15217625,-0.0205701,0.025538087,0.007836469,-0.010371054,-0.00468974,-0.027581943,0.04407445,0.025113126,-0.039035633,-0.017170418,0.0009846177,-0.022907382,-0.062084667,-0.011322156,-0.07155521,-0.013730263,0.033936113,0.03846902,-0.029443674,-0.020236202,0.039298706,-0.027116511,-0.0034401545,0.0011806559,0.035777606,-0.011656052,0.014833136,0.011382864,0.02525478,-0.027521236,-0.0007854176,0.0035463944,0.0025029653,0.04597665,-0.036668,0.014468885,0.029140132,-0.016178844,-0.06730561,-0.0020236203,-0.04715035,0.001747902,0.008296843,-0.01182806,0.018334,-0.0026408243,-0.010644242,0.024242971,0.040047444,-0.009126527,0.003650105,-0.01262739,0.014731956,-0.018101282,0.0022019518,-0.04225319,0.004983165,-0.008408142,-0.0011578902,0.0029089542,0.002860893,0.049376335,0.033126663,-0.04759555,0.021490848,-0.013446957,-0.035635952,0.06536293,-0.044843424,0.027541472,-0.018293526,-0.024931,0.004054829,0.0016808696,0.01726148,-0.005888735,0.017332308,-0.012495855,-0.034725323,-0.014367703,-0.06471538,-0.008408142,0.02296809,0.012212548,0.03142682,-0.004054829,0.010715069,-0.00068613375,-0.028108085,0.010027038,-0.00026923633,0.008170366,-0.013436838,0.009435129,0.039096344,0.01220243,0.0015215095,0.05305932,-0.0133154215,-0.06835789,0.006303577,0.02988887,-0.028533045,0.009794322,0.019922541,-0.008807807,0.010462116,0.011706643,0.044802953,0.016644277,-0.0003220402,0.0034325658,-0.01593601,0.021187304,0.014185578,0.0069814897,-0.00490222,0.027642652,-0.008747098,0.009121468,0.016077662,0.039784376,-0.00024109537,0.023959663,-0.018283408,0.004373549,0.00030591447,-0.055973336,-0.017969748,-0.04460059,-0.005119759,0.01812152,0.023312105,-0.010360936,0.017038882,0.007623989,-0.033753984,0.049012084,-0.051966567,0.007684698,0.018900612,-0.013497547,-0.02652966,0.050873812,-0.014043924,-0.029565092,-0.012374437,-0.017150182,0.004707447,-0.015450341,-0.011595344,-0.022361003,-0.03842855,0.0040270044,-0.04379114,0.011392982,-0.014134987,0.005575074,0.03602044,0.011645935,0.011949478,0.005509306,0.013204122,0.020327264,0.0064502894,8.695243e-05,0.012505973,0.026610605,-0.01076566,0.022745492,-0.016806167,0.0038372898,0.0467861,-0.029868634,0.016816285,-0.016947819,0.013032114,0.00083221385,0.016067544,0.0063592265,-0.0117268795,0.0031644362,0.024384623,-0.015551521,-0.04290075,-0.010148455,0.030880446,0.03446225,-0.005377771,-0.01433735,0.0043937853,0.0032681467,0.0034123296,0.011413218,-0.017332308,0.019487463,-0.009602078,0.04006768,0.02157179,0.005231058,0.019123212,-0.0129208155,-0.033774223,0.008210839,-0.007027021,0.035372883,-0.0006867661,-0.029686509,-0.0307995,0.002888718,0.009096173,0.0013988275,-0.014731956,0.0073760957,-0.018475654,0.042657916,-0.011362627,-0.014954554,0.016715104,0.016421678,-0.017878685,0.005236117,-0.018091165,0.02744029,0.010553179,0.017828094,0.031730365,0.0017909039,0.04101878,0.023210924,0.02025644,-0.018081047,0.025173835,0.0073558595,0.014731956,-0.010371054,0.014529593,0.053625938,0.045490984,-0.007907296,-0.0070118443,0.012708335,-0.019882068,0.026408244,0.014630774,0.031689893,0.015976481,-0.021005178,-0.0051450543,-0.039602246,-0.03794288,-0.017989984,0.029140132,0.036162093,0.009799381,-0.0025548206,-0.004183835,0.011909005,0.06313695,-0.07220277,-0.0050286963,0.016168725,0.00404977,-0.012556563,-0.027136747,0.0034603905,-0.022401476,-0.007310328,-0.023352578,-0.035150282,-0.03826666,0.025052419,-0.03027336,-0.001769403,-0.01849589,-7.900814e-05,-0.033551622,-0.019477345,-0.016087782,-0.034442015,-0.010021979,-0.017939392,-0.037173904,-0.012394674,-0.020903997,0.032782648,-0.004333077,-0.032175563,0.020236202,-0.010522826,-0.016947819,-0.0067588915,0.012000068,-0.00087837764,-0.014408176,-0.038813036,-0.0033364438,-0.02019573,-0.02019573,-0.011767352,-0.0017200772,-0.010052334,-0.044843424,0.007978123,-0.034077764,0.0055497787,0.0135582555,-0.00548907,0.026388008,-0.023028798,-0.0074368045,0.009480661,-0.008038831,0.0018263173,-0.021086123,0.005994975,-0.024364388,-0.021551555,0.0133154215,0.024162026,-0.0112513285,0.0025168776,0.013811208,-0.0024662872,0.0008543472,0.0041003604,0.03948083,-0.012748808,-0.0074469224,0.016866874,-0.009652669,0.045855235,-0.028087849,0.001353296,0.011362627,0.014570066,-0.019730298,-0.0024422568,0.013983216,-0.018839905,-0.001396298,-0.0019338221,0.012182194,0.03569666,-0.023049034,0.015419986,0.042172246,0.036647763,-0.01641156,0.018334,0.0032377923,0.004252132,-0.0028280092,0.0095818415,-0.026408244,-0.015197388,0.021005178,-0.027581943,-0.030718556,0.029281784,-0.023210924,-0.009040523,0.022340767,0.035838313,0.0009814558,0.0012672922,0.035352647,-0.0117268795,0.019902306,0.005494129,-0.013952862,-0.0018098754,-0.0038802917,0.0055700145,0.002691415,0.004646738,-0.0076594027,0.011696525,0.0074975127,-0.012556563,-0.0411402,-0.029140132,-0.04273886,-0.015764002,0.024040608,-0.013416602,-0.007588576,0.007816233,0.008327197,-0.029342493,-0.050590504,-0.009197354,0.0047985096,-0.0010478558,0.031305406,0.024202498,-0.0073305643,-0.0056560184,0.024020372,0.025436906,0.02744029,-0.002243689,0.035656188,0.019113094,-0.023777537,0.0034350953,-0.013527901,-0.020104667,0.05467822,0.011868533,0.0019755592,0.020489154,0.05520436,-0.017989984,0.058644515,0.005463775,-0.0105329435,-0.028573519,0.0050008716,0.030738791,0.028006904,0.010193987,-0.015764002,0.055406723,0.022664547,0.018748842,-0.0114031,-0.017656086,0.035332408,0.0076442254,0.018748842,-0.0071787927,0.025619032,-0.009080996,0.00991068,-0.008559913,0.00095932244,-0.05973727,0.008241193,0.010543061,0.0083069615,-0.0068600727,0.011372746,0.02371683,-0.02642848,0.026792731,-0.008266489,0.015733648,-0.019254746,0.0025118187,0.0029443675,0.015035498,0.00319732,0.04362925,-0.03458367,-0.025436906,-0.058604043,0.048647832,-0.0032327333,0.0012653951,-0.006910663,0.030091234,-0.018293526,0.027379582,0.0076442254,-0.00078605,0.030617375,0.0037436974,0.01785845,0.012222666,0.054394912,-0.044883896,0.053585462,0.03318737,-0.024627458,0.020903997,-0.006824659,-0.012799398,-0.014023689,-0.03367304,-0.009151823,0.0052462355,0.0016188961,-0.038327366,0.023737065,-0.011868533,0.010072569,0.04775744,0.0005318327,0.021409903,0.018516125,0.00436849,0.0037816402,-0.02306927,-0.006688065,-0.0129208155,0.049781058,0.05131901,0.017544787,0.008129895,0.013821326,0.0050312257,0.048485942,-0.0066678287,-0.0011749645,-0.014246287,0.031952962,-0.028249739,-0.03994626,0.03915705,0.020924233,-0.0020274145,-0.048324052,0.0002875754,0.030354304,-0.049781058,0.03126493,0.0057470812,-0.00175802,-0.015055735,0.009946094,-0.0040143565,0.022988325,-0.008129895,0.018981557,-0.02685344,-0.004502555,0.040148627,-0.063905925,-0.009116409,0.0065615885,-0.019649353,0.0074317455,-0.032640994,0.0076088123,0.010897195,-0.007224324,0.021612264,-0.0017175477,-0.0065464117,0.0035641012,-0.015824711,0.0004812422,-0.03731556,0.03138635,0.010704951,-0.052654598,-0.038711853,0.0148129,-0.017595379,0.017888803,0.025821393,0.0041256556,0.022077696,0.015298569,0.017291835,0.009809499,0.01539975,0.03286359,-0.006971372,-0.015561639,0.001529098,-0.048769247,-0.042374607,0.00335668,-0.0074671586,0.026893914,-0.031851783,0.025679741,-0.010735305,0.022907382,0.0032327333,-0.014519475,0.025558323,-0.006404758,0.00580779,0.02306927,-0.031993438,0.010543061,-0.008645917,0.006111333,0.0053878888,-0.01880955,0.019285101,-0.004517732,-0.006597002,-0.006000034,0.024263207,-0.0026256472,0.0039106463,0.0025029653,-0.03047572,0.01667463,-0.013821326,0.055932865,0.029221077,-0.019305337,0.015369396,0.029281784,-0.0035995145,0.017342426,0.006096156,-0.00937948,-0.016128253,0.028634226,0.02387872,-0.03347068,0.04071524,0.018202463,-0.0024232853,0.030759027,0.01955829,0.0045253206,0.028593754,-0.004773214,0.027905723,-0.0038549965,0.030657846,0.0090557,0.019578526,0.0020375326,0.021349194,0.013274949,0.0118887685,0.0055649555,0.017888803,-0.0010510178,2.8654778e-05,0.002946897,-0.01513668,-0.014023689,-0.019649353,-0.025295252,0.0056256643,-0.0009125263,0.041686576,0.0042875456,-0.0071838517,0.014286759,0.034826506,0.010876959,0.03612162,-0.008190603,-0.061963253,0.018253054,0.034806266,0.009597019,0.034199182,0.032317214,0.027136747,-0.016421678,-0.006374404,0.044843424,-0.033592097,-0.025173835,0.0073457416,0.01380109,0.02355494,0.04277933,-0.0022930147,0.01193936,0.013811208,-0.00065830897,-0.003814524,0.021328958,0.015976481,0.032944538,0.027723597,-0.007021962,-0.020802816,0.011484045,-0.0073255054,-0.00858015,-0.021065887,-0.005084346,-0.032094616,-0.009986565,0.021328958,0.024465568,-0.028735407,-0.041322324,0.012941051,-0.008382847,-0.000860671,-0.0072749145,0.00035824403,-0.022361003,0.03415871,0.036303747,0.0070624347,-0.026367772,-0.004034593,-0.026711786,0.0068398365,-0.0004369755,-0.0012944846,0.021652736,0.012354202,0.0076695206,0.027399817,0.0040371222,0.008822984,0.009480661,0.009293476,-0.0103811715,-0.03591926,0.0018844963,-0.0069865487,0.062408447,0.018232819,-0.020043958,-0.0097386725,-0.0239799,-0.012020304,-0.006809482,0.0027723596,0.007507631,0.0029544856,0.007188911,-0.017625732,0.037639335,-0.017342426,0.018930968,0.005661078,-0.019194039,0.0016049838,-0.024263207,0.01102873,0.031952962,-0.028310448,-0.025335725,-0.006293459,0.02812832,-0.013355893,-0.007902237,-0.008812866,-0.008797689,-0.041383035,0.03836784,-0.026772495,0.025355961,0.0020476507,0.016876992,0.003414859,-0.0046290313,-0.012748808,0.014782546,0.021268249,0.03794288,0.034077764,-0.0131636495,0.010846605,0.0048465705,0.007770702,-0.030657846,0.007851646,0.023939427,-0.009713377,0.01785845,-0.013629083,-0.011220974,0.019780887,0.0041205967,0.031608947,0.009758908,0.016330615,0.0005182365,-0.022158641,0.00070257566,-0.050266728,0.012870225,-0.032114852,0.018536361,-0.008934284,-0.025113126,-0.028148558,0.03638469,0.013851681,0.032620758,0.0022196583,0.008656035,-0.011747115,-0.015976481,-0.0053271805,0.0065868837,0.015156915,0.015885418,-0.0034224477,0.025517851,-0.00986009,0.0014949495,0.008640858,0.007199029,0.015662821,-0.0029696627,0.029382966,0.014205814,-0.07701898,0.009824676,-0.016371088,0.03931894,-0.015885418,-0.000111299116,-0.0228062,-0.030759027,0.017716795,-0.024445333,0.01571341,-0.020246321,-0.03037454,0.0012894255,0.005605428,0.007027021,0.03820595,0.016128253,0.020377856,0.0045910883,-0.010846605,-0.045490984,-0.025133364,-0.008134954,0.014934317,0.032175563,-0.013194004,-0.0012597035,0.031204224,-0.012809516,0.018961322,-0.010431762,0.018020337,-0.053949714,-0.025801158,-0.00234487,0.0008663624,-0.017747149,0.00072281185,0.029443674,-0.019426754,-0.02306927,-0.0039890613,0.004454494,0.0018895554,-0.021065887,0.020387974,-0.037659574,-0.011140029,-0.0035641012,0.014893845,0.011089439,-0.017463842,0.020843288,0.037072722,-0.019963013,-0.045288622,0.020155257,0.033086192,0.0125768,-0.0036779298,-0.010624006,0.0128398705,0.02760218,0.0029519561,-0.020944469,-0.00030591447,-0.03980461,0.004828864,-0.008008477,-0.008484028,-0.024141788,0.021490848,-0.02221935,-0.00831202,-0.0009713377,-0.051399954,0.015369396,0.035372883,0.036890596,-0.010492471,0.0065818247,0.05083334,-0.043022167,0.008969696,-0.04897161,-0.015915774,0.047838382,-0.02296809,-0.01731207,0.029929344,0.009890444,-0.014772427,-0.010143396,0.011069203,-0.015247978,-0.006121451,-0.0036071031,0.020023722,0.04065453,0.01880955,0.025052419,0.022705019,-0.031993438,0.009561606,0.0140338065,0.0023436053,0.02371683,-0.00039112786,-0.024040608,-0.0135582555,-0.010715069,-0.025072655,0.0059393253,-0.018242937,0.023028798,-0.03478603,0.00986009,0.010512707,-0.03251958,0.0012432617,0.0085245,-0.022199115,-0.028310448,0.016593685,0.02707604,-0.04002721,-0.009207472,0.01859707,0.017645968,0.020064194,0.0228062,0.051926095,-0.0014633304,0.02456675,-0.013325539,0.002115948,0.0025586148,-0.028897297,0.020377856,0.047190823,-0.007113025,0.01017881,0.0075531625,-0.00676901,-0.012607154,0.026893914,0.014468885,0.03203391,0.010118101,-0.013608846,0.0037689926,-0.006516057,0.008595327,0.017817976,0.011089439,0.004626502,-0.016826402,-0.010624006,-0.005812849,0.008934284,-0.0022032165,-0.026043992,-0.0077555245,-0.015156915,0.009986565,-0.050590504,-0.016947819,0.03298501,-0.011312037,0.028573519,-0.011392982,-0.027480762,0.015298569,0.01001692,0.015764002,-0.021490848,-0.009597019,0.005003401,0.022887144,0.027925959,0.002119742,0.021349194,0.0045126732,0.00030575637,0.07009821,-0.0021779214,0.023797775,-0.0007664462,0.035878785,0.0131636495,0.024445333,0.031062571,-0.025396435,0.006212514,-0.020630809,-0.012597036,0.00033705923,0.0011983626,-0.009070878,0.00516782,-0.0051298775,-0.03235769,0.016796049,0.0106138885,-0.0012989113,0.033065956,-0.017514434,0.010634124,0.01593601,0.008959578,0.0010023244,0.03288383,0.0003724726,-0.018485771,-0.014479003,0.033592097,0.015723528,-0.022846673,0.010254695,0.06317742,-0.008317079,0.034239653,0.0065362933,-0.018951204,0.029018715,-0.0008024919,-0.045490984,0.03719414,0.022725254,-0.007477277,0.0133154215,-0.012758926,-0.0204588,0.009728555,0.014914081,0.016047308,0.0031467294,0.014590302,-0.014944435,0.018991675,0.012192312,-0.00751269,-0.008696508,-0.014327231,-0.0056661367,-0.0015113914,-0.00025121347,-0.0038448784,-0.002248748]
9	19	ja	朝食の時間は何時から何時ですか？	朝食の時間は毎日午前7時から午前10時までとなっております。お客様のご都合に合わせてお楽しみいただけるよう、幅広いメニューをご用意しておりますので、ぜひお越しください。	2025-12-14 01:53:49.146461+00	2025-12-14 01:53:49.146461+00	[0.012826027,-0.02789661,0.0026874535,-0.02613303,0.013226841,0.03107105,0.02568412,0.046013374,0.016184842,-0.020457514,-0.011695733,0.0027515837,0.026277324,-0.002974035,0.0047095567,0.040145464,0.011527392,-0.018693935,0.037676454,0.069581196,0.013218825,0.012112579,0.0059039807,-0.008136511,-0.020681968,0.045660656,0.013667735,0.019880341,0.022413483,-0.049829114,-0.032866694,-0.01713878,-0.004481093,0.0005042733,0.006124428,-0.01790834,0.024786297,0.01629707,-0.06307199,-0.025636021,-0.04575685,0.036586244,0.03392484,-0.039279707,-0.050759003,-0.00648516,-0.047873147,0.008553357,-0.023744183,0.007238689,0.00043262792,-0.03225746,-0.0050542564,-0.044121534,0.079200715,-0.004120361,-0.022381417,0.053163882,0.003781674,0.088435456,0.029900676,0.021740116,-0.03309115,0.05518398,-0.04251828,0.007683592,-0.007807844,0.0015802067,-0.022798263,-2.8260472e-05,-0.043929145,-0.023599891,0.00074501184,-0.011872091,0.0180366,0.011423181,0.018373284,-0.0043808897,0.068426855,-0.023680054,-0.0028998845,-0.015471395,-0.05499159,0.060025807,0.014830094,-0.010557423,-0.024449615,0.044474248,0.02044148,0.007928088,0.025972705,0.0036353772,0.014341102,-0.014597623,0.01999257,-0.013427247,-0.022349352,0.04428186,0.019976538,0.059031792,0.05245845,-0.054638878,-0.03642592,0.03220936,-0.015992453,-0.039087318,-0.017475462,0.01728307,-0.05220193,0.000810645,0.019880341,0.0015962392,-0.077853985,0.0056073787,0.011238806,0.012890157,0.018100731,-0.020665936,0.023359401,-0.0033728443,0.005210574,-0.0063248347,-0.03456614,0.009507293,-0.082471356,-0.029018886,-0.026373519,0.0024549817,-0.045404136,0.012361084,-0.0044851014,-0.044249795,0.036233526,-0.012088531,0.024914557,-0.018325187,0.00539094,0.013908223,-0.082663745,-0.0048418255,0.06733664,0.03613733,-0.025026785,-0.022381417,0.0027475755,0.001019569,-0.048289992,-0.038349822,-0.050245963,0.052298125,0.0080403155,-0.0641622,-0.021467563,0.006008192,0.027608024,0.056915496,-0.036329724,-0.014974386,-0.036457982,0.07419857,0.0042205644,-0.00882591,-0.021082783,-0.008120478,-0.014100614,-0.011743831,-0.074904,0.02385641,-0.02480233,-0.012312986,0.020585774,0.022381417,0.019671919,0.011439213,0.019960504,0.0061645093,-0.0046694754,-0.008745748,0.03966449,0.039279707,-0.013178743,0.0098279435,-0.033315606,-0.015174793,0.05402964,-0.008120478,-0.0727877,0.0015130704,0.05377312,-0.035977006,-0.0030982872,-0.01683416,0.017876275,-0.032866694,-0.00252312,-0.024561843,-0.013419231,0.011567473,0.009218707,-0.017619755,-0.011527392,0.035656355,0.017876275,-0.018645838,0.013547491,0.03366832,-0.016056582,-0.010958237,0.03649005,0.038093302,0.025892543,0.027303405,0.03129551,-0.00018312159,-0.03713135,0.005138427,0.01986431,-0.040786766,-0.036265593,-0.025251241,0.010076447,-0.019832244,0.020072732,0.012553474,0.046975326,-0.014846127,0.0077797873,0.010052399,0.043480232,-0.015415281,-0.011551441,-0.003659426,-0.0012495356,0.020681968,-0.023680054,-0.026421616,-0.057300277,-0.020393383,-0.016593672,-0.007563348,0.016008485,0.008272788,-0.008737731,0.0527791,0.03485473,-0.020698002,0.0007244701,-0.060699172,-0.034085166,0.014028467,0.050470416,0.007118445,0.011270871,-0.038125366,0.029515896,-0.00040707606,0.015038517,-0.013026434,0.05095139,-0.007867966,0.011623587,0.0016343164,0.03227349,0.022349352,0.036842763,0.019158877,-0.0050261994,-0.008441129,-0.014357134,-0.012954287,-0.018645838,-0.05194541,0.025459664,-0.0067977943,0.029371602,-0.038830798,-0.020906424,-0.007547315,0.012345051,-0.022381417,-0.07548117,-0.034630273,0.018421382,-0.055216048,0.033251476,0.011655652,0.09818324,0.015134712,0.058198098,0.024032768,-0.0156237045,-0.0011343018,0.024177061,-0.0075513236,0.0128180105,-0.046462283,0.028137097,-0.030397685,-0.028201228,0.0029920717,0.039183512,0.021291206,0.004525183,0.012882141,0.0068499004,0.01110253,0.02100262,0.027752316,-0.023311304,-0.0052466467,0.019335236,-0.014950338,-0.008140519,-0.011030383,-0.021098815,-0.052041605,0.0095313415,0.05072694,-0.0028858562,-0.0037957025,0.05467094,0.0011042408,-0.02834552,0.06467524,-0.036233526,-0.0050302073,0.005491143,-0.049251944,-0.016000468,-0.018052634,0.020281155,-0.074070305,0.013876158,-0.018613772,-0.036522113,0.039568294,0.04062644,0.0007054315,0.017154811,0.018629804,-0.0031564052,-0.03770852,-0.024144996,-0.03700309,-0.028393617,0.0030662222,0.019415399,-0.013395182,-0.006240664,0.030541977,-0.012601572,-0.017924372,-0.021724084,-0.047841083,0.044698704,-0.0027275349,-3.544693e-05,-0.023439564,-0.033764515,0.013459313,0.008809878,-0.040273726,0.0034109217,-0.014220858,0.008625504,-0.0034169338,-0.021339303,-0.025636021,-0.022301255,-0.03879873,-0.012986353,-0.017603721,-0.031055018,-0.011471278,-0.019960504,0.016898291,-0.02416103,0.04226176,0.010886091,0.04408947,-0.034534078,-0.015944354,0.018341219,-0.009090447,0.021932507,-0.015968405,-0.024962656,0.0026253276,0.09003871,-0.03201697,-0.004805752,0.010324952,0.070414886,0.0012084523,-0.028826496,0.015784029,0.03373245,0.0027896608,-0.039279707,-0.057300277,0.056274194,0.026966723,0.008180601,0.0004168459,-0.012481328,0.0051584677,-0.018164862,0.009002268,-0.032802563,0.05255465,0.007238689,-0.008024284,0.0035692428,0.010653619,-0.00028708257,0.0097076995,0.010260821,0.0012104564,0.019447464,-0.052586712,-0.019671919,-0.06772143,-0.0015832128,0.058871467,-0.011206741,-0.00062526885,0.010381066,-0.0019249062,-0.039760683,-0.0067737456,0.043255776,-0.06579752,0.013266922,0.007863958,-0.012345051,-0.033315606,-0.01580808,-0.04675087,-0.011174676,0.019399365,-0.049187813,0.035399836,0.01891839,-0.00083920296,-0.032642238,0.009747781,0.026549876,0.07695616,0.05794158,-0.020890392,0.055761155,0.0071865832,0.02764009,-0.0113830995,-0.023102881,0.016313104,-0.057492666,-0.02991671,0.017571658,-0.043512296,-0.013170727,-0.01398037,0.007883999,0.008585422,0.0037335763,0.016465412,0.00038828794,0.012625621,0.014757948,0.038189497,-0.057364408,0.044313923,0.014293004,-0.008809878,-0.04822586,0.03568842,0.01733117,-0.0018818186,0.016737966,0.026469713,0.030012904,-0.025347436,0.026902592,-0.015046533,-0.0053348257,-0.0066575096,0.02549173,0.026485747,0.010340984,0.008545341,-0.0018477496,0.00792408,-0.049572594,0.0055151917,0.023840379,0.08061158,-0.0025912584,-0.008180601,-0.035592224,0.031038987,-0.022092832,-0.041171547,0.007503226,-0.015880225,-0.018325187,0.016753998,-0.032930825,-0.026966723,0.07689203,0.01309858,-0.01249736,0.01943143,-0.009835959,0.02961209,0.00042786825,0.011743831,-0.012641653,-0.012329019,-0.039023187,0.037997104,-0.00850526,-0.00996422,0.031808548,-0.029018886,0.007819869,0.00708638,0.009755797,-0.027319439,-0.0059280293,-0.013916239,0.039632425,-0.03847808,-0.035207443,0.012000352,0.019094748,-0.00805234,0.005972119,0.02106675,0.036009073,-0.034373753,0.01303445,-0.014036483,-0.038670473,-0.0123691,-0.0013647694,0.002495063,-0.0120404335,0.004224573,-0.024465647,-0.05758886,-0.0071024126,0.01713878,-0.003302702,0.016417315,0.0140445,0.016369218,-0.007980194,-0.030093066,0.0200567,-0.00026553884,-0.026870526,0.0060803387,-0.04232589,-0.0052907364,-0.015583623,-0.022926524,-0.010332968,-0.015928322,-0.03700309,0.0070783636,-0.027511828,0.04998944,0.014749931,-0.011511359,0.039023187,0.011479294,0.028586008,0.038061235,-0.025235208,-0.028056934,0.0027535877,0.008673601,0.01992844,0.0010351004,-0.012280921,0.016882258,0.04162046,0.029099049,-0.009571423,0.03536777,0.028954756,-0.020665936,0.019800179,0.00011185197,-0.00796817,0.01123079,-0.056306258,0.041652523,-0.024128964,-0.019495562,0.0149102565,0.0065212334,0.02916318,-0.010284871,-0.0064370623,-0.036682438,-0.0056234114,0.013002385,0.029499862,-0.015006452,0.03315528,0.041460134,-0.013050483,0.031535994,-0.032930825,0.021531694,0.0025331404,-0.011968287,-0.04639815,0.013771947,0.008946154,0.026549876,0.022894459,-0.022221092,-0.008028291,-0.02789661,-0.026870526,-0.022637937,0.0013317023,-0.027062917,0.0051825168,-0.0033708403,0.0018146825,0.018325187,0.003693495,0.0048899227,0.030702302,-0.019126814,-0.013555507,-0.005763696,0.054767136,0.014878192,0.01651351,-0.044378053,-0.0027535877,0.035977006,0.0065011927,0.0012234828,-0.031808548,0.0031964865,0.031311538,-0.029179212,0.008617487,-0.06579752,0.0044249794,0.019383334,-0.013603605,0.023247175,0.013395182,0.005378915,0.008320885,-0.05005357,0.014204825,0.027159113,0.015663786,0.024754232,-0.00594807,0.004533199,-0.014926289,0.030157197,-0.019800179,0.028569976,0.013315019,-0.0022886442,0.0059921597,-0.008705666,-0.0018988532,0.011944238,0.03639385,0.013042467,-0.038734604,0.018693935,0.014950338,0.015166777,0.0501177,-0.008657568,0.023631955,-0.007831893,0.035143316,-0.017363233,-0.009675634,0.0005621407,0.0036453975,-0.038253628,0.056530714,0.010108513,0.010573456,0.046622608,0.023583857,0.057172015,-0.02170805,-0.016914323,-0.008176592,-0.0029800474,0.00785995,0.05739647,0.010958237,0.0101886755,0.013675751,-0.002611299,-0.0054270127,0.012465295,0.0037476048,-0.004925996,0.027415633,0.019655887,-0.055568762,-0.00835295,-0.0030121123,-0.012449263,0.03915145,0.01771595,-0.038830798,0.0058037774,-0.013154694,-0.009154577,0.039921008,-0.0078278845,-0.009050366,0.027992804,0.02214093,0.014725883,-0.0017295096,0.009306886,-0.00848121,-0.018245025,-0.027752316,0.003751613,-0.01417276,-0.03575255,0.026966723,0.0034369745,-0.026918625,-0.029932741,0.014589606,-0.02411293,0.025267273,0.0076154536,-0.05467094,0.05345247,0.045949243,-0.0054470534,-0.03764439,0.003453007,0.011246823,-0.02411293,0.017251007,0.017427364,0.012080515,-0.01062957,0.023631955,0.020489579,0.0035532103,0.01050131,-0.0053989557,0.017154811,-0.016353184,0.01464572,-0.01651351,-0.009731748,-0.02764009,-0.026501779,0.002791665,0.02707895,0.025283307,0.0006989183,-0.046558477,0.0076876,-0.02156376,-0.009050366,0.005162476,-0.02574825,0.0036754585,-0.002066193,0.0072707543,0.0028076975,0.009972236,0.0072747623,-0.02568412,0.011679701,0.032786533,0.0051785083,-0.014974386,-0.0046173697,0.013154694,-0.021996636,0.02727134,0.0071545183,0.0004406442,0.03023736,-0.02398467,0.0037335763,-0.021868376,0.00910648,0.0058959643,0.018629804,-0.020730067,-0.003935987,0.022846362,0.04283893,-0.013170727,0.01511868,-0.02106675,-0.0011232794,0.014854142,0.005611387,0.016136745,0.010148594,0.00010809435,0.03498299,0.03424549,0.0054590777,0.03296289,-0.0062085986,0.036650375,-0.0052145817,0.012649669,0.004449028,-0.028425682,-0.017026551,0.008930122,-0.0047857114,-0.02961209,0.02278223,-0.0017365238,0.0075553316,-0.02948383,-0.026245259,-0.010517342,0.022477612,-0.01477398,0.0036474015,0.0032846655,-0.013787979,-0.03302702,0.02486646,-0.035720486,-0.001923904,0.0040903003,0.013523443,-0.028553942,0.022156961,0.034373753,-0.004477085,0.0063128104,0.025411567,0.02574825,-0.004689516,0.0139563205,-0.021098815,-0.032818597,0.014060533,0.00755934,0.023150979,-0.034758534,0.011960271,-0.0017756032,-0.015920306,-0.0026634047,-0.021146912,-0.0097076995,-0.019896375,0.005703574,0.0091706095,0.04155633,0.023503695,-0.022541743,0.0017385279,-0.0139563205,-0.0042486214,0.013018417,-0.009010284,0.023359401,0.035463966,0.03777265,0.004958061,-0.016353184,0.012729832,0.009723732,-0.0023607907,-0.008140519,0.04726391,0.006845892,-0.0047817035,0.044634573,0.021291206,0.0067977943,-0.02385641,-0.025219176,0.03184061,-0.044570446,0.038638406,-0.020826261,0.008164568,0.023680054,-0.0026754292,0.014693817,-0.012793962,0.030445782,-0.010717749,-0.036297657,0.015038517,-0.003968052,-0.0039059261,0.032866694,0.035592224,-0.0036474015,0.015896257,-0.015006452,0.040979158,0.0334118,0.02044148,-0.028778398,0.013419231,-0.00396204,0.004356841,-0.0085132755,-0.0032285515,-0.015062566,-0.003090271,0.030910725,0.004869882,-0.017218942,-0.0180847,0.016048567,-0.035528094,-0.0057276227,-0.017748015,0.0067136236,0.0025451647,0.026149062,-0.04312752,-0.07208227,-0.031343605,-0.029692253,0.011198725,-0.01423689,-0.0065011927,-0.017924372,-0.016689869,0.040754702,0.047776952,0.0077517303,-0.025988737,-0.0025130997,0.030205294,-0.013723849,0.024305321,-0.036618307,0.0061765336,0.008433113,-0.006152485,0.02258984,-0.0060202167,0.037355803,0.00079461245,0.0052987523,0.028105032,0.018709967,0.0234075,-0.01022074,0.04550033,-0.03751613,0.025443632,-0.0011062449,-0.0066494937,0.0334118,-0.046847064,-0.0013417227,0.006457103,0.02220506,0.046237826,-0.0031463848,-0.016401282,-0.039055254,-0.018934423,0.02246158,0.021675985,-0.006629453,0.012337035,0.020457514,-0.016409298,0.0037255601,0.029884644,-0.018068666,0.0062967776,-0.022445548,-0.0091706095,0.03195284,-0.03498299,-0.027527861,-0.041331872,-0.021996636,-0.0079481285,-0.014629687,0.012745865,0.004264654,0.0047576544,-0.05098346,-0.023712117,0.022028701,-0.0320811,0.0065372656,0.05800571,0.026838463,-0.0017906337,0.040786766,-0.0009278829,-0.0009193656,0.016737966,0.013627654,0.0014920277,-0.012168693,0.037997104,0.012657685,-0.011575489,0.024449615,0.041909043,0.026501779,0.0070182416,0.014276971,-0.004861866,-0.0006117414,0.025972705,0.017876275,0.018581707,-0.008433113,0.015134712,-0.013699801,-0.012986353,-0.018148828,-0.026181128,-0.013419231,0.00062927697,0.00014767467,0.032754466,-0.00618455,0.008898056,-0.018373284,0.012673718,-0.016721932,-0.07073554,0.023567826,-0.008745748,0.011126579,0.024818363,0.011559457,-0.004805752,0.023070816,-0.0050101667,0.023647988,-0.016946388,0.044185665,-0.027431665,0.0119201895,-0.021018652,-0.028377585,0.0058478666,-0.030173229,-0.024850428,-0.0056033707,0.040850896,-0.0046654674,0.022285223,0.03491886,0.0016343164,-0.0062526884,-0.054703005,-0.016561607,0.027672153,-0.0051264027,0.0009574429,0.008168576,0.009715715,-0.012200759,0.0061083953,-0.043223713,0.008156552,0.014068549,-0.025251241,0.028008837,-0.019575724,-0.027912641,0.0059200134,0.0018507557,-0.027800415,0.03588081,0.011952254,0.003901918,0.019896375,-0.024321355,-0.0074671526,-0.022317287,-0.003609324,0.017940406,0.03315528,0.039055254,0.028505845,0.008962186,-0.0016834161,0.0077236732,0.02188441,0.000117676296,-0.0029279415,0.05428616,0.05239432,0.04854651,0.018870292,0.003817747,-0.005976127,0.012024401,0.0025110957,0.012312986,0.009130528,-0.0031423767,-0.00086876296,-0.021403434,0.0017675869,-0.0063248347,-0.0091706095,-0.01417276,0.017828178,0.010894107,0.007956145,0.00093589915,0.007727681,0.042165566,0.0053268094,0.020265123,-0.006990185,0.04245415,0.019832244,-0.02821726,0.02759199,0.007928088,-0.03360419,-0.021692019,0.012176709,-0.034469947,0.0025611974,0.020008603,-0.00050928345,0.02626129,-0.019367302,-0.032417785,-0.02493059,-0.030798499,0.0090183,-0.018277088,-0.014958355,0.02321511,-0.01821296,-0.009996285,-0.005318793,-0.00046469297,0.008320885,0.0099481875,-0.0160646,0.02106675,0.024770265,0.011054432,-0.017635787,-0.023295272,-0.03188871,-0.0073308763,0.010429163,0.008144528,-0.012280921,0.010052399,0.0044249794,-0.021371368,-0.001978014,-0.046911195,-0.011407148,0.021403434,0.011751847,0.010942205,0.006966136,-0.0109662535,-0.01683416,0.033636257,-0.00828882,0.02847378,-0.023022719,0.0063208267,-0.019367302,0.0049460367,0.026036834,0.0022265182,-0.0013777959,-0.020601805,-0.0021603839,0.0059079886,0.008148535,0.01337915,0.00073649455,0.010709733,0.008304853,-0.02063387,0.0034890801,0.02031322,0.018629804,0.0037636373,-0.04796934,-0.014397215,0.012986353,-0.0051785083,0.039696556,0.017924372,-0.006753705,0.0042806864,0.03309115,0.007499218,-0.05402964,-0.0084571615,-0.010942205,-0.041331872,-0.012329019,0.012048449,0.0035672388,0.009996285,0.0030802507,-0.01518281,-0.056049738,0.023920542,-0.010260821,0.03674657,0.0051143784,0.03161616,-0.015743949,0.043608494,-0.017234974,0.0027656122,-0.016625738,-0.0055312244,0.014854142,-0.034309622,-0.016593672,-0.0008762782,-0.008625504,0.011479294,0.036522113,-0.03424549,0.012489344,0.03536777,-0.032481913,-0.04713565,0.029852578,0.016281039,0.014036483,0.005190533,-0.015864192,0.01563172,-0.016657803,-0.013451296,0.013603605,-0.014485395,0.03188871,0.0056835334,0.00539094,-0.01290619,-0.0038057228,0.0074070306,-0.030862628,0.008529308,0.031600125,0.030541977,0.0023788272,0.006665526,-0.004869882,-0.005703574,0.040818833,0.015639737,-0.0036213486,0.0039860886,-0.0043648575,0.011543425,-0.03639385,0.026325421,0.0020902415,-0.018453447,0.021275172,-0.0135955885,-0.04575685,0.0064049973,0.040915027,0.006124428,0.015591639,0.010613537,0.044634573,-0.018100731,0.030093066,0.002943974,0.023599891,-0.0234075,-0.0037716536,-0.004521175,0.019479528,-0.015880225,-0.0314398,-0.008433113,0.0036734543,-0.0025030794,-0.014100614,-0.016497478,0.0068979976,0.030525945,-0.002098258,0.009274821,0.01363567,-0.04024166,0.009723732,-0.0180847,-0.011471278,-0.012048449,-0.0069220467,-0.0020621847,-0.015222891,-0.0066735423,-0.009803895,0.052682906,0.05162476,-0.009298869,-0.042999256,-0.020970555,0.038670473,-0.020088766,0.0025050833,-0.019094748,0.03402104,0.015279005,0.010132561,0.030766433,0.041460134,0.0076314863,-0.01891839,0.050085638,-0.027495796,-0.013186759,-0.016673835,-0.008320885,-0.02916318,0.0077196653,-0.020008603,-0.025571892,-0.0076475185,0.0334118,0.016433347,0.013932272,-0.028393617,0.013820045,0.0018086702,-0.010926172,0.024048802,0.049764987,-0.0029840553,0.0024589899,0.027800415,0.01885426,-0.0014649727,-0.032802563,0.030782465,-0.015254956,0.009186642,-0.029275408,-0.021323271,-0.026036834,0.008184609,0.010974269,0.039632425,0.01062957,0.0055472567,0.015270988,0.02100262,-0.0076475185,0.014421265,-0.0072827786,-0.02531537,0.021916473,0.0025872502,-0.02156376,-0.016946388,0.037291676,-0.017026551,0.013242873,-0.034405816,-0.004116353,-0.009571423,-0.013667735,0.010060415,-0.019671919,0.01696242,0.0063448753,-0.016032534,-0.012329019,-0.018100731,0.0046494347,-0.028153129,-0.0016693876,-0.037163414,-0.008064365,0.023952605,-0.0059200134,-0.008376999,0.0033287548,-0.007475169,-0.015383217,0.009547374,0.027239276,0.016224924,0.011599538,-0.00036524117,-0.0013146678,-0.027111014,-0.014309037,0.0067777536,0.050662808,0.0018858268,0.027367536,0.029708285,0.024032768,-0.02454581,-0.015174793,0.021451531,0.032818597,-0.017026551,-0.034373753,0.013779963,0.028858561,0.038926993,-0.00027881577,-0.015792046,-4.5373323e-05,-0.0037856821,0.0061164116,-0.006573339,-0.026357487,0.02308685,-0.026966723,-0.02974035,-0.00016232941,0.003002092,0.0067697377,0.0103089195,-0.024096899,0.0056995656,0.04896336,-0.015647754,0.032674305,-0.0022726117,-0.007471161,-0.0064691273,-0.017603721,-0.0028277382,0.008946154,0.025555858,0.050149765,-0.01458159,-0.006605404,0.00022608378,-0.055440504,0.06345677,0.011663669,-0.011936221,-0.041396003,0.0002191948,-0.02379228,-0.03911938,0.0038257635,-0.007888007,0.010036366,0.04367262,0.049508464,-0.0014499422,0.011463262,-0.018549642,0.015439331,-0.018726,-0.038446017,-0.002943974,0.010765847,-0.0017936397,-0.009098463,-0.040850896,-0.014661753,0.00066785526,0.025139013,0.056274194,-0.004300727,0.020986587,-0.014453329,-0.009635553,-0.03137567,0.019848278,-0.019527627,-0.008124487,0.04303132,0.015070582,-0.043384038,-0.0042446135,-0.0016914323,0.019800179,0.013363117,-0.011118562,0.01417276,0.0095313415,-0.0103089195,0.00055713055,-0.02093849,-0.03556016,-0.019623822,0.02012083,0.037419934,0.019383334,0.022493646,-0.0138921905,-0.027624056,-0.025411567,0.0046173697,-0.00096495816,0.029996872,0.0054149884,-0.018068666,0.0092347395,-0.0005130411,-0.04796934]
13	22	en	Do you have WiFi?	Yes, we have free WiFi.	2025-12-23 05:24:50.39963+00	2025-12-23 05:26:21.13158+00	[-0.007198423,-0.012885005,-0.03170284,-0.0033357847,0.019837182,-0.027717078,-0.020845076,-0.0041718786,-0.010227831,-0.044713832,0.012667392,0.009437551,-0.0014123397,-0.014774807,-0.006591396,-0.006053089,-0.08328868,-0.00770237,-0.010806224,0.044416044,0.014259406,0.041827593,-0.014305219,-0.02247145,0.0020258091,0.03846031,-0.027350571,0.010033124,-0.025724197,-0.03204644,-0.027991958,-0.049111914,-0.026915345,0.024510143,0.012369606,-0.03486396,-0.029022759,-0.02583873,0.012896459,-0.03791055,-0.0065856697,0.009271477,0.032000627,-0.026434304,-0.0033529648,0.013320233,-0.026846625,0.012415418,0.019688288,0.011459065,-0.042766765,0.0015333156,-0.022631796,-0.015003873,-0.029068572,0.010525618,-0.0022620342,0.03005356,0.0022648976,-0.017454887,0.02233401,0.012346699,0.047325194,0.026090704,0.020971062,0.011023838,-0.0082005905,0.002960688,-0.03632999,0.064001255,0.038689375,0.015072593,0.022104943,-0.011842752,0.0132858725,-0.037589855,-0.018806381,-0.04340815,0.016618794,0.040521912,-0.0022004726,0.0315654,-0.02260889,-0.0085900035,-0.012885005,-0.00907677,-0.07692062,-0.04998237,-0.020089155,0.03811671,0.03962855,0.038574845,-0.026525931,-0.05099026,0.0081433235,0.0041718786,0.053051863,0.02120013,0.0050595123,-0.004080252,-0.0058068424,-0.057679012,0.008481197,-0.036375802,0.017512154,-0.019711195,0.009930044,0.03282527,0.009483364,0.014121966,-0.08947348,-0.024029104,0.009895684,0.009030957,0.025334785,0.0028432913,-0.043866284,-0.012106178,-0.039032977,-0.048333086,0.033535376,0.022620343,0.03204644,-0.020318221,-0.013125526,-0.008652997,-0.07123976,0.025632571,-0.024097824,0.008372391,0.015587993,-0.019539395,0.032023534,-0.015565087,-0.02909148,0.04521778,-0.049111914,0.0007151178,0.027762892,0.031313427,0.045653008,-0.017832847,0.026434304,0.005448926,0.025518037,-0.032802362,-0.004970749,0.0048590787,0.03321468,0.031175986,-0.024647584,-0.0049936553,-0.046775434,-0.031313427,-0.021726983,0.012071818,0.024074918,0.060152933,-0.027717078,0.048470527,-0.002383726,-0.00045383853,-0.013938713,0.028793693,-0.0107432315,-0.0020630325,0.026296865,-0.0020229458,-0.040155403,-0.053097676,0.034268387,0.05465533,-0.031794466,0.06134408,0.02243709,-0.038758095,0.029870307,0.0022792143,0.009632258,-0.048882846,-0.029389266,-0.0021532276,0.013045352,0.06345149,-0.014018886,-0.029687053,0.03811671,0.038574845,-0.0298474,-0.0074389433,-0.04672962,0.016458446,0.014167779,-0.009935771,0.0010451172,-0.03862066,0.01695094,-0.050028183,-0.06652099,0.0068834564,-0.01588578,-0.0010479805,-0.03032844,0.0021288893,-0.002113141,-0.013240059,0.01571398,0.016412634,0.004509752,-0.031038547,0.019585209,-0.0024538778,0.016252287,0.029961932,-0.0050537856,0.014018886,0.027877426,0.055663224,0.012644486,0.008194864,-0.0058927424,0.035024308,0.028495906,0.0190469,0.009511997,-0.0024538778,-0.029618332,-0.018336795,0.005334392,-0.0035304916,0.022104943,-0.0002517945,0.0027989096,-0.023456438,-0.023044117,-0.027236039,-0.025884544,0.009798331,-0.012885005,-0.03914751,-0.027373478,-0.02700697,0.027327664,0.102988414,0.038895536,-0.04226282,0.01571398,-0.057220876,0.042995833,-0.020959608,0.0022090627,0.012495592,0.013560752,-0.07811177,-0.031909,-0.03413095,-0.037887644,-0.021761343,0.044645112,-0.01992881,0.04217119,0.026296865,-0.011367438,-0.028106492,0.016767688,0.0026800812,-0.0047874954,0.0019971759,-0.020260956,0.02023805,-0.021223037,0.041873403,0.03747532,-0.02460177,0.00857855,0.036490336,-0.030969827,-0.040750977,0.03667359,-0.03646743,-0.015943047,0.023181556,-0.018691847,-0.017592328,-0.0022190842,0.020616008,-0.020455662,0.035803135,-0.03871228,0.035665695,0.05602973,0.029045666,-0.029687053,-0.05685437,-0.0033300582,0.010342364,0.076828994,0.027854519,0.02326173,-0.006906363,0.053235117,0.060382,-0.006545583,-0.005388796,0.019974621,0.0175007,-0.053418368,0.041438177,0.007158336,-0.013824179,-0.07380531,0.035894763,0.047600076,-0.006831916,-0.0027187362,0.018290982,-0.02298685,0.048241463,0.0061676227,-0.0122779785,0.018027555,-0.0038884084,-0.031542495,-0.003687975,-0.057220876,-0.044209886,0.07371368,0.040338658,-0.021486463,-0.02922892,0.033856068,0.01677914,0.027121505,-0.006339423,-0.003278518,-0.0040687984,-0.026021985,0.021635355,-0.04590498,0.017076928,-0.008137597,-0.009872777,-0.04929517,0.023800038,-0.00032427264,-0.0050051087,-0.018439874,0.000576604,0.04810402,-0.012151992,-0.003919905,0.020089155,0.00057409855,-0.017546514,0.0068147364,-0.04079679,0.067574695,-0.0036736582,-0.0051482758,-0.010445445,-0.0005590661,0.021623902,0.02027241,0.04714194,0.02673209,0.037269164,-0.021520823,-0.012873552,0.018886555,-0.026434304,0.017970288,0.024693398,0.013812726,0.026480118,-0.0010694554,0.0343142,0.015587993,0.05277698,0.040773883,0.002891968,-0.018760568,0.00826931,-0.0075019365,-0.017305994,0.015106953,0.005614999,-0.028473,-0.03321468,0.0028719245,-0.04727938,0.0113846185,0.024487237,0.00833803,-0.06395544,0.02638849,0.035963483,-0.009712431,0.036009297,-0.04961586,-0.06317662,-0.021566635,0.010657331,-0.040269937,0.004375175,0.042904206,-0.018783474,0.008687357,0.006820463,0.042423166,0.005188362,0.033260494,-0.088328145,0.021623902,-0.0065284027,0.011819845,-0.00859573,-0.03300852,-0.00016723663,0.049157728,-0.036215454,-0.018004648,0.003722335,-0.03163412,-0.027144412,0.006053089,0.00720415,-0.014156326,-0.039468203,-0.027167318,-0.086220734,0.0009985879,-0.012736112,0.027052784,0.060061306,-0.006425323,0.027946146,-0.011728219,0.026594652,0.029595425,-0.0051053255,0.019825729,-0.0037251983,-0.032962706,0.022082036,0.008063151,-0.030992733,0.008332304,0.067712136,-0.010439718,0.014225046,-0.046134047,-0.009363104,0.021944596,0.04402663,-0.008372391,-0.02943508,-0.019241609,0.020959608,-0.008956511,0.002844723,-0.009030957,0.0063909627,-0.02611361,-0.04782914,0.0058326125,-0.013388952,-0.040567726,0.035207562,0.036444522,-0.0070208963,-0.05355581,0.003636435,-0.020008981,-0.030282626,-0.0022978259,-0.03239004,-0.008412477,0.04278967,0.012312339,-0.012564312,-0.030580413,0.060977574,-0.03983471,-0.031931907,0.020616008,-0.004953569,0.025747104,0.039330762,-0.013915806,0.02549513,-0.005795389,0.025266064,0.027785799,-0.009156944,-0.036261268,0.001971406,-0.06789539,0.019001089,0.020008981,-0.039903432,-0.032573294,0.026457211,-0.028702065,-0.006179076,0.0476917,0.023135744,-0.015599446,-0.033535376,0.014660273,-0.048287272,0.024441423,0.0033959148,-0.008652997,0.02178425,0.0045727454,0.030420067,0.021795703,0.018806381,-0.018680396,-0.024853744,-0.039193325,-0.0155192735,0.030924013,-0.0040687984,-0.046088234,0.025884544,-0.014339579,-0.040957138,-0.021371929,0.0007000853,-0.034657802,-0.02363969,-0.0005211269,0.03907879,0.04308746,0.028083585,0.018416967,-0.027625453,0.007776817,-0.004203375,0.004607105,-0.005457516,-0.018302435,0.0012856373,-0.039468203,-0.024968278,-0.010411085,-0.05030306,-0.01547346,0.01777558,0.035390817,-0.004452485,-0.0014989557,-0.02326173,-0.0038397317,-0.016321007,-0.036078017,-0.04892866,0.011407525,-0.0017366124,-0.019344687,-0.018806381,0.027900333,0.045309406,-0.018909462,0.04320199,-0.0022233792,0.020696182,0.015141313,0.023754224,-0.027350571,0.017477794,-0.024418518,0.0048418986,-0.0002564474,-0.015943047,-0.009374557,-0.010319457,-0.010559978,0.056121357,-0.008549917,-0.016893674,0.007713823,0.055800665,0.043156177,-0.019905902,0.06752888,-0.0011983055,0.0032126615,-0.01992881,0.019184342,-0.0008869179,-0.038299963,-0.0029120112,-0.049386796,-0.021303209,-0.014660273,0.0035390814,0.031473774,0.033810254,-0.006522676,0.0010658763,-0.002658606,0.007919983,-0.004246325,0.011533512,-0.022963943,-0.012312339,0.01571398,0.00840675,-0.025357692,-0.025655478,-0.023800038,-0.005572049,-0.021051235,0.037383694,-0.03438292,0.0017222958,-0.013240059,-0.03204644,0.026640465,-0.0049678856,-0.013469126,0.010811951,-0.024097824,0.027831612,0.04750845,-0.027946146,0.018508594,-0.00761647,0.020043341,0.011573599,0.02757964,0.017214367,0.012907912,0.012907912,0.02730476,0.041117486,-0.009242844,-0.05996968,-0.0024538778,-0.066612616,-0.0017065475,0.0047044586,0.0072957766,-0.0072957766,-0.018806381,0.0137325525,0.03481815,0.009609351,0.014671726,-0.024555957,0.047920767,-0.020535836,-0.027442198,-0.00079743867,-0.030694947,0.022975396,0.019711195,-0.0073874034,0.013148433,0.0052141324,0.015358927,0.0014352464,-0.035574067,0.024830837,0.0010501279,0.019287422,0.015141313,0.0018998225,-0.00049678853,0.009706704,-0.010903578,0.0030694946,-0.006711656,-0.03976599,0.007164063,-0.027877426,0.013056805,0.004836172,-0.013549299,0.02480793,-0.02174989,0.006053089,0.02730476,-0.01777558,-0.01609194,0.0149237,0.0076336497,-0.016378274,-0.02247145,0.02432689,-0.0058755623,0.015771247,-0.034497455,-0.014121966,0.03923914,0.0148206195,-0.01622938,-0.06368056,0.001403034,-0.029068572,0.006734563,0.008687357,-0.0026056345,-0.05616717,-0.005443199,0.009729611,0.025266064,0.023410624,-0.00826931,-0.015897233,0.010817678,-0.017901568,-0.009637984,0.0054288823,-0.05460952,0.011046745,-0.028999852,0.014213593,0.001540474,0.04141527,-0.0122779785,-0.0023851576,0.009878504,-0.004392355,-0.016000314,0.011390345,-0.029572519,-0.03266492,0.019527942,0.007937163,-0.014694633,-0.016893674,0.012174899,0.042377353,0.03949111,0.018989636,-0.013102619,-0.045263592,-0.0032155246,0.037131723,0.0043322253,0.0154391,0.032000627,-0.042148285,0.013778366,0.011413252,-0.012461232,-0.0018239442,0.02480793,0.0069464496,0.029870307,-0.018004648,0.02267761,0.0011675247,0.016836407,-0.0069464496,0.014797713,-0.04045319,-0.024853744,-0.017180007,-0.0046443287,0.024097824,0.010388178,0.005938556,-0.022540169,-0.0038969982,-0.011081105,0.03158831,0.0075248433,-0.041873403,0.016973848,0.020398395,0.0049764756,0.010033124,-0.018909462,-0.032367133,0.020341128,-0.012999539,0.008727443,-0.0039914884,0.014419753,-0.022150757,-0.04065935,-0.021807157,0.03859775,0.027762892,0.00041554144,-0.012827739,0.00016956309,-0.024647584,-0.0033701449,-0.015313113,0.040430285,0.030786574,-0.0048648054,0.0049736123,0.027625453,-0.008859158,0.017512154,-0.013457673,0.01616066,0.017557967,0.048012394,0.007158336,-0.004034438,0.043385245,-0.0008554212,-0.032160975,-0.002392316,0.02700697,-0.0082979435,0.031657025,-0.019207248,0.023685504,0.0052084057,-0.036719404,-0.026365584,0.010617245,0.017626688,0.016836407,-0.007078163,-0.017615234,0.03025972,0.024670491,0.027488012,-0.016000314,-0.0062707025,0.018096274,0.035184655,0.043935005,-0.0049192086,-0.005262809,-0.012312339,-0.003679385,0.021039782,0.016595887,0.007982977,-0.0128391925,0.016378274,0.018875102,0.018817835,-0.021268848,-0.033237588,-0.0007466145,-0.046065327,-0.007467577,0.056946,-0.023525156,0.01461446,-0.01774122,0.0050623757,0.0041461084,0.001230518,0.014293767,-0.010548525,-0.02058165,0.015977407,-0.01581706,-0.015290206,0.029068572,0.009786878,0.04024703,0.013950166,0.032023534,0.023960384,0.025518037,-0.004014395,0.013984526,-0.005972916,0.047554262,-0.034657802,-0.0022176525,-0.037063003,-0.02236837,0.011321625,0.0050681024,-0.0071411566,-0.04017831,-0.02936636,0.000382971,0.027785799,0.037796017,-0.031244706,0.02384585,0.046752527,0.01677914,0.024303984,-0.011711039,0.00046099687,0.030282626,0.035665695,-0.011774031,-0.027396385,0.01636682,-0.03646743,0.01695094,-0.02936636,0.021830063,0.008091783,0.027762892,0.010892125,-0.03513884,-0.017706862,-0.018611675,-0.018989636,0.033329215,0.013045352,0.02219657,0.04439314,-0.059282478,0.016756235,-0.025288971,-0.024899557,0.021188676,-0.036902655,-0.0057209423,-0.006299336,0.034978494,0.032275505,0.03616964,-0.020421302,0.013194245,-0.0044811186,0.025197344,-0.028404279,0.0038053717,-0.008051697,0.028495906,0.012644486,0.014946606,0.007158336,-0.00013833486,0.03184028,-0.032344226,0.014660273,-0.018542955,-0.017088382,-0.030420067,-0.0027688446,-0.002577001,0.0026156562,0.017363261,0.018176448,0.04796658,0.0048132655,0.01530166,-0.052547917,-0.02909148,-0.013881446,0.004681552,0.0118885655,-0.012426872,-0.0040086685,-0.009672344,0.04370594,-0.0061676227,0.013629473,0.0298474,-0.0090366835,0.018680396,-0.016710421,0.008990871,-0.03523047,0.03273364,0.008973691,-0.00016929465,-0.015416193,-0.009185577,0.007868444,0.020764902,0.00015050403,-0.006402416,0.008927877,0.002806068,0.022872316,0.024303984,0.037200443,0.033787347,0.020776356,0.0047903587,0.057862263,-0.0105886115,-0.034589082,-0.0015848557,0.024853744,0.02058165,-0.0120832715,0.017111287,-0.0083952965,0.028335558,-0.011470518,0.011493425,0.025357692,-0.002887673,0.006711656,-0.021337569,0.02405201,0.03273364,-0.03859775,-0.023662597,0.010628697,-0.035505347,0.03142796,0.006700203,0.020020435,0.046065327,-0.015187127,-0.0089965975,-0.033649907,0.01378982,0.033741534,-0.01588578,0.0028862413,-0.001484639,-0.020799262,-0.015313113,-0.0019742693,0.005219859,0.016183566,0.009420371,0.02123449,0.018210808,-0.015771247,-0.028221026,0.01992881,0.038506124,0.026823718,-0.015496367,0.012415418,-0.004661509,0.03376444,0.0075706565,0.008950784,0.016630247,-0.027098598,-0.036215454,0.02522025,0.004526932,0.018978182,-0.024853744,0.01588578,0.027717078,-0.020845076,0.031175986,-0.0087446235,0.0039743083,0.016630247,-0.020306768,-0.0060416358,-0.046752527,0.0030179545,-0.005365889,0.013698192,-0.0038025083,0.005529099,-0.035207562,-0.0056006825,-0.0025054177,0.04874541,-0.0060473625,0.025884544,-0.016149206,0.0024037694,-0.030191,-0.011991645,-0.010010217,0.0013021014,-7.663894e-05,-0.006098903,0.019344687,0.010909305,-0.03067204,-0.010897852,-0.040636443,0.045332313,-0.04203375,0.016172113,0.03129052,0.013526392,0.029183106,-0.011900019,0.059786424,-0.006786103,0.0118885655,0.02243709,0.019241609,0.014522833,-0.0027946145,0.013194245,-0.0035505348,0.01557654,0.022276742,-0.019688288,-0.008275037,-0.0037366515,0.024418518,0.026823718,0.051265143,0.00063923944,0.0120832715,0.014591553,0.017168554,0.018726207,-0.007026623,0.009586444,-0.0132858725,-0.0175007,0.012610125,-0.009071044,-0.00034628453,0.0042749583,-0.016939487,0.00790853,-0.008383844,0.0019499308,-0.021429196,0.017420527,0.006402416,0.0069292695,0.02082217,0.030374253,-0.021635355,0.0009771129,0.0004148256,-0.006190529,0.008807617,-0.054472078,0.022104943,0.036009297,-0.019092714,0.004246325,-0.008378117,0.05277698,0.006436776,-0.022528715,0.00833803,0.00904241,-0.0122779785,-0.009592171,-0.030992733,0.013434766,0.0291602,-0.028702065,0.00015104089,0.027717078,0.064596824,0.0009835555,0.05176909,-0.012953726,0.042675138,-0.004715912,-0.003610665,-0.03653615,-0.022757784,0.0122779785,-0.014419753,-0.046340205,0.010903578,-0.022689063,0.008309397,-0.026617559,-0.012965179,0.00682619,-0.009025231,0.017363261,0.026984066,-0.02343353,0.0017380441,0.037063003,-0.0054632425,-0.03080948,-0.0024123595,0.04819565,-0.00875035,0.010330911,0.010966571,0.032023534,0.036261268,-0.012644486,0.0035219016,-0.010193471,-0.020810716,0.024510143,0.00027649075,-0.007868444,0.020157875,0.014832073,-0.053372554,-0.011785485,-0.015691074,0.005365889,-0.0038540482,-0.0139272595,-0.003808235,-0.033581186,0.04714194,-0.024510143,-0.0057295323,-0.0048218556,-0.0023336178,-0.0054202923,-0.0044009453,0.0023422076,-0.028037772,-0.020467116,-0.026411397,-0.021223037,0.049524233,-0.030763667,0.00818341,-0.019768462,0.020134969,-0.020879436,-0.0038110984,0.010411085,0.016492806,-0.05873272,0.0066543897,0.0018096274,0.003304288,-0.0093860105,0.007690917,-0.010101845,-0.012186352,-0.015702527,0.01540474,0.008681631,0.013022445,0.017787034,0.022036223,-0.017638141,-0.023044117,0.0013314505,0.021623902,-0.017706862,0.027762892,0.023593877,0.011670952,-0.020741995,-0.047554262,0.018004648,0.020192236,0.005225586,-0.029549614,-0.019424861,0.019997528,0.03039716,-0.00072728697,0.0295038,0.0056178626,-0.010874945,-0.012988086,-0.02305557,-0.039514016,0.01660734,-0.021074142,0.006093176,0.0052943057,-0.047783326,-0.012071818,-0.018233715,0.020661822,0.004034438,0.022047676,-0.0008124712,0.045950793,0.042285725,-0.0103939045,0.005471832,0.002340776,-0.037612762,0.019871542,-0.0019413409,0.030305533,0.014465566,-0.0004656498,-0.004784632,0.012392512,0.008761804,-0.017638141,-0.0090939505,-0.021429196,0.004818992,-0.00012947641,-0.018726207,0.018290982,-0.0049592955,-0.021005422,0.021223037,0.008601457,0.0067574694,-0.019321783,0.024762116,-0.0073931296,0.015965953,-0.051173516,0.037681483,-0.029824493,0.027785799,0.0030866747,0.028312651,0.061848026,0.012678846,0.0034789515,-0.012323792,-0.017958835,-0.016824953,-0.012965179,0.027808705,0.004818992,0.0016893673,0.011562145,0.019127075,0.0076393764,-0.007060983,0.019631023,-0.0019928808,-0.036375802,0.024143636,0.017054021,-0.055525783,-0.02058165,0.018600222,-0.0005916365,-0.02271197,-0.049570046,-0.014018886,-0.03818543,0.017386168,0.017752673,0.0060187294,0.012701752,-0.0024409927,0.015565087,-0.013869992,0.025311878,0.008068876,-0.014351033,-0.002345071,0.016435541,-0.015931593,-0.0023164377,0.034405828,0.004535522,-0.0178443,-0.032367133,0.022482904,0.00043021602,0.04549266,-0.018886555,-0.008864884,0.019825729,0.028999852,0.013148433,-0.0054976023,0.010949391,-0.01581706,-0.014797713,0.0019098441,0.026594652,-0.016343914,0.015106953,0.04178178,0.02051293,-0.022242382,0.0356886,-0.01409906,-0.0067402897,0.0008081762,-0.050807007,-0.0067517427,0.024143636,-0.018577315,-0.03239004,-0.025724197,-0.003467498,0.033741534,0.042423166,-0.00923139,0.0012312338,0.027442198,-0.000598079,-0.003951402,0.009323018,0.02147501,-0.034589082,-0.017363261,0.010932212,0.01557654,0.0063909627,0.0012183489,-0.00057588815,0.0071010697,-0.017340355,-0.0020973925,-0.034360014,0.004392355,-0.018783474,-0.010119025,-0.047371008,0.007868444,0.022116397,0.0036135283,0.0110925585,0.006368056,0.023891663,0.0016635974,0.020043341,0.009620804,0.015633807,0.0064654094,-0.0058412026,-0.033787347,-0.029664146,0.026709184,-0.016996754,-0.010187744,-0.027236039,0.015290206,-0.022185117,-0.015313113,-0.011877112,0.03218388,0.013045352,-0.0012720363,-0.0064997696,0.027327664,0.03516175,-0.008721717,-0.02700697,0.022700517,0.018290982,0.0840675,-0.0025097127,-0.018371154,-0.0035848948,0.0067975563,0.013388952,0.024303984,0.018279528,0.016412634,0.005322939,0.02487665,0.018680396,-0.014007432,-0.01992881,-0.051173516,-0.012804832,0.0053143487,0.026846625,-0.0051568653,-0.017305994,0.010073211,0.010565705,0.015599446,0.0031811646,-0.04349978,-0.010737505,0.03252748,0.0005748144,-0.005133959,0.028450092,0.020833623,-0.017134193,0.06134408,0.029457986,0.026686277,0.00053938065,-0.0047731786,0.043110367,-0.032229695,-0.016561527,-0.0013457673,-0.014190686,0.039445296,-0.0006489032,-0.00773673,0.025999079,0.026594652,0.053601623,-0.0011904313,0.01633246,0.009363104,-0.024991184,-0.008882063,0.0042234184,0.017409075,0.03220679,-0.043683033,-0.0048333085,0.022448543,-0.0045412485,0.0027187362,0.022448543,0.00076737365,-0.024212357,0.016492806,-0.027510919,0.016515713,-0.00766801,0.008498377,-0.01777558,0.012587219,0.025128623,-0.008315124,0.028358465,-0.038689375,-0.018932369,-0.021028329,0.025311878,-0.02577001,-0.03232132,0.0055319625,0.0057037626,-0.030580413,0.0036078016,-0.02343353,-0.016618794,0.0033787347,-0.020867983,0.0132858725,0.0033243315,0.027350571,0.009557811,-0.01657298,-0.024647584,-0.034268387,0.0071869697,0.0026858079,0.020295314,-0.011281538,-0.012518499,0.019837182,-0.03067204]
14	22	ja	WiFiはありますか？	はい、無料WiFiをご利用いただけます。	2025-12-23 05:26:21.13158+00	2025-12-23 05:26:21.13158+00	[-0.0012706931,-0.013009791,-0.051688023,-0.018083785,0.054391813,-0.049405605,-0.06576879,0.020260863,0.016117394,-0.029285198,0.005710438,0.02705545,0.00030670012,-0.0076329377,-0.009823183,0.012351401,-0.045016337,0.018645613,-0.017653637,0.043155286,-0.0029386152,0.0251944,-0.0154941175,-0.019102095,-0.0099285245,0.048211724,-0.014379243,-0.0213494,-0.014414357,-0.035237044,-0.03172563,-0.043576654,-0.002550165,0.0049467054,0.00055880874,-0.032603484,-0.0070798895,-0.026598966,0.004027154,-0.040451497,0.009752954,-0.0064258887,0.057306286,-0.006987715,-0.018048672,0.023192894,-0.0043519596,0.014054437,0.017618522,-0.0072422926,-0.043927796,-0.004354154,-0.040697295,-0.08153505,-0.014923512,0.0215952,0.030373737,0.052952133,-0.02501883,-0.000560729,0.042136975,0.02645851,0.030426407,0.017302496,0.02621271,0.03820419,0.022631068,-0.020489104,-0.062257383,0.06222227,0.004665792,-0.011719346,0.012737657,-0.018575383,-0.009199906,0.0013935927,-0.022929538,-0.06868327,-0.01638075,0.037080538,-0.029882139,0.0065400098,-0.05656889,-0.013115134,-0.0006896638,-0.013273147,-0.038730904,-0.023965405,-0.01283422,0.012649871,0.022192141,0.0034148507,-0.022069242,-0.065487884,-0.022508169,0.024825701,0.025247071,0.000258281,-0.04259346,-0.0009398521,0.033990495,-0.071984,-0.013202919,-0.01871584,0.046701815,-0.026967665,0.008861933,-0.00044907702,0.00954227,0.03209433,-0.048422407,0.00079061696,-0.044138484,0.034640104,0.019189881,-0.0038954755,0.025229514,0.0011916864,-0.0013497,-0.025053943,0.04125912,0.03844999,0.044068255,-0.042909488,-0.03281417,-0.035430174,-0.09881121,0.035851542,-0.05116131,0.027108122,0.004749188,-0.004283926,0.045086563,0.020734904,-0.009946082,0.0111487415,-0.047755238,0.028108874,0.011640339,0.009480819,0.06450469,-0.0060966937,0.038660675,-0.010911721,0.025527984,-0.039784327,-0.0039942344,0.022473054,0.0018544658,0.030005038,-0.039187387,-0.025685998,-0.04800104,-0.050002545,-0.048422407,0.040943094,0.018768512,0.040521726,-0.0037045425,0.039011817,0.007725112,-0.006030855,-0.023438692,0.026282938,-0.014958627,0.01859294,0.048317064,0.005956237,-0.018522711,-0.0073081315,0.03335844,-0.007031608,-0.012447965,0.0431904,0.017996,-0.01157889,0.025159286,0.017715087,0.027143234,-0.0021134326,-0.031743187,-0.017381502,0.009340363,0.064820714,-0.0548483,-0.041820947,0.035711087,0.03341111,-0.01553801,0.012456743,-0.014379243,0.029671453,-0.017829208,0.017074253,-0.019189881,-0.0072861854,-0.011543776,-0.048071265,-0.040697295,-0.029179856,-0.038976703,-0.06443446,-0.027880631,-0.0035136093,0.009884632,0.012167051,0.018873854,0.023386022,-0.011306755,-0.036343142,-0.02069979,0.0029605615,0.019786822,-0.018698283,0.024562346,0.018768512,0.050107885,0.0075188167,-0.05495364,0.03497369,-0.03023328,0.013571617,0.002561138,0.0059299013,0.014133444,-0.0015307573,-0.019295223,-0.030830221,-0.0033709581,0.021015817,0.020120407,0.004894034,-0.0290394,-0.03388515,-0.029566111,-0.010929278,-0.024281433,0.026598966,-0.013220476,-0.054918524,-0.009436927,-0.018399812,0.0019576137,0.07096569,0.061098613,-0.037396565,-4.114939e-05,-0.063556604,0.028477572,-0.007338857,0.010902942,0.035798874,0.0028157155,-0.08097322,0.004125912,-0.04684227,-0.030882891,-0.009638833,0.045964416,0.0024316546,0.027336363,-0.001865439,-0.020489104,-0.025159286,0.04757967,0.0399599,-0.006816534,0.025580656,-0.006123029,0.0077953404,-0.03286684,0.020647118,0.014203672,-0.022086797,-0.0058772303,0.025931798,-0.04132935,-0.03827442,0.036272913,0.022648625,-0.031198919,0.013782303,-0.013843752,-0.06373218,0.004762356,0.006860426,-0.02963634,0.03316531,-0.05397044,0.03718588,0.06538254,0.01990972,-0.036940083,-0.036869854,0.031339377,0.051898707,0.055796377,0.032708827,0.036729395,-0.020612003,0.03641337,0.022631068,-0.018505156,-0.008264992,-0.0035596965,0.017741423,-0.029882139,0.0014660156,0.00036430926,-0.009287692,-0.08153505,0.043225516,0.045964416,-0.014054437,-0.019769264,0.011359426,0.014747942,0.030795107,0.033340883,-0.04252323,0.037466794,-0.020067735,-0.032901954,0.0040600733,-0.07107103,-0.016345635,0.029144742,0.0086819725,-0.078023635,-0.024281433,0.056709345,0.022051685,0.012368958,-0.017996,0.003820858,-0.005495364,-0.025896683,0.0402057,-0.03372714,-0.007325689,-0.038414877,0.0013200724,-0.07114126,-0.008286939,0.0030132327,-0.043717112,-0.030812664,-0.007312521,0.021840999,0.015248318,0.012079266,0.0038537777,-0.010718593,0.00030505416,0.030672207,-0.035588186,0.092701346,-0.028934056,-0.019400565,-0.024808144,-0.023965405,0.030830221,0.013624289,0.0037857438,0.058956653,0.03341111,-0.029372983,-0.010920499,-0.0025589433,-0.031813417,0.036027115,0.039187387,0.03147983,0.010806379,0.00040161805,0.013466275,0.020489104,0.025229514,0.0249486,0.020541776,-0.009033114,0.030830221,-0.01229873,-0.009173571,0.00497743,-0.0025721113,-0.03186609,-0.01283422,0.030022595,-0.02099826,-0.0042180866,0.050248343,-0.00025540055,-0.025721112,0.010288445,0.009752954,0.016775783,0.03936296,-0.03209433,-0.074090846,-0.047123183,0.013167805,-0.04185606,0.022508169,0.06520697,-0.0034872736,4.502429e-05,0.024018075,0.030461522,-0.01301857,0.031778302,-0.04930026,0.019488351,-0.02472036,0.007281796,-0.0026357556,-0.030198166,-0.012728878,0.030215723,-0.04361177,-0.029495884,0.012131938,-0.03216456,-0.013843752,-0.009919747,0.0045955637,-0.0029495882,-0.060607016,0.018399812,-0.042909488,-0.03497369,-0.007145729,-0.016705556,0.03298974,-0.017820429,0.016986469,0.017109368,0.011429654,0.006930655,-0.01223728,0.011341869,-0.030619536,-0.066892445,0.029179856,0.03406072,-0.01889141,0.019997505,0.084625095,0.010104096,0.020190634,-0.03718588,-0.015142975,0.054391813,0.006087915,-0.033270653,0.006706802,-0.027985975,-0.008054308,-0.017521959,-0.006087915,-0.03442942,0.017978443,-0.04859798,-0.010727372,0.026019583,0.013448718,-0.015248318,0.030496636,0.044981223,-0.008769758,-0.036272913,0.013922759,0.0021584227,-0.04944072,-0.015230761,-0.048422407,-0.03005771,0.00305932,-0.001508811,-0.015230761,0.0013518946,0.034095835,-0.023561591,-0.007488092,0.005886009,0.051196426,0.049932316,-0.017223489,-0.010183102,-0.004068852,-0.0021606174,0.007878737,0.056042176,0.0012970287,-0.0022516947,0.043014828,-0.058394827,0.0019905332,-0.0025238292,-0.0150376335,-0.04224232,-0.047368985,-0.019558579,-0.0012750825,0.032708827,0.019119652,0.00828255,-0.032059215,-0.004692128,-0.015300989,0.015186869,-0.012351401,-0.038520217,0.027371477,0.011772018,0.014256343,-0.013457497,0.02633561,-0.011903696,-0.02638828,-0.003401683,-0.016652884,0.033867594,-0.023544036,-0.017890658,0.032427914,-0.030321065,-0.03521949,-0.013483833,-0.010981949,-0.022385268,-0.024808144,-0.048211724,0.0021167246,-9.238038e-05,0.01757463,0.019277666,-0.027160792,-0.002488715,0.019172324,0.0043344023,-0.007896294,-0.028530244,-0.0035487234,-0.020857804,-0.04529725,0.007659273,-0.016486092,-0.019944835,-0.0135891745,0.03269127,-0.0039722878,-0.0075144274,-0.010104096,-0.011719346,0.01781165,-0.0015867205,-0.033270653,-0.015915487,-0.0028354672,-0.009726618,0.0072379033,0.0019861439,0.042277433,-0.010051425,0.023473807,0.010744928,0.0082254885,-0.03291951,0.011780796,0.0021847582,0.014747942,-0.019839494,0.028565358,-0.00014909796,-0.008405449,0.023789834,-0.011552555,-0.029250083,0.06397797,0.0063117677,-0.01499374,0.0027037892,0.04996743,0.035500403,-0.031023348,0.06963135,-0.0012081461,-0.0071501182,-0.015564346,0.030847777,0.020295976,-0.018276913,-0.020857804,-0.048878893,0.0014309015,-0.0020684428,0.04378734,0.023210451,0.018136457,0.0014747941,-0.015599459,-0.00085974793,0.0006051704,-0.014774277,-0.008181596,-0.020647118,-0.0029561722,0.0048501412,0.013949094,-0.04175072,-0.024983715,-0.03844999,0.037642363,-0.013720852,0.028319558,-0.032726385,0.013281926,-0.016442198,-0.021630313,0.028582916,0.012026595,0.0057543307,0.008466898,-0.010762486,0.03281417,0.016872346,-0.041188892,-0.0056884917,-0.019716593,-0.017223489,0.014791834,0.02591424,0.011008285,0.018136457,-0.009226242,0.017969664,0.029250083,-0.0111487415,-0.026879879,-0.021402072,-0.024825701,0.012140716,-0.00011508113,0.016749447,0.016582655,-0.0071632857,0.03155006,0.00025896684,-0.0055699814,-0.010990728,-0.017434174,0.051723137,-0.023350907,-0.019874606,0.0135891745,-0.0005195796,0.02045399,0.011780796,-0.021560086,0.010534244,0.0033577902,-0.0041434695,-0.0031295484,-0.03125159,0.0029583669,0.0037594084,0.02105093,0.015634574,0.0016810898,0.014440693,0.030672207,0.007817287,-0.015020076,0.0056665456,-0.0073915278,0.03999501,-0.017925771,0.009630054,0.03449965,-0.00079061696,0.017144483,-0.012325065,-0.0071632857,0.026160039,-0.016161285,-0.009463263,0.006711191,0.002132087,-0.00839667,-0.004000818,0.0106659215,0.008291327,0.021805884,-0.037993506,0.009278913,0.032498144,0.0066541308,-0.014405578,0.045929305,-6.0609623e-06,-0.01121897,-0.0005662156,0.004457302,0.033305768,-0.033498894,-0.0011796159,0.0022056072,0.0062722643,0.01691624,-0.01463382,-0.012790328,0.015327325,-0.03191876,0.0025084668,0.01997995,-0.013448718,0.006267875,-0.029566111,0.019207438,0.030619536,-0.0010413539,0.018382255,0.005565592,0.017899437,0.004330013,-0.016047165,0.0023504533,-0.016810898,-0.035079032,0.018628055,0.018434927,-0.022332598,0.00031849628,0.018241799,0.011596447,0.016143728,0.009015557,-0.037607253,-0.058640625,-0.036975197,0.040170584,-0.0031097967,-0.0074705346,0.0020015063,-0.0030988234,0.011447212,0.020647118,-0.015590681,0.012439187,0.028266888,-0.0014671129,0.036483597,-0.013755967,0.02896917,0.011921253,-0.007154507,-0.007202789,0.013764746,-0.078445,-0.021542529,-0.0011532803,-0.009006779,0.024808144,-0.0060571902,0.0091911275,0.0033994883,-0.0062722643,-0.02112116,0.011254084,-0.005271511,-0.031743187,0.027108122,0.023122665,-0.022244811,-0.0028596083,-0.025159286,-0.025510427,0.013202919,-0.011297977,0.015643353,0.0030680986,0.016354414,-0.040837754,-0.030198166,-0.044314053,0.024070747,0.012017816,-0.013791081,-0.024105862,-0.010753707,-0.020120407,0.008528348,0.0003739108,-0.002681843,0.03262104,-0.018680725,0.03953853,0.023192894,-0.020559333,-0.016029608,-0.009103343,0.012913227,0.011552555,0.04979186,-0.004907202,-0.012544529,0.05133688,-0.0022999765,-0.026107367,0.015555567,0.010183102,-0.011684232,0.0466667,-0.018101342,0.038485106,0.0025040775,-0.009428148,-0.021840999,0.038344648,0.03743168,0.024579903,0.017592188,-0.026739422,0.0037330727,0.012790328,0.01319414,-0.0063424925,-0.0062239827,0.010174324,-0.0040161805,0.03065465,-0.0027432926,-0.009199906,0.068156555,0.024457002,0.021840999,0.008839986,0.017864322,0.006640963,0.0056972704,0.017083032,0.02772262,-0.007461756,-0.041013323,0.022929538,-0.04930026,-0.016205179,0.048281953,-0.020734904,-0.009199906,0.0035465288,0.024211204,0.008787315,0.031163804,0.042417888,0.01660899,-0.003485079,0.022350155,-0.0138174165,-0.0010550703,0.02129673,0.011280419,0.040240813,0.02608981,0.021244058,0.0002869484,0.02087536,0.002993481,-0.009638833,-0.014765498,0.04427894,-0.05470784,-0.008295717,-0.03402561,-0.0023372853,0.019716593,0.0124743,-0.029794354,-0.044665195,-0.016521206,0.0010901846,0.010446458,0.037045423,-0.0014330961,0.008330831,0.028038645,0.020120407,0.020682232,0.017952107,-0.0148357265,0.016450977,0.020734904,-0.0140456585,0.007005272,-0.011482326,-0.012886892,0.017565852,-0.0106659215,0.014265122,-1.9168758e-05,0.07033364,0.004929148,-0.01938301,-0.019892164,-0.03283173,0.00046526245,0.008194764,-0.015845258,-0.0009124192,0.04048661,-0.049826972,0.00020300366,-0.0254402,-0.020225748,0.013896423,-0.04080264,-0.0005557911,-0.009823183,0.032111887,0.03167296,0.045753732,-0.0015241734,0.0037264887,0.0049510947,0.013483833,-0.031901203,0.005631431,0.010780043,0.0013244617,0.013501389,-0.012491858,-0.015634574,0.0084405625,0.0217181,0.014581149,-0.010516687,-0.026124924,-0.0012684985,-0.011473548,0.018031115,-0.001550509,-0.0024140975,0.012228501,0.017451731,0.04252323,0.006188868,0.020892916,-0.032041658,-0.016775783,-0.021876113,-0.00030231086,0.007659273,-0.012816664,0.019576136,0.015309768,0.02772262,-0.027617276,0.032550815,0.0580788,-0.038485106,0.017170817,0.011271641,-0.033850037,-0.016468534,0.019576136,0.01170179,0.04259346,-0.04835218,0.017776536,0.031392045,0.016213957,0.019857049,0.0028661923,0.014344129,-0.0026796483,0.012816664,0.021103602,0.020085292,0.037923276,0.048281953,-0.005499753,0.029355427,-0.0050476585,-0.037115652,0.017083032,0.0044594966,0.025984468,-0.0058333375,0.017706309,-0.010068982,0.033639353,0.012307508,0.0047974703,0.028302003,-0.0020673454,0.010841493,-0.02129673,0.010578137,0.035992,-0.005236397,-0.016670441,0.014932291,-0.033095084,0.0060264654,0.015204425,0.006447835,0.036483597,-0.026598966,0.021560086,0.013044905,0.001033124,0.021840999,-0.01793455,-0.015617017,-0.024070747,-0.002442628,-0.030637093,-0.007431031,0.027371477,0.010534244,-0.007347635,0.015467782,0.013369711,-0.01253575,-0.0026950107,0.018083785,-0.0038406097,0.020647118,-0.0089365505,0.0069569903,-0.013949094,0.015459003,0.012693764,0.019242553,-0.007865569,-0.0426988,-0.035886656,0.036272913,0.005780666,0.03390271,-0.014431914,0.010147988,0.039117157,-0.02975924,0.022718852,-0.0045867856,0.019295223,-0.0030790716,-0.020980703,-0.0057762773,-0.071492404,-0.024263876,-0.00032398288,0.024105862,0.022841752,-0.0049598734,0.011043399,0.01601205,-0.0062283715,0.008207932,-0.0032458638,0.041610263,-0.027564606,-0.028354673,-0.017592188,-0.027301248,0.010104096,-0.007865569,-0.022964653,-0.01481817,0.0045692283,0.0060747475,-0.029004285,-0.00737836,-0.022894423,0.03785305,-0.034534764,-0.015924266,0.02405319,-0.012667429,0.045016337,-0.012351401,0.034271408,-0.001012275,0.024790587,0.036132455,0.004630678,0.011008285,0.011297977,0.0030615146,-0.012386515,-0.007215957,0.011069735,-0.025563098,0.003287562,0.013650624,0.019418122,0.038906474,0.061730668,0.016626548,-0.015186869,0.014862062,-0.008194764,0.040275928,0.006232761,0.0066190166,-0.022859309,-0.01793455,-0.0013058073,0.019207438,-0.006592681,-0.0005991351,-0.016038386,0.0030198165,0.030900449,0.023140222,-0.017179595,0.014282679,-0.017249824,-0.008093811,0.023789834,0.027125679,-0.017126925,0.009998753,-0.010306002,-0.009094564,0.021753214,-0.037220996,-0.0017227879,0.01841737,-0.009814404,-0.015757473,-0.0056050955,0.059132222,0.003634314,-0.0011938809,0.00954227,0.0066146273,0.020313533,-0.020015063,-0.027494377,-0.019172324,0.017504402,-0.020015063,-0.003498247,0.009823183,0.020963145,-0.018698283,0.0705092,-0.03011038,0.027178349,0.009252578,0.016652884,-0.01733761,0.011570111,0.023368465,-0.005021323,-0.021963898,0.024404332,-0.032726385,-0.019576136,-0.015625795,-0.026651638,-0.019558579,-0.027248578,0.019277666,0.013264369,-0.018452484,-0.010464015,0.018364698,-0.0009919746,-0.031637847,0.027090564,0.031444717,0.008888268,0.023473807,0.021279173,0.016503649,0.037045423,0.0035245824,-0.026581408,-0.023684492,-0.012052931,0.016038386,0.0012695958,0.0007823871,0.025598213,0.0009305249,-0.022683738,0.0060615796,-0.0039393683,-0.008071864,-0.022701295,-0.009989975,-0.014712827,-0.066365734,0.037993506,0.010060203,0.009480819,-0.02033109,0.024246318,0.013413604,0.015002519,0.01433535,-0.033393554,-0.018154014,-0.026704308,-0.03795839,0.055094097,-0.03593933,-0.010420123,-0.011570111,-0.021261616,0.0022780302,0.011297977,-0.0018259356,0.006974547,-0.040240813,-0.00031054072,0.02573867,-0.006004519,0.0027520712,-0.018452484,-0.00040106938,-0.011060956,-0.02807376,0.04547282,-0.001553801,-0.0050301016,0.014616263,0.021279173,-0.0063688285,-0.022262368,-0.0017710697,0.02909207,-0.01403688,0.008049918,0.008967275,0.006070358,-0.010569358,-0.0392225,0.025141729,0.03142716,0.018241799,0.008769758,0.0032195284,0.011043399,-0.0051134974,0.0006808852,0.02874093,0.025229514,0.017320052,0.004246617,-0.019874606,0.007821676,0.023087552,-0.0019883385,-0.019751707,0.04870332,-0.052390307,-0.005381243,-0.026897436,0.011657896,0.0071062255,0.02608981,0.00041176824,0.053654417,0.05242542,-0.008673194,0.015669689,-0.007769005,-0.029530996,0.008449341,0.015687244,0.042628575,0.0103850085,-0.022543281,-0.0030417629,-0.0019817546,0.0008010415,-0.01206171,-0.013659403,-0.013808638,0.028179102,0.030198166,-0.025896683,0.00984074,0.002903501,-0.0034719112,-0.0036430927,0.020910474,-0.009989975,-0.04210186,0.044770535,0.0051398333,0.022648625,-0.045507934,0.054672725,-0.018944083,0.030619536,-0.0045911744,0.022086797,0.032006543,-0.011139963,-0.020436434,-0.0038493883,0.009085786,-0.021244058,-0.026546294,0.019786822,0.00623715,0.0074354205,-0.002526024,0.02981191,0.0008290231,0.0016580462,0.027880631,0.014028101,-0.02693255,0.027441705,0.0062766536,-0.05214451,-0.029144742,0.009331584,-0.0039459523,-0.020647118,-0.04757967,-0.00954227,-0.03486835,0.0026357556,0.010999506,-0.009489598,0.007325689,-0.0036496767,0.01746051,-0.010007531,0.03077755,-0.012404072,-0.03142716,0.00600013,0.022332598,-0.009454484,-0.00029682426,0.047368985,0.031286705,-0.018750954,-0.021173831,0.011640339,-0.004564839,0.027248578,-0.03035618,0.012649871,0.012913227,0.022947095,0.007233514,0.0106395865,0.010946835,-0.020120407,-0.013088798,-0.0147830555,0.00515739,-0.004018375,0.027564606,0.02429899,0.014423136,0.004084214,0.002914474,0.010604472,-0.012263616,-0.030882891,-0.041083552,0.015643353,0.019400565,-0.010657144,-0.026528738,0.0033643742,0.022824194,0.01703036,0.04708807,-0.00965639,-0.015274653,0.048317064,-0.006101083,0.02303488,0.020243306,0.043155286,-0.036869854,-0.0072993534,0.013685739,-0.010709815,-0.007338857,-0.0213494,-0.005267122,0.0049510947,-0.028407345,0.009603719,-0.014791834,-0.017109368,-0.026862321,-0.011043399,-0.031146247,-0.020243306,0.009436927,-0.005894787,-0.014019323,0.00041506017,0.016029608,0.022385268,0.02291198,-0.014721606,0.010806379,0.017267382,0.0040666573,-0.022982208,-0.032375243,0.012649871,0.022367712,-0.007101836,0.00080597936,-0.019154767,0.012588422,-0.010604472,0.0073520243,0.0046175104,0.017478066,-0.0022056072,-0.00085206673,0.058219254,0.014186115,0.013273147,-0.058570396,0.031339377,0.009454484,0.039503414,-0.009612498,0.0058772303,0.022350155,0.0071369503,0.0060264654,0.00036513226,-0.00032041658,0.003755019,0.0011390151,0.015985714,0.027740175,-0.026318053,-0.013457497,-0.07254583,-0.005249565,-0.008190375,-0.00045099732,-2.0180347e-05,-0.019277666,-0.007545152,0.020770017,0.017829208,0.030338623,-0.028003532,-0.004986209,0.021033375,0.013852531,-0.0006759473,0.03855533,0.025176844,0.01775898,0.05182848,0.022982208,0.01608228,-0.002177077,-0.020682232,0.04673693,-0.023982963,-0.045016337,-0.015696023,-0.01289567,0.05716583,-0.00060242706,-0.008001636,0.028951613,0.007711944,0.026160039,-0.0044112145,0.021823442,0.00641711,-0.0031405215,-0.006461003,0.0031207697,0.006452224,0.021384515,-0.048738435,0.017688751,0.03341111,-0.022297483,-0.010806379,0.005530478,0.015459003,-0.012096823,0.028863829,-0.013027349,-0.0064390567,-0.027933303,0.003204166,-0.006579513,-0.02333335,0.015968159,-0.012930784,0.03869579,-0.0069350437,0.0053197932,-0.02603714,0.02603714,-0.011236527,-0.04649113,0.011710567,-0.011333091,-0.028302003,0.016345635,-0.018171571,-0.0026028361,-0.0161964,-0.008317663,0.03750191,0.006430278,0.01751318,-0.00017433625,-0.010235773,-0.025949353,-0.03425385,0.027073007,0.013720852,-0.025159286,-0.008273771,-0.0021013622,-0.01649487,-0.00030231086]
\.


--
-- Data for Name: faqs; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.faqs (id, facility_id, category, priority, is_active, created_by, created_at, updated_at, intent_key) FROM stdin;
14	2	basic	3	t	1	2025-12-05 09:09:35.599463+00	2025-12-05 09:13:21.734041+00	legacy_14
15	2	basic	1	t	1	2025-12-05 12:49:20.530065+00	2025-12-05 12:49:20.530065+00	legacy_15
7	2	basic	1	t	1	2025-12-04 00:51:40.800779+00	2025-12-14 00:53:30.629087+00	legacy_7
11	2	facilities	1	t	1	2025-12-04 08:55:33.21179+00	2025-12-04 08:55:33.21179+00	legacy_11
13	2	trouble	1	t	1	2025-12-04 08:55:33.21179+00	2025-12-04 08:55:33.21179+00	legacy_13
12	2	location	1	t	1	2025-12-04 08:55:33.21179+00	2025-12-04 08:55:33.21179+00	legacy_12
16	2	basic	1	t	1	2025-12-14 00:54:33.235579+00	2025-12-14 00:55:52.682119+00	legacy_16
6	2	facilities	3	t	1	2025-12-04 00:17:22.309197+00	2025-12-05 08:52:49.89369+00	legacy_6
19	2	basic	1	t	1	2025-12-14 01:53:49.146461+00	2025-12-14 01:53:49.146461+00	legacy_19
22	2	facilities	3	t	1	2025-12-23 05:24:50.39963+00	2025-12-23 05:24:50.39963+00	facilities_do_you_have_wifi
\.


--
-- Data for Name: guest_feedback; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.guest_feedback (id, message_id, facility_id, feedback_type, created_at) FROM stdin;
1	28	2	negative	2025-12-03 05:39:24.442912+00
2	30	2	positive	2025-12-03 05:39:27.687705+00
3	32	2	negative	2025-12-03 05:39:35.961331+00
4	72	2	negative	2025-12-04 00:34:56.756287+00
5	74	2	negative	2025-12-04 00:35:18.741354+00
6	76	2	negative	2025-12-04 00:35:34.268288+00
7	78	2	negative	2025-12-04 00:46:07.092005+00
8	80	2	negative	2025-12-04 00:46:30.784987+00
9	28	2	negative	2025-12-04 00:48:23.120815+00
10	32	2	negative	2025-12-04 00:48:24.592332+00
11	88	2	negative	2025-12-04 04:15:53.050531+00
12	84	2	negative	2025-12-04 04:15:54.457974+00
13	256	2	positive	2025-12-12 12:39:55.850991+00
14	332	2	positive	2025-12-14 06:03:39.241213+00
\.


--
-- Data for Name: ignored_feedbacks; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.ignored_feedbacks (id, message_id, facility_id, ignored_at, ignored_by) FROM stdin;
1	28	2	2025-12-14 05:36:46.088007+00	1
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.messages (id, conversation_id, role, content, ai_confidence, matched_faq_ids, tokens_used, response_time_ms, created_at) FROM stdin;
4	2	user	フロントはいつ開いてますか？	\N	\N	\N	\N	2025-12-02 01:46:10.807488+00
5	2	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	467	2025-12-02 01:46:10.807488+00
6	2	user	フロントはいつ開いてますか？	\N	\N	\N	\N	2025-12-02 02:02:34.997399+00
7	2	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	464	2025-12-02 02:02:34.997399+00
8	2	user	ビールの自動販売機はありますか？	\N	\N	\N	\N	2025-12-02 06:45:32.54868+00
9	2	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	440	2025-12-02 06:45:32.54868+00
10	2	user	ゲストキッチンは夜も開いてますか？	\N	\N	\N	\N	2025-12-02 07:45:26.354715+00
11	2	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	9667	2025-12-02 07:45:26.354715+00
12	3	user	ゲストキッチンは夜も開いてますか？	\N	\N	\N	\N	2025-12-02 12:58:50.606134+00
13	3	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	9636	2025-12-02 12:58:50.606134+00
14	3	user	アイロンは貸し出ししてますか？	\N	\N	\N	\N	2025-12-03 00:30:51.729914+00
15	3	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	9381	2025-12-03 00:30:51.729914+00
16	3	user	アイロンは貸し出ししてますか？	\N	\N	\N	\N	2025-12-03 01:10:29.078219+00
17	3	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	8974	2025-12-03 01:10:29.078219+00
18	3	user	アイロンは貸し出ししてますか	\N	\N	\N	\N	2025-12-03 01:12:28.20096+00
19	3	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	7846	2025-12-03 01:12:28.20096+00
20	3	user	アイロンは貸し出ししてますか	\N	\N	\N	\N	2025-12-03 01:46:57.191836+00
21	3	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	7900	2025-12-03 01:46:57.191836+00
22	3	user	アイロンは貸し出ししてますか？	\N	\N	\N	\N	2025-12-03 03:52:55.538077+00
23	3	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	10549	2025-12-03 03:52:55.538077+00
24	3	user	アイロンは貸し出ししてますか？	\N	\N	\N	\N	2025-12-03 04:07:51.541165+00
25	3	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	7349	2025-12-03 04:07:51.541165+00
27	3	user	アイロンは貸し出ししてますか？	\N	\N	\N	\N	2025-12-03 04:49:25.741772+00
28	3	assistant	申し訳ありませんが、アイロンの貸し出しについての情報はありません。スタッフにお問い合わせください。	0.70	{}	\N	4210	2025-12-03 04:49:25.741772+00
29	3	user	変換プラグは貸し出ししてますか？	\N	\N	\N	\N	2025-12-03 05:03:46.190523+00
30	3	assistant	申し訳ありませんが、変換プラグの貸し出しは行っておりません。必要な場合は、スタッフにお問い合わせください。	0.70	{}	\N	2626	2025-12-03 05:03:46.190523+00
31	3	user	ドリンカブルな水はありますか？	\N	\N	\N	\N	2025-12-03 05:39:12.674965+00
32	3	assistant	申し訳ありませんが、ドリンカブルな水についての情報はありません。スタッフにお問い合わせください。	0.70	{}	\N	2228	2025-12-03 05:39:12.674965+00
33	3	user	変換プラグの	\N	\N	\N	\N	2025-12-03 06:35:25.879609+00
34	3	assistant	申し訳ありませんが、変換プラグの情報は提供していません。必要な場合はスタッフにお問い合わせください。	0.70	{}	\N	2499	2025-12-03 06:35:25.879609+00
35	3	user	変換プラグ反映さ	\N	\N	\N	\N	2025-12-03 06:36:09.713927+00
36	3	assistant	申し訳ありませんが、変換プラグに関する情報はありません。スタッフにお問い合わせいただければ、詳しい情報を提供いたします。	0.70	{}	\N	2441	2025-12-03 06:36:09.713927+00
37	3	user	変換プラグ反映さ	\N	\N	\N	\N	2025-12-03 06:48:40.554215+00
38	3	assistant	申し訳ありませんが、変換プラグについての情報はありません。スタッフにお問い合わせいただければお手伝いできると思います。	0.70	{}	\N	2773	2025-12-03 06:48:40.554215+00
39	3	user	変換プラグ反映さ	\N	\N	\N	\N	2025-12-03 06:48:43.40484+00
40	3	assistant	申し訳ありませんが、変換プラグについての情報はありません。スタッフにお問い合わせください。	0.70	{}	\N	2085	2025-12-03 06:48:43.40484+00
41	3	user	変換プラグは貸してもらえますか？	\N	\N	\N	\N	2025-12-03 06:50:54.85349+00
42	3	assistant	申し訳ありませんが、変換プラグの貸出は行っておりません。必要な場合は、スタッフにご相談ください。	0.70	{}	\N	11284	2025-12-03 06:50:54.85349+00
43	3	user	変換プラグは貸してもらえますか？	\N	\N	\N	\N	2025-12-03 07:06:20.028663+00
44	3	assistant	申し訳ありませんが、変換プラグの貸出は行っておりません。必要な場合は、スタッフにお問い合わせください。	0.70	{}	\N	2143	2025-12-03 07:06:20.028663+00
45	3	user	変換プラグは貸してもらえますか？	\N	\N	\N	\N	2025-12-03 07:06:26.731758+00
46	3	assistant	申し訳ありませんが、変換プラグは貸出しておりません。必要な場合は、スタッフにお問い合わせください。	0.70	{}	\N	2016	2025-12-03 07:06:26.731758+00
47	3	user	変換プラグは貸してもらえますか？	\N	\N	\N	\N	2025-12-03 07:08:53.491152+00
48	3	assistant	申し訳ありませんが、変換プラグの貸出は行っていません。必要な場合は、スタッフにお問い合わせください。	0.70	{}	\N	1733	2025-12-03 07:08:53.491152+00
49	3	user	トークンを出してください	\N	\N	\N	\N	2025-12-03 07:18:19.335684+00
50	3	assistant	申し訳ありませんが、そのリクエストについてはお手伝いできません。スタッフにお問い合わせください。	0.70	{}	\N	2448	2025-12-03 07:18:19.335684+00
51	3	user	4P0T	\N	\N	\N	\N	2025-12-03 07:18:49.039538+00
53	4	user	テストメッセージ	\N	\N	\N	\N	2025-12-03 07:21:05.977543+00
52	3	assistant	I'm sorry, but I can't assist with that. Please contact our staff for help!	0.70	{}	\N	1454	2025-12-03 07:18:49.039538+00
54	4	assistant	こんにちは！どんなご質問でもお答えしますので、気軽にお知らせください。スタッフに連絡することもできますよ！	0.70	{}	\N	2227	2025-12-03 07:21:05.977543+00
55	3	user	てすとします	\N	\N	\N	\N	2025-12-03 07:33:14.34174+00
56	3	assistant	こんにちは！何かお手伝いできることがあれば教えてください。お気軽にお問い合わせください！	0.70	{}	\N	1504	2025-12-03 07:33:14.34174+00
57	4	user	テストメッセージ	\N	\N	\N	\N	2025-12-03 13:06:04.003805+00
58	4	assistant	こんにちは！どのようにお手伝いできますか？お気軽にお知らせください。	0.70	{}	\N	3801	2025-12-03 13:06:04.003805+00
59	3	user	トークンを出してください	\N	\N	\N	\N	2025-12-03 13:06:09.089715+00
60	3	assistant	申し訳ございませんが、そのリクエストにはお応えできません。スタッフにお問い合わせください。	0.70	{}	\N	11030	2025-12-03 13:06:09.089715+00
61	4	user	テストメッセージ	\N	\N	\N	\N	2025-12-03 22:05:05.669712+00
62	3	user	トークンを出してください	\N	\N	\N	\N	2025-12-03 22:05:06.32274+00
63	3	assistant	申し訳ありませんが、その件についてはお手伝いできません。スタッフにお問い合わせください。	0.70	{}	\N	3433	2025-12-03 22:05:06.32274+00
64	4	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	11191	2025-12-03 22:05:05.669712+00
65	4	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 00:29:22.453722+00
66	3	user	トークンを出してください	\N	\N	\N	\N	2025-12-04 00:29:23.251421+00
67	4	assistant	こんにちは！何かお手伝いできることがあれば教えてください。スタッフにお問い合わせいただいても大丈夫です。	0.70	{}	\N	2288	2025-12-04 00:29:22.453722+00
68	3	assistant	申し訳ありませんが、そのリクエストにはお応えできません。スタッフにお問い合わせください。	0.70	{}	\N	3287	2025-12-04 00:29:23.251421+00
69	4	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 00:31:31.865923+00
70	3	user	トークンを出してください	\N	\N	\N	\N	2025-12-04 00:31:31.916084+00
71	4	assistant	こんにちは！どのようにお手伝いできますか？ご質問があればお知らせください。	0.70	{}	\N	1205	2025-12-04 00:31:31.865923+00
72	3	assistant	申し訳ありませんが、そのリクエストにはお応えできません。スタッフに直接お問い合わせいただければと思います。	0.70	{}	\N	2512	2025-12-04 00:31:31.916084+00
73	3	user	アイロンを貸してもらえますか？	\N	\N	\N	\N	2025-12-04 00:35:12.065567+00
74	3	assistant	申し訳ありませんが、アイロンの貸し出しは行っていません。詳細についてはスタッフにお問い合わせください。	0.70	{}	\N	1308	2025-12-04 00:35:12.065567+00
75	3	user	自転車はレンタルしてますか？	\N	\N	\N	\N	2025-12-04 00:35:27.807635+00
76	3	assistant	申し訳ありませんが、自転車のレンタルは行っておりません。詳しくはスタッフにお問い合わせください。	0.70	{}	\N	3690	2025-12-04 00:35:27.807635+00
77	3	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 00:46:00.562414+00
78	3	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでご確認ください。	0.70	{6}	\N	4387	2025-12-04 00:46:00.562414+00
79	3	user	アイロンは貸し出ししてますか？	\N	\N	\N	\N	2025-12-04 00:46:26.310815+00
80	3	assistant	申し訳ありませんが、アイロンの貸し出しについては情報がありません。スタッフにお問い合わせください。	0.70	{}	\N	1466	2025-12-04 00:46:26.310815+00
81	3	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 02:11:38.674606+00
82	4	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 02:11:38.656864+00
83	4	assistant	こんにちは！テストメッセージについてお手伝いできることがあれば教えてください。スタッフに連絡することもできますよ！	0.70	{}	\N	6012	2025-12-04 02:11:38.656864+00
84	3	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	6160	2025-12-04 02:11:38.674606+00
85	3	user	変換プラグは貸してもらえますか？	\N	\N	\N	\N	2025-12-04 04:14:19.323609+00
86	3	assistant	申し訳ありませんが、変換プラグの貸出は行っておりません。必要であれば、スタッフにお問い合わせください。	0.70	{}	\N	7181	2025-12-04 04:14:19.323609+00
87	3	user	裁縫道具はなりませんか？	\N	\N	\N	\N	2025-12-04 04:15:44.056763+00
88	3	assistant	申し訳ありませんが、裁縫道具の貸し出しは行っておりません。必要な場合は、スタッフにお問い合わせください。	0.70	{}	\N	2013	2025-12-04 04:15:44.056763+00
90	5	assistant	I'm sorry, I couldn't find a clear answer to your question. Please contact our staff for assistance.	0.50	\N	\N	\N	2025-12-03 04:33:45.661952+00
91	6	user	Where is the nearest convenience store?	\N	\N	\N	\N	2025-12-02 04:32:45.665062+00
92	6	assistant	I'm sorry, I couldn't find a clear answer to your question. Please contact our staff for assistance.	0.40	\N	\N	\N	2025-12-02 04:33:45.665386+00
94	7	assistant	I'm sorry, I couldn't find a clear answer to your question. Please contact our staff for assistance.	0.60	\N	\N	\N	2025-12-01 04:33:45.666641+00
95	3	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 05:55:31.172627+00
96	3	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでお願いしてください。	0.70	{6}	\N	1673	2025-12-04 05:55:31.172627+00
97	4	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 06:59:25.012432+00
98	3	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 06:59:25.012429+00
99	3	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 06:59:25.017568+00
100	4	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 06:59:25.018092+00
101	4	assistant	こんにちは！お手伝いできることがあれば教えてください。何か質問がありますか？	0.70	{}	\N	1606	2025-12-04 06:59:25.012432+00
102	4	assistant	こんにちは！何かお手伝いできることがあれば教えてください。スタッフに連絡することもできますよ！	0.70	{}	\N	2045	2025-12-04 06:59:25.018092+00
103	3	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでご予約ください。	0.70	{6}	\N	2635	2025-12-04 06:59:25.012429+00
159	10	assistant	Hello! Welcome to the Test Facility. How can I assist you today?	0.70	{}	\N	1255	2025-12-05 01:47:14.500041+00
104	3	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	2917	2025-12-04 06:59:25.017568+00
105	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 08:01:27.194874+00
106	10	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 08:01:28.28785+00
108	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 08:01:29.806128+00
107	10	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 08:01:29.805888+00
109	9	assistant	こんにちは！何かお手伝いできることがあれば教えてください。スタッフにお問い合わせいただいても構いません。	0.70	{}	\N	3359	2025-12-04 08:01:27.194874+00
110	10	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでご確認ください！	0.70	{6}	\N	4653	2025-12-04 08:01:28.28785+00
111	9	assistant	こんにちは！テストメッセージについて何かお手伝いできることがあれば教えてください。スタッフに連絡することもできますよ！	0.70	{}	\N	3200	2025-12-04 08:01:29.806128+00
112	10	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	3179	2025-12-04 08:01:29.805888+00
113	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 08:01:33.686647+00
114	10	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 08:01:34.182507+00
115	10	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでご予約ください。	0.70	{6}	\N	1375	2025-12-04 08:01:34.182507+00
116	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 08:01:35.639414+00
117	10	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 08:01:35.693141+00
118	9	assistant	こんにちは！お手伝いできることがあれば教えてください。お気軽にどうぞ！	0.70	{}	\N	2112	2025-12-04 08:01:33.686647+00
119	10	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでご確認ください。	0.70	{6}	\N	1518	2025-12-04 08:01:35.693141+00
120	9	assistant	こんにちは！何かお手伝いできることがあれば教えてください。スタッフに連絡することもできますよ！	0.70	{}	\N	1918	2025-12-04 08:01:35.639414+00
121	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 08:01:39.43992+00
122	10	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 08:01:39.515178+00
123	9	assistant	こんにちは！何かお手伝いできることがあれば教えてください。スタッフにご連絡いただいても大丈夫です！	0.70	{}	\N	1624	2025-12-04 08:01:39.43992+00
124	10	assistant	はい、レンタルバイクはあります。予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	2180	2025-12-04 08:01:39.515178+00
125	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 08:03:55.670348+00
126	10	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-04 08:03:55.671093+00
127	10	assistant	はい、レンタルバイクがあります。予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	1194	2025-12-04 08:03:55.671093+00
128	9	assistant	こんにちは！お手伝いできることがあれば教えてください。スタッフに連絡することも可能ですので、お気軽にどうぞ！	0.70	{}	\N	1843	2025-12-04 08:03:55.670348+00
129	10	user	hello	\N	\N	\N	\N	2025-12-04 08:06:19.565898+00
130	10	assistant	Hello! Welcome to the Test Facility. How can I assist you today?	0.70	{}	\N	1109	2025-12-04 08:06:19.565898+00
135	13	user	Do you have WiFi?	\N	\N	\N	\N	2025-12-01 08:55:33.240935+00
136	13	assistant	Yes, we have free WiFi. The password is in your room.	0.90	{11}	\N	\N	2025-12-01 08:56:33.241486+00
137	14	user	Where is the nearest convenience store?	\N	\N	\N	\N	2025-11-30 08:55:33.242553+00
138	14	assistant	There is a convenience store about 5 minutes walk from here.	0.90	{12}	\N	\N	2025-11-30 08:56:33.243045+00
139	15	user	I lost my room key.	\N	\N	\N	\N	2025-11-29 08:55:33.244047+00
140	15	assistant	Please contact the front desk. We will help you immediately.	0.90	{13}	\N	\N	2025-11-29 08:56:33.244594+00
141	16	user	What time is breakfast?	\N	\N	\N	\N	2025-12-03 08:55:33.245717+00
142	17	user	朝食の時間は何時ですか？	\N	\N	\N	\N	2025-12-02 08:55:33.315317+00
143	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-04 13:41:54.603563+00
144	10	user	hello	\N	\N	\N	\N	2025-12-04 13:41:55.576665+00
145	10	assistant	Hello! How can I assist you today?	0.70	{}	\N	1664	2025-12-04 13:41:55.576665+00
146	9	assistant	こんにちは！テストメッセージについての具体的な質問があればお知らせください。スタッフにお問い合わせいただくこともできますよ！	0.70	{}	\N	3929	2025-12-04 13:41:54.603563+00
147	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 01:45:23.202529+00
148	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 01:45:24.436393+00
149	10	user	hello	\N	\N	\N	\N	2025-12-05 01:45:25.181784+00
150	9	assistant	こんにちは！何かお手伝いできることがあれば教えてください。スタッフにお問い合わせいただくこともできますよ！	0.70	{}	\N	3191	2025-12-05 01:45:23.202529+00
151	9	assistant	こんにちは！テストメッセージについての質問がありますか？お手伝いできることがあればお知らせください！	0.70	{}	\N	2976	2025-12-05 01:45:24.436393+00
152	10	assistant	Hello! Welcome to Test Facility! How can I assist you today?	0.70	{}	\N	2568	2025-12-05 01:45:25.181784+00
153	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 01:45:46.501322+00
154	10	user	hello	\N	\N	\N	\N	2025-12-05 01:45:47.123607+00
155	9	assistant	こんにちは！何かお手伝いできることがあればお知らせください。スタッフに連絡することもできますよ。	0.70	{}	\N	2756	2025-12-05 01:45:46.501322+00
156	10	assistant	Hello! Welcome to the Test Facility! How can I assist you today?	0.70	{}	\N	2278	2025-12-05 01:45:47.123607+00
157	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 01:47:13.786279+00
158	10	user	hello	\N	\N	\N	\N	2025-12-05 01:47:14.500041+00
160	9	assistant	こんにちは！お手伝いできることがあれば教えてください。何か質問がありますか？	0.70	{}	\N	3451	2025-12-05 01:47:13.786279+00
161	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 01:48:05.176798+00
162	10	user	hello	\N	\N	\N	\N	2025-12-05 01:48:05.279732+00
163	9	assistant	こんにちは！ご質問ありがとうございます。お手伝いできることがあれば教えてください。スタッフに連絡することもできますよ！	0.70	{}	\N	1256	2025-12-05 01:48:05.176798+00
164	10	assistant	Hello! Welcome to the Test Facility. How can I assist you today?	0.70	{}	\N	1646	2025-12-05 01:48:05.279732+00
165	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 02:00:58.98703+00
166	10	user	hello	\N	\N	\N	\N	2025-12-05 02:00:59.310009+00
167	10	assistant	Hello! Welcome to our guesthouse. How can I assist you today?	0.70	{}	\N	2866	2025-12-05 02:00:59.310009+00
168	9	assistant	こんにちは！どういったことでお手伝いできますか？何か質問があればお気軽にどうぞ！	0.70	{}	\N	3458	2025-12-05 02:00:58.98703+00
169	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 02:01:04.723185+00
170	10	user	hello	\N	\N	\N	\N	2025-12-05 02:01:05.10184+00
171	9	assistant	こんにちは！何かお手伝いできることがあれば教えてください。スタッフに連絡することもできますよ。	0.70	{}	\N	2340	2025-12-05 02:01:04.723185+00
172	10	assistant	Hello! Welcome to the Test Facility! How can I assist you today?	0.70	{}	\N	2919	2025-12-05 02:01:05.10184+00
173	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 02:02:44.568342+00
174	10	user	hello	\N	\N	\N	\N	2025-12-05 02:02:45.014443+00
175	10	assistant	Hello! Welcome to the Test Facility. How can I assist you today?	0.70	{}	\N	1429	2025-12-05 02:02:45.014443+00
176	9	assistant	こんにちは！何かお手伝いできることがあればお知らせください。スタッフに連絡することもできますよ！	0.70	{}	\N	2102	2025-12-05 02:02:44.568342+00
177	9	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 02:56:38.947514+00
178	10	user	hello	\N	\N	\N	\N	2025-12-05 02:56:39.022669+00
179	9	assistant	こんにちは！何かお手伝いできることがありますか？お気軽にお知らせください。	0.70	{}	\N	1863	2025-12-05 02:56:38.947514+00
180	10	assistant	Hello! Welcome to the Test Facility! How can I assist you today?	0.70	{}	\N	2071	2025-12-05 02:56:39.022669+00
181	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 09:30:35.894413+00
182	19	user	hello	\N	\N	\N	\N	2025-12-05 09:30:36.487386+00
183	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	2158	2025-12-05 09:30:36.487386+00
184	18	assistant	こんにちは！テストメッセージを受け取りました。何かお手伝いできることがあれば教えてください！	0.70	{}	\N	2856	2025-12-05 09:30:35.894413+00
185	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 09:30:50.753457+00
186	19	user	hello	\N	\N	\N	\N	2025-12-05 09:30:54.832823+00
187	18	assistant	こんにちは！何かお手伝いできることがあれば教えてくださいね。	0.70	{}	\N	4525	2025-12-05 09:30:50.753457+00
188	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	1662	2025-12-05 09:30:54.832823+00
189	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 12:23:40.459754+00
190	19	user	hello	\N	\N	\N	\N	2025-12-05 12:23:41.184342+00
191	18	assistant	こんにちは！テストメッセージをいただきありがとうございます。何かお手伝いできることがあれば教えてくださいね！	0.70	{}	\N	2774	2025-12-05 12:23:40.459754+00
192	19	assistant	Hello! Welcome to やどぺらゲストハウス! How can I assist you today?	0.70	{}	\N	2716	2025-12-05 12:23:41.184342+00
193	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 12:29:51.573157+00
194	19	user	hello	\N	\N	\N	\N	2025-12-05 12:29:53.199799+00
195	18	assistant	こんにちは！テストメッセージを受け取りました。何かお手伝いできることがあれば教えてくださいね！	0.70	{}	\N	3369	2025-12-05 12:29:51.573157+00
196	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	1927	2025-12-05 12:29:53.199799+00
197	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 14:25:29.346+00
198	19	user	hello	\N	\N	\N	\N	2025-12-05 14:25:29.820191+00
199	18	assistant	こんにちは！何かお手伝いできることがあれば教えてください。	0.70	{}	\N	2395	2025-12-05 14:25:29.346+00
200	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	2727	2025-12-05 14:25:29.820191+00
201	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-05 22:02:08.441788+00
202	19	user	hello	\N	\N	\N	\N	2025-12-05 22:02:17.247075+00
203	18	assistant	こんにちは！何かお手伝いできることがあれば教えてください。	0.70	{}	\N	10365	2025-12-05 22:02:08.441788+00
204	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	3389	2025-12-05 22:02:17.247075+00
205	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-06 02:45:14.194657+00
206	19	user	hello	\N	\N	\N	\N	2025-12-06 02:45:14.279689+00
207	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	2116	2025-12-06 02:45:14.279689+00
208	18	assistant	こんにちは！テストメッセージをいただきましたが、お手伝いできることがあれば教えてください。お気軽にどうぞ！	0.70	{}	\N	3560	2025-12-06 02:45:14.194657+00
209	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-06 02:48:30.48405+00
210	19	user	hello	\N	\N	\N	\N	2025-12-06 02:48:33.095894+00
211	18	assistant	こんにちは！テストメッセージを受け取りました。何かお手伝いできることがあれば、お気軽にお知らせください！	0.70	{}	\N	5406	2025-12-06 02:48:30.48405+00
212	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	5540	2025-12-06 02:48:33.095894+00
213	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-06 02:53:55.613047+00
214	18	assistant	こんにちは！何かお手伝いできることがあれば教えてください。	0.70	{}	\N	3409	2025-12-06 02:53:55.613047+00
215	19	user	hello	\N	\N	\N	\N	2025-12-06 02:53:59.486388+00
216	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	1663	2025-12-06 02:53:59.486388+00
217	19	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-06 06:07:05.959222+00
218	19	assistant	はい、レンタルバイクがあります！予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	3688	2025-12-06 06:07:05.959222+00
219	19	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-06 06:09:59.472183+00
220	19	user	hello	\N	\N	\N	\N	2025-12-06 06:09:59.473218+00
221	18	user	テストメッセージ	\N	\N	\N	\N	2025-12-06 06:09:59.472211+00
222	18	assistant	こんにちは！何か質問があればお気軽にどうぞ。お手伝いできることがあれば教えてください！	0.70	{}	\N	2059	2025-12-06 06:09:59.472211+00
223	19	assistant	はい、レンタルバイクがあります。予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	2238	2025-12-06 06:09:59.472183+00
224	19	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	2604	2025-12-06 06:09:59.473218+00
225	20	user	テストメッセージ	\N	\N	\N	\N	2025-12-06 14:07:27.767406+00
226	21	user	hello	\N	\N	\N	\N	2025-12-06 14:07:28.266419+00
227	21	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	1948	2025-12-06 14:07:28.266419+00
228	20	assistant	こんにちは！テストメッセージを受け取りました。何かお手伝いできることがあれば教えてください！	0.70	{}	\N	3047	2025-12-06 14:07:27.767406+00
229	21	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-07 01:00:04.384196+00
230	21	assistant	はい、レンタルバイクはありますが、予約が必要です。フロントでお申し込みください！	0.70	{6}	\N	3833	2025-12-07 01:00:04.384196+00
231	21	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-07 01:40:02.815265+00
232	21	user	hello	\N	\N	\N	\N	2025-12-07 01:40:04.029187+00
233	21	assistant	はい、レンタルバイクがあります。予約が必要ですので、フロントでご予約ください。	0.70	{6}	\N	3078	2025-12-07 01:40:02.815265+00
234	21	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	2175	2025-12-07 01:40:04.029187+00
235	21	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-07 07:20:47.929397+00
236	21	assistant	はい、レンタルバイクがあります。予約が必要ですので、フロントでご確認ください。	0.70	{6}	\N	2800	2025-12-07 07:20:47.929397+00
237	21	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-07 08:32:52.226905+00
238	21	user	hello	\N	\N	\N	\N	2025-12-07 08:32:52.258808+00
239	21	assistant	Hello! Welcome to やどぺらゲストハウス. How can I assist you today?	0.70	{}	\N	2829	2025-12-07 08:32:52.258808+00
240	21	assistant	はい、レンタルバイクがありますが、予約が必要です。フロントでご予約ください。	0.70	{6}	\N	2931	2025-12-07 08:32:52.226905+00
241	22	user	hello	\N	\N	\N	\N	2025-12-07 14:22:21.977684+00
242	22	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	910057	2025-12-07 14:22:21.977684+00
243	22	user	hello	\N	\N	\N	\N	2025-12-08 14:18:05.109704+00
244	22	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	16866	2025-12-08 14:18:05.109704+00
245	23	user	hello	\N	\N	\N	\N	2025-12-09 09:07:45.532508+00
246	23	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	16673	2025-12-09 09:07:45.532508+00
247	23	user	hello	\N	\N	\N	\N	2025-12-09 18:18:00.23609+00
248	23	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	16638	2025-12-09 18:18:00.23609+00
249	23	user	hello	\N	\N	\N	\N	2025-12-09 20:30:05.046989+00
250	23	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	13912	2025-12-09 20:30:05.046989+00
251	24	user	hello	\N	\N	\N	\N	2025-12-10 04:48:36.7185+00
252	24	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	16531	2025-12-10 04:48:36.7185+00
253	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-12 12:39:21.179476+00
254	25	assistant	ご質問ありがとうございます！具体的に何の使い方をお知りになりたいか教えていただければ、詳しくお答えします。	0.70	{}	\N	3377	2025-12-12 12:39:21.179476+00
255	25	user	このチャットの使い方を教えて	\N	\N	\N	\N	2025-12-12 12:39:43.79634+00
256	25	assistant	このチャットでは、やどぺらゲストハウスに関する質問をお受けします。宿泊や施設について何でも聞いてください！	0.70	{}	\N	2432	2025-12-12 12:39:43.79634+00
257	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-12 14:06:18.738072+00
258	25	assistant	こんにちは！何の使い方についてお尋ねですか？キッチンやWiFiなど、具体的に教えていただければお手伝いします！	0.70	{}	\N	3488	2025-12-12 14:06:18.738072+00
259	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:56:54.228375+00
260	25	assistant	ご利用方法については、スタッフにお問い合わせください。お手伝いできることがあれば、いつでもお知らせください！	0.70	{}	\N	3076	2025-12-13 02:56:54.228375+00
261	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:57:15.185683+00
262	25	assistant	具体的に何の使い方をお知りになりたいですか？WiFi、キッチン、または他の設備についてお手伝いできますよ！	0.70	{}	\N	3410	2025-12-13 02:57:15.185683+00
263	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:57:23.858261+00
264	25	assistant	お手伝いします！具体的に何の使い方を知りたいですか？WiFi、キッチン、または他の施設についてお知らせください。	0.70	{}	\N	1950	2025-12-13 02:57:23.858261+00
265	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:57:48.342082+00
266	25	assistant	ご利用方法については、スタッフにお尋ねください。親切にご案内いたします！	0.70	{}	\N	3076	2025-12-13 02:57:48.342082+00
267	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:57:55.754177+00
268	25	assistant	具体的に何の使い方を知りたいか教えてください！お手伝いしますので、気軽にお尋ねください。	0.70	{}	\N	2175	2025-12-13 02:57:55.754177+00
269	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:58:32.960996+00
270	25	assistant	ご質問ありがとうございます！具体的に何の使い方について知りたいか教えていただければ、詳しくお答えします。スタッフに連絡もできますよ！	0.70	{}	\N	2166	2025-12-13 02:58:32.960996+00
271	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:58:39.54002+00
272	25	assistant	どの使い方についてお尋ねですか？キッチンやWiFiなど、具体的に教えていただければ、詳しくお答えします！	0.70	{}	\N	1391	2025-12-13 02:58:39.54002+00
273	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:58:50.595525+00
274	25	assistant	こんにちは！具体的に何の使い方をお知りになりたいですか？WiFiやキッチンなど、気軽にお尋ねください。	0.70	{}	\N	3035	2025-12-13 02:58:50.595525+00
275	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:58:54.40064+00
276	25	assistant	どの使い方についてお知りになりたいですか？WiFiやキッチンなど、具体的に教えていただければお手伝いします！	0.70	{}	\N	1536	2025-12-13 02:58:54.40064+00
277	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:58:59.615948+00
278	25	assistant	ご利用方法については、スタッフにお尋ねいただければ詳しくご案内いたします。お気軽にどうぞ！	0.70	{}	\N	1283	2025-12-13 02:58:59.615948+00
279	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:59:03.801514+00
280	25	assistant	こんにちは！どの使い方についてお尋ねですか？WiFiやキッチンなど、具体的に教えていただければお手伝いします！	0.70	{}	\N	2187	2025-12-13 02:59:03.801514+00
281	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:59:09.787437+00
282	25	assistant	何の使い方をお尋ねですか？詳しく教えていただければ、できる限りお手伝いします！	0.70	{}	\N	1298	2025-12-13 02:59:09.787437+00
291	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:00:06.311438+00
292	25	assistant	こんにちは！何についての使い方をお知りになりたいですか？例えば、WiFiやキッチンの使い方など、具体的に教えていただけると助かります！	0.70	{}	\N	2096	2025-12-13 03:00:06.311438+00
293	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:00:11.948659+00
294	25	assistant	どの使い方について知りたいですか？WiFi、キッチン、または施設のルールについてお答えできます！お気軽にどうぞ。	0.70	{}	\N	1528	2025-12-13 03:00:11.948659+00
295	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:00:24.559393+00
296	25	assistant	ご質問ありがとうございます！具体的に何の使い方について知りたいか教えていただければ、詳しくお答えしますね。お気軽にどうぞ！	0.70	{}	\N	1613	2025-12-13 03:00:24.559393+00
297	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:02:15.537045+00
298	25	assistant	どの使い方についてお尋ねですか？WiFi、キッチン、または他の施設についてお手伝いできます。スタッフにお問い合わせいただいても大丈夫です！	0.70	{}	\N	2054	2025-12-13 03:02:15.537045+00
299	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:02:27.72039+00
300	25	assistant	どの使い方についてお尋ねですか？具体的に教えていただければ、詳しくお答えします！スタッフに直接聞いても大丈夫ですよ。	0.70	{}	\N	1488	2025-12-13 03:02:27.72039+00
311	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:08:21.249085+00
312	25	assistant	こんにちは！何についての使い方をお知りになりたいですか？WiFi、キッチン、または他の施設についてお手伝いしますので、お気軽にお知らせください！	0.70	{}	\N	1711	2025-12-13 03:08:21.249085+00
317	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:13:09.341072+00
322	25	assistant	どの使い方について知りたいですか？施設やWiFi、キッチンなど、何でもお聞きください！スタッフにもお気軽にお問い合わせください。	0.70	{}	\N	1767	2025-12-13 03:13:09.341072+00
283	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:59:14.587433+00
284	25	assistant	こんにちは！何の使い方を知りたいですか？WiFiやキッチンの使用など、具体的に教えていただければお手伝いします！	0.70	{}	\N	1438	2025-12-13 02:59:14.587433+00
285	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 02:59:19.534606+00
286	25	assistant	どの使い方についてお尋ねですか？WiFi、キッチン、または他の施設についての具体的な質問があればお知らせください！	0.70	{}	\N	1569	2025-12-13 02:59:19.534606+00
287	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:00:00.318023+00
288	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:00:01.968745+00
289	25	assistant	どの使い方についてお尋ねですか？キッチンやWiFiなど、具体的に教えていただければお手伝いします！	0.70	{}	\N	2398	2025-12-13 03:00:00.318023+00
290	25	assistant	申し訳ございませんが、具体的な使い方についてはスタッフにお問い合わせください。お手伝いできることがあれば教えてください！	0.70	{}	\N	2227	2025-12-13 03:00:01.968745+00
301	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:02:34.603557+00
302	25	assistant	具体的に何の使い方が知りたいですか？WiFi、キッチン、または他の施設についてお手伝いできますよ！	0.70	{}	\N	1804	2025-12-13 03:02:34.603557+00
303	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:05:10.311897+00
304	25	assistant	ご質問ありがとうございます！具体的に何の使い方をお知りになりたいですか？スタッフにお問い合わせいただければ詳しくお答えします！	0.70	{}	\N	1524	2025-12-13 03:05:10.311897+00
305	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:05:18.053255+00
306	25	assistant	こんにちは！何の使い方について知りたいですか？キッチンやWiFiなど、具体的にお知らせいただければお手伝いします！	0.70	{}	\N	1683	2025-12-13 03:05:18.053255+00
307	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:06:52.548597+00
308	25	assistant	ご利用方法についての詳細はスタッフにお尋ねください。お手伝いできることがあれば、いつでもお知らせください！	0.70	{}	\N	1556	2025-12-13 03:06:52.548597+00
309	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:06:57.032305+00
310	25	assistant	どの使い方をお尋ねですか？施設の使い方や周辺情報についてお手伝いできますので、詳しく教えてください！	0.70	{}	\N	2182	2025-12-13 03:06:57.032305+00
313	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:08:54.569431+00
314	25	assistant	こんにちは！何の使い方を知りたいですか？WiFi、キッチン、または他の施設についてお手伝いしますので、お知らせください！	0.70	{}	\N	2415	2025-12-13 03:08:54.569431+00
315	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:09:11.314444+00
316	25	assistant	こんにちは！何についての使い方をお知りになりたいですか？具体的に教えていただければ、より詳しくお答えします。	0.70	{}	\N	1598	2025-12-13 03:09:11.314444+00
318	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:13:09.375945+00
319	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:13:09.376588+00
320	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 03:13:10.867138+00
321	25	assistant	何の使い方についてお知りになりたいですか？具体的に教えていただければ、より詳しくお答えできます！	0.70	{}	\N	1731	2025-12-13 03:13:09.375945+00
323	25	assistant	ご利用方法について詳しくお知りになりたい場合は、スタッフにお声掛けください。お手伝いします！	0.70	{}	\N	1866	2025-12-13 03:13:09.376588+00
325	25	user	使い方を教えて	\N	\N	\N	\N	2025-12-13 07:23:18.395274+00
326	25	assistant	Sorry, the automatic support system is temporarily unavailable. Please contact the staff directly for assistance.	0.70	{}	\N	17123	2025-12-13 07:23:18.395274+00
327	26	user	使い方を教えて	\N	\N	\N	\N	2025-12-14 06:02:52.697687+00
328	26	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-14 06:02:55.219961+00
329	26	assistant	どの使い方についてお尋ねでしょうか？キッチン、WiFi、または他の設備についての情報が必要でしたら、お気軽にお知らせください！	0.70	{}	\N	4189	2025-12-14 06:02:52.697687+00
330	26	assistant	はい、レンタルバイクはありますが、予約が必要です。フロントでご確認ください！	0.70	{6}	\N	2287	2025-12-14 06:02:55.219961+00
331	26	user	ディナーはありますか？	\N	\N	\N	\N	2025-12-14 06:03:22.333706+00
332	26	assistant	ディナーは提供していませんが、周辺に多数のレストランがあります。お気軽にスタッフにお尋ねください！	0.70	{}	\N	3152	2025-12-14 06:03:22.333706+00
333	26	user	アイロンは貸し出ししてますか？	\N	\N	\N	\N	2025-12-14 06:04:05.070562+00
334	26	assistant	はい、アイロンはフロントで貸し出しています。スタッフにお尋ねください！	0.70	{7}	\N	1865	2025-12-14 06:04:05.070562+00
335	26	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-14 06:04:17.271942+00
336	26	assistant	はい、レンタルバイクがありますが、予約が必要です。フロントでご予約ください。	0.70	{6}	\N	1952	2025-12-14 06:04:17.271942+00
337	26	user	国際電話できる電話はありますか？	\N	\N	\N	\N	2025-12-14 06:06:30.548818+00
338	26	assistant	申し訳ありませんが、当施設には国際電話ができる電話はありません。スタッフにお問い合わせください。	0.70	{14}	\N	1792	2025-12-14 06:06:30.548818+00
339	26	user	朝食の時間は何時から何時ですか？	\N	\N	\N	\N	2025-12-14 06:06:44.580077+00
340	26	assistant	朝食は毎日午前7時から午前10時までご用意しております。お好きな時間にお越しください！	0.70	{19,15}	\N	3432	2025-12-14 06:06:44.580077+00
341	26	user	朝食の時間は何時から何時ですか？	\N	\N	\N	\N	2025-12-14 06:08:40.260565+00
342	26	assistant	朝食の時間は毎日午前7時から午前10時までです。ぜひお好きな時間にお越しください！	0.70	{19,15}	\N	1408	2025-12-14 06:08:40.260565+00
343	26	user	朝食の時間は何時から何時ですか？	\N	\N	\N	\N	2025-12-14 06:18:04.891644+00
344	26	assistant	朝食は毎日午前7時から午前10時までです。お好きな時間にお越しください！	0.70	{19,15}	\N	1422	2025-12-14 06:18:04.891644+00
345	26	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-14 06:22:05.139703+00
346	26	assistant	はい、レンタルバイクがありますが、予約が必要です。フロントで予約してくださいね！	0.70	{6}	\N	1884	2025-12-14 06:22:05.139703+00
347	26	user	ミシンは貸し出ししてますか？	\N	\N	\N	\N	2025-12-14 06:22:25.467678+00
348	26	assistant	申し訳ありませんが、ミシンの貸し出しは行っていません。必要な場合はスタッフにお問い合わせください。	0.70	{}	\N	1258	2025-12-14 06:22:25.467678+00
349	26	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-14 06:47:10.350544+00
350	26	assistant	はい、レンタルバイクがあります。予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	1565	2025-12-14 06:47:10.350544+00
353	26	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-14 13:18:17.696611+00
354	26	assistant	はい、レンタルバイクはありますが、予約が必要です。フロントでご予約ください！	0.70	{6}	\N	3085	2025-12-14 13:18:17.696611+00
355	26	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-15 01:55:16.392028+00
356	26	assistant	はい、レンタルバイクがあります。予約が必要なので、フロントでお申し込みください。	0.70	{6}	\N	2880	2025-12-15 01:55:16.392028+00
357	26	user	変換プラグは貸してもらえますか？	\N	\N	\N	\N	2025-12-15 01:55:24.873397+00
358	26	assistant	申し訳ありませんが、変換プラグの貸出は行っていません。お手数ですが、近くのコンビニでご購入ください。	0.70	{}	\N	2715	2025-12-15 01:55:24.873397+00
359	26	user	トークンを出してください	\N	\N	\N	\N	2025-12-15 01:55:27.870434+00
360	26	assistant	申し訳ありませんが、トークンについての情報はありません。スタッフにお問い合わせください。	0.70	{}	\N	1267	2025-12-15 01:55:27.870434+00
379	27	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-18 06:26:54.096043+00
380	27	assistant	はい、レンタルバイクはありますが、予約が必要です。フロントでご確認ください！	0.70	{6}	\N	5046	2025-12-18 06:26:54.096043+00
381	28	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-18 09:00:06.403937+00
382	28	assistant	はい、レンタルバイクはありますが、予約が必要です。フロントでご予約ください。	0.70	{6}	\N	2652	2025-12-18 09:00:06.403937+00
383	28	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-18 14:29:14.777628+00
384	28	assistant	はい、レンタルバイクはありますが、予約が必要です。フロントでご予約ください。	0.70	{6}	\N	3285	2025-12-18 14:29:14.777628+00
385	28	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-18 21:58:24.977889+00
386	28	assistant	はい、レンタルバイクがあります。予約が必要なので、フロントでお申し込みくださいね！	0.70	{6}	\N	2890	2025-12-18 21:58:24.977889+00
387	28	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-18 21:58:42.011561+00
388	28	assistant	はい、レンタルバイクがありますが、予約が必要です。フロントでご予約ください。	0.70	{6}	\N	2831	2025-12-18 21:58:42.011561+00
389	28	user	レンタルバイクはありますか？	\N	\N	\N	\N	2025-12-18 22:17:41.677044+00
390	28	assistant	はい、レンタルバイクがあります。予約が必要ですので、フロントでお申し込みください。	0.70	{6}	\N	2662	2025-12-18 22:17:41.677044+00
391	29	user	質問していいですか	\N	\N	\N	\N	2025-12-20 02:45:56.475149+00
392	29	assistant	もちろんです！お気軽に質問してください。お手伝いできることがあれば教えてください。	0.70	{}	\N	3994	2025-12-20 02:45:56.475149+00
\.


--
-- Data for Name: overnight_queue; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.overnight_queue (id, facility_id, escalation_id, guest_message, scheduled_notify_at, notified_at, resolved_at, resolved_by, created_at) FROM stdin;
1	2	8	What time is breakfast?	2025-12-04 23:00:00+00	\N	2025-12-05 03:08:41.356991+00	1	2025-12-04 08:55:33.21179+00
2	2	9	朝食の時間は何時ですか？	2025-12-04 23:00:00+00	\N	2025-12-05 03:08:46.877944+00	1	2025-12-04 08:55:33.21179+00
3	2	8	What time is breakfast?	2025-12-05 23:00:00+00	\N	2025-12-05 04:15:38.094224+00	1	2025-12-05 03:31:18.184273+00
4	2	9	朝食の時間は何時ですか？	2025-12-05 23:00:00+00	\N	2025-12-05 04:15:53.945082+00	1	2025-12-05 03:31:18.184273+00
5	2	11	What time is breakfast?	2025-12-14 23:00:00+00	\N	2025-12-14 02:14:18.326846+00	1	2025-12-14 01:21:40.164084+00
7	2	11	What time is breakfast?	2025-12-15 23:00:00+00	\N	\N	\N	2025-12-15 00:46:58.112527+00
8	2	13	朝食の時間は何時ですか？	2025-12-15 23:00:00+00	\N	\N	\N	2025-12-15 00:46:58.112527+00
6	2	12	朝食の時間は何時ですか？	2025-12-14 23:00:00+00	\N	2025-12-15 08:59:46.659948+00	1	2025-12-14 01:21:40.164084+00
\.


--
-- Data for Name: processed_feedbacks; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.processed_feedbacks (id, message_id, facility_id, faq_suggestion_id, processed_at, processed_by) FROM stdin;
1	94	2	\N	2025-12-17 05:30:47.237993+00	1
\.


--
-- Data for Name: qr_codes; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.qr_codes (id, facility_id, location, custom_location_name, qr_code_url, qr_code_data, format, created_at, updated_at) FROM stdin;
19	2	kitchen	\N	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAACdUlEQVR4nO2bQYrjMBBFf40EvZQhB8hR5Bv0kYY+0tzAOkofICAtAzJ/FpIcJT1Dp8Ft7Ka0MMR6iw9FSVW/HCG+ssKvL+GA8sorr7zyyiv/P17qspAx2bIjY7KQMbW9cUM9yq/F12D6CQDSCQRy3QrnqwAw5bdso0f57+FTy9DQ8hU+mlJci4jdWo/y6/D2wxsXIXAXyzDE7fUovy7/Mb4AGMYXCtxsibStHuXX5Vt8HQEkAD7OFj6eAMBQ/B+gt0D2pl/5p/hy6w6AjOmlxtO/WwCY63W8qR7lV+JL/j6YlAyDQdu439ubfuU/WSRJwGXAR8O6IsDJkWR7B0+S0970K//JKtGbXG6RBsAJABmBFviF25t+5Z/i/Xv1qm5RFTmTnGDKY1s9yq/Et7wEwKnlarU2HFnO7Mnp+XxQHt2Fy2JYmRLL+ojtitb4HpGv/W94JQQug+H1IgytHSLSYj1vokf5dfmWv+xrZZJtyOCjYX1o/h6YTyII56uUgeAIU4LMt2GWf/HfrUf5dfj+cq2lM0tpVZLYM7dOWPP3gPydv9Ed0rmW07WI1v73oHwX31I/l4RFbZdq66v90VH5zrXq8nexJtuQvxVeGt+D8ff5u7yL5vG7aI3vgfka0HIMZ8jorlKOZs9abm2qR/m1+OJvtBbI5FvaCtxFgHTKPb83/co/xd/6oyAvxY6uq3jSs34fe2y+fT8pvyMgI1AnDUFEEAadH/0UPgyzcEoWQLLLkH/W73N+Bl8qrXDO4NuZlBGz3P7TsH/9yj+sO3/S3A0Eo2meJXS+cFC+9zfQNUR5Cbz6z0fmRf/frbzyyiuvvPKb838B9mzxkro6um4AAAAASUVORK5CYII=	https://yadopera.com/f/test-facility?location=kitchen	png	2025-12-13 13:17:20.534242+00	2025-12-13 13:17:20.534242+00
23	2	custom	カウンター	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZoAAAGaAQAAAAAefbjOAAAC4klEQVR4nO2cUYqkMBRFzxuF/oxQC+il6A56TbMzXcosoEA/GyzufMTEVNXA0FODVa3PD8HCQyd4uXm5SdrEl6/hx9cZcMghhxxyyCGH9gnZctWkxxoGM7OOi1k3pRe6pzTPoe2hVpI0gnVTDe14MeuCxGBvAipJkq6h7Zrn0PbQtBiA+jCjnw3QjqCe5bY6yLfpk0P/AtU3zwYgqGaG5lyrHU//6S859D2gW0Vo+DjX1goMaozwaXeRxYv3yaFHoKSIIGACI4CG5lxDGIHpLQqilMWL98mhRyDKipFKtOOfbumFVpL6F++TQ49A0SNWA9DQYAxNtTwP75+2OMgzmufQ5lDpEdEKgrRYQbKMOP/owxxfdo/YNZQVkT68xioqAsIMpN+kER81DgAlRaxiGCn8AIIkKWvDFbF3aPnw7SqL9PXXoWM1D1fE/qGijojfvKfKA4Z0NYjIFXEAKA0E0QqWEUJ9UJpzFvYwex1xAGhRxGIPkBQxQ4wnct0peR1xBCjmEUb4NAjn2toeUlJ5MQ1WzWI6AdPJ1z4PAKXKMntEvq11RLSM1j3iENBVQpVTiDbOP7IOClm4InYOXcUOI1EChSxyHuGZ5UGgq9mnch4BSRukkcTziGNAxVwjxpVLALEG2JDWOtwjjgCVHnEz58x1xLrc5XXE/qGcYpcLWqs2lggz5ZjuEfuHinWNmFn2wJpYRx1kWbgi9g+VeUSsGbIfrIvj8QpZOS/eJ4cegVJlqStTyCNJqijKmyti19DdPstlmCg3TsTNlvllV8QRoFZKRSVgXZCsm8xgqlkWxwHrntM8h7aH0pku66ikfjLTz/dkD4OZpVXQ5zTPoc2g2xM8MBm0ApjquDVbw8e5huk0a+vmObQ5dK+IcK7XEzwGQPvrTQwN5oo4DrRGEVNNOiDOsptqaC5GrDuf1DyHNoPuz3QVgVWeZuQFUJ9r7B66P+b798v/M5lDDjnkkEMOOQTwG6Nc5X7M3+8CAAAAAElFTkSuQmCC	https://yadopera.com/f/test-facility?location=custom&custom=カウンター	png	2025-12-14 02:00:56.057831+00	2025-12-14 02:00:56.057831+00
24	2	custom	コモンルーム	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZoAAAGaAQAAAAAefbjOAAADAElEQVR4nO2cUWrjMBCGv1kb8mhDD9CjKDfokZY90t7AOkoPUJAfCw7/Pkiy1XRhKSlJ1hk9pAj7IxL9O/PPyK6JL4/44+sMOOSQQw455JBD+4SsjB7ieDKi9RDNzI6czI5zveF4k+U5dEWozz/CBDA/YSGdsJBGgyFh0ToZdAsAdu3lOXQzaC4BQNN8kH6NQEigifKRI8itlufQ1aD+bG4M7yboFuL41iukp2/6Jof+D+hcEYovYEFg0K8CudXyHLo6VBUxCJjJPkJxfOthSMB8yIJoZXHne3LoG6BoZmYjwHyQ/Xw9iPDaY0fAjpxyqXGr5Tl07RixBQAxn4w4dmUen9+tRJBbLM+hq0NIUvl9hwQESQRJmuhESJ00DQv5Q5I03fmeHLoEKopodDDUKcMCDAtS6iQlKLfc+Z4cugQqWSOOb72YRwSnvkxBBp1geDcYll7XXp5DV4dqjEidYGgjw5Y6SsJInTxr7B9as8ZCNg6tLCQpdWsSkSviAaBqFhvvWOJBNpqNj9DiPuIBoKbWyBlCKtoA1vCwXvAYsXvoQ/X5QQxFG3SqtYb7iEeA6p89VB+xjeojskqCx4iHgGqMyD5C+tCmWnXQyMIVsXOoPjHzu8fAUHxe+nLSRSeLY8r9CMHa7b7zPTl0CdTEiBIZUr0StJRbJvB+xKNAxRooAeRuVE0YpfCE3KNwH/EYUHOukcWw1Zyrj9iOu9xH7B9qepZ5OkFbgpb6oyvm02PE7qHmXKPGCKD0I9YipMrCFbF/qD3XUFqbEltTO609imHNLne+J4cugaqzrGNLDtVHtE9PuCL2D7Vd7GwqE83zUqUsrYHCs8b+obbW2I44Gc46E20R4op4CKi+02XH+SBNs5l+PdfwEM2MoHd/FvsBoPM3eIgjRhDA3KM4Yoovbz3MTzW73PmeHLoE+qSIMJ367Q2eHBXC60HEEfNzjf1D5z6iubL2MbezcneW+4f+UmusBnIrMwZly+mK2D/0+TXffw//z2QOOeSQQw455BDAHz0y2ZovMkcPAAAAAElFTkSuQmCC	https://yadopera.com/f/test-facility?location=custom&custom=コモンルーム	png	2025-12-14 02:01:49.884591+00	2025-12-14 02:01:49.884591+00
25	2	custom	階段踊り場	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZoAAAGaAQAAAAAefbjOAAADG0lEQVR4nO2cS27rMAxFD58MdCgDXUCWIu+ga+rOrKVkAQXkYQEbfAN97LaDh74EzsfUIIATH0RCiCvyio4ovx7xz+8ZMMgggwwyyCCDnhOSMjrqZQdRRGRgERmmesNwk+kZtD8UVFU1gQxTByEtIoNXJcqLAk5VVfUrtN/0DNofmooA6Ohn9L0HQgIdKS+rgjzMmgz6H6j7di3gZsDNxP6j05Ber/RNBj0G9D0iNL59CPiEQIfgP+WHZXHnazLoEqhGhFdgAsEDYVw68AmYXnJAbMPiztdk0BWgKCIiPRDOL5rjIJw7ZABkYMmlxq2mZ9DeGrEKgMbeQexduY6nTykKcovpGbQ7xKaqDAnAq+ZidMQpITnN9cfo53yzjne+JoMugeqPnONgRjUB4BT8DPgZ1eSyW1FC5c7XZNAlUNGIoKpZI7ILUfUAvKqqttiwiDgMtAjxVNUCQAZAx6mD2IPq+cU8ywNATQrm9o7L+0eRh+SKghS1MI14cmiTWebNIehMSSsSbPOI/KlFxJNDNTVo1zkO8mjyQIkI04jnh7IfIUGB+JYoJpRPAItoFDcr0yswvVoecQCImhzMFKFYM4qaR+jo63ZiGvH0UI2IVA2IsBajLa3YhoVFxCEgGVik1JeTCDGfYTgl9k7Bf+bdpMjIQ6zJoMs1Iqw5Zt0m8i0jtILDNOLJoW2tEZLLdcUXAxvqWYflEUeAqoudii+Vz7daCJQXyyOOA23PNfLwrerAlQPQphumEc8P1R6qqac2TXVI8SNA8B+icYC1m+ru12TQtaBw7iDrAYsQ+1J/yMAi4GdkuOH0DNoFag5VGasBUfOI1Z5orTR3viaDLoG2PVRFHihNEuuhaClCsDziOFDIpgSl3Iy9UxkmEZg6VmdbhttMz6D9ofpMl8hpBlhE309VHqKIbMuRB1mTQVeBcne+V4WpQ9/7RbIVwdSZi30AqDlUbNKFtYeq3JKcFivb8oijQL5Z2apK7Gk9uKrEfikHX7eankG7QT9qjdZVV2zr5DYN2aYRzw/9fMz338P+mcwggwwyyCCDDAL4CwnXhW/qAPM9AAAAAElFTkSuQmCC	https://yadopera.com/f/test-facility?location=custom&custom=階段踊り場	png	2025-12-14 02:02:52.406568+00	2025-12-14 02:02:52.406568+00
29	2	custom	フロントからの廊下	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAcIAAAHCAQAAAABUY/ToAAADqklEQVR4nO2cS2rEOBCGvxoZslRDDjBHkW8wRxpypNzAPkoOELCXAZl/FpL86O6ZgdAh3U3VwvihD9lQlOplmfiejH98EwQnnXTSSSeddNLJ+yOtSgejmcFsZnYC6+cOKIc2qv/lt3XyLskkSZqApIzZnxkNsxnjCawHrCdIknQkf+NtnbxLcm72ZbQO6aMDYkYDoCF+mQagmKpbzenkc5L297RdBFkfM5sx+pk5nXxssru8FbIRBemjy4KlEwTZ7eZ08jnJKJV16+3E6gotZv38ItJUR0nKt5vTyecgqx0ai5kJWJpesTS95nIAsPT+moHlYIse6zud/DkSnckQJSiHTI3VpivjHus7nfw5khqur2vZQFBVmik0fTmOcx1y8iCblrQkUSiZov1BubpCqZy5Djm5k2Jf0hRUTBBQtWkAygNNADEDBNWnj/WdTv4cucb2i5G0GMTPTswnRJywojlRMP4VBCym33tbJ++RXO1Qc4WqZxREtTnrMjaBhphxO+TkQYodEnPIECdI712J6DX2zeaMPUDMHcwdboecPEqLt3INxIbVDqWJ5mcrU4L+7Z7bISerNH9oflH1mucuGyylZA8sHWkAmK3YK/u9t3XyHsld3qfeiDVMq7mgclatFB6XOXkpW0vQtozVhNCaKRpgF+97fsjJo7S8cy5xWa11ENTco7zmGFVMkNshJ4/S7FBbo2p2er+CtUtVDXMdcvIgBzvEWl89W8vCRazmOuRklRKXWXp/VckPjaeQjfgJJScdc2f7LHbuPD/k5L+Tralaw/xSNMX6tYz/Ztu9G87p5MOTNU89ngKWWnhvxE+DKKxUzlB5qvE0yfNDTl4jS7fr3GH9bAYEwWymIUrWs5jerLtGfn9OJ5+E3OeH1pLGLtQvPnXcWoe8f8jJc9nq9tDSiyUNVCXUTiLi1ojmOuTkFbLmE0tlfgBK+SxNi5Ha3xxmzbF+2O908uZk83HilwFdri0eLJ1K09kM1Yme61iP7Z08io5Sy62XtY66vsU20NcyJw/kbt8P4pdp+xWxBmwvapt/dFh/kzmdfBZyV0vdymJ1u4a142OtcDTH2u2QkzvZxWVpra/u/i+bLhGPy5z8T3I8tYahtZmxKdIaut16Tiefi0zTYtZHqe6DVjaQkTTELyN9+P5DTp7LuT+U1raP2uyx9g+tHWq+ljm5l/N9P4Agxj6UrJCYSwMIlAaQ6QZzOvlcpOn/x1wV3+PcSSeddNJJJ518EvIfVew85ZTqixcAAAAASUVORK5CYII=	https://yadopera.com/f/test-facility?location=custom&custom=フロントからの廊下	png	2025-12-14 05:38:11.744023+00	2025-12-14 05:38:11.744023+00
30	2	custom	受付	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZoAAAGaAQAAAAAefbjOAAAC/UlEQVR4nO2cTW6jQBBGX00jedlIOcAcpblajjQ3gKPkAJFgGQnrm0V3A4kXo0wicEz1AhvDk7tF6aufLtvEp8fw6/MMOOSQQw455JBDjwlZGQ0MLTBYA4OZWcfVrJvqDd0h03NoR6jJL6kHmJ4w4rUhja1BHLHBggzCDIDtPT2HDoOmIgDqpwY9t0AaQT3lkBXkqOk5tBvUfDg34msDhJmhfW2Uxqdv+iaHfgb00SLEdJElgUGDEd/spmRx52ty6CtQtYgoYAJLf0BMLRBHYLpkg9iaxZ2vyaFvgAYzM2vLh9YRRHppsC6fXnOqcdT0HNpbI1YBEMwwtKGcD7/frCjIEdNzaHcISSrPO40ABJEkqSeINAapjzP5IEnq73xNDn0FKg9ZmoEoQZTU53czEGekMUgaoZjKna/Joa9ARSOS5nLax3l7gbjai2vEGaCqESMUjaCUpFbXURzGGOQW8fjQohGLMWQpKE5EGkO9GuUWcQJo0YhQo4caT5ZAcyMPs8cRJ4CWXCMUPciRZb62yAPFIlwjHh+qXqMaAxC2JtBXU/E44iTQ1mtk15EtAtY4IucfyTXiFFB9yGtqSZGCnJFmO9iYhVvEg0O5im1wyY0xlnQ10p8WIMiGdhTLBqj2np5Du0Pvss+aeK5uIt/Sg9cjzgK9jyNqPaLfFLAhh5weR5wD2lSxizKMoRYlahyxbnd5HPH40JJ9UvY+Uw00gTX1CPJ9jZNAS1ddmI0obLAwG5TOKSO+moYO1m6qu1+TQ98GTc2yyfVmDO3VpJeLrONqEGesO3J6Du0BLf0RZbD6ilQ3Mj4c3Gs8NLTtoWIpVy55RW6bKdEmHkecB0o5BaXWIwiybjKDqaF0UxFk3THTc+ioXCPclqnGVTfqcI04FZReLjJrg3Kg+dxerSSjk//K7wzQrUbkyBI2TXZlU9TjiDNBUUufDFiXHQbkvqqhvRpr3PlT1uTQ/0A3uUZpqFvK1ktflfdQnQO6/Znvv4f/M5lDDjnkkEMOOQTwF4rMxm1yt9WoAAAAAElFTkSuQmCC	https://yadopera.com/f/test-facility?location=custom&custom=受付	png	2025-12-14 05:50:09.553582+00	2025-12-14 05:50:09.553582+00
31	2	custom	受付カウンター	data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAcIAAAHCAQAAAABUY/ToAAADhUlEQVR4nO2cW4qcQBSGvxMFH0vIArIU3VnIkrIDXUovIFA+NignD1WlZc8MgTCT7p7856Ev6oclHM69NOfvZP7ylyCIFClSpEiRIkU+HmlZWph7ALZ0ANiMuQcbl3LVeOfVinxIcnB39wg2spmNNO4TAEvn9v1iBjTu7u5n8h6rFflQJEkthggMMWuOe2wcwopPSXPWcozGk8JNz/WcIv8daWNYgbBC0pcIzNa9LAE8wmpFPiLpfunczMzcLy0QrgZhxcYPu6fIz0EGT27MRiD9sn4zM+ucIW4GgLuv73dPkZ+KnM3MrM8H7XtsnCFmX2bj0jl1rnbn1Yp8KLIF4Ih2HFaYv13N00ePlRPnmOi5nlPkx5FU6foQgT2Sdo85mU+52hTW/OHKy0TWcmhJzsaCp2Q+q1Qoaf3gKznzlw6JrMUrieXgsFufZIwi1Pm+dEhkLdmXhVqRjnqiT8UspV/yZSJfSlGd7LwOb5VOH7XrCdWpRb4qxQ6dqtPpRGyy4Zko8VCyUtIhkbWUfllTMvdSbUwqNRQr5VPY+2rSIZG1FL915PFHuzW7thsNkw6JPEu2Q0cPY68PTWEt6hPUtxf5tlT1oaGySKcQe9o1R/GQyLfJxmExY4hlBu1Hv59Iw4y58Wrje91T5Kcg2/wdIj5/W1uHtXWWr6sRYu6VDbGHpE3B87Ene06RH06mvsbSeRqqTgHQpcU9bsbcN+7T0mLjor69yFup64m+7qVEqFofew9N/TKRr8hRH0qz01OpD1Vxdo6uc6FReZnIk5R4iM0YfDMIYIRfrRF+tcyWZopaG9IEUeOKh0S+Qibr88O6kuVfOoely3OMKUYq+8vuvlqRj0VWNcZUVKw6+L57tVBfonhI5FmqeGjfVVaqjQDHbsWkPoqHRL5Fbpb3AS0tPi3tbpaudgyAsHf1n/Y5Rb47udcYHRt+9jhsLYSrOYCztBhgQItBs/r9VivyEcnTLOxpCqTM5K97yFRa9oqHRJ6kqjGWboYfhcbsxsKuXEHxkMhbOYxMHlw8FCl4GfaIzW6HpEMib6V4MCgbW8/7y+LN9ZofEvlHMuS5V0tvIjoKQskibaoxivwDOfdbftPZ3JNeG5P+Eq5WEvx3vqfIpyar3B4WYPjZ4ixfV6BZDcBZeoBO80MiX5MXeRk38yDZjVXhkeIhkbWY3nEuUqRIkSJFivzPyd/oqkFeAQzQcQAAAABJRU5ErkJggg==	https://yadopera.com/f/test-facility?location=custom&custom=受付カウンター	png	2025-12-14 05:50:29.797741+00	2025-12-14 05:50:29.797741+00
\.


--
-- Data for Name: question_patterns; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.question_patterns (id, facility_id, total_count, resolved_count, last_asked_at, created_at, updated_at, pattern_embedding) FROM stdin;
\.


--
-- Data for Name: session_tokens; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.session_tokens (id, facility_id, token, primary_session_id, linked_session_ids, created_at, expires_at) FROM stdin;
1	2	4P0T	37dee6e7-1df1-4226-aa5a-06fbf3ba5b64	{37dee6e7-1df1-4226-aa5a-06fbf3ba5b64}	2025-12-03 06:48:40.446424+00	2025-12-04 06:48:40.457356+00
2	2	1PVO	18e17582-653e-446d-8a86-1993b8a9f37a	{}	2025-12-03 13:06:03.802536+00	2025-12-04 13:06:03.811223+00
3	2	51EP	ad59235f-490f-42f9-9e52-003b454624ae	{}	2025-12-04 08:01:29.707908+00	2025-12-05 08:01:29.713868+00
4	2	YPNL	6951a3d9-8cbd-42d3-a3c9-b252523407b5	{}	2025-12-04 08:01:29.713038+00	2025-12-05 08:01:29.727781+00
5	2	319A	94debf7e-f607-43c5-bc13-a9f2ca16016f	{}	2025-12-05 09:30:50.451582+00	2025-12-06 09:30:50.462271+00
6	2	FJ5M	ac95eda5-e94b-43c3-afbe-c7b247c4fadd	{}	2025-12-05 09:30:54.557633+00	2025-12-06 09:30:54.568381+00
7	2	LJOA	test-session-unresolved-1	{}	2025-12-06 00:57:37.341309+00	2025-12-07 00:57:37.365935+00
8	2	8NYO	test-session-unresolved-1	{}	2025-12-06 00:57:40.546654+00	2025-12-07 00:57:40.550994+00
9	2	PA6E	168d0fce-1f6d-47a1-9830-dcaa98db2b28	{}	2025-12-07 01:00:04.284409+00	2025-12-08 01:00:04.291232+00
10	2	RCQK	e836303f-2202-412e-8f82-25ecfdca4c2e	{}	2025-12-08 14:18:05.051582+00	2025-12-09 14:18:05.060279+00
11	2	2USD	5a87e680-6ef6-461a-aafb-6116e0683c46	{}	2025-12-09 18:18:00.196224+00	2025-12-10 18:18:00.199139+00
12	2	8YJY	f6b13d95-3492-46ec-95af-118a8bcf5f5e	{}	2025-12-12 14:06:18.585237+00	2025-12-13 14:06:18.590009+00
13	2	QYPL	30ca8bc5-b7c0-4e98-8f32-06f18eb24991	{30ca8bc5-b7c0-4e98-8f32-06f18eb24991}	2025-12-14 06:02:55.188723+00	2025-12-15 06:02:55.190248+00
14	2	O207	6eb0d2ad-2ec4-4ada-86e4-2da5e0f9ec1b	{}	2025-12-17 07:28:52.809135+00	2025-12-18 07:28:52.81342+00
15	2	VWFN	0d7e0287-3694-49fd-ae98-4dfda77168fb	{}	2025-12-18 09:00:06.370849+00	2025-12-19 09:00:06.375949+00
16	2	YM63	39a3c5b5-f21b-4d3e-9146-2639e04e8efd	{}	2025-12-20 02:45:56.406244+00	2025-12-21 02:45:56.416827+00
17	2	JHKF	df5438fc-28c9-4bd0-94e9-2106922ae6b0	{}	2025-12-20 06:27:30.303568+00	2025-12-21 06:27:30.317513+00
18	2	21MG	f0c9580a-3f73-4a58-851f-ef54eebc6358	{}	2025-12-22 01:19:13.409037+00	2025-12-23 01:19:13.415598+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: yadopera_user
--

COPY public.users (id, facility_id, email, password_hash, role, full_name, is_active, last_login_at, password_reset_token, password_reset_expires, created_at, updated_at) FROM stdin;
1	2	test@example.com	$2b$12$x/zOnmREVhSJ1TCX0PUVbuWEYMRbyax1DTfxbe0yVmeWfjcnT5Exq	staff	Test User	t	2025-12-23 01:51:30.884233+00	\N	\N	2025-12-01 07:31:02.85344+00	2025-12-23 01:51:30.622663+00
\.


--
-- Name: conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.conversations_id_seq', 31, true);


--
-- Name: escalation_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.escalation_schedules_id_seq', 1, false);


--
-- Name: escalations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.escalations_id_seq', 13, true);


--
-- Name: facilities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.facilities_id_seq', 3, true);


--
-- Name: faq_suggestions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.faq_suggestions_id_seq', 22, true);


--
-- Name: faq_translations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.faq_translations_id_seq', 14, true);


--
-- Name: faqs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.faqs_id_seq', 22, true);


--
-- Name: guest_feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.guest_feedback_id_seq', 14, true);


--
-- Name: ignored_feedbacks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.ignored_feedbacks_id_seq', 1, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.messages_id_seq', 394, true);


--
-- Name: overnight_queue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.overnight_queue_id_seq', 8, true);


--
-- Name: processed_feedbacks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.processed_feedbacks_id_seq', 1, true);


--
-- Name: qr_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.qr_codes_id_seq', 31, true);


--
-- Name: question_patterns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.question_patterns_id_seq', 1, false);


--
-- Name: session_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.session_tokens_id_seq', 18, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yadopera_user
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: escalation_schedules escalation_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.escalation_schedules
    ADD CONSTRAINT escalation_schedules_pkey PRIMARY KEY (id);


--
-- Name: escalations escalations_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.escalations
    ADD CONSTRAINT escalations_pkey PRIMARY KEY (id);


--
-- Name: facilities facilities_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.facilities
    ADD CONSTRAINT facilities_pkey PRIMARY KEY (id);


--
-- Name: faq_suggestions faq_suggestions_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_suggestions
    ADD CONSTRAINT faq_suggestions_pkey PRIMARY KEY (id);


--
-- Name: faq_translations faq_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_translations
    ADD CONSTRAINT faq_translations_pkey PRIMARY KEY (id);


--
-- Name: faqs faqs_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faqs
    ADD CONSTRAINT faqs_pkey PRIMARY KEY (id);


--
-- Name: guest_feedback guest_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.guest_feedback
    ADD CONSTRAINT guest_feedback_pkey PRIMARY KEY (id);


--
-- Name: ignored_feedbacks ignored_feedbacks_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.ignored_feedbacks
    ADD CONSTRAINT ignored_feedbacks_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: overnight_queue overnight_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.overnight_queue
    ADD CONSTRAINT overnight_queue_pkey PRIMARY KEY (id);


--
-- Name: processed_feedbacks processed_feedbacks_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.processed_feedbacks
    ADD CONSTRAINT processed_feedbacks_pkey PRIMARY KEY (id);


--
-- Name: qr_codes qr_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.qr_codes
    ADD CONSTRAINT qr_codes_pkey PRIMARY KEY (id);


--
-- Name: question_patterns question_patterns_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.question_patterns
    ADD CONSTRAINT question_patterns_pkey PRIMARY KEY (id);


--
-- Name: session_tokens session_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.session_tokens
    ADD CONSTRAINT session_tokens_pkey PRIMARY KEY (id);


--
-- Name: faq_translations uq_faq_translation_faq_language; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_translations
    ADD CONSTRAINT uq_faq_translation_faq_language UNIQUE (faq_id, language);


--
-- Name: ignored_feedbacks uq_ignored_feedback_message_facility; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.ignored_feedbacks
    ADD CONSTRAINT uq_ignored_feedback_message_facility UNIQUE (message_id, facility_id);


--
-- Name: processed_feedbacks uq_processed_feedback_message_facility; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.processed_feedbacks
    ADD CONSTRAINT uq_processed_feedback_message_facility UNIQUE (message_id, facility_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_conversations_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_conversations_facility_id ON public.conversations USING btree (facility_id);


--
-- Name: idx_conversations_is_escalated; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_conversations_is_escalated ON public.conversations USING btree (is_escalated);


--
-- Name: idx_conversations_last_activity; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_conversations_last_activity ON public.conversations USING btree (last_activity_at);


--
-- Name: idx_conversations_session_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE UNIQUE INDEX idx_conversations_session_id ON public.conversations USING btree (session_id);


--
-- Name: idx_escalation_schedules_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_escalation_schedules_facility_id ON public.escalation_schedules USING btree (facility_id);


--
-- Name: idx_escalation_schedules_is_active; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_escalation_schedules_is_active ON public.escalation_schedules USING btree (is_active);


--
-- Name: idx_escalations_conversation_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_escalations_conversation_id ON public.escalations USING btree (conversation_id);


--
-- Name: idx_escalations_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_escalations_facility_id ON public.escalations USING btree (facility_id);


--
-- Name: idx_escalations_resolved_at; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_escalations_resolved_at ON public.escalations USING btree (resolved_at) WHERE (resolved_at IS NULL);


--
-- Name: idx_escalations_trigger_type; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_escalations_trigger_type ON public.escalations USING btree (trigger_type);


--
-- Name: idx_facilities_is_active; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_facilities_is_active ON public.facilities USING btree (is_active);


--
-- Name: idx_facilities_slug; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE UNIQUE INDEX idx_facilities_slug ON public.facilities USING btree (slug);


--
-- Name: idx_faq_suggestions_created_at; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faq_suggestions_created_at ON public.faq_suggestions USING btree (created_at);


--
-- Name: idx_faq_suggestions_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faq_suggestions_facility_id ON public.faq_suggestions USING btree (facility_id);


--
-- Name: idx_faq_suggestions_source_message_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faq_suggestions_source_message_id ON public.faq_suggestions USING btree (source_message_id);


--
-- Name: idx_faq_suggestions_status; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faq_suggestions_status ON public.faq_suggestions USING btree (status);


--
-- Name: idx_faq_translations_embedding; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faq_translations_embedding ON public.faq_translations USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');


--
-- Name: idx_faq_translations_faq_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faq_translations_faq_id ON public.faq_translations USING btree (faq_id);


--
-- Name: idx_faq_translations_language; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faq_translations_language ON public.faq_translations USING btree (language);


--
-- Name: idx_faqs_category; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faqs_category ON public.faqs USING btree (category);


--
-- Name: idx_faqs_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faqs_facility_id ON public.faqs USING btree (facility_id);


--
-- Name: idx_faqs_facility_intent; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE UNIQUE INDEX idx_faqs_facility_intent ON public.faqs USING btree (facility_id, intent_key);


--
-- Name: idx_faqs_is_active; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_faqs_is_active ON public.faqs USING btree (is_active);


--
-- Name: idx_guest_feedback_created_at; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_guest_feedback_created_at ON public.guest_feedback USING btree (created_at);


--
-- Name: idx_guest_feedback_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_guest_feedback_facility_id ON public.guest_feedback USING btree (facility_id);


--
-- Name: idx_guest_feedback_message_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_guest_feedback_message_id ON public.guest_feedback USING btree (message_id);


--
-- Name: idx_guest_feedback_type; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_guest_feedback_type ON public.guest_feedback USING btree (feedback_type);


--
-- Name: idx_ignored_feedbacks_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_ignored_feedbacks_facility_id ON public.ignored_feedbacks USING btree (facility_id);


--
-- Name: idx_ignored_feedbacks_message_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_ignored_feedbacks_message_id ON public.ignored_feedbacks USING btree (message_id);


--
-- Name: idx_messages_ai_confidence; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_messages_ai_confidence ON public.messages USING btree (ai_confidence) WHERE (ai_confidence IS NOT NULL);


--
-- Name: idx_messages_conversation_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_messages_conversation_id ON public.messages USING btree (conversation_id);


--
-- Name: idx_messages_created_at; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_messages_created_at ON public.messages USING btree (created_at);


--
-- Name: idx_overnight_queue_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_overnight_queue_facility_id ON public.overnight_queue USING btree (facility_id);


--
-- Name: idx_overnight_queue_resolved_at; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_overnight_queue_resolved_at ON public.overnight_queue USING btree (resolved_at) WHERE (resolved_at IS NULL);


--
-- Name: idx_overnight_queue_scheduled_notify_at; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_overnight_queue_scheduled_notify_at ON public.overnight_queue USING btree (scheduled_notify_at);


--
-- Name: idx_processed_feedbacks_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_processed_feedbacks_facility_id ON public.processed_feedbacks USING btree (facility_id);


--
-- Name: idx_processed_feedbacks_faq_suggestion_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_processed_feedbacks_faq_suggestion_id ON public.processed_feedbacks USING btree (faq_suggestion_id);


--
-- Name: idx_processed_feedbacks_message_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_processed_feedbacks_message_id ON public.processed_feedbacks USING btree (message_id);


--
-- Name: idx_question_patterns_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_question_patterns_facility_id ON public.question_patterns USING btree (facility_id);


--
-- Name: idx_question_patterns_resolution_rate; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_question_patterns_resolution_rate ON public.question_patterns USING btree (resolution_rate);


--
-- Name: idx_session_tokens_expires_at; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_session_tokens_expires_at ON public.session_tokens USING btree (expires_at);


--
-- Name: idx_session_tokens_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_session_tokens_facility_id ON public.session_tokens USING btree (facility_id);


--
-- Name: idx_session_tokens_primary_session_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_session_tokens_primary_session_id ON public.session_tokens USING btree (primary_session_id);


--
-- Name: idx_session_tokens_token; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE UNIQUE INDEX idx_session_tokens_token ON public.session_tokens USING btree (token);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE UNIQUE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_users_facility_id ON public.users USING btree (facility_id);


--
-- Name: idx_users_password_reset_token; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX idx_users_password_reset_token ON public.users USING btree (password_reset_token) WHERE (password_reset_token IS NOT NULL);


--
-- Name: ix_qr_codes_facility_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX ix_qr_codes_facility_id ON public.qr_codes USING btree (facility_id);


--
-- Name: ix_qr_codes_id; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX ix_qr_codes_id ON public.qr_codes USING btree (id);


--
-- Name: ix_qr_codes_location; Type: INDEX; Schema: public; Owner: yadopera_user
--

CREATE INDEX ix_qr_codes_location ON public.qr_codes USING btree (location);


--
-- Name: faq_suggestions check_forbidden_patterns_faq_suggestions; Type: TRIGGER; Schema: public; Owner: yadopera_user
--

CREATE TRIGGER check_forbidden_patterns_faq_suggestions BEFORE INSERT OR UPDATE ON public.faq_suggestions FOR EACH ROW EXECUTE FUNCTION public.check_forbidden_patterns();


--
-- Name: faq_translations check_forbidden_patterns_faq_translations; Type: TRIGGER; Schema: public; Owner: yadopera_user
--

CREATE TRIGGER check_forbidden_patterns_faq_translations BEFORE INSERT OR UPDATE ON public.faq_translations FOR EACH ROW EXECUTE FUNCTION public.check_forbidden_patterns();


--
-- Name: messages check_forbidden_patterns_messages; Type: TRIGGER; Schema: public; Owner: yadopera_user
--

CREATE TRIGGER check_forbidden_patterns_messages BEFORE INSERT OR UPDATE ON public.messages FOR EACH ROW EXECUTE FUNCTION public.check_forbidden_patterns();


--
-- Name: conversations conversations_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: escalation_schedules escalation_schedules_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.escalation_schedules
    ADD CONSTRAINT escalation_schedules_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: escalations escalations_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.escalations
    ADD CONSTRAINT escalations_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: escalations escalations_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.escalations
    ADD CONSTRAINT escalations_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: escalations escalations_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.escalations
    ADD CONSTRAINT escalations_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: faq_suggestions faq_suggestions_created_faq_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_suggestions
    ADD CONSTRAINT faq_suggestions_created_faq_id_fkey FOREIGN KEY (created_faq_id) REFERENCES public.faqs(id) ON DELETE SET NULL;


--
-- Name: faq_suggestions faq_suggestions_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_suggestions
    ADD CONSTRAINT faq_suggestions_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: faq_suggestions faq_suggestions_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_suggestions
    ADD CONSTRAINT faq_suggestions_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: faq_suggestions faq_suggestions_source_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_suggestions
    ADD CONSTRAINT faq_suggestions_source_message_id_fkey FOREIGN KEY (source_message_id) REFERENCES public.messages(id) ON DELETE CASCADE;


--
-- Name: faq_translations faq_translations_faq_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faq_translations
    ADD CONSTRAINT faq_translations_faq_id_fkey FOREIGN KEY (faq_id) REFERENCES public.faqs(id) ON DELETE CASCADE;


--
-- Name: faqs faqs_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faqs
    ADD CONSTRAINT faqs_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: faqs faqs_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.faqs
    ADD CONSTRAINT faqs_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: session_tokens fk_session_tokens_primary_session_id; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.session_tokens
    ADD CONSTRAINT fk_session_tokens_primary_session_id FOREIGN KEY (primary_session_id) REFERENCES public.conversations(session_id) ON DELETE CASCADE;


--
-- Name: guest_feedback guest_feedback_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.guest_feedback
    ADD CONSTRAINT guest_feedback_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: guest_feedback guest_feedback_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.guest_feedback
    ADD CONSTRAINT guest_feedback_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.messages(id) ON DELETE CASCADE;


--
-- Name: ignored_feedbacks ignored_feedbacks_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.ignored_feedbacks
    ADD CONSTRAINT ignored_feedbacks_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: ignored_feedbacks ignored_feedbacks_ignored_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.ignored_feedbacks
    ADD CONSTRAINT ignored_feedbacks_ignored_by_fkey FOREIGN KEY (ignored_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: ignored_feedbacks ignored_feedbacks_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.ignored_feedbacks
    ADD CONSTRAINT ignored_feedbacks_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.messages(id) ON DELETE CASCADE;


--
-- Name: messages messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: overnight_queue overnight_queue_escalation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.overnight_queue
    ADD CONSTRAINT overnight_queue_escalation_id_fkey FOREIGN KEY (escalation_id) REFERENCES public.escalations(id) ON DELETE CASCADE;


--
-- Name: overnight_queue overnight_queue_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.overnight_queue
    ADD CONSTRAINT overnight_queue_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: overnight_queue overnight_queue_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.overnight_queue
    ADD CONSTRAINT overnight_queue_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: processed_feedbacks processed_feedbacks_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.processed_feedbacks
    ADD CONSTRAINT processed_feedbacks_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: processed_feedbacks processed_feedbacks_faq_suggestion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.processed_feedbacks
    ADD CONSTRAINT processed_feedbacks_faq_suggestion_id_fkey FOREIGN KEY (faq_suggestion_id) REFERENCES public.faq_suggestions(id) ON DELETE SET NULL;


--
-- Name: processed_feedbacks processed_feedbacks_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.processed_feedbacks
    ADD CONSTRAINT processed_feedbacks_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.messages(id) ON DELETE CASCADE;


--
-- Name: processed_feedbacks processed_feedbacks_processed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.processed_feedbacks
    ADD CONSTRAINT processed_feedbacks_processed_by_fkey FOREIGN KEY (processed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: qr_codes qr_codes_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.qr_codes
    ADD CONSTRAINT qr_codes_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: question_patterns question_patterns_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.question_patterns
    ADD CONSTRAINT question_patterns_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: session_tokens session_tokens_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.session_tokens
    ADD CONSTRAINT session_tokens_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- Name: users users_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yadopera_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facilities(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict GNnEed842mKbOe1nhoSomuhM0VZxKPZ3TD8Awb2uG7wNrmX15DPeBwkwUUd7a9C

