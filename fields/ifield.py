
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Input fields
#
#  @module fields.ifield

import wx

from globals.strings import IsString
from ui.helper       import FieldEnabled


## An input field that sets a default value.
class InputField:
  def __init__(self, defaultValue, required=False, outLabel=None):
    self.Default = defaultValue
    self.Required = required
    self.OutputLabel = outLabel

    # initialize with default value
    self.Reset()

  ## Retrieves the field's default value.
  def GetDefaultValue(self):
    return self.Default

  ## Retrieves label for text output.
  def GetOutputLabel(self):
    return self.OutputLabel

  ## @todo Doxygen
  def HasOutputLabel(self):
    return IsString(self.OutputLabel) and self.OutputLabel != wx.EmptyString

  ## Checks if field is required for building.
  #
  #  @return
  #    `True` if the field is enabled & 'Required' attribute set to `True`.
  def IsRequired(self):
    if FieldEnabled(self) and self.Required:
      return True
    return False

  ## Resets field to default value.
  def Reset(self):
    if isinstance(self, wx.Choice):
      if self.GetCount():
        if IsString(self.Default):
          self.SetStringSelection(self.Default)
          return self.StringSelection == self.Default

        else:
          self.SetSelection(self.Default)
          return self.Selection == self.Default

    elif isinstance(self, wx.ListCtrl):
      #  FIXME: What to do if default value is not 'None'
      if self.Default == None:
        return self.DeleteAllItems()
    else:
      self.SetValue(self.Default)

  ## Sets the field's default value.
  def SetDefaultValue(self, value):
    self.Default = value

  ## Re-define in inheriting classes.
  def SetValue(self, value):
    pass
