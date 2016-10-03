#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


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
RELEASE = GetInfoValue('RELEASE')


def UpdateSingleLineFile(filename, testline, newvalue=VERSION, suffix=''):
    l_length = len(testline)
    
    FILE = open(filename, 'r')
    lines_orig = FILE.read().split('\n')
    FILE.close()
    
    lines_new = list(lines_orig)
    
    for l in lines_new:
        l_index = lines_new.index(l)
        if l[:l_length] == testline:
            lines_new[l_index] = '{}{}{}'.format(testline, newvalue, suffix)
            break
    
    if lines_new != lines_orig:
        print('Writing new version information to {}'.format(filename))
        
        FILE = open(filename, 'w')
        FILE.write('\n'.join(lines_new))
        FILE.close()



UpdateSingleLineFile(version_files['constants'], 'VER_MAJ = ', newvalue=VER_MAJ)
UpdateSingleLineFile(version_files['constants'], 'VER_MIN = ', newvalue=VER_MIN)
UpdateSingleLineFile(version_files['constants'], 'VER_REL = ', newvalue=VER_REL)
UpdateSingleLineFile(version_files['constants'], 'RELEASE = ', newvalue=RELEASE)
UpdateSingleLineFile(version_files['makefile'], 'VERSION = ')
UpdateSingleLineFile(version_files['doxyfile'], 'PROJECT_NUMBER         = ')
UpdateSingleLineFile(version_files['locale'], '"Project-Id-Version: Debreate ', suffix='\\n"')
