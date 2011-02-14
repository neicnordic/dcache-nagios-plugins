import os, re, pipes
from config import dcache_web_host, dcache_web_port

class DCacheWeb(object):
    def __init__(self, host = dcache_web_host, port = dcache_web_port):
	self.host = host
	self.port = port

    def popen_lynx(self, url_dir):
	"""Returns a file descriptor to a lynx sub-process which dumps the
	given page as text.  The file descriptor must be closed by the
	caller."""

	url = 'http://%s:%s%s'%(self.host, self.port, url_dir)
	return os.popen('lynx -width 200 -dump %s' % pipes.quote(url))

    def get_pool_group_names(self):
	"""Return the pool group names as a set of strings."""

	fd = self.popen_lynx('/pools/list/PoolManager')
	for ln in fd:
	    if 'Total Space/MB' in ln:
		break
	pools = []
	for ln in fd:
	    mo = re.match('\s*\[\d+\]\s*(\w+)', ln)
	    if not mo:
		break
	    pools.append(mo.group(1))
	fd.close()
	assert len(pools) > 0
	return pools

    def _get_cell_names(self, url_dir):
	fd = self.popen_lynx(url_dir)
	for ln in fd:
	    if 'CellName' in ln and 'DomainName' in ln:
		break
	cell_names = []
	for ln in fd:
	    if '____________________________' in ln:
		break
	    mo = re.match('\s*(\S+)', ln)
	    if not mo:
		break
	    cell_names.append(mo.group(1))
	fd.close()
	assert len(cell_names) > 0
	return cell_names

    def get_cell_names(self):
	"""Returns a set of all cell names."""
	return self._get_cell_names('/cellInfo')

    def get_pool_names(self):
	"""Returns a set of all cell names corresponding to pools."""
	return self._get_cell_names('/usageInfo')
