# -*- coding: utf-8 -*-

## \package input.list

# MIT licensing
# See: docs/LICENSE.txt


import os, wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import TextEditMixin

from dbr.colors         import COLOR_warn
from dbr.language       import GT
from dbr.log            import Logger
from globals.fileio     import FileItem
from globals.paths      import ConcatPaths
from globals.strings    import IsString
from input.essential    import EssentialField
from input.ifield       import InputField
from ui.layout          import BoxSizer
from ui.panel           import BorderedPanel
from ui.panel           import ControlPanel


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


## ListCtrlBase that notifies main window to mark project dirty
#
#  This is a dummy class to facilitate merging to & from unstable branch
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
#
#  This is a dummy class to facilitate merging to & from unstable branch
class ListCtrlESS(ListCtrl, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
        
        ListCtrl.__init__(self, parent, win_id, pos, size, style, validator, name)
        EssentialField.__init__(self)


## List control intended for managing files
#
#  TODO: Derive FileList from this
#
#  \param hlExex
#    If \b \e True, will highlight executable files with red text
class BasicFileList(ListCtrl):
    def __init__(self, parent, win_id=wx.ID_ANY, hlExes=False, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.LC_ICON|wx.LC_REPORT|wx.LC_NO_HEADER,
            name=wx.ListCtrlNameStr):
        
        ListCtrl.__init__(self, parent, win_id, pos, size, style, name=name)
        
        self.HLExes = hlExes
        
        ## List of globals.fileio.FileItem instances
        self.Files = []
    
    
    ## Adds new globals.fileio.FileItem instance to end of list
    #
    #  \param item
    #    Either the path to a file or a FileItem instance
    #  \param target
    #    File's target installation directory (only if item is not FileItem instance)
    #  \return
    #    \b \e True if successfully added to list
    def Add(self, item, target=None):
        return self.Insert(self.GetCount(), item, target)
    
    
    ## Appends new globals.fileio.FileItem instance to end of list
    #
    #  Alias of input.list.BasicFileList.Add
    #  
    #  \param item
    #    Either the path to a file or a FileItem instance
    #  \param target
    #    File's target installation directory (only if item is not FileItem instance)
    #  \return
    #    \b \e True if successfully added to list
    def Append(self, item, target=None):
        return self.Add(item, target)
    
    
    ## Deletes an item from the file list
    #
    #  \param item
    #    Can be integer index, file path string, or FileItem instance
    #  \return
    #    \b \e True if the file item was deleted from list
    def Delete(self, item):
        item = self.GetIndex(item)
        
        if self.DeleteItem(item):
            self.Files.Pop(item)
            
            return True
        
        return False
    
    
    
    ## Retrieves the basename of the file's path
    #
    #  \param item
    #    Can be integer index, file path string, or FileItem instance
    #  \return
    #    \b \e String representation of the filename
    def GetBasename(self, item):
        return self.GetFileItem(item).GetBasename()
    
    
    ## Retrieves all file basenames in list
    #
    #  \return
    #    \b \e Tuple list of string file basenames
    def GetBasenames(self):
        basenames = []
        
        for FILE in self.Files:
            basenames.append(FILE.GetBasename())
        
        return tuple(basenames)
    
    
    ## Retrieves all executables
    def GetExecutables(self):
        exe_list = []
        for FILE in self.Files:
            if FILE.IsExecutable():
                exe_list.append(FILE.GetPath())
        
        return exe_list
    
    
    ## Retrieves globals.fileio.FileItem instance
    #
    #  \param item
    #    Can be item index, string path, or FileItem instance
    #  \return
    #    \b \e FileItem instance
    def GetFileItem(self, item):
        if IsString(item):
            for FILE in self.Files:
                if FILE.GetPath() == item:
                    item = FILE
                    
                    break
        
        elif isinstance(item, int):
            item = self.Files[item]
        
        if isinstance(item, FileItem):
            return item
    
    
    ## Retrieves the index of given item
    #
    #  \param item
    #    Can be \b \e FileItem instance or string representing file path
    #  \return
    #    \b \e Integer index of given item
    def GetIndex(self, item):
        item = self.GetFileItem(item)
        
        return self.Files.index(item)
    
    
    ## Retrieves full path of file
    #
    #  \param item
    #    Can be \b \e Integer index, string path, or FileName instance
    def GetPath(self, item):
        return self.GetFileItem(item).GetPath()
    
    
    ## Retrieves all file paths
    def GetPaths(self):
        paths = []
        for FILE in self.Files:
            paths.append(FILE.GetPath())
        
        return tuple(paths)
    
    
    ## Retrieves target path of file
    #
    #  \param item
    #    Can be \b \e Integer index, string path, or FileName instance
    def GetTarget(self, item):
        return self.GetFileItem(item).GetTarget()
    
    
    ## Retrieves all target paths from files
    #
    #  \return
    #    \b \e Tuple list of all target paths
    def GetTargets(self):
        targets = []
        
        for FILE in self.Files:
            targets.append(FILE.GetTarget())
        
        return tuple(targets)
    
    
    ## Inserts new globals.fileio.FileItem instance to list at given index
    #
    #  \param index
    #    \b \e Integer index at wich to insert itme
    #  \param item
    #    Can be \b \e Integer index, string path, or FileName instance
    #  \param target
    #    File's target installation directory (only if item is not FileItem instance)
    #  \return
    #    \b \e True if successfully added to list
    def Insert(self, index, item, target=None):
        item = self.GetFileItem(item)
        
        self.InsertStringItem(index, item.GetPath())
        
        self.Files.insert(index, item)
        
        if self.HLExes:
            self.SetItemTextColour(index, wx.RED)
        
        return item in self.Files
    
    
    ## Removes an item from the file list
    #
    #  Alias of input.list.BasicFileList.Delete
    def Remove(self, item):
        return self.Delete(item)
    
    
    ## Resets the list to default value (empty)
    def Reset(self):
        if ListCtrl.Reset(self):
            self.Files = []
            
            return True
        
        return False


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
        self.target_col = 1
        
        # Stores the information for file sources paths
        self.sources_list = []
        
        # FIXME: Way to do this dynamically?
        col_width = 150  # self.GetSize()[0] / 4
        
        self.InsertColumn(self.filename_col, GT(u'File / Folder'), width=col_width)
        # Last column is automatcially stretched to fill remaining size
        self.InsertColumn(self.target_col, GT(u'Staged Target'))
        
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
        self.SetStringItem(list_index, self.target_col, target_dir)
        
        self.sources_list.insert(list_index, source_dir)
        
        if os.path.isdir(source_path):
            self.SetItemTextColour(list_index, self.FOLDER_TEXT_COLOR)
        
        else:
            if os.access(source_path, os.X_OK) or executable:
                self.SetFileExecutable(list_index)
            
            if not os.path.isfile(source_path):
                self.SetItemBackgroundColour(list_index, COLOR_warn)
                
                # File was added but does not exist on filesystem
                return False
        
        return True
    
    
    ## TODO: Doxygen
    def DeleteAllItems(self):
        ListCtrl.DeleteAllItems(self)
        self.sources_list = []
    
    
    ## Retrieves the filename at given index
    #  
    #  \param i_index
    #    \b \e Integer row of the item
    #  \param basename
    #    If \b \e True, only retrives the file's basename
    def GetFilename(self, index, basename=False):
        filename = self.GetItemText(index)
        
        if basename:
            filename = os.path.basename(filename)
        
        return filename
    
    
    ## Retrieves an item's path
    def GetPath(self, index):
        file_dir = self.sources_list[index]
        file_name = self.GetItemText(index, self.filename_col)
        
        return ConcatPaths((file_dir, file_name))
    
    
    ## TODO: Doxygen
    def GetRowData(self, row):
        filename = self.GetFilename(row)
        source_dir = self.GetSource(row)
        target_dir = self.GetTarget(row)
        executable = self.IsExecutable(row)
        
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
        return self.sources_list[i_index]
    
    
    ## TODO: Doxygen
    def GetTarget(self, i_index):
        return self.GetItemText(i_index, self.target_col)
    
    
    ## Checks if item at index is a directory
    def IsDirectory(self, index):
        return os.path.isdir(self.GetPath(index))
    
    
    ## Checks if the file list is empty
    def IsEmpty(self):
        return not self.GetItemCount()
    
    
    ## Retrieves is the item at 'i_index' is executable
    #  
    #  \param i_index
    #        \b \e int : The list row to check
    def IsExecutable(self, index):
        return self.GetItemTextColour(index) == wx.RED
    
    
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
            self.sources_list.pop(current_selected)
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
            self.SetItemTextColour(row, wx.RED)
            
            return
        
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
#
#  This is a dummy class to facilitate merging to & from unstable branch
class FileListESS(FileList, EssentialField):
    def __init__(self, parent, win_id=wx.ID_ANY, name=wx.ListCtrlNameStr):
        FileList.__init__(self, parent, win_id, name)
        EssentialField.__init__(self)
