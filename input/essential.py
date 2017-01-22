# -*- coding: utf-8 -*-

## \package input.essential

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.combo import OwnerDrawnComboBox

from globals.wizardhelper import GetTopWindow


## Abstract class that sends a message to main window to mark project dirty when field is changed
class EssentialField:
    def __init__(self):
        
        if isinstance(self, (wx.TextCtrl, wx.ComboBox, OwnerDrawnComboBox)):
            self.Bind(wx.EVT_TEXT, self.NotifyMainWindow)
        
        elif isinstance(self, wx.Choice):
            self.Bind(wx.EVT_CHOICE, self.NotifyMainWindow)
        
        elif isinstance(self, wx.CheckBox):
            self.Bind(wx.EVT_CHECKBOX, self.NotifyMainWindow)
    
    
    def NotifyMainWindow(self, event=None):
        if event:
            event.Skip(True)
        
        GetTopWindow().ProjectChanged(event)
