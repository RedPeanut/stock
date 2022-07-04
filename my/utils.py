# -*- coding: utf-8 -*-



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
