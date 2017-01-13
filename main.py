# -*- coding: utf-8 -*-

## \package main

# MIT licensing
# See: docs/LICENSE.txt


import os, subprocess, webbrowser, wx
from urllib2 import HTTPError
from urllib2 import URLError

from command_line           import parsed_args_s
from dbr.about              import AboutDialog
from dbr.config             import ConfCode
from dbr.config             import GetDefaultConfigValue
from dbr.config             import ReadConfig
from dbr.config             import WriteConfig
from dbr.dialogs            import ErrorDialog
from dbr.dialogs            import GetDialogWildcards
from dbr.dialogs            import GetFileOpenDialog
from dbr.dialogs            import GetFileSaveDialog
from dbr.dialogs            import ShowDialog
from dbr.dialogs            import ShowErrorDialog
from dbr.functions          import CreateTempDirectory
from dbr.functions          import GetCurrentVersion
from dbr.functions          import RemoveTempDirectory
from dbr.functions          import UsingDevelopmentVersion
from dbr.help               import HelpDialog
from dbr.icon               import Icon
from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import LogWindow
from dbr.log                import Logger
from dbr.menu               import MenuBar
from dbr.moduleaccess       import ModuleAccessCtrl
from dbr.quickbuild         import QuickBuild
from dbr.statusbar          import StatusBar
from dbr.wizard             import Wizard
from globals                import ident
from globals.application    import APP_homepage
from globals.application    import APP_project_gh
from globals.application    import APP_project_sf
from globals.application    import AUTHOR_email
from globals.application    import AUTHOR_name
from globals.application    import VERSION_string
from globals.application    import VERSION_tuple
from globals.bitmaps        import ICON_CLOCK
from globals.bitmaps        import ICON_GLOBE
from globals.bitmaps        import ICON_LOGO
from globals.bitmaps        import LOGO
from globals.compression    import CompressionHandler
from globals.compression    import DEFAULT_COMPRESSION_ID
from globals.compression    import compression_formats
from globals.compression    import compression_mimetypes
from globals.errorcodes     import dbrerrno
from globals.execute        import GetExecutable
from globals.fileio         import ReadFile
from globals.mime           import GetFileMimeType
from globals.paths          import PATH_app
from globals.paths          import PATH_local
from globals.project        import ID_PROJ_A
from globals.project        import ID_PROJ_L
from globals.project        import ID_PROJ_T
from globals.project        import ID_PROJ_Z
from globals.project        import PROJECT_ext
from globals.wizardhelper   import GetTopWindow
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


default_title = GT(u'Debreate - Debian Package Builder')


