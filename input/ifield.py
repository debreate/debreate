# -*- coding: utf-8 -*-

## \package input.ifield
#
#  Input fields

# MIT licensing
# See: docs/LICENSE.txt


import wx

from globals.strings import IsString


## An input field that sets a default value
class InputField:
    def __init__(self, defaultValue):
        # TODO: Rename to 'self.Default'
        self.default = defaultValue
        
        # Initialize with default value
        self.Reset()
    
    
    ## Retrieves the field's default value
    def GetDefaultValue(self):
        return self.default
    
    
    ## Resets field to default value
    def Reset(self):
        if isinstance(self, wx.Choice):
            if self.GetCount():
                if IsString(self.default):
                    self.SetStringSelection(self.default)
                    
                    return self.StringSelection == self.default
                
                else:
                    self.SetSelection(self.default)
                    
                    return self.Selection == self.default
        
        else:
            self.SetValue(self.default)
        
        return self.Value == self.default
    
    
    ## Sets the field's default value
    def SetDefaultValue(self, value):
        self.default = value
