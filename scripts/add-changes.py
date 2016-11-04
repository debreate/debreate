#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# HOWTO:
#   To add a changelog entry:
#     - Edit the INFO file in the root directory
#     - Change the values of AUTHOR & EMAIL
#     - Run this script (from any location)
#       - A new entry will be written to 'docs/changelog'
#     - Edit 'docs/changelog' to add new changes
#     - For Debian builds:
#       - Copy 'docs/changelog' to 'debian/changelog'
#
#    If a filename is used as the first argument, the
#    script will copy any lines beginning with an alpha-
#    numeric character & add them to the changelog
#    output file.

import os, sys, time, errno
from scripts_globals import file_CHANGELOG, GetInfoValue


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
    
    if len(changes_lines):
        return changes_lines
    
    return None


# Package details
package = GetInfoValue('NAME').lower()
new_version = GetInfoValue('VERSION')

# Packager details
packager = GetInfoValue('AUTHOR')
email = GetInfoValue('EMAIL')

# Distribution details
dist = GetInfoValue('DIST')
urgency = GetInfoValue('URGENCY')

date_string = unicode(time.strftime('%a, %d %b %Y'))
time_string = unicode(time.strftime('%T %z'))


# Check if we are importing changes from a text file
if len(sys.argv) > 1:
    CHANGES = AddChanges(sys.argv[1])

if CHANGES != None and len(CHANGES):
    for LI in CHANGES:
        l_index = CHANGES.index(LI)
        if l_index == 0:
            CHANGES[l_index] = '  * {}'.format(CHANGES[l_index])
        else:
            CHANGES[l_index] = '    {}'.format(CHANGES[l_index])
    
    CHANGES = '\n'.join(CHANGES)
else:
    CHANGES = '  *'

entry_string = '{} ({}) {}; urgency={}\n\n{}\n\n'.format(package, new_version, dist, urgency, CHANGES)
entry_string += ' -- {} <{}>  {} {}'.format(packager, email, date_string, time_string)

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
        if 'debreate ({})'.format(new_version) in LI:
            print('There is already an entry for version {}, exiting ...'.format(new_version))
            sys.exit(0)
    
    cl_text = '{}\n\n\n{}'.format(entry_string, cl_text)

cl_data = open(file_CHANGELOG, 'w')
cl_data.write(cl_text)
cl_data.close()
