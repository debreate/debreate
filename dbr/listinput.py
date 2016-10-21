# -*- coding: utf-8 -*-

## \package dbr.listinput

# MIT licensing
# See: docs/LICENSE.txt


import wx


## A list control with no border
class ListCtrl(wx.ListCtrl):
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, wx.BORDER_NONE|style,
                validator, name)


## Hack to make list control border have rounded edges
class ListCtrlPanel(wx.Panel):
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
        wx.Panel.__init__(self, parent, ID, pos, size, wx.TAB_TRAVERSAL|wx.BORDER_THEME,
                name)
        
        self.listarea = ListCtrl(self, style=style, validator=validator)
        
        # Match panel background color to list control
        self.SetBackgroundColour(self.listarea.GetBackgroundColour())
        
        self.layout_V1 = wx.BoxSizer(wx.VERTICAL)
        self.layout_V1.Add(self.listarea, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.layout_V1)
        self.Layout()
    
    
    def AppendColumn(self, heading, fmt=wx.LIST_FORMAT_LEFT, width=-1):
        self.listarea.AppendColumn(heading, fmt, width)
    
    
    def Arrange(self, flag=wx.LIST_ALIGN_DEFAULT):
        self.listarea.Arrange(flag)
    
    
    def ClearAll(self):
        self.listarea.ClearAll()
    
    
    def DeleteAllItems(self):
        self.listarea.DeleteAllItems()
    
    
    def DeleteItem(self, item):
        self.listarea.DeleteItem(item)
    
    
    def EditLabel(self, item):
        self.listarea.EditLabel(item)
    
    
    def GetColumnCount(self):
        return self.listarea.GetColumnCount()
    
    
    def GetColumnWidth(self, col):
        return self.listarea.GetColumnWidth(col)
    
    
    def GetCountPerPage(self):
        return self.listarea.GetCountPerPage()
    
    
    def GetFirstSelected(self):
        return self.listarea.GetFirstSelected()
    
    
    def GetItem(self, row, col):
        return self.listarea.GetItem(row, col)
    
    
    def GetItemCount(self):
        return self.listarea.GetItemCount()
    
    
    def GetItemText(self, item, col=0):
        return self.listarea.GetItemText(item, col)
    
    
    def GetNextItem(self, item, geometry=wx.LIST_NEXT_ALL, state=wx.LIST_STATE_DONTCARE):
        return self.listarea.GetNextItem(item, geometry, state)
    
    
    def GetSelectedItemCount(self):
        return self.listarea.GetSelectedItemCount()
    
    
    def HitTest(self, point, flags, ptrSubItem=None):
        return self.listarea.HitTest(point, flags, ptrSubItem)
    
    
    def InsertColumn(self, col, heading, fmt=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE):
        self.listarea.InsertColumn(col, heading, fmt, width)
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: imageIndex unused; Unknown purpose, not documented
    def InsertStringItem(self, index, label, imageIndex=None):
        self.listarea.InsertStringItem(index, label)
    
    
    def SetColumnWidth(self, col, width):
        self.listarea.SetColumnWidth(col, width)
        self.listarea.Layout()
    
    
    def SetItemBackgroundColour(self, item, color):
        self.listarea.SetItemBackgroundColour(item, color)
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: imageId unused; Unknown purpose, not documented
    def SetStringItem(self, index, col, label, imageId=None):
        self.listarea.SetStringItem(index, col, label)
