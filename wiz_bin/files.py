# -*- coding: utf-8 -*-


import wx, os
from wx.lib.mixins import \
    listctrl as wxMixinListCtrl

import dbr
from dbr.language import GT
from dbr.constants import ID_FILES, ID_CUSTOM
from dbr import DebugEnabled, Logger
from dbr.wizard import WizardPage


ID_pin = 100
ID_fin = 101
ID_pout = 102

ID_AddDir = 140
ID_AddFile = 141
ID_Refresh = 142

# FIXME: Use global from dbr.constants
home = os.getenv(u'HOME')


class Panel(wx.Panel, WizardPage):
    """Class defining controls for the "Paths" page"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, ID_FILES, name=GT(u'Files'))
        WizardPage.__init__(self)
        
        # For identifying page to parent
        #self.ID = "FILES"
        
        # Allows calling parent methods
        self.parent = parent
        self.debreate = self.GetGrandParent()
        
        # Create a Context Menu
        self.menu = wx.Menu()
        
        self.add_dir = wx.MenuItem(self.menu, ID_AddDir, GT(u'Add Folder'))
        self.add_file = wx.MenuItem(self.menu, ID_AddFile, GT(u'Add File'))
        self.refresh = wx.MenuItem(self.menu, ID_Refresh, GT(u'Refresh'))
        
        if DebugEnabled():
            wx.EVT_MENU(self, ID_AddDir, self.AddPath)
            wx.EVT_MENU(self, ID_AddFile, self.AddPath)
        else:
            wx.EVT_MENU(self, ID_AddDir, self.AddPathDeprecated)
            wx.EVT_MENU(self, ID_AddFile, self.AddPathDeprecated)
        wx.EVT_MENU(self, ID_Refresh, self.OnRefresh)
        
        self.menu.AppendItem(self.add_dir)
        self.menu.AppendItem(self.add_file)
        self.menu.AppendSeparator()
        self.menu.AppendItem(self.refresh)
        
        # Directory listing for importing files and folders
        self.dir_tree = wx.GenericDirCtrl(self, -1, home, size=(300,20))
        
        wx.EVT_CONTEXT_MENU(self.dir_tree, self.OnRightClick)
        
        # ----- Add/Remove/Clear buttons
        path_add = dbr.buttons.ButtonAdd(self)
        path_remove = dbr.buttons.ButtonDel(self)
        button_clear = dbr.buttons.ButtonClear(self)
        
        if DebugEnabled():
            wx.EVT_BUTTON(path_add, -1, self.AddPath)
        else:
            wx.EVT_BUTTON(path_add, -1, self.AddPathDeprecated)
        
        if DebugEnabled():
            wx.EVT_BUTTON(path_remove, -1, self.RemoveSelected)
        else:
            wx.EVT_BUTTON(path_remove, -1, self.DelPathDeprecated)
        
        wx.EVT_BUTTON(button_clear, -1, self.ClearAll)
        
        # ----- Destination path
        # choices of destination
        self.radio_bin = wx.RadioButton(self, -1, "/bin", style=wx.RB_GROUP)
        self.radio_usrbin = wx.RadioButton(self, -1, "/usr/bin")
        self.radio_usrlib = wx.RadioButton(self, -1, "/usr/lib")
        self.radio_locbin = wx.RadioButton(self, -1, "/usr/local/bin")
        self.radio_loclib = wx.RadioButton(self, -1, "/usr/local/lib")
        self.radio_cst = wx.RadioButton(self, ID_CUSTOM, GT(u'Custom'))
        
        # Start with "Custom" selected
        self.radio_cst.SetValue(True)
        
        # group buttons together
        self.radio_group = (self.radio_bin, self.radio_usrbin, self.radio_usrlib, self.radio_locbin, self.radio_loclib, self.radio_cst)
        
        # create an event to enable/disable custom widget
        for item in self.radio_group:
            wx.EVT_RADIOBUTTON(item, -1, self.SetDestination)
        
        # make them look pretty
        radio_sizer = wx.GridSizer(3, 2, 5, 5)
        for item in self.radio_group:
            radio_sizer.Add(item, 0)
        self.radio_border = wx.StaticBox(self, -1, GT(u'Target'), size=(20,20))
        radio_box = wx.StaticBoxSizer(self.radio_border, wx.HORIZONTAL)
        radio_box.Add(radio_sizer, 0)
        
        self.prev_dest_value = "/usr/bin"
        self.dest_cust = wx.TextCtrl(self, -1, self.prev_dest_value)
        wx.EVT_KEY_DOWN(self.dest_cust, self.GetDestValue)
        wx.EVT_KEY_UP(self.dest_cust, self.CheckDest)
        cust_sizer = wx.BoxSizer(wx.VERTICAL)  # put the textctrl in own sizer so expands horizontally
        cust_sizer.Add(self.dest_cust, 1, wx.EXPAND)
        
        self.dest_browse = dbr.buttons.ButtonBrowse(self, ID_pout)
        
        wx.EVT_BUTTON(self.dest_browse, -1, self.OnBrowse)
        
        self.path_dict = {ID_pout: self.dest_cust}
        
        path_add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        path_add_sizer.Add(path_add, 0)
        path_add_sizer.Add(path_remove, 0)
        path_add_sizer.Add(button_clear, 0, wx.ALIGN_CENTER_VERTICAL)
        path_add_sizer.Add(cust_sizer, 1, wx.ALIGN_CENTER_VERTICAL)
        path_add_sizer.Add(self.dest_browse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
        
        
        # Display area for files added to list
        self.dest_area = FileList(self, -1)
        
        # List that stores the actual paths to the files
        self.list_data = []
        
        # Set the width of first column on creation
        parent_size = self.GetGrandParent().GetSize()
        parent_width = parent_size[1]
        
        # Old style list
        if not DebugEnabled():
            self.dest_area.InsertColumn(0, GT(u'File'), width=parent_width/3-10)
            self.dest_area.InsertColumn(1, GT(u'Target'))
        
        wx.EVT_KEY_DOWN(self.dest_area, self.DelPathDeprecated)
        
        LMR_sizer = wx.BoxSizer(wx.HORIZONTAL)
        LMR_sizer.Add(self.dest_area, 1, wx.EXPAND)
        
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
        
        # Lists of widgets that change language
        self.setlabels = {	self.dest_browse: u'Custom' }
    
    
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
    
    def OnBrowse(self, event):
        if self.parent.parent.cust_dias.IsChecked() == True:
            dia = dbr.OpenDir(self)
            if dia.DisplayModal() == True:
                self.dest_cust.SetValue(dia.GetPath())
        else:
            dia = wx.DirDialog(self, GT(u'Choose Target Directory'), os.getcwd(), wx.DD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                self.dest_cust.SetValue(dia.GetPath())
#		if dia.GetPath() == True:
#			self.dest_cust.SetValue(dia.GetPath())
#		if dia.Open == True:
#			self.dest_cust.SetValue(dia.GetPath())
    
    def GetDestValue(self, event):
        if self.dest_cust.GetValue() != wx.EmptyString:
            if self.dest_cust.GetValue()[0] == u'/':
                self.prev_dest_value = self.dest_cust.GetValue()
        event.Skip()
    
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
        
        # TODO: Change 'self.radio_group' to 'self.targets'
        for target in self.radio_group:
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
                if DebugEnabled():
                    for filename in FILES:
                        files.append((filename, PATH))
        
        file_count = len(files)
        efficiency_threshold = 100
        
        # Show a progress dialog that can be aborted
        if file_count > efficiency_threshold:
            task_progress = wx.ProgressDialog(GT(u'Progress'), GT(u'Getting files from {}'.format(source)),
                    file_count, self, wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_CAN_ABORT)
            
            task = 0
            while task < file_count:
                if task_progress.WasCancelled():
                    task_progress.Destroy()
                    break
                
                self.dest_area.AddFile(files[task][0], files[task][1], target_dir)
                
                task += 1
                task_progress.Update(task)
        
        else:
            for F in files:
                self.dest_area.AddFile(F[0], F[1], target_dir)
    
    
    def AddPathDeprecated(self, event):
        total_files = 0
        pin = self.dir_tree.GetPath()
        
        target_col = 1
        
        if DebugEnabled():
            target_col = 2
        
        for item in self.radio_group:
            if self.radio_cst.GetValue() == True:
                pout = self.dest_cust.GetValue()
            elif item.GetValue() == True:
                pout = item.GetLabel()
        if os.path.isdir(pin):
            for root, dirs, files in os.walk(pin):
                for F in files:
                    total_files += 1
            
            if total_files: # Continue if files are found
                cont = True
                count = 0
                msg_files = GT(u'Getting files from %s')
                loading = wx.ProgressDialog(GT(u'Progress'), msg_files % (pin), total_files, self,
                                            wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_CAN_ABORT)
                for root, dirs, files in os.walk(pin):
                    for filename in files:
                        if cont == (False,False):  # If "cancel" pressed destroy the progress window
                            break
                        else:
                            sub_dir = root.split(pin)[1] # remove full path to insert into listctrl
                            absolute_filename = u'{}/{}'.format(root, F)
                            if sub_dir != wx.EmptyString:
                                # Add the sub-dir to dest
                                dest = u'%s%s' % (pout, sub_dir)
                                
                                # Hidden list
                                self.list_data.insert(0, (absolute_filename, F, dest))
                                
                                if DebugEnabled():
                                    self.dest_area.AddItem(filename, root, pout)
                                
                                else:
                                    self.dest_area.InsertStringItem(0, filename)
                                    self.dest_area.SetStringItem(0, target_col, dest)
                            
                            else:
                                self.list_data.insert(0, (absolute_filename, F, pout))
                                self.dest_area.InsertStringItem(0, F)
                                self.dest_area.SetStringItem(0, target_col, pout)
                            count += 1
                            cont = loading.Update(count)
                            if os.access(absolute_filename, os.X_OK):
                                self.dest_area.SetItemTextColour(0, u'red')
        
        elif os.path.isfile(pin):
            filename = os.path.basename(pin)
            source_dir = os.path.dirname(pin)
            
            # Add info to unseen list
            self.list_data.insert(0, (pin, filename, pout))
            
            if DebugEnabled():
                self.dest_area.AddItem(filename, source_dir, pout)
            
            else:
                self.dest_area.InsertStringItem(0, filename)
                self.dest_area.SetStringItem(0, target_col, pout)
            
            # If file is executable, mark with red text
            if os.access(pin, os.X_OK):
                self.dest_area.SetItemTextColour(0, u'red')
    
    def OnRefresh(self, event):
        path = self.dir_tree.GetPath()
#		if isfile(path):
#			path = os.path.split(path)[0]
        
        self.dir_tree.ReCreateTree()
        self.dir_tree.SetPath(path)
    
    def SelectAll(self):
        self.dest_area.SelectAll()
    
    
    def RemoveSelected(self, event):
        self.dest_area.RemoveSelected()
    
    
    # FIXME: Deprecated; Replace with self.RemoveSelected
    def DelPathDeprecated(self, event):
        try:
            modifier = event.GetModifiers()
            keycode = event.GetKeyCode()
        except AttributeError:
            keycode = event.GetEventObject().GetId()
        
        if keycode == wx.WXK_DELETE:
            selected = [] # Items to remove from visible list
            toremove = [] # Items to remove from invisible list
            total = self.dest_area.GetSelectedItemCount()
            current = self.dest_area.GetFirstSelected()
            if current != -1:
                selected.insert(0, current)
                while total > 1:
                    total = total - 1
                    prev = current
                    current = self.dest_area.GetNextSelected(prev)
                    selected.insert(0, current)
            for path in selected:
                # Remove the item from the invisible list
                for item in self.list_data:
                    filename = self.dest_area.GetItemText(path)
                    dest = self.dest_area.GetItem(path, 1).GetText()
                    if filename.encode(u'utf-8') == item[1].decode(u'utf-8') and dest.encode(u'utf-8') == item[2].decode(u'utf-8'):
                        toremove.append(item)
                    
                self.dest_area.DeleteItem(path) # Remove the item from the visible list
            
            for item in toremove:
                self.list_data.remove(item)
            
        elif keycode == 65 and modifier == wx.MOD_CONTROL:
            self.SelectAll()
    
    
    def ClearAll(self, event):
        confirm = wx.MessageDialog(self, GT(u'Clear all files?'), GT(u'Confirm'), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_YES:
            self.dest_area.DeleteAllItems()
            self.list_data = []
    
    def SetDestination(self, event):
        # Event handler that disables the custom destination if the corresponding radio button isn't selected
        if self.radio_cst.GetValue() == True:
            self.dest_cust.Enable()
            self.dest_browse.Enable()
        else:
            self.dest_cust.Disable()
            self.dest_browse.Disable()
    
    
    def ResetAllFields(self):
        self.radio_cst.SetValue(True)
        self.SetDestination(None)
        self.dest_cust.SetValue(u'/usr/bin')
        self.dest_area.DeleteAllItems()
        self.list_data = []
    
    def SetFieldData(self, data):
        # Clear files list
        self.list_data = []
        self.dest_area.DeleteAllItems()
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
                absolute_filename = files_data[files_total].split(u' -> ')[1]
                dest = files_data[files_total].split(u' -> ')[2]
                
                # Check if files still exist
                if os.path.exists(src[0]):
                    self.dest_area.InsertStringItem(0, absolute_filename)
                    self.dest_area.SetStringItem(0, 1, dest)
                    self.list_data.insert(0, (src[0], absolute_filename, dest))
                    # Check if file is executable
                    if src[1]:
                        self.dest_area.SetItemTextColour(0, u'red') # Set text color to red
                else:
                    missing_files.append(src[0])
            
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
    #  FIXME: Deprecated
    #  \return
    #        \b \e str : A string of files & their targets formatted for text output
    def GetFilesInfoDeprecated(self):
        file_list = []
        item_count = self.dest_area.GetItemCount()
        if item_count > 0:
            count = 0
            while count < item_count:
                item_file = self.dest_area.GetItemText(count)
                item_dest = self.dest_area.GetItem(count, 1).GetText()
                for item in self.list_data:
                    # Decode to unicode
                    i0 = item[0].encode(u'utf-8')
                    i1 = item[1].decode(u'utf-8')
                    i2 = item[2].encode(u'utf-8')
                    if i1 == item_file and i2.decode(u'utf-8') == item_dest:
                        item_src = i0
                # Populate list with tuples of ("src", "file", "dest")
                if self.dest_area.GetItemTextColour(count) == (255, 0, 0):
                    file_list.append((u'%s*' % item_src, item_file, item_dest))
                else:
                    file_list.append((item_src, item_file, item_dest))
                count += 1
        
            return_list = []
            for F in file_list:
                f0 = F[0]
                f1 = F[1]
                f2 = F[2]
                return_list.append(u'%s -> %s -> %s' % (f0, f1, f2))
            
            return u'\n'.join(return_list)
        else:
            # Not files are listed
            return wx.EmptyString
    
    
    ## Legacy project file output
    #  
    #  FIXME: Deprecated
    #  Gathers info for exporting to saved project (text) file.
    #  \return
    #        \b \e str : Text-formatted file list
    def GatherData(self):
        f_info = self.GetFilesInfoDeprecated()
        f_status = u'1'
        
        if f_info == wx.EmptyString:
            f_status = u'0'
        
        return u'<<FILES>>\n{}\n{}\n<</FILES>>'.format(f_status, f_info)
    
    
    ## Retrieves information on files to be packaged
    #  
    #  FIXME: Use different style formatting instead of calling self.GetFilesInfoDeprecated()
    #  \return
    #        \b \e tuple(str, str) : A tuple containing the filename & a list of files with their targets formatted for text output
    def GetPageInfo(self):
        page_info = self.GetFilesInfoDeprecated()
        
        if not page_info:
            return None
        
        return (__name__, page_info)



## An editable list
#  
#  Creates a ListCtrl class in which every column's text can be edited
class FileList(wx.ListCtrl, wxMixinListCtrl.ListCtrlAutoWidthMixin, wxMixinListCtrl.TextEditMixin):
    def __init__(self, parent, window_id=wx.ID_ANY):
        wx.ListCtrl.__init__(self, parent, window_id,
                style=wx.BORDER_SIMPLE|wx.LC_REPORT)
        wxMixinListCtrl.ListCtrlAutoWidthMixin.__init__(self)
        wxMixinListCtrl.TextEditMixin.__init__(self)
        
        self.debreate = parent.debreate
        
        self.filename_col = 0
        self.source_col = 1
        self.target_col = 2
        
        # DEBUG:
        # TODO: Remove from DEBUG when finished
        if DebugEnabled():
            width=self.debreate.GetSize()[1]/3-10
            
            self.InsertColumn(self.filename_col, GT(u'File'), width=width)
            self.InsertColumn(self.source_col, GT(u'Source Directory'), width=width)
            self.InsertColumn(self.target_col, GT(u'Staged Target'))
            
            wx.EVT_LIST_INSERT_ITEM(self.GetChildren()[1], self.GetId(), self.OnInsertItem)
        
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)
    
    
    def OnInsertItem(self, event):
        Logger.Debug(__name__, u'FileList item inserted')
        
        children = self.GetChildren()
        
        Logger.Debug(__name__, u'Parent ID: {}'.format(self.GetId()))
        
        # Looking for the list of files
        list = None
        
        for x in range(0, len(children)):
            child = children[x]
            
            Logger.Debug(__name__, u'Child ID: {}'.format(child.GetId()))
            Logger.Debug(__name__, u'Child type: {}'.format(type(child)))
            Logger.Debug(__name__, u'Child name'.format(child.GetName()))
            
        event.Skip()
    
    
    ## Defines actions to take when left-click or left-double-click event occurs
    #  
    #  The super method is overridden to ensure that 'event.Skip' is called.
    #  TODO: Notify wxPython project of 'event.Skip' error
    def OnLeftDown(self, event=None):
        wxMixinListCtrl.TextEditMixin.OnLeftDown(self, event)
        
        event.Skip()
    
    
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
        wxMixinListCtrl.TextEditMixin.OpenEditor(self, self.target_col, row)
    
    
    def AddFile(self, filename, source_dir, target_dir):
        Logger.Debug(__name__,
            GT(u'Adding filename: {}, source: {}, target: {}'.format(
                                                                        filename, source_dir,
                                                                        target_dir
                                                                    )
            )
        )
        
        source_col = 1
        target_col = 2
        
        # FIXME: Needs to get list count first to append
        list_index = 0
        
        self.InsertStringItem(list_index, filename)
        self.SetStringItem(list_index, source_col, source_dir)
        self.SetStringItem(list_index, target_col, target_dir)
    
    
    def SelectAll(self):
        file_count = self.GetItemCount()
        
        for x in range(file_count):
            self.Select(x)
    
    
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
