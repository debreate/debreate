# -*- coding: utf-8 -*-

## \package wiz_bin.control


import os, wx

from dbr.buttons        import ButtonBrowse64
from dbr.buttons        import ButtonPreview64
from dbr.buttons        import ButtonSave64
from dbr.charctrl       import CharCtrl
from dbr.dialogs        import GetFileOpenDialog
from dbr.dialogs        import GetFileSaveDialog
from dbr.dialogs        import ShowDialog
from dbr.functions      import FieldEnabled
from dbr.help           import HelpButton
from dbr.language       import GT
from dbr.log            import Logger
from dbr.textinput      import MultilineTextCtrlPanel
from dbr.wizard         import WizardPage
from globals.errorcodes import dbrerrno
from globals.ident      import ID_CONTROL
from globals.ident      import ID_DEPENDS
from globals.tooltips   import SetPageToolTips


## This panel displays the field input of the control file
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ID_CONTROL)
        
        # Bypass checking this page for build
        # This is mandatory & done manually
        self.prebuild_check = False
        
        self.SetScrollbars(0, 20, 0, 0)
        
        self.bg = wx.Panel(self)
        
        # Buttons to open, save, & preview control file
        btn_open = ButtonBrowse64(self.bg)
        btn_save = ButtonSave64(self.bg)
        btn_preview = ButtonPreview64(self.bg)
        
        # Button to open a help dialog (WIP)
        btn_help = HelpButton(self.bg)
        
        pack_txt = wx.StaticText(self.bg, label=GT(u'Package'), name=u'package')
        pack_txt.req = True
        self.pack = CharCtrl(self.bg, name=pack_txt.Name)
        self.pack.req = True
        
        ver_txt = wx.StaticText(self.bg, label=GT(u'Version'), name=u'version')
        ver_txt.req = True
        self.ver = CharCtrl(self.bg, name=ver_txt.Name)
        self.ver.req = True
        
        auth_txt = wx.StaticText(self.bg, label=GT(u'Maintainer'), name=u'maintainer')
        auth_txt.req = True
        self.auth = wx.TextCtrl(self.bg, name=auth_txt.Name)
        self.auth.req = True
        
        email_txt = wx.StaticText(self.bg, label=GT(u'Email'), name=u'email')
        email_txt.req = True
        self.email = wx.TextCtrl(self.bg, name=email_txt.Name)
        self.email.req = True
        
        self.arch_opt = (
            u'all', u'alpha', u'amd64', u'arm', u'arm64', u'armeb', u'armel',
            u'armhf', u'avr32', u'hppa', u'i386', u'ia64', u'lpia',
            u'm32r', u'm68k', u'mips', u'mipsel', u'powerpc',
            u'powerpcspe', u'ppc64', u's390', u's390x', u'sh3',
            u'sh3eb', u'sh4', u'sh4eb', u'sparc', u'sparc64')
        
        arch_txt = wx.StaticText(self.bg, label=GT(u'Architecture'), name=u'arch')
        self.arch = wx.Choice(self.bg, choices=self.arch_opt, name=arch_txt.Name)
        self.arch.default = 0
        self.arch.SetSelection(self.arch.default)
        
        # ***** Recommended Group ***** #
        self.sect_opt = (
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
        
        sect_txt = wx.StaticText(self.bg, label=GT(u'Section'), name=u'section')
        self.sect = wx.ComboBox(self.bg, choices=self.sect_opt, name=sect_txt.Name)
        
        self.prior_opt = (
            u'optional', u'standard', u'important', u'required', u'extra',
            )
        
        prior_txt = wx.StaticText(self.bg, label=GT(u'Priority'), name=u'priority')
        self.prior = wx.Choice(self.bg, choices=self.prior_opt, name=prior_txt.Name)
        self.prior.default = 0
        self.prior.SetSelection(self.prior.default)
        
        syn_txt = wx.StaticText(self.bg, label=GT(u'Short Description'), name=u'synopsis')
        self.syn = wx.TextCtrl(self.bg, name=syn_txt.Name)
        
        desc_txt = wx.StaticText(self.bg, label=GT(u'Long Description'), name=u'description')
        self.desc = MultilineTextCtrlPanel(self.bg, name=desc_txt.Name)
        
        # ***** Optional Group ***** #
        src_txt = wx.StaticText(self.bg, label=GT(u'Source'), name=u'source')
        self.src = wx.TextCtrl(self.bg, name=src_txt.Name)
        
        url_txt = wx.StaticText(self.bg, label=GT(u'Homepage'), name=u'homepage')
        self.url = wx.TextCtrl(self.bg, name=url_txt.Name)
        
        self.ess_opt = (
            u'yes', u'no',
            )
        
        ess_txt = wx.StaticText(self.bg, label=GT(u'Essential'), name=u'essential')
        self.ess = wx.Choice(self.bg, choices=self.ess_opt, name=ess_txt.Name)
        self.ess.default = 1
        self.ess.SetSelection(self.ess.default)
        
        self.bins = (
            (self.pack, self.arch, self.ver, self.auth, self.email),
            (self.sect, self.prior),
            (self.src, self.url, self.ess),
            )
        
        # List all widgets to check if fields have changed after keypress
        # This is for determining if the project is saved
        self.text_widgets = {
            self.pack: wx.EmptyString, self.ver: wx.EmptyString
            }
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        # Buttons
        layout_buttons = wx.BoxSizer(wx.HORIZONTAL)
        layout_buttons.Add(btn_open, 0)
        layout_buttons.Add(btn_save, 0)
        layout_buttons.Add(btn_preview, 0)
        layout_buttons.AddStretchSpacer(1)
        layout_buttons.Add(btn_help, 0)
        
        # Required fields
        layout_required = wx.FlexGridSizer(0, 4, 5, 5)
        layout_required.AddGrowableCol(1)
        layout_required.AddGrowableCol(3)
        
        layout_required.AddSpacer(5)
        layout_required.AddSpacer(5)
        layout_required.AddSpacer(5)
        layout_required.AddSpacer(5)
        layout_required.AddMany((
            (pack_txt), (self.pack, 0, wx.EXPAND), (ver_txt), (self.ver, 0, wx.EXPAND),
            (auth_txt), (self.auth, 0, wx.EXPAND), (email_txt), (self.email, 0, wx.EXPAND),
            arch_txt, (self.arch)
            ))
        
        border_info = wx.StaticBox(self.bg, label=GT(u'Required'))
        bbox_info = wx.StaticBoxSizer(border_info, wx.VERTICAL)
        
        bbox_info.Add(layout_required, 0, wx.EXPAND)
        
        # Recommended fields
        r_temp = wx.FlexGridSizer(0, 4, 5, 5)
        r_temp.AddGrowableCol(1)
        r_temp.AddGrowableCol(3)
        
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddMany((
            (sect_txt),
            (self.sect, 0, wx.EXPAND),
            (prior_txt),
            (self.prior),
            ))
        
        border_description = wx.StaticBox(self.bg, label=GT(u'Recommended'))
        bbox_description = wx.StaticBoxSizer(border_description, wx.VERTICAL)
        
        bbox_description.AddSpacer(5)
        bbox_description.Add(r_temp, 0, wx.EXPAND)
        bbox_description.AddSpacer(5)
        bbox_description.AddMany((
            (syn_txt, 0), (self.syn, 0, wx.EXPAND),
            ))
        bbox_description.AddSpacer(5)
        bbox_description.AddMany((
            (desc_txt, 0), (self.desc, 1, wx.EXPAND),
            ))
        
        # Optional fields
        b_temp = wx.FlexGridSizer(0, 4, 5, 5)
        
        b_temp.AddGrowableCol(1)
        b_temp.AddGrowableCol(3)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddMany((
            (src_txt), (self.src, 0, wx.EXPAND),
            (url_txt), (self.url, 0, wx.EXPAND),
            (ess_txt), (self.ess, 1),
            ))
        
        border_author = wx.StaticBox(self.bg, label=GT(u'Optional'))
        bbox_author = wx.StaticBoxSizer(border_author, wx.VERTICAL)
        
        bbox_author.Add(b_temp, 0, wx.EXPAND)
        
        # Main background panel sizer
        # FIXME: Is background panel (self.bg) necessary
        layout_bg = wx.BoxSizer(wx.VERTICAL)
        layout_bg.Add(layout_buttons, 0, wx.EXPAND|wx.ALL, 5)
        layout_bg.Add(bbox_info, 0, wx.EXPAND|wx.ALL, 5)
        layout_bg.Add(bbox_description, 1, wx.EXPAND|wx.ALL, 5)
        layout_bg.Add(bbox_author, 0, wx.EXPAND|wx.ALL, 5)
        
        self.bg.SetAutoLayout(True)
        self.bg.SetSizer(layout_bg)
        self.bg.Layout()
        
        # Page's main sizer
        layout_main = wx.BoxSizer(wx.VERTICAL)
        layout_main.Add(self.bg, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_main)
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
        main_window = wx.GetApp().GetTopWindow()
        
        # Creat a list to store info
        ctrl_list = []
        
        getvals = (
            (u'Package',self.pack),
            (u'Version',self.ver),
            (u'Source',self.src),
            (u'Section',self.sect),
            (u'Homepage',self.url),
            )
        
        for key in getvals:
            key_enabled = FieldEnabled(key[1])
            
            if key_enabled and u''.join(key[1].GetValue().split(u' ')) != u'':
                if key[0] == u'Package' or key[0] == u'Version':
                    ctrl_list.append(u'{}: {}'.format(key[0], u'-'.join(key[1].GetValue().split(u' '))))
                
                else:
                    ctrl_list.append(u'{}: {}'.format(key[0], key[1].GetValue()))
        
        # Add the Maintainer
        auth_enabled = FieldEnabled(self.auth)
        
        if auth_enabled and self.auth.GetValue() != u'':
            ctrl_list.insert(3, u'Maintainer: {} <{}>'.format(self.auth.GetValue(), self.email.GetValue()))
        
        # Add the "choice" options
        getsels = {
            u'Architecture': (self.arch,self.arch_opt),
            u'Priority': (self.prior,self.prior_opt),
            u'Essential': (self.ess,self.ess_opt)
        }
        
        for key in getsels:
            sel_enabled = FieldEnabled(getsels[key][0])
            
            if sel_enabled:
                if key == u'Essential' and self.ess.GetCurrentSelection() == 1:
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
        dep_area = main_window.page_depends.dep_area
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
        syn = self.syn.GetValue()
        desc = self.desc.GetValue()
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
        return self.pack.GetValue()
    
    
    def ImportPageInfo(self, filename):
        Logger.Debug(__name__, GT(u'Importing file: {}'.format(filename)))
        
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        # Dependencies
        depends_page = None
        for child in self.GetParent().GetChildren():
            if child.GetId() == ID_DEPENDS:
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
            u'Package': self.pack.SetValue,
            u'Version': self.ver.SetValue,
            u'Maintainer': self.auth.SetValue,
            u'Email': self.email.SetValue,
            u'Architecture': self.arch,
            u'Section': self.sect.SetValue,
            u'Priority': self.prior,
            u'Description': self.syn.SetValue,
            u'Source': self.src.SetValue,
            u'Homepage': self.url.SetValue,
            u'Essential': self.ess,
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
            self.desc.SetValue(desc)
    
    
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
        main_window = wx.GetApp().GetTopWindow()
        
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
        main_window = wx.GetApp().GetTopWindow()
        
        modified = False
        for widget in self.text_widgets:
            if widget.GetValue() != self.text_widgets[widget]:
                modified = True
        
        main_window.SetSavedStatus(modified)
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def OnPreview(self, event=None):
        # Show a preview of the control file
        control = self.GetCtrlInfo()
        
        dia = wx.Dialog(self, title=GT(u'Preview'), size=(500,400))
        preview = MultilineTextCtrlPanel(dia, style=wx.TE_READONLY)
        preview.SetValue(control)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND)
        
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
        main_window = wx.GetApp().GetTopWindow()
        
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
        for child in self.bg.GetChildren():
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
            (u'Package', self.pack), (u'Version', self.ver),
            (u'Source', self.src), (u'Section', self.sect),
            (u'Homepage', self.url), (u'Description', self.syn),
            )
        
        # Fields that use "SetSelection()" function
        set_selection_fields = (
            (u'Architecture', self.arch, self.arch_opt),
            (u'Priority', self.prior, self.prior_opt),
            (u'Essential', self.ess, self.ess_opt),
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
        self.desc.SetValue(u'\n'.join(leftovers))
        
        # Set the "Author" and "Email" fields
        if author != wx.EmptyString:
            self.auth.SetValue(author.split(u' <')[0])
            self.email.SetValue(author.split(u' <')[1].split(u'>')[0])
        
        # Return depends data to parent to be sent to page_depends
        return depends_containers
