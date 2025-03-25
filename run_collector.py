from modules.collect_economic_data import collectEconomicData
from modules.DB import SupabaseDB
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 클래스 초기화
db = SupabaseDB()
collect_economic_data = collectEconomicData()

#------------------ 최근 10년간 일별 국내 데이터 ------------------#
start = (datetime.today() - relativedelta(years=10)).strftime("%Y%m%d")
end = datetime.today().strftime("%Y%m%d")

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
