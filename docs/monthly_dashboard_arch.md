\# やどぺら ダッシュボード統計設計書

\*\*作成日\*\*: 2025-01-14    
\*\*バージョン\*\*: v1.0    
\*\*対象フェーズ\*\*: Phase 2（PoC準備）〜Phase 4（本格展開）

\---

\#\# 1\. 料金プラン定義

\#\#\# 1.1 プラン一覧

| プラン名 | 月額料金 | 質問数上限 | 超過時単価 | FAQ登録数上限 | 同時利用言語数 | 想定規模 |  
|---------|---------|-----------|-----------|-------------|-------------|---------|  
| Free | ¥0 | 30件 | 超過後はFAQ対応のみ | 20件 | 1言語（日本語固定） | 〜25床 |  
| Mini | ¥1,980 | 無制限 | ¥30/質問 | 30件 | 2言語 | 〜25床 |  
| Small | ¥3,980 | 200件 | ¥30/質問 | 50件 | 3言語 | 〜25床 |  
| Standard | ¥5,980 | 500件 | ¥30/質問 | 100件 | 4言語 | 26-50床 |  
| Premium | ¥7,980 | 1,000件 | ¥30/質問 | 無制限 | 無制限 | 51床以上 |

\#\#\# 1.2 質問数カウント定義

