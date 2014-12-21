# Scripts Page

from common import setWXVersion
setWXVersion()

import wx, os, db

ID = wx.NewId()

ID_Import = 100
ID_Remove = 101

ID_Preinst = wx.NewId()
ID_Postinst = wx.NewId()
ID_Prerm = wx.NewId()
ID_Postrm = wx.NewId()

class Panel(wx.Panel):
    def __init__(self, parent, id=ID, name=_('Scripts')):
        wx.Panel.__init__(self, parent, id, name=_('Scripts'))
        
        # For identifying page to parent
        #self.ID = "SCRIPTS"
        
        # Allows calling parent methods
        self.debreate = parent.parent
        
        # Check boxes for choosing scripts
        self.chk_preinst = wx.CheckBox(self, ID_Preinst, _('Make this script'))
        self.chk_postinst = wx.CheckBox(self, ID_Postinst, _('Make this script'))
        self.chk_prerm = wx.CheckBox(self, ID_Prerm, _('Make this script'))
        self.chk_postrm = wx.CheckBox(self, ID_Postrm, _('Make this script'))
        
        # Radio buttons for displaying between pre- and post- install scripts
        self.rb_preinst = wx.RadioButton(self, ID_Preinst, _('Pre-Install'), style=wx.RB_GROUP)
        self.rb_postinst = wx.RadioButton(self, ID_Postinst, _('Post-Install'))
        self.rb_prerm = wx.RadioButton(self, ID_Prerm, _('Pre-Remove'))
        self.rb_postrm = wx.RadioButton(self, ID_Postrm, _('Post-Remove'))
        
        # Text area for each radio button
        self.te_preinst = wx.TextCtrl(self, ID_Preinst, style=wx.TE_MULTILINE)
        self.te_postinst = wx.TextCtrl(self, ID_Postinst, style=wx.TE_MULTILINE)
        self.te_prerm = wx.TextCtrl(self, ID_Prerm, style=wx.TE_MULTILINE)
        self.te_postrm = wx.TextCtrl(self, ID_Postrm, style=wx.TE_MULTILINE)
        
        # For testing to make sure scripts page is reset back to defaults
        #self.te_preinst.SetBackgroundColour("red")
        
        self.script_te = {	self.rb_preinst: self.te_preinst, self.rb_postinst: self.te_postinst,
                            self.rb_prerm: self.te_prerm, self.rb_postrm: self.te_postrm
                            }
        self.script_chk = {	self.rb_preinst: self.chk_preinst, self.rb_postinst: self.chk_postinst,
                            self.rb_prerm: self.chk_prerm, self.rb_postrm: self.chk_postrm }
        
        for rb in self.script_te:
            wx.EVT_RADIOBUTTON(rb, -1, self.ScriptSelect)
            self.script_te[rb].Hide()
        for rb in self.script_chk:
            self.script_chk[rb].Hide()
        
        # Organizing radio buttons
        srb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        srb_sizer.AddMany( [
            (self.chk_preinst),(self.chk_postinst),
            (self.chk_prerm),(self.chk_postrm)
            ] )
        srb_sizer.AddStretchSpacer(1)
        srb_sizer.Add(self.rb_preinst, 0)
        srb_sizer.Add(self.rb_postinst, 0)
        srb_sizer.Add(self.rb_prerm, 0)
        srb_sizer.Add(self.rb_postrm, 0)
        
        # Sizer for left half of scripts panel
        sleft_sizer = wx.BoxSizer(wx.VERTICAL)
        sleft_sizer.Add(srb_sizer, 0, wx.EXPAND|wx.BOTTOM, 5)
        sleft_sizer.Add(self.te_preinst, 1, wx.EXPAND)
        sleft_sizer.Add(self.te_postinst, 1, wx.EXPAND)
        sleft_sizer.Add(self.te_prerm, 1,wx.EXPAND)
        sleft_sizer.Add(self.te_postrm, 1, wx.EXPAND)
        
        # Auto-Link options
        # Executable list - generate button will make scripts to link to files in this list
        self.xlist = []
        
        # Auto-Link path for new link
        self.al_text = wx.StaticText(self, -1, _('Path'))
        self.al_input = db.PathCtrl(self, -1, "/usr/bin", db.PATH_WARN)
        
        #wx.EVT_KEY_UP(self.al_input, ChangeInput)
        
        alpath_sizer = wx.BoxSizer(wx.HORIZONTAL)
        alpath_sizer.Add(self.al_text, 0, wx.ALIGN_CENTER)
        alpath_sizer.Add(self.al_input, 1, wx.ALIGN_CENTER)
        
        # Auto-Link executables to be linked
        if (wx.MAJOR_VERSION < 3):
            self.executables = wx.ListCtrl(self, -1, size=(200,200), style=wx.BORDER_SIMPLE|wx.LC_SINGLE_SEL)
        else:
            self.executables = wx.ListCtrl(self, -1, size=(200,200), style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        self.executables.InsertColumn(0, "")
        
        # Auto-Link import, generate and remove buttons
        self.al_import = db.ButtonImport(self, ID_Import)
        self.al_import.SetToolTip(wx.ToolTip(_('Import executables from Files section')))
        self.al_del = db.ButtonDel(self, ID_Remove)
        self.al_gen = db.ButtonBuild(self)
        self.al_gen.SetToolTip(wx.ToolTip(_('Generate Scripts')))
        
        wx.EVT_BUTTON(self.al_import, ID_Import, self.ImportExe)
        wx.EVT_BUTTON(self.al_gen, -1, self.OnGenerate)
        wx.EVT_BUTTON(self.al_del, ID_Remove, self.ImportExe)
        
        albutton_sizer = wx.BoxSizer(wx.HORIZONTAL)
        albutton_sizer.Add(self.al_import, 1)#, wx.ALIGN_CENTER|wx.RIGHT, 5)
        albutton_sizer.Add(self.al_del, 1)
        albutton_sizer.Add(self.al_gen, 1)#, wx.ALIGN_CENTER)
        
        # Nice border for auto-generate scripts area
        self.autogen_border = wx.StaticBox(self, -1, _('Auto-Link Executables'), size=(20,20))  # Size mandatory or causes gui errors
        autogen_box = wx.StaticBoxSizer(self.autogen_border, wx.VERTICAL)
        autogen_box.Add(alpath_sizer, 0, wx.EXPAND)
        autogen_box.Add(self.executables, 0, wx.TOP|wx.BOTTOM, 5)
        autogen_box.Add(albutton_sizer, 0, wx.EXPAND)
        #autogen_box.AddSpacer(5)
        #autogen_box.Add(self.al_del, 0, wx.ALIGN_CENTER)
        
        # Text explaining Auto-Link
        """self.al_text = wx.StaticText(self, -1, "How to use Auto-Link: Press the \"import\" button to \
import any executables from the \"files\" tab.  Then press the \"generate\" button.  \"postinst\" and \"prerm\" \
scripts will be created that will place a symbolic link to your executables in the path displayed above.")
        self.al_text.Wrap(210)"""
        
        # *** HELP *** #
        self.button_help = db.ButtonQuestion64(self)
        self.al_help = wx.Dialog(self, -1, _('Auto-Link Help'))
        description = _('Debreate offers an Auto-Link Executables feature. What this does is finds any executables in the Files section and creates a postinst script that will create soft links to them in the specified path. This is useful if you are installing executables to a directory that is not found in the system PATH but want to access it from the PATH. For example, if you install an executable "bar" to the directory "/usr/share/foo" in order to execute "bar" from a terminal you would have to type /usr/share/foo/bar. Auto-Link can be used to place a link to "bar" somewhere on the system path like "/usr/bin". Then all that needs to be typed is bar to execute the program. Auto-Link also creates a prerm script that will delete the link upon removing the package.')
        instructions = _('How to use Auto-Link: Press the IMPORT button to import any executables from the Files section. Then press the GENERATE button. Post-Install and Pre-Remove scripts will be created that will place symbolic links to your executables in the path displayed above.')

        self.al_help_te = wx.TextCtrl(self.al_help, -1, '%s\n\n%s' % (description, instructions),
                style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.al_help_ok = db.ButtonConfirm(self.al_help)
        
        al_help_sizer = wx.BoxSizer(wx.VERTICAL)
        al_help_sizer.AddMany([ (self.al_help_te, 1, wx.EXPAND), (self.al_help_ok, 0, wx.ALIGN_RIGHT) ])
        self.al_help.SetSizer(al_help_sizer)
        self.al_help.Layout()
        
        wx.EVT_BUTTON(self.button_help, wx.ID_HELP, self.OnHelpButton)
        
        # Sizer for right half of scripts panel
        sright_sizer = wx.BoxSizer(wx.VERTICAL)
        sright_sizer.AddSpacer(17)
        sright_sizer.Add(autogen_box, 0)
        #sright_sizer.Add(self.al_text, 0)
        sright_sizer.Add(self.button_help, 0, wx.ALIGN_CENTER)
        
        
        # ----- Layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(sleft_sizer, 1, wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(sright_sizer, 0, wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
        
        
        # ----- Main page sizer
#		page_sizer = wx.BoxSizer(wx.VERTICAL)
#		page_sizer.AddSpacer(10)
#		page_sizer.Add(type_border, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
#		page_sizer.Add(panel_border, 1, wx.EXPAND|wx.ALL, 5)
#		
#		# ----- Page Layout
#		self.SetAutoLayout(True)
#		self.SetSizer(page_sizer)
#		self.Layout()
        
        self.ScriptSelect(None)
        
    def SetLanguage(self):
        # Get language pack for "Scripts" tab
        lang = languages.Scripts()
        
        # Set language to change to
        cur_lang = self.debreate.GetLanguage()
        
        for item in self.setlabels:
            item.SetLabel(lang.GetLanguage(self.setlabels[item], cur_lang))
        
        # Refresh widget layout
        self.Layout()
    
    
    def ScriptSelect(self, event):
        for rb in self.script_te:
            if rb.GetValue() == True:
                self.script_te[rb].Show()
                self.script_chk[rb].Show()
            else:
                self.script_te[rb].Hide()
                self.script_chk[rb].Hide()
        self.Layout()
    
    
    # Importing the executable for Auto-Link
    def ImportExe(self, event):
        id = event.GetId()
        if id == ID_Import:
            # First clear the Auto-Link display and the executable list
            self.executables.DeleteAllItems()
            self.xlist = []
            
            # Get executables from "files" tab
            files = self.debreate.page_files.dest_area
            max = files.GetItemCount()  # Sets the max iterate value
            count = 0
            while count < max:
                # Searches for executables (distinguished by red text)
                if files.GetItemTextColour(count) == (255, 0, 0, 255):
                    filename = os.path.split(files.GetItemText(count))[1]  # Get the filename from the source
                    dest = files.GetItem(count, 1)  # Get the destination of executable
                    try:
                        # If destination doesn't start with "/" do not include executable
                        if dest.GetText()[0] == "/":
                            if dest.GetText()[-1] == "/" or dest.GetText()[-1] == " ":
                                # In case the full path of the destination is "/" keep going
                                if len(dest.GetText()) == 1:
                                    dest_path = ""
                                else:
                                    search = True
                                    slashes = 1  # Set the number of spaces to remove from dest path in case of multiple "/"
                                    while search:
                                        # Find the number of slashes/spaces at the end of the filename
                                        endline = slashes-1
                                        if dest.GetText()[-slashes] == "/" or dest.GetText()[-slashes] == " ":
                                            slashes += 1
                                        else:
                                            dest_path = dest.GetText()[:-endline]
                                            search = False
                            else:
                                dest_path = dest.GetText()
                            
                            # Put "destination/filename" together in executable list
                            self.xlist.insert(0, "%s/%s" %(dest_path, filename))
                            self.executables.InsertStringItem(0, filename)
                            self.executables.SetItemTextColour(0, "red")
                        else:
                            print "panscripts.py: The executables destination is not valid"
                    except IndexError:
                        print "panscripts.py: The executables destination is not available"
                count += 1
        
        elif id == ID_Remove:
            exe = self.executables.GetFirstSelected()
            if exe != -1:
                self.executables.DeleteItem(exe)
                self.xlist.remove(self.xlist[exe])
    
    
    def OnGenerate(self, event):
        # Create the scripts to link the executables
        
        # Create a list of commands to put into the script
        postinst_list = []
        prerm_list = []
        
        link_path = self.al_input.GetValue() # Get destination for link from Auto-Link input textctrl
        total = len(self.xlist)  # Get the amount of links to be created
        
        if total > 0:
            cont = True
            
            # If the link path does not exist on the system post a warning message
            if os.path.isdir(link_path) == False:
                cont = False
                msg_path = _('Path "%s" does not exist. Continue?')
                link_error_dia = wx.MessageDialog(self, msg_path % (link_path), _('Path Warning'),
                    style=wx.YES_NO)
                if link_error_dia.ShowModal() == wx.ID_YES:
                    cont = True
            
            if cont:
                count = 0
                while count < total:
                    filename = os.path.split(self.xlist[count])[1]
                    if "." in filename:
                        linkname = ".".join(filename.split(".")[:-1])
                        link = "%s/%s" % (link_path, linkname)
                    else:
                        link = "%s/%s" % (link_path, filename)
    #				link = "%s/%s" % (link_path, os.path.split(self.xlist[count])[1])
                    postinst_list.append("ln -fs \"%s\" \"%s\"" % (self.xlist[count], link))
                    prerm_list.append("rm \"%s\"" % (link))
                    count += 1
                
                postinst = "\n\n".join(postinst_list)
                prerm = "\n\n".join(prerm_list)
                
                self.te_postinst.SetValue("#! /bin/bash -e\n\n%s" % postinst)
                self.chk_postinst.SetValue(True)
                self.te_prerm.SetValue("#! /bin/bash -e\n\n%s" % prerm)
                self.chk_prerm.SetValue(True)
                
                dia = wx.MessageDialog(self, _('post-install and pre-remove scripts generated'), _('Success'), wx.OK)
                dia.ShowModal()
                dia.Destroy()
    
    def ChangeBG(self, exists):
        if self.al_input.GetValue() == "":
            self.al_input.SetValue("/")
        elif exists == False:
            self.al_input.SetBackgroundColour((255, 0, 0, 255))
        else:
            self.al_input.SetBackgroundColour((255, 255, 255, 255))
    
    # *** HELP *** #
    def OnHelpButton(self, event):
        self.al_help.CenterOnParent()
        self.al_help.ShowModal()
        self.al_help.Close()
    
    
    def ResetAllFields(self):
        for rb in self.script_chk:
            self.script_chk[rb].SetValue(False)
        for rb in self.script_te:
            self.script_te[rb].Clear()
#			# Reset to show Preinstall script as default
#			if rb == self.rb_preinst:
#				self.script_te[rb].Show()
#			else:
#				self.script_te[rb].Hide()
        self.rb_preinst.SetValue(True)
        self.ScriptSelect(None)
        
        self.al_input.SetValue("/usr/bin")
        self.al_input.SetBackgroundColour((255, 255, 255, 255))
        self.executables.DeleteAllItems()
    
    def SetFieldData(self, data):
        preinst = data.split("<<PREINST>>\n")[1].split("\n<</PREINST>>")[0]
        postinst = data.split("<<POSTINST>>\n")[1].split("\n<</POSTINST>>")[0]
        prerm = data.split("<<PRERM>>\n")[1].split("\n<</PRERM>>")[0]
        postrm = data.split("<<POSTRM>>\n")[1].split("\n<</POSTRM>>")[0]
        
        if int(preinst[0]):
            self.chk_preinst.SetValue(True)
            self.te_preinst.SetValue(preinst[2:]) # 2 removes firs line
        else:
            self.chk_preinst.SetValue(False)
            self.te_preinst.Clear()
        if int(postinst[0]):
            self.chk_postinst.SetValue(True)
            self.te_postinst.SetValue(postinst[2:]) # 2 removes firs line
        else:
            self.chk_postinst.SetValue(False)
            self.te_postinst.Clear()
        if int(prerm[0]):
            self.chk_prerm.SetValue(True)
            self.te_prerm.SetValue(prerm[2:]) # 2 removes firs line
        else:
            self.chk_prerm.SetValue(False)
            self.te_prerm.Clear()
        if int(postrm[0]):
            self.chk_postrm.SetValue(True)
            self.te_postrm.SetValue(postrm[2:]) # 2 removes firs line
        else:
            self.chk_postrm.SetValue(False)
            self.te_postrm.Clear()
    
    def GatherData(self):
        # Custom dictionary of scripts
        script_list = (
            (self.chk_preinst, self.te_preinst, "PREINST"),
            (self.chk_postinst, self.te_postinst, "POSTINST"),
            (self.chk_prerm, self.te_prerm, "PRERM"),
            (self.chk_postrm, self.te_postrm, "POSTRM")
        )
        
        # Create a list to return the data
        data = []
        #make_scripts = False # Return empty script section
        for group in script_list:
            if group[0].GetValue():
                #make_scripts = True
                data.append("<<%s>>\n1\n%s\n<</%s>>" % (group[2], group[1].GetValue(), group[2]))
            else:
                data.append("<<%s>>\n0\n<</%s>>" % (group[2], group[2]))
                
        
        return "<<SCRIPTS>>\n%s\n<</SCRIPTS>>" % "\n".join(data)