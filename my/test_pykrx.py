# -*- coding: utf-8 -*-

"""
"""


def main(args=None):

    # tickers = stock.get_market_ticker_list()
    # print(tickers)

    from pykrx import stock
    from pykrx import bond

    df = stock.get_market_cap()
    print(df.head())
    pass


if __name__ == '__main__':
    main()
