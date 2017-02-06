# -*- coding: utf-8 -*-

## \package ui.textpreview

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language   import GT
from input.text     import TextAreaPanel
from ui.dialog      import BaseDialog
from ui.layout      import BoxSizer
from ui.style       import layout as lyt


## A simple dialog for previewing text
class TextPreview(BaseDialog):
    def __init__(self, parent=None, ID=wx.ID_ANY, title=GT(u'Preview'), text=wx.EmptyString,
            pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE,
            name=wx.DialogNameStr, monospace=True, readonly=True):
        
        BaseDialog.__init__(self, parent, ID, title, pos, size, style, name)
        
        ti_style = 0
        if readonly:
            ti_style = wx.TE_READONLY
        
        # FIXME: Hide caret
        text_display = TextAreaPanel(self, monospace=monospace, style=ti_style)
        
        if text:
            text_display.SetValue(text)
        
        # *** Event Handling *** #
        
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(text_display, 1, wx.EXPAND|lyt.PAD_LR|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Retrieves the text area
    def GetTextArea(self):
        for C in self.GetChildren():
            if isinstance(C, TextAreaPanel):
                return C
    
    
    ## Retrieves the displayed text
    def GetValue(self):
        text_display = self.GetTextArea()
        
        if text_display:
            return text_display.GetValue()
    
    
    ## Close dialog with button events
    def OnButton(self, event=None):
        if event:
            self.EndModal(event.GetEventObject().GetId())
    
    
    ## Sets the displayed text
    def SetValue(self, text):
        text_display = self.GetTextArea()
        
        if text_display:
            return text_display.SetValue(text)
