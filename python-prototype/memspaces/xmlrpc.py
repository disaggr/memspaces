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
This module implements a simple client and server component for tuple spaces.
'''

from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer


class MemSpaceApi(object):
    '''
    this class implements the tuple space api on the server side.
    '''

    def __init__(self):
        '''
        constructor - prepare the tuple storage
        '''
        self._tuples = []

    def put(self, tpl):
        '''
        put the given tuple into the tuple space.
        '''
        self._tuples.append(tpl)

    def get(self, tpl):
        '''
        take the queried tuple from the tuple space and return it.
        '''
        for i, t in enumerate(self._tuples):
            if len(tpl) == len(t) and all(x == y or x is None for (x, y) in zip(tpl, t)):
                res = self._tuples[i]
                del self._tuples[i]
                return res
        return None

    def read(self, tpl):
        '''
        seek the given tuple in the tuple space and return it.
        '''
        for i, t in enumerate(self._tuples):
            if len(tpl) == len(t) and all(x == y or x is None for (x, y) in zip(tpl, t)):
                return self._tuples[i]
        return None


class MemSpaceClient(ServerProxy):
    '''
    The tuple spaces client.
    '''

    def __init__(self, server, *args, **kwargs):
        '''
        constructor - connect to the given server.
        '''
        super(MemSpaceClient, self).__init__(
            server,
            allow_none=True,
            use_builtin_types=True,
            *args, **kwargs
        )


class MemSpaceServer(SimpleXMLRPCServer):
    '''
    The tuple spaces server.
    '''

    def __init__(self, server, port, *args, **kwargs):
        '''
        constructor - start listening on the given server and port.
        '''
        super(MemSpaceServer, self).__init__(
            (server, port),
            allow_none=True,
            use_builtin_types=True,
            logRequests=False,
            *args, **kwargs
        )
        self.register_instance(MemSpaceApi())
