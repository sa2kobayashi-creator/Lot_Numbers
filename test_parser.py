"""
パーサーの動作をテスト
"""
import re

test_cases = [
    ("ミニロト", "本数字　：6　12　16　19　31ボーナス：25", 5),
    ("ロト6", "本数字　：5　7　21　22　38　41ボーナス：24", 6),
    ("ロト7", "本数字　：3　12　25　29　30　32 33ボーナス：28　31", 7),
]

for name, text, expected_count in test_cases:
    print(f"\n{name}: '{text}'")
    
    # 現在の正規表現
    main_match = re.search(r'本数字[：:]\s*([^ボ]+?)(?:ボーナス|$)', text)
    if main_match:
        main_text = main_match.group(1).strip()
        print(f"  マッチした部分: '{main_text}'")
        main_nums = re.findall(r'\d+', main_text)
        print(f"  抽出された数字: {main_nums}")
        print(f"  数字数: {len(main_nums)}, 期待: {expected_count}")
    else:
        print("  マッチしませんでした")
    
    # ボーナス
    bonus_match = re.search(r'ボーナス[：:]\s*(.+)', text)
    if bonus_match:
        bonus_text = bonus_match.group(1).strip()
        bonus_nums = re.findall(r'\d+', bonus_text)
        print(f"  ボーナス: {bonus_nums}")

