# -*- coding: utf-8 -*-

## \package wiz_bin.build


import os, commands, shutil, thread, traceback, time
import wx

from dbr                import Logger, DebugEnabled
import dbr
from dbr.dialogs        import DetailedMessageDialog
from dbr.dialogs        import ErrorDialog
from dbr.dialogs        import GetFileSaveDialog
from dbr.dialogs        import ShowDialog
from dbr.functions      import BuildBinaryPackageFromTree
from dbr.functions      import CreateTempDirectory
from dbr.functions      import GetBoolean
from dbr.functions      import RemoveTempDirectory
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from dbr.wizard         import WizardPage
from globals.bitmaps    import ICON_ERROR
from globals.bitmaps    import ICON_INFORMATION
from globals.commands   import CMD_lintian
from globals.commands   import CMD_md5sum
from globals.errorcodes import errno
from globals.ident      import ID_BUILD
from globals.ident      import ID_CHANGELOG
from globals.ident      import ID_CONTROL
from globals.ident      import ID_COPYRIGHT
from globals.ident      import ID_FILES
from globals.ident      import ID_MAN
from globals.ident      import ID_MENU
from globals.ident      import ID_SCRIPTS


class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ID_BUILD)
        
        # Bypass build prep check
        self.prebuild_check = False
        
        self.debreate = parent.GetDebreateWindow()
        
        # --- Tool Tips --- #
        md5_tip = wx.ToolTip(GT(u'Create checksums for files in package'))
        del_tip = wx.ToolTip(GT(u'Delete temporary directory tree after package has been created'))
        #tip_lint = wx.ToolTip(GT(u'Checks the package for errors according to lintian's specifics'))
        dest_tip = wx.ToolTip(GT(u'Choose the folder where you would like the .deb to be created'))
        build_tip = wx.ToolTip(GT(u'Start building'))
        
        
        # Add checkable items to this list
        self.build_options = []
        
        # ----- Extra Options
        self.chk_md5 = wx.CheckBox(self, -1, GT(u'Create md5sums file'))
        self.chk_md5.SetName(u'MD5')
        self.chk_md5.default = False
        
        if not CMD_md5sum:
            self.chk_md5.Disable()
            self.chk_md5.SetToolTip(wx.ToolTip(GT(u'Install md5sum package for this option')))
        else:
            self.chk_md5.SetToolTip(md5_tip)
            self.build_options.append(self.chk_md5)
        
        # For creating md5sum hashes
        self.md5 = dbr.MD5()
        
        # Deletes the temporary build tree
        self.chk_rmtree = wx.CheckBox(self, -1, GT(u'Delete build tree'))
        self.chk_rmtree.SetName(u'RMTREE')
        self.chk_rmtree.SetToolTip(del_tip)
        self.chk_rmtree.default = True
        self.chk_rmtree.SetValue(self.chk_rmtree.default)
        self.build_options.append(self.chk_rmtree)
        
        # Checks the output .deb for errors
        self.chk_lint = wx.CheckBox(self, -1, GT(u'Check package for errors with lintian'))
        self.chk_lint.SetName(u'LINTIAN')
        self.chk_lint.default = True
        #self.chk_lint.SetToolTip(tip_lint)
        if not CMD_lintian:
            self.chk_lint.Disable()
            self.chk_lint.SetToolTip(wx.ToolTip(GT(u'Install lintian package for this option')))
        else:
            #self.chk_lint.SetToolTip(tip_lint)
            self.chk_lint.SetValue(self.chk_lint.default)
            self.build_options.append(self.chk_lint)
        
        # Installs the deb on the system
        self.chk_install = wx.CheckBox(self, -1, GT(u'Install package after build'))
        self.chk_install.SetName(u'INSTALL')
        self.chk_install.default = False
        self.build_options.append(self.chk_install)
        
        options1_border = wx.StaticBox(self, -1, GT(u'Extra options')) # Nice border for the options
        options1_sizer = wx.StaticBoxSizer(options1_border, wx.VERTICAL)
        options1_sizer.AddMany( [
            (self.chk_md5, 0),
            (self.chk_rmtree, 0),
            (self.chk_lint, 0),
            (self.chk_install, 0)
            ] )
        
        # --- summary
        #self.summary = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        # Lines to put in the summary
        #self.summary_type = wx.EmptyString
        
        #wx.EVT_SHOW(self, self.SetSummary)
        
        # --- BUILD
        self.build_button = dbr.ButtonBuild64(self)
        self.build_button.SetToolTip(build_tip)
        
        self.build_button.Bind(wx.EVT_BUTTON, self.OnBuild)
        
        build_sizer = wx.BoxSizer(wx.HORIZONTAL)
        build_sizer.Add(self.build_button, 1)
        
        # --- Display log
        self.log = dbr.OutputLog(self)
        
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
    
    
    ## Method that builds the actual Debian package
    #  
    #  TODO: Create temp stage directory tree
    #  TODO: Delete temp stage directory tree
    #  TODO: Run dpkg-deb command
    #  TODO: Test for errors when building deb package with other filename extension
    #  TODO: Remove deprecated methods that this one replaces
    #  \param out_file
    #        \b \e str|unicode : Absolute path to target file
    def Build(self, out_file):
        pages_build_ids = self.BuildPrep()
        
        if pages_build_ids != None:
            steps_count = len(pages_build_ids)
            current_step = 0
            
            # Steps from build page
            for chk in self.chk_md5, self.chk_lint, self.chk_rmtree:
                if chk.IsChecked():
                    steps_count += 1
            
            # FIXME: Enable PD_CAN_ABORT
            build_progress = wx.ProgressDialog(GT(u'Building'), GT(u'Starting build'),
                    steps_count, self.GetDebreateWindow(), wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
            wx.Yield()
            
            time.sleep(3)
            
            try:
                for P in self.wizard.pages:
                    if build_progress.WasCancelled():
                        break
                    
                    page_id = P.GetId()
                    
                    if P.GetId() in pages_build_ids:
                        page_label = P.GetLabel()
                        
                        # FIXME: Progress bar not updating
                        wx.Yield()
                        build_progress.Update(current_step,
                                GT(u'Processing page "{}" ({}/{})').format(page_label, current_step+1, steps_count))
                        # TODO: Remove
                        time.sleep(1)
                        
                        if page_id == ID_CONTROL:
                            Logger.Debug(__name__, page_label)
                        
                        elif page_id == ID_FILES:
                            Logger.Debug(__name__, page_label)
                        
                        elif page_id == ID_MAN:
                            Logger.Debug(__name__, page_label)
                        
                        elif page_id == ID_SCRIPTS:
                            Logger.Debug(__name__, page_label)
                        
                        elif page_id == ID_CHANGELOG:
                            Logger.Debug(__name__, page_label)
                        
                        elif page_id == ID_COPYRIGHT:
                            Logger.Debug(__name__, page_label)
                        
                        elif page_id == ID_MENU:
                            Logger.Debug(__name__, page_label)
                        
                        elif page_id == ID_BUILD:
                            Logger.Debug(__name__, page_label)
                        
                        current_step += 1
                
                if not build_progress.WasCancelled():
                    if self.chk_md5.IsChecked():
                        wx.Yield()
                        build_progress.Update(current_step,
                                GT(u'Creating MD5 checksum ({}/{})').format(current_step+1, steps_count))
                        
                        self.CreateMD5Sum(u'Null dir')
                        
                        current_step += 1
                
                if not build_progress.WasCancelled():
                    if self.chk_lint.IsChecked():
                        wx.Yield()
                        build_progress.Update(current_step,
                                GT(u'Checking package with lintian ({}/{})').format(current_step+1, steps_count))
                        
                        self.CheckPackageLintian(u'Null package')
                        
                        current_step += 1
                
                if not build_progress.WasCancelled():
                    if self.chk_rmtree.IsChecked():
                        wx.Yield()
                        build_progress.Update(current_step,
                                GT(u'Removing staged build tree ({}/{})').format(current_step+1, steps_count))
                        
                        current_step += 1
                
                if not build_progress.WasCancelled():
                    wx.Yield()
                    build_progress.Update(steps_count, GT(u'Build finished'))
                    
                    # Show finished dialog for short moment
                    time.sleep(1)
                
                build_progress.Destroy()
            
            except:
                build_progress.Destroy()
                
                # TODO: Use dbr.error dialog
                err_msg = GT(u'Error occurred during build')
                Logger.Error(__name__, u'{}:\n{}'.format(err_msg, traceback.format_exc()))
                
                err_dialog = ErrorDialog(self.GetDebreateWindow(), GT(u'Error occured during build'))
                err_dialog.SetDetails(traceback.format_exc())
                err_dialog.ShowModal()
                
                err_dialog.Destroy()
        
        return
        
        try:
            temp_dir = CreateTempDirectory()
            
            if temp_dir != errno.EACCES:
                Logger.Debug(__name__, GT(u'Temporary directory: {}').format(temp_dir))
                
                # Create DEBIAN sub-directory
                os.makedirs(u'{}/DEBIAN'.format(temp_dir))
                
                if self.chk_md5.IsChecked():
                    self.CreateMD5Sum(temp_dir)
                
                if self.chk_lint.IsChecked():
                    self.CheckPackageLintian(u'Null package')
                
                if self.chk_rmtree.IsChecked():
                    RemoveTempDirectory(temp_dir)
                
                return
            
            # FIXME: Throw exception or show error dialog here, temp_dir was not created
        
        except:
            err_dialog = ErrorDialog(self.GetDebreateWindow(), GT(u'Error occured during build'))
            err_dialog.SetDetails(traceback.format_exc())
            err_dialog.ShowModal()
            
            err_dialog.Destroy()
        
        return
        
        
        filename = os.path.basename(out_file)
        target_dir = os.path.dirname(out_file)
        
        Logger.Debug(__name__, GT(u'Building package {} in {}').format(filename, target_dir))
        
        build_ret = BuildBinaryPackageFromTree(temp_dir, out_file)
        
        if build_ret == errno.ENOENT:
            ErrorDialog(self.GetDebreateWindow(), GT(u'Cannot build from non-existent directory')).ShowModal()
        
        # TODO: Make sure temp directory is deleted
        shutil.rmtree(temp_dir)
    
    
    ## 
    #  
    #  \return
    #        \b \e tuple containing data & label for each page
    def BuildPrep(self):
        prep_ids = []
        
        for P in self.wizard.pages:
            if P.prebuild_check:
                Logger.Debug(__name__, GT(u'Pre-build check for page "{}"'.format(P.GetName())))
                prep_ids.append(P.GetId())
        
        try:
            # List of page IDs to process during build
            build_page_ids = []
            
            steps_count = len(prep_ids)
            current_step = 0
            
            msg_label1 = GT(u'Prepping page "{}"')
            msg_label2 = GT(u'Step {}/{}')
            msg_label = u'{} ({})'.format(msg_label1, msg_label2)
            
            prep_progress = wx.ProgressDialog(GT(u'Preparing Build'), msg_label2.format(current_step, steps_count),
                    steps_count, self.GetDebreateWindow(), wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
            
            for P in self.wizard.pages:
                if prep_progress.WasCancelled():
                    break
                
                page_id = P.GetId()
                page_label = P.GetLabel()
                
                if page_id in prep_ids:
                    Logger.Debug(__name__, msg_label.format(page_label, current_step+1, steps_count))
                    
                    wx.Yield()
                    prep_progress.Update(current_step, msg_label.format(page_label, current_step+1, steps_count))
                    
                    if P.IsExportable():
                        build_page_ids.append(page_id)
                    
                    current_step += 1
                
            if not prep_progress.WasCancelled():
                wx.Yield()
                prep_progress.Update(current_step, GT(u'Prepping finished'))
                
                # Show finished dialog for short period
                time.sleep(1)
            
            prep_progress.Destroy()
            
            return build_page_ids
            
        except:
            prep_progress.Destroy()
            
            err_traceback = traceback.format_exc()
            
            err_title = GT(u'Error occured during pre-build')
            Logger.Error(__name__, u'{}:\n{}'.format(err_title, err_traceback))
            
            err_dialog = ErrorDialog(self, err_title)
            err_dialog.SetDetails(err_traceback)
            err_dialog.ShowModal()
            
            # Cleanup
            err_dialog.Destroy()
            del err_title
        
        return None
    
    
    # TODO: Finish defining
    def CheckPackageLintian(self, package):
        Logger.Debug(__name__,
                GT(u'Checking package "{}" for lintian errors ...').format(os.path.basename(package)))
    
    
    # TODO: Finish defining
    def CreateMD5Sum(self, directory):
        Logger.Debug(__name__,
                GT(u'Creating MD5sum file in {}').format(directory))
    
    
    def SetSummary(self, event):
        #page = event.GetSelection()
        
        # Make sure the page is not destroyed so no error is thrown
        if self:
            # Set summary when "Build" page is shown
            # Get the file count
            files_total = self.debreate.page_files.dest_area.GetItemCount()
            f = GT(u'File Count')
            file_count = u'%s: %s' % (f, files_total)
            # Scripts to make
            scripts_to_make = []
            scripts = ((u'preinst', self.debreate.page_scripts.chk_preinst),
                (u'postinst', self.debreate.page_scripts.chk_postinst),
                (u'prerm', self.debreate.page_scripts.chk_prerm),
                (u'postrm', self.debreate.page_scripts.chk_postrm))
            for script in scripts:
                if script[1].IsChecked():
                    scripts_to_make.append(script[0])
            s = GT(u'Scripts')
            if len(scripts_to_make):
                scripts_to_make = u'%s: %s' % (s, u', '.join(scripts_to_make))
            else:
                scripts_to_make = u'%s: 0' % (s)
                    
            self.summary.SetValue(u'\n'.join((file_count, scripts_to_make)))
    
    # TODO: Finish defining
    def OnBuild(self, event):
        meta = self.debreate.page_control
        required_fields = {
            GT(u'Control'): (meta.pack, meta.ver, meta.auth, meta.email,),
        }
        
        if self.debreate.page_menu.activate.GetValue():
            #required_fields.append(self.debreate.page_menu.name_input)
            required_fields[GT(u'Menu Launcher')] = (self.debreate.page_menu.name_input,)
        
        for page_name in required_fields:
            for F in required_fields[page_name]:
                if TextIsEmpty(F.GetValue()):
                    field_name = F.GetName()
                    
                    Logger.Debug(__name__,
                            u'{}: {} ➜ {}'.format(GT(u'A required field is empty'), page_name, field_name))
                    
                    err_dialog = wx.MessageDialog(self.GetDebreateWindow(), GT(u'A required field is empty'),
                            GT(u'Error'), style=wx.OK|wx.ICON_ERROR)
                    err_dialog.SetExtendedMessage(u'{} ➜ {}'.format(page_name, field_name))
                    err_dialog.ShowModal()
                    
                    for P in self.wizard.pages:
                        if P.GetLabel() == page_name:
                            self.wizard.ShowPage(P.GetId())
                    
                    return
        
        
        ttype = GT(u'Debian Packages')
        save_dialog = GetFileSaveDialog(self.GetDebreateWindow(), GT(u'Build Package'),
                u'{} (*.deb)|*.deb'.format(ttype), u'deb')
        
        if ShowDialog(save_dialog):
            self.Build(save_dialog.GetPath())
    
    
    # FIXME: Deprecated, delete
    def OnBuildDeprecated(self, event):
        # Check to make sure that all required fields have values
        meta = self.debreate.page_control
        required = [meta.pack, meta.ver, meta.auth, meta.email]
        if self.debreate.page_menu.activate.GetValue():
            required.append(self.debreate.page_menu.name_input)
        cont = True
        
        for item in required:
            if item.GetValue() == wx.EmptyString:
                cont = False
        
        if cont:
            # Characters that should not be in filenames
            invalid_chars = (u' ', u'/')
            
            # Get information from control page for default filename
            pack_value = meta.pack.GetValue()
            pack_letters = pack_value.split()  # Remove whitespace
            pack = u'-'.join(pack_letters)  # Replace whitespace with "-"
            
            ver_value = meta.ver.GetValue()
            ver_digits = ver_value.split()  # Remove whitespace
            ver = u''.join(ver_digits)
            
            arch_index = meta.arch.GetCurrentSelection()
            arch = meta.arch_opt[arch_index]
            
            # If all required fields were met, continue to build
            def BuildIt(build_path, filename):
                temp_tree = u'%s/%s__dbp__' % (build_path, filename)
                
                deb = u'"%s/%s.deb"' % (build_path, filename) # Actual path to new .deb
                
                # *** Pre-build operations *** #
                
                tasks = 2 # 2 Represents preparing build tree and actual build of .deb
                progress = 0
                prebuild_progress = wx.ProgressDialog(GT(u'Preparing to build'), GT(u'Gathering control information'), 9,
                        self, wx.PD_AUTO_HIDE)
                
                try:
                    # Control & Depends (string)
                    wx.Yield()
                    control_data = self.debreate.page_control.GetCtrlInfo()
                    progress += 1
                    tasks += 1
                    prebuild_progress.Update(progress, GT(u'Checking files'))
                    
                    # Files (tuple)
                    wx.Yield()
                    files_data = self.debreate.page_files.GetPageInfo(True)#.GatherData().split(u'\n')[2:-1]
                    progress += 1
                    for file in files_data:
                        tasks += 1
                    prebuild_progress.Update(progress, GT(u'Checking scripts'))
                    
                    Logger.Debug(__name__, GT(u'Formatting files information ...'))
                    
                    if DebugEnabled():
                        print(files_data)
                        prebuild_progress.Destroy()
                        
                        return
                    
                    # Scripts (tuple)
                    wx.Yield()
                    scripts_data = self.debreate.page_scripts.GatherData()[1:-1]
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
                            create_script = True # Show that we are going to make the script
                        script = u'\n'.join(script[1:])
                        scripts.append((script_name, create_script, script))
                    
                    ###############################
                    ## *** RESERVED FOR DOCS *** ##
                    ###############################
                    
                    # *** Changelog
                    prebuild_progress.Update(progress, GT(u'Checking changelog'))
                    
                    wx.Yield()
                    #create_docs = False
                    #doc_data = self.debreate.page_docs.GatherData()
                    # Changelog (list)
                    changelog_data = self.debreate.page_clog.GatherData()
                    changelog_data = changelog_data.split(u'<<CHANGELOG>>\n')[1].split(u'\n<</CHANGELOG>>')[0].split(u'\n')
                    create_changelog = False
                    if self.debreate.page_clog.GetChangelog() != wx.EmptyString:
                        create_changelog = True
                    if create_changelog:
                        tasks += 1
                        changelog_dest = changelog_data[0].split(u'<<DEST>>')[1].split(u'<</DEST>>')[0]
                        changelog_data = u'\n'.join(changelog_data[1:])
                        
                    progress += 1
                    
                    # *** COPYRIGHT
                    prebuild_progress.Update(progress, GT(u'Checking copyright'))
                    
                    wx.Yield()
                    copyright = self.debreate.page_cpright.GetCopyright()
                    create_copyright = False
                    if copyright != wx.EmptyString:
                        create_copyright = True
                        tasks += 1
                    progress += 1
                    
                    # *** MENU (list)
                    prebuild_progress.Update(progress, GT(u'Checking menu launcher'))
                    
                    wx.Yield()
                    create_menu = self.debreate.page_menu.activate.GetValue()
                    if create_menu:
                        tasks += 1
                        menu_data = self.debreate.page_menu.GetMenuInfo().split(u'\n')
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
                    
                    delete_tree = self.chk_rmtree.GetValue()
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
                    
    #                try:
                    progress = 0
                    build_progress = wx.ProgressDialog(GT(u'Building'), GT(u'Preparing build tree'), tasks, self,
                            wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_AUTO_HIDE)#|wx.PD_CAN_ABORT)
                    
                    wx.Yield()
                    if os.path.isdir(u'%s/DEBIAN' % (temp_tree)):
                        c = u'rm -r "%s"' % (temp_tree)
                        if commands.getstatusoutput(c.encode(u'utf-8'))[0]:
                            wx.MessageDialog(self, GT(u'An Error Occurred:\nCould not delete "%s"') % (temp_tree), GT(u'Can\'t Continue'), style=wx.OK|wx.ICON_ERROR).ShowModal()
                    # Make a fresh build tree
                    os.makedirs(u'%s/DEBIAN' % (temp_tree))
                    progress += 1
                    
                    # *** FILES
                    build_progress.Update(progress, GT(u'Copying files'))
                    
                    wx.Yield()
                    for file in files_data:
                        # Create new directories
                        new_dir = u'{}{}'.format(temp_tree, file.split(u' -> ')[2])
                        if not os.path.isdir(new_dir):
                            os.makedirs(new_dir)
                        # Get file path
                        file = file.split(u' -> ')[0]
                        # Remove asteriks from exectuables
                        exe = False # Used to set executable permissions
                        if file[-1] == u'*':
                            exe = True
                            file = file[:-1]
                        # Copy files
                        copy_path = u'%s/%s' % (new_dir, os.path.split(file)[1])
                        shutil.copy(file, copy_path)
                        # Set file permissions
                        if exe:
                            c = u'chmod 0755 %s' % (copy_path)
                            commands.getoutput(c.encode(u'utf-8'))
                        else:
                            c = u'chmod 0644 %s' % (copy_path)
                            commands.getoutput(c.encode(u'utf-8'))
                        progress += 1
                        build_progress.Update(progress)
                    #progress += 1
                    
                    # Make sure that the dirctory is available in which to place documentation
                    if create_changelog or create_copyright:
                        doc_dir = u'%s/usr/share/doc/%s' % (temp_tree, pack)
                        if not os.path.isdir(doc_dir):
                            os.makedirs(doc_dir)
                    
                    # *** CHANGELOG
                    if create_changelog:
                        build_progress.Update(progress, GT(u'Creating changelog'))
                        
                        wx.Yield()
                        # If changelog will be installed to default directory
                        if changelog_dest == u'DEFAULT':
                            changelog_dest = u'%s/usr/share/doc/%s' % (temp_tree, pack)
                        else:
                            changelog_dest = u'{}{}'.format(temp_tree, changelog_dest)
                        if not os.path.isdir(changelog_dest):
                            os.makedirs(changelog_dest)
                        changelog_file = open(u'%s/changelog' % (changelog_dest), u'w')
                        changelog_file.write(changelog_data.encode(u'utf-8'))
                        changelog_file.close()
                        c = u'gzip --best "%s/changelog"' % (changelog_dest)
                        clog_status = commands.getstatusoutput(c.encode(u'utf-8'))
                        if clog_status[0]:
                            clog_error = GT(u'Couldn\'t create changelog')
                            changelog_error = wx.MessageDialog(self, u'%s\n\n%s' % (clog_error, clog_status[1]),
                                    GT(u'Error'), wx.OK)
                            changelog_error.ShowModal()
                        progress += 1
                    
                    # *** COPYRIGHT
                    if create_copyright:
                        build_progress.Update(progress, GT(u'Creating copyright'))
                        
                        wx.Yield()
                        cp_file = open(u'%s/usr/share/doc/%s/copyright' % (temp_tree, pack), u'w')
                        cp_file.write(copyright.encode(u'utf-8'))
                        cp_file.close()
                        progress += 1
                    
                    # *** MENU
                    if create_menu:
                        build_progress.Update(progress, GT(u'Creating menu launcher'))
                        
                        wx.Yield()
                        #if menu_data[0]:
                        # This may be changed later to set a custom directory
                        menu_dir = u'%s/usr/share/applications' % (temp_tree)
                        for field in menu_data:
                            if field.split(u'=')[0] == u'Name':
                                menu_filename = u'='.join(field.split(u'=')[1:])
                        
                        # Remove invalid characters from filename
                        for char in invalid_chars:
                            menu_filename = u'_'.join(menu_filename.split(char)) # Replace invalid char with "underscore"
                        if not os.path.isdir(menu_dir):
                            os.makedirs(menu_dir)
                        menu_file = open(u'%s/%s.desktop' % (menu_dir, menu_filename), u'w')
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
                    installed_size = os.popen((u'du -hsk "%s"' % (temp_tree)).encode(u'utf-8')).readlines()
                    installed_size = installed_size[0].split(u'\t')
                    installed_size = installed_size[0]
                    # Insert Installed-Size into control file
                    control_data = control_data.split(u'\n')
                    control_data.insert(2, u'Installed-Size: %s' % (installed_size))
                    # dpkg fails if there is no newline at end of file
                    control_data.append(u'\n')
                    control_data = u'\n'.join(control_data)
                    control_file = open(u'%s/DEBIAN/control' % (temp_tree), u'w')
                    control_file.write(control_data.encode(u'utf-8'))
                    control_file.close()
                    progress += 1
                    
                    # *** SCRIPTS
                    build_progress.Update(progress, GT(u'Creating scripts'))
                    
                    wx.Yield()
                    for script in scripts:
                        if script[1]:
                            script_file = open(u'%s/DEBIAN/%s' % (temp_tree, script[0]), u'w')
                            script_file.write(script[2].encode(u'utf-8'))
                            script_file.close()
                            # Make sure scipt path is wrapped in quotes to avoid whitespace errors
                            os.system((u'chmod +x "%s/DEBIAN/%s"' % (temp_tree, script[0])).encode(u'utf-8'))
                            progress += 1
                            build_progress.Update(progress)
                    
                    # *** FINAL BUILD
                    build_progress.Update(progress, GT(u'Running dpkg'))[0]
    #                c_tree = temp_tree.encode(u'utf-8')
    #                print c_tree
    #                c_deb = deb.encode(u'utf-8')
    #                print c_deb
                    working_dir = os.path.split(temp_tree)[0]
                    c_tree = os.path.split(temp_tree)[1]
                    c_deb = u'%s.deb' % filename
                    
                    # Move the working directory becuase dpkg seems to have problems with spaces in path
                    os.chdir(working_dir)
                                
                    wx.Yield()
    #                if subprocess.call(['fakeroot', 'dpkg', '-b', c_tree, c_deb]):
    #                    build_status = (1, 0)
    #                try:
                    build_status = commands.getstatusoutput((u'fakeroot dpkg-deb -b "%s" "%s"' % (c_tree, c_deb)).encode(u'utf-8'))
                    progress += 1
                    
                    # *** DELETE BUILD TREE
                    if delete_tree:
                        build_progress.Update(progress, GT(u'Removing temp directory'))
                        
                        # Don't delete build tree if build failed
                        if not build_status[0]:
                            wx.Yield()
                            # Delete the build tree
                            if commands.getstatusoutput((u'rm -r "%s"' % temp_tree).encode(u'utf-8'))[0]:
                                wx.MessageDialog(self, GT(u'An error occurred when trying to delete the build tree'),
                                    _(u'Error'), style=wx.OK|wx.ICON_EXCLAMATION).ShowModal()
                        progress += 1
                    
                    # *** ERROR CHECK
                    if error_check:
                        build_progress.Update(progress, GT(u'Checking package for errors'))
                        wx.Yield()
                        
                        errors = commands.getoutput((u'lintian %s' % deb).encode(u'utf-8'))
                        e1 = GT(u'Lintian found some issues with the package.')
                        e2 = GT(u'Details saved to %s')
                        e2 = e2 % (filename)
                        if errors.decode(u'utf-8') != wx.EmptyString:
                            error_log = open(u'%s/%s.lintian' % (build_path, filename), u'w')
                            error_log.write(errors)
                            error_log.close()
                            DetailedMessageDialog(self, GT(u'Lintian Errors'), ICON_INFORMATION,
                            u'%s\n%s.lintian"' % (e1, e2),
                            errors
                            ).ShowModal()
                        progress += 1
                    
                    # Close progress dialog
                    build_progress.Update(progress)
                    
                    if build_status[0]:
                        ErrorDialog(self, GT(u'Package build failed'), build_status[1]).ShowModal()
                    else:
                        wx.MessageDialog(self, GT(u'Package created successfully'), GT(u'Success'),
                                style=wx.OK|wx.ICON_INFORMATION).ShowModal()
                        
                        # Installing the package
                        if self.chk_install.GetValue():
                            self.log.ToggleOutput()
                            print GT(u'Getting administrative privileges from user')
                            pshow = GT(u'Password')
                            command_executed = False
                            tries = 0
                            while (tries < 3):
                                password = wx.GetPasswordFromUser(pshow, GT(u'Installing Package'))
                                if (password == u''):
                                    print GT(u'Empty password: Cancelling')
                                    break
                                e = dbr.RunSudo(password, u'dpkg -i %s' % (deb))
                                if (not e):
                                    if (tries == 2):
                                        print GT(u'Authentication failure')
                                        install_fail = GT(u'Could not install %s')
                                        print install_fail % (deb)
                                    else:
                                        print GT(u'Password mismatch, try again')
                                else:
                                    command_executed = True
                                    print GT(u'Authenticated')
                                    break
                                tries += 1
                            
                            # Check if package installed correctly
                            if (int(os.popen(u'dpkg -L %s ; echo $?' % (pack)).read().split(u'\n')[-2]) and command_executed):
                                wx.MessageDialog(self, GT(u'The package failed to install'), GT(u'Error'), wx.OK|wx.ICON_ERROR).ShowModal()
                            elif (command_executed):
                                wx.MessageDialog(self, GT(u'The package installed successfully'), GT(u'Sucess'), wx.OK).ShowModal()
                            self.log.ToggleOutput()
                    
                    return build_status[0]
                
                except:
                    prebuild_progress.Destroy()
                    
                    err_traceback = traceback.format_exc()
                    #print(u'Printing traceback: {}'.format(test))
                    
                    err_title = GT(u'Error occured during pre-build')
                    Logger.Error(__name__, u'{}:\n{}'.format(err_title, err_traceback))
                    
                    err_dialog = ErrorDialog(self, err_title)
                    err_dialog.SetDetails(err_traceback)
                    err_dialog.ShowModal()
                    
                    # Cleanup
                    err_dialog.Destroy()
                    del err_title
            
            
            cont = False
            
            # Dialog for save destination
            ttype = GT(u'Debian Packages')
            save_dia = GetFileSaveDialog(self.GetDebreateWindow(), GT(u'Save'), u'{}|*.deb'.format(ttype))
            save_dia.SetFilename(u'%s_%s_%s.deb' % (pack, ver, arch))
            if ShowDialog(save_dia):
                cont = True
                path = os.path.split(save_dia.GetPath())[0]
                filename = os.path.split(save_dia.GetPath())[1].split(u'.deb')[0]
            
            if cont:
                for char in invalid_chars:
                    filename = u'_'.join(filename.split(char))
                BuildIt(path, filename)
        
        else:
            # If continue returned False, show an error dialog
            err = wx.MessageDialog(self, GT(u'One of the required fields is empty'), GT(u'Can\'t Continue'),
                    wx.OK|wx.ICON_WARNING)
            err.ShowModal()
            err.Destroy()
    
    def ResetAllFields(self):
        self.chk_install.SetValue(False)
        # chk_md5 should be reset no matter
        self.chk_md5.SetValue(False)
        # FIXME: Should use a more universal method to check for executables
        if os.path.exists(u'/usr/bin/md5sum'):
            self.chk_md5.Enable()
        else:
            self.chk_md5.Disable()
        self.chk_rmtree.SetValue(True)
        # FIXME: Should use a more universal method to check for executables
        if os.path.exists(u'/usr/bin/lintian'):
            self.chk_lint.Enable()
            self.chk_lint.SetValue(True)
        else:
            self.chk_lint.Disable()
            self.chk_lint.SetValue(False)
    
    def SetFieldData(self, data):
        self.ResetAllFields()
        build_data = data.split(u'\n')
        # FIXME: Should use a more universal method to check for executables
        if os.path.exists(u'/usr/bin/md5sum'):
            self.chk_md5.SetValue(int(build_data[0]))
        self.chk_rmtree.SetValue(int(build_data[1]))
        # FIXME: Should use a more universal method to check for executables
        if os.path.exists(u'usr/bin/lintian'):
            self.chk_lint.SetValue(int(build_data[2]))
    
    def GatherData(self):
        build_list = []
        
        if self.chk_md5.GetValue(): build_list.append(u'1')
        else: build_list.append(u'0')
        if self.chk_rmtree.GetValue(): build_list.append(u'1')
        else: build_list.append(u'0')
        if self.chk_lint.GetValue(): build_list.append(u'1')
        else: build_list.append(u'0')
        return u'<<BUILD>>\n%s\n<</BUILD>>' % u'\n'.join(build_list)
    
    
    def GetPageInfo(self):
        # 'install after build' is not exported to project for safety
        
        fields = {}
        omit_options = (
            self.chk_install,
        )
        
        for O in self.build_options:
            # Leave options out that should not be saved
            if O not in omit_options:
                fields[O.GetName()] = unicode(O.GetValue())
        
        page_info = wx.EmptyString
        
        for F in fields:
            if page_info == wx.EmptyString:
                page_info = u'{}={}'.format(F, fields[F])
            else:
                page_info = u'{}\n{}={}'.format(page_info, F, fields[F])
        
        if page_info == wx.EmptyString:
            return None
        
        return (__name__, page_info)
    
    
    def ImportPageInfo(self, filename):
        if not os.path.isfile(filename):
            return errno.ENOENT
        
        FILE = open(filename, u'r')
        build_data = FILE.read().split(u'\n')
        FILE.close()
        
        options_definitions = {}
        
        for L in build_data:
            if u'=' in L:
                key = L.split(u'=')
                value = GetBoolean(key[-1])
                key = key[0]
                
                options_definitions[key] = value
        
        for O in self.build_options:
            name = O.GetName()
            if name in options_definitions and isinstance(options_definitions[name], bool):
                O.SetValue(options_definitions[name])
        
        return 0
    
    
    def ResetPageInfo(self):
        for O in self.build_options:
            O.SetValue(O.default)


##########################################
## *** BUIDING FROM PREEXISTING FILE SYSTEM TREE **  ##
##########################################

class QuickBuild(wx.Dialog):
    def __init__(self, parent, id=-1, title=GT(u'Quick Build')):
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, (400,200))
        
        self.parent = parent # allows calling parent events
        
        # Set icon
#        rpmicon = wx.Icon("%s/bitmaps/rpm16.png" % application_path, wx.BITMAP_TYPE_PNG)
#        self.SetIcon(rpmicon)
        
        filename_txt = wx.StaticText(self, -1, GT(u'Name'))
        self.filename = wx.TextCtrl(self, -1)
        path_txt = wx.StaticText(self, -1, GT(u'Path to build tree'))
        self.path = wx.TextCtrl(self, -1) # Path to the root of the directory tree
        self.get_path = dbr.ButtonBrowse(self)
        self.build = dbr.ButtonBuild(self)
        self.build.SetToolTip(wx.ToolTip(GT(u'Start building')))
        self.cancel = dbr.ButtonCancel(self)
        
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
        
        # Debugging build
        self.build_error = (0, u'"QuickBuild.build_error" still in initial state')
        
        # DEBUG:
        self.filename.SetValue(u'blah')
        self.path.SetValue(u'/media/jordan/External/Development/Debreate/test-app/build/dummy-package_0.1_all__dbp__')
    
    
    def Browse(self, event):
        if False: #self.parent.cust_dias.IsChecked():
            dia = dbr.OpenDir(self)
            if dia.DisplayModal() == True:
                self.path.SetValue(dia.GetPath())
        else:
            dia = wx.DirDialog(self, GT(u'Choose Directory'), os.getcwd(), wx.CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                self.path.SetValue(dia.GetPath())
        dia.Destroy()
    
    def ShowProgress(self, event):
        self.gauge.Pulse()
    
    def Build(self, path, arg2):
        root = path[1]
        work_dir = path[0]
        filename = path[2]
        os.chdir(work_dir)
        self.build_error = commands.getstatusoutput((u'fakeroot dpkg-deb -b "{}" "{}.deb"'.format(root, filename)).encode(u'utf-8'))
        self.timer.Stop()
        self.gauge.SetValue(100)
        self.Enable()
    
    def OnBuild(self, event):
        path = self.path.GetValue()
        root = os.path.split(path)[1]
        work_dir = os.path.split(path)[0]
        filename = self.filename.GetValue()
        if u''.join(filename.split(u' ')) == u'':
            filename = root
        if filename.split(u'.')[-1] == u'deb':
            filename = u'.'.join(filename.split(u'.')[:-1])
        
        if os.path.isdir(path):
            # Disable the window so it can't be closed while working
            self.Disable()
            thread.start_new_thread(self.Build, ((root, work_dir, filename), None))
            self.timer.Start(100)
        else:
            e = GT(u'Could not locate \"%s\"')
            e = e % (path)
            wx.MessageDialog(self, e, GT(u'Error'), wx.OK|wx.ICON_ERROR).ShowModal()
            return
        
        if not os.path.isfile(u'{}/{}.deb'.format(work_dir, filename)):
            self.build_error = (1, GT(u'An unknown error has occurred'))
            return
        
        error = self.build_error[0]
        error_output = self.build_error[1]
        
        if error:
            DetailedMessageDialog(self, GT(u'Error'), ICON_ERROR, GT(u'Package build failed'),
                    error_output).ShowModal()
        
        else:
            wx.MessageDialog(self, GT(u'Package created successfully'), GT(u'Success'),
                    style=wx.OK|wx.ICON_INFORMATION).ShowModal()
            
    
    def OnQuit(self, event):
        self.Close()
        event.Skip()
