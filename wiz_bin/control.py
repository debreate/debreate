# -*- coding: utf-8 -*-

# This panel displays the field input of the control file


import os
from wx import \
	ALL as wxALL, \
	EXPAND as wxEXPAND, \
	FD_CHANGE_DIR as wxFD_CHANGE_DIR, \
	FD_OVERWRITE_PROMPT as wxFD_OVERWRITE_PROMPT, \
	FD_SAVE as wxFD_SAVE, \
	HORIZONTAL as wxHORIZONTAL, \
	TE_MULTILINE as wxTE_MULTILINE, \
	TE_READONLY as wxTE_READONLY, \
	VERTICAL as wxVERTICAL, \
	EVT_BUTTON as wxEVT_BUTTON, \
	EVT_KEY_DOWN as wxEVT_KEY_DOWN, \
	EVT_KEY_UP as wxEVT_KEY_UP, \
	EVT_SHOW as wxEVT_SHOW, \
	EVT_SIZE as wxEVT_SIZE, \
	ID_OK as wxID_OK
from wx import \
	BoxSizer as wxBoxSizer, \
	Choice as wxChoice, \
	ComboBox as wxComboBox, \
	Dialog as wxDialog, \
	EmptyString as wxEmptyString, \
	FileDialog as wxFileDialog, \
	FlexGridSizer as wxFlexGridSizer, \
	Panel as wxPanel, \
	ScrolledWindow as wxScrolledWindow, \
	StaticBox as wxStaticBox, \
	StaticBoxSizer as wxStaticBoxSizer, \
	StaticText as wxStaticText, \
	TextCtrl as wxTextCtrl

import dbr
from dbr.constants import ID_CONTROL


