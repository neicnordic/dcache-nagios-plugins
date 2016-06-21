import os, re, pipes
from config import dcache_web_host, dcache_web_port

class DCacheQueryError(Exception):
    pass

class DCacheCell(object):
    def __init__(self, cell_name, domain):
        self.cell_name = cell_name
        self.domain = domain

    def __str__(self):
        return self.cell_name+'/'+self.domain

class DCachePool(DCacheCell):
    _domain_re = re.compile(r'(.*_[a-z]+)_*([0-9]*)Domain$')
    _hostname_re = re.compile(r'([a-z0-9-]+\.)+(dk|fi|no|se|si)')

    def __init__(self, cell_name, domain,
                 total_space_MiB = None, free_space_MiB = None,
                 precious_space_MiB = None):
        DCacheCell.__init__(self, cell_name, domain)
        mo = re.match(self._domain_re, self.domain)
        if not mo:
            raise DCacheQueryError(
                'Cannot deduce host name from domain %s.'%self.domain)
        hostname = mo.group(1).replace('_', '.')
        if not re.match(self._hostname_re, hostname):
            raise DCacheQueryError(
                'Invalid host name or unknown TLD deduced for %s.'%self.domain)
        self.hostname = hostname
        self.pool_number = mo.group(2) and int(mo.group(2)) or 0
        self.total_space_MiB = total_space_MiB
        self.free_space_MiB = free_space_MiB
        self.precious_space_MiB = precious_space_MiB

class DCachePoolgroup(object):
    def __init__(self, poolgroup_name, pools,
                 total_space_MB, free_space_MB, precious_space_MB):
        self.poolgroup_name = poolgroup_name
        self.pools = pools
        self.total_space_MB = total_space_MB
        self.free_space_MB = free_space_MB
        self.precious_space_MB = precious_space_MB

class DCacheWeb(object):
    _poolgroup_re = re.compile(r'\s*\[\d+\](\S+)\s+(\d+)\s+(\d+)\s+(\d+)')
    _poolgroup_pool_re = re.compile(r'\s*(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)')

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

    def _get_cells(self, url_dir, ctor = DCacheCell):
        fd = self.popen_lynx(url_dir)
        for ln in fd:
            if 'CellName' in ln and 'DomainName' in ln:
                break
        cells = []
        for ln in fd:
            if '____________________________' in ln:
                break
            mo = re.match('\s*(\S+)\s+(\S+)', ln)
            if not mo:
                break
            cells.append(ctor(mo.group(1), mo.group(2)))
        fd.close()
        assert len(cells) > 0
        return cells

    def get_cell_names(self):
        """Returns a set of all cell names."""
        return map(lambda cell: cell.cell_name, self._get_cells('/cellInfo'))

    def get_pool_names(self):
        """Returns a set of all cell names corresponding to pools."""
        return map(lambda cell: cell.cell_name, self._get_cells('/usageInfo'))

    def get_pools(self):
        return self._get_cells('/usageInfo', DCachePool)

    def get_poolgroup(self, poolgroup_name):
        fh = self.popen_lynx(
                '/pools/list/PoolManager//%s/spaces'%poolgroup_name)
        found_poolgroup = False
        for ln in fh:
            mo = re.match(self._poolgroup_re, ln)
            if mo and mo.group(1) == poolgroup_name:
                total_space_MB = int(mo.group(2))
                free_space_MB = int(mo.group(3))
                precious_space_MB = int(mo.group(4))
                found_poolgroup = True
                break
        assert found_poolgroup
        for ln in fh:
            if 'CellName' in ln:
                break
        pools = []
        for ln in fh:
            mo = re.match(self._poolgroup_pool_re, ln)
            if mo:
                pool = DCachePool(mo.group(1), mo.group(2),
                                  total_space_MiB = int(mo.group(3)),
                                  free_space_MiB = int(mo.group(4)),
                                  precious_space_MiB = int(mo.group(5)))
                pools.append(pool)
        fh.close()
        return DCachePoolgroup(poolgroup_name, pools,
                               total_space_MB, free_space_MB,
                               precious_space_MB)
