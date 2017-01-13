# -*- coding: utf-8 -*-

## \package wiz_bin.build

# MIT licensing
# See: docs/LICENSE.txt


import commands, math, os, subprocess, time, traceback, wx

from dbr.buttons            import ButtonBuild64
from dbr.checklist          import CheckListDialog
from dbr.custom             import OutputLog
from dbr.dialogs            import DetailedMessageDialog
from dbr.dialogs            import ErrorDialog
from dbr.dialogs            import GetFileSaveDialog
from dbr.dialogs            import ShowDialog
from dbr.functions          import CreateTempDirectory
from dbr.functions          import GetBoolean
from dbr.functions          import RemoveTempDirectory
from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from dbr.wizard             import WizardPage
from globals                import ident
from globals.application    import AUTHOR_email
from globals.bitmaps        import ICON_INFORMATION
from globals.errorcodes     import dbrerrno
from globals.execute        import GetExecutable
from globals.execute        import GetSystemInstaller
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.paths          import ConcatPaths
from globals.paths          import PATH_app
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetPage
from globals.wizardhelper   import GetTopWindow


## TODO: Doxygen
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.BUILD)
        
        # Bypass build prep check
        self.prebuild_check = False
        
        # Add checkable items to this list
        self.build_options = []
        
        # ----- Extra Options
        self.chk_md5 = wx.CheckBox(self, label=GT(u'Create md5sums file'))
        # The » character denotes that an alternate tooltip should be shown if the control is disabled
        self.chk_md5.tt_name = u'md5»'
        self.chk_md5.SetName(u'MD5')
        self.chk_md5.default = False
        
        if not GetExecutable(u'md5sum'):
            self.chk_md5.Disable()
        
        else:
            self.build_options.append(self.chk_md5)
        
        # Option to strip binaries
        self.chk_strip = wx.CheckBox(self, label=GT(u'Strip binaries'), name=u'strip»')
        self.chk_strip.default = True
        
        # Deletes the temporary build tree
        self.chk_rmtree = wx.CheckBox(self, label=GT(u'Delete stage directory'))
        self.chk_rmtree.SetName(u'RMSTAGE')
        self.chk_rmtree.default = True
        self.chk_rmtree.SetValue(self.chk_rmtree.default)
        self.build_options.append(self.chk_rmtree)
        
        # Checks the output .deb for errors
        self.chk_lint = wx.CheckBox(self, label=GT(u'Check package for errors with lintian'))
        self.chk_lint.tt_name = u'lintian»'
        self.chk_lint.SetName(u'LINTIAN')
        self.chk_lint.default = True
        
        if not GetExecutable(u'lintian'):
            self.chk_lint.Disable()
        
        else:
            self.chk_lint.SetValue(self.chk_lint.default)
            self.build_options.append(self.chk_lint)
        
        # Installs the deb on the system
        self.chk_install = wx.CheckBox(self, label=GT(u'Install package after build'))
        self.chk_install.tt_name = u'install»'
        self.chk_install.SetName(u'INSTALL')
        self.chk_install.default = False
        
        if not GetSystemInstaller():
            self.chk_install.Disable()
        
        else:
            self.build_options.append(self.chk_install)
        
        options1_border = wx.StaticBox(self, label=GT(u'Extra options')) # Nice border for the options
        options1_sizer = wx.StaticBoxSizer(options1_border, wx.VERTICAL)
        options1_sizer.AddMany( [
            (self.chk_md5, 0),
            (self.chk_strip, 0),
            (self.chk_rmtree, 0),
            (self.chk_lint, 0),
            (self.chk_install, 0)
            ] )
        
        # *** Lintian Overrides *** #
        
        if DebugEnabled():
            # FIXME: Move next to lintian check box
            self.lint_overrides = []
            btn_lint_overrides = wx.Button(self, label=GT(u'Lintian overrides'))
            btn_lint_overrides.Bind(wx.EVT_BUTTON, self.OnSetLintOverrides)
        
        # --- BUILD
        self.build_button = ButtonBuild64(self)
        self.build_button.SetName(u'build')
        
        self.build_button.Bind(wx.EVT_BUTTON, self.OnBuild)
        
        build_sizer = wx.BoxSizer(wx.HORIZONTAL)
        build_sizer.Add(self.build_button, 1)
        
        # --- Display log
        self.log = OutputLog(self)
        
        # --- Page 7 Sizer --- #
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(options1_sizer, 0, wx.LEFT, 5)
        lyt_main.AddSpacer(5)
        
        if DebugEnabled():
            #lyt_main.Add(wx.StaticText(self, label=GT(u'Lintian overrides')), 0, wx.LEFT, 5)
            lyt_main.Add(btn_lint_overrides, 0, wx.LEFT, 5)
        
        lyt_main.AddSpacer(5)
        lyt_main.Add(build_sizer, 0, wx.ALIGN_CENTER)
        lyt_main.Add(self.log, 2, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        
        SetPageToolTips(self)
    
    
    ## Method that builds the actual Debian package
    #  
    #  TODO: Test for errors when building deb package with other filename extension
    #  TODO: Remove deprecated methods that this one replaces
    #  \param out_file
    #        \b \e str|unicode : Absolute path to target file
    def Build(self, out_file):
        def log_message(msg, current_step, total_steps):
            return u'{} ({}/{})'.format(msg, current_step, total_steps)
        
        wizard = self.GetWizard()
        pages_build_ids = self.BuildPrep()
        
        if pages_build_ids != None:
            main_window = GetTopWindow()
            
            # Reported at the end of build
            build_summary = []
            
            steps_count = len(pages_build_ids)
            current_step = 0
            
            # Steps from build page
            for chk in self.chk_md5, self.chk_lint, self.chk_rmtree:
                if chk.IsChecked():
                    steps_count += 1
            
            # Control file & .deb build step
            steps_count += 2
            
            stage = CreateTempDirectory()
            
            log_msg = GT(u'Starting build')
            
            wx.YieldIfNeeded()
            # FIXME: Enable PD_CAN_ABORT
            build_progress = wx.ProgressDialog(GT(u'Building'), log_msg,
                    steps_count, main_window, wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
            
            build_summary.append(u'{}:'.format(log_msg))
            
            try:
                for P in wizard.pages:
                    if build_progress.WasCancelled():
                        break
                    
                    if P.GetId() in pages_build_ids:
                        p_label = P.GetLabel()
                        
                        log_msg = log_message(
                            GT(u'Processing page "{}"').format(p_label), current_step+1, steps_count)
                        
                        # FIXME: Progress bar not updating???
                        wx.YieldIfNeeded()
                        build_progress.Update(current_step, log_msg)
                        
                        ret_code, ret_value = P.ExportBuild(stage)
                        
                        build_summary.append(u'\n{}:\n{}'.format(log_msg, ret_value))
                        
                        if ret_code > 0:
                            build_progress.Destroy()
                            
                            err_msg = GT(u'Error occurred during build')
                            Logger.Error(__name__, u'\n{}:\n{}'.format(err_msg, ret_value))
                            
                            err_dialog = ErrorDialog(main_window, GT(u'Error occured during build'))
                            err_dialog.SetDetails(ret_value)
                            err_dialog.ShowModal()
                            
                            err_dialog.Destroy()
                            
                            return
                        
                        current_step += 1
                
                # *** Control File *** #
                if not build_progress.WasCancelled():
                    wx.YieldIfNeeded()
                    
                    log_msg = log_message(GT(u'Creating control file'), current_step+1, steps_count)
                    build_progress.Update(current_step, log_msg)
                    
                    Logger.Debug(__name__, log_msg)
                    
                    # Retrieve control page
                    pg_control = wizard.GetPage(ident.CONTROL)
                    if not pg_control:
                        Logger.Error(__name__, GT(u'Could not retrieve control page'))
                        build_progress.Destroy()
                        err_msg = ErrorDialog(main_window, GT(u'Fatal Error'),
                                GT(u'Could not retrieve control page'))
                        err_msg.SetDetails(GT(u'Please contact the developer: {}').format(AUTHOR_email))
                        err_msg.ShowModal()
                        
                        return
                    
                    installed_size = self.OnBuildGetInstallSize(stage)
                    
                    Logger.Debug(__name__, GT(u'Installed size: {}').format(installed_size))
                    
                    build_summary.append(u'\n{}:'.format(log_msg))
                    build_summary.append(
                        pg_control.ExportBuild(u'{}/DEBIAN'.format(stage).replace(u'//', u'/'), installed_size)
                        )
                    
                    current_step += 1
                
                # *** MD5 Checksum *** #
                if not build_progress.WasCancelled():
                    if self.chk_md5.IsChecked():
                        log_msg = log_message(GT(u'Creating MD5 checksum'), current_step+1, steps_count)
                        #log_msg = GT(u'Creating MD5 checksum')
                        #step = u'{}/{}'.format(current_step+1, steps_count)
                        
                        Logger.Debug(__name__, log_msg)
                        
                        wx.YieldIfNeeded()
                        build_progress.Update(current_step, log_msg)
                        
                        build_summary.append(u'\n{}:'.format(log_msg))
                        build_summary.append(self.OnBuildMD5Sum(stage))
                        
                        current_step += 1
                
                # *** Create .deb from Stage *** #
                if not build_progress.WasCancelled():
                    log_msg = log_message(GT(u'Creating .deb package'), current_step+1, steps_count)
                    
                    wx.YieldIfNeeded()
                    build_progress.Update(current_step, log_msg)
                    
                    build_summary.append(u'\n{}:'.format(log_msg))
                    build_summary.append(self.OnBuildCreatePackage(stage, out_file))
                    
                    current_step += 1
                
                # *** Lintian *** #
                if not build_progress.WasCancelled():
                    if self.chk_lint.IsChecked():
                        log_msg = log_message(GT(u'Checking package with lintian'), current_step+1, steps_count)
                        
                        wx.YieldIfNeeded()
                        build_progress.Update(current_step, log_msg)
                        
                        build_summary.append(u'\n{}:'.format(log_msg))
                        build_summary.append(self.OnBuildCheckPackage(out_file))
                        
                        current_step += 1
                
                # *** Delete Stage *** #
                if not build_progress.WasCancelled():
                    if self.chk_rmtree.IsChecked():
                        log_msg = log_message(GT(u'Removing staged build tree'), current_step+1, steps_count)
                        
                        wx.YieldIfNeeded()
                        build_progress.Update(current_step, log_msg)
                        
                        build_summary.append(u'\n{}:'.format(log_msg))
                        RemoveTempDirectory(stage)
                        
                        if not os.path.isdir(stage):
                            build_summary.append(GT(u'Staged build tree removed successfully'))
                        
                        else:
                            build_summary.append(GT(u'Failed to remove staged build tree'))
                        
                        current_step += 1
                
                # *** Show Completion Status *** #
                wx.YieldIfNeeded()
                build_progress.Update(steps_count, GT(u'Build completed'))
                
                # Show finished dialog for short moment
                time.sleep(1)
                
                # TODO: Add error count to build summary
                
                build_progress.Destroy()
                
                build_summary = u'\n'.join(build_summary)
                summary_dialog = DetailedMessageDialog(main_window, GT(u'Build Summary'),
                        ICON_INFORMATION, GT(u'Build completed'), build_summary)
                summary_dialog.ShowModal()
            
            except:
                build_progress.Destroy()
                
                err_msg = GT(u'Error occurred during build')
                Logger.Error(__name__, u'{}:\n{}'.format(err_msg, traceback.format_exc()))
                
                err_dialog = ErrorDialog(main_window, GT(u'Error occured during build'))
                err_dialog.SetDetails(traceback.format_exc())
                err_dialog.ShowModal()
                
                err_dialog.Destroy()
        
        return
    
    
    ## TODO: Doxygen
    #  
    #  \return
    #        \b \e tuple containing data & label for each page
    def BuildPrep(self):
        wizard = self.GetWizard()
        prep_ids = []
        
        for P in wizard.pages:
            if P.prebuild_check:
                Logger.Debug(__name__, GT(u'Pre-build check for page "{}"'.format(P.GetName())))
                prep_ids.append(P.GetId())
        
        try:
            main_window = GetTopWindow()
            
            # List of page IDs to process during build
            pg_build_ids = []
            
            steps_count = len(prep_ids)
            current_step = 0
            
            msg_label1 = GT(u'Prepping page "{}"')
            msg_label2 = GT(u'Step {}/{}')
            msg_label = u'{} ({})'.format(msg_label1, msg_label2)
            
            prep_progress = wx.ProgressDialog(GT(u'Preparing Build'), msg_label2.format(current_step, steps_count),
                    steps_count, main_window, wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
            
            for P in wizard.pages:
                if prep_progress.WasCancelled():
                    break
                
                p_id = P.GetId()
                p_label = P.GetLabel()
                
                if p_id in prep_ids:
                    Logger.Debug(__name__, msg_label.format(p_label, current_step+1, steps_count))
                    
                    wx.Yield()
                    prep_progress.Update(current_step, msg_label.format(p_label, current_step+1, steps_count))
                    
                    if P.IsExportable():
                        pg_build_ids.append(p_id)
                    
                    current_step += 1
            
            if not prep_progress.WasCancelled():
                wx.Yield()
                prep_progress.Update(current_step, GT(u'Prepping finished'))
                
                # Show finished dialog for short period
                time.sleep(1)
            
            prep_progress.Destroy()
            
            return pg_build_ids
        
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
    
    
    ## TODO: Doxygen
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
        
        p_info = wx.EmptyString
        
        for F in fields:
            if p_info == wx.EmptyString:
                p_info = u'{}={}'.format(F, fields[F])
            
            else:
                p_info = u'{}\n{}={}'.format(p_info, F, fields[F])
        
        if p_info == wx.EmptyString:
            return None
        
        return (__name__, p_info)
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, filename):
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        build_data = ReadFile(filename, split=True)
        
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
    
    
    ## TODO: Doxygen
    def OnBuild(self, event=None):
        if event:
            event.Skip()
        
        wizard = self.GetWizard()
        
        pg_control = wizard.GetPage(ident.CONTROL)
        pg_files = wizard.GetPage(ident.FILES)
        pg_launcher = wizard.GetPage(ident.MENU)
        
        required_fields = {
            GT(u'Control'): pg_control.GetRequiredFields(),
        }
        
        if pg_launcher.chk_enable.GetValue():
            required_fields[GT(u'Menu Launcher')] = pg_launcher.GetRequiredFields()
            
            for RF in required_fields[GT(u'Menu Launcher')]:
                Logger.Debug(__name__, GT(u'Required field (Menu Launcher): {}').format(RF.GetName()))
        
        for p_name in required_fields:
            Logger.Debug(__name__, GT(u'Page name: {}').format(p_name))
            for F in required_fields[p_name]:
                if not isinstance(F, wx.StaticText) and TextIsEmpty(F.GetValue()):
                    f_name = F.GetName()
                    
                    Logger.Warning(__name__,
                            u'{}: {} ➜ {}'.format(GT(u'A required field is empty'), p_name, f_name))
                    
                    err_dialog = wx.MessageDialog(GetTopWindow(), GT(u'A required field is empty'),
                            GT(u'Error'), style=wx.OK|wx.ICON_ERROR)
                    err_dialog.SetExtendedMessage(u'{} ➜ {}'.format(p_name, f_name))
                    err_dialog.ShowModal()
                    
                    for P in wizard.pages:
                        if P.GetLabel() == p_name:
                            Logger.Debug(__name__, GT(u'Showing page with required field: {}').format(p_name))
                            wizard.ShowPage(P.GetId())
                    
                    return
        
        if pg_files.file_list.MissingFiles():
            main_window = GetTopWindow()
            
            Logger.Warning(__name__, GT(u'Files are missing in file list'))
            
            err_dialog = ErrorDialog(main_window, GT(u'Warning'), GT(u'Files are missing in file list'))
            err_dialog.ShowModal()
            
            err_dialog.Destroy()
            
            wizard.ShowPage(ident.FILES)
            
            return
        
        
        ttype = GT(u'Debian Packages')
        save_dialog = GetFileSaveDialog(main_window, GT(u'Build Package'),
                u'{} (*.deb)|*.deb'.format(ttype), u'deb')
        
        package = pg_control.ti_package.GetValue()
        version = pg_control.ti_version.GetValue()
        arch = pg_control.sel_arch.GetStringSelection()
        save_dialog.SetFilename(u'{}_{}_{}.deb'.format(package, version, arch))
        
        if ShowDialog(save_dialog):
            self.Build(save_dialog.GetPath())
    
    
    ## TODO: Doxygen
    def OnBuildCheckPackage(self, target_package):
        Logger.Debug(__name__,
                GT(u'Checking package "{}" for lintian errors ...').format(os.path.basename(target_package)))
        
        # FIXME: commands module deprecated?
        output = commands.getoutput(u'{} "{}"'.format(GetExecutable(u'lintian'), target_package))
        
        return output
    
    
    ## TODO: Doxygen
    def OnBuildCreatePackage(self, stage, target_file):
        Logger.Debug(__name__, GT(u'Creating {} from {}').format(target_file, stage))
        
        packager = GetExecutable(u'dpkg-deb')
        fakeroot = GetExecutable(u'fakeroot')
        
        if not fakeroot or not packager:
            return (dbrerrno.ENOENT, GT(u'Cannot run "fakeroot dpkg'))
        
        packager = os.path.basename(packager)
        
        Logger.Debug(__name__, GT(u'System packager: {}').format(packager))
        
        # DEBUG:
        cmd = u'{} {} -b "{}" "{}"'.format(fakeroot, packager, stage, target_file)
        Logger.Debug(__name__, GT(u'Executing: {}').format(cmd))
        
        output = subprocess.check_output([fakeroot, packager, u'-b', stage, target_file], stderr=subprocess.STDOUT)
        
        Logger.Debug(__name__, GT(u'Build output: {}').format(output))
        
        return output
    
    
    ## Retrieves total size of directory contents
    #  
    #  TODO: Move this method to control page
    #  
    #  \param stage
    #        \b \e unicode|str : Directory to scan
    #  \return
    #        \b \e int : Integer representing installed size
    def OnBuildGetInstallSize(self, stage):
        Logger.Debug(__name__, GT(u'Retrieving installed size for {}').format(stage))
        
        installed_size = 0
        for ROOT, DIRS, FILES in os.walk(stage):
            for F in FILES:
                if ROOT != u'{}/DEBIAN'.format(stage).replace(u'//', u'/'):
                    F = u'{}/{}'.format(ROOT, F).replace(u'//', u'/')
                    installed_size += os.stat(F).st_size
            
        # Convert to kilobytes & round up
        if installed_size:
            installed_size = int(math.ceil(float(installed_size) / float(1024)))
        
        return installed_size
    
    
    ## TODO: Doxygen
    # 
    # FIXME: Hashes for .png images (binary files???) is not the same as those
    #        produced by debuild
    # TODO:  Create global md5 function???
    def OnBuildMD5Sum(self, target_dir):
        Logger.Debug(__name__,
                GT(u'Creating MD5sum file in {}').format(target_dir))
        
        md5_list = []
        #md5hash_size = 32
        debian_dir = u'{}/DEBIAN'.format(target_dir).replace(u'//', u'/')
        text_formats = (u'text', u'script',)
        
        for ROOT, DIRS, FILES in os.walk(target_dir):
            for F in FILES:
                if ROOT != debian_dir:
                    F = ConcatPaths((ROOT, F,))
                    Logger.Debug(__name__, GT(u'Retrieving md5 for {}').format(F))
                    
                    read_format = u't'
                    '''
                    # Read binary by default
                    read_format = u'b'
                    for T in text_formats:
                        if T in GetFileMimeType(F):
                            read_format = u't'
                            break
                    '''
                    
                    md5 = commands.getoutput(u'{} -{} "{}"'.format(GetExecutable(u'md5sum'), read_format, F))
                    
                    # Need to remove stage dir from file path
                    md5 = md5.replace(u'{}/'.format(target_dir), u'')
                    md5_list.append(md5)
        
        if not md5_list:
            return GT(u'Could not create md5sums')
        
        if not os.path.isdir(debian_dir):
            os.makedirs(debian_dir)
        
        md5_file = ConcatPaths((debian_dir, u'md5sums'))
        
        WriteFile(md5_file, md5_list)
        
        return GT(u'md5sums created: {}').format(md5_file)
    
    
    ## TODO: Doxygen
    def OnSetLintOverrides(self, event=None):
        Logger.Debug(__name__, GT(u'Setting Lintian overrides...'))
        
        lintian_tags_file = u'{}/data/lintian/tags'.format(PATH_app)
        
        if os.path.isfile(lintian_tags_file):
            lint_lines = ReadFile(lintian_tags_file, split=True)
            
            lint_tags = []
            for L in lint_lines:
                if not TextIsEmpty(L):
                    lint_tags.append(L)
            
            if lint_tags:
                # Create the dialog
                overrides_dialog = CheckListDialog(self, title=GT(u'Lintian Overrides'),
                        allow_custom=True)
                overrides_dialog.InitCheckList(tuple(lint_tags))
                
                for T in lint_tags:
                    if T in self.lint_overrides:
                        overrides_dialog.SetItemCheckedByLabel(T)
                        self.lint_overrides.remove(T)
                
                # Remaining tags should be custom entries
                if lint_tags:
                    for T in lint_tags:
                        overrides_dialog.AddItem(T, True)
                
                if overrides_dialog.ShowModal() == wx.ID_OK:
                    # Remove old overrides
                    self.lint_overrides = []
                    for L in overrides_dialog.GetCheckedLabels():
                        Logger.Debug(__name__, GT(u'Adding Lintian override: {}').format(L))
                        
                        self.lint_overrides.append(L)
    
    
    ## TODO: Doxygen
    def ResetPageInfo(self):
        for O in self.build_options:
            O.SetValue(O.default)
    
    
    ## TODO: Doxygen
    def SetFieldDataLegacy(self, data):
        self.ResetPageInfo()
        build_data = data.split(u'\n')
        
        if GetExecutable(u'md5sum'):
            self.chk_md5.SetValue(int(build_data[0]))
        
        self.chk_rmtree.SetValue(int(build_data[1]))
        
        if GetExecutable(u'lintian'):
            self.chk_lint.SetValue(int(build_data[2]))
    
    
    ## TODO: Doxygen
    def SetSummary(self, event=None):
        pg_scripts = GetPage(ident.SCRIPTS)
        
        # Make sure the page is not destroyed so no error is thrown
        if self:
            # Set summary when "Build" page is shown
            # Get the file count
            files_total = GetPage(ident.FILES).GetFileCount()
            f = GT(u'File Count')
            file_count = u'{}: {}'.format(f, files_total)
            
            # Scripts to make
            scripts_to_make = []
            scripts = ((u'preinst', pg_scripts.chk_preinst),
                (u'postinst', pg_scripts.chk_postinst),
                (u'prerm', pg_scripts.chk_prerm),
                (u'postrm', pg_scripts.chk_postrm))
            for script in scripts:
                if script[1].IsChecked():
                    scripts_to_make.append(script[0])
            
            s = GT(u'Scripts')
            if len(scripts_to_make):
                scripts_to_make = u'{}: {}'.format(s, u', '.join(scripts_to_make))
            
            else:
                scripts_to_make = u'{}: 0'.format(s)
            
            self.summary.SetValue(u'\n'.join((file_count, scripts_to_make)))
