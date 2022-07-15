# -*- coding: utf-8 -*-

"""
TODO:

- 220703
dart API -> 20년 4분기 이전 데이터 수집

- 220604
v KeyError: 예) 004310 현대약품
v csv로 떨구기
? 로거
> git pull marcap
자동스케쥴링을 위해선?
 스크립트로 작성?
 웹이벤트(스크립트)와의 연결?

- 220529
v GP/A=매출총이익/총자산=(총매출-원가)/총자산
v 영업이익
? 차입금 증가율
v 자산성장률(총자산증가율)
? 주가변동성
"""

""" 회사정보 가져오기:
(기본): 오늘포함 최근 영업일 
base=target일 경우: 익월 첫날부터 역으로
"""
def get_firm_data_v3(options):

    import pandas as pd
    from marcap import marcap_data
    import datetime

    if options.base == 'target':
        split = options.quarter.split('/')
        y = int(split[0])
        m = int(split[1])
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1

        next = datetime.datetime(y, m, 1)
    else:
        next = datetime.datetime.now()

    yyyymmdd = next.strftime('%Y-%m-%d')
    result = marcap_data(yyyymmdd)
    while len(result) <= 0:
        next = next + datetime.timedelta(days=-1)
        yyyymmdd = next.strftime('%Y-%m-%d')
        result = marcap_data(yyyymmdd)

    result = result.sort_values(by='Name', ascending=True)
    result = result.reset_index(drop=False)
    return result


def get_encparam(code):

    import requests
    import re

    url = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=' + code
    resp = requests.get(url)
    search = re.search("encparam: '(.*)'", resp.text)

    if search is None:
        return False

    encparam = search.group(1)
    return encparam


def make_map(split, YYMM):

    """
    [
        {
            q: '2021/03'
            #i: 0,
            n: ,
        },
        ...
    ]
    """

    list = [None] * len(split)
    for i, q in enumerate(split):
        list[i] = {'q':q,'n':None}
    #list = list({q:v,i:i} for i,v in enumerate(split))

    for i,x in enumerate(split):
        for j,y in enumerate(YYMM):
            if x in y:
                list[i]['n'] = j+1
                break
        pass

    map = {}
    for i in range(0, len(split)):
        quarter = split[i]
        for j in range(0, len(YYMM)):
            if quarter in YYMM[j]:
                map[i] = j+1
                break
        pass
    return (list, map)


#
def make_dataframe(title, url, encparam, code, name, options, ACC_NMs):

    #print('title = ' + title)
    # if title == '재무상태표':
    #     print('for break...')

    import requests
    import pandas as pd

    result = {'resultCode': 0, 'resultMsg': '', 'resultData': None}

    url = url + \
          '&encparam=' + encparam + \
          '&frq=' + options.frq + \
          '&frqTyp=' + options.frq + \
          '&cmp_cd=' + code
    headers = {'Referer': 'HACK'}
    resp = requests.get(url, headers=headers)

    json = resp.json()
    YYMM = json.get('YYMM')

    n = None
    for i in range(0, len(YYMM)):
        if options.quarter in YYMM[i]:
            n = i+1
            break

    if n is None:
        result['resultCode'] = -1
        result['resultMsg'] = '조회분기데이터없음, 건너뛰기!'
        return result

    DATA = json.get('DATA')
    if DATA is None:
        result['resultCode'] = -1
        result['resultMsg'] = '데이터조회실패, 건너뛰기!'
        return result

    dict = {}
    for i in range(0, len(DATA)):
        original = DATA[i].get('ACC_NM')
        replaced = DATA[i].get('ACC_NM').replace('.', '')
        for j in range(0, len(ACC_NMs)):
            if \
                    (ACC_NMs[j].startswith('!') == False and replaced == ACC_NMs[j]) \
                    or (ACC_NMs[j].startswith('!') == True and original == ACC_NMs[j].replace('!', '')) \
            :
                dict[replaced] = DATA[i].get('DATA'+str(n))
                break
        pass

    result['resultCode'] = 0
    result['resultMsg'] = '정상적으로 조회되었습니다.'
    result['resultData'] = pd.DataFrame(dict, [code])
    #result.index.name = options.quarter
    return result


def crawling(args=None):

    import os

    os.system('sh marcap.sh')

    import sys
    import time
    import requests
    import pandas as pd
    import traceback
    from optparse import OptionParser

    usage = \
