# import requests
# import re
from urllib.request import urlopen, Request
# import requests
# from bs4 import BeautifulSoup as bs
import pandas as pd
import traceback


def make_dataframe(code, gb, index, rows, options):
    result = {'resultCode': 0, 'resultMsg': '', 'resultData': None}
    list = pd.read_html(get_html(code, gb))
    df = list[index]
    if type(df.columns) == pd.core.indexes.multi.MultiIndex:
        df.columns = df.columns.droplevel(0)
    df.iloc[:, 0] = df.iloc[:, 0].str.replace('계산에 참여한 계정 펼치기', '')
    df = df.set_index(df.columns[0])

    if options.curr_quarter in df.columns:
        df = df[[options.curr_quarter]]
        pass
    elif options.last_quarter in df.columns:
        result['resultCode'] = 1
        df = df[[options.last_quarter]]
    else:
        result['resultCode'] = -1
        result['resultMsg'] = '조회분기데이터없음, 건너뛰기!'
        return result

    df = df.loc[rows]
    dict = df.T.to_dict('records')[0]
    result['resultMsg'] = '정상적으로 조회되었습니다.'
    result['resultData'] = pd.DataFrame(dict, [code])
    return result


def get_html(code, gb=0):
    """
    :param code: 종목코드
    :param gb: 데이터 종류 (0:재무제표,1:재무비율,2:투자지표,3:컨센서스, 4:Snapshot)
    :return: 
    """
    urls = [
        'SVD_Finance.asp?NewMenuID=103',
        'SVD_FinanceRatio.asp?NewMenuID=103',
        'SVD_Invest.asp?NewMenuID=105',
        'SVD_Consensus.asp?NewMenuID=108',
        'SVD_Main.asp?NewMenuID=101',
    ]

    if gb > 4:
        return None

    url = 'https://comp.fnguide.com/SVO2/ASP/' + urls[gb] \
          + '&gicode=A' + code \
          + '&pGB=1&cID=&MenuYn=Y&ReportGB=&stkGb=701'  # remain params

    try:
        response = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        read = urlopen(response).read()
    except Exception:
        traceback.print_exc()
        return None

    return read


class Fnguide:

    def __init__(self):
        pass

    def make_dataframe(self):
        pass
