
import random


def test_simple(memspace):
    memspace.put(('hello', 'world'))
    assert ('hello', 'world') == tuple(memspace.get((None, None)))


def test_front_to_back(memspace):
    for i in range(100):
        memspace.put((i, 'test %d' % i))
    for i in range(100):
        assert (i, 'test %d' % i) == tuple(memspace.get((i, None)))


def test_back_to_front(memspace):
    for i in range(100):
        memspace.put((i, 'test %d' % i))
    for i in reversed(range(100)):
        assert (i, 'test %d' % i) == tuple(memspace.get((i, None)))


def test_shuffled(memspace):
    for i in range(100):
        memspace.put((i, 'test %d' % i))
    for i in random.sample(range(100), 100):
        assert (i, 'test %d' % i) == tuple(memspace.get((i, None)))


def test_read(memspace):
    for i in range(100):
        memspace.put((i, 'test %d' % i))
    for i in random.sample(range(100), 100):
        assert (i, 'test %d' % i) == tuple(memspace.read((i, None)))
    for i in random.sample(range(100), 100):
        assert (i, 'test %d' % i) == tuple(memspace.get((i, None)))
