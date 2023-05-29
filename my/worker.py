# -*- coding: utf-8 -*-
"""
"""

import threading
import time
import traceback
import pandas as pd
import my.static


class Worker(threading.Thread):

    """
    """

    WAIT_TIME = 0.01

    def __init__(self, lock, options, callback):
        super(Worker, self).__init__()
        self.lock = lock
        self.options = options
        self.callback = callback

        self._successful = 0
        self._running = True
        self._data = None

        self.start()

    def run(self):

        while self._running:

            if self._data is not None and isinstance(self._data, pd.Series):

                try:

                    row = self._data
                    code = row['Code']
                    name = row['Name']

                    self._log('{} {} {}'.format(row.name, code, name))

                    encparam = my.static.get_encparam(code)
                    if encparam is None or encparam == '' or encparam is False:
                        self._log('암호키 읽어오기 실패, 건너뛰기!')
                        self._reset()
                        continue

                    init_df = pd.DataFrame({
                        '종목명': row['Name'],
                        '전분기': '', # insert whether using previous data in here
                        '기준일': row['Date'].strftime('%Y-%m-%d'),
                        '소속부': row['Dept'],
                        '시가총액': row['Marcap'],
                        '상장주식수': row['Stocks'],
                    }, [code])
                    init_df.index.name = '종목코드'

                    # 재무분석
                    result = my.static.make_dataframe(
                        '포괄손익계산서',
                        'https://navercomp.wisereport.co.kr/v2/company/cF3002.aspx?rpt=0&finGubun=MAIN&cn=',
                        encparam, code, name, self.options,
                        ['매출액(수익)', '매출총이익', '영업이익', '당기순이익']
                    )

                    if result is None or result['resultCode'] == -1:
                        self._log(result['resultMsg'])
                        self._reset()
                        continue
                    elif result['resultCode'] == 1:
                        init_df['전분기'] = 'v'

                    income_state_df = result['resultData']

                    result = my.static.make_dataframe(
                        '재무상태표',
                        'https://navercomp.wisereport.co.kr/v2/company/cF3002.aspx?rpt=1&finGubun=MAIN&cn=',
                        encparam, code, name, self.options,
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

                    # 투자지표
                    result = my.static.make_dataframe(
                        '수익성',
                        'https://navercomp.wisereport.co.kr/v2/company/cF4002.aspx?rpt=1&finGubun=MAIN&cn=',
                        encparam, code, name, self.options,
                        ['영업이익률', 'ROE', 'ROA', 'ROIC']
                    )
                    profitability_df = result['resultData']

                    result = my.static.make_dataframe(
                        '성장성',
                        'https://navercomp.wisereport.co.kr/v2/company/cF4002.aspx?rpt=2&finGubun=MAIN&cn=',
                        encparam, code, name, self.options,
                        ['총자산증가율']
                    )
                    growth_df = result['resultData']

                    result = my.static.make_dataframe(
                        '안정성',
                        'https://navercomp.wisereport.co.kr/v2/company/cF4002.aspx?rpt=3&finGubun=MAIN&cn=',
                        encparam, code, name, self.options,
                        ['부채비율', '유동비율']
                    )
                    stability_df = result['resultData']

                    result = my.static.make_dataframe(
                        '활동성',
                        'https://navercomp.wisereport.co.kr/v2/company/cF4002.aspx?rpt=5&finGubun=MAIN&cn=',
                        encparam, code, name, self.options,
                        ['PER', 'PBR', 'PCR', 'PSR', 'EV/EBITDA', '현금배당수익률', '현금배당성향(%)']
                    )
                    activity_df = result['resultData']

                    merged = pd.merge(init_df, income_state_df, how='outer', left_index=True, right_index=True)
                    merged = pd.merge(merged, finance_state_df, how='outer', left_index=True, right_index=True)
                    # merged = pd.merge(merged, cs_df, how='outer', left_index=True, right_index=True)
                    merged = pd.merge(merged, growth_df, how='outer', left_index=True, right_index=True)
                    merged = pd.merge(merged, profitability_df, how='outer', left_index=True, right_index=True)
                    merged = pd.merge(merged, stability_df, how='outer', left_index=True, right_index=True)
                    merged = pd.merge(merged, activity_df, how='outer', left_index=True, right_index=True)

                    self._successful += 1
                    self.lock.acquire()
                    self.callback(merged)
                    self.lock.release()
                    self._reset()

                except OSError:
                    self._log('네트워크 끊김, 재시도!')
                except Exception:
                    traceback.print_exc()
                    self._reset()

            time.sleep(self.WAIT_TIME)

        # Call the destructor function of ...

    def close(self):
        """ Clean the worker """
        self._running = False

    @property
    def successful(self):
        """Return the number of successful for current worker. """
        return self._successful

    def _log(self, msg):
        """ This method is used to write the given data in a synchronized way """
        self.lock.acquire()
        print(msg)
        self.lock.release()

    def _reset(self):
        """Reset self._data back to the original state. """
        self._data = None

    def set_data(self, data):
        self._data = data

    def available(self):
        """Return True if the worker has no job else False. """
        return self._data is None
