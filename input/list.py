# -*- coding: utf-8 -*-

## \package input.list

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from fields.ifield      import InputField
from input.essential    import EssentialField
from ui.layout          import BoxSizer
from ui.panel           import BorderedPanel
from ui.panel           import ControlPanel


## A list control with no border
class ListCtrlBase(wx.ListView, ListCtrlAutoWidthMixin, InputField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr,
            defaultValue=None, required=False, outLabel=None):
        
        wx.ListView.__init__(self, parent, win_id, pos, size, style|wx.BORDER_NONE,
                validator, name)
        ListCtrlAutoWidthMixin.__init__(self)
        InputField.__init__(self, defaultValue, required, outLabel)
        
        self.clr_enabled = self.GetBackgroundColour()
        self.clr_disabled = parent.GetBackgroundColour()
        
        if not self.GetColumnCount() and self.WindowStyleFlag & wx.LC_REPORT:
            self.InsertColumn(0)
        
        # *** Event Handling *** #
        
        wx.EVT_KEY_DOWN(self, self.OnSelectAll)
    
    
    ## Add items to end of list
    #
    #  \param items
    #    String item or string items list
    def AppendStringItem(self, items):
        if items:
            row_index = self.GetItemCount()
            if isinstance(items, (unicode, str)):
                self.InsertStringItem(row_index, items)
            
            elif isinstance(items, (tuple, list)):
                self.InsertStringItem(row_index, items[0])
                
                if len(items) > 1:
                    column_index = 0
                    for I  in items[1:]:
                        column_index += 1
                        self.SetStringItem(row_index, column_index, I)
    
    
    ## Disables the list control
    def Disable(self, *args, **kwargs):
        self.SetBackgroundColour(self.clr_disabled)
        
        return wx.ListView.Disable(self, *args, **kwargs)
    
    
    ## Enables/Disables the list control
    def Enable(self, *args, **kwargs):
        if args[0]:
            self.SetBackgroundColour(self.clr_enabled)
        
        else:
            self.SetBackgroundColour(self.clr_disabled)
        
        return wx.ListView.Enable(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def GetSelectedIndexes(self):
        selected_indexes = []
        selected = None
        for X in range(self.GetSelectedItemCount()):
            if X == 0:
                selected = self.GetFirstSelected()
            
            else:
                selected = self.GetNextSelected(selected)
            
            selected_indexes.append(selected)
        
        if selected_indexes:
            return tuple(sorted(selected_indexes))
        
        return None
    
    
    ## Retrieve a tuple list of contents
    def GetListTuple(self, col=0, typeTuple=True):
        items = []
        
        for INDEX in range(self.GetItemCount()):
            items.append(self.GetItemText(INDEX, col))
        
        if typeTuple:
            return tuple(items)
        
        return items
    
    
    ## Override inherited method
    #
    #  Makes the 'title' argument optional
    def InsertColumn(self, index, title=wx.EmptyString, fmt=wx.LIST_FORMAT_LEFT,
                width=wx.LIST_AUTOSIZE):
        
        return wx.ListView.InsertColumn(self, index, title, fmt, width)
    
    
    ## TODO: Doxygen
    def OnSelectAll(self, event=None):
        select_all = False
        if isinstance(event, wx.KeyEvent):
            if event.GetKeyCode() == 65 and event.GetModifiers() == 2:
                select_all = True
        
        if select_all:
            for X in range(self.GetItemCount()):
                self.Select(X)
        
        if event:
            event.Skip()
    
    
    ## Removes all selected rows in descending order
    def RemoveSelected(self):
        selected_indexes = self.GetSelectedIndexes()
        if selected_indexes != None:
            for index in reversed(selected_indexes):
                self.DeleteItem(index)
    
    
    ## TODO: Doxygen
    def SetSingleStyle(self, style, add=True):
        style_set = wx.ListView.SetSingleStyle(self, style, add)
        
        if not self.GetColumnCount() and self.WindowStyleFlag & wx.LC_REPORT:
            self.InsertColumn(0)
        
        return style_set


## ListCtrlBase that notifies main window to mark project dirty
class ListCtrlBaseESS(ListCtrlBase, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr,
            defaultValue=None, required=False, outLabel=None):
        
        ListCtrlBase.__init__(self, parent, win_id, pos, size, style, validator, name,
                defaultValue, required, outLabel)
        EssentialField.__init__(self)


## Hack to make list control border have rounded edges
class ListCtrl(BorderedPanel, ControlPanel):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr,
            defaultValue=None, required=False, outLabel=None):
        
        BorderedPanel.__init__(self, parent, win_id, pos, size, name=name)
        
        if isinstance(self, EssentialField):
            self.MainCtrl = ListCtrlBaseESS(self, style=style, validator=validator,
                    defaultValue=defaultValue, required=required, outLabel=outLabel)
        
        else:
            self.MainCtrl = ListCtrlBase(self, style=style, validator=validator,
                    defaultValue=defaultValue, required=required, outLabel=outLabel)
        
        # Match panel background color to list control
        self.SetBackgroundColour(self.MainCtrl.GetBackgroundColour())
        
        self.layout_V1 = BoxSizer(wx.VERTICAL)
        self.layout_V1.Add(self.MainCtrl, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.layout_V1)
        self.Layout()
        
        if wx.MAJOR_VERSION == 3 and wx.MINOR_VERSION == 0:
            wx.EVT_SIZE(self, self.OnResize)
    
    
    ## TODO: Doxygen
    def AppendColumn(self, heading, fmt=wx.LIST_FORMAT_LEFT, width=-1):
        self.MainCtrl.AppendColumn(heading, fmt, width)
    
    
    ## TODO: Doxygen
    def AppendStringItem(self, items):
        self.MainCtrl.AppendStringItem(items)
    
    
    ## TODO: Doxygen
    def Arrange(self, flag=wx.LIST_ALIGN_DEFAULT):
        self.MainCtrl.Arrange(flag)
    
    
    ## TODO: Doxygen
    def ClearAll(self):
        self.MainCtrl.ClearAll()
    
    
    ## TODO: Doxygen
    def DeleteAllItems(self):
        self.MainCtrl.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def DeleteItem(self, item):
        self.MainCtrl.DeleteItem(item)
    
    
    ## Disables the panel & list control
    def Disable(self, *args, **kwargs):
        self.MainCtrl.Disable(*args, **kwargs)
        
        return BorderedPanel.Disable(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def EditLabel(self, item):
        self.MainCtrl.EditLabel(item)
    
    
    ## Enables/Disables the panel & list control
    def Enable(self, *args, **kwargs):
        self.MainCtrl.Enable(*args, **kwargs)
        
        return BorderedPanel.Enable(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def GetColumnCount(self):
        return self.MainCtrl.GetColumnCount()
    
    
    ## TODO: Doxygen
    def GetColumnWidth(self, col):
        return self.MainCtrl.GetColumnWidth(col)
    
    
    ## Retrieves number of files in list
    def GetCount(self):
        return self.GetItemCount()
    
    
    ## TODO: Doxygen
    def GetCountPerPage(self):
        return self.MainCtrl.GetCountPerPage()
    
    
    ## TODO: Doxygen
    def GetFirstSelected(self):
        return self.MainCtrl.GetFirstSelected()
    
    
    ## TODO: Doxygen
    def GetFocusedItem(self):
        return self.MainCtrl.GetFocusedItem()
    
    
    ## TODO: Doxygen
    def GetItem(self, row, col):
        return self.MainCtrl.GetItem(row, col)
    
    
    ## TODO: Doxygen
    def GetItemCount(self):
        return self.MainCtrl.GetItemCount()
    
    
    ## TODO: Doxygen
    def GetItemText(self, item, col=0):
        if wx.MAJOR_VERSION > 2:
            return self.MainCtrl.GetItemText(item, col)
        
        return self.MainCtrl.GetItem(item, col).GetText()
    
    
    ## TODO: Doxygen
    def GetItemTextColour(self, item):
        return self.MainCtrl.GetItemTextColour(item)
    
    
    ## TODO: Doxygen
    def GetListCtrl(self):
        return self.MainCtrl
    
    
    ## Retrieve a tuple list of contents
    def GetListTuple(self, col=0, typeTuple=True):
        return self.MainCtrl.GetListTuple(col, typeTuple)
    
    
    ## TODO: Doxygen
    def GetNextItem(self, item, geometry=wx.LIST_NEXT_ALL, state=wx.LIST_STATE_DONTCARE):
        return self.MainCtrl.GetNextItem(item, geometry, state)
    
    
    ## TODO: Doxygen
    def GetNextSelected(self, item):
        self.MainCtrl.GetNextSelected(item)
    
    
    ## TODO: Doxygen
    def GetPanelStyle(self, *args, **kwargs):
        return BorderedPanel.GetWindowStyle(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def GetPanelStyleFlag(self, *args, **kwargs):
        return BorderedPanel.GetWindowStyleFlag(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def GetSelectedIndexes(self):
        return self.MainCtrl.GetSelectedIndexes()
    
    
    ## TODO: Doxygen
    def GetSelectedItemCount(self):
        return self.MainCtrl.GetSelectedItemCount()
    
    
    ## TODO: Doxygen
    def GetWindowStyle(self):
        return self.MainCtrl.GetWindowStyle()
    
    
    ## TODO: Doxygen
    def GetWindowStyleFlag(self):
        return self.MainCtrl.GetWindowStyleFlag()
    
    
    ## TODO: Doxygen
    def HitTest(self, point, flags, ptrSubItem=None):
        return self.MainCtrl.HitTest(point, flags, ptrSubItem)
    
    
    ## TODO: Doxygen
    def InsertColumn(self, col, heading, fmt=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE):
        self.MainCtrl.InsertColumn(col, heading, fmt, width)
    
    
    ## TODO: Doxygen
    #
    #  FIXME: imageIndex unused; Unknown purpose, not documented
    def InsertStringItem(self, index, label, imageIndex=None):
        self.MainCtrl.InsertStringItem(index, label)
    
    
    ## Checks if field is required for building
    def IsRequired(self):
        return self.MainCtrl.IsRequired()
    
    
    ## Some bug workarounds for resizing the list & its columns in wx 3.0
    #
    #  The last column is automatically expanded to fill
    #    the remaining space.
    #  FIXME: Unknown if this bug persists in wx 3.1
    def OnResize(self, event=None):
        if (self.GetWindowStyleFlag()) & wx.LC_REPORT:
            # FIXME: -10 should be a dynamic number set by the sizer's padding
            self.SetSize(wx.Size(self.GetParent().Size[0] - 10, self.Size[1]))
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def RemoveSelected(self):
        self.MainCtrl.RemoveSelected()
    
    
    ## Resets the list to default values
    def Reset(self):
        return self.MainCtrl.Reset()
    
    
    ## TODO: Doxygen
    def SetColumnWidth(self, col, width):
        self.MainCtrl.SetColumnWidth(col, width)
        self.MainCtrl.Layout()
    
    
    ## TODO: Doxygen
    def SetItemBackgroundColour(self, item, color):
        self.MainCtrl.SetItemBackgroundColour(item, color)
    
    
    ## TODO: Doxygen
    def SetItemTextColour(self, item, color):
        self.MainCtrl.SetItemTextColour(item, color)
    
    
    ## TODO: Doxygen
    def SetPanelStyle(self, *args, **kwargs):
        return BorderedPanel.SetWindowStyle(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def SetPanelStyleFlag(self, *args, **kwargs):
        return BorderedPanel.SetWindowStyleFlag(self, *args, **kwargs)
    
    
    ## TODO: Doxygen
    def SetSingleStyle(self, *args, **kwargs):
        self.MainCtrl.SetSingleStyle(*args, **kwargs)
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: imageId unused; Unknown purpose, not documented
    def SetStringItem(self, index, col, label, imageId=None):
        self.MainCtrl.SetStringItem(index, col, label)
    
    
    ## TODO: Doxygen
    def SetWindowStyle(self, *args, **kwargs):
        return self.MainCtrl.SetWindowStyle(*args, **kwargs)
    
    
    ## TODO: Doxygen
    def SetWindowStyleFlag(self, *args, **kwargs):
        return self.MainCtrl.SetWindowStyleFlag(*args, **kwargs)


## ListCtrl that notifies main window to mark project dirty
class ListCtrlESS(ListCtrl, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr,
            defaultValue=None, required=False, outLabel=None):
        
        ListCtrl.__init__(self, parent, win_id, pos, size, style, validator, name,
                defaultValue, required, outLabel)
        EssentialField.__init__(self)
