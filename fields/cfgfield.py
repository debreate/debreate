
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module fields.cfgfield
#
#  Fields that affect settings

import wx

from dbr.config    import ConfCode
from dbr.config    import SetDefaultConfigKey
from libdbr        import config
from libdbr.logger import Logger


logger = Logger(__name__)

## Class that updates the configuration file when a specific event occurs.
class ConfigField:
  def __init__(self, cfgKey=None, cfgSect=None, defaultValue=False):
    self.ConfigKey = cfgKey or self.GetName()
    self.ConfigSection = cfgSect

    # Add to recognized configuration keys
    SetDefaultConfigKey(self.ConfigKey, self.GetDefaultValue())

    # Set state using config file if found
    state = config.get("user").getBool(self.ConfigKey, default=defaultValue, section=cfgSect)

    ret_codes = (
      ConfCode.FILE_NOT_FOUND,
      ConfCode.KEY_NOT_DEFINED,
      ConfCode.KEY_NO_EXIST,
      )

    if state not in (ret_codes):
      self.SetValue(state)

    else:
      logger.debug("Key not found: {}".format(self.ConfigKey))

    # *** Event Handling *** #

    if isinstance(self, wx.CheckBox):
      self.Bind(wx.EVT_CHECKBOX, self.OnToggle)

  ## Re-define in inheriting classes.
  def GetDefaultValue(self):
    return ""

  ## Re-define in inheriting classes.
  def GetName(self):
    return ""

  ## Re-define in inheriting classes.
  def SetValue(self, value):
    pass

  ## @todo Doxygen
  def GetConfigKey(self):
    return self.ConfigKey

  ## @todo Doxygen
  def GetConfigSection(self):
    return self.ConfigSection

  ## @todo Doxygen
  def GetConfigValue(self):
    GETVAL = 1
    CHOICE = 2

    ftypes = {
      GETVAL: (wx.TextCtrl, wx.CheckBox,),
      CHOICE: wx.Choice,
      }

    if isinstance(self, ftypes[GETVAL]):
      return self.GetValue()

    if isinstance(self, ftypes[CHOICE]):
      return self.GetStringSelection()

  ## @todo Doxygen
  def OnToggle(self, event=None):
    if event:
      event.Skip()
    cfg_user = config.get("user")
    cfg_user.setValue(self.ConfigKey, self.GetConfigValue(), section=self.GetConfigSection())
    cfg_user.save()

  ## @todo Doxygen
  def SetConfigKey(self, cfgKey):
    self.ConfigKey = cfgKey

  ## @todo Doxygen
  def SetConfigSection(self, cfgSect):
    self.ConfigSection = cfgSect
