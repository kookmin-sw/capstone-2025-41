from modules.collect_economic_data import collectEconomicData
from modules.DB import SupabaseDB
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta

# 클래스 초기화
db = SupabaseDB()
collect_economic_data = collectEconomicData()

# 한국 시간 설정
kst = pytz.timezone("Asia/Seoul")

#------------------ 최근 10년간 일별 국내 데이터 ------------------#
# 수집 날짜
start = (datetime.now(kst) - relativedelta(years=10)).strftime("%Y%m%d")
end = datetime.now(kst).strftime("%Y%m%d")

# 국고채(3년), 국고채(10년), 기준금리, KOSPI, KOSDAQ, 원/달러 환율
daily_domestic_code_lst = [
    ("817Y002", "010200000"), ("817Y002", "010210000"), ("722Y001", "0101000"), ("802Y001", "0001000"),
    ("802Y001", "0089000"), ("731Y001", "0000001")
]
freq = "D"  # 일별
code_dict = {"국고채(3년)": "kr_bond_3y", "국고채(10년)": "kr_bond_10y",
             "한국은행 기준금리": "kr_base_rate", "KOSPI지수": "kospi",
             "KOSDAQ지수": "kosdaq", "원/미국달러(매매기준율)": "usd_krw"}

dataset_daily = collect_economic_data.daily_domestic(start, end, daily_domestic_code_lst, freq, code_dict)
db.insert_domestic_daily_economic(dataset_daily)


#------------------ 최근 10년간 월별 국내 데이터 ------------------#
# 수집 날짜
start = (datetime.now(kst) - relativedelta(years=10)).strftime("%Y%m")
end = datetime.now(kst).strftime("%Y%m")

# 실업률, 고용률, 소비자물가지수, 생산자물가지수, 경상수지
monthly_domestic_code_lst = [
    ("901Y027", "I61BC/I28B"), ("901Y027", "I61E/I28B"), ("901Y009", "0"), ("404Y014", "*AA"), ("301Y017", "SA000")
]
freq = "M"  # 월별
code_dict = {"실업률": "unemp_rate", "고용률": "emp_rate", "4.2.1. 소비자물가지수": "cpi",
             "4.1.1.1. 생산자물가지수(기본분류)": "ppi", "경상수지": "curr_account"}

dataset_monthly = collect_economic_data.monthly_domestic(start, end, monthly_domestic_code_lst, freq, code_dict)
db.insert_domestic_monthly_economic(dataset_monthly)
