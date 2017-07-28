
from multiprocessing import Process
import pytest
import memspaces


@pytest.fixture(scope='module')
def hostname():
    return 'localhost'


@pytest.fixture(scope='module')
def port():
    return 10000


@pytest.fixture(scope='module')
def server(request, hostname, port):
    srv = memspaces.MemSpaceServer(hostname, port)
    p = Process(target=srv.serve_forever)
    p.start()
    yield srv
    p.terminate()
    p.join()


@pytest.fixture
def memspace(server, hostname, port):
    return memspaces.MemSpaceClient('http://%s:%d' % (hostname, port))
