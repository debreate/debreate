# -*- coding: utf-8 -*-

## \package ui.charctrl
#  
#  This script is used for field data that cannot use certain characters

# MIT licensing
# See: docs/LICENSE.txt


import wx

from globals.strings import TextIsEmpty


# List of characters that cannot be entered
# NOTE: 46 = ".", 47 = "/"
invalid_chars = (u'/', u'\\', u'_')


## A customized text area that disallows certain character input
#  
#  \implements wx.TextCtrl
class CharCtrl(wx.TextCtrl):
    def __init__(self, parent, ctrl_id=wx.ID_ANY, value=wx.EmptyString, name=wx.TextCtrlNameStr):
        wx.TextCtrl.__init__(self, parent, ctrl_id, value, name=name)
        
        wx.EVT_KEY_UP(self, self.OnKeyUp)
    
    
    ## Actions to take when key is released
    def OnKeyUp(self, event=None):
        insertion_point = self.GetInsertionPoint()
        text = self.GetValue()
        original_text = text
        
        # Remove whitespace
        for C in (u' ', u'\t'):
            if C in text:
                text = text.replace(C, u'-')
        
        if not TextIsEmpty(text):
            for C in invalid_chars:
                if C in text:
                    text = text.replace(C, u'-')
            
            if text != original_text:
                self.SetValue(text)
                self.SetInsertionPoint(insertion_point)
