# -*- coding: utf-8 -*-

## \package wiz_bin.menu

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, wx

from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.ident          import chkid
from globals.ident          import inputid
from globals.ident          import listid
from globals.ident          import pgid
from globals.ident          import selid
from globals.ident          import txtid
from globals.strings        import GS
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetMainWindow
from input.list             import ListCtrl
from input.select           import Choice
from input.select           import ComboBox
from input.text             import TextArea
from input.text             import TextAreaPanel
from input.toggle           import CheckBox
from ui.button              import ButtonAdd
from ui.button              import ButtonBrowse64
from ui.button              import ButtonClear
from ui.button              import ButtonPreview64
from ui.button              import ButtonRemove
from ui.button              import ButtonSave64
from ui.dialog              import ConfirmationDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.textpreview         import TextPreview
from ui.wizard              import WizardPage


## Page for creating a system menu launcher
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.MENU) #, name=GT(u'Menu Launcher'))
        
        ## Override default label
        self.label = GT(u'Menu Launcher')
        
        self.opts_button = []
        self.opts_input = []
        self.opts_choice = []
        self.opts_list = []
        
        self.labels = []
        
        # --- Buttons to open/preview/save .desktop file
        btn_open = ButtonBrowse64(self)
        btn_open.SetName(u'open')
        
        btn_save = ButtonSave64(self)
        btn_save.SetName(u'export')
        self.opts_button.append(btn_save)
        
        btn_preview = ButtonPreview64(self)
        btn_preview.SetName(u'preview')
        self.opts_button.append(btn_preview)
        
        # --- CHECKBOX
        chk_enable = CheckBox(self, chkid.ENABLE, GT(u'Create system menu launcher'))
        
        # --- Custom output filename
        txt_filename = wx.StaticText(self, txtid.FNAME, GT(u'Filename'), name=u'filename')
        ti_filename = TextArea(self, inputid.FNAME, name=txt_filename.Name)
        
        chk_filename = CheckBox(self, chkid.FNAME, GT(u'Use "Name" as output filename (<Name>.desktop)'),
                name=u'filename chk', defaultValue=True)
        
        # --- NAME (menu)
        txt_name = wx.StaticText(self, label=GT(u'Name'), name=u'name*')
        self.labels.append(txt_name)
        ti_name = TextArea(self, inputid.NAME, name=u'Name')
        ti_name.req = True
        self.opts_input.append(ti_name)
        
        # --- EXECUTABLE
        txt_exec = wx.StaticText(self, label=GT(u'Executable'), name=u'exec')
        self.labels.append(txt_exec)
        
        ti_exec = TextArea(self, inputid.EXEC, name=u'Exec')
        self.opts_input.append(ti_exec)
        
        # --- COMMENT
        txt_comm = wx.StaticText(self, label=GT(u'Comment'), name=u'comment')
        self.labels.append(txt_comm)
        
        ti_comm = TextArea(self, inputid.DESCR, name=u'Comment')
        self.opts_input.append(ti_comm)
        
        # --- ICON
        txt_icon = wx.StaticText(self, label=GT(u'Icon'), name=u'icon')
        self.labels.append(txt_icon)
        
        ti_icon = TextArea(self, inputid.ICON, name=u'Icon')
        self.opts_input.append(ti_icon)
        
        # --- TYPE
        opts_type = (u'Application', u'Link', u'Directory',)
        
        txt_type = wx.StaticText(self, label=GT(u'Type'), name=u'type')
        self.labels.append(txt_type)
        
        ti_type = ComboBox(self, inputid.TYPE, choices=opts_type, name=u'Type',
                defaultValue=opts_type[0])
        self.opts_input.append(ti_type)
        
        # --- TERMINAL
        opts_term = (u'true', u'false',)
        
        txt_term = wx.StaticText(self, label=GT(u'Terminal'), name=u'terminal')
        self.labels.append(txt_term)
        
        sel_term = Choice(self, selid.TERM, choices=opts_term, name=u'Terminal',
                defaultValue=1)
        self.opts_choice.append(sel_term)
        
        # --- STARTUP NOTIFY
        notify_opt = (u'true', u'false',)
        
        txt_notify = wx.StaticText(self, label=GT(u'Startup Notify'), name=u'startupnotify')
        self.labels.append(txt_notify)
        
        sel_notify = Choice(self, selid.NOTIFY, choices=notify_opt, name=u'StartupNotify')
        self.opts_choice.append(sel_notify)
        
        # --- ENCODING
        opts_enc = (
            u'UTF-1', u'UTF-7', u'UTF-8', u'CESU-8', u'UTF-EBCDIC',
            u'UTF-16', u'UTF-32', u'SCSU', u'BOCU-1', u'Punycode',
            u'GB 18030',
            )
        
        txt_enc = wx.StaticText(self, label=GT(u'Encoding'), name=u'encoding')
        self.labels.append(txt_enc)
        
        ti_enc = ComboBox(self, inputid.ENC, choices=opts_enc, name=u'Encoding',
                defaultValue=opts_enc[2])
        self.opts_input.append(ti_enc)
        
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
        
        txt_category = wx.StaticText(self, label=GT(u'Category'), name=u'category')
        self.labels.append(txt_category)
        
        # This option does not get set by importing a new project
        ti_category = ComboBox(self, inputid.CAT, choices=opts_category, name=txt_category.Name,
                defaultValue=opts_category[0])
        self.opts_input.append(ti_category)
        
        btn_catadd = ButtonAdd(self, name=u'add category')
        btn_catdel = ButtonRemove(self, name=u'rm category')
        btn_catclr = ButtonClear(self, name=u'clear categories')
        
        for B in btn_catadd, btn_catdel, btn_catclr:
            self.opts_button.append(B)
        
        # FIXME: Allow using multi-select + remove
        lst_categories = ListCtrl(self, listid.CAT, name=u'Categories')
        # Can't set LC_SINGLE_SEL in constructor for wx 3.0 (ListCtrl bug???)
        lst_categories.SetSingleStyle(wx.LC_SINGLE_SEL)
        
        # For manually setting background color after enable/disable
        lst_categories.default_color = lst_categories.GetBackgroundColour()
        self.opts_list.append(lst_categories)
        
        # ----- MISC
        txt_other = wx.StaticText(self, label=GT(u'Other'), name=u'other')
        self.labels.append(txt_other)
        
        ti_other = TextAreaPanel(self, inputid.OTHER, name=txt_other.Name)
        ti_other.EnableDropTarget()
        self.opts_input.append(ti_other)
        
        self.OnToggle()
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        CENTER_EXPAND = wx.ALIGN_CENTER_VERTICAL|wx.EXPAND
        CENTER_RIGHT = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
        LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        RIGHT_CENTER = wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL
        
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_open, 0)
        lyt_buttons.Add(btn_save, 0)
        lyt_buttons.Add(btn_preview, 0)
        
        lyt_cat_btn = BoxSizer(wx.HORIZONTAL)
        lyt_cat_btn.Add(btn_catadd, 0)
        lyt_cat_btn.Add(btn_catdel, 0)
        lyt_cat_btn.Add(btn_catclr, 0)
        
        lyt_cat_input = BoxSizer(wx.VERTICAL)
        lyt_cat_input.Add(txt_category, 0, LEFT_BOTTOM)
        lyt_cat_input.Add(ti_category, 0, wx.TOP|wx.BOTTOM, 5)
        lyt_cat_input.Add(lyt_cat_btn, 0)
        
        lyt_cat_main = BoxSizer(wx.HORIZONTAL)
        lyt_cat_main.Add(lyt_cat_input, 0)
        lyt_cat_main.Add(lst_categories, 1, wx.EXPAND|wx.LEFT, 5)
        
        lyt_grid = wx.GridBagSizer(5, 5)
        lyt_grid.SetCols(4)
        lyt_grid.AddGrowableCol(1)
        
        # Row 1
        lyt_grid.Add(txt_filename, (0, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(ti_filename, pos=(0, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(chk_filename, pos=(0, 2), span=(1, 2), flag=CENTER_RIGHT)
        
        # Row 2
        lyt_grid.Add(txt_name, (1, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(ti_name, (1, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(txt_type, (1, 2), flag=RIGHT_CENTER)
        lyt_grid.Add(ti_type, (1, 3), flag=CENTER_EXPAND)
        
        # Row 3
        lyt_grid.Add(txt_exec, (2, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(ti_exec, (2, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(txt_term, (2, 2), flag=RIGHT_CENTER)
        lyt_grid.Add(sel_term, (2, 3), flag=LEFT_CENTER)
        
        # Row 4
        lyt_grid.Add(txt_comm, (3, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(ti_comm, (3, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(txt_notify, (3, 2), flag=RIGHT_CENTER)
        lyt_grid.Add(sel_notify, (3, 3), flag=LEFT_CENTER)
        
        # Row 5
        lyt_grid.Add(txt_icon, (4, 0), flag=RIGHT_CENTER)
        lyt_grid.Add(ti_icon, (4, 1), flag=CENTER_EXPAND)
        lyt_grid.Add(txt_enc, (4, 2), flag=RIGHT_CENTER)
        lyt_grid.Add(ti_enc, (4, 3), flag=CENTER_EXPAND)
        
        lyt_border = BoxSizer(wx.VERTICAL)
        
        lyt_border.Add(lyt_grid, 0, wx.EXPAND|wx.BOTTOM, 5)
        lyt_border.Add(lyt_cat_main, 0, wx.EXPAND|wx.TOP, 5)
        lyt_border.AddSpacer(5)
        lyt_border.Add(txt_other, 0)
        lyt_border.Add(ti_other, 1, wx.EXPAND)
        
        # --- Page 5 Sizer --- #
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_buttons, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM, 5)
        lyt_main.Add(chk_enable, 0, wx.LEFT, 5)
        lyt_main.Add(lyt_border, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        btn_open.Bind(wx.EVT_BUTTON, self.OnLoadLauncher)
        btn_save.Bind(wx.EVT_BUTTON, self.OnSaveLauncher)
        btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewLauncher)
        
        chk_enable.Bind(wx.EVT_CHECKBOX, self.OnToggle)
        
        chk_filename.Bind(wx.EVT_CHECKBOX, self.OnSetCustomFilename)
        
        wx.EVT_KEY_DOWN(ti_category, self.SetCategory)
        wx.EVT_KEY_DOWN(lst_categories, self.SetCategory)
        btn_catadd.Bind(wx.EVT_BUTTON, self.SetCategory)
        btn_catdel.Bind(wx.EVT_BUTTON, self.SetCategory)
        btn_catclr.Bind(wx.EVT_BUTTON, self.SetCategory)
    
    
    ## TODO: Doxygen
    def ExportPage(self):
        return self.GetLauncherInfo()
    
    
    ## TODO: Doxygen
    def GatherData(self):
        if GetField(self, chkid.ENABLE).GetValue():
            data = self.GetLauncherInfo()
            data = u'\n'.join(data.split(u'\n')[1:])
            
            if not GetField(self, chkid.FNAME).GetValue():
                data = u'[FILENAME={}]\n{}'.format(GetField(self, inputid.FNAME).GetValue(), data)
            
            return u'<<MENU>>\n1\n{}\n<</MENU>>'.format(data)
        
        else:
            return u'<<MENU>>\n0\n<</MENU>>'
    
    
    ## Formats the launcher information for export
    def GetLauncherInfo(self):
        desktop_list = [u'[Desktop Entry]']
        
        name = GetField(self, inputid.NAME).GetValue()
        if not TextIsEmpty(name):
            desktop_list.append(u'Name={}'.format(name))
        
        desktop_list.append(u'Version=1.0')
        
        executable = GetField(self, inputid.EXEC).GetValue()
        if not TextIsEmpty(executable):
            desktop_list.append(u'Exec={}'.format(executable))
        
        comment = GetField(self, inputid.DESCR).GetValue()
        if not TextIsEmpty(comment):
            desktop_list.append(u'Comment={}'.format(comment))
        
        icon = GetField(self, inputid.ICON).GetValue()
        if not TextIsEmpty(icon):
            desktop_list.append(u'Icon={}'.format(icon))
        
        launcher_type = GetField(self, inputid.TYPE).GetValue()
        if not TextIsEmpty(launcher_type):
            desktop_list.append(u'Type={}'.format(launcher_type))
        
        desktop_list.append(u'Terminal={}'.format(GS(GetField(self, selid.TERM).GetSelection() == 0).lower()))
        
        desktop_list.append(u'StartupNotify={}'.format(GS(GetField(self, selid.NOTIFY).GetSelection() == 0).lower()))
        
        encoding = GetField(self, inputid.ENC).GetValue()
        if not TextIsEmpty(encoding):
            desktop_list.append(u'Encoding={}'.format(encoding))
        
        lst_categories = GetField(self, listid.CAT)
        categories = []
        cat_total = lst_categories.GetItemCount()
        count = 0
        while count < cat_total:
            C = lst_categories.GetItemText(count)
            if not TextIsEmpty(C):
                categories.append(lst_categories.GetItemText(count))
            
            count += 1
        
        # Add a final semi-colon if categories is not empty
        if categories:
            categories = u';'.join(categories)
            if categories[-1] != u';':
                categories = u'{};'.format(categories)
            
            desktop_list.append(u'Categories={}'.format(categories))
        
        other = GetField(self, inputid.OTHER).GetValue()
        if not TextIsEmpty(other):
            desktop_list.append(other)
        
        return u'\n'.join(desktop_list)
    
    
    ## Retrieves the filename to be used for the menu launcher
    def GetOutputFilename(self):
        if not GetField(self, chkid.FNAME).GetValue():
            filename = GetField(self, inputid.FNAME).GetValue().strip(u' ').replace(u' ', u'_')
            if not TextIsEmpty(filename):
                return filename
        
        return GetField(self, inputid.NAME).GetValue().strip(u' ').replace(u' ', u'_')
    
    
    ## TODO: Doxygen
    def IsBuildExportable(self):
        return GetField(self, chkid.ENABLE).GetValue()
    
    
    ## Loads a .desktop launcher's data
    #  
    #  FIXME: Might be problems with reading/writing launchers (see OnSaveLauncher)
    #         'Others' field not being completely filled out.
    def OnLoadLauncher(self, event=None):
        dia = wx.FileDialog(GetMainWindow(), GT(u'Open Launcher'), os.getcwd(),
                style=wx.FD_CHANGE_DIR)
        
        if ShowDialog(dia):
            path = dia.GetPath()
            
            data = ReadFile(path, split=True)
            
            # Remove unneeded lines
            if data[0] == u'[Desktop Entry]':
                data = data[1:]
            
            self.Reset()
            self.SetLauncherData(u'\n'.join(data))
    
    
    ## TODO: Doxygen
    def OnPreviewLauncher(self, event=None):
        # Show a preview of the .desktop config file
        config = self.GetLauncherInfo()
        
        dia = TextPreview(title=GT(u'Menu Launcher Preview'),
                text=config, size=(500,400))
        
        dia.ShowModal()
        dia.Destroy()
    
    
    ## Saves launcher information to file
    #  
    #  FIXME: Might be problems with reading/writing launchers (see OnLoadLauncher)
    #         'Others' field not being completely filled out.
    def OnSaveLauncher(self, event=None):
        Logger.Debug(__name__, u'Export launcher ...')
        
        # Get data to write to control file
        menu_data = self.GetLauncherInfo().encode(u'utf-8')
        
        dia = wx.FileDialog(GetMainWindow(), GT(u'Save Launcher'), os.getcwd(),
            style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
        
        if ShowDialog(dia):
            path = dia.GetPath()
            
            # Create a backup file
            overwrite = False
            if os.path.isfile(path):
                backup = u'{}.backup'.format(path)
                shutil.copy(path, backup)
                overwrite = True
            
            try:
                WriteFile(path, menu_data)
                
                if overwrite:
                    os.remove(backup)
            
            except UnicodeEncodeError:
                detail1 = GT(u'Unfortunately Debreate does not support unicode yet.')
                detail2 = GT(u'Remove any non-ASCII characters from your project.')
                
                ShowErrorDialog(GT(u'Save failed'), u'{}\n{}'.format(detail1, detail2), title=GT(u'Unicode Error'))
                
                os.remove(path)
                # Restore from backup
                shutil.move(backup, path)
    
    
    ## TODO: Doxygen
    def OnSetCustomFilename(self, event=None):
        chk_filename = GetField(self, chkid.FNAME)
        txt_filename = GetField(self, txtid.FNAME)
        ti_filename = GetField(self, inputid.FNAME)
        
        if not chk_filename.IsEnabled():
            txt_filename.Enable(False)
            ti_filename.Enable(False)
            return
        
        if chk_filename.GetValue():
            txt_filename.Enable(False)
            ti_filename.Enable(False)
            return
        
        txt_filename.Enable(True)
        ti_filename.Enable(True)
    
    
    ## TODO: Doxygen
    def OnToggle(self, event=None):
        enable = GetField(self, chkid.ENABLE).IsChecked()
        
        listctrl_bgcolor_defs = {
            True: GetField(self, listid.CAT).default_color,
            False: wx.Colour(214, 214, 214),
        }
        
        for group in self.opts_button, self.opts_choice, self.opts_input, \
                self.opts_list, self.labels:
            for O in group:
                O.Enable(enable)
                
                # Small hack to gray-out ListCtrl when disabled
                if isinstance(O, wx.ListCtrl):
                    O.SetBackgroundColour(listctrl_bgcolor_defs[enable])
        
        GetField(self, chkid.FNAME).Enable(enable)
        self.OnSetCustomFilename()
    
    
    ## TODO: Doxygen
    def Reset(self):
        chk_filename = GetField(self, chkid.FNAME)
        
        chk_filename.SetValue(chk_filename.default)
        GetField(self, inputid.FNAME).Clear()
        
        for O in self.opts_input:
            O.SetValue(O.default)
        
        for O in self.opts_choice:
            O.SetSelection(O.default)
        
        for O in self.opts_list:
            O.DeleteAllItems()
        
        chk_enable = GetField(self, chkid.ENABLE)
        
        chk_enable.SetValue(chk_enable.default)
        self.OnToggle()
    
    
    ## TODO: Doxygen
    def SetCategory(self, event=None):
        try:
            ID = event.GetKeyCode()
        
        except AttributeError:
            ID = event.GetEventObject().GetId()
        
        cat = GetField(self, inputid.CAT).GetValue()
        cat = cat.split()
        cat = u''.join(cat)
        
        lst_categories = GetField(self, listid.CAT)
        
        if ID in (wx.ID_ADD, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            lst_categories.InsertStringItem(lst_categories.GetItemCount(), cat)
        
        elif ID in (wx.ID_REMOVE, wx.WXK_DELETE):
            if lst_categories.GetItemCount() and lst_categories.GetSelectedItemCount():
                cur_cat = lst_categories.GetFirstSelected()
                lst_categories.DeleteItem(cur_cat)
        
        elif ID == wx.ID_CLEAR:
            if lst_categories.GetItemCount():
                if ConfirmationDialog(GetMainWindow(), GT(u'Confirm'),
                        GT(u'Clear categories?')).ShowModal() in (wx.ID_OK, wx.OK):
                    lst_categories.DeleteAllItems()
        
        if event:
            event.Skip()
    
    
    ## Fills out launcher information from loaded file
    #  
    #  \param data
    #    Information to fill out menu launcher fields
    #  \param enabled
    #    \b \e bool : Launcher will be flagged for export if True
    def SetLauncherData(self, data, enabled=True):
        # Make sure we are dealing with a list
        if isinstance(data, (unicode, str)):
            data = data.split(u'\n')
        
        # Data list is not empty
        if data:
            Logger.Debug(__name__, u'Loading launcher')
            
            if data[0].isnumeric():
                enabled = int(data.pop(0)) > 0
            
            if DebugEnabled():
                for L in data:
                    print(u'  Launcher line: {}'.format(L))
            
            Logger.Debug(__name__, u'Enabling launcher: {}'.format(enabled))
            
            if enabled:
                GetField(self, chkid.ENABLE).SetValue(True)
                
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
                    (u'Name', GetField(self, inputid.NAME)),
                    (u'Exec', GetField(self, inputid.EXEC)),
                    (u'Comment', GetField(self, inputid.DESCR)),
                    (u'Icon', GetField(self, inputid.ICON)),
                    (u'Type', GetField(self, inputid.TYPE)),
                    (u'Encoding', GetField(self, inputid.ENC)),
                    )
                
                for label, control in set_value_fields:
                    try:
                        control.SetValue(data_defs[label])
                        data_defs_remove.append(label)
                    
                    except KeyError:
                        pass
                
                # Fields using SetSelection() function
                set_selection_fields = (
                    (u'Terminal', GetField(self, selid.TERM)),
                    (u'StartupNotify', GetField(self, selid.NOTIFY)),
                    )
                
                for label, control in set_selection_fields:
                    try:
                        control.SetStringSelection(data_defs[label].lower())
                        data_defs_remove.append(label)
                    
                    except KeyError:
                        pass
                
                try:
                    lst_categories = GetField(self, listid.CAT)
                    categories = tuple(data_defs[u'Categories'].split(u';'))
                    for C in categories:
                        lst_categories.InsertStringItem(lst_categories.GetItemCount(), C)
                    
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
                        
                        if not TextIsEmpty(filename):
                            Logger.Debug(__name__, u'Setting custom filename: {}'.format(filename))
                            
                            GetField(self, inputid.FNAME).SetValue(filename)
                            GetField(self, chkid.FNAME).SetValue(False)
                        
                        # Remove so not added to misc. list
                        misc_defs.pop(index)
                        
                        continue
                
                if misc_defs:
                    GetField(self, inputid.OTHER).SetValue(u'\n'.join(sorted(misc_defs)))
                
                self.OnToggle()
