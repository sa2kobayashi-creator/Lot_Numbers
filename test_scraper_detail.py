"""
loto-life.netのロト系のHTML構造を詳しく確認
"""
import requests
from bs4 import BeautifulSoup

urls = {
    "ミニロト": "https://loto-life.net/mini-loto/past",
    "ロト6": "https://loto-life.net/loto6/past",
    "ロト7": "https://loto-life.net/loto7/past",
}

for name, url in urls.items():
    print(f"\n{'='*60}")
    print(f"{name}: {url}")
    print('='*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        tables = soup.find_all('table')
        
        if tables:
            # 最初のテーブルを詳しく確認
            table = tables[0]
            rows = table.find_all('tr')
            
            print(f"行数: {len(rows)}")
            
            # 各行を詳しく表示
            for i, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                print(f"\n行 {i}:")
                for j, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    print(f"  列{j}: '{text}'")
                    # HTML構造も確認
                    if '本数字' in text or 'ボーナス' in text:
                        print(f"    HTML: {cell}")
            
            # 行1の当選番号部分を詳しく解析
            if len(rows) > 1:
                number_row = rows[1]
                number_cells = number_row.find_all(['td', 'th'])
                if len(number_cells) >= 2:
                    number_text = number_cells[1].get_text(strip=True)
                    print(f"\n当選番号テキスト: '{number_text}'")
                    
                    # 正規表現でテスト
                    import re
                    main_match = re.search(r'本数字[：:]\s*(.+?)(?:ボーナス|$)', number_text)
                    if main_match:
                        print(f"本数字部分: '{main_match.group(1)}'")
                        main_nums = re.findall(r'\d+', main_match.group(1))
                        print(f"抽出された数字: {main_nums}")
                    
                    bonus_match = re.search(r'ボーナス[：:]\s*(.+)', number_text)
                    if bonus_match:
                        print(f"ボーナス部分: '{bonus_match.group(1)}'")
                        bonus_nums = re.findall(r'\d+', bonus_match.group(1))
                        print(f"抽出されたボーナス: {bonus_nums}")
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

