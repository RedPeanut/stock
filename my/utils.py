# -*- coding: utf-8 -*-

# Jupyter Notebook Checker
def is_notebook():
    """ Jupyter Notebook을 사용하는지 확인하는 함수

    Returns
    -------
    bool
        Jupyter Notebook 사용시 True
    """
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:
            return False
    except Exception:
        return False
    return True


def format_time_from_seconds(time):
    
    if time < 0:
        return ''

    secs = int(time) % 60
    mins = int(time / 60) % 60
    hours = int(time / 3600) % 24
    days = int(time / 86400) % 365
    years = int(time / 31536000)
    
    result = ''
    if years > 0:
        result += years + 'y '
    if years > 0 or days > 0:
        result += days + 'd '
    result += two_digits(hours) + ':' + two_digits(mins) + ':' + two_digits(secs)
    
    return result


def two_digits(i):
    if i < 10:
        return '0' + str(i)
    else:
        return str(i)
