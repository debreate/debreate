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
APPEND = wx.NewId()
BROWSE = wx.NewId()
CUSTOM = wx.NewId()
DEBUG = wx.NewId()
DIALOGS = wx.NewId()
IMPORT = wx.NewId()
LOG = wx.NewId()
MENU_TT = wx.NewId()
OVERWRITE = wx.NewId()
STAGE = wx.NewId()
TARGET = wx.NewId()
THEME = wx.NewId()

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

# Field/Control IDs
F_ARCH = wx.NewId()
F_CUSTOM = wx.NewId()
F_EMAIL = wx.NewId()
F_LIST = wx.NewId()
F_MAINTAINER = wx.NewId()
F_NAME = wx.NewId()
F_PACKAGE = wx.NewId()
F_VERSION = wx.NewId()
