from os import environ

from bs4 import BeautifulSoup
from core.gateway import HttpGateway
from core.logging import create_logger
from flask import abort
from datetime import datetime
from jsonschema import ValidationError, validate

logger = create_logger(__name__)


class AlmaProcessor:
    TEXTBOOKS_SCHEMA = {'type': 'array', 'items': {'type': 'string'}}
    HOLDINGS_SCHEMA = {'type': 'object', 'items': {'type': 'string'}}

    def __init__(self, server):
        self.server = server

    @staticmethod
    def unique_mms_ids(data):
        """
        Returns a deduplicated set of mms_ids from the request data
        """
        return set(data)

    @staticmethod
    def unique_holdings(data):
        """
        Returns a deduplicated set of mms_ids from the request data
        """
        return dict(data)

    def parse_holdings(self, content, check_TT=True):
        """
        Parse holdings/items of a given mms + holdings ID.
        One query per record though a single result can include multiple items.
        Defaults to Top Textbooks only query (check_TT).
        """
        response_data = {}
        soup = BeautifulSoup(content, features='xml')
        bibs = soup.find_all('item')

        if len(bibs) == 0:
            abort(502, 'No holdings data found in request')

        for bib in bibs:
            try:
                bib_data = bib.find('bib_data')
                holding_data = bib.find('holding_data')
                item_data = bib.find('item_data')
                logger.debug(item_data)
            except AttributeError:
                abort(502, 'fields not found in bibs')

            is_TT = False
            temp_locations = None
            if check_TT:
                try:
                    temp_locations = holding_data.find_all('temp_location', attrs={'desc': 'Top Textbook'})
                except AttributeError:
                    is_TT = False

                if temp_locations is None or len(temp_locations) == 0:
                    try:
                        temp_locations = item_data.find_all('location', attrs={'desc': 'Top Textbook'})
                    except AttributeError:
                        is_TT = False

                logger.debug(temp_locations)
                for loc in temp_locations:
                    if loc.text == 'TPTXB':
                        is_TT = True

            if (check_TT and is_TT) or not check_TT:
                mms_id = bib_data.find('mms_id').text
                barcode = item_data.find('barcode').text
                item_count = 0
                item_available = False
                awaiting_reshelving = False
                try:
                    awaiting_reshelving = item_data.find('awaiting_reshelving').text
                    item_in_place = item_data.find('base_status', attrs={'desc': 'Item in place'})
                    item_count = int(item_in_place.text)
                    if item_count > 0:
                        item_available = True
                except AttributeError:
                    item_available = False

                response_data[barcode] = {'available': item_available, 'count': item_count,
                                          'reshelving': awaiting_reshelving}

        return response_data

    def parse_bibs(self, content, limit_collection, include_course, check_holdings):
        """
        Parses the bibliographic xml content from the Alma API.
        Many records are processed in a single query.
        Retrieves the availability and amount. Can be limited by collection.
        An additional holdings check can be run if item is unavailable.
        """
        response_data = {}
        soup = BeautifulSoup(content, features='xml')

        bibs = soup.find_all('bib')

        for bib in bibs:
            holdings_url = None
            try:
                avas = bib.find_all('datafield', attrs={'tag': 'AVA'})
                holdings_url = bib.find('holdings')['link']
                title = bib.find('title').text
            except AttributeError:
                logger.warning('No AVA found for content ')
                # abort(502, 'fields not found in bibs')
                continue

            logger.debug(holdings_url)
            holdings_info = self.getAdditional(holdings_url)
            # logger.debug(holdings_info)
            holdings_soup = BeautifulSoup(holdings_info, features='xml')
            info_url = holdings_soup.find('holding')['link']
            logger.debug(info_url)
            info = self.getAdditional(info_url + '/items')
            # logger.debug(info)

            if len(avas) == 0:
                logger.warning('No AVA found for content ')
                # abort(502, 'No AVA tag found in content')
                continue

            logger.debug(avas)
            for ava in avas:
                availability = None
                total_items = None
                location_code = None
                call_number = None
                physical_location = None
                mms_find = ava.find('subfield', attrs={'code': '0'})
                if mms_find is not None:
                    mms_id = mms_find.text
                avail_find = ava.find('subfield', attrs={'code': 'e'})
                if avail_find is not None:
                    availability = avail_find.text
                total_find = ava.find('subfield', attrs={'code': 'f'})
                if total_find is not None:
                    total_items = total_find.text
                location_find = ava.find('subfield', attrs={'code': 'j'})
                if location_find is not None:
                    location_code = location_find.text
                call_find = ava.find('subfield', attrs={'code': 'd'})
                if call_find is not None:
                    call_number = call_find.text
                physical_find = ava.find('subfield', attrs={'code': 'b'})
                if physical_find is not None:
                    physical_location = physical_find.text

                logger.debug(f'{mms_id=}')
                logger.debug(f'{availability=}')
                logger.debug(f'{total_items=}')
                logger.debug(f'{location_code=}')
                logger.debug(f'{call_number=}')
                logger.debug(f'{physical_location=}')

                if limit_collection is not None and limit_collection != location_code:
                    continue

                course_code = None
                if include_course and call_number is not None:
                    course_array = call_number.split('/')
                    if course_array[0] is not None and len(course_array[0]) > 0:
                        course_code = course_array[0]

                location_code = None
                if physical_location is not None:
                    location_code = physical_location.replace(" ", "_")

                item_key = mms_id + '--' + location_code

                if course_code is not None:
                    item_key += '--' + course_code

                key_exists = False
                if item_key in response_data:
                    if 'count' in response_data[item_key] and int(total_items) > 0:
                        modified_dict = response_data[item_key]
                        old_count = modified_dict['count']
                        new_count = int(total_items) + int(old_count)
                        modified_dict['count'] = new_count
                        response_data[item_key] = modified_dict
                        key_exists = True

                if not key_exists:
                    if availability == 'available':
                        logger.debug(f'{total_items} available textbooks for {mms_id}')
                        response_data[item_key] = {'location': physical_location,
                                                   'count': total_items, 'status': availability,
                                                   'call_number': call_number}

                    elif availability == 'unavailable':
                        logger.debug(f'No available textbooks for {mms_id}')
                        response_data[item_key] = {'location': physical_location,
                                                   'count': 0, 'status': availability, 'call_number': call_number}
                        if check_holdings:
                            stored_date = None
                            logger.debug(holdings_url)
                            holdings_info = self.getAdditional(holdings_url)
                            holdings_soup = BeautifulSoup(holdings_info, features='xml')
                            info_url = holdings_soup.find('holding')['link']
                            logger.debug(info_url)
                            info = self.getAdditional(info_url + '/items')
                            info_soup = BeautifulSoup(info, features='xml')
                            logger.debug(info_soup)
                            due_dates = info_soup.find_all('due_date')
                            for date in due_dates:
                                logger.debug(date)
                                proc_date = datetime.fromisoformat(date.text)
                                if stored_date is None:
                                    stored_date = proc_date
                                if stored_date < proc_date:
                                    stored_date = proc_date
                                logger.debug(proc_date)
                            if stored_date is not None:
                                response_data[item_key]['due_date'] = stored_date

                    else:
                        logger.debug(f'Availability status of {availability} for {mms_id}')
                        response_data[item_key] = {'location': physical_location,
                                                   'status': 'Check Holding', 'call_number': call_number}

                    response_data[item_key]['title'] = title
                    response_data[item_key]['mms_id'] = mms_id
                    if course_code is not None:
                        response_data[item_key]['course'] = course_code

        return response_data

    def processHoldings(self, data):
        try:
            validate(data, self.HOLDINGS_SCHEMA)
        except ValidationError as e:
            logger.warning(str(e))
            abort(400, 'Invalid JSON')

        holdings = self.unique_holdings(data)

        response_data = {}
        for mms_id, holdings_id in holdings.items():
            holdings_raw = self.getHoldings(mms_id, holdings_id)
            response_raw = self.parse_holdings(holdings_raw)
            if (mms_id in response_data) and holdings_id in response_data[mms_id]:
                current_holdings = response_data[mms_id][holdings_id]
                updated_holdings = current_holdings | response_raw
                response_data[mms_id][holdings_id] = updated_holdings
            else:
                response_data[mms_id] = {holdings_id: response_raw}

        return response_data

    def processBibs(self, data, limit_collection=None, include_course=False, check_holdings=False):
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

        logger.debug(len(mms_ids))

        # Send request
        query_content = self.queryServer(mms_ids)

        # Process the xml content
        alma_data = self.parse_bibs(query_content, limit_collection, include_course, check_holdings)

        for mms_id in alma_data:
            if mms_id not in alma_data:
                logger.warning(f'{mms_id} not found in Alma.')

        return alma_data

    def queryServer(self, mms_ids):
        """
        Generates parameters neceessary to query Alma Server.
        Request content is xml, processed in :meth:`parse_bibs`
        """
        return self.server.retrieveBibs(mms_ids)

    def getHoldings(self, mms_id, holdings_id):
        """
        Generates parameters neceessary to query Alma Server.
        Request content is xml, processed in :meth:`parse_holdings`
        """
        return self.server.retrieveHoldings(mms_id, holdings_id)

    def getAdditional(self, url):
        """
        Allows for querying of alma provided URL without additional
        parameters needed. Used in :meth:`parse_bibs`
        """
        return self.server.retrieveAdditional(url)


class AlmaServerGateway:
    def __init__(self, config) -> None:
        if config is None:
            raise RuntimeError('Config file not provided')

        if 'host' not in config or 'endpoint' not in config:
            raise RuntimeError('Gateway configuration not valid')

        self.config = config
        self.api_key = environ.get('ALMA_API_KEY', '')

    def retrieveBibs(self, mms_ids):
        params = {'mms_id': ','.join(mms_ids), 'view': 'full', 'expand': 'p_avail', 'apikey': self.api_key}

        url = self.config['host'] + self.config['endpoint']
        return HttpGateway.get(url, params)

    def retrieveHoldings(self, mms_id, holdings_id):
        params = {'apikey': self.api_key, 'expand': 'due_date'}

        url = self.config['host'] + self.config['endpoint'] + mms_id + '/holdings/' + holdings_id + '/items'
        return HttpGateway.get(url, params)

    def retrieveAdditional(self, url):
        params = {'apikey': self.api_key, 'expand': 'due_date'}

        return HttpGateway.get(url, params)
