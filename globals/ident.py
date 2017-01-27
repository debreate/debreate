# -*- coding: utf-8 -*-

## \package globals.ident
#  
#  Miscellaneous IDs

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language import GT


## Creates a new bitwise compatible ID
#  
#  Along with return a new ID, it also updates the id_wrapper reference
#  
#  FIXME: Better method than using a list to pass reference?
#  \param id_wrapper
#    \b \e List instance to reference ID number so can be incremented
#  \return
#    New ID number
def AddId(id_wrapper):
    new_id = id_wrapper[0]
    id_wrapper[0] *= 2
    
    return new_id


# *** Button IDs *** #
PREV = wx.NewId()
NEXT = wx.NewId()

# *** Custom IDs *** #
CUSTOM = wx.NewId()
DEBUG = wx.NewId()
DIALOGS = wx.NewId()
DIST = wx.NewId()
EXPAND = wx.NewId()
LOG = wx.NewId()
MENU_TT = wx.NewId()
OVERWRITE = wx.NewId()
RENAME = wx.NewId()
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


## General IDs
class genid:
    APPEND = wx.NewId()
    BROWSE = wx.NewId()
    BUILD = wx.NewId()
    IMPORT = wx.NewId()


# Page IDs
next_page_id = 1000
page_ids = {}
def NewPageId(page_name=None):
    global next_page_id
    
    this_page_id = next_page_id
    next_page_id += 1
    
    page_ids[this_page_id] = page_name
    
    return this_page_id


## Page IDs
class pgid:
    GREETING = NewPageId(GT(u'Information'))
    CONTROL = NewPageId(GT(u'Control'))
    DEPENDS = NewPageId(GT(u'Depends'))
    FILES = NewPageId(GT(u'Files'))
    MAN = NewPageId(GT(u'Man'))
    SCRIPTS = NewPageId(GT(u'Scripts'))
    CHANGELOG = NewPageId(GT(u'Changelog'))
    COPYRIGHT = NewPageId(GT(u'Copyright'))
    MENU = NewPageId(GT(u'Menu'))
    BUILD = NewPageId(GT(u'Build'))


## IDs for input fields
class inputid:
    ARCH = wx.NewId()
    CUSTOM = wx.NewId()
    EMAIL = wx.NewId()
    LIST = wx.NewId()
    MAINTAINER = wx.NewId()
    MD5 = wx.NewId()
    NAME = wx.NewId()
    PACKAGE = wx.NewId()
    VERSION = wx.NewId()


## IDs for reference manual menu item links
class refid:
    DEBSRC = wx.NewId()
    DPM = wx.NewId()
    DPMCtrl = wx.NewId()
    DPMLog = wx.NewId()
    LAUNCHERS = wx.NewId()
    LINT_TAGS = wx.NewId()
    LINT_OVERRIDE = wx.NewId()
    MAN = wx.NewId()
    UPM = wx.NewId()
