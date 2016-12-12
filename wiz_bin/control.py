# -*- coding: utf-8 -*-

## \package wiz_bin.control

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.buttons            import ButtonBrowse64
from dbr.buttons            import ButtonPreview64
from dbr.buttons            import ButtonSave64
from dbr.charctrl           import CharCtrl
from dbr.dialogs            import GetFileOpenDialog
from dbr.dialogs            import GetFileSaveDialog
from dbr.dialogs            import ShowDialog
from dbr.language           import GT
from dbr.log                import Logger
from dbr.panel              import BorderedPanel
from dbr.textinput          import MultilineTextCtrlPanel
from dbr.wizard             import WizardPage
from globals                import ident
from globals.errorcodes     import dbrerrno
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import FieldEnabled
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetTopWindow


## This panel displays the field input of the control file
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.CONTROL)
        
        # Bypass checking this page for build
        # This is mandatory & done manually
        self.prebuild_check = False
        
        self.SetScrollbars(0, 20, 0, 0)
        
        self.pnl_bg = wx.Panel(self)
        
        # Buttons to open, save, & preview control file
        btn_open = ButtonBrowse64(self.pnl_bg)
        btn_save = ButtonSave64(self.pnl_bg)
        btn_preview = ButtonPreview64(self.pnl_bg)
        
        # Button to open a help dialog (WIP)
        #btn_help = HelpButton(self.pnl_bg)
        
        # *** Required fields *** #
        
        pnl_require = BorderedPanel(self.pnl_bg)
        
        txt_package = wx.StaticText(pnl_require, label=GT(u'Package'), name=u'package')
        txt_package.req = True
        self.ti_package = CharCtrl(pnl_require, ident.F_NAME, name=txt_package.Name)
        self.ti_package.req = True
        
        txt_version = wx.StaticText(pnl_require, label=GT(u'Version'), name=u'version')
        txt_version.req = True
        self.ti_version = CharCtrl(pnl_require, ident.F_VERSION, name=txt_version.Name)
        self.ti_version.req = True
        
        txt_maintainer = wx.StaticText(pnl_require, label=GT(u'Maintainer'), name=u'maintainer')
        txt_maintainer.req = True
        self.ti_maintainer = wx.TextCtrl(pnl_require, ident.F_MAINTAINER, name=txt_maintainer.Name)
        self.ti_maintainer.req = True
        
        txt_email = wx.StaticText(pnl_require, label=GT(u'Email'), name=u'email')
        txt_email.req = True
        self.ti_email = wx.TextCtrl(pnl_require, ident.F_EMAIL, name=txt_email.Name)
        self.ti_email.req = True
        
        self.opts_arch = (
            u'all', u'alpha', u'amd64', u'arm', u'arm64', u'armeb', u'armel',
            u'armhf', u'avr32', u'hppa', u'i386', u'ia64', u'lpia', u'm32r',
            u'm68k', u'mips', u'mipsel', u'powerpc', u'powerpcspe', u'ppc64',
            u's390', u's390x', u'sh3', u'sh3eb', u'sh4', u'sh4eb', u'sparc',
            u'sparc64',
            )
        
        txt_arch = wx.StaticText(pnl_require, label=GT(u'Architecture'), name=u'arch')
        self.sel_arch = wx.Choice(pnl_require, choices=self.opts_arch, name=txt_arch.Name)
        self.sel_arch.default = 0
        self.sel_arch.SetSelection(self.sel_arch.default)
        
        # *** Recommended fields *** #
        
        pnl_recommend = BorderedPanel(self.pnl_bg)
        
        opts_section = (
            u'admin', u'cli-mono', u'comm', u'database', u'devel', u'debug',
            u'doc', u'editors', u'electronics', u'embedded', u'fonts', u'games',
            u'gnome', u'graphics', u'gnu-r', u'gnustep', u'hamradio', u'haskell',
            u'httpd', u'interpreters', u'java', u'kde', u'kernel', u'libs',
            u'libdevel', u'lisp', u'localization', u'mail', u'math',
            u'metapackages', u'misc', u'net', u'news', u'ocaml', u'oldlibs',
            u'otherosfs', u'perl', u'php', u'python', u'ruby', u'science',
            u'shells', u'sound', u'tex', u'text', u'utils', u'vcs', u'video',
            u'web', u'x11', u'xfce', u'zope',
            )
        
        txt_section = wx.StaticText(pnl_recommend, label=GT(u'Section'), name=u'section')
        self.ti_section = wx.ComboBox(pnl_recommend, choices=opts_section, name=txt_section.Name)
        
        self.opts_priority = (
            u'optional', u'standard', u'important', u'required', u'extra',
            )
        
        txt_priority = wx.StaticText(pnl_recommend, label=GT(u'Priority'), name=u'priority')
        self.sel_priority = wx.Choice(pnl_recommend, choices=self.opts_priority, name=txt_priority.Name)
        self.sel_priority.default = 0
        self.sel_priority.SetSelection(self.sel_priority.default)
        
        txt_synopsis = wx.StaticText(pnl_recommend, label=GT(u'Short Description'), name=u'synopsis')
        self.ti_synopsis = wx.TextCtrl(pnl_recommend, name=txt_synopsis.Name)
        
        txt_description = wx.StaticText(pnl_recommend, label=GT(u'Long Description'), name=u'description')
        self.ti_description = MultilineTextCtrlPanel(pnl_recommend, name=txt_description.Name)
        
        # *** Optional fields *** #
        
        pnl_option = BorderedPanel(self.pnl_bg)
        
        txt_source = wx.StaticText(pnl_option, label=GT(u'Source'), name=u'source')
        self.ti_source = wx.TextCtrl(pnl_option, name=txt_source.Name)
        
        txt_homepage = wx.StaticText(pnl_option, label=GT(u'Homepage'), name=u'homepage')
        self.ti_homepage = wx.TextCtrl(pnl_option, name=txt_homepage.Name)
        
        self.opts_essential = (
            u'yes', u'no',
            )
        
        txt_essential = wx.StaticText(pnl_option, label=GT(u'Essential'), name=u'essential')
        self.sel_essential = wx.Choice(pnl_option, choices=self.opts_essential, name=txt_essential.Name)
        self.sel_essential.default = 1
        self.sel_essential.SetSelection(self.sel_essential.default)
        
        # List all widgets to check if fields have changed after keypress
        # This is for determining if the project is saved
        self.text_widgets = {
            self.ti_package: wx.EmptyString, self.ti_version: wx.EmptyString
            }
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        RIGHT_CENTER = wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT
        
        # Buttons
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_open, 0)
        lyt_buttons.Add(btn_save, 0)
        lyt_buttons.Add(btn_preview, 0)
        #lyt_buttons.AddStretchSpacer(1)
        #lyt_buttons.Add(btn_help, 0)
        
        # Required fields
        lyt_require = wx.FlexGridSizer(0, 4, 5, 5)
        lyt_require.AddGrowableCol(1)
        lyt_require.AddGrowableCol(3)
        
        lyt_require.AddMany((
            (txt_package, 0, RIGHT_CENTER|wx.LEFT|wx.TOP, 5),
            (self.ti_package, 0, wx.EXPAND|wx.TOP, 5),
            (txt_version, 0, RIGHT_CENTER|wx.TOP, 5),
            (self.ti_version, 0, wx.EXPAND|wx.TOP|wx.RIGHT, 5),
            (txt_maintainer, 0, RIGHT_CENTER|wx.LEFT, 5),
            (self.ti_maintainer, 0, wx.EXPAND),
            (txt_email, 0, RIGHT_CENTER, 5),
            (self.ti_email, 0, wx.EXPAND|wx.RIGHT, 5),
            (txt_arch, 0, RIGHT_CENTER|wx.LEFT|wx.BOTTOM, 5),
            (self.sel_arch, 0, wx.BOTTOM, 5)
            ))
        
        pnl_require.SetSizer(lyt_require)
        pnl_require.SetAutoLayout(True)
        pnl_require.Layout()
        
        # Recommended fields
        lyt_recommend = wx.GridBagSizer()
        lyt_recommend.SetCols(4)
        lyt_recommend.AddGrowableCol(1)
        lyt_recommend.AddGrowableRow(3)
        
        lyt_recommend.Add(txt_section, (0, 2), flag=RIGHT_CENTER|wx.TOP|wx.BOTTOM, border=5)
        lyt_recommend.Add(self.ti_section, (0, 3),
                flag=wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM, border=5)
        lyt_recommend.Add(txt_synopsis, (0, 0), (1, 2), LEFT_BOTTOM|wx.LEFT, 5)
        lyt_recommend.Add(self.ti_synopsis, (1, 0), (1, 2), wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_recommend.Add(txt_priority, (1, 2), flag=RIGHT_CENTER, border=5)
        lyt_recommend.Add(self.sel_priority, (1, 3), flag=wx.EXPAND|wx.RIGHT, border=5)
        lyt_recommend.Add(txt_description, (2, 0), (1, 2), LEFT_BOTTOM|wx.LEFT|wx.TOP, 5)
        lyt_recommend.Add(self.ti_description, (3, 0), (1, 4),
                wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        pnl_recommend.SetSizer(lyt_recommend)
        pnl_recommend.SetAutoLayout(True)
        pnl_recommend.Layout()
        
        # Optional fields
        lyt_option = wx.FlexGridSizer(0, 4, 5, 5)
        
        lyt_option.AddGrowableCol(1)
        lyt_option.AddGrowableCol(3)
        lyt_option.AddSpacer(5)
        lyt_option.AddSpacer(5)
        lyt_option.AddSpacer(5)
        lyt_option.AddSpacer(5)
        lyt_option.AddMany((
            (txt_source, 0, RIGHT_CENTER|wx.LEFT, 5),
            (self.ti_source, 0, wx.EXPAND),
            (txt_homepage, 0, RIGHT_CENTER, 5),
            (self.ti_homepage, 0, wx.EXPAND|wx.RIGHT, 5),
            (txt_essential, 0, RIGHT_CENTER|wx.LEFT|wx.BOTTOM, 5),
            (self.sel_essential, 1, wx.LEFT|wx.BOTTOM, 5),
            ))
        
        pnl_option.SetSizer(lyt_option)
        pnl_option.SetAutoLayout(True)
        pnl_option.Layout()
        
        # Main background panel sizer
        # FIXME: Is background panel (self.pnl_bg) necessary
        lyt_bg = wx.BoxSizer(wx.VERTICAL)
        lyt_bg.Add(lyt_buttons, 0, wx.ALIGN_RIGHT|wx.BOTTOM, 5)
        lyt_bg.Add(wx.StaticText(self.pnl_bg, label=GT(u'Required')), 0)
        lyt_bg.Add(pnl_require, 0, wx.EXPAND)
        lyt_bg.Add(wx.StaticText(self.pnl_bg, label=GT(u'Recommended')), 0, wx.TOP, 5)
        lyt_bg.Add(pnl_recommend, 1, wx.EXPAND)
        lyt_bg.Add(wx.StaticText(self.pnl_bg, label=GT(u'Optional')), 0, wx.TOP, 5)
        lyt_bg.Add(pnl_option, 0, wx.EXPAND)
        
        self.pnl_bg.SetAutoLayout(True)
        self.pnl_bg.SetSizer(lyt_bg)
        self.pnl_bg.Layout()
        
        # Page's main sizer
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(5)
        lyt_main.Add(self.pnl_bg, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event Handlers *** #
        
        btn_open.Bind(wx.EVT_BUTTON, self.OnBrowse)
        btn_save.Bind(wx.EVT_BUTTON, self.OnSave)
        btn_preview.Bind(wx.EVT_BUTTON, self.OnPreview)
        
        # These are used for controlling the column width/size in the co-authors field
        # FIXME: Deprecated?
        wx.EVT_SIZE(self, self.OnResize)
        
        for widget in self.text_widgets:
            wx.EVT_KEY_DOWN(widget, self.OnKeyDown)
            wx.EVT_KEY_UP(widget, self.OnKeyUp)
    
    
    ## TODO: Doxygen
    def ExportBuild(self, target, installed_size=0):
        self.Export(target, u'control')
        
        absolute_filename = u'{}/control'.format(target).replace(u'//', u'/')
        
        if not os.path.isfile(absolute_filename):
            return GT(u'Control file was not created')
        
        if installed_size:
            FILE_BUFFER = open(absolute_filename, u'r')
            control_data = FILE_BUFFER.read().split(u'\n')
            FILE_BUFFER.close()
            
            size_line = u'Installed-Size: {}'.format(installed_size)
            if len(control_data) > 3:
                control_data.insert(3, size_line)
            
            else:
                control_data.append(size_line)
            
            FILE_BUFFER = open(absolute_filename, u'w')
            FILE_BUFFER.write(u'\n'.join(control_data))
            FILE_BUFFER.close()
        
        return GT(u'Control file created: {}').format(absolute_filename)
    
    
    ## TODO: Doxygen
    ## FIXME: Deprecated???
    def GetCtrlInfo(self):
        main_window = GetTopWindow()
        
        # Creat a list to store info
        ctrl_list = []
        
        getvals = (
            (u'Package',self.ti_package),
            (u'Version',self.ti_version),
            (u'Source',self.ti_source),
            (u'Section',self.ti_section),
            (u'Homepage',self.ti_homepage),
            )
        
        for key in getvals:
            key_enabled = FieldEnabled(key[1])
            
            if key_enabled and u''.join(key[1].GetValue().split(u' ')) != u'':
                if key[0] == u'Package' or key[0] == u'Version':
                    ctrl_list.append(u'{}: {}'.format(key[0], u'-'.join(key[1].GetValue().split(u' '))))
                
                else:
                    ctrl_list.append(u'{}: {}'.format(key[0], key[1].GetValue()))
        
        # Add the Maintainer
        auth_enabled = FieldEnabled(self.ti_maintainer)
        
        if auth_enabled and self.ti_maintainer.GetValue() != u'':
            ctrl_list.insert(3, u'Maintainer: {} <{}>'.format(self.ti_maintainer.GetValue(), self.ti_email.GetValue()))
        
        # Add the "choice" options
        getsels = {
            u'Architecture': (self.sel_arch,self.opts_arch),
            u'Priority': (self.sel_priority,self.opts_priority),
            u'Essential': (self.sel_essential,self.opts_essential)
        }
        
        for key in getsels:
            sel_enabled = FieldEnabled(getsels[key][0])
            
            if sel_enabled:
                if key == u'Essential' and self.sel_essential.GetCurrentSelection() == 1:
                    pass
                
                else:
                    ctrl_list.append(u'{}: {}'.format(key, getsels[key][1][getsels[key][0].GetCurrentSelection()]))
        
        # *** Get dependencies *** #
        dep_list = [] # Depends
        pre_list = [] # Pre-Depends
        rec_list = [] # Recommends
        sug_list = [] # Suggests
        enh_list = [] # Enhances
        con_list = [] # Conflicts
        rep_list = [] # Replaces
        brk_list = [] # Breaks
        
        all_deps = {
            u'Depends': dep_list,
            u'Pre-Depends': pre_list,
            u'Recommends': rec_list,
            u'Suggests': sug_list,
            u'Enhances': enh_list,
            u'Conflicts': con_list,
            u'Replaces': rep_list,
            u'Breaks': brk_list,
            }
        
        # Get amount of items to add
        dep_area = GetField(ident.DEPENDS, ident.F_LIST)
        dep_count = dep_area.GetItemCount()
        count = 0
        while count < dep_count:
            # Get each item from dependencied page
            dep_type = dep_area.GetItem(count, 0).GetText()
            dep_val = dep_area.GetItem(count, 1).GetText()
            for item in all_deps:
                if dep_type == item:
                    all_deps[item].append(dep_val)
            
            count += 1
        
        for item in all_deps:
            if len(all_deps[item]) != 0:
                ctrl_list.append(u'{}: {}'.format(item, u', '.join(all_deps[item])))
        
        # *** Get description *** #
        syn = self.ti_synopsis.GetValue()
        desc = self.ti_description.GetValue()
        # Make sure synopsis isn't empty: Join spaces
        if u''.join(syn.split(u' ')) != u'':
            ctrl_list.append(u'Description: {}'.format(syn))
            # Make sure description isn't empty: Join newlines and spaces
            if u''.join(u''.join(desc.split(u' ')).split(u'\n')) != u'':
                desc_temp = []
                for line in desc.split(u'\n'):
                    if u''.join(line.split(u' ')) == u'':
                        desc_temp.append(u' .')
                    
                    else:
                        desc_temp.append(u' {}'.format(line))
                    
                ctrl_list.append(u'\n'.join(desc_temp))
        
        ctrl_list.append(u'\n')
        return u'\n'.join(ctrl_list)
    
    
    ## TODO: Doxygen
    def GetPackageName(self):
        return self.ti_package.GetValue()
    
    
    def ImportPageInfo(self, filename):
        Logger.Debug(__name__, GT(u'Importing file: {}'.format(filename)))
        
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        # Dependencies
        depends_page = None
        for child in self.GetParent().GetChildren():
            if child.GetId() == ident.DEPENDS:
                depends_page = child
        
        def set_choice(choice_object, value, label):
            choices = choice_object.GetStrings()
            for L in choices:
                c_index = choices.index(L)
                if value == L:
                    choice_object.SetSelection(c_index)
                    return
            
            Logger.Warning(__name__, GT(u'{} option not availabled: {}'.format(label, value)))
        
        import_functions = {
            u'Package': self.ti_package.SetValue,
            u'Version': self.ti_version.SetValue,
            u'Maintainer': self.ti_maintainer.SetValue,
            u'Email': self.ti_email.SetValue,
            u'Architecture': self.sel_arch,
            u'Section': self.ti_section.SetValue,
            u'Priority': self.sel_priority,
            u'Description': self.ti_synopsis.SetValue,
            u'Source': self.ti_source.SetValue,
            u'Homepage': self.ti_homepage.SetValue,
            u'Essential': self.sel_essential,
        }
        
        dependencies = (
            u'Depends',
            u'Pre-Depends',
            u'Recommends',
            u'Suggests',
            u'Conflicts',
            u'Replaces',
            u'Breaks',
        )
        
        FILE_BUFFER = open(filename)
        control_data = FILE_BUFFER.read().split(u'\n')
        FILE_BUFFER.close()
        
        control_defs = {}
        remove_indexes = []
        for LI in control_data:
            line_index = control_data.index(LI)
            if u': ' in LI:
                key = LI.split(u': ')
                control_defs[key[0]] = key[1]
                
                remove_indexes.append(line_index)
            
            elif LI == wx.EmptyString:
                remove_indexes.append(line_index)
            
            else:
                # Remove leading whitespace from lines
                c_index = 0
                for C in LI:
                    if C != u' ':
                        break
                    
                    c_index += 1
                
                control_data[line_index] = LI[c_index:]
        
        remove_indexes.reverse()
        
        for I in remove_indexes:
            control_data.remove(control_data[I])
        
        for LI in control_data:
            if LI == u'.':
                control_data[control_data.index(LI)] = u''
        
        desc = u'\n'.join(control_data)
        
        # Extract email from Maintainer field
        if u'Maintainer' in control_defs:
            if u' <' in control_defs[u'Maintainer'] and u'>' in control_defs[u'Maintainer']:
                control_defs[u'Maintainer'] = control_defs[u'Maintainer'].split(u' <')
                control_defs[u'Email'] = control_defs[u'Maintainer'][1].split(u'>')[0]
                control_defs[u'Maintainer'] = control_defs[u'Maintainer'][0]
        
        for label in control_defs:
            if label in dependencies:
                if depends_page != None:
                    depends_page.ImportPageInfo(label, control_defs[label])
                
                else:
                    Logger.Warning(__name__, GT(u'Could not set {}: {}'.format(label, control_defs[label])))
            
            elif label in import_functions:
                if isinstance(import_functions[label], wx.Choice):
                    set_choice(import_functions[label], control_defs[label], label)
                
                else:
                    import_functions[label](control_defs[label])
        
        if desc != wx.EmptyString:
            self.ti_description.SetValue(desc)
    
    
    ## Tells the build script whether page should be built
    #  
    #  \override dbr.wizard.WizardPage.IsExportable
    def IsExportable(self):
        # Build page must always be built
        return True
    
    
    ## Retrieves information for control file export
    #  
    #  \param string_format
    #        \b \e bool : If True, only string-formatted info is returned
    #  \return
    #        \b \e tuple(str, str) : A tuple containing the filename & a string representation of control file formatted for text output
    def GetPageInfo(self, string_format=False):
        if string_format:
            return self.GetCtrlInfo()
        
        return (__name__, self.GetCtrlInfo())
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event=None):
        main_window = GetTopWindow()
        
        wildcards = (
            GT(u'All files'), u'*',
            GT(u'CONTROL file'), u'CONTROL',
        )
        
        browse_dialog = GetFileOpenDialog(main_window, GT(u'Open File'), wildcards)
        if ShowDialog(browse_dialog):
            file_path = browse_dialog.GetPath()
            self.ImportPageInfo(file_path)
    
    
    ## TODO: Doxygen
    def OnCtrlKey(self, event=None):
        key = event.GetKeyCode()
        mod = event.GetModifiers()
        
        if mod == 2 and key == 80:
            self.OnPreview(None)
        
        if event:
            event.Skip()
    
    
    ## Determining of project is modified
    #  
    #  TODO: Doxygen
    def OnKeyDown(self, event=None):
        for widget in self.text_widgets:
            self.text_widgets[widget] = widget.GetValue()
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def OnKeyUp(self, event=None):
        main_window = GetTopWindow()
        
        modified = False
        for widget in self.text_widgets:
            if widget.GetValue() != self.text_widgets[widget]:
                modified = True
        
        main_window.SetSavedStatus(modified)
        
        if event:
            event.Skip()
    
    
    ## Show a preview of the control file
    def OnPreview(self, event=None):
        control = self.GetCtrlInfo()
        
        # Ensure only one empty newline at end of preview (same as actual output)
        control = control.rstrip(u'\n') + u'\n'
        
        dia = wx.Dialog(self, title=GT(u'Control File Preview'), size=(500,400))
        preview = MultilineTextCtrlPanel(dia, style=wx.TE_READONLY)
        preview.SetValue(control)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND|wx.ALL, 5)
        
        dia.SetSizer(dia_sizer)
        dia.Layout()
        
        dia.ShowModal()
        dia.Destroy()
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Define
    def OnResize(self, event=None):
        #self.ReLayout()
        pass
    
    
    ## TODO: Doxygen
    def OnSave(self, event=None):
        main_window = GetTopWindow()
        
        wildcards = (
            GT(u'All files'), u'*',
        )
        
        save_dialog = GetFileSaveDialog(main_window, GT(u'Save Control Information'), wildcards)
        if ShowDialog(save_dialog):
            file_path = save_dialog.GetPath()
            self.Export(os.path.dirname(file_path), os.path.basename(file_path))
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Unfinished???
    def ReLayout(self):
        # Organize all widgets correctly
        lc_width = self.coauth.GetSize()[0]
        self.coauth.SetColumnWidth(0, lc_width/2)
    
    
    ## Resets all fields on page to default values
    def ResetPageInfo(self):
        for child in self.pnl_bg.GetChildren():
            if isinstance(child, (wx.TextCtrl, wx.ComboBox)):
                # Can't use Clear() method for wx.ComboBox
                child.SetValue(wx.EmptyString)
            
            elif isinstance(child, wx.Choice):
                # wx.Choice instances should have custom member wx.Choice.default set
                child.SetSelection(child.default)
    
    
    ## TODO: Doxygen
    def SetFieldDataLegacy(self, data):
        if isinstance(data, str):
            # Decode to unicode string if input is byte string
            data = data.decode(u'utf-8')
        
        control_data = data.split(u'\n')
        
        # Remove newline at end of document required by dpkg
        if control_data[-1] == u'\n':
            control_data = control_data[:-1]
        
        # Fields that use "SetValue()" function
        set_value_fields = (
            (u'Package', self.ti_package), (u'Version', self.ti_version),
            (u'Source', self.ti_source), (u'Section', self.ti_section),
            (u'Homepage', self.ti_homepage), (u'Description', self.ti_synopsis),
            )
        
        # Fields that use "SetSelection()" function
        set_selection_fields = (
            (u'Architecture', self.sel_arch, self.opts_arch),
            (u'Priority', self.sel_priority, self.opts_priority),
            (u'Essential', self.sel_essential, self.opts_essential),
            )
        
        # Store Dependencies
        depends_containers = (
            [u'Depends'], [u'Pre-Depends'], [u'Recommends'], [u'Suggests'],
            [u'Enhances'], [u'Conflicts'], [u'Replaces'], [u'Breaks'],
            )
        
        # Anything left over is dumped into this list then into the description
        leftovers = []
        
        # Separate Maintainer for later since is divided by Author/Email
        author = wx.EmptyString
        
        for field in control_data:
            if u': ' in field:
                f1 = field.split(u': ')[0]
                f2 = u': '.join(field.split(u': ')[1:]) # For dependency fields that have ": " in description
                # Catch Maintainer and put in author variable
                if f1 == u'Maintainer':
                    author = f2
                
                # Set the rest of the wx.TextCtrl fields
                for setval in set_value_fields:
                    if f1 == setval[0]:
                        setval[1].SetValue(f2)
                
                # Set the wx.Choice fields
                for setsel in set_selection_fields:
                    if f1 == setsel[0]:
                        try:
                            setsel[1].SetSelection(setsel[2].index(f2))
                        
                        except ValueError:
                            pass
                
                # Set dependencies
                for container in depends_containers:
                    if f1 == container[0]:
                        for dep in f2.split(u', '):
                            container.append(dep)
            
            else:
                if field == u' .':
                    # Add a blank line for lines marked with a "."
                    leftovers.append(wx.EmptyString)
                
                elif field == u'\n' or field == u' ' or field == wx.EmptyString:
                    # Ignore empty lines
                    pass
                
                elif field[0] == u' ':
                    # Remove the first space generated in the description
                    leftovers.append(field[1:])
                
                else:
                    leftovers.append(field)
        
        # Put leftovers in long description
        self.ti_description.SetValue(u'\n'.join(leftovers))
        
        # Set the "Author" and "Email" fields
        if author != wx.EmptyString:
            self.ti_maintainer.SetValue(author.split(u' <')[0])
            self.ti_email.SetValue(author.split(u' <')[1].split(u'>')[0])
        
        # Return depends data to parent to be sent to page_depends
        return depends_containers
