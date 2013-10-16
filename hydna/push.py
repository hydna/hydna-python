import httplib
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

    if scheme == 'https':
        http_cls = httplib.HTTPSConnection
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
    con.request('POST', channel, data, headers)

    r = con.getresponse()

    if r.status == httplib.OK:
        return True

    if r.status == httplib.BAD_REQUEST:
        raise exceptions.RequestError(r.read())
    
    raise exceptions.RequestError("Unknown error.")
