from core.utils import logger
from flask import abort
from jsonschema import ValidationError


class InternalServerError(Exception):
    """
    Raised when this application is encounters an unrecoverable error in it
    own processing, such as when a server authorization key is invalid, and
    the application receives a '401 Unauthorized' response from the server
    """
    pass

class TooManyRequestsError(Exception):
    """
    Raised when this application receives a '429 Too Many Requests' error from
    the server
    """
    pass

class BadGatewayError(Exception):
    """
    Raised when this application receives a '500 Server Error' from the server,
    or the server response is unparseable
    """

class GatewayTimeoutError(Exception):
    """
    When this application's request to the server times outs
    """


def handle_request(request, processor):
    if not request.is_json:
        abort(400, "Request was not JSON")

    requestData = request.get_json()

    try:
        processor.validate(requestData)
        responseData = processor.process(requestData)
        return responseData
    except ValidationError as e:
        logger.error(str(e))
        abort(400, "JSON received is not valid.")
    except InternalServerError as ise:
        logger.error(str(ise))
        abort(500, ise)
    except TooManyRequestsError as tmre:
        logger.error(str(tmre))
        abort(429, str(tmre))
    except BadGatewayError as bge:
        logger.error(str(bge))
        abort(502, str(bge))
    except GatewayTimeoutError as gte:
        logger.error(str(gte))
        abort(504, str(gte))
    except Exception as e:
      abort(500, "Something went wrong:" + str(e))