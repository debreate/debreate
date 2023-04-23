
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module input.toggle

import wx

from fields.cfgfield import ConfigField
from fields.cmdfield import CommandField
from input.essential import EssentialField
from ui.helper       import FieldEnabled


## Standard wx.CheckBox.
class CheckBox(wx.CheckBox, CommandField):
  def __init__(self, parent, win_id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
        size=wx.DefaultSize, style=0, name=wx.CheckBoxNameStr, defaultValue=False,
        commands=None, requireAll=False):

    wx.CheckBox.__init__(self, parent, win_id, label, pos, size, style, name=name)
    CommandField.__init__(self, commands, requireAll)

    self.Default = defaultValue
    self.tt_name = name

    # Initialize with default value
    self.SetValue(self.Default)

  ## @todo Doxygen
  def GetDefaultValue(self):
    return self.Default

  ## Retrieves current 'checked' state.
  #
  #  Differences from inherited method:
  #  - Always returns False if the object is disabled
  def GetValue(self):
    if not FieldEnabled(self):
      return False
    return wx.CheckBox.GetValue(self)

  ## Resets check box to default value.
  def Reset(self):
    self.SetChecked(self.GetDefaultValue())

  ## Manually emit EVT_CHECKBOX when setting value.
  #
  #  @param state
  #    If `True`, the check is on, otherwise it is off.
  def SetChecked(self, state=True):
    wx.PostEvent(self, wx.CommandEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED))
    return self.SetValue(state)

  ## @todo Doxygen
  def SetDefaultValue(self, value):
    self.Default = value

  ## Override inherited method to not allow changing value if disabled.
  #
  #  @todo parameters
  #  @todo return
  def SetValue(self, value):
    if FieldEnabled(self):
      return wx.CheckBox.SetValue(self, value)

## CheckBox that updates config file when value is changed.
#
#  @todo parameters
class CheckBoxCFG(CheckBox, ConfigField):
  def __init__(self, parent, win_id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
        size=wx.DefaultSize, style=0, name=wx.CheckBoxNameStr, defaultValue=False,
        commands=None, requireAll=False, cfgKey=None, cfgSect=None):

    CheckBox.__init__(self, parent, win_id, label, pos, size, style, name, defaultValue,
        commands, requireAll)
    ConfigField.__init__(self, cfgKey, cfgSect, defaultValue)


## CheckBox class that notifies main window to mark project dirty.
#
#  This is a dummy class to facilitate merging to & from unstable branch.
#
#  @todo parameters
class CheckBoxESS(CheckBox, EssentialField):
  def __init__(self, parent, win_id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
        size=wx.DefaultSize, style=0, name=wx.CheckBoxNameStr, defaultValue=False,
        commands=None, requireAll=False):

    CheckBox.__init__(self, parent, win_id, label, pos, size, style, name, defaultValue,
        commands, requireAll)
    EssentialField.__init__(self)
