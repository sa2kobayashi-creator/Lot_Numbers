"""
Streamlitメインアプリケーション
宝くじデータ管理・分析アプリ
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import DatabaseManager
from analyzer import LotteryAnalyzer
from data_fetcher import DataFetcher
import json


# ページ設定
st.set_page_config(
    page_title="宝くじデータ分析アプリ",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = LotteryAnalyzer(st.session_state.db_manager)
if 'fetcher' not in st.session_state:
    st.session_state.fetcher = DataFetcher(st.session_state.db_manager)


def main():
    """メインアプリケーション"""
    st.title("🎰 宝くじデータ分析アプリ")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("📊 メニュー")
        page = st.radio(
            "ページを選択",
            ["🏠 ホーム", "📥 データ登録", "📊 データ分析", "📈 統計情報", "🔍 データ検索"]
        )
    
    # ページルーティング
    if page == "🏠 ホーム":
        show_home()
    elif page == "📥 データ登録":
        show_data_registration()
    elif page == "📊 データ分析":
        show_data_analysis()
    elif page == "📈 統計情報":
        show_statistics()
    elif page == "🔍 データ検索":
        show_data_search()


def show_home():
    """ホームページ"""
    st.header("ホーム")
    st.markdown("""
    ### このアプリについて
    
    このアプリは、以下の宝くじの過去データを管理・分析するためのツールです：
    
    - **ナンバーズ**: 4桁の数字（0000-9999）
    - **ロト6**: 1-43から6個の数字
    - **ロト7**: 1-37から7個の数字
    - **ミニロト**: 1-31から5個の数字
    
    ### 主な機能
    
    1. **データ登録**: 手動またはCSVファイルからデータを登録
    2. **データ分析**: 出現頻度、ペア分析など
    3. **統計情報**: データベースの統計情報を表示
    4. **データ検索**: 日付範囲でデータを検索・表示
    
    ### 使い方
    
    サイドバーのメニューから目的のページを選択してください。
    
    ### 過去データの入手方法
    
    過去データを登録する方法については、以下のドキュメントを参照してください：
    - **DATA_SOURCES.md**: データ入手先と方法の詳細
    
    主な入手方法：
    1. **公式サイト**: 各都道府県の財務局サイト
    2. **宝くじ情報サイト**: 各種情報提供サイト
    3. **CSVインポート**: 手動で作成したCSVファイルから一括インポート
    4. **Webスクレイピング**: プログラムで自動取得（利用規約要確認）
    """)


def show_data_registration():
    """データ登録ページ"""
    st.header("📥 データ登録")
    
    st.info("💡 **過去データの入手方法**: `DATA_SOURCES.md` ファイルを参照してください。")
    
    tab1, tab2, tab3 = st.tabs(["手動登録", "CSVインポート", "Webスクレイピング"])
    
    with tab1:
        st.subheader("手動データ登録")
        lottery_type = st.selectbox(
            "宝くじタイプを選択",
            ["ナンバーズ3", "ナンバーズ4", "ロト6", "ロト7", "ミニロト"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            draw_date = st.date_input("抽選日", value=date.today())
        with col2:
            draw_number = st.number_input("抽選回数", min_value=1, value=1)
        
        if lottery_type == "ナンバーズ4":
            winning_number = st.text_input("当選番号（4桁）", max_chars=4)
            if st.button("登録"):
                if len(winning_number) == 4 and winning_number.isdigit():
                    if st.session_state.fetcher.add_manual_numbers(
                        str(draw_date), draw_number, winning_number
                    ):
                        st.success("データを登録しました！")
                    else:
                        st.error("登録に失敗しました（重複の可能性があります）")
                else:
                    st.error("4桁の数字を入力してください")

        elif lottery_type == "ナンバーズ3":
            winning_number = st.text_input("当選番号（3桁）", max_chars=3)
            if st.button("登録"):
                if len(winning_number) == 3 and winning_number.isdigit():
                    if st.session_state.fetcher.add_manual_numbers3(
                        str(draw_date), draw_number, winning_number
                    ):
                        st.success("データを登録しました！")
                    else:
                        st.error("登録に失敗しました（重複の可能性があります）")
                else:
                    st.error("3桁の数字を入力してください")
        
        elif lottery_type == "ロト6":
            st.write("当選番号（6個、1-43の範囲）")
            numbers = []
            cols = st.columns(6)
            for i, col in enumerate(cols):
                with col:
                    num = col.number_input(f"数字{i+1}", min_value=1, max_value=43, key=f"loto6_{i}")
                    numbers.append(num)
            bonus = st.number_input("ボーナス番号（オプション）", min_value=1, max_value=43, value=None)
            
            if st.button("登録"):
                if len(set(numbers)) == 6:
                    bonus_val = int(bonus) if bonus else None
                    if st.session_state.fetcher.add_manual_loto6(
                        str(draw_date), draw_number, numbers, bonus_val
                    ):
                        st.success("データを登録しました！")
                    else:
                        st.error("登録に失敗しました（重複の可能性があります）")
                else:
                    st.error("6個の異なる数字を入力してください")
        
        elif lottery_type == "ロト7":
            st.write("当選番号（7個、1-37の範囲）")
            numbers = []
            cols = st.columns(7)
            for i, col in enumerate(cols):
                with col:
                    num = col.number_input(f"数字{i+1}", min_value=1, max_value=37, key=f"loto7_{i}")
                    numbers.append(num)
            colb1, colb2 = st.columns(2)
            with colb1:
                bonus = st.number_input("ボーナス番号1（オプション）", min_value=1, max_value=37, value=None, key="loto7_bonus1")
            with colb2:
                bonus2 = st.number_input("ボーナス番号2（オプション）", min_value=1, max_value=37, value=None, key="loto7_bonus2")
            
            if st.button("登録"):
                if len(set(numbers)) == 7:
                    bonus_val = int(bonus) if bonus else None
                    bonus_val2 = int(bonus2) if bonus2 else None
                    if st.session_state.fetcher.add_manual_loto7(
                        str(draw_date), draw_number, numbers, bonus_val, bonus_val2
                    ):
                        st.success("データを登録しました！")
                    else:
                        st.error("登録に失敗しました（重複の可能性があります）")
                else:
                    st.error("7個の異なる数字を入力してください")
        
        elif lottery_type == "ミニロト":
            st.write("当選番号（5個、1-31の範囲）")
            numbers = []
            cols = st.columns(5)
            for i, col in enumerate(cols):
                with col:
                    num = col.number_input(f"数字{i+1}", min_value=1, max_value=31, key=f"miniloto_{i}")
                    numbers.append(num)
            bonus = st.number_input("ボーナス番号（オプション）", min_value=1, max_value=31, value=None)
            
            if st.button("登録"):
                if len(set(numbers)) == 5:
                    bonus_val = int(bonus) if bonus else None
                    if st.session_state.fetcher.add_manual_miniloto(
                        str(draw_date), draw_number, numbers, bonus_val
                    ):
                        st.success("データを登録しました！")
                    else:
                        st.error("登録に失敗しました（重複の可能性があります）")
                else:
                    st.error("5個の異なる数字を入力してください")
    
    with tab2:
        st.subheader("CSVファイルからインポート")
        st.markdown("""
        CSVファイルの形式：
        - **ナンバーズ3/4**: `draw_date`, `draw_number`, `winning_number`
        - **ロト6/ロト7/ミニロト**: `draw_date`, `draw_number`, `numbers` (リスト形式), `bonus_number` (オプション)
        """)
        
        lottery_type_csv = st.selectbox(
            "宝くじタイプを選択",
            ["ナンバーズ3", "ナンバーズ4", "ロト6", "ロト7", "ミニロト"],
            key="csv_type"
        )
        
        # サンプルCSV作成機能
        st.markdown("---")
        st.subheader("サンプルCSVファイルの作成")
        st.write("CSVファイルの形式を確認するために、サンプルファイルを作成できます。")
        
        if st.button("サンプルCSVを作成", key="create_sample_csv"):
            type_map = {
                "ナンバーズ3": "numbers3",
                "ナンバーズ4": "numbers",
                "ロト6": "loto6",
                "ロト7": "loto7",
                "ミニロト": "miniloto"
            }
            filename = f"sample_{type_map[lottery_type_csv]}.csv"
            st.session_state.fetcher.create_sample_csv(type_map[lottery_type_csv], filename)
            st.success(f"サンプルCSVファイルを作成しました: {filename}")
            st.info("ファイルはプロジェクトのルートディレクトリに保存されます。")
        
        uploaded_file = st.file_uploader("CSVファイルをアップロード", type=['csv'], key="csv_uploader")
        
        if uploaded_file is not None:
            if st.button("インポート実行"):
                type_map = {
                    "ナンバーズ3": "numbers3",
                    "ナンバーズ4": "numbers",
                    "ロト6": "loto6",
                    "ロト7": "loto7",
                    "ミニロト": "miniloto"
                }
                # 一時ファイルとして保存
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    count = st.session_state.fetcher.import_from_csv(
                        tmp_path, type_map[lottery_type_csv]
                    )
                    st.success(f"{count}件のデータをインポートしました！")
                finally:
                    os.unlink(tmp_path)
    
    with tab3:
        st.subheader("Webスクレイピング")
        st.warning("""
        ⚠️ **重要**: Webスクレイピングを使用する前に、以下の点を確認してください：
        
        1. **利用規約の確認**: 対象サイトの利用規約を必ず確認し、スクレイピングが許可されているか確認してください
        2. **サーバー負荷**: 適切な間隔を空けてアクセスし、サーバーに負荷をかけないようにしてください
        3. **法的責任**: スクレイピングによる問題は自己責任となります
        """)
        
        lottery_type_scrape = st.selectbox(
            "宝くじタイプを選択",
            ["ナンバーズ3", "ナンバーズ4", "ロト6", "ロト7", "ミニロト"],
            key="scrape_type"
        )
        
        url = st.text_input("スクレイピング対象のURLを入力")
        
        st.info("""
        **注意**: この機能は汎用的なパーサーを使用しています。
        実際のサイトのHTML構造に合わせて、`data_fetcher.py`の`_default_parser`メソッドを
        カスタマイズする必要がある場合があります。
        """)
        
        if url and st.button("スクレイピング実行"):
            type_map = {
                "ナンバーズ3": "numbers3",
                "ナンバーズ4": "numbers",
                "ロト6": "loto6",
                "ロト7": "loto7",
                "ミニロト": "miniloto"
            }
            
            try:
                with st.spinner("データを取得中..."):
                    count = st.session_state.fetcher.scrape_from_url(
                        url, type_map[lottery_type_scrape]
                    )
                
                if count > 0:
                    st.success(f"{count}件のデータを取得しました！")
                else:
                    st.error("データの取得に失敗しました。URLまたはHTML構造を確認してください。")
                    st.info("""
                    **トラブルシューティング**:
                    - URLが正しいか確認してください
                    - サイトのHTML構造が想定と異なる可能性があります
                    - `data_fetcher.py`のパーサーをカスタマイズする必要があるかもしれません
                    """)
            except ImportError as e:
                st.error("Webスクレイピング機能を使用するには、追加のパッケージが必要です。")
                st.code("pip install beautifulsoup4 lxml", language="bash")
                st.error(str(e))


def show_data_analysis():
    """データ分析ページ"""
    st.header("📊 データ分析")
    
    lottery_type = st.selectbox(
        "宝くじタイプを選択",
        ["ナンバーズ3", "ナンバーズ4", "ロト6", "ロト7", "ミニロト"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日", value=None, key="analysis_start")
    with col2:
        end_date = st.date_input("終了日", value=None, key="analysis_end")
    
    start_str = str(start_date) if start_date else None
    end_str = str(end_date) if end_date else None
    
    tab1, tab2, tab3, tab4 = st.tabs(["出現頻度", "推奨数字", "ペア分析", "詳細分析"])
    
    with tab1:
        st.subheader("数字出現頻度")
        include_bonus = st.checkbox("ボーナス番号を含める", value=False)
        
        if lottery_type == "ナンバーズ3":
            df = st.session_state.analyzer.analyze_numbers_frequency(3, start_str, end_str)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df)
            else:
                st.warning("データがありません")
        elif lottery_type == "ナンバーズ4":
            df = st.session_state.analyzer.analyze_numbers_frequency(4, start_str, end_str)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df)
            else:
                st.warning("データがありません")
        
        elif lottery_type == "ロト6":
            df = st.session_state.analyzer.analyze_loto6_frequency(start_str, end_str, include_bonus)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index('数字'))
            else:
                st.warning("データがありません")
        
        elif lottery_type == "ロト7":
            df = st.session_state.analyzer.analyze_loto7_frequency(start_str, end_str, include_bonus)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index('数字'))
            else:
                st.warning("データがありません")
        
        elif lottery_type == "ミニロト":
            df = st.session_state.analyzer.analyze_miniloto_frequency(start_str, end_str, include_bonus)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index('数字'))
            else:
                st.warning("データがありません")
    
    with tab2:
        st.subheader("推奨数字")
        strategy = st.selectbox(
            "戦略を選択",
            ["hot", "cold", "mixed"],
            format_func=lambda x: {"hot": "出現頻度が高い", "cold": "出現頻度が低い", "mixed": "混合"}[x]
        )
        
        if lottery_type in ["ナンバーズ3", "ナンバーズ4"]:
            st.info("ナンバーズの推奨数字機能は開発中です")
        else:
            type_map = {
                "ロト6": "loto6",
                "ロト7": "loto7",
                "ミニロト": "miniloto"
            }
            count_map = {
                "ロト6": 6,
                "ロト7": 7,
                "ミニロト": 5
            }
            
            recommended = st.session_state.analyzer.get_recommended_numbers(
                type_map[lottery_type],
                strategy,
                count_map[lottery_type],
                start_str,
                end_str
            )
            
            if recommended:
                st.write("**推奨数字:**")
                st.write(sorted(recommended))
                st.write(f"**数字の数:** {len(recommended)}")
            else:
                st.warning("データが不足しています")
    
    with tab3:
        st.subheader("数字ペア分析")
        top_n = st.slider("表示する上位ペア数", 10, 50, 20)
        
        if lottery_type in ["ナンバーズ3", "ナンバーズ4"]:
            st.info("ナンバーズのペア分析機能は開発中です")
        else:
            type_map = {
                "ロト6": "loto6",
                "ロト7": "loto7",
                "ミニロト": "miniloto"
            }
            
            df = st.session_state.analyzer.analyze_number_pairs(
                type_map[lottery_type],
                start_str,
                end_str,
                top_n
            )
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("データがありません")
    
    with tab4:
        st.subheader("詳細分析")
        
        if lottery_type in ["ナンバーズ3", "ナンバーズ4"]:
            st.info("ナンバーズの詳細分析機能は開発中です")
        else:
            type_map = {
                "ロト6": "loto6",
                "ロト7": "loto7",
                "ミニロト": "miniloto"
            }
            
            hot_numbers = st.session_state.analyzer.get_hot_numbers(
                type_map[lottery_type], 10, start_str, end_str
            )
            cold_numbers = st.session_state.analyzer.get_cold_numbers(
                type_map[lottery_type], 10, start_str, end_str
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**出現頻度が高い数字（上位10個）**")
                if hot_numbers:
                    st.write(sorted(hot_numbers))
                else:
                    st.warning("データがありません")
            
            with col2:
                st.write("**出現頻度が低い数字（下位10個）**")
                if cold_numbers:
                    st.write(sorted(cold_numbers))
                else:
                    st.warning("データがありません")


def show_statistics():
    """統計情報ページ"""
    st.header("📈 統計情報")
    
    tables = {
        "ナンバーズ3": "numbers3",
        "ナンバーズ4": "numbers",
        "ロト6": "loto6",
        "ロト7": "loto7",
        "ミニロト": "miniloto"
    }
    
    for name, table in tables.items():
        st.subheader(name)
        stats = st.session_state.db_manager.get_statistics(table)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総レコード数", f"{stats['count']:,}件")
        with col2:
            st.metric("最古のデータ", stats['min_date'] or "なし")
        with col3:
            st.metric("最新のデータ", stats['max_date'] or "なし")
        
        st.markdown("---")


def show_data_search():
    """データ検索ページ"""
    st.header("🔍 データ検索")
    
    lottery_type = st.selectbox(
        "宝くじタイプを選択",
        ["ナンバーズ3", "ナンバーズ4", "ロト6", "ロト7", "ミニロト"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日", value=None, key="search_start")
    with col2:
        end_date = st.date_input("終了日", value=None, key="search_end")
    
    start_str = str(start_date) if start_date else None
    end_str = str(end_date) if end_date else None
    
    if st.button("検索"):
        if lottery_type == "ナンバーズ4":
            df = st.session_state.db_manager.get_numbers_data(start_str, end_str)
        elif lottery_type == "ナンバーズ3":
            df = st.session_state.db_manager.get_numbers3_data(start_str, end_str)
        elif lottery_type == "ロト6":
            df = st.session_state.db_manager.get_loto6_data(start_str, end_str)
            # JSON形式のnumbersを展開
            if not df.empty and 'numbers' in df.columns:
                df['numbers'] = df['numbers'].apply(lambda x: json.loads(x))
        elif lottery_type == "ロト7":
            df = st.session_state.db_manager.get_loto7_data(start_str, end_str)
            if not df.empty and 'numbers' in df.columns:
                df['numbers'] = df['numbers'].apply(lambda x: json.loads(x))
        elif lottery_type == "ミニロト":
            df = st.session_state.db_manager.get_miniloto_data(start_str, end_str)
            if not df.empty and 'numbers' in df.columns:
                df['numbers'] = df['numbers'].apply(lambda x: json.loads(x))
        
        if not df.empty:
            st.write(f"**検索結果: {len(df)}件**")
            st.dataframe(df, use_container_width=True)
            
            # CSVダウンロード
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="CSVとしてダウンロード",
                data=csv,
                file_name=f"{lottery_type}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("該当するデータがありません")


if __name__ == "__main__":
    main()

