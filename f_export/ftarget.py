# -*- coding: utf-8 -*-

## \package f_export.ftarget

# MIT licensing
# See: docs/LICENSE.txt


import wx

from input.pathctrl import PathCtrl
from input.toggle   import CheckBox
from ui.layout      import BoxSizer
from ui.panel       import BorderedPanel


## A class that defines a standard target check box & custom target text input area
#  
#  \param defaultPath
#    Default install target
#  \param win_id
#    Window ID
#  \param defaultType
#    Should be either \b \e CheckBox or derived class
#  \param defaultValue
#    \b \e Boolean to set default path check box value to checked or not (default is True)
#  \param customType
#    Should be wx.TextCtrl or derived class
class FileOTarget(BorderedPanel):
    def __init__(self, parent, defaultPath, win_id=-1, defaultType=CheckBox, defaultValue=True,
            customType=PathCtrl, name=u'file_output_target', pathIds=[]):
        
        BorderedPanel.__init__(self, parent, win_id, name=name)
        
        id_default = wx.ID_ANY
        id_custom = wx.ID_ANY
        
        if pathIds:
            if isinstance(pathIds, int):
                id_default = pathIds
            
            else:
                id_default = pathIds[0]
                
                if len(pathIds) > 1:
                    id_custom = pathIds[1]
        
        self.PathDefault = defaultType(self, id_default, defaultPath, defaultValue=defaultValue)
        
        self.PathCustom = customType(self, id_custom)
        
        # *** Event Handing *** #
        
        self.PathDefault.Bind(wx.EVT_CHECKBOX, self.OnSelectTarget)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        
        lyt_main.AddSpacer(5)
        lyt_main.Add(self.PathDefault, 0, wx.LEFT|wx.RIGHT, 5)
        lyt_main.AddSpacer(5)
        lyt_main.Add(self.PathCustom, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.AddSpacer(5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Post Layout/Event Actions *** #
        
        self.PathDefault.SetChecked(self.PathDefault.GetDefaultValue())
    
    
    ## Retrieves the custom set target path
    def GetCustomPath(self):
        return self.PathCustom.GetValue()
    
    
    ## Retrieves the object representing the default path
    def GetDefaultObject(self):
        return self.PathDefault
    
    
    ## Retrieves the default target path
    def GetDefaultPath(self):
        return self.PathDefault.GetLabel()
    
    
    ## Retrieves currently selected path
    def GetPath(self):
        if self.PathDefault.GetValue():
            return self.GetDefaultPath()
        
        return self.GetCustomPath()
    
    
    ## Enables/Disables custom target field
    def OnSelectTarget(self, event=None):
        self.PathCustom.Enable(not self.PathDefault.GetValue())
        
        if event:
            event.Skip(True)
    
    
    ## Reset controls to default settings
    def Reset(self):
        self.PathDefault.Reset()
        self.PathCustom.Reset()
    
    
    ## Selects custom path & sets value
    #  
    #  \param path
    #    New value for custom path
    #  \return
    #    \b \e True if using custom path & is equal to 'path' parameter
    def SetPath(self, path):
        if self.PathDefault.GetValue():
            self.PathDefault.SetChecked(False)
        
        self.PathCustom.SetValue(path)
        
        return self.PathCustom.Value == path and not self.Path.Value
    
    
    ## Check if using default path
    def UsingDefault(self):
        return self.PathDefault.GetValue()
