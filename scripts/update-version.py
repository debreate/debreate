#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


from os.path import exists
import sys


info_file = 'INFO'
constants_file = 'dbr/constants.py'
makefile_file = 'Makefile'

for I in (info_file, constants_file, makefile_file):
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

ver = keys['VERSION']
ver_maj = ver.split('.')[0]
ver_min = ver.split('.')[1]
ver_rel = ver.split('.')[2]
release = keys['RELEASE']


# Update version numbers in 'constants.py'
FILE = open(constants_file, 'r')
constants_data = FILE.read().split('\n')
FILE.close()

for l in constants_data:
	index = constants_data.index(l)
	if ('VER_MAJ =' in l):
		constants_data[index] = 'VER_MAJ = {}'.format(ver_maj)
	elif ('VER_MIN =' in l):
		constants_data[index] = 'VER_MIN = {}'.format(ver_min)
	elif ('VER_REL =' in l):
		constants_data[index] = 'VER_REL = {}'.format(ver_rel)
	elif ('RELEASE =' in l):
		constants_data[index] = 'RELEASE = {}'.format(release)

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
		makefile_data[index] = 'VERSION = {}'.format(ver)

FILE = open(makefile_file, 'w')
FILE.write('\n'.join(makefile_data))
FILE.close()
