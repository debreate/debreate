# -*- coding: utf-8 -*-

## \package input.filelist

# MIT licensing
# See: docs/LICENSE.txt


import os, wx
from wx.lib.mixins.listctrl import TextEditMixin

from dbr.colors         import COLOR_executable
from dbr.colors         import COLOR_link
from dbr.colors         import COLOR_warn
from dbr.language       import GT
from dbr.log            import Logger
from globals.fileitem   import FileItem
from globals.mime       import GetFileMimeType
from globals.paths      import ConcatPaths
from globals.strings    import IsString
from input.essential    import EssentialField
from input.list         import ListCtrl


## List control intended for managing files
#
#  TODO: Derive FileList from this
#
#  \param hlExex
#    If \b \e True, will highlight executable files with red text
class BasicFileList(ListCtrl, TextEditMixin):
    def __init__(self, parent, win_id=wx.ID_ANY, hlExes=False, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.LC_ICON|wx.LC_REPORT|wx.LC_NO_HEADER,
            name=wx.ListCtrlNameStr, defaultValue=None, required=False, outLabel=None):
        
        ListCtrl.__init__(self, parent, win_id, pos, size, style, name=name,
                defaultValue=defaultValue, required=required, outLabel=outLabel)
        TextEditMixin.__init__(self)
        
        # Highlights executables in red if 'True'
        self.HLExes = hlExes
        
        ## List of globals.fileitem.FileItem instances
        self.FileItems = []
    
    
    ## Adds new globals.fileitem.FileItem instance to end of list
    #
    #  \param item
    #    Either the path to a file or a FileItem instance
    #  \param target
    #    File's target installation directory (only if item is not FileItem instance)
    #  \return
    #    \b \e True if successfully added to list
    def Add(self, item, target=None):
        return self.Insert(self.GetCount(), item, target)
    
    
    ## Appends new globals.fileitem.FileItem instance to end of list
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
            self.FileItems.Pop(item)
            
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
        
        for FILE in self.FileItems:
            basenames.append(FILE.GetBasename())
        
        return tuple(basenames)
    
    
    ## Retrieves all executables
    def GetExecutables(self):
        exe_list = []
        for FILE in self.FileItems:
            if FILE.IsExecutable():
                exe_list.append(FILE.GetPath())
        
        return exe_list
    
    
    ## Retrieves globals.fileitem.FileItem instance
    #
    #  \param item
    #    Can be item index, string path, or FileItem instance
    #  \return
    #    \b \e FileItem instance
    def GetFileItem(self, item):
        if IsString(item):
            for FILE in self.FileItems:
                if FILE.GetPath() == item:
                    item = FILE
                    
                    break
        
        elif isinstance(item, int):
            item = self.FileItems[item]
        
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
        
        return self.FileItems.index(item)
    
    
    ## Retrieves full path of file
    #
    #  \param item
    #    Can be \b \e Integer index, string path, or FileName instance
    def GetPath(self, item):
        return self.GetFileItem(item).GetPath()
    
    
    ## Retrieves all file paths
    def GetPaths(self):
        paths = []
        for FILE in self.FileItems:
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
        
        for FILE in self.FileItems:
            targets.append(FILE.GetTarget())
        
        return tuple(targets)
    
    
    ## Inserts new globals.fileitem.FileItem instance to list at given index
    #
    #  \param index
    #    \b \e Integer index at which to insert item
    #  \param item
    #    Can be \b \e Integer index, string path, or FileName instance
    #  \param target
    #    File's target installation directory (only if item is not FileItem instance)
    #  \return
    #    \b \e True if successfully added to list
    def Insert(self, index, item, target=None):
        item = self.GetFileItem(item)
        
        self.InsertStringItem(index, item.GetPath())
        
        self.FileItems.insert(index, item)
        
        if self.HLExes:
            self.SetItemTextColour(index, wx.RED)
        
        return item in self.FileItems
    
    
    ## Removes an item from the file list
    #
    #  Alias of input.list.BasicFileList.Delete
    def Remove(self, item):
        return self.Delete(item)
    
    
    ## Resets the list to default value (empty)
    def Reset(self):
        if ListCtrl.Reset(self):
            self.FileItems = []
            
            return True
        
        return False


