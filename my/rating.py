# -*- coding: utf-8 -*-

def rating(args=None):

    from optparse import OptionParser

    usage = \
'''
'''
    parser = OptionParser(usage=usage)
    parser.add_option('--name',
                      dest='name',
                      default='',
                      help='파일명: YY_NQ_년월일_시분초.xlsx')
    (options, args) = parser.parse_args(args)

    import os
    import pandas as pd
    import numpy as np

    path = os.path.realpath(os.path.abspath(__file__))
    curr_dir = os.path.dirname(path)
    filepath = curr_dir + '/download/' + options.name
    data = pd.read_excel(filepath)
    #filename = os.path.basename(filepath)

    # 전처리
    data['종목코드'] = data['종목코드'].apply(lambda x: '{:06d}'.format(x))

    # 섹터,산업,대표,홈페이지 컬럼 추가
    import FinanceDataReader as fdr
    krx = fdr.StockListing('KRX')
    krx = krx[['Symbol','Sector','Industry','Representative','HomePage']]
    merged = pd.merge(data, krx, how='left', left_on='종목코드', right_on='Symbol')
    merged.insert(merged.columns.get_loc('종목명')+1, '섹터', merged['Sector'], allow_duplicates=False)
    merged.insert(merged.columns.get_loc('섹터')+1, '산업', merged['Industry'], allow_duplicates=False)
    merged.insert(merged.columns.get_loc('산업')+1, '대표', merged['Representative'], allow_duplicates=False)
    merged.insert(merged.columns.get_loc('대표')+1, '홈페이지', merged['HomePage'], allow_duplicates=False)
    merged = merged.drop(['Symbol'], axis=1)
    merged = merged.drop(['Sector'], axis=1)
    merged = merged.drop(['Industry'], axis=1)
    merged = merged.drop(['Representative'], axis=1)
    merged = merged.drop(['HomePage'], axis=1)

    # 중국기업 필터링
    merged = merged.loc[~merged['종목코드'].str.startswith('9')]

    # 종합순위(1/PER+1/PBR+1/PCR+1/PSR)
    merged['GP/A'] = merged['매출총이익']/merged['자산총계']
    merged['1/PER'] = 1/merged['PER']
    merged['1/PER 순위'] = merged['1/PER'].rank(ascending=False)
    merged['1/PBR'] = 1/merged['PBR']
    merged['1/PBR 순위'] = merged['1/PBR'].rank(ascending=False)
    merged['1/PCR'] = 1/merged['PCR']
    merged['1/PCR 순위'] = merged['1/PCR'].rank(ascending=False)
    merged['1/PSR'] = 1/merged['PSR']
    merged['1/PSR 순위'] = merged['1/PSR'].rank(ascending=False)
    merged['종합 순위'] = (merged['1/PER 순위'] + merged['1/PBR 순위'] + merged['1/PCR 순위'] + merged['1/PSR 순위']).rank().sort_values(ascending=True)

    # NCAV
    merged['NCAV'] = (merged['유동자산'] - merged['부채총계']) * 100000000 / merged['시가총액']
    merged['NCAV 순위'] = merged['NCAV'].rank(ascending=False).sort_values()

    # 파일명: YY_NQ_년월일_시분초.xlsx
    import datetime
    name = options.name
    now = datetime.datetime.now()

    # 종합순위
    sorted = merged.sort_values(by='종합 순위', ascending=True)
    sorted.to_excel(curr_dir + '/download/' + name[:5] + '_종합순위_' + now.strftime('%y%m%d_%H%M%S') + '.xlsx')

    # 종합순위+소형주
    tailed = merged.sort_values(by='시가총액', ascending=False).tail(int(len(merged)*0.2))
    #tailed['종합 순위'] = tailed['종합 순위'].rank().sort_values(ascending=True)
    tailed = tailed.sort_values(by='종합 순위', ascending=True)
    tailed.to_excel(curr_dir + '/download/' + name[:5] + '_종합순위(소형주)_' + now.strftime('%y%m%d_%H%M%S') + '.xlsx')

    # # NCAV
    # filter = (merged['유동자산'] - merged['부채총계']) * 100000000 > merged['시가총액'] * 1.0
    # filtered = merged.loc[filter]
    # filter = merged['당기순이익'] > 0
    # filtered = filtered.loc[filter]
    # sorted = filtered.sort_values(by='NCAV 순위', ascending=True)
    # sorted.to_excel(curr_dir + '/download/' + name[:5] + '_NCAV_' + now.strftime('%y%m%d_%H%M%S') + '.xlsx')

    pass


if __name__ == '__main__':
    rating()