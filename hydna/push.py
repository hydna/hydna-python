import httplib
import os
import socket
import ssl
import urllib

from hydna import core
from hydna import exceptions

def send(uri, data, origin=None, ua=core.DEFAULT_UA, priority=None):
    """Send `data` to `uri` and return `True` on successful request. Optional
    arguments:

        `origin` - origin of the request.
        `ua` - specify custom user agent
        `priority` - priority of message (0 - 7)

    Will raise `RequestError` when request fails. See `core.parse_uri`
    for other exceptions.

    """
    if priority is not None and priority not in xrange(0, 8):
        raise exceptions.PriorityError("Invalid priority.")
    return push(uri, data, emit=False, origin=origin, ua=ua,
                priority=priority)

def emit(uri, data, origin=None, ua=core.DEFAULT_UA):
    """Emit `data` to `uri` and return `True` on successful request. Optional
    arguments:

        `origin` - origin of the request.
        `ua` - specify custom user agent

    Will raise `RequestError` when request fails. See `core.parse_uri`
    for other exceptions.

    """
    return push(uri, data, emit=True, origin=origin, ua=ua)

def push(uri, data, emit, origin, ua, priority=None):
    if priority is not None and emit:
        raise exceptions.PriorityError("Cannot set a priority when emitting "
                                       "signals.")

    (scheme, domain, channel, token) = core.parse_uri(uri)
    data = core.clean_payload(data)
    token = core.clean_token(token)

    if scheme == 'https':
        # does not validate certificate!
        http_cls = ValidatingHTTPSConnection
    else:
        http_cls = httplib.HTTPConnection

    con = http_cls(domain)

    headers = {
        'User-Agent': ua,
    }
    if emit:
        headers['X-Emit'] = 'yes'

    if origin is not None:
        headers['Origin'] = origin

    if priority is not None:
        headers['X-Priority'] = priority

    if token is not None:
        channel = '%s?%s' % (channel, urllib.quote(token))

    try:
        con.request('POST', channel, data, headers)
    except socket.gaierror:
        raise exceptions.RequestError("Unable to resolve hostname.")

    r = con.getresponse()

    if r.status == httplib.OK:
        return True

    if r.status == httplib.BAD_REQUEST:
        raise exceptions.RequestError(r.read())
    
    raise exceptions.RequestError("Unknown error.")


class ValidatingHTTPSConnection(httplib.HTTPSConnection):
    """
    >>> h = ValidatingHTTPSConnection('google.com').request('GET', '/')
    >>> h = ValidatingHTTPSConnection('facebook.com').request('GET', '/')
    >>> h = ValidatingHTTPSConnection('github.com').request('GET', '/')
    >>> h = ValidatingHTTPSConnection('testing.hydna.net').request('GET', '/')
    >>> h = ValidatingHTTPSConnection('hydna.com').request('GET', '/')

    """
    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 ca_certs_file=None, strict=None,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        httplib.HTTPSConnection.__init__(self, host, port, key_file,
                                         cert_file, strict, timeout)
        if ca_certs_file is None:
            path = os.path.abspath(os.path.dirname(__file__))
            ca_certs_file = os.path.join(path, 'cacerts', 'cacert.pem')
        self.ca_certs_file = ca_certs_file

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        try:
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ca_certs=self.ca_certs_file)
        except ssl.SSLError, e:
            raise ValueError(e)

        if ssl.CERT_REQUIRED:
            if not self.valid_hostname():
                # TODO: replace with custom exception
                raise ValueError('Certificate hostname mismatch')

    def valid_hostname(self):
        cert = self.sock.getpeercert()
        hostname = self.host.split(':')[0]

        for host in self.issued_for_hostnames(cert):
            if host.startswith('*') and hostname.endswith(host[1:]):
                return True
            if hostname == host:
                return True
        return False

    def issued_for_hostnames(self, cert):
        valid_hosts = set()

        for key, value in cert.iteritems():
            if key.lower() == 'subjectaltname':
                valid_hosts.update([entry for entry_type, entry in value if
                                    entry_type.lower() == 'dns'])
            elif key.lower() == 'subject':
                valid_hosts.update([entry[0][1] for entry in value if
                                    entry[0][0].lower() == 'commonName'])

        return valid_hosts

if __name__ == '__main__':
    import doctest
    doctest.testmod()
