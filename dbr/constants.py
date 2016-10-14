# -*- coding: utf-8 -*-

## \package dbr.constants
#  
#  Global variables used throughout the application & should remain constant.


# System modules
import wx, os, sys, errno

# Local modules
from dbr.language import GT
from dbr.commandcheck import CommandExists


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

## Determins if the application is running as portable or installed
INSTALLED = False
if os.path.isfile(u'{}/INSTALLED'.format(application_path)):
    INSTALLED = True

def GetPrefix():
    global application_path, INSTALLED
    
    if not INSTALLED:
        return application_path
    
    FILE = open(u'{}/INSTALLED'.format(application_path))
    lines = FILE.read().split(u'\n')
    FILE.close()
    
    for L in lines:
        if u'=' in L:
            key = L.split(u'=')
            value = key[1]
            key = key[0]
            
            if key.lower() == u'prefix':
                return value
    
    return application_path


PREFIX = GetPrefix()

## Application's displayed name
APP_NAME = GT(u'Debreate')
AUTHOR = u'Jordan Irwin'
EMAIL = u'antumdeluge@gmail.com'
MAIN_ICON = wx.Icon(u'{}/bitmaps/debreate64.png'.format(application_path), wx.BITMAP_TYPE_PNG)

# Version information #
RELEASE = 0
VER_MAJ = 0
VER_MIN = 8
VER_REL = 0

VERSION = (VER_MAJ, VER_MIN, VER_REL)
VERSION_STRING = u'{}.{}.{}'.format(VER_MAJ, VER_MIN, VER_REL)

# Development version
if not RELEASE:
    VERSION_STRING = u'{}-dev'.format(VERSION_STRING)

# Website & hosting information #
HOMEPAGE = u'https://antumdeluge.github.io/debreate-web/'
PROJECT_HOME_GH = u'https://github.com/AntumDeluge/debreate'
PROJECT_HOME_SF = u'https://sourceforge.net/projects/debreate'

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

# Page IDs
next_page_id = 1000
page_ids = {}
def NewPageId(page_name=None):
    global next_page_id
    
    this_page_id = next_page_id
    next_page_id += 1
    
    page_ids[this_page_id] = page_name
    
    return this_page_id

ID_GREETING = NewPageId(GT(u'Greeting'))
ID_CONTROL = NewPageId(GT(u'Control'))
ID_DEPENDS = NewPageId(GT(u'Depends'))
ID_FILES = NewPageId(GT(u'Files'))
ID_MAN = NewPageId(GT(u'Man'))
ID_SCRIPTS = NewPageId(GT(u'Scripts'))
ID_CHANGELOG = NewPageId(GT(u'Changelog'))
ID_COPYRIGHT = NewPageId(GT(u'Copyright'))
ID_MENU = NewPageId(GT(u'Menu'))
ID_BUILD = NewPageId(GT(u'Build'))

# ID for custom fields
ID_CUSTOM = wx.NewId()

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
