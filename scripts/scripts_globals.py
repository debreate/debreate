# -*- coding: utf-8 -*-

# MIT licensing
# See: docs/LICENSE.txt

import os, sys, errno


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


def ConcatPaths(root, tail):
    if not root:
        return tail.replace('//', '/')
    
    return '{}/{}'.format(root, tail).replace('//', '/')


scripts_dir = os.path.dirname(__file__)
root_dir = os.path.split(scripts_dir)[0]

FILE_info = '{}/INFO'.format(root_dir)

if not os.path.isfile(FILE_info):
    print('[ERROR] Required file not found: {}'.format(FILE_info))
    sys.exit(errno.ENOENT)

FILE_locale = '{}/locale/debreate.pot'.format(root_dir)
PY_app = '{}/globals/application.py'.format(root_dir)

FILE_make = '{}/Makefile'.format(root_dir)
FILE_changelog = '{}/docs/changelog'.format(root_dir)
FILE_changelog_debian = 'debian/changelog'

f_opened = open(FILE_info)
data_INFO = f_opened.read().split('\n')
f_opened.close()

keys_INFO = {}

for L in data_INFO:
    if len(L):
        # Skip lines that begin with hashtag or whitespace
        if L[0] not in ('#', ' '):
            if '=' in L:
                key = L.split('=')
                value = key[1]
                key = key[0].upper()
                
                keys_INFO[key] = value


def GetInfoValue(key):
    return keys_INFO[key.upper()]


required_locale_files = (
)

version_files = {
    'application': PY_app,
    'locale': FILE_locale,
    'makefile': FILE_make,
}

debian_files = {
    'changelog': FILE_changelog,
    'changelog debian': FILE_changelog_debian,
    }
