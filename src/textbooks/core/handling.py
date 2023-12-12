import logging
from os import environ

import requests
from bs4 import BeautifulSoup
from flask import abort
from jsonschema import ValidationError, validate
from textbooks.core.utils import json_formatter

logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
logHandler.setFormatter(json_formatter)
logger.addHandler(logHandler)

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


class TopTextbooksProcessor:
    TEXTBOOKS_SCHEMA = {'type': 'array', 'items': {'type': 'string'}}

    def __init__(self, server):
        self.server = server

    @staticmethod
    def unique_mms_ids(data):
        """
        Returns a deduplicated set of mms_ids from the request data
        """
        return set(data)

    def parse_xml(self, content):
        """
        Parses the xml content from the Alma API.
        Retrieves the availability and amount of available books.
        """
        response_data = {}
        soup = BeautifulSoup(content, features='xml')
        avas = soup.find_all('datafield', attrs={'tag': 'AVA'})

        if len(avas) == 0:
            abort(502, 'No AVA tag found in content')

        for ava in avas:
            try:
                mms_id = ava.find('subfield', attrs={'code': '0'}).text
                availability = ava.find('subfield', attrs={'code': 'e'}).text
                total_items = ava.find('subfield', attrs={'code': 'f'}).text
                location_code = ava.find('subfield', attrs={'code': 'j'}).text
            except AttributeError:
                abort(502, 'Subfields not found in AVA')

            logger.debug(f'{mms_id=}')
            logger.debug(f'{availability=}')
            logger.debug(f'{total_items=}')
            logger.debug(f'{location_code=}')

            if location_code != 'TPTXB':
                continue

            if availability == 'available':
                logger.info(f'{total_items} available textbooks for {mms_id}')
                response_data[mms_id] = {'count': total_items, 'status': availability}

            elif availability == 'unavailable':
                logger.info(f'No available textbooks for {mms_id}')
                response_data[mms_id] = {'count': 0, 'status': availability}

            else:
                logger.info(f'Availability status of {availability} for {mms_id}')
                response_data[mms_id] = {'status': 'Check Holding'}

        return response_data

    def process(self, data):
        """
        Validates JSON received from Drupal.
        Queries the Alma Server if data is valid
        """
        try:
            validate(data, self.TEXTBOOKS_SCHEMA)
        except ValidationError as e:
            logger.warning(str(e))
            abort(400, 'JSON received is not valid.')

        # Process data
        mms_ids = self.unique_mms_ids(data)

        # Send request
        query_content = self.server.queryServer(mms_ids)

        # Process the xml content
        alma_data = self.parse_xml(query_content)

        for mms_id in alma_data:
            if mms_id not in alma_data:
                logger.warning(f'{mms_id} not found in Alma.')

        return alma_data
