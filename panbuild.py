# Build Page
# -*- coding: utf-8 -*-

from common import *
import db, os, commands, shutil, db_md5, thread
from os.path import exists

ID = wx.NewId()

class Panel(wx.Panel):
    def __init__(self, parent, id=ID, name=_('Build')):
        wx.Panel.__init__(self, parent, id, name=_('Build'))
        
        # For identifying page to parent
        #self.ID = "BUILD"
        
        self.parent = parent.parent # allows calling of parent events
        
        # --- Tool Tips --- #
        md5_tip = wx.ToolTip(_('Create checksums for files in package'))
        del_tip = wx.ToolTip(_('Delete temporary directory tree after package has been created'))
        #tip_lint = wx.ToolTip(_("Checks the package for errors according to lintian's specifics"))
        dest_tip = wx.ToolTip(_("Choose the folder where you would like the .deb to be created"))
        build_tip = wx.ToolTip(_('Start building'))
        
        
        # ----- Extra Options
        self.chk_md5 = wx.CheckBox(self, -1, _('Create md5sums file'))
        if not exists("/usr/bin/md5sum"):
            self.chk_md5.Disable()
            self.chk_md5.SetToolTip(wx.ToolTip(_('(Install md5sum package for this option)')))
        else:
            self.chk_md5.SetToolTip(md5_tip)
        
        # For creating md5sum hashes
        self.md5 = db_md5.MD5()
        
        # Deletes the temporary build tree
        self.chk_del = wx.CheckBox(self, -1, _('Delete build tree'))
        self.chk_del.SetToolTip(del_tip)
        self.chk_del.SetName("DEL")
        self.chk_del.SetValue(True)
        
        # Checks the output .deb for errors
        self.chk_lint = wx.CheckBox(self, -1, _('Check package for errors with lintian'))
        #self.chk_lint.SetToolTip(tip_lint)
        if not exists("/usr/bin/lintian"):
            self.chk_lint.Disable()
            self.chk_lint.SetToolTip(wx.ToolTip(_('Install lintian package for this option')))
        else:
            #self.chk_lint.SetToolTip(tip_lint)
            self.chk_lint.SetValue(True)
        
        # Installs the deb on the system
        self.chk_install = wx.CheckBox(self, -1, _('Install package after build'))
        
        options1_border = wx.StaticBox(self, -1, _('Extra options')) # Nice border for the options
        options1_sizer = wx.StaticBoxSizer(options1_border, wx.VERTICAL)
        options1_sizer.AddMany( [
            (self.chk_md5, 0),
            (self.chk_del, 0),
            (self.chk_lint, 0),
            (self.chk_install, 0)
            ] )
        
        # --- summary
        #self.summary = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        # Lines to put in the summary
        #self.summary_type = wx.EmptyString
        
        #wx.EVT_SHOW(self, self.SetSummary)
        
        # --- BUILD
        self.build_button = db.ButtonBuild64(self)
        self.build_button.SetToolTip(build_tip)
        
        self.build_button.Bind(wx.EVT_BUTTON, self.OnBuild)
        
        build_sizer = wx.BoxSizer(wx.HORIZONTAL)
        build_sizer.Add(self.build_button, 1)
        
        # --- Display log
        self.log = OutputLog(self)
        
        # --- Page 7 Sizer --- #
        page_sizer = wx.BoxSizer(wx.VERTICAL)
        page_sizer.AddSpacer(10)
        page_sizer.Add(options1_sizer, 0, wx.LEFT, 5)
