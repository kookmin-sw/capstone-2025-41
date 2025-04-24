# modules/mypage.py

import streamlit as st
import json

def show_my_page(user, user_manager):
    st.title("👤 마이페이지")

    if not user:
        st.error("⚠️ 사용자 정보를 불러올 수 없습니다. 다시 로그인해 주세요.")
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"
        st.rerun()
        return

    # --- 계정 정보 --- #
    st.subheader("📌 내 계정 정보")
    st.write(f"**아이디:** {user['username']}")
    st.write(f"**비밀번호:** {'•' * len(user['password'])}")
    st.write(f"**계좌 번호:** {user['account_no']}")

    if "editing_user_info" not in st.session_state:
        st.session_state["editing_user_info"] = False

    if not st.session_state["editing_user_info"]:
        if st.button("계정 정보 수정"):
            st.session_state["editing_user_info"] = True
            st.rerun()
    else:
        with st.form("edit_user_info"):
            st.text_input("아이디", value=user["username"], disabled=True)
            new_password = st.text_input("비밀번호", type="password", value=user["password"])
            new_account_no = st.text_input("계좌 번호", value=user["account_no"])
            new_api_key = st.text_input("한국투자증권 APP Key", value=user["api_key"])
            new_api_secret = st.text_input("한국투자증권 APP Secret", value=user["api_secret"])

            col1, col2 = st.columns(2)
            with col1:
                save = st.form_submit_button("저장")
            with col2:
                cancel = st.form_submit_button("취소")

        if save:
            updated_data = {
                "password": new_password,
                "account_no": new_account_no,
                "api_key": new_api_key,
                "api_secret": new_api_secret
            }
            user_manager.update_user_info(user["username"], updated_data)
            st.success("✅ 정보가 성공적으로 수정되었습니다!")
            st.session_state["editing_user_info"] = False
            st.rerun()

        elif cancel:
            st.session_state["editing_user_info"] = False
            st.rerun()

    # --- 투자 성향 --- 
    st.subheader("나의 투자 성향 정보")

    personal = user.get("personal", {})
    if isinstance(personal, str):
        try:
            personal = json.loads(personal)
        except json.JSONDecodeError:
            personal = {}

    if "editing_personal" not in st.session_state:
        st.session_state["editing_personal"] = False

    if not st.session_state["editing_personal"]:
        if not personal:
            st.info("아직 투자 성향 정보가 없습니다.")
        for key, value in personal.items():
            st.markdown(f"**{key}**: {value}")

        if st.button("성향 정보 수정"):
            st.session_state["editing_personal"] = True
            st.rerun()
    else:
        with st.form("edit_personal_form"):
            age = st.number_input("나이", min_value=0, max_value=120, value=personal.get("age", 0))

            gender_options = ["선택 안 함", "남성", "여성"]
            gender_value = personal.get("gender", "선택 안 함")
            gender = st.selectbox("성별", gender_options, index=gender_options.index(gender_value) if gender_value in gender_options else 0)

            type_options = ["보수형", "중립형", "공격형"]
            type_value = personal.get("investment_type", "중립형")
            investment_type = st.selectbox("투자 성향", type_options, index=type_options.index(type_value) if type_value in type_options else 1)

            goal_options = ["자산 증식", "은퇴 준비", "단기 수익", "기타"]
            goal_value = personal.get("investment_goal", "자산 증식")
            investment_goal = st.selectbox("투자 목적", goal_options, index=goal_options.index(goal_value) if goal_value in goal_options else 0)

            horizon_options = ["1년 이하", "1~3년", "3~5년", "5년 이상"]
            horizon_value = personal.get("investment_horizon", "1~3년")
            investment_horizon = st.selectbox("투자 기간", horizon_options, index=horizon_options.index(horizon_value) if horizon_value in horizon_options else 1)

            risk_options = ["낮음", "중간", "높음"]
            risk_value = personal.get("risk_tolerance", "중간")
            risk_tolerance = st.selectbox("리스크 허용도", risk_options, index=risk_options.index(risk_value) if risk_value in risk_options else 1)

            monthly_investment = st.number_input("월 투자 가능 금액 (원)", step=10000, value=personal.get("monthly_investment", 0))

            asset_options = ["주식", "ETF", "부동산", "채권", "대체투자", "기타"]
            preferred_assets = st.multiselect(
                "선호 자산군",
                asset_options,
                default=[a for a in personal.get("preferred_assets", []) if a in asset_options]
            )

            save = st.form_submit_button("저장")
            cancel = st.form_submit_button("취소")


        if save:
            updated_personal = {
                "age": age,
                "gender": gender,
                "investment_type": investment_type,
                "investment_goal": investment_goal,
                "investment_horizon": investment_horizon,
                "risk_tolerance": risk_tolerance,
                "monthly_investment": monthly_investment,
                "preferred_assets": preferred_assets
            }
            user_manager.update_user_personal(user["username"], updated_personal)
            st.success("✅ 투자 성향 정보가 업데이트되었습니다!")
            st.session_state["editing_personal"] = False
            st.rerun()

        if cancel:
            st.session_state["editing_personal"] = False
            st.rerun()
