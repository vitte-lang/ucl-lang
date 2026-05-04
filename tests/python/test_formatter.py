from ucl_py.formatter import format_program

def test_fmt():
    class P: items=[]
    assert isinstance(format_program(P()), str)
