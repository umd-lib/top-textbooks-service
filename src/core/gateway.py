from time import perf_counter

import requests
from bs4 import BeautifulSoup
from flask import abort

from core.logging import create_logger

logger = create_logger(__name__)


class HttpGateway:
    @staticmethod
    def _parse_error(content):
        if content is None:
            logger.warning('Failed to retreive xml from Alma API')
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
                logger.warning('Failed to retrieve error code and message in content')
                return

            logger.warning(f'Alma API error {error_code}: {error_message}')

    @staticmethod
    def get(url, params):
        logger.debug(f'{url=}, {params=}')

        request_start_time = perf_counter()
        r = requests.get(url, params=params)
        request_response_time = f"{(perf_counter() - request_start_time):.4f} seconds"

        if r.status_code == 400:
            logger.warning(f"Received {r.status_code} from '{url}' in {request_response_time}")
            HttpGateway._parse_error(r.content)
            abort(r.status_code, 'Received 400 from the Alma API')

        if r.status_code == 500:
            logger.warning(f"Received {r.status_code} from '{url}' in {request_response_time}")
            abort(r.status_code, 'Received 500 from the Alma API')

        if not r.ok:
            logger.warning(f"Received unexpected {r.status_code} from '{url}' in {request_response_time}")
            abort(r.status_code, r.reason)

        logger.info(f"Received {r.status_code} from '{url}' in {request_response_time}")

        return r.content
