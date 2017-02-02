# -*- coding: utf-8 -*-

## \package input.select

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.combo import OwnerDrawnComboBox

from dbr.font           import MONOSPACED_MD
from globals.strings    import TextIsEmpty
from input.essential    import EssentialField
from input.ifield       import InputField


## Custom wx.Choice class for compatibility with older wx versions
class Choice(wx.Choice, InputField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            choices=[], style=0, validator=wx.DefaultValidator, name=wx.ChoiceNameStr,
            defaultValue=0):
        
        wx.Choice.__init__(self, parent, win_id, pos, size, choices, style, validator, name)
        InputField.__init__(self, defaultValue)
    
    
    ## wx 2.8 does not define wx.Choice.Set
    #  
    #  \param items
    #    List of items to be set
    #  \override wx.Choice.Set
    def Set(self, items):
        cached_value = self.GetStringSelection()
        
        if not isinstance(items, (tuple, list, dict,)):
            items = (items,)
        
        if wx.MAJOR_VERSION > 2:
            wx.Choice.Set(self, items)
        
        else:
            self.Clear()
            
            for I in items:
                self.Append(I)
        
        if cached_value:
            self.SetStringSelection(cached_value)


## Choice class that notifies main window to mark the project dirty
#
#  This is a dummy class to facilitate merging to & from unstable branch
class ChoiceESS(Choice, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            choices=[], style=0, validator=wx.DefaultValidator, name=wx.ChoiceNameStr):
        
        Choice.__init__(self, parent, win_id, pos, size, choices, style, validator, name)
        EssentialField.__init__(self)


## Custom combo box that sets background colors when enabled/disabled
#  
#  This is a workaround for wx versions older than 3.0
#  
#  Notes on processing combo box events (EVT_COMBOBOX)
#    wx 2.8:
#        wx.combo.OwnerDrawnComboBox
#            - Keyboard:     Emits EVT_TEXT
#            - Drop-down:    Emits EVT_COMBOBOX & 2 EVT_TEXT
#            - Mouse scroll: Does nothing
#        wx.ComboBox
#            - Keyboard:     Emits EVT_TEXT
#            - Drop-down:    Emits EVT_COMBOBOX & EVT_TEXT
#            - Mouse scroll: Emits EVT_COMBOBOX & EVT_TEXT (Note: Doesn't scroll until after drop-down select)
#    wx 3.0:
#        wx.combo.OwnerDrawnComboBox
#            - Keyboard:     Emits EVT_TEXT
#            - Drop-down:    Emits EVT_COMBOBOX & 2 EVT_TEXT
#            - Mouse scroll: Emits EVT_COMBOBOX
#            Other Notes: Mouse scroll emits EVT_KEY_DOWN
#        wx.ComboBox
#            - Keyboard:     Emits EVT_TEXT
#            - Drop-down:    Emits EVT_COMBOBOX & EVT_TEXT
#            - Mouse scroll: Emits EVT_COMBOBOX & EVT_TEXT (Note: Doesn't scroll until after drop-down select)
class ComboBox(OwnerDrawnComboBox, InputField):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator,
            name=wx.ComboBoxNameStr, monospace=False, defaultValue=wx.EmptyString):
        
        OwnerDrawnComboBox.__init__(self, parent, win_id, value, pos, size, choices, style,
                validator, name)
        InputField.__init__(self, defaultValue)
        
        if wx.MAJOR_VERSION < 3:
            self.clr_disabled = self.GetBackgroundColour()
            self.clr_enabled = self.GetTextCtrl().GetBackgroundColour()
        
        if monospace:
            self.TextCtrl.SetFont(MONOSPACED_MD)
            # FIXME: This doesn't work (use monospace in popup list)
            self.PopupControl.GetControl().SetFont(MONOSPACED_MD)
    
    
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
    
    
    ## Override inherited method for compatibility with older wx versions
    #  
    #  \param items
    #    \b \e String or \b \e list of string items
    def Set(self, items):
        # Text control is cleared when options are changed
        cached_value = self.GetValue()
        
        if not isinstance(items, (tuple, list, dict)):
            items = (items,)
        
        if wx.MAJOR_VERSION > 2:
            OwnerDrawnComboBox.Set(self, items)
        
        else:
            self.Clear()
            
            for I in items:
                self.Append(I)
        
        if not TextIsEmpty(cached_value):
            self.SetValue(cached_value)


## ComboBox class that notifies main window to mark the project dirty
#
#  This is a dummy class to facilitate merging to & from unstable branch
class ComboBoxESS(ComboBox, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator,
            name=wx.ComboBoxNameStr, monospace=False, defaultValue=wx.EmptyString):
        
        ComboBox.__init__(self, parent, win_id, value, pos, size, choices, style, validator,
                name, monospace, defaultValue)
        EssentialField.__init__(self)
