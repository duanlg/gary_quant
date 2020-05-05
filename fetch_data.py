#!/anaconda2/bin/python
#coding=utf-8

#from __future__ import unicode_literals
import tushare as ts
import pandas as pd
import time

TS_TOKEN = '9d807d772a4c194d1867b24d57196cbbe28f753402417c19d170b25c'

def get_current_market_cap():
    df = ts.get_today_all()
    return df


'''
    StockList handles how to get the intended stock list upon stock_type specified.
'''
class StockList(object):
    def __init__(self, stock_type):
        self.stock_type = stock_type
        self.pro = ts.pro_api(TS_TOKEN)

    def get_stock_list(self):
        # all stocks except financial ones
        if self.stock_type == 'CN_ALL':
            df = self.pro.stock_basic(exchange='', list_status='L', \
                                      fields='ts_code,symbol,name, area,industry,list_date')
            #remove financial stocks
            df2 = pd.DataFrame(columns = ['ts_code', 'symbol', 'name', 'area', 'industry', 'list_date'])
            for i in range(0, len(df)):
                if df.iloc[i]['industry'] not in [u'银行', u'保险']:
                    df2 = df2.append(df.iloc[i], ignore_index=True)

        elif self.stock_type == 'HS300':
            #remove financial ones
            pass
        else:
            print 'no such a type!'

        return df2

class StockMarket(object):
    def __init__(self, stock_code, trade_date):
        self.stock_code = stock_code
        self.trade_date = trade_date
        self.pro = ts.pro_api(TS_TOKEN)

    def get_total_mkt_val(self):
        # need to get all stocks one time in future for efficiency
        df = self.pro.daily_basic(ts_code=self.stock_code, trade_date=self.trade_date, fields = 'ts_code,total_mv')

        mkt_val = 0
        if len(df) == 0:
            print "WARNING: Cannot get market value for ts_code=%s" % (self.stock_code)
            mkt_val = 0
        else:
            mkt_val = df.iloc[0]['total_mv']

        return mkt_val


class FinancialData(object):
    def __init__(self, stock_code, period):
        self.stock_code = stock_code
        self.period = report_period
        self.pro = ts.pro_api(TS_TOKEN)

    '''
        get EBIT
    '''
    def get_income_data(self):
        try:
            df = self.pro.income(ts_code=self.stock_code, period=self.period,
                        fields='ts_code, ann_date, end_date, report_type, basic_eps, ebit')
        except Exception:
            print "ERROR: exception occurred when get income data for ts_code=%s" % (self.stock_code)
            df = None
        return df

    def get_balance_data(self):
        wc_fields = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' \
                         % ('ts_code,', 'fix_assets,',
                            'accounts_receiv,', 'notes_receiv,', 'oth_receiv,', 'prepayment,', 'inventories,',
                            'lt_eqt_invest,', 'invest_real_estate,',
                            'acct_payable,', 'adv_receipts,', 'payroll_payable,', 'taxes_payable,', 'oth_payable,',
                            'acc_exp,', 'deferred_inc,', 'oth_cur_liab'
                            )
        ent_val_fields = '%s%s%s%s%s%s%s' \
                        % ('minority_int,', 'oth_eqt_tools,',
                           'st_borr,', 'lt_borr,', 'non_cur_liab_due_1y,', 'bond_payable,', 'int_payable' )
        balance_fields = '%s,%s' % (wc_fields, ent_val_fields)

        try:
            df = self.pro.balancesheet(ts_code=self.stock_code, period='20181231',
                                   fields=balance_fields)
        except Exception:
            print "ERROR: exception occurred when get balance data for ts_code=%s" % (self.stock_code)
            df = None
        return df

    '''
        Calculate Capital used in Magic Formula, which equals Net Working Capital + Fixed Assets
    '''
    def get_magic_cap(self, balance_df):
        df = balance_df
        df.fillna(0, inplace=True) # Replace None and NaN if there is

        #not sure why it return 2 records. Will investigate why
        fix_assets = df.iloc[-1]['fix_assets']

        #deferred_inc = 0 if df['deferred_inc'][1] is None else df['deferred_inc'][1]
        #oth_cur_liab = 0 if df['oth_cur_liab'][1] is None else df['oth_cur_liab'][1]
        non_int_cur_liability = df.iloc[-1]['acct_payable'] + df.iloc[-1]['adv_receipts'] \
            +  df.iloc[-1]['payroll_payable'] + df.iloc[-1]['taxes_payable'] + df.iloc[-1]['oth_payable'] \
            +  df.iloc[-1]['acc_exp'] + df.iloc[-1]['deferred_inc'] + df.iloc[-1]['oth_cur_liab']

        nwc = df.iloc[-1]['accounts_receiv'] + df.iloc[-1]['oth_receiv'] + df.iloc[-1]['prepayment'] \
            + df.iloc[-1]['inventories'] + df.iloc[-1]['lt_eqt_invest'] + df.iloc[-1]['invest_real_estate'] \
            - non_int_cur_liability

        magic_cap = fix_assets + nwc

        return magic_cap

    def get_total_int_liability(self, balance_df):
        balance_df.fillna(0, inplace=True)

        total_int_liab = balance_df.iloc[-1]['minority_int'] + balance_df.iloc[-1]['oth_eqt_tools'] \
            + balance_df.iloc[-1]['st_borr'] + balance_df.iloc[-1]['lt_borr'] \
            + balance_df.iloc[-1]['non_cur_liab_due_1y'] + balance_df.iloc[-1]['bond_payable'] \
            + balance_df.iloc[-1]['int_payable']

        return total_int_liab

    def get_ebit(self, income_df):
        #df = FinancialData.get_income_data(self)
        #ebit = income_df['ebit'][-1]
        ebit = income_df.iloc[-1]['ebit']
        return ebit





