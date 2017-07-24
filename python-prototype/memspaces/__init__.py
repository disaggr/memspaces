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
import memspaces implementations to module level
'''

import logging
from logging.config import dictConfig
from .xmlrpc import MemSpaceClient, MemSpaceServer
from .shmem import MemSpace


LOGGING_CONFIG = dict(
    version=1,
    formatters={
        'f': {
            'format': '%(asctime)s [%(name)s] [%(levelname)s] :: %(message)s'
        }
    },
    handlers={
        'h': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
            'level': logging.WARNING
        }
    },
    root={
        'handlers': ['h'],
        'level': logging.WARNING,
    },
)

dictConfig(LOGGING_CONFIG)
