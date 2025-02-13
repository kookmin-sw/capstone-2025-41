import mojito
import pandas as pd

class KoreaInvestmentAPI:
    def __init__(self, KEY, SECRET, acc_no, mock=False):
        self.KEY = KEY
        self.SECRET = SECRET
        self.acc_no = acc_no
        self.broker = mojito.KoreaInvestment(
            api_key = KEY,
            api_secret = SECRET,
            acc_no = acc_no,
            mock = mock
        )

    def get_balance(self):
        resp = self.broker.fetch_balance()
        stock = resp["output1"]
        account = resp["output2"]

        stock_dict = {"bfdy_buy_qty": "전일매수수량", "bfdy_cprs_icdc": "전일대비증감",
                        "bfdy_sll_qty": "전일매도수량", "evlu_amt": "평가금액",
                        "evlu_erng_rt": "평가수익률", "evlu_pfls_amt": "평가손익금액",
                        "evlu_pfls_rt": "평가손익률", "expd_dt": "만기일자",
                        "fltt_rt": "등락률", "grta_rt_name": "보즘금률명",
                        "hldg_qty": "보유수량", "item_mgna_rt_name": "종목증거금률명",
                        "loan_amt": "대출금액", "loan_dt": "대출일자",
                        "ord_psbl_qty": "주문가능수량", "pchs_amt": "매입금액",
                        "pchs_avg_pric": "매입평균가격", "pdno": "상품번호",
                        "prdt_name": "상품명", "prpr": "현재가", "sbst_pric": "대용가격",
                        "stck_loan_unpr": "주식대출단가", "stln_slng_chgs": "대주매각대금",
                        "thdt_buyqty": "금일매수수량", "thdt_sll_qty": "금일매도수량",
                        "trad_dvsn_name": "매매구분명"}

        account_dict = {"asst_icdc_amt": "자산증감액", "asst_icdc_erng_rt": "자산증감수익률",
                        "bfdy_buy_amt": "전일매수금액", "bfdy_sll_amt": "전일매도금액",
                        "bfdy_tlex_amt": "전일제비용금액", "thdt_tlex_amt": "금일제비용금액",
                        "bfdy_tot_asst_evlu_amt": "전일총자산평가금액", "cma_evlu_amt": "CMA평가금액",
                        "d2_auto_rdpt_amt": "D+2자동상환금액", "dnca_tot_amt": "예수금총금액",
                        "evlu_amt_smtl_amt": "평가금액합계금액", "evlu_pfls_smtl_amt": "평가손익합계금액",
                        "fncg_gld_auto_rdpt_yn": "융자금자동상환여부", "nass_amt": "순자산금액",
                        "nxdy_auto_rdpt_amt": "익일자동상환금액", "nxdy_excc_amt": "익일정산금액",
                        "pchs_amt_smtl_amt": "매입금액합계금액", "prvs_rcdl_excc_amt": "가수도정산금액",
                        "scts_evlu_amt": "유가평가금액", "thdt_buy_amt": "금일매수금액",
                        "thdt_sll_amt": "금일매도금액", "tot_evlu_amt": "총평가금액",
                        "tot_loan_amt": "총대출금액", "tot_stln_slng_chgs": "총대주매각대금"}

        stock_df = pd.DataFrame(stock)
        account_df = pd.DataFrame(account)

        stock_df = stock_df.rename(columns=stock_dict)
        account_df = account_df.rename(columns=account_dict)

        stock_df = stock_df[["상품번호", "상품명", "보유수량", "매입금액", "현재가", "평가금액",
                            "평가손익금액", "평가손익률", "등락률"]]

        account_df = account_df[["자산증감액", "자산증감수익률", "총평가금액", "평가손익합계금액"]]

        return stock_df, account_df








