# -*- coding: utf-8 -*-


import os, wx

from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonBrowse
from dbr.buttons        import ButtonClear
from dbr.buttons        import ButtonRefresh
from dbr.buttons        import ButtonRemove
from dbr.dialogs        import GetDirDialog
from dbr.dialogs        import ShowDialog
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from dbr.listinput      import FileList
from globals.ident      import ID_CUSTOM
from globals.ident      import ID_FILES
from globals.paths      import PATH_home
from globals.tooltips   import SetPageToolTips


ID_AddDir = 140
ID_AddFile = 141
ID_Refresh = 142


## Class defining controls for the "Paths" page
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_FILES, name=GT(u'Files'))
        
        self.SetScrollbars(20, 20, 0, 0)
        
        # Create a Context Menu
        self.menu = wx.Menu()
        
        self.add_dir = wx.MenuItem(self.menu, ID_AddDir, GT(u'Add Folder'))
        self.add_file = wx.MenuItem(self.menu, ID_AddFile, GT(u'Add File'))
        self.refresh = wx.MenuItem(self.menu, ID_Refresh, GT(u'Refresh'))
        
        self.menu.AppendItem(self.add_dir)
        self.menu.AppendItem(self.add_file)
        self.menu.AppendSeparator()
        self.menu.AppendItem(self.refresh)
        
        # Directory listing for importing files and folders
        self.dir_tree = wx.GenericDirCtrl(self, dir=PATH_home, size=(300,20),
                style=wx.BORDER_THEME)
        
        # ----- Target path
        target_panel = wx.Panel(self, style=wx.BORDER_THEME)
        
        # choices of destination
        self.radio_bin = wx.RadioButton(target_panel, label=u'/bin', style=wx.RB_GROUP)
        self.radio_usrbin = wx.RadioButton(target_panel, label=u'/usr/bin')
        self.radio_usrlib = wx.RadioButton(target_panel, label=u'/usr/lib')
        self.radio_locbin = wx.RadioButton(target_panel, label=u'/usr/local/bin')
        self.radio_loclib = wx.RadioButton(target_panel, label=u'/usr/local/lib')
        self.radio_custom = wx.RadioButton(target_panel, ID_CUSTOM, GT(u'Custom'))
        
        # Start with "Custom" selected
        self.radio_custom.SetValue(True)
        
        # group buttons together
        self.targets = (
            self.radio_bin,
            self.radio_usrbin,
            self.radio_usrlib,
            self.radio_locbin,
            self.radio_loclib,
            self.radio_custom,
            )
        
        # ----- Add/Remove/Clear buttons
        btn_add = ButtonAdd(self)
        btn_add.SetName(u'add')
        btn_remove = ButtonRemove(self)
        btn_remove.SetName(u'remove')
        btn_clear = ButtonClear(self)
        btn_clear.SetName(u'clear')
        
        self.prev_dest_value = u'/usr/bin'
        self.input_target = wx.TextCtrl(self, value=self.prev_dest_value, name=u'target')
        self.input_target.default = u'/usr/bin'
        
        self.btn_browse = ButtonBrowse(self)
        self.btn_browse.SetName(u'browse')
        
        btn_refresh = ButtonRefresh(self)
        btn_refresh.SetName(u'refresh')
        
        # Display area for files added to list
        self.file_list = FileList(self, name=u'filelist')
        
        # *** Layout *** #
        
        layout_target = wx.GridSizer(3, 2, 5, 5)
        for item in self.targets:
            layout_target.Add(item, 0, wx.LEFT|wx.RIGHT, 5)
        
        target_panel.SetAutoLayout(True)
        target_panel.SetSizer(layout_target)
        target_panel.Layout()
        
        # Put text input in its own sizer to force expand
        layout_input = wx.BoxSizer(wx.HORIZONTAL)
        layout_input.Add(self.input_target, 1, wx.ALIGN_CENTER_VERTICAL)
        
        layout_buttons = wx.BoxSizer(wx.HORIZONTAL)
        
        layout_buttons.Add(btn_add, 0)
        layout_buttons.Add(btn_remove, 0)
        layout_buttons.Add(btn_clear, 0)
        layout_buttons.Add(layout_input, 1, wx.ALIGN_CENTER_VERTICAL)
        layout_buttons.Add(self.btn_browse, 0)
        layout_buttons.Add(btn_refresh, 0)
        
        layout_Vright = wx.BoxSizer(wx.VERTICAL)
        layout_Vright.AddSpacer(10)
        layout_Vright.Add(wx.StaticText(self, label=GT(u'Target')), 0, wx.BOTTOM, 5)
        layout_Vright.Add(target_panel, 0)
        layout_Vright.Add(layout_buttons, 0, wx.EXPAND)
        layout_Vright.Add(self.file_list, 5, wx.EXPAND|wx.TOP, 5)
        
        layout_main = wx.FlexGridSizer(1, 2)
        layout_main.AddGrowableRow(0)
        layout_main.AddGrowableCol(1, 2)
        
        layout_main.Add(self.dir_tree, 0, wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, 5)
        layout_main.Add(layout_Vright, 1, wx.EXPAND|wx.RIGHT, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_main)
        self.Layout()
        
        
        SetPageToolTips(self)
        
        
        # *** Events *** #
        
        # create an event to enable/disable custom widget
        for item in self.targets:
            wx.EVT_RADIOBUTTON(item, wx.ID_ANY, self.SetDestination)
        
        # Context menu events for directory tree
        wx.EVT_CONTEXT_MENU(self.dir_tree, self.OnRightClickTree)
        wx.EVT_MENU(self, ID_AddDir, self.OnAddPath)
        wx.EVT_MENU(self, ID_AddFile, self.OnAddPath)
        wx.EVT_MENU(self, ID_Refresh, self.OnRefreshTree)
        
        # Button events
        btn_add.Bind(wx.EVT_BUTTON, self.OnAddPath)
        btn_remove.Bind(wx.EVT_BUTTON, self.OnRemoveSelected)
        btn_clear.Bind(wx.EVT_BUTTON, self.OnClearFileList)
        self.btn_browse.Bind(wx.EVT_BUTTON, self.OnBrowse)
        btn_refresh.Bind(wx.EVT_BUTTON, self.OnRefreshFileList)
        
        # ???: Not sure what these do
        wx.EVT_KEY_DOWN(self.input_target, self.GetDestValue)
        wx.EVT_KEY_UP(self.input_target, self.CheckDest)
        
        # Key events for file list
        wx.EVT_KEY_DOWN(self.file_list, self.OnRemoveSelected)
    
    
    ## TODO: Doxygen
    def CheckDest(self, event=None):
        if TextIsEmpty(self.input_target.GetValue()):
            self.input_target.SetValue(self.prev_dest_value)
            self.input_target.SetInsertionPoint(-1)
        
        elif self.input_target.GetValue()[0] != u'/':
            self.input_target.SetValue(self.prev_dest_value)
            self.input_target.SetInsertionPoint(-1)
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def GatherData(self):
        file_list = []
        item_count = self.file_list.GetItemCount()
        if item_count > 0:
            count = 0
            while count < item_count:
                item_file = self.file_list.GetItemText(count)
                item_dest = self.file_list.GetItem(count, 1).GetText()
                for item in self.list_data:
                    # Decode to unicode
                    i0 = item[0].encode(u'utf-8')
                    i1 = item[1].decode(u'utf-8')
                    i2 = item[2].encode(u'utf-8')
                    if i1 == item_file and i2.decode(u'utf-8') == item_dest:
                        item_src = i0
                
                # Populate list with tuples of ('src', 'file', 'dest')
                if self.file_list.GetItemTextColour(count) == (255, 0, 0):
                    file_list.append((u'{}*'.format(item_src), item_file, item_dest))
                
                else:
                    file_list.append((item_src, item_file, item_dest))
                
                count += 1
        
            return_list = []
            for FILE in file_list:
                f0 = u'{}'.encode(u'utf-8').format(FILE[0])
                f1 = u'{}'.encode(u'utf-8').format(FILE[1])
                f2 = u'{}'.encode(u'utf-8').format(FILE[2])
                return_list.append(u'{} -> {} -> {}'.format(f0, f1, f2))
            
            return u'<<FILES>>\n1\n{}\n<</FILES>>'.format(u'\n'.join(return_list))
        
        else:
            # Place a "0" in FILES field if we are not saving any files
            return u'<<FILES>>\n0\n<</FILES>>'
    
    
    ## TODO: Doxygen
    def GetDestValue(self, event=None):
        if not TextIsEmpty(self.input_target.GetValue()):
            if self.input_target.GetValue()[0] == u'/':
                self.prev_dest_value = self.input_target.GetValue()
        
        if event:
            event.Skip()
    
    
    ## Add a selected path to the list of files
    def OnAddPath(self, event=None):
        total_files = 0
        pin = self.dir_tree.GetPath()
        
        for item in self.targets:
            if self.radio_custom.GetValue() == True:
                pout = self.input_target.GetValue()
                
                break
            
            elif item.GetValue() == True:
                pout = item.GetLabel()
                
                break
        
        if os.path.isdir(pin):
            for root, dirs, files in os.walk(pin):
                for FILE in files:
                    total_files += 1
            
            if total_files: # Continue if files are found
                cont = True
                count = 0
                msg_files = GT(u'Getting files from {}')
                task_progress = wx.ProgressDialog(GT(u'Progress'), msg_files.format(pin), total_files, self,
                                            wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_CAN_ABORT)
                
                for source_dir, DIRS, FILES in os.walk(pin):
                    for filename in FILES:
                        # If "cancel" pressed destroy the progress window
                        if cont == (False, False):
                            task_progress.Destroy()
                            return
                        
                        else:
                            # Remove full path to insert into listctrl
                            target_dir = source_dir.split(pin)[1]
                            if not TextIsEmpty(target_dir):
                                # Add the sub-dir to dest
                                target_dir = u'{}{}'.format(pout, target_dir)
                                
                                self.file_list.AddFile(filename, source_dir, target_dir)
                            
                            else:
                                self.file_list.AddFile(filename, source_dir, pout)
                            
                            count += 1
                            cont = task_progress.Update(count)
                
                task_progress.Destroy()
        
        elif os.path.isfile(pin):
            filename = os.path.basename(pin)
            source_dir = os.path.dirname(pin)
            
            self.file_list.AddFile(filename, source_dir, pout)
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event=None):
        dia = GetDirDialog(wx.GetApp().GetTopWindow(), GT(u'Choose Target Directory'))
        if ShowDialog(dia):
            self.input_target.SetValue(dia.GetPath())
    
    
    ## TODO: Doxygen
    def OnClearFileList(self, event=None):
        confirm = wx.MessageDialog(self, GT(u'Clear all files?'), GT(u'Confirm'), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_YES:
            self.file_list.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def OnRefreshFileList(self, event=None):
        self.file_list.RefreshFileList()
    
    
    ## TODO: Doxygen
    def OnRefreshTree(self, event=None):
        path = self.dir_tree.GetPath()
        
        self.dir_tree.ReCreateTree()
        self.dir_tree.SetPath(path)
    
    
    ## TODO: Doxygen
    def OnRemoveSelected(self, event=None):
        try:
            modifier = event.GetModifiers()
            keycode = event.GetKeyCode()
        
        except AttributeError:
            keycode = event.GetEventObject().GetId()
        
        if keycode == wx.WXK_DELETE:
            self.file_list.RemoveSelected()
        
        elif keycode == 65 and modifier == wx.MOD_CONTROL:
            self.file_list.SelectAll()
    
    
    ## TODO: Doxygen
    def OnRightClickTree(self, event=None):
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
    def RemoveSelected(self, event=None):
        self.file_list.RemoveSelected()
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.radio_custom.SetValue(True)
        self.SetDestination(None)
        self.input_target.SetValue(self.input_target.default)
        self.file_list.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SetDestination(self, event=None):
        # Event handler that disables the custom destination if the corresponding radio button isn't selected
        if self.radio_custom.GetValue() == True:
            self.input_target.Enable()
            self.btn_browse.Enable()
        
        else:
            self.input_target.Disable()
            self.btn_browse.Disable()
    
    
    ## TODO: Doxygen
    def SetFieldData(self, data):
        # Clear files list
        self.file_list.DeleteAllItems()
        files_data = data.split(u'\n')
        if int(files_data[0]):
            # Get file count from list minus first item "1"
            files_total = len(files_data)
            
            # Store missing files here
            missing_files = []
            
            while files_total > 1:
                files_total -= 1
                executable = False
                
                absolute_filename = files_data[files_total].split(u' -> ')[0]
                
                if absolute_filename[-1] == u'*':
                    # Set executable flag and remove "*"
                    executable = True
                    absolute_filename = absolute_filename[:-1]
                
                filename = os.path.basename(absolute_filename)
                source_dir = os.path.dirname(absolute_filename)
                target_dir = files_data[files_total].split(u' -> ')[2]
                
                self.file_list.AddFile(filename, source_dir, target_dir, executable)
                
                # Check if files still exist
                if not os.path.exists(absolute_filename):
                    missing_files.append(absolute_filename)
            
            # If files are missing show a message
            if len(missing_files):
                alert = wx.Dialog(self, title=GT(u'Missing Files'))
                alert_text = wx.StaticText(alert, label=GT(u'Could not locate the following files:'))
                alert_list = wx.TextCtrl(alert, style=wx.TE_MULTILINE|wx.TE_READONLY)
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
