
import random

def test_simple(memspace_xmlrpc):
    memspace_xmlrpc.put(('hello', 'world'))
    assert ('hello', 'world') == tuple(memspace_xmlrpc.take((None, None)))

def test_front_to_back(memspace_xmlrpc):
    for i in range(100):
        memspace_xmlrpc.put((i, 'test %d' % i))
    for i in range(100):
        assert (i, 'test %d' % i) == tuple(memspace_xmlrpc.take((i, None)))

def test_back_to_front(memspace_xmlrpc):
    for i in range(100):
        memspace_xmlrpc.put((i, 'test %d' % i))
    for i in reversed(range(100)):
        assert (i, 'test %d' % i) == tuple(memspace_xmlrpc.take((i, None)))

def test_shuffled(memspace_xmlrpc):
    for i in range(100):
        memspace_xmlrpc.put((i, 'test %d' % i))
    for i in random.sample(range(100), 100):
        assert (i, 'test %d' % i) == tuple(memspace_xmlrpc.take((i, None)))
