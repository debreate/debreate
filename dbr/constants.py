# -*- coding: utf-8 -*-

## \package dbr.constants
#  
#  Global variables used throughout the application & should remain constant.


# System modules
import wx, os, sys

# Local modules
from dbr.language import GT
from globals.paths import PATH_app


# *** System Information *** #


# *** Debreate Information *** #

## Determins if the application is running as portable or installed
INSTALLED = False
if os.path.isfile(u'{}/INSTALLED'.format(PATH_app)):
    INSTALLED = True

def GetPrefix():
    global PATH_app, INSTALLED
    
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
ID_THEME = wx.NewId()

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

# *** FIXME: Deprecated??? Colors depicting importance of fields
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


# *** File Types *** #
FTYPE_EXE = wx.NewId()

file_types_defs = {
    FTYPE_EXE: GT(u'script/executable'),
}


# *** Colors *** #
COLOR_ERROR = wx.Colour(255, 143, 115)
