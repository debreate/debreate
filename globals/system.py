# -*- coding: utf-8 -*-

## \package globals.system

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, wx

from globals.fileio     import ReadFile
from globals.strings    import RemoveEmptyLines


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


## Get a list of available system release codenames
def GetOSCodeNames():
    code_names = []
    
    # Ubuntu & Linux Mint distributions
    global OS_codename, OS_upstream_codename
    
    for CN in (OS_codename, OS_upstream_codename,):
        if CN and CN not in code_names:
            code_names.append(CN)
    
    # Debian distributions
    FILE_debian = u'/etc/debian_version'
    if os.path.isfile(FILE_debian):
        debian_names = RemoveEmptyLines(ReadFile(FILE_debian, split=True))[:1]
        if u'/' in debian_names[0]:
            debian_names = debian_names[0].split(u'/')
        
        # Add generic Debian release names
        debian_names = debian_names + [u'stable', u'testing', u'unstable',]
        
        for CN in debian_names:
            code_names.append(CN)
    
    return tuple(sorted(code_names))
