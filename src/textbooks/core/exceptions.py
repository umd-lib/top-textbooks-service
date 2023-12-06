from flask import abort


class TooManyRequestsError(Exception):
    """
    Raised when this application receives a '429 Too Many Requests' error from
    the server
    """
    def __init__(self, message) -> None:
        abort(429, message)


class InternalServerError(Exception):
    """
    Raised when this application is encounters an unrecoverable error in it
    own processing, such as when a server authorization key is invalid, and
    the application receives a '401 Unauthorized' response from the server
    """
    def __init__(self, message) -> None:
        abort(500, message)


class BadGatewayError(Exception):
    """
    Raised when this application receives a '500 Server Error' from the server,
    or the server response is unparseable
    """
    def __init__(self, message) -> None:
        abort(502, message)


class GatewayTimeoutError(Exception):
    """
    When this application's request to the server times outs
    """
    def __init__(self, message) -> None:
        abort(504, message)
