# -*- coding: utf-8 -*-

"""
"""

from datetime import datetime, timedelta
import pandas as pd
import my.static
import my.fnguide
import my.utils


def main(args=None):

    class Options:
        def __init__(self):
            self.base = None
            self.target = None
            self.frq = 1
            a_month_ago = datetime.now().replace(day=1) - timedelta(days=1)
            div = int(a_month_ago.month / 3)
            year = a_month_ago.year
            if div == 0:
                year = a_month_ago.year - 1
                nq = 12
            else:
                nq = div * 3
            self.quarter = str(year) + '/' + my.utils.two_digits(nq)
            # self.curr_quarter = self.quarter

    options = Options()

    options.curr_quarter = options.quarter

    year = int(options.quarter.split('/')[0])
    month = int(options.quarter.split('/')[1])
    if month == 3:
        month = 12
        year -= 1
    else:
        month -= 3
    last_quarter = str(year) + '/' + my.utils.two_digits(month)
    options.last_quarter = last_quarter

    # _firm_data = my.static.get_firm_data_v3(Options())['resultData']['resultList']
    # print(_firm_data)
    # _firm_data = _firm_data.iloc[0:1]

    _3s = {
        'Date': [datetime.strptime('2023-07-27', '%Y-%m-%d')],
        'Code': ['060310'],
        'Name': ['3S'],
        'Close': ['2445'],
        'Dept': ['중견기업부'],
        'ChangeCode': ['1'],
        'Changes': ['115'],
        'ChagesRatio': ['4.94'],
        'Volume': ['415472'],
        'Amount': ['1011089765'],
        'Open': ['2320'],
        'High': ['2480'],
        'Low': ['2315'],
        'Marcap': ['118672089690'],
        'Stocks': ['48536642'],
        'Market': ['KOSDAQ'],
        'MarketId': ['KSQ'],
        'Rank': ['1349'],
    }
    _firm_data = pd.DataFrame(_3s, index=_3s['Date'])
    row = _firm_data.iloc[0]

    code = row['Code']
    name = row['Name']

    init_df = pd.DataFrame({
        '종목명': row['Name'],
        '전분기': '',  # insert whether using previous data in here
        '기준일': row['Date'].strftime('%Y-%m-%d'),
        '소속부': row['Dept'],
        '시가총액': row['Marcap'],
        '상장주식수': row['Stocks'],
    }, [code])
    init_df.index.name = '종목코드'

    '''
    재무제표(연간/분기): 
    포괄손익계산서: ['매출액', '매출총이익', '영업이익', '당기순이익']
    재무상태표: ['자산', '유동자산', '비유동자산', '부채', '자본']
    현금흐름표:
    '''
    result = my.fnguide.make_dataframe(
        code,
        0, 1,  # 포괄손익계산서: 재무제표 2번째 테이블
        ['매출액', '매출총이익', '영업이익', '당기순이익'],
        options
    )
    income_state_df = result['resultData']

    result = my.fnguide.make_dataframe(
        code,
        0, 3,  # 재무상태표: 재무제표 4번째 테이블
        ['자산', '유동자산', '비유동자산', '부채', '자본'],
        options
    )
    finance_state_df = result['resultData']

    '''
    재무비율(누적/3개월): 
    - 재무비율 [누적] > 수익성비율: ['영업이익률','ROE', 'ROA','ROIC']
    - 재무비율 [3개월] > 수익성비율: ['영업이익률']
    - 재무비율 [누적] > 성장성비율: //['총자산증가율']
    - 재무비율 [누적] > 안정성비율: ['부채비율', '유동비율']
    '''
    result = my.fnguide.make_dataframe(
        code,
        1, 0,  # [누적]: 재무비율 1번째 테이블
        ['영업이익률','ROE', 'ROA','ROIC', '부채비율', '유동비율'],
        options
    )
    financial_ratio_df = result['resultData']

    '''
    # 투자지표(연간+최근분기): 
    - Multiples: ['PER', 'PBR', 'PCR', 'PSR', 'EV/EBITDA']
    - Dividends: ['배당성향(%)']
    '''
    result = my.fnguide.make_dataframe(
        code,
        2, 3,  # [누적]: 투자지표 4번째 테이블
        ['PER', 'PBR', 'PCR', 'PSR', 'EV/EBITDA', '배당성향(현금)(%)'],
        options
    )
    invest_index_df = result['resultData']

    '''
    # Snapshot
    - Financial Highlight: 배당수익률
    '''
    result = my.fnguide.make_dataframe(
        code,
        4, 15,  # [누적]: Snapshot 16번째 테이블
        ['배당수익률'],
        options
    )
    snapshot_df = result['resultData']

    pass


if __name__ == '__main__':
    main()
