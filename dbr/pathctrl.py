# -*- coding: utf-8 -*-


import os, wx


PATH_DEFAULT = wx.NewId()
PATH_WARN = wx.NewId()

class PathCtrl(wx.TextCtrl):
    def __init__(self, parent, id=wx.ID_ANY, value=wx.EmptyString, type=PATH_DEFAULT):
        wx.TextCtrl.__init__(self, parent, id, value)
        
        self.type = type
        
        # Get the value of the textctrl so it can be restored
        self.default = u'/'
        
        # Make sure first character is forward slash
        wx.EVT_KEY_UP(self, self.OnKeyUp)
    
    def OnKeyUp(self, event):
        value = self.GetValue()
        insertion_point = self.GetInsertionPoint()+1
        if value == wx.EmptyString or value[0] != u'/':
            self.SetValue(u'/{}'.format(value))
            self.SetInsertionPoint(insertion_point)
        
        # If PathCtrl is set to warn on non-existent paths, change background color to red when path
        # doesn't exist
        value = self.GetValue()
        if self.type == PATH_WARN:
            if not os.path.exists(value):
                self.SetBackgroundColour(u'red')
            else:
                self.SetBackgroundColour(u'white')
        event.Skip()