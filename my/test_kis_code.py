# -*- coding: utf-8 -*-

"""
"""

import subprocess
import sys
import os
from datetime import datetime
import pandas as pd


def should_run_script(file_path):
    if not os.path.exists(file_path):
        return True
    
    mtime = os.path.getmtime(file_path)
    file_date = datetime.fromtimestamp(mtime).date()
    today = datetime.now().date()
    return file_date < today


def main(args=None):
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

    read = pd.read_excel('kospi_code.xlsx')
    print(read)

    pass


if __name__ == '__main__':
    main()