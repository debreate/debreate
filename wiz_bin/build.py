# -*- coding: utf-8 -*-

## \package wiz_bin.build

# MIT licensing
# See: docs/LICENSE.txt


import commands, os, shutil, subprocess, wx

from dbr.buttons            import ButtonBuild64
from dbr.custom             import OutputLog
from dbr.custom             import SaveFile
from dbr.dialogs            import ShowErrorDialog
from dbr.dialogs            import ShowMessageDialog
from dbr.functions          import FieldEnabled
from dbr.functions          import TextIsEmpty
from dbr.language           import GT
from dbr.log                import Logger
from dbr.md5                import MD5Hasher
from dbr.message            import MessageDialog
from dbr.panel              import BorderedPanel
from globals.bitmaps        import ICON_INFORMATION
from globals.commands       import CMD_gdebi_gui
from globals.commands       import CMD_lintian
from globals.commands       import CMD_md5sum
from globals.commands       import CMD_system_installer
from globals.ident          import FID_ARCH
from globals.ident          import FID_EMAIL
from globals.ident          import FID_MAINTAINER
from globals.ident          import FID_PACKAGE
from globals.ident          import FID_VERSION
from globals.ident          import ID_BUILD
from globals.ident          import ID_CHANGELOG
from globals.ident          import ID_CONTROL
from globals.ident          import ID_COPYRIGHT
from globals.ident          import ID_FILES
from globals.ident          import ID_MENU
from globals.ident          import ID_SCRIPTS
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetField


