"""
データモデル定義
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import date


@dataclass
class Numbers3Data:
    """ナンバーズ3データモデル"""
    draw_date: date
    draw_number: int
    winning_number: str  # 3桁の数字（例: "123"）
    
    def __post_init__(self):
        if len(self.winning_number) != 3:
            raise ValueError("当選番号は3桁である必要があります")


@dataclass
class NumbersData:
    """ナンバーズデータモデル"""
    draw_date: date
    draw_number: int
    winning_number: str  # 4桁の数字（例: "1234"）
    
    def __post_init__(self):
        if len(self.winning_number) != 4:
            raise ValueError("当選番号は4桁である必要があります")


@dataclass
class Loto6Data:
    """ロト6データモデル"""
    draw_date: date
    draw_number: int
    numbers: List[int]  # 6個の数字（1-43）
    bonus_number: Optional[int] = None  # ボーナス番号（1-43）
    
    def __post_init__(self):
        if len(self.numbers) != 6:
            raise ValueError("ロト6は6個の数字が必要です")
        if not all(1 <= n <= 43 for n in self.numbers):
            raise ValueError("ロト6の数字は1-43の範囲である必要があります")
        if self.bonus_number and not (1 <= self.bonus_number <= 43):
            raise ValueError("ボーナス番号は1-43の範囲である必要があります")


@dataclass
class Loto7Data:
    """ロト7データモデル"""
    draw_date: date
    draw_number: int
    numbers: List[int]  # 7個の数字（1-37）
    bonus_number: Optional[int] = None  # ボーナス番号1（1-37）
    bonus_number2: Optional[int] = None  # ボーナス番号2（1-37）
    
    def __post_init__(self):
        if len(self.numbers) != 7:
            raise ValueError("ロト7は7個の数字が必要です")
        if not all(1 <= n <= 37 for n in self.numbers):
            raise ValueError("ロト7の数字は1-37の範囲である必要があります")
        if self.bonus_number and not (1 <= self.bonus_number <= 37):
            raise ValueError("ボーナス番号は1-37の範囲である必要があります")
        if self.bonus_number2 and not (1 <= self.bonus_number2 <= 37):
            raise ValueError("ボーナス番号2は1-37の範囲である必要があります")


@dataclass
class MinilotoData:
    """ミニロトデータモデル"""
    draw_date: date
    draw_number: int
    numbers: List[int]  # 5個の数字（1-31）
    bonus_number: Optional[int] = None  # ボーナス番号（1-31）
    
    def __post_init__(self):
        if len(self.numbers) != 5:
            raise ValueError("ミニロトは5個の数字が必要です")
        if not all(1 <= n <= 31 for n in self.numbers):
            raise ValueError("ミニロトの数字は1-31の範囲である必要があります")
        if self.bonus_number and not (1 <= self.bonus_number <= 31):
            raise ValueError("ボーナス番号は1-31の範囲である必要があります")

