import logging
from os import environ

import requests
from bs4 import BeautifulSoup
from flask import abort
from jsonschema import ValidationError, validate

from core.utils import create_logger

logger = create_logger(__name__)

debug = environ.get('FLASK_DEBUG', default=False)
logger.setLevel(logging.DEBUG if debug else logging.INFO)


class AlmaServerGateway:
    def __init__(self, config) -> None:
        # Probably a yaml file
        self.config = config
        if 'host' not in config or 'endpoint' not in config:
            raise RuntimeError('Gateway configuration not valid')

        self.api_key = environ.get('ALMA_API_KEY', '')

    def queryServer(self, mms_ids):
        """
        Generates parameters neceessary to query Alma Server.
        Request content is xml, processed in :meth:`parse_xml`
        """
        url = self.config['host'] + self.config['endpoint']
        params = {'mms_id': ','.join(mms_ids), 'view': 'full', 'expand': 'p_avail', 'apikey': self.api_key}

        logger.debug(f'{params=}')
        logger.debug(f'{url=}')

        r = requests.get(url, params=params)

        if r.status_code == 400:
            abort(r.status_code, 'Received 400 from Alma API')

        if r.status_code == 500:
            abort(r.status_code, 'Received 500 from Alma API')

        if not r.ok:
            logger.warning(f'Received unexpected {r.status_code} from Alma API')
            abort(r.status_code, r.reason)

        logger.info(f'Received {r.status_code} from Alma API')

        return r.content
