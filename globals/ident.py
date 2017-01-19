# -*- coding: utf-8 -*-

## \package globals.ident
#  
#  Miscellaneous IDs

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language import GT


# *** Button IDs *** #
PREV = wx.NewId()
NEXT = wx.NewId()

# *** Custom IDs *** #
ALIEN = wx.NewId()
APPEND = wx.NewId()
BROWSE = wx.NewId()
CUSTOM = wx.NewId()
DEBUG = wx.NewId()
DIALOGS = wx.NewId()
DIST = wx.NewId()
EXPAND = wx.NewId()
IMPORT = wx.NewId()
LOG = wx.NewId()
MENU_TT = wx.NewId()
MULTI = wx.NewId()
OVERWRITE = wx.NewId()
RENAME = wx.NewId()
SINGLE = wx.NewId()
STAGE = wx.NewId()
TARGET = wx.NewId()
THEME = wx.NewId()

# *** Menu IDs *** #
ACTION = wx.NewId()
DIALOGS = wx.NewId()
LAUNCHERS = wx.NewId()
OPENLOGS = wx.NewId()
OPTIONS = wx.NewId()
PAGE = wx.NewId()
QBUILD = wx.NewId()
THEME = wx.NewId()
TOOLTIPS = wx.NewId()
UPDATE = wx.NewId()

# *** Reference menu IDs *** #
DPM = wx.NewId()
DPMCtrl = wx.NewId()
DPMLog = wx.NewId()
UPM = wx.NewId()
LINT_TAGS = wx.NewId()
LINT_OVERRIDE = wx.NewId()

# Page IDs
next_page_id = 1000
page_ids = {}
def NewPageId(page_name=None):
    global next_page_id
    
    this_page_id = next_page_id
    next_page_id += 1
    
    page_ids[this_page_id] = page_name
    
    return this_page_id

GREETING = NewPageId(GT(u'Greeting'))
CONTROL = NewPageId(GT(u'Control'))
DEPENDS = NewPageId(GT(u'Depends'))
FILES = NewPageId(GT(u'Files'))
MAN = NewPageId(GT(u'Man'))
SCRIPTS = NewPageId(GT(u'Scripts'))
CHANGELOG = NewPageId(GT(u'Changelog'))
COPYRIGHT = NewPageId(GT(u'Copyright'))
MENU = NewPageId(GT(u'Menu'))
BUILD = NewPageId(GT(u'Build'))

# *** Compression format IDs *** #
COMPRESSION = wx.NewId() # FIXME: Unused?
ZIP_NONE = wx.NewId()
ZIP_GZ = wx.NewId()
ZIP_BZ2 = wx.NewId()
ZIP_XZ = wx.NewId()
ZIP_ZIP = wx.NewId()

# Field/Control IDs
F_ARCH = wx.NewId()
F_CUSTOM = wx.NewId()
F_EMAIL = wx.NewId()
F_LIST = wx.NewId()
F_MAINTAINER = wx.NewId()
F_NAME = wx.NewId()
F_PACKAGE = wx.NewId()
F_VERSION = wx.NewId()
