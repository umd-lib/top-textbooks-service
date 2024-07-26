from typing import Any, Optional, TextIO

from core.logging import create_logger
from core.web_errors import blueprint
from flask import Flask, abort, request
from yaml import safe_load

from alma import __version__
from alma.processor import AlmaServerGateway, AlmaProcessor

logger = create_logger(__name__)


def get_config(config_source: Optional[str | TextIO] = None) -> Optional[dict[str, Any]]:
    if config_source is None:
        return None

    if isinstance(config_source, str):
        with open(config_source) as fh:
            return safe_load(fh)

    if config_source:
        return safe_load(config_source)


def app(config: Optional[str | TextIO] = None) -> Flask:
    server = AlmaServerGateway(config=get_config(config))
    return _create_app(server)


def _create_app(server: Optional[AlmaServerGateway] = None) -> Flask:
    _app = Flask(
        import_name=__name__,
    )
    _app.register_blueprint(blueprint)
    logger.info(f'Starting alma-service/{__version__}')

    @_app.route('/')
    def root():
        return {'status': 'ok'}

    @_app.route('/ping')
    def ping():
        return {'status': 'ok'}

    @_app.route('/api/textbooks', methods=['GET', 'POST'])  # type: ignore
    def bibs():
        if not request.is_json:
            abort(400, 'Request was not JSON')

        requestData = request.get_json()
        logger.info(f'{requestData=}')
        processor = AlmaProcessor(server)
        responseData = processor.processBibs(requestData, 'TPTXB')
        return responseData

    @_app.route('/api/holdings', methods=['GET', 'POST'])  # type: ignore
    def holdings():
        if not request.is_json:
            abort(400, 'Request was not JSON')

        requestData = request.get_json()
        logger.info(f'{requestData=}')
        processor = AlmaProcessor(server)
        responseData = processor.processHoldings(requestData)
        return responseData

    @_app.route('/api/equipment', methods=['GET', 'POST'])  # type: ignore
    def equipment():
        if not request.is_json:
            abort(400, 'Request was not JSON')

        requestData = request.get_json()
        logger.info(f'{requestData=}')
        processor = AlmaProcessor(server)
        responseData = processor.processBibs(requestData, limit_collection=None,
                                             include_course=False, check_holdings=True)
        return responseData

    return _app
