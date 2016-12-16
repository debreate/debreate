# -*- coding: utf-8 -*-

## \package globals.system

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, wx

from globals.fileio import ReadFile


# *** Python Info *** #

PY_VER_MAJ = sys.version_info[0]
PY_VER_MIN = sys.version_info[1]
PY_VER_REL = sys.version_info[2]
PY_VER_STRING = u'{}.{}.{}'.format(PY_VER_MAJ, PY_VER_MIN, PY_VER_REL)


# *** wxWidgets Info *** #

WX_VER_STRING = u'{}.{}.{}'.format(wx.MAJOR_VERSION, wx.MINOR_VERSION, wx.RELEASE_VERSION)


# *** Operating System Info *** #

def GetOSInfo(key, upstream=False):
    lsb_release = u'/etc/lsb-release'
    
    if upstream:
        lsb_release = u'/etc/upstream-release/lsb-release'
    
    if not os.path.isfile(lsb_release):
        return None
    
    release_data = ReadFile(lsb_release, split=True)
    
    value = None
    
    for L in release_data:
        if L.startswith(key):
            value = L.replace(u'{}='.format(key), u'').replace(u'"', u'')
            break
    
    return value


OS_name = GetOSInfo(u'DISTRIB_ID')
OS_version = GetOSInfo(u'DISTRIB_RELEASE')
OS_codename = GetOSInfo(u'DISTRIB_CODENAME')

OS_upstream_name = GetOSInfo(u'DISTRIB_ID', True)
OS_upstream_version = GetOSInfo(u'DISTRIB_RELEASE', True)
OS_upstream_codename = GetOSInfo(u'DISTRIB_CODENAME', True)
