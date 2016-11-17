# -*- coding: utf-8 -*-


import os, subprocess, webbrowser, wx
from urllib2 import URLError, HTTPError

import dbr
from dbr.compression        import CompressionHandler
from dbr.compression        import DEFAULT_COMPRESSION_ID
from dbr.compression        import ID_ZIP_BZ2
from dbr.compression        import ID_ZIP_GZ
from dbr.compression        import ID_ZIP_NONE
from dbr.compression        import ID_ZIP_XZ
from dbr.compression        import ID_ZIP_ZIP
from dbr.compression        import compression_formats
from dbr.compression        import compression_mimetypes
from dbr.config             import ConfCode
from dbr.config             import GetDefaultConfigValue
from dbr.config             import ReadConfig
from dbr.config             import WriteConfig
from dbr.dialogs            import ErrorDialog
from dbr.dialogs            import GetDialogWildcards
from dbr.dialogs            import GetFileOpenDialog
from dbr.dialogs            import GetFileSaveDialog
from dbr.dialogs            import ShowDialog
from dbr.error              import ShowError
from dbr.functions          import CreateTempDirectory
from dbr.functions          import GetCurrentVersion
from dbr.functions          import GetFileMimeType
from dbr.functions          import RemoveTempDirectory
from dbr.functions          import UsingDevelopmentVersion
from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import LogWindow
from dbr.log                import Logger
from dbr.quickbuild         import QuickBuild
from globals.application    import APP_homepage
from globals.application    import APP_project_gh
from globals.application    import APP_project_sf
from globals.application    import AUTHOR_email
from globals.application    import AUTHOR_name
from globals.application    import VERSION_string
from globals.application    import VERSION_tuple
from globals.commands       import CMD_tar
from globals.commands       import CMD_xdg_open
from globals.errorcodes     import dbrerrno
from globals.ident          import ID_DEBUG
from globals.ident          import ID_LOG
from globals.ident          import ID_THEME
from globals.paths          import PATH_app
from globals.paths          import PATH_local
from globals.project        import ID_PROJ_A
from globals.project        import ID_PROJ_L
from globals.project        import ID_PROJ_T
from globals.project        import ID_PROJ_Z
from globals.project        import PROJECT_ext
from wiz_bin.build          import Panel as PageBuild
from wiz_bin.changelog      import Panel as PageChangelog
from wiz_bin.control        import Panel as PageControl
from wiz_bin.copyright      import Panel as PageCopyright
from wiz_bin.depends        import Panel as PageDepends
from wiz_bin.files          import Panel as PageFiles
from wiz_bin.greeting       import Panel as PageGreeting
from wiz_bin.launchers      import Panel as PageLaunchers
from wiz_bin.man            import Panel as PageMan
from wiz_bin.scripts        import Panel as PageScripts


# Options menu
ID_Dialogs = wx.NewId()
ID_MENU_TT = wx.NewId()
ID_LOG_DIR_OPEN = wx.NewId()

# Debian Policy Manual IDs
ID_DPM = wx.NewId()
ID_DPMCtrl = wx.NewId()
ID_DPMLog = wx.NewId()
ID_UPM = wx.NewId()
ID_LINT_TAGS = wx.NewId()
ID_LINT_OVERRIDE = wx.NewId()

ID_QBUILD = wx.NewId()
ID_UPDATE = wx.NewId()


default_title = GT(u'Debreate - Debian Package Builder')


