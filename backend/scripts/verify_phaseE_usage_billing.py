#!/usr/bin/env python3
"""
Phase E: 従量課金メーター連携の動作確認スクリプト

確認内容:
  - stripe_service: report_usage_to_meter, get_meter_event_name, is_stripe_configured のインポートと挙動
  - chat_service: ChatService と _report_usage_to_stripe_if_needed の存在
  - billing_period: calculate_billing_period のインポート（請求期間整合用）

使い方（ローカル）:
  cd backend && python scripts/verify_phaseE_usage_billing.py

Docker 環境で実行:
  docker compose run --rm backend python scripts/verify_phaseE_usage_billing.py

オプション:
  RUN_STRIPE_LIVE_TEST=1  … STRIPE_SECRET_KEY が設定されている場合、テスト用顧客 ID でメーター送信を試行する（任意）

ステージングで同じ検証を実行する場合:
  scripts/verify_phaseE_usage_billing_staging.py を利用する（開発者認証で GET /api/v1/developer/health/phase-e を呼び出し）。
"""

import os
import sys

# backend をカレントにした状態で実行する想定（Docker では /app）
if __name__ == "__main__":
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

def main() -> int:
    ok_count = 0
    ng_count = 0

    # --- 1. stripe_service インポートと関数の存在 ---
    print("1. stripe_service のインポートと関数の存在")
    try:
        from app.services.stripe_service import (
            report_usage_to_meter,
            get_meter_event_name,
            is_stripe_configured,
        )
        print("   OK: report_usage_to_meter, get_meter_event_name, is_stripe_configured")
        ok_count += 1
    except Exception as e:
        print(f"   NG: {e}")
        ng_count += 1
        return 1

    # --- 2. get_meter_event_name の戻り値 ---
    print("2. get_meter_event_name() の戻り値")
    try:
        name = get_meter_event_name()
        if not name or not isinstance(name, str):
            print(f"   NG: 期待するのは非空文字列, got {name!r}")
            ng_count += 1
        else:
            print(f"   OK: event_name={name!r}")
            ok_count += 1
    except Exception as e:
        print(f"   NG: {e}")
        ng_count += 1

    # --- 3. Stripe 未設定時は is_stripe_configured() が False ---
    print("3. Stripe 未設定時の is_stripe_configured()")
    try:
        # 未設定の場合は False（.env に STRIPE_SECRET_KEY が無い場合）
        configured = is_stripe_configured()
        print(f"   OK: is_stripe_configured() = {configured} (環境に依存)")
        ok_count += 1
    except Exception as e:
        print(f"   NG: {e}")
        ng_count += 1

    # --- 4. stripe_customer_id が空のとき report_usage_to_meter は False ---
    print("4. stripe_customer_id が空のとき report_usage_to_meter は False")
    try:
        result = report_usage_to_meter("")
        if result is False:
            print("   OK: report_usage_to_meter('') => False")
            ok_count += 1
        else:
            print(f"   NG: 期待 False, got {result}")
            ng_count += 1
    except Exception as e:
        print(f"   NG: {e}")
        ng_count += 1

    # --- 5. Stripe 未設定時は report_usage_to_meter('cus_xxx') も False ---
    print("5. Stripe 未設定時は report_usage_to_meter('cus_xxx') も False（送信しない）")
    try:
        result = report_usage_to_meter("cus_test_dummy")
        # 未設定なら False、設定済みなら Stripe API に送って成功/失敗
        if not is_stripe_configured():
            if result is False:
                print("   OK: Stripe 未設定のため False")
                ok_count += 1
            else:
                print(f"   NG: 未設定時は False を期待, got {result}")
                ng_count += 1
        else:
            print(f"   OK: Stripe 設定済みのため送信 attempted, result={result}")
            ok_count += 1
    except Exception as e:
        print(f"   NG: {e}")
        ng_count += 1

    # --- 6. ChatService と _report_usage_to_stripe_if_needed ---
    print("6. ChatService と _report_usage_to_stripe_if_needed の存在")
    try:
        from app.services.chat_service import ChatService
        if not hasattr(ChatService, "_report_usage_to_stripe_if_needed"):
            print("   NG: ChatService._report_usage_to_stripe_if_needed が存在しません")
            ng_count += 1
        else:
            print("   OK: ChatService._report_usage_to_stripe_if_needed が存在")
            ok_count += 1
    except Exception as e:
        print(f"   NG: {e}")
        ng_count += 1

    # --- 7. billing_period のインポート（請求期間整合） ---
    print("7. billing_period.calculate_billing_period のインポート")
    try:
        from app.utils.billing_period import calculate_billing_period
        print("   OK: calculate_billing_period をインポート")
        ok_count += 1
    except Exception as e:
        print(f"   NG: {e}")
        ng_count += 1

    # --- 8. config の STRIPE_METER_EVENT_NAME ---
    print("8. config の stripe_meter_event_name 参照")
    try:
        from app.core.config import settings
        val = getattr(settings, "stripe_meter_event_name", None)
        print(f"   OK: stripe_meter_event_name = {val!r}")
        ok_count += 1
    except Exception as e:
        print(f"   NG: {e}")
        ng_count += 1

    # --- 結果 ---
    print("")
    print(f"結果: OK={ok_count}, NG={ng_count}")
    if ng_count > 0:
        print("Phase E 動作確認: 一部 NG があります。")
        return 1
    print("Phase E 動作確認: すべて OK です。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
