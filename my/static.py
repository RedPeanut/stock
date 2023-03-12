# -*- coding: utf-8 -*-

def get_firm_data_v4(options):
    from pykrx import stock
    return stock.get_market_cap()


def get_firm_data_v3(options):
    """ 회사정보 가져오기:
    (기본): 오늘포함 최근 영업일
    base=target일 경우: 익월 첫날부터 역으로
    """

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
    resultList = marcap_data(yyyymmdd)
    while len(resultList) <= 0:
        next = next + datetime.timedelta(days=-1)
        yyyymmdd = next.strftime('%Y-%m-%d')
        resultList = marcap_data(yyyymmdd)

    resultList = resultList.sort_values(by='Name', ascending=True)
    resultList = resultList.reset_index(drop=False)

    result = {'resultCode': 0, 'resultMsg': '', 'resultData': None}
    result['resultCode'] = 0
    result['resultMsg'] = ''
    result['resultData'] = {'resultList': resultList, 'yyyymmdd': yyyymmdd}
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


def make_dataframe(title, url, encparam, code, name, options, ACC_NMs):

    # print('title = ' + title)
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
            n = i + 1
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
                dict[replaced] = DATA[i].get('DATA' + str(n))
                break
        pass

    result['resultCode'] = 0
    result['resultMsg'] = '정상적으로 조회되었습니다.'
    result['resultData'] = pd.DataFrame(dict, [code])
    # result.index.name = options.quarter
    return result