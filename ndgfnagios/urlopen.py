import urllib2, httplib

# http://stackoverflow.com/questions/1875052/using-paired-certificates-with-urllib2
class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

def urlopen(url, certkey = None, cert = None):
    if certkey is None or cert is None:
        return urllib2.urlopen(url)
    else:
        opener = urllib2.build_opener(HTTPSClientAuthHandler(certkey, cert))
        return opener.open(url)
