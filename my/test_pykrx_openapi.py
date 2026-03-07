# -*- coding: utf-8 -*-

"""
"""


def main(args=None):
    from pykrx_openapi import KRXOpenAPI
    client = KRXOpenAPI(api_key="E00D851FA5124A54B28379394C483B204A00DAE1")
    data = client.get_kospi_daily_trade(bas_dd="20260227")
    print(data)
    pass


if __name__ == '__main__':
    main()
