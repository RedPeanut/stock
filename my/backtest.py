# -*- coding: utf-8 -*-

"""
TODO:
- 220703
모듈로 변형 -> 노트북에서 활용

- 220702
모멘텀, 추세추종
가격데이터가 없는 종목(거래정지 등)
옵션: 할로윈

네이버 금융 재무제표 반영일 15일?
"""


def main():

    from optparse import OptionParser

    usage = \
'''
usage: %prog [options]
'''
    parser = OptionParser(usage=usage)
    parser.add_option('--start',
                      dest='start',
                      default='',
                      help='YYYY/MM (시작월1일)')
    parser.add_option('--end',
                      dest='end',
                      default='',
                      help='YYYY/MM (종료월말일)')
    parser.add_option('--period',
                      dest='period',
                      default='',
                      help='YYYY/MM~YYYY/MM (시작월1일~종료월말일)')
    parser.add_option('--initial_money',
                      dest='initial_money',
                      default='',
                      help='초기자금(단위:백만원)')
    parser.add_option('--strategy',
                      dest='strategy',
                      default='0',
                      help='1:저평가,2:소형주+저평가,3:NCAV,4:F-Score (/*| 구분자로 조합*/)')
    parser.add_option('--duration',
                      dest='duration',
                      default='H',
                      help='H:활로윈(default),/*Y:매년,M:매월*/,[1-12]:지정한개월수마다 (0: 리밸런싱 안함)')
    parser.add_option('--number',
                      dest='number',
                      default='20',
                      help='종목수(기본:20)')
    parser.add_option('--fee',
                      dest='fee',
                      default='0.015',
                      help='수수료(%)')
    (options, args) = parser.parse_args()

    import datetime

    split = options.period.split('~')
    start_year = int(split[0].split('/')[0])
    start_month = int(split[0].split('/')[1])
    end_year = int(split[1].split('/')[0])
    end_month = int(split[1].split('/')[1])

    duration = int(options.duration)

    y = start_year
    m = start_month

    import os
    import pandas as pd
    from marcap import marcap_data
    #import numpy as np

    path = os.path.realpath(os.path.abspath(__file__))
    curr_dir = os.path.dirname(path)

    #

    UNIT_OF_INITIAL_MONEY = 1000000
    number = int(options.number)

    backtest = None
    total = None

    while m <= end_month and y <= end_year:

        # Rebalance

        portfolio = {}
        stock_amount = 0
        cash_amount = 0

        if backtest is None:
            initial_money = int(options.initial_money) * UNIT_OF_INITIAL_MONEY
        else:
            initial_money = backtest['합계'][-1]

        print('start: ' + str(y) + 'y ' + str(m) + 'm')

        next_m = m + duration
        if next_m > 12:
            next_y = y + 1
            next_m = next_m - 12
        else:
            next_y = y

        if next_m == 1:
            end_m = 12
            end_y = next_y - 1
        else:
            end_m = next_m - 1
            end_y = next_y

        print('end: ' + str(end_y) + 'y ' + str(end_m) + 'm')

        # Load appropriate data file

        # 조회 전분기 엑셀 선택
        # 1 2 3 4 5 6 7 8 9 10 11 12
        # 0 1 2 3 4 5 6 7 8 9 10 11 12
        curr_q = int((m-1)/3)+1
        if curr_q == 1:
            prev_y = str(y - 1)[2:4]
            prev_q = 4
        else:
            prev_y = str(y)[2:4]
            prev_q = curr_q - 1

        #if f'{y[3:4]}_{prev_q}Q_종합순위' in filename:
        findname = '{}_{}Q_종합순위'.format(prev_y, prev_q)

        selected = None
        for i, f in enumerate(os.listdir(curr_dir + '/download')):

            #if i == 9:
                #print('for break...')

            if os.path.isfile(os.path.join(curr_dir + '/download', f)):
                filename, ext = os.path.splitext(os.path.basename(f))
                filename = filename.replace('종합순위', '종합순위') # WTF : 21_1Q_종합순위_220605_162809.xlsx

                if findname in filename and 'xlsx' in ext and not '소형주' in filename:
                    selected = f
                    break

                pass

            pass

        if selected is None:
            raise Exception(findname + ' 엑셀파일을 찾기 못하였습니다.')

        print(selected)

        # Extract stock
        data = pd.read_excel(curr_dir + '/download/' + selected)

        # 전처리
        data['종목코드'] = data['종목코드'].apply(lambda x: '{:06d}'.format(x))

        if y == 2018:
            data = data.drop(data[data['종목코드'] == '069460'].index) # 069460 대호에이엘
            pass
        elif y == 2019:
            data = data.drop(data[data['종목코드'] == '007530'].index) # 007530 영신금속
            # data = data.drop(data[data['종목코드'] == '200350'].index) # 200350 래몽래인
            # data = data.drop(data[data['종목코드'] == '211050'].index) # 211050 인카금융서비스
            data = data.drop(data[data['종목코드'] == '024830'].index) # 024830 세원물산
            pass
        elif y == 2020:
            pass
        elif y == 2021:
            pass
        elif y == 2022:
            data = data.drop(data[data['종목코드'] == '011300'].index) # 011300 성안
            data = data.drop(data[data['종목코드'] == '058450'].index) # 058450 일야
            pass


        # 1:저평가,2:소형주,3:NCAV,4:F-Score (/*| 구분자로 조합*/)
        split = options.strategy.split('|')
        if '1' in split:
            sorted = data.sort_values(by='종합 순위', ascending=True)
        if '2' in split:
            tailed = data.sort_values(by='시가총액', ascending=False).tail(int(len(data)*0.2))
            sorted = tailed.sort_values(by='종합 순위', ascending=True)
        if '3' in split:
            filter = (data['유동자산'] - data['부채총계']) * 100000000 > data['시가총액'] * 1.0
            filtered = data.loc[filter]
            filter = data['당기순이익'] > 0
            filtered = filtered.loc[filter]
            sorted = filtered.sort_values(by='NCAV 순위', ascending=True)
        head = sorted.head(int(options.number))

        # Backtest
        start_date = '{:d}-{:02d}-01'.format(y, m)
        last_day_of_month = [31,28,31,30,31,30,31,31,30,31,30,31]
        end_d = last_day_of_month[m-1]
        end_date = '{:d}-{:02d}-{:02d}'.format(end_y, end_m, end_d)
        price = marcap_data(start_date, end_date)

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
            n = int(initial_money / number / close)
            portfolio[row['종목코드']] = n
            stock_amount += n * close

        cash_amount = initial_money - stock_amount

        if y == 2018:
            pass
        elif y == 2019:
            pass
        elif y == 2020:
            pass
        elif y == 2021:
            pass

        series = 0
        for i, row in head.iterrows():
            #print('{} {} {}'.format(i, row['종목코드'], row['종목명']))
            # if row['종목코드'] in '007530,200350,211050,024830':
            #     print('for break...')
            temp = price.loc[price['Code'] == row['종목코드']]
            filled = (temp['Close'] * portfolio[row['종목코드']]).fillna(method='ffill')
            series = series + filled
            #series = series.fillna(method='ffill')

        backtest = pd.DataFrame({'주식': series})
        backtest['현금'] = [cash_amount] * len(backtest)
        backtest['합계'] = backtest['주식'] + backtest['현금']
        backtest = backtest.dropna()
        #backtest = backtest.fillna(method='ffill')

        if total is None:
            total = backtest
        else:
            total = pd.concat([total[:-1], backtest])

        m = m + duration
        if m > 12:
            y = y + 1
            m = m - 12

        pass

    total['일변화율'] = total['합계'].pct_change()
    total['총변화율'] = total['합계'] / (int(options.initial_money) * UNIT_OF_INITIAL_MONEY) - 1

    # MDD
    max_list = [0]
    mdd_list = [0]

    for i in range(1, len(total[1:])+1):
        index = total.index[i]
        max_list.append(total['총변화율'][:index].max())
        #mdd_list.append(total['총변화율'][index] - max_list[-1])
        if max_list[-1] > max_list[-2]: # 고점 돌파
            #mdd_list.append(total['총변화율'][index] - max_list[-2])
            mdd_list.append(total['일변화율'][index])
            #mdd_list.append(0)
        else: # max_list[-1] <= max_list[-2]: # 고점 대비
            mdd_list.append(total['총변화율'][index] - max_list[-1]) # ?

        # if total.iloc[i]['일변화율'] > total.iloc[i-1]['일변화율']: #
        #     mdd_list.append(total['일변화율'][index])
        # else: # 고정대비 하락
        #     mdd_list.append(total['총변화율'][index] - max_list[-1])
        pass

    total['max'] = max_list
    total['MDD'] = mdd_list

    # Plot
    import matplotlib.pyplot as plt

    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False
    #plt.rcParams['figure.figsize'] = (14,4)
    plt.rcParams['axes.grid'] = True

    plt.figure(figsize=(10, 6))
    #plt.subplot(nrows,ncols,index)
    #fig, axes = plt.subplots(3, 1, constrained_layout=True)
    plt.subplot(211)
    total['총변화율'].plot(title='총변화율')
    plt.subplot(313)
    total['MDD'].plot(title='MDD')

    # plt.subplots_adjust(hspace=3)
    plt.show()

    #print('for break...')
    pass


if __name__ == '__main__':
    main()
