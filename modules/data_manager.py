from modules.korea_investment_api import KoreaInvestmentAPI

class DataManager(KoreaInvestmentAPI):
    def __init__(self, KEY, SECRET, acc_no, mock):
        self.stock_file = "data/finance_data.csv"
        self.account_file = "data/account_data.csv"
        self.stock_df, self.account_df = self.load_data(KEY, SECRET, acc_no, mock)

    def load_data(self, KEY, SECRET, acc_no, mock):
        broker = KoreaInvestmentAPI(KEY, SECRET, acc_no, mock)
        stock_df, account_df = broker.get_balance()

        return stock_df, account_df

    def get_stock(self):
        return self.stock_df

    def get_account(self):
        return self.account_df

    def save_data(self):
        self.stock_df.to_csv(self.stock_file, index=False)
        self.account_df.to_csv(self.account_file_file, index=False)
