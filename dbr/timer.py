
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.timer

import wx

from dbr.event import TimerStopEvent


## A custom timer that posts a TimerStopEvent when Stop() is called
class DebreateTimer(wx.Timer):
  def __init__(self, owner, ID=wx.ID_ANY):
    wx.Timer.__init__(self, owner, ID)

  def Stop(self, *args, **kwargs):
    return_value = wx.Timer.Stop(self, *args, **kwargs)
    wx.PostEvent(self.GetOwner(), TimerStopEvent(0))
    return return_value
