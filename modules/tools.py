from langchain.tools import tool
import streamlit as st
from modules.DB import SupabaseDB
import FinanceDataReader as fdr

# 일반 Python 함수 (직접 호출용)
def get_asset_summary_text() -> str:
    user_id = st.session_state.get("id")
    if not user_id:
        return "로그인된 사용자 ID가 없습니다."

    supabase = SupabaseDB()
    user_info = supabase.get_user(user_id)
    if not user_info or "id" not in user_info[0]:
        return "Supabase에서 사용자 정보를 찾을 수 없습니다."

    uid = user_info[0]["id"]
    stocks = supabase.get_stock_data(uid)
    cash = supabase.get_cash_data(uid)
    account = supabase.get_account_data(uid)

    stock_info_str = "\n".join([
        f"- {s['상품명']}, 현재가 {s['현재가']}원, 매입금액 ({s['매입금액']})원 {s['보유수량']}주, 평가금액 {s['평가금액']}원, 등락률 {s['등락률']}%, 평가손익금액 {s['평가손익금액']}원, 평가손익률 {s['평가손익률']}%"
        for s in stocks
    ]) if stocks else "보유 종목 없음"

    account_info_str = (
        f"평가손익합계금액: {account['평가손익합계금액']}, 총 평가금액: {account['총평가금액']}원"
        if account else "계좌 정보 없음"
    )

    return f"""
[사용자 자산 요약]
- 현금 보유액: {cash}원
- {account_info_str}
- 보유 종목:
{stock_info_str}
""".strip()

def get_etf_summary_text() -> str:
    user_id = st.session_state.get("id")
    if not user_id:
        return "❌ 로그인된 사용자 ID가 없습니다."

    supabase = SupabaseDB()
    etf_data = supabase.get_etf_data_json()

    if not etf_data:
        return "❌ 저장된 ETF 데이터가 없습니다."

    summary = "\n\n".join([
        f"📌 {etf_name}:\n" + "\n".join([f"- {k}: {v}" for k, v in etf_info.items()])
        for etf_name, etf_info in etf_data.items()
    ])

    return f"[ETF 요약]\n{summary}"

def get_economic_summary_text() -> str:
    supabase = SupabaseDB()

    daily_data = supabase.client.table("domestic_daily_economic").select("*").order("time", desc=True).limit(5).execute().data
    monthly_data = supabase.client.table("domestic_monthly_economic").select("*").order("time", desc=True).limit(3).execute().data

    if not daily_data and not monthly_data:
        return "❌ 불러올 수 있는 경제 지표 데이터가 없습니다."

    def format_entry(entry):
        return "\n".join([f"- {k}: {v}" for k, v in entry.items() if k != "id"])

    daily_summary = "\n\n".join([f"📅 {d['time']} 일간 지표:\n{format_entry(d)}" for d in daily_data])
    monthly_summary = "\n\n".join([f"🗓️ {m['time']} 월간 지표:\n{format_entry(m)}" for m in monthly_data])

    return f"[최신 경제 지표 요약]\n\n{daily_summary}\n\n{monthly_summary}"



