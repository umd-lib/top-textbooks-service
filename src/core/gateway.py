from time import perf_counter

import requests
from bs4 import BeautifulSoup
from flask import abort

from core.logging import create_logger

logger = create_logger(__name__)


class HttpGateway:
    @staticmethod
    def _parse_error(content):
        if content == '':
            logger.warning('Failed to retrieve xml from Alma API')
            return

        soup = BeautifulSoup(content, features='xml')
        errors = soup.find_all('error')

        if len(errors) == 0:
            logger.warning('Failed to find errors in content')
            return

        for error in errors:
            try:
                error_code = error.find('errorCode').text
                error_message = error.find('errorMessage').text
            except AttributeError:
                logger.warning('Failed to retrieve error code and/or message in content')
                return

            logger.warning(f'Alma API error {error_code}: {error_message}')

    @staticmethod
    def log_response(level: str, url, response, request_response_time):
        log = getattr(logger, level)
        log(
            f"Received {response.status_code} from '{url}'",
            extra={'http_status_code': response.status_code, 'request_response_time_in_secs': request_response_time}
        )

    @staticmethod
    def get(url, params):
        logger.debug(f'{url=}, {params=}')

        request_start_time = perf_counter()
        r = requests.get(url, params=params)
        request_response_time = (perf_counter() - request_start_time)

        if r.status_code == 400:
            HttpGateway.log_response('warning', url, r, request_response_time)
            error_content = r.content.decode('UTF-8') if r.content else ''
            HttpGateway._parse_error(error_content)
            abort(r.status_code, 'Received 400 from the Alma API')

        if r.status_code == 500:
            HttpGateway.log_response('warning', url, r, request_response_time)
            abort(r.status_code, 'Received 500 from the Alma API')

        if not r.ok:
            HttpGateway.log_response('warning', url, r, request_response_time)
            abort(r.status_code, r.reason)

        HttpGateway.log_response('info', url, r, request_response_time)
        return r.content
