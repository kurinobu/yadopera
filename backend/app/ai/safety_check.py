"""
安全カテゴリ判定（v0.3新規）
"""

# 医療関連キーワード
MEDICAL_KEYWORDS = [
    'hospital', 'doctor', 'ambulance', 'emergency', 'sick', 'injured',
    'fever', 'allergy', 'medicine', 'pharmacy', 'pain', 'bleeding', 'unconscious',
    '病院', '医者', '救急車', '具合悪い', '怪我', '熱', 'アレルギー', '薬', '痛い'
]

# 安全・避難関連キーワード
SAFETY_KEYWORDS = [
    'fire', 'earthquake', 'evacuation', 'evacuate', 'escape', 'escape route',
    'emergency exit', 'tsunami', 'typhoon',
    '火災', '火事', '地震', '避難', '非常口', '津波', '台風'
]


def check_safety_category(question: str) -> bool:
    """
    安全カテゴリ判定（v0.3新規）
    医療・安全関連キーワード検出時は即エスカレーション
    
    Args:
        question: ゲストの質問
    
    Returns:
        bool: 安全カテゴリに該当する場合はTrue
    """
    question_lower = question.lower()
    
    # 医療関連キーワード検出
    if any(keyword in question_lower for keyword in MEDICAL_KEYWORDS):
        return True
    
    # 安全・避難関連キーワード検出
    if any(keyword in question_lower for keyword in SAFETY_KEYWORDS):
        return True
    
    return False

