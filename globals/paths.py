# -*- coding: utf-8 -*-

## \package globals.paths
#  
#  Global paths used in the app

# MIT licensing
# See: docs/LICENSE.txt


import os

from globals.strings import GS
from globals.strings import IsString


## Joints multiple strings into a single path
#
#  \param pathList
#    <b><i>List</i></b> of strings to be concatenated
#  \param tail
#    Strings to be concatenated to root argument (pathList)
def ConcatPaths(pathList, *tail):
    # Convert string arg to list
    if IsString(pathList):
        pathList = [pathList,]
    
    # Make sure we are working with a list instance
    pathList = list(pathList)
    
    # Append tail arguments
    if tail:
        pathList += tail
    
    # Clean up tail arguments
    for INDEX in range(len(pathList)):
        pathList[INDEX] = pathList[INDEX].strip(u'/')
    
    path = u'/'.join(pathList)
    
    while u'//' in path:
        path = path.replace(u'//', u'/')
    
    # FIXME: How to add 'absolute' argument with ambiguous arg count for 'tail'
    absolute = True
    if absolute and not path.startswith(u'/'):
        path = u'/' + path
    
    return path


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
