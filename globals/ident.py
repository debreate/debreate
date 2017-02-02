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


## Creates a ID & adds to a member list
#
#  \param member_list
#    \b \e List instance to add ID to
def NewId(member_list=None):
    new_id = wx.NewId()
    
    if isinstance(member_list, list):
        member_list.append(new_id)
    
    return new_id


# *** Button IDs *** #
PREV = wx.NewId()
NEXT = wx.NewId()

# *** Custom IDs *** #
ALIEN = wx.NewId()
CUSTOM = wx.NewId()
DEBUG = wx.NewId()
DIALOGS = wx.NewId()
DIST = wx.NewId()
EXPAND = wx.NewId()
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
    BGPANEL = wx.NewId()
    BROWSE = wx.NewId()
    BUILD = wx.NewId()
    IMPORT = wx.NewId()


# Page IDs
next_page_id = 1000
page_ids = {}

## Creates a new page ID & adds to a member list instance for iteration
def NewPageId(page_name=None, member_list=None):
    global next_page_id
    
    this_page_id = next_page_id
    next_page_id += 1
    
    page_ids[this_page_id] = page_name
    
    if isinstance(member_list, list):
        # Add to member list for iterating
        member_list.append(this_page_id)
    
    return this_page_id


## Abstract ID class
class FieldId:
    def __init__(self):
        self.IdList = []
    
    
    ## Adds a predetermined ID to ID list
    def AddStaticId(self, static_id):
        self.IdList.append(static_id)
        
        return static_id
    
    
    ## Add a new ID
    def NewId(self):
        return NewId(self.IdList)


## Page IDs
class pgid:
    IdList = []
    
    GREETING = NewPageId(GT(u'Information'), IdList)
    CONTROL = NewPageId(GT(u'Control'), IdList)
    DEPENDS = NewPageId(GT(u'Depends'), IdList)
    FILES = NewPageId(GT(u'Files'), IdList)
    MAN = NewPageId(GT(u'Man'), IdList)
    SCRIPTS = NewPageId(GT(u'Scripts'), IdList)
    CHANGELOG = NewPageId(GT(u'Changelog'), IdList)
    COPYRIGHT = NewPageId(GT(u'Copyright'), IdList)
    MENU = NewPageId(GT(u'Menu'), IdList)
    BUILD = NewPageId(GT(u'Build'), IdList)


## IDs for text input fields
class InputId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.ARCH = self.NewId()
        self.CAT = self.NewId()
        self.CAT2 = self.NewId()
        self.CHANGES = self.NewId()
        self.CHECK = self.NewId()
        self.CUSTOM = self.NewId()
        self.DESCR = self.NewId()
        self.DIST = self.NewId()
        self.EMAIL = self.NewId()
        self.ENC = self.NewId()
        self.EXEC = self.NewId()
        self.FNAME = self.NewId()
        self.ICON = self.NewId()
        self.KEY = self.NewId()
        self.LIST = self.NewId()
        self.MAINTAINER = self.NewId()
        self.MD5 = self.NewId()
        self.MIME = self.NewId()
        self.NAME = self.NewId()
        self.NOTIFY = self.NewId()
        self.OTHER = self.NewId()
        self.PACKAGE = self.NewId()
        self.TARGET = self.NewId()
        self.TERM = self.NewId()
        self.TYPE = self.NewId()
        self.VALUE = self.NewId()
        self.VERSION = self.NewId()

inputid = InputId()


## IDs for button fields
class BtnId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.ADD = self.AddStaticId(wx.ID_ADD)
        self.BROWSE = self.NewId()
        self.CANCEL = self.AddStaticId(wx.ID_CANCEL)
        self.CLEAR = self.AddStaticId(wx.ID_CLEAR)
        self.CONFIRM = self.AddStaticId(wx.ID_YES|wx.ID_OK)
        self.MODE = self.NewId()
        self.PREVIEW = self.AddStaticId(wx.ID_PREVIEW)
        self.REMOVE = self.AddStaticId(wx.ID_REMOVE)
        self.RENAME = self.NewId()
        self.SAVE = self.AddStaticId(wx.ID_SAVE)

btnid = BtnId()


## IDs for check box fields
class ChkId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.CAT = self.NewId()
        self.ENABLE = self.NewId()
        self.FNAME = self.NewId()
        self.NOTIFY = self.NewId()
        self.TERM = self.NewId()

chkid = ChkId()


## IDs for list fields
class ListId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.CAT = self.NewId()

listid = ListId()


## IDs for choice/selection fields
class SelId(FieldId):
    def __init__(self):
        FieldId.__init__(self)

selid = SelId()


## IDs for static text fields
class TxtId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.FNAME = self.NewId()

txtid = TxtId()


## IDs for reference manual menu item links
class RefId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.DEBSRC = self.NewId()
        self.DPM = self.NewId()
        self.DPMCtrl = self.NewId()
        self.DPMLog = self.NewId()
        self.LAUNCHERS = self.NewId()
        self.LINT_TAGS = self.NewId()
        self.LINT_OVERRIDE = self.NewId()
        self.MAN = self.NewId()
        self.UPM = self.NewId()

refid = RefId()
