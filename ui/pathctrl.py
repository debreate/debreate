# -*- coding: utf-8 -*-

## \package ui.pathctrl

# MIT licensing
# See: docs/LICENSE.txt


import os, wx


PATH_DEFAULT = wx.NewId()
PATH_WARN = wx.NewId()


## TODO: Doxygen
#  
#  FIXME: Use boolean value instead of type
class PathCtrl(wx.TextCtrl):
    def __init__(self, parent, ctrl_id=wx.ID_ANY, value=wx.EmptyString, ctrl_type=PATH_DEFAULT,
                default=wx.EmptyString):
        wx.TextCtrl.__init__(self, parent, ctrl_id, value)
        
        self.ctrl_type = ctrl_type
        
        # Get the value of the textctrl so it can be restored
        self.default = default
        
        # For restoring color of text area
        self.clr_default = self.GetBackgroundColour()
        
        # Make sure first character is forward slash
        wx.EVT_KEY_UP(self, self.OnKeyUp)
        
        # Check if path is available on construction
        if self.ctrl_type == PATH_WARN:
            self.SetPathAvailable()
    
    
    ## TODO: Doxygen
    def GetDefaultValue(self):
        return self.default
    
    
    ## TODO: Doxygen
    def OnKeyUp(self, event=None):
        value = self.GetValue()
        insertion_point = self.GetInsertionPoint()+1
        if value == wx.EmptyString or value[0] != u'/':
            self.SetValue(u'/{}'.format(value))
            self.SetInsertionPoint(insertion_point)
        
        # If PathCtrl is set to warn on non-existent paths, change background color to red when path
        # doesn't exist
        value = self.GetValue()
        if self.ctrl_type == PATH_WARN:
            self.SetPathAvailable()
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def Reset(self):
        self.SetValue(self.default)
        
        if self.ctrl_type == PATH_WARN:
            self.SetPathAvailable()
        
        self.SetInsertionPointEnd()
    
    
    ## TODO: Doxygen
    def SetPathAvailable(self):
        if os.path.isdir(self.GetValue()):
            self.SetBackgroundColour(self.clr_default)
            return
        
        self.SetBackgroundColour(u'red')
    
    
    ## TODO: Doxygen
    def SetDefaultValue(self, default):
        self.default = default
