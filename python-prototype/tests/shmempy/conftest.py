
import pytest
import memspaces


@pytest.fixture(scope='module')
def shmem_name():
    return 'MemSpaceTest'


@pytest.fixture
def memspace(shmem_name):
    space = memspaces.MemSpace(shmem_name)
    yield space
    space.unlink()
