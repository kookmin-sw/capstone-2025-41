import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import os
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 데이터 저장 경로
ETF_DATA_FILE = "data/etf_data.json"

# ETF 리스트 (KODEX 미국 S&P500 섹터별 ETF 종목코드 사용)
ETF_LIST = {
    'Kodex 미국S&P500산업재(합성)': '200030',
    'Kodex 미국S&P500커뮤니케이션': '379810',
    'Kodex 미국S&P500유틸리티': '379800'
}

class ETFAnalyzer:
    @staticmethod
    def save_etf_data():
        """ ETF 데이터 수집 및 저장 (모든 데이터 저장) """
        etf_data = {}
        for name, code in ETF_LIST.items():
            df = fdr.DataReader(code)
            # 🔥 Timestamp → 문자열 변환 (시간 제거)
            etf_data[name] = {str(date.date()): float(price) for date, price in df['Close'].items()} 
        
        with open(ETF_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(etf_data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_etf_data():
        """ 저장된 ETF 데이터 로드 """
        if os.path.exists(ETF_DATA_FILE):
            with open(ETF_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def visualize_etf():
        """ ETF 데이터 시각화 (최근 1년 데이터만 표시, 실시간 갱신) """
        placeholder = st.empty()  # 🔥 그래프를 실시간으로 갱신할 공간 생성

        while True:  # 🔥 무한 루프 실행 (Streamlit에서 자동으로 새로고침됨)
            etf_data = ETFAnalyzer.load_etf_data()
            
            if not etf_data:
                st.warning("ETF 데이터가 없습니다. 먼저 데이터를 수집해주세요!")
                return

            # 🔥 최근 1년(12개월) 데이터만 필터링
            one_year_ago = datetime.now() - timedelta(days=365)

            fig = go.Figure()
            for name, prices in etf_data.items():
                # 🔥 날짜 변환 시 시간 제거 (split 사용)
                dates = [datetime.strptime(date.split(" ")[0], "%Y-%m-%d") for date in prices.keys()]
                closes = list(prices.values())

                # 🔥 1년치 데이터만 필터링
                recent_dates = [date for date in dates if date >= one_year_ago]
                recent_closes = [closes[i] for i in range(len(dates)) if dates[i] >= one_year_ago]

                fig.add_trace(go.Scatter(x=recent_dates, y=recent_closes, mode='lines', name=name))

            fig.update_layout(title="ETF 종가 추이 (최근 1년, 실시간 갱신)", xaxis_title="날짜", yaxis_title="종가 (KRW)")

            placeholder.plotly_chart(fig)  # 🔥 그래프를 업데이트 (덮어쓰기)

            time.sleep(60)
