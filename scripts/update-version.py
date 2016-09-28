#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


from os.path import exists
import sys


info_file = 'INFO'
constants_file = 'dbr/constants.py'
makefile_file = 'Makefile'
doxygen_file = 'docs/Doxyfile'

for I in (info_file, constants_file, makefile_file, doxygen_file):
	if not exists(I):
		print('ERROR: "{}" file not found, cannot update version'.format(I))
		sys.exit(1)

FILE = open(info_file)
info_data = FILE.read().split('\n')
FILE.close()

keys = {}

for l in info_data:
	if '=' in l:
		key = l.split('=')[0]
		value = l.split('=')[1]
		keys[key] = value

VERSION = keys['VERSION']
VER_MAJ = VERSION.split('.')[0]
VER_MIN = VERSION.split('.')[1]
VER_REL = VERSION.split('.')[2]
RELEASE = keys['RELEASE']


# Update version numbers in 'constants.py'
FILE = open(constants_file, 'r')
constants_data = FILE.read().split('\n')
FILE.close()

for l in constants_data:
	index = constants_data.index(l)
	if ('VER_MAJ =' in l):
		constants_data[index] = 'VER_MAJ = {}'.format(VER_MAJ)
	elif ('VER_MIN =' in l):
		constants_data[index] = 'VER_MIN = {}'.format(VER_MIN)
	elif ('VER_REL =' in l):
		constants_data[index] = 'VER_REL = {}'.format(VER_REL)
	elif ('RELEASE =' in l):
		constants_data[index] = 'RELEASE = {}'.format(RELEASE)

FILE = open(constants_file, 'w')
FILE.write('\n'.join(constants_data))
FILE.close()


# Update version numbers in 'Makefile'
FILE = open(makefile_file, 'r')
makefile_data = FILE.read().split('\n')
FILE.close()

for l in makefile_data:
	index = makefile_data.index(l)
	if ('VERSION =' in l or 'VERSION=' in l):
		makefile_data[index] = 'VERSION = {}'.format(VERSION)

FILE = open(makefile_file, 'w')
FILE.write('\n'.join(makefile_data))
FILE.close()


# Update version in 'Doxyfile'
FILE = open(doxygen_file, 'r')
doxygen_data = FILE.read().split('\n')
FILE.close()

file_changed = False

for l in doxygen_data:
    index = doxygen_data.index(l)
    if 'PROJECT_NUMBER         =' in l:
        doxygen_data[index] = 'PROJECT_NUMBER         = {}'.format(VERSION)
        file_changed = True

if file_changed:
    FILE = open(doxygen_file, 'w')
    FILE.write('\n'.join(doxygen_data))
    FILE.close()
