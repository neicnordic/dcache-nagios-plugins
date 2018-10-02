from dcache_nagios_plugins.urlopen import urlopen
try: from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

# The full XML data is available from /info.  The document is wrappend in
# dCache.  Subelements can also be fetched independently under a sub-URL
# composed from the element names, at least down to a certain level.  The
# toplevel elements are:
#
#     doors
#     summary
#     linkgroups
#     unitgroups
#     domains
#     links
#     nas
#     pools
#     units
#     reservations
#     poolgroups

class DCacheTags(object):
    def __getattr__(self, name):
        return '{http://www.dcache.org/2008/01/Info}' + name
DCACHE = DCacheTags()

class PoolInfo(object):
    def __init__(self, name):
        self.name = name
        self.enabled = None
        self.read_only = None
        self.last_heartbeat = None
        self.poolgrouprefs = []
        self.space_total = None
        self.space_break_even = None
        self.space_precious = None
        self.space_removable = None
        self.space_gap = None
        self.space_LRU_seconds = None
        self.space_used = None
        self.space_free = None


class PoolgroupInfo(object):
    def __init__(self, name, linkrefs=None, poolrefs=None):
        self.name = name
        self.linkrefs = linkrefs or []

        self.space_total = None
        self.space_free = None
        self.space_removable = None
        self.space_precious = None
        self.space_used = None

        self.poolrefs = poolrefs or []

    @property
    def available_space(self):
        return self.space_removable + self.space_free

    @property
    def nonprecious_space(self):
        return self.space_total - self.space_precious

    def __repr__(self):
        return 'PoolgroupInfo(%r, %d, %d, %d, %d, %d, {%s}, {%s})' \
            % (self.name,
               self.space_total,
               self.space_free,
               self.space_removable,
               self.space_precious,
               self.space_used,
               ', '.join(self.linkrefs),
               ', '.join(self.poolrefs))

def _scan_metric(metric_elt):
    t = metric_elt.get('type')
    s = metric_elt.text
    if t == 'boolean':
        x = {'true': True, 'false': False}[s]
    elif t == 'integer':
        x = int(s)
    elif t == 'float':
        x = float(s)
    else:
        raise AssertionError('Unsupported type %s.'%t)
    return (metric_elt.get('name'), x)

def load_pools(url, certkey=None, cert=None):
    fh = urlopen(url, certkey = certkey, cert = cert)
    doc = etree.parse(fh)
    for e_p in doc.findall('.//' + DCACHE.pools + '/' + DCACHE.pool):
        name = e_p.get('name')
        metrics = dict(map(_scan_metric, e_p.findall(DCACHE.metric)))
        p = PoolInfo(name)
        p.enabled = metrics.get('enabled')
        p.read_only = metrics.get('read-only')
        p.last_heartbeat = metrics.get('last-heartbeat')
        p.poolgrouprefs = [e.get('name') for e in
                e_p.findall(DCACHE.poolgroups + '/' + DCACHE.poolgroupref)]
        e_space = e_p.find(DCACHE.space)
        if e_space:
            space_metrics = dict(map(_scan_metric, e_space.findall(DCACHE.metric)))
            p.space_total = space_metrics.get('total')
            p.space_break_even = space_metrics.get('break-even')
            p.space_precious = space_metrics.get('precious')
            p.space_removable = space_metrics.get('removable')
            p.space_gap = space_metrics.get('gap')
            p.space_LRU_seconds = space_metrics.get('LRU-seconds')
            p.space_used = space_metrics.get('used')
            p.space_free = space_metrics.get('free')
        yield p
    fh.close()

def load_pool(url, certkey = None, cert = None):
    pools = list(load_pools(url, certkey = certkey, cert = cert))
    if len(pools) == 1:
        return pools[0]
    elif len(pools) == 0:
        return None
    else:
        raise RuntimeError('Request for single pool gave %d results.' % len(pools))

def load_domain_poolnames(info_url, certkey=None, cert = None):
    fh = urlopen(info_url + '/domains', certkey = certkey, cert = cert)
    doc = etree.parse(fh)
    for domain_ele in doc.findall(DCACHE.domains + '/' + DCACHE.domain):
        dn = domain_ele.get('name')
        pns = set()
        for pool_ele in domain_ele.findall(DCACHE.cells + '/' + DCACHE.cell):
            for metric_ele in pool_ele.findall(DCACHE.metric):
                if metric_ele.get('name') == 'class':
                    if metric_ele.text == 'Pool':
                        pns.add(pool_ele.get('name'))
                    break
        if len(pns) > 0:
            yield dn, pns
    fh.close()

def load_domain_of_pool_dict(info_url, certkey = None, cert = None):
    data = load_domain_poolnames(info_url, certkey = certkey, cert = cert)
    return dict((pn, dn) for dn, pns in data for pn in pns)

def load_pools_of_domain_dict(info_url, certkey = None, cert = None):
    data = load_domain_poolnames(info_url, certkey = certkey, cert = cert)
    return dict((dn, pns) for dn, pns in data)

def load_poolgroups(url, certkey = None, cert = None):
    fh = urlopen(url, certkey = certkey, cert = cert)
    doc = etree.parse(fh)
    for e_g in doc.findall('.//' + DCACHE.poolgroup):
        name = e_g.get('name')
        linkrefs = [e.get('name') for e in
                    e_g.findall(DCACHE.links + '/' + DCACHE.linkref)]
        poolrefs = [e.get('name') for e in
                    e_g.findall(DCACHE.pools + '/' + DCACHE.poolref)]
        space = dict(map(_scan_metric, e_g.findall(DCACHE.space+'/'+DCACHE.metric)))
        pg = PoolgroupInfo(name, linkrefs = linkrefs, poolrefs = poolrefs)
        pg.space_total = space['total']
        pg.space_free = space['free']
        pg.space_removable = space['removable']
        pg.space_precious = space['precious']
        pg.space_used = space['used']
        yield pg
    fh.close()

def load_poolgroup(url, certkey = None, cert = None):
    poolgroups = list(load_poolgroups(url, certkey = certkey, cert = cert))
    if len(poolgroups) == 1:
        return poolgroups[0]
    elif len(poolgroups) == 0:
        return None
    else:
        raise RuntimeError('Request for a single pool group gave %d entries.'
                           % len(poolgroups))
