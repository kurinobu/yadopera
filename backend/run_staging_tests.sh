#!/bin/bash
# Phase 1 ステージング環境テスト実行スクリプト
# 実行前に、Railwayダッシュボードから接続情報を取得して環境変数を設定してください

set -e

echo "=========================================="
echo "Phase 1 ステージング環境テスト実行"
echo "=========================================="
echo ""

# 環境変数の確認
if [ -z "$TEST_DATABASE_URL" ]; then
    echo "❌ エラー: TEST_DATABASE_URLが設定されていません"
    echo ""
    echo "Railwayダッシュボードから接続情報を取得して、以下の環境変数を設定してください:"
    echo ""
    echo "export TEST_DATABASE_URL=\"postgresql+asyncpg://postgres:password@host:port/database\""
    echo "export REDIS_URL=\"redis://default:password@host:port\""
    echo "export USE_POSTGRES_TEST=\"true\""
    echo "export USE_OPENAI_MOCK=\"true\""
    echo "export SECRET_KEY=\"your-secret-key-min-32-chars\""
    echo "export CORS_ORIGINS=\"http://localhost:5173\""
    echo ""
    exit 1
fi

echo "✅ 環境変数が設定されています"
echo ""

# テスト実行
echo "テストを実行しています..."
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="test_results_staging_${TIMESTAMP}.txt"

pytest tests/ -v --tb=short > "${OUTPUT_FILE}" 2>&1
TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
echo "テスト実行完了"
echo "=========================================="
echo ""
echo "結果ファイル: ${OUTPUT_FILE}"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ すべてのテストがパスしました！"
    echo ""
    echo "テスト結果のサマリー:"
    tail -20 "${OUTPUT_FILE}"
else
    echo "❌ 一部のテストが失敗しました"
    echo ""
    echo "テスト結果のサマリー:"
    tail -30 "${OUTPUT_FILE}"
fi

echo ""
echo "詳細な結果は ${OUTPUT_FILE} を確認してください"
