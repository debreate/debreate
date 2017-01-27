# -*- coding: utf-8 -*-

## \package wiz_bin.build

# MIT licensing
# See: docs/LICENSE.txt


import commands, os, shutil, subprocess, traceback, wx

from dbr.functions          import FileUnstripped
from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from dbr.md5                import WriteMD5
from globals.bitmaps        import ICON_EXCLAMATION
from globals.bitmaps        import ICON_INFORMATION
from globals.cmdcheck       import CommandExists
from globals.errorcodes     import dbrerrno
from globals.execute        import ExecuteCommand
from globals.execute        import GetExecutable
from globals.execute        import GetSystemInstaller
from globals.fileio         import WriteFile
from globals.ident          import inputid
from globals.ident          import pgid
from globals.paths          import ConcatPaths
from globals.strings        import GS
from globals.strings        import TextIsEmpty
from globals.system         import PY_VER_MAJ
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import FieldEnabled
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetMainWindow
from globals.wizardhelper   import GetPage
from input.toggle           import CheckBox
from ui.button              import ButtonBuild64
from ui.dialog              import DetailedMessageDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.output              import OutputLog
from ui.panel               import BorderedPanel
from ui.progress            import PD_DEFAULT_STYLE
from ui.progress            import ProgressDialog
from ui.wizard              import WizardPage


