# -*- coding: utf-8 -*-

## \package wiz_bin.files

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, traceback, wx

from dbr.language           import GT
from dbr.log                import Logger
from globals                import ident
from globals.bitmaps        import ICON_ERROR
from globals.bitmaps        import ICON_EXCLAMATION
from globals.errorcodes     import dbrerrno
from globals.fileio         import ReadFile
from globals.ident          import pgid
from globals.paths          import ConcatPaths
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import FieldEnabled
from globals.wizardhelper   import GetMainWindow
from input.list             import FileListESS
from ui.button              import ButtonAdd
from ui.button              import ButtonBrowse
from ui.button              import ButtonClear
from ui.button              import ButtonRefresh
from ui.button              import ButtonRemove
from ui.dialog              import ConfirmationDialog
from ui.dialog              import DetailedMessageDialog
from ui.dialog              import GetDirDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.dialog              import ShowMessageDialog
from ui.layout              import BoxSizer
from ui.panel               import BorderedPanel
from ui.progress            import PD_DEFAULT_STYLE
from ui.progress            import ProgressDialog
from ui.tree                import DirectoryTreePanel
from ui.wizard              import WizardPage


# Set the maximum file count to process without showing progress dialog
efficiency_threshold = 250

# Set the maximum file count to process without showing warning dialog
warning_threshhold = 1000


