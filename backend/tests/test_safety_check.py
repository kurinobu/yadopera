"""
安全カテゴリ判定テスト
"""

import pytest
from app.ai.safety_check import check_safety_category, MEDICAL_KEYWORDS, SAFETY_KEYWORDS


class TestSafetyCheck:
    """安全カテゴリ判定テスト"""
    
    def test_medical_keyword_detection(self):
        """医療関連キーワード検出テスト"""
        test_cases = [
            ("I need a hospital", True),
            ("Call a doctor", True),
            ("I'm sick", True),
            ("I have a fever", True),
            ("I need medicine", True),
            ("I'm in pain", True),
            ("病院に行きたい", True),
            ("医者を呼んで", True),
            ("具合悪い", True),
            ("What time is check-in?", False),
            ("Where is the WiFi password?", False),
        ]
        
        for question, expected in test_cases:
            result = check_safety_category(question)
            assert result == expected, f"Failed for: {question}"
    
    def test_safety_keyword_detection(self):
        """安全・避難関連キーワード検出テスト"""
        test_cases = [
            ("There's a fire!", True),
            ("Earthquake!", True),
            ("Where is the emergency exit?", True),
            ("I need to evacuate", True),
            ("火災です", True),
            ("地震です", True),
            ("非常口はどこですか", True),
            ("What time is check-in?", False),
            ("Where is the laundry room?", False),
        ]
        
        for question, expected in test_cases:
            result = check_safety_category(question)
            assert result == expected, f"Failed for: {question}"
    
    def test_case_insensitive(self):
        """大文字小文字を区別しないテスト"""
        test_cases = [
            ("FIRE!", True),
            ("fire", True),
            ("Fire", True),
            ("HOSPITAL", True),
            ("hospital", True),
        ]
        
        for question, expected in test_cases:
            result = check_safety_category(question)
            assert result == expected, f"Failed for: {question}"
    
    def test_keyword_list_completeness(self):
        """キーワードリストの完全性テスト"""
        assert len(MEDICAL_KEYWORDS) > 0, "Medical keywords list should not be empty"
        assert len(SAFETY_KEYWORDS) > 0, "Safety keywords list should not be empty"
        
        # 主要なキーワードが含まれているか確認
        assert "hospital" in MEDICAL_KEYWORDS
        assert "fire" in SAFETY_KEYWORDS
        assert "病院" in MEDICAL_KEYWORDS
        assert "火災" in SAFETY_KEYWORDS


