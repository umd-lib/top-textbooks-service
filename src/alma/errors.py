
from flask import Blueprint, jsonify

from alma.utils import logger

blueprint = Blueprint('error_handlers', __name__)


@blueprint.app_errorhandler(400)
def custom_400(e):
    logger.error(e.description)

    response = jsonify({'status': 400,
                        'error': 'Bad Request',
                        'message': e.description})
    response.status_code = 400
    return response

@blueprint.app_errorhandler(404)
def custom_404(e):
    logger.error(e.description)

    response = jsonify({'status': 404,
                        'error': 'Not Found',
                        'message': e.description})
    response.status_code = 404
    return response

@blueprint.app_errorhandler(429)
def too_many_requests(e):
    logger.error(e.description)

    response = jsonify({'status': 429,
                        'error': 'Too Many Requests',
                        'message': e.description})
    response.status_code = 429
    return response

@blueprint.app_errorhandler(500)
def internal_server_error(e):
    logger.error(e.description)

    response = jsonify({'status': 500,
                        'error': 'Internal Server Error',
                        'message': e.description})
    response.status_code = 500
    return response

@blueprint.app_errorhandler(502)
def bad_gateway(e):
    logger.error(e.description)

    response = jsonify({'status': 502,
                        'error': 'Bad Gateway',
                        'message': e.description})
    response.status_code = 502
    return response

@blueprint.app_errorhandler(504)
def gateway_timed_out(e):
    logger.error(e.description)

    response = jsonify({'status': 504,
                        'error': 'Gateway Timed Out',
                        'message': e.description})
    response.status_code = 504
    return response
