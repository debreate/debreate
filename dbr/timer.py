# -*- coding: utf-8 -*-

## \package dbr.timer

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.lib.newevent import NewCommandEvent


## Event to post when Timer.Stop() is called
TimerStopEvent, EVT_TIMER_STOP = NewCommandEvent()


## A custom timer that posts a TimerStopEvent when Stop() is called
class DebreateTimer(wx.Timer):
    def __init__(self, owner, ID=wx.ID_ANY):
        wx.Timer.__init__(self, owner, ID)
    
    def Stop(self, *args, **kwargs):
        return_value = wx.Timer.Stop(self, *args, **kwargs)
        
        wx.PostEvent(self.GetOwner(), TimerStopEvent(0))
        
        return return_value
