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
    
    GREETING = NewPageId(GT(u'Greeting'), IdList)
    CONTROL = NewPageId(GT(u'Control'), IdList)
    DEPENDS = NewPageId(GT(u'Depends'), IdList)
    FILES = NewPageId(GT(u'Files'), IdList)
    MAN = NewPageId(GT(u'Man'), IdList)
    SCRIPTS = NewPageId(GT(u'Scripts'), IdList)
    CHANGELOG = NewPageId(GT(u'Changelog'), IdList)
    COPYRIGHT = NewPageId(GT(u'Copyright'), IdList)
    LAUNCHERS = NewPageId(GT(u'Menu'), IdList)
    BUILD = NewPageId(GT(u'Build'), IdList)


# *** Compression format IDs *** #
COMPRESSION = wx.NewId() # FIXME: Unused?
ZIP_NONE = wx.NewId()
ZIP_GZ = wx.NewId()
ZIP_BZ2 = wx.NewId()
ZIP_XZ = wx.NewId()
ZIP_ZIP = wx.NewId()


## IDs for text input fields
class InputId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.ARCH = self.NewId()
        self.CAT = self.NewId()
        self.CAT2 = self.NewId()
        self.CHECK = self.NewId()
        self.CUSTOM = self.NewId()
        self.DESCR = self.NewId()
        self.EMAIL = self.NewId()
        self.ENC = self.NewId()
        self.EXEC = self.NewId()
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
        self.TERM = self.NewId()
        self.TYPE = self.NewId()
        self.VALUE = self.NewId()
        self.VERSION = self.NewId()

inputid = InputId()


## IDs for button controls
class btnid:
    ADD = wx.ID_ADD
    CANCEL = wx.ID_CANCEL
    CONFIRM = wx.ID_YES|wx.ID_OK
    MODE = wx.NewId()
    RENAME = wx.NewId()


## IDs for check box fields
class ChkId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.ENABLE = self.NewId()
        self.FNAME = self.NewId()

chkid = ChkId()


## IDs for list fields
class ListId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.CAT = self.NewId()

listid = ListId()


## IDs referencing manual pages
class manid:
    # Starting ID number
    current_id = [1]
    
    CHOICE = AddId(current_id)
    EXPAND = AddId(current_id)
    REMOVABLE = AddId(current_id)
    STATIC = AddId(current_id)
    MULTILINE = AddId(current_id)
    MUTABLE = AddId(current_id)


## IDs for choice/selection fields
class SelId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.NOTIFY = self.NewId()
        self.TERM = self.NewId()

selid = SelId()


## IDs for static text fields
class TxtId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.FNAME = self.NewId()

txtid = TxtId()


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
