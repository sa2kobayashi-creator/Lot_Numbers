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
import os


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
    
    # セッション状態の初期化（設定）
    if 'prediction_settings' not in st.session_state:
        st.session_state.prediction_settings = load_settings()
    
    # サイドバー
    with st.sidebar:
        st.header("📊 メニュー")
        page = st.radio(
            "ページを選択",
            ["🏠 ホーム", "📥 データ登録", "📊 データ分析", "📈 統計情報", "🔍 データ検索", "⚙️ 設定"]
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
    elif page == "⚙️ 設定":
        show_settings()


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
        
        # loto-life.netのURLを自動設定
        url_map = {
            "ナンバーズ3": "https://loto-life.net/numbers3/past",
            "ナンバーズ4": "https://loto-life.net/numbers4/past",
            "ロト6": "https://loto-life.net/loto6/past",
            "ロト7": "https://loto-life.net/loto7/past",
            "ミニロト": "https://loto-life.net/mini-loto/past"
        }
        
        default_url = url_map.get(lottery_type_scrape, "")
        
        st.info(f"💡 **推奨URL**: {default_url}")
        
        url = st.text_input(
            "スクレイピング対象のURLを入力",
            value=default_url,
            key="scrape_url"
        )
        
        st.info("""
        **注意**: loto-life.netの場合は専用パーサーが使用されます。
        他のサイトの場合は汎用パーサーが使用されますが、HTML構造に合わせて
        カスタマイズが必要な場合があります。
        """)
        
        # 一括実行セクション
        st.markdown("---")
        st.subheader("一括スクレイピング")
        st.write("すべての宝くじタイプを一括でスクレイピングします。")
        
        if st.button("一括スクレイピング実行（ナンバーズ3, 4, ロト6, 7, ミニロト）", 
                     key="batch_scrape_button",
                     type="primary"):
            type_map = {
                "ナンバーズ3": "numbers3",
                "ナンバーズ4": "numbers",
                "ロト6": "loto6",
                "ロト7": "loto7",
                "ミニロト": "miniloto"
            }
            
            url_map = {
                "ナンバーズ3": "https://loto-life.net/numbers3/past",
                "ナンバーズ4": "https://loto-life.net/numbers4/past",
                "ロト6": "https://loto-life.net/loto6/past",
                "ロト7": "https://loto-life.net/loto7/past",
                "ミニロト": "https://loto-life.net/mini-loto/past"
            }
            
            results = {}
            total_count = 0
            
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                lottery_types = ["ナンバーズ3", "ナンバーズ4", "ロト6", "ロト7", "ミニロト"]
                
                for idx, lottery_type_name in enumerate(lottery_types):
                    status_text.text(f"処理中: {lottery_type_name}...")
                    progress_bar.progress((idx + 1) / len(lottery_types))
                    
                    url = url_map[lottery_type_name]
                    lottery_type_code = type_map[lottery_type_name]
                    
                    try:
                        result = st.session_state.fetcher.scrape_from_url(
                            url, lottery_type_code
                        )
                        results[lottery_type_name] = {
                            'count': result['count'],
                            'total_found': result['total_found'],
                            'duplicated': result['duplicated'],
                            'status': result['status'],
                            'message': result['message'],
                            'url': url
                        }
                        total_count += result['count']
                    except Exception as e:
                        results[lottery_type_name] = {
                            'count': 0,
                            'status': 'error',
                            'error': str(e),
                            'url': url
                        }
                
                progress_bar.progress(1.0)
                status_text.text("完了！")
                
                # 結果表示
                st.markdown("---")
                st.subheader("一括スクレイピング結果")
                
                for lottery_type_name, result in results.items():
                    if result['status'] == 'success':
                        st.success(f"✅ **{lottery_type_name}**: {result['message']}")
                    elif result['status'] == 'duplicated':
                        st.warning(f"⚠️ **{lottery_type_name}**: **重複しています**")
                        st.info(f"   {result['message']}")
                        st.caption(f"   見つかったデータ: {result['total_found']}件（すべて重複）")
                    elif result['status'] == 'no_data':
                        st.error(f"❌ **{lottery_type_name}**: **データが見つかりませんでした**")
                        st.info(f"   {result['message']}")
                        st.caption(f"   URL: {result['url']}")
                    else:
                        st.error(f"❌ **{lottery_type_name}**: **エラーが発生しました**")
                        st.error(f"   {result.get('message', result.get('error', '不明なエラー'))}")
                
                st.info(f"**合計**: {total_count}件のデータを取得しました")
                
            except ImportError as e:
                st.error("Webスクレイピング機能を使用するには、追加のパッケージが必要です。")
                st.code("pip install beautifulsoup4 lxml", language="bash")
                st.error(str(e))
        
        st.markdown("---")
        st.subheader("個別スクレイピング")
        
        if url and st.button("スクレイピング実行", key="single_scrape_button"):
            type_map = {
                "ナンバーズ3": "numbers3",
                "ナンバーズ4": "numbers",
                "ロト6": "loto6",
                "ロト7": "loto7",
                "ミニロト": "miniloto"
            }
            
            try:
                with st.spinner("データを取得中..."):
                    result = st.session_state.fetcher.scrape_from_url(
                        url, type_map[lottery_type_scrape]
                    )
                
                if result['status'] == 'success':
                    st.success(result['message'])
                elif result['status'] == 'duplicated':
                    st.warning("⚠️ **重複しています**")
                    st.info(result['message'])
                elif result['status'] == 'no_data':
                    st.error("❌ **データが見つかりませんでした**")
                    st.info(result['message'])
                    st.caption("URLまたはHTML構造を確認してください。")
                else:
                    st.error(f"❌ **エラーが発生しました**")
                    st.error(result['message'])
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
        start_date = st.date_input(
            "開始日", 
            value=None, 
            min_value=date(1990, 1, 1),
            max_value=date.today(),
            key="analysis_start",
            help="指定しない場合は全期間のデータを対象にします"
        )
    with col2:
        end_date = st.date_input(
            "終了日", 
            value=None,
            min_value=date(1990, 1, 1),
            max_value=date.today(),
            key="analysis_end",
            help="指定しない場合は全期間のデータを対象にします"
        )
    
    start_str = str(start_date) if start_date else None
    end_str = str(end_date) if end_date else None
    
    # 日付範囲の表示
    if start_date or end_date:
        date_range_text = "分析対象期間: "
        if start_date and end_date:
            date_range_text += f"{start_date} ～ {end_date}"
        elif start_date:
            date_range_text += f"{start_date} ～ 最新"
        elif end_date:
            date_range_text += f"最古 ～ {end_date}"
        st.info(f"📅 {date_range_text}")
    else:
        st.info("📅 **分析対象期間: 全期間**（開始日・終了日が未指定のため、データベース内のすべてのデータを対象にします）")
    
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
            digits = 3 if lottery_type == "ナンバーズ3" else 4
            
            # 高度な推奨数字生成を使用
            use_advanced = st.checkbox(
                "高度な分析を使用（設定で選択した要素を考慮）",
                value=False,
                key="use_advanced_prediction"
            )
            
            if use_advanced:
                recommended_list = st.session_state.analyzer.get_recommended_numbers_numbers_advanced(
                    digits, strategy, st.session_state.prediction_settings,
                    start_str, end_str, top_n=5
                )
            else:
                recommended_list = st.session_state.analyzer.get_recommended_numbers_numbers(
                    digits, strategy, start_str, end_str, top_n=5
                )
            
            if recommended_list:
                st.write("**推奨数字（ランキング）:**")
                for rank, number in enumerate(recommended_list, 1):
                    st.write(f"{rank}位: **{number}**")
                st.write(f"**数字の桁数:** {digits}桁")
                if use_advanced:
                    st.info("💡 高度な分析を使用しています。設定ページで使用する要素を変更できます。")
            else:
                st.warning("データが不足しています")
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
            
            # 高度な推奨数字生成を使用
            use_advanced = st.checkbox(
                "高度な分析を使用（設定で選択した要素を考慮）",
                value=False,
                key="use_advanced_prediction_loto"
            )
            
            if use_advanced:
                with st.spinner("高度な分析を実行中...（数秒かかる場合があります）"):
                    recommended_patterns = st.session_state.analyzer.get_recommended_numbers_multiple_advanced(
                        type_map[lottery_type],
                        strategy,
                        count_map[lottery_type],
                        st.session_state.prediction_settings,
                        top_n=5,
                        start_date=start_str,
                        end_date=end_str
                    )
            else:
                recommended_patterns = st.session_state.analyzer.get_recommended_numbers_multiple(
                    type_map[lottery_type],
                    strategy,
                    count_map[lottery_type],
                    top_n=5,
                    start_date=start_str,
                    end_date=end_str
                )
            
            if recommended_patterns:
                st.write("**推奨数字（ランキング）:**")
                for rank, pattern in enumerate(recommended_patterns, 1):
                    st.write(f"{rank}位: **{sorted(pattern)}**")
                st.write(f"**1パターンあたりの数字の数:** {count_map[lottery_type]}")
                if use_advanced:
                    st.info("💡 高度な分析を使用しています。設定ページで使用する要素を変更できます。")
            else:
                st.warning("データが不足しています")
    
    with tab3:
        st.subheader("数字ペア分析")
        top_n = st.slider("表示する上位ペア数", 10, 50, 20)
        
        if lottery_type in ["ナンバーズ3", "ナンバーズ4"]:
            digits = 3 if lottery_type == "ナンバーズ3" else 4
            df = st.session_state.analyzer.analyze_numbers_pairs(
                digits, start_str, end_str, top_n
            )
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("データがありません")
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
            digits = 3 if lottery_type == "ナンバーズ3" else 4
            
            # 詳細分析
            detailed = st.session_state.analyzer.get_numbers_detailed_analysis(
                digits, start_str, end_str
            )
            
            if detailed:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**各桁の出現頻度が高い数字（上位5個）**")
                    for digit, numbers in detailed.get('hot_digits', {}).items():
                        st.write(f"{digit}: {numbers}")
                
                with col2:
                    st.write("**各桁の出現頻度が低い数字（下位5個）**")
                    for digit, numbers in detailed.get('cold_digits', {}).items():
                        st.write(f"{digit}: {numbers}")
            
            # 追加分析
            st.markdown("---")
            st.subheader("追加分析")
            
            analysis_tabs = st.tabs([
                "合計値", "奇偶比率", "大小比率", "連番", "重複", 
                "前回差", "リピート率", "ミラー数字", "デジタルルート",
                "トレンド", "EMA", "ランレングス", "マルコフ連鎖"
            ])
            
            with analysis_tabs[0]:  # 合計値
                sum_df = st.session_state.analyzer.analyze_numbers_sum(digits, start_str, end_str)
                if not sum_df.empty:
                    st.dataframe(sum_df, use_container_width=True)
                    st.bar_chart(sum_df.set_index('合計値'))
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[1]:  # 奇偶比率
                odd_even = st.session_state.analyzer.analyze_numbers_odd_even_ratio(digits, start_str, end_str)
                if odd_even:
                    st.write(f"**平均奇数個数:** {odd_even.get('平均奇数個数', 0):.2f}")
                    st.write(f"**平均偶数個数:** {odd_even.get('平均偶数個数', 0):.2f}")
                    if 'パターン分布' in odd_even:
                        st.dataframe(odd_even['パターン分布'], use_container_width=True)
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[2]:  # 大小比率
                high_low = st.session_state.analyzer.analyze_numbers_high_low_ratio(digits, start_str, end_str)
                if high_low:
                    st.write(f"**平均高数字個数:** {high_low.get('平均高数字個数', 0):.2f}")
                    st.write(f"**平均低数字個数:** {high_low.get('平均低数字個数', 0):.2f}")
                    if 'パターン分布' in high_low:
                        st.dataframe(high_low['パターン分布'], use_container_width=True)
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[3]:  # 連番
                consecutive_df = st.session_state.analyzer.analyze_numbers_consecutive(digits, start_str, end_str)
                if not consecutive_df.empty:
                    st.dataframe(consecutive_df, use_container_width=True)
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[4]:  # 重複
                duplicates = st.session_state.analyzer.analyze_numbers_duplicates(digits, start_str, end_str)
                if duplicates:
                    for key, value in duplicates.items():
                        st.write(f"**{key}:** {value['回数']}回 ({value['割合']:.2f}%)")
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[5]:  # 前回差
                diff_df = st.session_state.analyzer.analyze_numbers_previous_difference(digits, start_str, end_str)
                if not diff_df.empty:
                    st.dataframe(diff_df, use_container_width=True)
                    st.bar_chart(diff_df.set_index('差'))
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[6]:  # リピート率
                repeat = st.session_state.analyzer.analyze_numbers_repeat_rate(digits, start_str, end_str)
                if repeat:
                    for key, value in repeat.items():
                        st.write(f"**{key}:** {value:.2f}")
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[7]:  # ミラー数字
                mirror_df = st.session_state.analyzer.analyze_numbers_mirror(digits, start_str, end_str)
                if not mirror_df.empty:
                    st.dataframe(mirror_df, use_container_width=True)
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[8]:  # デジタルルート
                root_df = st.session_state.analyzer.analyze_numbers_digital_root(digits, start_str, end_str)
                if not root_df.empty:
                    st.dataframe(root_df, use_container_width=True)
                    st.bar_chart(root_df.set_index('デジタルルート'))
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[9]:  # トレンド
                trend_df = st.session_state.analyzer.analyze_numbers_trend(digits, periods=10, start_date=start_str, end_date=end_str)
                if not trend_df.empty:
                    st.dataframe(trend_df, use_container_width=True)
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[10]:  # EMA
                ema_df = st.session_state.analyzer.analyze_numbers_ema(digits, span=10, start_date=start_str, end_date=end_str)
                if not ema_df.empty:
                    st.dataframe(ema_df, use_container_width=True)
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[11]:  # ランレングス
                runlength = st.session_state.analyzer.analyze_numbers_runlength(digits, start_str, end_str)
                if runlength:
                    for key, value in runlength.items():
                        st.write(f"**{key}**")
                        st.write(f"- 平均ランレングス: {value['平均ランレングス']:.2f}")
                        st.write(f"- 最大ランレングス: {value['最大ランレングス']}")
                        st.write(f"- 分布: {dict(value['ランレングス分布'])}")
                else:
                    st.warning("データがありません")
            
            with analysis_tabs[12]:  # マルコフ連鎖
                markov = st.session_state.analyzer.analyze_numbers_markov(digits, start_str, end_str)
                if markov:
                    for key, matrix in markov.items():
                        st.write(f"**{key}の遷移確率行列**")
                        st.dataframe(matrix, use_container_width=True)
                else:
                    st.warning("データがありません")
            
            # 日付との関係性分析
            st.markdown("---")
            st.subheader("日付との関係性分析")
            
            date_analysis = st.session_state.analyzer.analyze_date_relationship_numbers(
                digits, start_str, end_str
            )
            
            if date_analysis:
                # 曜日別
                if 'weekday' in date_analysis:
                    st.write("**曜日別の抽選回数**")
                    st.dataframe(date_analysis['weekday'], use_container_width=True)
                    st.bar_chart(date_analysis['weekday'].set_index('曜日'))
                
                # 月別
                if 'month' in date_analysis:
                    st.write("**月別の抽選回数**")
                    st.dataframe(date_analysis['month'], use_container_width=True)
                    st.bar_chart(date_analysis['month'].set_index('月'))
                
                # 日付別
                if 'day' in date_analysis:
                    st.write("**日付（1-31日）別の抽選回数**")
                    st.dataframe(date_analysis['day'], use_container_width=True)
                    st.bar_chart(date_analysis['day'].set_index('日'))
                
                # 日付との相関
                if 'digit_date_correlation' in date_analysis:
                    st.write("**各桁の数字と日付（1-31日）の相関係数**")
                    st.dataframe(date_analysis['digit_date_correlation'], use_container_width=True)
                    st.info("相関係数が1に近いほど正の相関、-1に近いほど負の相関があります。")
                
                # 月初・月末
                if 'month_period' in date_analysis:
                    st.write("**月初・月末の出現傾向**")
                    st.dataframe(date_analysis['month_period'], use_container_width=True)
                    st.bar_chart(date_analysis['month_period'].set_index('期間'))
            else:
                st.warning("データがありません")
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
        start_date = st.date_input(
            "開始日", 
            value=None,
            min_value=date(1990, 1, 1),
            max_value=date.today(),
            key="search_start"
        )
    with col2:
        end_date = st.date_input(
            "終了日", 
            value=None,
            min_value=date(1990, 1, 1),
            max_value=date.today(),
            key="search_end"
        )
    
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


def load_settings():
    """設定ファイルから設定を読み込む"""
    settings_file = "prediction_settings.json"
    default_settings = {
        'use_frequency': True,
        'use_sum': False,
        'use_odd_even': False,
        'use_high_low': False,
        'use_consecutive': False,
        'use_duplicates': False,
        'use_previous_diff': False,
        'use_repeat_rate': False,
        'use_mirror': False,
        'use_digital_root': False,
        'use_trend': False,
        'use_ema': False,
        'use_runlength': False,
        'use_markov': False
    }
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # デフォルト設定とマージ（新しいキーが追加された場合に対応）
                for key in default_settings:
                    if key not in loaded_settings:
                        loaded_settings[key] = default_settings[key]
                return loaded_settings
        except (json.JSONDecodeError, IOError) as e:
            st.warning(f"設定ファイルの読み込みに失敗しました。デフォルト設定を使用します。エラー: {e}")
            return default_settings
    else:
        return default_settings


def save_settings(settings: dict):
    """設定をファイルに保存する"""
    settings_file = "prediction_settings.json"
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        st.error(f"設定ファイルの保存に失敗しました: {e}")
        return False


def show_settings():
    """設定ページ"""
    st.header("⚙️ 予測設定")
    st.markdown("予測に使用する分析要素を選択してください。")
    
    st.subheader("基本分析")
    use_frequency = st.checkbox(
        "数字の出現頻度", 
        value=st.session_state.prediction_settings['use_frequency'],
        help="各数字（0〜9）の出現頻度を考慮",
        key="setting_frequency"
    )
    
    st.subheader("統計的分析")
    col1, col2 = st.columns(2)
    
    with col1:
        use_sum = st.checkbox(
            "合計値分析", 
            value=st.session_state.prediction_settings['use_sum'],
            help="数字の合計値の傾向を考慮",
            key="setting_sum"
        )
        use_odd_even = st.checkbox(
            "奇偶比率", 
            value=st.session_state.prediction_settings['use_odd_even'],
            help="奇数と偶数の比率を考慮",
            key="setting_odd_even"
        )
        use_high_low = st.checkbox(
            "大小比率", 
            value=st.session_state.prediction_settings['use_high_low'],
            help="高数字（5-9）と低数字（0-4）の比率を考慮",
            key="setting_high_low"
        )
        use_digital_root = st.checkbox(
            "デジタルルート", 
            value=st.session_state.prediction_settings['use_digital_root'],
            help="合計値を1桁化した値の傾向を考慮",
            key="setting_digital_root"
        )
    
    with col2:
        use_consecutive = st.checkbox(
            "連番分析", 
            value=st.session_state.prediction_settings['use_consecutive'],
            help="連続する数字の出現率を考慮",
            key="setting_consecutive"
        )
        use_duplicates = st.checkbox(
            "重複数字分析", 
            value=st.session_state.prediction_settings['use_duplicates'],
            help="同一数字の複数出現（ダブル/トリプル）を考慮",
            key="setting_duplicates"
        )
        use_mirror = st.checkbox(
            "ミラー数字", 
            value=st.session_state.prediction_settings['use_mirror'],
            help="ミラー数字（0↔9, 1↔8など）の相関を考慮",
            key="setting_mirror"
        )
    
    st.subheader("時系列分析")
    col1, col2 = st.columns(2)
    
    with col1:
        use_trend = st.checkbox(
            "トレンド分析", 
            value=st.session_state.prediction_settings['use_trend'],
            help="過去n回のトレンドを考慮",
            key="setting_trend"
        )
        use_ema = st.checkbox(
            "EMA（指数移動平均）", 
            value=st.session_state.prediction_settings['use_ema'],
            help="指数移動平均からの偏差を考慮",
            key="setting_ema"
        )
        use_runlength = st.checkbox(
            "ランレングス", 
            value=st.session_state.prediction_settings['use_runlength'],
            help="連続で出る数字の長さを考慮",
            key="setting_runlength"
        )
    
    with col2:
        use_previous_diff = st.checkbox(
            "前回との差", 
            value=st.session_state.prediction_settings['use_previous_diff'],
            help="前回数字との差の傾向を考慮",
            key="setting_previous_diff"
        )
        use_repeat_rate = st.checkbox(
            "リピート率", 
            value=st.session_state.prediction_settings['use_repeat_rate'],
            help="前回・前々回からの引っ張り数字を考慮",
            key="setting_repeat_rate"
        )
        use_markov = st.checkbox(
            "マルコフ連鎖", 
            value=st.session_state.prediction_settings['use_markov'],
            help="遷移確率を考慮",
            key="setting_markov"
        )
    
    st.markdown("---")
    
    # 設定を更新
    st.session_state.prediction_settings = {
        'use_frequency': use_frequency,
        'use_sum': use_sum,
        'use_odd_even': use_odd_even,
        'use_high_low': use_high_low,
        'use_consecutive': use_consecutive,
        'use_duplicates': use_duplicates,
        'use_previous_diff': use_previous_diff,
        'use_repeat_rate': use_repeat_rate,
        'use_mirror': use_mirror,
        'use_digital_root': use_digital_root,
        'use_trend': use_trend,
        'use_ema': use_ema,
        'use_runlength': use_runlength,
        'use_markov': use_markov
    }
    
    if st.button("設定を保存", key="save_settings"):
        if save_settings(st.session_state.prediction_settings):
            st.success("✅ 設定を保存しました！再起動後も設定が保持されます。")
        else:
            st.error("❌ 設定の保存に失敗しました。")
    
    st.markdown("---")
    st.subheader("現在の設定")
    st.json(st.session_state.prediction_settings)


if __name__ == "__main__":
    main()

