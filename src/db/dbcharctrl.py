# This script is used for field data that cannot use certain characters

from common import setWXVersion
setWXVersion()

import wx

class CharCtrl(wx.TextCtrl):
    def __init__(self, parent, id=wx.ID_ANY, value=wx.EmptyString):
        wx.TextCtrl.__init__(self, parent, id, value)
        
        # List of characters that connot be used in the field
        # 46 = ".", 47 = "/"
        self.invalid_chars = (" ", "/", "_")
        
        # A list of keys that should not be affected when using the spacebar
        self.shift_exceptions = (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN)
        
        # A list of keys that should not be affected when using the Ctrl key
        self.ctrl_exceptions = ("A", "A")
        
        wx.EVT_KEY_UP(self, self.OnKeyUp)
    
    def OnKeyUp(self, event):
        modifier = event.GetModifiers()
        keycode = event.GetKeyCode()
        char = self.GetValue()[self.GetInsertionPoint()-1]
        
        def ReplaceChar():
            value = self.GetValue()
            insertion = self.GetInsertionPoint()
            total_chars = len(value)
            while total_chars > 0:
                total_chars -= 1
                if value[total_chars] in self.invalid_chars:
                    self.Replace(total_chars, total_chars+1, "-")
            self.SetInsertionPoint(insertion)
            
        
        if modifier == wx.MOD_SHIFT and char in self.invalid_chars:
            ReplaceChar()
        elif char in self.invalid_chars:
            ReplaceChar()
        else:
            pass
        event.Skip()