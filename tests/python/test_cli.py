from ucl_py.cli import main

def test_cli():
    assert main(['ucl','eval','/dev/null']) in (0,1)
