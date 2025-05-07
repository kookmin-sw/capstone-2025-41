import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import os
import FinanceDataReader as fdr
from datetime import timedelta
import datetime
from modules.DB import SupabaseDB

# ETF 리스트 (KODEX 미국 S&P500 섹터별 ETF 종목코드 사용)
ETF_LIST = {
    'Kodex 미국S&P500테크놀로지': '463680',
    'Kodex 미국S&P500금융': '453650',
    'Kodex 미국S&P500커뮤니케이션': '463690',
    'Kodex 미국S&P500경기소비재': '453660',
    'Kodex 미국S&P500산업재(합성)': '200030',
    'Kodex 미국S&P500헬스케어': '453640',
    'Kodex 미국S&P500에너지(합성)': '218420',
    'Kodex 미국S&P500필수소비재': '453630',
    #'Kodex 미국S&P500부동산': '',
    #'Kodex 미국S&P500소재': '',
    'Kodex 미국S&P500유틸리티': '463640'
}

# 섹터 이름 변환 (짧게 표시)
sector_short_names = {
    "Kodex 미국S&P500테크놀로지": "테크놀로지",
    "Kodex 미국S&P500금융": "금융",
    "Kodex 미국S&P500헬스케어": "헬스케어",
    "Kodex 미국S&P500경기소비재": "경기소비재",
    "Kodex 미국S&P500커뮤니케이션": "커뮤니케이션",
    "Kodex 미국S&P500산업재(합성)": "산업재",
    "Kodex 미국S&P500필수소비재": "필수소비재",
    "Kodex 미국S&P500에너지(합성)": "에너지",
    #"Kodex 미국S&P500부동산": "부동산",
    "Kodex 미국S&P500유틸리티": "유틸리티",
    #"Kodex 미국S&P500소재": "소재"
}



class ETFAnalyzer:
    
    def __init__(self):
        """Supabase 연결"""
        self.db = SupabaseDB()

    def save_etf_data(self):
        """ETF 데이터를 Supabase에 JSON 형태로 저장"""
        etf_data = {}

        for name, code in ETF_LIST.items():
            df = fdr.DataReader(code)
            
            print(f"📌 {name}({code})에서 가져온 데이터 (상위 5개):")
            print(df.head())  # 🔍 ETF 데이터가 정상적으로 로드되는지 확인
            
            if df.empty:
                print(f"⚠️ {name}({code})의 데이터를 가져오지 못했습니다.")
                continue  # 데이터가 없으면 건너뜀

            df.index = pd.to_datetime(df.index, errors='coerce')  # 날짜 변환
            df.index = df.index.strftime('%Y-%m-%d')  # Timestamp를를 문자열 변환

            etf_data[name] = df[['Close']].to_dict(orient='index')  # JSON 저장

            print(f"{name}({code}) 데이터 저장 완료. 저장된 데이터 개수: {len(etf_data[name])}")  # 디버깅/ 저장된 데이터 개수 확인

        print("📌 Supabase에 저장할 데이터 (최종):", etf_data)  # 🔍 디버깅/ Supabase에 저장할 전체 데이터 확인

        if not etf_data:
            print("📌 저장할 ETF 데이터가 없습니다.")
            return

        self.db.insert_etf_data_json(etf_data)
        print("ETF 데이터가 Supabase에 JSON 형태로 저장되었습니다.")


    def load_etf_data(self):
        """Supabase에서 JSON 형태의 ETF 데이터를 불러옴"""
        etf_data = self.db.get_etf_data_json()

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
                    border-border-radius: 5px;
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
                key="us_etf_select"
            )

            # 기간 선택 섹션
            st.markdown("### 📅 분석 기간 설정")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                period_mode = st.radio(
                    "기간 선택 방식",
                    ["설정된 기간", "직접 선택"],
                    horizontal=True,
                    key="us_period_mode"
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
                        index=1,
                        key="us_period_select"
                    )
                    days_ago = period_options[selected_period]
                    end_date = datetime.datetime.today()
                    start_date = end_date - timedelta(days=days_ago)
                else:
                    date_range = st.date_input(
                        "조회할 기간 선택",
                        [datetime.date.today() - timedelta(days=30), datetime.date.today()],
                        key="us_date_range"
                    )
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        days_ago = None
                    else:
                        st.error("날짜 범위를 올바르게 선택하세요.")
                        st.stop()

            # 선택된 기간 표시
            st.info(f"📊 분석 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")

        # ETF 데이터 로드
        analyzer = ETFAnalyzer()  # 인스턴스 생성
        etf_data = analyzer.load_etf_data()  # Supabase에서 데이터 불러오기

        if not etf_data:
            st.warning("ETF 데이터가 없습니다. 먼저 데이터를 수집해주세요!")
            return

        # 선택한 ETF만 필터링 (ETF가 실제 데이터에 존재하는 경우만)
        etf_data_filtered = {}
        etf_short_to_full = {short: full for full, short in sector_short_names.items()}  # 역변환 딕셔너리

        for short_name in selected_short_names:
            full_name = etf_short_to_full.get(short_name)
            if full_name and full_name in etf_data:
                etf_data_filtered[short_name] = etf_data[full_name]

        if not etf_data_filtered:
            st.warning("선택한 ETF의 데이터가 없습니다.")
            return

        # S&P500 섹터별 비중 데이터 (트리맵 크기)
        sector_weights = {
            "테크놀로지": 30.12,
            "금융": 14.44,
            "헬스케어": 10.67,
            "경기소비재": 10.87,
            "커뮤니케이션": 9.73,
            "산업재": 8.10,
            "필수소비재": 6.5,
            "에너지": 3.22,
            "유틸리티": 2.29
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

            labels.append(sector)
            values.append(sector_weights.get(sector, 1))
            changes.append(change)
            text_labels.append(f"<b>{sector}</b><br>{change:.2f}%")


        fig = go.Figure(go.Treemap(
            labels=labels,
            parents=["" for _ in labels],
            values=values,  #  트리맵 크기는 S&P500 섹터별 비중 사용
            marker=dict(
                colors=changes,  #  색상은 증감률 기준
                colorscale=[  # 색상 범위 조정 (더 선명한 색상 사용)
                    [0, "#1a237e"],  # 진한 파랑
                    [0.25, "#3949ab"],  # 중간 파랑
                    [0.5, "#e8eaf6"],  # 연한 파랑
                    [0.75, "#e53935"],  # 진한 빨강
                    [1, "#b71c1c"]  # 더 진한 빨강
                ],
                cmid=0,
                line=dict(width=1, color="black"),  # 선 두께를 1로 줄이고 한 번만 표시
                pad=dict(t=2, l=2, r=2, b=2)  # 섹터 간 간격 추가
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
            plot_bgcolor="black",
            shapes=[dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(
                    color="black",
                    width=5
                )
            )]
        )


        st.plotly_chart(fig)
        
