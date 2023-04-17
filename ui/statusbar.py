
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.statusbar

import wx

from libdbr.logger import Logger


## A status bar for compatibility between wx 3.0 & older versions.
#
#  @deprecated
class StatusBar(wx.StatusBar):
  if wx.MAJOR_VERSION > 2:
    sb_style = wx.STB_DEFAULT_STYLE
  else:
    sb_style = wx.STB_SIZEGRIP

  def __init__(self, parent, ID=wx.ID_ANY, style=sb_style,
        name="Status"):
    wx.StatusBar.__init__(self, parent, ID, style, name)
    Logger(__name__).deprecated(StatusBar)

    parent.SetStatusBar(self)
