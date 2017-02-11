# -*- coding: utf-8 -*-

## \package globals.ident
#  
#  Miscellaneous IDs

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language   import GT
from dbr.log        import Logger


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


# *** Custom IDs *** #
DIST = wx.NewId()
EXPAND = wx.NewId()
RENAME = wx.NewId()
SINGLE = wx.NewId()


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
    #
    #  \param staticId
    #    <b><i>integer</i></b>:
    #      Predefined ID to set
    def AddStaticId(self, staticId):
        self.IdList.append(staticId)
        
        return staticId
    
    
    ## Add a new ID
    def NewId(self):
        return NewId(self.IdList)


## Page IDs
class PageId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.Labels = {}
        
        self.GREETING = self.NewId(GT(u'Greeting'))
        self.CONTROL = self.NewId(GT(u'Control'))
        self.DEPENDS = self.NewId(GT(u'Depends'))
        self.FILES = self.NewId(GT(u'Files'))
        self.MAN = self.NewId(GT(u'Man'))
        self.SCRIPTS = self.NewId(GT(u'Scripts'))
        self.CHANGELOG = self.NewId(GT(u'Changelog'))
        self.COPYRIGHT = self.NewId(GT(u'Copyright'))
        self.LAUNCHERS = self.NewId(GT(u'Menu'))
        self.BUILD = self.NewId(GT(u'Build'))
    
    
    ## Adds a predetermined ID to ID list & text label to label list
    #
    #  \param staticId
    #    <b><i>integer</i></b>:
    #      Predefined ID to set
    #  \param label
    #    <b><i>string</i></b>
    #      Page label/title
    def AddStaticId(self, staticId, label):
        new_id = FieldId.AddStaticId(self, staticId)
        
        self.Labels[new_id] = label
        
        return new_id
    
    
    ## Add a new ID & text label to label list
    #
    #  param label
    #    <b><i>string</i></b>:
    #      Page label/title
    def NewId(self, label):
        #new_id = FieldId.NewId(self)
        new_id = NewPageId(label, self.IdList)
        
        self.Labels[new_id] = label
        
        return new_id

pgid = PageId()


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
        self.CHANGES = self.NewId()
        self.CHECK = self.NewId()
        self.CUSTOM = self.NewId()
        self.DESCR = self.NewId()
        self.DIST = self.NewId()
        self.EMAIL = self.NewId()
        self.ENC = self.NewId()
        self.EXEC = self.NewId()
        self.ICON = self.NewId()
        self.KEY = self.NewId()
        self.LIST = self.NewId()
        self.MAINTAINER = self.NewId()
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
class ButtonId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        ## Image labels associated with button IDs
        self.Images = {}
        
        self.ADD = self.AddStaticId(wx.ID_ADD, u'add')
        self.APPEND = self.NewId(u'append')
        self.BIN = self.NewId()
        self.BROWSE = self.NewId(u'browse')
        self.BUILD = self.NewId(u'build')
        self.CANCEL = self.AddStaticId(wx.ID_CANCEL, u'cancel')
        self.CLEAR = self.AddStaticId(wx.ID_CLEAR, u'clear')
        self.CLOSE = self.AddStaticId(wx.ID_CLOSE)
        self.CONFIRM = self.AddStaticId(wx.ID_OK, u'confirm')
        self.EXIT = self.AddStaticId(wx.ID_EXIT, u'exit')
        self.FULL = self.NewId(u'full')
        self.HELP = self.AddStaticId(wx.ID_HELP, u'help')
        self.HIDE = self.NewId(u'hide')
        self.IMPORT = self.NewId(u'import')
        self.MODE = self.NewId(u'mode')
        self.NEXT = self.NewId(u'next')
        self.PREV = self.NewId(u'prev')
        self.PREVIEW = self.AddStaticId(wx.ID_PREVIEW, u'preview')
        self.REFRESH = self.AddStaticId(wx.ID_REFRESH, u'refresh')
        self.REMOVE = self.AddStaticId(wx.ID_REMOVE, u'remove')
        self.RENAME = self.NewId(u'rename')
        self.SAVE = self.AddStaticId(wx.ID_SAVE, u'save')
        self.SHORT = self.NewId(u'short')
        self.SRC = self.NewId()
        self.STAGE = self.NewId()
        self.TARGET = self.NewId()
        self.ZOOM = self.AddStaticId(wx.ID_PREVIEW_ZOOM, u'zoom')
    
    
    ## Adds a predetermined ID to ID list & optional bitmap image reference
    #
    #  \param staticId
    #    <b><i>integer</i></b>:
    #      Predefined ID to set
    #  \param imageName
    #    <b><i>string</i></b>:
    #      Image file basename
    def AddStaticId(self, staticId, imageName=None):
        self.Images[staticId] = imageName
        
        return FieldId.AddStaticId(self, staticId)
    
    
    ## Retrieves the image linked to the ID
    #
    #  \param btnId
    #    Requested button ID
    #  \return
    #    <b><i>string</i></b>:
    #      Image label associated with button ID (<b><i>None</i></b> if ID has no image)
    def GetImage(self, btnId):
        if btnId in self.Images:
            return self.Images[btnId]
        
        Logger.Warn(__name__, u'ButtonId.GetImage: Requested button ID {} with no associated image'.format(btnId))
    
    
    ## Adds a new ID & optional bitmap image reference
    #
    #  \param imageName
    #    <b><i>string</i></b>:
    #      Image file basename
    def NewId(self, imageName=None):
        new_id = FieldId.NewId(self)
        
        self.Images[new_id] = imageName
        
        return new_id

btnid = ButtonId()


## IDs for check box fields
class ChkId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.CAT = self.NewId()
        self.DELETE = self.AddStaticId(wx.ID_DELETE)
        self.EDIT = self.AddStaticId(wx.ID_EDIT)
        self.ENABLE = self.NewId()
        self.FNAME = self.NewId()
        self.INSTALL = self.NewId()
        self.LINT = self.NewId()
        self.MD5 = self.NewId()
        self.NOTIFY = self.NewId()
        self.REMOVE = self.NewId()
        self.STRIP = self.NewId()
        self.TARGET = self.NewId()
        self.TERM = self.NewId()

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


## IDs for menus
class MenuId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.ABOUT = self.AddStaticId(wx.ID_ABOUT)
        self.ACTION = self.NewId()
        self.ALIEN = self.NewId()
        self.COMPRESS = self.NewId()
        self.DEBUG = self.NewId()
        self.DIST = self.NewId()
        self.EXIT = btnid.EXIT
        self.FILE = self.AddStaticId(wx.ID_FILE)
        self.HELP = btnid.HELP
        self.LOG = self.NewId()
        self.NEW = self.AddStaticId(wx.ID_NEW)
        self.OPEN = self.AddStaticId(wx.ID_OPEN)
        self.OPENLOGS = self.NewId()
        self.OPTIONS = self.NewId()
        self.PAGE = self.NewId()
        self.QBUILD = self.NewId()
        self.SAVE = btnid.SAVE
        self.SAVEAS = self.AddStaticId(wx.ID_SAVEAS)
        self.THEME = self.NewId()
        self.TOOLTIPS = self.NewId()
        self.UPDATE = self.NewId()

menuid = MenuId()


## IDs for choice/selection fields
class SelId(FieldId):
    def __init__(self):
        FieldId.__init__(self)
        
        self.LICENSE = self.NewId()
        self.URGENCY = self.NewId()

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
