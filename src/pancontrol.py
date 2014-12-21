# -*- coding: utf-8 -*-

# This panel displays the field input of the control file

from common import setWXVersion
setWXVersion()

import wx, db, os

ID = wx.NewId()

class Panel(wx.ScrolledWindow):
    def __init__(self, parent, id=ID, name=_('Control')):
        wx.ScrolledWindow.__init__(self, parent, id, name=_('Control'))
        
        self.parent = parent
        self.SetScrollbars(0, 20, 0, 0)
        
        self.bg = wx.Panel(self)
        
        # Buttons to Open, Save & Preview control file
        button_open = db.ButtonBrowse64(self.bg)
        wx.EVT_BUTTON(button_open, -1, self.OnBrowse)
        button_save = db.ButtonSave64(self.bg)
        wx.EVT_BUTTON(button_save, -1, self.OnSave)
        button_preview = db.ButtonPreview64(self.bg)
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
        self.pack_txt = wx.StaticText(self.bg, -1, _('Package'))
        self.pack = db.CharCtrl(self.bg, -1)
        
        # ----- Version ( B[m], D[m], C[m] )
        self.ver_txt = wx.StaticText(self.bg, -1, _('Version'))
        self.ver = db.CharCtrl(self.bg)
        
        # ----- Maintainer ( B[m], S[m], D[m], C[m] )
        self.auth_txt = wx.StaticText(self.bg, -1, _('Maintainer'))
        self.auth = wx.TextCtrl(self.bg, -1)
        self.email_txt = wx.StaticText(self.bg, -1, _('Email'))
        self.email = wx.TextCtrl(self.bg, -1)
        
        # ----- Architecture ( B[m], SB[m], D, C[m] )
        self.arch_opt = (	'all', 'alpha', 'amd64', 'arm', 'armeb', 'armel', 'armhf', 'avr32', 'hppa', 'i386', 'ia64', 'lpia',
                            'm32r', 'm68k', 'mips', 'mipsel', 'powerpc', 'powerpcspe', 'ppc64', 's390', 's390x', 'sh3', 'sh3eb',
                            'sh4', 'sh4eb', 'sparc', 'sparc64')
        self.arch_txt = wx.StaticText(self.bg, -1, _('Architecture'))
        self.arch = wx.Choice(self.bg, -1, choices=self.arch_opt)
        
        # ***** Recommended Group ***** #
        # ----- Section ( B[r], S[r], SB[r] )
        self.sect_opt = ("admin", "cli-mono", "comm", "database", "devel", "debug", "doc", "editors",
            "electronics", "embedded", "fonts", "games", "gnome", "graphics", "gnu-r", "gnustep",
            "hamradio", "haskell", "httpd", "interpreters", "java", "kde", "kernel", "libs", "libdevel",
            "lisp", "localization", "mail", "math", 'metapackages', "misc", "net", "news", "ocaml", "oldlibs",
            "otherosfs", "perl", "php", "python", "ruby", "science", "shells", "sound", "tex", "text",
            "utils", "vcs", "video", "web", "x11", "xfce", "zope")
        self.sect_txt = wx.StaticText(self.bg, -1, _('Section'))
        #self.sect = db.Combo(self.bg, -1, choices=self.sect_opt)
        self.sect = wx.ComboBox(self.bg, -1, choices=self.sect_opt)
        
        # ----- Priority ( B[r], S[r], SB[r] )
        self.prior_opt = ('optional', 'standard', 'important', 'required', 'extra')
        self.prior_txt = wx.StaticText(self.bg, -1, _('Priority'))
        self.prior = wx.Choice(self.bg, -1, choices=self.prior_opt)
        
        # ----- Description ( B[m], SB[m], C[m] )
        self.syn_txt = wx.StaticText(self.bg, -1, _('Short Description'))
        self.syn = wx.TextCtrl(self.bg)
        self.desc_txt = wx.StaticText(self.bg, -1, _('Long Description'))
        self.desc = wx.TextCtrl(self.bg, style=wx.TE_MULTILINE)
        
        # ***** Optional Group ***** #
        # ----- Source ( B, S[m], D[m], C[m] )
        self.src_txt = wx.StaticText(self.bg, -1, _('Source'))
        self.src = wx.TextCtrl(self.bg, -1)
        
        # ----- Homepage ( B, S, SB, D )
        self.url_txt = wx.StaticText(self.bg, -1, _('Homepage'))
        self.url = wx.TextCtrl(self.bg)
        
        # ----- Essential ( B, SB )
        self.ess_opt = ('yes', 'no')
        self.ess_txt = wx.StaticText(self.bg, -1, _('Essential'))
        self.ess = wx.Choice(self.bg, -1, choices=self.ess_opt)
        self.ess.SetSelection(1)
        
        # ----- Standards-Version ( S[r], D[r] )
        #self.stdver_txt = wx.StaticText(self.bg, -1, "Standards-Version")
        #self.stdver = wx.TextCtrl(self.bg)
        
        
        
        # ----- Uploaders ( S, D )
        #self.coauth_txt = wx.StaticText(self.bg, -1, "Uploaders/Co-Maintainers")
        #self.coauth = db.LCReport(self.bg, -1)
        #self.coauth.InsertColumn(0, "Maintainer")
        #self.coauth.InsertColumn(1, "Email")
        #self.coauth.SetToolTip(wx.ToolTip("Right-click to add"))
        
        
        # ----- Build-Depends ( S, D ) (Will be done on different panel)
        # ----- Depends ( B, SB ) (This is done in another panel)
        # ----- Installed-Size ( B ) (This is done automaticlly)
        
        
        # ***** Other group ***** #
        # ----- Format ( D[m], C[m] )
        #self.format_txt = wx.StaticText(self.bg, -1, "Format")
        #self.format = wx.TextCtrl(self.bg)
        
        # ----- Binary ( D, C[m] )
        #self.bin_txt = wx.StaticText(self.bg, -1, "Binary")
        #self.bin = wx.TextCtrl(self.bg)
        
        # ----- Files ( D[m], C[m] )
        #self.files_txt = wx.StaticText(self.bg, -1, "Files")
        #self.files = wx.TextCtrl(self.bg)
        
        # ----- Date ( C[m] )
        #self.date_txt = wx.StaticText(self.bg, -1, "Date")
        #self.date = wx.TextCtrl(self.bg)
        
        # ----- Changed-By ( C )
        #self.editor_txt = wx.StaticText(self.bg, -1, "Changed-By")
        #self.editor = wx.TextCtrl(self.bg)
        #self.eemail_txt = wx.StaticText(self.bg, -1, "Email")
        #self.eemail = wx.TextCtrl(self.bg)
        
        # ----- Changes ( C[m] )
        #self.changes_txt = wx.StaticText(self.bg, -1, "Changes")
        #self.changes = wx.TextCtrl(self.bg)
        
        # ----- Distribution ( C[m] )
        #self.dist_txt = wx.StaticText(self.bg, -1, "Distribution")
        #self.dist = wx.TextCtrl(self.bg)
        
        # ----- Urgency ( C[r] )
        #self.urge_opt = ('low', 'medium', 'high', 'emergency', 'critical')
        #self.urge_txt = wx.StaticText(self.bg, -1, "Urgency")
        #self.urge = wx.Choice(self.bg, -1, choices=self.urge_opt)
        
        # ----- Closes ( C )
        #self.closes_txt = wx.StaticText(self.bg, -1, "Closes")
        #self.closes = wx.TextCtrl(self.bg)
        
        
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
#            (self.arch_txt), (self.arch), (self.src_txt), (self.src, 0, wx.EXPAND),
#            (self.sect_txt), (self.sect, 0, wx.EXPAND), (self.prior_txt), (self.prior),
#            (self.url_txt), (self.url, 0, wx.EXPAND), (self.ess_txt), (self.ess),
#            #(self.stdver_txt), (self.stdver, 0, wx.EXPAND)
#            ])
        
        # Border box
        self.border_info = wx.StaticBox(self.bg, -1, _('Required'))
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
        self.border_description = wx.StaticBox(self.bg, -1, _('Recommended'))
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
        
        # ----- Changed to "Optional
