import sys

class ConfigurationError(Exception):
    pass

def fst(x):
    return x[0]

def snd(x):
    return x[1]

def error_at(path, lineno, msg, *args, **kwargs):
    if args:
	msg = msg%args
    if kwargs:
	msg = msg%kwargs
    sys.stderr('%s:%d: %s'%(path, lineno, msg))

def iter_tabfile(f, path, ncols, space_in_last = False):
    fd = open(path)
    if space_in_last:
	maxsplit = ncols - 1
    else:
	maxsplit = -1
    lineno = 0
    have_error = False
    for ln in fd:
	lineno += 1
	if ln.strip().startswith('#'):
	    continue
	cols = ln.split(None, maxsplit)
	if len(cols) != ncols:
	    error_at(path, lineno, "Expecting %d columns", ncols)
	    have_error = True
	else:
	    f(cols)
    if have_error:
	raise ConfigurationError("Errors found in %s."%path)

def tabfile_as_list(path, ncols, **kwargs):
    xs = []
    iter_tabfile(lambda x: xs.append(x), nclos, **kwargs)
    return xs

def tabfile_as_dict(get_key, get_val, path, ncols, **kwargs):
    m = {}
    def f(cols):
	key = get_key(cols)
	if key in m:
	    raise ConfigurationError("Duplicate key %s."%key)
	m[key] = get_val(cols)
    iter_tabfile(f, path, ncols, **kwargs)
    return m
