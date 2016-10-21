# -*- coding: utf-8 -*-

## \package wiz_bin.files


import wx, os, shutil
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, TextEditMixin

from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonBrowse
from dbr.buttons        import ButtonClear
from dbr.buttons        import ButtonDel
from dbr.buttons        import ButtonRefresh
from dbr.dialogs        import DetailedMessageDialog
from dbr.dialogs        import GetDirDialog
from dbr.dialogs        import ShowDialog
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from dbr.log            import Logger
from dbr.wizard         import WizardPage
from globals.bitmaps    import ICON_ERROR
from globals.constants  import COLOR_ERROR
from globals.constants  import FTYPE_EXE
from globals.constants  import file_types_defs
from globals.errorcodes import dbrerrno
from globals.ident      import ID_CUSTOM
from globals.ident      import ID_FILES
from globals.paths      import PATH_home
from globals.tooltips   import SetPageToolTips


ID_pin = 100
ID_fin = 101
ID_pout = 102

ID_AddDir = 140
ID_AddFile = 141
ID_Refresh = 142


## TODO: Doxygen
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ID_FILES)
        
        # Allows calling parent methods
        self.parent = parent
        self.debreate = self.GetGrandParent()
        
        # Create a Context Menu
        self.menu = wx.Menu()
        
        self.add_dir = wx.MenuItem(self.menu, ID_AddDir, GT(u'Add Folder'))
        self.add_file = wx.MenuItem(self.menu, ID_AddFile, GT(u'Add File'))
        self.refresh = wx.MenuItem(self.menu, ID_Refresh, GT(u'Refresh'))
        
        wx.EVT_MENU(self, ID_AddDir, self.AddPath)
        wx.EVT_MENU(self, ID_AddFile, self.AddPath)
        wx.EVT_MENU(self, ID_Refresh, self.OnRefresh)
        
        self.menu.AppendItem(self.add_dir)
        self.menu.AppendItem(self.add_file)
        self.menu.AppendSeparator()
        self.menu.AppendItem(self.refresh)
        
        # Directory listing for importing files and folders
        self.dir_tree = wx.GenericDirCtrl(self, -1, PATH_home, size=(300,20))
        
        wx.EVT_CONTEXT_MENU(self.dir_tree, self.OnRightClick)
        
        # ----- Add/Remove/Clear buttons
        path_add = ButtonAdd(self)
        path_add.SetName(u'add')
        path_remove = ButtonDel(self)
        path_remove.SetName(u'remove')
        button_clear = ButtonClear(self)
        button_clear.SetName(u'clear')
        
        wx.EVT_BUTTON(path_add, -1, self.AddPath)
        wx.EVT_BUTTON(path_remove, -1, self.RemoveSelected)
        wx.EVT_BUTTON(button_clear, -1, self.ClearAll)
        
        # ----- Destination path
        # choices of destination
        self.radio_bin = wx.RadioButton(self, -1, u'/bin', style=wx.RB_GROUP)
        self.radio_usrbin = wx.RadioButton(self, -1, u'/usr/bin')
        self.radio_usrlib = wx.RadioButton(self, -1, u'/usr/lib')
        self.radio_locbin = wx.RadioButton(self, -1, u'/usr/local/bin')
        self.radio_loclib = wx.RadioButton(self, -1, u'/usr/local/lib')
        self.radio_cst = wx.RadioButton(self, ID_CUSTOM, GT(u'Custom'))
        
        # Start with "Custom" selected
        self.radio_cst.SetValue(True)
        
        # group buttons together
        self.targets = (
            self.radio_bin,
            self.radio_usrbin,
            self.radio_usrlib,
            self.radio_locbin,
            self.radio_loclib,
            self.radio_cst,
            )
        
        # create an event to enable/disable custom widget
        for item in self.targets:
            wx.EVT_RADIOBUTTON(item, -1, self.SetDestination)
        
        # make them look pretty
        radio_sizer = wx.GridSizer(3, 2, 5, 5)
        for item in self.targets:
            radio_sizer.Add(item, 0)
        self.radio_border = wx.StaticBox(self, -1, GT(u'Target'), size=(20,20))
        radio_box = wx.StaticBoxSizer(self.radio_border, wx.HORIZONTAL)
        radio_box.Add(radio_sizer, 0)
        
        self.prev_dest_value = u'/usr/bin'
        self.dest_cust = wx.TextCtrl(self, -1, self.prev_dest_value, name=u'target')
        
        wx.EVT_KEY_DOWN(self.dest_cust, self.GetDestValue)
        wx.EVT_KEY_UP(self.dest_cust, self.CheckDest)
        
        cust_sizer = wx.BoxSizer(wx.VERTICAL)  # put the textctrl in own sizer so expands horizontally
        cust_sizer.Add(self.dest_cust, 1, wx.EXPAND)
        
        self.dest_browse = ButtonBrowse(self)
        self.dest_browse.SetName(u'browse')
        self.dest_browse.SetId(ID_pout)
        
        wx.EVT_BUTTON(self.dest_browse, -1, self.OnBrowse)
        
        self.path_dict = {ID_pout: self.dest_cust}
        
        # TODO: Make custom button
        btn_refresh = ButtonRefresh(self)
        btn_refresh.SetName(u'refresh')
        
        btn_refresh.Bind(wx.EVT_BUTTON, self.OnRefreshFileList)
        
        path_add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        path_add_sizer.Add(path_add, 0)
        path_add_sizer.Add(path_remove, 0)
        path_add_sizer.Add(button_clear, 0, wx.ALIGN_CENTER_VERTICAL)
        path_add_sizer.Add(cust_sizer, 1, wx.ALIGN_CENTER_VERTICAL)
        path_add_sizer.Add(self.dest_browse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        path_add_sizer.Add(btn_refresh, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        
        
        # Display area for files added to list
        self.file_list = FileList(self)
        self.file_list.SetName(u'filelist')
        
        # List that stores the actual paths to the files
        # FIXME: Deprecated???
        self.list_data = []
        
        wx.EVT_KEY_DOWN(self.file_list, self.DelPathDeprecated)
        
        LMR_sizer = wx.BoxSizer(wx.HORIZONTAL)
        LMR_sizer.Add(self.file_list, 1, wx.EXPAND)
        
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        page_sizer.AddSpacer(10)
        page_sizer.Add(radio_box, 0, wx.ALL, 5)
        page_sizer.Add(path_add_sizer, 0, wx.EXPAND|wx.ALL, 5)
        page_sizer.Add(LMR_sizer, 5, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        sizer = wx.FlexGridSizer(1, 2)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(1, 2)
        sizer.Add(self.dir_tree, 1, wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        sizer.Add(page_sizer, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
        
        
        SetPageToolTips(self)
    
    
    ## TODO: Doxygen
    def ExportBuild(self, target):
        if not os.path.isdir(target):
            return (dbrerrno.ENOENT, GT(u'Target directory does not exist: {}').format(target))
        
        if self.file_list.MissingFiles():
            return (dbrerrno.ENOENT, GT(u'Missing files in file list'))
        
        file_count = self.file_list.GetItemCount()
        for R in range(file_count):
            filename, source_dir, stage_dir, executable = self.file_list.GetRowData(R)
            
            stage_dir = u'{}/{}'.format(target, stage_dir).replace(u'//', u'/')
            staged_file = u'{}/{}'.format(stage_dir, filename).replace(u'//', u'/')
            
            filename = u'{}/{}'.format(source_dir, filename).replace(u'//', u'/')
            Logger.Debug(__name__,
                    GT(u'Coppying file: {} -> {}').format(filename, stage_dir))
            
            if not os.path.isdir(stage_dir):
                os.makedirs(stage_dir)
            
            shutil.copy(filename, stage_dir)
            
            if executable:
                os.chmod(staged_file, 0755)
            
            if not os.path.isfile(staged_file):
                return(dbrerrno.ENOENT, GT(u'File was not copied to stage: {}').format(staged_file))
        
        return (dbrerrno.SUCCESS, None)
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        return not self.file_list.IsEmpty()
    
    
    ## TODO: Doxygen
    def OnRefreshFileList(self, event=None):
        self.file_list.Refresh()
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Rename to OnRightClickTree or similar
    def OnRightClick(self, event):
        # Show a context menu for adding files and folders
        path = self.dir_tree.GetPath()
        if os.path.isdir(path):
            self.add_dir.Enable(True)
            self.add_file.Enable(False)
        elif os.path.isfile(path):
            self.add_dir.Enable(False)
            self.add_file.Enable(True)
        self.dir_tree.PopupMenu(self.menu)
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event):
        dia = GetDirDialog(self.GetDebreateWindow(), GT(u'Choose Target Directory'))
        if ShowDialog(dia):
            self.dest_cust.SetValue(dia.GetPath())
    
    
    ## TODO: Doxygen
    def GetDestValue(self, event):
        if self.dest_cust.GetValue() != wx.EmptyString:
            if self.dest_cust.GetValue()[0] == u'/':
                self.prev_dest_value = self.dest_cust.GetValue()
        event.Skip()
    
    
    ## TODO: Doxygen
    def CheckDest(self, event):
        if self.dest_cust.GetValue() == wx.EmptyString:
            self.dest_cust.SetValue(self.prev_dest_value)
            self.dest_cust.SetInsertionPoint(-1)
        elif self.dest_cust.GetValue()[0] != u'/':
            self.dest_cust.SetValue(self.prev_dest_value)
            self.dest_cust.SetInsertionPoint(-1)
        event.Skip()
    
    
    ## Add a selected path to the list of files
    #  
    #  TODO: Rename to OnAddPath
    def AddPath(self, event):
        # List of files tuple formatted as: filename, source
        files = []
        
        source = self.dir_tree.GetPath()
        target_dir = None
        
        for target in self.targets:
            if target.GetValue():
                if target.GetId() == ID_CUSTOM:
                    target_dir = self.dest_cust.GetValue()
                
                else:
                    target_dir = target.GetLabel()
                
                break
        
        if target_dir == None:
            Logger.Error(__name__, GT(u'Expected string for staging target, got None type instead'))
        
        if os.path.isfile(source):
            filename = os.path.basename(source)
            source_dir = os.path.dirname(source)
            
            files.append((filename, source_dir))
        
        elif os.path.isdir(source):
            for PATH, DIRS, FILES in os.walk(source):
                for filename in FILES:
                    files.append((filename, PATH))
        
        file_count = len(files)
        
        # Set the maximum file count to process without showing progress dialog
        efficiency_threshold = 250
        
        # Set the maximum file count to process without showing warning dialog
        warning_threshhold = 1000
        
        get_files = True
        if file_count > warning_threshhold:
            count_warnmsg = GT(u'Importing {} files'.format(file_count))
            count_warnmsg = u'{}. {}.'.format(count_warnmsg, GT(u'This could take a VERY long time'))
            count_warnmsg = u'{}\n{}'.format(count_warnmsg, GT(u'Are you sure you want to continue?'))
            
            get_files = wx.MessageDialog(self, count_warnmsg, GT(u'WARNING'),
                    style=wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING).ShowModal() == wx.ID_YES
        
        if get_files:
            # Show a progress dialog that can be aborted
            if file_count > efficiency_threshold:
                task_msg = GT(u'Getting files from {}'.format(source))
                task_progress = wx.ProgressDialog(GT(u'Progress'), u'{}\n'.format(task_msg), file_count, self,
                        wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_CAN_ABORT)
                
                # Add text to show current file number being processed
                count_text = wx.StaticText(task_progress, wx.ID_ANY, u'0 / {}'.format(file_count))
                tprogress_layout = task_progress.GetSizer()
                tprogress_layout.Insert(1, count_text, -1, wx.ALIGN_CENTER)
                
                # Resize the dialog to fit the new text
                tprogress_size = task_progress.GetSize()
                task_progress.SetSize(wx.Size(tprogress_size[0], tprogress_size[1] + tprogress_size[1]/9))
                
                task_progress.Layout()
                
                task = 0
                while task < file_count:
                    if task_progress.WasCancelled():
                        task_progress.Destroy()
                        break
                    
                    # Get the index before progress dialog is updated
                    task_index = task
                    
                    task += 1
                    count_text.SetLabel(u'{} / {}'.format(task, file_count))
                    task_progress.Update(task)#, u'{}\n{} / {}'.format(task_msg, task, file_count))
                    
                    self.file_list.AddFile(files[task_index][0], files[task_index][1], target_dir)
            
            else:
                for F in files:
                    self.file_list.AddFile(F[0], F[1], target_dir)
        
            self.file_list.Sort()
    
    
    ## TODO: Doxygen
    def OnRefresh(self, event):
        path = self.dir_tree.GetPath()
#		if isfile(path):
#			path = os.path.split(path)[0]
        
        self.dir_tree.ReCreateTree()
        self.dir_tree.SetPath(path)
    
    
    ## TODO: Doxygen
    def SelectAll(self):
        self.file_list.SelectAll()
    
    
    ## TODO: Doxygen
    def RemoveSelected(self, event):
        self.file_list.RemoveSelected()
    
    
    # FIXME: Deprecated; Replace with self.OnKeyDelete|self.OnKeyDown
    def DelPathDeprecated(self, event):
        try:
            modifier = event.GetModifiers()
            keycode = event.GetKeyCode()
        except AttributeError:
            keycode = event.GetEventObject().GetId()
        
        if keycode == wx.WXK_DELETE:
            selected = [] # Items to remove from visible list
            toremove = [] # Items to remove from invisible list
            total = self.file_list.GetSelectedItemCount()
            current = self.file_list.GetFirstSelected()
            if current != -1:
                selected.insert(0, current)
                while total > 1:
                    total = total - 1
                    prev = current
                    current = self.file_list.GetNextSelected(prev)
                    selected.insert(0, current)
            for path in selected:
                # Remove the item from the invisible list
                for item in self.list_data:
                    filename = self.file_list.GetItemText(path)
                    dest = self.file_list.GetItem(path, 1).GetText()
                    if filename.encode(u'utf-8') == item[1].decode(u'utf-8') and dest.encode(u'utf-8') == item[2].decode(u'utf-8'):
                        toremove.append(item)
                    
                self.file_list.DeleteItem(path) # Remove the item from the visible list
            
            for item in toremove:
                self.list_data.remove(item)
            
        elif keycode == 65 and modifier == wx.MOD_CONTROL:
            self.SelectAll()
    
    
    ## TODO: Doxygen
    def ClearAll(self, event):
        confirm = wx.MessageDialog(self, GT(u'Clear all files?'), GT(u'Confirm'), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_YES:
            self.file_list.DeleteAllItems()
            self.list_data = []
    
    
    ## TODO: Doxygen
    def SetDestination(self, event):
        # Event handler that disables the custom destination if the corresponding radio button isn't selected
        if self.radio_cst.GetValue() == True:
            self.dest_cust.Enable()
            self.dest_browse.Enable()
        else:
            self.dest_cust.Disable()
            self.dest_browse.Disable()
    
    
    ## TODO: Doxygen
    def SetFieldDataLegacy(self, data):
        # Clear files list
        self.list_data = []
        self.file_list.DeleteAllItems()
        files_data = data.split(u'\n')
        if int(files_data[0]):
            # Get file count from list minus first item "1"
            files_total = len(files_data)
            
            # Store missing files here
            missing_files = []
            
            while files_total > 1:
                files_total -= 1
                src = (files_data[files_total].split(u' -> ')[0], False)
                
                # False changes to true if src file is executable
                if src[0][-1] == u'*':
                    src = (src[0][:-1], True) # Set executable flag and remove "*"
                filename = files_data[files_total].split(u' -> ')[1]
                dest = files_data[files_total].split(u' -> ')[2]
                
                # Check if files still exist
                if os.path.exists(src[0]):
                    # Deprecated
                    #self.file_list.InsertStringItem(0, absolute_filename)
                    #self.file_list.SetStringItem(0, 1, dest)
                    self.file_list.AddFile(filename, os.path.dirname(src[0]), dest)
                    self.list_data.insert(0, (src[0], filename, dest))
                    # Check if file is executable
                    if src[1]:
                        self.file_list.SetItemTextColour(0, u'red') # Set text color to red
                else:
                    missing_files.append(src[0])
                
            self.file_list.Sort()
            
            # If files are missing show a message
            if len(missing_files):
                alert = wx.Dialog(self, -1, GT(u'Missing Files'))
                alert_text = wx.StaticText(alert, -1, GT(u'Could not locate the following files:'))
                alert_list = wx.TextCtrl(alert, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
                alert_list.SetValue(u'\n'.join(missing_files))
                button_ok = wx.Button(alert, wx.ID_OK)
                
                alert_sizer = wx.BoxSizer(wx.VERTICAL)
                alert_sizer.AddSpacer(5)
                alert_sizer.Add(alert_text, 1)
                alert_sizer.Add(alert_list, 3, wx.EXPAND)
                alert_sizer.Add(button_ok, 0, wx.ALIGN_RIGHT)
                
                alert.SetSizerAndFit(alert_sizer)
                alert.Layout()
                
                alert.ShowModal()
    
    
    ## Retrieves information on files to be packaged
    #  
    #  \return
    #        \b \e tuple(str, str) : A tuple containing the filename & a list of files with their targets formatted for text output
    def GetPageInfo(self, string_format=False):
        item_count = self.file_list.GetItemCount()
        
        if item_count:
            #file_list = []
            files_definitions = {}
            for X in range(item_count):
                row_data = self.file_list.GetRowData(X)
                filename = u'{}/{}'.format(row_data[1], row_data[0])
                target = row_data[2]
                executable = row_data[3]
                
                if executable:
                    # Use asterix to mark executables (file that may not be actual executables on the filesystem)
                    filename = u'{} *'.format(filename)
                
                if target in files_definitions:
                    files_definitions[target].append(filename)
                    continue
                
                files_definitions[target] = [filename,]
            
            files_data = []
            for D in files_definitions:
                files_data.append(u'[{}]'.format(D))
                
                for F in files_definitions[D]:
                    files_data.append(F)
            
            files_data = u'\n'.join(files_data)
            
            if string_format:
                return files_data
            
            return (__name__, files_data)
        
        return None
    
    
    ## TODO: Doxygen
    #  
    #  \override dbr.wizard.Wizard.ImportPageInfo
    def ImportPageInfo(self, filename):
        Logger.Debug(__name__, GT(u'Importing page info from {}').format(filename))
        
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        FILE = open(filename)
        files_data = FILE.read().split(u'\n')
        FILE.close()
        
        # Lines beginning with these characters will be ignored
        ignore_characters = (
            u'',
            u' ',
            u'#',
        )
        
        target = None
        targets_list = []
        
        for L in files_data:
            if not TextIsEmpty(L) and L[0] not in ignore_characters:
                if u'[' in L and u']' in L:
                    target = L.split(u'[')[-1].split(u']')[0]
                    continue
                
                if target:
                    executable = (len(L) > 1 and L[-2:] == u' *')
                    if executable:
                        L = L[:-2]
                    
                    targets_list.append((target, L, executable))
        
        missing_files = []
        
        for T in targets_list:
            if not os.path.isfile(T[1]):
                missing_files.append(T[1])
            
            source_file = os.path.basename(T[1])
            source_dir = os.path.dirname(T[1])
            
            self.file_list.AddFile(source_file, source_dir, T[0], executable=T[2])
        
        if len(missing_files):
            err_line1 = GT(u'The following files are missing from the filesystem.')
            err_line2 = GT(u'They will be highlighted on the Files page.')
            DetailedMessageDialog(self.debreate, title=GT(u'Warning'), icon=ICON_ERROR,
                    text=u'\n'.join((err_line1, err_line2)),
                    details=u'\n'.join(missing_files)).ShowModal()
        
        return 0
    
    ## Resets all fields on page to default values
    #  
    #  \override dbr.wizard.Wizard.ImportPageInfo
    def ResetPageInfo(self):
        self.file_list.DeleteAllItems()



## An editable list
#  
#  Creates a ListCtrl class in which every column's text can be edited
class FileList(wx.ListCtrl, ListCtrlAutoWidthMixin, TextEditMixin):
    def __init__(self, parent, window_id=wx.ID_ANY):
        wx.ListCtrl.__init__(self, parent, window_id,
                style=wx.BORDER_SIMPLE|wx.LC_REPORT)
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
    
    
    ## TODO: Doxygen
    def MissingFiles(self):
        return self.Refresh()
    
    
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
    
    
    ## Toggles executable flag for selected list items
    #  
    #  TODO: Define & execute with context menu
    def ToggleExecutable(self):
        pass
    
    
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


## A custom progress dialog
#  
#  FIXME: Not working; Remove???
class ProgressDialog(wx.Dialog):
    def __init__(self, parent, title, message, task_count):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title,
                style=wx.DEFAULT_DIALOG_STYLE)
        
        self.task_count = task_count
        
        # FIXME: How to make ProgressDialog inherit wx.ProgressDialog class
        #self.progress_dialog = wx.ProgressDialog(title, message, task_count, self, style)
        
        message_text = wx.StaticText(self, wx.ID_ANY, message)
        self.count_text = wx.StaticText(self, wx.ID_ANY, u'0 / {}'.format(task_count))
        self.progress = wx.Gauge(self, wx.ID_ANY, task_count)
        
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(message_text, -1)
        layout.Add(self.count_text, -1, wx.ALIGN_CENTER)
        layout.Add(self.progress, -1, wx.ALIGN_CENTER|wx.EXPAND)
        
        # Resize the dialog to fit new text
        #self.progress_size = self.progress_dialog.GetSize()
        #self.progress_size = wx.Size(self.progress_size[0], self.progress_size[1] + self.progress_size[1]/9)
        #self.progress_dialog.SetSize(self.progress_size)
        
        self.SetSizer(layout)
        self.SetAutoLayout(True)
        self.Layout()
        
        #self.progress_dialog.Bind(wx.EVT_SIZE, self.OnBorderResize)
        
        self.ShowModal()
    
    
    def Update(self, *args, **kwargs):
        self.count_text.SetLabel(u'{} / {}'.format(args[0], self.task_count))
        self.progress.SetValue(args[0])
        
        self.count_text.Refresh()
        self.progress.Refresh()
        self.Refresh()
    
    
    def WasCancelled(self):
        return False
    
    
    def Destroy(self):
        self.progress_dialog.Destroy()
        self.EndModal()
        del(self)
    
    
    def OnBorderResize(self, event=None):
        if event != None:
            # FIXME: Hack
            self.SetSize(self.progress_size)