## TODO: Doxygen
class MainWindow(wx.Frame, ModuleAccessCtrl):
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, default_title, pos, size)
        ModuleAccessCtrl.__init__(self, __name__)
        
        # Make sure that this frame is set as the top window
        if not GetTopWindow() == self:
            Logger.Debug(__name__, GT(u'Setting MainWindow instance as top window'))
            
            wx.GetApp().SetTopWindow(self)
        
        if DebugEnabled():
            self.SetTitle(u'{} ({})'.format(default_title, GT(u'debugging')))
        
        self.SetMinSize(wx.Size(640, 400))
        
        # ----- Set Titlebar Icon
        self.SetIcon(Icon(LOGO))
        
        # ----- Status Bar
        stat_bar = StatusBar(self)
        
        # *** File Menu *** #
        self.m_file = wx.Menu()
        
        mi_new = wx.MenuItem(self.m_file, wx.ID_NEW, GT(u'New project'),
                help=GT(u'Start a new project'))
        mi_open = wx.MenuItem(self.m_file, wx.ID_OPEN, GT(u'Open'),
                help=GT(u'Open a previously saved project'))
        mi_save = wx.MenuItem(self.m_file, wx.ID_SAVE, GT(u'Save'),
                help=GT(u'Save current project'))
        mi_saveas = wx.MenuItem(self.m_file, wx.ID_SAVEAS, GT(u'Save as'),
                help=GT(u'Save current project with a new filename'))
        
        # Quick Build
        mi_quickbuild = wx.MenuItem(self.m_file, ident.QBUILD, GT(u'Quick Build'),
                GT(u'Build a package from an existing build tree'))
        mi_quickbuild.SetBitmap(ICON_CLOCK)
        
        mi_quit = wx.MenuItem(self.m_file, wx.ID_EXIT, GT(u'Quit'),
                help=GT(u'Exit Debreate'))
        
        self.m_file.AppendItem(mi_new)
        self.m_file.AppendItem(mi_open)
        self.m_file.AppendItem(mi_save)
        self.m_file.AppendItem(mi_saveas)
        self.m_file.AppendSeparator()
        self.m_file.AppendItem(mi_quickbuild)
        self.m_file.AppendSeparator()
        self.m_file.AppendItem(mi_quit)
        
        # *** Page Menu *** #
        ## This menu is filled from dbr.wizard.Wizard
        self.m_page = wx.Menu()
        
        # *** Action Menu *** #
        m_action = wx.Menu()
        
        # FIXME: Use global ID???
        mi_build = wx.MenuItem(m_action, wx.NewId(), GT(u'Build'),
                GT(u'Start building .deb package'))
        
        m_action.AppendItem(mi_build)
        
        # ----- Options Menu
        m_opt = wx.Menu()
        
        # Show/Hide tooltips
        self.opt_tooltips = wx.MenuItem(m_opt, ident.TOOLTIPS, GT(u'Show tooltips'),
                GT(u'Show or hide tooltips'), kind=wx.ITEM_CHECK)
        
        m_opt.AppendItem(self.opt_tooltips)
        
        show_tooltips = ReadConfig(u'tooltips')
        if show_tooltips != ConfCode.KEY_NO_EXIST:
            self.opt_tooltips.Check(show_tooltips)
        
        else:
            self.opt_tooltips.Check(GetDefaultConfigValue(u'tooltips'))
        
        self.OnToggleToolTips()
        
        # Dialogs options
        self.mi_dialogs = wx.MenuItem(m_opt, ident.DIALOGS, GT(u'Use Custom Dialogs'),
            GT(u'Use System or Custom Save/Open Dialogs'), kind=wx.ITEM_CHECK)
        
        # FIXME: Disabled until fixed
        #m_opt.AppendItem(self.mi_dialogs)
        
        # Project compression options
        self.m_compress = wx.Menu()
        
        opt_z_none = wx.MenuItem(self.m_compress, ident.ZIP_NONE,
                GT(u'Uncompressed'), GT(u'Use uncompressed tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_z_gz = wx.MenuItem(self.m_compress, ident.ZIP_GZ,
                GT(u'Gzip'), GT(u'Use compressed Gzip tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_z_bz2 = wx.MenuItem(self.m_compress, ident.ZIP_BZ2,
                GT(u'Bzip2'), GT(u'Use compressed Bzip2 tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_z_zip = wx.MenuItem(self.m_compress, ident.ZIP_ZIP,
                GT(u'Zip'), GT(u'Use compressed zip file for project save format'),
                kind=wx.ITEM_RADIO)
        
        opts_compress = [
            opt_z_none,
            opt_z_gz,
            opt_z_bz2,
            opt_z_zip,
        ]
        
        if GetExecutable(u'tar') != None:
            opt_z_xz = wx.MenuItem(self.m_compress, ident.ZIP_XZ,
                    GT(u'XZ'), GT(u'Use compressed xz tarball for project save format'),
                    kind=wx.ITEM_RADIO)
            opts_compress.insert(3, opt_z_xz)
        
        for OPT in opts_compress:
            self.m_compress.AppendItem(OPT)
            wx.EVT_MENU(self.m_compress, OPT.GetId(), self.OnSetCompression)
        
        # Default compression
        self.m_compress.Check(ident.ZIP_BZ2, True)
        
        m_opt.AppendSubMenu(self.m_compress, GT(u'Project Compression'),
                GT(u'Set the compression type for project save output'))
        
        # *** Option Menu: open logs directory *** #
        
        if GetExecutable(u'xdg-open'):
            mi_logs_dir = wx.MenuItem(m_opt, ident.OPENLOGS, GT(u'Open logs directory'))
            m_opt.AppendItem(mi_logs_dir)
            
            wx.EVT_MENU(m_opt, ident.OPENLOGS, self.OnLogDirOpen)
        
        # ----- Help Menu
        m_help = wx.Menu()
        
        # ----- Version update
        mi_update = wx.MenuItem(m_help, ident.UPDATE, GT(u'Check for Update'))
        mi_update.SetBitmap(ICON_LOGO)
        
        m_help.AppendItem(mi_update)
        m_help.AppendSeparator()
        
        # Menu with links to the Debian Policy Manual webpages
        self.m_policy = wx.Menu()
        
        m_dpm = wx.MenuItem(self.m_policy, ident.DPM, GT(u'Debian Policy Manual'),
                u'http://www.debian.org/doc/debian-policy')
        m_dpm.SetBitmap(ICON_GLOBE)
        m_dpm_ctrl = wx.MenuItem(self.m_policy, ident.DPMCtrl, GT(u'Control Files'),
                u'http://www.debian.org/doc/debian-policy/ch-controlfields.html')
        m_dpm_ctrl.SetBitmap(ICON_GLOBE)
        m_dpm_log = wx.MenuItem(self.m_policy, ident.DPMLog, GT(u'Changelog'),
                u'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog')
        m_dpm_log.SetBitmap(ICON_GLOBE)
        m_upm = wx.MenuItem(self.m_policy, ident.UPM, GT(u'Ubuntu Policy Manual'),
                u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/')
        m_upm.SetBitmap(ICON_GLOBE)
        m_deb_src = wx.MenuItem(self.m_policy, 222, GT(u'Building debs from Source'),
                u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source') # This is here only temporarily for reference
        m_deb_src.SetBitmap(ICON_GLOBE)
        m_lint_tags = wx.MenuItem(self.m_policy, ident.LINT_TAGS, GT(u'Lintian Tags Explanation'),
                u'http://lintian.debian.org/tags-all.html')
        m_lint_tags.SetBitmap(ICON_GLOBE)
        m_lint_overrides = wx.MenuItem(self.m_policy, ident.LINT_OVERRIDE, GT(u'Overriding Lintian Tags'),
                u'https://lintian.debian.org/manual/section-2.4.html')
        m_lint_overrides.SetBitmap(ICON_GLOBE)
        m_launchers = wx.MenuItem(self.m_policy, ident.LAUNCHERS, GT(u'Launchers / Desktop entries'),
                u'https://www.freedesktop.org/wiki/Specifications/desktop-entry-spec/')
        m_launchers.SetBitmap(ICON_GLOBE)
        
        self.m_policy.AppendItem(m_dpm)
        self.m_policy.AppendItem(m_dpm_ctrl)
        self.m_policy.AppendItem(m_dpm_log)
        self.m_policy.AppendItem(m_upm)
        self.m_policy.AppendItem(m_deb_src)
        self.m_policy.AppendItem(m_lint_tags)
        self.m_policy.AppendItem(m_lint_overrides)
        self.m_policy.AppendItem(m_launchers)
        
        lst_policy_ids = (
            ident.DPM,
            ident.DPMCtrl,
            ident.DPMLog,
            ident.UPM,
            222,
            ident.LINT_TAGS,
            ident.LINT_OVERRIDE,
            ident.LAUNCHERS,
            )
        
        for ID in lst_policy_ids:
            wx.EVT_MENU(self, ID, self.OpenPolicyManual)
        
        mi_help = wx.MenuItem(m_help, wx.ID_HELP, GT(u'Help'), GT(u'Open a usage document'))
        mi_about = wx.MenuItem(m_help, wx.ID_ABOUT, GT(u'About'), GT(u'About Debreate'))
        
        m_help.AppendMenu(-1, GT(u'Reference'), self.m_policy)
        m_help.AppendSeparator()
        m_help.AppendItem(mi_help)
        m_help.AppendItem(mi_about)
        
        menubar = MenuBar(self)
        
        menubar.Append(self.m_file, GT(u'File'), wx.ID_FILE)
        menubar.Append(self.m_page, GT(u'Page'), ident.PAGE)
        menubar.Append(m_action, GT(u'Action'), ident.ACTION)
        menubar.Append(m_opt, GT(u'Options'), ident.OPTIONS)
        menubar.Append(m_help, GT(u'Help'), wx.ID_HELP)
        
        self.wizard = Wizard(self)
        
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
        
        bin_pages = [
            self.page_info, self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_launchers, self.page_build
            ]
        
        if DebugEnabled():
            bin_pages.insert(4, self.page_man)
        
        self.wizard.SetPages(bin_pages)
        
        # Menu for debugging & running tests
        if DebugEnabled():
            self.m_debug = wx.Menu()
            
            menubar.Append(self.m_debug, GT(u'Debug'), ident.DEBUG)
            
            self.m_debug.AppendItem(wx.MenuItem(self.m_debug, ident.LOG, GT(u'Show log'),
                    GT(u'Toggle debug log window'), kind=wx.ITEM_CHECK))
            
            if u'log-window' in parsed_args_s:
                self.m_debug.Check(ident.LOG, True)
            
            self.log_window = LogWindow(self, Logger.GetLogFile())
            
            # Window colors
            self.m_debug.AppendItem(
                wx.MenuItem(self.m_debug, ident.THEME, GT(u'Toggle window colors')))
            
            wx.EVT_MENU(self, ident.LOG, self.log_window.OnToggleWindow)
            wx.EVT_MENU(self, ident.THEME, self.OnToggleTheme)
        
        self.loaded_project = None
        self.dirty = None
        
        # Initialize with clean project
        # TODO: This can be bypassed if opening a project from command line
        self.SetProjectDirty(False)
        
        # *** Layout *** #
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.wizard, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        wx.EVT_MENU(self, wx.ID_NEW, self.OnNewProject)
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnOpenProject)
        
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnSaveProject)
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveProjectAs)
        wx.EVT_MENU(self, ident.QBUILD, self.OnQuickBuild)
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnQuit)
        wx.EVT_CLOSE(self, self.OnQuit) #custom close event shows a dialog box to confirm quit
        
        wx.EVT_MENU(self, ident.TOOLTIPS, self.OnToggleToolTips)
        
        wx.EVT_MENU(self, ident.UPDATE, self.OnCheckUpdate)
        
        wx.EVT_MENU(self, wx.ID_HELP, self.OnHelp)
        wx.EVT_MENU(self, wx.ID_ABOUT, self.OnAbout)
        
        self.wizard.EVT_CHANGE_PAGE(self, wx.ID_ANY, self.OnPageChanged)
        
        for M in self.m_page.GetMenuItems():
            Logger.Debug(__name__, GT(u'Menu page: {}').format(M.GetLabel()))
            wx.EVT_MENU(self, M.GetId(), self.GoToPage)
        
        # Action menu events
        wx.EVT_MENU(self, mi_build.GetId(), self.page_build.OnBuild)
    
    
    ## TODO: Doxygen
    def GetCompression(self):
        for Z in self.m_compress.GetMenuItems():
            Z_ID = Z.GetId()
            if self.m_compress.IsChecked(Z_ID):
                return compression_formats[Z_ID]
        
        default_compression = GetDefaultConfigValue(u'compression')
        
        Logger.Debug(__name__,
                GT(u'Setting compression to default value: {}'.format(default_compression)))
        
        return default_compression
    
    
    ## TODO: Doxygen
    def GetCompressionId(self):
        for Z in self.m_compress.GetMenuItems():
            Z_ID = Z.GetId()
            if self.m_compress.IsChecked(Z_ID):
                return Z_ID
        
        Logger.Warning(__name__, GT(u'Did not find compatible compression ID, using default'))
        
        return DEFAULT_COMPRESSION_ID
    
    
    ## Retrieves the Wizard instance
    #  
    #  \return
    #        dbr.wizard.Wizard
    def GetWizard(self):
        return self.wizard
    
    
    ## Changes wizard page from menu
    def GoToPage(self, event=None):
        page_id = None
        
        if event:
            page_id = event.GetId()
            Logger.Debug(__name__, GT(u'Page ID from menu event: {}').format(page_id))
        
        else:
            for M in self.m_page.GetMenuItems():
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
    
    
    ## TODO: Doxygen
    def IsNewProject(self):
        title = self.GetTitle()
        
        return bool(title == self.default_title)
    
    
    ## TODO: Doxygen
    def IsSaved(self):
        title = self.GetTitle()
        
        return bool(title[-1] == u'*')
    
    
    ## Opens a dialog box with information about the program
    def OnAbout(self, event=None):
        about = AboutDialog(self)
        
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
    
    
    ## Checks for new release availability
    def OnCheckUpdate(self, event=None):
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
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Appears to have errors
    def OnHelp(self, event=None):
        if DebugEnabled():
            HelpDialog(self).ShowModal()
        
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
        
        subprocess.check_output([GetExecutable(u'xdg-open'), u'{}/logs'.format(PATH_local)], stderr=subprocess.STDOUT)
    
    
    ## TODO: Doxygen
    def OnNewProject(self, event=None):
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
    
    
    ## TODO: Doxygen
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
            
            # wx.ID_NO means save & continue
            elif overwrite_dirty == wx.ID_NO:
                if self.loaded_project == None:
                    err_msg = GT(u'No project loaded, cannot save')
                    Logger.Error(__name__, u'OnOpenProject; {}'.format(err_msg))
                    
                    err_dialog = ErrorDialog(self, err_msg)
                    err_dialog.ShowModal()
                    
                    return
                
                Logger.Debug(__name__, GT(u'OnOpenProject; Saving dirty project & continuing'))
                
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
    
    
    ## TODO: Doxygen
    def OnPageChanged(self, event=None):
        ID = self.wizard.GetCurrentPageId()
        Logger.Debug(__name__, GT(u'Event: EVT_CHANGE_PAGE, Page ID: {}').format(ID))
        
        if not self.m_page.IsChecked(ID):
            self.m_page.Check(ID, True)
    
    
    ## TODO: Doxygen
    def OnQuickBuild(self, event=None):
        QB = QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
    
    
    ## Shows a quit dialog & exits the application
    #  
    #  If user confirms quit, closes main window & exits.
    def OnQuit(self, event=None):
        confirm = wx.MessageDialog(self, GT(u'You will lose any unsaved information'), GT(u'Quit?'),
                                   wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        
        if confirm.ShowModal() == wx.ID_OK:
            confirm.Destroy()
            
            maximized = self.IsMaximized()
            
            # Get window attributes and save to config file
            
            # Save default window settings if maximized
            # FIXME: Better solution?
            if maximized:
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
    
    
    ## TODO: Doxygen
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
    
    
    ## TODO: Doxygen
    def OnSaveProjectAs(self, event=None):
        wildcards = (
            u'{} (.{})'.format(GT(u'Debreate project files'), PROJECT_ext),
            u'*.{}'.format(PROJECT_ext),
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
    
    
    ## TODO: Doxygen
    def OnToggleLogWindow(self, event=None):
        Logger.Debug(__name__, GT(u'Toggling log window'))
        
        if event != None:
            self.ShowLogWindow(self.m_debug.IsChecked(ident.DEBUG))
            return
        
        self.m_debug.Check(ident.DEBUG, self.log_window.IsShown())
    
    
    ## TODO: Doxygen
    def OnToggleTheme(self, event=None):
        self.ToggleTheme(self)
    
    
    ## Shows or hides tooltips
    def OnToggleToolTips(self, event=None):
        enabled = self.opt_tooltips.IsChecked()
        wx.ToolTip.Enable(enabled)
        
        # Update configuration in realtime
        # TODO: Use realtime for more or all options
        WriteConfig(u'tooltips', enabled)
    
    
    ## Opens web links from the help menu
    def OpenPolicyManual(self, event=None):
        if isinstance(event, wx.CommandEvent):
            event_id = event.GetId()
        
        elif isinstance(event, int):
            event_id = event
        
        else:
            Logger.Error(__name__,
                    u'Cannot open policy manual link with object type {}'.format(type(event)))
            
            return
        
        url = self.m_policy.GetHelpString(event_id)
        webbrowser.open(url)
    
    
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
            p_text = ReadFile(project_file)
            
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
    
    
    ## TODO: Doxygen
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
            ShowErrorDialog(u'{}: {}'.format(GT(u'Project load error'), ret_code[1]),
                    ret_code[0], parent=self)
            return
        
        self.wizard.ImportPagesInfo(temp_dir)
        RemoveTempDirectory(temp_dir)
        
        # Mark project as loaded
        return dbrerrno.SUCCESS
    
    
    ## TODO: Doxygen
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
        # FIXME:
        #self.SetTitle(u'Debreate - {}'.format(filename))
        
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
        m_data = data.split(u'<<MENU>>\n')[1].split(u'\n<</MENU>>')[0]
        self.page_launchers.SetFieldDataLegacy(m_data)
        
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
            ShowErrorDialog(u'{}: {}'.format(GT(u'Could not create staging directory'), temp_dir),
                    parent=self)
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
        
        ShowErrorDialog(u'{}: {}'.format(GT(u'Project save failed'), target_path), parent=self)
    
    
    ## Sets compression in the main menu
    #  
    #  \param compression_id
    #        \b \e int : Compression ID to search for in menu iteration
    def SetCompression(self, compression_id):
        for Z in self.m_compress.GetMenuItems():
            Z_ID = Z.GetId()
            
            if compression_id == Z_ID:
                Z.Check()
                
                Logger.Debug(__name__,
                        GT(u'Project compression set to "{}"'.format(compression_formats[Z_ID])))
                
                return
        
        Logger.Debug(__name__,
                GT(u'Urecognized compression ID: {}'.format(compression_id)))
    
    
    ## TODO: Doxygen
    def SetProjectDirty(self, dirty=True):
        # Don't do anything if status isn't changing
        if not dirty == self.dirty:
            self.dirty = dirty
            self.m_file.Enable(wx.ID_SAVE, dirty)
            
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
    
    
    ## TODO: Doxygen
    def SetSavedStatus(self, status):
        if status: # If status is changing to unsaved this is True
            title = self.GetTitle()
            if self.IsSaved() and title != default_title:
                self.SetTitle(u'{}*'.format(title))
    
    
    ## TODO: Doxygen
    def ShowLogWindow(self, show=True):
        Logger.Debug(__name__, GT(u'Show log window: {}').format(show))
        
        self.log_window.Show(show)
        
        if self.m_debug.IsChecked(ident.DEBUG) != show:
            self.m_debug.Check(ident.DEBUG, show)
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Finish definition
    def ToggleTheme(self, window):
        for C in window.GetChildren():
            self.ToggleTheme(C)
        
        bg_color = window.GetBackgroundColour()
        fg_color = window.GetForegroundColour()
        
        window.SetBackgroundColour(fg_color)
        window.SetForegroundColour(bg_color)
