import unittest
import dart_fss


class MyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        import dart_fss_classifier
        assert dart_fss_classifier.attached_plugin() == True

        api_key = '98fc399b120769da91658e4b2ef55c4e25f3e303'
        dart_fss.set_api_key(api_key=api_key)
        cls.corp_list = dart_fss.get_corp_list()

    def setUp(self):
        pass

    def test_page_1(self):

        separate = False
        report_tp = 'quarter'

        from dart_fss.fs import extract
        from dart_fss.utils import create_folder
        from dart_fss.errors.errors import NotFoundConsolidated
        import traceback
        import os

        try:

            # o [00193328]수산인더스트리 / 10
            # o [01442966]마스턴프리미어리츠 / 2
            # x [01180118]코람코더원리츠 / 1 / 연결재무제표 찾을수 없음
            # o [01515323]LG에너지솔루션 /
            # o [01436558]신한서부티엔디리츠
            # o [01576102]미래에셋글로벌리츠
            # o [01596425]SK스퀘어
            # o [01480780]NH올원리츠
            # o [01244601]카카오페이 / 1 /

            # x [01323032]케이카 / 1 /
            # [00972503]일진하이솔루스
            # [00767460]PI첨단소재

            corp = self.corp_list.find_by_corp_name('카카오페이', exactly=True)[0]
            #print(idx, corp)

            # separate = False
            path = os.path.join(os.getcwd(), 'fsdata' + ('_개별' if separate is True else '_연결'))
            create_folder(path)

            # report_tp = 'annual' if corp.info.get('report_tp') is None else corp.info.get('report_tp')
            filename = '{}_{}.xlsx'.format(corp.info.get('corp_code'), report_tp)

            if not os.path.exists(path + '/' + filename):
                fs = extract(corp.corp_code, bgn_de='19000101', report_tp=report_tp, separate=separate)
                fs.save(separate=separate)

            self.assertEqual(1, 1)
            return

        except NotFoundConsolidated:
            traceback.print_exc()
            print('연결재무제표 찾을수 없음')
        except Exception as ex:
            traceback.print_exc()

        self.assertEqual(1, 2)
        return


if __name__ == '__main__':
    unittest.main()
