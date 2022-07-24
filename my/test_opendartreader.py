# -*- coding: utf-8 -*-

"""
"""


def main():

    import OpenDartReader

    # ==== 0. 객체 생성 ====
    # 객체 생성 (API KEY 지정)
    api_key = '98fc399b120769da91658e4b2ef55c4e25f3e303'

    dart = OpenDartReader(api_key)
    dart.corp_codes['stock_code'] = dart.corp_codes['stock_code'].apply(lambda x: x.strip())

    '''
    corp_code corp_name stock_code modify_date
    2011   00260985      한빛네트     036720    20170630
    2023   00264529      엔플렉스     040130    20170630
    2024   00358545    동서정보기술     055000    20170630
    2786   00231567     애드모바일     032600    20170630
    3891   00247939       씨모스     037600    20170630
    ...         ...       ...        ...         ...
    94447  00124090      한국특강     007280    20220708
    94457  00985686      큐브엔터     182360    20220412
    94517  00487546     웰크론한텍     076080    20220712
    94518  01594764   신한제9호스팩     405640    20220712
    94520  01020843       엔에스     217820    20220712
    '''

    # # 2015 x 2018
    # finstate = dart.finstate('00124090', 2015)
    # finstate_all = dart.finstate_all('00124090', 2015)
    #finstate = dart.finstate('00260985', 2018)

    # # 삼성전자 상장이후 모든 공시 목록 (5,142 건+)
    #list = dart.list('005930', start='1900')

    # ==== 3. 상장기업 재무정보 ====
    # 2000 x 2008 x 2011 x 2013 x 2014 x 2015 o
    finstate = dart.finstate('삼성전자', 2012) # 사업보고서

    # finstate = dart.finstate('삼성전자', 2015, '')
    # finstate_all = dart.finstate_all('00164742', 2015) # 현대자동차

    # # 삼성전자 2018Q1 재무제표
    # dart.finstate('삼성전자', 2018, reprt_code='11013')

    ## 단일기업 전체 재무제표 (삼성전자 2018 전체 재무제표)
    #dart.finstate_all('005930', 2018)

    pass


if __name__ == '__main__':
    main()


