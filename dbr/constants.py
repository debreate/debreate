# -*- coding: utf-8 -*-

## \package dbr.constants
#  
#  Global variables used throughout the application & should remain constant.


# System modules
import errno, os, sys, wx

# Local modules
from dbr.language       import GT
from dbr.commandcheck   import CommandExists
from globals.paths      import PATH_app


# *** System Information *** #

## Root home directory where configuration is stored
#  
#  The configuration file is set to <HOME>/.config/debreate/config
home_path = os.getenv(u'HOME')

## Directory where local files will be stored
#  
#  <HOME>/.local/share/debreate
local_path = u'{}/.local/share/debreate'.format(home_path)


# *** Debreate Information *** #

## Determins if the application is running as portable or installed
INSTALLED = False
if os.path.isfile(u'{}/INSTALLED'.format(PATH_app)):
    INSTALLED = True

def GetPrefix():
    INSTALLED
    
    if not INSTALLED:
        return PATH_app
    
    FILE = open(u'{}/INSTALLED'.format(PATH_app))
    lines = FILE.read().split(u'\n')
    FILE.close()
    
    for L in lines:
        if u'=' in L:
            key = L.split(u'=')
            value = key[1]
            key = key[0]
            
            if key.lower() == u'prefix':
                return value
    
    return PATH_app


PREFIX = GetPrefix()

## Application's displayed name
APP_NAME = GT(u'Debreate')
AUTHOR = u'Jordan Irwin'
EMAIL = u'antumdeluge@gmail.com'
MAIN_ICON = wx.Icon(u'{}/bitmaps/debreate64.png'.format(PATH_app), wx.BITMAP_TYPE_PNG)

# Project filename
PROJECT_LEGACY_SUFFIX = u'dbp'
PROJECT_FILENAME_SUFFIX = u'dbpz'

ID_PROJ_Z = wx.NewId()
ID_PROJ_L = wx.NewId()
ID_PROJ_A = wx.NewId()
ID_PROJ_T = wx.NewId()

supported_suffixes = (
    u'dbpz',
    u'dbp',
    u'tar',
    u'tar.gz',
    u'tar.bz2',
    u'tar.xz',
    u'zip',
)

PROJ_DEF_Z = GT(u'Debreate projects')
PROJ_DEF_L = GT(u'Legacy Debreate projects')
PROJ_DEF_A = GT(u'All supported formats')
PROJ_DEF_T = GT(u'Supported compressed archives')

project_wildcards = {
    ID_PROJ_Z: (PROJ_DEF_Z, (supported_suffixes[0],)),
    ID_PROJ_L: (PROJ_DEF_L, (supported_suffixes[1],)),
    ID_PROJ_A: (PROJ_DEF_A, supported_suffixes),
    ID_PROJ_T: (PROJ_DEF_T, supported_suffixes[2:])
}

# *** Python Info *** #

PY_VER_MAJ = sys.version_info[0]
PY_VER_MIN = sys.version_info[1]
PY_VER_REL = sys.version_info[2]
PY_VER_STRING = u'{}.{}.{}'.format(PY_VER_MAJ, PY_VER_MIN, PY_VER_REL)


# *** wxWidgets Info *** #

WX_VER_STRING = u'{}.{}.{}'.format(wx.MAJOR_VERSION, wx.MINOR_VERSION, wx.RELEASE_VERSION)


# *** Custom IDs *** #
ID_OVERWRITE = wx.NewId()
ID_APPEND = wx.NewId()
ID_HELP = wx.NewId()
ID_DEBUG = wx.NewId()
ID_LOG = wx.NewId()

# FIXME: Unused IDs
ID_BIN = wx.NewId()
ID_SRC = wx.NewId()
ID_DSC = wx.NewId()
ID_CNG = wx.NewId()

# Error IDs
ERR_DIR_NOT_AVAILABLE = wx.NewId()
ERR_FILE_READ = wx.NewId()
ERR_FILE_WRITE = wx.NewId()

error_definitions = {
    ERR_DIR_NOT_AVAILABLE: u'Directory Not Available',
    ERR_FILE_READ: u'Could Not Read File',
    ERR_FILE_WRITE: u'Could Not Write File',
}


# *** Icons *** #
ICON_ERROR = u'{}/bitmaps/error64.png'.format(PATH_app)
ICON_INFORMATION = u'{}/bitmaps/question64.png'.format(PATH_app)


# *** Colors depicting importance of fields
Mandatory = (255,200,192)
Recommended = (197,204,255)
Optional = (255,255,255)
Unused = (200,200,200)
Disabled = (246, 246, 245)


## Location of common licenses installed on the system
system_licenses_path = u'/usr/share/common-licenses'


# *** Default *** #
DEFAULT_SIZE = (800, 650)
DEFAULT_POS = (0, 0)


# *** Define some new error codes *** #
custom_errno = errno
current_code = errno.errorcode.keys()[-1]

custom_errno.SUCCESS = -1
custom_errno.errorcode[custom_errno.SUCCESS] = u'SUCCESS'

current_code += 1
custom_errno.EBADFT = current_code
custom_errno.errorcode[custom_errno.EBADFT] = u'EBADFT'

# *** File Types *** #
FTYPE_EXE = wx.NewId()

file_types_defs = {
    FTYPE_EXE: GT(u'script/executable'),
}


# *** Colors *** #
COLOR_ERROR = wx.Colour(255, 143, 115)


# *** Optional system executable commands *** #
cmd_tar = CommandExists(u'tar')
cmd_md5sum = CommandExists(u'md5sum')
cmd_lintian = CommandExists(u'lintian')
cmd_gzip = CommandExists(u'gzip')