class Panel(wxScrolledWindow):
    def __init__(self, parent):
        wxScrolledWindow.__init__(self, parent, ID_CONTROL, name=_(u'Control'))
        
        self.parent = parent
        self.SetScrollbars(0, 20, 0, 0)
        
        self.bg = wxPanel(self)
        
        # Buttons to Open, Save & Preview control file
        button_open = dbr.ButtonBrowse64(self.bg)
        wxEVT_BUTTON(button_open, -1, self.OnBrowse)
        button_save = dbr.ButtonSave64(self.bg)
        wxEVT_BUTTON(button_save, -1, self.OnSave)
        button_preview = dbr.ButtonPreview64(self.bg)
        wxEVT_BUTTON(button_preview, -1, self.OnPreview)
        
        button_sizer = wxBoxSizer(wxHORIZONTAL)
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
        self.pack_txt = wxStaticText(self.bg, -1, _('Package'))
        self.pack = dbr.CharCtrl(self.bg, -1)
        
        # ----- Version ( B[m], D[m], C[m] )
        self.ver_txt = wxStaticText(self.bg, -1, _('Version'))
        self.ver = dbr.CharCtrl(self.bg)
        
        # ----- Maintainer ( B[m], S[m], D[m], C[m] )
        self.auth_txt = wxStaticText(self.bg, -1, _('Maintainer'))
        self.auth = wxTextCtrl(self.bg, -1)
        self.email_txt = wxStaticText(self.bg, -1, _('Email'))
        self.email = wxTextCtrl(self.bg, -1)
        
        # ----- Architecture ( B[m], SB[m], D, C[m] )
        self.arch_opt = (	'all', 'alpha', 'amd64', 'arm', 'armeb', 'armel', 'armhf', 'avr32', 'hppa', 'i386', 'ia64', 'lpia',
                            'm32r', 'm68k', 'mips', 'mipsel', 'powerpc', 'powerpcspe', 'ppc64', 's390', 's390x', 'sh3', 'sh3eb',
                            'sh4', 'sh4eb', 'sparc', 'sparc64')
        self.arch_txt = wxStaticText(self.bg, -1, _('Architecture'))
        self.arch = wxChoice(self.bg, -1, choices=self.arch_opt)
        
        # ***** Recommended Group ***** #
        # ----- Section ( B[r], S[r], SB[r] )
        self.sect_opt = (u'admin', u'cli-mono', u'comm', u'database', u'devel', u'debug', u'doc', u'editors',
            u'electronics', u'embedded', u'fonts', u'games', u'gnome', u'graphics', u'gnu-r', u'gnustep',
            u'hamradio', u'haskell', u'httpd', u'interpreters', u'java', u'kde', u'kernel', u'libs', u'libdevel',
            u'lisp', u'localization', u'mail', u'math', u'metapackages', u'misc', u'net', u'news', u'ocaml', u'oldlibs',
            u'otherosfs', u'perl', u'php', u'python', u'ruby', u'science', u'shells', u'sound', u'tex', u'text',
            u'utils', u'vcs', u'video', u'web', u'x11', u'xfce', u'zope')
        self.sect_txt = wxStaticText(self.bg, -1, _(u'Section'))
        #self.sect = db.Combo(self.bg, -1, choices=self.sect_opt)
        self.sect = wxComboBox(self.bg, -1, choices=self.sect_opt)
        
        # ----- Priority ( B[r], S[r], SB[r] )
        self.prior_opt = ('optional', 'standard', 'important', 'required', 'extra')
        self.prior_txt = wxStaticText(self.bg, -1, _('Priority'))
        self.prior = wxChoice(self.bg, -1, choices=self.prior_opt)
        
        # ----- Description ( B[m], SB[m], C[m] )
        self.syn_txt = wxStaticText(self.bg, -1, _('Short Description'))
        self.syn = wxTextCtrl(self.bg)
        self.desc_txt = wxStaticText(self.bg, -1, _('Long Description'))
        self.desc = wxTextCtrl(self.bg, style=wxTE_MULTILINE)
        
        # ***** Optional Group ***** #
        # ----- Source ( B, S[m], D[m], C[m] )
        self.src_txt = wxStaticText(self.bg, -1, _('Source'))
        self.src = wxTextCtrl(self.bg, -1)
        
        # ----- Homepage ( B, S, SB, D )
        self.url_txt = wxStaticText(self.bg, -1, _('Homepage'))
        self.url = wxTextCtrl(self.bg)
        
        # ----- Essential ( B, SB )
        self.ess_opt = ('yes', 'no')
        self.ess_txt = wxStaticText(self.bg, -1, _('Essential'))
        self.ess = wxChoice(self.bg, -1, choices=self.ess_opt)
        self.ess.SetSelection(1)
        
        # ----- Standards-Version ( S[r], D[r] )
        #self.stdver_txt = wxStaticText(self.bg, -1, "Standards-Version")
        #self.stdver = wxTextCtrl(self.bg)
        
        
        
        # ----- Uploaders ( S, D )
        #self.coauth_txt = wxStaticText(self.bg, -1, "Uploaders/Co-Maintainers")
        #self.coauth = db.LCReport(self.bg, -1)
        #self.coauth.InsertColumn(0, "Maintainer")
        #self.coauth.InsertColumn(1, "Email")
        #self.coauth.SetToolTip(wxToolTip("Right-click to add"))
        
        
        # ----- Build-Depends ( S, D ) (Will be done on different panel)
        # ----- Depends ( B, SB ) (This is done in another panel)
        # ----- Installed-Size ( B ) (This is done automaticlly)
        
        
        # ***** Other group ***** #
        # ----- Format ( D[m], C[m] )
        #self.format_txt = wxStaticText(self.bg, -1, "Format")
        #self.format = wxTextCtrl(self.bg)
        
        # ----- Binary ( D, C[m] )
        #self.bin_txt = wxStaticText(self.bg, -1, "Binary")
        #self.bin = wxTextCtrl(self.bg)
        
        # ----- Files ( D[m], C[m] )
        #self.files_txt = wxStaticText(self.bg, -1, "Files")
        #self.files = wxTextCtrl(self.bg)
        
        # ----- Date ( C[m] )
        #self.date_txt = wxStaticText(self.bg, -1, "Date")
        #self.date = wxTextCtrl(self.bg)
        
        # ----- Changed-By ( C )
        #self.editor_txt = wxStaticText(self.bg, -1, "Changed-By")
        #self.editor = wxTextCtrl(self.bg)
        #self.eemail_txt = wxStaticText(self.bg, -1, "Email")
        #self.eemail = wxTextCtrl(self.bg)
        
        # ----- Changes ( C[m] )
        #self.changes_txt = wxStaticText(self.bg, -1, "Changes")
        #self.changes = wxTextCtrl(self.bg)
        
        # ----- Distribution ( C[m] )
        #self.dist_txt = wxStaticText(self.bg, -1, "Distribution")
        #self.dist = wxTextCtrl(self.bg)
        
        # ----- Urgency ( C[r] )
        #self.urge_opt = ('low', 'medium', 'high', 'emergency', 'critical')
        #self.urge_txt = wxStaticText(self.bg, -1, "Urgency")
        #self.urge = wxChoice(self.bg, -1, choices=self.urge_opt)
        
        # ----- Closes ( C )
        #self.closes_txt = wxStaticText(self.bg, -1, "Closes")
        #self.closes = wxTextCtrl(self.bg)
        
        
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
        self.box_info = wxFlexGridSizer(0, 4, 5, 5)
        self.box_info.AddGrowableCol(1)
        self.box_info.AddGrowableCol(3)
        self.box_info.AddSpacer(5)
        self.box_info.AddSpacer(5)
        self.box_info.AddSpacer(5)
        self.box_info.AddSpacer(5)
        self.box_info.AddMany([
            (self.pack_txt), (self.pack, 0, wxEXPAND), (self.ver_txt), (self.ver, 0, wxEXPAND),
            (self.auth_txt), (self.auth, 0, wxEXPAND), (self.email_txt), (self.email, 0, wxEXPAND),
            self.arch_txt, (self.arch)
            ])
