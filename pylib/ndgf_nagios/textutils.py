import sys

def print_columnated(ncols, f, xs):
    column_width = 80 / ncols
    padding = column_width*' '
    n = len(xs)
    stride = (n + ncols - 1) / ncols
    xs += [None for i in range(n, ncols*stride)]
    ys = zip(*[xs[j*stride : (j + 1)*stride] for j in range(0, ncols)])
    for cols in ys:
	for col in cols:
	    s = f(col)
	    if len(s) < column_width:
		s += (column_width - len(s))*' '
	    else:
		s = s[0 : column_width - 1] + '|'
	    sys.stdout.write(s)
	sys.stdout.write('\n')
