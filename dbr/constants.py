# -*- coding: utf-8 -*-


import sys

from wx import \
    NewId as wxNewId
from wx import \
    MAJOR_VERSION as wxMAJOR_VERSION, \
    MINOR_VERSION as wxMINOR_VERSION, \
    RELEASE_VERSION as wxRELEASE_VERSION

from dbr.language import GT


### *** Debreate Info *** ###

APP_NAME = GT('Debreate')

### Version information ###
RELEASE = 0
VER_MAJ = 0
VER_MIN = 7
VER_REL = 11

if not RELEASE:
    VER_REL += 1

VERSION = (VER_MAJ, VER_MIN, VER_REL)
VERSION_STRING = u'{}.{}.{}'.format(VER_MAJ, VER_MIN, VER_REL)

# Development version
if not RELEASE:
    VERSION_STRING = '{}-dev'.format(VERSION_STRING)

### Website & hosting information ###
HOMEPAGE = u'http://debreate.sourceforge.net/'
gh_project = u'https://github.com/AntumDeluge/debreate'
sf_project = u'https://sourceforge.net/projects/debreate'


### *** Python Info *** ###

PY_VER_MAJ = sys.version_info[0]
PY_VER_MIN = sys.version_info[1]
PY_VER_REL = sys.version_info[2]
PY_VER_STRING = u'{}.{}.{}'.format(PY_VER_MAJ, PY_VER_MIN, PY_VER_REL)


### *** wxWidgets Info *** ###

WX_VER_STRING = '{}.{}.{}'.format(wxMAJOR_VERSION, wxMINOR_VERSION, wxRELEASE_VERSION)


### *** Custom IDs *** ###
ID_OVERWRITE = wxNewId()
ID_APPEND = wxNewId()
# FIXME: Unused IDs
ID_BIN = wxNewId()
ID_SRC = wxNewId()
ID_DSC = wxNewId()
ID_CNG = wxNewId()
