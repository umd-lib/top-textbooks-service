from time import perf_counter

import requests
from flask import abort

from core.logging import create_logger

logger = create_logger(__name__)


class HttpGateway:
    def get(url, params):
        logger.debug(f'{url=}, {params=}')

        request_start_time = perf_counter()
        r = requests.get(url, params=params)
        request_response_time = f"{(perf_counter() - request_start_time):.4f} seconds"

        if r.status_code == 400:
            abort(r.status_code, f"Received 400 from '{url}' in {request_response_time}")

        if r.status_code == 500:
            abort(r.status_code, f"Received 500 from '{url}' in {request_response_time}")

        if not r.ok:
            logger.warning(f"Received unexpected {r.status_code} from '{url}' in {request_response_time}")
            abort(r.status_code, r.reason)

        logger.info(f"Received {r.status_code} from '{url}' in {request_response_time}")

        return r.content
