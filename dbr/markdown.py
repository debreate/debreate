# -*- coding: utf-8 -*-

## \package dbr.markdown

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.richtext import RE_MULTILINE
from wx.richtext import RichTextCtrl

from ui.button   import ButtonConfirm


## Class to parse & display Markdown text
class MarkdownCtrl(RichTextCtrl):
    def __init__(self, parent, rt_id=wx.ID_ANY):
        RichTextCtrl.__init__(self, parent, rt_id, style=RE_MULTILINE)
        
    
    def LoadFile(self, *args, **kwargs):
        return RichTextCtrl.LoadFile(self, *args, **kwargs)



## Class that displays a dialog with a MarkdownCtrl
class MarkdownDialog(wx.Dialog):
    def __init__(self, parent, title=wx.EmptyString, style=wx.DEFAULT_DIALOG_STYLE|wx.OK):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=title, style=style)
        
        self.markdown = MarkdownCtrl(self)
        self.loaded_file = None
        
        layout_V1 = wx.BoxSizer(wx.VERTICAL)
        layout_V1.Add(self.markdown, 1, wx.ALL|wx.EXPAND, 5)
        
        if style & wx.OK:
            self.btn_confirm = ButtonConfirm(self)
            layout_V1.Add(self.btn_confirm, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_V1)
        self.Layout()
    
    
    def GetFile(self):
        return self.loaded_file
    
    
    def GetText(self):
        return self.markdown.GetValue()
    
    
    def LoadFile(self, md_file):
        self.markdown.LoadFile(md_file)
        self.loaded_file = md_file
    
    
    def SetText(self, md_text):
        self.markdown.SetValue(md_text)
