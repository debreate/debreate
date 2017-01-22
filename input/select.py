# -*- coding: utf-8 -*-

## \package input.select

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.combo import OwnerDrawnComboBox

from dbr.font           import MONOSPACED_MD
from globals.strings    import TextIsEmpty
from input.essential    import EssentialField


## Custom wx.Choice class for compatibility with older wx versions
class Choice(wx.Choice):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            choices=[], style=0, validator=wx.DefaultValidator, name=wx.ChoiceNameStr):
        
        wx.Choice.__init__(self, parent, win_id, pos, size, choices, style, validator, name)
    
    
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
class ChoiceESS(Choice, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            choices=[], style=0, validator=wx.DefaultValidator, name=wx.ChoiceNameStr):
        
        Choice.__init__(self, parent, win_id, pos, size, choices, style, validator, name)
        EssentialField.__init__(self)


## Custom combo box that sets background colors when enabled/disabled
#  
#  This is a workaround for wx versions older than 3.0
class ComboBox(OwnerDrawnComboBox):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator,
            name=wx.ComboBoxNameStr, monospace=False):
        
        OwnerDrawnComboBox.__init__(self, parent, win_id, value, pos, size, choices, style,
                validator, name)
        
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
class ComboBoxESS(ComboBox, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator,
            name=wx.ComboBoxNameStr, monospace=False):
        
        ComboBox.__init__(self, parent, win_id, value, pos, size, choices, style, validator,
                name, monospace)
        EssentialField.__init__(self)
        
        # *** Event Handling *** #
        
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheelEvent)
    
    
    ## Process an EVT_MOUSEWHEEL
    def OnMouseWheelEvent(self, event=None):
        if event:
            # Allow mouse wheel to change text
            event.Skip(True)
        
        # The following behavior only applies to wx 3.0 & later
        if wx.MAJOR_VERSION > 2:
            # This is a workaround since wx.combo.OwnerDrawnComboBox doesn't emit EVT_TEXT on mouse wheel event
            if isinstance(self, EssentialField):
                self.NotifyMainWindow(event)