if __name__ == '__main__':
    #all_mkt_cap = get_current_market_cap()
    #mkt_val = all_mkt_cap[all_mkt_cap.code == '600352'].mktcap
    #print type(mkt_val)

    trade_date = '20190905'
    report_period = '20181231'
    ts_type = 'CN_ALL'

    print "Get list of stocks as per the specified range starting..."

    ts_basic = StockList(ts_type)
    ts_df = ts_basic.get_stock_list()

    print "Calculate ROC and Yield Ratio for each stock starting..."

    ts_df['roc'] = 0  #add a new column for "ROC"
    ts_df['yield_ratio'] = 0 # add a new column for Yield Ratio

    for i in range(0, len(ts_df)):
        stock_code = ts_df.iloc[i]['ts_code']
        print stock_code
        #stock_code = '688321.SH'
        fina_data = FinancialData(stock_code, report_period)
        ebit = 0
        income_df = fina_data.get_income_data()
        if income_df is None:
            ebit = 0
        else:
            ebit = fina_data.get_ebit(income_df)

        magic_cap = 0
        total_int_liab = 0
        balance_df = fina_data.get_balance_data()
        if balance_df is None:
            magic_cap = 0
            total_int_liab = 0
        else:
            magic_cap = fina_data.get_magic_cap(balance_df)
            total_int_liab = fina_data.get_total_int_liability(balance_df)

        # get market value
        ts_market = StockMarket(stock_code, trade_date)
        mkt_val = ts_market.get_total_mkt_val()

        roc = ebit / magic_cap if magic_cap != 0 else 0
        yield_ratio = ebit / (mkt_val + total_int_liab) if (mkt_val + total_int_liab) != 0 else 0

        ts_df.roc.loc[i] = roc
        ts_df.yield_ratio.loc[i] = yield_ratio
        print "INFO: calculate ROC and Yield Ratio for stocks one by one:"
        print ts_df.iloc[i]

        #timeout and error occurs for non-interrupting connection to tushare
        time.sleep(1)

    print "INFO: calculate ROC and Yield Ratio completed"

    #Rank on ROC and Yield_ratio
    ts_df['roc_ranked'] = ts_df['roc'].rank(ascending=0, method='min')
    ts_df['yr_ranked'] = ts_df['yield_ratio'].rank(ascending=0, method='min')

    ts_df['sum_rank'] = ts_df['roc_ranked'] + ts_df['yr_ranked']
    ts_df_sorted = ts_df.sort_values(by='sum_rank', ascending=False)

    print "INFO: Sort by ranking of ROC and Yield Ratio completed"
    print "INFO: Select the first 30 stocks as follows:"
    print ts_df_sorted[0:29]


