# -*- coding: utf-8 -*-

## \package dbr.event
#  
#  Custom event types & binders

# MIT licensing
# See: docs/LICENSE.txt


from wx.lib.newevent import NewCommandEvent


## Event to post when ui.wizard.Wizard.ShowPage is called
ChangePageEvent = NewCommandEvent()
EVT_CHANGE_PAGE = ChangePageEvent[1]
ChangePageEvent = ChangePageEvent[0]

## Event to post when dbr.timer.DebreateTimer.Stop() is called
TimerStopEvent = NewCommandEvent()
EVT_TIMER_STOP = TimerStopEvent[1]
TimerStopEvent = TimerStopEvent[0]
