
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.output

import sys, wx

from input.text import TextAreaPanel


## A generic display area that captures \e stdout & \e stderr
class OutputLog(TextAreaPanel):
  def __init__(self, parent):
    TextAreaPanel.__init__(self, parent, style=wx.TE_READONLY)
    self.stdout = sys.stdout
    self.stderr = sys.stderr


  ## Adds test to the display area
  def write(self, string):
    self.AppendText(string)


  ## TODO: Doxygen
  def ToggleOutput(self, event=None):
    if sys.stdout == self:
      sys.stdout = self.stdout
      sys.stderr = self.stderr

    else:
      sys.stdout = self
      sys.stdout = self
