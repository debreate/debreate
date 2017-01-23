# -*- coding: utf-8 -*-

## \package dbr.event
#  
#  Custom event types & binders

# MIT licensing
# See: docs/LICENSE.txt


from wx.lib.newevent import NewCommandEvent


ChangePageEvent = NewCommandEvent()
EVT_CHANGE_PAGE = ChangePageEvent[1]
ChangePageEvent = ChangePageEvent[0]
