# -*- coding: utf-8 -*-

"""
"""


def main():

    api_key='98fc399b120769da91658e4b2ef55c4e25f3e303'
    
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

    print(len(corp_list._stock_market))

    from dart_fss.utils import dict_to_html, create_folder
    from dart_fss.errors.errors import NotFoundConsolidated
    import traceback

    # 59 [00651901]에어부산 ?
    # 61 [01325979]세아제강

    try:
        corp = corp_list.find_by_corp_name('세아제강', exactly=True)[0]
        #print(idx, corp)

        import os

        path = os.getcwd()
        path = os.path.join(path, 'fsdata')
        create_folder(path)

        report_tp = 'annual' if corp.info.get('report_tp') is None else corp.info.get('report_tp')
        filename = '{}_{}.xlsx'.format(corp.info.get('corp_code'), report_tp)

        if not os.path.exists(path + '/' + filename):

            all_report_tp = ('annual', 'half', 'quarter')
            all_report_name = ('Annual', 'Semiannual', 'Quarterly')
            all_pblntf_detail_ty = ('A001', 'A002', 'A003')

            reports = corp.search_filings(bgn_de='19000101', page_count=100, last_reprt_at='Y')
            length = len(reports)

            #fs = corp.extract_fs(bgn_de='19000101', report_tp=report_tp)
            #fs.save()

            pass
    except NotFoundConsolidated:
        print('연결재무제표 찾을수 없음')
    except Exception as ex:
        traceback.print_exc()

    pass


if __name__ == '__main__':
    main()