class MainWindow(wx.Frame):
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, default_title, pos, size)
        
        if DebugEnabled():
            self.SetTitle(u'{} ({})'.format(default_title, GT(u'debugging')))
        
        self.SetMinSize((640,400))
        
        # ----- Set Titlebar Icon
        self.main_icon = wx.Icon(u'{}/bitmaps/debreate64.png'.format(PATH_app), wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.main_icon)
        
        # If window is maximized this will store last window size and position for next session
        wx.EVT_MAXIMIZE(self, self.OnMaximize)
        
        # ----- Status Bar
        self.stat_bar = wx.StatusBar(self, -1)
        self.SetStatusBar(self.stat_bar)
        
        
        
        # ***** Menu Bar ***** #
        
        # ----- File Menu
        self.menu_file = wx.Menu()
        
        # Quick Build
        self.QuickBuild = wx.MenuItem(self.menu_file, ID_QBUILD,
                                         GT(u'Quick Build'), GT(u'Build a package from an existing build tree'))
        self.QuickBuild.SetBitmap(wx.Bitmap(u'{}/bitmaps/clock16.png'.format(PATH_app)))
        
        self.menu_file.Append(wx.ID_NEW, help=GT(u'Start a new project'))
        self.menu_file.Append(wx.ID_OPEN, help=GT(u'Open a previously saved project'))
        self.menu_file.Append(wx.ID_SAVE, help=GT(u'Save current project'))
        self.menu_file.Append(wx.ID_SAVEAS, help=GT(u'Save current project with a new filename'))
        self.menu_file.AppendSeparator()
        self.menu_file.AppendItem(self.QuickBuild)
        self.menu_file.AppendSeparator()
        self.menu_file.Append(wx.ID_EXIT)
        
        wx.EVT_MENU(self, wx.ID_NEW, self.OnNewProject)
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnOpenProject)
        
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnSaveProject)
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveProjectAs)
        wx.EVT_MENU(self, ID_QBUILD, self.OnQuickBuild)
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnQuit)
        wx.EVT_CLOSE(self, self.OnQuit) #custom close event shows a dialog box to confirm quit
        
        # *** Page Menu *** #
        ## This menu is filled from dbr.wizard.Wizard
        self.menu_page = wx.Menu()
        
        # *** Action Menu *** #
        self.menu_action = wx.Menu()
        
        # FIXME: Use global ID???
        action_build = wx.MenuItem(self.menu_action, wx.NewId(), GT(u'Build'),
                GT(u'Start building .deb package'))
        
        self.menu_action.AppendItem(action_build)
        
        # ----- Options Menu
        self.menu_opt = wx.Menu()
        
        # Show/Hide tooltips
        self.opt_tooltips = wx.MenuItem(self.menu_opt, ID_MENU_TT, GT(u'Show tooltips'),
                GT(u'Show or hide tooltips'), kind=wx.ITEM_CHECK)
        wx.EVT_MENU(self, ID_MENU_TT, self.OnToggleToolTips)
        self.menu_opt.AppendItem(self.opt_tooltips)
        
        show_tooltips = ReadConfig(u'tooltips')
        if show_tooltips != ConfCode.KEY_NO_EXIST:
            self.opt_tooltips.Check(show_tooltips)
        
        else:
            self.opt_tooltips.Check(GetDefaultConfigValue(u'tooltips'))
        self.OnToggleToolTips()
        
        # Dialogs options
        self.cust_dias = wx.MenuItem(self.menu_opt, ID_Dialogs, GT(u'Use Custom Dialogs'),
            GT(u'Use System or Custom Save/Open Dialogs'), kind=wx.ITEM_CHECK)
        #self.menu_opt.AppendItem(self.cust_dias)
        
        # Project compression options
        self.menu_compression = wx.Menu()
        
        opt_compression_uncompressed = wx.MenuItem(self.menu_compression, ID_ZIP_NONE,
                GT(u'Uncompressed'), GT(u'Use uncompressed tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_compression_gz = wx.MenuItem(self.menu_compression, ID_ZIP_GZ,
                GT(u'Gzip'), GT(u'Use compressed Gzip tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_compression_bz2 = wx.MenuItem(self.menu_compression, ID_ZIP_BZ2,
                GT(u'Bzip2'), GT(u'Use compressed Bzip2 tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_compression_zip = wx.MenuItem(self.menu_compression, ID_ZIP_ZIP,
                GT(u'Zip'), GT(u'Use compressed zip file for project save format'),
                kind=wx.ITEM_RADIO)
        
        compression_opts = [
            opt_compression_uncompressed,
            opt_compression_gz,
            opt_compression_bz2,
            opt_compression_zip,
        ]
        
        if CMD_tar != None:
            opt_compression_xz = wx.MenuItem(self.menu_compression, ID_ZIP_XZ,
                    GT(u'XZ'), GT(u'Use compressed xz tarball for project save format'),
                    kind=wx.ITEM_RADIO)
            compression_opts.insert(3, opt_compression_xz)
        
        for OPT in compression_opts:
            self.menu_compression.AppendItem(OPT)
            wx.EVT_MENU(self.menu_compression, OPT.GetId(), self.OnSetCompression)
        
        # Default compression
        self.menu_compression.Check(ID_ZIP_BZ2, True)
        
        self.menu_opt.AppendSubMenu(self.menu_compression, GT(u'Project Compression'),
                GT(u'Set the compression type for project save output'))
        
        
        # *** Option Menu: open logs directory *** #
        
        if CMD_xdg_open:
            opt_logs_open = wx.MenuItem(self.menu_opt, ID_LOG_DIR_OPEN, GT(u'Open logs directory'))
            self.menu_opt.AppendItem(opt_logs_open)
            
            wx.EVT_MENU(self.menu_opt, ID_LOG_DIR_OPEN, self.OnLogDirOpen)
        
        # ----- Help Menu
        self.menu_help = wx.Menu()
        
        # ----- Version update
        self.version_check = wx.MenuItem(self.menu_help, ID_UPDATE, GT(u'Check for Update'))
        self.menu_help.AppendItem(self.version_check)
        self.menu_help.AppendSeparator()
        
        wx.EVT_MENU(self, ID_UPDATE, self.OnCheckUpdate)
        
        # Menu with links to the Debian Policy Manual webpages
        self.Policy = wx.Menu()
        
        globe = wx.Bitmap(u'{}/bitmaps/globe16.png'.format(PATH_app))
        self.DPM = wx.MenuItem(self.Policy, ID_DPM, GT(u'Debian Policy Manual'), u'http://www.debian.org/doc/debian-policy')
        self.DPM.SetBitmap(globe)
        self.DPMCtrl = wx.MenuItem(self.Policy, ID_DPMCtrl, GT(u'Control Files'), u'http://www.debian.org/doc/debian-policy/ch-controlfields.html')
        self.DPMCtrl.SetBitmap(globe)
        self.DPMLog = wx.MenuItem(self.Policy, ID_DPMLog, GT(u'Changelog'),
                u'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog')
        self.DPMLog.SetBitmap(globe)
        self.UPM = wx.MenuItem(self.Policy, ID_UPM, GT(u'Ubuntu Policy Manual'),
                u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/')
        self.UPM.SetBitmap(globe)
        self.DebFrmSrc = wx.MenuItem(self.Policy, 222, GT(u'Building debs from Source'),
                u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source') # This is here only temporarily for reference
        self.DebFrmSrc.SetBitmap(globe)
        self.LintianTags = wx.MenuItem(self.Policy, ID_LINT_TAGS, GT(u'Lintian Tags Explanation'),
                u'http://lintian.debian.org/tags-all.html')
        self.LintianTags.SetBitmap(globe)
        self.LintOverrides = wx.MenuItem(self.Policy, ID_LINT_OVERRIDE, GT(u'Overriding Lintian Tags'),
                u'https://lintian.debian.org/manual/section-2.4.html')
        self.LintOverrides.SetBitmap(globe)
        
        self.Policy.AppendItem(self.DPM)
        self.Policy.AppendItem(self.DPMCtrl)
        self.Policy.AppendItem(self.DPMLog)
        self.Policy.AppendItem(self.UPM)
        self.Policy.AppendItem(self.DebFrmSrc)
        self.Policy.AppendItem(self.LintianTags)
        self.Policy.AppendItem(self.LintOverrides)
        
        self.references = {
                    ID_DPM: u'http://www.debian.org/doc/debian-policy',
                    ID_DPMCtrl: u'http://www.debian.org/doc/debian-policy/ch-controlfields.html',
                    ID_DPMLog: u'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog',
                    ID_UPM: u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/',
                    222: u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source',
                    ID_LINT_TAGS: u'http://lintian.debian.org/tags-all.html',
                    ID_LINT_OVERRIDE: u'https://lintian.debian.org/manual/section-2.4.html',
                    }
        for R_ID in self.references:
            wx.EVT_MENU(self, R_ID, self.OpenPolicyManual)
        
        
        self.Help = wx.MenuItem(self.menu_help, wx.ID_HELP, GT(u'Help'), GT(u'Open a usage document'))
        self.About = wx.MenuItem(self.menu_help, wx.ID_ABOUT, GT(u'About'), GT(u'About Debreate'))
        
        self.menu_help.AppendMenu(-1, GT(u'Reference'), self.Policy)
        self.menu_help.AppendSeparator()
        self.menu_help.AppendItem(self.Help)
        self.menu_help.AppendItem(self.About)
        
        wx.EVT_MENU(self, wx.ID_HELP, self.OnHelp)
        wx.EVT_MENU(self, wx.ID_ABOUT, self.OnAbout)
        
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        
        self.menubar.Append(self.menu_file, GT(u'File'))
        self.menubar.Append(self.menu_page, GT(u'Page'))
        self.menubar.Append(self.menu_action, GT(u'Action'))
        self.menubar.Append(self.menu_opt, GT(u'Options'))
        self.menubar.Append(self.menu_help, GT(u'Help'))
        
        self.wizard = dbr.Wizard(self) # Binary
        self.wizard.EVT_CHANGE_PAGE(self, wx.ID_ANY, self.OnPageChanged)
        
        self.page_info = PageGreeting(self.wizard)
        self.page_info.SetInfo()
        self.page_control = PageControl(self.wizard)
        self.page_depends = PageDepends(self.wizard)
        self.page_files = PageFiles(self.wizard)
        
        # TODO: finish manpage section
        if DebugEnabled():
            self.page_man = PageMan(self.wizard)
        
        self.page_scripts = PageScripts(self.wizard)
        self.page_clog = PageChangelog(self.wizard)
        self.page_cpright = PageCopyright(self.wizard)
        self.page_launchers = PageLaunchers(self.wizard)
        self.page_build = PageBuild(self.wizard)
        
        self.all_pages = (
            self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_launchers, self.page_build
            )
        
        self.bin_pages = [
            self.page_info, self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_launchers, self.page_build
            ]
        
        if DebugEnabled():
            self.bin_pages.insert(4, self.page_man)
        
        self.wizard.SetPages(self.bin_pages)
        
        for M in self.menu_page.GetMenuItems():
            Logger.Debug(__name__, GT(u'Menu page: {}').format(M.GetLabel()))
            wx.EVT_MENU(self, M.GetId(), self.GoToPage)
        
        # ----- Layout
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.wizard, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.main_sizer)
        self.Layout()
        
        
        # Action menu events
        wx.EVT_MENU(self, action_build.GetId(), self.page_build.OnBuild)
        
        
        # Menu for debugging & running tests
        if DebugEnabled():
            self.menu_debug = wx.Menu()
            
            self.menubar.Append(self.menu_debug, GT(u'Debug'))
            
            self.menu_debug.AppendItem(wx.MenuItem(self.menu_debug, ID_LOG, GT(u'Show log'),
                    GT(u'Toggle debug log window'), kind=wx.ITEM_CHECK))
            
            self.log_window = LogWindow(self, Logger.GetLogFile())
            
            wx.EVT_MENU(self, ID_LOG, self.log_window.OnToggleWindow)
            
            # Window colors
            self.menu_debug.AppendItem(
                wx.MenuItem(self.menu_debug, ID_THEME, GT(u'Toggle window colors')))
            
            wx.EVT_MENU(self, ID_THEME, self.OnToggleTheme)
            
            # Create the log window
            #self.log_window = LogWindow(self, Logger.GetLogFile())
            #self.ShowLogWindow(True)
        
        
        self.loaded_project = None
        self.dirty = None
        
        # Initialize with clean project
        # TODO: This can be bypassed if opening a project from command line
        self.SetProjectDirty(False)
    
    
    def GetCompression(self):
        for Z in self.menu_compression.GetMenuItems():
            Z_ID = Z.GetId()
            if self.menu_compression.IsChecked(Z_ID):
                return compression_formats[Z_ID]
        
        default_compression = GetDefaultConfigValue(u'compression')
        
        Logger.Debug(__name__,
                GT(u'Setting compression to default value: {}'.format(default_compression)))
        
        return default_compression
    
    
    def GetCompressionId(self):
        for Z in self.menu_compression.GetMenuItems():
            Z_ID = Z.GetId()
            if self.menu_compression.IsChecked(Z_ID):
                return Z_ID
        
        Logger.Warning(__name__, GT(u'Did not find compatible compression ID, using default'))
        return DEFAULT_COMPRESSION_ID
    
    
    ## Changes wizard page from menu
    def GoToPage(self, event=None):
        page_id = None
        
        if event:
            page_id = event.GetId()
            Logger.Debug(__name__, GT(u'Page ID from menu event: {}').format(page_id))
        
        else:
            for M in self.menu_page.GetMenuItems():
                if M.IsChecked():
                    page_id = M.GetId()
                    Logger.Debug(__name__, GT(u'Page ID from menu item: {}').format(page_id))
                    break
        
        if page_id == None:
            Logger.Error(__name__, GT(u'Could not get page ID'))
            return
        
        self.wizard.ShowPage(page_id)
    
    
    ## Checks if current project is dirty
    def IsDirty(self):
        return self.dirty
    
    
    def IsNewProject(self):
        title = self.GetTitle()
        
        return bool(title == self.default_title)
    
    
    def IsSaved(self):
        title = self.GetTitle()
        
        return bool(title[-1] == u'*')
    
    
    ## Opens a dialog box with information about the program
    def OnAbout(self, event):
        about = dbr.AboutDialog(self)
        
        about.SetGraphic(u'{}/bitmaps/debreate64.png'.format(PATH_app))
        about.SetVersion(VERSION_string)
        about.SetDescription(GT(u'A package builder for Debian based systems'))
        about.SetAuthor(AUTHOR_name)
        
        about.SetWebsites((
            (GT(u'Homepage'), APP_homepage),
            (GT(u'GitHub Project'), APP_project_gh),
            (GT(u'Sourceforge Project'), APP_project_sf),
        ))
        
        about.AddJobs(
            AUTHOR_name,
            (
                GT(u'Head Developer'),
                GT(u'Packager'),
                u'{} (es, it)'.format(GT(u'Translation')),
            ),
            AUTHOR_email
        )
        
        about.AddJobs(
            u'Hugo Posnic',
            (
                GT(u'Code Contributor'),
                GT(u'Website Designer & Author'),
            ),
            u'hugo.posnic@gmail.com'
        )
        
        about.AddJob(u'Lander Usategui San Juan', GT(u'General Contributor'), u'lander@erlerobotics.com')
        
        about.AddTranslator(u'Karim Oulad Chalha', u'herr.linux88@gmail.com', u'ar', )
        about.AddTranslator(u'Philippe Dalet', u'philippe.dalet@ac-toulouse.fr', u'fr')
        about.AddTranslator(u'Zhmurkov Sergey', u'zhmsv@yandex.ru', u'ru')
        
        about.SetChangelog()
        
        about.SetLicense()
        
        about.ShowModal()
        about.Destroy()
    
    
    ### ***** Check for New Version ***** ###
    def OnCheckUpdate(self, event):
        if UsingDevelopmentVersion():
            wx.MessageDialog(self, GT(u'This is a development version. Update checking is disabled. '),
                    GT(u'Debreate'), wx.OK|wx.ICON_INFORMATION).ShowModal()
            
            return
        
        current = GetCurrentVersion()
        wx.SafeYield()
        Logger.Debug(__name__, GT(u'URL request result: {}').format(current))
        if isinstance(current, (URLError, HTTPError)):
            current = unicode(current)
            wx.MessageDialog(self, current, GT(u'Error'), wx.OK|wx.ICON_ERROR).ShowModal()
        elif isinstance(current, tuple) and current > VERSION_tuple:
            current = u'{}.{}.{}'.format(current[0], current[1], current[2])
            l1 = GT(u'Version {} is available!').format(current)
            l2 = GT(u'Would you like to go to Debreate\'s website?')
            update = wx.MessageDialog(self, u'{}\n\n{}'.format(l1, l2), GT(u'Debreate'), wx.YES_NO|wx.ICON_INFORMATION).ShowModal()
            if (update == wx.ID_YES):
                wx.LaunchDefaultBrowser(APP_homepage)
        elif isinstance(current, (unicode, str)):
            err_msg = GT(u'An error occurred attempting to retrieve version from remote website:')
            err_msg = u'{}\n\n{}'.format(err_msg, current)
            
            Logger.Error(__name__, err_msg)
            
            err = wx.MessageDialog(self, err_msg,
                    GT(u'Error'), wx.OK|wx.ICON_INFORMATION)
            err.CenterOnParent()
            err.ShowModal()
        else:
            err = wx.MessageDialog(self, GT(u'Debreate is up to date!'), GT(u'Debreate'), wx.OK|wx.ICON_INFORMATION)
            err.CenterOnParent()
            err.ShowModal()
    
    
    def OnHelp(self, event):
        if DebugEnabled():
            dbr.HelpDialog(self).ShowModal()
        
        else:
            # First tries to open pdf help file. If fails tries to open html help file. If fails opens debreate usage webpage
            wx.Yield()
            status = subprocess.call([u'xdg-open', u'{}/docs/usage.pdf'.format(PATH_app)])
            if status:
                wx.Yield()
                status = subprocess.call([u'xdg-open', u'{}/docs/usage'.format(PATH_app)])
            if status:
                wx.Yield()
                webbrowser.open(u'http://debreate.sourceforge.net/usage')
    
    
    ## Opens the logs directory in the system's default file manager
    def OnLogDirOpen(self, event=None):
        Logger.Debug(__name__, GT(u'Opening log directory ...'))
        
        subprocess.check_output([CMD_xdg_open, u'{}/logs'.format(PATH_local)], stderr=subprocess.STDOUT)
    
    
    ## FIXME: Unused???
    def OnMaximize(self, event):
        print(u'Maximized')
    
    
    ### ***** Menu Handlers ***** ###
    
    def OnNewProject(self, event):
        dia = wx.MessageDialog(self, GT(u'You will lose any unsaved information\n\nContinue?'),
                GT(u'Start New Project'), wx.YES_NO|wx.NO_DEFAULT)
        if dia.ShowModal() == wx.ID_YES:
            Logger.Debug(__name__, GT(u'Project loaded before OnNewProject: {}').format(self.ProjectLoaded()))
            
            self.wizard.ResetPagesInfo()
            self.loaded_project = None
            self.SetProjectDirty(False)
            
            Logger.Debug(__name__, GT(u'Project loaded after OnNewProject: {}').format(self.ProjectLoaded()))
            
            if DebugEnabled() and self.ProjectLoaded():
                Logger.Debug(__name__, GT(u'Loaded project: {}').format(self.loaded_project))
    
    
    def OnOpenProject(self, event=None):
        if self.IsDirty():
            Logger.Debug(__name__, GT(u'Attempting to open new project while dirty'))
            
            ignore_dirty = wx.MessageDialog(self,
                    GT(u'{} is unsaved, any changes will be lost').format(self.loaded_project),
                    GT(u'Confirm Open New Project'),
                    style=wx.YES_NO|wx.CANCEL|wx.CANCEL_DEFAULT|wx.ICON_WARNING)
                    
            ignore_dirty.SetExtendedMessage(GT(u'Continue without saving?'))
            ignore_dirty.SetYesNoLabels(GT(u'Continue'), GT(u'Save'))
            overwrite_dirty = ignore_dirty.ShowModal()
            
            if overwrite_dirty == wx.ID_CANCEL:
                Logger.Debug(__name__, GT(u'OnOpenProject; Cancelling open over dirty project'))
                return
            
            elif overwrite_dirty == wx.ID_NO:
                # ID_NO is save & continue
                
                if self.loaded_project == None:
                    err_msg = GT(u'No project loaded, cannot save')
                    Logger.Error(__name__, u'OnOpenProject; {}'.format(err_msg))
                    
                    err_dialog = ErrorDialog(self, err_msg)
                    err_dialog.ShowModal()
                    
                    return
                
                Logger.Debug(__name__, GT(u'OnOpenProject; Saving dirty project & continuing'))
                
                # Save & continue
                self.SaveProject(self.loaded_project)
            
            else:
                Logger.Debug(__name__, GT(u'OnOpenProject; Destroying changes of dirty project'))
        
        wc_z = GetDialogWildcards(ID_PROJ_Z)
        wc_l = GetDialogWildcards(ID_PROJ_L)
        wc_a = GetDialogWildcards(ID_PROJ_A)
        wc_t = GetDialogWildcards(ID_PROJ_T)
        
        wildcards = (
            wc_a[0], wc_a[1],
            wc_z[0], wc_z[1],
            wc_t[0], wc_t[1],
            wc_l[0], wc_l[1],
        )
        
        open_dialog = GetFileOpenDialog(self, GT(u'Open Debreate Project'), wildcards)
        
        # FIXME: Should have confirmation if current project marked "dirty"
        if ShowDialog(open_dialog):
            # Remove current project
            self.wizard.ResetPagesInfo()
            
            # Get the path and set the saved project
            opened_path = open_dialog.GetPath()
            
            self.OpenProject(opened_path)
    
    
    def OnPageChanged(self, event):
        ID = self.wizard.GetCurrentPageId()
        Logger.Debug(__name__, GT(u'Event: EVT_CHANGE_PAGE, Page ID: {}').format(ID))
        
        if not self.menu_page.IsChecked(ID):
            self.menu_page.Check(ID, True)
    
    
    def OnQuickBuild(self, event):
        QB = QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
    
    
    ## Shows a quit dialog & exits the application
    #  
    #  If user confirms quit, closes main window & exits.
    def OnQuit(self, event):
        confirm = wx.MessageDialog(self, GT(u'You will lose any unsaved information'), GT(u'Quit?'),
                                   wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_OK: # Show a dialog to confirm quit
            confirm.Destroy()
            
            maximized = self.IsMaximized()
            
            # Get window attributes and save to config file
            if maximized:    # Save default window settings if maximized
                WriteConfig(u'size', GetDefaultConfigValue(u'size'))
                WriteConfig(u'position', GetDefaultConfigValue(u'position'))
                WriteConfig(u'center', GetDefaultConfigValue(u'center'))
                WriteConfig(u'maximize', True)
            else:
                WriteConfig(u'size', (self.GetSize()[0], self.GetSize()[1]))
                WriteConfig(u'position', (self.GetPosition()[0], self.GetPosition()[1]))
                WriteConfig(u'center', False)
                WriteConfig(u'maximize', False)
            
            config_wdir = ReadConfig(u'workingdir')
            current_wdir = os.getcwd()
            
            # Workaround for issues with some dialogs not writing to config
            if config_wdir != current_wdir:
                WriteConfig(u'workingdir', current_wdir)
            
            self.Destroy()
        
        else:
            confirm.Destroy()
    
    
    def OnSaveProject(self, event=None):
        if not self.ProjectLoaded():
            self.OnSaveProjectAs(event)
            return
        
        # Only save if changes have been made
        if self.dirty:
            Logger.Debug(__name__, GT(u'Project loaded; Saving without showing dialog'))
            
            # Saving over currently loaded project
            if self.SaveProject(self.loaded_project) == dbrerrno.SUCCESS:
                self.SetProjectDirty(False)
    
    
    def OnSaveProjectAs(self, event=None):
        wildcards = (
            u'{} (.{})'.format(GT(u'Debreate project files'), PROJECT_ext), u'*.{}'.format(PROJECT_ext),
        )
        
        save_dialog = GetFileSaveDialog(self, GT(u'Save Debreate Project'), wildcards,
                PROJECT_ext)
        
        if ShowDialog(save_dialog):
            project_path = save_dialog.GetPath()
            project_filename = save_dialog.GetFilename()
            project_extension = save_dialog.GetExtension()
            
            Logger.Debug(__name__, GT(u'Project save path: {}').format(project_path))
            Logger.Debug(__name__, GT(u'Project save filename: {}').format(project_filename))
            Logger.Debug(__name__, GT(u'Project save extension: {}').format(project_extension))
            
            if self.SaveProject(project_path) == dbrerrno.SUCCESS:
                self.SetProjectDirty(False)
            
            return
        
        Logger.Debug(__name__, GT(u'Not saving project'))
    
    
    ## Writes compression value to config in real time
    def OnSetCompression(self, event=None):
        if event:
            event_id = event.GetId()
            Logger.Debug(__name__, GT(u'OnSetCompression; Event ID: {}').format(event_id))
            Logger.Debug(__name__, GT(u'OnSetCompression; Compression from event ID: {}').format(compression_formats[event_id]))
            
            if event_id in compression_formats:
                WriteConfig(u'compression', compression_formats[event_id])
                return
        
        Logger.Warning(__name__,
                GT(u'OnSetCompression; Could not write to config, ID not found in compression formats: {}').format(event_id))
                
    
    def OnToggleLogWindow(self, event=None):
        Logger.Debug(__name__, GT(u'Toggling log window'))
        
        if event != None:
            self.ShowLogWindow(self.menu_debug.IsChecked(ID_DEBUG))
            return
        
        self.menu_debug.Check(ID_DEBUG, self.log_window.IsShown())
    
    
    def OnToggleTheme(self, event=None):
        self.ToggleTheme(self)
    
    
    ## Shows or hides tooltips
    def OnToggleToolTips(self, event=None):
        enabled = self.opt_tooltips.IsChecked()
        wx.ToolTip.Enable(enabled)
        
        # Update configuration in realtime
        # TODO: Use realtime for more or all options
        WriteConfig(u'tooltips', enabled)
    
    
    # ----- Help Menu
    def OpenPolicyManual(self, event):
        EVENT_ID = event.GetId()  # Get the id for the webpage link we are opening
        webbrowser.open(self.references[EVENT_ID])
    
    
    ## Tests project type & calls correct method to read project file
    #  
    #  \param project_file
    #    \b \e unicode|str : Path to project file
    def OpenProject(self, project_file):
        mime_type = GetFileMimeType(project_file)
        
        Logger.Debug(__name__, GT(u'Opening project: {}').format(project_file))
        Logger.Debug(__name__, GT(u'Project mime type: {}').format(mime_type))
        
        project_opened = None
        if mime_type == u'text/plain':
            p_open = open(project_file, u'r')
            p_text = p_open.read()
            p_open.close()
            
            filename = os.path.split(project_file)[1]
            
            # Legacy projects should return None since we can't save in that format
            project_opened = self.OpenProjectLegacy(p_text, filename)
            
        else:
            project_opened = self.OpenProjectArchive(project_file, mime_type)
        
        Logger.Debug(__name__, GT(u'Project loaded before OnOpenProject: {}').format(self.ProjectLoaded()))
        
        if project_opened == dbrerrno.SUCCESS:
            self.loaded_project = project_file
        
        Logger.Debug(__name__, GT(u'Project loaded after OnOpenPreject: {}').format(self.ProjectLoaded()))
        
        if DebugEnabled() and self.ProjectLoaded():
            Logger.Debug(__name__, GT(u'Loaded project: {}').format(self.loaded_project))
    
    
    def OpenProjectArchive(self, filename, file_type):
        Logger.Debug(__name__, GT(u'Compressed project archive detected'))
        
        if file_type not in compression_mimetypes:
            Logger.Error(__name__, GT(u'Cannot open project with compression mime type "{}"'.format(file_type)))
            return dbrerrno.EBADFT
        
        compression_id = compression_mimetypes[file_type]
        
        z_format = compression_formats[compression_id]
        
        if z_format in (u'tar', u'zip'):
            z_format = u'r'
        else:
            z_format = u'r:{}'.format(z_format)
        
        Logger.Debug(__name__, GT(u'Opening compressed project with "{}" format').format(z_format))
        
        temp_dir = CreateTempDirectory()
        
        p_archive = CompressionHandler(compression_id)
        ret_code = p_archive.Uncompress(filename, temp_dir)
        
        if isinstance(ret_code, tuple) and ret_code[0]:
            ShowError(self, u'{}: {}'.format(GT(u'Project load error'), ret_code[1]), ret_code[0])
            return
        
        self.wizard.ImportPagesInfo(temp_dir)
        RemoveTempDirectory(temp_dir)
        
        # Mark project as loaded
        return dbrerrno.SUCCESS
    
    
    def OpenProjectLegacy(self, data, filename):
        Logger.Debug(__name__, GT(u'Legacy project format (text) detected'))
        def ProjectError():
            wx.MessageDialog(self, GT(u'Not a valid Debreate project'), GT(u'Error'),
    		                       style=wx.OK|wx.ICON_ERROR).ShowModal()
        
        if data == wx.EmptyString:
            ProjectError()
            return
        
        lines = data.split(u'\n')
        app = lines[0].split(u'-')[0].split(u'[')[1]
        
        if app != u'DEBREATE':
            ProjectError()
            return
            
        # Set title to show open project
        #self.SetTitle(u'Debreate - %s' % filename)
        
        # *** Get Control Data *** #
        control_data = data.split(u'<<CTRL>>\n')[1].split(u'\n<</CTRL>>')[0]
        depends_data = self.page_control.SetFieldDataLegacy(control_data)
        self.page_depends.SetFieldDataLegacy(depends_data)
        
        # *** Get Files Data *** #
        files_data = data.split(u'<<FILES>>\n')[1].split(u'\n<</FILES>>')[0]
        self.page_files.SetFieldDataLegacy(files_data)
        
        # *** Get Scripts Data *** #
        scripts_data = data.split(u'<<SCRIPTS>>\n')[1].split(u'\n<</SCRIPTS>>')[0]
        self.page_scripts.SetFieldDataLegacy(scripts_data)
        
        # *** Get Changelog Data *** #
        clog_data = data.split(u'<<CHANGELOG>>\n')[1].split(u'\n<</CHANGELOG>>')[0]
        self.page_clog.SetChangelogLegacy(clog_data)
        
        # *** Get Copyright Data *** #
        try:
            cpright_data = data.split(u'<<COPYRIGHT>>\n')[1].split(u'\n<</COPYRIGHT')[0]
            self.page_cpright.SetCopyright(cpright_data)
        except IndexError:
            pass
        
        # *** Get Menu Data *** #
        menu_data = data.split(u'<<MENU>>\n')[1].split(u'\n<</MENU>>')[0]
        self.page_launchers.SetFieldDataLegacy(menu_data)
        
        # Get Build Data
        build_data = data.split(u'<<BUILD>>\n')[1].split(u'\n<</BUILD')[0]#.split(u'\n')
        self.page_build.SetFieldDataLegacy(build_data)
    
    
    ## Checks if a project is loaded
    def ProjectLoaded(self):
        return self.loaded_project != None
    
    
    ## Saves project in archive format
    #  
    #  Supported uncompressed formats are unix tarball.
    #  Supported compressed formats are Gzip & Bzip2
    #    tarballs.
    #  Proposed formats are xz compressed tarball &
    #    zip compressed file.
    def SaveProject(self, target_path):
        Logger.Debug(__name__, GT(u'Saving in new project format'))
        Logger.Debug(__name__, GT(u'Saving to file {}').format(target_path))
        
        temp_dir = CreateTempDirectory()
        
        if not os.path.exists(temp_dir) or temp_dir == dbrerrno.EACCES:
            ShowError(self, u'{}: {}'.format(GT(u'Could not create staging directory'), temp_dir))
            return
        
        Logger.Debug(__name__, GT(u'Temp dir created: {}').format(temp_dir))
        
        working_path = os.path.dirname(target_path)
        output_filename = os.path.basename(target_path)
        
        Logger.Debug(
            __name__,
            u'Save project\n\tWorking path: {}\n\tFilename: {}\n\tTemp directory: {}'.format(working_path,
                                                                                        output_filename, temp_dir)
        )
        
        export_pages = (
            self.page_control,
            self.page_files,
            self.page_scripts,
            self.page_clog,
            self.page_cpright,
            self.page_launchers,
            self.page_build,
        )
        self.wizard.ExportPages(export_pages, temp_dir)
        
        p_archive = CompressionHandler(self.GetCompressionId())
        
        Logger.Debug(
                __name__,
                GT(u'Compressing "{}" with format: {} ({})').format
                    (
                        target_path,
                        p_archive.GetCompressionFormat(),
                        p_archive.GetCompressionMimetype()
                    )
        )
        
        if os.path.isfile(target_path) or target_path == self.loaded_project:
            Logger.Debug(__name__, GT(u'Overwriting old project file: {}').format(target_path))
        
        p_archive.Compress(temp_dir, u'{}'.format(target_path))
        
        if os.path.isfile(target_path):
            Logger.Debug(__name__, GT(u'Project saved: {}').format(target_path))
            
            RemoveTempDirectory(temp_dir)
            
            return dbrerrno.SUCCESS
        
        ShowError(self, u'{}: {}'.format(GT(u'Project save failed'), target_path))
    
    
    def SetProjectDirty(self, dirty=True):
        # Don't do anything if status isn't changing
        if not dirty == self.dirty:
            self.dirty = dirty
            self.menu_file.Enable(wx.ID_SAVE, dirty)
            
            delim = u' ({})'.format(GT(u'unsaved'))
            title = self.GetTitle()
            t_end = title[-len(delim):]
            
            Logger.Debug(__name__, GT(u'SetProjectDirty; Title: {}').format(title))
            Logger.Debug(__name__, GT(u'End of title: {}').format(t_end))
            
            if dirty and t_end != delim:
                self.SetTitle(u'{}{}'.format(title, delim))
            
            else:
                if t_end == delim:
                    self.SetTitle(u'{}'.format(title[:-len(delim)]))
            
            return
        
        Logger.Debug(__name__, GT(u'Dirty status not changing'))
    
    
    def SetSavedStatus(self, status):
        if status: # If status is changing to unsaved this is True
            title = self.GetTitle()
            if self.IsSaved() and title != default_title:
                self.SetTitle(u'{}*'.format(title))
    
    
    ## Sets compression in the main menu
    #  
    #  \param compression_id
    #        \b \e int : Compression ID to search for in menu iteration
    def SetCompression(self, compression_id):
        for Z in self.menu_compression.GetMenuItems():
            Z_ID = Z.GetId()
            
            if compression_id == Z_ID:
                Z.Check()
                
                Logger.Debug(__name__,
                        GT(u'Project compression set to "{}"'.format(compression_formats[Z_ID])))
                
                return
        
        Logger.Warning(__name__,
                GT(u'Attempt to set compression to non-existent value: {}'.format(compression_formats[compression_id])))
    
    
    def ShowLogWindow(self, show=True):
        Logger.Debug(__name__, GT(u'Show log window: {}').format(show))
        
        self.log_window.Show(show)
        
        if self.menu_debug.IsChecked(ID_DEBUG) != show:
            self.menu_debug.Check(ID_DEBUG, show)
    
    
    def ToggleTheme(self, window):
        for C in window.GetChildren():
            self.ToggleTheme(C)
    
        bg_color = window.GetBackgroundColour()
        fg_color = window.GetForegroundColour()
        
        window.SetBackgroundColour(fg_color)
        window.SetForegroundColour(bg_color)
