import os
import re
import pipes

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
                 total_space_MiB=None, free_space_MiB=None,
                 precious_space_MiB=None):
        DCacheCell.__init__(self, cell_name, domain)
        mo = re.match(self._domain_re, self.domain)
        if not mo:
            raise DCacheQueryError(
                'Cannot deduce host name from domain %s.' % self.domain)
        hostname = mo.group(1).replace('_', '.')
        if not re.match(self._hostname_re, hostname):
            raise DCacheQueryError(
                'Invalid host name or unknown '
                'TLD deduced for %s.' % self.domain)
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
