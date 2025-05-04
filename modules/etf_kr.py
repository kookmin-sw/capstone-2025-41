import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import os
import FinanceDataReader as fdr
from datetime import timedelta
import datetime
from modules.DB import SupabaseDB

# ETF 리스트 (KODEX 한국 섹터별 ETF 종목코드 사용)
ETF_LIST = {
    'KODEX 은행': '091170',
    'KODEX 에너지화학': '117460',
    'KODEX IT': '266370',
    'KODEX 자동차': '091180',
    'KODEX 철강': '117680',
    'KODEX 반도체': '091160',
    'KODEX 건설': '117700',
    'KODEX 미디어통신': '266360',
    'KODEX 바이오': '244580',
    'KODEX 헬스케어': '266420'
}

# 섹터 이름 변환 (짧게 표시)
sector_short_names = {
    "KODEX 은행": "은행",
    "KODEX 에너지화학": "에너지화학",
    "KODEX IT": "IT",
    "KODEX 자동차": "자동차",
    "KODEX 철강": "철강",
    "KODEX 반도체": "반도체",
    "KODEX 건설": "건설",
    "KODEX 미디어통신": "미디어통신",
    "KODEX 바이오": "바이오",
    "KODEX 헬스케어": "헬스케어"
}

class ETFAnalyzer:
    
    def __init__(self):
        """Supabase 연결"""
        self.db = SupabaseDB()

    def save_etf_data(self):
        """ETF 데이터를 Supabase에 JSON 형태로 저장"""
        etf_data = {}

        for name, code in ETF_LIST.items():
            print(f"\n=== {name} 데이터 수집 시작 ===")
            df = fdr.DataReader(code)
            
            print(f"📌 {name}({code})에서 가져온 데이터 (상위 5개):")
            print(df.head())  # 🔍 ETF 데이터가 정상적으로 로드되는지 확인
            
            if df.empty:
                print(f"⚠️ {name}({code})의 데이터를 가져오지 못했습니다.")
                continue  # 데이터가 없으면 건너뜀

            df.index = pd.to_datetime(df.index, errors='coerce')  # 날짜 변환
            df.index = df.index.strftime('%Y-%m-%d')  # Timestamp를를 문자열 변환

            etf_data[name] = df[['Close']].to_dict(orient='index')  # JSON 저장
            print(f"✅ {name}({code}) 데이터 저장 완료. 저장된 데이터 개수: {len(etf_data[name])}")
            print(f"마지막 날짜의 종가: {list(etf_data[name].values())[-1]['Close']}")

        print("\n📌 Supabase에 저장할 데이터의 ETF 목록:", list(etf_data.keys()))
        print(f"📌 전체 ETF 개수: {len(etf_data)}")

        if not etf_data:
            print("📌 저장할 ETF 데이터가 없습니다.")
            return

        self.db.insert_etf_data_kr_json(etf_data)
        print("ETF 데이터가 Supabase에 JSON 형태로 저장되었습니다.")

    def load_etf_data(self):
        """Supabase에서 JSON 형태의 ETF 데이터를 불러옴"""
        etf_data = self.db.get_etf_data_kr_json()

        if not etf_data:
            print("📌 Supabase에 ETF 데이터가 없습니다.")
            return {}

        return etf_data

    @staticmethod
    def visualize_etf():
        """ ETF 데이터 트리맵 시각화 (섹터별 비중 유지 + 증감률 표시) """
        # UI 스타일 개선
        st.markdown("""
            <style>
                .stSelectbox, .stMultiSelect {
                    background-color: white;
                    border-radius: 5px;
                    margin-bottom: 10px;
                }
                .stRadio > label {
                    background-color: #f0f2f6;
                    padding: 10px;
                    border-radius: 5px;
                    margin-right: 10px;
                }
                div[data-testid="stDateInput"] {
                    background-color: white;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                }
            </style>
        """, unsafe_allow_html=True)

        # 컨테이너로 UI 요소 그룹화
        with st.container():
            # ETF 선택 섹션
            st.markdown("### 📈 분석할 ETF 선택")
            selected_short_names = st.multiselect(
                "원하는 ETF를 선택하세요 (다중 선택 가능)", 
                list(sector_short_names.values()),
                default=list(sector_short_names.values()),
                key="kr_etf_select"
            )

            # 기간 선택 섹션
            st.markdown("### 📅 분석 기간 설정")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                period_mode = st.radio(
                    "기간 선택 방식",
                    ["설정된 기간", "직접 선택"],
                    horizontal=True,
                    key="kr_period_mode"
                )

            with col2:
                if period_mode == "설정된 기간":
                    period_options = {
                        "1일": 1,
                        "1주": 7,
                        "1개월": 30,
                        "3개월": 90,
                        "6개월": 180,
                        "1년": 365
                    }
                    selected_period = st.selectbox(
                        "적용 기간",
                        list(period_options.keys()),
                        index=1,  # 1주 선택을 위해 인덱스를 1로 변경
                        key="kr_period_select"
                    )
                    days_ago = period_options[selected_period]
                    end_date = datetime.datetime.today()
                    start_date = end_date - timedelta(days=days_ago)
                else:
                    date_range = st.date_input(
                        "조회할 기간 선택",
                        [datetime.date.today() - timedelta(days=30), datetime.date.today()],
                        key="kr_date_range"
                    )
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        days_ago = None
                    else:
                        st.error("날짜 범위를 올바르게 선택하세요.")
                        st.stop()

            # 선택된 기간 표시
            st.info(f"📊 분석 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")

        analyzer = ETFAnalyzer()  # 인스턴스 생성
        etf_data = analyzer.load_etf_data()  # Supabase에서 데이터 불러오기
        print("\n=== ETF 데이터 로드 결과 ===")
        print("📌 불러온 ETF 목록:", list(etf_data.keys()))
        print(f"📌 전체 ETF 개수: {len(etf_data)}")

        if not etf_data:
            st.warning("ETF 데이터가 없습니다. 먼저 데이터를 수집해주세요!")
            return

        # ETF 선택 기능 추가
        etf_short_to_full = {short: full for full, short in sector_short_names.items()}  # 역변환 딕셔너리
        etf_full_to_short = {full: short for full, short in sector_short_names.items()}  # 변환용 딕셔너리

        # 선택된 짧은 이름을 다시 원래 ETF 이름으로 변환
        selected_etfs = [etf_short_to_full[short] for short in selected_short_names if short in etf_short_to_full]
        print("\n=== 선택된 ETF 정보 ===")
        print("📌 선택된 ETF 목록:", selected_etfs)

        # ETF 데이터 로드
        etf_data = analyzer.load_etf_data()
        if not etf_data:
            st.warning("ETF 데이터가 없습니다. 먼저 데이터를 수집해주세요!")
            return

        # 선택한 ETF만 필터링
        etf_data_filtered = {etf: etf_data[etf] for etf in selected_etfs if etf in etf_data and len(etf_data[etf]) > 0}
        print("\n=== 필터링된 ETF 정보 ===")
        print("📌 필터링된 ETF 목록:", list(etf_data_filtered.keys()))
        print(f"📌 필터링된 ETF 개수: {len(etf_data_filtered)}")

        # 한국 섹터별 비중 데이터 (2024년 3월 기준 KOSPI 업종별 시가총액 비중 기반)
        sector_weights = {
            "KODEX IT": 30.5,
            "KODEX 반도체": 15.2,
            "KODEX 은행": 10.8,
            "KODEX 에너지화학": 9.7,
            "KODEX 자동차": 8.5,
            "KODEX 바이오": 7.3,
            "KODEX 헬스케어": 6.8,
            "KODEX 미디어통신": 5.2,
            "KODEX 철강": 3.5,
            "KODEX 건설": 2.5
        }

        labels, values, changes, text_labels = [], [], [], []
        for sector, data in etf_data_filtered.items():
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index = pd.to_datetime(df.index, errors='coerce')
            df = df.dropna().sort_index()

            # 선택한 날짜 범위 내 데이터만 필터링
            df_filtered = df.loc[start_date:end_date]

            if len(df_filtered) < 1:
                continue  # 데이터가 부족하면 건너뜀

            latest_price = df_filtered['Close'].iloc[-1]
            # 1일 기준일 경우 전날 데이터와 비교
            if period_mode == "설정된 기간" and days_ago == 1:
                prev_date = start_date - timedelta(days=1)
                
                # 전날 데이터 찾기 (이전 거래일 탐색)
                while prev_date.strftime('%Y-%m-%d') not in df.index and prev_date > df.index.min():
                    prev_date -= timedelta(days=1)

                if prev_date.strftime('%Y-%m-%d') in df.index:
                    prev_price = df.loc[prev_date.strftime('%Y-%m-%d'), 'Close']
                else:
                    continue  # 이전 거래일 데이터가 없으면 스킵

            else:
                prev_price = df_filtered['Close'].iloc[0]  # 일반적인 경우
           
            change = round((latest_price - prev_price) / prev_price * 100, 2)

            labels.append(sector_short_names.get(sector, sector))
            values.append(sector_weights.get(sector, 1))
            changes.append(change)
            text_labels.append(f"<b>{sector_short_names.get(sector, sector)}</b><br>{change:.2f}%")

        if not labels:
            st.warning("선택한 기간에 데이터가 없습니다.")
            return

        # Treemap 생성
        fig = go.Figure(go.Treemap(
            labels=labels,
            parents=["" for _ in labels],
            values=values,  #  트리맵 크기는 섹터별 비중 사용
            marker=dict(
                colors=changes,  #  색상은 증감률 기준
                colorscale=[  # 색상 범위 조정 (부드러운 블루-레드 계열)
                    [0, "#4575b4"],  # 진한 파랑
                    [0.25, "#91bfdb"],  # 연한 파랑
                    [0.5, "#e0f3f8"],  # 흰색 계열
                    [0.75, "#f4a6a6"],  # 연한 주황
                    [1, "#d73027"]  # 진한 빨강
                ],
                cmid=0,
                line=dict(width=1.5, color="white")  #  테두리 선
            ),
            text=text_labels,  #  트리맵 내부 텍스트: 섹터명 + 증감률
            textposition="middle center",
            hoverinfo="none",
            hovertemplate="<b>%{label}</b><br>" + 
                  "섹터비중: %{value:.2f}%<br>" +
                  "1일 수익률: %{customdata:.2f}%" +
                  "<extra></extra>",  # 불필요한 정보 제거
            customdata=changes,  # customdata를 이용해 1일 수익률 전달
            textinfo="text",  # 트리맵 내부에는 증감률만 표시
            textfont=dict(size=18, family="Arial", color="black"),  #  글씨 크기 키우고 색상 변경
        ))

        fig.update_layout(
            width=900,
            height=600,
            margin=dict(t=10, l=10, r=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig)
