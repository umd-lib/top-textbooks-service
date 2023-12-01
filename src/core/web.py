
from core.errors import blueprint
from core.utils import logger
from flask import Flask
from textbooks import __version__


def app(processor, processor_endpoint) -> Flask:
    return _create_app(processor, processor_endpoint)


def _create_app(processor, processor_endpoint) -> Flask:
    _app = Flask(
        import_name=__name__,
    )
    _app.register_blueprint(blueprint)
    _app.register_blueprint(processor_endpoint)
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

    return _app
