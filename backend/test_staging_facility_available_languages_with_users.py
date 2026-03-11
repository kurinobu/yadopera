"""
ステージング環境での施設情報取得APIの利用可能言語取得テスト（ユーザーIDベース）
API経由でテストを実行
"""

import asyncio
import httpx
import os
from typing import Dict, Optional
import json


# テスト環境設定
STAGING_API_URL = os.getenv("STAGING_API_URL", "https://yadopera-backend-staging.onrender.com")
API_BASE = f"{STAGING_API_URL}/api/v1"

# テスト用ユーザー情報
TEST_USERS = {
    "Free": {"email": "test31@example.com", "password": "testpassword123"},
    "Mini": {"email": "test41@example.com", "password": "testpassword123"},
    "Small": {"email": "test51@example.com", "password": "testpassword123"},
    "Standard": {"email": "test61@example.com", "password": "testpassword123"},
    "Premium": {"email": "test71@example.com", "password": "testpassword123"},
}

# 期待される言語リスト（多言語5: Premium は zh-CN, es 追加）
EXPECTED_LANGUAGES = {
    "Free": ["ja"],
    "Mini": ["ja", "en"],
    "Small": ["ja", "en", "zh-TW"],
    "Standard": ["ja", "en", "zh-TW", "fr"],
    "Premium": ["ja", "en", "zh-TW", "zh-CN", "fr", "ko", "es"],
}


