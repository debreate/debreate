# -*- coding: utf-8 -*-

## \package ui.statusbar

# MIT licensing
# See: docs/LICENSE.txt


import wx


## A status bar for compatibility between wx 3.0 & older versions
class StatusBar(wx.StatusBar):
    if wx.MAJOR_VERSION > 2:
        sb_style = wx.STB_DEFAULT_STYLE
    
    else:
        sb_style = wx.ST_SIZEGRIP
    
    def __init__(self, parent, ID=wx.ID_ANY, style=sb_style,
                name=wx.StatusLineNameStr):
        wx.StatusBar.__init__(self, parent, ID, style, name)
        
        parent.SetStatusBar(self)
