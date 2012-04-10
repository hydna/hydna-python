import httplib
import urllib

from hydna import core
from hydna import exceptions

def push(uri, data, origin=None, ua=core.DEFAULT_UA, priority=None):
    """Send `data` to `uri` and return `True` on successful request. Optional
    arguments:

        `origin` - origin of the request.
        `ua` - specify custom user agent
        `priority` - priority of message (1 - 3)

    Will raise `RequestError` when request fails. See `core.parse_uri`
    for other exceptions.

    """
    if priority is not None and priority not in (1, 2, 3):
        raise exceptions.PriorityError("Invalid priority.")
    return send(uri, data, emit=False, origin=origin, ua=ua,
                priority=priority)

def emit(uri, data, origin=None, ua=core.DEFAULT_UA):
    """Emit `data` to `uri` and return `True` on successful request. Optional
    arguments:

        `origin` - origin of the request.
        `ua` - specify custom user agent

    Will raise `RequestError` when request fails. See `core.parse_uri`
    for other exceptions.

    """
    return send(uri, data, emit=True, origin=origin, ua=ua)

def send(uri, data, emit, origin, ua, priority=None):
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

    path = '/%s/' % channel
    if token is not None:
        path = '%s?%s' % (path, urllib.quote(token))
    con.request('POST', '/%s/' % channel, data, headers)

    r = con.getresponse()

    if r.status == httplib.OK:
        return True

    if r.status == httplib.BAD_REQUEST:
        raise exceptions.RequestError(r.read())
    
    raise exceptions.RequestError("Unknown error.")
