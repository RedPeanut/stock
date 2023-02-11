# -*- coding: utf-8 -*-

"""
"""


def main(args=None):

    # tickers = stock.get_market_ticker_list()
    # print(tickers)

    from pykrx import stock
    from pykrx import bond

    pykrx = stock.get_market_cap()
    print(pykrx)

    from marcap import marcap_data
    import datetime

    next = now = datetime.datetime.now()
    marcap = marcap_data(next.strftime('%Y-%m-%d'))
    while len(marcap) <= 0:
        next = next + datetime.timedelta(days=-1)
        marcap = marcap_data(next.strftime('%Y-%m-%d'))
    print(marcap)

    # print(pykrx[pykrx['종목명'] == '엠피씨플러스'])
    # print(marcap[marcap['Name'] == '엠피씨플러스'])
    pass


if __name__ == '__main__':
    main()
