import streamlit as st
import plotly.graph_objects as go
from plotly.colors import qualitative

class Visualization:
    def __init__(self, stock_df, account_df, cash):
        self.stock_df = stock_df
        self.account_df = account_df
        self.cash = cash

    def portfolio_doughnut_chart(self):
        # label: 상품명, short_label: 축약 상품명, balance: 평가금액
        label = list(self.stock_df["상품명"]) + ["현금(₩)"]
        short_label = list(map(lambda x: x[:10] + "..." if len(x) > 10 else x, list(self.stock_df["상품명"]))) + ["현금(₩)"]
        balance = list(self.stock_df["평가금액"]) + [self.cash]

        # plotly
        fig = go.Figure(data=[go.Pie(
            labels=short_label,
            values=balance,
            hole=0.65,
            customdata=label,
            marker={"colors": qualitative.Dark2},
            hovertemplate="%{customdata}<br>₩%{value:,}<br><extra></extra>"
        )])

        # 크기 및 마진 조정
        fig.update_layout(
            width=500,
            height=500,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            legend={
                "font": {"size": 12},
                "x": 1, "y": 0.9
            }
        )

        total_value = int(float(self.account_df.loc[0, '총평가금액'])) + int(float(st.session_state['cash']))

        # 도넛 중앙에 텍스트 추가
        fig.add_annotation(
            text=f"₩{total_value:,}",
            x=0.5, y=0.5,
            font={"size": 25, "color": "black"},
            showarrow=False
        )

        st.plotly_chart(fig)
