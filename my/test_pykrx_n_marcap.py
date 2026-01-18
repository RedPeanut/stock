# -*- coding: utf-8 -*-

"""
"""


def main(args=None):

    # tickers = stock.get_market_ticker_list()
    # print(tickers)

    from datetime import datetime, timedelta
    from pykrx.website import krx
    from pykrx import stock
    from pykrx import bond

    nearest_business_day = stock.get_nearest_business_day_in_a_week()
    if isinstance(nearest_business_day, datetime):
        nearest_business_day = krx.datetime2string(nearest_business_day)
    # print('nearest_business_day =', nearest_business_day)

    # pykrx = stock.get_market_cap()
    # print(pykrx)

    # from marcap import marcap_data
    # import datetime

    # next = now = datetime.datetime.now()
    # marcap = marcap_data(next.strftime('%Y-%m-%d'))
    # while len(marcap) <= 0:
    #     next = next + datetime.timedelta(days=-1)
    #     marcap = marcap_data(next.strftime('%Y-%m-%d'))
    # print(marcap)

    # # print(pykrx[pykrx['종목명'] == '엠피씨플러스'])
    # # print(marcap[marcap['Name'] == '엠피씨플러스'])
    pass


if __name__ == '__main__':
    main()
