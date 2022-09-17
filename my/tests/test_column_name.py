import unittest
import re


class MyTests(unittest.TestCase):

    def test_column_name(self):

        pre = '^([Ⅰ-ⅩIVX]*)(\.*)(\s*)'
        post = '(\(손실\))*$'

        re_sales = pre + '(수익\(매출액\)|매출|매출액)'
        re_operating_profit = pre + '영업이익' + post
        re_net_income = pre + '(당기순이익|당기순손익|당\(분\)기순이익|분기순이익)' + post

        # print(re.search(re_op, '영업이익'))
        # print(re.search(re_op, 'Ⅴ.영업이익'))

        # print(re.search(re_ni, '당기순이익'))
        # print(re.search(re_ni, 'VI.당기순이익(손실)'))
        # print(re.search(re_ni, 'Ⅹ.당기순이익(손실)'))
        # print(re.search(re_ni, 'Ⅹ.당기순이익(손실)'))
        # print(re.search(re_ni, 'ⅥI.당기순이익(손실)'))
        print(re.search(re_net_income, 'V.분기순이익'))

        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
