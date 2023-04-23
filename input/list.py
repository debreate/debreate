
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module input.list

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from fields.ifield   import InputField
from input.essential import EssentialField
from ui.layout       import BoxSizer
from ui.panel        import BorderedPanel
from ui.panel        import ControlPanel


## A list control with no border.
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

    # *** Event Handling *** #

    self.Bind(wx.EVT_KEY_DOWN, self.OnSelectAll)

  ## Add items to end of list.
  #
  #  @param items
  #    String item or string items list.
  def AppendStringItem(self, items):
    if items:
      row_index = self.GetItemCount()
      if isinstance(items, str):
        self.InsertItem(row_index, items)

      elif isinstance(items, (tuple, list)):
        self.InsertItem(row_index, items[0])

        if len(items) > 1:
          column_index = 0
          for I  in items[1:]:
            column_index += 1
            self.SetItem(row_index, column_index, I)

  ## Disables the list control.
  def Disable(self, *args, **kwargs):
    self.SetBackgroundColour(self.clr_disabled)
    return wx.ListView.Disable(self, *args, **kwargs)

  ## Enables/Disables the list control.
  def Enable(self, *args, **kwargs):
    if args[0]:
      self.SetBackgroundColour(self.clr_enabled)
    else:
      self.SetBackgroundColour(self.clr_disabled)
    return wx.ListView.Enable(self, *args, **kwargs)

  ## Retrieves the string label of a given column
  def GetColumnLabel(self, col):
    return self.GetColumn(col).GetText()

  ## Retrieves labels for all columns.
  #
  #  @return
  #    <b><i>String</i></b> list of all column labels.
  def GetColumnLabels(self):
    labels = []

    for COL in range(self.GetColumnCount()):
      labels.append(self.GetColumnLabel(COL))

    return labels

  ## @todo Doxygen
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

  ## Retrieve a tuple list of contents.
  def GetListTuple(self, col=0, typeTuple=True):
    items = []
    for INDEX in range(self.GetItemCount()):
      items.append(self.GetItemText(INDEX, col))
    if typeTuple:
      return tuple(items)
    return items

  ## Override inherited method.
  #
  #  Makes the 'title' argument optional.
  def InsertColumn(self, index, title=wx.EmptyString, fmt=wx.LIST_FORMAT_LEFT,
        width=wx.LIST_AUTOSIZE):
    return wx.ListView.InsertColumn(self, index, title, fmt, width)

  ## @todo Doxygen
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

  ## Removes all selected rows in descending order.
  def RemoveSelected(self):
    selected_indexes = self.GetSelectedIndexes()
    if selected_indexes != None:
      for index in reversed(selected_indexes):
        if index < 0:
          # don't try to delete indexes that don't exist
          continue
        self.DeleteItem(index)

  ## @todo Doxygen
  def SetSingleStyle(self, style, add=True):
    style_set = wx.ListView.SetSingleStyle(self, style, add)

    if not self.GetColumnCount() and self.WindowStyleFlag & wx.LC_REPORT:
      self.InsertColumn(0)

    return style_set

  ## Sets the string label for a given column.
  def SetColumnLabel(self, col, label):
    col_info = self.GetColumn(col)
    col_info.SetText(label)

    return self.SetColumn(col, col_info)

  ## Sets list's column count & labels.
  #
  #  @param labels
  #    List of string labels for column headers.
  #  @param colWidth
  #    <b><i>Integer</b></i> width of each column.
  def SetColumns(self, labels, colWidth):
    # Remove previous columns
    self.DeleteAllColumns()

    cols = range(len(labels))
    for INDEX in cols:
      if INDEX == cols[-1]:
        # Last column fills remaining space
        self.InsertColumn(INDEX, labels[INDEX])

        continue

      self.InsertColumn(INDEX, labels[INDEX], width=colWidth)

## ListCtrlBase that notifies main window to mark project dirty.
#
#  This is a dummy class to facilitate merging to & from unstable branch.
class ListCtrlBaseESS(ListCtrlBase, EssentialField):
  def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
      style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr,
      defaultValue=None, required=False, outLabel=None):

    ListCtrlBase.__init__(self, parent, win_id, pos, size, style, validator, name,
        defaultValue, required, outLabel)
    EssentialField.__init__(self)

