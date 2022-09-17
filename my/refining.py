# -*- coding: utf-8 -*-

"""

TODO:
백테스트 편하게
연별? 분기별?

bs: 재무상태표, pl: 손익계산서, cf: 현금흐름표, ce: 자본변동표

PER:
current(전년), v trailing(이전12개월), forward(예상)
손익계산서 - 영업이익, 당기순이익, 주당순이익

PBR:

PCR:

PSR:

"""


def refining(args=None):

    from optparse import OptionParser

    usage = \
        '''
        '''
    parser = OptionParser(usage=usage)
    parser.add_option('--target',
                      dest='target',
                      default='',
                      help='YYYY_NQ')
    (options, args) = parser.parse_args(args)

    import os

    dirname = 'fsdata_일괄'
    # curr_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(dirname):
        print(dirname + ' 디렉토리가 없습니다.')
        return

    # filtered = list(filter(lambda x: x.startswith('2015_4Q'), os.listdir(dirname)))
    # filtered = [e for e in os.listdir(dirname) if lambda x: x.startswith('2015_4Q') and not os.path.isdir(e)]

    filtered = []
    for i, f in enumerate(os.listdir(dirname)):
        if not os.path.isdir(dirname + '/' + f) \
                and f.startswith(options.target):
            filtered.append(f)
            pass
        pass

    map = {
        'BS': {'name': '재무상태표', 'order': 1},
        'PL': {'name': '손익계산서', 'order': 2},
        'CF': {'name': '현금흐름표', 'order': 3},
        'CE': {'name': '자본변동표', 'order': 4},
    }

    # print(filtered)
    filtered.sort(key=lambda x: map[x.split('_')[2]]['order'])
    # print(filtered)

    import pandas as pd
    import tempfile
    import zipfile

    with tempfile.TemporaryDirectory() as extract_path:

        for i, f in enumerate(filtered):

            filepath = os.path.join(dirname, f)
            split = f.split('_')
            yyyy = split[0]
            quarter = split[1]
            alias = split[2]
            filename = split[3]
            print('{} {}'.format(i, f))

            with zipfile.ZipFile(filepath, 'r') as zip_ref:

                if \
                        map[alias]['name'] == '재무상태표' \
                        or map[alias]['name'] == '현금흐름표':

                    for j, info in enumerate(zip_ref.infolist()):

                        history = []
                        curr_total = None
                        prev_total = None
                        prev_prev_total = None

                        # 한글 파일명 인코딩 수정
                        _filename = info.filename.encode('cp437').decode('euc-kr')
                        info.filename = _filename

                        zip_ref.extract(info, extract_path)
                        read = pd.read_csv(extract_path + '/' + info.filename, sep='\t', encoding='cp949')

                        # read['columns'] = read[['회사명', '항목명']].groupby(['회사명'])['항목명'].transform(lambda x: ','.join(str(x)))
                        # read['len'] = read['columns'].apply(lambda x: len(x.split(',')))

                        n = 1
                        first_row = read.iloc[0]
                        company_name = first_row['회사명']
                        # stock_code = first_row['종목코드']
                        # 종목코드(1)	회사명	시장구분	-업종	업종명(5)	결산월	결산기준일	-보고서종류	-통화
                        columns = [read.columns[1]] + [read.columns[2]] + [read.columns[3]] + [read.columns[5]] + [
                            read.columns[6]] + [read.columns[7]]
                        curr = [first_row['종목코드'], first_row['회사명'], first_row['시장구분'], first_row['업종명'],
                                first_row['결산월'], first_row['결산기준일']]
                        prev = curr.copy()
                        prev_prev = curr.copy()

                        import re

                        for column in read.columns:

                            if re.search(r'당기 (1분|반|3분)기 누적', column) \
                                    or re.search(r'전기 (1분|반|3분)기 3개월', column) \
                                    or re.search(r'전기 (1분|반|3분)기 누적', column):
                                read.drop([column], axis='columns', inplace=True)
                                continue

                            if column.startswith('당기'):
                                read.rename(columns={column: '당기'}, inplace=True)
                            elif column.startswith('전기'):
                                read.rename(columns={column: '전기'}, inplace=True)
                            elif column.startswith('전전기'):
                                read.rename(columns={column: '전전기'}, inplace=True)

                        from .utils import is_notebook
                        if is_notebook():
                            from tqdm import tqdm_notebook as tqdm
                        else:
                            from tqdm import tqdm

                        length = len(read)

                        for idx in tqdm(range(length), desc='{} rows'.format(length), unit='rows', disable=False):

                            row = read.iloc[idx]

                            if company_name != row['회사명']:

                                # if company_name == 'GS':
                                #     print('for break...')

                                # print('idx = {}, 회사명 = {}'.format(idx, company_name))
                                # print('stock_code = ' + stock_code)
                                # print('{} {}'.format(n, columns))

                                line = pd.DataFrame(data=[curr], columns=columns)
                                line = line.loc[:, ~line.columns.duplicated()].copy()

                                # line.index.name = '종목코드'
                                if curr_total is None:
                                    curr_total = line
                                else:
                                    curr_total = pd.concat([curr_total, line], ignore_index=True, axis=0)

                                # if idx > 200:
                                #     break

                                company_name = row['회사명']
                                # stock_code = row['종목코드']
                                columns = [read.columns[1]] + [read.columns[2]] + [read.columns[3]] + [read.columns[5]] + [read.columns[6]] + [read.columns[7]]
                                curr = [row['종목코드'], row['회사명'], row['시장구분'], row['업종명'], row['결산월'], row['결산기준일']]
                                prev = curr.copy()
                                prev_prev = curr.copy()

                                n += 1

                            elif idx == len(read) - 1:
                                # print('{} {}'.format(n, columns))
                                line = pd.DataFrame(data=[curr], columns=columns)
                                line = line.loc[:, ~line.columns.duplicated()].copy()
                                curr_total = pd.concat([curr_total, line], ignore_index=True, axis=0)
                                continue

                            # if '이익' in row['항목명'] and row['항목명'] not in history:
                            #     history.append(row['항목명'])
                            #     print(row['항목명'])

                            item_code = row['항목코드']
                            item_name = row['항목명']
                            # item_name = item_name.replace(' ', '')
                            searched = False

                            if map[alias]['name'] == '재무상태표':

                                columns += [item_name]
                                searched = True

                            elif map[alias]['name'] == '손익계산서':

                                if item_code in ['ifrs-full_Revenue', 'ifrs_revenue']:
                                    columns += ['매출액']
                                elif item_code in ['ifrs-full_GrossProfit', 'ifrs_GrossProfit']:
                                    columns += ['매출총이익']
                                elif item_code in ['dart_OperatingIncomeLoss']:
                                    columns += ['영업이익']
                                elif item_code in ['ifrs-full_ProfitLoss', 'ifrs_ProfitLoss']:
                                    columns += ['당기순이익']

                                pass

                            elif map[alias]['name'] == '현금흐름표':

                                columns += [item_name]
                                searched = True

                            if searched:
                                curr += [row['당기']]
                                prev += [row['전기']]
                                prev_prev += [row['전전기']]

                            pass  # end of for idx in tqdm:

                        #
                        curr_total['종목코드'] = curr_total['종목코드'].apply(lambda x: x.replace('[', '').replace(']', ''))
                        curr_total.set_index(keys=['종목코드'])

                        import datetime

                        makedirs = dirname + '/' + yyyy + '_' + quarter
                        if not os.path.exists(makedirs):
                            os.makedirs(makedirs)

                        now = datetime.datetime.now()
                        curr_total.to_excel('{}/{}_{}_{}_{}_{}.xlsx'.format(makedirs, yyyy, quarter,
                                                                            '연결' if '연결' in _filename else '개별',
                                                                            map[alias]['name'],
                                                                            now.strftime('%y%m%d_%H%M%S')))

                        # print('for break...')
                        pass  # end of for j, info in enumerate(zip_ref.infolist()):

                    pass
                elif map[alias]['name'] == '손익계산서':
                    pass

                pass # end of with zipfile...

            # print('for break...')
            pass # end of for i, f in enumerate(filtered):

        pass # end of with tempfile.TemporaryDirectory() as extract_path:

    pass # end of refining()


if __name__ == '__main__':
    refining()
