# -*- coding: utf-8 -*-


import os, sys, errno


scripts_dir = os.path.dirname(__file__)
root_dir = os.path.split(scripts_dir)[0]

file_INFO = '{}/INFO'.format(root_dir)

file_CONSTANTS = '{}/dbr/constants.py'.format(root_dir)
file_MAKEFILE = '{}/Makefile'.format(root_dir)
file_DOXYFILE = '{}/docs/Doxyfile'.format(root_dir)
file_LOCALE = '{}/locale/debreate.pot'.format(root_dir)

file_CHANGELOG = '{}/docs/changelog'.format(root_dir)

if not os.path.isfile(file_INFO):
    print('[ERROR] Required file not found: {}'.format(file_INFO))
    sys.exit(errno.ENOENT)

f_opened = open(file_INFO)
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
    'constants': file_CONSTANTS,
    'makefile': file_MAKEFILE,
    'doxyfile': file_DOXYFILE,
    'locale': file_LOCALE,
}
