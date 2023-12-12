import json

import pytest
from textbooks.core.exceptions import (
    BadGatewayError,
    GatewayTimeoutError,
    TooManyRequestsError,
)
from textbooks.web import _create_app


@pytest.fixture
def app():
    app = _create_app(server=None)

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def test_returns_404_not_found_when_endpoint_does_not_exist(client):
    response = client.post('/does-not-exist')
    assert response.status_code == 404


def test_returns_400_bad_request_when_data_is_not_json(client):
    response = client.post('/textbooks', data='{"invalid data": "invalid"}', content_type='text/plain')
    assert response.status_code == 400
    assert 'Request was not JSON' == json.loads(response.text)['message']


def test_returns_400_bad_request_when_data_is_invalid(client):
    response = client.post('/textbooks', data='{"invalid data": "invalid"}', content_type='application/json')
    assert response.status_code == 400
    assert 'JSON received is not valid.' == json.loads(response.text)['message']


def raise_(ex):
    raise ex


class MockAlmaServerGateway:
    def __init__(self, responseFunction):
        self.responseFunction = responseFunction

    def queryServer(self, result_data):
        self.responseFunction()


def test_server_returns_429_too_many_requests_error():
    testGateway = MockAlmaServerGateway(lambda: raise_(TooManyRequestsError('Too Many Requests')))
    app = _create_app(testGateway)
    client = app.test_client()
    response = client.post('/textbooks', data='[]', content_type='application/json')
    assert response.status_code == 429


def test_server_returns_502_bad_gateway_error():
    testGateway = MockAlmaServerGateway(lambda: raise_(BadGatewayError('Bad Gateway')))
    app = _create_app(testGateway)
    client = app.test_client()
    response = client.post('/textbooks', data='[]', content_type='application/json')
    assert response.status_code == 502


def test_server_returns_504_gateway_timeout_error():
    testGateway = MockAlmaServerGateway(lambda: raise_(GatewayTimeoutError('Gateway Timed Out')))
    app = _create_app(testGateway)
    client = app.test_client()
    response = client.post('/textbooks', data='[]', content_type='application/json')
    assert response.status_code == 504
