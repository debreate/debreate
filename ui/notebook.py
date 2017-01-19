# -*- coding: utf-8 -*-

## \package ui.notebook

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.aui import AuiNotebook
from wx.aui import AUI_NB_CLOSE_BUTTON
from wx.aui import AUI_NB_TAB_MOVE
from wx.aui import AUI_NB_TAB_SPLIT


## Custom notebook class for compatibility with legacy wx versions
class Notebook(AuiNotebook):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=AUI_NB_TAB_SPLIT|AUI_NB_TAB_MOVE|AUI_NB_CLOSE_BUTTON, name=u'notebook'):
        AuiNotebook.__init__(self, parent, win_id, pos, size, style)
        
        # wx.aui.AuiNotebook does not allow setting name from constructor
        self.Name = name
    
    
    ## Deletes all pages
    #  
    #  \override wx.aui.AuiNotebook.DeleteAllPages
    def DeleteAllPages(self):
        if wx.MAJOR_VERSION > 2:
            return AuiNotebook.DeleteAllPages(self)
        
        # Reversing only used for deleting pages from right to left (not necessary)
        for INDEX in reversed(range(self.GetPageCount())):
            self.DeletePage(INDEX)
