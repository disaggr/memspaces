 ##############################################################################
 #    memspaces - tuple spaces in shared memory                               #
 #    Copyright (C) 2017  Andreas Grapentin                                   #
 #                                                                            #
 #    This program is free software: you can redistribute it and/or modify    #
 #    it under the terms of the GNU General Public License as published by    #
 #    the Free Software Foundation, either version 3 of the License, or       #
 #    (at your option) any later version.                                     #
 #                                                                            #
 #    This program is distributed in the hope that it will be useful,         #
 #    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
 #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
 #    GNU General Public License for more details.                            #
 #                                                                            #
 #    You should have received a copy of the GNU General Public License       #
 #    along with this program.  If not, see <http://www.gnu.org/licenses/>.   #
 ##############################################################################

'''
MemSpace implementation based on shared memory
'''

import mmap
import time
import logging
import struct
import pickle
import posix_ipc
from posix_ipc import SharedMemory, Semaphore, ExistentialError, O_CREX

LOG = logging.getLogger()

PAGESIZE = 4 * 1024

MEMSPACE_VERSION = 1
SHMEM_SIZE = PAGESIZE * 100
MEMSPACE_VERSION = 1
DATA_START = PAGESIZE

FLAG_INVALID = 0x01

OFFSET_VERSION = 0x10
OFFSET_END = 0x20

