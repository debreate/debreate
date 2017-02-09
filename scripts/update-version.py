#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, errno
from scripts_globals import version_files, GetInfoValue


for F in version_files:
    if not os.path.isfile(version_files[F]):
        print('[ERROR] Required file not found: {}'.format(version_files[F]))
        sys.exit(errno.ENOENT)


VERSION = GetInfoValue('VERSION')
VER_MAJ = VERSION.split('.')[0]
VER_MIN = VERSION.split('.')[1]
VER_REL = VERSION.split('.')[2]
VERSION_dev = GetInfoValue('VERSION_dev')


def UpdateSingleLineFile(filename, testline, newvalue=VERSION, suffix=''):
    FILE = open(filename, 'r')
    lines_orig = FILE.read().split('\n')
    FILE.close()
    
    lines_new = list(lines_orig)
    
    for l in lines_new:
        l_index = lines_new.index(l)
        if l.strip(' ').startswith(testline):
            # Preserve whitespace
            ws = ''
            if l.startswith(' '):
                ws = l.split(testline)[0]
            
            lines_new[l_index] = '{}{}{}{}'.format(ws, testline, newvalue, suffix)
            
            # Only change first instance
            break
    
    if lines_new != lines_orig:
        print('Writing new version information to {}'.format(filename))
        
        FILE = open(filename, 'w')
        FILE.write('\n'.join(lines_new))
        FILE.close()


UpdateSingleLineFile(version_files['application'], 'VERSION_maj = ', newvalue=VER_MAJ)
UpdateSingleLineFile(version_files['application'], 'VERSION_min = ', newvalue=VER_MIN)
UpdateSingleLineFile(version_files['application'], 'VERSION_rel = ', newvalue=VER_REL)
UpdateSingleLineFile(version_files['application'], 'VERSION_dev = ', newvalue=VERSION_dev)
UpdateSingleLineFile(version_files['doxyfile'], 'PROJECT_NUMBER         = ')
UpdateSingleLineFile(version_files['locale'], '"Project-Id-Version: Debreate ', suffix='\\n"')
UpdateSingleLineFile(version_files['makefile'], 'VERSION = ', newvalue=VERSION)
