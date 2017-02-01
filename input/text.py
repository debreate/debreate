# -*- coding: utf-8 -*-

## \package input.text

# MIT licensing
# See: docs/LICENSE.txt


import time, wx

from dbr.font               import MONOSPACED_LG
from dbr.language           import GT
from globals.fileio         import ReadFile
from globals.strings        import TextIsEmpty
from globals.wizardhelper   import GetMainWindow
from input.essential        import EssentialField
from ui.layout              import BoxSizer
from ui.panel               import BorderedPanel
from ui.panel               import ControlPanel


## Text control set up for handling file drop events
class TextArea(wx.TextCtrl):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, defaultValue=wx.EmptyString,
            pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
            name=wx.TextCtrlNameStr):
        
        wx.TextCtrl.__init__(self, parent, win_id, value, pos, size, style, validator, name)
        
        self.default = defaultValue
        
        # Enable to override default behavior of adding filename string
        self.DragAcceptFiles(True)
        
        self.accepts_drop = False
        
        # *** Event handlers *** #
        
        self.Bind(wx.EVT_DROP_FILES, self.OnDropFiles)
    
    
    ## Allow dropping files from file manager
    def EnableDropTarget(self, enable=True):
        self.accepts_drop = enable
    
    
    ## Retrieve default value
    def GetDefaultValue(self):
        return self.default
    
    
    ## TODO: Doxygen
    def IsDropTarget(self):
        return self.accepts_drop
    
    
    ## TODO: Doxygen
    def OnDropFiles(self, event=None):
        if not self.IsEnabled() or not event:
            return False
        
        # Flash red if doesn't accept file drops
        if not self.IsDropTarget():
            parent = self.GetParent()
            
            if isinstance(parent, TextAreaPanel):
                main_object = parent
            
            else:
                main_object = self
            
            bgcolor = main_object.GetBackgroundColour()
            main_object.SetBackgroundColour(wx.RED)
            
            wx.Yield()
            time.sleep(0.1)
            
            main_object.SetBackgroundColour(bgcolor)
            
            return False
        
        filename = event.GetFiles()
        
        if not filename:
            return False
        
        # Use only the first file
        if isinstance(filename, (tuple, list)):
            filename = filename[0]
        
        if not TextIsEmpty(self.GetValue()):
            msg_li1 = GT(u'This will delete all text')
            msg_li2 = GT(u'Continue?')
            
            # FIXME: Use custom dialogs (currently cannot import)
            message = wx.MessageDialog(GetMainWindow(), u'{}\n\n{}'.format(msg_li1, msg_li2),
                    GT(u'Warning'), wx.OK|wx.CANCEL|wx.ICON_WARNING)
            
            confirmed = message.ShowModal() in (wx.OK, wx.ID_OK, wx.YES, wx.ID_YES)
            
            if not confirmed:
                return False
        
        try:
            input_text = ReadFile(filename)
            
            if input_text:
                self.SetValue(input_text)
                
                return True
        
        except UnicodeDecodeError:
            pass
        
        #ShowErrorDialog(GT(u'There was an error reading file: {}').format(filename))
        wx.MessageDialog(GetMainWindow(), GT(u'There was an error reading file: {}').format(filename),
                GT(u'Error'), wx.OK|wx.ICON_ERROR).ShowModal()
        
        return False
    
    
    ## Reset text area to default value
    def Reset(self):
        self.SetValue(self.default)
    
    
    ## Sets the default value
    def SetDefaultValue(self, value):
        self.default = value


## TextArea that notifies main window to mark the project dirty
class TextAreaESS(TextArea, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, defaultValue=wx.EmptyString,
            pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
            name=wx.TextCtrlNameStr, outLabel=None):
        
        TextArea.__init__(self, parent, win_id, value, defaultValue, pos, size, style, validator,
                name)
        EssentialField.__init__(self, outLabel)