class MemSpace(object):
    '''
    this class implements a memspace shmem participart
    '''
    def __init__(self, name='MemSpace'):
        '''
        constructor - connect to the shmem
        '''
        self._name = name

        self._mmap = None
        self._lock = None

        self._open()

    def __enter__(self):
        '''
        with statement enter method - just return self.
        '''
        return self

    def __exit__(self, _type, _value, _traceback):
        '''
        with statement exit method - close.
        '''
        self.close()

    @property
    def end(self):
        '''
        produce the position of the tuple after the last
        '''
        return struct.unpack_from('I', self._mmap, OFFSET_END)[0]

    @end.setter
    def end(self, value):
        '''
        set the new end position
        '''
        struct.pack_into('I', self._mmap, OFFSET_END, value)

    def put(self, tpl):
        '''
        put the given tuple into the tuple space.
        '''
        LOG.info('memspace %s: put: %s', self._name, tpl)

        data = pickle.dumps(tpl)
        LOG.debug('  data: %s', data)

        self._lock.acquire()
        LOG.debug('  lock acquired')

        end = self.end
        LOG.debug('  space end: %#010x', end)

        LOG.debug('  packing tuple metadata to offset')
        struct.pack_into('IBB', self._mmap, end, len(data), len(tpl), 0)

        LOG.debug('  writing tuple payload')
        self._mmap[end+6:end+6+len(data)] = data

        LOG.debug('  updating END symbol')
        self.end = end + len(data) + 6

        self._lock.release()
        LOG.debug('  lock released')

    def get(self, tpl):
        '''
        take the queried tuple from the tuple space and return it.
        '''
        LOG.info('memspace %s: get: %s', self._name, tpl)

        start = DATA_START
        while start < self.end:
            LOG.info('  offset: %#010x', start)

            (length, fields, flags) = struct.unpack_from('IBB', self._mmap, start)
            LOG.debug('    length: %#010x, fields: %d, flags: %s', length, fields, '{0:b}'.format(flags))
            if fields != len(tpl):
                LOG.info('    skip: length mismatch.')
                start += 6 + length
                continue
            if flags & FLAG_INVALID:
                LOG.info('     skip: tuple invalidated.')
                start += 6 + length
                continue

            data = self._mmap[start+6:start+6+length]
            LOG.debug('    data: %s', data)

            data = pickle.loads(data)
            LOG.debug('    unpacked: %s', data)

            if all(x == y or y is None for (x, y) in zip(data, tpl)):
                LOG.info('    tentative match :-)')

                self._lock.acquire()
                LOG.debug('    lock acquired')

                (new_flags,) = struct.unpack_from('B', self._mmap, start + 5)
                if new_flags & FLAG_INVALID:
                    LOG.info('    already invalidated... moving on')

                    self._lock.release()
                    LOG.debug('    lock released')
                    start += 6 + length
                    continue

                LOG.info('    real match :^D')

                struct.pack_into('B', self._mmap, start + 5, new_flags | FLAG_INVALID)
                LOG.debug('    invalidated tuple')

                self._lock.release()
                LOG.debug('    lock released')

                return data

            start += 6 + length

        LOG.info('  tail reached. no match.')
        return None

    def read(self, tpl):
        '''
        seek the given tuple in the tuple space and return it.
        '''
        LOG.info('memspace %s: read: %s', self._name, tpl)

        start = DATA_START
        while True:
            LOG.info('  offset: %#010x', start)

            (length, fields, flags) = struct.unpack_from('IBB', self._mmap, start)
            LOG.debug('    length: %#010x, fields: %d, flags: %s', length, fields, '{0:b}'.format(flags))
            if fields != len(tpl):
                LOG.info('    skip: length mismatch.')
                start += 6 + length
                continue
            if flags & FLAG_INVALID:
                LOG.info('    skip: tuple invalidated.')
                start += 6 + length
                continue

            data = self._mmap[start+6:start+6+length]
            LOG.debug('    data: %s', data)

            data = pickle.loads(data)
            LOG.debug('    unpacked: %s', data)

            if all(x == y or y is None for (x, y) in zip(data, tpl)):
                LOG.info('    real match :^D')
                return data

            start += 6 + length

        LOG.info('  tail reached. no match.')
        return None

    def close(self):
        '''
        close the connection to the shmem
        '''
        self._mmap.close()
        self._lock.close()

    def unlink(self):
        '''
        close and destroy the shm and semaphore
        '''
        self.close()
        posix_ipc.unlink_shared_memory(self._name)
        posix_ipc.unlink_semaphore(self._name)

    def _open(self):
        '''
        connect to the shmem of the given name. this initializes the shmem, if
        it does not exist, on exactly one client
        '''
        try:
            self._connect()
        except ExistentialError:
            LOG.warning('shmem %s: connect failed, need to create', self._name)
            try:
                self._create()
            except ExistentialError:
                LOG.warning('shmem %s: create failed, someone was faster', self._name)
                self._connect()

        # wait for space to be initialized
        tries = 0
        while self._mmap[:8] != b'memspace':
            time.sleep(1)
            tries += 1
            if tries >= 10:
                raise ValueError('MemSpace wait timed out - corrupted?')
        if self._mmap[OFFSET_VERSION] != MEMSPACE_VERSION:
            raise ValueError('MemSpace version mismatch')

    def _connect(self):
        '''
        attempt to connect to the shared memory
        '''
        LOG.info('shmem %s: attempting connect', self._name)
        shmem = SharedMemory(self._name)
        self._mmap = mmap.mmap(shmem.fd, shmem.size)
        shmem.close_fd()
        self._lock = Semaphore(self._name)
        LOG.info('shmem %s: connect succeeded', self._name)

    def _create(self):
        '''
        attempt to create and initialize the shared memory
        '''
        LOG.info('shmem %s: attempting create shmem', self._name)
        shmem = SharedMemory(self._name, size=SHMEM_SIZE, flags=O_CREX)
        LOG.info('shmem %s: attempting create mmap', self._name)
        self._mmap = mmap.mmap(shmem.fd, shmem.size)
        shmem.close_fd()
        LOG.info('shmem %s: attempting create semaphore', self._name)
        # TODO: posix_ipc does not support unnamed semaphores yet...
        #       using a named semaphore for now.
        self._lock = Semaphore(self._name, flags=O_CREX)
        LOG.info('shmem %s: create succeeded', self._name)

        try:
            self._initialize()
            self._lock.release()
        except:
            LOG.exception('shmem %s: initialize failed; attempting unlink', self._name)
            shmem.unlink()
            self._lock.unlink()
            raise

    def _initialize(self):
        '''
        prepare the shmem control structures
        '''
        LOG.info('shmem %s: attempting initialize', self._name)
        LOG.info('  writing version number')
        self._mmap[OFFSET_VERSION] = MEMSPACE_VERSION
        LOG.info('  writing initial tail offset')
        self.end = DATA_START
        LOG.info('  writing magic number')
        self._mmap[:8] = b'memspace'
        LOG.info('shmem %s: initialize succeeded', self._name)
