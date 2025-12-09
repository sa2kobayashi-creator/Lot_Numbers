"""
データ分析・抽出機能
過去データから最適な値を抽出する
"""
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import Counter
from database import DatabaseManager


class LotteryAnalyzer:
    """宝くじデータ分析クラス"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        分析クラスの初期化
        
        Args:
            db_manager: データベースマネージャーインスタンス
        """
        self.db = db_manager
    
    def analyze_numbers_frequency(self, digits: int = 4,
                                  start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None) -> pd.DataFrame:
        """
        ナンバーズの各桁の出現頻度を分析
        
        Returns:
            各桁（0-9）の出現回数
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # 各桁の出現回数をカウント
        # 1始まりでキーを用意（桁1, 桁2,...）
        digit_counts = {f'桁{i}': Counter() for i in range(1, digits + 1)}
        
        for winning_number in df['winning_number']:
            for i, digit in enumerate(winning_number):
                digit_counts[f'桁{i+1}'][int(digit)] += 1
        
        # DataFrameに変換
        result = pd.DataFrame(digit_counts)
        result = result.fillna(0).astype(int)
        result.index.name = '数字'
        
        return result
    
    def analyze_loto6_frequency(self, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, 
                               include_bonus: bool = False) -> pd.DataFrame:
        """
        ロト6の数字出現頻度を分析
        
        Args:
            start_date: 開始日
            end_date: 終了日
            include_bonus: ボーナス番号を含めるか
        
        Returns:
            各数字（1-43）の出現回数
        """
        df = self.db.get_loto6_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        number_counts = Counter()
        
        for _, row in df.iterrows():
            numbers = json.loads(row['numbers'])
            for num in numbers:
                number_counts[num] += 1
            
            if include_bonus and pd.notna(row['bonus_number']):
                number_counts[row['bonus_number']] += 1
        
        result = pd.DataFrame({
            '数字': list(range(1, 44)),
            '出現回数': [number_counts.get(i, 0) for i in range(1, 44)]
        })
        
        return result.sort_values('出現回数', ascending=False)
    
    def analyze_loto7_frequency(self, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, 
                               include_bonus: bool = False) -> pd.DataFrame:
        """
        ロト7の数字出現頻度を分析
        
        Args:
            start_date: 開始日
            end_date: 終了日
            include_bonus: ボーナス番号を含めるか
        
        Returns:
            各数字（1-37）の出現回数
        """
        df = self.db.get_loto7_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        number_counts = Counter()
        
        for _, row in df.iterrows():
            numbers = json.loads(row['numbers'])
            for num in numbers:
                number_counts[num] += 1
            
            if include_bonus:
                if pd.notna(row['bonus_number']):
                    number_counts[row['bonus_number']] += 1
                # 2つ目のボーナス
                if 'bonus_number2' in row.keys() and pd.notna(row['bonus_number2']):
                    number_counts[row['bonus_number2']] += 1
        
        result = pd.DataFrame({
            '数字': list(range(1, 38)),
            '出現回数': [number_counts.get(i, 0) for i in range(1, 38)]
        })
        
        return result.sort_values('出現回数', ascending=False)
    
    def analyze_miniloto_frequency(self, start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None, 
                                  include_bonus: bool = False) -> pd.DataFrame:
        """
        ミニロトの数字出現頻度を分析
        
        Args:
            start_date: 開始日
            end_date: 終了日
            include_bonus: ボーナス番号を含めるか
        
        Returns:
            各数字（1-31）の出現回数
        """
        df = self.db.get_miniloto_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        number_counts = Counter()
        
        for _, row in df.iterrows():
            numbers = json.loads(row['numbers'])
            for num in numbers:
                number_counts[num] += 1
            
            if include_bonus and pd.notna(row['bonus_number']):
                number_counts[row['bonus_number']] += 1
        
        result = pd.DataFrame({
            '数字': list(range(1, 32)),
            '出現回数': [number_counts.get(i, 0) for i in range(1, 32)]
        })
        
        return result.sort_values('出現回数', ascending=False)
    
    def get_hot_numbers(self, lottery_type: str, top_n: int = 10, 
                       start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> List[int]:
        """
        出現頻度の高い数字を取得
        
        Args:
            lottery_type: 宝くじタイプ ('loto6', 'loto7', 'miniloto')
            top_n: 取得する上位N個
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            出現頻度の高い数字のリスト
        """
        if lottery_type == 'loto6':
            df = self.analyze_loto6_frequency(start_date, end_date)
        elif lottery_type == 'loto7':
            df = self.analyze_loto7_frequency(start_date, end_date)
        elif lottery_type == 'miniloto':
            df = self.analyze_miniloto_frequency(start_date, end_date)
        else:
            return []
        
        if df.empty:
            return []
        
        return df.head(top_n)['数字'].tolist()
    
    def get_cold_numbers(self, lottery_type: str, top_n: int = 10, 
                        start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> List[int]:
        """
        出現頻度の低い数字を取得
        
        Args:
            lottery_type: 宝くじタイプ ('loto6', 'loto7', 'miniloto')
            top_n: 取得する上位N個
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            出現頻度の低い数字のリスト
        """
        if lottery_type == 'loto6':
            df = self.analyze_loto6_frequency(start_date, end_date)
        elif lottery_type == 'loto7':
            df = self.analyze_loto7_frequency(start_date, end_date)
        elif lottery_type == 'miniloto':
            df = self.analyze_miniloto_frequency(start_date, end_date)
        else:
            return []
        
        if df.empty:
            return []
        
        return df.tail(top_n)['数字'].tolist()
    
    def analyze_number_pairs(self, lottery_type: str, 
                            start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, 
                            top_n: int = 20) -> pd.DataFrame:
        """
        数字のペア出現頻度を分析
        
        Args:
            lottery_type: 宝くじタイプ ('loto6', 'loto7', 'miniloto')
            start_date: 開始日
            end_date: 終了日
            top_n: 表示する上位N個
        
        Returns:
            ペア出現頻度のDataFrame
        """
        if lottery_type == 'loto6':
            df = self.db.get_loto6_data(start_date, end_date)
        elif lottery_type == 'loto7':
            df = self.db.get_loto7_data(start_date, end_date)
        elif lottery_type == 'miniloto':
            df = self.db.get_miniloto_data(start_date, end_date)
        else:
            return pd.DataFrame()
        
        if df.empty:
            return pd.DataFrame()
        
        pair_counts = Counter()
        
        for _, row in df.iterrows():
            numbers = sorted(json.loads(row['numbers']))
            # すべてのペアを生成
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    pair = (numbers[i], numbers[j])
                    pair_counts[pair] += 1
        
        # DataFrameに変換
        pairs_data = []
        for pair, count in pair_counts.most_common(top_n):
            pairs_data.append({
                '数字1': pair[0],
                '数字2': pair[1],
                '出現回数': count
            })
        
        return pd.DataFrame(pairs_data)
    
    def get_recommended_numbers(self, lottery_type: str, 
                               strategy: str = 'hot', 
                               count: int = 6,
                               start_date: Optional[str] = None, 
                               end_date: Optional[str] = None) -> List[int]:
        """
        推奨数字を取得
        
        Args:
            lottery_type: 宝くじタイプ ('loto6', 'loto7', 'miniloto')
            strategy: 戦略 ('hot': 出現頻度高い, 'cold': 出現頻度低い, 'mixed': 混合)
            count: 取得する数字の数
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            推奨数字のリスト
        """
        if strategy == 'hot':
            return self.get_hot_numbers(lottery_type, count, start_date, end_date)
        elif strategy == 'cold':
            return self.get_cold_numbers(lottery_type, count, start_date, end_date)
        elif strategy == 'mixed':
            hot_count = count // 2
            cold_count = count - hot_count
            hot = self.get_hot_numbers(lottery_type, hot_count, start_date, end_date)
            cold = self.get_cold_numbers(lottery_type, cold_count, start_date, end_date)
            return hot + cold
        else:
            return []

