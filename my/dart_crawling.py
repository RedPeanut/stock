# -*- coding: utf-8 -*-

"""
- 220724
페이징 -> 51페이지 x 50개 > 2512
연결재무제표 없는 기업 처리
"""


def dart_crawling(args=None):

    from optparse import OptionParser
    import datetime

    usage = \
        '''
        usage: %prog [options]
        '''

    parser = OptionParser(usage=usage)
    parser.add_option('--page',
                      dest='page',
                      default='1',
                      help='')
    parser.add_option('--size',
                      dest='size',
                      default='50',
                      help='')
    parser.add_option('--report_tp',
                      dest='report_tp',
                      default='quarter',
                      help='annual:연간,half:연간+반기,quarter:연간+반기+분기')
    parser.add_option('--separate',
                      dest='separate',
                      default='T',
                      help='T:연결,F:별도')
    parser.add_option('--bgn_de',
                      dest='bgn_de',
                      default='19000101',
                      help='검색시작일자(YYYYMMDD), 기본값:19000101')
    parser.add_option('--end_de',
                      dest='end_de',
                      default='',
                      help='검색종료일자(YYYYMMDD), 기본값:당일')
    (options, args) = parser.parse_args(args)

    separate = True if options.separate == 'T' else False
    report_tp = options.report_tp
    end_de = datetime.datetime.now().strftime('%y%m%d') if options.end_de == '' else options.end_de
    bgn_de = options.bgn_de

    api_key = '98fc399b120769da91658e4b2ef55c4e25f3e303'

    import dart_fss as dart
    # import dart_fss_classifier
    # assert dart_fss_classifier.attached_plugin() == True

    import time
    from my.utils import ( format_time_from_seconds )

    # Open DART API KEY 설정
    dart.set_api_key(api_key=api_key)

    start_time = time.time()

    # DART 에 공시된 회사 리스트 불러오기
    corp_list = dart.get_corp_list()

    #print(len(corp_list._stock_market))

    from dart_fss.fs import extract_v2
    from dart_fss.utils import dict_to_html, create_folder
    from dart_fss.errors.errors import NotFoundConsolidated
    import traceback
    import os

    page = int(options.page)
    size = int(options.size)
    first_index = (page-1) * size

    for idx, (key, value) in enumerate(corp_list._stock_market.items()):

        if first_index <= idx < first_index + size:

            try:
                corp = corp_list.find_by_stock_code(key)
                print(idx, corp)

                if corp is None:
                    continue

                # separate = False
                path = os.path.join(os.getcwd(), 'fsdata' + ('_개별' if separate is True else '_연결'))
                create_folder(path)

                # report_tp = 'annual' if corp.info.get('report_tp') is None else corp.info.get('report_tp')
                filename = '{}_{}.xlsx'.format(corp.info.get('corp_code'), report_tp)

                if not os.path.exists(path + '/' + filename):
                    fs = extract_v2(corp, bgn_de=bgn_de, end_de=end_de, report_tp=report_tp, separate=separate)
                    fs.save(separate=separate)

            except NotFoundConsolidated:
                # traceback.print_exc()
                print('연결재무제표 찾을수 없음')
                continue
            except Exception as e:
                traceback.print_exc()
                continue
        pass

    print('total elapsed time = ' + format_time_from_seconds(time.time() - start_time))
    pass


if __name__ == '__main__':
    dart_crawling()
