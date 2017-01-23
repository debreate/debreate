# -*- coding: utf-8 -*-

## \package app

# MIT licensing
# See: docs/LICENSE.txt


import wx


## Custom wx.App class for setting & retrieving main window instance
class DebreateApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        
        self.MainWindow = None
    
    
    ## Retrieve main window instance
    def GetMainWindow(self):
        return self.MainWindow
    
    
    ## Set the main window instance
    def SetMainWindow(self, window):
        self.MainWindow = window
