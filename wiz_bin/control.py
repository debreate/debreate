# -*- coding: utf-8 -*-

# This panel displays the field input of the control file


import wx, os

import dbr
from dbr.language import GT
from dbr.constants import ID_CONTROL, custom_errno, ID_DEPENDS
from dbr.wizard import WizardPage
from dbr import Logger
from dbr.functions import GetFileOpenDialog, ShowDialog, GetFileSaveDialog


class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ID_CONTROL)
        
        self.wizard = parent
        self.debreate = parent.parent
        
        self.SetScrollbars(0, 20, 0, 0)
        
        self.bg = wx.Panel(self)
        
        # Buttons to Open, Save & Preview control file
        button_open = dbr.ButtonBrowse64(self.bg)
        button_save = dbr.ButtonSave64(self.bg)
        button_preview = dbr.ButtonPreview64(self.bg)
        
        wx.EVT_BUTTON(button_open, -1, self.OnBrowse)
        wx.EVT_BUTTON(button_save, -1, self.OnSave)
        wx.EVT_BUTTON(button_preview, -1, self.OnPreview)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(button_open, 0)
        button_sizer.Add(button_save, 0)
        button_sizer.Add(button_preview, 0)
        
        
        # ***** Required Group ***** #
        # Key:  B - Binary
        #       S - Source
        #       D - Debian Source Control (*.dsc)
        #       C - Changes
        #      [m]- mandatory
        #      [r]- recommended
        
        # ----- Package ( B[m], SB[m] )
        self.pack_txt = wx.StaticText(self.bg, -1, GT(u'Package'))
        self.pack = dbr.CharCtrl(self.bg)
        
        # ----- Version ( B[m], D[m], C[m] )
        self.ver_txt = wx.StaticText(self.bg, -1, GT(u'Version'))
        self.ver = dbr.CharCtrl(self.bg)
        
        # ----- Maintainer ( B[m], S[m], D[m], C[m] )
        self.auth_txt = wx.StaticText(self.bg, -1, GT(u'Maintainer'))
        self.auth = wx.TextCtrl(self.bg, -1)
        self.email_txt = wx.StaticText(self.bg, -1, GT(u'Email'))
        self.email = wx.TextCtrl(self.bg, -1)
        
        # ----- Architecture ( B[m], SB[m], D, C[m] )
        self.arch_opt = (
            u'all', u'alpha', u'amd64', u'arm', u'arm64', u'armeb', u'armel',
            u'armhf', u'avr32', u'hppa', u'i386', u'ia64', u'lpia',
            u'm32r', u'm68k', u'mips', u'mipsel', u'powerpc',
            u'powerpcspe', u'ppc64', u's390', u's390x', u'sh3',
            u'sh3eb', u'sh4', u'sh4eb', u'sparc', u'sparc64')
        self.arch_txt = wx.StaticText(self.bg, -1, GT(u'Architecture'))
        self.arch = wx.Choice(self.bg, -1, choices=self.arch_opt)
        self.arch.default = 0
        self.arch.SetSelection(self.arch.default)
        
        # ***** Recommended Group ***** #
        # ----- Section ( B[r], S[r], SB[r] )
        self.sect_opt = (u'admin', u'cli-mono', u'comm', u'database', u'devel', u'debug', u'doc', u'editors',
            u'electronics', u'embedded', u'fonts', u'games', u'gnome', u'graphics', u'gnu-r', u'gnustep',
            u'hamradio', u'haskell', u'httpd', u'interpreters', u'java', u'kde', u'kernel', u'libs', u'libdevel',
            u'lisp', u'localization', u'mail', u'math', u'metapackages', u'misc', u'net', u'news', u'ocaml', u'oldlibs',
            u'otherosfs', u'perl', u'php', u'python', u'ruby', u'science', u'shells', u'sound', u'tex', u'text',
            u'utils', u'vcs', u'video', u'web', u'x11', u'xfce', u'zope')
        self.sect_txt = wx.StaticText(self.bg, -1, GT(u'Section'))
        #self.sect = db.Combo(self.bg, -1, choices=self.sect_opt)
        self.sect = wx.ComboBox(self.bg, -1, choices=self.sect_opt)
        
        # ----- Priority ( B[r], S[r], SB[r] )
        self.prior_opt = (u'optional', u'standard', u'important', u'required', u'extra')
        self.prior_txt = wx.StaticText(self.bg, -1, GT(u'Priority'))
        self.prior = wx.Choice(self.bg, -1, choices=self.prior_opt)
        self.prior.default = 0
        self.prior.SetSelection(self.prior.default)
        
        # ----- Description ( B[m], SB[m], C[m] )
        self.syn_txt = wx.StaticText(self.bg, -1, GT(u'Short Description'))
        self.syn = wx.TextCtrl(self.bg)
        self.desc_txt = wx.StaticText(self.bg, -1, GT(u'Long Description'))
        self.desc = wx.TextCtrl(self.bg, style=wx.TE_MULTILINE)
        
        # ***** Optional Group ***** #
        # ----- Source ( B, S[m], D[m], C[m] )
        self.src_txt = wx.StaticText(self.bg, -1, GT(u'Source'))
        self.src = wx.TextCtrl(self.bg, -1)
        
        # ----- Homepage ( B, S, SB, D )
        self.url_txt = wx.StaticText(self.bg, -1, GT(u'Homepage'))
        self.url = wx.TextCtrl(self.bg)
        
        # ----- Essential ( B, SB )
        self.ess_opt = (u'yes', u'no')
        self.ess_txt = wx.StaticText(self.bg, -1, GT(u'Essential'))
        self.ess = wx.Choice(self.bg, -1, choices=self.ess_opt)
        self.ess.default = 1
        self.ess.SetSelection(self.ess.default)
        
        # ----- Binary (Mandatory, Recommended, Optional, Not Used)
        # Not in list: Description[m], Depends[o], Installed-Size[o]
        self.bins = (	(self.pack, self.arch, self.ver, self.auth, self.email),
                        (self.sect, self.prior),
                        (self.src, self.url, self.ess),
                        #(self.stdver, self.coauth, self.format, self.bin, self.files, self.date, self.editor,
                        #self.eemail, self.changes, self.dist, self.urge, self.closes)
                        )
        
        # ----- Source (Mandatory, Recommended, Optional, Not Used)
        # Not in list: Build-Depends[o]
