# -*- coding: utf-8 -*-

## \package input.toggle

# MIT licensing
# See: docs/LICENSE.txt


import wx

from fields.cmdfield    import CommandField
from input.cfgfield     import ConfigField
from input.essential    import EssentialField
from wiz.helper         import FieldEnabled


## Standard wx.CheckBox
class CheckBox(wx.CheckBox, CommandField):
    def __init__(self, parent, win_id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=0, name=wx.CheckBoxNameStr, defaultValue=False,
                commands=None, requireAll=False):
        
        wx.CheckBox.__init__(self, parent, win_id, label, pos, size, style, name=name)
        CommandField.__init__(self, commands, requireAll)
        
        self.default = defaultValue
        self.tt_name = name
        
        # Initialize with default value
        self.SetValue(self.default)
    
    
    ## TODO: Doxygen
    def GetDefaultValue(self):
        return self.default
    
    
    ## Retrieves current 'checked' state
    #  
    #  Differences from inherited method:
    #  - Always returns False if the object is disabled
    #  \override wx.CheckBox.GetValue
    def GetValue(self):
        if not FieldEnabled(self):
            return False
        
        return wx.CheckBox.GetValue(self)
    
    
    ## Resets check box to default value
    def Reset(self):
        self.SetChecked(self.GetDefaultValue())
    
    
    ## Manually emit EVT_CHECKBOX when setting value
    #  
    #  \param state
    #    If \b \e True, the check is on, otherwise it is off
    def SetChecked(self, state=True):
        wx.PostEvent(self, wx.CommandEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED))
        
        return self.SetValue(state)
    
    
    ## TODO: Doxygen
    def SetDefaultValue(self, value):
        self.default = value
    
    
    ## Override inherited method to not allow changing value if disabled
    def SetValue(self, value):
        if FieldEnabled(self):
            return wx.CheckBox.SetValue(self, value)


## CheckBox that updates config file when value is changed
class CheckBoxCFG(CheckBox, ConfigField):
    def __init__(self, parent, win_id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=0, name=wx.CheckBoxNameStr, defaultValue=False,
                commands=None, requireAll=False, cfgKey=None, cfgSect=None):
        
        CheckBox.__init__(self, parent, win_id, label, pos, size, style, name, defaultValue,
                commands, requireAll)
        ConfigField.__init__(self, cfgKey, cfgSect)


## CheckBox class that notifies main window to mark project dirty
class CheckBoxESS(CheckBox, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=0, name=wx.CheckBoxNameStr, defaultValue=False,
                commands=None, requireAll=False):
        
        CheckBox.__init__(self, parent, win_id, label, pos, size, style, name, defaultValue,
                commands, requireAll)
        EssentialField.__init__(self)
