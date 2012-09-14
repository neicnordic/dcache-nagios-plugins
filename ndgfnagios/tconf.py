import os, sys

def parse_error(path, lineno, msg):
    sys.stderr.write('%s:%d: %s\n'%(path, lineno, msg))
    sys.exit(os.EX_DATAERR)

class TconfCustomVisitor(object):
    def __init__(self):
	self.section_name = None
	self.defaults = {}

    def enter_section(self, name, **kwargs):
	self.section_name = name
	self.defaults = kwargs

    def leave_section(self, section_name):
	assert self.section_name == section_name
	self.section_name = None

    def _complete(self, kwargs):
	for k, v in self.defaults.iteritems():
	    if not k in kwargs:
		kwargs[k] = v

    def invoke(self, macro_name, *args, **kwargs):
	self._complete(kwargs)
	getattr(self, macro_name)(self, *args, **kwargs)

    def template(self, name, *formal_args, **formal_kwargs):
	pass

_template_handlers = []
def reg_template_handler(suffix, handler):
    _template_handlers.append((suffix, handler))

class TconfTemplateVisitor(TconfCustomVisitor):

    def __init__(self, template_dirs = ['.'], outfile = sys.stdout):
	TconfCustomVisitor.__init__(self)
	self.template_dirs = template_dirs
	self.outfile = sys.stdout

    def template(self, name, *formal_args, **formal_kwargs):
	found = False
	for dir in self.template_dirs:
	    for suffix, handler in _template_handlers:
		path = os.path.join(dir, name + suffix)
		if os.path.exists(path):
		    found = True
		    break
	if not found:
	    suffixes = map(lambda h: h[0], _template_handlers)
	    raise AttributeError("Cannot find template named %s; scanned dirs "
				 "%s and suffixes %s."
		    %(name, ', '.join(self.template_dirs), ', '.join(suffixes)))
	templ = handler(self, path)
	def f(self, *args, **kwargs):
	    for k, v in formal_kwargs.iteritems():
		if not k in kwargs:
		    kwargs[k] = v
	    for k, v in zip(formal_args, args):
		kwargs[k] = v
	    self.outfile.write(templ(kwargs))
	setattr(self, name, f)

class TconfAccumulatingVisitor(TconfCustomVisitor):
    def __init__(self):
	self.calls = {}

    def invoke(self, macro_name, *args, **kwargs):
	self._complete(kwargs)
	if not macro_name in self.calls:
	    self.calls[macro_name] = []
	self.calls[macro_name].append((args, kwargs))

def _get_args(preargs):
    args = []
    kwargs = {}
    for arg in preargs:
	if ':' in arg:
	    k, v = arg.split(':', 1)
	    kwargs[k] = v
	elif arg[-1] == '?':
	    kwargs[arg[:-1]] = None
	else:
	    args.append(arg)
    return args, kwargs

def load_tconf(path, visitor):
    fh = open(path)
    section_name = None
    lineno = 0
    while True:
	ln = fh.readline()
	if ln == '':
	    break
	lineno += 1
	if ln.isspace() or ln.strip().startswith('#'):
	    continue
	while ln.endswith('\\\n'):
	    lineno += 1
	    ln = ln[:-2] + fh.readline()
	words = ln.split()
	keyword = words[0]
	args, kwargs = _get_args(words[1:])
	if ln[0].isspace():
	    if section_name is None:
		parse_error(path, lineno, 'Missing section directive.')
		continue
	    visitor.invoke(keyword, *args, **kwargs)
	elif keyword == 'section':
	    if not section_name is None:
		visitor.leave_section(section_name)
	    if len(args) != 1:
		parse_error(path, lineno,
		    'The section directive takes a single unnamed argument.')
	    section_name = args[0]
	    visitor.enter_section(section_name, **kwargs)
	elif keyword == 'template':
	    visitor.template(*args, **kwargs)
	else:
	    parse_error('Unknown directive %s or missing indentation before '
			'macro name'%keyword)
    if not section_name is None:
	visitor.leave_section(section_name)
    fh.close()


# Register Template Handlers
#
try:
    import tempita
    def _tempita_handler(self, path):
	templ = tempita.Template.from_filename(path)
	return templ.substitute
    reg_template_handler('.tempita', _tempita_handler)
except ImportError:
    pass

def _interp_handler(self, path):
    fh = open(path)
    templ = fh.read()
    fh.close()
    return lambda kwargs: templ % kwargs
reg_template_handler('.templ', _interp_handler)
