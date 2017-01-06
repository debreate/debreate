# -*- coding: utf-8 -*-

## \package dbr.selectinput

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.combo import OwnerDrawnComboBox


## Custom combo box that sets background colors when enabled/disabled
#  
#  This is a workaround for wx versions older than 3.0
class ComboBox(OwnerDrawnComboBox):
    def __init__(self, parent, ID=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0,
            validator=wx.DefaultValidator, name=wx.ComboBoxNameStr):
        OwnerDrawnComboBox.__init__(self, parent, ID, value, pos, size, choices, style,
                validator, name)
        
        if wx.MAJOR_VERSION < 3:
            self.clr_disabled = self.GetBackgroundColour()
            self.clr_enabled = self.GetTextCtrl().GetBackgroundColour()
    
    
    ## TODO: Doxygen
    def Disable(self):
        return self.Enable(False)
    
    
    ## TODO: Doxygen
    def Enable(self, *args, **kwargs):
        return_value =  OwnerDrawnComboBox.Enable(self, *args, **kwargs)
        
        if wx.MAJOR_VERSION < 3:
            text_area = self.GetTextCtrl()
            
            if self.IsEnabled():
                text_area.SetBackgroundColour(self.clr_enabled)
            
            else:
                text_area.SetBackgroundColour(self.clr_disabled)
        
        return return_value
