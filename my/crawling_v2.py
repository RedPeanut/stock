# -*- coding: utf-8 -*-
"""
"""

from datetime import datetime, timedelta
import os
import platform
import time
import threading
import pandas as pd
import my.static
import my.worker
import my.utils


class Crawling:

    """
    """
    # ENABLE_DEBUG = True
    WAIT_TIME = 0.01

    def __init__(self, options):

        self._options = options

        self._time_it_took = 0
        self._successful = 0
        self._running = True

        # self._merged = None
        self._total = None

        from pykrx.website import krx
        from pykrx import stock

        nearest_business_day = stock.get_nearest_business_day_in_a_week()
        if isinstance(nearest_business_day, datetime):
            nearest_business_day = krx.datetime2string(nearest_business_day)
        # print('nearest_business_day =', nearest_business_day)
        self._firm_data = stock.get_market_cap(nearest_business_day)
        df = self._firm_data
        df.reset_index(inplace=True)
        df.rename(columns={
            '티커': 'Code',
            '종목명': 'Name',
            '소속부': 'Dept',
            '종가': 'Close',
            '시가총액': 'Marcap',
            '상장주식수': 'Stocks',
        }, inplace=True)
        df.insert(0, 'Date', [datetime.strptime(nearest_business_day, '%Y%m%d') for i in range(len(df))])
        # self._firm_data = self._firm_data.iloc[0:30]

        # self._firm_data = my.static.get_firm_data_v3(options)['resultData']['resultList']
        # self._firm_data = self._firm_data.iloc[0:20]

        lock = threading.Lock()
        params = (lock, options, self.callback)
        self._workers = [my.worker.Worker(*params) for _ in range(int(options.workers))]
        self.run()

    def run(self):

        self._time_it_took = time.time()

        i = 0

        while self._running:

            # get next item in self._firm_data
            if i < len(self._firm_data):
                row = self._firm_data.iloc[i]
            else:
                row = None

            if row is not None:
                worker = self._get_worker()
                if worker is not None:
                    worker.set_data(row)
                    i += 1
                else:
                    time.sleep(self.WAIT_TIME)
                    continue

            # 더이상 처리할 데이터가 없고 워커들이 일을 모두 끝냈으면
            if row is None and self._jobs_done():
                break

            time.sleep(self.WAIT_TIME)

        # Close all the workers
        for worker in self._workers:
            worker.close()

        # Join and collect
        for worker in self._workers:
            worker.join()
            self._successful += worker.successful

        # self._time_it_took = time.time() - self._time_it_took

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(curr_dir + '/download/', exist_ok=True)
        now = datetime.now()

        split = self._options.quarter.split('/')
        yy = split[0][2:4]
        nq = str(int(int(split[1]) / 3)) + 'Q'
        self._total.to_excel(r'' + curr_dir + '/download/' + yy + '_' + nq + '_' + now.strftime('%y%m%d_%H%M%S') + '.xlsx')

        print('total elapsed time = ' + my.utils.format_time_from_seconds(time.time() - self._time_it_took))

    def callback(self, merged):
        if self._total is None:
            self._total = merged
        else:
            self._total = pd.concat([self._total, merged])

    def _get_worker(self):
        for worker in self._workers:
            if worker.available():
                return worker
        return None

    def _jobs_done(self):
        """Returns True if the workers have finished their jobs else False. """
        for worker in self._workers:
            if not worker.available():
                return False
        return True


if __name__ == '__main__':

    if platform.system() == 'Windows':
        os.system('marcap.bat')
    else:  # Linux, Mac
        os.system('sh marcap.sh')

    from optparse import OptionParser

    usage = \
        '''
        usage: %prog [options]
        '''

    parser = OptionParser(usage=usage)
    parser.add_option('--frq',
                      dest='frq',
                      default='1',
                      help='주기: 0:연간,1(default):분기')
    parser.add_option('--quarter',
                      dest='quarter',
                      default='',
                      help='조회분기: YYYY/MM 형식 (default:빈값,최근분기)')
    parser.add_option('--base',
                      dest='base',
                      default='',
                      help='기준일: target:조회분기 (default:빈값,오늘)')
    parser.add_option('--workers',
                      dest='workers',
                      default='8',
                      help='워커갯수: (default:빈값,8)')
    (options, args) = parser.parse_args()

    if options.quarter is None or options.quarter == '':
        a_month_ago = datetime.now().replace(day=1) - timedelta(days=1)
        div = int(a_month_ago.month / 3)
        year = a_month_ago.year
        if div == 0:
            year = a_month_ago.year - 1
            nq = 12
        else:
            nq = div*3
        options.quarter = str(year) + '/' + my.utils.two_digits(nq)

    options.curr_quarter = options.quarter

    year = int(options.quarter.split('/')[0])
    month = int(options.quarter.split('/')[1])
    if month == 3:
        month = 12
        year -= 1
    else:
        month -= 3
    last_quarter = str(year) + '/' + my.utils.two_digits(month)
    options.last_quarter = last_quarter

    Crawling(options)
