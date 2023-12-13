import pytest
from core.gateway import HttpGateway
from werkzeug.exceptions import BadGateway, BadRequest, GatewayTimeout, InternalServerError, NotFound, TooManyRequests


def test_200_response_from_server(requests_mock, caplog):
    requests_mock.get('http://test.com', text='Application OK', status_code=200)
    response = HttpGateway.get('http://test.com', {})
    assert 'Application OK' == response.decode('UTF-8')
    assert 'Received 200' in caplog.text


def test_400_response_from_server(requests_mock, caplog):
    requests_mock.get('http://test.com', text='Bad Request', status_code=400)
    with pytest.raises(BadRequest):
        HttpGateway.get('http://test.com', {})

    assert 'Received unexpected 400' in caplog.text


def test_404_response_from_server(requests_mock, caplog):
    requests_mock.get('http://test.com', text='Not Found', status_code=404)
    with pytest.raises(NotFound):
        HttpGateway.get('http://test.com', {})

    assert 'Received unexpected 404' in caplog.text


def test_429_response_from_server(requests_mock, caplog):
    requests_mock.get('http://test.com', text='Too Many Requests', status_code=429)
    with pytest.raises(TooManyRequests):
        HttpGateway.get('http://test.com', {})

    assert 'Received unexpected 429' in caplog.text


def test_500_response_from_server(requests_mock, caplog):
    requests_mock.get('http://test.com', text='', status_code=500)
    with pytest.raises(InternalServerError):
        HttpGateway.get('http://test.com', {})

    assert 'Received unexpected 500' in caplog.text


def test_502_response_from_server(requests_mock, caplog):
    requests_mock.get('http://test.com', text='Bad Gateway', status_code=502)
    with pytest.raises(BadGateway):
        HttpGateway.get('http://test.com', {})

    assert 'Received unexpected 502' in caplog.text


def test_504_response_from_server(requests_mock, caplog):
    requests_mock.get('http://test.com', text='Gateway Timeout', status_code=504)
    with pytest.raises(GatewayTimeout):
        HttpGateway.get('http://test.com', {})

    assert 'Received unexpected 504' in caplog.text
