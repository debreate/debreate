# -*- coding: utf-8 -*-

# MIT licensing
# See: docs/LICENSE.txt

import os, sys, errno


## Check if an item is a string
def IsString(item):
    if sys.version_info[0] <= 2:
        return isinstance(item, (unicode, str))
    
    return isinstance(item, str)


def PrependStringZeros(string):
    longest = 4
    difference = longest - len(string)
    
    for X in range(difference):
        string = '0{}'.format(string)
    
    return string


def lprint(message, line=None):
    newlines = 0
    
    if isinstance(message, (unicode, str)):
        while message.startswith('\n'):
            newlines += 1
            message = message[1:]
    
    if line != None:
        message = '[L:{}] {}'.format(PrependStringZeros(str(line)), message)
    
    for X in range(newlines):
        message = '\n{}'.format(message)
    
    print(message)


## Join one or more strings into a path
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
        pathList[INDEX] = pathList[INDEX].strip('/')
    
    path = '/'.join(pathList)
    
    while '//' in path:
        path = path.replace('//', '/')
    
    # FIXME: How to add 'absolute' argument with ambiguous arg count for 'tail'
    absolute = True
    if absolute and not path.startswith('/'):
        path = '/' + path
    
    return path


DIR_scripts = os.path.dirname(__file__)
DIR_root = os.path.dirname(DIR_scripts)

FILE_info = '{}/INFO'.format(DIR_root)

if not os.path.isfile(FILE_info):
    print('[ERROR] Required file not found: {}'.format(FILE_info))
    sys.exit(errno.ENOENT)

FILE_doxyfile = '{}/docs/Doxyfile'.format(DIR_root)
FILE_locale = '{}/locale/debreate.pot'.format(DIR_root)
PY_app = '{}/globals/application.py'.format(DIR_root)

FILE_make = '{}/Makefile.in'.format(DIR_root)
FILE_changelog = '{}/docs/changelog'.format(DIR_root)
FILE_changelog_debian = 'debian/changelog'

FILE_BUFFER = open(FILE_info)
INFO_data = FILE_BUFFER.read().split('\n')
FILE_BUFFER.close()

INFO_keys = {}

for L in INFO_data:
    if len(L):
        # Skip lines that begin with hashtag or whitespace
        if L[0] not in ('#', ' '):
            if '=' in L:
                key = L.split('=')
                value = key[1]
                key = key[0].upper()
                
                INFO_keys[key] = value


def GetInfoValue(key):
    return INFO_keys[key.upper()]


required_locale_files = (
)

version_files = {
    'application': PY_app,
    'doxyfile': FILE_doxyfile,
    'locale': FILE_locale,
    'makefile': FILE_make,
}

debian_files = {
    'changelog': FILE_changelog,
    'changelog debian': FILE_changelog_debian,
    }
