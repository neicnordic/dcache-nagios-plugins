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

    def find_file(self, fn):
	for dir in self.template_dirs:
	    path = os.path.join(dir, fn)
	    if os.path.exists(path):
		return path
	raise RuntimeError('Cannot find %s in %s.' % (fn, self.template_dirs))

    def get_template(self, name, from_template):
	path = self.find_file(name)
	return from_template.__class__.from_filename(
		    path,
		    namespace = from_template.namespace,
		    get_template = from_template.get_template)

    def template(self, name, *formal_args, **formal_kwargs):
	found = False
	for suffix, handler in _template_handlers:
	    path = self.find_file(name + suffix)
	    if path:
		break
	if path is None:
	    suffixes = map(lambda h: h[0], _template_handlers)
	    raise AttributeError("Cannot find template named %s; scanned dirs "
				 "%s and suffixes %s."
		    %(name, ', '.join(self.template_dirs), ', '.join(suffixes)))
	templ = handler(self, path, get_template = self.get_template)
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

class TconfSection(object):

    def __init__(self, section_name):
	self.section_name = section_name
	self.calls = {}

    def invoke(self, macro_name, *args, **kwargs):
	if not macro_name in self.calls:
	    self.calls[macro_name] = []
	self.calls[macro_name].append((args, kwargs))

class TconfSectionedAccumulatingVisitor(TconfCustomVisitor):
    def __init__(self):
	self.sections = {}
	self._section_name = None

    def enter_section(self, section_name, **kwargs):
	self._section_name = section_name
	self.sections[section_name] = TconfSection(section_name)

    def leave_section(self, section_name):
	self._section_name = None

    def invoke(self, macro_name, *args, **kwargs):
	self.sections[self._section_name].invoke(macro_name, *args, **kwargs)

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
    def _tempita_handler(self, path, get_template = None):
	templ = tempita.Template.from_filename(path, get_template = get_template)
	return templ.substitute
    reg_template_handler('.tempita', _tempita_handler)
except ImportError:
    pass

def _interp_handler(self, path, get_template = None):
    fh = open(path)
    templ = fh.read()
    fh.close()
    return lambda kwargs: templ % kwargs
reg_template_handler('.templ', _interp_handler)
