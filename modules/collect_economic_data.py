import json
import requests
import pandas as pd
import streamlit as st

class collectEconomicData:
    def __init__(self):
        self.api_key = st.secrets["ecos"]["api_key"]

    def daily_domestic(self, start, end, code_lst, freq):
        """ ECOS에서 일별 국내 경제 지표를 수집하는 함수 """
        
        dataset = pd.DataFrame(index=pd.date_range(start, end))
        dataset.index.name = "time"
        for code in code_lst:
            url = f"http://ecos.bok.or.kr/api/StatisticSearch/{self.api_key}/json/kr/1/10000/{code[0]}/{freq}/{start}/{end}/{code[1]}"
            r = requests.get(url)
            jo = json.loads(r.text)
            result = pd.json_normalize(jo['StatisticSearch']['row'])
            data_name = pd.unique(result["ITEM_NAME1"])[0]

            df = result[["TIME", "DATA_VALUE"]]
            df = df.rename(columns={"TIME": "time", "DATA_VALUE": data_name})
            df[data_name] = pd.to_numeric(df[data_name])
            df["time"] = pd.to_datetime(df["time"])
            df = df.set_index("time")
            dataset = dataset.join(df, how="left")

        return dataset

    def monthly_domestic(self, start, end, code_lst, freq):
        """ ECOS에서 월별 국내 경제 지표를 수집하는 함수 """

        dataset = pd.DataFrame(index=pd.date_range(start + "01", end + "01", freq="MS").strftime("%Y%m"))
        dataset.index.name = "time"
        dataset.index = pd.to_datetime(dataset.index, format='%Y%m').to_period('M')

        for code in code_lst:
            url = f"http://ecos.bok.or.kr/api/StatisticSearch/{self.api_key}/json/kr/1/10000/{code[0]}/{freq}/{start}/{end}/{code[1]}"
            r = requests.get(url)
            jo = json.loads(r.text)
            result = pd.json_normalize(jo['StatisticSearch']['row'])
            if code[0] in ("901Y009", "404Y014", "901Y093", "901Y094", "901Y095"):
                data_name = pd.unique(result["STAT_NAME"])[0]
            else:
                data_name = pd.unique(result["ITEM_NAME1"])[0]

            df = result[["TIME", "DATA_VALUE"]]
            df = df.rename(columns={"TIME": "time", "DATA_VALUE": data_name})
            df[data_name] = pd.to_numeric(df[data_name])
            df['time'] = pd.to_datetime(df['time'], format='%Y%m').dt.to_period('M')
            df = df.set_index("time")
            dataset = dataset.join(df, how="left")

        return dataset