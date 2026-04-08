# -*- coding: utf-8 -*-

import subprocess
import sys
import os
from datetime import datetime
import pandas as pd


def should_run_script(file_path) -> bool:
    if not os.path.exists(file_path):
        return True
    
    mtime = os.path.getmtime(file_path)
    file_date = datetime.fromtimestamp(mtime).date()
    today = datetime.now().date()
    return file_date < today


def main(args=None) -> pd.DataFrame:
    '''
    '''

    if should_run_script('kospi_code.xlsx'):
        target_script_kospi = os.path.join("open-trading-api", "stocks_info", "kis_kospi_code_mst.py")
        subprocess.run([sys.executable, target_script_kospi], check=True)
    else:
        print("kospi_code.xlsx is up to date. Skipping kis_kospi_code_mst.py.")

    if should_run_script('kosdaq_code.xlsx'):
        target_script_kosdaq = os.path.join("open-trading-api", "stocks_info", "kis_kosdaq_code_mst.py")
        subprocess.run([sys.executable, target_script_kosdaq], check=True)
    else:
        print("kosdaq_code.xlsx is up to date. Skipping kis_kosdaq_code_mst.py.")

    kospi = pd.read_excel('kospi_code.xlsx')
    kosdaq = pd.read_excel('kosdaq_code.xlsx')
    # print(kospi)

    # sorted(kospi['그룹코드'].unique().tolist())
    # # ['BC', 'DR', 'EF', 'EN', 'FS', 'IF', 'MF', 'PF', 'RT', 'SR', 'ST', 'SW']

    # sorted(kosdaq['증권그룹구분코드'].unique().tolist())
    # # ['DR', 'FS', 'ST']

    # kospi_filtered = kospi[kospi['그룹코드'].isin(['DR','FS','IF','MF','ST'])]
    # kosdaq_filtered = kosdaq[kosdaq['그룹코드'].isin(['DR','FS','IF','MF','ST'])]

    '''
    ST:주권 MF:증권투자회사 RT:부동산투자회사
    SC:선박투자회사 IF:사회간접자본투융자회사
    DR:주식예탁증서 EW:ELW EF:ETF
    SW:신주인수권증권 SR:신주인수권증서
    BC:수익증권 FE:해외ETF FS:외국주권
    '''

    kospi_filtered = kospi[kospi['그룹코드'].isin(['DR','FS','IF','MF','ST'])].copy()

    def get_dept(row):
        # active_status = [
        #     col for col in ['투자주의환기', '거래정지', '정리매매', '관리종목', '경고예고', '불성실공시', '우회상장']
        #     if str(row[col]).strip().upper() == 'Y'
        # ]
        active_status = [
            col for col in ['SPAC', '투자주의환기', '거래정지', '정리매매', '관리종목', '경고예고', '불성실공시', '우회상장']
                if col in row.index and str(row[col]).strip().upper() == 'Y'
        ]
        
        market_warning_map = {
            '1': '투자주의',
            '2': '투자경고',
            '3': '투자위험'
        }
        
        warning_val = str(row['시장경고']).strip()
        
        if warning_val in market_warning_map:
            active_status.append(market_warning_map[warning_val])
        
        return ', '.join(active_status) if active_status else ''
    
    kospi_filtered['Dept'] = kospi_filtered.apply(get_dept, axis=1)

    kospi_result = kospi_filtered[['단축코드', '한글명', 'Dept', '시가총액', '상장주수']].rename(columns={
        '단축코드': 'Code',
        '한글명': 'Name',
        '시가총액': 'Marcap',
        '상장주수': 'Stocks',
    })

    # kosdaq_filtered = kosdaq[kosdaq['증권그룹구분코드'].isin(['DR','FS','ST'])]

    kosdaq_renamed = kosdaq.rename(columns={
        '기업인수목적회사여부': 'SPAC',
        '(코스닥)투자주의환기종목여부': '투자주의환기',
        '거래정지 여부': '거래정지',
        '정리매매 여부': '정리매매',
        '관리 종목 여부': '관리종목',
        '시장 경고위험 예고 여부': '경고예고',
        '불성실 공시 여부': '불성실공시',
        '우회 상장 여부': '우회상장',
        '시장 경고 구분 코드': '시장경고', # 
        '한글종목명': '한글명',
        '전일기준 시가총액 (억)': '시가총액',
        '상장 주수(천)': '상장주수'
    })

    kosdaq_renamed['Dept'] = kosdaq_renamed.apply(get_dept, axis=1)

    kosdaq_result = kosdaq_renamed[['단축코드', '한글명', 'Dept', '시가총액', '상장주수']].rename(columns={
        '단축코드': 'Code',
        '한글명': 'Name',
        '시가총액': 'Marcap',
        '상장주수': 'Stocks',
    })

    # print(kospi_result)
    # print(kosdaq_result)

    # 둘을 합치고 시총(Marcap)순으로 정렬
    combined = pd.concat([kospi_result, kosdaq_result], axis=0, ignore_index=True)
    combined = combined.sort_values(by='Marcap', ascending=False).reset_index(drop=True)

    # print(combined)
    # cwd = os.getcwd()
    # print(f"current directory is {cwd}")
    # combined.to_excel(r'' + cwd + '/tmp.xlsx')
    return combined


if __name__ == '__main__':
    main()