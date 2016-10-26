# -*- coding: utf-8 -*-

## \package globals.ident
#  
#  Miscellaneous IDs

# MIT licensing
# See: docs/LICENSE.txt


# System modules
import wx

from dbr.language import GT


# *** Custom IDs *** #
ID_OVERWRITE = wx.NewId()
ID_APPEND = wx.NewId()
ID_DEBUG = wx.NewId()
ID_LOG = wx.NewId()
ID_STAGE = wx.NewId()
ID_TARGET = wx.NewId()
ID_THEME = wx.NewId()
ID_IMPORT = wx.NewId()

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

# *** Button IDs *** #
ID_PREV = wx.NewId()
ID_NEXT = wx.NewId()
