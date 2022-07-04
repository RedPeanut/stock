# -*- coding: utf-8 -*-

"""
"""


def main():

    from optparse import OptionParser

    usage = \
'''
usage: %prog [options]
'''

    parser = OptionParser(usage=usage)
    parser.add_option('--name',
                      dest='name',
                      default='',
                      help='path/to/file/xxx_yymmdd_hhmmss.xlsx')
    (options, args) = parser.parse_args()

    # extract filename and extension

    import os
    fullpath = options.name #'/Users/jkkim/workspace/python/stock/my/download/21_1Q_종합순위_220605_162809.xlsx'
    directory = fullpath[:fullpath.rindex('/')]
    filename, ext = os.path.splitext(os.path.basename(fullpath))

    import FinanceDataReader as fdr
    krx = fdr.StockListing('KRX')

    import pandas as pd
    old = pd.read_excel(fullpath)

    # modify table (add column,...)

    old['종목코드'] = old['종목코드'].apply(lambda x: '{:06d}'.format(x))
    old = old.iloc[:,1:]

    krx = krx[['Symbol','Sector','Industry','Representative']]
    merged = pd.merge(old, krx, how='left', left_on='종목코드', right_on='Symbol')
    merged.insert(merged.columns.get_loc('종목명')+1, '섹터', merged['Sector'], allow_duplicates=False)
    merged.insert(merged.columns.get_loc('섹터')+1, '산업', merged['Industry'], allow_duplicates=False)
    merged.insert(merged.columns.get_loc('산업')+1, '대표', merged['Representative'], allow_duplicates=False)
    merged = merged.drop(['Symbol'], axis=1)
    merged = merged.drop(['Sector'], axis=1)
    merged = merged.drop(['Industry'], axis=1)
    merged = merged.drop(['Representative'], axis=1)

    # overwrite the file
    merged.to_excel(fullpath)

    print('for break...')
    pass


if __name__ == '__main__':
    main()



