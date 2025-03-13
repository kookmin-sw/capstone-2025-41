from modules.korea_investment_api import KoreaInvestmentAPI
from modules.DB import SupabaseDB
import streamlit as st

class AccountManager(KoreaInvestmentAPI):
    def __init__(self, KEY, SECRET, acc_no, mock, user_id):
        self.db = SupabaseDB()  # Supabase 연결
        self.user_id = user_id  # user_id 저장
        self.stock_df, self.account_df = self.load_data(KEY, SECRET, acc_no, mock, user_id)
        self.cash = self.db.get_cash_data(user_id)  # 사용자별 현금 데이터 불러오기

    def load_data(self, KEY, SECRET, acc_no, mock, user_id):
        """한국투자증권 API에서 데이터 가져와 Supabase에 저장"""
        broker = KoreaInvestmentAPI(KEY, SECRET, acc_no, mock)
        stock_df, account_df = broker.get_balance()
        account_data = account_df.to_dict(orient="records")
        # Supabase에 저장 (리스트 형태로 해야 함함)
        self.db.insert_stock_data(user_id, stock_df.to_dict(orient="records"))
        self.db.insert_account_data(user_id, account_data)

        return stock_df, account_df


    def save_data(self, user_id):
        """현재 데이터 Supabase에 저장 (user_id 포함)"""
        self.db.insert_stock_data(user_id, self.stock_df.to_dict(orient="records"))
        self.db.insert_account_data(user_id, self.account_df.to_dict(orient="records"))
        self.db.insert_cash_data(user_id, self.cash)


    def modify_cash(self, amount):
        """현금 보유량 수정 (Supabase 업데이트)"""
        self.db.insert_cash_data(self.user_id, float(amount))  # `user_id` 추가
        self.cash = float(amount)


    def get_cash(self):
        return self.cash

    def get_stock(self):
        return self.stock_df

    def get_account(self):
        return self.account_df
