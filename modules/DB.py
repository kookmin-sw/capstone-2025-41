import streamlit as st
from supabase import create_client

class SupabaseDB:
    def __init__(self):
        """Supabase 연결"""
        self.url = st.secrets["supabase"]["url"]
        self.key = st.secrets["supabase"]["key"]
        self.client = create_client(self.url, self.key)

    def insert_user(self, user_data):
        """사용자 데이터 저장"""
        response = self.client.table("users").insert(user_data).execute()
        return response

    def get_user(self, username):
        """사용자 데이터 가져오기"""
        response = self.client.table("users").select("*").eq("username", username).execute()
        return response.data if response.data else None

    def insert_stock_data(self, user_id, stock_data):
        """주식 데이터 Supabase에 저장 (중복되면 업데이트)"""
        for stock in stock_data:
            stock["user_id"] = user_id  # `user_id` 추가
        self.client.table("stocks").upsert(stock_data).execute()  # 중복되면 업데이트

    def insert_account_data(self, user_id, account_data):
        """계좌 데이터 Supabase에 저장 (리스트 처리)"""
        for account in account_data:
            account["user_id"] = user_id  # `user_id` 추가
        self.client.table("accounts").upsert(account_data).execute()  # 중복되면 업데이트

    def insert_cash_data(self, user_id, cash_amount):
        """현금 데이터 Supabase에 저장 (중복되면 업데이트)"""
        self.client.table("cash").upsert({"user_id": user_id, "현금": cash_amount}).execute()


    def get_stock_data(self, user_id):
        """Supabase에서 특정 사용자의 주식 데이터 가져오기"""
        response = self.client.table("stocks").select("*").eq("user_id", user_id).execute()
        return response.data if response.data else []

    def get_account_data(self, user_id):
        """Supabase에서 특정 사용자의 계좌 데이터 가져오기"""
        response = self.client.table("accounts").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    def get_cash_data(self, user_id):
        """Supabase에서 특정 사용자의 현금 데이터 가져오기"""
        response = self.client.table("cash").select("현금").eq("user_id", user_id).execute()
        return response.data[0]["현금"] if response.data else 0
