"""
データベース設定とスキーマ定義
SQLiteを使用して大量の宝くじデータを保存
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd


class DatabaseManager:
    """データベース管理クラス"""
    
    def __init__(self, db_path: str = "lottery_data.db"):
        """
        データベースマネージャーの初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """データベースとテーブルの初期化"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()
        
        # ナンバーズ4テーブル（4桁）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date DATE NOT NULL,
                draw_number INTEGER NOT NULL,
                winning_number TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, draw_number)
            )
        """)

        # ナンバーズ3テーブル（3桁）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS numbers3 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date DATE NOT NULL,
                draw_number INTEGER NOT NULL,
                winning_number TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, draw_number)
            )
        """)
        
        # ロト6テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loto6 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date DATE NOT NULL,
                draw_number INTEGER NOT NULL,
                numbers TEXT NOT NULL,
                bonus_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, draw_number)
            )
        """)
        
        # ロト7テーブル（ボーナス2つをサポート）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loto7 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date DATE NOT NULL,
                draw_number INTEGER NOT NULL,
                numbers TEXT NOT NULL,
                bonus_number INTEGER,
                bonus_number2 INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, draw_number)
            )
        """)
        
        # ミニロトテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS miniloto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date DATE NOT NULL,
                draw_number INTEGER NOT NULL,
                numbers TEXT NOT NULL,
                bonus_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, draw_number)
            )
        """)
        
        # インデックスの作成（検索性能向上）
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_numbers_date ON numbers(draw_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_numbers3_date ON numbers3(draw_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_loto6_date ON loto6(draw_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_loto7_date ON loto7(draw_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_miniloto_date ON miniloto(draw_date)")
        
        # 既存DBへの列追加（ロト7の2つ目のボーナス）
        self._ensure_column(cursor, "loto7", "bonus_number2 INTEGER")
        
        self.conn.commit()

    def _ensure_column(self, cursor: sqlite3.Cursor, table: str, column_def: str):
        """
        既存テーブルに列がなければ追加する
        """
        col_name = column_def.split()[0]
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cursor.fetchall()]
        if col_name not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
    
    def insert_numbers(self, draw_date: str, draw_number: int, winning_number: str) -> bool:
        """
        ナンバーズデータの挿入
        
        Args:
            draw_date: 抽選日 (YYYY-MM-DD)
            draw_number: 抽選回数
            winning_number: 当選番号 (4桁)
        
        Returns:
            成功した場合True
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO numbers (draw_date, draw_number, winning_number)
                VALUES (?, ?, ?)
            """, (draw_date, draw_number, winning_number))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"エラー: {e}")
            return False

    def insert_numbers3(self, draw_date: str, draw_number: int, winning_number: str) -> bool:
        """
        ナンバーズ3データの挿入（3桁）
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO numbers3 (draw_date, draw_number, winning_number)
                VALUES (?, ?, ?)
            """, (draw_date, draw_number, winning_number))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"エラー: {e}")
            return False
    
    def insert_loto6(self, draw_date: str, draw_number: int, numbers: List[int], 
                     bonus_number: Optional[int] = None) -> bool:
        """
        ロト6データの挿入
        
        Args:
            draw_date: 抽選日 (YYYY-MM-DD)
            draw_number: 抽選回数
            numbers: 当選番号リスト（6個）
            bonus_number: ボーナス番号（オプション）
        
        Returns:
            成功した場合True
        """
        try:
            cursor = self.conn.cursor()
            numbers_json = json.dumps(sorted(numbers))
            cursor.execute("""
                INSERT OR IGNORE INTO loto6 (draw_date, draw_number, numbers, bonus_number)
                VALUES (?, ?, ?, ?)
            """, (draw_date, draw_number, numbers_json, bonus_number))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"エラー: {e}")
            return False
    
    def insert_loto7(self, draw_date: str, draw_number: int, numbers: List[int], 
                     bonus_number: Optional[int] = None, bonus_number2: Optional[int] = None) -> bool:
        """
        ロト7データの挿入
        
        Args:
            draw_date: 抽選日 (YYYY-MM-DD)
            draw_number: 抽選回数
            numbers: 当選番号リスト（7個）
            bonus_number: ボーナス番号（オプション）
        
        Returns:
            成功した場合True
        """
        try:
            cursor = self.conn.cursor()
            numbers_json = json.dumps(sorted(numbers))
            cursor.execute("""
                INSERT OR IGNORE INTO loto7 (draw_date, draw_number, numbers, bonus_number, bonus_number2)
                VALUES (?, ?, ?, ?, ?)
            """, (draw_date, draw_number, numbers_json, bonus_number, bonus_number2))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"エラー: {e}")
            return False
    
    def insert_miniloto(self, draw_date: str, draw_number: int, numbers: List[int], 
                        bonus_number: Optional[int] = None) -> bool:
        """
        ミニロトデータの挿入
        
        Args:
            draw_date: 抽選日 (YYYY-MM-DD)
            draw_number: 抽選回数
            numbers: 当選番号リスト（5個）
            bonus_number: ボーナス番号（オプション）
        
        Returns:
            成功した場合True
        """
        try:
            cursor = self.conn.cursor()
            numbers_json = json.dumps(sorted(numbers))
            cursor.execute("""
                INSERT OR IGNORE INTO miniloto (draw_date, draw_number, numbers, bonus_number)
                VALUES (?, ?, ?, ?)
            """, (draw_date, draw_number, numbers_json, bonus_number))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"エラー: {e}")
            return False
    
    def get_numbers_data(self, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """ナンバーズデータの取得"""
        query = "SELECT * FROM numbers WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND draw_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND draw_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY draw_date DESC, draw_number DESC"
        return pd.read_sql_query(query, self.conn, params=params)

    def get_numbers3_data(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """ナンバーズ3データの取得"""
        query = "SELECT * FROM numbers3 WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND draw_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND draw_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY draw_date DESC, draw_number DESC"
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_loto6_data(self, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """ロト6データの取得"""
        query = "SELECT * FROM loto6 WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND draw_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND draw_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY draw_date DESC, draw_number DESC"
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_loto7_data(self, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """ロト7データの取得"""
        query = "SELECT * FROM loto7 WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND draw_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND draw_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY draw_date DESC, draw_number DESC"
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_miniloto_data(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """ミニロトデータの取得"""
        query = "SELECT * FROM miniloto WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND draw_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND draw_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY draw_date DESC, draw_number DESC"
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_statistics(self, table_name: str) -> Dict[str, Any]:
        """統計情報の取得"""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # 日付形式（YYYY-MM-DDまたはYYYY/MM/DD）のデータのみを取得
        # 数値や不正な形式のデータを除外
        cursor.execute(f"""
            SELECT MIN(draw_date) as min_date, MAX(draw_date) as max_date 
            FROM {table_name}
            WHERE draw_date LIKE '____-__-__' OR draw_date LIKE '____/__/__'
        """)
        date_range = cursor.fetchone()
        
        min_date = date_range[0] if date_range[0] else None
        max_date = date_range[1] if date_range[1] else None
        
        # 日付形式を統一（YYYY-MM-DD）
        if min_date and '/' in str(min_date):
            min_date = str(min_date).replace('/', '-')
        if max_date and '/' in str(max_date):
            max_date = str(max_date).replace('/', '-')
        
        return {
            "count": count,
            "min_date": min_date,
            "max_date": max_date
        }
    
    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()

