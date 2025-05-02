import streamlit as st

class InvestmentProfiler:
    @staticmethod
    def get_investment_score(show_result=False, previous_answers=None):
        total_score = 0
        
        st.write("### 투자 성향 진단 설문")
        st.write("각 질문에 답변해 주세요.")
        
        # 1. 투자 경험
        experience_options = {
            "없음": 1,
            "간단한 예·적금 외에는 없음": 2,
            "펀드, 채권 등 투자 경험 있음": 3,
            "주식, 펀드 등 투자 자산 보유 중": 4,
            "고위험 상품(해외주식, 파생상품 등) 경험 있음": 5
        }
        default_idx = list(experience_options.keys()).index(previous_answers.get('investment_experience', "없음")) if previous_answers else 0
        experience = st.radio(
            "1. 귀하의 투자 경험은 어느 정도입니까?",
            list(experience_options.keys()),
            index=default_idx
        )
        total_score += experience_options[experience]

        # 2. 투자 가능 기간
        horizon_options = {
            "1년 미만": 1,
            "1~2년": 2,
            "3~4년": 3,
            "5~7년": 4,
            "8년 이상": 5
        }
        default_idx = list(horizon_options.keys()).index(previous_answers.get('investment_horizon', "1년 미만")) if previous_answers else 0
        horizon = st.radio(
            "2. 투자 가능한 기간은 얼마나 되나요?",
            list(horizon_options.keys()),
            index=default_idx
        )
        total_score += horizon_options[horizon]

        # 3. 손실 감내 수준
        risk_options = {
            "손실은 절대 허용할 수 없다": 1,
            "5% 미만 손실만 감수 가능": 2,
            "10~15% 정도까지 감수 가능": 3,
            "20~30%까지 가능": 4,
            "30% 이상도 괜찮다": 5
        }
        default_idx = list(risk_options.keys()).index(previous_answers.get('risk_tolerance', "손실은 절대 허용할 수 없다")) if previous_answers else 0
        risk = st.radio(
            "3. 다음 중 본인의 손실 감내 수준에 가장 가까운 것은?",
            list(risk_options.keys()),
            index=default_idx
        )
        total_score += risk_options[risk]

        # 4. 기대 수익률
        return_options = {
            "2% 이하": 1,
            "3~4%": 2,
            "5~7%": 3,
            "8~12%": 4,
            "13% 이상": 5
        }
        default_idx = list(return_options.keys()).index(previous_answers.get('expected_return', "2% 이하")) if previous_answers else 0
        returns = st.radio(
            "4. 기대하는 연 수익률 수준은?",
            list(return_options.keys()),
            index=default_idx
        )
        total_score += return_options[returns]

        # 5. 중요 투자 요소
        priority_options = {
            "원금 보전": 1,
            "원금 보전 + 약간의 수익": 2,
            "수익과 안정성 균형": 3,
            "수익 우선": 4,
            "고수익 추구": 5
        }
        default_idx = list(priority_options.keys()).index(previous_answers.get('investment_priority', "원금 보전")) if previous_answers else 0
        priority = st.radio(
            "5. 투자 시 가장 중요하게 생각하는 요소는?",
            list(priority_options.keys()),
            index=default_idx
        )
        total_score += priority_options[priority]

        # 6. 금융 이해도
        knowledge_options = {
            "전혀 모른다": 1,
            "기초적인 수준이다": 2,
            "기본적인 상품 구조를 이해한다": 3,
            "다양한 자산을 구분하고 분석할 수 있다": 4,
            "경제 흐름과 시장 분석이 가능하다": 5
        }
        default_idx = list(knowledge_options.keys()).index(previous_answers.get('financial_knowledge', "전혀 모른다")) if previous_answers else 0
        knowledge = st.radio(
            "6. 금융 및 투자에 대한 본인의 이해 수준은?",
            list(knowledge_options.keys()),
            index=default_idx
        )
        total_score += knowledge_options[knowledge]

        # 투자 성향 결정
        investment_style = InvestmentProfiler.get_investment_style(total_score)
        
        result = {
            "total_score": total_score,
            "investment_style": investment_style,
            "details": {
                "investment_experience": experience,
                "investment_horizon": horizon,
                "risk_tolerance": risk,
                "expected_return": returns,
                "investment_priority": priority,
                "financial_knowledge": knowledge
            }
        }

        if show_result:
            InvestmentProfiler.show_result(result)

        return result

    @staticmethod
    def get_investment_style(score):
        if score <= 9:
            return "안정형"
        elif score <= 14:
            return "안정추구형"
        elif score <= 19:
            return "위험중립형"
        elif score <= 24:
            return "적극투자형"
        else:
            return "공격투자형"

    @staticmethod
    def show_result(result):
        st.write("### 투자 성향 진단 결과")
        st.write(f"**투자 성향:** {result['investment_style']}")
        
        st.write("### 세부 응답")
        details = result['details']
        st.write(f"- 투자 경험: {details['investment_experience']}")
        st.write(f"- 투자 가능 기간: {details['investment_horizon']}")
        st.write(f"- 손실 감내 수준: {details['risk_tolerance']}")
        st.write(f"- 기대 수익률: {details['expected_return']}")
        st.write(f"- 중요 투자 요소: {details['investment_priority']}")
        st.write(f"- 금융 이해도: {details['financial_knowledge']}") 