def get_owned_stock_summary_text():
    """보유 종목의 실시간 주가 정보 + 추세/변동성/위치 판단 포함"""
    username = st.session_state.get("id")
    if not username:
        return "❌ 사용자 ID가 없습니다. 로그인 상태를 확인해주세요."

    supabase = SupabaseDB()
    user_info = supabase.get_user(username)
    if not user_info or "id" not in user_info[0]:
        return "❌ 사용자 정보를 Supabase에서 찾을 수 없습니다."

    user_id = user_info[0]["id"]
    stock_data = supabase.get_stock_data(user_id)
    if not stock_data:
        return "현재 보유 중인 주식이 없습니다."

    summary_lines = ["📊 [보유 종목 상세 판단 요약]"]

    for stock in stock_data:
        code = str(stock.get("상품번호")).zfill(6)
        name = stock.get("상품명", f"종목코드 {code}")

        try:
            df = fdr.DataReader(code)
            df = df.sort_index()
            latest = df.iloc[-1]
            close = int(latest['Close'])
            volume = int(latest['Volume'])

            ma20 = int(df['Close'].rolling(window=20).mean().iloc[-1])
            ma60 = int(df['Close'].rolling(window=60).mean().iloc[-1])
            ma120 = int(df['Close'].rolling(window=120).mean().iloc[-1])

            # 이평선 돌파 여부
            above_20 = close > ma20
            above_60 = close > ma60
            above_120 = close > ma120

            if all([above_20, above_60, above_120]):
                ma_trend = "모든 이평선 위에 있음 → 강한 상승 흐름"
            elif not any([above_20, above_60, above_120]):
                ma_trend = "모든 이평선 아래에 있음 → 하락세 지속 가능성"
            else:
                ma_trend = "이평선 위/아래 혼재 → 조정 구간 가능성"

            # 고저점 및 시점
            high_price = int(df['High'].rolling(window=252).max().iloc[-1])
            low_price = int(df['Low'].rolling(window=252).min().iloc[-1])
            high_date = df[df['High'] == high_price].index[-1].strftime("%Y-%m-%d")
            low_date = df[df['Low'] == low_price].index[-1].strftime("%Y-%m-%d")
            high_days_ago = (df.index[-1] - df[df['High'] == high_price].index[-1]).days
            low_days_ago = (df.index[-1] - df[df['Low'] == low_price].index[-1]).days

            # 고저점 대비 등락률
            from_high = round((close - high_price) / high_price * 100, 2)
            from_low = round((close - low_price) / low_price * 100, 2)

            # 최근 5일 상승률
            pct_5d = round((df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100, 2)

            # 거래량 변화율 (오늘 vs 최근 5일 평균)
            vol_mean5 = df['Volume'][-6:-1].mean()
            vol_change_pct = round((volume - vol_mean5) / vol_mean5 * 100, 2)

            # 일일 평균 변동폭 (5일)
            daily_volatility = round(((df['High'] - df['Low']) / df['Low']).rolling(window=5).mean().iloc[-1] * 100, 2)

            # 현재가의 상대 위치 (52주 범위 내 비율)
            relative_pos = round((close - low_price) / (high_price - low_price) * 100, 2)

            summary_lines.append(
                f"{name} ({code})\n"
                f"• 현재가: {close}원, 거래량: {volume} ({vol_change_pct:+.1f}% 변화)\n"
                f"• 최근 5일 수익률: {pct_5d:+.2f}%, 일간 평균 변동폭: ±{daily_volatility:.2f}%\n"
                f"• 이동평균선: MA20={ma20}원 / MA60={ma60}원 / MA120={ma120}원\n"
                f"  ↳ 현재가는 {'위' if above_20 else '아래'}(MA20), "
                f"{'위' if above_60 else '아래'}(MA60), {'위' if above_120 else '아래'}(MA120)\n"
                f"  ↳ 종합 판단: {ma_trend}\n"
                f"• 52주 저점: {low_price}원 ({low_date}, {low_days_ago}일 전)\n"
                f"• 52주 고점: {high_price}원 ({high_date}, {high_days_ago}일 전)\n"
                f"• 고점 대비 {abs(from_high):.2f}% {'하락' if from_high < 0 else '상승'}, 저점 대비 {from_low:.2f}% 상승\n"
                f"• 현재가는 52주 범위 중 {relative_pos:.1f}% 위치\n"
            )



        except Exception as e:
            print(f"⚠️ {code} 시세 데이터 오류: {e}")
            summary_lines.append(
                f"{name} ({code})\n"
                f"• 시세 데이터 조회 실패\n"
            )

    return "\n".join(summary_lines)


# Agent용 Tool (내부에서 위 함수 재사용)

@tool
def get_asset_summary_tool(input_text: str) -> str:
    """
    LangChain Agent에서 호출할 수 있는 자산 요약 Tool입니다.
    (입력값은 무시합니다.)
    """
    return get_asset_summary_text()

@tool
def get_etf_summary_tool(input_text: str) -> str:
    """
    ETF 데이터를 요약해주는 LangChain Tool입니다. (입력값은 무시합니다.)
    """
    return get_etf_summary_text()

@tool
def get_economic_summary_tool(input_text: str) -> str:
    """
    최근 경제 지표 데이터를 요약해주는 LangChain Tool입니다. (입력값은 무시합니다.)
    """
    return get_economic_summary_text()
