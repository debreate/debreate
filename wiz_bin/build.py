# -*- coding: utf-8 -*-

## \package wiz_bin.build

# MIT licensing
# See: docs/LICENSE.txt


import commands, math, os, subprocess, time, traceback, wx

from dbr.functions          import GetBoolean
from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from globals                import ident
from globals.application    import AUTHOR_email
from globals.bitmaps        import ICON_EXCLAMATION
from globals.bitmaps        import ICON_INFORMATION
from globals.cmdcheck       import CommandExists
from globals.errorcodes     import dbrerrno
from globals.execute        import GetExecutable
from globals.execute        import GetSystemInstaller
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.ident          import pgid
from globals.paths          import ConcatPaths
from globals.paths          import PATH_app
from globals.stage          import CreateStage
from globals.stage          import RemoveStage
from globals.strings        import RemoveEmptyLines
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import FieldEnabled
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetMainWindow
from globals.wizardhelper   import GetPage
from input.toggle           import CheckBoxESS
from startup.tests          import GetTestList
from ui.button              import ButtonBuild64
from ui.checklist           import CheckListDialog
from ui.dialog              import DetailedMessageDialog
from ui.dialog              import GetFileSaveDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.output              import OutputLog
from ui.panel               import BorderedPanel
from ui.progress            import PD_DEFAULT_STYLE
from ui.progress            import ProgressDialog
from ui.progress            import TimedProgressDialog
from ui.wizard              import WizardPage