'''
usage: %prog [options]
'''

    parser = OptionParser(usage=usage)
    parser.add_option('--frq',
                      dest='frq',
                      default='1',
                      help='0:연간,1(default):분기')
    parser.add_option('--quarter',
                      dest='quarter',
                      help='YYYY/MM')
    parser.add_option('--base',
                      dest='base',
                      default='',
                      help='기준일: (default)=오늘, target=조회분기')
    (options, args) = parser.parse_args(args)

    merged = None
    total = None

    start = time.time()

    firm_data = get_firm_data_v3(options)

    i = 0
    while i < len(firm_data):

        row = firm_data.iloc[i]

        # if row['Code'] != '004310' and row['Name'] != '현대약품':
        #     continue

        # if i < 60:
        #     i += 1
        #     continue
        #
        # if i >= 65:
        #     break

        code = row['Code']
        name = row['Name']
        #marcap = row['Marcap']

        try:

            print(i, code, name)
            #time.sleep(0.1) #

            encparam = get_encparam(code)
            if encparam == None or encparam == '' or encparam == False:
                print('암호키 읽어오기 실패, 건너뛰기!')
                i += 1
                continue

            """
            Date : 날짜 (DatetimeIndex)
            ? Rank: 시가총액 순위 (당일)
            Code : 종목코드
            Name : 종명이름
            Marcap : 시가총액(백만원?)
            Stocks : 상장주식수
            """

            init_df = pd.DataFrame({
                '종목명': row['Name'],
                '기준일': row['Date'].strftime('%Y-%m-%d'),
                '시가총액': row['Marcap'],
                '상장주식수': row['Stocks']
            }, [code])
            init_df.index.name = '종목코드'

            ## 재무분석

            result = make_dataframe(
                '포괄손익계산서',
                'https://navercomp.wisereport.co.kr/v2/company/cF3002.aspx?rpt=0&finGubun=MAIN&cn=',
                encparam, code, name, options,
                ['매출액(수익)', '매출총이익', '영업이익', '당기순이익']
            )

            if result == None or result['resultCode'] != 0:
                print(result['resultMsg'])
                i += 1
                continue

            income_state_df = result['resultData']

            result = make_dataframe(
                '재무상태표',
                'https://navercomp.wisereport.co.kr/v2/company/cF3002.aspx?rpt=1&finGubun=MAIN&cn=',
                encparam, code, name, options,
                ['자산총계', '!유동자산', '비유동자산', '부채총계', '자본금']
            )
            finance_state_df = result['resultData']

            # result = make_dataframe(
            #     '현금흐름표',
            #     'https://navercomp.wisereport.co.kr/v2/company/cF3002.aspx?rpt=2&finGubun=MAIN&cn=',
            #     encparam, code, name, options,
            #     ['당기순이익']
            # )
            # cash_state_df = result['resultData']

            ## 투자지표

            result = make_dataframe(
                '수익성',
                'https://navercomp.wisereport.co.kr/v2/company/cF4002.aspx?rpt=1&finGubun=MAIN&cn=',
                encparam, code, name, options,
                ['영업이익률', 'ROE', 'ROA', 'ROIC']
            )
            profitability_df = result['resultData']

            result = make_dataframe(
                '성장성',
                'https://navercomp.wisereport.co.kr/v2/company/cF4002.aspx?rpt=2&finGubun=MAIN&cn=',
                encparam, code, name, options,
                ['총자산증가율']
            )
            growth_df = result['resultData']

            result = make_dataframe(
                '안정성',
                'https://navercomp.wisereport.co.kr/v2/company/cF4002.aspx?rpt=3&finGubun=MAIN&cn=',
                encparam, code, name, options,
                ['부채비율', '유동비율']
            )
            stability_df = result['resultData']

            result = make_dataframe(
                '활동성',
                'https://navercomp.wisereport.co.kr/v2/company/cF4002.aspx?rpt=5&finGubun=MAIN&cn=',
                encparam, code, name, options,
                ['PER', 'PBR', 'PCR', 'PSR', 'EV/EBITDA', '현금배당수익률', '현금배당성향(%)']
            )
            activity_df = result['resultData']

            merged = pd.merge(init_df, income_state_df, how='outer', left_index=True, right_index=True)
            merged = pd.merge(merged, finance_state_df, how='outer', left_index=True, right_index=True)
            #merged = pd.merge(merged, cs_df, how='outer', left_index=True, right_index=True)
            merged = pd.merge(merged, growth_df, how='outer', left_index=True, right_index=True)
            merged = pd.merge(merged, profitability_df, how='outer', left_index=True, right_index=True)
            merged = pd.merge(merged, stability_df, how='outer', left_index=True, right_index=True)
            merged = pd.merge(merged, activity_df, how='outer', left_index=True, right_index=True)
            if total is None:
                total = merged
            else:
                total = pd.concat([total, merged])

            i += 1

        except OSError:
            print('네트워크 끊김, 재시도!')
            continue
        # except KeyError:
        #     print('조회분기데이터 없음, 건너뛰기!')
        #     i += 1
        #     continue
        except Exception as e:
            traceback.print_exc()
            i += 1
            continue

    # data = total
    #
    # # 중국기업 필터링
    # data = data.loc[~data.index.str.startswith('9')]
    #
    # # 종합순위(1/PER+1/PBR+1/PCR+1/PSR)
    # data['GP/A'] = data['매출총이익']/data['자산총계']
    # data['1/PER'] = 1/data['PER']
    # data['1/PER 순위'] = data['1/PER'].rank(ascending=False)
    # data['1/PBR'] = 1/data['PBR']
    # data['1/PBR 순위'] = data['1/PBR'].rank(ascending=False)
    # data['1/PCR'] = 1/data['PCR']
    # data['1/PCR 순위'] = data['1/PCR'].rank(ascending=False)
    # data['1/PSR'] = 1/data['PSR']
    # data['1/PSR 순위'] = data['1/PSR'].rank(ascending=False)
    # data['종합 순위'] = (data['1/PER 순위'] + data['1/PBR 순위'] + data['1/PCR 순위'] + data['1/PSR 순위']).rank().sort_values(ascending=True)
    #
    # # NCAV
    # data['NCAV'] = (data['유동자산'] - data['부채총계']) * 100000000 / data['시가총액']
    # data['NCAV 순위'] = data['NCAV'].rank(ascending=False).sort_values()
    #
    # sorted = data.sort_values(by='종합 순위', ascending=True)

    import os
    import datetime
    from my.utils import ( format_time_from_seconds )

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(curr_dir + '/download/', exist_ok=True)
    now = datetime.datetime.now()

    split = options.quarter.split('/')
    yy = split[0][2:4]
    nq = str(int(int(split[1])/3))+'Q'
    total.to_excel(r'' + curr_dir + '/download/' + yy + '_' + nq + '_' +  now.strftime('%y%m%d_%H%M%S') + '.xlsx')

    print('total elapsed time = ' + format_time_from_seconds(time.time() - start))
    pass


if __name__ == '__main__':
    crawling()
