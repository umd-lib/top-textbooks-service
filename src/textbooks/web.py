from flask import Flask, abort, request
from jsonschema import ValidationError, validate

from textbooks import __version__
from textbooks.errors import blueprint
from textbooks.utils import logger, textbooks_schema


def app() -> Flask:
    return _create_app()


def _create_app() -> Flask:
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

    @_app.route('/textbooks', methods=['GET', 'POST'])
    def textbooks():
        data = request.get_json() if request.is_json else abort(400, "Request was not JSON")

        try:
            validate(textbooks_schema, data)
        except ValidationError as e:
            logger.error(str(e))
            abort(400, "JSON received is not valid.")

        # Using the JSON received from drupal generate get requests to alma

        # Collect the responses back into and collect the count and the

        return "This is the endpoint for the textbooks"

    @_app.route('/equipment', methods=['GET', 'POST'])
    def equipment():
        return "This is the endpoint for the equipment"

    return _app
