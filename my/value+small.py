# -*- coding: utf-8 -*-

"""
TODO:
종목가져오기
종합, 종합+소형, NCAV

"""

# def backtest(start_date, end_date, how_many, initial_money):
#     pass

def main():

    from optparse import OptionParser

    usage = \
'''
'''
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    import os
    import pandas as pd
    import numpy as np
    import datetime

    path = os.path.realpath(os.path.abspath(__file__))
    curr_dir = os.path.dirname(path)

    # data_17_4Q = pd.read_excel(curr_dir + '/download/17_4Q_종합순위_220605_162750.xlsx')
    # data_18_4Q = pd.read_excel(curr_dir + '/download/18_4Q_종합순위_220605_162757.xlsx')
    # data_19_4Q = pd.read_excel(curr_dir + '/download/19_4Q_종합순위_220605_163051.xlsx')
    # data_20_4Q = pd.read_excel(curr_dir + '/download/20_4Q_종합순위_220605_162803.xlsx')
    data_21_1Q = pd.read_excel(curr_dir + '/download/21_1Q_종합순위_220605_162809.xlsx')
    # data_21_2Q = pd.read_excel(curr_dir + '/download/21_2Q_종합순위_220605_162821.xlsx')
    data_21_3Q = pd.read_excel(curr_dir + '/download/21_3Q_종합순위_220605_162743.xlsx')
    # data_21_4Q = pd.read_excel(curr_dir + '/download/21_4Q_종합순위_220605_162815.xlsx')
    data_22_1Q = pd.read_excel(curr_dir + '/download/22_1Q_종합순위_220605_162827.xlsx')

    from marcap import marcap_data

    price = marcap_data('2021-01-01', '2022-06-05')
    #filtered = price.loc[price['Code'].isin(code.to_list())]
    total = None

    # 1번째

    #strategry =
    start_date = '2021-05-01'
    end_date = '2021-10-31'
    how_many = 20
    initial_money = 20000000

    filtered = price['2021-05':'2021-10']

    data = data_21_1Q
    data['종목코드'] = data['종목코드'].apply(lambda x: '{:06d}'.format(x))
    tailed = data.sort_values(by='시가총액', ascending=False).tail(int(len(data)*0.2))
    sorted = tailed.sort_values(by='종합 순위', ascending=True)
    head = sorted.head(how_many)
    #code = head['종목코드']

    portfolio = {}
    stock_amount = 0

    for i, row in head.iterrows():
        code = price.loc[price['Code'] == row['종목코드']]

        day = None
        next = start_date
        while day is None:
            try:
                day = code.loc[next]
            except KeyError:
                next = datetime.datetime.strptime(next, '%Y-%m-%d') + datetime.timedelta(days=+1)
                next = next.strftime('%Y-%m-%d')

        close = day['Close']
        n = int(initial_money / how_many / close)
        portfolio[row['종목코드']] = n
        stock_amount += n * close

    cash_amount = initial_money - stock_amount

    series = None
    for i, row in head.iterrows():
        dataframe = filtered.loc[filtered['Code'] == row['종목코드']]
        series = series + dataframe['Close'] * portfolio[row['종목코드']]

    backtest = pd.DataFrame({'주식': series})
    backtest['현금'] = [cash_amount] * len(backtest)
    backtest['합계'] = backtest['주식'] + backtest['현금']
    #backtest['일변화율'] = backtest['합계'].pct_change()
    #backtest['총변화율'] = backtest['합계'] / initial_money - 1

    # # 각종목별 변화율 그려보기
    # backtest = pd.DataFrame()
    # series = 0
    # for i, row in head.iterrows():
    #     dataframe = filtered.loc[filtered['Code'] == row['종목코드']]
    #     series = dataframe['Close'] * portfolio[row['종목코드']]
    #     backtest[row['종목명']] = dataframe['Close'] * portfolio[row['종목코드']]
    #
    # import matplotlib.pyplot as plt
    #
    # plt.rcParams["font.family"] = 'AppleGothic'
    # plt.rcParams['axes.unicode_minus'] = False
    #
    # plt.figure(figsize=(10, 6))
    # backtest.plot()
    # plt.show()
    # return

    if total is None:
        total = backtest
    else:
        total = total.concat([total[:-1], backtest])

    # 2번째
    #strategry =
    start_date = '2021-11-01'
    end_date = '2022-04-30'
    how_many = 20
    initial_money = backtest['합계'][-1]

    filtered = price['2021-11':'2022-04']

    data = data_21_3Q
    data['종목코드'] = data['종목코드'].apply(lambda x: '{:06d}'.format(x))
    tailed = data.sort_values(by='시가총액', ascending=False).tail(int(len(data)*0.2))
    sorted = tailed.sort_values(by='종합 순위', ascending=True)
    head = sorted.head(how_many)

    portfolio = {}
    stock_amount = 0

    for i, row in head.iterrows():
        code = price.loc[price['Code'] == row['종목코드']]

        day = None
        next = start_date
        while day is None:
            try:
                day = code.loc[next]
            except KeyError:
                next = datetime.datetime.strptime(next, '%Y-%m-%d') + datetime.timedelta(days=+1)
                next = next.strftime('%Y-%m-%d')

        close = day['Close']
        n = int(initial_money / how_many / close)
        portfolio[row['종목코드']] = n
        stock_amount += n * close

    cash_amount = initial_money - stock_amount

    series = 0
    for i, row in head.iterrows():
        dataframe = filtered.loc[filtered['Code'] == row['종목코드']]
        series = series + dataframe['Close'] * portfolio[row['종목코드']]

    backtest = pd.DataFrame({'주식': series})
    backtest['현금'] = [cash_amount] * len(backtest)
    backtest['합계'] = backtest['주식'] + backtest['현금']
    #backtest['일변화율'] = backtest['합계'].pct_change()
    #backtest['총변화율'] = backtest['합계'] / initial_money - 1

    if total is None:
        total = backtest
    else:
        total = pd.concat([total[:-1], backtest])

    # 3번째
    #strategry =
    start_date = '2022-05-01'
    #end_date = '2022-10-31'
    how_many = 20
    initial_money = backtest['합계'][-1]

    filtered = price['2022-05':]

    data = data_22_1Q
    data['종목코드'] = data['종목코드'].apply(lambda x: '{:06d}'.format(x))
    tailed = data.sort_values(by='시가총액', ascending=False).tail(int(len(data)*0.2))
    sorted = tailed.sort_values(by='종합 순위', ascending=True)
    head = sorted.head(how_many)

    portfolio = {}
    stock_amount = 0

    for i, row in head.iterrows():
        code = price.loc[price['Code'] == row['종목코드']]

        day = None
        next = start_date
        while day is None:
            try:
                day = code.loc[next]
            except KeyError:
                next = datetime.datetime.strptime(next, '%Y-%m-%d') + datetime.timedelta(days=+1)
                next = next.strftime('%Y-%m-%d')

        close = day['Close']
        n = int(initial_money / how_many / close)
        portfolio[row['종목코드']] = n
        stock_amount += n * close

    cash_amount = initial_money - stock_amount

    series = 0
    for i, row in head.iterrows():
        dataframe = filtered.loc[filtered['Code'] == row['종목코드']]
        series = series + dataframe['Close'] * portfolio[row['종목코드']]

    backtest = pd.DataFrame({'주식': series})
    backtest['현금'] = [cash_amount] * len(backtest)
    backtest['합계'] = backtest['주식'] + backtest['현금']
    #backtest['일변화율'] = backtest['합계'].pct_change()
    #backtest['총변화율'] = backtest['합계'] / initial_money - 1

    if total is None:
        total = backtest
    else:
        total = pd.concat([total[:-1], backtest])

    total['일변화율'] = total['합계'].pct_change()
    total['총변화율'] = total['합계'] / 20000000 - 1

    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    total['총변화율'].plot()
    plt.show()

    pass


if __name__ == '__main__':
    main()
