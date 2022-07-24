# -*- coding: utf-8 -*-

"""
"""


def main():

    api_key='98fc399b120769da91658e4b2ef55c4e25f3e303'
    
    # import OpenDartReader
    #
    # odr = OpenDartReader(api_key)
    # odr.corp_codes['stock_code'] = odr.corp_codes['stock_code'].apply(lambda x: x.strip())
    # finstate = dart.finstate('삼성전자', 2012)
    # finstate_all = dart.finstate_all('005930', 2012) #

    import dart_fss as dart
    import dart_fss_classifier
    assert dart_fss_classifier.attached_plugin() == True
    import time
    from my.utils import ( format_time_from_seconds )

    # Open DART API KEY 설정
    dart.set_api_key(api_key=api_key)

    #start_time = time.time()

    # DART 에 공시된 회사 리스트 불러오기
    corp_list = dart.get_corp_list()

    #print('elapsed time = ' + format_time_from_seconds(time.time() - start_time))

    #start_time = time.time()
    # # 삼성전자 검색
    # samsung = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    #
    # # 연간 연결재무제표 불러오기
    # # 2000 ? 2012 o
    # fs = samsung.extract_fs(bgn_de='19000101')
    #
    # print('2.elapsed time = ' + format_time_from_seconds(time.time() - start_time))
    # #start = time.time()
    #
    # # 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
    # fs.save()

    pass


if __name__ == '__main__':
    main()
