# -*- coding: utf-8 -*-

## \package input.list

# MIT licensing
# See: docs/LICENSE.txt


import os, wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import TextEditMixin

from dbr.colors             import COLOR_warn
from dbr.language           import GT
from dbr.log                import Logger
from globals.constants      import FTYPE_EXE
from globals.constants      import file_types_defs
from globals.paths          import ConcatPaths
from globals.wizardhelper   import GetMainWindow
from input.essential        import EssentialField
from input.ifield           import InputField
from ui.layout              import BoxSizer
from ui.panel               import BorderedPanel
from ui.panel               import ControlPanel


## A list control with no border
class ListCtrlBase(wx.ListView, ListCtrlAutoWidthMixin, InputField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr,
            defaultValue=None):
        
        wx.ListView.__init__(self, parent, win_id, pos, size, style|wx.BORDER_NONE,
                validator, name)
        ListCtrlAutoWidthMixin.__init__(self)
        InputField.__init__(self, defaultValue)
        
        self.clr_enabled = self.GetBackgroundColour()
        self.clr_disabled = parent.GetBackgroundColour()
        
        if not self.GetColumnCount() and self.WindowStyleFlag & wx.LC_REPORT:
            self.InsertColumn(0)
        
        # *** Event Handling *** #
        
        wx.EVT_KEY_DOWN(self, self.OnSelectAll)
    
    
    ## Add items to end of list
    #  
    #  \param items
    #        String item or string items list
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
    
    
    ## Override inherited method to post list event for EssentialField instances
    def SetStringItem(self, *args, **kwargs):
        string_set = wx.ListView.SetStringItem(self, *args, **kwargs)
        
        # FIXME: Not sure why this check is necessary here.
        #        Without, sets project dirty at load time.
        if GetMainWindow().ProjectIsLoaded():
            # Cause EssentialField instances to emit event that will tell main window to mark paroject dirty
            if isinstance(self, EssentialField) or isinstance(self.Parent, EssentialField):
                Logger.Debug(__name__, u'EssentialField instance posting list event')
                
                wx.PostEvent(self, wx.CommandEvent(wx.wxEVT_COMMAND_LIST_END_LABEL_EDIT))
        
        return string_set


