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
                       parser_func: Optional[callable] = None) -> Dict[str, Any]:
        """
        URLからデータをスクレイピングしてデータベースに保存
        
        注意: この機能を使用する前に、対象サイトの利用規約を必ず確認してください。
        サーバーに負荷をかけないよう、適切な間隔を空けてアクセスしてください。
        
        Args:
            url: スクレイピング対象のURL
            lottery_type: 宝くじタイプ ('numbers', 'numbers3', 'loto6', 'loto7', 'miniloto')
            parser_func: カスタムパーサー関数（オプション）
        
        Returns:
            辞書: {
                'count': 保存されたレコード数,
                'total_found': 見つかったデータ数,
                'duplicated': 重複でスキップされた数,
                'status': 'success' | 'duplicated' | 'no_data' | 'error',
                'message': メッセージ
            }
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
            
            # loto-life.netの場合は専用パーサーを使用
            if 'loto-life.net' in url:
                data_list = self._parse_loto_life(soup, lottery_type)
            elif parser_func:
                data_list = parser_func(soup)
            else:
                # デフォルトのパーサー（サイト構造に応じてカスタマイズが必要）
                data_list = self._default_parser(soup, lottery_type)
            
            # データが見つからなかった場合
            if not data_list:
                return {
                    'count': 0,
                    'total_found': 0,
                    'duplicated': 0,
                    'status': 'no_data',
                    'message': 'データが見つかりませんでした。URLまたはHTML構造を確認してください。'
                }
            
            count = 0
            duplicated_count = 0
            error_count = 0
            
            for data in data_list:
                try:
                    inserted = False
                    if lottery_type == 'numbers':
                        inserted = self.db.insert_numbers(data['draw_date'], data['draw_number'], data['winning_number'])
                    elif lottery_type == 'numbers3':
                        inserted = self.db.insert_numbers3(data['draw_date'], data['draw_number'], data['winning_number'])
                    elif lottery_type == 'loto6':
                        inserted = self.db.insert_loto6(data['draw_date'], data['draw_number'], 
                                                       data['numbers'], data.get('bonus_number'))
                    elif lottery_type == 'loto7':
                        inserted = self.db.insert_loto7(data['draw_date'], data['draw_number'], 
                                                       data['numbers'], data.get('bonus_number'), data.get('bonus_number2'))
                    elif lottery_type == 'miniloto':
                        inserted = self.db.insert_miniloto(data['draw_date'], data['draw_number'], 
                                                          data['numbers'], data.get('bonus_number'))
                    
                    if inserted:
                        count += 1
                    else:
                        duplicated_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"挿入エラー: {lottery_type} - 抽選回数{data.get('draw_number')}, エラー: {e}")
            
            # サーバー負荷軽減のため、リクエスト間に待機
            time.sleep(1)
            
            # 結果を返す
            total_found = len(data_list)
            
            if count > 0:
                status = 'success'
                message = f'{count}件のデータを取得しました'
                if duplicated_count > 0:
                    message += f'（{duplicated_count}件は重複のためスキップ）'
            elif duplicated_count > 0:
                status = 'duplicated'
                message = f'{duplicated_count}件のデータが見つかりましたが、すべて既にデータベースに存在するため追加されませんでした（重複しています）'
            elif error_count > 0:
                status = 'error'
                message = f'データの挿入中にエラーが発生しました（{error_count}件）'
            else:
                status = 'no_data'
                message = 'データが見つかりませんでした'
            
            return {
                'count': count,
                'total_found': total_found,
                'duplicated': duplicated_count,
                'status': status,
                'message': message
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'count': 0,
                'total_found': 0,
                'duplicated': 0,
                'status': 'error',
                'message': f'ネットワークエラー: サイトにアクセスできませんでした（{str(e)}）'
            }
        except Exception as e:
            error_msg = f"スクレイピングエラー: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return {
                'count': 0,
                'total_found': 0,
                'duplicated': 0,
                'status': 'error',
                'message': f'エラーが発生しました: {str(e)}'
            }
    
    def _parse_loto_life(self, soup, lottery_type: str) -> List[Dict[str, Any]]:
        """
        loto-life.net専用パーサー
        
        Args:
            soup: BeautifulSoupオブジェクト
            lottery_type: 宝くじタイプ
        
        Returns:
            データのリスト
        """
        data_list = []
        
        # テーブルを探す（class='table'を持つテーブルを優先的に探す）
        tables = soup.find_all('table', class_='table')
        if not tables:
            # class='table'がない場合は、すべてのテーブルを探す
            tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            # theadとtbodyの両方から行を取得
            thead_rows = table.find_all('thead')
            tbody_rows = table.find_all('tbody')
            
            # ヘッダー行を探す（thead内のth）
            header_text = ""
            if thead_rows:
                header_th = thead_rows[0].find('th')
                if header_th:
                    header_text = header_th.get_text(strip=True)
            
            # ヘッダーが見つからない場合は、最初のtrから探す
            if not header_text:
                all_rows = table.find_all('tr')
                if all_rows:
                    header_cells = all_rows[0].find_all(['td', 'th'])
                    if header_cells:
                        header_text = header_cells[0].get_text(strip=True)
            
            if not header_text:
                continue
            
            try:
                # 抽選回数を抽出（例: "第1363回"）
                draw_number_match = re.search(r'第(\d+)回', header_text)
                if not draw_number_match:
                    continue
                draw_number = int(draw_number_match.group(1))
                
                # 抽選日を抽出（例: "2025年12月02日"）
                date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', header_text)
                if not date_match:
                    continue
                year, month, day = date_match.groups()
                draw_date = f"{year}-{int(month):02d}-{int(day):02d}"
                
                # 当選番号を探す（tbody内の「当選番号」というthの後のtd）
                number_text = ""
                if tbody_rows:
                    tbody = tbody_rows[0]
                    # 「当選番号」というテキストを含むthを探す
                    winning_number_th = tbody.find('th', string=re.compile('当選番号'))
                    if winning_number_th:
                        # 同じ行のtdを探す
                        parent_tr = winning_number_th.find_parent('tr')
                        if parent_tr:
                            td = parent_tr.find('td')
                            if td:
                                number_text = td.get_text(separator=' ', strip=True)
                
                # 見つからない場合は、従来の方法で探す
                if not number_text:
                    all_rows = table.find_all('tr')
                    for row in all_rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            # 「当選番号」を含むセルを探す
                            for i, cell in enumerate(cells):
                                if '当選番号' in cell.get_text():
                                    if i + 1 < len(cells):
                                        number_text = cells[i + 1].get_text(separator=' ', strip=True)
                                        break
                            if number_text:
                                break
                
                if not number_text:
                    continue
                
                if lottery_type in ['numbers', 'numbers3']:
                    # ナンバーズの場合（例: "3493"）
                    winning_number = number_text.replace(' ', '').replace('-', '')
                    expected_length = 3 if lottery_type == 'numbers3' else 4
                    if len(winning_number) == expected_length and winning_number.isdigit():
                        data_list.append({
                            'draw_date': draw_date,
                            'draw_number': draw_number,
                            'winning_number': winning_number
                        })
                
                elif lottery_type in ['loto6', 'loto7', 'miniloto']:
                    # ロト系の場合（例: "本数字　：6　12　16　19　31ボーナス：25"）
                    # HTMLでは<br/>で改行されているが、get_text()で1行になる
                    numbers = []
                    expected_count = 6 if lottery_type == 'loto6' else (7 if lottery_type == 'loto7' else 5)
                    max_num = 43 if lottery_type == 'loto6' else (37 if lottery_type == 'loto7' else 31)
                    
                    # "本数字"の後の数字を抽出（"ボーナス"の前まで）
                    # 文字列分割方式で確実に抽出
                    if 'ボーナス' in number_text:
                        parts = number_text.split('ボーナス')
                        if len(parts) > 0 and '本数字' in parts[0]:
                            main_part = parts[0]
                            # "本数字："の後の部分を取得
                            if '：' in main_part:
                                main_text = main_part.split('：')[1].strip()
                            elif ':' in main_part:
                                main_text = main_part.split(':')[1].strip()
                            else:
                                # "本数字"の後の部分を取得
                                main_text = main_part.split('本数字')[1].strip()
                                # 先頭の「：」や「:」を除去
                                main_text = re.sub(r'^[：:\s　]+', '', main_text)
                            
                            # 数字を抽出（スペースや全角スペースで区切られている）
                            # まず、連続する数字を抽出
                            main_nums = re.findall(r'\d+', main_text)
                            for num_str in main_nums:
                                num = int(num_str)
                                if 1 <= num <= max_num and num not in numbers:
                                    numbers.append(num)
                                    if len(numbers) >= expected_count:
                                        break
                    else:
                        # ボーナスがない場合（通常はないが念のため）
                        if '本数字' in number_text:
                            if '：' in number_text:
                                main_text = number_text.split('：')[1].strip()
                            elif ':' in number_text:
                                main_text = number_text.split(':')[1].strip()
                            else:
                                main_text = number_text.split('本数字')[1].strip()
                                main_text = re.sub(r'^[：:\s　]+', '', main_text)
                            
                            main_nums = re.findall(r'\d+', main_text)
                            for num_str in main_nums:
                                num = int(num_str)
                                if 1 <= num <= max_num and num not in numbers:
                                    numbers.append(num)
                                    if len(numbers) >= expected_count:
                                        break
                    
                    # ボーナス番号を抽出
                    bonus = None
                    bonus2 = None
                    
                    bonus_match = re.search(r'ボーナス[：:]\s*(.+)', number_text)
                    if bonus_match:
                        bonus_text = bonus_match.group(1).strip()
                        bonus_nums = re.findall(r'\d+', bonus_text)
                        
                        if lottery_type == 'loto7':
                            # ロト7はボーナス2つ
                            if len(bonus_nums) >= 1:
                                bonus = int(bonus_nums[0])
                            if len(bonus_nums) >= 2:
                                bonus2 = int(bonus_nums[1])
                        else:
                            # ロト6、ミニロトはボーナス1つ
                            if len(bonus_nums) >= 1:
                                bonus = int(bonus_nums[0])
                    
                    # デバッグ情報（必要に応じて）
                    if len(numbers) != expected_count:
                        print(f"警告: {lottery_type} 抽選回数{draw_number} - 期待される数字数: {expected_count}, 実際: {len(numbers)}, 数字: {numbers}, テキスト: '{number_text}'")
                    
                    if len(numbers) == expected_count:
                        data_dict = {
                            'draw_date': draw_date,
                            'draw_number': draw_number,
                            'numbers': sorted(numbers)
                        }
                        if bonus is not None:
                            data_dict['bonus_number'] = bonus
                        if bonus2 is not None:
                            data_dict['bonus_number2'] = bonus2
                        data_list.append(data_dict)
            
            except (ValueError, AttributeError, IndexError, TypeError) as e:
                # エラーは静かにスキップ（デバッグ時のみ表示）
                continue
        
        return data_list
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        日付文字列をYYYY-MM-DD形式に正規化
        
        Args:
            date_str: 日付文字列
        
        Returns:
            正規化された日付文字列（YYYY-MM-DD）またはNone
        """
        if not date_str:
            return None
        
        # 様々な日付形式に対応
        date_patterns = [
            r'(\d{4})[年/](\d{1,2})[月/](\d{1,2})',  # YYYY年MM月DD日、YYYY/MM/DD
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                year, month, day = match.groups()
                return f"{year}-{int(month):02d}-{int(day):02d}"
        
        return None
    
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

