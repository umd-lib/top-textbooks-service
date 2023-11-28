from flask import Flask, abort, request
from jsonschema import ValidationError, validate

from alma import __version__
from alma.errors import blueprint
from alma.utils import logger, schema


def app() -> Flask:
    return _create_app()


def _create_app() -> Flask:
    _app = Flask(
        import_name=__name__,
        static_url_path='/oai/static',
    )
    _app.register_blueprint(blueprint)
    logger.info(f'Starting alma-service/{__version__}')

    @_app.route('/')
    def root():
        return f"""
        <h1>Alma Service for Top Textbooks and Equipment Availability</h1>
        <h2>Version: alma-service/{__version__}</h2>
        <h3>Endpoints</h3>
        <ul>
            <li>/textbooks</li>
            <li>/equipment</li>
        </ul>
        <p>
            For Top Textbooks use the /textbooks endpoint,
            and for Equipment Avaliablity, use the /equipment endpoint
        </p>
        """

    @_app.route('/textbooks', methods=['GET', 'POST'])
    def textbooks():
        data = request.get_json() if request.is_json else abort(400, "Request was not JSON")

        try:
            validate(schema, data)
        except ValidationError as e:
            logger.error(str(e))
            abort(400, "JSON received is not valid.")



        return "This is the endpoint for the textbooks"

    @_app.route('/equipment', methods=['GET', 'POST'])
    def equipment():
        return "This is the endpoint for the equipment"

    return _app
