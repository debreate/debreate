#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, errno, time


# Ubuntu release
release = u'xenial'
urgency = u'low'

FILE_changelog = u'docs/changelog'
FILE_changelog_debian = u'debian/changelog'

# Reading source log
if not os.path.isfile(FILE_changelog):
    print(u'ERROR: Source changelog does not exist, can\'t continue: {}'.format(FILE_changelog))
    
    sys.exit(errno.ENOENT)

TEMP = open(FILE_changelog, u'r')
changelog_data = TEMP.read().split(u'\n')
TEMP.close()

# Extract version number
#version_string = changelog_data[0]
#changelog_data = changelog_data[1:]

cutoff_index = 0
for L in changelog_data:
    if not L.strip():
        # Reached a new segment
        cutoff_index = changelog_data.index(L)
        break

version_data = changelog_data[:cutoff_index]

# Format new entry
version_data[0] = u'debreate ({}) {}; urgency={}'.format(version_data[0], release, urgency)

for L in version_data:
    if L.startswith(u'- '):
        version_data[changelog_data.index(L)] = u'    {}'.format(L[1:])

version_data[1] = version_data[1].replace(u'    ', u'  * ')

version_data.insert(1, u'')
version_data.append(u'')
version_data.append(u' -- Jordan Irwin <antumdeluge@gmail.com>  {}'.format(time.strftime(u'%a, %d %b %Y %H:%M:%S %z')))

version_data = u'\n'.join(version_data)

print(u'Writing new changelog entry:\n\n{}'.format(version_data))

if os.path.isfile(FILE_changelog_debian):
    TEMP = open(FILE_changelog_debian, u'r')
    version_data = u'{}\n\n\n{}'.format(version_data, TEMP.read())
    TEMP.close()

TEMP = open(FILE_changelog_debian, u'w')
TEMP.write(version_data)
TEMP.close()
