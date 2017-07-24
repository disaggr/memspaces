
from multiprocessing import Process
import time
import pytest
import memspaces
from posix_ipc import ExistentialError, unlink_shared_memory, unlink_semaphore


@pytest.fixture(scope='module')
def hostname():
    return 'localhost'

@pytest.fixture(scope='module')
def port():
    return 10000

@pytest.fixture(scope='module')
def shmem_name():
    return 'MemSpaceTest'

@pytest.fixture(scope='module')
def server(request, hostname, port):
    srv = memspaces.MemSpaceServer(hostname, port)
    p = Process(target=srv.serve_forever)
    p.start()
    yield srv
    p.terminate()
    p.join()

@pytest.fixture
def memspace_xmlrpc(server, hostname, port):
    return memspaces.MemSpaceClient('http://%s:%d' % (hostname, port))

def nothrow(error, func, args=()):
    try:
        func(*args)
    except error:
        pass

@pytest.fixture
def memspace(shmem_name):
    nothrow(ExistentialError, unlink_shared_memory, (shmem_name,))
    nothrow(ExistentialError, unlink_semaphore, ('/memspace_%s_lock' % shmem_name,))
    with memspaces.MemSpace(shmem_name) as space:
        yield space
    unlink_shared_memory(shmem_name)
    unlink_semaphore('/memspace_%s_lock' % shmem_name)