#            (self.arch_txt), (self.arch), (self.src_txt), (self.src, 0, wxEXPAND),
#            (self.sect_txt), (self.sect, 0, wxEXPAND), (self.prior_txt), (self.prior),
#            (self.url_txt), (self.url, 0, wxEXPAND), (self.ess_txt), (self.ess),
#            #(self.stdver_txt), (self.stdver, 0, wxEXPAND)
#            ])
        
        # Border box
        self.border_info = wxStaticBox(self.bg, -1, _('Required'))
        bbox_info = wxStaticBoxSizer(self.border_info, wxVERTICAL)
        bbox_info.Add(self.box_info, 0, wxEXPAND)
        
        # ----- Changed to "Recommended"
        r_temp = wxFlexGridSizer(0, 4, 5, 5)
        r_temp.AddGrowableCol(1)
        r_temp.AddGrowableCol(3)
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddSpacer(5)
        r_temp.AddMany([ (self.sect_txt), (self.sect, 0, wxEXPAND), (self.prior_txt), (self.prior) ])
        # Border box
        self.border_description = wxStaticBox(self.bg, -1, _('Recommended'))
        bbox_description = wxStaticBoxSizer(self.border_description, wxVERTICAL)
        bbox_description.AddSpacer(5)
        bbox_description.Add(r_temp, 0, wxEXPAND)
        bbox_description.AddSpacer(5)
        bbox_description.AddMany([
            (self.syn_txt, 0),
            (self.syn, 0, wxEXPAND)
            ])
        bbox_description.AddSpacer(5)
        bbox_description.AddMany([
            (self.desc_txt, 0),
            (self.desc, 1, wxEXPAND)
            ])
        
        # ----- Changed to "Optional
#        self.box_author = wxBoxSizer(wxHORIZONTAL)
#        self.box_author.AddMany([
#            (self.auth_txt), (self.auth, 1),
#            (self.email_txt), (self.email, 1)
#            ])
        
        b_temp = wxFlexGridSizer(0, 4, 5, 5)
        b_temp.AddGrowableCol(1)
        b_temp.AddGrowableCol(3)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddSpacer(5)
        b_temp.AddMany([
            (self.src_txt), (self.src, 0, wxEXPAND), (self.url_txt), (self.url, 0, wxEXPAND),
            (self.ess_txt), (self.ess, 1)
            ])

        # Border box
        self.border_author = wxStaticBox(self.bg, -1, _('Optional'))
        bbox_author = wxStaticBoxSizer(self.border_author, wxVERTICAL)
        bbox_author.Add(b_temp, 0, wxEXPAND)
#        bbox_author.AddSpacer(5)
#        bbox_author.Add(self.box_author, 0, wxEXPAND)
#        bbox_author.AddSpacer(5)
#        bbox_author.AddMany([
#            (self.coauth_txt, 0, wxALIGN_CENTER),
#            (self.coauth, 1, wxEXPAND)
#            ])
        
        # ----- Other
