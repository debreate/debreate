# -*- coding: utf-8 -*-


import sys
from wx import \
	TE_MULTILINE as wxTE_MULTILINE, \
	TE_READONLY as wxTE_READONLY, \
    EVT_BUTTON as wxEVT_BUTTON, \
    RIGHT as wxRIGHT, \
    LEFT as wxLEFT, \
    ALIGN_RIGHT as wxALIGN_RIGHT, \
    ALIGN_CENTER as wxALIGN_CENTER, \
    TOP as wxTOP, \
    BOTTOM as wxBOTTOM, \
    ALL as wxALL, \
    VERTICAL as wxVERTICAL, \
    HORIZONTAL as wxHORIZONTAL, \
    OK as wxOK, \
    ID_CANCEL as wxID_CANCEL
from wx import \
    BoxSizer as wxBoxSizer, \
    Button as wxButton, \
	Dialog as wxDialog, \
	FileDropTarget as wxFileDropTarget, \
    StaticText as wxStaticText, \
	TextCtrl as wxTextCtrl, \
    MessageDialog as wxMessageDialog

from wx.lib.docview import PathOnly
import wx.combo.ComboCtrl

from dbr.constants import ID_APPEND, ID_OVERWRITE
from dbr.functions import TextIsEmpty
from dbr.language import GT


db_here = PathOnly(__file__).decode(u'utf-8')



################
###     CLASSES       ###
################

### -*- A very handy widget that captures stdout and stderr to a wxTextCtrl -*- ###
class OutputLog(wxTextCtrl):
    def __init__(self, parent, id=-1):
        wxTextCtrl.__init__(self, parent, id, style=wxTE_MULTILINE|wxTE_READONLY)
        self.SetBackgroundColour(u'black')
        self.SetForegroundColour(u'white')
        self.stdout = sys.stdout
        self.stderr = sys.stderr
    
    def write(self, string):
        self.AppendText(string)
    
    def ToggleOutput(self, event=None):
        if (sys.stdout == self):
            sys.stdout = self.stdout
            sys.stderr = self.stderr
        else:
            sys.stdout = self
            sys.stdout = self


