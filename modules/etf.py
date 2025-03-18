import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import os
import FinanceDataReader as fdr
from datetime import timedelta
import datetime
from modules.DB import SupabaseDB

# 데이터 저장 경로
ETF_DATA_FILE = "data/etf_data.json"

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

            df.index = pd.to_datetime(df.index, errors='coerce')  # ✅ 날짜 변환
            df.index = df.index.strftime('%Y-%m-%d')  # ✅ Timestamp → 문자열 변환

            etf_data[name] = df[['Close']].to_dict(orient='index')  # 🔥 JSON 저장 가능

            print(f"✅ {name}({code}) 데이터 저장 완료. 저장된 데이터 개수: {len(etf_data[name])}")  # 🔍 저장된 데이터 개수 확인

        print("📌 Supabase에 저장할 데이터 (최종):", etf_data)  # 🔍 Supabase에 저장할 전체 데이터 확인

        if not etf_data:
            print("📌 저장할 ETF 데이터가 없습니다.")
            return

        self.db.insert_etf_data_json(etf_data)
        print("✅ ETF 데이터가 Supabase에 JSON 형태로 저장되었습니다.")


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
        st.title("📊 S&P500 섹터 트리맵")

        analyzer = ETFAnalyzer()  # ✅ 인스턴스 생성
        etf_data = analyzer.load_etf_data()  # ✅ Supabase에서 데이터 불러오기

        if not etf_data:
            st.warning("ETF 데이터가 없습니다. 먼저 데이터를 수집해주세요!")
            return

        
        # ETF 선택 기능 추가
        # ETF 이름을 짧은 이름으로 변환하여 표시
        etf_short_to_full = {short: full for full, short in sector_short_names.items()}  # 역변환 딕셔너리
        etf_full_to_short = {full: short for full, short in sector_short_names.items()}  # 변환용 딕셔너리

        selected_short_names = st.multiselect(
            "📌 원하는 ETF를 선택하세요 (다중 선택 가능)", 
            list(sector_short_names.values()),  # UI에서 짧은 이름으로 표시
            default=list(sector_short_names.values())  # 기본은 전체 선택
        )

        # 선택된 짧은 이름을 다시 원래 ETF 이름으로 변환
        selected_etfs = [etf_short_to_full[short] for short in selected_short_names if short in etf_short_to_full]

        period_mode = st.radio("📌 기간 선택 방식", ["설정된 기간", "직접 선택"], horizontal=True)

        if period_mode == "설정된 기간":
            period_options = {
                "1일": 1,
                "1주": 7,
                "1개월": 30,
                "3개월": 90,
                "6개월": 180,
                "1년": 365
            }
            selected_period = st.selectbox("적용 기간", list(period_options.keys()), index=0)
            days_ago = period_options[selected_period]

            # 오늘 날짜 기준으로 시작일과 종료일 설정
            end_date = datetime.datetime.today()  # 오늘 날짜 가져오기
            start_date = end_date - timedelta(days=days_ago)

        else:
            # 사용자 지정 날짜 입력
            date_range = st.date_input("조회할 기간 선택", [datetime.date.today() - timedelta(days=30), datetime.date.today()])
            
            # 사용자가 선택한 날짜를 변수로 저장
            if len(date_range) == 2:
                start_date, end_date = date_range
            else:
                st.error("날짜 범위를 올바르게 선택하세요.")
                st.stop()  # 🚨 날짜가 없으면 코드 실행 중단

        # 선택한 기간을 출력
        st.write(f"📅 **조회 기간:** {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")



        # ETF 데이터 로드
        etf_data = analyzer.load_etf_data()  # ✅ 인스턴스에서 호출
        if not etf_data:
            st.warning("ETF 데이터가 없습니다. 먼저 데이터를 수집해주세요!")
            return

        # 선택한 ETF만 필터링 (ETF가 실제 데이터에 존재하는 경우만)
        etf_data_filtered = {etf: etf_data[etf] for etf in selected_etfs if etf in etf_data and len(etf_data[etf]) > 0}


        # S&P500 섹터별 비중 데이터 (트리맵 크기)
        sector_weights = {
            "Kodex 미국S&P500테크놀로지": 30.12,
            "Kodex 미국S&P500금융": 14.44,
            "Kodex 미국S&P500헬스케어": 10.67,
            "Kodex 미국S&P500경기소비재": 10.87,
            "Kodex 미국S&P500커뮤니케이션": 9.73,
            "Kodex 미국S&P500산업재(합성)": 8.10,
            "Kodex 미국S&P500필수소비재": 6.5,
            "Kodex 미국S&P500에너지(합성)": 3.22,
            "Kodex 미국S&P500부동산": 2.13,
            "Kodex 미국S&P500유틸리티": 2.29,
            "Kodex 미국S&P500소재": 1.94
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
            prev_price = df_filtered['Close'].iloc[0]  # 선택한 기간의 시작 가격
            change = round((latest_price - prev_price) / prev_price * 100, 2)

            labels.append(sector_short_names.get(sector, sector))
            values.append(sector_weights.get(sector, 1))
            changes.append(change)
            text_labels.append(f"<b>{sector_short_names.get(sector, sector)}</b><br>{change:.2f}%")


        fig = go.Figure(go.Treemap(
            labels=labels,
            parents=["" for _ in labels],
            values=values,  #  트리맵 크기는 S&P500 섹터별 비중 사용
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
        