## An editable list
#
#  Creates a ListCtrl class in which every column's text can be edited
class FileList(ListCtrl, TextEditMixin, wx.FileDropTarget):
    def __init__(self, parent, win_id=wx.ID_ANY, name=wx.ListCtrlNameStr, defaultValue=None,
            required=False, outLabel=None):
        
        ListCtrl.__init__(self, parent, win_id, style=wx.LC_REPORT, name=name,
                defaultValue=defaultValue, required=required, outLabel=outLabel)
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
        col_width = 150
        
        self.InsertColumn(self.filename_col, GT(u'File'), width=col_width)
        self.InsertColumn(self.source_col, GT(u'Source Directory'), width=col_width)
        self.InsertColumn(self.target_col, GT(u'Staged Target'), width=col_width)
        # Last column is automatically stretched to fill remaining size
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
        self.SetStringItem(list_index, self.type_col, GetFileMimeType(source_path))
        
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
    
    
    ## TODO: Doxygen
    def DeleteAllItems(self):
        ListCtrl.DeleteAllItems(self)
    
    
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
        file_dir = self.GetItemText(index, self.source_col)
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
    
    
    ## Retrieves the source path of a file
    #
    #  \param row
    #    Row index of item
    def GetSource(self, row):
        return self.GetItemText(row, self.source_col)
    
    
    ## Retrieves target directory of a file
    #
    #  \param row
    #    Row index of item
    def GetTarget(self, row):
        return self.GetItemText(row, self.target_col)
    
    
    ## Retrieves mime type of a file
    #
    #  \param row
    #    Row index of item
    def GetType(self, row):
        return self.GetItemText(row, self.type_col)
    
    
    ## Checks if an item is a directory
    #
    #  \param row
    #    Row index of item
    def IsDirectory(self, row):
        return os.path.isdir(self.GetPath(row))
    
    
    ## Checks if the file list is empty
    def IsEmpty(self):
        return not self.GetItemCount()
    
    
    ## Checks if an item is executable
    #
    #  \param row
    #    Row index of item
    def IsExecutable(self, row):
        return self.GetItemTextColour(row) == wx.RED
    
    
    ## Checks if an item is a symbolic link
    #
    #  \param row
    #    Row index of item
    def IsSymlink(self, row):
        return u'symlink' in self.GetType(row)
    
    
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
    #
    #  \return
    #        \b \e bool : True if files are missing, False if all okay
    def RefreshFileList(self):
        dirty = False
        for row in range(self.GetItemCount()):
            item_color = self.DEFAULT_BG_COLOR
            text_color = self.DEFAULT_TEXT_COLOR
            row_defs = self.GetRowDefs(row)
            
            absolute_filename = u'{}/{}'.format(row_defs[u'source'], row_defs[u'filename'])
            
            if not os.path.exists(absolute_filename):
                item_color = COLOR_warn
                dirty = True
            
            elif os.path.isdir(absolute_filename):
                text_color = self.FOLDER_TEXT_COLOR
            
            elif self.IsSymlink(row):
                text_color = COLOR_link
            
            elif os.access(absolute_filename, os.X_OK):
                text_color = COLOR_executable
            
            self.SetItemTextColour(row, text_color)
            self.SetItemBackgroundColour(row, item_color)
        
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
    
    
    ## Selects all items in the list
    def SelectAll(self):
        file_count = self.GetItemCount()
        
        for x in range(file_count):
            self.Select(x)
    
    
    ## Marks a file as executable
    #
    #  \param row
    #    Row index of item
    def SetFileExecutable(self, row, executable=True):
        if executable:
            self.SetItemTextColour(row, wx.RED)
            
            return
        
        self.SetItemTextColour(row, self.DEFAULT_TEXT_COLOR)
    
    
    ## Sorts listed items in target column alphabetically
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
    def __init__(self, parent, win_id=wx.ID_ANY, name=wx.ListCtrlNameStr, defaultValue=None,
            required=False, outLabel=None):
        
        FileList.__init__(self, parent, win_id, name, defaultValue, required, outLabel)
        EssentialField.__init__(self)