## ListCtrlBase that notifies main window to mark project dirty
class ListCtrlBaseESS(ListCtrlBase, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
        
        ListCtrlBase.__init__(self, parent, win_id, pos, size, style, validator, name)
        EssentialField.__init__(self)


## Hack to make list control border have rounded edges
class ListCtrl(BorderedPanel, ControlPanel):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
        
        BorderedPanel.__init__(self, parent, win_id, pos, size, name=name)
        
        if isinstance(self, EssentialField):
            self.MainCtrl = ListCtrlBaseESS(self, style=style, validator=validator)
        
        else:
            self.MainCtrl = ListCtrlBase(self, style=style, validator=validator)
        
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
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
        
        ListCtrl.__init__(self, parent, win_id, pos, size, style, validator, name)
                #essential=True)
        EssentialField.__init__(self)


## An editable list
#  
#  Creates a ListCtrl class in which every column's text can be edited
class FileList(ListCtrl, TextEditMixin, wx.FileDropTarget):
    def __init__(self, parent, win_id=wx.ID_ANY, name=wx.ListCtrlNameStr):
        ListCtrl.__init__(self, parent, win_id, style=wx.LC_REPORT, name=name)
        TextEditMixin.__init__(self)
        wx.FileDropTarget.__init__(self)
        
        ListCtrl.SetDropTarget(self, self)
        
        self.DEFAULT_BG_COLOR = self.GetBackgroundColour()
        self.DEFAULT_TEXT_COLOR = self.GetForegroundColour()
        self.FOLDER_TEXT_COLOR = wx.BLUE
        
        self.filename_col = 0
        self.source_col = 1
        self.target_col = 2
        self.type_col = 3
        
        # FIXME: Way to do this dynamically?
        col_width = 150  # self.GetSize()[0] / 4
        
        self.InsertColumn(self.filename_col, GT(u'File'), width=col_width)
        self.InsertColumn(self.source_col, GT(u'Source Directory'), width=col_width)
        self.InsertColumn(self.target_col, GT(u'Staged Target'), width=col_width)
        # Last column is automatcially stretched to fill remaining size
        self.InsertColumn(self.type_col, GT(u'File Type'))
        
        # Legacy versions of wx don't set sizes correctly in constructor
        if wx.MAJOR_VERSION < 3:
            for col in range(3):
                if col == 0:
                    self.SetColumnWidth(col, 100)
                    continue
                
                self.SetColumnWidth(col, 200)
        
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)
        
        # Resize bug hack
        if wx.MAJOR_VERSION == 3 and wx.MINOR_VERSION == 0:
            wx.EVT_SIZE(self, self.OnResize)
    
    
    ## TODO: Doxygen
    #  
    #  \param filename
    #        \b \e unicode|str : Basename of file
    #  \param source_dir
    #        \b \e unicode|str : Directory where file is located
    #  \param target_dir
    #        \b \e unicode|str : Target directory where file will ultimately be installed
    #  \param executable
    #        \b \e bool : Whether or not the file should be marked as executable
    #  \return
    #        \b \e bool : True if file exists on the filesystem
    def AddFile(self, filename, source_dir, target_dir=None, executable=False):
        list_index = self.GetItemCount()
        
        # Method can be called with two argements: absolute filename & target directory
        if target_dir == None:
            target_dir = source_dir
            source_dir = os.path.dirname(filename)
            filename = os.path.basename(filename)
        
        source_path = ConcatPaths((source_dir, filename))
        
        Logger.Debug(__name__, GT(u'Adding file: {}').format(source_path))
        
        self.InsertStringItem(list_index, filename)
        self.SetStringItem(list_index, self.source_col, source_dir)
        self.SetStringItem(list_index, self.target_col, target_dir)
        
        if os.path.isdir(source_path):
            self.SetItemTextColour(list_index, self.FOLDER_TEXT_COLOR)
        
        else:
            # TODO: Use 'GetFileMimeType' module to determine file type
            if os.access(source_path, os.X_OK) or executable:
                self.SetFileExecutable(list_index)
            
            if not os.path.isfile(source_path):
                self.SetItemBackgroundColour(list_index, COLOR_warn)
                
                # File was added but does not exist on filesystem
                return False
        
        return True
    
    
    ## Retrieves is the item at 'i_index' is executable
    #  
    #  \param i_index
    #        \b \e int : The list row to check
    def FileIsExecutable(self, i_index):
        return self.GetItemText(i_index, self.type_col) == file_types_defs[FTYPE_EXE]
    
    
    ## TODO: Doxygen
    def DeleteAllItems(self):
        ListCtrl.DeleteAllItems(self)
    
    
    ## TODO: Doxygen
    #  
    #  \param i_index
    #        \b \e int : The list row
    def GetFilename(self, i_index):
        return self.GetItemText(i_index)
    
    
    ## TODO: Doxygen
    def GetRowData(self, row):
        filename = self.GetFilename(row)
        source_dir = self.GetSource(row)
        target_dir = self.GetTarget(row)
        executable = self.FileIsExecutable(row)
        
        return (filename, source_dir, target_dir, executable)
    
    
    ## TODO: Doxygen
    def GetRowDefs(self, row):
        row_data = self.GetRowData(row)
        
        row_defs = {
            u'filename': row_data[0],
            u'source': row_data[1],
            u'target': row_data[2],
            u'executable': row_data[3],
        }
        
        return row_defs
    
    
    ## TODO: Doxygen
    #  
    #  \param i_index
    #        \b \e int : List row
    def GetSource(self, i_index):
        return self.GetItemText(i_index, self.source_col)
    
    
    ## TODO: Doxygen
    def GetTarget(self, i_index):
        return self.GetItemText(i_index, self.target_col)
    
    
    ## Checks if the file list is empty
    def IsEmpty(self):
        return not self.GetItemCount()
    
    
    ## TODO: Doxygen
    def MissingFiles(self):
        return self.RefreshFileList()
    
    
    ## Action to take when a file/folder is dropped onto the list from a file manager
    def OnDropFiles(self, x, y, filename):
        self.GetParent().OnDropFiles(filename)
    
    
    ## Defines actions to take when left-click or left-double-click event occurs
    #  
    #  The super method is overridden to ensure that 'event.Skip' is called.
    #  TODO: Notify wxPython project of 'event.Skip' error
    def OnLeftDown(self, event=None):
        TextEditMixin.OnLeftDown(self, event=None)
        
        if event:
            event.Skip()
    
    
    ## Works around resize bug in wx 3.0
    #  
    #  Uses parent width & its children to determine
    #    desired width.
    #  FIXME: Unknown if this bug persists in wx 3.1
    #  FIXME: Do not override, should be inherited from ListCtrl
    def OnResize(self, event=None):
        if event:
            event.Skip(True)
        
        parent = self.GetParent()
        
        width = self.GetSize()
        height = width[1]
        width = width[0]
        
        # Use the parent window & its children to determine desired width
        target_width = parent.GetSize()[0] - parent.GetDirTreePanel().GetSize()[0] - 15
        
        if width > 0 and target_width > 0:
            if width != target_width:
                
                Logger.Debug(__name__,
                        GT(u'File list failed to resize. Forcing manual resize to target width: {}').format(target_width))
                
                self.SetSize(wx.Size(target_width, height))
    
    
    ## Opens an editor for target
    #  
    #  The super method is overridden to only
    #  allow editing the "target" column.
    #  
    #  \param col
    #    \b \e int : Column received from the
    #                event (replaced with "target" column)
    #  \param row
    #    \b \e int : Row index to be edited
    def OpenEditor(self, col, row):
        TextEditMixin.OpenEditor(self, self.target_col, row)
    
    
    ## Refresh file list
    #  
    #  Missing files are marked with a distinct color.
    #  TODO: Update executable status
    #  \return
    #        \b \e bool : True if files are missing, False if all okay
    def RefreshFileList(self):
        dirty = False
        for row in range(self.GetItemCount()):
            item_color = self.DEFAULT_BG_COLOR
            executable = False
            row_defs = self.GetRowDefs(row)
            
            absolute_filename = u'{}/{}'.format(row_defs[u'source'], row_defs[u'filename'])
            
            if os.path.isdir(absolute_filename):
                self.SetItemTextColour(row, self.FOLDER_TEXT_COLOR)
            
            else:
                if not os.path.isfile(absolute_filename):
                    item_color = COLOR_warn
                    dirty = True
                
                self.SetItemBackgroundColour(row, item_color)
                
                if os.access(absolute_filename, os.X_OK):
                    executable = True
                
                self.SetFileExecutable(row, executable)
        
        return dirty
    
    
    ## Removes selected files from list
    def RemoveSelected(self):
        selected_total = self.GetSelectedItemCount()
        selected_count = selected_total
        
        while selected_count:
            current_selected = self.GetFirstSelected()
            
            Logger.Debug(__name__,
                    GT(u'Removing selected item {} of {}'.format(selected_total - selected_count + 1,
                                                                          selected_total
                                                                          )))
            
            self.DeleteItem(current_selected)
            selected_count = self.GetSelectedItemCount()
    
    
    ## TODO: Doxygen
    def SelectAll(self):
        file_count = self.GetItemCount()
        
        for x in range(file_count):
            self.Select(x)
    
    
    ## Marks a file as executable
    #  
    #  \param row
    #        \b \e int : Row to change
    def SetFileExecutable(self, row, executable=True):
        if executable:
            self.SetStringItem(row, self.type_col, file_types_defs[FTYPE_EXE])
            self.SetItemTextColour(row, wx.RED)
            
            return
        
        # FIXME: Delete item rather than setting to wx.EmptyString???
        self.SetStringItem(row, self.type_col, wx.EmptyString)
        self.SetItemTextColour(row, self.DEFAULT_TEXT_COLOR)
    
    
    ## Sorts listed items in target column alphabetially
    #  
    #  TODO: Sort listed items
    def Sort(self):
        pass
    
    
    ## Toggles executable flag for selected list items
    #  
    #  TODO: Define & execute with context menu
    def ToggleExecutable(self):
        pass


## FileList that notifies main window to mark project dirty
class FileListESS(FileList, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, name=wx.ListCtrlNameStr):
        FileList.__init__(self, parent, win_id, name) #, essential=True)
        EssentialField.__init__(self)
