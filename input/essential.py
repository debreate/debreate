
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module input.essential

import wx

from wx.adv import OwnerDrawnComboBox

import ui.app

from startup    import startup
from ui.helper  import FieldEnabled
from ui.panel   import ControlPanel


## This is a dummy class to facilitate merging to & from unstable branch.
class EssentialField:
  def __init__(self):
    pass


## Abstract class that sends a message to main window to mark project dirty when field is changed.
class EssentialFieldUnused:
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

  ## @todo Doxygen
  def NotifyMainWindow(self, event=None):
    if event:
      event.Skip(True)
    if startup.initialized and FieldEnabled(self):
      ui.app.getMainWindow().OnProjectChanged(event)
