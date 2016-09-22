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
#  The configuration file is set to <HOME>/.config/debreate/config
home_path = os.getenv(u'HOME')

## Directory where local files will be stored
#  
#  <HOME>/.local/share/debreate
local_path = u'{}/.local/share/debreate'.format(home_path)


# *** Debreate Information *** #

## Application's displayed name
APP_NAME = GT(u'Debreate')

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
    VERSION_STRING = u'{}-dev'.format(VERSION_STRING)

# Website & hosting information #
HOMEPAGE = u'http://debreate.sourceforge.net/'
gh_project = u'https://github.com/AntumDeluge/debreate'
sf_project = u'https://sourceforge.net/projects/debreate'

PROJECT_FILENAME_SUFFIX = u'dbpz'

# *** Python Info *** #

PY_VER_MAJ = sys.version_info[0]
PY_VER_MIN = sys.version_info[1]
PY_VER_REL = sys.version_info[2]
PY_VER_STRING = u'{}.{}.{}'.format(PY_VER_MAJ, PY_VER_MIN, PY_VER_REL)


# *** wxWidgets Info *** #

WX_VER_STRING = u'{}.{}.{}'.format(wxMAJOR_VERSION, wxMINOR_VERSION, wxRELEASE_VERSION)


# *** Custom IDs *** #
ID_OVERWRITE = wxNewId()
ID_APPEND = wxNewId()
# FIXME: Unused IDs
ID_BIN = wxNewId()
ID_SRC = wxNewId()
ID_DSC = wxNewId()
ID_CNG = wxNewId()

# Page IDs
ID_BUILD = wxNewId()
ID_CHANGELOG = wxNewId()
ID_CONTROL = wxNewId()
ID_COPYRIGHT = wxNewId()
ID_DEPENDS = wxNewId()
ID_FILES = wxNewId()
ID_GREETING = wxNewId()
ID_MAN = wxNewId()
ID_MENU = wxNewId()
ID_SCRIPTS = wxNewId()


# *** Icons *** #
ICON_ERROR = u'{}/bitmaps/error64.png'.format(application_path)
ICON_INFORMATION = u'{}/bitmaps/question64.png'.format(application_path)


# *** Colors depicting importance of fields
Mandatory = (255,200,192)
Recommended = (197,204,255)
Optional = (255,255,255)
Unused = (200,200,200)
Disabled = (246, 246, 245)


## Location of common licenses installed on the system
system_licenses_path = u'/usr/share/common-licenses'
