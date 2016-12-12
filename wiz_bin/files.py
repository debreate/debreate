# -*- coding: utf-8 -*-

## \package wiz_bin.files

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, wx

from dbr.buttons            import ButtonAdd
from dbr.buttons            import ButtonBrowse
from dbr.buttons            import ButtonClear
from dbr.buttons            import ButtonRefresh
from dbr.buttons            import ButtonRemove
from dbr.dialogs            import DetailedMessageDialog
from dbr.dialogs            import GetDirDialog
from dbr.dialogs            import ShowDialog
from dbr.functions          import TextIsEmpty
from dbr.help               import HelpButton
from dbr.language           import GT
from dbr.listinput          import FileList
from dbr.log                import Logger
from dbr.textinput          import MultilineTextCtrlPanel
from dbr.wizard             import WizardPage
from globals                import ident
from globals.bitmaps        import ICON_ERROR
from globals.errorcodes     import dbrerrno
from globals.paths          import PATH_home
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetTopWindow


ID_pin = 100
ID_fin = 101
ID_pout = 102

ID_AddDir = 140
ID_AddFile = 141
ID_Refresh = 142


## Class defining controls for the "Paths" page
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.FILES)
        
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
        
        btn_help = HelpButton(self)
        
        # ----- Target path
        target_panel = wx.Panel(self, style=wx.BORDER_THEME)
        
        # choices of destination
        self.radio_bin = wx.RadioButton(target_panel, label=u'/bin', style=wx.RB_GROUP)
        self.radio_usrbin = wx.RadioButton(target_panel, label=u'/usr/bin')
        self.radio_usrlib = wx.RadioButton(target_panel, label=u'/usr/lib')
        self.radio_locbin = wx.RadioButton(target_panel, label=u'/usr/local/bin')
        self.radio_loclib = wx.RadioButton(target_panel, label=u'/usr/local/lib')
        self.radio_custom = wx.RadioButton(target_panel, ident.CUSTOM, GT(u'Custom'))
        
        # Start with "Custom" selected
        self.radio_custom.SetValue(True)
        
        # group buttons together
        # FIXME: Unnecessary???
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
        
        self.btn_browse = ButtonBrowse(self)
        self.btn_browse.SetName(u'browse')
        self.btn_browse.SetId(ID_pout)
        
        # TODO: Make custom button
        btn_refresh = ButtonRefresh(self)
        btn_refresh.SetName(u'refresh')
        
        # Display area for files added to list
        self.file_list = FileList(self, name=u'filelist')
        
        # List that stores the actual paths to the files
        # FIXME: Deprecated???
        self.list_data = []
        
        
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
        
        layout_buttons = wx.FlexGridSizer(cols=6)
        layout_buttons.SetFlexibleDirection(wx.HORIZONTAL)
        layout_buttons.AddGrowableCol(3)
        
        layout_buttons.Add(btn_add, 0, wx.RIGHT, 5)
        layout_buttons.Add(btn_remove, 0, wx.RIGHT, 5)
        layout_buttons.Add(btn_clear, 0, wx.RIGHT, 5)
        layout_buttons.Add(layout_input, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        layout_buttons.Add(self.btn_browse, 0, wx.RIGHT, 5)
        layout_buttons.Add(btn_refresh, 0)
        
        layout_Vright = wx.BoxSizer(wx.VERTICAL)
        layout_Vright.Add(btn_help, 0, wx.ALIGN_RIGHT|wx.TOP, 5)
        layout_Vright.Add(wx.StaticText(self, label=GT(u'Target')), 0, wx.BOTTOM, 5)
        layout_Vright.Add(target_panel, 0)
        layout_Vright.Add(layout_buttons, 0, wx.EXPAND)
        layout_Vright.Add(self.file_list, 1, wx.EXPAND, wx.TOP, 5)
        
        layout_main = wx.BoxSizer(wx.HORIZONTAL)
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
        btn_remove.Bind(wx.EVT_BUTTON, self.RemoveSelected)
        btn_clear.Bind(wx.EVT_BUTTON, self.ClearAll)
        self.btn_browse.Bind(wx.EVT_BUTTON, self.OnBrowse)
        btn_refresh.Bind(wx.EVT_BUTTON, self.OnRefreshFileList)
        
        # ???: Not sure what these do
        wx.EVT_KEY_DOWN(self.input_target, self.GetDestValue)
        wx.EVT_KEY_UP(self.input_target, self.CheckDest)
        
        # Key events for file list
        wx.EVT_KEY_DOWN(self.file_list, self.DelPathDeprecated)
    
    
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
    def ClearAll(self, event=None):
        confirm = wx.MessageDialog(self, GT(u'Clear all files?'), GT(u'Confirm'), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_YES:
            self.file_list.DeleteAllItems()
            self.list_data = []
    
    
    # FIXME: Deprecated; Replace with self.OnKeyDelete|self.OnKeyDown
    def DelPathDeprecated(self, event=None):
        try:
            modifier = event.GetModifiers()
            keycode = event.GetKeyCode()
        
        except AttributeError:
            keycode = event.GetEventObject().GetId()
        
        if keycode in (wx.ID_REMOVE, wx.WXK_DELETE):
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
    def GetDestValue(self, event=None):
        if not TextIsEmpty(self.input_target.GetValue()):
            if self.input_target.GetValue()[0] == u'/':
                self.prev_dest_value = self.input_target.GetValue()
        
        if event:
            event.Skip()
    
    
    ## Retrieve number of files in list
    def GetFileCount(self):
        return self.file_list.GetItemCount()
    
    
    ## Retrieve FileList instance
    def GetFileList(self):
        return self.file_list
    
    
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
            main_window = GetTopWindow()
            
            err_line1 = GT(u'The following files are missing from the filesystem.')
            err_line2 = GT(u'They will be highlighted on the Files page.')
            DetailedMessageDialog(main_window, title=GT(u'Warning'), icon=ICON_ERROR,
                    text=u'\n'.join((err_line1, err_line2)),
                    details=u'\n'.join(missing_files)).ShowModal()
        
        return 0
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        return not self.file_list.IsEmpty()
    
    
    ## Add a selected path to the list of files
    def OnAddPath(self, event=None):
        # List of files tuple formatted as: filename, source
        files = []
        
        source = self.dir_tree.GetPath()
        target_dir = None
        
        for target in self.targets:
            if target.GetValue():
                if target.GetId() == ident.CUSTOM:
                    target_dir = self.input_target.GetValue()
                
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
    def OnBrowse(self, event=None):
        dia = GetDirDialog(GetTopWindow(), GT(u'Choose Target Directory'))
        if ShowDialog(dia):
            self.input_target.SetValue(dia.GetPath())
    
    
    ## TODO: Doxygen
    def OnRefreshFileList(self, event=None):
        self.file_list.Refresh()
    
    
    ## TODO: Doxygen
    def OnRefreshTree(self, event=None):
        path = self.dir_tree.GetPath()
        
        self.dir_tree.ReCreateTree()
        self.dir_tree.SetPath(path)
    
    
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
    
    
    ## Resets all fields on page to default values
    #  
    #  \override dbr.wizard.Wizard.ImportPageInfo
    def ResetPageInfo(self):
        self.file_list.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SelectAll(self):
        self.file_list.SelectAll()
    
    
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
                alert_list = MultilineTextCtrlPanel(alert, style=wx.TE_READONLY)
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
    
    
    ## TODO: Doxygen
    def Destroy(self):
        self.progress_dialog.Destroy()
        self.EndModal()
        del(self)
    
    
    ## TODO: Doxygen
    def OnBorderResize(self, event=None):
        if event != None:
            # FIXME: Hack
            self.SetSize(self.progress_size)
    
    
    ## TODO: Doxygen
    def Update(self, *args, **kwargs):
        self.count_text.SetLabel(u'{} / {}'.format(args[0], self.task_count))
        self.progress.SetValue(args[0])
        
        self.count_text.Refresh()
        self.progress.Refresh()
        self.Refresh()
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Define
    def WasCancelled(self):
        return False
