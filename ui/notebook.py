# -*- coding: utf-8 -*-

## \package ui.notebook

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.aui     import AUI_NB_CLOSE_ON_ACTIVE_TAB
from wx.aui     import AUI_NB_SCROLL_BUTTONS
from wx.aui     import AUI_NB_TAB_MOVE
from wx.aui     import AUI_NB_TAB_SPLIT
from wx.aui     import AUI_NB_TOP
from wx.aui     import AuiNotebook

from dbr.log    import Logger
from ui.panel   import ScrolledPanel


# ???: What is TAB_SPLIT for?
DEFAULT_NB_STYLE = AUI_NB_TOP|AUI_NB_TAB_SPLIT|AUI_NB_TAB_MOVE|AUI_NB_CLOSE_ON_ACTIVE_TAB|AUI_NB_SCROLL_BUTTONS


## Custom notebook class for compatibility with legacy wx versions
class Notebook(AuiNotebook):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=DEFAULT_NB_STYLE, name=u'notebook'):
        
        AuiNotebook.__init__(self, parent, win_id, pos, size, style)
        
        # wx.aui.AuiNotebook does not allow setting name from constructor
        self.Name = name
    
    
    ## Adds a new page
    #  
    #  \param caption
    #    Label displayed on tab
    #  \param page
    #    \b \e wx.Window instance that will be new page (if None, a new instance is created)
    #  \param select
    #    Specifies whether the page should be selected
    #  \param bitmap:
    #    Specifies optional image
    def AddPage(self, caption, page=None, win_id=wx.ID_ANY, select=False, imageId=0):
        if not page:
            page = wx.Panel(self, win_id)
        
        # Existing instance should already have an ID
        elif win_id != wx.ID_ANY:
            Logger.Warning(__name__, u'Option "win_id" is only used if "page" is None')
        
        if wx.MAJOR_VERSION <= 2:
            if not isinstance(imageId, wx.Bitmap):
                imageId = wx.NullBitmap
        
        AuiNotebook.AddPage(self, page, caption, select, imageId)
        
        return page
    
    
    ## Adds a ui.panel.ScrolledPanel instance as new page
    #  
    #  \param caption
    #    Label displayed on tab
    #  \param select
    #    Specifies whether the page should be selected
    #  \param bitmap:
    #    Specifies optional image
    def AddScrolledPage(self, caption, win_id=wx.ID_ANY, select=False, imageId=0):
        return self.AddPage(caption, ScrolledPanel(self), win_id, select, imageId)
    
    
    ## Deletes all pages
    #  
    #  \override wx.aui.AuiNotebook.DeleteAllPages
    def DeleteAllPages(self):
        if wx.MAJOR_VERSION > 2:
            return AuiNotebook.DeleteAllPages(self)
        
        # Reversing only used for deleting pages from right to left (not necessary)
        for INDEX in reversed(range(self.GetPageCount())):
            self.DeletePage(INDEX)
