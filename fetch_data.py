import tushare as ts

TS_TOKEN = '9d807d772a4c194d1867b24d57196cbbe28f753402417c19d170b25c'

def get_current_market_value():
    data = ts.get_today_all()


def get_ebit(stock_code):
    ts.set_token(TS_TOKEN)
    pro = ts.pro_api()
    df = pro.income(ts_code = '600000.SH', start_date='20180101', end_date='20180730',
                    fields='ts_code, ann_date, f_ann_date, basic_eps')
    print type(df)

'''
    StockList handles how to get the intended stock list upon stock_type specified.
'''
class StockList(object):
    def __init__(self, stock_type):
        self.stock_type = stock_type

    def get_stock_list(self):
        # all stocks except financial ones
        if stock_type == 'CN_ALL':
            #remove financial stocks
            pass
        elif stock_type == 'HS300':
            #remove financial ones
            pass
        else:
            print 'no such a type!'

        return stock_list


class FinancialData(object):
    def __init__(self, stock_code):
        self.stock_code = stock_code
        self.pro = ts.pro_api(TS_TOKEN)

    '''
        get EBIT
    '''
    def get_income_data(self):
        #df = pro.fina_indicator(ts_code=self.stock_code, start_date='20180101', end_date='20181231',
        #                        fields='ts_code, ann_date, eps, ebit, fcff, fcfe, roic, roe, roa')
        #df = pro.income(ts_code=self.stock_code, start_date='20180101', end_date='20181231',
        #                fields='ts_code, ann_date, end_date, report_type, basic_eps, ebit')
        df = self.pro.income(ts_code=self.stock_code, period='20181231',
                        fields='ts_code, ann_date, end_date, report_type, basic_eps, ebit')
        print df

        return df

    def get_balance_data(self):
        balance_fields = 'ts_code, fix_assets, '
                        + 'accounts_receiv, notes_receiv, oth_receiv, '
        df = self.pro.balancesheet(ts_code=self.stock_code, period='20181231',
                                   fields='ts_code,fix_assets,accounts_receiv, notes_receiv, oth_receiv, prepayment')
        print df
        return df



if __name__ == '__main__':
    #get_current_market_value()
    #get_ebit('600000.SH')
    stock_code = '600352.SH'
    fina_data = FinancialData(stock_code)
    fina_data.get_income_data()
    fina_data.get_balance_data()
    print('aaaaaa')
