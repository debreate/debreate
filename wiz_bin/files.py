# -*- coding: utf-8 -*-

## \package wiz_bin.files

# MIT licensing
# See: docs/LICENSE.txt


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
from dbr.panel          import BorderedPanel
from globals.ident      import FID_CUSTOM
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
        self.mnu_tree = wx.Menu()
        
        self.mitm_adddir = wx.MenuItem(self.mnu_tree, ID_AddDir, GT(u'Add Folder'))
        self.mitm_addfile = wx.MenuItem(self.mnu_tree, ID_AddFile, GT(u'Add File'))
        mitm_refresh = wx.MenuItem(self.mnu_tree, ID_Refresh, GT(u'Refresh'))
        
        self.mnu_tree.AppendItem(self.mitm_adddir)
        self.mnu_tree.AppendItem(self.mitm_addfile)
        self.mnu_tree.AppendSeparator()
        self.mnu_tree.AppendItem(mitm_refresh)
        
        # Directory listing for importing files and folders
        self.tree_directories = wx.GenericDirCtrl(self, dir=PATH_home, size=(300,20),
                style=wx.BORDER_THEME)
        
        # ----- Target path
        pnl_target = BorderedPanel(self)
        
        # choices of destination
        rb_bin = wx.RadioButton(pnl_target, label=u'/bin', style=wx.RB_GROUP)
        rb_usrbin = wx.RadioButton(pnl_target, label=u'/usr/bin')
        rb_usrlib = wx.RadioButton(pnl_target, label=u'/usr/lib')
        rb_locbin = wx.RadioButton(pnl_target, label=u'/usr/local/bin')
        rb_loclib = wx.RadioButton(pnl_target, label=u'/usr/local/lib')
        self.rb_custom = wx.RadioButton(pnl_target, FID_CUSTOM, GT(u'Custom'))
        self.rb_custom.default = True
        
        # Start with "Custom" selected
        self.rb_custom.SetValue(self.rb_custom.default)
        
        # group buttons together
        self.grp_targets = (
            rb_bin,
            rb_usrbin,
            rb_usrlib,
            rb_locbin,
            rb_loclib,
            )
        
        # ----- Add/Remove/Clear buttons
        btn_add = ButtonAdd(self)
        btn_remove = ButtonRemove(self)
        btn_clear = ButtonClear(self)
        
        self.prev_dest_value = u'/usr/bin'
        self.ti_target = wx.TextCtrl(self, value=self.prev_dest_value, name=u'target')
        self.ti_target.default = u'/usr/bin'
        
        self.btn_browse = ButtonBrowse(self)
        
        btn_refresh = ButtonRefresh(self)
        
        # Display area for files added to list
        self.lst_files = FileList(self, name=u'filelist')
        
        # *** Layout *** #
        
        lyt_target = wx.GridSizer(3, 2, 5, 5)
        
        for item in self.grp_targets:
            lyt_target.Add(item, 0, wx.LEFT|wx.RIGHT, 5)
        
        lyt_target.Add(self.rb_custom, 0, wx.LEFT|wx.RIGHT, 5)
        
        pnl_target.SetAutoLayout(True)
        pnl_target.SetSizer(lyt_target)
        pnl_target.Layout()
        
        # Put text input in its own sizer to force expand
        lyt_input = wx.BoxSizer(wx.HORIZONTAL)
        lyt_input.Add(self.ti_target, 1, wx.ALIGN_CENTER_VERTICAL)
        
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        
        lyt_buttons.Add(btn_add, 0)
        lyt_buttons.Add(btn_remove, 0)
        lyt_buttons.Add(btn_clear, 0)
        lyt_buttons.Add(lyt_input, 1, wx.ALIGN_CENTER_VERTICAL)
        lyt_buttons.Add(self.btn_browse, 0)
        lyt_buttons.Add(btn_refresh, 0)
        
        lyt_right = wx.BoxSizer(wx.VERTICAL)
        lyt_right.AddSpacer(10)
        lyt_right.Add(wx.StaticText(self, label=GT(u'Target')), 0, wx.BOTTOM, 5)
        lyt_right.Add(pnl_target, 0)
        lyt_right.Add(lyt_buttons, 0, wx.EXPAND)
        lyt_right.Add(self.lst_files, 5, wx.EXPAND|wx.TOP, 5)
        
        lyt_main = wx.FlexGridSizer(1, 2)
        lyt_main.AddGrowableRow(0)
        lyt_main.AddGrowableCol(1, 2)
        
        lyt_main.Add(self.tree_directories, 0, wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, 5)
        lyt_main.Add(lyt_right, 1, wx.EXPAND|wx.RIGHT, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        SetPageToolTips(self)
        
        # *** Event handlers *** #
        
        # create an event to enable/disable custom widget
        for item in self.grp_targets:
            wx.EVT_RADIOBUTTON(item, wx.ID_ANY, self.SetDestination)
        
        # Context menu events for directory tree
        wx.EVT_CONTEXT_MENU(self.tree_directories, self.OnRightClickTree)
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
        wx.EVT_KEY_DOWN(self.ti_target, self.GetDestValue)
        wx.EVT_KEY_UP(self.ti_target, self.CheckDest)
        
        # Key events for file list
        wx.EVT_KEY_DOWN(self.lst_files, self.OnRemoveSelected)
    
    
    ## TODO: Doxygen
    def CheckDest(self, event=None):
        if TextIsEmpty(self.ti_target.GetValue()):
            self.ti_target.SetValue(self.prev_dest_value)
            self.ti_target.SetInsertionPoint(-1)
        
        elif self.ti_target.GetValue()[0] != u'/':
            self.ti_target.SetValue(self.prev_dest_value)
            self.ti_target.SetInsertionPoint(-1)
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def GatherData(self):
        file_list = []
        item_count = self.lst_files.GetItemCount()
        if item_count > 0:
            count = 0
            while count < item_count:
                item_file = self.lst_files.GetItemText(count)
                item_dest = self.lst_files.GetItem(count, 1).GetText()
                for item in self.list_data:
                    # Decode to unicode
                    i0 = item[0].encode(u'utf-8')
                    i1 = item[1].decode(u'utf-8')
                    i2 = item[2].encode(u'utf-8')
                    if i1 == item_file and i2.decode(u'utf-8') == item_dest:
                        item_src = i0
                
                # Populate list with tuples of ('src', 'file', 'dest')
                if self.lst_files.GetItemTextColour(count) == (255, 0, 0):
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
        if not TextIsEmpty(self.ti_target.GetValue()):
            if self.ti_target.GetValue()[0] == u'/':
                self.prev_dest_value = self.ti_target.GetValue()
        
        if event:
            event.Skip()
    
    
    ## Add a selected path to the list of files
    def OnAddPath(self, event=None):
        total_files = 0
        pin = self.tree_directories.GetPath()
        
        if self.rb_custom.GetValue():
            pout = self.ti_target.GetValue()
        
        else:
            for item in self.grp_targets:
                if item.GetValue() == True:
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
                                
                                self.lst_files.AddFile(filename, source_dir, target_dir)
                            
                            else:
                                self.lst_files.AddFile(filename, source_dir, pout)
                            
                            count += 1
                            cont = task_progress.Update(count)
                
                task_progress.Destroy()
        
        elif os.path.isfile(pin):
            filename = os.path.basename(pin)
            source_dir = os.path.dirname(pin)
            
            self.lst_files.AddFile(filename, source_dir, pout)
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event=None):
        dia = GetDirDialog(wx.GetApp().GetTopWindow(), GT(u'Choose Target Directory'))
        if ShowDialog(dia):
            self.ti_target.SetValue(dia.GetPath())
    
    
    ## TODO: Doxygen
    def OnClearFileList(self, event=None):
        confirm = wx.MessageDialog(self, GT(u'Clear all files?'), GT(u'Confirm'), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_YES:
            self.lst_files.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def OnRefreshFileList(self, event=None):
        self.lst_files.RefreshFileList()
    
    
    ## TODO: Doxygen
    def OnRefreshTree(self, event=None):
        path = self.tree_directories.GetPath()
        
        self.tree_directories.ReCreateTree()
        self.tree_directories.SetPath(path)
    
    
    ## TODO: Doxygen
    def OnRemoveSelected(self, event=None):
        try:
            modifier = event.GetModifiers()
            keycode = event.GetKeyCode()
        
        except AttributeError:
            keycode = event.GetEventObject().GetId()
        
        if keycode == wx.WXK_DELETE:
            self.lst_files.RemoveSelected()
        
        elif keycode == 65 and modifier == wx.MOD_CONTROL:
            self.lst_files.SelectAll()
    
    
    ## TODO: Doxygen
    def OnRightClickTree(self, event=None):
        # Show a context menu for adding files and folders
        path = self.tree_directories.GetPath()
        if os.path.isdir(path):
            self.mitm_adddir.Enable(True)
            self.mitm_addfile.Enable(False)
        
        elif os.path.isfile(path):
            self.mitm_adddir.Enable(False)
            self.mitm_addfile.Enable(True)
        
        self.tree_directories.PopupMenu(self.mnu_tree)
    
    
    ## TODO: Doxygen
    def RemoveSelected(self, event=None):
        self.lst_files.RemoveSelected()
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.rb_custom.SetValue(self.rb_custom.default)
        self.SetDestination(None)
        self.ti_target.SetValue(self.ti_target.default)
        self.lst_files.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SetDestination(self, event=None):
        # Event handler that disables the custom destination if the corresponding radio button isn't selected
        if self.rb_custom.GetValue() == True:
            self.ti_target.Enable()
            self.btn_browse.Enable()
        
        else:
            self.ti_target.Disable()
            self.btn_browse.Disable()
    
    
    ## TODO: Doxygen
    def SetFieldData(self, data):
        # Clear files list
        self.lst_files.DeleteAllItems()
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
                
                self.lst_files.AddFile(filename, source_dir, target_dir, executable)
                
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
