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

        total_value = int(float(self.account_df.loc[0, '총평가금액'])) + int(float(self.cash))

        # 도넛 중앙에 텍스트 추가
        fig.add_annotation(
            text=f"₩{int(total_value):,}",
            x=0.5, y=0.5,
            font={"size": 25, "color": "black"},
            showarrow=False
        )

        st.plotly_chart(fig)

    def total_assets_doughnut_chart(self, financial_data):
        # 자산 데이터 준비
        asset_data = {
            "현금": financial_data.get("cash", 0),
            "비상금": financial_data.get("emergency_fund", 0),
            "예/적금": financial_data.get("savings", 0),
            "펀드/ETF": financial_data.get("funds", 0),
            "부동산": financial_data.get("real_estate", 0),
            "연금/보험": financial_data.get("pension", 0),
            "코인/기타 자산": financial_data.get("other_assets", 0)
        }
        
        # 0원 이상인 자산만 필터링
        asset_data = {k: v for k, v in asset_data.items() if v > 0}
        
        if not asset_data:
            st.info("자산 정보가 없습니다.")
            return
            
        # plotly
        fig = go.Figure(data=[go.Pie(
            labels=list(asset_data.keys()),
            values=list(asset_data.values()),
            hole=0.65,
            marker={"colors": qualitative.Dark2},
            hovertemplate="%{label}<br>₩%{value:,}<br><extra></extra>"
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

        total_value = sum(asset_data.values())

        # 도넛 중앙에 텍스트 추가
        fig.add_annotation(
            text=f"₩{int(total_value):,}",
            x=0.5, y=0.5,
            font={"size": 25, "color": "black"},
            showarrow=False
        )

        st.plotly_chart(fig)

    def stock_portfolio_doughnut_chart(self):
        """주식 포트폴리오 도넛 차트"""
        if self.stock_df is None or len(self.stock_df) == 0:
            return
            
        # 주식 데이터 준비
        asset_data = {}
        for _, stock in self.stock_df.iterrows():
            asset_data[stock["상품명"]] = float(stock["평가금액"])
        
        # plotly
        fig = go.Figure(data=[go.Pie(
            labels=list(asset_data.keys()),
            values=list(asset_data.values()),
            hole=0.65,
            marker={"colors": qualitative.Dark2},
            hovertemplate="%{label}<br>₩%{value:,}<br><extra></extra>"
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

        total_value = sum(asset_data.values())

        # 도넛 중앙에 텍스트 추가
        fig.add_annotation(
            text=f"₩{int(total_value):,}",
            x=0.5, y=0.5,
            font={"size": 25, "color": "black"},
            showarrow=False
        )

        st.markdown("### 주식 포트폴리오")
        st.plotly_chart(fig)

    def integrated_assets_doughnut_chart(self, financial_data):
        # 탭 생성
        tab1, tab2 = st.tabs(["📊 총 자산 현황", "💰 주식 포트폴리오"])
        
        with tab1:
            # 자산 데이터 준비
            asset_data = {
                "현금": float(financial_data.get("cash", 0)),
                "비상금": float(financial_data.get("emergency_fund", 0)),
                "예/적금": float(financial_data.get("savings", 0)),
                "펀드/ETF": float(financial_data.get("funds", 0)),
                "부동산": float(financial_data.get("real_estate", 0)),
                "연금/보험": float(financial_data.get("pension", 0)),
                "코인/기타 자산": float(financial_data.get("other_assets", 0)),
                "주식": 0.0  # 주식 항목 추가
            }
            
            # 주식 데이터 합산
            if self.stock_df is not None:
                total_stock_value = self.stock_df["평가금액"].astype(float).sum()
                asset_data["주식"] = total_stock_value
            
            # 0원 이상인 자산만 필터링
            asset_data = {k: v for k, v in asset_data.items() if v > 0}
            
            if not asset_data:
                st.info("자산 정보가 없습니다.")
                return
                
            # plotly
            fig = go.Figure(data=[go.Pie(
                labels=list(asset_data.keys()),
                values=list(asset_data.values()),
                hole=0.65,
                marker={"colors": qualitative.Dark2},
                hovertemplate="%{label}<br>₩%{value:,}<br><extra></extra>"
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

            total_value = sum(asset_data.values())

            # 도넛 중앙에 텍스트 추가
            fig.add_annotation(
                text=f"₩{int(total_value):,}",
                x=0.5, y=0.5,
                font={"size": 25, "color": "black"},
                showarrow=False
            )

            st.plotly_chart(fig)
        
        with tab2:
            if self.stock_df is not None and len(self.stock_df) > 0:
                self.stock_portfolio_doughnut_chart()
            else:
                st.info("보유 중인 주식이 없습니다.")
