import streamlit as st
from modules.DB import SupabaseDB
import FinanceDataReader as fdr
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np    

def collect_backtest_stock_data():
    """보유 종목의 과거 데이터를 수집하여 backtest_stocks 테이블에 저장"""
    username = st.session_state.get("id")
    if not username:
        return "로그인된 사용자 ID가 없습니다."

    supabase = SupabaseDB()
    user_info = supabase.get_user(username)
    if not user_info or "id" not in user_info[0]:
        return "Supabase에서 사용자 정보를 찾을 수 없습니다."

    user_id = user_info[0]["id"]
    stocks = supabase.get_stock_data(user_id)

    if not stocks:
        return "현재 보유 중인 주식이 없습니다."

    success_count, error_count = 0, 0

    for stock in stocks:
        try:
            code = str(stock.get("상품번호")).zfill(6)
            name = stock.get("상품명", f"종목코드 {code}")

            # ────────────────────────────────────────────────
            # 1) 주가 데이터 수집
            df = fdr.DataReader(code).sort_index()

            # 2) NaN / ±Inf 값을 None 으로 변환 → JSON 직렬화 안전
            df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
            # ────────────────────────────────────────────────

            # 3) dict 변환 & 날짜를 문자열로
            daily_data = {
                d.strftime("%Y-%m-%d"): v
                for d, v in df.to_dict("index").items()
            }

            stock_data = {
                "daily_data": daily_data,
                "current_holdings": {
                    "보유수량": stock.get("보유수량"),
                    "매입금액": stock.get("매입금액"),
                    "현재가":  stock.get("현재가")
                },
                "last_updated": datetime.now().isoformat()
            }

            # 4) 업서트 – 단일 레코드도 리스트로 감싸기
            supabase.client.table("backtest_stocks").upsert([{
                "id":         user_id,
                "stock_code": code,
                "stock_name": name,
                "data":       stock_data
            }]).execute()

            success_count += 1
            st.success(f"✅ {name}({code}) 데이터 저장 완료")

        except Exception as e:
            error_count += 1
            st.error(f"⚠️ {code} 데이터 수집/저장 오류: {e}")

    return f"백테스팅용 주식 데이터 수집 완료 (성공: {success_count}개, 실패: {error_count}개)"

def get_backtest_data(username, stock_code=None):
    """저장된 백테스팅 데이터를 가져옴"""
    supabase = SupabaseDB()
    
    # 먼저 username으로 user_id(UUID) 가져오기
    user_info = supabase.get_user(username)
    if not user_info or "id" not in user_info[0]:
        return []
    
    user_id = user_info[0]["id"]
    
    if stock_code:
        response = supabase.client.table("backtest_stocks").select("*").eq("id", user_id).eq("stock_code", stock_code).execute()
    else:
        response = supabase.client.table("backtest_stocks").select("*").eq("id", user_id).execute()
    
    return response.data

