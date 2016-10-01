# -*- coding: utf-8 -*-


import os, sys, errno


scripts_dir = os.path.dirname(__file__)
root_dir = os.path.split(scripts_dir)[0]

file_INFO = '{}/INFO'.format(root_dir)

if not os.path.isfile(file_INFO):
    print('[ERROR] Required file not found: {}'.format(file_INFO))
    sys.exit(errno.ENOENT)

f_opened = open(file_INFO)
data_INFO = f_opened.read().split('\n')
f_opened.close()

keys_INFO = {}

for L in data_INFO:
    if '=' in L:
        key = L.split('=')
        value = key[1]
        key = key[0].upper()
        
        keys_INFO[key] = value


def GetInfoValue(key):
    return keys_INFO[key.upper()]


required_locale_files = (
)
