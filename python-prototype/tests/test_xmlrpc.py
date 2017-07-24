
def test_simple(memspace_xmlrpc):
    memspace_xmlrpc.put(('hello', 'world'))
    assert ('hello', 'world') == tuple(memspace_xmlrpc.take((None, None)))
