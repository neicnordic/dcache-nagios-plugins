import urllib
from ndgfnagios.utils import dmap
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

class PoolgroupInfo(object):
    def __init__(self, name, linkrefs = [], poolrefs = []):
	self.name = name
	self.linkrefs = linkrefs

	self.total_space = None
	self.free_space = None
	self.removable_space = None
	self.precious_space = None
	self.used_space = None

	self.poolrefs = poolrefs

    @property
    def available_space(self):
	return self.removable_space + self.free_space

    @property
    def nonprecious_space(self):
	return self.total_space - self.precious_space

    def __repr__(self):
	return 'PoolgroupInfo(%r, %d, %d, %d, %d, %d, {%s}, {%s})' \
	    %(self.name,
	      self.total_space,
	      self.free_space,
	      self.removable_space,
	      self.precious_space,
	      self.used_space,
	      ', '.join(self.linkrefs),
	      ', '.join(self.poolrefs))

def _scan_metric(metric_elt):
    t = metric_elt.get('type')
    s = metric_elt.text
    if t == 'boolean':
	x = {'true': True, 'false': False}[s]
    elif t == 'integer':
	x = int(s)
    else:
	raise AssertionError('Unsupported type %s.'%t)
    return (metric_elt.get('name'), x)

def load_pools(url):
    fh = urllib.urlopen(url)
    doc = etree.parse(fh)
    for e_p in doc.findall('.//' + DCACHE.pools + '/' + DCACHE.pool):
	name = e_p.get('name')
	metrics = dmap(_scan_metric, e_p.findall(DCACHE.metric))
	p = PoolInfo(name)
	p.enabled = metrics['enabled']
	p.read_only = metrics['read-only']
	p.last_heartbeat = metrics['last-heartbeat']
	p.poolgrouprefs = [e.get('name') for e in
		e_p.findall(DCACHE.poolgroups + '/' + DCACHE.poolgroupref)]
	yield p
    fh.close()

def load_domain_poolnames(info_url):
    fh = urllib.urlopen(info_url + '/domains')
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

def load_domain_of_pool_dict(info_url):
    return dict((pn, dn) for dn, pns in load_domain_poolnames(info_url)
			 for pn in pns)

def load_pools_of_domain_dict(info_url):
    return dict((dn, pns) for dn, pns in load_domain_poolnames(info_url))

def load_poolgroups(url):
    fh = urllib.urlopen(url)
    doc = etree.parse(fh)
    for e_g in doc.findall('.//' + DCACHE.poolgroup):
	name = e_g.get('name')
	linkrefs = [e.get('name') for e in
		    e_g.findall(DCACHE.links + '/' + DCACHE.linkref)]
	poolrefs = [e.get('name') for e in
		    e_g.findall(DCACHE.pools + '/' + DCACHE.poolref)]
	space = dmap(_scan_metric, e_g.findall(DCACHE.space+'/'+DCACHE.metric))
	pg = PoolgroupInfo(name, linkrefs = linkrefs, poolrefs = poolrefs)
	pg.total_space = space['total']
	pg.free_space = space['free']
	pg.removable_space = space['removable']
	pg.precious_space = space['precious']
	pg.used_space = space['used']
	yield pg
    fh.close()
