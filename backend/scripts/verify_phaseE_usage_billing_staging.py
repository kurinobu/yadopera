#!/usr/bin/env python3
"""
Phase E: ステージング環境で従量課金メーター連携の動作確認を行うスクリプト

ステージングのバックエンドにデプロイ済みのコードに対して、
GET /api/v1/developer/health/phase-e を呼び出し、検証結果を表示する。

使い方:
  # 開発者パスワードでログインしてトークン取得し、Phase E 検証を実行（推奨）
  DEVELOPER_PASSWORD=your_developer_password python scripts/verify_phaseE_usage_billing_staging.py

  # すでに JWT を持っている場合
  DEV_JWT=eyJ... python scripts/verify_phaseE_usage_billing_staging.py

  # ステージングの URL を変更する場合（デフォルト: https://yadopera-backend-staging.onrender.com）
  STAGING_BACKEND_URL=https://your-staging.onrender.com DEVELOPER_PASSWORD=... python scripts/verify_phaseE_usage_billing_staging.py

ローカルから実行（backend ディレクトリがカレントでなくても可）:
  python backend/scripts/verify_phaseE_usage_billing_staging.py
"""

import os
import sys
import json

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Run: pip install httpx")
    sys.exit(2)

STAGING_BACKEND_URL = os.environ.get(
    "STAGING_BACKEND_URL",
    "https://yadopera-backend-staging.onrender.com",
).rstrip("/")
DEV_JWT = os.environ.get("DEV_JWT", "")
DEVELOPER_PASSWORD = os.environ.get("DEVELOPER_PASSWORD", "")


def get_developer_token() -> str:
    if DEV_JWT:
        return DEV_JWT
    if not DEVELOPER_PASSWORD:
        print(
            "Set DEVELOPER_PASSWORD or DEV_JWT in environment.\n"
            "Example: DEVELOPER_PASSWORD=your_pass python scripts/verify_phaseE_usage_billing_staging.py"
        )
        sys.exit(1)
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            f"{STAGING_BACKEND_URL}/api/v1/developer/auth/login",
            json={"password": DEVELOPER_PASSWORD},
        )
    if r.status_code != 200:
        print(f"Developer login failed: {r.status_code} {r.text[:300]}")
        sys.exit(1)
    data = r.json()
    token = data.get("access_token")
    if not token:
        print("Login response had no access_token.")
        sys.exit(1)
    return token


def run_phase_e_verification(token: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(timeout=30.0) as client:
        r = client.get(
            f"{STAGING_BACKEND_URL}/api/v1/developer/health/phase-e",
            headers=headers,
        )
    if r.status_code != 200:
        print(f"Phase E health request failed: {r.status_code}")
        print(r.text[:500])
        return False
    data = r.json()
    ok_count = data.get("ok_count", 0)
    ng_count = data.get("ng_count", 0)
    all_ok = data.get("all_ok", False)
    checks = data.get("checks", [])

    print(f"Staging backend: {STAGING_BACKEND_URL}")
    print("Phase E verification result:")
    for c in checks:
        status = "OK" if c.get("ok") else "NG"
        msg = c.get("message") or ""
        print(f"  [{status}] {c.get('name', '')} {msg}")
    print("")
    print(f"Result: OK={ok_count}, NG={ng_count}")
    if all_ok:
        print("Phase E staging verification: All OK.")
    else:
        print("Phase E staging verification: Some checks failed.")
    return all_ok


def main() -> int:
    print("Getting developer token...")
    token = get_developer_token()
    print("Running Phase E verification on staging...")
    ok = run_phase_e_verification(token)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
