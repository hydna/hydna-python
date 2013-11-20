# encoding: utf-8
import urllib
import urlparse

from hydna import exceptions

DEFAULT_UA = 'Hydna Python Client'

MAX_PAYLOAD_SIZE = 0xFFFA
MAX_TOKEN_SIZE = MAX_PAYLOAD_SIZE

def clean_payload(payload):
    """Raise `PayloadError` if the length of `payload` (in bytes)
    exceeds `MAX_PAYLOAD_SIZE`; otherwise return original value.

    >>> p1 = MAX_PAYLOAD_SIZE * 'a'
    >>> p1 == clean_payload(p1)
    True

    >>> try:
    ...     clean_payload(((MAX_PAYLOAD_SIZE - 1) * u'a') + u'ä')
    ... except exceptions.PayloadError:
    ...     pass

    """
    if len(payload.encode('utf-8')) > MAX_PAYLOAD_SIZE:
        raise exceptions.PayloadError("Payload exceeds maximum length "
                                             "allowed.")
    return payload

def clean_token(token):
    """Raise `TokenError` if the length of `token` (in bytes) exceeds
    `MAX_TOKEN_SIZE`; otherwise return unquoted value.

    >>> p1 = MAX_TOKEN_SIZE * 'a'
    >>> p1 == clean_token(p1)
    True

    >>> try:
    ...     clean_token(((MAX_TOKEN_SIZE - 1) * u'a') + u'ä')
    ... except exceptions.TokenError:
    ...     pass

    """
    if token is None:
        return None

    token = urllib.unquote(token)

    if len(token.encode('utf-8')) > MAX_TOKEN_SIZE:
        raise exceptions.TokenError("Token exceeds maximum length "
                                           "allowed.")
    return token

def parse_uri(uri):
    """Parse `uri` and return a 4-tuple containing scheme (http or https),
    domain, channel, and token. The token (querystring) is expected to be
    quoted.

    Will raise `ChannelError`, `TokenError`, or `URIError` if `uri` could not
    be properly parsed.

    >>> parse_uri("http://public.hydna.net/?token")
    ('http', 'public.hydna.net', '/', 'token')

    >>> parse_uri("http://public.hydna.net")
    ('http', 'public.hydna.net', '/', None)

    >>> parse_uri("http://public.hydna.net/")
    ('http', 'public.hydna.net', '/', None)

    >>> parse_uri("http://public.hydna.net/312")
    ('http', 'public.hydna.net', '/312', None)

    >>> parse_uri("http://public.hydna.net/312/")
    ('http', 'public.hydna.net', '/312/', None)

    """
    # we're assuming that the user meant to use regular HTTP if no
    # scheme name was specified.
    if not uri.startswith('http'):
        uri = 'http://%s' % uri

    bits = urlparse.urlparse(uri)

    if not bits.netloc:
        raise exceptions.URIError("No domain name parsed.")

    channel = bits.path or '/'
    token = clean_token(bits.query or None)

    return (bits.scheme, bits.netloc, channel, token)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