## A text control that is multiline & uses a themed border
class TextAreaML(TextArea):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, defaultValue=wx.EmptyString,
            pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
            name=wx.TextCtrlNameStr):
        
        TextArea.__init__(self, parent, win_id, value, defaultValue, pos, size, style|wx.TE_MULTILINE,
                validator, name)
    
    
    ## Sets the font size of the text area
    #  
    #  \param point_size
    #        \b \e int : New point size of font
    def SetFontSize(self, point_size):
        font = self.GetFont()
        font.SetPointSize(point_size)
        
        self.SetFont(font)


## TextAreaML that notifies main window to mark the project dirty
class TextAreaMLESS(TextAreaML, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, defaultValue=wx.EmptyString,
            pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
            name=wx.TextCtrlNameStr, outLabel=None):
        
        TextAreaML.__init__(self, parent, win_id, value, defaultValue, pos, size, style, validator,
                name)
        EssentialField.__init__(self, outLabel)


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


## Somewhat of a hack to attemtp to get rounded corners on text control border
class TextAreaPanel(BorderedPanel, ControlPanel):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, defaultValue=wx.EmptyString,
            monospace=False, button=MT_NO_BTN, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
            name=wx.TextCtrlNameStr):
        
        BorderedPanel.__init__(self, parent, win_id, pos, size, name=name)
        
        self.MainCtrl = TextAreaML(self, value=value, defaultValue=defaultValue,
                style=style|wx.BORDER_NONE)
        
        # For setting color of disabled panel
        self.clr_disabled = self.GetBackgroundColour()
        self.clr_enabled = self.MainCtrl.GetBackgroundColour()
        
        # Match panel color to text control
        self.SetBackgroundColour(self.MainCtrl.GetBackgroundColour())
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.HORIZONTAL)
        lyt_main.Add(self.MainCtrl, 1, wx.EXPAND|wx.ALL, 2)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Post-layout Actions *** #
        
        if monospace:
            self.SetMonospaced(button)
    
    
    ## Clears all text in the text area
    def Clear(self):
        self.MainCtrl.Clear()
    
    
    ## Disables self & text area
    def Disable(self):
        return self.Enable(False)
    
    
    ## Disables or enables self & text area
    #  
    #  Because of issues with text control background color, it
    #  must be set manually when the parent TextAreaPanel
    #  is disabled. This causes some text artifacts in wx 3.0
    #  when using the SetValue & WriteText methods. Because of
    #  that, when the control is enabled/disabled, the value
    #  is stored, then the control cleared. When the new
    #  background color is set, the value is restored, causing
    #  the text to take on the same background color.
    def Enable(self, *args, **kwargs):
        # Clearing text area is done as workaround for text background color bug
        current_value = self.MainCtrl.GetValue()
        insertion_point = self.MainCtrl.GetInsertionPoint()
        self.MainCtrl.Clear()
        
        return_value = BorderedPanel.Enable(self, *args, **kwargs)
        
        if self.IsEnabled():
            self.SetBackgroundColour(self.clr_enabled)
        
            # Older versions of wx do not change color of disabled multiline text control
            if wx.MAJOR_VERSION < 3:
                self.MainCtrl.SetBackgroundColour(self.clr_enabled)
        
        else:
            self.SetBackgroundColour(self.clr_disabled)
        
            # Older versions of wx do not change color of disabled multiline text control
            if wx.MAJOR_VERSION < 3:
                self.MainCtrl.SetBackgroundColour(self.clr_disabled)
        
        # Reinstate the text
        self.MainCtrl.SetValue(current_value)
        self.MainCtrl.SetInsertionPoint(insertion_point)
        
        return return_value
    
    
    ## Allow dropping files from file manager
    def EnableDropTarget(self, enable=True):
        return self.MainCtrl.EnableDropTarget(enable)
    
    
    ## Retrieves the caret instance of the wx.TextCtrl
    def GetCaret(self):
        return self.MainCtrl.GetCaret()
    
    
    ## Retrieves text area's default value
    def GetDefaultValue(self):
        return self.MainCtrl.GetDefaultValue()
    
    
    ## Retrieves font that text area is using
    def GetFont(self):
        return self.MainCtrl.GetFont()
    
    
    ## Retrieves carat position
    def GetInsertionPoint(self):
        return self.MainCtrl.GetInsertionPoint()
    
    
    ## TODO: Doxygen
    def GetLastPosition(self):
        return self.MainCtrl.GetLastPosition()
    
    
    ## Retrieves the text area object
    def GetTextCtrl(self):
        return self.MainCtrl
    
    
    ## Retrieves text from text input
    def GetValue(self):
        return self.MainCtrl.GetValue()
    
    
    ## Returns True if text area is empty
    def IsEmpty(self):
        return self.MainCtrl.IsEmpty()
    
    
    ## TODO: Doxygen
    def OnToggleTextSize(self, event=None):
        # Save insertion point
        insertion = self.MainCtrl.GetInsertionPoint()
        
        sizes = {
            7: 8,
            8: 10,
            10: 11,
            11: 7,
        }
        
        font = self.MainCtrl.GetFont()
        new_size = sizes[font.GetPointSize()]
        font.SetPointSize(new_size)
        
        self.MainCtrl.SetFont(font)
        self.MainCtrl.SetInsertionPoint(insertion)
        self.MainCtrl.SetFocus()
    
    
    ## Resets text area to default value
    def Reset(self):
        return self.MainCtrl.Reset()
    
    
    ## Sets text area's default value
    def SetDefaultValue(self, value):
        return self.MainCtrl.SetDefaultValue(value)
    
    
    ## TODO: Doxygen
    def SetBackgroundColour(self, *args, **kwargs):
        self.MainCtrl.SetBackgroundColour(*args, **kwargs)
        return BorderedPanel.SetBackgroundColour(self, *args, **kwargs)
    
    
    ## Sets the caret instance for the wx.TextCtrl
    def SetCaret(self, caret):
        return self.MainCtrl.SetCaret(caret)
    
    
    ## Sets font in text area
    def SetFont(self, font):
        self.MainCtrl.SetFont(font)
    
    
    ## Sets the font size of the text in the text area
    #  
    #  \override ui.textinput.MultilineTextCtrl.SetFontSize
    def SetFontSize(self, point_size):
        self.MainCtrl.SetFontSize(point_size)
    
    
    ## TODO: Doxygen
    def SetForegroundColour(self, *args, **kwargs):
        self.MainCtrl.SetForegroundColour(*args, **kwargs)
        return BorderedPanel.SetForegroundColour(self, *args, **kwargs)
    
    
    ## Places carat to position in text area
    def SetInsertionPoint(self, point):
        self.MainCtrl.SetInsertionPoint(point)
    
    
    ## Places carat at end of text area
    def SetInsertionPointEnd(self):
        self.MainCtrl.SetInsertionPointEnd()
    
    
    ## Sets text in text area
    def SetValue(self, text):
        self.MainCtrl.SetValue(text)
    
    
    ## Sets text area font to monospaced
    def SetMonospaced(self, button):
        self.MainCtrl.SetFont(MONOSPACED_LG)
        
        if button:
            lyt_main = self.GetSizer()
            
            btn_text_size = wx.Button(self, label=GT(u'Text Size'))
            if button in (MT_BTN_TL, MT_BTN_TR):
                lyt_main.Insert(0, btn_text_size, 0, button_H_pos[button]|wx.LEFT|wx.RIGHT, 5)
            
            else:
                lyt_main.Add(btn_text_size, 0, button_H_pos[button]|wx.LEFT|wx.RIGHT, 5)
            
            btn_text_size.Bind(wx.EVT_BUTTON, self.OnToggleTextSize)
            
            self.Layout()
    
    
    ## TODO: Doxygen
    def ShowPosition(self, pos):
        return self.MainCtrl.ShowPosition(pos)
    
    
    ## Writes to the text area
    def WriteText(self, text):
        self.MainCtrl.WriteText(text)


## TextAreaPanel that notifies main window to mark the project dirty
class TextAreaPanelESS(TextAreaPanel, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, value=wx.EmptyString, defaultValue=wx.EmptyString,
            monospace=False, button=MT_NO_BTN, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
            name=wx.TextCtrlNameStr, outLabel=None):
        
        TextAreaPanel.__init__(self, parent, win_id, value, defaultValue, monospace, button, pos,
                size, style, name)
        EssentialField.__init__(self, outLabel)
