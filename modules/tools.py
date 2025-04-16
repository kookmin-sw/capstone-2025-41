from langchain.tools import tool
import streamlit as st
from modules.DB import SupabaseDB

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
        f"- {s['상품명']} ({s['매입금액']}): {s['보유수량']}주, 평가금액 {s['평가금액']}원"
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
    from modules.DB import SupabaseDB
    import streamlit as st

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
    from modules.DB import SupabaseDB

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
