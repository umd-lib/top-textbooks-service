import requests
from flask import abort

from core.utils import create_logger

logger = create_logger(__name__)


class HttpGateway:
    def get(url, params):
        logger.debug(f'{params=}')
        logger.debug(f'{url=}')

        r = requests.get(url, params=params)

        if r.status_code == 400:
            abort(r.status_code, f"Received 400 from upstream server '{url}'")

        if r.status_code == 500:
            abort(r.status_code, f"Received 500 from upstream server '{url}'")

        if not r.ok:
            logger.warning(f"Received unexpected {r.status_code} from upstream server '{url}'")
            abort(r.status_code, r.reason)

        logger.info(f"Received {r.status_code} from upstream server '{url}'")

        return r.content
