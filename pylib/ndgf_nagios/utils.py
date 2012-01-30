import math, re

def dmap(f, it):
    return dict(map(f, it))

class FreeObject(object):
    def __init__(self, **kwargs):
	for k, v in kwargs.iteritems():
	    setattr(self, k, v)

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

def size_unit(s):
    try:
	return _size_of_unit[s]
    except KeyError:
	raise ValueError('Invalid unit %s for size.'%s)

def size_float(s):
    mo = re.match(_measured_re, s)
    if mo:
	return float(mo.group(1)) * size_unit(mo.group(2))
    return float(s)

def show_size(x):
    if x == 0:
	return '0'
    n = int(math.log(x) / math.log(1024))
    if n < 0:
	n = 0
    elif n > max(_unit_by_log1024_size):
	n = max(_unit_by_log1024_size)
    u = _unit_by_log1024_size[n]
    return '%.3g %s'%(x / size_unit(u), u)

def counted_noun(count, sing_word, pl_word = None):
    if count == 1:
	return '%d %s'%(count, sing_word)
    else:
	return '%d %s'%(count, pl_word or sing_word + 's')
