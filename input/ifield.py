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
    def __init__(self, defaultValue, outLabel=None):
        # TODO: Rename to 'self.Default'
        self.default = defaultValue
        self.OutputLabel = outLabel
        
        # Initialize with default value
        self.Reset()
    
    
    ## Retrieves the field's default value
    def GetDefaultValue(self):
        return self.default
    
    
    ## Retrieves label for text output
    def GetOutputLabel(self):
        return self.OutputLabel
    
    
    ## TODO: Doxygen
    def HasOutputLabel(self):
        return IsString(self.OutputLabel) and self.OutputLabel != wx.EmptyString
    
    
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
        
        elif isinstance(self, wx.ListCtrl):
            #  FIXME: What to do if default value is not 'None'
            if self.default == None:
                return self.DeleteAllItems()
        
        else:
            self.SetValue(self.default)
    
    
    ## Sets the field's default value
    def SetDefaultValue(self, value):
        self.default = value