## Build page
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_BUILD, name=GT(u'Build'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        # ----- Extra Options
        
        pnl_options = BorderedPanel(self)
        
        self.chk_md5 = wx.CheckBox(pnl_options, label=GT(u'Create md5sums file'))
        # The » character denotes that an alternate tooltip should be shown if the control is disabled
        self.chk_md5.tt_name = u'md5»'
        self.chk_md5.SetName(u'MD5')
        self.chk_md5.default = False
        
        if not CMD_md5sum:
            self.chk_md5.Disable()
        
        # For creating md5sum hashes
        self.md5 = MD5Hasher()
        
        # Deletes the temporary build tree
        self.chk_rmstage = wx.CheckBox(pnl_options, label=GT(u'Delete build tree'))
        self.chk_rmstage.SetName(u'rmstage')
        self.chk_rmstage.default = True
        self.chk_rmstage.SetValue(self.chk_rmstage.default)
        
        # Checks the output .deb for errors
        self.chk_lint = wx.CheckBox(pnl_options, label=GT(u'Check package for errors with lintian'))
        self.chk_lint.tt_name = u'lintian»'
        self.chk_lint.SetName(u'LINTIAN')
        self.chk_lint.default = True
        
        if not CMD_lintian:
            self.chk_lint.Disable()
        
        else:
            self.chk_lint.SetValue(self.chk_lint.default)
        
        # Installs the deb on the system
        self.chk_install = wx.CheckBox(pnl_options, label=GT(u'Install package after build'))
        self.chk_install.tt_name = u'install»'
        self.chk_install.SetName(u'INSTALL')
        self.chk_install.default = False
        
        if not CMD_gdebi_gui:
            self.chk_install.Enable(False)
        
        btn_build = ButtonBuild64(self)
        btn_build.SetName(u'build')
        
        # Display log
        dsp_log = OutputLog(self)
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        lyt_options = wx.BoxSizer(wx.VERTICAL)
        lyt_options.AddMany((
            (self.chk_md5, 0, wx.LEFT|wx.RIGHT, 5),
            (self.chk_rmstage, 0, wx.LEFT|wx.RIGHT, 5),
            (self.chk_lint, 0, wx.LEFT|wx.RIGHT, 5),
            (self.chk_install, 0, wx.LEFT|wx.RIGHT, 5)
            ))
        
        pnl_options.SetSizer(lyt_options)
        pnl_options.SetAutoLayout(True)
        pnl_options.Layout()
        
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_build, 1)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(wx.StaticText(self, label=GT(u'Extra Options')), 0,
                wx.ALIGN_LEFT|wx.ALIGN_BOTTOM|wx.LEFT, 5)
        lyt_main.Add(pnl_options, 0, wx.LEFT, 5)
        lyt_main.AddSpacer(5)
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_buttons, 0, wx.ALIGN_CENTER)
        lyt_main.Add(dsp_log, 2, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)
    
    
    ## TODO: Doxygen
    def GatherData(self):
        build_list = []
        
        if self.chk_md5.GetValue():
            build_list.append(u'1')
        
        else:
            build_list.append(u'0')
        
        if self.chk_rmstage.GetValue():
            build_list.append(u'1')
        
        else:
            build_list.append(u'0')
        
        if self.chk_lint.GetValue():
            build_list.append(u'1')
        
        else:
            build_list.append(u'0')
        
        return u'<<BUILD>>\n{}\n<</BUILD>>'.format(u'\n'.join(build_list))
    
    
    ## Installs the built .deb package onto the system
    #  
    #  Uses the system's package installer:
    #    gdebi if available or dpkg
    #  
    #  Shows a success dialog if installed. Otherwise shows an
    #  error dialog.
    #  \param package
    #        \b \e unicode|str : Path to package to be installed
    def InstallPackage(self, package):
        if not CMD_system_installer:
            ShowErrorDialog(
                GT(u'Cannot install package'),
                GT(u'A compatible package manager could not be found on the system'),
                __name__,
                warn=True
                )
            
            return
        
        Logger.Info(__name__, GT(u'Attempting to install package: {}').format(package))
        Logger.Info(__name__, GT(u'Installing with {}').format(CMD_system_installer))
        
        install_output = None
        install_cmd = (CMD_system_installer, package,)
        
        wx.Yield()
        if CMD_system_installer == CMD_gdebi_gui:
            install_output = subprocess.Popen(install_cmd)
        
        # Command appears to not have been executed correctly
        if install_output == None:
            ShowErrorDialog(
                GT(u'Could not install package: {}'),
                GT(u'An unknonw error occurred'),
                __name__
                )
            
            return
        
        # Command executed but did not return success code
        if install_output.returncode:
            err_details = (
                GT(u'Process returned code {}').format(install_output.returncode),
                GT(u'Command executed: {}').format(u' '.join(install_cmd)),
                )
            
            ShowErrorDialog(
                GT(u'An error occurred during installation'),
                u'\n'.join(err_details),
                __name__
                )
            
            return
        
        # TODO: This code is kept for future purposes
        # Gdebi Gtk uses a GUI so no need to show a dialog of our own
        if CMD_system_installer != CMD_gdebi_gui:
            # Command executed & returned successfully
            ShowMessageDialog(
                GT(u'Package was installed to system'),
                GT(u'Success')
                )
    
    
    ## TODO: Doxygen
    def OnBuild(self, event=None):
        main_window = wx.GetApp().GetTopWindow()
        wizard = main_window.GetWizard()
        
        pg_control = wizard.GetPage(ID_CONTROL)
        pg_files = wizard.GetPage(ID_FILES)
        pg_scripts = wizard.GetPage(ID_SCRIPTS)
        pg_clog = wizard.GetPage(ID_CHANGELOG)
        pg_copyright = wizard.GetPage(ID_COPYRIGHT)
        pg_menu = wizard.GetPage(ID_MENU)
        
        fld_package = GetField(pg_control, FID_PACKAGE)
        fld_version = GetField(pg_control, FID_VERSION)
        fld_maint = GetField(pg_control, FID_MAINTAINER)
        fld_email = GetField(pg_control, FID_EMAIL)
        
        # Check to make sure that all required fields have values
        required = [
            fld_package,
            fld_version,
            fld_maint,
            fld_email,
            ]
        
        create_launcher = pg_menu.chk_enable.GetValue()
        
        if create_launcher:
            required.append(pg_menu.ti_name)
            
            if not pg_menu.chk_filename.GetValue():
                required.append(pg_menu.ti_filename)
        
        required_ok = True
        
        for item in required:
            if TextIsEmpty(item.GetValue()):
                required_ok = False
        
        if not required_ok:
            # If required_ok returned False, show an error dialog
            err = wx.MessageDialog(self, GT(u'One of the required fields is empty'), GT(u'Cannot Continue'),
                    wx.OK|wx.ICON_WARNING)
            err.ShowModal()
            err.Destroy()
            
            return
        
        # Characters that should not be in filenames
        invalid_chars = (u' ', u'/')
        
        # Get information from control page for default filename
        pack_value = fld_package.GetValue()
        pack_letters = pack_value.split()  # Remove whitespace
        pack = u'-'.join(pack_letters)  # Replace whitespace with "-"
        
        ver_value = fld_version.GetValue()
        ver_digits = ver_value.split()  # Remove whitespace
        ver = u''.join(ver_digits)
        
        arch = GetField(pg_control, FID_ARCH).GetStringSelection()
        
        # If all required fields were met, continue to build
        def BuildIt(build_path, filename):
            
            temp_tree = u'{}/{}__dbp__'.format(build_path, filename)
            
            deb = u'"{}/{}.deb"'.format(build_path, filename) # Actual path to new .deb
            
            # *** Pre-build operations *** #
            
            tasks = 2 # 2 Represents preparing build tree and actual build of .deb
            progress = 0
            prebuild_progress = wx.ProgressDialog(GT(u'Preparing to build'), GT(u'Gathering control information'), 9,
                    self, wx.PD_AUTO_HIDE)
            
            # Control & Depends (string)
            wx.Yield()
            control_data = pg_control.GetCtrlInfo()
            progress += 1
            tasks += 1
            prebuild_progress.Update(progress, GT(u'Checking files'))
            
            # Files (tuple)
            wx.Yield()
            files_data = pg_files.GatherData().split(u'\n')[2:-1]
            progress += 1
            for FILE in files_data:
                tasks += 1
            
            prebuild_progress.Update(progress, GT(u'Checking scripts'))
            
            # Scripts (tuple)
            wx.Yield()
            scripts_data = pg_scripts.GatherData()[1:-1]
            progress += 1
            # Separate the scripts
            preinst = (u'<<PREINST>>\n', u'\n<</PREINST>>', u'preinst')
            postinst = (u'<<POSTINST>>\n', u'\n<</POSTINST>>', u'postinst')
            prerm = (u'<<PRERM>>\n', u'\n<</PRERM>>', u'prerm')
            postrm = (u'<<POSTRM>>\n', u'\n<</POSTRM>>', u'postrm')
            scripts_temp = (preinst, postinst, prerm, postrm, )
            # Create a list to put the actual scripts in
            scripts = []
            
            for script in scripts_temp:
                create_script = False
                script_name = script[2]
                script = scripts_data.split(script[0])[1].split(script[1])[0].split(u'\n')
                if int(script[0]):
                    tasks += 1
                    # Show that we are going to make the script
                    create_script = True
                
                script = u'\n'.join(script[1:])
                scripts.append((script_name, create_script, script))
            
            # *** Changelog
            prebuild_progress.Update(progress, GT(u'Checking changelog'))
            wx.Yield()
            
            # Changelog (list)
            changelog_data = pg_clog.GatherData()
            changelog_data = changelog_data.split(u'<<CHANGELOG>>\n')[1].split(u'\n<</CHANGELOG>>')[0].split(u'\n')
            create_changelog = False
            
            if pg_clog.GetChangelog() != wx.EmptyString:
                create_changelog = True
            
            if create_changelog:
                tasks += 1
                changelog_dest = changelog_data[0].split(u'<<DEST>>')[1].split(u'<</DEST>>')[0]
                changelog_data = u'\n'.join(changelog_data[1:])
            
            progress += 1
            
            # *** COPYRIGHT
            prebuild_progress.Update(progress, GT(u'Checking copyright'))
            wx.Yield()
            
            cpright = pg_copyright.GetCopyright()
            create_copyright = False
            if cpright != wx.EmptyString:
                create_copyright = True
                tasks += 1
            
            progress += 1
            
            # *** MENU (list)
            prebuild_progress.Update(progress, GT(u'Checking menu launcher'))
            wx.Yield()
            
            if create_launcher:
                tasks += 1
                menu_data = pg_menu.GetLauncherInfo().split(u'\n')
            
            progress += 1
            
            # *** MD5SUMS
            prebuild_progress.Update(progress, GT(u'Checking create md5sums'))
            wx.Yield()
            
            create_md5 = self.chk_md5.GetValue()
            if create_md5:
                tasks += 1
            
            progress += 1
            
            # *** Delete Build Tree
            prebuild_progress.Update(progress, GT(u'Checking delete build tree'))
            wx.Yield()
            
            delete_tree = self.chk_rmstage.GetValue()
            if delete_tree:
                tasks += 1
            
            progress += 1
            
            # *** Check for Errors
            prebuild_progress.Update(progress, GT(u'Checking lintian'))
            wx.Yield()
            
            error_check = self.chk_lint.GetValue()
            if error_check:
                tasks += 1
            
            progress += 1
            
            prebuild_progress.Update(progress)
            
            progress = 0
            build_progress = wx.ProgressDialog(GT(u'Building'), GT(u'Preparing build tree'), tasks, self,
                    wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_AUTO_HIDE)#|wx.PD_CAN_ABORT)
            
            wx.Yield()
            if os.path.isdir(u'{}/DEBIAN'.format(temp_tree)):
                c = u'rm -r "{}"'.format(temp_tree)
                if commands.getstatusoutput(c.encode(u'utf-8'))[0]:
                    err_msg1 = GT(u'Cannot continue:')
                    err_msg2 = GT(u'Could not delete staged directory: {}').format(temp_tree)
                    wx.MessageDialog(self, u'{}\n{}'.format(err_msg1, err_msg2),
                            GT(u'Error'), style=wx.OK|wx.ICON_ERROR).ShowModal()
                    
                    return
            
            # Make a fresh build tree
            os.makedirs(u'{}/DEBIAN'.format(temp_tree))
            progress += 1
            
            # *** FILES
            build_progress.Update(progress, GT(u'Copying files'))
            
            wx.Yield()
            for FILE in files_data:
                # Create new directories
                new_dir = u'{}{}'.format(temp_tree, FILE.split(u' -> ')[2])
                if not os.path.isdir(new_dir):
                    os.makedirs(new_dir)
                
                # Get FILE path
                FILE = FILE.split(u' -> ')[0]
                
                # Remove asteriks from exectuables
                exe = False # Used to set executable permissions
                if FILE[-1] == u'*':
                    exe = True
                    FILE = FILE[:-1]
                
                # Copy files
                copy_path = u'{}/{}'.format(new_dir, os.path.split(FILE)[1])
                shutil.copy(FILE, copy_path)
                
                # Set FILE permissions
                if exe:
                    os.chmod(copy_path, 0755)
                
                else:
                    os.chmod(copy_path, 0644)
                
                progress += 1
                build_progress.Update(progress)
            
            # Make sure that the dirctory is available in which to place documentation
            if create_changelog or create_copyright:
                doc_dir = u'{}/usr/share/doc/{}'.format(temp_tree, pack)
                if not os.path.isdir(doc_dir):
                    os.makedirs(doc_dir)
            
            # *** CHANGELOG
            if create_changelog:
                build_progress.Update(progress, GT(u'Creating changelog'))
                
                wx.Yield()
                # If changelog will be installed to default directory
                if changelog_dest == u'DEFAULT':
                    changelog_dest = u'{}/usr/share/doc/{}'.format(temp_tree, pack)
                
                else:
                    changelog_dest = u'{}{}'.format(temp_tree, changelog_dest)
                
                if not os.path.isdir(changelog_dest):
                    os.makedirs(changelog_dest)
                
                changelog_file = open(u'{}/changelog'.format(changelog_dest), u'w')
                changelog_file.write(changelog_data.encode(u'utf-8'))
                changelog_file.close()
                c = u'gzip -n --best "{}/changelog"'.format(changelog_dest)
                clog_status = commands.getstatusoutput(c.encode(u'utf-8'))
                if clog_status[0]:
                    clog_error = GT(u'Could not create changelog')
                    changelog_error = wx.MessageDialog(self, u'{}\n\n{}'.format(clog_error, clog_status[1]),
                            GT(u'Error'), wx.OK)
                    changelog_error.ShowModal()
                
                progress += 1
            
            # *** COPYRIGHT
            if create_copyright:
                build_progress.Update(progress, GT(u'Creating copyright'))
                
                wx.Yield()
                cp_file = open(u'{}/usr/share/doc/{}/copyright'.format(temp_tree, pack), u'w')
                cp_file.write(cpright.encode(u'utf-8'))
                cp_file.close()
                progress += 1
            
            # *** MENU
            if create_launcher:
                build_progress.Update(progress, GT(u'Creating menu launcher'))
                
                wx.Yield()
                #if menu_data[0]:
                # This may be changed later to set a custom directory
                menu_dir = u'{}/usr/share/applications'.format(temp_tree)
                
                menu_filename = pg_menu.GetOutputFilename()
                
                # Remove invalid characters from filename
                for char in invalid_chars:
                    menu_filename = menu_filename.replace(char, u'_')
                
                if not os.path.isdir(menu_dir):
                    os.makedirs(menu_dir)
                
                menu_file = open(u'{}/{}.desktop'.format(menu_dir, menu_filename), u'w')
                menu_file.write(u'\n'.join(menu_data).encode(u'utf-8'))
                menu_file.close()
                progress += 1
            
            if create_md5:
                build_progress.Update(progress, GT(u'Creating md5sums'))
                
                wx.Yield()
                self.md5.WriteMd5(build_path, temp_tree)
                progress += 1
                build_progress.Update(progress, GT(u'Creating control file'))
            
            # *** CONTROL
            else:
                build_progress.Update(progress, GT(u'Creating control file'))
            
            wx.Yield()
            # Get installed-size
            installed_size = os.popen((u'du -hsk "{}"'.format(temp_tree)).encode(u'utf-8')).readlines()
            installed_size = installed_size[0].split(u'\t')
            installed_size = installed_size[0]
            # Insert Installed-Size into control file
            control_data = control_data.split(u'\n')
            control_data.insert(2, u'Installed-Size: {}'.format(installed_size))
            # dpkg fails if there is no newline at end of file
            control_data.append(u'\n')
            control_data = u'\n'.join(control_data)
            control_file = open(u'{}/DEBIAN/control'.format(temp_tree), u'w')
            control_file.write(control_data.encode(u'utf-8'))
            control_file.close()
            progress += 1
            
            # *** SCRIPTS
            build_progress.Update(progress, GT(u'Creating scripts'))
            
            wx.Yield()
            for script in scripts:
                if script[1]:
                    script_file = open(u'{}/DEBIAN/{}'.format(temp_tree, script[0]), u'w')
                    script_file.write(script[2].encode(u'utf-8'))
                    script_file.close()
                    # Make sure scipt path is wrapped in quotes to avoid whitespace errors
                    os.system((u'chmod +x "{}/DEBIAN/{}"'.format(temp_tree, script[0])).encode(u'utf-8'))
                    progress += 1
                    build_progress.Update(progress)
            
            # *** FINAL BUILD
            build_progress.Update(progress, GT(u'Running dpkg'))[0]
            working_dir = os.path.split(temp_tree)[0]
            c_tree = os.path.split(temp_tree)[1]
            c_deb = u'{}.deb'.format(filename)
            
            # Move the working directory becuase dpkg seems to have problems with spaces in path
            os.chdir(working_dir)
                        
            wx.Yield()
            build_status = commands.getstatusoutput((u'fakeroot dpkg-deb -b "{}" "{}"'.format(c_tree, c_deb)).encode(u'utf-8'))
            progress += 1
            
            # *** DELETE BUILD TREE
            if delete_tree:
                build_progress.Update(progress, GT(u'Removing temp directory'))
                
                wx.Yield()
                if commands.getstatusoutput((u'rm -r "{}"'.format(temp_tree)).encode(u'utf-8'))[0]:
                    wx.MessageDialog(self, GT(u'An error occurred when trying to delete the build tree'),
                            GT(u'Error'), style=wx.OK|wx.ICON_EXCLAMATION)
                
                progress += 1
            
            # *** ERROR CHECK
            if error_check:
                build_progress.Update(progress, GT(u'Checking package for errors'))
                wx.Yield()
                
                errors = commands.getoutput((u'lintian {}'.format(deb)).encode(u'utf-8'))
                e1 = GT(u'Lintian found some issues with the package.')
                e2 = GT(u'Details saved to {}')
                e2 = e2.format(filename)
                if errors.decode(u'utf-8') != wx.EmptyString:
                    error_log = open(u'{}/{}.lintian'.format(build_path, filename), u'w')
                    error_log.write(errors)
                    error_log.close()
                    
                    MessageDialog(self, wx.ID_ANY, GT(u'Lintian Errors'), ICON_INFORMATION,
                            u'{}\n{}.lintian"'.format(e1, e2), errors).ShowModal()
                
                progress += 1
            
            # Close progress dialog
            build_progress.Update(progress)
            
            if build_status[0]:
                # Temp dir will not be deleted if build fails
                wx.MessageDialog(self, GT(u'Package build failed'), GT(u'Error'),
                        style=wx.OK|wx.ICON_ERROR).ShowModal()
            
            else:
                wx.MessageDialog(self, GT(u'Package created successfully'), GT(u'Success'),
                        style=wx.OK|wx.ICON_INFORMATION).ShowModal()
                
                # Installing the package
                if FieldEnabled(self.chk_install) and self.chk_install.GetValue():
                    self.InstallPackage(c_deb)
            
            return build_status[0]
        
        cont = False
        
        # Dialog for save destination
        ttype = GT(u'Debian Packages')
        if main_window.cust_dias.IsChecked():
            save_dia = SaveFile(self)
            save_dia.SetFilter(u'{}|*.deb'.format(ttype))
            save_dia.SetFilename(u'{}_{}_{}.deb'.format(pack, ver, arch))
            if save_dia.DisplayModal():
                cont = True
                path = save_dia.GetPath()
                filename = save_dia.GetFilename().split(u'.deb')[0]
        
        else:
            save_dia = wx.FileDialog(self, GT(u'Save'), os.getcwd(), wx.EmptyString, u'{}|*.deb'.format(ttype),
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
            save_dia.SetFilename(u'{}_{}_{}.deb'.format(pack, ver, arch))
            if save_dia.ShowModal() == wx.ID_OK:
                cont = True
                path = os.path.split(save_dia.GetPath())[0]
                filename = os.path.split(save_dia.GetPath())[1].split(u'.deb')[0]
        
        if cont:
            for char in invalid_chars:
                filename = u'_'.join(filename.split(char))
            BuildIt(path, filename)
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.chk_install.SetValue(False)
        # chk_md5 should be reset no matter
        self.chk_md5.SetValue(False)
        if CMD_md5sum:
            self.chk_md5.Enable()
        
        else:
            self.chk_md5.Disable()
        
        self.chk_rmstage.SetValue(True)
        if CMD_lintian:
            self.chk_lint.Enable()
            self.chk_lint.SetValue(True)
        
        else:
            self.chk_lint.Disable()
            self.chk_lint.SetValue(False)
    
    
    ## TODO: Doxygen
    def SetFieldData(self, data):
        self.ResetAllFields()
        build_data = data.split(u'\n')
        if CMD_md5sum:
            self.chk_md5.SetValue(int(build_data[0]))
        
        self.chk_rmstage.SetValue(int(build_data[1]))
        if CMD_lintian:
            self.chk_lint.SetValue(int(build_data[2]))
    
    
    ## TODO: Doxygen
    def SetSummary(self, event=None):
        main_window = wx.GetApp().GetTopWindow()
        
        # Make sure the page is not destroyed so no error is thrown
        if self:
            # Set summary when "Build" page is shown
            # Get the file count
            files_total = main_window.page_files.dest_area.GetItemCount()
            f = GT(u'File Count')
            file_count = u'{}: {}'.format(f, files_total)
            # Scripts to make
            scripts_to_make = []
            scripts = ((u'preinst', main_window.page_scripts.chk_preinst),
                (u'postinst', main_window.page_scripts.chk_postinst),
                (u'prerm', main_window.page_scripts.chk_prerm),
                (u'postrm', main_window.page_scripts.chk_postrm))
            
            for script in scripts:
                if script[1].IsChecked():
                    scripts_to_make.append(script[0])
            
            s = GT(u'Scripts')
            if len(scripts_to_make):
                scripts_to_make = u'{}: {}'.format(s, u', '.join(scripts_to_make))
            
            else:
                scripts_to_make = u'{}: 0'.format(s)
            
            self.summary.SetValue(u'\n'.join((file_count, scripts_to_make)))
