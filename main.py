# -*- coding: utf-8 -*-

## \package main

# MIT licensing
# See: docs/LICENSE.txt


import os, subprocess, webbrowser, wx
from urllib2 import HTTPError
from urllib2 import URLError

from command_line           import parsed_args_s
from dbr.config             import ConfCode
from dbr.config             import GetDefaultConfigValue
from dbr.config             import ReadConfig
from dbr.config             import WriteConfig
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
from globals.moduleaccess   import ModuleAccessCtrl
from globals.paths          import PATH_app
from globals.paths          import PATH_local
from globals.project        import ID_PROJ_A
from globals.project        import ID_PROJ_L
from globals.project        import ID_PROJ_T
from globals.project        import ID_PROJ_Z
from globals.project        import PROJECT_ext
from globals.wizardhelper   import GetTopWindow
from startup.tests          import GetTestList
from ui.about               import AboutDialog
from ui.dialog              import ConfirmationDialog
from ui.dialog              import DetailedMessageDialog
from ui.dialog              import ErrorDialog
from ui.dialog              import GetDialogWildcards
from ui.dialog              import GetFileOpenDialog
from ui.dialog              import GetFileSaveDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.distcache           import DistNamesCacheDialog
from ui.menu                import MenuBar
from ui.quickbuild          import QuickBuild
from ui.statusbar           import StatusBar
from ui.wizard              import Wizard
from wiz_bin.build          import Panel as PageBuild
from wiz_bin.changelog      import Panel as PageChangelog
from wiz_bin.control        import Panel as PageControl
from wiz_bin.copyright      import Panel as PageCopyright
from wiz_bin.depends        import Panel as PageDepends
from wiz_bin.files          import Panel as PageFiles
from wiz_bin.greeting       import Panel as PageGreeting
from wiz_bin.launchers      import Panel as PageLaunchers
from wiz_bin.manuals        import Panel as PageMan
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
        
        testing = u'alpha' in GetTestList() or DebugEnabled()
        
        if DebugEnabled():
            self.SetTitle(u'{} ({})'.format(default_title, GT(u'debugging')))
        
        self.SetMinSize(wx.Size(640, 400))
        
        # ----- Set Titlebar Icon
        self.SetIcon(Icon(LOGO))
        
        # ----- Status Bar
        StatusBar(self)
        
        # *** File Menu *** #
        self.menu_file = wx.Menu()
        
        mitm_new = wx.MenuItem(self.menu_file, wx.ID_NEW, GT(u'New project'),
                help=GT(u'Start a new project'))
        mitm_open = wx.MenuItem(self.menu_file, wx.ID_OPEN, GT(u'Open'),
                help=GT(u'Open a previously saved project'))
        mitm_save = wx.MenuItem(self.menu_file, wx.ID_SAVE, GT(u'Save'),
                help=GT(u'Save current project'))
        mitm_saveas = wx.MenuItem(self.menu_file, wx.ID_SAVEAS, GT(u'Save as'),
                help=GT(u'Save current project with a new filename'))
        
        # Quick Build
        mitm_quickbuild = wx.MenuItem(self.menu_file, ident.QBUILD, GT(u'Quick Build'),
                GT(u'Build a package from an existing build tree'))
        mitm_quickbuild.SetBitmap(ICON_CLOCK)
        
        mitm_quit = wx.MenuItem(self.menu_file, wx.ID_EXIT, GT(u'Quit'),
                help=GT(u'Exit Debreate'))
        
        self.menu_file.AppendItem(mitm_new)
        self.menu_file.AppendItem(mitm_open)
        self.menu_file.AppendItem(mitm_save)
        self.menu_file.AppendItem(mitm_saveas)
        self.menu_file.AppendSeparator()
        self.menu_file.AppendItem(mitm_quickbuild)
        
        if testing:
            mitm_alien = wx.MenuItem(self.menu_file, ident.ALIEN, GT(u'Convert packages'))
            self.menu_file.AppendItem(mitm_alien)
        
        self.menu_file.AppendSeparator()
        self.menu_file.AppendItem(mitm_quit)
        
        # *** Page Menu *** #
        ## This menu is filled from ui.wizard.Wizard
        self.menu_page = wx.Menu()
        
        # *** Action Menu *** #
        menu_action = wx.Menu()
        
        # FIXME: Use global ID???
        mitm_build = wx.MenuItem(menu_action, wx.NewId(), GT(u'Build'),
                GT(u'Start building .deb package'))
        
        menu_action.AppendItem(mitm_build)
        
        # ----- Options Menu
        menu_opt = wx.Menu()
        
        # Show/Hide tooltips
        self.opt_tooltips = wx.MenuItem(menu_opt, ident.TOOLTIPS, GT(u'Show tooltips'),
                GT(u'Show or hide tooltips'), kind=wx.ITEM_CHECK)
        
        # A bug with wx 2.8 does not allow tooltips to be toggled off
        if wx.MAJOR_VERSION > 2:
            menu_opt.AppendItem(self.opt_tooltips)
        
        if menu_opt.FindItemById(ident.TOOLTIPS):
            show_tooltips = ReadConfig(u'tooltips')
            if show_tooltips != ConfCode.KEY_NO_EXIST:
                self.opt_tooltips.Check(show_tooltips)
            
            else:
                self.opt_tooltips.Check(GetDefaultConfigValue(u'tooltips'))
            
            self.OnToggleToolTips()
        
        # Project compression options
        self.menu_compress = wx.Menu()
        
        opt_z_none = wx.MenuItem(self.menu_compress, ident.ZIP_NONE,
                GT(u'Uncompressed'), GT(u'Use uncompressed tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_z_gz = wx.MenuItem(self.menu_compress, ident.ZIP_GZ,
                GT(u'Gzip'), GT(u'Use compressed Gzip tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_z_bz2 = wx.MenuItem(self.menu_compress, ident.ZIP_BZ2,
                GT(u'Bzip2'), GT(u'Use compressed Bzip2 tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_z_zip = wx.MenuItem(self.menu_compress, ident.ZIP_ZIP,
                GT(u'Zip'), GT(u'Use compressed zip file for project save format'),
                kind=wx.ITEM_RADIO)
        
        opts_compress = [
            opt_z_none,
            opt_z_gz,
            opt_z_bz2,
            opt_z_zip,
        ]
        
        if GetExecutable(u'tar') != None:
            opt_z_xz = wx.MenuItem(self.menu_compress, ident.ZIP_XZ,
                    GT(u'XZ'), GT(u'Use compressed xz tarball for project save format'),
                    kind=wx.ITEM_RADIO)
            opts_compress.insert(3, opt_z_xz)
        
        for OPT in opts_compress:
            self.menu_compress.AppendItem(OPT)
            wx.EVT_MENU(self.menu_compress, OPT.GetId(), self.OnSetCompression)
        
        # Default compression
        self.menu_compress.Check(ident.ZIP_BZ2, True)
        
        menu_opt.AppendSubMenu(self.menu_compress, GT(u'Project Compression'),
                GT(u'Set the compression type for project save output'))
        
        # *** Option Menu: open logs directory *** #
        
        if GetExecutable(u'xdg-open'):
            mitm_logs_open = wx.MenuItem(menu_opt, ident.OPENLOGS, GT(u'Open logs directory'))
            menu_opt.AppendItem(mitm_logs_open)
            
            wx.EVT_MENU(menu_opt, ident.OPENLOGS, self.OnLogDirOpen)
        
        # *** OS distribution names cache *** #
        
        opt_distname_cache = wx.MenuItem(menu_opt, ident.DIST, GT(u'Update dist names cache'),
                GT(u'Creates/Updates list of distribution names for changelog page'))
        menu_opt.AppendItem(opt_distname_cache)
        
        # ----- Help Menu
        menu_help = wx.Menu()
        
        # ----- Version update
        mitm_update = wx.MenuItem(menu_help, ident.UPDATE, GT(u'Check for update'),
                GT(u'Check if a new version is available for download'))
        mitm_update.SetBitmap(ICON_LOGO)
        
        menu_help.AppendItem(mitm_update)
        menu_help.AppendSeparator()
        
        # Menu with links to the Debian Policy Manual webpages
        self.menu_policy = wx.Menu()
        
        policy_links = (
            (ident.DPM, GT(u'Debian Policy Manual'),
                    u'https://www.debian.org/doc/debian-policy',),
            (ident.DPMCtrl, GT(u'Control files'),
                    u'https://www.debian.org/doc/debian-policy/ch-controlfields.html',),
            (ident.DPMLog, GT(u'Changelog'),
                    u'https://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog',),
            (ident.UPM, GT(u'Ubuntu Policy Manual'),
                    u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/',),
            (ident.LINT_TAGS, GT(u'Lintian Tags Explanation'),
                    u'https://lintian.debian.org/tags-all.html',),
            (ident.LINT_OVERRIDE, GT(u'Overriding Lintian Tags'),
                    u'https://lintian.debian.org/manual/section-2.4.html',),
            (ident.LAUNCHERS, GT(u'Launchers / Desktop entries'),
                    u'https://www.freedesktop.org/wiki/Specifications/desktop-entry-spec/',),
            # Unofficial links
            None,
            # FIXME: Use wx.NewId()
            (222, GT(u'Building debs from Source'),
                    u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source',), # This is here only temporarily for reference
            (ident.MAN, GT(u'Writing manual pages'),
                    u'https://liw.fi/manpages/',),
            )
        
        for LINK in policy_links:
            if not LINK:
                self.menu_policy.AppendSeparator()
            
            elif len(LINK) > 2:
                link_id = LINK[0]
                label = LINK[1]
                url = LINK[2]
                
                if len(LINK) > 3:
                    icon = LINK[3]
                
                else:
                    icon = ICON_GLOBE
                
                mitm = wx.MenuItem(self.menu_policy, link_id, label, url)
                mitm.SetBitmap(icon)
                self.menu_policy.AppendItem(mitm)
                
                wx.EVT_MENU(self, link_id, self.OpenPolicyManual)
        
        mitm_help = wx.MenuItem(menu_help, wx.ID_HELP, GT(u'Help'), GT(u'Open a usage document'))
        mitm_about = wx.MenuItem(menu_help, wx.ID_ABOUT, GT(u'About'), GT(u'About Debreate'))
        
        menu_help.AppendMenu(-1, GT(u'Reference'), self.menu_policy)
        menu_help.AppendSeparator()
        menu_help.AppendItem(mitm_help)
        menu_help.AppendItem(mitm_about)
        
        menubar = MenuBar(self)
        
        menubar.Append(self.menu_file, GT(u'File'), wx.ID_FILE)
        menubar.Append(self.menu_page, GT(u'Page'), ident.PAGE)
        menubar.Append(menu_action, GT(u'Action'), ident.ACTION)
        
        if menu_opt.GetMenuItemCount():
            menubar.Append(menu_opt, GT(u'Options'), ident.OPTIONS)
        
        menubar.Append(menu_help, GT(u'Help'), wx.ID_HELP)
        
        self.wizard = Wizard(self)
        
        self.page_info = PageGreeting(self.wizard)
        self.page_info.SetInfo()
        self.page_control = PageControl(self.wizard)
        self.page_depends = PageDepends(self.wizard)
        self.page_files = PageFiles(self.wizard)
        
        # TODO: finish manpage section
        if testing:
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
        
        if testing:
            bin_pages.insert(4, self.page_man)
        
        self.wizard.SetPages(bin_pages)
        
        # Menu for debugging & running tests
        if DebugEnabled():
            self.menu_debug = wx.Menu()
            
            menubar.Append(self.menu_debug, GT(u'Debug'), ident.DEBUG)
            
            self.menu_debug.AppendItem(wx.MenuItem(self.menu_debug, ident.LOG, GT(u'Show log'),
                    GT(u'Toggle debug log window'), kind=wx.ITEM_CHECK))
            
            if u'log-window' in parsed_args_s:
                self.menu_debug.Check(ident.LOG, True)
            
            self.log_window = LogWindow(self, Logger.GetLogFile())
            
            # Window colors
            self.menu_debug.AppendItem(
                wx.MenuItem(self.menu_debug, ident.THEME, GT(u'Toggle window colors')))
            
            wx.EVT_MENU(self, ident.LOG, self.log_window.OnToggleWindow)
            wx.EVT_MENU(self, ident.THEME, self.OnToggleTheme)
        
        self.loaded_project = None
        
        # *** Current Project Status *** #
        
        # FIXME: Deprecated/Remove
        self.dirty = None
        
        self.ProjectDirty = False
        self.dirty_mark = u' *'
        
        # Initialize with clean project
        # TODO: This can be bypassed if opening a project from command line
        self.SetProjectDirty(False)
        
        # *** Event Handling *** #
        
        wx.EVT_MENU(self, wx.ID_NEW, self.OnNewProject)
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnOpenProject)
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnSaveProject)
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveProjectAs)
        wx.EVT_MENU(self, ident.QBUILD, self.OnQuickBuild)
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnQuit)
        
        wx.EVT_MENU(self, ident.TOOLTIPS, self.OnToggleToolTips)
        wx.EVT_MENU(self, ident.DIST, self.OnUpdateDistNamesCache)
        
        wx.EVT_MENU(self, ident.UPDATE, self.OnCheckUpdate)
        wx.EVT_MENU(self, wx.ID_HELP, self.OnHelp)
        wx.EVT_MENU(self, wx.ID_ABOUT, self.OnAbout)
        
        self.wizard.EVT_CHANGE_PAGE(self, wx.ID_ANY, self.OnPageChanged)
        
        for M in self.menu_page.GetMenuItems():
            Logger.Debug(__name__, GT(u'Menu page: {}').format(M.GetLabel()))
            wx.EVT_MENU(self, M.GetId(), self.GoToPage)
        
        # Action menu events
        wx.EVT_MENU(self, mitm_build.GetId(), self.page_build.OnBuild)
        
        wx.EVT_CLOSE(self, self.OnQuit) # Custom close event shows a dialog box to confirm quit
        
        # *** Layout *** #
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.wizard, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## TODO: Doxygen
    def GetCompression(self):
        for Z in self.menu_compress.GetMenuItems():
            Z_ID = Z.GetId()
            if self.menu_compress.IsChecked(Z_ID):
                return compression_formats[Z_ID]
        
        default_compression = GetDefaultConfigValue(u'compression')
        
        Logger.Debug(__name__,
                GT(u'Setting compression to default value: {}'.format(default_compression)))
        
        return default_compression
    
    
    ## TODO: Doxygen
    def GetCompressionId(self):
        for Z in self.menu_compress.GetMenuItems():
            Z_ID = Z.GetId()
            if self.menu_compress.IsChecked(Z_ID):
                return Z_ID
        
        Logger.Warning(__name__, GT(u'Did not find compatible compression ID, using default'))
        
        return DEFAULT_COMPRESSION_ID
    
    
    ## Retrieves the Wizard instance
    #  
    #  \return
    #        ui.wizard.Wizard
    def GetWizard(self):
        return self.wizard
    
    
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
        update_test = u'update-fail' in GetTestList()
        
        if UsingDevelopmentVersion() and not update_test:
            DetailedMessageDialog(GetTopWindow(), GT(u'Update'),
                    text=GT(u'Update checking is disabled in development versions')).ShowModal()
            return
        
        wx.SafeYield()
        
        if update_test:
            # Set a bad url to force error
            current = GetCurrentVersion(u'http://dummyurl.blah/')
        
        else:
            current = GetCurrentVersion()
        
        Logger.Debug(__name__, GT(u'URL request result: {}').format(current))
        
        error_remote = GT(u'An error occurred attempting to contact remote website')
        
        if isinstance(current, (URLError, HTTPError)):
            current = unicode(current)
            ShowErrorDialog(error_remote, current)
        
        elif isinstance(current, tuple) and current > VERSION_tuple:
            current = u'{}.{}.{}'.format(current[0], current[1], current[2])
            l1 = GT(u'Version {} is available!').format(current)
            l2 = GT(u'Would you like to go to Debreate\'s website?')
            if ConfirmationDialog(GetTopWindow(), GT(u'Update'), u'{}\n\n{}'.format(l1, l2)).Confirmed():
                wx.LaunchDefaultBrowser(APP_homepage)
        
        elif isinstance(current, (unicode, str)):
            ShowErrorDialog(error_remote, current)
        
        else:
            DetailedMessageDialog(GetTopWindow(), GT(u'Debreate'), text=GT(u'Debreate is up to date!')).ShowModal()
    
    
    ## Action to take when 'Help' is selected from the help menu
    #  
    #  Opens a help dialog if using 'alpha' test. Otherwise, opens
    #  PDF usage document. If openening usage document fails, attempts
    #  to open web browser in remote usage page.
    #  TODO: Use dialog as main method
    def OnHelp(self, event=None):
        if u'alpha' in GetTestList():
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
        confirm = ConfirmationDialog(self, GT(u'Start New Project'),
                text=GT(u'You will lose any unsaved information\n\nContinue?'))
        
        if confirm.Confirmed():
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
        
        if not self.menu_page.IsChecked(ID):
            self.menu_page.Check(ID, True)
    
    
    ## TODO: Doxygen
    def OnQuickBuild(self, event=None):
        QB = QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
    
    
    ## Shows a dialog to confirm quit and write window settings to config file
    def OnQuit(self, event=None):
        if ConfirmationDialog(self, GT(u'Quit?'),
                text=GT(u'You will lose any unsaved information')).Confirmed():
            
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
                WriteConfig(u'position', self.GetPositionTuple())
                WriteConfig(u'size', self.GetSizeTuple())
                WriteConfig(u'center', False)
                WriteConfig(u'maximize', False)
            
            config_wdir = ReadConfig(u'workingdir')
            current_wdir = os.getcwd()
            
            # Workaround for issues with some dialogs not writing to config
            if config_wdir != current_wdir:
                WriteConfig(u'workingdir', current_wdir)
            
            self.Destroy()
    
    
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
            self.ShowLogWindow(self.menu_debug.IsChecked(ident.DEBUG))
            return
        
        self.menu_debug.Check(ident.DEBUG, self.log_window.IsShown())
    
    
    ## TODO: Doxygen
    def OnToggleTheme(self, event=None):
        self.ToggleTheme(self)
    
    
    ## Shows or hides tooltips
    def OnToggleToolTips(self, event=None):
        enabled = self.opt_tooltips.IsChecked()
        wx.ToolTip.Enable(enabled)
        
        WriteConfig(u'tooltips', enabled)
    
    
    ## Opens a dialog for creating/updating list of distribution names cache file
    def OnUpdateDistNamesCache(self, event=None):
        DistNamesCacheDialog().ShowModal()
    
    
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
        
        url = self.menu_policy.GetHelpString(event_id)
        webbrowser.open(url)
    
    
    ## Tests project type & calls correct method to read project file
    #  
    #  \param project_file
    #    \b \e unicode|str : Path to project file
    def OpenProject(self, project_file):
        Logger.Debug(__name__, u'Opening project: {}'.format(project_file))
        
        mime_type = GetFileMimeType(project_file)
        
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
        
        # *** Get Control Data *** #
        control_data = data.split(u'<<CTRL>>\n')[1].split(u'\n<</CTRL>>')[0]
        depends_data = self.page_control.Set(control_data)
        self.page_depends.Set(depends_data)
        
        # *** Get Files Data *** #
        files_data = data.split(u'<<FILES>>\n')[1].split(u'\n<</FILES>>')[0]
        self.page_files.Set(files_data)
        
        # *** Get Scripts Data *** #
        scripts_data = data.split(u'<<SCRIPTS>>\n')[1].split(u'\n<</SCRIPTS>>')[0]
        self.page_scripts.Set(scripts_data)
        
        # *** Get Changelog Data *** #
        clog_data = data.split(u'<<CHANGELOG>>\n')[1].split(u'\n<</CHANGELOG>>')[0]
        self.page_clog.Set(clog_data)
        
        # *** Get Copyright Data *** #
        try:
            cpright_data = data.split(u'<<COPYRIGHT>>\n')[1].split(u'\n<</COPYRIGHT')[0]
            self.page_cpright.Set(cpright_data)
        
        except IndexError:
            pass
        
        # *** Get Menu Data *** #
        m_data = data.split(u'<<MENU>>\n')[1].split(u'\n<</MENU>>')[0]
        self.page_launchers.Set(m_data)
        
        # Get Build Data
        build_data = data.split(u'<<BUILD>>\n')[1].split(u'\n<</BUILD')[0]#.split(u'\n')
        self.page_build.Set(build_data)
    
    
    ## TODO: Doxygen
    #  
    #  \return
    #    \b \e True if 'dirty' status was changed
    def ProjectChanged(self, event=None):
        changed = False
        
        if not self.ProjectDirty:
            self.ProjectDirty = True
            self.SetTitle(u'{}{}'.format(self.GetTitle(), self.dirty_mark))
            
            changed = True
        
        if DebugEnabled():
            Logger.Debug(__name__, u'MainWindow.OnProjectChanged: {}'.format(changed), newline=True)
            print(u'  Object: {}'.format(event.GetEventObject()))
        
        return changed
    
    
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
        for Z in self.menu_compress.GetMenuItems():
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
        
        if self.menu_debug.IsChecked(ident.DEBUG) != show:
            self.menu_debug.Check(ident.DEBUG, show)
    
    
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
