# -*- coding: utf-8 -*-

## \package dbr.textinput

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.font       import MONOSPACED_LG
from dbr.functions  import TextIsEmpty
from dbr.language   import GT
from dbr.panel      import BorderedPanel


## A text control that is multiline & uses a themed border
class MultilineTextCtrl(wx.TextCtrl):
    def __init__(self, parent, ID=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.TextCtrlNameStr):
        wx.TextCtrl.__init__(self, parent, ID, value, pos, size, style|wx.TE_MULTILINE|wx.BORDER_NONE,
                validator, name)
    
    
    ## Sets the font size of the text area
    #  
    #  \param point_size
    #        \b \e int : New point size of font
    def SetFontSize(self, point_size):
        font = self.GetFont()
        font.SetPointSize(point_size)
        
        self.SetFont(font)


## Somewhat of a hack to attemtp to get rounded corners on text control border
class MultilineTextCtrlPanel(BorderedPanel):
    def __init__(self, parent, ID=wx.ID_ANY, value=wx.EmptyString, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=0, name=wx.TextCtrlNameStr):
        BorderedPanel.__init__(self, parent, ID, pos, size, name=name)
        
        self.textarea = MultilineTextCtrl(self, style=style)
        if not TextIsEmpty(value):
            self.textarea.SetValue(value)
        
        # For setting color of disabled panel
        self.clr_disabled = self.GetBackgroundColour()
        self.clr_enabled = self.textarea.GetBackgroundColour()
        
        # Match panel color to text control
        self.SetBackgroundColour(self.textarea.GetBackgroundColour())
        
        self.layout_V1 = wx.BoxSizer(wx.HORIZONTAL)
        self.layout_V1.Add(self.textarea, 1, wx.EXPAND|wx.ALL, 2)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.layout_V1)
        self.Layout()
    
    
    ## Clears all text in the text area
    def Clear(self):
        self.textarea.Clear()
    
    
    ## Disables self & text area
    def Disable(self):
        return self.Enable(False)
    
    
    ## Disables or enables self & text area
    #  
    #  Because of issues with text control background color, it
    #  must be set manually when the parent MultilineTextCtrlPanel
    #  is disabled. This causes some text artifacts in wx 3.0
    #  when using the SetValue & WriteText methods. Because of
    #  that, when the control is enabled/disabled, the value
    #  is stored, then the control cleared. When the new
    #  background color is set, the value is restored, causing
    #  the text to take on the same background color.
    def Enable(self, *args, **kwargs):
        # Clearing text area is done as workaround for text background color bug
        current_value = self.textarea.GetValue()
        insertion_point = self.textarea.GetInsertionPoint()
        self.textarea.Clear()
        
        return_value = BorderedPanel.Enable(self, *args, **kwargs)
        
        if self.IsEnabled():
            self.SetBackgroundColour(self.clr_enabled)
        
            # Older versions of wx do not change color of disabled multiline text control
            if wx.MAJOR_VERSION < 3:
                self.textarea.SetBackgroundColour(self.clr_enabled)
        
        else:
            self.SetBackgroundColour(self.clr_disabled)
        
            # Older versions of wx do not change color of disabled multiline text control
            if wx.MAJOR_VERSION < 3:
                self.textarea.SetBackgroundColour(self.clr_disabled)
        
        # Reinstate the text
        self.textarea.SetValue(current_value)
        self.textarea.SetInsertionPoint(insertion_point)
        
        return return_value
    
    
    ## Retrieves the caret instance of the wx.TextCtrl
    def GetCaret(self):
        return self.textarea.GetCaret()
    
    
    ## Retrieves font that text area is using
    def GetFont(self):
        return self.textarea.GetFont()
    
    
    ## Retrieves carat position
    def GetInsertionPoint(self):
        return self.textarea.GetInsertionPoint()
    
    
    ## TODO: Doxygen
    def GetLastPosition(self):
        return self.textarea.GetLastPosition()
    
    
    ## Retrieves the text area object
    def GetTextCtrl(self):
        return self.textarea
    
    
    ## Retrieves text from text input
    def GetValue(self):
        return self.textarea.GetValue()
    
    
    ## Returns True if text area is empty
    def IsEmpty(self):
        return self.textarea.IsEmpty()
    
    
    ## TODO: Doxygen
    def SetBackgroundColour(self, *args, **kwargs):
        self.textarea.SetBackgroundColour(*args, **kwargs)
        return BorderedPanel.SetBackgroundColour(self, *args, **kwargs)
    
    
    ## Sets the caret instance for the wx.TextCtrl
    def SetCaret(self, caret):
        return self.textarea.SetCaret(caret)
    
    
    ## Sets font in text area
    def SetFont(self, font):
        self.textarea.SetFont(font)
    
    
    ## Sets the font size of the text in the text area
    #  
    #  \override dbr.textinput.MultilineTextCtrl.SetFontSize
    def SetFontSize(self, point_size):
        self.textarea.SetFontSize(point_size)
    
    
    ## TODO: Doxygen
    def SetForegroundColour(self, *args, **kwargs):
        self.textarea.SetForegroundColour(*args, **kwargs)
        return BorderedPanel.SetForegroundColour(self, *args, **kwargs)
    
    
    ## Places carat to position in text area
    def SetInsertionPoint(self, point):
        self.textarea.SetInsertionPoint(point)
    
    
    ## Places carat at end of text area
    def SetInsertionPointEnd(self):
        self.textarea.SetInsertionPointEnd()
    
    
    ## Sets text in text area
    def SetValue(self, text):
        self.textarea.SetValue(text)
    
    
    ## TODO: Doxygen
    def ShowPosition(self, pos):
        return self.textarea.ShowPosition(pos)
    
    
    ## Writes to the text area
    def WriteText(self, text):
        self.textarea.WriteText(text)


