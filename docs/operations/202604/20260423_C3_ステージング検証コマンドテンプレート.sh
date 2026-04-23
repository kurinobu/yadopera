#!/usr/bin/env bash
set -euo pipefail

# C-3 ステージング検証コマンドテンプレート
# 使い方:
# 1) 必要な環境変数を export
# 2) 必要な curl を順に実行
# 3) 結果を実施記録に貼り付け

# 必須（例）
# export BASE_URL="https://<staging-api-host>"
# export FACILITY_ID="1"
# export SESSION_ID="<guest-session-id>"
# export ADMIN_BEARER_TOKEN="<admin-jwt>"

echo "=== C-3 ステージング検証（テンプレート）==="
echo "BASE_URL=${BASE_URL:-<unset>}"
echo "FACILITY_ID=${FACILITY_ID:-<unset>}"
echo "SESSION_ID=${SESSION_ID:-<unset>}"
echo

echo "1) C-3 OFF時（期待: 404）"
curl -i -X POST "${BASE_URL}/api/v1/chat/contact-consent" \
  -H "Content-Type: application/json" \
  -d "{
    \"facility_id\": ${FACILITY_ID},
    \"session_id\": \"${SESSION_ID}\",
    \"email\": \"guest@example.com\",
    \"guest_name\": \"Guest\",
    \"consent\": true
  }"
echo
echo

echo "2) C-3 ON時（期待: 200 + contactability_status=contactable）"
curl -i -X POST "${BASE_URL}/api/v1/chat/contact-consent" \
  -H "Content-Type: application/json" \
  -d "{
    \"facility_id\": ${FACILITY_ID},
    \"session_id\": \"${SESSION_ID}\",
    \"email\": \"guest@example.com\",
    \"guest_name\": \"Guest\",
    \"consent\": true
  }"
echo
echo

echo "3) 管理画面: 会話詳細取得（受付番号/状態確認）"
curl -i -X GET "${BASE_URL}/api/v1/chat/history/${SESSION_ID}?facility_id=${FACILITY_ID}" \
  -H "Authorization: Bearer ${ADMIN_BEARER_TOKEN}" \
  -H "Content-Type: application/json"
echo
echo

echo "4) B-1 管理者手動返信（期待: 201）"
curl -i -X POST "${BASE_URL}/api/v1/admin/conversations/${SESSION_ID}/reply" \
  -H "Authorization: Bearer ${ADMIN_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"スタッフです。確認して対応します。\"
  }"
echo
echo "=== 完了 ==="
