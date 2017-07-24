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
this module is the entry point for the tuple spaces server.
'''

import argparse
from memspaces import MemSpaceServer


def main():
    '''
    entry point - invoked when run from the command line.
    '''
    parser = argparse.ArgumentParser(description='memspaces xmlrpc server')
    parser.add_argument(
        '--listen', action='store', default='127.0.0.1',
        help='the host to listen on for memspaces client connections')
    parser.add_argument(
        '--port', action='store', default=8888, type=int,
        help='the port to listen on for memspaces client connections')

    args = parser.parse_args()
    server = MemSpaceServer(args.listen, args.port)
    server.serve_forever()


if __name__ == '__main__':
    main()
