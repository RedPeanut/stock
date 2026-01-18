# -*- coding: utf-8 -*-

"""
"""


def main(args=None):
    import FinanceDataReader as fdr
    import datetime

    now = datetime.datetime.now()
    oneWeekAgo = now + datetime.timedelta(days=-7)
    start = oneWeekAgo.strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')

    # 삼성전자로 판단
    df = fdr.DataReader('005930', start, end)
    nearest_business_day = df.index[-1]
    # print(nearest_business_day.strftime('%Y%m%d'))

    # 가장 마지막 값의 날짜(Date) 가 최근 영업일
    # print(df['Date'].iloc[-1])

    krx = fdr.StockListing('KRX')
    krx.insert(0, 'Date', [nearest_business_day for i in range(len(krx))])
    krx = krx.iloc[0:20]
    print(krx)

    # print(type(stock_list.keys()))
    # df = fdr.DataReader(stock_list.keys(), '2026-01-11', '2026-01-18')
    # df.columns = stock_list.values()
    # print(df.head())
    pass


if __name__ == '__main__':
    main()