#        self.box_other = wxFlexGridSizer(0, 4, 5, 5)
#        self.box_other.AddGrowableCol(1)
#        self.box_other.AddGrowableCol(3)
#        self.box_other.AddSpacer(5)
#        self.box_other.AddSpacer(5)
#        self.box_other.AddSpacer(5)
#        self.box_other.AddSpacer(5)
#        self.box_other.AddMany([
#            (self.format_txt), (self.format, 0, wxEXPAND), (self.bin_txt), (self.bin, 0, wxEXPAND),
#            (self.files_txt), (self.files, 0, wxEXPAND), (self.date_txt), (self.date, 0, wxEXPAND),
#            (self.editor_txt), (self.editor, 0, wxEXPAND), (self.eemail_txt), (self.eemail, 0, wxEXPAND),
#            (self.changes_txt), (self.changes, 0, wxEXPAND), (self.dist_txt), (self.dist, 0, wxEXPAND),
#            (self.urge_txt), (self.urge), (self.closes_txt), (self.closes, 0, wxEXPAND)
#            ])
#        
#        self.border_other = wxStaticBox(self.bg, -1, "Other")
#        bbox_other = wxStaticBoxSizer(self.border_other, wxVERTICAL)
#        bbox_other.Add(self.box_other, 0, wxEXPAND)
        
        
        # Main Layout
        main_sizer = wxBoxSizer(wxVERTICAL)
        main_sizer.Add(button_sizer, 0, wxALL, 5)
        #main_sizer.AddSpacer(10)
        main_sizer.Add(bbox_info, 0, wxEXPAND|wxALL, 5)
        #main_sizer.AddSpacer(10)
        main_sizer.Add(bbox_description, 1, wxEXPAND|wxALL, 5)
        #main_sizer.AddSpacer(10)
        main_sizer.Add(bbox_author, 0, wxEXPAND|wxALL, 5)
        #main_sizer.AddSpacer(10)
        #main_sizer.Add(bbox_other, 0, wxEXPAND|wxALL, 5)
        
        self.bg.SetAutoLayout(True)
        self.bg.SetSizer(main_sizer)
        self.bg.Layout()
        
        
        scroll_sizer = wxBoxSizer(wxVERTICAL)
        scroll_sizer.Add(self.bg, 1, wxEXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(scroll_sizer)
        self.Layout()
        
        # Set Ctrl+P hotkey to show preview of control file
        children = self.bg.GetChildren()
        for child in children:
            wxEVT_KEY_DOWN(child, self.OnCtrlKey)
        
        
        # These are used for controlling the column width/size in the co-authors field
        #self.ReLayout()
        wxEVT_SIZE(self, self.OnResize)
        
        # Defines fields to be accessed
        wxEVT_SHOW(self, self.OnShow)
        
        # List all widgets to check if fields have changed after keypress
        # This is for determining if the project is saved
        self.text_widgets = {
            self.pack: wxEmptyString, self.ver: wxEmptyString
            }
        for widget in self.text_widgets:
            wxEVT_KEY_DOWN(widget, self.OnKeyDown)
            wxEVT_KEY_UP(widget, self.OnKeyUp)
        
    
    def OnResize(self, event):
        #self.ReLayout()
        pass
    
    def ReLayout(self):
        # Organize all widgets correctly
        lc_width = self.coauth.GetSize()[0]
        self.coauth.SetColumnWidth(0, lc_width/2)
#		self.coauth.SetColumnWidth(1, lc_width/2-25)
        
    
    # *** Setting Field Priority *** #
    
    def EnableAll(self):
        # Reset all widgets to be enabled
        children = self.bg.GetChildren()
        for child in children:
            child.Enable()
            child.SetBackgroundColour(dbr.Optional)
    
    def SetBuildType(self, id):
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
        cont = False
        if self.parent.parent.cust_dias.IsChecked():
            dia = dbr.OpenFile(self)
            if dia.DisplayModal():
                cont = True
        else:
            dia = wxFileDialog(self, _('Open File'), os.getcwd(), style=wxFD_CHANGE_DIR)
            if dia.ShowModal() == wxID_OK:
                cont = True
        
        if cont:
            path = dia.GetPath()
            file = open(path, 'r')
            control_data = file.read()
            depends_data = self.SetFieldData(control_data)
            self.parent.parent.page_depends.SetFieldData(depends_data)
    
    def OnSave(self, event):
        # Get data to write to control file
        control = self.GetCtrlInfo().encode('utf-8')
        
        # Saving?
        cont = False
        
        # Open a "Save Dialog"
        if self.parent.parent.cust_dias.IsChecked():
            dia = dbr.SaveFile(self, _('Save Control Information'))
            dia.SetFilename('control')
            if dia.DisplayModal():
                cont = True
                path = "%s/%s" % (dia.GetPath(), dia.GetFilename())
        else:
            dia = wxFileDialog(self, 'Save Control Information', os.getcwd(),
                style=wxFD_SAVE|wxFD_CHANGE_DIR|wxFD_OVERWRITE_PROMPT)
            dia.SetFilename('control')
            if dia.ShowModal() == wxID_OK:
                cont = True
                path = dia.GetPath()
        
        if cont:
            filename = dia.GetFilename()
            file = open(path, 'w')
            file.write(control)
            file.close()
    
    def OnPreview(self, event):
        # Show a preview of the control file
        control = self.GetCtrlInfo()
        
        dia = wxDialog(self, -1, _('Preview'), size=(500,400))
        preview = wxTextCtrl(dia, -1, style=wxTE_MULTILINE|wxTE_READONLY)
        preview.SetValue(control)
        
        dia_sizer = wxBoxSizer(wxVERTICAL)
        dia_sizer.Add(preview, 1, wxEXPAND)
        
        dia.SetSizer(dia_sizer)
        dia.Layout()
        
        dia.ShowModal()
        dia.Destroy()
    
    
    def OnCtrlKey(self, event):
        obj = event.GetEventObject()
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
                    (u'Homepage',self.url), #("Standards-Version",self.stdver), ("Format",self.format),
                    #("Binary",self.bin), ("Files",self.files), ("Date",self.date), ("Changes",self.changes),
                    #("Distribution",self.dist), ("Closes",self.closes) )
                    )
        
        for key in getvals:
            key_enabled = dbr.FieldEnabled(key[1])
            
            if key_enabled and u''.join(key[1].GetValue().split(u' ')) != u'':
                if key[0] == u'Package' or key[0] == u'Version':
                    ctrl_list.append(u'%s: %s' % (key[0], "-".join(key[1].GetValue().split(u' '))))
                else:
                    ctrl_list.append(u'%s: %s' % (key[0], key[1].GetValue()))
        
        # Add the Maintainer
        auth_enabled = dbr.FieldEnabled(self.auth)
        
        if auth_enabled and self.auth.GetValue() != '':
            ctrl_list.insert(3, "Maintainer: %s <%s>" % (self.auth.GetValue(), self.email.GetValue()))
        
        # Add the "choice" options
        getsels = {	"Architecture": (self.arch,self.arch_opt), "Priority": (self.prior,self.prior_opt),
                    "Essential": (self.ess,self.ess_opt)#, "Urgency": (self.urge,self.urge_opt)
                    }
        for key in getsels:
            sel_enabled = dbr.FieldEnabled(getsels[key][0])
            
            if sel_enabled:
                if key == "Essential" and self.ess.GetCurrentSelection() == 1:
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
#                coauths.append("%s <%s>" % (auth.GetText(), email.GetText()))
#                cocount += 1
#            ctrl_list.append("Uploaders: %s" % "; ".join(coauths))
        
        
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
        dep_area = self.parent.parent.page_depends.dep_area
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
        if ''.join(syn.split(' ')) != '':
            ctrl_list.append(u'Description: %s' % syn)
            # Make sure description isn't empty: Join newlines and spaces
            if ''.join(''.join(desc.split(' ')).split('\n')) != '':
                desc_temp = []
                for line in desc.split(u'\n'):
                    if ''.join(line.split(u' ')) == u'':
                        desc_temp.append(u' .')
                    else:
                        desc_temp.append(u' %s' % line)
                ctrl_list.append(u'\n'.join(desc_temp))
        
        ctrl_list.append(u'\n')
        return u'\n'.join(ctrl_list)
    
    
    # *** Opening Project/File & Setting Fields *** "
    
    def SetFieldData(self, data):
        if type(data) == type(''):
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
        author = wxEmptyString
        
        for field in control_data:
            if u': ' in field:
                f1 = field.split(u': ')[0]
                f2 = u': '.join(field.split(u': ')[1:]) # For dependency fields that have ": " in description
                # Catch Maintainer and put in author variable
                if f1 == u'Maintainer':
                    author = f2
                # Set the rest of the wxTextCtrl fields
                for setval in set_value_fields:
                    if f1 == setval[0]:
                        setval[1].SetValue(f2)
                # Set the wxChoice fields
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
                    leftovers.append(wxEmptyString) # Add a blank line for lines marked with a "."
                elif field == u'\n' or field == u' ' or field == wxEmptyString:
                    pass # Ignore empty lines
                elif field[0] == u' ':
                    leftovers.append(field[1:]) # Remove the first space generated in the description
                else:
                    leftovers.append(field)
        
        # Put leftovers in long description
        self.desc.SetValue(u'\n'.join(leftovers))
        
        # Set the "Author" and "Email" fields
        if author != wxEmptyString:
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
        self.parent.parent.SetSavedStatus(modified)
        event.Skip()