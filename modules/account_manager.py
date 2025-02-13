from modules.korea_investment_api import KoreaInvestmentAPI
import json
import os

class AccountManager(KoreaInvestmentAPI):
    def __init__(self, KEY, SECRET, acc_no, mock):
        self.stock_file = "data/stock_data.json"
        self.account_file = "data/account_data.json"
        self.cash_file = "data/cash_data.json"
        self.stock_df, self.account_df = self.load_data(KEY, SECRET, acc_no, mock)
        
        # cash_data.json 파일이 없는 경우 default값 삽입
        if not os.path.exists(self.cash_file):
            self.modify_cash()

        # cash 데이터 가져오기
        with open(self.cash_file, "r", encoding="utf-8") as f:
            self.cash = json.load(f)["현금"]

    def load_data(self, KEY, SECRET, acc_no, mock):
        broker = KoreaInvestmentAPI(KEY, SECRET, acc_no, mock)
        stock_df, account_df = broker.get_balance()
        stock_df.iloc[:, 2:] = stock_df.iloc[:, 2:].astype(float)
        account_df = account_df.astype(float)

        return stock_df, account_df

    def modify_cash(self, amount=0):
        """ 현금 보유량을 수정하는 함수 (default=0) """
        cash = {"현금": float(amount)}

        with open(self.cash_file, "w", encoding="utf-8") as f:
            json.dump(cash, f, ensure_ascii=False, indent=4)

    def get_cash(self):
        return self.cash

    def get_stock(self):
        return self.stock_df

    def get_account(self):
        return self.account_df

    def save_data(self):
        self.stock_df.to_json(self.stock_file, orient="records", force_ascii=False, indent=4)
        self.account_df.to_json(self.account_file, orient="records", force_ascii=False, indent=4)
