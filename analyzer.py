"""
データ分析・抽出機能
過去データから最適な値を抽出する
"""
import json
import itertools
import random
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter
from datetime import datetime
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
    
    def get_recommended_numbers_multiple(self, lottery_type: str,
                                         strategy: str = 'hot',
                                         count: int = 6,
                                         top_n: int = 5,
                                         start_date: Optional[str] = None,
                                         end_date: Optional[str] = None) -> List[List[int]]:
        """
        推奨数字を複数パターン取得（ランキング形式）
        
        Args:
            lottery_type: 宝くじタイプ ('loto6', 'loto7', 'miniloto')
            strategy: 戦略 ('hot': 出現頻度高い, 'cold': 出現頻度低い, 'mixed': 混合)
            count: 1パターンあたりの数字の数
            top_n: 返す推奨数字パターンの数（デフォルト5）
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            推奨数字のリストのリスト（最大top_n個）
        """
        # 出現頻度データを取得
        if lottery_type == 'loto6':
            freq_df = self.analyze_loto6_frequency(start_date, end_date)
            max_num = 43
        elif lottery_type == 'loto7':
            freq_df = self.analyze_loto7_frequency(start_date, end_date)
            max_num = 37
        elif lottery_type == 'miniloto':
            freq_df = self.analyze_miniloto_frequency(start_date, end_date)
            max_num = 31
        else:
            return []
        
        if freq_df.empty:
            return []
        
        # 数字とその出現頻度を取得
        number_freq = {}
        for _, row in freq_df.iterrows():
            number_freq[row['数字']] = row['出現回数']
        
        # すべての数字に出現頻度を設定（出現回数0の数字も含む）
        for num in range(1, max_num + 1):
            if num not in number_freq:
                number_freq[num] = 0
        
        recommended_patterns = []
        
        if strategy == 'hot':
            # 出現頻度が高い数字から複数のパターンを生成
            sorted_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)
            
            # 上位数字から異なる組み合わせを生成
            top_numbers = [num for num, _ in sorted_numbers[:count * 2]]  # 候補を多めに取得
            
            # 組み合わせを生成してスコア付け
            scored_patterns = []
            
            for _ in range(1000):  # 十分な組み合わせを生成
                if strategy == 'hot':
                    # 出現頻度が高い数字を優先的に選ぶ
                    pattern = random.sample(top_numbers, min(count, len(top_numbers)))
                    score = sum(number_freq.get(num, 0) for num in pattern)
                elif strategy == 'cold':
                    # 出現頻度が低い数字を優先的に選ぶ
                    bottom_numbers = [num for num, _ in sorted_numbers[-count * 2:]]
                    pattern = random.sample(bottom_numbers, min(count, len(bottom_numbers)))
                    score = -sum(number_freq.get(num, 0) for num in pattern)  # 低い方が良いので負のスコア
                else:  # mixed
                    hot_count = count // 2
                    cold_count = count - hot_count
                    hot_nums = [num for num, _ in sorted_numbers[:count * 2]]
                    cold_nums = [num for num, _ in sorted_numbers[-count * 2:]]
                    pattern = random.sample(hot_nums, min(hot_count, len(hot_nums))) + \
                              random.sample(cold_nums, min(cold_count, len(cold_nums)))
                    score = sum(number_freq.get(num, 0) for num in pattern[:hot_count]) - \
                            sum(number_freq.get(num, 0) for num in pattern[hot_count:])
                
                pattern = sorted(pattern)
                if pattern not in scored_patterns:
                    scored_patterns.append((pattern, score))
            
            # スコアでソート
            scored_patterns.sort(key=lambda x: x[1], reverse=True)
            
            # 上位top_n個を取得
            for pattern, _ in scored_patterns[:top_n]:
                recommended_patterns.append(pattern)
        
        elif strategy == 'cold':
            # 出現頻度が低い数字から複数のパターンを生成
            sorted_numbers = sorted(number_freq.items(), key=lambda x: x[1])
            
            bottom_numbers = [num for num, _ in sorted_numbers[:count * 2]]
            
            scored_patterns = []
            
            for _ in range(1000):
                pattern = random.sample(bottom_numbers, min(count, len(bottom_numbers)))
                score = sum(number_freq.get(num, 0) for num in pattern)  # 低い方が良い
                pattern = sorted(pattern)
                if pattern not in scored_patterns:
                    scored_patterns.append((pattern, score))
            
            scored_patterns.sort(key=lambda x: x[1])  # 昇順
            
            for pattern, _ in scored_patterns[:top_n]:
                recommended_patterns.append(pattern)
        
        else:  # mixed
            sorted_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)
            hot_count = count // 2
            cold_count = count - hot_count
            hot_nums = [num for num, _ in sorted_numbers[:count * 2]]
            cold_nums = [num for num, _ in sorted_numbers[-count * 2:]]
            
            scored_patterns = []
            
            for _ in range(1000):
                pattern = random.sample(hot_nums, min(hot_count, len(hot_nums))) + \
                          random.sample(cold_nums, min(cold_count, len(cold_nums)))
                score = sum(number_freq.get(num, 0) for num in pattern[:hot_count]) - \
                        sum(number_freq.get(num, 0) for num in pattern[hot_count:])
                pattern = sorted(pattern)
                if pattern not in scored_patterns:
                    scored_patterns.append((pattern, score))
            
            scored_patterns.sort(key=lambda x: x[1], reverse=True)
            
            for pattern, _ in scored_patterns[:top_n]:
                recommended_patterns.append(pattern)
        
        return recommended_patterns
    
    def get_recommended_numbers_numbers(self, digits: int, strategy: str, 
                                        start_date: Optional[str] = None, 
                                        end_date: Optional[str] = None,
                                        top_n: int = 5) -> List[str]:
        """
        ナンバーズの推奨数字を取得（複数候補）
        
        Args:
            digits: 桁数 (3 or 4)
            strategy: 戦略 ('hot': 出現頻度高い, 'cold': 出現頻度低い, 'mixed': 混合)
            start_date: 開始日
            end_date: 終了日
            top_n: 返す推奨数字の数（デフォルト5）
        
        Returns:
            推奨数字のリスト（最大top_n個）
        """
        freq_df = self.analyze_numbers_frequency(digits, start_date, end_date)
        
        if freq_df.empty:
            return []
        
        recommended_list = []
        
        if strategy == 'hot':
            # 各桁の出現頻度が高い数字の組み合わせを生成
            # 各桁の上位数字を取得
            digit_options = {}
            for col in freq_df.columns:
                # 各桁の上位5個の数字を取得
                top_digits = freq_df[col].nlargest(5).index.tolist()
                digit_options[col] = top_digits
            
            # 組み合わせを生成（各桁の上位数字の組み合わせ）
            combinations = list(itertools.product(*digit_options.values()))
            
            # 各組み合わせのスコアを計算（出現頻度の合計）
            scored_combinations = []
            for combo in combinations:
                score = 0
                for i, digit in enumerate(combo):
                    col = list(freq_df.columns)[i]
                    score += freq_df.loc[digit, col]
                scored_combinations.append((combo, score))
            
            # スコアでソート（降順）
            scored_combinations.sort(key=lambda x: x[1], reverse=True)
            
            # 上位top_n個を取得
            for combo, _ in scored_combinations[:top_n]:
                recommended_list.append(''.join(map(str, combo)))
        
        elif strategy == 'cold':
            # 各桁の出現頻度が低い数字の組み合わせを生成
            digit_options = {}
            for col in freq_df.columns:
                # 各桁の下位5個の数字を取得
                bottom_digits = freq_df[col].nsmallest(5).index.tolist()
                digit_options[col] = bottom_digits
            
            combinations = list(itertools.product(*digit_options.values()))
            
            # 各組み合わせのスコアを計算（出現頻度の合計、低い方が良い）
            scored_combinations = []
            for combo in combinations:
                score = 0
                for i, digit in enumerate(combo):
                    col = list(freq_df.columns)[i]
                    score += freq_df.loc[digit, col]
                scored_combinations.append((combo, score))
            
            # スコアでソート（昇順）
            scored_combinations.sort(key=lambda x: x[1])
            
            # 上位top_n個を取得
            for combo, _ in scored_combinations[:top_n]:
                recommended_list.append(''.join(map(str, combo)))
        
        elif strategy == 'mixed':
            # 前半の桁はhot、後半の桁はcold
            mid = digits // 2
            digit_options = {}
            for i, col in enumerate(freq_df.columns):
                if i < mid:
                    # 前半は上位数字
                    digit_options[col] = freq_df[col].nlargest(5).index.tolist()
                else:
                    # 後半は下位数字
                    digit_options[col] = freq_df[col].nsmallest(5).index.tolist()
            
            combinations = list(itertools.product(*digit_options.values()))
            
            # 各組み合わせのスコアを計算
            scored_combinations = []
            for combo in combinations:
                score = 0
                for i, digit in enumerate(combo):
                    col = list(freq_df.columns)[i]
                    if i < mid:
                        # 前半は高い方が良い
                        score += freq_df.loc[digit, col]
                    else:
                        # 後半は低い方が良い（負のスコアとして扱う）
                        score -= freq_df.loc[digit, col]
                scored_combinations.append((combo, score))
            
            # スコアでソート（降順）
            scored_combinations.sort(key=lambda x: x[1], reverse=True)
            
            # 上位top_n個を取得
            for combo, _ in scored_combinations[:top_n]:
                recommended_list.append(''.join(map(str, combo)))
        
        return recommended_list
    
    def analyze_numbers_pairs(self, digits: int, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, top_n: int = 20) -> pd.DataFrame:
        """
        ナンバーズのペア分析
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
            top_n: 表示する上位N個
        
        Returns:
            ペア出現頻度のDataFrame
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        pair_counts = Counter()
        
        for winning_number in df['winning_number']:
            # 連続する桁のペアを抽出
            for i in range(len(winning_number) - 1):
                pair = winning_number[i:i+2]
                pair_counts[pair] += 1
        
        # DataFrameに変換
        pairs_data = []
        for pair, count in pair_counts.most_common(top_n):
            pairs_data.append({
                'ペア': pair,
                '出現回数': count
            })
        
        return pd.DataFrame(pairs_data)
    
    def get_numbers_detailed_analysis(self, digits: int, start_date: Optional[str] = None, 
                                     end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        ナンバーズの詳細分析
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            詳細分析結果の辞書
        """
        freq_df = self.analyze_numbers_frequency(digits, start_date, end_date)
        
        if freq_df.empty:
            return {}
        
        # 各桁のホット/コールドナンバー
        hot_digits = {}
        cold_digits = {}
        
        for col in freq_df.columns:
            hot_digits[col] = freq_df[col].nlargest(5).index.tolist()
            cold_digits[col] = freq_df[col].nsmallest(5).index.tolist()
        
        return {
            'hot_digits': hot_digits,
            'cold_digits': cold_digits
        }
    
    def analyze_date_relationship_numbers(self, digits: int, start_date: Optional[str] = None, 
                                         end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        ナンバーズの日付との関係性を分析
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            日付関連の分析結果（曜日別、月別、日付別など）
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return {}
        
        # draw_dateを日付型に変換
        df['draw_date'] = pd.to_datetime(df['draw_date'], errors='coerce')
        df = df.dropna(subset=['draw_date'])
        
        if df.empty:
            return {}
        
        results = {}
        
        # 1. 曜日別の出現頻度
        df['weekday'] = df['draw_date'].dt.day_name()
        weekday_counts = df['weekday'].value_counts().sort_index()
        results['weekday'] = pd.DataFrame({
            '曜日': weekday_counts.index,
            '抽選回数': weekday_counts.values
        })
        
        # 2. 月別の出現頻度
        df['month'] = df['draw_date'].dt.month
        month_counts = df['month'].value_counts().sort_index()
        results['month'] = pd.DataFrame({
            '月': month_counts.index,
            '抽選回数': month_counts.values
        })
        
        # 3. 日付（1-31日）別の出現頻度
        df['day'] = df['draw_date'].dt.day
        day_counts = df['day'].value_counts().sort_index()
        results['day'] = pd.DataFrame({
            '日': day_counts.index,
            '抽選回数': day_counts.values
        })
        
        # 4. 各桁の数字と日付の相関
        # 抽選日の日付（1-31）と各桁の数字の相関
        digit_date_correlation = {}
        for i in range(1, digits + 1):
            digit_col = f'digit_{i}'
            # 有効な数字のみを抽出（NaNを除外）
            df[digit_col] = pd.to_numeric(df['winning_number'].str[i-1], errors='coerce')
            # NaNを含む行を除外して相関を計算
            valid_df = df[['day', digit_col]].dropna()
            if len(valid_df) > 1:
                correlation = valid_df.corr().iloc[0, 1]
                digit_date_correlation[f'桁{i}'] = correlation if not pd.isna(correlation) else 0.0
            else:
                digit_date_correlation[f'桁{i}'] = 0.0
        
        results['digit_date_correlation'] = pd.DataFrame({
            '桁': list(digit_date_correlation.keys()),
            '日付との相関係数': list(digit_date_correlation.values())
        })
        
        # 5. 月末・月初の出現傾向
        df['is_month_start'] = df['day'] <= 3
        df['is_month_end'] = df['day'] >= 28
        results['month_period'] = pd.DataFrame({
            '期間': ['月初（1-3日）', '月末（28-31日）', 'その他'],
            '抽選回数': [
                df['is_month_start'].sum(),
                df['is_month_end'].sum(),
                (~(df['is_month_start'] | df['is_month_end'])).sum()
            ]
        })
        
        return results
    
    def analyze_numbers_sum(self, digits: int, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """
        ナンバーズの合計値分析
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            合計値の出現頻度
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        sums = []
        for winning_number in df['winning_number']:
            total = sum(int(d) for d in winning_number)
            sums.append(total)
        
        sum_counts = Counter(sums)
        result = pd.DataFrame({
            '合計値': sorted(sum_counts.keys()),
            '出現回数': [sum_counts[s] for s in sorted(sum_counts.keys())]
        })
        
        return result
    
    def analyze_numbers_odd_even_ratio(self, digits: int, start_date: Optional[str] = None, 
                                      end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        ナンバーズの奇偶比率分析
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            奇偶比率の統計
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return {}
        
        odd_even_patterns = Counter()
        odd_counts = []
        even_counts = []
        
        for winning_number in df['winning_number']:
            odd_count = sum(1 for d in winning_number if int(d) % 2 == 1)
            even_count = digits - odd_count
            odd_counts.append(odd_count)
            even_counts.append(even_count)
            pattern = f"奇数{odd_count}個/偶数{even_count}個"
            odd_even_patterns[pattern] += 1
        
        return {
            '平均奇数個数': np.mean(odd_counts),
            '平均偶数個数': np.mean(even_counts),
            'パターン分布': pd.DataFrame({
                'パターン': list(odd_even_patterns.keys()),
                '出現回数': list(odd_even_patterns.values())
            }).sort_values('出現回数', ascending=False)
        }
    
    def analyze_numbers_high_low_ratio(self, digits: int, start_date: Optional[str] = None, 
                                       end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        ナンバーズの大小比率分析（高:5～9 / 低:0～4）
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            大小比率の統計
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return {}
        
        high_low_patterns = Counter()
        high_counts = []
        low_counts = []
        
        for winning_number in df['winning_number']:
            high_count = sum(1 for d in winning_number if int(d) >= 5)
            low_count = digits - high_count
            high_counts.append(high_count)
            low_counts.append(low_count)
            pattern = f"高{high_count}個/低{low_count}個"
            high_low_patterns[pattern] += 1
        
        return {
            '平均高数字個数': np.mean(high_counts),
            '平均低数字個数': np.mean(low_counts),
            'パターン分布': pd.DataFrame({
                'パターン': list(high_low_patterns.keys()),
                '出現回数': list(high_low_patterns.values())
            }).sort_values('出現回数', ascending=False)
        }
    
    def analyze_numbers_consecutive(self, digits: int, start_date: Optional[str] = None, 
                                   end_date: Optional[str] = None) -> pd.DataFrame:
        """
        ナンバーズの連番出現率分析
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            連番の出現頻度
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        consecutive_counts = Counter()
        total_with_consecutive = 0
        
        for winning_number in df['winning_number']:
            digits_list = [int(d) for d in winning_number]
            has_consecutive = False
            
            # 連番を検出（例: 12, 23, 34など）
            for i in range(len(digits_list) - 1):
                if digits_list[i+1] == digits_list[i] + 1:
                    consecutive_pair = f"{digits_list[i]}{digits_list[i+1]}"
                    consecutive_counts[consecutive_pair] += 1
                    has_consecutive = True
            
            if has_consecutive:
                total_with_consecutive += 1
        
        result = pd.DataFrame({
            '連番': list(consecutive_counts.keys()),
            '出現回数': list(consecutive_counts.values())
        }).sort_values('出現回数', ascending=False)
        
        return result
    
    def analyze_numbers_duplicates(self, digits: int, start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        ナンバーズの同一数字複数出現分析（ダブル/トリプル）
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            ダブル/トリプルの出現統計
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return {}
        
        double_count = 0
        triple_count = 0
        quadruple_count = 0
        no_duplicate_count = 0
        
        for winning_number in df['winning_number']:
            digit_counts = Counter(winning_number)
            max_count = max(digit_counts.values())
            
            if max_count >= 4:
                quadruple_count += 1
            elif max_count >= 3:
                triple_count += 1
            elif max_count >= 2:
                double_count += 1
            else:
                no_duplicate_count += 1
        
        total = len(df)
        
        return {
            'ダブル（2回出現）': {'回数': double_count, '割合': double_count / total * 100},
            'トリプル（3回出現）': {'回数': triple_count, '割合': triple_count / total * 100},
            'クアッド（4回出現）': {'回数': quadruple_count, '割合': quadruple_count / total * 100},
            '重複なし': {'回数': no_duplicate_count, '割合': no_duplicate_count / total * 100}
        }
    
    def analyze_numbers_previous_difference(self, digits: int, start_date: Optional[str] = None, 
                                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        前回数字との差分析
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            前回との差の出現頻度
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # 日付でソート
        df = df.sort_values('draw_date')
        df = df.reset_index(drop=True)
        
        difference_counts = Counter()
        
        for i in range(1, len(df)):
            prev_number = str(df.iloc[i-1]['winning_number'])
            curr_number = str(df.iloc[i]['winning_number'])
            
            # 文字列の長さをチェック
            if len(prev_number) < digits or len(curr_number) < digits:
                continue
            
            # 各桁の差を計算
            for j in range(digits):
                try:
                    prev_digit = int(prev_number[j])
                    curr_digit = int(curr_number[j])
                    diff = (curr_digit - prev_digit) % 10  # 0-9の範囲に正規化
                    difference_counts[diff] += 1
                except (ValueError, IndexError):
                    continue
        
        result = pd.DataFrame({
            '差': sorted(difference_counts.keys()),
            '出現回数': [difference_counts[d] for d in sorted(difference_counts.keys())]
        })
        
        return result
    
    def analyze_numbers_repeat_rate(self, digits: int, start_date: Optional[str] = None, 
                                    end_date: Optional[str] = None) -> Dict[str, float]:
        """
        リピート率分析（前回、前々回からの引っ張り数字）
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            リピート率の統計
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty or len(df) < 2:
            return {}
        
        # 日付でソート
        df = df.sort_values('draw_date')
        df = df.reset_index(drop=True)
        
        prev_repeat_count = 0
        prev_prev_repeat_count = 0
        total_comparisons = 0
        
        for i in range(1, len(df)):
            prev_number = set(df.iloc[i-1]['winning_number'])
            curr_number = set(df.iloc[i]['winning_number'])
            
            # 前回からのリピート
            repeat_digits = prev_number & curr_number
            prev_repeat_count += len(repeat_digits)
            
            # 前々回からのリピート
            if i >= 2:
                prev_prev_number = set(df.iloc[i-2]['winning_number'])
                prev_prev_repeat = prev_prev_number & curr_number
                prev_prev_repeat_count += len(prev_prev_repeat)
            
            total_comparisons += digits
        
        return {
            '前回からの平均リピート数': prev_repeat_count / (len(df) - 1),
            '前々回からの平均リピート数': prev_prev_repeat_count / max(1, len(df) - 2),
            '前回からのリピート率': (prev_repeat_count / total_comparisons * 100) if total_comparisons > 0 else 0
        }
    
    def analyze_numbers_mirror(self, digits: int, start_date: Optional[str] = None, 
                              end_date: Optional[str] = None) -> pd.DataFrame:
        """
        ミラー数字分析（0↔9, 1↔8, 2↔7, 3↔6, 4↔5）
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            ミラー数字の相関
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        mirror_pairs = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0}
        mirror_correlations = []
        
        for i in range(digits):
            digit_col = f'桁{i+1}'
            # 文字列の長さをチェックしてから抽出
            df_temp = df.copy()
            df_temp[digit_col] = df_temp['winning_number'].astype(str).apply(
                lambda x: int(x[i]) if len(x) > i and x[i].isdigit() else None
            )
            df_temp = df_temp.dropna(subset=[digit_col])
            
            if df_temp.empty:
                continue
            
            # ミラーペアの相関を計算
            for digit, mirror in mirror_pairs.items():
                if digit >= mirror:  # 重複を避ける
                    continue
                
                digit_series = (df_temp[digit_col] == digit).astype(int)
                mirror_series = (df_temp[digit_col] == mirror).astype(int)
                
                if digit_series.sum() > 0 and mirror_series.sum() > 0:
                    correlation = digit_series.corr(mirror_series)
                    if not pd.isna(correlation):
                        mirror_correlations.append({
                            '桁': i+1,
                            '数字ペア': f"{digit}↔{mirror}",
                            '相関係数': correlation
                        })
        
        if mirror_correlations:
            return pd.DataFrame(mirror_correlations)
        else:
            return pd.DataFrame()
    
    def analyze_numbers_digital_root(self, digits: int, start_date: Optional[str] = None, 
                                    end_date: Optional[str] = None) -> pd.DataFrame:
        """
        デジタルルート分析（合計値を1桁化）
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            デジタルルートの出現頻度
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        def digital_root(n):
            while n >= 10:
                n = sum(int(d) for d in str(n))
            return n
        
        roots = []
        for winning_number in df['winning_number']:
            total = sum(int(d) for d in winning_number)
            root = digital_root(total)
            roots.append(root)
        
        root_counts = Counter(roots)
        result = pd.DataFrame({
            'デジタルルート': sorted(root_counts.keys()),
            '出現回数': [root_counts[r] for r in sorted(root_counts.keys())]
        })
        
        return result
    
    def analyze_numbers_trend(self, digits: int, periods: int = 10, 
                             start_date: Optional[str] = None, 
                             end_date: Optional[str] = None) -> pd.DataFrame:
        """
        過去n回のトレンド分析
        
        Args:
            digits: 桁数 (3 or 4)
            periods: 分析する期間数
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            トレンド分析結果
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # 日付でソート
        df = df.sort_values('draw_date')
        df = df.reset_index(drop=True)
        
        if len(df) < periods:
            return pd.DataFrame()
        
        # 各桁の最近n回の平均
        recent_df = df.tail(periods)
        trends = []
        
        for i in range(1, digits + 1):
            digit_col = f'桁{i}'
            recent_df[digit_col] = pd.to_numeric(recent_df['winning_number'].astype(str).str[i-1], errors='coerce')
            recent_df = recent_df.dropna(subset=[digit_col])
            if recent_df.empty:
                continue
            avg = recent_df[digit_col].mean()
            trends.append({
                '桁': i,
                f'過去{periods}回平均': avg,
                '標準偏差': recent_df[digit_col].std()
            })
        
        return pd.DataFrame(trends)
    
    def analyze_numbers_ema(self, digits: int, span: int = 10, 
                            start_date: Optional[str] = None, 
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        EMA（指数移動平均）分析
        
        Args:
            digits: 桁数 (3 or 4)
            span: EMAの期間
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            EMA分析結果
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # 日付でソート
        df = df.sort_values('draw_date')
        df = df.reset_index(drop=True)
        
        ema_results = []
        
        for i in range(1, digits + 1):
            digit_col = f'桁{i}'
            df[digit_col] = pd.to_numeric(df['winning_number'].astype(str).str[i-1], errors='coerce')
            df = df.dropna(subset=[digit_col])
            if df.empty:
                continue
            
            # EMA計算
            ema = df[digit_col].ewm(span=span, adjust=False).mean()
            latest_ema = ema.iloc[-1]
            deviation = df[digit_col].iloc[-1] - latest_ema
            
            ema_results.append({
                '桁': i,
                f'EMA({span})': latest_ema,
                '最新値': df[digit_col].iloc[-1],
                '偏差': deviation
            })
        
        return pd.DataFrame(ema_results)
    
    def analyze_numbers_runlength(self, digits: int, start_date: Optional[str] = None, 
                                 end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        ランレングス分析（連続で出る数字の長さ）
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            ランレングス統計
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return {}
        
        # 日付でソート
        df = df.sort_values('draw_date')
        df = df.reset_index(drop=True)
        
        runlengths = {i: [] for i in range(1, digits + 1)}
        
        for i in range(1, digits + 1):
            digit_col = f'桁{i}'
            df[digit_col] = pd.to_numeric(df['winning_number'].astype(str).str[i-1], errors='coerce')
            df = df.dropna(subset=[digit_col])
            if df.empty:
                continue
            
            current_digit = None
            current_length = 0
            
            for digit in df[digit_col]:
                if digit == current_digit:
                    current_length += 1
                else:
                    if current_length > 0:
                        runlengths[i].append(current_length)
                    current_digit = digit
                    current_length = 1
            
            if current_length > 0:
                runlengths[i].append(current_length)
        
        result = {}
        for i in range(1, digits + 1):
            if runlengths[i]:
                result[f'桁{i}'] = {
                    '平均ランレングス': np.mean(runlengths[i]),
                    '最大ランレングス': max(runlengths[i]),
                    'ランレングス分布': Counter(runlengths[i])
                }
        
        return result
    
    def analyze_numbers_markov(self, digits: int, start_date: Optional[str] = None, 
                              end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        マルコフ連鎖による遷移確率分析
        
        Args:
            digits: 桁数 (3 or 4)
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            各桁の遷移確率行列
        """
        if digits == 3:
            df = self.db.get_numbers3_data(start_date, end_date)
        else:
            df = self.db.get_numbers_data(start_date, end_date)
        
        if df.empty:
            return {}
        
        # 日付でソート
        df = df.sort_values('draw_date')
        df = df.reset_index(drop=True)
        
        markov_matrices = {}
        
        for i in range(1, digits + 1):
            digit_col = f'桁{i}'
            df[digit_col] = pd.to_numeric(df['winning_number'].astype(str).str[i-1], errors='coerce')
            df = df.dropna(subset=[digit_col])
            if df.empty:
                continue
            
            # 遷移カウント
            transition_counts = {}
            for j in range(len(df) - 1):
                from_state = df[digit_col].iloc[j]
                to_state = df[digit_col].iloc[j+1]
                
                if from_state not in transition_counts:
                    transition_counts[from_state] = Counter()
                transition_counts[from_state][to_state] += 1
            
            # 遷移確率行列を作成（0-9のすべての数字を含む）
            states = list(range(10))  # 0-9のすべての数字
            transition_matrix = []
            
            for from_state in states:
                row = []
                total = sum(transition_counts.get(from_state, Counter()).values())
                for to_state in states:
                    count = transition_counts.get(from_state, Counter()).get(to_state, 0)
                    prob = count / total if total > 0 else 1.0 / len(states)  # データがない場合は均等確率
                    row.append(prob)
                transition_matrix.append(row)
            
            markov_matrices[f'桁{i}'] = pd.DataFrame(
                transition_matrix,
                index=states,
                columns=states
            )
        
        return markov_matrices
    
    def get_recommended_numbers_numbers_advanced(self, digits: int, strategy: str,
                                                settings: Dict[str, bool],
                                                start_date: Optional[str] = None,
                                                end_date: Optional[str] = None,
                                                top_n: int = 5) -> List[str]:
        """
        ナンバーズの推奨数字を取得（高度版：設定に基づいて複数の要素を考慮）
        
        Args:
            digits: 桁数 (3 or 4)
            strategy: 戦略 ('hot': 出現頻度高い, 'cold': 出現頻度低い, 'mixed': 混合)
            settings: 予測設定（どの要素を使用するか）
            start_date: 開始日
            end_date: 終了日
            top_n: 返す推奨数字の数
        
        Returns:
            推奨数字のリスト（最大top_n個）
        """
        # 基本の出現頻度分析
        freq_df = self.analyze_numbers_frequency(digits, start_date, end_date)
        
        if freq_df.empty:
            return []
        
        # 各桁の候補数字を取得（上位5個）
        digit_options = {}
        for col in freq_df.columns:
            if settings.get('use_frequency', True):
                top_digits = freq_df[col].nlargest(5).index.tolist()
            else:
                top_digits = list(range(10))
            digit_options[col] = top_digits
        
        # 組み合わせを生成
        combinations = list(itertools.product(*digit_options.values()))
        
        # 各組み合わせのスコアを計算
        scored_combinations = []
        
        for combo in combinations:
            score = 0.0
            combo_str = ''.join(map(str, combo))
            
            # 1. 出現頻度スコア
            if settings.get('use_frequency', True):
                freq_score = 0
                for i, digit in enumerate(combo):
                    col = list(freq_df.columns)[i]
                    freq_score += freq_df.loc[digit, col]
                score += freq_score * 0.3  # 重み: 0.3
            
            # 2. 合計値スコア
            if settings.get('use_sum', False):
                sum_df = self.analyze_numbers_sum(digits, start_date, end_date)
                if not sum_df.empty:
                    combo_sum = sum(int(d) for d in combo)
                    # 最も出現頻度の高い合計値に近いほど高スコア
                    most_common_sum = sum_df.loc[sum_df['出現回数'].idxmax(), '合計値']
                    sum_diff = abs(combo_sum - most_common_sum)
                    sum_score = max(0, 10 - sum_diff)  # 差が小さいほど高スコア
                    score += sum_score * 0.1
            
            # 3. 奇偶比率スコア
            if settings.get('use_odd_even', False):
                odd_even = self.analyze_numbers_odd_even_ratio(digits, start_date, end_date)
                if odd_even:
                    avg_odd = odd_even.get('平均奇数個数', digits / 2)
                    combo_odd = sum(1 for d in combo if int(d) % 2 == 1)
                    odd_diff = abs(combo_odd - avg_odd)
                    odd_score = max(0, 5 - odd_diff)
                    score += odd_score * 0.1
            
            # 4. 大小比率スコア
            if settings.get('use_high_low', False):
                high_low = self.analyze_numbers_high_low_ratio(digits, start_date, end_date)
                if high_low:
                    avg_high = high_low.get('平均高数字個数', digits / 2)
                    combo_high = sum(1 for d in combo if int(d) >= 5)
                    high_diff = abs(combo_high - avg_high)
                    high_score = max(0, 5 - high_diff)
                    score += high_score * 0.1
            
            # 5. 連番スコア
            if settings.get('use_consecutive', False):
                consecutive_df = self.analyze_numbers_consecutive(digits, start_date, end_date)
                if not consecutive_df.empty:
                    # 連番があるかチェック
                    has_consecutive = False
                    for i in range(len(combo) - 1):
                        if combo[i+1] == combo[i] + 1:
                            has_consecutive = True
                            break
                    if has_consecutive:
                        score += 2.0 * 0.05
            
            # 6. 重複スコア
            if settings.get('use_duplicates', False):
                duplicates = self.analyze_numbers_duplicates(digits, start_date, end_date)
                if duplicates:
                    combo_counts = Counter(combo)
                    max_count = max(combo_counts.values())
                    # ダブルが適度にある場合にスコア
                    if max_count == 2:
                        score += 1.5 * 0.05
            
            # 7. デジタルルートスコア
            if settings.get('use_digital_root', False):
                root_df = self.analyze_numbers_digital_root(digits, start_date, end_date)
                if not root_df.empty:
                    def digital_root(n):
                        while n >= 10:
                            n = sum(int(d) for d in str(n))
                        return n
                    combo_root = digital_root(sum(combo))
                    most_common_root = root_df.loc[root_df['出現回数'].idxmax(), 'デジタルルート']
                    if combo_root == most_common_root:
                        score += 1.0 * 0.05
            
            # 8. トレンドスコア
            if settings.get('use_trend', False):
                trend_df = self.analyze_numbers_trend(digits, periods=10, start_date=start_date, end_date=end_date)
                if not trend_df.empty:
                    for i, digit in enumerate(combo):
                        col = f'桁{i+1}'
                        if col in trend_df['桁'].values:
                            trend_avg = trend_df[trend_df['桁'] == i+1][f'過去10回平均'].values[0]
                            trend_diff = abs(digit - trend_avg)
                            trend_score = max(0, 5 - trend_diff)
                            score += trend_score * 0.05
            
            # 9. EMAスコア
            if settings.get('use_ema', False):
                ema_df = self.analyze_numbers_ema(digits, span=10, start_date=start_date, end_date=end_date)
                if not ema_df.empty:
                    for i, digit in enumerate(combo):
                        col = f'桁{i+1}'
                        if col in ema_df['桁'].values:
                            ema_value = ema_df[ema_df['桁'] == i+1]['EMA(10)'].values[0]
                            ema_diff = abs(digit - ema_value)
                            ema_score = max(0, 5 - ema_diff)
                            score += ema_score * 0.05
            
            # 10. マルコフ連鎖スコア
            if settings.get('use_markov', False):
                markov_matrices = self.analyze_numbers_markov(digits, start_date, end_date)
                if markov_matrices:
                    # 最新のデータを取得して遷移確率を計算
                    if digits == 3:
                        df = self.db.get_numbers3_data(start_date, end_date)
                    else:
                        df = self.db.get_numbers_data(start_date, end_date)
                    
                    if not df.empty:
                        df = df.sort_values('draw_date')
                        last_number = df.iloc[-1]['winning_number']
                        
                        markov_score = 0
                        for i, digit in enumerate(combo):
                            col = f'桁{i+1}'
                            if col in markov_matrices:
                                try:
                                    prev_digit = int(last_number[i])
                                    # 遷移確率行列に存在するかチェック
                                    if (prev_digit in markov_matrices[col].index and 
                                        digit in markov_matrices[col].columns):
                                        transition_prob = markov_matrices[col].loc[prev_digit, digit]
                                        markov_score += transition_prob
                                    else:
                                        # 存在しない場合はデフォルト値（0）を使用
                                        markov_score += 0.0
                                except (ValueError, IndexError, KeyError):
                                    # エラーが発生した場合はスキップ
                                    markov_score += 0.0
                        score += markov_score * 0.1
            
            scored_combinations.append((combo, score, combo_str))
        
        # 戦略に応じてソート
        if strategy == 'hot':
            scored_combinations.sort(key=lambda x: x[1], reverse=True)
        elif strategy == 'cold':
            scored_combinations.sort(key=lambda x: x[1])
        else:  # mixed
            scored_combinations.sort(key=lambda x: x[1], reverse=True)
        
        # 上位top_n個を取得
        recommended_list = [combo_str for _, _, combo_str in scored_combinations[:top_n]]
        
        return recommended_list
    
    def get_recommended_numbers_multiple_advanced(self, lottery_type: str,
                                                  strategy: str = 'hot',
                                                  count: int = 6,
                                                  settings: Dict[str, bool] = None,
                                                  top_n: int = 5,
                                                  start_date: Optional[str] = None,
                                                  end_date: Optional[str] = None) -> List[List[int]]:
        """
        ロト6/7/ミニロトの推奨数字を複数パターン取得（高度版：設定に基づいて複数の要素を考慮）
        
        Args:
            lottery_type: 宝くじタイプ ('loto6', 'loto7', 'miniloto')
            strategy: 戦略 ('hot': 出現頻度高い, 'cold': 出現頻度低い, 'mixed': 混合)
            count: 1パターンあたりの数字の数
            settings: 予測設定（どの要素を使用するか）
            top_n: 返す推奨数字パターンの数（デフォルト5）
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            推奨数字のリストのリスト（最大top_n個）
        """
        if settings is None:
            settings = {}
        
        # 出現頻度データを取得
        if lottery_type == 'loto6':
            freq_df = self.analyze_loto6_frequency(start_date, end_date)
            max_num = 43
        elif lottery_type == 'loto7':
            freq_df = self.analyze_loto7_frequency(start_date, end_date)
            max_num = 37
        elif lottery_type == 'miniloto':
            freq_df = self.analyze_miniloto_frequency(start_date, end_date)
            max_num = 31
        else:
            return []
        
        if freq_df.empty:
            return []
        
        # 数字とその出現頻度を取得
        number_freq = {}
        for _, row in freq_df.iterrows():
            number_freq[row['数字']] = row['出現回数']
        
        # すべての数字に出現頻度を設定（出現回数0の数字も含む）
        for num in range(1, max_num + 1):
            if num not in number_freq:
                number_freq[num] = 0
        
        # 候補数字を取得（出現頻度が高い/低い数字）
        sorted_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)
        
        if strategy == 'hot':
            candidate_numbers = [num for num, _ in sorted_numbers[:max_num // 2]]
        elif strategy == 'cold':
            candidate_numbers = [num for num, _ in sorted_numbers[-max_num // 2:]]
        else:  # mixed
            candidate_numbers = list(range(1, max_num + 1))
        
        # 事前にデータを取得（ループ外で一度だけ）
        historical_data = None
        avg_sum = None
        avg_odd = None
        avg_high = None
        pair_df = None
        pair_dict = {}  # ペアの出現回数を辞書で保持
        
        # 必要なデータを事前に取得
        if (settings.get('use_sum', False) or 
            settings.get('use_odd_even', False) or 
            settings.get('use_high_low', False) or
            settings.get('use_duplicates', False)):
            try:
                if lottery_type == 'loto6':
                    historical_data = self.db.get_loto6_data(start_date, end_date)
                elif lottery_type == 'loto7':
                    historical_data = self.db.get_loto7_data(start_date, end_date)
                else:
                    historical_data = self.db.get_miniloto_data(start_date, end_date)
                
                if not historical_data.empty:
                    import json
                    sums = []
                    odd_counts = []
                    mid = max_num // 2
                    high_counts = []
                    
                    for numbers_json in historical_data['numbers']:
                        try:
                            numbers = json.loads(numbers_json)
                            sums.append(sum(numbers))
                            odd_counts.append(sum(1 for n in numbers if n % 2 == 1))
                            high_counts.append(sum(1 for n in numbers if n > mid))
                        except (json.JSONDecodeError, TypeError, ValueError):
                            continue
                    
                    if sums:
                        avg_sum = sum(sums) / len(sums)
                    if odd_counts:
                        avg_odd = sum(odd_counts) / len(odd_counts)
                    if high_counts:
                        avg_high = sum(high_counts) / len(high_counts)
            except Exception as e:
                # エラーが発生した場合は、該当する分析をスキップ
                pass
        
        # ペア分析データを事前に取得（取得数を減らして高速化）
        if settings.get('use_duplicates', False):
            try:
                # top_nを減らして高速化（50→30）
                pair_df = self.analyze_number_pairs(lottery_type, start_date, end_date, top_n=30)
                if not pair_df.empty:
                    # ペアの出現回数を辞書に格納（高速アクセス用）
                    for _, row in pair_df.iterrows():
                        pair_dict[(row['数字1'], row['数字2'])] = row['出現回数']
            except Exception as e:
                # エラーが発生した場合は、ペア分析をスキップ
                pair_df = None
                pair_dict = {}
        
        # 組み合わせを生成してスコア付け
        scored_patterns = []
        seen_patterns = set()  # 重複チェック用のセット（タプルを使用）
        # ループ回数をさらに減らす（ロト6/7/ミニロトの組み合わせ数を考慮）
        # ロト6: 43C6 ≈ 6,096,454, ロト7: 37C7 ≈ 10,295,472, ミニロト: 31C5 ≈ 169,911
        # 実際には候補数字を絞っているので、もっと少ない回数で十分
        max_iterations = min(300, len(candidate_numbers) * 10)  # 候補数に応じて調整
        
        for iteration in range(max_iterations):
            try:
                pattern = tuple(sorted(random.sample(candidate_numbers, min(count, len(candidate_numbers)))))
                
                # 重複チェック（セットを使用して高速化）
                if pattern in seen_patterns:
                    continue
                seen_patterns.add(pattern)
                
                score = 0.0
                
                # 1. 出現頻度スコア
                if settings.get('use_frequency', True):
                    freq_score = sum(number_freq.get(num, 0) for num in pattern)
                    score += freq_score * 0.3
                
                # 2. 合計値スコア
                if settings.get('use_sum', False) and avg_sum is not None:
                    pattern_sum = sum(pattern)
                    sum_diff = abs(pattern_sum - avg_sum)
                    sum_score = max(0, 20 - sum_diff)
                    score += sum_score * 0.1
                
                # 3. 奇偶比率スコア
                if settings.get('use_odd_even', False) and avg_odd is not None:
                    pattern_odd = sum(1 for num in pattern if num % 2 == 1)
                    odd_diff = abs(pattern_odd - avg_odd)
                    odd_score = max(0, 5 - odd_diff)
                    score += odd_score * 0.1
                
                # 4. 大小比率スコア
                if settings.get('use_high_low', False) and avg_high is not None:
                    mid = max_num // 2
                    pattern_high = sum(1 for num in pattern if num > mid)
                    high_diff = abs(pattern_high - avg_high)
                    high_score = max(0, 5 - high_diff)
                    score += high_score * 0.1
                
                # 5. 連番スコア
                if settings.get('use_consecutive', False):
                    has_consecutive = False
                    sorted_pattern = sorted(pattern)
                    for i in range(len(sorted_pattern) - 1):
                        if sorted_pattern[i+1] == sorted_pattern[i] + 1:
                            has_consecutive = True
                            break
                    if has_consecutive:
                        score += 2.0 * 0.05
                
                # 6. ペアスコア（重複の代わり）
                if settings.get('use_duplicates', False) and pair_dict:
                    pair_score = 0
                    for i in range(len(pattern) - 1):
                        pair = (pattern[i], pattern[i+1])
                        if pair in pair_dict:
                            pair_score += pair_dict[pair]
                    score += pair_score * 0.05
                
                scored_patterns.append((list(pattern), score))
                
                # 十分なパターンが集まったら早期終了（top_nの5倍で十分）
                if len(scored_patterns) >= top_n * 5:
                    break
                    
            except Exception as e:
                # エラーが発生した場合はスキップして続行
                continue
        
        # スコアでソート
        if strategy == 'hot':
            scored_patterns.sort(key=lambda x: x[1], reverse=True)
        elif strategy == 'cold':
            scored_patterns.sort(key=lambda x: x[1])
        else:  # mixed
            scored_patterns.sort(key=lambda x: x[1], reverse=True)
        
        # 上位top_n個を取得
        recommended_patterns = []
        for pattern, _ in scored_patterns[:top_n]:
            recommended_patterns.append(pattern)
        
        return recommended_patterns

