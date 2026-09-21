
import pytest
from src.parser import parse_draw, ParseError

GOOD = """
<html><body><h1>XSMB 15/09/2026</h1>
<div>G.ĐB 12345</div><div>G.1 54321</div><div>G.2 11111 22222</div>
<div>G.3 10001 10002 10003 10004 10005 10006</div>
<div>G.4 2001 2002 2003 2004</div><div>G.5 3001 3002 3003 3004 3005 3006</div>
<div>G.6 401 402 403</div><div>G.7 01 02 03 04</div>
</body></html>
"""
def test_parse_valid_draw():
    d=parse_draw(GOOD,"https://example.test")
    assert d.day=="2026-09-15"
    assert d.special_prize=="12345"
    assert len(d.numbers)==27
    assert d.numbers[0]=="45"
def test_reject_malformed():
    with pytest.raises(ParseError):
        parse_draw("<html>XSMB 15/09/2026 G.ĐB 12345</html>","x")
