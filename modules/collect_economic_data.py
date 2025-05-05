import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred
from itertools import product

# .env 파일의 환경 변수 불러오기
load_dotenv()

class collectEconomicData:
    def __init__(self):
        self.ecos_api_key = os.getenv("ECOS_API_KEY")
        self.fred_api_key = os.getenv("FRED_API_KEY")
    def daily_domestic(self, start, end, code_lst, freq, code_dict):
        """ ECOS에서 일별 국내 경제 지표를 수집하는 함수 """
        
        dataset = pd.DataFrame(index=pd.date_range(start, end))
        dataset.index.name = "time"
        for code in code_lst:
            url = f"http://ecos.bok.or.kr/api/StatisticSearch/{self.ecos_api_key}/json/kr/1/10000/{code[0]}/{freq}/{start}/{end}/{code[1]}"
            r = requests.get(url)
            jo = json.loads(r.text)
            result = pd.json_normalize(jo['StatisticSearch']['row'])
            data_name = pd.unique(result["ITEM_NAME1"])[0]

            df = result[["TIME", "DATA_VALUE"]]
            df = df.rename(columns={"TIME": "time", "DATA_VALUE": data_name})
            df[data_name] = pd.to_numeric(df[data_name])
            df["time"] = pd.to_datetime(df["time"])
            df = df.set_index("time")
            df = df.rename(columns=code_dict)
            dataset = dataset.join(df, how="left")

        dataset = dataset.reset_index()
        dataset["time"] = dataset["time"].dt.date

        return dataset

    def monthly_domestic(self, start, end, code_lst, freq, code_dict):
        """ ECOS에서 월별 국내 경제 지표를 수집하는 함수 """

        dataset = pd.DataFrame(index=pd.date_range(start + "01", end + "01", freq="MS").strftime("%Y%m"))
        dataset.index.name = "time"
        dataset.index = pd.to_datetime(dataset.index, format="%Y%m").to_period("M")

        for code in code_lst:
            url = f"http://ecos.bok.or.kr/api/StatisticSearch/{self.ecos_api_key}/json/kr/1/10000/{code[0]}/{freq}/{start}/{end}/{code[1]}"
            r = requests.get(url)
            jo = json.loads(r.text)
            result = pd.json_normalize(jo['StatisticSearch']['row'])
            if code[0] in ("901Y009", "404Y014"):
                data_name = pd.unique(result["STAT_NAME"])[0]
            else:
                data_name = pd.unique(result["ITEM_NAME1"])[0]

            df = result[["TIME", "DATA_VALUE"]]
            df = df.rename(columns={"TIME": "time", "DATA_VALUE": data_name})
            df[data_name] = pd.to_numeric(df[data_name])
            df['time'] = pd.to_datetime(df['time'], format='%Y%m').dt.to_period('M')
            df = df.set_index("time")
            df = df.rename(columns=code_dict)
            dataset = dataset.join(df, how="left")

        dataset = dataset.reset_index()

        return dataset

    def daily_us(self, start, end, code_lst, code_dict):
        """ FRED에서 일별 미국 경제 지표를 수집하는 함수 """

        fred = Fred(api_key=self.fred_api_key)
        dataset = pd.DataFrame(index=pd.date_range(start, end))

        dataset.index.name = "time"
        for code in code_lst:
            df = fred.get_series(code, start).to_frame(code)
            df = df.rename(columns=code_dict)

            dataset = dataset.join(df, how="left")

        dataset = dataset.reset_index()
        return dataset

    def monthly_us(self, start, end, code_lst, code_dict):
        """ FRED에서 월별 미국 경제 지표를 수집하는 함수 """

        fred = Fred(api_key=self.fred_api_key)
        dataset = pd.DataFrame(index=pd.date_range(start, end, freq="MS").to_period("M"))

        dataset.index.name = "time"
        for code in code_lst:
            df = fred.get_series(code, start).to_frame(code)
            df.index.name = "time"
            df.index = pd.to_datetime(df.index, format='%Y-%m').to_period('M')
            df = df.rename(columns=code_dict)

            dataset = dataset.join(df, how="left")

        dataset = dataset.reset_index()
        return dataset

    def real_estate(self, start, end, code_lst, freq):

        dataset = pd.DataFrame(index=pd.date_range(start + "01", end + "01", freq="MS").strftime("%Y%m"))
        dataset.index.name = "time"
        dataset.index = pd.to_datetime(dataset.index, format='%Y%m').to_period('M')

        for code in code_lst:
            url = f"http://ecos.bok.or.kr/api/StatisticSearch/{self.ecos_api_key}/json/kr/1/10000/{code[0]}/{freq}/{start}/{end}/{code[1]}/{code[2]}"
            r = requests.get(url)
            jo = json.loads(r.text)
            result = pd.json_normalize(jo['StatisticSearch']['row'])
            if code[0] in ("901Y009", "404Y014"):
                data_name = pd.unique(result["STAT_NAME"])[0]
            else:
                data_name = pd.unique(result["ITEM_NAME1"])[0]

            df = result[["TIME", "DATA_VALUE"]]
            df = df.rename(columns={"TIME": "time", "DATA_VALUE": data_name})
            df[data_name] = pd.to_numeric(df[data_name])
            df['time'] = pd.to_datetime(df['time'], format='%Y%m').dt.to_period('M')
            df = df.set_index("time")
            dataset = dataset.join(df, how="left", rsuffix=".x")

        dataset = dataset.reset_index()

        list1 = ["sale", "jeon", "month"]  # 매매, 전세, 월세
        list2 = ["apt", "row", "det"]  # 아파트, 연립다세대, 단독주택
        list3 = [
            "S",  # 서울
            "GG",  # 경기
            "IC",  # 인천
            "BS",  # 부산
            "DG",  # 대구
            "GJ",  # 광주
            "DJ",  # 대전
            "US",  # 울산
            "SJ",  # 세종
            "GW",  # 강원
            "CB",  # 충북
            "CN",  # 충남
            "JB",  # 전북
            "JN",  # 전남
            "GB",  # 경북
            "GN",  # 경남
            "JJ"  # 제주
        ]

        # 새로운 컬럼명
        new_col = [f"{a}_{b}_{c}" for a, b, c in product(list1, list2, list3)]
        new_col.insert(0, "time")

        dataset.columns = new_col

        return dataset