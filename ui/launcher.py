# -*- coding: utf-8 -*-

## \package ui.launcher

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, wx
from wx.combo import OwnerDrawnComboBox

from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from globals.errorcodes     import dbrerrno
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.ident          import inputid
from globals.ident          import page_ids
from globals.strings        import GS
from globals.strings        import TextIsEmpty
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetMainWindow
from input.list             import ListCtrlBase
from input.list             import ListCtrlPanel
from input.list             import ListCtrlPanelESS
from input.select           import ComboBoxESS
from input.text             import TextAreaESS
from input.text             import TextAreaPanelESS
from input.toggle           import CheckBoxESS
from ui.button              import ButtonAdd
from ui.button              import ButtonBrowse
from ui.button              import ButtonClear
from ui.button              import ButtonPreview
from ui.button              import ButtonRemove
from ui.button              import ButtonSave
from ui.dialog              import ConfirmationDialog
from ui.dialog              import GetFileOpenDialog
from ui.dialog              import GetFileSaveDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.panel               import ScrolledPanel
from ui.textpreview         import TextPreview
from ui.wizard              import WizardPage


## Template for individual launchers
class LauncherTemplate(ScrolledPanel):
    def __init__(self, parent, win_id=wx.ID_ANY, name=u'launcher'):
        ScrolledPanel.__init__(self, parent, win_id, name=name)
        
        # --- Buttons to open/preview/save .desktop file
        btn_open = ButtonBrowse(self)
        btn_open.SetName(u'open')
        
        btn_save = ButtonSave(self)
        btn_save.SetName(u'export')
        
        btn_preview = ButtonPreview(self)
        btn_preview.SetName(u'preview')
        
        # --- TYPE
        opts_type = (u'Application', u'Link', u'Directory',)
        
        txt_type = wx.StaticText(self, label=GT(u'Type'), name=u'type')
        self.ti_type = ComboBoxESS(self, inputid.TYPE, opts_type[0], choices=opts_type,
                name=u'Type')
        self.ti_type.default = self.ti_type.GetValue()
        
        # --- ENCODING
        opts_enc = (
            u'UTF-1', u'UTF-7', u'UTF-8', u'CESU-8', u'UTF-EBCDIC',
            u'UTF-16', u'UTF-32', u'SCSU', u'BOCU-1', u'Punycode',
            u'GB 18030',
            )
        
        txt_enc = wx.StaticText(self, label=GT(u'Encoding'), name=u'encoding')
        self.ti_enc = ComboBoxESS(self, inputid.ENC, opts_enc[2], choices=opts_enc,
                name=u'Encoding')
        self.ti_enc.default = self.ti_enc.GetValue()
        
        # --- TERMINAL
        chk_term = CheckBoxESS(self, inputid.TERM, GT(u'Terminal'), name=u'Terminal')
        
        # --- STARTUP NOTIFY
        chk_notify = CheckBoxESS(self, inputid.NOTIFY, GT(u'Startup Notify'), name=u'StartupNotify',
                defaultValue=True)
        
        # --- NAME (menu)
        txt_name = wx.StaticText(self, label=GT(u'Name'), name=u'name*')
        self.ti_name = TextAreaESS(self, inputid.NAME, name=u'Name')
        self.ti_name.req = True
        self.ti_name.default = wx.EmptyString
        
        # --- EXECUTABLE
        txt_exec = wx.StaticText(self, label=GT(u'Executable'), name=u'exec')
        self.ti_exec = TextAreaESS(self, inputid.EXEC, name=u'Exec')
        self.ti_exec.default = wx.EmptyString
        
        # --- COMMENT
        txt_comm = wx.StaticText(self, label=GT(u'Comment'), name=u'comment')
        self.ti_comm = TextAreaESS(self, inputid.DESCR, name=u'Comment')
        self.ti_comm.default = wx.EmptyString
        
        # --- ICON
        txt_icon = wx.StaticText(self, label=GT(u'Icon'), name=u'icon')
        self.ti_icon = TextAreaESS(self, inputid.ICON, name=u'Icon')
        self.ti_icon.default = wx.EmptyString
        
        # --- CATEGORIES
        opts_category = (
            u'2DGraphics',
            u'Accessibility', u'Application', u'ArcadeGame', u'Archiving', u'Audio', u'AudioVideo',
            u'BlocksGame', u'BoardGame',
            u'Calculator', u'Calendar', u'CardGame', u'Compression', u'ContactManagement', u'Core',
            u'DesktopSettings', u'Development', u'Dictionary', u'DiscBurning', u'Documentation',
            u'Email',
            u'FileManager', u'FileTransfer',
            u'Game', u'GNOME', u'Graphics', u'GTK',
            u'HardwareSettings',
            u'InstantMessaging',
            u'KDE',
            u'LogicGame',
            u'Math', u'Monitor',
            u'Network',
            u'OCR', u'Office',
            u'P2P', u'PackageManager', u'Photography', u'Player', u'Presentation', u'Printing',
            u'Qt',
            u'RasterGraphics', u'Recorder', u'RemoteAccess',
            u'Scanning', u'Screensaver', u'Security', u'Settings', u'Spreadsheet', u'System',
            u'Telephony', u'TerminalEmulator', u'TextEditor',
            u'Utility',
            u'VectorGraphics', u'Video', u'Viewer',
            u'WordProcessor', u'Wine', u'Wine-Programs-Accessories',
            u'X-GNOME-NetworkSettings', u'X-GNOME-PersonalSettings', u'X-GNOME-SystemSettings',
            u'X-KDE-More', u'X-Red-Hat-Base', u'X-SuSE-ControlCenter-System',
            )
        
        txt_category = wx.StaticText(self, label=GT(u'Categories'), name=u'category')
        
        # This option does not get set by importing a new project
        self.ti_category = ComboBoxESS(self, value=opts_category[0], choices=opts_category,
                name=txt_category.Name)
        self.ti_category.default = self.ti_category.GetValue()
        
        btn_catadd = ButtonAdd(self, name=u'add category')
        btn_catdel = ButtonRemove(self, name=u'rm category')
        btn_catclr = ButtonClear(self, name=u'clear categories')
        
        # FIXME: Allow using multi-select + remove
        self.lst_categories = ListCtrlPanelESS(self, inputid.CAT, style=wx.LC_REPORT)
        self.lst_categories.SetSingleStyle(wx.LC_NO_HEADER)
        
        # For manually setting background color after enable/disable
        self.lst_categories.default_color = self.lst_categories.GetBackgroundColour()
        self.lst_categories.SetName(u'Categories')
        
        # ----- MISC
        txt_other = wx.StaticText(self, label=GT(u'Other'), name=u'other')
        self.ti_other = TextAreaPanelESS(self, inputid.OTHER, name=txt_other.Name)
        self.ti_other.default = wx.EmptyString
        self.ti_other.EnableDropTarget()
        
        # *** Layout *** #
        
        LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        
        lyt_opts1 = wx.FlexGridSizer()
        lyt_opts1.SetCols(3)
        lyt_opts1.SetRows(2)
        
        lyt_opts1.Add(txt_type, 0, LEFT_CENTER)
        lyt_opts1.Add(self.ti_type, 0, wx.EXPAND|wx.LEFT, 5)
        lyt_opts1.Add(chk_term, 0, LEFT_CENTER|wx.LEFT, 5)
        lyt_opts1.Add(txt_enc, 0, LEFT_CENTER|wx.TOP, 5)
        lyt_opts1.Add(self.ti_enc, 0, wx.LEFT|wx.TOP, 5)
        lyt_opts1.Add(chk_notify, 0, LEFT_CENTER|wx.LEFT|wx.TOP, 5)
        
        lyt_top = BoxSizer(wx.HORIZONTAL)
        lyt_top.Add(lyt_opts1, 0, wx.EXPAND|wx.ALIGN_BOTTOM)
        lyt_top.AddStretchSpacer(1)
        lyt_top.Add(btn_open, 0, wx.ALIGN_TOP)
        lyt_top.Add(btn_save, 0, wx.ALIGN_TOP)
        lyt_top.Add(btn_preview, 0, wx.ALIGN_TOP)
        
        lyt_mid = wx.GridBagSizer()
        lyt_mid.SetCols(4)
        lyt_mid.AddGrowableCol(1)
        lyt_mid.AddGrowableCol(3)
        
        # Row 1
        row = 0
        lyt_mid.Add(txt_name, (row, 0), flag=LEFT_CENTER)
        lyt_mid.Add(self.ti_name, (row, 1), flag=wx.EXPAND|wx.LEFT, border=5)
        lyt_mid.Add(txt_exec, (row, 2), flag=LEFT_CENTER|wx.LEFT, border=5)
        lyt_mid.Add(self.ti_exec, (row, 3), flag=wx.EXPAND|wx.LEFT, border=5)
        
        # Row 2
        row += 1
        lyt_mid.Add(txt_comm, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
        lyt_mid.Add(self.ti_comm, (row, 1), flag=wx.EXPAND|wx.LEFT|wx.TOP, border=5)
        lyt_mid.Add(txt_icon, (row, 2), flag=LEFT_CENTER|wx.LEFT|wx.TOP, border=5)
        lyt_mid.Add(self.ti_icon, (row, 3), flag=wx.EXPAND|wx.LEFT|wx.TOP, border=5)
        
        lyt_cat_btn = BoxSizer(wx.HORIZONTAL)
        lyt_cat_btn.Add(btn_catadd, 0)
        lyt_cat_btn.Add(btn_catdel, 0)
        lyt_cat_btn.Add(btn_catclr, 0)
        
        lyt_cat_input = BoxSizer(wx.VERTICAL)
        lyt_cat_input.Add(txt_category, 0, LEFT_BOTTOM)
        lyt_cat_input.Add(self.ti_category, 0, wx.TOP|wx.BOTTOM, 5)
        lyt_cat_input.Add(lyt_cat_btn, 0)
        
        lyt_cat_main = BoxSizer(wx.HORIZONTAL)
        lyt_cat_main.Add(lyt_cat_input, 0)
        lyt_cat_main.Add(self.lst_categories, 1, wx.EXPAND|wx.LEFT, 5)
        
        # --- Page 5 Sizer --- #
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_top, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(lyt_mid, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        lyt_main.Add(lyt_cat_main, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        lyt_main.AddSpacer(5)
        lyt_main.Add(txt_other, 0)
        lyt_main.Add(self.ti_other, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        btn_open.Bind(wx.EVT_BUTTON, self.OnLoadLauncher)
        btn_save.Bind(wx.EVT_BUTTON, self.OnExportLauncher)
        btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewLauncher)
        
        wx.EVT_KEY_DOWN(self.ti_category, self.SetCategory)
        wx.EVT_KEY_DOWN(self.lst_categories, self.SetCategory)
        btn_catadd.Bind(wx.EVT_BUTTON, self.SetCategory)
        btn_catdel.Bind(wx.EVT_BUTTON, self.SetCategory)
        btn_catclr.Bind(wx.EVT_BUTTON, self.SetCategory)
    
    
    ## TODO: Doxygen
    def Export(self, out_dir, out_name=wx.EmptyString, executable=False):
        if out_name == wx.EmptyString:
            out_name = page_ids[self.GetId()].upper()
        
        ret_code = WizardPage.Export(self, out_dir, out_name)
        
        absolute_filename = u'{}/{}'.format(out_dir, out_name).replace(u'//', u'/')
        if executable:
            os.chmod(absolute_filename, 0755)
        
        Logger.Debug(__name__, GT(u'Output filename: {}').format(out_name))
        
        return ret_code
    
    
    ## TODO: Doxygen
    def ExportBuild(self, stage):
        stage = u'{}/usr/share/applications'.format(stage).replace(u'//', u'/')
        
        if not os.path.isdir(stage):
            os.makedirs(stage)
        
        ret_code = self.Export(stage, u'{}.desktop'.format(self.GetOutputFilename()))
        if ret_code:
            return (ret_code, GT(u'Could not export menu launcher'))
        
        return (0, None)
    
    
    ## Saves launcher information to text file
    #
    #  \param target
    #    Filename path to export
    #  \param executable
    #    Set executable flag on target filename if True
    def ExportToFile(self, target, executable=False):
        launcher = self.GetLauncherInfo()
        
        WriteFile(target, launcher)
        
        # FIXME: Check timestamp
        if os.path.isfile(target):
            if executable:
                mode = 0755
            
            else:
                mode = 0644
            
            os.chmod(target, mode)
            
            if os.access(target, mode):
                return True
        
        return False
    
    
    ## Retrieves Desktop Entry file information
    #  
    #  \return
    #    Text formatted for desktop entry file output
    def Get(self, get_module=False):
        l_lines = [u'[Desktop Entry]']
        
        id_list = (
            inputid.VERSION,
            inputid.ENC,
            inputid.NAME,
            inputid.EXEC,
            inputid.DESCR,
            inputid.ICON,
            inputid.TYPE,
            inputid.TERM,
            inputid.NOTIFY,
            inputid.MIME,
            inputid.CAT,
            inputid.OTHER,
            )
        
        for ID in id_list:
            field = GetField(self, ID)
            
            if field:
                if ID == inputid.OTHER:
                    l_lines.append(field.GetValue().strip(u' \t\r\n'))
                    
                    continue
                
                if isinstance(field, (wx.TextCtrl, OwnerDrawnComboBox,)):
                    value = field.GetValue().strip()
                    
                    if not TextIsEmpty(value):
                        l_lines.append(u'{}={}'.format(field.GetName(), value))
                    
                    continue
                
                if isinstance(field, wx.CheckBox):
                    value = GS(field.GetValue()).lower()
                    
                    l_lines.append(u'{}={}'.format(field.GetName(), value))
                    
                    continue
                
                if isinstance(field, (ListCtrlBase, ListCtrlPanel,)):
                    value = u';'.join(field.GetListTuple())
                    
                    if not value.endswith(u';'):
                        value = u'{};'.format(value)
                    
                    if not TextIsEmpty(value):
                        l_lines.append(u'{}={}'.format(field.GetName(), value))
        
        l_text = u'\n'.join(l_lines)
        
        if get_module:
            # FIXME: 'MENU' needed?
            l_text = (__name__, l_text, u'MENU')
        
        return l_text
    
    
    ## Formats the launcher information for export
    #
    #  FIXME: Obsolete???
    def GetLauncherInfo(self):
        desktop_list = [u'[Desktop Entry]']
        
        name = self.ti_name.GetValue()
        if not TextIsEmpty(name):
            desktop_list.append(u'Name={}'.format(name))
        
        desktop_list.append(u'Version=1.0')
        
        executable = self.ti_exec.GetValue()
        if not TextIsEmpty(executable):
            desktop_list.append(u'Exec={}'.format(executable))
        
        comment = self.ti_comm.GetValue()
        if not TextIsEmpty(comment):
            desktop_list.append(u'Comment={}'.format(comment))
        
        icon = self.ti_icon.GetValue()
        if not TextIsEmpty(icon):
            desktop_list.append(u'Icon={}'.format(icon))
        
        launcher_type = self.ti_type.GetValue()
        if not TextIsEmpty(launcher_type):
            desktop_list.append(u'Type={}'.format(launcher_type))
        
        desktop_list.append(u'Terminal={}'.format(GS(self.sel_term.GetSelection() == 0).lower()))
        
        desktop_list.append(u'StartupNotify={}'.format(GS(self.sel_notify.GetSelection() == 0).lower()))
        
        encoding = self.ti_enc.GetValue()
        if not TextIsEmpty(encoding):
            desktop_list.append(u'Encoding={}'.format(encoding))
        
        categories = []
        cat_total = self.lst_categories.GetItemCount()
        count = 0
        while count < cat_total:
            C = self.lst_categories.GetItemText(count)
            if not TextIsEmpty(C):
                categories.append(self.lst_categories.GetItemText(count))
            
            count += 1
        
        # Add a final semi-colon if categories is not empty
        if categories:
            categories = u';'.join(categories)
            if categories[-1] != u';':
                categories = u'{};'.format(categories)
            
            desktop_list.append(u'Categories={}'.format(categories))
        
        other = self.ti_other.GetValue()
        if not TextIsEmpty(other):
            desktop_list.append(other)
        
        return u'\n'.join(desktop_list)
    
    
    ## Retrieves the filename to be used for the menu launcher
    def GetOutputFilename(self):
        # FIXME: Use tab 'name' or 'title' attribute
        return self.ti_name.GetValue().strip(u' ').replace(u' ', u'_')
    
    
    ## Overrides ui.wizard.GetRequiredField
    def GetRequiredFields(self, children=None):
        required_fields = list(WizardPage.GetRequiredFields(self, children=children))
        
        return tuple(required_fields)
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, filename):
        Logger.Debug(__name__, GT(u'Importing page info from {}').format(filename))
        
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        menu_data = ReadFile(filename, split=True, convert=list)
        
        if u'[Desktop Entry]' in menu_data[0]:
            menu_data.remove(menu_data[0])
        
        menu_definitions = {}
        unused_raw_lines = []
        
        for L in menu_data:
            if u'=' in L:
                key = L.split(u'=')
                value = key[-1]
                key = key[0]
                
                menu_definitions[key] = value
                
                continue
            
            # Any unrecognizable lines will be added to "Other" section
            unused_raw_lines.append(L)
        
        
        def set_value(option):
            key = option.GetName()
            value = None
            
            if key in menu_definitions:
                value = menu_definitions[key]
                
                if not TextIsEmpty(value):
                    if option in self.opts_input:
                        option.SetValue(value)
                        return True
                    
                    elif option in self.opts_choice:
                        if option.SetStringSelection(value):
                            return True
                    
                    elif option in self.opts_list:
                        if key == self.lst_categories.GetName():
                            value = value.split(u';')
                            
                            if value:
                                for X, val in enumerate(value):
                                    self.lst_categories.InsertStringItem(X, val)
                                return True
            
            return False
        
        categories_used = []
        
        for group in self.opts_input, self.opts_choice, self.opts_list:
            for O in group:
                if set_value(O):
                    categories_used.append(O.GetName())
        
        
        # List of keys that can be ignored if unused
        bypass_unused = (
            u'Version',
        )
        
        categories_unused = []
        for key in menu_definitions:
            if key not in categories_used and key not in bypass_unused:
                categories_unused.append(u'{}={}'.format(key, menu_definitions[key]))
        
        categories_unused += unused_raw_lines
        if len(categories_unused):
            categories_unused = u'\n'.join(categories_unused)
            
            self.ti_other.SetValue(categories_unused)
        
        return 0
    
    
    ## Saves launcher information to file
    #  
    #  FIXME: Might be problems with reading/writing launchers (see OnLoadLauncher)
    #         'Others' field not being completely filled out.
    def OnExportLauncher(self, event=None):
        Logger.Debug(__name__, u'Export launcher ...')
        
        export = GetFileSaveDialog(GetMainWindow(), GT(u'Save Launcher'))
        
        if ShowDialog(export):
            target = export.GetPath()
            
            # Create a backup file
            # FIXME: Create backup files in WriteFile function?
            overwrite = False
            if os.path.isfile(target):
                backup = u'{}.backup'.format(target)
                shutil.copy(target, backup)
                overwrite = True
            
            try:
                self.ExportToFile(target)
                
                if overwrite:
                    os.remove(backup)
            
            except UnicodeEncodeError:
                detail1 = GT(u'Unfortunately Debreate does not support unicode yet.')
                detail2 = GT(u'Remove any non-ASCII characters from your project.')
                
                ShowErrorDialog(GT(u'Save failed'), u'{}\n{}'.format(detail1, detail2), title=GT(u'Unicode Error'))
                
                os.remove(target)
                # Restore from backup
                shutil.move(backup, target)
    
    
    ## Loads a .desktop launcher's data
    #  
    #  FIXME: Might be problems with reading/writing launchers (see OnExportLauncher)
    #         'Others' field not being completely filled out.
    def OnLoadLauncher(self, event=None):
        dia = GetFileOpenDialog(GetMainWindow(), GT(u'Open Launcher'))
        
        if ShowDialog(dia):
            path = dia.GetPath()
            
            data = ReadFile(path, split=True, convert=list)
            
            # Remove unneeded lines
            if data[0] == u'[Desktop Entry]':
                data = data[1:]
            
            self.Reset()
            # First line needs to be changed to '1'
            data.insert(0, u'1')
            self.Set(u'\n'.join(data))
    
    
    ## Show a preview of the .desktop launcher
    def OnPreviewLauncher(self, event=None):
        preview = TextPreview(title=GT(u'Menu Launcher Preview'),
                text=self.Get(), size=(500,400))
        
        ShowDialog(preview)
    
    
    ## TODO: Doxygen
    def Reset(self):
        for O in self.opts_input:
            O.SetValue(O.default)
        
        for O in self.opts_choice:
            O.SetSelection(O.default)
        
        for O in self.opts_list:
            O.DeleteAllItems()
    
    
    ## TODO: Doxygen
    def SetCategory(self, event=None):
        try:
            ID = event.GetKeyCode()
        
        except AttributeError:
            ID = event.GetEventObject().GetId()
        
        cat = self.ti_category.GetValue()
        cat = cat.split()
        cat = u''.join(cat)
        
        if ID in (wx.ID_ADD, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.lst_categories.InsertStringItem(self.lst_categories.GetItemCount(), cat)
        
        elif ID in (wx.ID_REMOVE, wx.WXK_DELETE):
            if self.lst_categories.GetItemCount() and self.lst_categories.GetSelectedItemCount():
                cur_cat = self.lst_categories.GetFirstSelected()
                self.lst_categories.DeleteItem(cur_cat)
        
        elif ID == wx.ID_CLEAR:
            if self.lst_categories.GetItemCount():
                if ConfirmationDialog(GetMainWindow(), GT(u'Confirm'),
                        GT(u'Clear categories?')).ShowModal() in (wx.ID_OK, wx.OK):
                    self.lst_categories.DeleteAllItems()
        
        if event:
            event.Skip()
    
    
    ## Fills out launcher information from loaded file
    #  
    #  \param data
    #    Information to fill out menu launcher fields
    #  \param enabled
    #    \b \e bool : Launcher will be flagged for export if True
    def Set(self, data):
        # Make sure we are dealing with a list
        if isinstance(data, (unicode, str)):
            data = data.split(u'\n')
        
        # Data list is not empty
        if data:
            Logger.Debug(__name__, u'Loading launcher')
            
            if DebugEnabled():
                for L in data:
                    print(u'  Launcher line: {}'.format(L))
            
            data_defs = {}
            data_defs_remove = []
            misc_defs = []
            
            for L in data:
                if u'=' in L:
                    if L[0] == u'[' and L[-1] == u']':
                        key = L[1:-1].split(u'=')
                        value = key[1]
                        key = key[0]
                        
                        misc_defs.append(u'{}={}'.format(key, value))
                    
                    else:
                        key = L.split(u'=')
                        value = key[1]
                        key = key[0]
                        
                        data_defs[key] = value
            
            # Fields using SetValue() function
            set_value_fields = (
                (u'Name', self.ti_name),
                (u'Exec', self.ti_exec),
                (u'Comment', self.ti_comm),
                (u'Icon', self.ti_icon),
                (u'Type', self.ti_type),
                (u'Encoding', self.ti_enc),
                )
            
            for label, control in set_value_fields:
                try:
                    control.SetValue(data_defs[label])
                    data_defs_remove.append(label)
                
                except KeyError:
                    pass
            
            # Fields using SetSelection() function
            set_selection_fields = (
                (u'Terminal', self.sel_term),
                (u'StartupNotify', self.sel_notify),
                )
            
            for label, control in set_selection_fields:
                try:
                    control.SetStringSelection(data_defs[label].lower())
                    data_defs_remove.append(label)
                
                except KeyError:
                    pass
            
            try:
                categories = tuple(data_defs[u'Categories'].split(u';'))
                for C in categories:
                    self.lst_categories.InsertStringItem(self.lst_categories.GetItemCount(), C)
                
                data_defs_remove.append(u'Categories')
            
            except KeyError:
                pass
            
            for K in data_defs_remove:
                if K in data_defs:
                    del data_defs[K]
            
            # Add any leftover keys to misc/other
            for K in data_defs:
                if K not in (u'Version',):
                    misc_defs.append(u'{}={}'.format(K, data_defs[K]))
            
            for index in reversed(range(len(misc_defs))):
                K = misc_defs[index]
                
                # Set custom filename
                if u'FILENAME=' in K:
                    filename = K.replace(u'FILENAME=', u'')
                    
                    # Remove so not added to misc. list
                    misc_defs.pop(index)
                    
                    continue
            
            if misc_defs:
                self.ti_other.SetValue(u'\n'.join(sorted(misc_defs)))
