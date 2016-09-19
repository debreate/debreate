# -*- coding: utf-8 -*-

## \package dbr.constants
#  Global constants used throughout Debreate


import sys, os

from wx import \
    NewId as wxNewId
from wx import \
    MAJOR_VERSION as wxMAJOR_VERSION, \
    MINOR_VERSION as wxMINOR_VERSION, \
    RELEASE_VERSION as wxRELEASE_VERSION

from dbr.language import GT


# *** System Information *** #

## Full path to the application's directory
#  
#  FIXME: Hack to get parent directory
application_path = os.path.dirname(os.path.dirname(__file__))

## Root home directory where configuration is stored
#  
#  The configuration file is set to HOME/.config/debreate/config
homedir = os.getenv('HOME')


# *** Debreate Information *** #

## Application's displayed name
APP_NAME = GT('Debreate')

# Version information #
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

# Website & hosting information #
HOMEPAGE = u'http://debreate.sourceforge.net/'
gh_project = u'https://github.com/AntumDeluge/debreate'
sf_project = u'https://sourceforge.net/projects/debreate'

PROJECT_FILENAME_SUFFIX = 'dbpz'

## Enable debugging
#  
#  If DEBUG is set to 'True', some extra code will be executed
DEBUG = True


# *** Python Info *** #

PY_VER_MAJ = sys.version_info[0]
PY_VER_MIN = sys.version_info[1]
PY_VER_REL = sys.version_info[2]
PY_VER_STRING = u'{}.{}.{}'.format(PY_VER_MAJ, PY_VER_MIN, PY_VER_REL)


# *** wxWidgets Info *** #

WX_VER_STRING = '{}.{}.{}'.format(wxMAJOR_VERSION, wxMINOR_VERSION, wxRELEASE_VERSION)


# *** Custom IDs *** #
ID_OVERWRITE = wxNewId()
ID_APPEND = wxNewId()
# FIXME: Unused IDs
ID_BIN = wxNewId()
ID_SRC = wxNewId()
ID_DSC = wxNewId()
ID_CNG = wxNewId()


# *** Icons *** #
ICON_ERROR = "{}/bitmaps/error64.png".format(application_path)
ICON_INFORMATION = "{}/bitmaps/question64.png".format(application_path)


# *** Colors depicting importance of fields
Mandatory = (255,200,192)
Recommended = (197,204,255)
Optional = (255,255,255)
Unused = (200,200,200)
Disabled = (246, 246, 245)
