# -*- coding: utf-8 -*-

## \package dbr.custom

# MIT licensing
# See: docs/LICENSE.txt


import sys, wx

from dbr.textinput import TextAreaPanel


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
