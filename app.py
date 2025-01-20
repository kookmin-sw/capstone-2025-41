import streamlit as st
from modules.data_manager import DataManager
from modules.visualization import Visualization

st.title("계좌 불러오기")

# 주식 데이터, 계좌 데이터 초기화
stock_df = None
account_df = None

# API_KEY, SECRET_KEY, 계좌번호 등 입력 (이 부분은 이후에 "회원 가입" 페이지와 "계좌 불러오기" 페이지로 이동)
with st.form("inform_input"):
    KEY = st.text_input("한국투자증권의 APP Key를 입력하세요")
    SECRET = st.text_input("한국투자증권의 APP Secret를 입력하세요")
    acc_no = st.text_input("한국투자증권의 계좌번호를 입력하세요")

    if st.checkbox("모의투자 계좌입니다"):
        mock = True
    else:
        mock = False

    if st.form_submit_button("저장"):
        try:
            data_manager = DataManager(KEY, SECRET, acc_no, mock)
            stock_df = data_manager.get_stock()
            account_df = data_manager.get_account()
        except:
            st.write("**⚠️데이터를 불러오는 데 실패했습니다**")

if account_df is not None and stock_df is not None:
    total = int(account_df.loc[0, '총평가금액'])
    profit = int(account_df.loc[0, '평가손익합계금액'])
    
    st.subheader("📜나의 포트폴리오")
    st.metric("총자산", f"{total:,}원",
                f"{int(account_df.loc[0, '평가손익합계금액']):,}원  |  "\
                f"{round(profit/(total-profit) * 100, 2):,.2f}%")

    #---------------- 메인 페이지 시각화 ----------------#
    visualization = Visualization(stock_df, account_df)

    # 포트폴리오 도넛 차트 시각화
    visualization.portfolio_doughnut_chart()