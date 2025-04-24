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

    # --- 투자 성향 --- #
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
        else:

            for key, value in personal.items():
                if isinstance(value, list):
                    value = ", ".join(value)
                st.markdown(f"**{key}**: {value}")

        if st.button("성향 정보 수정"):
            st.session_state["editing_personal"] = True
            st.rerun()
    else:
        with st.form("edit_personal_form"):
            # 옵션 정의
            age_group_options = ["20~39세", "40~49세", "50~65세", "66~79세", "80세 이상"]
            horizon_options = ["5년 이상", "3~5년", "2~3년", "1~2년", "1년 미만"]
            experience_options = [
                "적음",
                "보통",
                "많음"
            ]
            
            knowledge_options = [
                "투자 경험 없음",
                "일부 이해함",
                "깊이 있게 이해함"
            ]

            return_options = [
                "무조건 원금 보전",
                "원금 기준 ±5%",
                "원금 기준 ±10%",
                "원금 기준 ±20%",
                "원금 기준 ±20% 초과"
            ]
            style_options = ["안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"]
            goal_options = ["예적금 수준 수익", "시장 평균 이상 수익", "적극적인 자산 증식", "생계자금 운용"]
            asset_options = ["주식", "부동산", "예적금", "외화", "금", "암호화폐", "기타"]

            # 필드 렌더링
            age_group = st.selectbox("연령대", age_group_options, index=age_group_options.index(personal.get("age_group", "20~39세")))
            investment_horizon = st.selectbox("투자 가능 기간", horizon_options, index=horizon_options.index(personal.get("investment_horizon", "3~5년")))
            investment_experience = st.radio(
                "투자경험", 
                experience_options, 
                index=experience_options.index(
                personal.get("investment_experience", "보통") 
                if isinstance(personal.get("investment_experience"), str) 
                else personal.get("investment_experience", ["보통"])[0]
                )
            )
            knowledge_level = st.radio("금융지식 수준/이해도", knowledge_options, index=knowledge_options.index(personal.get("knowledge_level", "일부 이해함")))
            return_tolerance = st.radio("기대 이익수준 및 손실감내 수준", return_options, index=return_options.index(personal.get("return_tolerance", "원금 기준 ±10%")))
            investment_style = st.selectbox("투자성향", style_options, index=style_options.index(personal.get("investment_style", "위험중립형")))
            investment_goal = st.multiselect("투자목표", goal_options, default=personal.get("investment_goal", []))
            preferred_assets = st.multiselect("선호 자산군", asset_options, default=personal.get("preferred_assets", []))

            col1, col2 = st.columns(2)
            with col1:
                save = st.form_submit_button("저장")
            with col2:
                cancel = st.form_submit_button("취소")

            if save:
                updated_personal = {
                    "age_group": age_group,
                    "investment_horizon": investment_horizon,
                    "investment_experience": investment_experience,
                    "knowledge_level": knowledge_level,
                    "return_tolerance": return_tolerance,
                    "investment_style": investment_style,
                    "investment_goal": investment_goal,
                    "preferred_assets": preferred_assets
                }

                user_manager.update_user_info(user["username"], {"personal": updated_personal})


                st.success("✅ 투자 성향 정보가 업데이트되었습니다!")
                st.session_state["editing_personal"] = False
                st.rerun()
            elif cancel:
                st.session_state["editing_personal"] = False
                st.rerun()
