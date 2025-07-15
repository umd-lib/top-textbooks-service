import os

from alma.processor import AlmaServerGateway, AlmaProcessor


def resource_file_as_string(filepath):
    with open(os.path.normpath(filepath), 'r') as resource_file:
        return resource_file.read()


def test_unique_mms_ids():
    data = {'abc', '123', 'abc'}
    unique_data = AlmaProcessor(server=None).unique_mms_ids(data)
    assert isinstance(unique_data, set)
    assert unique_data == {'abc', '123'}


def test_retrieve_bibs_item_available(requests_mock):
    xml_response = resource_file_as_string('tests/resources/retrieve_bibs_200_response_available.xml')
    requests_mock.get('http://example.com/test_endpoint', text=xml_response, status_code=200)

    mock_config = {'host': 'http://example.com', 'endpoint': '/test_endpoint'}
    processor = AlmaProcessor(AlmaServerGateway(mock_config))

    mock_request = ["990008536900108238"]
    expected_result = {'990008536900108238--CPMCK': {'location': 'CPMCK', 'count': '1', 'status': 'available',
                                                     'call_number': 'CLAS170/Iliad of Homer',
                                                     'title': 'The Iliad of Homer /', 'mms_id': '990008536900108238'}}

    processed_result = processor.processBibs(mock_request, 'TPTXB')

    assert processed_result == expected_result
