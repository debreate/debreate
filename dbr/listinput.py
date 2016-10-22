# -*- coding: utf-8 -*-

## \package dbr.listinput

# MIT licensing
# See: docs/LICENSE.txt


import wx, os
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, TextEditMixin

from dbr.language       import GT
from dbr.log            import Logger
from globals.constants  import COLOR_ERROR
from globals.constants  import FTYPE_EXE
from globals.constants  import file_types_defs


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
    
    
    def SetSingleStyle(self, style, add=True):
        self.listarea.SetSingleStyle(style, add)
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: imageId unused; Unknown purpose, not documented
    def SetStringItem(self, index, col, label, imageId=None):
        self.listarea.SetStringItem(index, col, label)



## An editable list
#  
#  Creates a ListCtrl class in which every column's text can be edited
class FileList(ListCtrlPanel, ListCtrlAutoWidthMixin, TextEditMixin):
    def __init__(self, parent, window_id=wx.ID_ANY):
        ListCtrlPanel.__init__(self, parent, window_id, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        TextEditMixin.__init__(self)
        
        self.parent = parent
        self.debreate = parent.debreate
        self.dir_tree = parent.dir_tree
        
        self.DEFAULT_BG_COLOR = self.GetBackgroundColour()
        
        self.filename_col = 0
        self.source_col = 1
        self.target_col = 2
        self.type_col = 3
        
        col_width = self.GetSize()[0] / 4
        
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
        
        wx.EVT_LIST_INSERT_ITEM(self.GetChildren()[1], self.GetId(), self.OnInsertItem)
        
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)
        
        # Resize bug hack
        if wx.MAJOR_VERSION == 3 and wx.MINOR_VERSION == 0:
            wx.EVT_SIZE(self, self.OnResize)
    
    
    ## TODO: Doxygen
    def AddFile(self, filename, source_dir, target_dir=None, executable=False):
        list_index = self.GetItemCount()
        
        # Method can be called with two argements: absolute filename & target directory
        if target_dir == None:
            target_dir = source_dir
            source_dir = os.path.dirname(filename)
            filename = os.path.basename(filename)
        
        Logger.Debug(__name__, GT(u'Adding file: {}/{}').format(source_dir, filename))
        
        self.InsertStringItem(list_index, filename)
        self.SetStringItem(list_index, self.source_col, source_dir)
        self.SetStringItem(list_index, self.target_col, target_dir)
        
        # TODO: Use 'GetFileMimeType' module to determine file type
        if os.access(u'{}/{}'.format(source_dir, filename), os.X_OK) or executable:
            self.SetStringItem(list_index, self.type_col, file_types_defs[FTYPE_EXE])
        
        #self.Refresh()
        if not os.path.isfile(u'{}/{}'.format(source_dir, filename)):
            self.SetItemBackgroundColour(list_index, COLOR_ERROR)
    
    
    ## Retrivies is the item at 'i_index' is executable
    #  
    #  TODO: Doxygen
    def FileIsExecutable(self, i_index):
        if self.GetItemText(i_index, self.type_col) == file_types_defs[FTYPE_EXE]:
            return True
        
        return False
    
    
    ## TODO: Doxygen
    def GetFilename(self, i_index):
        return self.GetItemText(i_index)
    
    
    ## TODO: Doxygen
    def GetRowData(self, row):
        filename = self.GetItem(row, self.filename_col).GetText()
        source_dir = self.GetItem(row, self.source_col).GetText()
        target_dir = self.GetItem(row, self.target_col).GetText()
        executable = self.GetItem(row, self.type_col).GetText() == file_types_defs[FTYPE_EXE]
        
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
    def GetSource(self, i_index):
        return self.GetItemText(i_index, self.source_col)
    
    
    ## TODO: Doxygen
    def GetTarget(self, i_index):
        return self.GetItemText(i_index, self.target_col)
    
    
    ## TODO: Doxygen
    def IsEmpty(self):
        item_count = self.GetItemCount()
        Logger.Debug(__name__, GT(u'File list is empty ({} files): {}').format(item_count, not item_count))
        return not item_count
    
    
    ## TODO: Doxygen
    def MissingFiles(self):
        return self.Refresh()
    
    
    ## TODO: Doxygen
    def OnInsertItem(self, event):
        Logger.Debug(__name__, u'FileList item inserted')
        
        children = self.GetChildren()
        
        Logger.Debug(__name__, u'Parent ID: {}'.format(self.GetId()))
        
        for x in range(0, len(children)):
            child = children[x]
            
            Logger.Debug(__name__, u'Child ID: {}'.format(child.GetId()))
            Logger.Debug(__name__, u'Child type: {}'.format(type(child)))
            Logger.Debug(__name__, u'Child name: {}'.format(child.GetName()))
            
        event.Skip()
    
    
    ## Defines actions to take when left-click or left-double-click event occurs
    #  
    #  The super method is overridden to ensure that 'event.Skip' is called.
    #  TODO: Notify wxPython project of 'event.Skip' error
    def OnLeftDown(self, event=None):
        TextEditMixin.OnLeftDown(self, event)
        
        event.Skip()
    
    
    ## Works around resize bug in wx 3.0
    #  
    #  Uses parent width & its children to determine
    #    desired width.
    #  FIXME: Unknown if this bug persists in wx 3.1
    def OnResize(self, event=None):
        if event:
            event.Skip(True)
        
        width = self.GetSize()
        height = width[1]
        width = width[0]
        
        # Use the parent window & its children to determine desired width
        target_width = self.parent.GetSize()[0] - self.parent.dir_tree.GetSize()[0] - 15
        
        if width > 0 and target_width > 0:
            if width != target_width:
                
                Logger.Warning(__name__,
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
    def Refresh(self):
        dirty = False
        for R in range(self.GetItemCount()):
            item_color = self.DEFAULT_BG_COLOR
            row_defs = self.GetRowDefs(R)
            
            if not os.path.isfile(u'{}/{}'.format(row_defs[u'source'], row_defs[u'filename'])):
                item_color = COLOR_ERROR
                dirty = True
            
            self.SetItemBackgroundColour(R, item_color)
        
        return dirty
    
    
    ## Removes selected files from list
    #  
    #  TODO: Define
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
