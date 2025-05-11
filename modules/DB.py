import streamlit as st
from supabase import create_client
import json
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

# .env 파일의 환경 변수 불러오기
load_dotenv()

class SupabaseDB:
    def __init__(self):
        """Supabase 연결"""
        if os.getenv("SUPABASE_URL"):
            self.url = os.getenv("SUPABASE_URL")
        else:
            self.url = st.secrets["supabase"]["url"]

        if os.getenv("SUPABASE_KEY"):
            self.key = os.getenv("SUPABASE_KEY")
        else:
            self.key = st.secrets["supabase"]["key"]

        self.client = create_client(self.url, self.key)

    def insert_user(self, user_data):
        """사용자 데이터 저장"""
        response = self.client.table("users").insert(user_data).execute()
        return response

    def get_user(self, username):
        """사용자 데이터 가져오기"""
        response = self.client.table("users").select("*").eq("username", username).execute()
        if response.data:
            user = response.data[0]

            # personal 필드가 문자열이면 JSON으로 복원
            if isinstance(user.get("personal"), str):
                try:
                    user["personal"] = json.loads(user["personal"])
                except json.JSONDecodeError:
                    pass

            return [user]
        return None

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

    def get_cash_data(self, user_id):
        """사용자의 현금 데이터 가져오기"""
        try:
            user = self.get_user(user_id)
            if user and user[0].get("personal", {}).get("financial", {}).get("cash") is not None:
                return user[0]["personal"]["financial"]["cash"]
            return 0
        except Exception as e:
            print(f"현금 데이터 조회 중 오류 발생: {str(e)}")
            return 0

    def get_stock_data(self, user_id):
        """Supabase에서 특정 사용자의 주식 데이터 가져오기"""
        response = self.client.table("stocks").select("*").eq("user_id", user_id).execute()
        return response.data if response.data else []

    def get_account_data(self, user_id):
        """Supabase에서 특정 사용자의 계좌 데이터 가져오기"""
        response = self.client.table("accounts").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

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
        data = {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "article": json.dumps(article_data, ensure_ascii=False),
            "source": "naver"
        }
        return self.client.table("articles").upsert(data).execute()

    def get_article_data_today(self):
        """오늘 일자 뉴스 기사 JSON 데이터를 Supabase에서 불러오기"""
        response = self.client.table("articles").select("article").\
            eq("date", datetime.today().strftime("%Y-%m-%d")).execute()
        if response.data:
            return json.loads(response.data[0]["article"])
        return []

    def get_article_data_today_and_yesterday(self):
        """어제 및 오늘 날짜의 뉴스 기사 JSON 데이터를 Supabase에서 불러오기"""
        today = datetime.today().strftime("%Y-%m-%d")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        response = self.client.table("articles").select("article"). \
            in_("date", [yesterday, today]).execute()

        articles = []
        if response.data:
            for row in response.data:
                articles.extend(json.loads(row["article"]))  # 기사 리스트를 병합
        return articles

    def insert_economic(self, eco_df, table_nm):
        """경제 지표 데이터를 Supabase에 JSON 형태로 저장"""
        eco_df["time"] = eco_df["time"].astype(str)
        data_to_store = eco_df.to_dict(orient="records")
        data_to_store = [{k: (None if pd.isna(v) else v) for k, v in data_dict.items()} for data_dict in data_to_store]

        response = self.client.table(table_nm).upsert(data_to_store).execute()

    def insert_real_estate_report(self, real_estate_report):
        """부동산 동향 리포트를 Supabase에 저장"""
        data = {
            "date": datetime.today().strftime("%Y-%m"),
            "real_estate_report": json.dumps(real_estate_report, ensure_ascii=False)
        }
        return self.client.table("real_estate_report").upsert(data).execute()

    def get_real_estate_report(self):
        """부동산 동향 리포트를 Supabase에서 가져오기"""
        response = self.client.table("real_estate_report").select("real_estate_report").\
            eq("date", datetime.today().strftime("%Y-%m")).execute()
        if response.data:
            return json.loads(response.data[0]["real_estate_report"])
        return []

    def insert_macro_report(self, macro_report):
        """거시경제 동향 리포트를 Supabase에 저장"""
        data = {
            "date": datetime.today().strftime("%Y-%m"),
            "macro_report": json.dumps(macro_report, ensure_ascii=False)
        }
        return self.client.table("macro_report").upsert(data).execute()
    
    def get_macro_report(self):
        """거시경제 리포트를 Supabase에서 가져오기"""
        response = self.client.table("macro_report").select("macro_report").\
            eq("date", datetime.today().strftime("%Y-%m")).execute()
        if response.data:
            return json.loads(response.data[0]["macro_report"])
        return []

    def insert_user_personal(self, username, personal_data):
        """사용자 개인 투자 성향 JSON 데이터 저장"""
        json_string = json.dumps(personal_data, ensure_ascii=False)
        response = self.client.table("users").update({
            "personal": json_string
        }).eq("username", username).execute()
        return response

    def update_user_info(self, username, updated_data):
        """사용자 정보 업데이트"""
        # personal 필드가 딕셔너리인 경우 JSON 문자열로 변환
        if "personal" in updated_data and isinstance(updated_data["personal"], dict):
            updated_data["personal"] = json.dumps(updated_data["personal"], ensure_ascii=False)
        
        response = self.client.table("users").update(updated_data).eq("username", username).execute()
        return response

    def insert_etf_data_kr_json(self, etf_data):
        """한국 ETF 데이터를 Supabase에 JSON 형태로 저장"""
        data_to_store = [{"etf_name": name, "data": json.dumps(data)} for name, data in etf_data.items()]
        print("📌 Supabase에 업로드할 데이터:", data_to_store)

        response = self.client.table("etf_data_kr_json").upsert(data_to_store).execute()
        print("📌 Supabase 응답:", response)

    def get_etf_data_kr_json(self):
        """Supabase에서 한국 ETF JSON 데이터를 불러오기"""
        response = self.client.table("etf_data_kr_json").select("*").execute()
        return {row["etf_name"]: json.loads(row["data"]) for row in response.data} if response.data else {}
