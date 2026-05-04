from ucl_py.validator import validate

def test_schema():
    assert validate({}, {'a': 'int'})
