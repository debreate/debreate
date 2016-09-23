#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from datetime import datetime, date
import os, sys, time

cl_file = u'debian/changelog'
info_file = u'INFO'

if not os.path.isfile(info_file):
    print(u'ERROR: Cannot find file "{}" for reading'.format(info_file))
    sys.exit(1)

info_data = open(info_file, u'r')
info_lines = info_data.read().split(u'\n')
info_data.close()

info = {}
for L in info_lines:
    if len(L):
        # Skip lines that begin with hashtag or whitespace
        if L[0] not in (u'#', u' '):
            if u'=' in L:
                key = L.split(u'=')[0]
                value = L.split(u'=')[1]
                info[key] = value

# Package details
package = info[u'NAME'].lower()
new_version = info[u'VERSION']

# Packager details
packager = info[u'AUTHOR']
email = info[u'EMAIL']

# Distribution details
dist = info[u'DIST']
urgency = info[u'URGENCY']

date_string = unicode(time.strftime(u'%a, %d %b %Y'))
time_string = unicode(time.strftime(u'%T %z'))

entry_string = u'{} ({}) {}; urgency={}\n\n  *\n\n'.format(package, new_version, dist, urgency)
entry_string += u' -- {} <{}>  {} {}'.format(packager, email, date_string, time_string)


cl_prepend = os.path.isfile(cl_file)

if cl_prepend:
    cl_data = open(cl_file, u'r')
    cl_text = cl_data.read()
    cl_data.close()

    cl_text = u'{}\n\n\n{}'.format(entry_string, cl_text)

else:
    cl_text = u'{}\n'.format(entry_string)

cl_data = open(cl_file, u'w')
cl_data.write(cl_text)
cl_data.close()


