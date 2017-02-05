# -*- coding: utf-8 -*-

## \package input.essential

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.combo import OwnerDrawnComboBox

from startup.startup    import AppInitialized
from ui.panel           import ControlPanel
from wiz.helper         import FieldEnabled
from wiz.helper         import GetMainWindow


## Abstract class that sends a message to main window to mark project dirty when field is changed
class EssentialField:
    def __init__(self):
        if isinstance(self, ControlPanel):
            main_control = self.GetMainControl()
        
        else:
            main_control = self
        
        if isinstance(main_control, (wx.TextCtrl, wx.ComboBox, OwnerDrawnComboBox)):
            main_control.Bind(wx.EVT_TEXT, self.NotifyMainWindow)
        
        elif isinstance(main_control, wx.Choice):
            main_control.Bind(wx.EVT_CHOICE, self.NotifyMainWindow)
        
        elif isinstance(main_control, wx.CheckBox):
            main_control.Bind(wx.EVT_CHECKBOX, self.NotifyMainWindow)
        
        elif isinstance(main_control, wx.ListCtrl):
            main_control.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, self.NotifyMainWindow)
            main_control.Bind(wx.EVT_LIST_DELETE_ITEM, self.NotifyMainWindow)
            main_control.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.NotifyMainWindow)
            main_control.Bind(wx.EVT_LIST_INSERT_ITEM, self.NotifyMainWindow)
    
    
    ## TODO: Doxygen
    def NotifyMainWindow(self, event=None):
        if event:
            event.Skip(True)
        
        if AppInitialized() and FieldEnabled(self):
            GetMainWindow().OnProjectChanged(event)