def convert_to_dataframe(stock_data):
    """JSON 형태의 데이터를 DataFrame으로 변환"""
    daily_data = stock_data['data']['daily_data']
    df = pd.DataFrame.from_dict(daily_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df

def calculate_bollinger_bands(df, window=20, num_std=2):
    """볼린저 밴드 계산"""
    df['MA20'] = df['Close'].rolling(window=window).mean()
    df['std'] = df['Close'].rolling(window=window).std()
    df['Upper'] = df['MA20'] + (df['std'] * num_std)
    df['Lower'] = df['MA20'] - (df['std'] * num_std)
    return df

def calculate_strategy_performance(df, strategy='ma_crossover', initial_capital=10000000):
    """선택된 전략의 성과 계산"""
    if strategy == 'ma_crossover':
        # 기존 이동평균선 전략
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        
        # 매매 신호 생성
        df['Signal'] = 0
        df.loc[df['MA20'] > df['MA60'], 'Signal'] = 1  # 골든 크로스: 매수
        df.loc[df['MA20'] < df['MA60'], 'Signal'] = -1  # 데드 크로스: 매도
    
    elif strategy == 'bollinger_bands':
        # 볼린저 밴드 전략
        df = calculate_bollinger_bands(df)
        
        # 매매 신호 생성
        df['Signal'] = 0
        df.loc[df['Close'] < df['Lower'], 'Signal'] = 1  # 하단밴드 터치: 매수
        df.loc[df['Close'] > df['Upper'], 'Signal'] = -1  # 상단밴드 터치: 매도
    
    # 포지션 변화 감지
    df['Position_Change'] = df['Signal'].diff()
    
    # 거래 기록 생성 및 수익률 계산
    trades = []
    current_position = None
    buy_price = None
    
    for date, row in df[df['Position_Change'] != 0].iterrows():
        if row['Position_Change'] > 0:  # 매수 신호
            if current_position is None:  # 포지션이 없을 때만 매수
                current_position = 'buy'
                buy_price = row['Close']
                trades.append({
                    'date': date,
                    'type': '매수',
                    'price': buy_price,
                    'return': None  # 매수 시점에는 수익률 없음
                })
        elif row['Position_Change'] < 0:  # 매도 신호
            if current_position == 'buy':  # 매수 포지션이 있을 때만 매도
                current_position = None
                sell_price = row['Close']
                trade_return = (sell_price - buy_price) / buy_price  # 실제 수익률 계산
                trades.append({
                    'date': date,
                    'type': '매도',
                    'price': sell_price,
                    'return': trade_return
                })
    
    # 누적 수익률 계산
    cumulative_return = 1.0
    for trade in trades:
        if trade['type'] == '매도' and trade['return'] is not None:
            cumulative_return *= (1 + trade['return'])
    
    # 포트폴리오 가치 계산
    df['Market_Value'] = initial_capital * (1 + df['Close'].pct_change()).cumprod()
    df['Strategy_Value'] = initial_capital * cumulative_return
    
    return df, trades

def plot_price_chart(df, stock_name):
    """기본 주가 차트"""
    fig = go.Figure()
    
    # 캔들스틱 차트 - 단위를 만원으로 변환
    df_manwon = df.copy()
    for col in ['Open', 'High', 'Low', 'Close']:
        df_manwon[col] = df_manwon[col] / 10000

    fig.add_trace(go.Candlestick(
        x=df_manwon.index,
        open=df_manwon['Open'],
        high=df_manwon['High'],
        low=df_manwon['Low'],
        close=df_manwon['Close'],
        name='주가'
    ))
    
    # 차트 레이아웃 설정
    fig.update_layout(
        title=f"{stock_name} 주가 차트",
        yaxis_title="주가 (만원)",
        xaxis_title="날짜",
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def plot_volume_chart(df, stock_name):
    """거래량 차트"""
    fig = go.Figure()
    
    # 거래량 바 차트
    colors = ['red' if row['Close'] < row['Open'] else 'green' for _, row in df.iterrows()]
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='거래량',
        marker_color=colors,
        marker_line_width=0,
        opacity=0.7
    ))
    
    # 차트 레이아웃 설정
    fig.update_layout(
        title=f"{stock_name} 거래량",
        yaxis_title="거래량",
        xaxis_title="날짜",
        height=500,
        showlegend=False,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def plot_moving_averages(df, stock_name):
    """이동평균선 차트"""
    fig = go.Figure()
    
    # 모든 가격 데이터를 만원 단위로 변환
    df_manwon = df.copy()
    for col in ['Close', 'MA20', 'MA60']:
        df_manwon[col] = df_manwon[col] / 10000
    
    # 종가 라인
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['Close'],
        name='종가',
        line=dict(color='black', width=1)
    ))
    
    # 이동평균선
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['MA20'],
        name='20일 이동평균',
        line=dict(color='orange', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['MA60'],
        name='60일 이동평균',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title=f"{stock_name} 이동평균선",
        yaxis_title="주가 (만원)",
        xaxis_title="날짜",
        height=500
    )
    
    return fig

def plot_trading_signals(df, trades, stock_name):
    """매매 신호 차트"""
    fig = go.Figure()
    
    # 가격을 만원 단위로 변환
    df_manwon = df.copy()
    df_manwon['Close'] = df_manwon['Close'] / 10000
    
    # 종가 라인
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['Close'],
        name='종가',
        line=dict(color='black', width=1)
    ))
    
    # 매수/매도 포인트 (가격을 만원 단위로 변환)
    buy_points = [{'date': t['date'], 'price': t['price']/10000} for t in trades if t['type'] == '매수']
    sell_points = [{'date': t['date'], 'price': t['price']/10000} for t in trades if t['type'] == '매도']
    
    if buy_points:
        fig.add_trace(go.Scatter(
            x=[t['date'] for t in buy_points],
            y=[t['price'] for t in buy_points],
            mode='markers',
            name='매수 신호',
            marker=dict(color='red', size=10, symbol='triangle-up')
        ))
    
    if sell_points:
        fig.add_trace(go.Scatter(
            x=[t['date'] for t in sell_points],
            y=[t['price'] for t in sell_points],
            mode='markers',
            name='매도 신호',
            marker=dict(color='blue', size=10, symbol='triangle-down')
        ))
    
    fig.update_layout(
        title=f"{stock_name} 매매 신호",
        yaxis_title="주가 (만원)",
        xaxis_title="날짜",
        height=500
    )
    
    return fig

