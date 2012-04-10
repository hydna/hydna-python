class HydnaError(Exception):
    pass


class URIError(HydnaError):
    """A URI was found invalid for some reason."""
    pass


class TokenError(URIError):
    """Token was found invalid for some reason."""
    pass


class ChannelError(URIError):
    """Channel was found invalid for some reason."""
    pass


class PayloadError(HydnaError):
    """Payload was found invalid for some reason."""
    pass


class PriorityError(HydnaError):
    """Priority was found invalid for some reason."""
    pass


class RequestError(HydnaError):
    """General exception occurred when making a request to Hydna."""
    pass