#        self.box_author = wx.BoxSizer(wx.HORIZONTAL)
#        self.box_author.AddMany([
#            (self.auth_txt), (self.auth, 1),
#            (self.email_txt), (self.email, 1)
#            ])
        
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
        self.border_author = wx.StaticBox(self.bg, -1, _('Optional'))
        bbox_author = wx.StaticBoxSizer(self.border_author, wx.VERTICAL)
        bbox_author.Add(b_temp, 0, wx.EXPAND)
#        bbox_author.AddSpacer(5)
#        bbox_author.Add(self.box_author, 0, wx.EXPAND)
#        bbox_author.AddSpacer(5)
#        bbox_author.AddMany([
#            (self.coauth_txt, 0, wx.ALIGN_CENTER),
#            (self.coauth, 1, wx.EXPAND)
#            ])
        
        # ----- Other
#        self.box_other = wx.FlexGridSizer(0, 4, 5, 5)
#        self.box_other.AddGrowableCol(1)
#        self.box_other.AddGrowableCol(3)
#        self.box_other.AddSpacer(5)
#        self.box_other.AddSpacer(5)
#        self.box_other.AddSpacer(5)
#        self.box_other.AddSpacer(5)
#        self.box_other.AddMany([
#            (self.format_txt), (self.format, 0, wx.EXPAND), (self.bin_txt), (self.bin, 0, wx.EXPAND),
#            (self.files_txt), (self.files, 0, wx.EXPAND), (self.date_txt), (self.date, 0, wx.EXPAND),
#            (self.editor_txt), (self.editor, 0, wx.EXPAND), (self.eemail_txt), (self.eemail, 0, wx.EXPAND),
#            (self.changes_txt), (self.changes, 0, wx.EXPAND), (self.dist_txt), (self.dist, 0, wx.EXPAND),
#            (self.urge_txt), (self.urge), (self.closes_txt), (self.closes, 0, wx.EXPAND)
#            ])
#        
#        self.border_other = wx.StaticBox(self.bg, -1, "Other")
#        bbox_other = wx.StaticBoxSizer(self.border_other, wx.VERTICAL)
#        bbox_other.Add(self.box_other, 0, wx.EXPAND)
        
        
        # Main Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(button_sizer, 0, wx.ALL, 5)
        #main_sizer.AddSpacer(10)
        main_sizer.Add(bbox_info, 0, wx.EXPAND|wx.ALL, 5)
        #main_sizer.AddSpacer(10)
        main_sizer.Add(bbox_description, 1, wx.EXPAND|wx.ALL, 5)
        #main_sizer.AddSpacer(10)
        main_sizer.Add(bbox_author, 0, wx.EXPAND|wx.ALL, 5)
        #main_sizer.AddSpacer(10)
        #main_sizer.Add(bbox_other, 0, wx.EXPAND|wx.ALL, 5)
        
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
#		self.coauth.SetColumnWidth(1, lc_width/2-25)
        
    
    # *** Setting Field Priority *** #
    
    def EnableAll(self):
        # Reset all widgets to be enabled
        children = self.bg.GetChildren()
        for child in children:
            child.Enable()
            child.SetBackgroundColour(db.Optional)
    
    def SetBuildType(self, id):
        # First enable all fields that were disabled
        self.EnableAll()
        
        group = self.bins
        
        for man in group[0]:
            man.SetBackgroundColour(db.Mandatory)
        for rec in group[1]:
            rec.SetBackgroundColour(db.Recommended)
        for opt in group[2]:
            opt.SetBackgroundColour(db.Optional)
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
            dia = db.OpenFile(self)
            if dia.DisplayModal():
                cont = True
        else:
            dia = wx.FileDialog(self, _('Open File'), os.getcwd(), style=wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
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
            dia = db.SaveFile(self, _('Save Control Information'))
            dia.SetFilename('control')
            if dia.DisplayModal():
                cont = True
                path = "%s/%s" % (dia.GetPath(), dia.GetFilename())
        else:
            dia = wx.FileDialog(self, 'Save Control Information', os.getcwd(),
                style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
            dia.SetFilename('control')
            if dia.ShowModal() == wx.ID_OK:
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
        
        dia = wx.Dialog(self, -1, _('Preview'), size=(500,400))
        preview = wx.TextCtrl(dia, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        preview.SetValue(control)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND)
        
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
        
        getvals = (	("Package",self.pack), ("Version",self.ver), ("Source",self.src), ("Section",self.sect),
                    ("Homepage",self.url), #("Standards-Version",self.stdver), ("Format",self.format),
                    #("Binary",self.bin), ("Files",self.files), ("Date",self.date), ("Changes",self.changes),
                    #("Distribution",self.dist), ("Closes",self.closes) )
                    )
        
        for key in getvals:
            if key[1].IsEnabled() and "".join(key[1].GetValue().split(" ")) != '':
                if key[0] == "Package" or key[0] == "Version":
                    ctrl_list.append("%s: %s" % (key[0], "-".join(key[1].GetValue().split(' '))))
                else:
                    ctrl_list.append("%s: %s" % (key[0], key[1].GetValue()))
        
        # Add the Maintainer
        if self.auth.IsEnabled and self.auth.GetValue() != '':
            ctrl_list.insert(3, "Maintainer: %s <%s>" % (self.auth.GetValue(), self.email.GetValue()))
        
        # Add the "choice" options
        getsels = {	"Architecture": (self.arch,self.arch_opt), "Priority": (self.prior,self.prior_opt),
                    "Essential": (self.ess,self.ess_opt)#, "Urgency": (self.urge,self.urge_opt)
                    }
        for key in getsels:
            if getsels[key][0].IsEnabled():
                if key == "Essential" and self.ess.GetCurrentSelection() == 1:
                    pass
                else:
                    ctrl_list.append("%s: %s" % (key, getsels[key][1][getsels[key][0].GetCurrentSelection()]))
        
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
        all_deps = {"Depends": dep_list, "Pre-Depends": pre_list, "Recommends": rec_list,
                    "Suggests": sug_list, "Enhances": enh_list, "Conflicts": con_list,
                    "Replaces": rep_list, "Breaks": brk_list}
        
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
                ctrl_list.append("%s: %s" % (item, ", ".join(all_deps[item])))
        
        
        # *** Get description *** #
        syn = self.syn.GetValue()
        desc = self.desc.GetValue()
        # Make sure synopsis isn't empty: Join spaces
        if ''.join(syn.split(' ')) != '':
            ctrl_list.append("Description: %s" % syn)
            # Make sure description isn't empty: Join newlines and spaces
            if ''.join(''.join(desc.split(' ')).split('\n')) != '':
                desc_temp = []
                for line in desc.split('\n'):
                    if ''.join(line.split(' ')) == '':
                        desc_temp.append(" .")
                    else:
                        desc_temp.append(" %s" % line)
                ctrl_list.append('\n'.join(desc_temp))
        
        ctrl_list.append("\n")
        return "\n".join(ctrl_list)
    
    
    # *** Opening Project/File & Setting Fields *** "
    
    def SetFieldData(self, data):
        if type(data) == type(''):
            # Decode to unicode string if input is byte string
            data = data.decode('utf-8')
        control_data = data.split("\n")
        # Remove newline at end of document required by dpkg
        if control_data[-1] == "\n":
            control_data = control_data[:-1]
        
        # Fields that use "SetValue()" function
        set_value_fields = (
            ("Package", self.pack), ("Version", self.ver),
            ("Source", self.src), ("Section", self.sect),
            ("Homepage", self.url), ("Description", self.syn)
            )
        
        # Fields that use "SetSelection()" function
        set_selection_fields = (
            ("Architecture", self.arch, self.arch_opt),
            ("Priority", self.prior, self.prior_opt),
            ("Essential", self.ess, self.ess_opt)
            )
        
        # Store Dependencies
        depends_containers = (
            ["Depends"], ["Pre-Depends"], ["Recommends"], ["Suggests"], ["Enhances"],
            ["Conflicts"], ["Replaces"], ["Breaks"]
            )
        
        # Anything left over is dumped into this list then into the description
        leftovers = []
        # Separate Maintainer for later since is divided by Author/Email
        author = wx.EmptyString
        
        for field in control_data:
            if ": " in field:
                f1 = field.split(": ")[0]
                f2 = ": ".join(field.split(": ")[1:]) # For dependency fields that have ": " in description
                # Catch Maintainer and put in author variable
                if f1 == "Maintainer":
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
                        for dep in f2.split(", "):
                            container.append(dep)
            else:
                if field == " .":
                    leftovers.append(wx.EmptyString) # Add a blank line for lines marked with a "."
                elif field == "\n" or field == " " or field == wx.EmptyString:
                    pass # Ignore empty lines
                elif field[0] == " ":
                    leftovers.append(field[1:]) # Remove the first space generated in the description
                else:
                    leftovers.append(field)
        
        # Put leftovers in long description
        self.desc.SetValue("\n".join(leftovers))
        
        # Set the "Author" and "Email" fields
        if author != wx.EmptyString:
            self.auth.SetValue(author.split(" <")[0])
            self.email.SetValue(author.split(" <")[1].split(">")[0])
        
        # Return depends data to parent to be sent to page_depends
        return depends_containers
    
    
    # *** Saving Project *** #
    
    def GatherData(self):
        data = self.GetCtrlInfo()
        return "<<CTRL>>\n%s<</CTRL>>" % data
    
    
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