class FacilityAvailableLanguagesTester:
    """施設情報取得APIの利用可能言語取得テストクラス"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_BASE, timeout=30.0)
        self.results: Dict[str, Dict] = {}
        self.facility_slugs: Dict[str, str] = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def login(self, email: str, password: str) -> Optional[str]:
        """ログインしてトークンを取得"""
        try:
            response = await self.client.post(
                "/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code != 200:
                print(f"❌ ログイン失敗: HTTP {response.status_code}")
                print(f"   レスポンス: {response.text}")
                return None
            
            data = response.json()
            token = data.get("access_token")
            
            if token:
                # トークンをヘッダーに設定
                self.client.headers.update({"Authorization": f"Bearer {token}"})
                print(f"✅ ログイン成功: {email}")
                return token
            else:
                print(f"❌ トークンが取得できませんでした: {email}")
                return None
                
        except Exception as e:
            print(f"❌ ログインエラー: {str(e)}")
            return None
    
    async def get_facility_info(self, plan: str) -> Optional[Dict]:
        """施設情報を取得"""
        try:
            # 施設設定APIから施設情報を取得
            response = await self.client.get("/admin/facility/settings")
            
            if response.status_code != 200:
                print(f"❌ 施設情報取得失敗: HTTP {response.status_code}")
                print(f"   レスポンス: {response.text}")
                return None
            
            data = response.json()
            
            # レスポンス構造を確認（デバッグ用）
            print(f"   📊 施設設定APIレスポンス構造: {list(data.keys())}")
            
            # 施設情報を取得（facilityキーの下にネストされている）
            facility = data.get("facility", {})
            
            if facility:
                slug = facility.get("slug")
                if slug:
                    self.facility_slugs[plan] = slug
                    print(f"✅ 施設情報取得成功: {plan}プラン, slug={slug}")
                    print(f"   plan_type: {facility.get('plan_type', 'N/A')}")
                    return facility
                else:
                    print(f"❌ 施設slugが取得できませんでした: {plan}プラン")
                    print(f"   施設情報: {facility}")
                    return None
            else:
                print(f"❌ 施設情報が取得できませんでした: {plan}プラン")
                print(f"   レスポンスデータ: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ 施設情報取得エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    async def test_facility_available_languages(self, plan: str, slug: str, expected_languages: list):
        """施設情報取得APIで利用可能言語をテスト"""
        print(f"\n{'='*60}")
        print(f"テスト: {plan}プラン")
        print(f"{'='*60}")
        print(f"施設slug: {slug}")
        print(f"期待される言語: {expected_languages}")
        
        try:
            # 施設情報取得APIを呼び出し
            response = await self.client.get(f"/facility/{slug}")
            
            if response.status_code != 200:
                print(f"❌ エラー: HTTP {response.status_code}")
                print(f"   レスポンス: {response.text}")
                self.results[plan] = {
                    "status": "FAILED",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                return False
            
            data = response.json()
            facility = data.get("facility", {})
            
            plan_type = facility.get("plan_type")
            available_languages = facility.get("available_languages", [])
            
            print(f"✅ APIレスポンス取得成功")
            print(f"   plan_type: {plan_type}")
            print(f"   available_languages: {available_languages}")
            
            # 検証
            success = True
            errors = []
            
            if plan_type != plan:
                success = False
                errors.append(f"plan_type不一致: 期待={plan}, 実際={plan_type}")
            
            if set(available_languages) != set(expected_languages):
                success = False
                errors.append(f"available_languages不一致: 期待={expected_languages}, 実際={available_languages}")
            
            if success:
                print(f"✅ テスト成功")
                self.results[plan] = {
                    "status": "PASSED",
                    "plan_type": plan_type,
                    "available_languages": available_languages
                }
            else:
                print(f"❌ テスト失敗")
                for error in errors:
                    print(f"   - {error}")
                self.results[plan] = {
                    "status": "FAILED",
                    "plan_type": plan_type,
                    "available_languages": available_languages,
                    "errors": errors
                }
            
            return success
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            import traceback
            traceback.print_exc()
            self.results[plan] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
    
    async def test_language_parameter(self, plan: str, slug: str):
        """languageパラメータのテスト"""
        print(f"\n{'='*60}")
        print(f"テスト: {plan}プラン - languageパラメータ")
        print(f"{'='*60}")
        
        test_cases = [
            ("ja", "日本語"),
            ("en", "英語"),
            ("zh-TW", "中国語"),
        ]
        
        for lang_code, lang_name in test_cases:
            try:
                response = await self.client.get(f"/facility/{slug}?language={lang_code}")
                
                if response.status_code != 200:
                    print(f"❌ {lang_name} ({lang_code}): HTTP {response.status_code}")
                    continue
                
                data = response.json()
                top_questions = data.get("top_questions", [])
                
                print(f"✅ {lang_name} ({lang_code}): {len(top_questions)}件のFAQ取得")
                
                if top_questions:
                    first_question = top_questions[0]
                    print(f"   最初のFAQ: {first_question.get('question', 'N/A')[:50]}...")
                
            except Exception as e:
                print(f"❌ {lang_name} ({lang_code}): エラー - {str(e)}")
    
    def print_summary(self):
        """テスト結果のサマリーを表示"""
        print(f"\n{'='*60}")
        print("テスト結果サマリー")
        print(f"{'='*60}")
        
        passed = sum(1 for r in self.results.values() if r.get("status") == "PASSED")
        failed = sum(1 for r in self.results.values() if r.get("status") == "FAILED")
        errors = sum(1 for r in self.results.values() if r.get("status") == "ERROR")
        
        print(f"✅ 成功: {passed}/{len(self.results)}")
        print(f"❌ 失敗: {failed}/{len(self.results)}")
        print(f"⚠️  エラー: {errors}/{len(self.results)}")
        
        print(f"\n詳細:")
        for plan, result in self.results.items():
            status = result.get("status", "UNKNOWN")
            if status == "PASSED":
                print(f"  ✅ {plan}: {result.get('plan_type')} - {result.get('available_languages')}")
            elif status == "FAILED":
                print(f"  ❌ {plan}: {result.get('errors', [])}")
            else:
                print(f"  ⚠️  {plan}: {result.get('error', 'Unknown error')}")
        
        print(f"\n取得した施設slug:")
        for plan, slug in self.facility_slugs.items():
            print(f"  - {plan}: {slug}")


async def main():
    """メイン関数"""
    print("="*60)
    print("ステージング環境: 施設情報取得APIテスト（ユーザーIDベース）")
    print("="*60)
    print(f"API URL: {STAGING_API_URL}")
    print()
    
    async with FacilityAvailableLanguagesTester() as tester:
        # 各プランのテストを実行
        for plan, user_info in TEST_USERS.items():
            print(f"\n{'='*60}")
            print(f"{plan}プランのテスト開始")
            print(f"{'='*60}")
            
            # ログイン
            token = await tester.login(user_info["email"], user_info["password"])
            if not token:
                print(f"❌ {plan}プランのログインに失敗しました。スキップします。")
                tester.results[plan] = {
                    "status": "ERROR",
                    "error": "Login failed"
                }
                continue
            
            # 施設情報を取得
            facility_info = await tester.get_facility_info(plan)
            if not facility_info:
                print(f"❌ {plan}プランの施設情報取得に失敗しました。スキップします。")
                tester.results[plan] = {
                    "status": "ERROR",
                    "error": "Facility info retrieval failed"
                }
                continue
            
            # 施設slugを取得
            slug = facility_info.get("slug")
            if not slug:
                print(f"❌ {plan}プランの施設slugが取得できませんでした。スキップします。")
                tester.results[plan] = {
                    "status": "ERROR",
                    "error": "Facility slug not found"
                }
                continue
            
            # トークンをクリア（公開APIなので認証不要）
            tester.client.headers.pop("Authorization", None)
            
            # 利用可能言語をテスト
            expected_languages = EXPECTED_LANGUAGES[plan]
            await tester.test_facility_available_languages(plan, slug, expected_languages)
        
        # languageパラメータのテスト（Premiumプランで実行）
        if "Premium" in tester.facility_slugs:
            tester.client.headers.pop("Authorization", None)
            await tester.test_language_parameter("Premium", tester.facility_slugs["Premium"])
        
        # サマリー表示
        tester.print_summary()
        
        # 結果を返す
        passed = sum(1 for r in tester.results.values() if r.get("status") == "PASSED")
        total = len(tester.results)
        
        if passed == total:
            print(f"\n✅ すべてのテストが成功しました ({passed}/{total})")
            return 0
        else:
            print(f"\n❌ 一部のテストが失敗しました ({passed}/{total})")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

