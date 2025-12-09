"""
データ取得機能
外部APIやCSVファイルからデータを取得してデータベースに保存

注意: Webスクレイピング機能を使用する場合は、各サイトの利用規約を必ず確認し、
サーバーに負荷をかけないよう適切な間隔を空けてアクセスしてください。
"""
import pandas as pd
import requests
import time
import re
import ast
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from database import DatabaseManager
from models import Numbers3Data, NumbersData, Loto6Data, Loto7Data, MinilotoData

# BeautifulSoupはオプショナル（Webスクレイピング機能を使用する場合のみ必要）
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None


class DataFetcher:
    """データ取得クラス"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        データ取得クラスの初期化
        
        Args:
            db_manager: データベースマネージャーインスタンス
        """
        self.db = db_manager
    
    def import_from_csv(self, file_path: str, lottery_type: str) -> int:
        """
        CSVファイルからデータをインポート
        
        Args:
            file_path: CSVファイルのパス
            lottery_type: 宝くじタイプ ('numbers', 'loto6', 'loto7', 'miniloto')
        
        Returns:
            インポートされたレコード数
        """
        try:
            # 複数のエンコーディングを試行
            encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp', 'utf-8-sig']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if df is None:
                raise ValueError("CSVファイルのエンコーディングを判別できませんでした")
            
            count = 0
            
            if lottery_type == 'numbers':
                # 列名または列インデックスでアクセス
                for _, row in df.iterrows():
                    try:
                        draw_date = str(row.get('draw_date', row.iloc[1] if len(row) > 1 else None))
                        draw_number = int(row.get('draw_number', row.iloc[0] if len(row) > 0 else None))
                        winning_number = str(row.get('winning_number', row.iloc[2] if len(row) > 2 else None))
                        
                        if draw_date and draw_number and winning_number:
                            if self.db.insert_numbers(draw_date, draw_number, winning_number):
                                count += 1
                    except (ValueError, IndexError, KeyError) as e:
                        continue

            elif lottery_type == 'numbers3':
                for _, row in df.iterrows():
                    try:
                        draw_date = str(row.get('draw_date', row.iloc[1] if len(row) > 1 else None))
                        draw_number = int(row.get('draw_number', row.iloc[0] if len(row) > 0 else None))
                        winning_number = str(row.get('winning_number', row.iloc[2] if len(row) > 2 else None))
                        if draw_date and draw_number and winning_number:
                            if self.db.insert_numbers3(draw_date, draw_number, winning_number):
                                count += 1
                    except (ValueError, IndexError, KeyError):
                        continue
            
            elif lottery_type == 'loto6':
                for _, row in df.iterrows():
                    try:
                        # 列名または列インデックスでアクセス
                        draw_date = str(row.get('draw_date', row.iloc[1] if len(row) > 1 else None))
                        draw_number = int(row.get('draw_number', row.iloc[0] if len(row) > 0 else None))
                        
                        # 当選番号を取得（列名または列インデックス）
                        if 'numbers' in row:
                            if isinstance(row['numbers'], str):
                                try:
                                    numbers = ast.literal_eval(row['numbers'])
                                except (ValueError, SyntaxError):
                                    numbers = json.loads(row['numbers'])
                            else:
                                numbers = row['numbers']
                        else:
                            # 列インデックスで取得（2-7列目が当選番号）
                            numbers = [int(row.iloc[i]) for i in range(2, 8) if i < len(row)]
                        
                        bonus = None
                        if 'bonus_number' in row:
                            bonus_val = row['bonus_number']
                            if pd.notna(bonus_val):
                                bonus = int(bonus_val)
                        elif len(row) > 7:
                            bonus_val = row.iloc[7]
                            if pd.notna(bonus_val):
                                bonus = int(bonus_val)
                        
                        if draw_date and draw_number and len(numbers) == 6:
                            if self.db.insert_loto6(draw_date, draw_number, numbers, bonus):
                                count += 1
                    except (ValueError, IndexError, KeyError) as e:
                        continue
            
            elif lottery_type == 'loto7':
                for _, row in df.iterrows():
                    try:
                        draw_date = str(row.get('draw_date', row.iloc[1] if len(row) > 1 else None))
                        draw_number = int(row.get('draw_number', row.iloc[0] if len(row) > 0 else None))
                        
                        if 'numbers' in row:
                            if isinstance(row['numbers'], str):
                                try:
                                    numbers = ast.literal_eval(row['numbers'])
                                except (ValueError, SyntaxError):
                                    numbers = json.loads(row['numbers'])
                            else:
                                numbers = row['numbers']
                        else:
                            # 列インデックスで取得（2-8列目が当選番号）
                            numbers = [int(row.iloc[i]) for i in range(2, 9) if i < len(row)]
                        
                        bonus = None
                        bonus2 = None
                        if 'bonus_number' in row:
                            bonus_val = row['bonus_number']
                            if pd.notna(bonus_val):
                                bonus = int(bonus_val)
                        elif len(row) > 8:
                            bonus_val = row.iloc[8]
                            if pd.notna(bonus_val):
                                bonus = int(bonus_val)
                        if 'bonus_number2' in row:
                            bonus_val2 = row['bonus_number2']
                            if pd.notna(bonus_val2):
                                bonus2 = int(bonus_val2)
                        elif len(row) > 9:
                            bonus_val2 = row.iloc[9]
                            if pd.notna(bonus_val2):
                                bonus2 = int(bonus_val2)
                        
                        if draw_date and draw_number and len(numbers) == 7:
                            if self.db.insert_loto7(draw_date, draw_number, numbers, bonus, bonus2):
                                count += 1
                    except (ValueError, IndexError, KeyError) as e:
                        continue
            
            elif lottery_type == 'miniloto':
                for _, row in df.iterrows():
                    try:
                        # 列インデックスでアクセス（1列目: 抽選回数, 2列目: 抽選日, 3-7列目: 当選番号, 8列目: ボーナス）
                        draw_date = str(row.iloc[1]) if len(row) > 1 else None
                        draw_number = int(row.iloc[0]) if len(row) > 0 else None
                        
                        # 3-7列目が当選番号（5個）
                        numbers = []
                        for i in range(2, 7):
                            if i < len(row):
                                try:
                                    num = int(row.iloc[i])
                                    numbers.append(num)
                                except (ValueError, TypeError):
                                    continue
                        
                        # 8列目がボーナス番号
                        bonus = None
                        if len(row) > 7:
                            try:
                                bonus_val = row.iloc[7]
                                if pd.notna(bonus_val) and str(bonus_val).strip():
                                    bonus = int(bonus_val)
                            except (ValueError, TypeError):
                                pass
                        
                        if draw_date and draw_number and len(numbers) == 5:
                            if self.db.insert_miniloto(draw_date, draw_number, numbers, bonus):
                                count += 1
                    except (ValueError, IndexError, KeyError, TypeError) as e:
                        continue
            
            return count
        
        except Exception as e:
            print(f"CSVインポートエラー: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def add_manual_numbers(self, draw_date: str, draw_number: int, winning_number: str) -> bool:
        """ナンバーズ4データを手動で追加"""
        return self.db.insert_numbers(draw_date, draw_number, winning_number)
    
    def add_manual_numbers3(self, draw_date: str, draw_number: int, winning_number: str) -> bool:
        """ナンバーズ3データを手動で追加"""
        return self.db.insert_numbers3(draw_date, draw_number, winning_number)
    
    def add_manual_loto6(self, draw_date: str, draw_number: int, numbers: List[int], 
                         bonus_number: Optional[int] = None) -> bool:
        """ロト6データを手動で追加"""
        return self.db.insert_loto6(draw_date, draw_number, numbers, bonus_number)
    
    def add_manual_loto7(self, draw_date: str, draw_number: int, numbers: List[int], 
                         bonus_number: Optional[int] = None, bonus_number2: Optional[int] = None) -> bool:
        """ロト7データを手動で追加"""
        return self.db.insert_loto7(draw_date, draw_number, numbers, bonus_number, bonus_number2)
    
    def add_manual_miniloto(self, draw_date: str, draw_number: int, numbers: List[int], 
                           bonus_number: Optional[int] = None) -> bool:
        """ミニロトデータを手動で追加"""
        return self.db.insert_miniloto(draw_date, draw_number, numbers, bonus_number)
    
    def scrape_from_url(self, url: str, lottery_type: str, 
                       parser_func: Optional[callable] = None) -> int:
        """
        URLからデータをスクレイピングしてデータベースに保存
        
        注意: この機能を使用する前に、対象サイトの利用規約を必ず確認してください。
        サーバーに負荷をかけないよう、適切な間隔を空けてアクセスしてください。
        
        Args:
            url: スクレイピング対象のURL
            lottery_type: 宝くじタイプ ('numbers', 'loto6', 'loto7', 'miniloto')
            parser_func: カスタムパーサー関数（オプション）
        
        Returns:
            保存されたレコード数
        """
        if not BS4_AVAILABLE:
            raise ImportError(
                "Webスクレイピング機能を使用するには、beautifulsoup4パッケージが必要です。\n"
                "以下のコマンドでインストールしてください: pip install beautifulsoup4 lxml"
            )
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # カスタムパーサーが指定されている場合はそれを使用
            if parser_func:
                data_list = parser_func(soup)
            else:
                # デフォルトのパーサー（サイト構造に応じてカスタマイズが必要）
                data_list = self._default_parser(soup, lottery_type)
            
            count = 0
            for data in data_list:
                if lottery_type == 'numbers':
                    if self.db.insert_numbers(data['draw_date'], data['draw_number'], data['winning_number']):
                        count += 1
                elif lottery_type == 'loto6':
                    if self.db.insert_loto6(data['draw_date'], data['draw_number'], 
                                           data['numbers'], data.get('bonus_number')):
                        count += 1
                elif lottery_type == 'loto7':
                    if self.db.insert_loto7(data['draw_date'], data['draw_number'], 
                                           data['numbers'], data.get('bonus_number')):
                        count += 1
                elif lottery_type == 'miniloto':
                    if self.db.insert_miniloto(data['draw_date'], data['draw_number'], 
                                              data['numbers'], data.get('bonus_number')):
                        count += 1
            
            # サーバー負荷軽減のため、リクエスト間に待機
            time.sleep(1)
            
            return count
        
        except Exception as e:
            print(f"スクレイピングエラー: {e}")
            return 0
    
    def _default_parser(self, soup, lottery_type: str) -> List[Dict[str, Any]]:
        """
        デフォルトのパーサー（サイト構造に応じてカスタマイズが必要）
        
        注意: この関数は汎用的なパーサーです。
        実際のサイトのHTML構造に合わせてカスタマイズしてください。
        """
        data_list = []
        
        # テーブルを探す
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # ヘッダー行をスキップ
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                
                try:
                    # 基本的な構造を想定（サイトによって異なる）
                    draw_date = cells[0].get_text(strip=True)
                    draw_number = int(re.search(r'\d+', cells[1].get_text(strip=True)).group())
                    
                    if lottery_type == 'numbers':
                        winning_number = cells[2].get_text(strip=True)
                        if len(winning_number) == 4 and winning_number.isdigit():
                            data_list.append({
                                'draw_date': draw_date,
                                'draw_number': draw_number,
                                'winning_number': winning_number
                            })
                    else:
                        # ロト系の場合
                        numbers_text = cells[2].get_text(strip=True)
                        numbers = [int(x) for x in re.findall(r'\d+', numbers_text)]
                        bonus = None
                        if len(cells) > 3:
                            bonus_text = cells[3].get_text(strip=True)
                            bonus_match = re.search(r'\d+', bonus_text)
                            if bonus_match:
                                bonus = int(bonus_match.group())
                        
                        if numbers:
                            data_list.append({
                                'draw_date': draw_date,
                                'draw_number': draw_number,
                                'numbers': numbers,
                                'bonus_number': bonus
                            })
                
                except (ValueError, AttributeError, IndexError) as e:
                    continue
        
        return data_list
    
    def create_sample_csv(self, lottery_type: str, output_path: str = "sample_data.csv"):
        """
        サンプルCSVファイルを作成
        
        Args:
            lottery_type: 宝くじタイプ ('numbers', 'loto6', 'loto7', 'miniloto')
            output_path: 出力ファイルパス
        """
        if lottery_type == 'numbers':
            sample_data = {
                'draw_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'draw_number': [1, 2, 3],
                'winning_number': ['1234', '5678', '9012']
            }
        elif lottery_type == 'loto6':
            sample_data = {
                'draw_date': ['2024-01-01', '2024-01-08'],
                'draw_number': [1, 2],
                'numbers': ['[1,2,3,4,5,6]', '[10,15,20,25,30,35]'],
                'bonus_number': [7, 40]
            }
        elif lottery_type == 'loto7':
            sample_data = {
                'draw_date': ['2024-01-01', '2024-01-08'],
                'draw_number': [1, 2],
                'numbers': ['[1,2,3,4,5,6,7]', '[10,15,20,25,30,35,37]'],
                'bonus_number': [8, 36],
                'bonus_number2': [9, 37]
            }
        elif lottery_type == 'miniloto':
            sample_data = {
                'draw_date': ['2024-01-01', '2024-01-08'],
                'draw_number': [1, 2],
                'numbers': ['[1,2,3,4,5]', '[10,15,20,25,30]'],
                'bonus_number': [6, 31]
            }
        elif lottery_type == 'numbers3':
            sample_data = {
                'draw_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'draw_number': [1, 2, 3],
                'winning_number': ['123', '456', '789']
            }
        else:
            return
        
        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"サンプルCSVファイルを作成しました: {output_path}")

