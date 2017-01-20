# -*- coding: utf-8 -*-

## \package dbr.message

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language   import GT
from ui.button      import ButtonConfirm
from ui.textinput   import TextAreaPanel


## TODO: Doxygen
class MessageDialog(wx.Dialog):
    def __init__(self, parent, ID=wx.ID_ANY, title=GT(u'Message'), icon=wx.NullBitmap, text=wx.EmptyString,
            details=wx.EmptyString):
        wx.Dialog.__init__(self, parent, ID, title, size=(500,500))
        
        self.icon = wx.StaticBitmap(self, -1, wx.Bitmap(icon))
        
        self.text = wx.StaticText(self, label=text)
        self.button_details = wx.ToggleButton(self, -1, u'Details')
        self.details = TextAreaPanel(self, value=details, size=(300,150), style=wx.TE_READONLY)
        self.details.SetSize(self.details.GetBestSize())
        
        wx.EVT_TOGGLEBUTTON(self.button_details, -1, self.ToggleDetails)
        
        self.button_ok = ButtonConfirm(self)
        
        r_sizer = wx.BoxSizer(wx.VERTICAL)
        r_sizer.AddSpacer(10)
        r_sizer.Add(self.text)
        r_sizer.AddSpacer(20)
        r_sizer.Add(self.button_details)
        r_sizer.Add(self.details, 1, wx.EXPAND)
        r_sizer.Add(self.button_ok, 0, wx.ALIGN_RIGHT)
        
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.icon, 0, wx.ALL, 20)
        self.main_sizer.Add(r_sizer, 1, wx.EXPAND)
        self.main_sizer.AddSpacer(10)
        
        self.SetAutoLayout(True)
        self.ToggleDetails(None)
        
        self.details.Hide()
    
    
    ## TODO: Doxygen
    def ToggleDetails(self, event=None):
        if self.button_details.GetValue():
            self.details.Show()
        
        else:
            self.details.Hide()
        self.SetSizerAndFit(self.main_sizer)
        self.Layout()