## Class defining controls for the "Paths" page
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.FILES)
        
        # *** Left Panel *** #
        
        pnl_treeopts = BorderedPanel(self)
        
        self.chk_individuals = wx.CheckBox(pnl_treeopts, label=GT(u'List files individually'),
                name=u'individually')
        self.chk_individuals.default = False
        
        self.chk_preserve_top = wx.CheckBox(pnl_treeopts, label=GT(u'Preserve top-level directories'),
                name=u'top-level')
        self.chk_preserve_top.default = False
        
        self.tree_dirs = DirectoryTreePanel(self, size=(300,20))
        
        # ----- Target path
        pnl_target = BorderedPanel(self)
        
        # choices of destination
        rb_bin = wx.RadioButton(pnl_target, label=u'/bin', style=wx.RB_GROUP)
        rb_usrbin = wx.RadioButton(pnl_target, label=u'/usr/bin')
        rb_usrlib = wx.RadioButton(pnl_target, label=u'/usr/lib')
        rb_locbin = wx.RadioButton(pnl_target, label=u'/usr/local/bin')
        rb_loclib = wx.RadioButton(pnl_target, label=u'/usr/local/lib')
        self.rb_custom = wx.RadioButton(pnl_target, ident.F_CUSTOM, GT(u'Custom'))
        self.rb_custom.default = True
        
        # Start with "Custom" selected
        self.rb_custom.SetValue(self.rb_custom.default)
        
        # group buttons together
        # FIXME: Unnecessary???
        self.grp_targets = (
            rb_bin,
            rb_usrbin,
            rb_usrlib,
            rb_locbin,
            rb_loclib,
            self.rb_custom,
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
        self.lst_files = FileListESS(self, ident.F_LIST, name=u'filelist')
        
        # *** Event Handling *** #
        
        # create an event to enable/disable custom widget
        for item in self.grp_targets:
            wx.EVT_RADIOBUTTON(item, wx.ID_ANY, self.OnSetDestination)
        
        # Context menu events for directory tree
        wx.EVT_MENU(self, wx.ID_ADD, self.OnImportFromTree)
        
        # Button events
        btn_add.Bind(wx.EVT_BUTTON, self.OnImportFromTree)
        btn_remove.Bind(wx.EVT_BUTTON, self.OnRemoveSelected)
        btn_clear.Bind(wx.EVT_BUTTON, self.OnClearFileList)
        self.btn_browse.Bind(wx.EVT_BUTTON, self.OnBrowse)
        btn_refresh.Bind(wx.EVT_BUTTON, self.OnRefreshFileList)
        
        # ???: Not sure what these do
        wx.EVT_KEY_DOWN(self.ti_target, self.GetDestValue)
        wx.EVT_KEY_UP(self.ti_target, self.CheckDest)
        
        # Key events for file list
        wx.EVT_KEY_DOWN(self.lst_files, self.OnRemoveSelected)
        
        self.Bind(wx.EVT_DROP_FILES, self.OnDropFiles)
        
        # *** Layout *** #
        
        lyt_treeopts = BoxSizer(wx.VERTICAL)
        lyt_treeopts.AddSpacer(5)
        lyt_treeopts.Add(self.chk_individuals, 0, wx.LEFT|wx.RIGHT, 5)
        lyt_treeopts.Add(self.chk_preserve_top, 0, wx.LEFT|wx.RIGHT, 5)
        lyt_treeopts.AddSpacer(5)
        
        pnl_treeopts.SetSizer(lyt_treeopts)
        
        lyt_left = BoxSizer(wx.VERTICAL)
        lyt_left.AddSpacer(10)
        lyt_left.Add(wx.StaticText(self, label=GT(u'Directory options')), 0, wx.ALIGN_BOTTOM)
        lyt_left.Add(pnl_treeopts, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.BOTTOM, 5)
        lyt_left.Add(self.tree_dirs, 1, wx.EXPAND)
        
        lyt_target = wx.GridSizer(3, 2, 5, 5)
        
        for item in self.grp_targets:
            lyt_target.Add(item, 0, wx.LEFT|wx.RIGHT, 5)
        
        pnl_target.SetAutoLayout(True)
        pnl_target.SetSizer(lyt_target)
        pnl_target.Layout()
        
        # Put text input in its own sizer to force expand
        lyt_input = BoxSizer(wx.HORIZONTAL)
        lyt_input.Add(self.ti_target, 1, wx.ALIGN_CENTER_VERTICAL)
        
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_add, 0)
        lyt_buttons.Add(btn_remove, 0)
        lyt_buttons.Add(btn_clear, 0)
        lyt_buttons.Add(lyt_input, 1, wx.ALIGN_CENTER_VERTICAL)
        lyt_buttons.Add(self.btn_browse, 0)
        lyt_buttons.Add(btn_refresh, 0)
        
        lyt_right = BoxSizer(wx.VERTICAL)
        lyt_right.AddSpacer(10)
        lyt_right.Add(wx.StaticText(self, label=GT(u'Target')))
        lyt_right.Add(pnl_target, 0, wx.TOP, 5)
        lyt_right.Add(lyt_buttons, 0, wx.EXPAND)
        lyt_right.Add(self.lst_files, 5, wx.EXPAND|wx.TOP, 5)
        
        PROP_LEFT = 0
        PROP_RIGHT = 1
        
        lyt_main = wx.FlexGridSizer(1, 2)
        lyt_main.AddGrowableRow(0)
        
        # Directory tree size issues with wx 2.8
        if wx.MAJOR_VERSION <= 2:
            PROP_LEFT = 1
            lyt_main.AddGrowableCol(0, 1)
        
        lyt_main.AddGrowableCol(1, 2)
        lyt_main.Add(lyt_left, PROP_LEFT, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        lyt_main.Add(lyt_right, PROP_RIGHT, wx.EXPAND|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        SetPageToolTips(self)
    
    
    ## Adds files to the list
    #  
    #  \param dirs
    #    \b \e dict : dict[dir] = [file list]
    #  \param show_dialog
    #    \b \e bool : If True, shows a progress dialog
    def AddPaths(self, dirs, file_count=None, show_dialog=False):
        target = self.GetTarget()
        
        if file_count == None:
            file_count = 0
            for D in dirs:
                for F in dirs[D]:
                    file_count += 1
        
        progress = None
        
        Logger.Debug(__name__, u'Adding {} files ...'.format(file_count))
        
        if show_dialog:
            progress = ProgressDialog(GetMainWindow(), GT(u'Adding Files'), maximum=file_count,
                    style=PD_DEFAULT_STYLE|wx.PD_CAN_ABORT)
            progress.Show()
        
        completed = 0
        for D in sorted(dirs):
            for F in sorted(dirs[D]):
                if progress and progress.WasCancelled():
                    progress.Destroy()
                    return False
                
                if progress:
                    wx.Yield()
                    progress.Update(completed, GT(u'Adding file {}').format(F))
                
                self.lst_files.AddFile(F, D, target)
                
                completed += 1
        
        if progress:
            wx.Yield()
            progress.Update(completed)
            
            progress.Destroy()
        
        return True
    
    
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
    def ExportBuild(self, target):
        if not os.path.isdir(target):
            return (dbrerrno.ENOENT, GT(u'Target directory does not exist: {}').format(target))
        
        if self.lst_files.MissingFiles():
            return (dbrerrno.ENOENT, GT(u'Missing files in file list'))
        
        file_count = self.lst_files.GetItemCount()
        for R in range(file_count):
            filename, source_dir, stage_dir, executable = self.lst_files.GetRowData(R)
            
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
    
    
    ## Retrieves information on files to be packaged
    #  
    #  \return
    #        \b \e tuple(str, str) : A tuple containing the filename & a list of files with their targets formatted for text output
    def Get(self, get_module=False):
        item_count = self.lst_files.GetItemCount()
        
        if not item_count:
            page = None
        
        else:
            files_definitions = {}
            for X in range(item_count):
                row_data = self.lst_files.GetRowData(X)
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
            
            page = u'\n'.join(files_data)
        
        if get_module:
            page = (__name__, page,)
        
        return page
    
    
    ## TODO: Doxygen
    def GetDestValue(self, event=None):
        if not TextIsEmpty(self.ti_target.GetValue()):
            if self.ti_target.GetValue()[0] == u'/':
                self.prev_dest_value = self.ti_target.GetValue()
        
        if event:
            event.Skip()
    
    
    ## Retrieve DirectoryTreePanel instance
    #  
    #  Used in input.list.FileList for referencing size
    def GetDirTreePanel(self):
        return self.tree_dirs
    
    
    ## Retrieve number of files in list
    def GetFileCount(self):
        return self.lst_files.GetItemCount()
    
    
    ## Retrieves FileList instances
    def GetListInstance(self):
        return self.lst_files
    
    
    ## Retrieves the target output directory
    def GetTarget(self):
        if FieldEnabled(self.ti_target):
            return self.ti_target.GetValue()
        
        for target in self.grp_targets:
            if target.GetId() != ident.F_CUSTOM and target.GetValue():
                return target.GetLabel()
    
    
    ## TODO: Doxygen
    #  
    #  \override ui.wizard.Wizard.ImportFromFile
    def ImportFromFile(self, filename):
        Logger.Debug(__name__, GT(u'Importing page info from {}').format(filename))
        
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        files_data = ReadFile(filename, split=True)
        
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
            # FIXME: Create method in FileList class to retrieve all missing files
            if not os.path.exists(T[1]):
                missing_files.append(T[1])
            
            source_file = os.path.basename(T[1])
            source_dir = os.path.dirname(T[1])
            
            self.lst_files.AddFile(source_file, source_dir, T[0], executable=T[2])
        
        if len(missing_files):
            main_window = GetMainWindow()
            
            err_line1 = GT(u'The following files/folders are missing from the filesystem.')
            err_line2 = GT(u'They will be highlighted on the Files page.')
            DetailedMessageDialog(main_window, title=GT(u'Warning'), icon=ICON_ERROR,
                    text=u'\n'.join((err_line1, err_line2)),
                    details=u'\n'.join(missing_files)).ShowModal()
        
        return 0
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        return not self.lst_files.IsEmpty()
    
    
    ## Reads files & directories & preps for loading into list
    #  
    #  \param paths_list
    #    \b \e tuple|list : List of string values of files & directories to be added
    def LoadPaths(self, paths_list):
        if isinstance(paths_list, tuple):
            paths_list = list(paths_list)
        
        if not paths_list or not isinstance(paths_list, list):
            return False
        
        file_list = []
        dir_list = {}
        
        prep = ProgressDialog(GetMainWindow(), GT(u'Processing Files'), GT(u'Scanning files ...'),
                style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
        
        # Only update the gauge every N files (hack until I figure out timer)
        update_interval = 450
        count = 0
        
        prep.Show()
        
        if not self.chk_preserve_top.GetValue():
            for INDEX in reversed(range(len(paths_list))):
                path = paths_list[INDEX]
                if os.path.isdir(path):
                    # Remove top-level directory from list
                    paths_list.pop(INDEX)
                    
                    insert_index = INDEX
                    for P in os.listdir(path):
                        paths_list.insert(insert_index, ConcatPaths((path, P)))
                        insert_index += 1
        
        try:
            for P in paths_list:
                if prep.WasCancelled():
                    prep.Destroy()
                    return False
                
                count += 1
                if count >= update_interval:
                    wx.Yield()
                    prep.Pulse()
                    count = 0
                
                if not self.chk_individuals.GetValue() or os.path.isfile(P):
                    file_list.append(P)
                    continue
                
                if os.path.isdir(P):
                    parent_dir = os.path.dirname(P)
                    
                    if parent_dir not in dir_list:
                        dir_list[parent_dir] = []
                    
                    for ROOT, DIRS, FILES in os.walk(P):
                        if prep.WasCancelled():
                            prep.Destroy()
                            return False
                        
                        wx.Yield()
                        prep.SetMessage(GT(u'Scanning directory {} ...').format(ROOT))
                        
                        count += 1
                        if count >= update_interval:
                            wx.Yield()
                            prep.Pulse()
                            count = 0
                        
                        for F in FILES:
                            if prep.WasCancelled():
                                prep.Destroy()
                                return False
                            
                            count += 1
                            if count >= update_interval:
                                wx.Yield()
                                prep.Pulse()
                                count = 0
                            
                            # os.path.dirname preserves top level directory
                            ROOT = ROOT.replace(os.path.dirname(P), u'').strip(u'/')
                            F = u'{}/{}'.format(ROOT, F).strip(u'/')
                            
                            if F not in dir_list[parent_dir]:
                                dir_list[parent_dir].append(F)
        
        except:
            prep.Destroy()
            
            ShowErrorDialog(GT(u'Could not retrieve file list'), traceback.format_exc())
            
            return False
        
        wx.Yield()
        prep.Pulse(GT(u'Counting Files'))
        
        file_count = len(file_list)
        
        count = 0
        for D in dir_list:
            for F in dir_list[D]:
                file_count += 1
                
                count += 1
                if count >= update_interval:
                    wx.Yield()
                    prep.Pulse()
                    count = 0
        
        prep.Destroy()
        
        # Add files to directory list
        for F in file_list:
            f_name = os.path.basename(F)
            f_dir = os.path.dirname(F)
            
            if f_dir not in dir_list:
                dir_list[f_dir] = []
            
            dir_list[f_dir].append(f_name)
        
        if file_count > warning_threshhold:
            count_warnmsg = GT(u'Importing {} files'.format(file_count))
            count_warnmsg = u'{}. {}.'.format(count_warnmsg, GT(u'This could take a VERY long time'))
            count_warnmsg = u'{}\n{}'.format(count_warnmsg, GT(u'Are you sure you want to continue?'))
            
            if not ConfirmationDialog(GetMainWindow(), text=count_warnmsg).Confirmed():
                return False
        
        return self.AddPaths(dir_list, file_count, show_dialog=file_count >= efficiency_threshold)
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event=None):
        dia = GetDirDialog(GetMainWindow(), GT(u'Choose Target Directory'))
        if ShowDialog(dia):
            self.ti_target.SetValue(dia.GetPath())
    
    
    ## TODO: Doxygen
    def OnClearFileList(self, event=None):
        if self.lst_files.GetItemCount():
            if ConfirmationDialog(GetMainWindow(), GT(u'Confirm'),
                        GT(u'Clear all files?')).Confirmed():
                self.lst_files.DeleteAllItems()
    
    
    ## Adds files to list from file manager drop
    #  
    #  FIXME: Need method AddDirectory or AddFileList (No longer needed???)
    def OnDropFiles(self, file_list):
        self.LoadPaths(file_list)
    
    
    ## Files & directories added from directory tree
    def OnImportFromTree(self, event=None):
        self.LoadPaths(self.DirTree.GetSelectedPaths())
    
    
    ## TODO: Doxygen
    def OnRefreshFileList(self, event=None):
        self.lst_files.RefreshFileList()
    
    
    ## TODO: Doxygen
    def OnRemoveSelected(self, event=None):
        try:
            modifier = event.GetModifiers()
            keycode = event.GetKeyCode()
        
        except AttributeError:
            keycode = event.GetEventObject().GetId()
        
        if keycode in (wx.ID_REMOVE, wx.WXK_DELETE):
            self.lst_files.RemoveSelected()
        
        elif keycode == 65 and modifier == wx.MOD_CONTROL:
            self.lst_files.SelectAll()
    
    
    ## Event handler that disables the custom destination if the corresponding radio button isn't selected
    def OnSetDestination(self, event=None):
        enable = self.rb_custom.GetValue()
        
        self.ti_target.Enable(enable)
        self.btn_browse.Enable(enable)
    
    
    ## Resets all fields on page to default values
    #  
    #  \override ui.wizard.Wizard.ImportFromFile
    def Reset(self):
        self.lst_files.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SelectAll(self):
        self.lst_files.SelectAll()
    
    
    ## TODO: Doxygen
    def Set(self, data):
        # Clear files list
        self.lst_files.DeleteAllItems()
        files_data = data.split(u'\n')
        if int(files_data[0]):
            # Get file count from list minus first item "1"
            files_total = len(files_data)
            
            # Store missing files here
            missing_files = []
            
            progress = None
            
            if files_total >= efficiency_threshold:
                progress = ProgressDialog(GetMainWindow(), GT(u'Adding Files'), maximum=files_total,
                        style=PD_DEFAULT_STYLE|wx.PD_CAN_ABORT)
                
                wx.Yield()
                progress.Show()
            
            current_file = files_total
            while current_file > 1:
                if progress and progress.WasCancelled():
                    progress.Destroy()
                    
                    # Project continues opening even if file import is cancelled
                    msg = (
                        GT(u'File import did not complete.'),
                        GT(u'Project files may be missing in file list.'),
                        )
                    
                    ShowMessageDialog(u'\n'.join(msg), GT(u'Import Cancelled'))
                    
                    return False
                
                current_file -= 1
                executable = False
                
                absolute_filename = files_data[current_file].split(u' -> ')[0]
                
                if absolute_filename[-1] == u'*':
                    # Set executable flag and remove "*"
                    executable = True
                    absolute_filename = absolute_filename[:-1]
                
                filename = os.path.basename(absolute_filename)
                source_dir = os.path.dirname(absolute_filename)
                target_dir = files_data[current_file].split(u' -> ')[2]
                
                if not self.lst_files.AddFile(filename, source_dir, target_dir, executable):
                    Logger.Warn(__name__, GT(u'File not found: {}').format(absolute_filename))
                    missing_files.append(absolute_filename)
                
                if progress:
                    update_value = files_total - current_file
                    
                    wx.Yield()
                    progress.Update(update_value+1, GT(u'Imported file {} of {}').format(update_value, files_total))
            
            if progress:
                progress.Destroy()
            
            Logger.Debug(__name__, u'Missing file count: {}'.format(len(missing_files)))
            
            # If files are missing show a message
            if missing_files:
                alert = DetailedMessageDialog(GetMainWindow(), GT(u'Missing Files'),
                        ICON_EXCLAMATION, GT(u'Could not locate the following files:'),
                        u'\n'.join(missing_files))
                alert.ShowModal()
            
            return True