#        self.srcs = (	(self.src, self.auth, self.email, self.pack, self.arch),
#                        (self.sect, self.prior, self.stdver, self.sect, self.prior),
#                        (self.coauth, self.url, self.ess),
#                        (self.ver, self.format, self.bin, self.files, self.date, self.editor, self.eemail,
#                        self.changes, self.dist, self.urge, self.closes)
#                        )
        
        # ----- Debian Source Control (.dsc) (Mandatory, Recommended, Optional, Not Used)
        # Not in list: Build-Depends
#        self.dscs = (	(self.src, self.auth, self.email, self.ver, self.format, self.files),
#                        [self.stdver],
#                        (self.coauth, self.url, self.arch, self.bin),
#                        (self.pack, self.sect, self.prior, self.ess, self.syn, self.desc, self.date, self.editor,
#                        self.eemail, self.changes, self.dist, self.urge, self.closes)
#                        )

        # ----- Changes (Mandatory, Recommended, Optional, Not Used)
        # Not in list: Description
#        self.chngs = (	(self.src, self.auth, self.email, self.arch, self.ver, self.format, self.bin, self.files,
#                         self.date, self.dist, self.changes),
#                        [self.urge],
#                        (self.editor, self.closes),
#                        (self.pack, self.sect, self.prior, self.url, self.ess, self.stdver, self.coauth)
#                        )
        
        
        # Divide the fields into different groups (Info, Description, Authors, and Other)
        
        # ----- Changed to "Required"
        self.box_info = wx.FlexGridSizer(0, 4, 5, 5)
        self.box_info.AddGrowableCol(1)
        self.box_info.AddGrowableCol(3)
        self.box_info.AddSpacer(5)
        self.box_info.AddSpacer(5)
        self.box_info.AddSpacer(5)
        self.box_info.AddSpacer(5)
        self.box_info.AddMany([
            (self.pack_txt), (self.pack, 0, wx.EXPAND), (self.ver_txt), (self.ver, 0, wx.EXPAND),
            (self.auth_txt), (self.auth, 0, wx.EXPAND), (self.email_txt), (self.email, 0, wx.EXPAND),
            self.arch_txt, (self.arch)
            ])
        
        # Border box
        self.border_info = wx.StaticBox(self.bg, -1, GT(u'Required'))
        bbox_info = wx.StaticBoxSizer(self.border_info, wx.VERTICAL)
        bbox_info.Add(self.box_info, 0, wx.EXPAND)
        
        # ----- Changed to "Recommended"
        r_temp = wx.FlexGridSizer(0, 4, 5, 5)
        r_temp.AddGrowableCol(1)
        r_temp.AddGrowableCol(3)
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddMany([ (self.sect_txt), (self.sect, 0, wx.EXPAND), (self.prior_txt), (self.prior) ])
        # Border box
        self.border_description = wx.StaticBox(self.bg, -1, GT(u'Recommended'))
        bbox_description = wx.StaticBoxSizer(self.border_description, wx.VERTICAL)
        bbox_description.AddSpacer(5)
        bbox_description.Add(r_temp, 0, wx.EXPAND)
        bbox_description.AddSpacer(5)
        bbox_description.AddMany([
            (self.syn_txt, 0),
            (self.syn, 0, wx.EXPAND)
            ])
        bbox_description.AddSpacer(5)
        bbox_description.AddMany([
            (self.desc_txt, 0),
            (self.desc, 1, wx.EXPAND)
            ])
        
        b_temp = wx.FlexGridSizer(0, 4, 5, 5)
        b_temp.AddGrowableCol(1)
        b_temp.AddGrowableCol(3)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddMany([
            (self.src_txt), (self.src, 0, wx.EXPAND), (self.url_txt), (self.url, 0, wx.EXPAND),
            (self.ess_txt), (self.ess, 1)
            ])

        # Border box
        self.border_author = wx.StaticBox(self.bg, -1, GT(u'Optional'))
        bbox_author = wx.StaticBoxSizer(self.border_author, wx.VERTICAL)
        bbox_author.Add(b_temp, 0, wx.EXPAND)
        
        
        # Main Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(button_sizer, 0, wx.ALL, 5)
        main_sizer.Add(bbox_info, 0, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(bbox_description, 1, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(bbox_author, 0, wx.EXPAND|wx.ALL, 5)
        
        self.bg.SetAutoLayout(True)
        self.bg.SetSizer(main_sizer)
        self.bg.Layout()
        
        
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_sizer.Add(self.bg, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(scroll_sizer)
        self.Layout()
        
        # Set Ctrl+P hotkey to show preview of control file
        children = self.bg.GetChildren()
        for child in children:
            wx.EVT_KEY_DOWN(child, self.OnCtrlKey)
        
        
        # These are used for controlling the column width/size in the co-authors field
        #self.ReLayout()
        wx.EVT_SIZE(self, self.OnResize)
        
        # Defines fields to be accessed
        wx.EVT_SHOW(self, self.OnShow)
        
        # List all widgets to check if fields have changed after keypress
        # This is for determining if the project is saved
        self.text_widgets = {
            self.pack: wx.EmptyString, self.ver: wx.EmptyString
            }
        for widget in self.text_widgets:
            wx.EVT_KEY_DOWN(widget, self.OnKeyDown)
            wx.EVT_KEY_UP(widget, self.OnKeyUp)
        
    
    def OnResize(self, event):
        #self.ReLayout()
        pass
    
    def ReLayout(self):
        # Organize all widgets correctly
        lc_width = self.coauth.GetSize()[0]
        self.coauth.SetColumnWidth(0, lc_width/2)
        
    
    # *** Setting Field Priority *** #
    
    def EnableAll(self):
        # Reset all widgets to be enabled
        children = self.bg.GetChildren()
        for child in children:
            child.Enable()
            child.SetBackgroundColour(dbr.Optional)
    
    # FIXME: I believe this is unused
    def SetBuildType(self, build_id):
        # First enable all fields that were disabled
        self.EnableAll()
        
        group = self.bins
        
        for man in group[0]:
            man.SetBackgroundColour(dbr.Mandatory)
        for rec in group[1]:
            rec.SetBackgroundColour(dbr.Recommended)
        for opt in group[2]:
            opt.SetBackgroundColour(dbr.Optional)
#        for dis in group[3]:
#            dis.Disable()
#            dis.SetBackgroundColour(db.Disabled)
        
        self.Layout()
    
    def OnShow(self, event):
        pass
        #self.SetBuildType(db.ID_BIN)
    
    
    # *** Open, Save & Preview control file *** #
    
    def OnBrowse(self, event):
        wildcards = (
            GT(u'All files'), u'*',
            GT(u'CONTROL file'), u'CONTROL',
        )
        
        browse_dialog = GetFileOpenDialog(self.debreate, GT(u'Open File'), wildcards)
        if ShowDialog(self.debreate, browse_dialog):
            file_path = browse_dialog.GetPath()
            self.ImportPageInfo(file_path)
    
    
    def OnSave(self, event):
        wildcards = (
            GT(u'All files'), u'*',
        )
        
        save_dialog = GetFileSaveDialog(self.debreate, GT(u'Save Control Information'), wildcards)
        if ShowDialog(self.debreate, save_dialog):
            file_path = save_dialog.GetPath()
            self.Export(os.path.dirname(file_path), os.path.basename(file_path))
    
    
    def OnPreview(self, event):
        # Show a preview of the control file
        control = self.GetCtrlInfo()
        
        dia = wx.Dialog(self, -1, GT(u'Preview'), size=(500,400))
        preview = wx.TextCtrl(dia, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        preview.SetValue(control)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND)
        
        dia.SetSizer(dia_sizer)
        dia.Layout()
        
        dia.ShowModal()
        dia.Destroy()
    
    
    def OnCtrlKey(self, event):
        key = event.GetKeyCode()
        mod = event.GetModifiers()
        
        if mod == 2 and key == 80:
            self.OnPreview(None)
        
        event.Skip()
    
    
    # *** Clearing All Fields for New Project *** #
    
    def ResetAllFields(self):
        self.pack.Clear()
        self.ver.Clear()
        self.arch.SetSelection(0)
        self.src.Clear()
        self.sect.Clear()
        self.prior.SetSelection(0)
        self.url.Clear()
        self.ess.SetSelection(1)
        #self.stdver.Clear()
        self.syn.Clear()
        self.desc.Clear()
        self.auth.Clear()
        self.email.Clear()
    
    
    # *** Gathering Page Data *** #
    
    def GetCtrlInfo(self):
        # Creat a list to store info
        ctrl_list = []
        
        getvals = (	(u'Package',self.pack), (u'Version',self.ver), (u'Source',self.src), (u'Section',self.sect),
                    (u'Homepage',self.url), #(u'Standards-Version',self.stdver), (u'Format',self.format),
                    #(u'Binary',self.bin), (u'Files',self.files), (u'Date',self.date), (u'Changes',self.changes),
                    #(u'Distribution',self.dist), (u'Closes',self.closes) )
                    )
        
        for key in getvals:
            key_enabled = dbr.FieldEnabled(key[1])
            
            if key_enabled and u''.join(key[1].GetValue().split(u' ')) != u'':
                if key[0] == u'Package' or key[0] == u'Version':
                    ctrl_list.append(u'%s: %s' % (key[0], u'-'.join(key[1].GetValue().split(u' '))))
                else:
                    ctrl_list.append(u'%s: %s' % (key[0], key[1].GetValue()))
        
        # Add the Maintainer
        auth_enabled = dbr.FieldEnabled(self.auth)
        
        if auth_enabled and self.auth.GetValue() != u'':
            ctrl_list.insert(3, u'Maintainer: %s <%s>' % (self.auth.GetValue(), self.email.GetValue()))
        
        # Add the "choice" options
        getsels = {
            u'Architecture': (self.arch,self.arch_opt),
            u'Priority': (self.prior,self.prior_opt),
            u'Essential': (self.ess,self.ess_opt)#, u'Urgency': (self.urge,self.urge_opt)
        }
        for key in getsels:
            sel_enabled = dbr.FieldEnabled(getsels[key][0])
            
            if sel_enabled:
                if key == u'Essential' and self.ess.GetCurrentSelection() == 1:
                    pass
                else:
                    ctrl_list.append(u'%s: %s' % (key, getsels[key][1][getsels[key][0].GetCurrentSelection()]))
        
        # Get the uploaders
#        coauths = []
#        cototal = self.coauth.GetItemCount()
#        cocount = 0
#        if cototal > 0:
#            while cocount != cototal:
#                auth = self.coauth.GetItem(cocount)
#                email = self.coauth.GetItem(cocount, 1)
#                coauths.append(u'%s <%s>' % (auth.GetText(), email.GetText()))
#                cocount += 1
#            ctrl_list.append(u'Uploaders: %s' % u'; '.join(coauths))
        
        
        # *** Get dependencies *** #
        dep_list = [] # Depends
        pre_list = [] # Pre-Depends
        rec_list = [] # Recommends
        sug_list = [] # Suggests
        enh_list = [] # Enhances
        con_list = [] # Conflicts
        rep_list = [] # Replaces
        brk_list = [] # Breaks
        all_deps = {u'Depends': dep_list, u'Pre-Depends': pre_list, u'Recommends': rec_list,
                    u'Suggests': sug_list, u'Enhances': enh_list, u'Conflicts': con_list,
                    u'Replaces': rep_list, u'Breaks': brk_list}
        
        # Get amount of items to add
        dep_area = self.debreate.page_depends.dep_area
        dep_count = dep_area.GetItemCount()
        count = 0
        while count < dep_count:
            # Get each item from dependencied page
            dep_type = dep_area.GetItem(count).GetText()
            dep_val = dep_area.GetItem(count, 1).GetText()
            for item in all_deps:
                if dep_type == item:
                    all_deps[item].append(dep_val)
            count += 1
            
        for item in all_deps:
            if len(all_deps[item]) != 0:
                ctrl_list.append(u'%s: %s' % (item, u', '.join(all_deps[item])))
        
        
        # *** Get description *** #
        syn = self.syn.GetValue()
        desc = self.desc.GetValue()
        # Make sure synopsis isn't empty: Join spaces
        if u''.join(syn.split(u' ')) != u'':
            ctrl_list.append(u'Description: %s' % syn)
            # Make sure description isn't empty: Join newlines and spaces
            if u''.join(u''.join(desc.split(u' ')).split(u'\n')) != u'':
                desc_temp = []
                for line in desc.split(u'\n'):
                    if u''.join(line.split(u' ')) == u'':
                        desc_temp.append(u' .')
                    else:
                        desc_temp.append(u' %s' % line)
                ctrl_list.append(u'\n'.join(desc_temp))
        
        ctrl_list.append(u'\n')
        return u'\n'.join(ctrl_list)
    
    
    # *** Opening Project/File & Setting Fields ***
    
    def SetFieldData(self, data):
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
            (u'Homepage', self.url), (u'Description', self.syn)
            )
        
        # Fields that use "SetSelection()" function
        set_selection_fields = (
            (u'Architecture', self.arch, self.arch_opt),
            (u'Priority', self.prior, self.prior_opt),
            (u'Essential', self.ess, self.ess_opt)
            )
        
        # Store Dependencies
        depends_containers = (
            [u'Depends'], [u'Pre-Depends'], [u'Recommends'], [u'Suggests'], [u'Enhances'],
            [u'Conflicts'], [u'Replaces'], [u'Breaks']
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
                    leftovers.append(wx.EmptyString) # Add a blank line for lines marked with a "."
                elif field == u'\n' or field == u' ' or field == wx.EmptyString:
                    pass # Ignore empty lines
                elif field[0] == u' ':
                    leftovers.append(field[1:]) # Remove the first space generated in the description
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
    
    
    # *** Saving Project *** #
    
    def GatherData(self):
        data = self.GetCtrlInfo()
        return u'<<CTRL>>\n%s<</CTRL>>' % data
    
    # *** Determining of project is modified
    def OnKeyDown(self, event):
        for widget in self.text_widgets:
            self.text_widgets[widget] = widget.GetValue()
        event.Skip()
    
    def OnKeyUp(self, event):
        modified = False
        for widget in self.text_widgets:
            if widget.GetValue() != self.text_widgets[widget]:
                modified = True
        self.debreate.SetSavedStatus(modified)
        event.Skip()
    
    
    ## Retrieves information for control file export
    #  
    #  FIXME: Should replace self.GetPageInfo()
    #  \return
    #        \b \e tuple(str, str) : A tuple containing the filename & a string representation of control file formatted for text output
    def GetPageInfo(self):
        return (__name__, self.GetCtrlInfo())
    
    
    def ImportPageInfo(self, filename):
        Logger.Debug(__name__, GT(u'Importing file: {}'.format(filename)))
        
        if not os.path.isfile(filename):
            return custom_errno.ENOENT
        
        # Dependencies
        depends_page = None
        for child in self.wizard.GetChildren():
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
        
        FILE = open(filename)
        control_data = FILE.read().split(u'\n')
        FILE.close()
        
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
    
    
    ## Resets all fields on page to default values
    def ResetPageInfo(self):
        for child in self.bg.GetChildren():
            if isinstance(child, (wx.TextCtrl, wx.ComboBox)):
                # Can't use Clear() method for wx.ComboBox
                child.SetValue(wx.EmptyString)
            
            elif isinstance(child, wx.Choice):
                # wx.Choice instances should have custom member wx.Choice.default set
                child.SetSelection(child.default)