def plot_performance_comparison(df, stock_name):
    """수익률 비교 차트"""
    fig = go.Figure()
    
    # 포트폴리오 가치를 만원 단위로 변환
    df_manwon = df.copy()
    df_manwon['Market_Value'] = df_manwon['Market_Value'] / 10000
    df_manwon['Strategy_Value'] = df_manwon['Strategy_Value'] / 10000
    
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['Market_Value'],
        name='Buy & Hold',
        line=dict(color='gray', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['Strategy_Value'],
        name='전략 수익률',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title=f"{stock_name} 수익률 비교",
        yaxis_title="포트폴리오 가치 (만원)",
        xaxis_title="날짜",
        height=500
    )
    
    return fig

def plot_bollinger_bands(df, stock_name):
    """볼린저 밴드 차트"""
    fig = go.Figure()
    
    # 가격을 만원 단위로 변환
    df_manwon = df.copy()
    for col in ['Close', 'MA20', 'Upper', 'Lower']:
        df_manwon[col] = df_manwon[col] / 10000
    
    # 종가 라인
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['Close'],
        name='종가',
        line=dict(color='black', width=1)
    ))
    
    # 이동평균선
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['MA20'],
        name='20일 이동평균',
        line=dict(color='blue', width=2)
    ))
    
    # 상단 밴드
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['Upper'],
        name='상단 밴드',
        line=dict(color='red', width=1, dash='dash')
    ))
    
    # 하단 밴드
    fig.add_trace(go.Scatter(
        x=df_manwon.index,
        y=df_manwon['Lower'],
        name='하단 밴드',
        line=dict(color='green', width=1, dash='dash')
    ))
    
    fig.update_layout(
        title=f"{stock_name} 볼린저 밴드",
        yaxis_title="주가 (만원)",
        xaxis_title="날짜",
        height=500
    )
    
    return fig

def get_period_data(df, months):
    """선택된 기간에 따라 데이터 필터링"""
    if months == 1:
        trading_days = 21
    elif months == 3:
        trading_days = 63
    elif months == 6:
        trading_days = 126
    elif months == 9:
        trading_days = 189
    else:  # 1년
        trading_days = 252
        
    return df.tail(trading_days)

