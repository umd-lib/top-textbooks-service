from os import environ

from bs4 import BeautifulSoup
from core.gateway import HttpGateway
from core.logging import create_logger
from flask import abort
from jsonschema import ValidationError, validate

logger = create_logger(__name__)


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
        query_content = self.queryServer(mms_ids)

        # Process the xml content
        alma_data = self.parse_xml(query_content)

        for mms_id in alma_data:
            if mms_id not in alma_data:
                logger.warning(f'{mms_id} not found in Alma.')

        return alma_data

    def queryServer(self, mms_ids):
        """
        Generates parameters neceessary to query Alma Server.
        Request content is xml, processed in :meth:`parse_xml`
        """
        return self.server.retrieveBibs(mms_ids)


class AlmaServerGateway:
    def __init__(self, config) -> None:
        # Probably a yaml file
        self.config = config
        if 'host' not in config or 'endpoint' not in config:
            raise RuntimeError('Gateway configuration not valid')

        self.api_key = environ.get('ALMA_API_KEY', '')

    def retrieveBibs(self, mms_ids):
        params = {'mms_id': ','.join(mms_ids), 'view': 'full', 'expand': 'p_avail', 'apikey': self.api_key}

        url = self.config['host'] + self.config['endpoint']
        return HttpGateway.get(url, params)
