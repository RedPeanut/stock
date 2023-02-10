# -*- coding: utf-8 -*-

"""
"""


def main(args=None):
    import dart_fss as dart
    api_key = '98fc399b120769da91658e4b2ef55c4e25f3e303'
    dart.set_api_key(api_key=api_key)
    corp_list = dart.get_corp_list()

    for idx, (key, value) in enumerate(corp_list._stock_market.items()):
        corp = corp_list.find_by_stock_code(key)
        print(idx, corp)
        pass

    pass


if __name__ == '__main__':
    main()