def main(strategy="이동평균선 교차"):
    
    if "id" not in st.session_state:
        st.warning("로그인이 필요합니다.")
        return

    # 저장된 종목 데이터 불러오기
    stocks_data = get_backtest_data(st.session_state["id"])

    # 설정 섹션을 expander로 구성
    with st.expander("⚙️ 백테스팅 설정", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 종목 선택 방식 선택
            selection_method = st.radio(
                "🔍 종목 선택 방식",
                ["보유 종목", "직접 검색"],
                horizontal=True
            )
            
            if selection_method == "보유 종목":
                # 기존 보유 종목 선택
                stock_options = {f"{data['stock_name']} ({data['stock_code']})": data['stock_code'] 
                                for data in stocks_data}
                selected_stock = st.selectbox("📌 분석할 종목", options=list(stock_options.keys()))
                stock_code = stock_options[selected_stock]
            else:
                # 직접 검색
                search_code = st.text_input("🔍 종목 코드 입력 (예: 005930)", 
                                          help="검색하고 싶은 주식의 종목 코드를 입력하세요.")
                if search_code:
                    try:
                        # 종목 코드 형식 맞추기 (6자리)
                        search_code = search_code.zfill(6)
                        
                        # FinanceDataReader를 사용하여 종목명 가져오기
                        df = fdr.DataReader(search_code)
                        if not df.empty:
                            # KRX 종목 목록에서 종목명 찾기
                            krx_list = fdr.StockListing('KRX')
                            stock_info = krx_list[krx_list['Code'] == search_code]
                            
                            if not stock_info.empty:
                                stock_name = stock_info.iloc[0]['Name']
                                stock_code = search_code
                                selected_stock = f"{stock_name} ({stock_code})"
                                st.success(f"✅ {stock_name} 종목을 찾았습니다.")
                            else:
                                st.error("❌ 해당 종목 코드의 정보를 찾을 수 없습니다.")
                                return
                        else:
                            st.error("❌ 해당 종목 코드의 데이터를 찾을 수 없습니다.")
                            return
                    except Exception as e:
                        st.error(f"❌ 종목 검색 중 오류가 발생했습니다: {str(e)}")
                        return
            
            # 기간 선택
            period_options = {
                "1개월": 1,
                "3개월": 3,
                "6개월": 6,
                "9개월": 9,
                "1년": 12
            }
            col_period, col_capital = st.columns(2)
            with col_period:
                selected_period = st.selectbox(
                    "📅 백테스팅 기간",
                    options=list(period_options.keys()),
                    index=4  # 기본값 1년
                )
            
            # 초기 자본금 설정
            with col_capital:
                initial_capital = st.number_input("💰 초기 자본금 (만원)", 
                                               min_value=100, 
                                               value=1000, 
                                               step=100,
                                               format="%d") * 10000
        
        with col2:
            st.write("")
            st.write("")
            # 데이터 수집 버튼
            if st.button("🔄 데이터 새로고침", use_container_width=True):
                with st.spinner("보유 종목 데이터를 수집하는 중... ⏳"):
                    result = collect_backtest_stock_data()
                    st.success(result)
                    st.session_state["backtest_data_loaded"] = True
            
            st.write("")
            # 실행 버튼
            run_backtest = st.button("🚀 백테스팅 실행", type="primary", use_container_width=True)
            
            if run_backtest:
                with st.spinner("백테스팅 분석 중..."):
                    # 세션 상태에 백테스팅 결과 저장
                    if selection_method == "보유 종목":
                        stock_data = get_backtest_data(st.session_state["id"], stock_code)[0]
                        df = convert_to_dataframe(stock_data)
                    else:
                        # 직접 검색한 종목의 경우 FinanceDataReader로 데이터 가져오기
                        df = fdr.DataReader(stock_code)
                        df = df.sort_index()
                        # NaN / ±Inf 값을 None으로 변환
                        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
                        
                        # stock_data 형식 맞추기
                        stock_data = {
                            'stock_code': stock_code,
                            'stock_name': selected_stock.split(' (')[0]
                        }
                    
                    df = get_period_data(df, period_options[selected_period])
                    
                    # 전략 선택에 따라 다른 전략 적용
                    strategy_key = 'ma_crossover' if strategy == "이동평균선 교차" else 'bollinger_bands'
                    df, trades = calculate_strategy_performance(df, strategy=strategy_key, initial_capital=initial_capital)
                    
                    st.session_state['backtest_results'] = {
                        'df': df,
                        'trades': trades,
                        'stock_data': stock_data,
                        'initial_capital': initial_capital,
                        'selected_period': selected_period,
                        'strategy': strategy
                    }
                    st.success("백테스팅이 완료되었습니다! ✨")

    # 구분선 추가
    st.divider()

    # 결과 표시
    if 'backtest_results' in st.session_state:
        results = st.session_state['backtest_results']
        df = results['df']
        trades = results['trades']
        stock_data = results['stock_data']
        initial_capital = results['initial_capital']
        selected_period = results['selected_period']
        strategy = results['strategy']
        
        # 분석 기간 정보
        period_col1, period_col2 = st.columns(2)
        with period_col1:
            st.info(f"📅 분석 시작일: {df.index[0].strftime('%Y-%m-%d')}")
        with period_col2:
            st.info(f"📅 분석 종료일: {df.index[-1].strftime('%Y-%m-%d')}")
        
        # 성과 지표 계산
        total_trades = len(trades)
        final_market_return = (df['Market_Value'].iloc[-1] / initial_capital - 1) * 100
        final_strategy_return = (df['Strategy_Value'].iloc[-1] / initial_capital - 1) * 100
        
        # 성과 지표 표시
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("총 거래 횟수", f"{total_trades}회")
            st.caption("💡 매수/매도 신호가 발생한 총 횟수")
        with metric_col2:
            st.metric("Buy & Hold 수익률", f"{final_market_return:.2f}%")
            st.caption(f"💡 {df.index[0].strftime('%Y-%m-%d')}에 매수 후 {df.index[-1].strftime('%Y-%m-%d')}까지 보유했을 때의 수익률")
        with metric_col3:
            st.metric("전략 수익률", f"{final_strategy_return:.2f}%")
            st.caption(f"💡 {strategy} 전략을 적용했을 때의 수익률")
        
        # 수익률 비교 설명
        with st.expander("📈 수익률 비교 설명"):
            st.info(f"""
            **{selected_period} 기준 백테스팅 결과**
            - **Buy & Hold**: 시작일({df.index[0].strftime('%Y-%m-%d')})에 매수하고 종료일({df.index[-1].strftime('%Y-%m-%d')})까지 보유하는 단순 전략
            - **{strategy} 전략**: {strategy} 전략을 적용한 수익률
            
            두 수익률을 비교하면 {strategy} 전략의 효과를 확인할 수 있습니다.
            전략 수익률이 더 높다면 {strategy} 전략이 단순 보유보다 효과적이었다는 의미입니다.
            """)
        
        # 탭으로 차트 구분
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 기본 주가 차트",
            "📈 거래량",
            "〽️ 이동평균선",
            "🎯 매매 신호",
            "💰 수익률 비교",
            "📝 매매 시뮬레이션"
        ])
        
        with tab1:
            st.plotly_chart(plot_price_chart(df, stock_data['stock_name']), use_container_width=True)
        
        with tab2:
            st.plotly_chart(plot_volume_chart(df, stock_data['stock_name']), use_container_width=True)
        
        with tab3:
            if strategy == "이동평균선 교차":
                st.plotly_chart(plot_moving_averages(df, stock_data['stock_name']), use_container_width=True)
            else:
                st.plotly_chart(plot_bollinger_bands(df, stock_data['stock_name']), use_container_width=True)
        
        with tab4:
            st.plotly_chart(plot_trading_signals(df, trades, stock_data['stock_name']), use_container_width=True)
        
        with tab5:
            st.plotly_chart(plot_performance_comparison(df, stock_data['stock_name']), use_container_width=True)
        
        with tab6:
            st.subheader(f"📊 {strategy} 전략 시뮬레이션 결과")
            if strategy == "이동평균선 교차":
                st.caption("MA20이 MA60을 상향돌파할 때 매수, 하향돌파할 때 매도하는 전략을 적용했을 경우의 시뮬레이션 결과입니다.")
            else:
                st.caption("주가가 하단밴드를 터치할 때 매수, 상단밴드를 터치할 때 매도하는 전략을 적용했을 경우의 시뮬레이션 결과입니다.")
            
            trades_df = pd.DataFrame(trades)
            if not trades_df.empty:
                trades_df['date'] = trades_df['date'].dt.strftime('%Y-%m-%d')
                trades_df.columns = ['거래일자', '매매구분', '거래가격', '수익률']
                trades_df['거래가격'] = (trades_df['거래가격'] / 10000).round(2)
                trades_df['수익률'] = trades_df['수익률'].apply(lambda x: f"{x*100:.2f}%" if pd.notnull(x) else "-")
                
                # 매매 구분에 따라 색상 적용
                def highlight_trades(row):
                    if row['매매구분'] == '매수':
                        return ['background-color: #e8f5e9'] * len(row)
                    else:
                        return ['background-color: #ffebee'] * len(row)
                
                # 스타일이 적용된 데이터프레임 표시
                st.dataframe(
                    trades_df.style
                    .apply(highlight_trades, axis=1)
                    .format({'거래가격': '{:,.2f} 만원'})
                    .set_properties(**{
                        'text-align': 'center',
                        'font-size': '14px',
                        'padding': '12px',
                        'border': '1px solid #e0e0e0'
                    })
                    .set_table_styles([
                        {'selector': 'th',
                         'props': [('background-color', '#f5f5f5'),
                                 ('color', '#424242'),
                                 ('font-weight', 'bold'),
                                 ('text-align', 'center'),
                                 ('padding', '12px'),
                                 ('border', '1px solid #e0e0e0'),
                                 ('font-size', '15px')]},
                        {'selector': 'td',
                         'props': [('padding', '12px'),
                                 ('border', '1px solid #e0e0e0')]},
                        {'selector': 'tr:hover',
                         'props': [('background-color', '#fafafa')]}
                    ]),
                    height=400
                )
                
                # 거래 통계 표시
                col1, col2, col3 = st.columns(3)
                with col1:
                    buy_count = len(trades_df[trades_df['매매구분'] == '매수'])
                    st.metric("총 매수 횟수", f"{buy_count}회")
                with col2:
                    sell_count = len(trades_df[trades_df['매매구분'] == '매도'])
                    st.metric("총 매도 횟수", f"{sell_count}회")
                with col3:
                    avg_price = trades_df['거래가격'].mean()
                    st.metric("평균 거래가격", f"{avg_price:,.2f} 만원")
    elif not stocks_data:
        st.info("🔄 백테스팅을 시작하려면 상단의 '데이터 새로고침' 버튼을 클릭하여 주식 데이터를 먼저 수집해주세요.")
    else:
        st.info("⚙️ 상단의 설정에서 백테스팅 옵션을 선택하고 실행해주세요.") 