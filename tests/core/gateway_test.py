import pytest
from core.gateway import HttpGateway
from werkzeug.exceptions import BadGateway, BadRequest, GatewayTimeout, InternalServerError, NotFound, TooManyRequests


def test_200_response_from_server(requests_mock, caplog):
    requests_mock.get('http://example.com', text='Application OK', status_code=200)
    response = HttpGateway.get('http://example.com', {})
    assert 'Application OK' == response.decode('UTF-8')
    assert 'Received 200' in caplog.text


def test_400_response_from_server(requests_mock, caplog):
    requests_mock.get('http://example.com', text='Bad Request', status_code=400)
    with pytest.raises(BadRequest):
        HttpGateway.get('http://example.com', {})

    assert 'Received 400' in caplog.text
    assert 'Failed to find errors in content' in caplog.text


def test_400_xml_no_content_from_server(requests_mock, caplog):
    requests_mock.get('http://example.com', text='', status_code=400)

    with pytest.raises(BadRequest):
        HttpGateway.get('http://example.com', {})

    assert 'Received 400' in caplog.text
    assert 'Failed to retrieve xml from Alma API' in caplog.text


def test_400_xml_no_error_code_from_server(requests_mock, caplog):
    xml_error_response_no_error_code = """
    <web_service_result xmlns= \"http://com/exlibris/urm/general/xmlbeans\">
      <errorsExist>true</errorsExist>
      <errorList>
          <error>
              <errorMessage>Input parameters mmsId adsf is not numeric.</errorMessage>
              <trackingId>E01-1412213335-METCK-AWAE1210089497</trackingId>
          </error>
      </errorList>
    </web_service_result>
    """

    requests_mock.get('http://example.com', text=xml_error_response_no_error_code, status_code=400)

    with pytest.raises(BadRequest):
        HttpGateway.get('http://example.com', {})

    assert 'Received 400' in caplog.text
    assert 'Failed to retrieve error code and/or message in content' in caplog.text


def test_400_xml_no_error_message_from_server(requests_mock, caplog):
    xml_error_response_no_error_code = """
    <web_service_result xmlns= \"http://com/exlibris/urm/general/xmlbeans\">
      <errorsExist>true</errorsExist>
      <errorList>
          <error>
              <errorCode>402204</errorCode>
              <trackingId>E01-1412213335-METCK-AWAE1210089497</trackingId>
          </error>
      </errorList>
    </web_service_result>
    """

    requests_mock.get('http://example.com', text=xml_error_response_no_error_code, status_code=400)

    with pytest.raises(BadRequest):
        HttpGateway.get('http://example.com', {})

    assert 'Received 400' in caplog.text
    assert 'Failed to retrieve error code and/or message in content' in caplog.text


def test_400_xml_error_response_from_server(requests_mock, caplog):
    xml_error_response = """
    <web_service_result xmlns= \"http://com/exlibris/urm/general/xmlbeans\">
      <errorsExist>true</errorsExist>
      <errorList>
          <error>
              <errorCode>402204</errorCode>
              <errorMessage>Input parameters mmsId adsf is not numeric.</errorMessage>
              <trackingId>E01-1412213335-METCK-AWAE1210089497</trackingId>
          </error>
      </errorList>
    </web_service_result>
    """

    requests_mock.get('http://example.com', text=xml_error_response, status_code=400)

    with pytest.raises(BadRequest):
        HttpGateway.get('http://example.com', {})

    assert 'Received 400' in caplog.text
    assert 'Alma API error 402204: Input parameters mmsId adsf is not numeric.' in caplog.text


def test_404_response_from_server(requests_mock, caplog):
    requests_mock.get('http://example.com', text='Not Found', status_code=404)
    with pytest.raises(NotFound):
        HttpGateway.get('http://example.com', {})

    assert 'Received 404' in caplog.text


def test_429_response_from_server(requests_mock, caplog):
    requests_mock.get('http://example.com', text='Too Many Requests', status_code=429)
    with pytest.raises(TooManyRequests):
        HttpGateway.get('http://example.com', {})

    assert 'Received 429' in caplog.text


def test_500_response_from_server(requests_mock, caplog):
    requests_mock.get('http://example.com', text='', status_code=500)
    with pytest.raises(InternalServerError):
        HttpGateway.get('http://example.com', {})

    assert 'Received 500' in caplog.text


def test_502_response_from_server(requests_mock, caplog):
    requests_mock.get('http://example.com', text='Bad Gateway', status_code=502)
    with pytest.raises(BadGateway):
        HttpGateway.get('http://example.com', {})

    assert 'Received 502' in caplog.text


def test_504_response_from_server(requests_mock, caplog):
    requests_mock.get('http://example.com', text='Gateway Timeout', status_code=504)
    with pytest.raises(GatewayTimeout):
        HttpGateway.get('http://example.com', {})

    assert 'Received 504' in caplog.text