MT_NO_BTN = 0
MT_BTN_TL = 1
MT_BTN_TR = 2
MT_BTN_BL = 3
MT_BTN_BR = 4

button_H_pos = {
    MT_BTN_TL: wx.ALIGN_LEFT,
    MT_BTN_TR: wx.ALIGN_RIGHT,
    MT_BTN_BL: wx.ALIGN_LEFT,
    MT_BTN_BR: wx.ALIGN_RIGHT,
}


## TODO: Doxygen
#  
#  TODO: Remove button & toggle text from external buttons
class MonospaceTextCtrl(MultilineTextCtrlPanel):
    def __init__(self, parent, ID=wx.ID_ANY, value=wx.EmptyString, button=MT_NO_BTN,
                pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL,
                name=wx.TextCtrlNameStr):
        MultilineTextCtrlPanel.__init__(self, parent, ID, value, pos, size, style, name)
        
        self.textarea.SetFont(MONOSPACED_LG)
        
        if button:
            btn_font = wx.Button(self, label=GT(u'Text Size'))
            if button in (MT_BTN_TL, MT_BTN_TR):
                self.layout_V1.Insert(0, btn_font, 0, button_H_pos[button]|wx.LEFT|wx.RIGHT, 5)
            
            else:
                self.layout_V1.Add(btn_font, 0, button_H_pos[button]|wx.LEFT|wx.RIGHT, 5)
            
            btn_font.Bind(wx.EVT_BUTTON, self.OnToggleTextSize)
    
    
    ## TODO: Doxygen
    def OnToggleTextSize(self, event=None):
        # Save insertion point
        insertion = self.textarea.GetInsertionPoint()
        
        sizes = {
            7: 8,
            8: 10,
            10: 11,
            11: 7,
        }
        
        font = self.textarea.GetFont()
        new_size = sizes[font.GetPointSize()]
        font.SetPointSize(new_size)
        
        self.textarea.SetFont(font)
        self.textarea.SetInsertionPoint(insertion)
        self.textarea.SetFocus()
