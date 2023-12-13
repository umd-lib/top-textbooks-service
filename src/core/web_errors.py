from flask import Blueprint, jsonify

from core.logging import create_logger

logger = create_logger(__name__)

blueprint = Blueprint('error_handlers', __name__)


@blueprint.app_errorhandler(400)
def _bad_request(e):
    logger.warning(e.description)

    response = jsonify({'status': 400, 'error': 'Bad Request', 'message': e.description})
    response.status_code = 400
    return response


@blueprint.app_errorhandler(404)
def _not_found(e):
    logger.warning(e.description)

    response = jsonify({'status': 404, 'error': 'Not Found', 'message': e.description})
    response.status_code = 404
    return response


@blueprint.app_errorhandler(429)
def _too_many_requests(e):
    logger.warning(e.description)

    response = jsonify({'status': 429, 'error': 'Too Many Requests', 'message': e.description})
    response.status_code = 429
    return response


@blueprint.app_errorhandler(500)
def _internal_server_error(e):
    logger.warning(e.description)

    response = jsonify({'status': 500, 'error': 'Internal Server Error', 'message': e.description})
    response.status_code = 500
    return response


@blueprint.app_errorhandler(502)
def _bad_gateway(e):
    logger.warning(e.description)

    response = jsonify({'status': 502, 'error': 'Bad Gateway', 'message': e.description})
    response.status_code = 502
    return response


@blueprint.app_errorhandler(504)
def _gateway_timed_out(e):
    logger.warning(e.description)

    response = jsonify({'status': 504, 'error': 'Gateway Timed Out', 'message': e.description})
    response.status_code = 504
    return response