## Build page
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.BUILD)
        
        # ----- Extra Options
        
        pnl_options = BorderedPanel(self)
        
        self.chk_md5 = CheckBox(pnl_options, inputid.MD5, label=GT(u'Create md5sums file'))
        # The » character denotes that an alternate tooltip should be shown if the control is disabled
        self.chk_md5.tt_name = u'md5»'
        self.chk_md5.SetName(u'MD5')
        self.chk_md5.default = True
        self.chk_md5.col = 0
        
        # Option to strip binaries
        self.chk_strip = CheckBox(pnl_options, label=GT(u'Strip binaries'), name=u'strip»')
        self.chk_strip.default = True
        self.chk_strip.col = 0
        
        # Deletes the temporary build tree
        self.chk_rmstage = CheckBox(pnl_options, label=GT(u'Delete staged directory'))
        self.chk_rmstage.SetName(u'rmstage')
        self.chk_rmstage.default = True
        self.chk_rmstage.SetValue(self.chk_rmstage.default)
        self.chk_rmstage.col = 0
        
        # Checks the output .deb for errors
        self.chk_lint = CheckBox(pnl_options, label=GT(u'Check package for errors with lintian'))
        self.chk_lint.tt_name = u'lintian»'
        self.chk_lint.SetName(u'LINTIAN')
        self.chk_lint.default = True
        self.chk_lint.col = 0
        
        # Installs the deb on the system
        self.chk_install = CheckBox(pnl_options, label=GT(u'Install package after build'))
        self.chk_install.tt_name = u'install»'
        self.chk_install.SetName(u'INSTALL')
        self.chk_install.default = False
        self.chk_install.col = 0
        
        btn_build = ButtonBuild64(self)
        btn_build.SetName(u'build')
        
        # Display log
        dsp_log = OutputLog(self)
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)
        
        # *** Layout *** #
        
        lyt_options = wx.GridBagSizer()
        
        next_row = 0
        prev_row = next_row
        for CHK in pnl_options.Children:
            row = next_row
            FLAGS = wx.LEFT|wx.RIGHT
            
            if CHK.col:
                row = prev_row
                FLAGS = wx.RIGHT
            
            lyt_options.Add(CHK, (row, CHK.col), flag=FLAGS, border=5)
            
            if not CHK.col:
                prev_row = next_row
                next_row += 1
        
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
        lyt_main.AddSpacer(5)
        lyt_main.Add(lyt_buttons, 0, wx.ALIGN_CENTER)
        lyt_main.Add(dsp_log, 2, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Post-layout functions *** #
        
        self.InitDefaultSettings()
    
    
    ## The actual build process
    #  
    #  \param task_list
    #        \b \e dict : Task string IDs & page data
    #  \param build_path
    #        \b \e unicode|str : Directory where .deb will be output
    #  \param filename
    #        \b \e unicode|str : Basename of output file without .deb extension
    #  \return
    #        \b \e dbrerror : SUCCESS if build completed successfully
    def Build(self, task_list, build_path, filename):
        # Declare this here in case of error before progress dialog created
        build_progress = None
        
        try:
            # Other mandatory tasks that will be processed
            mandatory_tasks = (
                u'stage',
                u'install_size',
                u'control',
                u'build',
                )
            
            # Add other mandatory tasks
            for T in mandatory_tasks:
                task_list[T] = None
            
            task_count = len(task_list)
            
            # Add each file for updating progress dialog
            if u'files' in task_list:
                task_count += len(task_list[u'files'])
            
            # Add each script for updating progress dialog
            if u'scripts' in task_list:
                task_count += len(task_list[u'scripts'])
            
            if DebugEnabled():
                task_msg = GT(u'Total tasks: {}').format(task_count)
                print(u'DEBUG: [{}] {}'.format(__name__, task_msg))
                for T in task_list:
                    print(u'\t{}'.format(T))
            
            create_changelog = u'changelog' in task_list
            create_copyright = u'copyright' in task_list
            
            pg_control = GetPage(pgid.CONTROL)
            pg_menu = GetPage(pgid.MENU)
            
            stage_dir = u'{}/{}__dbp__'.format(build_path, filename)
            
            if os.path.isdir(u'{}/DEBIAN'.format(stage_dir)):
                try:
                    shutil.rmtree(stage_dir)
                
                except OSError:
                    ShowErrorDialog(GT(u'Could not free stage directory: {}').format(stage_dir),
                            title=GT(u'Cannot Continue'))
                    
                    return (dbrerrno.EEXIST, None)
            
            # Actual path to new .deb
            deb = u'"{}/{}.deb"'.format(build_path, filename)
            
            progress = 0
            
            task_msg = GT(u'Preparing build tree')
            Logger.Debug(__name__, task_msg)
            
            wx.Yield()
            build_progress = ProgressDialog(GetMainWindow(), GT(u'Building'), task_msg,
                    maximum=task_count,
                    style=PD_DEFAULT_STYLE|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_CAN_ABORT)
            
            DIR_debian = ConcatPaths((stage_dir, u'DEBIAN'))
            
            # Make a fresh build tree
            os.makedirs(DIR_debian)
            progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            def UpdateProgress(current_task, message=None):
                task_eval = u'{} / {}'.format(current_task, task_count)
                
                if message:
                    Logger.Debug(__name__, u'{} ({})'.format(message, task_eval))
                    
                    wx.Yield()
                    build_progress.Update(current_task, message)
                    
                    return
                
                wx.Yield()
                build_progress.Update(current_task)
            
            # *** Files *** #
            if u'files' in task_list:
                UpdateProgress(progress, GT(u'Copying files'))
                
                files_data = task_list[u'files']
                for FILE in files_data:
                    file_defs = FILE.split(u' -> ')
                    
                    source_file = file_defs[0]
                    target_file = u'{}{}/{}'.format(stage_dir, file_defs[2], file_defs[1])
                    target_dir = os.path.dirname(target_file)
                    
                    if not os.path.isdir(target_dir):
                        os.makedirs(target_dir)
                    
                    # Remove asteriks from exectuables
                    exe = False
                    if source_file[-1] == u'*':
                        Logger.Debug(__name__, u'Adding executable to stage: {}'.format(target_file))
                        exe = True
                        source_file = source_file[:-1]
                    
                    if os.path.isdir(source_file):
                        Logger.Debug(__name__, u'Adding directory to stage: {}'.format(target_file))
                        
                        # HACK: Use os.path.dirname to avoid OSError: File exists
                        shutil.copytree(source_file, u'{}/{}'.format(target_dir, os.path.basename(source_file)))
                        
                        os.chmod(target_file, 0755)
                    
                    else:
                        Logger.Debug(__name__, u'Adding file to stage: {}'.format(target_file))
                        
                        shutil.copy(source_file, target_dir)
                        
                        # Set FILE permissions
                        if exe:
                            os.chmod(target_file, 0755)
                        
                        else:
                            os.chmod(target_file, 0644)
                    
                    # Individual files
                    progress += 1
                    UpdateProgress(progress)
                
                # Entire file task
                progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # *** Strip files ***#
            # FIXME: Needs only be run if 'files' step is used
            if u'strip' in task_list:
                UpdateProgress(progress, GT(u'Stripping binaries'))
                
                for ROOT, DIRS, FILES in os.walk(stage_dir):
                    for F in FILES:
                        # Don't check files in DEBIAN directory
                        if ROOT != DIR_debian:
                            F = ConcatPaths((ROOT, F))
                            
                            if FileUnstripped(F):
                                Logger.Debug(__name__, u'Unstripped file: {}'.format(F))
                                
                                # FIXME: Strip command should be set as class member?
                                ExecuteCommand(GetExecutable(u'strip'), F)
                
                progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            package = GetField(pg_control, inputid.PACKAGE).GetValue()
            
            # Make sure that the directory is available in which to place documentation
            if create_changelog or create_copyright:
                doc_dir = u'{}/usr/share/doc/{}'.format(stage_dir, package)
                if not os.path.isdir(doc_dir):
                    os.makedirs(doc_dir)
            
            # *** Changelog *** #
            if create_changelog:
                UpdateProgress(progress, GT(u'Creating changelog'))
                
                # If changelog will be installed to default directory
                changelog_target = task_list[u'changelog'][0]
                if changelog_target == u'STANDARD':
                    changelog_target = ConcatPaths((u'{}/usr/share/doc'.format(stage_dir), package))
                
                else:
                    changelog_target = ConcatPaths((stage_dir, changelog_target))
                
                if not os.path.isdir(changelog_target):
                    os.makedirs(changelog_target)
                
                WriteFile(u'{}/changelog'.format(changelog_target), task_list[u'changelog'][1])
                
                CMD_gzip = GetExecutable(u'gzip')
                
                if CMD_gzip:
                    UpdateProgress(progress, GT(u'Compressing changelog'))
                    c = u'{} -n --best "{}/changelog"'.format(CMD_gzip, changelog_target)
                    clog_status = commands.getstatusoutput(c.encode(u'utf-8'))
                    if clog_status[0]:
                        ShowErrorDialog(GT(u'Could not compress changelog'), clog_status[1], warn=True, title=GT(u'Warning'))
                
                progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # *** Copyright *** #
            if create_copyright:
                UpdateProgress(progress, GT(u'Creating copyright'))
                
                WriteFile(u'{}/usr/share/doc/{}/copyright'.format(stage_dir, package), task_list[u'copyright'])
                
                progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # Characters that should not be in filenames
            invalid_chars = (u' ', u'/')
            
            # *** Menu launcher *** #
            if u'launcher' in task_list:
                UpdateProgress(progress, GT(u'Creating menu launcher'))
                
                # This might be changed later to set a custom directory
                menu_dir = u'{}/usr/share/applications'.format(stage_dir)
                
                menu_filename = pg_menu.GetOutputFilename()
                
                # Remove invalid characters from filename
                for char in invalid_chars:
                    menu_filename = menu_filename.replace(char, u'_')
                
                if not os.path.isdir(menu_dir):
                    os.makedirs(menu_dir)
                
                WriteFile(u'{}/{}.desktop'.format(menu_dir, menu_filename), task_list[u'launcher'])
                
                progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # *** md5sums file *** #
            # Good practice to create hashes before populating DEBIAN directory
            if u'md5sums' in task_list:
                UpdateProgress(progress, GT(u'Creating md5sums'))
                
                if not WriteMD5(stage_dir, parent=build_progress):
                    # Couldn't call md5sum command
                    build_progress.Cancel()
                
                progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # *** Scripts *** #
            if u'scripts' in task_list:
                UpdateProgress(progress, GT(u'Creating scripts'))
                
                scripts = task_list[u'scripts']
                for script_name, script_text in scripts:
                    script_filename = ConcatPaths((u'{}/DEBIAN'.format(stage_dir), script_name))
                    
                    WriteFile(script_filename, script_text)
                    
                    # Make sure scipt path is wrapped in quotes to avoid whitespace errors
                    os.chmod(script_filename, 0755)
                    os.system((u'chmod +x "{}"'.format(script_filename)))
                    
                    # Individual scripts
                    progress += 1
                    UpdateProgress(progress)
                
                # Entire script task
                progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # *** Control file *** #
            UpdateProgress(progress, GT(u'Getting installed size'))
            
            # Get installed-size
            installed_size = os.popen((u'du -hsk "{}"'.format(stage_dir))).readlines()
            installed_size = installed_size[0].split(u'\t')
            installed_size = installed_size[0]
            
            # Insert Installed-Size into control file
            control_data = pg_control.ExportPage().split(u'\n')
            control_data.insert(2, u'Installed-Size: {}'.format(installed_size))
            
            progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # Create final control file
            UpdateProgress(progress, GT(u'Creating control file'))
            
            # dpkg fails if there is no newline at end of file
            control_data = u'\n'.join(control_data).strip(u'\n')
            # Ensure there is only one empty trailing newline
            # Two '\n' to show physical empty line, but not required
            # Perhaps because string is not null terminated???
            control_data = u'{}\n\n'.format(control_data)
            
            WriteFile(u'{}/DEBIAN/control'.format(stage_dir), control_data, no_strip=u'\n')
            
            progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # *** Final build *** #
            UpdateProgress(progress, GT(u'Running dpkg'))
            
            working_dir = os.path.split(stage_dir)[0]
            c_tree = os.path.split(stage_dir)[1]
            deb_package = u'{}.deb'.format(filename)
            
            # Move the working directory becuase dpkg seems to have problems with spaces in path
            os.chdir(working_dir)
            # FIXME: Should check for working fakeroot & dpkg-deb executables
            build_status = commands.getstatusoutput((u'{} {} -b "{}" "{}"'.format(GetExecutable(u'fakeroot'), GetExecutable(u'dpkg-deb'), c_tree, deb_package)))
            
            progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # *** Delete staged directory *** #
            if u'rmstage' in task_list:
                UpdateProgress(progress, GT(u'Removing temp directory'))
                
                try:
                    shutil.rmtree(stage_dir)
                
                except OSError:
                    ShowErrorDialog(GT(u'An error occurred when trying to delete the build tree'),
                            parent=build_progress)
                
                progress += 1
            
            if build_progress.WasCancelled():
                build_progress.Destroy()
                return (dbrerrno.ECNCLD, None)
            
            # *** ERROR CHECK
            if u'lintian' in task_list:
                UpdateProgress(progress, GT(u'Checking package for errors'))
                
                # FIXME: Should be set as class memeber?
                CMD_lintian = GetExecutable(u'lintian')
                errors = commands.getoutput((u'{} {}'.format(CMD_lintian, deb)))
                
                if errors != wx.EmptyString:
                    e1 = GT(u'Lintian found some issues with the package.')
                    e2 = GT(u'Details saved to {}').format(filename)
                    
                    WriteFile(u'{}/{}.lintian'.format(build_path, filename), errors)
                    
                    DetailedMessageDialog(build_progress, GT(u'Lintian Errors'),
                            ICON_INFORMATION, u'{}\n{}.lintian'.format(e1, e2), errors).ShowModal()
                
                progress += 1
            
            # Close progress dialog
            wx.Yield()
            build_progress.Update(progress)
            build_progress.Destroy()
            
            # Build completed successfullly
            if not build_status[0]:
                return (dbrerrno.SUCCESS, deb_package)
            
            if PY_VER_MAJ <= 2:
                # Unicode decoder has trouble with certain characters. Replace any
                # non-decodable characters with � (0xFFFD).
                build_output = list(build_status[1])
                
                # String & unicode string incompatibilities
                index = 0
                for C in build_output:
                    try:
                        GS(C)
                    
                    except UnicodeDecodeError:
                        build_output[index] = u'�'
                    
                    index += 1
                
                build_status = (build_status[0], u''.join(build_output))
            
            # Build failed
            return (build_status[0], build_status[1])
        
        except:
            if build_progress:
                build_progress.Destroy()
            
            return(dbrerrno.EUNKNOWN, traceback.format_exc())
    
    
    ## TODO: Doxygen
    #  
    #  \return
    #        \b \e tuple : Return code & build details
    def BuildPrep(self):
        # Declare these here in case of error before dialogs created
        save_dia = None
        prebuild_progress = None
        
        try:
            # List of tasks for build process
            # 'stage' should be very first task
            task_list = {}
            
            # Control page
            pg_control = GetPage(pgid.CONTROL)
            fld_package = GetField(pg_control, inputid.PACKAGE)
            fld_version = GetField(pg_control, inputid.VERSION)
            fld_maint = GetField(pg_control, inputid.MAINTAINER)
            fld_email = GetField(pg_control, inputid.EMAIL)
            fields_control = (
                fld_package,
                fld_version,
                fld_maint,
                fld_email,
                )
            
            # Menu launcher page
            pg_launcher = GetPage(pgid.MENU)
            
            # Check to make sure that all required fields have values
            required = list(fields_control)
            
            if pg_launcher.IsBuildExportable():
                task_list[u'launcher'] = pg_launcher.ExportPage()
                
                required.append(pg_launcher.ti_name)
                
                if not pg_launcher.chk_filename.GetValue():
                    required.append(pg_launcher.ti_filename)
            
            for item in required:
                if TextIsEmpty(item.GetValue()):
                    field_name = GT(item.GetName().title())
                    page_name = pg_control.GetName()
                    if item not in fields_control:
                        page_name = pg_launcher.GetName()
                    
                    return (dbrerrno.FEMPTY, u'{} ➜ {}'.format(page_name, field_name))
            
            # Get information from control page for default filename
            package = fld_package.GetValue()
            # Remove whitespace
            package = package.strip(u' \t')
            package = u'-'.join(package.split(u' '))
            
            version = fld_version.GetValue()
            # Remove whitespace
            version = version.strip(u' \t')
            version = u''.join(version.split())
            
            arch = GetField(pg_control, inputid.ARCH).GetStringSelection()
            
            # Dialog for save destination
            ttype = GT(u'Debian packages')
            save_dia = wx.FileDialog(self, GT(u'Save'), os.getcwd(), wx.EmptyString, u'{}|*.deb'.format(ttype),
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
            save_dia.SetFilename(u'{}_{}_{}.deb'.format(package, version, arch))
            if not save_dia.ShowModal() == wx.ID_OK:
                return (dbrerrno.ECNCLD, None)
            
            build_path = os.path.split(save_dia.GetPath())[0]
            filename = os.path.split(save_dia.GetPath())[1].split(u'.deb')[0]
            
            # Control, menu, & build pages not added to this list
            page_checks = (
                (pgid.FILES, u'files'),
                (pgid.SCRIPTS, u'scripts'),
                (pgid.CHANGELOG, u'changelog'),
                (pgid.COPYRIGHT, u'copyright'),
                )
            
            # Install step is not added to this list
            # 'control' should be after 'md5sums'
            # 'build' should be after 'control'
            other_checks = (
                (self.chk_md5, u'md5sums'),
                (self.chk_strip, u'strip'),
                (self.chk_rmstage, u'rmstage'),
                (self.chk_lint, u'lintian'),
                )
            
            prep_task_count = len(page_checks) + len(other_checks)
            
            progress = 0
            
            wx.Yield()
            prebuild_progress = ProgressDialog(GetMainWindow(), GT(u'Preparing to build'),
                    maximum=prep_task_count)
            
            if wx.MAJOR_VERSION < 3:
                # Resize dialog for better fit
                pb_size = prebuild_progress.GetSizeTuple()
                pb_size = (pb_size[0]+200, pb_size[1])
                prebuild_progress.SetSize(pb_size)
                prebuild_progress.CenterOnParent()
            
            for PID, id_string in page_checks:
                wx.Yield()
                prebuild_progress.Update(progress, GT(u'Checking {}').format(id_string))
                
                wizard_page = GetPage(PID)
                if wizard_page.IsBuildExportable():
                    task_list[id_string] = wizard_page.ExportPage()
                
                progress += 1
            
            for task_check, id_string in other_checks:
                wx.Yield()
                prebuild_progress.Update(progress, GT(u'Testing for: {}').format(task_check.GetLabel()))
                
                if task_check.GetValue():
                    task_list[id_string] = None
                
                progress += 1
            
            # Close progress dialog
            wx.Yield()
            prebuild_progress.Update(progress)
            prebuild_progress.Destroy()
            
            return (dbrerrno.SUCCESS, (task_list, build_path, filename))
        
        except:
            if save_dia:
                save_dia.Destroy()
            
            if prebuild_progress:
                prebuild_progress.Destroy()
            
            return (dbrerrno.EUNKNOWN, traceback.format_exc())
    
    
    ## TODO: Doxygen
    def GatherData(self):
        build_list = []
        
        options = (
            self.chk_md5,
            self.chk_rmstage,
            self.chk_lint,
            )
        
        for O in options:
            if O.GetValue():
                build_list.append(u'1')
            
            else:
                build_list.append(u'0')
        
        if self.chk_strip.GetValue():
            build_list.append(u'strip')
        
        return u'<<BUILD>>\n{}\n<</BUILD>>'.format(u'\n'.join(build_list))
    
    
    ## Sets up page with default settings
    def InitDefaultSettings(self):
        # md5sum file
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
        # Build preparation
        ret_code, build_prep = self.BuildPrep()
        
        if ret_code == dbrerrno.ECNCLD:
            return
        
        if ret_code == dbrerrno.FEMPTY:
            err_dia = DetailedMessageDialog(GetMainWindow(), GT(u'Cannot Continue'), ICON_EXCLAMATION,
                    text=u'{}\n{}'.format(GT(u'One of the required fields is empty'), build_prep))
            err_dia.ShowModal()
            err_dia.Destroy()
            
            return
        
        if ret_code == dbrerrno.SUCCESS:
            task_list, build_path, filename = build_prep
            
            # Actual build
            ret_code, result = self.Build(task_list, build_path, filename)
            
            # FIXME: Check .deb package timestamp to confirm build success
            if ret_code == dbrerrno.SUCCESS:
                DetailedMessageDialog(GetMainWindow(), GT(u'Success'), ICON_INFORMATION,
                        text=GT(u'Package created successfully')).ShowModal()
                
                # Installing the package
                if FieldEnabled(self.chk_install) and self.chk_install.GetValue():
                    self.InstallPackage(result)
                
                return
            
            if result:
                ShowErrorDialog(GT(u'Package build failed'), result)
            
            else:
                ShowErrorDialog(GT(u'Package build failed with unknown error'))
            
            return
        
        if build_prep:
            ShowErrorDialog(GT(u'Build preparation failed'), build_prep)
        
        else:
            ShowErrorDialog(GT(u'Build preparation failed with unknown error'))
    
    
    ## TODO: Doxygen
    def Reset(self):
        self.InitDefaultSettings()
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Use string names in project file but retain
    #        compatibility with older projects that use
    #        integer values.
    def Set(self, data):
        # ???: Redundant
        self.Reset()
        build_data = data.split(u'\n')
        
        if GetExecutable(u'md5sum'):
            try:
                self.chk_md5.SetValue(int(build_data[0]))
            
            except IndexError:
                pass
        
        try:
            self.chk_rmstage.SetValue(int(build_data[1]))
        
        except IndexError:
            pass
        
        if GetExecutable(u'lintian'):
            try:
                self.chk_lint.SetValue(int(build_data[2]))
            
            except IndexError:
                pass
        
        self.chk_strip.SetValue(GetExecutable(u'strip') and u'strip' in build_data)
    
    
    ## TODO: Doxygen
    def SetSummary(self, event=None):
        main_window = GetMainWindow()
        
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