### -*- Dialog for overwrite prompt of a text area -*- ###
class OverwriteDialog(wxDialog):
    def __init__(self, parent, id=-1, title=GT(u'Overwrite?'), message=u''):
        wxDialog.__init__(self, parent, id, title)
        self.message = wxStaticText(self, -1, message)
        
        self.button_overwrite = wxButton(self, ID_OVERWRITE, GT(u'Overwrite'))
        self.button_append = wxButton(self, ID_APPEND, GT(u'Append'))
        self.button_cancel = wxButton(self, wxID_CANCEL)
        
        ### -*- Button events -*- ###
        wxEVT_BUTTON(self.button_overwrite, ID_OVERWRITE, self.OnButton)
        wxEVT_BUTTON(self.button_append, ID_APPEND, self.OnButton)
        
        hsizer = wxBoxSizer(wxHORIZONTAL)
        hsizer.Add(self.button_overwrite, 0, wxLEFT|wxRIGHT, 5)
        hsizer.Add(self.button_append, 0, wxLEFT|wxRIGHT, 5)
        hsizer.Add(self.button_cancel, 0, wxLEFT|wxRIGHT, 5)
        
        vsizer = wxBoxSizer(wxVERTICAL)
        vsizer.Add(self.message, 1, wxALIGN_CENTER|wxALL, 5)
        vsizer.Add(hsizer, 0, wxALIGN_RIGHT|wxTOP|wxBOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizerAndFit(vsizer)
        self.Layout()
    
    def OnButton(self, event):
        id = event.GetEventObject().GetId()
        self.EndModal(id)
    
    def GetMessage(self, event=None):
        return self.message.GetLabel()


### -*- Object for Dropping Text Files -*-
class SingleFileTextDropTarget(wxFileDropTarget):
    def __init__(self, obj):
        wxFileDropTarget.__init__(self)
        self.obj = obj
    
    def OnDropFiles(self, x, y, filenames):
        if len(filenames) > 1:
            raise ValueError(GT(u'Too many files'))
        text = open(filenames[0]).read()
        try:
            if (not TextIsEmpty(self.obj.GetValue())):
                overwrite = OverwriteDialog(self.obj, message = GT(u'The text area is not empty!'))
                id = overwrite.ShowModal()
                if (id == ID_OVERWRITE):
                    self.obj.SetValue(text)
                elif (id == ID_APPEND):
                    self.obj.SetInsertionPoint(-1)
                    self.obj.WriteText(text)
            else:
                self.obj.SetValue(text)
        except UnicodeDecodeError:
            wxMessageDialog(None, GT(u'Error decoding file'), GT(u'Error'), wxOK).ShowModal()


# A customized combo control
# FIXME: Unused. Was used in page.control
class Combo(wx.combo.ComboCtrl):
    def __init__(self, parent, id=wx.ID_ANY, value="", choices=()):
        wx.combo.ComboCtrl.__init__(self, parent, id)
        
        self.Frame = self.GetTopLevelParent()
        self.parent = parent
        
        wx.EVT_LEFT_DOWN(self.Frame, self.HideItems)
        wx.EVT_LEFT_DOWN(parent, self.HideItems)
        
        # Locate textctrl for changing its bg/fg color
        self.bg = self.GetTextCtrl()
        
        wx.EVT_LEFT_DOWN(self.bg, self.HideItems)
        
        # Hide the List if textctrl loses focus
        wx.EVT_KILL_FOCUS(self.bg, self.HideItems)
        
        # Enable scrolling through list with up/down arrows
        wx.EVT_KEY_DOWN(self.bg, self.OnNavigate)
        
        # List to show when button pressed
        self.lb = wx.ListCtrl(self.parent, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL)
        self.lb.InsertColumn(0, '')
        for item in choices:
            self.lb.InsertStringItem(0, item)
        self.lb.Hide()
        
        # Select list item hovered by mouse
        wx.EVT_MOTION(self.lb, self.OnMouseOver)
        
        # Set the value of the textctrl when the mouse is clicked
        wx.EVT_LEFT_DOWN(self.lb, self.OnSelect)
        
        # If value argument is not blank, put string in textctrl
        self.SetValue(value)
    
    def PlaceList(self):
        # Lines the list up with the ComboCtrl
        
        # Make the list the same size as the ComboCtrl
        width = self.bg.GetSize()[0]
        self.lb.SetColumnWidth(0, width)
        self.lb.SetSize((width+23, 250)) # Makes the list flush with ComboCtrl
        
        # Place the list under the ComboBox
        cbpos = self.GetPosition()
        cbsize = self.GetSize()
        x = cbpos[0]
        y = cbpos[1] + cbsize[1]
        self.lb.SetPosition((x,y))
    
    def OnButtonClick(self):
        # Make sure that textctrl gets focus when button pressed
        self.bg.SetFocus()
        
        # Hide the list if it is already shown and do nothing else
        if self.lb.IsShown():
            self.lb.Hide()
        
        else:
            # Align list with ComboCtrl
            self.PlaceList()
            
            # Show the list
            self.lb.Show()
    
    def OnMouseOver(self, event):
        # Highlight the item hovered by mouse
        item = self.lb.HitTest(event.GetPosition()) # Returns a tuple so use "item[0]"
        self.lb.Select(item[0])
        event.Skip()
    
    def OnNavigate(self, event):
        # Make sure the list is in the right spot
        self.PlaceList()
        
        # Enable scrolling through list with up/down arrows
        key = event.GetKeyCode()
        cur_item = self.lb.GetFocusedItem()
        if key == 317:
            if self.lb.IsShown() == False:
                self.lb.Show()
            else:
                self.lb.Select(cur_item+1)
        elif key == 315 and cur_item > 0:
            self.lb.Select(cur_item-1)
        
        # Use "Enter" or "Return" keys to set TextCtrl as well
        elif key == wx.WXK_RETURN or key == wx.WXK_NUMPAD_ENTER:
            if self.lb.IsShown():
                self.OnSelect(None)
            else:
                self.lb.Show()
        
        event.Skip()
    
    def OnSelect(self, event):
        # Put the selected text in the txtctrl and hide the list
        self.SetValue(self.lb.GetItemText(self.lb.GetFocusedItem()))
        self.lb.Hide()
        # Give focus back to TextCtrl
        self.bg.SetFocus()
        self.bg.SetInsertionPointEnd()
    
    def HideItems(self, event):
        # Hide the list if it visible
        if self.lb.IsShown():
            self.lb.Hide()
        event.Skip()
    
    def SetValue(self, value):
        # Sets the text in the TextCtrl
        self.bg.SetValue(value)
    
    def SetBackgroundColour(self, color):
        self.bg.SetBackgroundColour(color)
        self.lb.SetBackgroundColour(color)
    
    def GetBackgroundColour(self):
        return self.bg.GetBackgroundColour()
    
    def SetForegroundColour(self, color):
        self.bg.SetForegroundColour(color)
        self.lb.SetForegroundColour(color)
    
    def GetForegroundColour(self):
        return self.bg.GetForegroundColour()
    
    def Clear(self):
        self.bg.Clear()
