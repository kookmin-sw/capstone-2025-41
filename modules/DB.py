import streamlit as st
from supabase import create_client
import json
import os

class SupabaseDB:
    def __init__(self):
        """Supabase 연결"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
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

    def insert_etf_data_json(self, etf_data):
        """ETF 데이터를 Supabase에 JSON 형태로 저장"""
        data_to_store = [{"etf_name": name, "data": json.dumps(data)} for name, data in etf_data.items()]
        print("📌 Supabase에 업로드할 데이터:", data_to_store)  # 🔍 업로드할 데이터 확인

        response = self.client.table("etf_data_json").upsert(data_to_store).execute()
        print("📌 Supabase 응답:", response)  # 🔍 Supabase 응답 출력

    def get_etf_data_json(self):
        """Supabase에서 ETF JSON 데이터를 불러오기"""
        response = self.client.table("etf_data_json").select("*").execute()
        return {row["etf_name"]: json.loads(row["data"]) for row in response.data} if response.data else {}
    
    def insert_article_data_json(self, article_data):
        """뉴스 기사 데이터를 JSON 형식으로 Supabase에 저장"""
        data = {"id": "naver_articles", "json_data": json.dumps(article_data, ensure_ascii=False)}
        return self.client.table("article_data_json").upsert(data).execute()

    def get_article_data_json(self):
        """뉴스 기사 JSON 데이터를 Supabase에서 불러오기"""
        response = self.client.table("article_data_json").select("json_data").eq("id", "naver_articles").execute()
        if response.data:
            return json.loads(response.data[0]["json_data"])
        return []

    def insert_domestic_daily_economic(self, domestic_daily_economic):
        """ETF 데이터를 Supabase에 JSON 형태로 저장"""
        data_to_store = domestic_daily_economic.to_dict(orient="records")
        print("📌 Supabase에 업로드할 데이터:", data_to_store)  # 🔍 업로드할 데이터 확인

        response = self.client.table("domestic_daily_economic").upsert(data_to_store).execute()
        print("📌 Supabase 응답:", response)  # 🔍 Supabase 응답 출력