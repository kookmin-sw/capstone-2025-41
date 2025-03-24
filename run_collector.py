from modules.collect_economic_data import collectEconomicData
from modules.DB import SupabaseDB
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta

# .env 파일 로드 (API 키들)
# load_dotenv()

# Supabase 연결 설정
# supabase_url = os.getenv("SUPABASE_URL")
# supabase_key = os.getenv("SUPABASE_KEY")
# supabase = create_client(supabase_url, supabase_key)

# 데이터 수집 클래스 초기화
collect_economic_data = collectEconomicData()

#------------------ 최근 10년간 일별 국내 데이터 ------------------#
start = (datetime.today() - relativedelta(years=10)).strftime("%Y%m%d")
end = datetime.today().strftime("%Y%m%d")

# 국고채(3년), 국고채(10년), 기준금리, KOSPI, KOSDAQ, 원/달러 환율
daily_domestic_code_lst = [
    ("817Y002", "010200000"), ("817Y002", "010210000"), ("722Y001", "0101000"), ("802Y001", "0001000"),
    ("802Y001", "0089000"),
    ("731Y001", "0000001")
]
freq = "D"  # 일별
code_dict = {"국고채(3년)": "kr_bond_3y", "국고채(10년)": "kr_bond_10y",
             "한국은행 기준금리": "kr_base_rate", "KOSPI지수": "kospi",
             "KOSDAQ지수": "kosdaq", "원/미국달러(매매기준율)": "usd_krw"}

dataset_daily = collect_economic_data.daily_domestic(start, end, daily_domestic_code_lst, freq, code_dict)

db = SupabaseDB()
db.insert_domestic_daily_economic(dataset_daily)

# TODO: DB 모듈 사용하여 dataset_daily 테이블 저장 (임시)
# https://chatgpt.com/c/67dfcb27-4bd0-8002-b85f-0542654a026b





















