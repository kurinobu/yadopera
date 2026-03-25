#!/usr/bin/env bash
# A-4（スタッフ通知メール）関連の pytest を、docker compose の PostgreSQL 上で実行する。
# 前提: リポジトリルートで docker compose の postgres サービスが起動可能であること（既定ポート 5433）。
#
# 使用例（リポジトリルート）:
#   bash backend/scripts/run_a4_tests_with_docker_postgres.sh
#   bash backend/scripts/run_a4_tests_with_docker_postgres.sh -q tests/test_escalation_notification_service.py::test_send_staff_escalation_notification_includes_receipt_id_everywhere

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker が見つかりません。" >&2
  exit 1
fi

docker compose up -d postgres

for i in $(seq 1 30); do
  if docker compose exec -T postgres pg_isready -U yadopera_user -d yadopera >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker compose exec -T postgres pg_isready -U yadopera_user -d yadopera >/dev/null 2>&1; then
  echo "postgres の起動待ちがタイムアウトしました。" >&2
  exit 1
fi

docker compose exec -T postgres psql -U yadopera_user -d postgres -tc \
  "SELECT 1 FROM pg_database WHERE datname = 'yadopera_test'" | grep -q 1 \
  || docker compose exec -T postgres psql -U yadopera_user -d postgres -c \
    "CREATE DATABASE yadopera_test;"

export USE_POSTGRES_TEST=true
export TEST_DATABASE_URL="${TEST_DATABASE_URL:-postgresql+asyncpg://yadopera_user:yadopera_password@127.0.0.1:5433/yadopera_test}"

cd "$ROOT/backend"
exec python -m pytest \
  tests/test_escalation_notification_service.py \
  tests/test_overnight_queue.py \
  "$@"
