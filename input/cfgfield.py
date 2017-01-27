# -*- coding: utf-8 -*-

## \package input.cfgfield
#  
#  Fields that affect settings

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.config import ConfCode
from dbr.config import ReadConfig
from dbr.config import SetDefaultConfigKey
from dbr.config import WriteConfig
from dbr.log    import Logger


## Class that updates the configuration file when a specific event occurs
class ConfigField:
    def __init__(self, cfgKey=None):
        self.ConfigKey = cfgKey
        
        if self.ConfigKey == None:
            self.ConfigKey = self.GetName()
        
        # Add to recognized configuration keys
        SetDefaultConfigKey(self.ConfigKey, self.GetDefaultValue())
        
        # Set state using config file if found
        state = ReadConfig(self.ConfigKey)
        
        print(u'\nDEBUG: ConfigField:')
        
        ret_codes = (
            ConfCode.FILE_NOT_FOUND,
            ConfCode.KEY_NOT_DEFINED,
            ConfCode.KEY_NO_EXIST,
            )
        
        # FIXME:
        if state not in (ret_codes):
            self.SetValue(state)
        
        else:
            Logger.Debug(__name__, u'Key not found: {}'.format(self.ConfigKey))
        
        # *** Event Handling *** #
        
        if isinstance(self, wx.CheckBox):
            self.Bind(wx.EVT_CHECKBOX, self.OnToggle)
    
    
    ## TODO: Doxygen
    def GetConfigKey(self):
        return self.ConfigKey
    
    
    ## TODO: Doxygen
    def GetConfigValue(self):
        GETVAL = 1
        CHOICE = 2
        
        ftypes = {
            GETVAL: (wx.TextCtrl, wx.CheckBox,),
            CHOICE: wx.Choice,
            }
        
        if isinstance(self, ftypes[GETVAL]):
            return self.GetValue()
        
        if isinstance(self, ftypes[CHOICE]):
            return self.GetStringSelection()
    
    
    ## TODO: Doxygen
    def OnToggle(self, event=None):
        if event:
            event.Skip()
        
        WriteConfig(self.ConfigKey, self.GetConfigValue())
    
    
    ## TODO: Doxygen
    def SetConfigKey(self, cfgKey):
        self.ConfigKey = cfgKey