## Hack to make list control border have rounded edges.
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

  ## @todo Doxygen
  def AppendColumn(self, heading, fmt=wx.LIST_FORMAT_LEFT, width=-1):
    self.MainCtrl.AppendColumn(heading, fmt, width)

  ## @todo Doxygen
  def AppendStringItem(self, items):
    self.MainCtrl.AppendStringItem(items)

  ## @todo Doxygen
  def Arrange(self, flag=wx.LIST_ALIGN_DEFAULT):
    self.MainCtrl.Arrange(flag)

  ## @todo Doxygen
  def ClearAll(self):
    self.MainCtrl.ClearAll()

  ## Removes all columns from the main control.
  #
  #  @return
  #    ListCtrlBase.DeleteAllColumns.
  def DeleteAllColumns(self):
    return self.MainCtrl.DeleteAllColumns()

  ## @todo Doxygen
  def DeleteAllItems(self):
    return self.MainCtrl.DeleteAllItems()

  ## @todo Doxygen
  def DeleteItem(self, item):
    return self.MainCtrl.DeleteItem(item)

  ## Disables the panel & list control
  def Disable(self, *args, **kwargs):
    self.MainCtrl.Disable(*args, **kwargs)
    return BorderedPanel.Disable(self, *args, **kwargs)

  ## @todo Doxygen
  def EditLabel(self, item):
    self.MainCtrl.EditLabel(item)

  ## Enables/Disables the panel & list control.
  def Enable(self, *args, **kwargs):
    self.MainCtrl.Enable(*args, **kwargs)
    return BorderedPanel.Enable(self, *args, **kwargs)

  ## @todo Doxygen
  def GetColumnCount(self):
    return self.MainCtrl.GetColumnCount()

  ## Retrieves the string label of a given column
  def GetColumnLabel(self, col):
    return self.MainCtrl.GetColumnLabel(col)

  ## Retrieves labels for all columns.
  #
  #  @return
  #    <b><i>String</i></b> list of all column labels.
  def GetColumnLabels(self):
    return self.MainCtrl.GetColumnLabels()

  ## @todo Doxygen
  def GetColumnWidth(self, col):
    return self.MainCtrl.GetColumnWidth(col)

  ## Retrieves number of files in list
  def GetCount(self):
    return self.GetItemCount()

  ## @todo Doxygen
  def GetCountPerPage(self):
    return self.MainCtrl.GetCountPerPage()

  ## @todo Doxygen
  def GetFirstSelected(self):
    return self.MainCtrl.GetFirstSelected()

  ## @todo Doxygen
  def GetFocusedItem(self):
    return self.MainCtrl.GetFocusedItem()

  ## @todo Doxygen
  def GetItem(self, row, col):
    return self.MainCtrl.GetItem(row, col)

  ## @todo Doxygen
  def GetItemCount(self):
    return self.MainCtrl.GetItemCount()

  ## @todo Doxygen
  def GetItemText(self, item, col=0):
    if wx.MAJOR_VERSION > 2:
      return self.MainCtrl.GetItemText(item, col)
    return self.MainCtrl.GetItem(item, col).GetText()

  ## @todo Doxygen
  def GetItemTextColour(self, item):
    return self.MainCtrl.GetItemTextColour(item)

  ## @todo Doxygen
  def GetListCtrl(self):
    return self.MainCtrl

  ## Retrieve a tuple list of contents
  def GetListTuple(self, col=0, typeTuple=True):
    return self.MainCtrl.GetListTuple(col, typeTuple)

  ## @todo Doxygen
  def GetNextItem(self, item, geometry=wx.LIST_NEXT_ALL, state=wx.LIST_STATE_DONTCARE):
    return self.MainCtrl.GetNextItem(item, geometry, state)

  ## @todo Doxygen
  def GetNextSelected(self, item):
    self.MainCtrl.GetNextSelected(item)

  ## @todo Doxygen
  def GetPanelStyle(self, *args, **kwargs):
    return BorderedPanel.GetWindowStyle(self, *args, **kwargs)

  ## @todo Doxygen
  def GetPanelStyleFlag(self, *args, **kwargs):
    return BorderedPanel.GetWindowStyleFlag(self, *args, **kwargs)

  ## @todo Doxygen
  def GetSelectedIndexes(self):
    return self.MainCtrl.GetSelectedIndexes()

  ## @todo Doxygen
  def GetSelectedItemCount(self):
    return self.MainCtrl.GetSelectedItemCount()

  ## @todo Doxygen
  def GetWindowStyle(self):
    return self.MainCtrl.GetWindowStyle()

  ## @todo Doxygen
  def GetWindowStyleFlag(self):
    return self.MainCtrl.GetWindowStyleFlag()

  ## @todo Doxygen
  def HitTest(self, point, flags, ptrSubItem=None):
    return self.MainCtrl.HitTest(point, flags, ptrSubItem)

  ## @todo Doxygen
  def InsertColumn(self, col, heading, fmt=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE):
    self.MainCtrl.InsertColumn(col, heading, fmt, width)

  ## @todo Doxygen
  #  @todo
  #    FIXME: imageIndex unused; Unknown purpose, not documented
  def InsertStringItem(self, index, label, imageIndex=None):
    self.MainCtrl.InsertItem(index, label)

  ## Checks if field is required for building.
  def IsRequired(self):
    return self.MainCtrl.IsRequired()

  ## Some bug workarounds for resizing the list & its columns in wx 3.0.
  #
  #  The last column is automatically expanded to fill.
  #  the remaining space.
  #
  #  @todo
  #    FIXME: Unknown if this bug persists in wx 3.1
  def OnResize(self, event=None):
    if (self.GetWindowStyleFlag()) & wx.LC_REPORT:
      # FIXME: -10 should be a dynamic number set by the sizer's padding
      self.SetSize(wx.Size(self.GetParent().GetSize().Width - 10, self.GetSize().Height))

    if event:
      event.Skip()

  ## @todo Doxygen
  def RemoveSelected(self):
    self.MainCtrl.RemoveSelected()

  ## Resets the list to default values.
  def Reset(self):
    return self.MainCtrl.Reset()

  ## Sets the string label for a given column.
  def SetColumnLabel(self, col, label):
    return self.MainCtrl.SetColumnLabel(col, label)

  ## Sets list's column count & labels.
  #
  #  @param labels
  #    List of string labels for column headers.
  #  @param colWidth
  #    <b><i>Integer</b></i> width of each column.
  def SetColumns(self, labels, colWidth):
    return self.MainCtrl.SetColumns(labels, colWidth)

  ## @todo Doxygen
  def SetColumnWidth(self, col, width):
    self.MainCtrl.SetColumnWidth(col, width)
    self.MainCtrl.Layout()

  ## @todo Doxygen
  def SetItemBackgroundColour(self, item, color):
    self.MainCtrl.SetItemBackgroundColour(item, color)

  ## @todo Doxygen
  def SetItemTextColour(self, item, color):
    self.MainCtrl.SetItemTextColour(item, color)

  ## @todo Doxygen
  def SetPanelStyle(self, *args, **kwargs):
    return BorderedPanel.SetWindowStyle(self, *args, **kwargs)

  ## @todo Doxygen
  def SetPanelStyleFlag(self, *args, **kwargs):
    return BorderedPanel.SetWindowStyleFlag(self, *args, **kwargs)

  ## @todo Doxygen
  def SetSingleStyle(self, *args, **kwargs):
    self.MainCtrl.SetSingleStyle(*args, **kwargs)

  ## @todo Doxygen
  #  @todo
  #    FIXME: imageId unused; Unknown purpose, not documented
  def SetStringItem(self, index, col, label, imageId=None):
    self.MainCtrl.SetItem(index, col, label)

  ## @todo Doxygen
  def SetWindowStyle(self, *args, **kwargs):
    return self.MainCtrl.SetWindowStyle(*args, **kwargs)

  ## @todo Doxygen
  def SetWindowStyleFlag(self, *args, **kwargs):
    return self.MainCtrl.SetWindowStyleFlag(*args, **kwargs)

## ListCtrl that notifies main window to mark project dirty.
#
#  This is a dummy class to facilitate merging to & from unstable branch.
class ListCtrlESS(ListCtrl, EssentialField):
  def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
      style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr,
      defaultValue=None, required=False, outLabel=None):

    ListCtrl.__init__(self, parent, win_id, pos, size, style, validator, name,
        defaultValue, required, outLabel)
    EssentialField.__init__(self)
