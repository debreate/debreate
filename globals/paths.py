# -*- coding: utf-8 -*-

## \package globals.paths
#  
#  Global paths used in the app

# MIT licensing
# See: docs/LICENSE.txt


import os

from globals.strings import GS


def ConcatPaths(path_list):
    if not isinstance(path_list, (list, tuple)):
        # FIXME: Need error checking
        return None
    
    return u'/'.join(path_list).replace(u'//', u'/')


# *** System paths *** #

## Directory where app is installed
#  HACK: test
#  HACK: Call os.path.dirname twice to get root directory.
#        This is necessary because this variable is
#        declared from a sub-directory.
PATH_app = GS(os.path.dirname(os.path.dirname(__file__)))

## User's home directory
#  
#  Used to set config directory.
PATH_home = GS(os.getenv(u'HOME'))

## Local folder to store files such as custom templates
PATH_local = ConcatPaths((PATH_home, u'.local/share/debreate'))

## Directory where cache files are stored
PATH_cache = ConcatPaths((PATH_local, u'cache'))

## Directory where log files are stored
PATH_logs = ConcatPaths((PATH_local, u'logs'))

## Directory where app bitmaps are stored
PATH_bitmaps = u'{}/bitmaps'.format(PATH_app)
