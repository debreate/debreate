# -*- coding: utf-8 -*-

## \package ui.textpreview

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language   import GT
from ui.dialog      import BaseDialog
from ui.textinput   import MonospaceTextArea


## A simple dialog for previewing text
class TextPreview(BaseDialog):
    def __init__(self, parent=None, ID=wx.ID_ANY, title=GT(u'Preview'), text=wx.EmptyString,
                pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE,
                name=wx.DialogNameStr):
        BaseDialog.__init__(self, parent, ID, title, pos, size, style, name)
        
        # FIXME: Hide caret
        text_display = MonospaceTextArea(self, style=wx.TE_READONLY)
        
        if text:
            text_display.SetValue(text)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(text_display, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Retrieves the text area
    def GetTextArea(self):
        for C in self.GetChildren():
            if isinstance(C, MonospaceTextArea):
                return C
    
    
    ## Retrieves the displayed text
    def GetValue(self):
        text_display = self.GetTextArea()
        
        if text_display:
            return text_display.GetValue()
    
    
    ## Sets the displayed text
    def SetValue(self, text):
        text_display = self.GetTextArea()
        
        if text_display:
            return text_display.SetValue(text)
