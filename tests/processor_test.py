from textbooks.core.handling import TopTextbooksProcessor


def test_unique_mms_ids():
    data = {'abc', '123', 'abc'}
    unique_data = TopTextbooksProcessor(server=None).unique_mms_ids(data)
    assert isinstance(unique_data, set)
    assert unique_data == {'abc', '123'}
