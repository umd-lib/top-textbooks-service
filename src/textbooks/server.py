
import click
from core.utils import logger
from core.web import app
from dotenv import load_dotenv
from waitress import serve

from textbooks import __version__
from textbooks.textbooks import TopTextbooksProcessor, construct_processor_endpoint


@click.command()
@click.option(
    '--listen',
    default='0.0.0.0:5000',
    help='Address and port to listen on. Default is "0.0.0.0:5000".',
    metavar='[ADDRESS]:PORT',
)
@click.version_option(__version__, '--version', '-V')
@click.help_option('--help', '-h')
def run(listen):
    load_dotenv()
    # if 'API_KEY' not in environ:
        # raise RuntimeError('API_KEY not set in environment')

    server_identity = f'top-textbooks-service/{__version__}'
    logger.info(f'Starting {server_identity}')
    try:
        processor = TopTextbooksProcessor()
        serve(
            app=app(processor, construct_processor_endpoint(processor)),
            listen=listen,
            ident=server_identity,
        )
    except (OSError, RuntimeError) as e:
        logger.error(f'Exiting: {e}')
        raise SystemExit(1) from e
