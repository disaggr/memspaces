
def test_simple(memspace):
    memspace.put(('hello', 'world'))
    assert ('hello', 'world') == memspace.take((None, None))
