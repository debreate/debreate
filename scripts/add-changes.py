#!/usr/bin/env python3

# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

# HOWTO:
#  To add a changelog entry:
#  - Run this script (from any location)
#    - A new entry will be written to 'docs/changelog'
#  - Edit 'docs/changelog' to add new changes
#  - For Debian builds:
#    - Run 'scripts/update-debian-changelog.py'
#
#  If a filename is used as the first argument, the
#  script will copy any lines beginning with an alpha-
#  numeric character & add them to the changelog
#  output file.

import os
import sys
import time
import errno

path_script = os.path.realpath(sys.argv[0])
dir_scripts = os.path.dirname(path_script)
dir_app = os.path.dirname(dir_scripts)

sys.path.insert(0, os.path.join(dir_app, "lib"))

from libdbr import config
from libdbr import paths

cfg = config.add("build", paths.join(dir_app, "build.conf"))
file_CHANGELOG = paths.join(dir_app, "docs/changelog.txt")
CHANGES = None

# Writes information from changes_file to changelog output
def AddChanges(changes_file):
	if not os.path.isfile(changes_file):
		print('ERROR: File does not exist: {}'.format(changes_file))
		sys.exit(errno.ENOENT)

	FILE = open(changes_file)
	changes_data = FILE.read().split('\n')
	FILE.close()

	changes_lines = []
	for LI in changes_data:
		if len(LI):
			# Only recognize lines that begin with an alphabetic letter or number
			if LI[0].isalnum():
				changes_lines.append(LI)

			# These lines are indented
			elif LI.strip(' ') and LI.strip(' ')[0] in ('-', '*', '\t'):
				changes_lines.append(LI.strip(' '))

	if len(changes_lines):
		return changes_lines

	return None


# Version details
new_version = cfg.getValue("version")
dev_version = cfg.getValue("version_dev")
if dev_version.isdigit():
	dev_version = int(dev_version)

	if dev_version:
		new_version = '{}dev{}'.format(new_version, dev_version)


# Check if we are importing changes from a text file
if len(sys.argv) > 1:
	CHANGES = AddChanges(sys.argv[1])

if CHANGES != None and len(CHANGES):
	for LI in CHANGES:
		l_index = CHANGES.index(LI)

		# These lines are indented
		if LI[0] in ('-', '*', '\t'):
			# Remove delimiter & strip whitespace
			CHANGES[l_index] = '  - {}'.format(LI[1:].strip(' '))
			continue

		CHANGES[l_index] = '- {}'.format(CHANGES[l_index])

	CHANGES = '\n'.join(CHANGES)
else:
	CHANGES = '- <add changes here>'

entry_string = '{}\n{}'.format(new_version, CHANGES)

new_log = not os.path.isfile(file_CHANGELOG)

if not new_log:
	cl_data = open(file_CHANGELOG, 'r')
	cl_text = cl_data.read()
	cl_data.close()

	# Check if log is empty
	new_log = (''.join(''.join(cl_text.split(' ')).split('\n')) == '')

if new_log:
	cl_text = '{}\n'.format(entry_string)

else:
	log_lines = cl_text.split('\n')
	for LI in log_lines:
		if LI.startswith(new_version):
			print('There is already an entry for version {}, exiting ...'.format(new_version))
			sys.exit(0)

	cl_text = '{}\n\n{}'.format(entry_string, cl_text)

cl_data = open(file_CHANGELOG, 'w')
cl_data.write(cl_text)
cl_data.close()