\*\*カウント対象\*\*: \`messages\`テーブルの\`role='user'\`（ゲストが送信したメッセージ）

\*\*カウント除外対象\*\*:  
\- システムメッセージ（\`role='system'\`）  
\- AI応答メッセージ（\`role='assistant'\`）  
\- 管理者メッセージ（エスカレーション対応時の\`role='staff'\`）

\*\*月次集計期間（請求期間ベース）\*\*: 契約開始日（\`plan_started_at\`）から30日間の請求期間で集計（Stripe統合を見据えた設計）

\*\*請求期間の計算ロジック\*\*:
- 請求期間は\`plan_started_at\`を基準に、30日間（1ヶ月）ごとに区切られる
- 現在時刻が含まれる請求期間を自動計算
- 例: \`plan_started_at = 2026-01-15 10:00:00\`の場合
  - 1回目の請求期間: 2026-01-15 10:00:00 〜 2026-02-15 09:59:59（JST）
  - 2回目の請求期間: 2026-02-15 10:00:00 〜 2026-03-15 09:59:59（JST）
- プラン変更時は\`plan_started_at\`を更新し、新しいプランの開始日から請求期間を計算
- すべての統計は\*\*日本時間（JST）\*\*基準、データベースはUTC保存、取得時にJST変換

\---

\#\# 2\. ダッシュボード統計カード設計

\#\#\# 2.1 月次統計カード（最優先表示エリア）

\#\#\#\# カード1: 今月の質問数 / プラン上限

\*\*表示項目\*\*:  
\`\`\`  
今月の質問数  
152 / 200件  
━━━━━━━━━━━ 76%  
あと48件で上限です  
\`\`\`

\*\*データ仕様\*\*:  
\- \*\*主要データ\*\*:   
  \- \`current\_month\_questions\`: 今月の質問数（INT）  
  \- \`plan\_limit\`: 契約プランの月間上限（INT、Miniの場合はNULL）  
  \- \`usage\_percentage\`: 使用率（DECIMAL、\`current\_month\_questions / plan\_limit \* 100\`）  
  \- \`remaining\_questions\`: 残り質問数（INT、\`plan\_limit \- current\_month\_questions\`）  
\- \*\*集計SQL\*\*:  
\`\`\`sql  
SELECT COUNT(\*) as current\_month\_questions  
FROM messages m  
JOIN conversations c ON m.conversation\_id \= c.id  
WHERE c.facility\_id \= :facility\_id  
  AND m.role \= 'user'  
  AND m.created\_at \>= :billing\_start\_utc  -- 請求期間開始時刻（UTC）
  AND m.created\_at \<= :billing\_end\_utc;    -- 請求期間終了時刻（UTC）
  
-- 請求期間は\`plan_started_at\`から計算（バックエンドで実装）  
\`\`\`  
\- \*\*プラン情報取得SQL\*\*:  
\`\`\`sql  
SELECT plan\_type, monthly\_question\_limit  
FROM facilities  
WHERE id \= :facility\_id;  
\`\`\`

\*\*表示ロジック\*\*:  
\- \*\*Freeプラン\*\*: 30件超過後は「FAQのみ対応中」バッジ表示  
\- \*\*Miniプラン\*\*: 上限表示なし、「従量課金プラン」バッジ表示  
\- \*\*Small/Standard/Premium\*\*: プログレスバー \+ 残数表示

\*\*色分けルール\*\*:  
| 使用率 | 色 | 表示メッセージ |  
|--------|-----|---------------|  
| 0-70% | 緑（\`text-green-600\`） | 「あと○○件で上限です」 |  
| 71-90% | 黄色（\`text-yellow-600\`） | 「残り○○件です」 |  
| 91-99% | オレンジ（\`text-orange-600\`） | 「⚠️ まもなく上限です」 |  
| 100%+ | 赤（\`text-red-600\`） | 「⚠️ 従量課金が発生しています」 |

\*\*API エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard/monthly-usage  
\`\`\`

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "current\_month\_questions": 152,  
  "plan\_type": "Small",  
  "plan\_limit": 200,  
  "usage\_percentage": 76.0,  
  "remaining\_questions": 48,  
  "overage\_questions": 0,  
  "status": "normal"  // "normal" | "warning" | "overage" | "faq\_only"  
}  
\`\`\`

\---

\#\#\#\# カード2: 今月のAI自動応答数

\*\*表示項目\*\*:  
\`\`\`  
AI自動応答数  
128件  
自動化率: 84.2%  
\`\`\`

\*\*データ仕様\*\*:  
\- \*\*主要データ\*\*:  
  \- \`ai\_responses\`: AI自動応答数（INT）  
  \- \`total\_questions\`: 今月の総質問数（INT）  
  \- \`automation\_rate\`: 自動化率（DECIMAL、\`ai\_responses / total\_questions \* 100\`）  
\- \*\*集計SQL\*\*:  
\`\`\`sql  
\-- AI自動応答数（エスカレーションされなかった質問）  
SELECT   
  COUNT(DISTINCT c.id) as ai\_responses,  
  (SELECT COUNT(\*)   
   FROM messages m2  
   JOIN conversations c2 ON m2.conversation\_id \= c2.id  
   WHERE c2.facility\_id \= :facility\_id  
     AND m2.role \= 'user'  
     AND m2.created\_at \>= :billing\_start\_utc  -- 請求期間開始時刻（UTC）
     AND m2.created\_at \<= :billing\_end\_utc    -- 請求期間終了時刻（UTC）  
  ) as total\_questions  
FROM conversations c  
LEFT JOIN escalations e ON c.id \= e.conversation\_id  
WHERE c.facility\_id \= :facility\_id  
  AND c.started\_at \>= :billing\_start\_utc  -- 請求期間開始時刻（UTC）
  AND c.started\_at \<= :billing\_end\_utc    -- 請求期間終了時刻（UTC）  
  AND e.id IS NULL;  \-- エスカレーションされていない会話のみ  
\`\`\`

\*\*API エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard/ai-automation  
\`\`\`

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "ai\_responses": 128,  
  "total\_questions": 152,  
  "automation\_rate": 84.2,  
  "comparison\_last\_month": "+5.3%"  // 先月比（Phase 3以降実装）  
}  
\`\`\`

\---

\#\#\#\# カード3: 今月のエスカレーション数

\*\*表示項目\*\*:  
\`\`\`  
スタッフ対応が必要だった質問  
24件  
うち未解決: 3件  
\`\`\`

\*\*データ仕様\*\*:  
\- \*\*主要データ\*\*:  
  \- \`total\_escalations\`: 今月のエスカレーション総数（INT）  
  \- \`unresolved\_escalations\`: 未解決数（INT）  
  \- \`resolved\_escalations\`: 解決済み数（INT）  
\- \*\*集計SQL\*\*:  
\`\`\`sql  
SELECT   
  COUNT(\*) as total\_escalations,  
  COUNT(\*) FILTER (WHERE resolved\_at IS NULL) as unresolved\_escalations,  
  COUNT(\*) FILTER (WHERE resolved\_at IS NOT NULL) as resolved\_escalations  
FROM escalations e  
JOIN conversations c ON e.conversation\_id \= c.id  
WHERE c.facility\_id \= :facility\_id  
  AND e.created\_at \>= :billing\_start\_utc  -- 請求期間開始時刻（UTC）
  AND e.created\_at \<= :billing\_end\_utc;    -- 請求期間終了時刻（UTC）  
\`\`\`

\*\*表示ロジック\*\*:  
\- 未解決数が1件以上の場合、赤バッジで強調表示  
\- 未解決0件の場合、緑チェックマーク表示

\*\*API エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard/escalations-summary  
\`\`\`

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "total\_escalations": 24,  
  "unresolved\_escalations": 3,  
  "resolved\_escalations": 21,  
  "unresolved\_list": \[  
    {  
      "id": 123,  
      "guest\_message": "WiFiが繋がりません",  
      "created\_at": "2025-01-14T10:30:00Z",  
      "language": "ja"  
    }  
  \]  
}  
\`\`\`

\---

\#\#\#\# カード4: 推定月額コスト（Phase 3以降実装）

\*\*表示項目\*\*:  
\`\`\`  
今月の推定料金  
¥4,940  
プラン: ¥3,980  
従量: ¥960（32件 × ¥30）  
\`\`\`

\*\*データ仕様\*\*:  
\- \*\*主要データ\*\*:  
  \- \`base\_fee\`: プラン基本料金（INT）  
  \- \`overage\_count\`: 超過質問数（INT）  
  \- \`overage\_fee\`: 従量料金（INT、\`overage\_count \* 30\`）  
  \- \`total\_estimated\_cost\`: 合計推定額（INT、\`base\_fee \+ overage\_fee\`）  
\- \*\*計算ロジック\*\*:  
\`\`\`python  
def calculate\_monthly\_cost(plan\_type: str, current\_month\_questions: int) \-\> dict:  
    plans \= {  
        "Free": {"base": 0, "limit": 30, "overage\_rate": 0},  \# 超過後はFAQ対応のみ  
        "Mini": {"base": 1980, "limit": 0, "overage\_rate": 30},  \# 最初から従量課金  
        "Small": {"base": 3980, "limit": 200, "overage\_rate": 30},  
        "Standard": {"base": 5980, "limit": 500, "overage\_rate": 30},  
        "Premium": {"base": 7980, "limit": 1000, "overage\_rate": 30}  
    }  
      
    plan \= plans\[plan\_type\]  
    base\_fee \= plan\["base"\]  
      
    if plan\_type \== "Free":  
        overage\_count \= max(0, current\_month\_questions \- plan\["limit"\])  
        overage\_fee \= 0  \# Freeプランは従量課金なし  
        note \= "30件超過後はFAQのみ対応" if overage\_count \> 0 else ""  
    elif plan\_type \== "Mini":  
        overage\_count \= current\_month\_questions  
        overage\_fee \= overage\_count \* plan\["overage\_rate"\]  
        note \= "全質問が従量課金対象"  
    else:  
        overage\_count \= max(0, current\_month\_questions \- plan\["limit"\])  
        overage\_fee \= overage\_count \* plan\["overage\_rate"\]  
        note \= ""  
      
    return {  
        "base\_fee": base\_fee,  
        "overage\_count": overage\_count,  
        "overage\_fee": overage\_fee,  
        "total\_estimated\_cost": base\_fee \+ overage\_fee,  
        "note": note  
    }  
\`\`\`

\*\*API エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard/estimated-cost  
\`\`\`

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "plan\_type": "Small",  
  "current\_month\_questions": 232,  
  "base\_fee": 3980,  
  "overage\_count": 32,  
  "overage\_fee": 960,  
  "total\_estimated\_cost": 4940,  
  "breakdown": {  
    "plan\_name": "Small",  
    "plan\_limit": 200,  
    "within\_limit": 200,  
    "overage": 32  
  },  
  "note": ""  
}  
\`\`\`

\---

\#\#\# 2.2 週次サマリーカード（副次的な参考情報）

\#\#\#\# カード5: 過去7日間の質問数トレンド

\*\*表示項目\*\*:  
\`\`\`  
過去7日間の推移  
\[折れ線グラフ\]  
合計: 52件（先週比 \+8.3%）  
\`\`\`

\*\*データ仕様\*\*:  
\- \*\*主要データ\*\*:  
  \- \`daily\_data\`: 日別質問数配列（Array）  
  \- \`total\_questions\`: 7日間合計（INT）  
  \- \`comparison\_previous\_week\`: 前週比（DECIMAL）  
\- \*\*集計SQL\*\*:  
\`\`\`sql  
SELECT   
  DATE(m.created\_at AT TIME ZONE 'Asia/Tokyo') as date,  
  COUNT(\*) as question\_count  
FROM messages m  
JOIN conversations c ON m.conversation\_id \= c.id  
WHERE c.facility\_id \= :facility\_id  
  AND m.role \= 'user'  
  AND m.created\_at \>= CURRENT\_TIMESTAMP \- INTERVAL '7 days'  
GROUP BY DATE(m.created\_at AT TIME ZONE 'Asia/Tokyo')  
ORDER BY date;  
\`\`\`

\*\*API エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard/weekly-trend  
\`\`\`

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "daily\_data": \[  
    {"date": "2025-01-08", "question\_count": 8},  
    {"date": "2025-01-09", "question\_count": 6},  
    {"date": "2025-01-10", "question\_count": 9},  
    {"date": "2025-01-11", "question\_count": 7},  
    {"date": "2025-01-12", "question\_count": 5},  
    {"date": "2025-01-13", "question\_count": 10},  
    {"date": "2025-01-14", "question\_count": 7}  
  \],  
  "total\_questions": 52,  
  "comparison\_previous\_week": "+8.3%",  
  "peak\_day": "2025-01-13",  
  "peak\_count": 10  
}  
\`\`\`

\*\*グラフ実装\*\*:  
\- ライブラリ: Chart.js または Recharts（Vue 3対応）  
\- グラフタイプ: 折れ線グラフ（Line Chart）  
\- X軸: 日付（MM/DD形式）  
\- Y軸: 質問数

\---

\#\#\#\# カード6: 過去7日間の平均信頼度

\*\*表示項目\*\*:  
\`\`\`  
AI回答の信頼度  
78.3%（先週比 \+2.1%）  
\`\`\`

\*\*データ仕様\*\*:  
\- \*\*主要データ\*\*:  
  \- \`average\_confidence\`: 平均信頼度（DECIMAL）  
  \- \`comparison\_previous\_week\`: 前週比（DECIMAL）  
\- \*\*集計SQL\*\*:  
\`\`\`sql  
SELECT   
  AVG(confidence\_score) \* 100 as average\_confidence  
FROM messages  
WHERE conversation\_id IN (  
  SELECT id FROM conversations WHERE facility\_id \= :facility\_id  
)  
  AND role \= 'assistant'  
  AND confidence\_score IS NOT NULL  
  AND created\_at \>= CURRENT\_TIMESTAMP \- INTERVAL '7 days';  
\`\`\`

\*\*API エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard/confidence-score  
\`\`\`

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "average\_confidence": 78.3,  
  "comparison\_previous\_week": "+2.1%",  
  "min\_confidence": 45.2,  
  "max\_confidence": 95.8,  
  "total\_responses": 128  
}  
\`\`\`

\---

\#\#\#\# カード7: 過去7日間のカテゴリ別質問数（円グラフ）

\*\*表示項目\*\*:  
\`\`\`  
よくある質問カテゴリ  
\[円グラフ\]  
1\. Basic（基本情報）: 35件  
2\. Facilities（設備）: 28件  
3\. Location（周辺情報）: 15件  
4\. Trouble（トラブル）: 9件  
\`\`\`

\*\*データ仕様\*\*:  
\- \*\*主要データ\*\*:  
  \- \`category\_breakdown\`: カテゴリ別内訳配列（Array）  
\- \*\*集計SQL\*\*:  
\`\`\`sql  
SELECT   
  f.category,  
  COUNT(\*) as count  
FROM messages m  
JOIN conversations c ON m.conversation\_id \= c.id  
LEFT JOIN faqs f ON m.matched\_faq\_id \= f.id  
WHERE c.facility\_id \= :facility\_id  
  AND m.role \= 'assistant'  
  AND m.matched\_faq\_id IS NOT NULL  
  AND m.created\_at \>= CURRENT\_TIMESTAMP \- INTERVAL '7 days'  
GROUP BY f.category  
ORDER BY count DESC;  
\`\`\`

\*\*API エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard/category-breakdown  
\`\`\`

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "category\_breakdown": \[  
    {"category": "Basic", "count": 35, "percentage": 40.2},  
    {"category": "Facilities", "count": 28, "percentage": 32.2},  
    {"category": "Location", "count": 15, "percentage": 17.2},  
    {"category": "Trouble", "count": 9, "percentage": 10.3}  
  \],  
  "total\_faq\_responses": 87  
}  
\`\`\`

\*\*グラフ実装\*\*:  
\- ライブラリ: Chart.js または Recharts  
\- グラフタイプ: ドーナツグラフ（Doughnut Chart）

\---

\#\#\# 2.3 リアルタイム情報カード

\#\#\#\# カード8: 未解決のエスカレーション（現状維持）

\*\*表示項目\*\*:  
\`\`\`  
未解決の質問  
\[リスト表示：最新10件\]  
\`\`\`

\*\*データ仕様\*\*:  
\- \*\*主要データ\*\*:  
  \- \`unresolved\_list\`: 未解決エスカレーション配列（Array）  
\- \*\*集計SQL\*\*:  
\`\`\`sql  
SELECT   
  e.id,  
  e.reason,  
  e.created\_at,  
  m.content as guest\_message,  
  c.language  
FROM escalations e  
JOIN conversations c ON e.conversation\_id \= c.id  
JOIN messages m ON m.conversation\_id \= c.id AND m.role \= 'user'  
WHERE c.facility\_id \= :facility\_id  
  AND e.resolved\_at IS NULL  
ORDER BY e.created\_at DESC  
LIMIT 10;  
\`\`\`

\*\*API エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard/unresolved-escalations  
\`\`\`

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "unresolved\_count": 3,  
  "unresolved\_list": \[  
    {  
      "id": 123,  
      "reason": "low\_confidence",  
      "guest\_message": "WiFiが繋がりません",  
      "created\_at": "2025-01-14T10:30:00Z",  
      "language": "ja",  
      "conversation\_id": 456  
    }  
  \]  
}  
\`\`\`

\---

\#\# 3\. データベース設計追加

\#\#\# 3.1 \`facilities\`テーブルへのカラム追加

\`\`\`sql  
ALTER TABLE facilities  
ADD COLUMN plan\_type VARCHAR(20) DEFAULT 'Free'   
  CHECK (plan\_type IN ('Free', 'Mini', 'Small', 'Standard', 'Premium')),  
ADD COLUMN monthly\_question\_limit INTEGER DEFAULT 30,  
ADD COLUMN faq\_limit INTEGER DEFAULT 20,  
ADD COLUMN language\_limit INTEGER DEFAULT 1,  
ADD COLUMN plan\_started\_at TIMESTAMP DEFAULT NOW(),  
ADD COLUMN plan\_updated\_at TIMESTAMP;

COMMENT ON COLUMN facilities.plan\_type IS '契約プラン種別';  
COMMENT ON COLUMN facilities.monthly\_question\_limit IS '月間質問数上限（Miniの場合はNULL）';  
COMMENT ON COLUMN facilities.faq\_limit IS 'FAQ登録数上限（Premiumの場合はNULL）';  
COMMENT ON COLUMN facilities.language\_limit IS '同時利用言語数上限（Premiumの場合はNULL）';  
\`\`\`

\#\#\# 3.2 \`messages\`テーブルへのカラム追加（既存想定）

\`\`\`sql  
\-- 既存想定カラム  
\-- matched\_faq\_id INTEGER REFERENCES faqs(id)  \-- マッチしたFAQ ID  
\-- confidence\_score DECIMAL(3,2)  \-- 信頼度スコア（0.00-1.00）  
\`\`\`

\#\#\# 3.3 月次集計テーブル（オプション：パフォーマンス最適化用）

\`\`\`sql  
CREATE TABLE monthly\_usage\_cache (  
  id SERIAL PRIMARY KEY,  
  facility\_id INTEGER REFERENCES facilities(id) ON DELETE CASCADE,  
  year\_month DATE NOT NULL,  \-- 月の初日（例: 2025-01-01）  
  total\_questions INTEGER DEFAULT 0,  
  ai\_responses INTEGER DEFAULT 0,  
  escalations INTEGER DEFAULT 0,  
  average\_confidence DECIMAL(5,2),  
  total\_cost INTEGER DEFAULT 0,  
  created\_at TIMESTAMP DEFAULT NOW(),  
  updated\_at TIMESTAMP DEFAULT NOW(),  
  UNIQUE(facility\_id, year\_month)  
);

CREATE INDEX idx\_monthly\_usage\_facility\_month ON monthly\_usage\_cache(facility\_id, year\_month);

COMMENT ON TABLE monthly\_usage\_cache IS '月次集計キャッシュ（日次バッチで更新）';  
\`\`\`

\---

\#\# 4\. API設計

\#\#\# 4.1 ダッシュボード統合エンドポイント

\*\*エンドポイント\*\*:  
\`\`\`  
GET /api/v1/admin/dashboard  
\`\`\`

\*\*説明\*\*: すべての統計データを一度に取得（フロントエンドの初期表示用）

\*\*レスポンス例\*\*:  
\`\`\`json  
{  
  "monthly\_usage": {  
    "current\_month\_questions": 152,  
    "plan\_type": "Small",  
    "plan\_limit": 200,  
    "usage\_percentage": 76.0,  
    "remaining\_questions": 48,  
    "overage\_questions": 0,  
    "status": "normal"  
  },  
  "ai\_automation": {  
    "ai\_responses": 128,  
    "total\_questions": 152,  
    "automation\_rate": 84.2  
  },  
  "escalations\_summary": {  
    "total\_escalations": 24,  
    "unresolved\_escalations": 3,  
    "resolved\_escalations": 21  
  },  
  "estimated\_cost": {  
    "base\_fee": 3980,  
    "overage\_fee": 0,  
    "total\_estimated\_cost": 3980  
  },  
  "weekly\_trend": {  
    "daily\_data": \[...\],  
    "total\_questions": 52,  
    "comparison\_previous\_week": "+8.3%"  
  },  
  "confidence\_score": {  
    "average\_confidence": 78.3,  
    "comparison\_previous\_week": "+2.1%"  
  },  
  "category\_breakdown": {  
    "category\_breakdown": \[...\]  
  },  
  "unresolved\_escalations": {  
    "unresolved\_count": 3,  
    "unresolved\_list": \[...\]  
  }  
}  
\`\`\`

\*\*認証\*\*: JWT必須（\`Authorization: Bearer {token}\`）

\*\*実装優先度\*\*:  
\- Phase 2（PoC準備）: \`monthly\_usage\`, \`ai\_automation\`, \`escalations\_summary\`, \`unresolved\_escalations\`  
\- Phase 3（PoC実施）: \`estimated\_cost\`, \`weekly\_trend\`, \`confidence\_score\`, \`category\_breakdown\`

\---

\#\# 5\. フロントエンド実装設計

\#\#\# 5.1 コンポーネント構成

\`\`\`  
src/views/admin/  
├── DashboardView.vue  \# ダッシュボードメインページ  
└── components/  
    ├── MonthlyUsageCard.vue  \# カード1: 今月の質問数/プラン上限  
    ├── AiAutomationCard.vue  \# カード2: AI自動応答数  
    ├── EscalationsSummaryCard.vue  \# カード3: エスカレーション数  
    ├── EstimatedCostCard.vue  \# カード4: 推定月額コスト（Phase 3）  
    ├── WeeklyTrendCard.vue  \# カード5: 週次トレンド  
    ├── ConfidenceScoreCard.vue  \# カード6: 平均信頼度  
    ├── CategoryBreakdownCard.vue  \# カード7: カテゴリ別内訳  
    └── UnresolvedListCard.vue  \# カード8: 未解決エスカレーション  
\`\`\`

\#\#\# 5.2 DashboardView.vue 実装例

\`\`\`vue  
\<template\>  
  \<div class="dashboard-container p-6 space-y-6"\>  
    \<\!-- 月次統計セクション \--\>  
    \<section class="monthly-stats"\>  
      \<h2 class="text-2xl font-bold mb-4"\>今月の利用状況\</h2\>  
      \<div class="grid grid-cols-1 md:grid-cols-3 gap-4"\>  
        \<MonthlyUsageCard :data="dashboardData.monthly\_usage" /\>  
        \<AiAutomationCard :data="dashboardData.ai\_automation" /\>  
        \<EscalationsSummaryCard :data="dashboardData.escalations\_summary" /\>  
      \</div\>  
      \<\!-- Phase 3以降 \--\>  
      \<div class="mt-4"\>  
        \<EstimatedCostCard   
          v-if="dashboardData.estimated\_cost"   
          :data="dashboardData.estimated\_cost"   
        /\>  
      \</div\>  
    \</section\>

    \<\!-- 週次トレンドセクション \--\>  
    \<section class="weekly-stats"\>  
      \<h2 class="text-xl font-bold mb-4"\>過去7日間の推移\</h2\>  
      \<div class="grid grid-cols-1 md:grid-cols-2 gap-4"\>  
        \<WeeklyTrendCard :data="dashboardData.weekly\_trend" /\>  
        \<ConfidenceScoreCard :data="dashboardData.confidence\_score" /\>  
      \</div\>  
    \</section\>

    \<\!-- カテゴリ別分析セクション \--\>  
    \<section class="category-stats"\>  
      \<h2 class="text-xl font-bold mb-4"\>カテゴリ別分析\</h2\>  
      \<CategoryBreakdownCard :data="dashboardData.category\_breakdown" /\>  
    \</section\>

    \<\!-- 未解決質問セクション \--\>  
    \<section class="unresolved-section"\>  
      \<h2 class="text-xl font-bold mb-4"\>対応が必要な質問\</h2\>  
      \<UnresolvedListCard :data="dashboardData.unresolved\_escalations" /\>  
    \</section\>  
  \</div\>  
\</template\>

\<script setup lang="ts"\>  
import { ref, onMounted } from 'vue';  
import { useAuthStore } from '@/stores/auth';  
import axios from 'axios';

const authStore \= useAuthStore();  
const dashboardData \= ref({});

const fetchDashboardData \= async () \=\> {  
  try {  
    const response \= await axios.get('/api/v1/admin/dashboard', {  
      headers: {  
        Authorization: \`Bearer ${authStore.token}\`  
      }  
    });  
    dashboardData.value \= response.data;  
  } catch (error) {  
    console.error('ダッシュボードデータ取得エラー:', error);  
  }  
};

onMounted(() \=\> {  
  fetchDashboardData();  
  // 5分ごとに自動更新（ポーリング）  
  setInterval(fetchDashboardData, 5 \* 60 \* 1000);  
});  
\</script\>  
\`\`\`

\#\#\# 5.3 MonthlyUsageCard.vue 実装例

\`\`\`vue  
\<template\>  
  \<div class="card bg-white rounded-lg shadow p-6"\>  
    \<h3 class="text-lg font-semibold mb-2"\>今月の質問数\</h3\>  
      
    \<\!-- Freeプラン：30件超過後 \--\>  
    \<div v-if="data.plan\_type \=== 'Free' && data.status \=== 'faq\_only'" class="text-center"\>  
      \<p class="text-3xl font-bold text-red-600"\>{{ data.current\_month\_questions }}件\</p\>  
      \<p class="text-sm text-gray-500 mt-1"\>30件超過：FAQのみ対応中\</p\>  
    \</div\>  
      
    \<\!-- Miniプラン：従量課金のみ \--\>  
    \<div v-else-if="data.plan\_type \=== 'Mini'" class="text-center"\>  
      \<p class="text-3xl font-bold"\>{{ data.current\_month\_questions }}件\</p\>  
      \<span class="inline-block mt-2 px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"\>  
        従量課金プラン  
      \</span\>  
    \</div\>  
      
    \<\!-- Small/Standard/Premium：プログレスバー表示 \--\>  
    \<div v-else\>  
      \<div class="flex items-end justify-between mb-2"\>  
        \<p class="text-3xl font-bold"\>{{ data.current\_month\_questions }}\</p\>  
        \<p class="text-gray-500"\>/ {{ data.plan\_limit }}件\</p\>  
      \</div\>  
        
      \<\!-- プログレスバー \--\>  
      \<div class="w-full bg-gray-200 rounded-full h-2 mb-2"\>  
        \<div   
          class="h-2 rounded-full transition-all"  
          :class="progressBarColor"  
          :style="{ width: data.usage\_percentage \+ '%' }"  
        \>\</div\>  
      \</div\>  
        
      \<\!-- ステータスメッセージ \--\>  
      \<p :class="statusTextColor" class="text-sm"\>  
        {{ statusMessage }}  
      \</p\>  
    \</div\>  
  \</div\>  
\</template\>

\<script setup lang="ts"\>  
import { computed } from 'vue';

const props \= defineProps\<{  
  data: {  
    current\_month\_questions: number;  
    plan\_type: string;  
    plan\_limit: number;  
    usage\_percentage:  
number;  
    remaining\_questions: number;  
    overage\_questions: number;  
    status: string;  
  }  
}\>();

const progressBarColor \= computed(() \=\> {  
  const usage \= props.data.usage\_percentage;  
  if (usage \>= 100\) return 'bg-red-600';  
  if (usage \>= 91\) return 'bg-orange-600';  
  if (usage \>= 71\) return 'bg-yellow-500';  
  return 'bg-green-600';  
});

const statusTextColor \= computed(() \=\> {  
  const usage \= props.data.usage\_percentage;  
  if (usage \>= 100\) return 'text-red-600 font-semibold';  
  if (usage \>= 91\) return 'text-orange-600 font-semibold';  
  if (usage \>= 71\) return 'text-yellow-600';  
  return 'text-green-600';  
});

const statusMessage \= computed(() \=\> {  
  const usage \= props.data.usage\_percentage;  
  if (usage \>= 100\) {  
    return \`⚠️ 従量課金が発生しています（${props.data.overage\_questions}件超過）\`;  
  }  
  if (usage \>= 91\) {  
    return \`⚠️ まもなく上限です（残り${props.data.remaining\_questions}件）\`;  
  }  
  if (usage \>= 71\) {  
    return \`残り${props.data.remaining\_questions}件です\`;  
  }  
  return \`あと${props.data.remaining\_questions}件で上限です\`;  
});  
\</script\>  
\`\`\`

\---

\#\# 6\. バックエンド実装設計（FastAPI）

\#\#\# 6.1 router/admin.py 実装例

\`\`\`python  
from fastapi import APIRouter, Depends, HTTPException  
from sqlalchemy.orm import Session  
from datetime import datetime, timedelta  
from typing import Optional  
import pytz

from app.database import get\_db  
from app.auth import get\_current\_user  
from app.models import Facility, Message, Conversation, Escalation, FAQ  
from app.schemas import DashboardResponse

router \= APIRouter(prefix="/api/v1/admin", tags=\["admin"\])

@router.get("/dashboard", response\_model=DashboardResponse)  
async def get\_dashboard(  
    current\_user \= Depends(get\_current\_user),  
    db: Session \= Depends(get\_db)  
):  
    """ダッシュボード統計データ取得"""  
      
    facility\_id \= current\_user.facility\_id  
    jst \= pytz.timezone('Asia/Tokyo')  
    now \= datetime.now(jst)  
      
    \# 請求期間を計算（\`plan_started_at\`から30日間）  
    from app.utils.billing_period import calculate_billing_period  
    plan_started_at_jst = facility.plan_started_at.astimezone(jst)  
    billing_start, billing_end = calculate_billing_period(plan_started_at_jst, now)  
      
    \# 施設情報取得  
    facility \= db.query(Facility).filter(Facility.id \== facility\_id).first()  
    if not facility:  
        raise HTTPException(status\_code=404, detail="Facility not found")  
      
    \# \--- 月次統計（請求期間ベース） \---  
    monthly\_usage \= get\_monthly\_usage(db, facility\_id, facility, billing\_start, billing\_end)  
    ai\_automation \= get\_ai\_automation(db, facility\_id, billing\_start, billing\_end)  
    escalations\_summary \= get\_escalations\_summary(db, facility\_id, billing\_start, billing\_end)  
    estimated\_cost \= calculate\_estimated\_cost(facility.plan\_type, monthly\_usage\['current\_month\_questions'\])  
      
    \# \--- 週次統計 \---  
    week\_start \= now \- timedelta(days=7)  
    weekly\_trend \= get\_weekly\_trend(db, facility\_id, week\_start, now)  
    confidence\_score \= get\_confidence\_score(db, facility\_id, week\_start, now)  
    category\_breakdown \= get\_category\_breakdown(db, facility\_id, week\_start, now)  
      
    \# \--- 未解決エスカレーション \---  
    unresolved\_escalations \= get\_unresolved\_escalations(db, facility\_id)  
      
    return {  
        "monthly\_usage": monthly\_usage,  
        "ai\_automation": ai\_automation,  
        "escalations\_summary": escalations\_summary,  
        "estimated\_cost": estimated\_cost,  
        "weekly\_trend": weekly\_trend,  
        "confidence\_score": confidence\_score,  
        "category\_breakdown": category\_breakdown,  
        "unresolved\_escalations": unresolved\_escalations  
    }

def get\_monthly\_usage(db, facility\_id, facility, month\_start, month\_end):  
    """今月の質問数/プラン上限"""  
      
    current\_month\_questions \= db.query(Message).join(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Message.role \== 'user',  
        Message.created\_at \>= month\_start,  
        Message.created\_at \<= month\_end  
    ).count()  
      
    plan\_limit \= facility.monthly\_question\_limit  
    usage\_percentage \= (current\_month\_questions / plan\_limit \* 100\) if plan\_limit else 0  
    remaining\_questions \= max(0, (plan\_limit or 0\) \- current\_month\_questions)  
    overage\_questions \= max(0, current\_month\_questions \- (plan\_limit or 0))  
      
    \# ステータス判定  
    if facility.plan\_type \== 'Free' and current\_month\_questions \> 30:  
        status \= 'faq\_only'  
    elif usage\_percentage \>= 100:  
        status \= 'overage'  
    elif usage\_percentage \>= 91:  
        status \= 'warning'  
    else:  
        status \= 'normal'  
      
    return {  
        "current\_month\_questions": current\_month\_questions,  
        "plan\_type": facility.plan\_type,  
        "plan\_limit": plan\_limit,  
        "usage\_percentage": round(usage\_percentage, 1),  
        "remaining\_questions": remaining\_questions,  
        "overage\_questions": overage\_questions,  
        "status": status  
    }

def get\_ai\_automation(db, facility\_id, month\_start, month\_end):  
    """AI自動応答数"""  
      
    \# 今月の総質問数  
    total\_questions \= db.query(Message).join(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Message.role \== 'user',  
        Message.created\_at \>= month\_start,  
        Message.created\_at \<= month\_end  
    ).count()  
      
    \# エスカレーションされなかった会話数（AI自動応答）  
    escalated\_conversation\_ids \= db.query(Escalation.conversation\_id).join(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Escalation.created\_at \>= month\_start,  
        Escalation.created\_at \<= month\_end  
    ).subquery()  
      
    ai\_responses \= db.query(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Conversation.started\_at \>= month\_start,  
        Conversation.started\_at \<= month\_end,  
        \~Conversation.id.in\_(escalated\_conversation\_ids)  
    ).count()  
      
    automation\_rate \= (ai\_responses / total\_questions \* 100\) if total\_questions \> 0 else 0  
      
    return {  
        "ai\_responses": ai\_responses,  
        "total\_questions": total\_questions,  
        "automation\_rate": round(automation\_rate, 1\)  
    }

def get\_escalations\_summary(db, facility\_id, month\_start, month\_end):  
    """エスカレーション数"""  
      
    escalations \= db.query(Escalation).join(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Escalation.created\_at \>= month\_start,  
        Escalation.created\_at \<= month\_end  
    ).all()  
      
    total\_escalations \= len(escalations)  
    unresolved\_escalations \= len(\[e for e in escalations if e.resolved\_at is None\])  
    resolved\_escalations \= total\_escalations \- unresolved\_escalations  
      
    return {  
        "total\_escalations": total\_escalations,  
        "unresolved\_escalations": unresolved\_escalations,  
        "resolved\_escalations": resolved\_escalations  
    }

def calculate\_estimated\_cost(plan\_type, current\_month\_questions):  
    """推定月額コスト"""  
      
    plans \= {  
        "Free": {"base": 0, "limit": 30, "overage\_rate": 0},  
        "Mini": {"base": 1980, "limit": 0, "overage\_rate": 30},  
        "Small": {"base": 3980, "limit": 200, "overage\_rate": 30},  
        "Standard": {"base": 5980, "limit": 500, "overage\_rate": 30},  
        "Premium": {"base": 7980, "limit": 1000, "overage\_rate": 30}  
    }  
      
    plan \= plans\[plan\_type\]  
    base\_fee \= plan\["base"\]  
      
    if plan\_type \== "Free":  
        overage\_count \= max(0, current\_month\_questions \- plan\["limit"\])  
        overage\_fee \= 0  
        note \= "30件超過後はFAQのみ対応" if overage\_count \> 0 else ""  
    elif plan\_type \== "Mini":  
        overage\_count \= current\_month\_questions  
        overage\_fee \= overage\_count \* plan\["overage\_rate"\]  
        note \= "全質問が従量課金対象"  
    else:  
        overage\_count \= max(0, current\_month\_questions \- plan\["limit"\])  
        overage\_fee \= overage\_count \* plan\["overage\_rate"\]  
        note \= ""  
      
    return {  
        "base\_fee": base\_fee,  
        "overage\_count": overage\_count,  
        "overage\_fee": overage\_fee,  
        "total\_estimated\_cost": base\_fee \+ overage\_fee,  
        "note": note  
    }

def get\_weekly\_trend(db, facility\_id, week\_start, now):  
    """過去7日間のトレンド"""  
    from sqlalchemy import func, cast, Date  
      
    daily\_data \= db.query(  
        cast(Message.created\_at, Date).label('date'),  
        func.count(Message.id).label('question\_count')  
    ).join(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Message.role \== 'user',  
        Message.created\_at \>= week\_start  
    ).group\_by(cast(Message.created\_at, Date)).all()  
      
    total\_questions \= sum(\[d.question\_count for d in daily\_data\])  
      
    return {  
        "daily\_data": \[{"date": str(d.date), "question\_count": d.question\_count} for d in daily\_data\],  
        "total\_questions": total\_questions,  
        "comparison\_previous\_week": "+0.0%"  \# 前週比計算はPhase 3で実装  
    }

def get\_confidence\_score(db, facility\_id, week\_start, now):  
    """平均信頼度"""  
    from sqlalchemy import func  
      
    avg\_confidence \= db.query(func.avg(Message.confidence\_score)).join(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Message.role \== 'assistant',  
        Message.confidence\_score.isnot(None),  
        Message.created\_at \>= week\_start  
    ).scalar()  
      
    return {  
        "average\_confidence": round(avg\_confidence \* 100, 1\) if avg\_confidence else 0,  
        "comparison\_previous\_week": "+0.0%"  
    }

def get\_category\_breakdown(db, facility\_id, week\_start, now):  
    """カテゴリ別内訳"""  
    from sqlalchemy import func  
      
    category\_data \= db.query(  
        FAQ.category,  
        func.count(Message.id).label('count')  
    ).join(Message, Message.matched\_faq\_id \== FAQ.id).join(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Message.role \== 'assistant',  
        Message.matched\_faq\_id.isnot(None),  
        Message.created\_at \>= week\_start  
    ).group\_by(FAQ.category).all()  
      
    total \= sum(\[c.count for c in category\_data\])  
      
    breakdown \= \[  
        {  
            "category": c.category,  
            "count": c.count,  
            "percentage": round(c.count / total \* 100, 1\) if total \> 0 else 0  
        }  
        for c in category\_data  
    \]  
      
    return {  
        "category\_breakdown": breakdown,  
        "total\_faq\_responses": total  
    }

def get\_unresolved\_escalations(db, facility\_id):  
    """未解決エスカレーション"""  
      
    unresolved \= db.query(Escalation).join(Conversation).filter(  
        Conversation.facility\_id \== facility\_id,  
        Escalation.resolved\_at.is\_(None)  
    ).order\_by(Escalation.created\_at.desc()).limit(10).all()  
      
    return {  
        "unresolved\_count": len(unresolved),  
        "unresolved\_list": \[  
            {  
                "id": e.id,  
                "reason": e.reason,  
                "guest\_message": e.conversation.messages\[0\].content if e.conversation.messages else "",  
                "created\_at": e.created\_at.isoformat(),  
                "language": e.conversation.language  
            }  
            for e in unresolved  
        \]  
    }  
\`\`\`

\---

\#\# 7\. 実装スケジュール

\#\#\# Phase 2（PoC準備）- Week 3-4

\- \[x\] データベース設計（\`facilities\`テーブル拡張）  
\- \[ \] バックエンドAPI実装  
  \- \[ \] \`/api/v1/admin/dashboard\`エンドポイント  
  \- \[ \] 月次統計計算ロジック（カード1-3）  
  \- \[ \] 未解決エスカレーション取得（カード8）  
\- \[ \] フロントエンド実装  
  \- \[ \] \`MonthlyUsageCard.vue\`（カード1）  
  \- \[ \] \`AiAutomationCard.vue\`（カード2）  
  \- \[ \] \`EscalationsSummaryCard.vue\`（カード3）  
  \- \[ \] \`UnresolvedListCard.vue\`（カード8）

\#\#\# Phase 3（PoC実施）- Month 1-2

\- \[ \] バックエンドAPI拡張  
  \- \[ \] 推定月額コスト計算（カード4）  
  \- \[ \] 週次トレンド集計（カード5）  
  \- \[ \] 平均信頼度計算（カード6）  
  \- \[ \] カテゴリ別内訳集計（カード7）  
\- \[ \] フロントエンド実装  
  \- \[ \] \`EstimatedCostCard.vue\`（カード4）  
  \- \[ \] \`WeeklyTrendCard.vue\`（カード5、Chart.js統合）  
  \- \[ \] \`ConfidenceScoreCard.vue\`（カード6）  
  \- \[ \] \`CategoryBreakdownCard.vue\`（カード7、ドーナツグラフ）  
\- \[ \] 前週比・前月比計算機能追加

\#\#\# Phase 4（本格展開）

\- \[ \] 月次集計キャッシュテーブル実装（パフォーマンス最適化）  
\- \[ \] Stripe連携による実請求額表示  
\- \[ \] プラン変更アラート機能  
\- \[ \] CSVエクスポート機能

\---

\#\# 8\. テストケース

\#\#\# 8.1 月次統計テスト

| テストケース | 入力 | 期待出力 |  
|-------------|------|---------|  
| Freeプラン30件以内 | 質問数20件、プランFree | status: "normal", remaining: 10 |  
| Freeプラン30件超過 | 質問数35件、プランFree | status: "faq\_only", note: "30件超過後はFAQのみ対応" |  
| Miniプラン | 質問数150件、プランMini | overage\_count: 150, overage\_fee: 4500 |  
| Smallプラン上限内 | 質問数150件、プランSmall | status: "normal", remaining: 50 |  
| Smallプラン超過 | 質問数232件、プランSmall | status: "overage", overage\_count: 32, overage\_fee: 960 |  
| Standardプラン警告範囲 | 質問数460件、プランStandard | status: "warning", usage\_percentage: 92.0 |

\#\#\# 8.2 API統合テスト

\`\`\`python  
\# tests/test\_dashboard.py  
import pytest  
from fastapi.testclient import TestClient  
from app.main import app  
from app.auth import create\_access\_token

client \= TestClient(app)

def test\_dashboard\_unauthorized():  
    response \= client.get("/api/v1/admin/dashboard")  
    assert response.status\_code \== 401

def test\_dashboard\_success(test\_db, test\_facility):  
    token \= create\_access\_token({"sub": test\_facility.id})  
    response \= client.get(  
        "/api/v1/admin/dashboard",  
        headers={"Authorization": f"Bearer {token}"}  
    )  
    assert response.status\_code \== 200  
    data \= response.json()  
    assert "monthly\_usage" in data  
    assert "ai\_automation" in data  
    assert data\["monthly\_usage"\]\["plan\_type"\] \== "Small"  
\`\`\`

\---

\#\# 9\. 注意事項・制約

\#\#\# 9.1 Freeプランの特殊処理

\- 30件超過後は\*\*AI応答を停止\*\*し、FAQ対応のみに切り替える  
\- フロントエンドで「FAQのみ対応中」バッジ表示  
\- ゲスト側UIで「現在FAQのみ対応しています」メッセージ表示

\#\#\# 9.2 Miniプランの従量課金

\- \*\*質問数上限なし\*\*（\`monthly\_question\_limit \= NULL\`）  
\- すべての質問が¥30/件で課金  
\- ダッシュボードでプログレスバーは表示せず、「従量課金プラン」バッジのみ

\#\#\# 9.3 タイムゾーン処理

\- すべての統計は\*\*日本時間（JST）\*\*基準  
\- データベースはUTC保存、取得時にJST変換

\#\#\# 9.4 パフォーマンス最適化

\- Phase 2: リアルタイム集計（ポーリング5分間隔）  
\- Phase 3: 日次バッチで\`monthly\_usage\_cache\`テーブル更新  
\- Phase 4: Redis キャッシュ活用（1時間TTL）

\---

\#\# 10\. 今後の拡張案

\#\#\# 10.1 プラン変更推奨機能（Phase 4）

使用状況に応じて最適プランを提案:  
\`\`\`  
現在のプラン: Small（¥3,980/月）  
今月の使用量: 380件（95%）  
推奨: Standardプランに変更すると月額¥2,000お得です  
\`\`\`

\#\#\# 10.2 アラート機能（Expansion Phase A）

\- 上限90%到達時にメール通知  
\- 3日連続でエスカレーション5件以上時に警告  
\- FAQ改善提案（信頼度低下検知）

\#\#\# 10.3 詳細分析ページ（Expansion Phase B）

\- 時間帯別ヒートマップ  
\- 言語別質問数推移  
\- 回答時間分布  
\- ゲストフィードバック詳細

\---

\*\*Document Version\*\*: v1.1    
\*\*Author\*\*: Claude (Anthropic)    
\*\*Created\*\*: 2025-01-14    
\*\*最終更新日\*\*: 2026-01-17    
\*\*更新内容\*\*: 月次集計期間をカレンダー月ベースから契約開始日ベースの請求期間に変更（Stripe統合を見据えた設計）    
\*\*Status\*\*: 実装準備完了