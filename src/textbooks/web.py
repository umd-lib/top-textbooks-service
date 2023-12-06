from flask import Flask, abort, request

from textbooks import __version__
from textbooks.core.handling import AlmaServerGateway, TopTextbooksProcessor
from textbooks.core.utils import logger
from textbooks.core.web_errors import blueprint


def app() -> Flask:
    server = AlmaServerGateway(config=None)
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

    @_app.route('/textbooks', methods=['GET', 'POST']) # type: ignore
    def textbooks():
        if not request.is_json:
            abort(400, "Request was not JSON")

        requestData = request.get_json()
        logger.info(requestData)
        processor = TopTextbooksProcessor(requestData, server)
        responseData = processor.process()
        return responseData

    return _app