#        page_sizer.AddSpacer(5)
#        page_sizer.Add(self.summary, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        page_sizer.AddSpacer(5)
        page_sizer.Add(build_sizer, 0, wx.ALIGN_CENTER)
        page_sizer.Add(self.log, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        #page_sizer.AddStretchSpacer(10)
        
        self.SetAutoLayout(True)
        self.SetSizer(page_sizer)
        self.Layout()
        
    
    def SetSummary(self, event):
        #page = event.GetSelection()
        
        # Make sure the page is not destroyed so no error is thrown
        if self:
            # Set summary when "Build" page is shown
            # Get the file count
            files_total = self.parent.page_files.dest_area.GetItemCount()
            f = _('File Count')
            file_count = '%s: %s' % (f, files_total)
            # Scripts to make
            scripts_to_make = []
            scripts = (("preinst", self.parent.page_scripts.chk_preinst),
                ("postinst", self.parent.page_scripts.chk_postinst),
                ("prerm", self.parent.page_scripts.chk_prerm),
                ("postrm", self.parent.page_scripts.chk_postrm))
            for script in scripts:
                if script[1].IsChecked():
                    scripts_to_make.append(script[0])
            s = _('Scripts')
            if len(scripts_to_make):
                scripts_to_make = '%s: %s' % (s, ', '.join(scripts_to_make))
            else:
                scripts_to_make = '%s: 0' % (s)
                    
            self.summary.SetValue("\n".join((file_count, scripts_to_make)))
    
    def OnBuild(self, event):
        # Check to make sure that all required fields have values
        meta = self.parent.page_control
        required = [meta.pack, meta.ver, meta.auth, meta.email]
        if self.parent.page_menu.activate.GetValue():
            required.append(self.parent.page_menu.name_input)
        cont = True
        
        for item in required:
            if item.GetValue() == wx.EmptyString:
                cont = False
        
        if cont:
            # Characters that should not be in filenames
            invalid_chars = (" ", "/")
            
            # Get information from control page for default filename
            pack_value = meta.pack.GetValue()
            pack_letters = pack_value.split()  # Remove whitespace
            pack = "-".join(pack_letters)  # Replace whitespace with "-"
            
            ver_value = meta.ver.GetValue()
            ver_digits = ver_value.split()  # Remove whitespace
            ver = "".join(ver_digits)
            
            arch_index = meta.arch.GetCurrentSelection()
            arch = meta.arch_opt[arch_index]
            
            # If all required fields were met, continue to build
            def BuildIt(build_path, filename):
                
                temp_tree = "%s/%s__dbp__" % (build_path, filename)
                
                deb = "\"%s/%s.deb\"" % (build_path, filename) # Actual path to new .deb
                
                # *** Pre-build operations *** #
                
                tasks = 2 # 2 Represents preparing build tree and actual build of .deb
                progress = 0
                prebuild_progress = wx.ProgressDialog(_('Preparing to build'), _('Gathering control information'), 9,
                        self, wx.PD_AUTO_HIDE)
                
                # Control & Depends (string)
                wx.Yield()
                control_data = self.parent.page_control.GetCtrlInfo()
                progress += 1
                tasks += 1
                prebuild_progress.Update(progress, _('Checking files'))
                
                # Files (tuple)
                wx.Yield()
                files_data = self.parent.page_files.GatherData().split("\n")[2:-1]
                progress += 1
                for file in files_data:
                    tasks += 1
                prebuild_progress.Update(progress, _('Checking scripts'))
                
                # Scripts (tuple)
                wx.Yield()
                scripts_data = self.parent.page_scripts.GatherData()[1:-1]
                progress += 1
                # Separate the scripts
                preinst = ("<<PREINST>>\n", "\n<</PREINST>>", "preinst")
                postinst = ("<<POSTINST>>\n", "\n<</POSTINST>>", "postinst")
                prerm = ("<<PRERM>>\n", "\n<</PRERM>>", "prerm")
                postrm = ("<<POSTRM>>\n", "\n<</POSTRM>>", "postrm")
                scripts_temp = (preinst, postinst, prerm, postrm, )
                # Create a list to put the actual scripts in
                scripts = []
                
                for script in scripts_temp:
                    create_script = False
                    script_name = script[2]
                    script = scripts_data.split(script[0])[1].split(script[1])[0].split("\n")
                    if int(script[0]):
                        tasks += 1
                        create_script = True # Show that we are going to make the script
                    script = "\n".join(script[1:])
                    scripts.append((script_name, create_script, script))
                
                ###############################
                ## *** RESERVED FOR DOCS *** ##
                ###############################
                
                # *** Changelog
                prebuild_progress.Update(progress, _('Checking changelog'))
                
                wx.Yield()
                #create_docs = False
                #doc_data = self.parent.page_docs.GatherData()
                # Changelog (list)
                changelog_data = self.parent.page_clog.GatherData()
                changelog_data = changelog_data.split("<<CHANGELOG>>\n")[1].split("\n<</CHANGELOG>>")[0].split("\n")
                create_changelog = False
                if self.parent.page_clog.GetChangelog() != wx.EmptyString:
                    create_changelog = True
                if create_changelog:
                    tasks += 1
                    changelog_dest = changelog_data[0].split("<<DEST>>")[1].split("<</DEST>>")[0]
                    changelog_data = "\n".join(changelog_data[1:])
                    
                progress += 1
                
                # *** COPYRIGHT
                prebuild_progress.Update(progress, _('Checking copyright'))
                
                wx.Yield()
                copyright = self.parent.page_cpright.GetCopyright()
                create_copyright = False
                if copyright != wx.EmptyString:
                    create_copyright = True
                    tasks += 1
                progress += 1
                
                # *** MENU (list)
                prebuild_progress.Update(progress, _('Checking menu launcher'))
                
                wx.Yield()
                create_menu = self.parent.page_menu.activate.GetValue()
                if create_menu:
                    tasks += 1
                    menu_data = self.parent.page_menu.GetMenuInfo().split("\n")
                progress += 1
                
                # *** MD5SUMS
                prebuild_progress.Update(progress, _('Checking create md5sums'))
                wx.Yield()
                
                create_md5 = self.chk_md5.GetValue()
                if create_md5:
                    tasks += 1
                progress += 1
                
                # *** Delete Build Tree
                prebuild_progress.Update(progress, _('Checking delete build tree'))
                wx.Yield()
                
                delete_tree = self.chk_del.GetValue()
                if delete_tree:
                    tasks += 1
                progress += 1
                
                # *** Check for Errors
                prebuild_progress.Update(progress, _('Checking lintian'))
                wx.Yield()
                
                error_check = self.chk_lint.GetValue()
                if error_check:
                    tasks += 1
                progress += 1
                
                prebuild_progress.Update(progress)
                
#                try:
                progress = 0
                build_progress = wx.ProgressDialog(_('Building'), _('Preparing build tree'), tasks, self,
                        wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_AUTO_HIDE)#|wx.PD_CAN_ABORT)
                
                wx.Yield()
                if os.path.isdir("%s/DEBIAN" % (temp_tree)):
                    c = 'rm -r "%s"' % (temp_tree)
                    if commands.getstatusoutput(c.encode('utf-8'))[0]:
                        wx.MessageDialog(self, _('An Error Occurred:\nCould not delete "%s"') % (temp_tree), _("Can't Continue"), style=wx.OK|wx.ICON_ERROR).ShowModal()
                # Make a fresh build tree
                os.makedirs("%s/DEBIAN" % (temp_tree))
                progress += 1
                
                # *** FILES
                build_progress.Update(progress, _('Copying files'))
                
                wx.Yield()
                for file in files_data:
                    # Create new directories
                    new_dir = "%s%s" % (temp_tree, file.split(" -> ")[2])
                    if not os.path.isdir(new_dir):
                        os.makedirs(new_dir)
                    # Get file path
                    file = file.split(" -> ")[0]
                    # Remove asteriks from exectuables
                    exe = False # Used to set executable permissions
                    if file[-1] == "*":
                        exe = True
                        file = file[:-1]
                    # Copy files
                    copy_path = u'%s/%s' % (new_dir, os.path.split(file)[1])
                    shutil.copy(file, copy_path)
                    # Set file permissions
                    if exe:
                        c = 'chmod 0755 %s' % (copy_path)
                        commands.getoutput(c.encode('utf-8'))
                    else:
                        c = 'chmod 0644 %s' % (copy_path)
                        commands.getoutput(c.encode('utf-8'))
                    progress += 1
                    build_progress.Update(progress)
                #progress += 1
                
                # Make sure that the dirctory is available in which to place documentation
                if create_changelog or create_copyright:
                    doc_dir = "%s/usr/share/doc/%s" % (temp_tree, pack)
                    if not os.path.isdir(doc_dir):
                        os.makedirs(doc_dir)
                
                # *** CHANGELOG
                if create_changelog:
                    build_progress.Update(progress, _('Creating changelog'))
                    
                    wx.Yield()
                    # If changelog will be installed to default directory
                    if changelog_dest == "DEFAULT":
                        changelog_dest = "%s/usr/share/doc/%s" % (temp_tree, pack)
                    else:
                        changelog_dest = "%s%s" % (temp_tree, changelog_dest)
                    if not os.path.isdir(changelog_dest):
                        os.makedirs(changelog_dest)
                    changelog_file = open("%s/changelog" % (changelog_dest), "w")
                    changelog_file.write(changelog_data.encode('utf-8'))
                    changelog_file.close()
                    c = 'gzip --best "%s/changelog"' % (changelog_dest)
                    clog_status = commands.getstatusoutput(c.encode('utf-8'))
                    if clog_status[0]:
                        clog_error = _("Couldn't create changelog")
                        changelog_error = wx.MessageDialog(self, '%s\n\n%s' % (clog_error, clog_status[1]),
                                _('Error'), wx.OK)
                        changelog_error.ShowModal()
                    progress += 1
                
                # *** COPYRIGHT
                if create_copyright:
                    build_progress.Update(progress, _('Creating copyright'))
                    
                    wx.Yield()
                    cp_file = open("%s/usr/share/doc/%s/copyright" % (temp_tree, pack), "w")
                    cp_file.write(copyright.encode('utf-8'))
                    cp_file.close()
                    progress += 1
                
                # *** MENU
                if create_menu:
                    build_progress.Update(progress, _('Creating menu launcher'))
                    
                    wx.Yield()
                    #if menu_data[0]:
                    # This may be changed later to set a custom directory
                    menu_dir = "%s/usr/share/applications" % (temp_tree)
                    for field in menu_data:
                        if field.split("=")[0] == "Name":
                            menu_filename = "=".join(field.split("=")[1:])
                    
                    # Remove invalid characters from filename
                    for char in invalid_chars:
                        menu_filename = "_".join(menu_filename.split(char)) # Replace invalid char with "underscore"
                    if not os.path.isdir(menu_dir):
                        os.makedirs(menu_dir)
                    menu_file = open("%s/%s.desktop" % (menu_dir, menu_filename), "w")
                    menu_file.write("\n".join(menu_data).encode('utf-8'))
                    menu_file.close()
                    progress += 1
                
                if create_md5:
                    build_progress.Update(progress, _('Creating md5sums'))
                    
                    wx.Yield()
                    self.md5.WriteMd5(build_path, temp_tree)
                    progress += 1
                    build_progress.Update(progress, _('Creating control file'))
                
                # *** CONTROL
                else:
                    build_progress.Update(progress, _('Creating control file'))
                
                wx.Yield()
                # Get installed-size
                installed_size = os.popen(("du -hsk \"%s\"" % (temp_tree)).encode('utf-8')).readlines()
                installed_size = installed_size[0].split("\t")
                installed_size = installed_size[0]
                # Insert Installed-Size into control file
                control_data = control_data.split("\n")
                control_data.insert(2, "Installed-Size: %s" % (installed_size))
                # dpkg fails if there is no newline at end of file
                control_data.append("\n")
                control_data = "\n".join(control_data)
                control_file = open("%s/DEBIAN/control" % (temp_tree), "w")
                control_file.write(control_data.encode('utf-8'))
                control_file.close()
                progress += 1
                
                # *** SCRIPTS
                build_progress.Update(progress, _('Creating scripts'))
                
                wx.Yield()
                for script in scripts:
                    if script[1]:
                        script_file = open("%s/DEBIAN/%s" % (temp_tree, script[0]), 'w')
                        script_file.write(script[2].encode('utf-8'))
                        script_file.close()
                        # Make sure scipt path is wrapped in quotes to avoid whitespace errors
                        os.system(('chmod +x "%s/DEBIAN/%s"' % (temp_tree, script[0])).encode('utf-8'))
                        progress += 1
                        build_progress.Update(progress)
                
                # *** FINAL BUILD
                build_progress.Update(progress, _('Running dpkg'))[0]
#                c_tree = temp_tree.encode('utf-8')
#                print c_tree
#                c_deb = deb.encode('utf-8')
#                print c_deb
                working_dir = os.path.split(temp_tree)[0]
                c_tree = os.path.split(temp_tree)[1]
                c_deb = '%s.deb' % filename
                
                # Move the working directory becuase dpkg seems to have problems with spaces in path
                os.chdir(working_dir)
                            
                wx.Yield()
#                if subprocess.call(['fakeroot', 'dpkg', '-b', c_tree, c_deb]):
#                    build_status = (1, 0)
#                try:
                build_status = commands.getstatusoutput(('fakeroot dpkg-deb -b "%s" "%s"' % (c_tree, c_deb)).encode('utf-8'))
                progress += 1
                
                # *** DELETE BUILD TREE
                if delete_tree:
                    build_progress.Update(progress, _('Removing temp directory'))
                    
                    wx.Yield()
                    # Delete the build tree
                    if commands.getstatusoutput(('rm -r "%s"' % temp_tree).encode('utf-8'))[0]:
                        wx.MessageDialog(self, _('An error occurred when trying to delete the build tree'), _('Error'), style=wx.OK|wx.ID_EXCLAMATION)
                    progress += 1
                
                # *** ERROR CHECK
                if error_check:
                    build_progress.Update(progress, _('Checking package for errors'))
                    wx.Yield()
                    
                    errors = commands.getoutput(('lintian %s' % deb).encode('utf-8'))
                    e1 = _('Lintian found some issues with the package.')
                    e2 = _('Details saved to %s')
                    e2 = e2 % (filename)
                    if errors.decode('utf-8') != wx.EmptyString:
                        error_log = open("%s/%s.lintian" % (build_path, filename), "w")
                        error_log.write(errors)
                        error_log.close()
                        db.MessageDialog(self, -1,
                        _('Lintian Errors'), db.ICON_INFORMATION,
                        '%s\n%s.lintian"' % (e1, e2),
                        errors
                        ).ShowModal()
                    progress += 1
                
                # Close progress dialog
                build_progress.Update(progress)
                
                if build_status[0]:
                    # Temp dir will not be deleted if build fails
                    wx.MessageDialog(self, _('Package build failed'), _('Error'),
                            style=wx.OK|wx.ICON_ERROR).ShowModal()
                else:
                    wx.MessageDialog(self, _('Package created successfully'), _('Success'),
                            style=wx.OK|wx.ICON_INFORMATION).ShowModal()
                    
                    # Installing the package
                    if self.chk_install.GetValue():
                        self.log.ToggleOutput()
                        print _(u'Getting administrative privileges from user')
                        pshow = _(u'Password')
                        command_executed = False
                        tries = 0
                        while (tries < 3):
                            password = wx.GetPasswordFromUser(pshow, _(u'Installing Package'))
                            if (password == u''):
                                print _(u'Empty password: Cancelling')
                                break
                            e = RunSudo(password, u'dpkg -i %s' % (deb))
                            if (not e):
                                if (tries == 2):
                                    print _(u'Authentication failure')
                                    install_fail = _(u'Could not install %s')
                                    print install_fail % (deb)
                                else:
                                    print _(u'Password mismatch, try again')
                            else:
                                command_executed = True
                                print _(u'Authenticated')
                                break
                            tries += 1
                        
                        # Check if package installed correctly
                        if (int(os.popen(u'dpkg -L %s ; echo $?' % (pack)).read().split(u'\n')[-2]) and command_executed):
                            wx.MessageDialog(self, _(u'The package failed to install'), _(u'Error'), wx.OK|wx.ICON_ERROR).ShowModal()
                        elif (command_executed):
                            wx.MessageDialog(self, _(u'The package installed successfully'), _(u'Sucess'), wx.OK).ShowModal()
                        self.log.ToggleOutput()
                
                return build_status[0]
            
            cont = False
            
            # Dialog for save destination
            ttype = _('Debian Packages')
            if self.parent.cust_dias.IsChecked():
                save_dia = db.SaveFile(self)
                save_dia.SetFilter("%s|*.deb" % ttype)
                save_dia.SetFilename("%s_%s_%s.deb" % (pack, ver, arch))
                if save_dia.DisplayModal():
                    cont = True
                    path = save_dia.GetPath()
                    filename = save_dia.GetFilename().split(".deb")[0]
            else:
                save_dia = wx.FileDialog(self, _("Save"), os.getcwd(), wx.EmptyString, "%s|*.deb" % ttype,
                        wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
                save_dia.SetFilename("%s_%s_%s.deb" % (pack, ver, arch))
                if save_dia.ShowModal() == wx.ID_OK:
                    cont = True
                    path = os.path.split(save_dia.GetPath())[0]
                    filename = os.path.split(save_dia.GetPath())[1].split(".deb")[0]
            
            if cont:
                for char in invalid_chars:
                    filename = "_".join(filename.split(char))
                BuildIt(path, filename)
        
        else:
            # If continue returned False, show an error dialog
            err = wx.MessageDialog(self, _('One of the required fields is empty'), _("Can't Continue"),
                    wx.OK|wx.ICON_WARNING)
            err.ShowModal()
            err.Destroy()
    
    def ResetAllFields(self):
        self.chk_install.SetValue(False)
        # chk_md5 should be reset no matter
        self.chk_md5.SetValue(False)
        if exists("/usr/bin/md5sum"):
            self.chk_md5.Enable()
        else:
            self.chk_md5.Disable()
        self.chk_del.SetValue(True)
        if exists("/usr/bin/lintian"):
            self.chk_lint.Enable()
            self.chk_lint.SetValue(True)
        else:
            self.chk_lint.Disable()
            self.chk_lint.SetValue(False)
    
    def SetFieldData(self, data):
        self.ResetAllFields()
        build_data = data.split("\n")
        if exists("/usr/bin/md5sum"):
            self.chk_md5.SetValue(int(build_data[0]))
        self.chk_del.SetValue(int(build_data[1]))
        if exists("usr/bin/lintian"):
            self.chk_lint.SetValue(int(build_data[2]))
    
    def GatherData(self):
        build_list = []
        
        if self.chk_md5.GetValue(): build_list.append("1")
        else: build_list.append("0")
        if self.chk_del.GetValue(): build_list.append("1")
        else: build_list.append("0")
        if self.chk_lint.GetValue(): build_list.append("1")
        else: build_list.append("0")
        return "<<BUILD>>\n%s\n<</BUILD>>" % "\n".join(build_list)


##########################################
## *** BUIDING FROM PREEXISTING FILE SYSTEM TREE **  ##
##########################################

class QuickBuild(wx.Dialog):
    def __init__(self, parent, id=-1, title=_('Quick Build')):
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, (400,200))
        
        self.parent = parent # allows calling parent events
        
        # Set icon
#        rpmicon = wx.Icon("%s/bitmaps/rpm16.png" % application_path, wx.BITMAP_TYPE_PNG)
#        self.SetIcon(rpmicon)
        
        filename_txt = wx.StaticText(self, -1, _('Name'))
        self.filename = wx.TextCtrl(self, -1)
        path_txt = wx.StaticText(self, -1, _('Path to build tree'))
        self.path = wx.TextCtrl(self, -1) # Path to the root of the directory tree
        self.get_path = db.ButtonBrowse(self)
        self.build = db.ButtonBuild(self)
        self.build.SetToolTip(wx.ToolTip(_('Start building')))
        self.cancel = db.ButtonCancel(self)
        
        wx.EVT_BUTTON(self.get_path, -1, self.Browse)
        wx.EVT_BUTTON(self.build, -1, self.OnBuild)
        wx.EVT_BUTTON(self.cancel, -1, self.OnQuit)
        
        H0 = wx.BoxSizer(wx.HORIZONTAL)
        H0.Add(self.filename, 1)
        
        H1 = wx.BoxSizer(wx.HORIZONTAL)
        H1.Add(self.path, 3, wx.ALIGN_CENTER)
        H1.Add(self.get_path, 0, wx.ALIGN_CENTER)
        
        H2 = wx.BoxSizer(wx.HORIZONTAL)
        H2.Add(self.build, 1, wx.RIGHT, 5)
        H2.Add(self.cancel, 1)
        
        self.gauge = wx.Gauge(self, -1, 100)
        
        # Create a timer for the gauge
        self.timer = wx.Timer(self)
        
        self.Bind(wx.EVT_TIMER, self.ShowProgress, self.timer)
        
        Vmain = wx.BoxSizer(wx.VERTICAL)
        Vmain.Add(filename_txt, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        Vmain.Add(H0, 2, wx.EXPAND|wx.ALL, 5)
        Vmain.Add(path_txt, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        Vmain.Add(H1, 2, wx.EXPAND|wx.ALL, 5)
        Vmain.Add(H2, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        Vmain.Add(self.gauge, 2, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(Vmain)
        self.Layout()
    
    
    def Browse(self, event):
        if self.parent.cust_dias.IsChecked():
            dia = db.OpenDir(self)
            if dia.DisplayModal() == True:
                self.path.SetValue(dia.GetPath())
        else:
            dia = wx.DirDialog(self, _('Choose Directory'), os.getcwd(), "", style=wx.CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                self.path.SetValue(dia.GetPath())
        dia.Destroy()
    
    def ShowProgress(self, event):
        self.gauge.Pulse()
    
    def Build(self, path, arg2):
        root = os.path.split(path)[1]
        work_dir = os.path.split(path)[0]
        filename = self.filename.GetValue()
        if ''.join(filename.split(' ')) == '':
            filename = root
        if filename.split('.')[-1] == 'deb':
            filename = '.'.join(filename.split('.')[:-1])
        os.chdir(work_dir)
        commands.getstatusoutput(('fakeroot dpkg-deb -b "%s" "%s.deb"' % (root, filename)).encode('utf-8'))
        self.timer.Stop()
        self.gauge.SetValue(100)
        self.Enable()
    
    def OnBuild(self, event):
        path = self.path.GetValue()
        if os.path.isdir(path):
            # Disable the window so it can't be closed while working
            self.Disable()
            thread.start_new_thread(self.Build, (path, None))
            self.timer.Start(100)
        else:
            e = _('Could not locate \"%s\"')
            e = e % (path)
            wx.MessageDialog(self, e, _('Error'), wx.OK|wx.ICON_ERROR).ShowModal()
    
    def OnQuit(self, event):
        self.Close()
