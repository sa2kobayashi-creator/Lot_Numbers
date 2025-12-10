"""
loto-life.netのHTML構造を確認するテストスクリプト
"""
import requests
from bs4 import BeautifulSoup

urls = {
    "ミニロト": "https://loto-life.net/mini-loto/past",
    "ロト6": "https://loto-life.net/loto6/past",
    "ロト7": "https://loto-life.net/loto7/past",
    "ナンバーズ4": "https://loto-life.net/numbers4/past",
    "ナンバーズ3": "https://loto-life.net/numbers3/past"
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
        
        # テーブルを探す
        tables = soup.find_all('table')
        print(f"テーブル数: {len(tables)}")
        
        if tables:
            # 最初のテーブルの構造を確認
            table = tables[0]
            rows = table.find_all('tr')
            print(f"行数: {len(rows)}")
            
            # 最初の3行を表示
            for i, row in enumerate(rows[:3]):
                cells = row.find_all(['td', 'th'])
                print(f"\n行 {i}:")
                for j, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    print(f"  列{j}: {text[:50]}")  # 最初の50文字のみ
        
        # その他の構造を確認
        print("\nその他の構造:")
        # クラス名やIDでテーブルを探す
        for class_name in ['table', 'data-table', 'result-table', 'past-table']:
            found = soup.find_all(class_=class_name)
            if found:
                print(f"  class='{class_name}' が見つかりました: {len(found)}個")
        
    except Exception as e:
        print(f"エラー: {e}")

