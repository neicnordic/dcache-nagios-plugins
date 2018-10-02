# coding: utf-8
import math
import re


_measured_re = re.compile(r'([+-]?[0-9.]+(?:[eE]-?[0-9]+)?)[_[:space:]]*(\S+)$')
_unit_by_log1024_size = {
    0: 'B', 1: 'KiB', 2: 'MiB', 3: 'GiB', 4: 'TiB', 5: 'PiB', 6: 'EiB'
}

_size_of_unit = {
    'B': 1,
    'KiB': 1024, 'MiB': 2**20, 'GiB': 2**30, 'TiB': 2**40,
    'PiB': 2**50, 'EiB': 2**60,
    'KB': 1000, 'MB': 10**6, 'GB': 10**9, 'TB': 10**12,
    'PB': 10**15, 'EB': 10**18,
}

_time_of_unit = {
    'ns': 1e-9,
    'μs': 1e-6, 'us': 1e-6,
    'ms': 1e-3,
    's': 1,
    'min': 60,
    'h': 3600,
    'day': 86400, 'days': 86400,
    'week': 604800, 'weeks': 604800}


def size_unit(s):
    try:
        return _size_of_unit[s]
    except KeyError:
        raise ValueError('Invalid unit %s for size.' % s)


def size_float(s):
    mo = re.match(_measured_re, s)
    if mo:
        return float(mo.group(1)) * size_unit(mo.group(2))
    return float(s)


def show_percent(x):
    if x >= 0.1:
        return '%.1f %%' % (x * 100)
    else:
        return '%.3g' % x


def show_time(x):
    if x < 0:
        return '-' + show_time(-x)
    if x == 0:
        return '0'
    if x < 1e-6:
        return '%.3g ns' % (x*1e9)
    if x < 1e-3:
        return '%.3g μs' % (x*1e6)
    if x < 1:
        return '%.3g ms' % (x*1e3)
    if x < 600:
        return '%.3g s' % x
    if x < 36000:
        return '%.3g min' % (x / 60)
    if x < 172800:
        return '%.3g h' % (x / 3600)
    return '%.3g days' % (x / 86400)


def show_size(x):
    if x < 0:
        return '-' + show_size(-x)
    if x == 0:
        return '0'
    n = int(math.log(x) / math.log(1024))
    if n < 0:
        n = 0
    elif n > max(_unit_by_log1024_size):
        n = max(_unit_by_log1024_size)
    u = _unit_by_log1024_size[n]
    return '%.3g %s' % (x / size_unit(u), u)


def split_unit(s):
    if '_' in s:
        v, u = s.split('_', 1)
        return (v, u)
    else:
        for i in range(len(s) - 1, -1, -1):
            if s[i].isdigit() or s[i] == '.':
                return s[:i+1], s[i+1:]
        raise ValueError('split_unit: Missing value.')


def int_of_sizestr(s):
    v, u = split_unit(s)
    if u == '':
        return int(v)
    else:
        return int(_size_of_unit[u] * float(v))


def float_of_timestr(s):
    v, u = split_unit(s)
    if u == '':
        return float(v)
    else:
        return _time_of_unit[u] * float(v)


def float_of_ratiostr(arg):
    if arg[-1] == '%':
        return float(arg[:-1]) * 0.01
    return float(arg)


def counted_noun(count, sing_word, pl_word=None):
    if count == 1:
        return '%d %s' % (count, sing_word)
    return '%d %s' % (count, pl_word or sing_word + 's')
