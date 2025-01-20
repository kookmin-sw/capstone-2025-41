# 예시 코드 (실제 구현 시에는 LangChain 등 사용)
class Chatbot:
    def __init__(self, finance_manager):
        self.finance_manager = finance_manager
        self.predefined_responses = {
            "잔액이 얼마야?": self.get_balance(),
            "이번 달 지출이 얼마야?": self.get_expense(),
            "이번 달 수입이 얼마야?": self.get_income(),
            "자산관리 조언 해줘": self.get_advice()
        }

    def get_balance(self):
        _, _, balance = self.finance_manager.get_summary()
        return f"현재 잔액은 **{balance:,} 원**입니다."

    def get_expense(self):
        _, expense, _ = self.finance_manager.get_summary()
        return f"이번 달 총 지출은 **{expense:,} 원**입니다."

    def get_income(self):
        income, _, _ = self.finance_manager.get_summary()
        return f"이번 달 총 수입은 **{income:,} 원**입니다."

    def get_advice(self):
        return "💡 지출을 줄이고 저축을 늘리는 것이 좋습니다!"

    def respond(self, user_input):
        return self.predefined_responses.get(user_input, "죄송해요, 이해하지 못했어요.")
