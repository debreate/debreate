# -*- coding: utf-8 -*-

# This panel displays the field input of the control file


import os, wx
from wx.combo import OwnerDrawnComboBox

from dbr.buttons    import ButtonBrowse64
from dbr.buttons    import ButtonPreview64
from dbr.buttons    import ButtonSave64
from dbr.charctrl   import CharCtrl
from dbr.custom     import OpenFile
from dbr.custom     import SaveFile
from dbr.functions  import FieldEnabled
from dbr.language   import GT
from globals.ident  import ID_CONTROL


## This panel displays the field input of the control file
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_CONTROL, name=GT(u'Control'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        self.bg = wx.Panel(self)
        
        # Buttons to open, save, & preview control file
        btn_open = ButtonBrowse64(self.bg)
        btn_open.SetToolTipString(GT(u'Import a control file'))
        btn_save = ButtonSave64(self.bg)
        btn_save.SetToolTipString(GT(u'Export control file'))
        btn_preview = ButtonPreview64(self.bg)
        btn_preview.SetToolTipString(GT(u'Preview control file'))
        
        pack_txt = wx.StaticText(self.bg, label=GT(u'Package'))
        pack_txt.req = True
        self.pack = CharCtrl(self.bg)
        self.pack.req = True
        
        tt_pack = GT(u'Name of the package/software')
        pack_txt.SetToolTipString(tt_pack)
        self.pack.SetToolTipString(tt_pack)
        
        ver_txt = wx.StaticText(self.bg, label=GT(u'Version'))
        ver_txt.req = True
        self.ver = CharCtrl(self.bg)
        self.ver.req = True
        
        tt_ver = GT(u'Package/Software release version')
        ver_txt.SetToolTipString(tt_ver)
        self.ver.SetToolTipString(tt_ver)
        
        auth_txt = wx.StaticText(self.bg, label=GT(u'Maintainer'))
        auth_txt.req = True
        self.auth = wx.TextCtrl(self.bg)
        self.auth.req = True
        
        tt_auth = GT(u'Package/Software maintainer\'s full name')
        auth_txt.SetToolTipString(tt_auth)
        self.auth.SetToolTipString(tt_auth)
        
        email_txt = wx.StaticText(self.bg, label=GT(u'Email'))
        email_txt.req = True
        self.email = wx.TextCtrl(self.bg)
        self.email.req = True
        
        tt_email = GT(u'Package/Software maintaner\'s email address')
        email_txt.SetToolTipString(tt_email)
        self.email.SetToolTipString(tt_email)
        
        self.arch_opt = (
            u'all', u'alpha', u'amd64', u'arm', u'arm64', u'armeb', u'armel',
            u'armhf', u'avr32', u'hppa', u'i386', u'ia64', u'lpia', u'm32r',
            u'm68k', u'mips', u'mipsel', u'powerpc', u'powerpcspe', u'ppc64',
            u's390', u's390x', u'sh3', u'sh3eb', u'sh4', u'sh4eb', u'sparc',
            u'sparc64',
            )
        
        arch_txt = wx.StaticText(self.bg, label=GT(u'Architecture'))
        self.arch = wx.Choice(self.bg, choices=self.arch_opt)
        self.arch.default = 0
        self.arch.SetSelection(self.arch.default)
        
        tt_arch = u'{}\n\n{}'.format(GT(u'Architecture on which software is designed to run'), GT(u'all = platform independent'))
        arch_txt.SetToolTipString(tt_arch)
        self.arch.SetToolTipString(tt_arch)
        
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
        
        sect_txt = wx.StaticText(self.bg, label=GT(u'Section'))
        self.sect = OwnerDrawnComboBox(self.bg, choices=self.sect_opt)
        
        tt_sect = GT(u'Section under which package managers will categorize package')
        sect_txt.SetToolTipString(tt_sect)
        self.sect.SetToolTipString(tt_sect)
        
        self.prior_opt = (
            u'optional', u'standard', u'important', u'required', u'extra',
            )
        
        prior_txt = wx.StaticText(self.bg, label=GT(u'Priority'))
        self.prior = wx.Choice(self.bg, choices=self.prior_opt)
        self.prior.SetSelection(0)
        
        tt_prior = GT(u'Priority of the package on the target system')
        prior_txt.SetToolTipString(tt_prior)
        self.prior.SetToolTipString(tt_prior)
        
        syn_txt = wx.StaticText(self.bg, label=GT(u'Short Description'))
        self.syn = wx.TextCtrl(self.bg)
        
        tt_syn = GT(u'Synopsis or one-line description')
        syn_txt.SetToolTipString(tt_syn)
        self.syn.SetToolTipString(tt_syn)
        
        desc_txt = wx.StaticText(self.bg, label=GT(u'Long Description'))
        self.desc = wx.TextCtrl(self.bg, style=wx.TE_MULTILINE)
        
        tt_desc = GT(u'Longer, multi-line description')
        desc_txt.SetToolTipString(tt_desc)
        self.desc.SetToolTipString(tt_desc)
        
        # ***** Optional Group ***** #
        src_txt = wx.StaticText(self.bg, label=GT(u'Source'))
        self.src = wx.TextCtrl(self.bg)
        
        tt_src = GT(u'Name of upstream source package')
        src_txt.SetToolTipString(tt_src)
        self.src.SetToolTipString(tt_src)
        
        url_txt = wx.StaticText(self.bg, label=GT(u'Homepage'))
        self.url = wx.TextCtrl(self.bg)
        
        tt_url = GT(u'Software\'s/Package\'s homepage URL')
        url_txt.SetToolTipString(tt_url)
        self.url.SetToolTipString(tt_url)
        
        self.ess_opt = (
            u'yes', u'no',
            )
        
        ess_txt = wx.StaticText(self.bg, label=GT(u'Essential'))
        self.ess = wx.Choice(self.bg, choices=self.ess_opt)
        self.ess.default = 1
        self.ess.SetSelection(self.ess.default)
        
        tt_ess = GT(u'Whether or not the package is essential to the system for stability/functionality')
        ess_txt.SetToolTipString(tt_ess)
        self.ess.SetToolTipString(tt_ess)
        
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
        
        # *** Layout *** #
        
        # Buttons
        layout_buttons = wx.BoxSizer(wx.HORIZONTAL)
        layout_buttons.Add(btn_open, 0)
        layout_buttons.Add(btn_save, 0)
        layout_buttons.Add(btn_preview, 0)
        
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
            (syn_txt, 0),
            (self.syn, 0, wx.EXPAND),
            ))
        bbox_description.AddSpacer(5)
        bbox_description.AddMany((
            (desc_txt, 0),
            (self.desc, 1, wx.EXPAND),
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
        layout_bg.Add(layout_buttons, 0, wx.ALL, 5)
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
        
        # Set Ctrl+P hotkey to show preview of control file
        for child in self.bg.GetChildren():
            wx.EVT_KEY_DOWN(child, self.OnCtrlKey)
        
        # Defines fields to be accessed
        wx.EVT_SHOW(self, self.OnShow)
        
        for widget in self.text_widgets:
            wx.EVT_KEY_DOWN(widget, self.OnKeyDown)
            wx.EVT_KEY_UP(widget, self.OnKeyUp)
    
    
    ## Saving project
    def GatherData(self):
        data = self.GetCtrlInfo()
        return u'<<CTRL>>\n{}<</CTRL>>'.format(data)
    
    
    ## TODO: Doxygen
    def GetCtrlInfo(self):
        main_window = wx.GetApp().GetTopWindow()
        
        # Creat a list to store info
        ctrl_list = []
        
        getvals = (
            (u'Package', self.pack),
            (u'Version', self.ver),
            (u'Source', self.src),
            (u'Section', self.sect),
            (u'Homepage', self.url),
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
            u'Essential': (self.ess,self.ess_opt),
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
            # Get each item from dependencies page
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
    def OnBrowse(self, event=None):
        main_window = wx.GetApp().GetTopWindow()
        
        cont = False
        if main_window.cust_dias.IsChecked():
            dia = OpenFile(self)
            if dia.DisplayModal():
                cont = True
        
        else:
            dia = wx.FileDialog(self, GT(u'Open File'), os.getcwd(), style=wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                cont = True
        
        if cont:
            file_path = dia.GetPath()
            
            FILE_BUFFER = open(file_path, u'r')
            control_data = FILE_BUFFER.read()
            FILE_BUFFER.close()
            
            depends_data = self.SetFieldData(control_data)
            main_window.page_depends.SetFieldData(depends_data)
    
    
    ## TODO: Doxygen
    def OnCtrlKey(self, event=None):
        key = event.GetKeyCode()
        mod = event.GetModifiers()
        
        if mod == 2 and key == 80:
            self.OnPreview(None)
        
        if event:
            event.Skip()
    
    
    ## Determins if project has been modified
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
        preview = wx.TextCtrl(dia, style=wx.TE_MULTILINE|wx.TE_READONLY)
        preview.SetValue(control)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND)
        
        dia.SetSizer(dia_sizer)
        dia.Layout()
        
        dia.ShowModal()
        dia.Destroy()
    
    
    ## TODO: Doxygen
    def OnSave(self, event=None):
        main_window = wx.GetApp().GetTopWindow()
        
        # Get data to write to control file
        control = self.GetCtrlInfo().encode(u'utf-8')
        
        # Saving?
        cont = False
        
        # Open a "Save Dialog"
        if main_window.cust_dias.IsChecked():
            dia = SaveFile(self, GT(u'Save Control Information'))
            dia.SetFilename(u'control')
            if dia.DisplayModal():
                cont = True
                path = u'{}/{}'.format(dia.GetPath(), dia.GetFilename())
        
        else:
            dia = wx.FileDialog(self, u'Save Control Information', os.getcwd(),
                style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
            dia.SetFilename(u'control')
            
            if dia.ShowModal() == wx.ID_OK:
                cont = True
                path = dia.GetPath()
        
        if cont:
            FILE_BUFFER = open(path, u'w')
            FILE_BUFFER.write(control)
            FILE_BUFFER.close()
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Define
    def OnShow(self, event=None):
        pass
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Unfinished???
    def ReLayout(self):
        # Organize all widgets correctly
        lc_width = self.coauth.GetSize()[0]
        self.coauth.SetColumnWidth(0, lc_width/2)
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.pack.Clear()
        self.ver.Clear()
        self.arch.SetSelection(0)
        self.src.Clear()
        self.sect.Clear()
        self.prior.SetSelection(0)
        self.url.Clear()
        self.ess.SetSelection(1)
        self.syn.Clear()
        self.desc.Clear()
        self.auth.Clear()
        self.email.Clear()
    
    
    ## Opening Project/File & Setting Fields
    def SetFieldData(self, data):
        if type(data) == type(u''):
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
