#!/usr/bin/env python3
"""
Phase 4 Phase C: 管理 API（プラン・請求）の動作確認スクリプト

使い方:
  # JWT を環境変数で指定
  ADMIN_JWT="eyJ..." python scripts/test_admin_plans_billing_api.py

  # または メール・パスワードでログインしてトークン取得
  ADMIN_EMAIL="test13@air-edison.com" ADMIN_PASSWORD="your_password" python scripts/test_admin_plans_billing_api.py

  # API のベース URL を変更（デフォルト: http://localhost:8000）
  API_BASE_URL="http://localhost:8000" ADMIN_JWT="eyJ..." python scripts/test_admin_plans_billing_api.py

Docker でバックエンドが動いている場合:
  docker compose run --rm backend python scripts/test_admin_plans_billing_api.py
  （その前に ADMIN_JWT または ADMIN_EMAIL+ADMIN_PASSWORD を backend/.env または -e で渡す）
"""

import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Run: pip install httpx")
    sys.exit(2)

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")
ADMIN_JWT = os.environ.get("ADMIN_JWT", "")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def get_token() -> str:
    if ADMIN_JWT:
        return ADMIN_JWT
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        print("Set ADMIN_JWT or both ADMIN_EMAIL and ADMIN_PASSWORD in environment.")
        sys.exit(1)
    with httpx.Client(timeout=15.0) as client:
        r = client.post(
            f"{API_BASE}/api/v1/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
    if r.status_code != 200:
        print(f"Login failed: {r.status_code} {r.text[:200]}")
        sys.exit(1)
    data = r.json()
    token = data.get("access_token")
    if not token:
        print("Login response had no access_token.")
        sys.exit(1)
    return token


def run_tests(token: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    all_ok = True

    # 1. GET /api/v1/admin/plans
    print("1. GET /api/v1/admin/plans")
    with httpx.Client(timeout=15.0) as client:
        r = client.get(f"{API_BASE}/api/v1/admin/plans", headers=headers)
    if r.status_code != 200:
        print(f"   NG status={r.status_code} body={r.text[:300]}")
        all_ok = False
    else:
        data = r.json()
        if "current_plan_type" not in data or "plans" not in data:
            print("   NG response missing current_plan_type or plans")
            all_ok = False
        elif len(data.get("plans", [])) != 5:
            print(f"   NG expected 5 plans, got {len(data.get('plans', []))}")
            all_ok = False
        else:
            print(f"   OK current_plan_type={data.get('current_plan_type')} plans={len(data['plans'])} stripe_configured={data.get('stripe_configured')}")

    # 2. GET /api/v1/admin/invoices
    print("2. GET /api/v1/admin/invoices")
    with httpx.Client(timeout=15.0) as client:
        r = client.get(f"{API_BASE}/api/v1/admin/invoices", headers=headers)
    if r.status_code != 200:
        print(f"   NG status={r.status_code} body={r.text[:300]}")
        all_ok = False
    else:
        data = r.json()
        if "invoices" not in data:
            print("   NG response missing invoices")
            all_ok = False
        else:
            count = len(data.get("invoices", []))
            print(f"   OK invoices={count}")

    # 3. 請求が1件以上あれば領収書 URL 取得を試す
    if all_ok and r.status_code == 200:
        data = r.json()
        invoices = data.get("invoices", [])
        if invoices and invoices[0].get("id"):
            inv_id = invoices[0]["id"]
            print(f"3. GET /api/v1/admin/invoices/{inv_id}/receipt")
            with httpx.Client(timeout=15.0) as client:
                r2 = client.get(f"{API_BASE}/api/v1/admin/invoices/{inv_id}/receipt", headers=headers)
            if r2.status_code != 200:
                print(f"   NG status={r2.status_code} (may be normal if no hosted URL)")
            else:
                rec = r2.json()
                url = rec.get("url", "")
                print(f"   OK url={url[:60]}..." if len(url) > 60 else f"   OK url={url}")
        else:
            print("3. GET .../receipt (skip: no invoices)")

    return all_ok


def main():
    print(f"API_BASE={API_BASE}")
    token = get_token()
    print("Token obtained.")
    ok = run_tests(token)
    print("---")
    print("Result: PASS" if ok else "Result: FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
