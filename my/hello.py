# -*- coding: utf-8 -*-

"""
"""


def main():

    import os
    import pandas as pd
    import numpy as np

    path = os.path.realpath(os.path.abspath(__file__))
    curr_dir = os.path.dirname(path)
    filepath = curr_dir + '/download/22_1Q_220716_011520.xlsx'
    #filepath = curr_dir + '/download/22_2Q_220716_011758.xlsx'
    data = pd.read_excel(filepath)

    data = data.loc[data['PER'] > 1 and data['PBR'] > 0.3]

    pass


if __name__ == '__main__':
    main()
