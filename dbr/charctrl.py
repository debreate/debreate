# -*- coding: utf-8 -*-

# This script is used for field data that cannot use certain characters

## \package dbr.charctrl

import wx

## A customized text area that disallows certain character input
#  
#  \implements wx.TextCtrl
class CharCtrl(wx.TextCtrl):
    ## Constructor
    #  
    #  \param parent
    #        Parent window
    #  \param id
    #        Window id (FIXME: Not necessary)
    #  \param value
    #        The initial text displayed (default: empty)
    def __init__(self, parent, id=wx.ID_ANY, value=wx.EmptyString):
        wx.TextCtrl.__init__(self, parent, id, value)
        
        ## List of characters that cannot be entered
        #  
        #  NOTE: 46 = ".", 47 = "/"
        self.invalid_chars = (u' ', u'/', u'_')
        
        ## List of keys that should not be affected when using the spacebar
        #  
        #  ??? FIXME: 'spacebar' or 'shift' typo?
        self.shift_exceptions = (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN)
        
        ## List of keys that should not be affected when using the Ctrl key
        self.ctrl_exceptions = (u'A', u'A')
        
        wx.EVT_KEY_UP(self, self.OnKeyUp)
    
    ## Actions to take when key is released
    def OnKeyUp(self, event):
        modifier = event.GetModifiers()
        
        char = u''
        insert_index = self.GetInsertionPoint()
        if insert_index > 0:
            char = self.GetValue()[insert_index - 1]
        
        def ReplaceChar():
            value = self.GetValue()
            insertion = self.GetInsertionPoint()
            total_chars = len(value)
            while total_chars > 0:
                total_chars -= 1
                if value[total_chars] in self.invalid_chars:
                    self.Replace(total_chars, total_chars + 1, u'-')
            self.SetInsertionPoint(insertion)
            
        
        if modifier == wx.MOD_SHIFT and char in self.invalid_chars:
            ReplaceChar()
        elif char in self.invalid_chars:
            ReplaceChar()
        else:
            pass
        event.Skip()