## Build page
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.BUILD)
        
        # Bypass build prep check
        self.prebuild_check = False
        
        # Add checkable items to this list
        # FIXME: Use a different method
        self.build_options = []
        
        # ----- Extra Options
        
        pnl_options = BorderedPanel(self)
        
        self.chk_md5 = CheckBoxESS(pnl_options, label=GT(u'Create md5sums file'))
        # The » character denotes that an alternate tooltip should be shown if the control is disabled
        self.chk_md5.tt_name = u'md5»'
        self.chk_md5.SetName(u'MD5')
        self.chk_md5.default = True
        
        # Option to strip binaries
        self.chk_strip = CheckBoxESS(pnl_options, label=GT(u'Strip binaries'), name=u'strip»')
        self.chk_strip.default = True
        
        # Deletes the temporary build tree
        self.chk_rmstage = CheckBoxESS(pnl_options, label=GT(u'Delete staged directory'))
        self.chk_rmstage.SetName(u'RMSTAGE')
        self.chk_rmstage.default = True
        self.chk_rmstage.SetValue(self.chk_rmstage.default)
        
        # Checks the output .deb for errors
        self.chk_lint = CheckBoxESS(pnl_options, label=GT(u'Check package for errors with lintian'))
        self.chk_lint.tt_name = u'lintian»'
        self.chk_lint.SetName(u'LINTIAN')
        self.chk_lint.default = True
        
        # Installs the deb on the system
        self.chk_install = wx.CheckBox(pnl_options, label=GT(u'Install package after build'))
        self.chk_install.tt_name = u'install»'
        self.chk_install.SetName(u'INSTALL')
        self.chk_install.default = False
        
        # *** Lintian Overrides *** #
        
        if u'alpha' in GetTestList():
            # FIXME: Move next to lintian check box
            self.lint_overrides = []
            btn_lint_overrides = wx.Button(self, label=GT(u'Lintian overrides'))
            btn_lint_overrides.Bind(wx.EVT_BUTTON, self.OnSetLintOverrides)
        
        btn_build = ButtonBuild64(self)
        btn_build.SetName(u'build')
        
        # Display log
        dsp_log = OutputLog(self)
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)
        
        # *** Layout *** #
        
        lyt_options = BoxSizer(wx.VERTICAL)
        lyt_options.AddMany((
            (self.chk_md5, 0, wx.LEFT|wx.RIGHT, 5),
            (self.chk_strip, 0, wx.LEFT|wx.RIGHT, 5),
            (self.chk_rmstage, 0, wx.LEFT|wx.RIGHT, 5),
            (self.chk_lint, 0, wx.LEFT|wx.RIGHT, 5),
            (self.chk_install, 0, wx.LEFT|wx.RIGHT, 5),
            ))
        
        pnl_options.SetSizer(lyt_options)
        pnl_options.SetAutoLayout(True)
        pnl_options.Layout()
        
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_build, 1)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(wx.StaticText(self, label=GT(u'Extra Options')), 0,
                wx.ALIGN_LEFT|wx.ALIGN_BOTTOM|wx.LEFT, 5)
        lyt_main.Add(pnl_options, 0, wx.LEFT, 5)
        lyt_main.AddSpacer(5)
        
        if u'alpha' in GetTestList():
            #lyt_main.Add(wx.StaticText(self, label=GT(u'Lintian overrides')), 0, wx.LEFT, 5)
            lyt_main.Add(btn_lint_overrides, 0, wx.LEFT, 5)
        
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_buttons, 0, wx.ALIGN_CENTER)
        lyt_main.Add(dsp_log, 2, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Post-layout functions *** #
        
        self.InitDefaultSettings()
    
    
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
            main_window = GetMainWindow()
            
            # Reported at the end of build
            build_summary = []
            
            steps_count = len(pages_build_ids)
            current_step = 0
            
            # Steps from build page
            for chk in self.chk_md5, self.chk_lint, self.chk_rmstage:
                if chk.IsChecked():
                    steps_count += 1
            
            # Control file & .deb build step
            steps_count += 2
            
            stage = CreateStage()
            
            log_msg = GT(u'Starting build')
            
            wx.YieldIfNeeded()
            # FIXME: Enable PD_CAN_ABORT
            build_progress = ProgressDialog(main_window, GT(u'Building'), log_msg,
                    maximum=steps_count)
            
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
                            
                            ShowErrorDialog(GT(u'Error occurred during build'), ret_value)
                            
                            return
                        
                        current_step += 1
                
                # *** Control File *** #
                if not build_progress.WasCancelled():
                    wx.YieldIfNeeded()
                    
                    log_msg = log_message(GT(u'Creating control file'), current_step+1, steps_count)
                    build_progress.Update(current_step, log_msg)
                    
                    Logger.Debug(__name__, log_msg)
                    
                    # Retrieve control page
                    pg_control = wizard.GetPage(pgid.CONTROL)
                    if not pg_control:
                        build_progress.Destroy()
                        
                        ShowErrorDialog(GT(u'Could not retrieve control page'),
                                GT(u'Please contact the developer: {}').format(AUTHOR_email),
                                title=u'Fatal Error')
                        
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
                    if self.chk_rmstage.IsChecked():
                        log_msg = log_message(GT(u'Removing staged build tree'), current_step+1, steps_count)
                        
                        wx.YieldIfNeeded()
                        build_progress.Update(current_step, log_msg)
                        
                        build_summary.append(u'\n{}:'.format(log_msg))
                        RemoveStage(stage)
                        
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
                
                ShowErrorDialog(GT(u'Error occurred during build'), traceback.format_exc())
        
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
            main_window = GetMainWindow()
            
            # List of page IDs to process during build
            pg_build_ids = []
            
            steps_count = len(prep_ids)
            current_step = 0
            
            msg_label1 = GT(u'Prepping page "{}"')
            msg_label2 = GT(u'Step {}/{}')
            msg_label = u'{} ({})'.format(msg_label1, msg_label2)
            
            prep_progress = ProgressDialog(main_window, GT(u'Preparing Build'),
                    msg_label2.format(current_step, steps_count), maximum=steps_count,
                    style=PD_DEFAULT_STYLE|wx.PD_CAN_ABORT)
            
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
            
            ShowErrorDialog(GT(u'Error occurred during pre-build'), traceback.format_exc())
        
        return None
    
    
    ## TODO: Doxygen
    def Get(self, get_module=False):
        # 'install after build' is not exported to project for safety
        
        fields = {}
        omit_options = (
            self.chk_install,
        )
        
        for O in self.build_options:
            # Leave options out that should not be saved
            if O not in omit_options:
                fields[O.GetName()] = unicode(O.GetValue())
        
        page = wx.EmptyString
        
        for F in fields:
            if page == wx.EmptyString:
                page = u'{}={}'.format(F, fields[F])
            
            else:
                page = u'{}\n{}={}'.format(page, F, fields[F])
        
        if page == wx.EmptyString:
            page = None
        
        if get_module:
            page = (__name__, page,)
        
        return page
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, filename):
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
    
    
    ## Sets up page with default settings
    def InitDefaultSettings(self):
        self.build_options = []
        
        option_list = (
            (self.chk_md5, GetExecutable(u'md5sum'),),
            (self.chk_strip, GetExecutable(u'strip'),),
            (self.chk_rmstage, True,),
            (self.chk_lint, GetExecutable(u'lintian'),),
            (self.chk_install, GetSystemInstaller(),),
            )
        
        for option, command in option_list:
            # FIXME: Commands should be updated globally
            if not isinstance(command, bool):
                command = CommandExists(command)
            
            option.Enable(bool(command))
            option.SetValue(FieldEnabled(option) and option.default)
            
            if bool(command):
                self.build_options.append(option)
    
    
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
        system_installer = GetSystemInstaller()
        
        if not system_installer:
            ShowErrorDialog(
                GT(u'Cannot install package'),
                GT(u'A compatible package manager could not be found on the system'),
                __name__,
                warn=True
                )
            
            return
        
        Logger.Info(__name__, GT(u'Attempting to install package: {}').format(package))
        Logger.Info(__name__, GT(u'Installing with {}').format(system_installer))
        
        install_cmd = (system_installer, package,)
        
        wx.Yield()
        # FIXME: Use ExecuteCommand here
        install_output = subprocess.Popen(install_cmd)
        
        # Command appears to not have been executed correctly
        if install_output == None:
            ShowErrorDialog(
                GT(u'Could not install package: {}'),
                GT(u'An unknown error occurred'),
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
    
    
    ## TODO: Doxygen
    def OnBuild(self, event=None):
        if event:
            event.Skip()
        
        wizard = self.GetWizard()
        
        pg_control = wizard.GetPage(pgid.CONTROL)
        pg_files = wizard.GetPage(pgid.FILES)
        pg_launcher = wizard.GetPage(pgid.LAUNCHERS)
        
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
                    
                    msg_l1 = GT(u'One of the required fields is empty')
                    msg_full = u'{}: {} ➜ {}'.format(msg_l1, p_name, f_name)
                    
                    Logger.Warning(__name__, msg_full)
                    
                    DetailedMessageDialog(GetMainWindow(), GT(u'Cannot Continue'), ICON_EXCLAMATION,
                            text=msg_full).ShowModal()
                    
                    for P in wizard.pages:
                        if P.GetLabel() == p_name:
                            Logger.Debug(__name__, GT(u'Showing page with required field: {}').format(p_name))
                            wizard.ShowPage(P.GetId())
                    
                    return
        
        if pg_files.file_list.MissingFiles():
            ShowErrorDialog(GT(u'Files are missing in file list'), warn=True, title=GT(u'Warning'))
            
            wizard.ShowPage(pgid.FILES)
            
            return
        
        
        ttype = GT(u'Debian Packages')
        save_dialog = GetFileSaveDialog(GetMainWindow(), GT(u'Build Package'),
                u'{} (*.deb)|*.deb'.format(ttype), u'deb')
        
        package = GetField(pg_control, ident.F_PACKAGE)
        version = GetField(pg_control, ident.F_VERSION)
        arch = GetField(pg_control, ident.F_ARCH)
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
    #  
    #  TODO: Show warning dialog that this could take a while
    #  TODO: Add cancel option to progress dialog
    #  FIXME: List should be cached so no need for re-scanning
    def OnSetLintOverrides(self, event=None):
        Logger.Debug(__name__, GT(u'Setting Lintian overrides...'))
        
        lintian_tags_file = u'{}/data/lintian/tags'.format(PATH_app)
        
        if not os.path.isfile(lintian_tags_file):
            Logger.Error(__name__, u'Lintian tags file is missing: {}'.format(lintian_tags_file))
            
            return False
        
        lint_tags = RemoveEmptyLines(ReadFile(lintian_tags_file, split=True))
        
        if lint_tags:
            Logger.Debug(__name__, u'Lintian tags set')
            
            # DEBUG: Start
            if DebugEnabled() and len(lint_tags) > 50:
                print(u'  Reducing tag count to 200 ...')
                
                lint_tags = lint_tags[:50]
            
            Logger.Debug(__name__, u'Processing {} tags'.format(len(lint_tags)))
            # DEBUG: End
            
            
            tag_count = len(lint_tags)
            
            def GetProgressMessage(message, count=tag_count):
                return u'{} ({} {})'.format(message, count, GT(u'tags'))
            
            
            progress = TimedProgressDialog(GetMainWindow(), GT(u'Building Tag List'),
                    GetProgressMessage(GT(u'Scanning default tags')))
            progress.Start()
            
            wx.Yield()
            
            # Create the dialog
            overrides_dialog = CheckListDialog(GetMainWindow(), title=GT(u'Lintian Overrides'),
                    allow_custom=True)
            # FIXME: Needs progress dialog
            overrides_dialog.InitCheckList(tuple(lint_tags))
            
            progress.SetMessage(GetProgressMessage(GT(u'Setting selected overrides')))
            
            for T in lint_tags:
                if T in self.lint_overrides:
                    overrides_dialog.SetItemCheckedByLabel(T)
                    self.lint_overrides.remove(T)
            
            progress.SetMessage(GetProgressMessage(GT(u'Adding custom tags'), len(self.lint_overrides)))
            
            # Remaining tags should be custom entries
            # FIXME:
            if self.lint_overrides:
                for T in self.lint_overrides:
                    overrides_dialog.AddItem(T, True)
            
            progress.Stop()
            
            if overrides_dialog.ShowModal() == wx.ID_OK:
                # Remove old overrides
                self.lint_overrides = []
                for L in overrides_dialog.GetCheckedLabels():
                    Logger.Debug(__name__, GT(u'Adding Lintian override: {}').format(L))
                    
                    self.lint_overrides.append(L)
            
            return True
        
        else:
            Logger.Debug(__name__, u'Setting lintian tags failed')
            
            return False
    
    
    ## TODO: Doxygen
    def Reset(self):
        for O in self.build_options:
            O.SetValue(O.default)
    
    
    ## TODO: Doxygen
    def Set(self, data):
        self.Reset()
        build_data = data.split(u'\n')
        
        if GetExecutable(u'md5sum'):
            self.chk_md5.SetValue(int(build_data[0]))
        
        self.chk_rmstage.SetValue(int(build_data[1]))
        
        if GetExecutable(u'lintian'):
            self.chk_lint.SetValue(int(build_data[2]))
    
    
    ## TODO: Doxygen
    def SetSummary(self, event=None):
        pg_scripts = GetPage(pgid.SCRIPTS)
        
        # Make sure the page is not destroyed so no error is thrown
        if self:
            # Set summary when "Build" page is shown
            # Get the file count
            files_total = GetPage(pgid.FILES).GetFileCount()
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
