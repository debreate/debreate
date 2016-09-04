#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

FILE = open('INFO')
info = FILE.read().split('\n')
FILE.close()

keys = {}

for l in info:
	if '=' in l:
		key = l.split('=')[0]
		value = l.split('=')[1]
		keys[key] = value

ver = keys['VERSION']
ver_maj = ver.split('.')[0]
ver_min = ver.split('.')[1]
ver_rel = ver.split('.')[2]
release = keys['RELEASE']


# Update version numbers in 'common.py'
FILE = open('common.py', 'r')
common = FILE.read().split('\n')
FILE.close()

for l in common:
	index = common.index(l)
	if ('ver_maj =' in l):
		common[index] = 'ver_maj = {}'.format(ver_maj)
	elif ('ver_min =' in l):
		common[index] = 'ver_min = {}'.format(ver_min)
	elif ('ver_rel =' in l):
		common[index] = 'ver_rel = {}'.format(ver_rel)
	elif ('RELEASE =' in l):
		common[index] = 'RELEASE = {}'.format(release)

FILE = open('common.py', 'w')
FILE.write('\n'.join(common))
FILE.close()


# Update version numbers in 'Makefile'
FILE = open('Makefile', 'r')
makefile = FILE.read().split('\n')
FILE.close()

for l in makefile:
	index = makefile.index(l)
	if ('VERSION =' in l or 'VERSION=' in l):
		makefile[index] = 'VERSION = {}'.format(ver)

FILE = open('Makefile', 'w')
FILE.write('\n'.join(makefile))
FILE.close()
