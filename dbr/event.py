
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.event
#
#  Custom event types & binders

from wx.lib.newevent import NewCommandEvent


## Event to post when ui.wizard.Wizard.ShowPage is called
ChangePageEvent = NewCommandEvent()
EVT_CHANGE_PAGE = ChangePageEvent[1]
ChangePageEvent = ChangePageEvent[0]

## Event to post when dbr.timer.DebreateTimer.Stop is called
TimerStopEvent = NewCommandEvent()
EVT_TIMER_STOP = TimerStopEvent[1]
TimerStopEvent = TimerStopEvent[0]

## Event to post when ui.logwindow.LogWindow.PollLogFile is called
RefreshLogEvent = NewCommandEvent()
EVT_REFRESH_LOG = RefreshLogEvent[1]
RefreshLogEvent = RefreshLogEvent[0]
