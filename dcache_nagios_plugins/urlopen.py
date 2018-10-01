import codecs, ssl, urllib.request

def urlopen(url, certkey = None, cert = None):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    if not certkey is None and not cert is None:
        context.load_cert_chain(certfile = cert, keyfile = certkey)
    r = urllib.request.urlopen(url, context = context)
    return codecs.getreader('utf-8')(r)
