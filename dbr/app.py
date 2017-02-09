# -*- coding: utf-8 -*-

## \package dbr.app

# MIT licensing
# See: docs/LICENSE.txt


import wx


## Custom wx.App class for setting & retrieving main window instance
class DebreateApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        
        self.MainWindow = None
    
    
    ## Retrieves main window instance
    def GetMainWindow(self):
        return self.MainWindow
    
    
    ## Retrieves the wiz.wizard.Wizard instance
    def GetWizard(self):
        if self.MainWindow:
            return self.MainWindow.GetWizard()
    
    
    ## Set the main window instance
    def SetMainWindow(self, window):
        self.MainWindow = window
