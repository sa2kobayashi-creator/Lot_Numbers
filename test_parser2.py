"""
パーサーの動作をテスト（改善版）
"""
import re

test_cases = [
    ("ミニロト", "本数字　：6　12　16　19　31ボーナス：25", 5),
    ("ロト6", "本数字　：5　7　21　22　38　41ボーナス：24", 6),
    ("ロト7", "本数字　：3　12　25　29　30　32 33ボーナス：28　31", 7),
]

for name, text, expected_count in test_cases:
    print(f"\n{name}: '{text}'")
    
    # 方法1: 本数字：からボーナスの前まで
    pattern1 = r'本数字[：:][\s　]*(.+?)(?:ボーナス|$)'
    match1 = re.search(pattern1, text)
    if match1:
        main_text = match1.group(1).strip()
        print(f"  方法1 - マッチ: '{main_text}'")
        nums = re.findall(r'\d+', main_text)
        print(f"  数字: {nums}, 数: {len(nums)}")
    
    # 方法2: 本数字：の後、ボーナス：の前
    pattern2 = r'本数字[：:][\s　]*(.+?)[ボ]'
    match2 = re.search(pattern2, text)
    if match2:
        main_text = match2.group(1).strip()
        print(f"  方法2 - マッチ: '{main_text}'")
        nums = re.findall(r'\d+', main_text)
        print(f"  数字: {nums}, 数: {len(nums)}")
    
    # 方法3: 分割して取得
    if 'ボーナス' in text:
        parts = text.split('ボーナス')
        if len(parts) > 0:
            main_part = parts[0]
            if '本数字' in main_part:
                main_text = main_part.split('本数字')[1].split('：')[1] if '：' in main_part.split('本数字')[1] else main_part.split('本数字')[1].split(':')[1]
                print(f"  方法3 - マッチ: '{main_text.strip()}'")
                nums = re.findall(r'\d+', main_text)
                print(f"  数字: {nums}, 数: {len(nums)}")

