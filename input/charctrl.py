
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Field data that cannot use certain characters.
#
#  @module input.charctrl

import wx

from libdbr import strings


# List of characters that cannot be entered
# NOTE: 46 = ".", 47 = "/"
invalid_chars = ("/", "\\", "_")


## A customized text area that disallows certain character input.
#
#  @implements wx.TextCtrl
class CharCtrl(wx.TextCtrl):
  def __init__(self, parent, ctrl_id=wx.ID_ANY, value=wx.EmptyString, name=wx.TextCtrlNameStr):
    wx.TextCtrl.__init__(self, parent, ctrl_id, value, name=name)

    wx.EVT_KEY_UP(self, self.OnKeyUp)

  ## Actions to take when key is released.
  def OnKeyUp(self, event=None):
    insertion_point = self.GetInsertionPoint()
    text = self.GetValue()
    original_text = text

    # Remove whitespace
    for C in (" ", "\t"):
      if C in text:
        text = text.replace(C, "-")

    if not strings.isEmpty(text):
      for C in invalid_chars:
        if C in text:
          text = text.replace(C, "-")

      if text != original_text:
        self.SetValue(text)
        self.SetInsertionPoint(insertion_point)
