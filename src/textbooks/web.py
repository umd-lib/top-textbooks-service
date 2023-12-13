from typing import Any, Optional, Text, TextIO

from core.logging import create_logger
from core.web_errors import blueprint
from flask import Flask, abort, request
from yaml import safe_load

from textbooks import __version__
from textbooks.processor import AlmaServerGateway, TopTextbooksProcessor

logger = create_logger(__name__)


def get_config(config_source: Optional[str | TextIO] = None) -> dict[str, Any]:
    if config_source is None:
        raise RuntimeError('Config file not provided')

    if isinstance(config_source, str):
        with open(config_source) as fh:
            return safe_load(fh)

    if config_source:
        return safe_load(config_source)


def app(config: Optional[str | TextIO] = None) -> Flask:
    server = AlmaServerGateway(config=get_config(config))
    return _create_app(server)


def _create_app(server) -> Flask:
    _app = Flask(
        import_name=__name__,
    )
    _app.register_blueprint(blueprint)
    logger.info(f'Starting top-textbooks-service/{__version__}')

    @_app.route('/')
    def root():
        return f"""
        <h1>Service for Top Textbooks</h1>
        <h2>Version: top-textbooks-service/{__version__}</h2>
        <h3>Endpoints</h3>
        <ul>
            <li>/textbooks</li>
        </ul>
        """

    @_app.route('/api/textbooks', methods=['GET', 'POST'])  # type: ignore
    def textbooks():
        if not request.is_json:
            abort(400, 'Request was not JSON')

        requestData = request.get_json()
        logger.info(f'{requestData=}')
        processor = TopTextbooksProcessor(server)
        responseData = processor.process(requestData)
        return responseData

    return _app
