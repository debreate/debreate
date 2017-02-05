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
from dbr.event              import EVT_CHANGE_PAGE
from dbr.functions          import GetCurrentVersion
from dbr.functions          import UsingDevelopmentVersion
from dbr.help               import HelpDialog
from dbr.icon               import Icon
from dbr.language           import GT
from dbr.log                import DebugEnabled
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
from globals.ident          import genid
from globals.ident          import menuid
from globals.ident          import pgid
from globals.ident          import refid
from globals.mime           import GetFileMimeType
from globals.moduleaccess   import ModuleAccessCtrl
from globals.paths          import PATH_app
from globals.paths          import PATH_local
from globals.project        import ID_PROJ_A
from globals.project        import ID_PROJ_L
from globals.project        import ID_PROJ_T
from globals.project        import ID_PROJ_Z
from globals.project        import PROJECT_ext
from globals.stage          import CreateStage
from globals.stage          import RemoveStage
from globals.strings        import GS
from startup.tests          import GetTestList
from ui.about               import AboutDialog
from ui.dialog              import ConfirmSaveDialog
from ui.dialog              import ConfirmationDialog
from ui.dialog              import DetailedMessageDialog
from ui.dialog              import GetDialogWildcards
from ui.dialog              import GetFileOpenDialog
from ui.dialog              import GetFileSaveDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.distcache           import DistNamesCacheDialog
from ui.layout              import BoxSizer
from ui.menu                import MenuBar
from ui.quickbuild          import QuickBuild
from ui.statusbar           import StatusBar
from ui.wizard              import Wizard
from wizbin.build           import Panel as PageBuild
from wizbin.changelog       import Panel as PageChangelog
from wizbin.control         import Panel as PageControl
from wizbin.copyright       import Panel as PageCopyright
from wizbin.depends         import Panel as PageDepends
from wizbin.files           import Panel as PageFiles
from wizbin.greeting        import Panel as PageGreeting
from wizbin.launchers       import Panel as PageLaunchers
from wizbin.manuals         import Panel as PageMan
from wizbin.scripts         import Panel as PageScripts


default_title = GT(u'Debreate - Debian Package Builder')


## TODO: Doxygen
class MainWindow(wx.Frame, ModuleAccessCtrl):
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, default_title, pos, size)
        ModuleAccessCtrl.__init__(self, __name__)
        
        # Make sure that this frame is set as the top window
        if not wx.GetApp().GetTopWindow() == self:
            Logger.Debug(__name__, GT(u'Setting MainWindow instance as top window'))
            
            wx.GetApp().SetTopWindow(self)
        
        testing = u'alpha' in GetTestList() or DebugEnabled()
        
        if DebugEnabled():
            self.SetTitle(u'{} ({})'.format(default_title, GT(u'debugging')))
        
        self.SetMinSize(wx.Size(640, 400))
        
        # ----- Set Titlebar Icon
        self.SetIcon(Icon(LOGO))
        
        # *** Status Bar *** #
        StatusBar(self)
        
        # *** Menus *** #
        menubar = MenuBar(self)
        
        menu_file = wx.Menu()
        
        menubar.Append(menu_file, GT(u'File'), menuid.FILE)
        # This menu is filled from wiz.wizard.Wizard.SetPages
        menubar.Append(wx.Menu(), GT(u'Page'), menuid.PAGE)
        
        # *** File Menu *** #
        
        mitems_file = [
            (menuid.NEW, GT(u'New project'), GT(u'Start a new project'),),
            (menuid.OPEN, GT(u'Open'), GT(u'Open a previously saved project'),),
            (menuid.SAVE, GT(u'Save'), GT(u'Save current project'),),
            (menuid.SAVEAS, GT(u'Save as'), GT(u'Save current project with a new filename'),),
            None,
            (menuid.QBUILD, GT(u'Quick Build'), GT(u'Build a package from an existing build tree'), ICON_CLOCK,),
            None,
            (menuid.EXIT, GT(u'Quit'), GT(u'Exit Debreate'),),
            ]
        
        if testing:
            mitems_file.append((ident.ALIEN, GT(u'Convert packages'), GT(u'Convert between package types')))
        
        # Adding all menus to menu bar
        
        mitems = (
            mitems_file,
            )
        
        for menu_list in mitems:
            for mitem in menu_list:
                print(u'Instance: {}'.format(type(mitem)))
                if not mitem:
                    menu_file.AppendSeparator()
                
                else:
                    itm = wx.MenuItem(menu_file, mitem[0], mitem[1], mitem[2])
                    if len(mitem) > 3:
                        itm.SetBitmap(mitem[3])
                    
                    menu_file.AppendItem(itm)
        
        # *** Action Menu *** #
        menu_action = wx.Menu()
        
        mitm_build = wx.MenuItem(menu_action, genid.BUILD, GT(u'Build'),
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
            (refid.DPM, GT(u'Debian Policy Manual'),
                    u'https://www.debian.org/doc/debian-policy',),
            (refid.DPMCtrl, GT(u'Control files'),
                    u'https://www.debian.org/doc/debian-policy/ch-controlfields.html',),
            (refid.DPMLog, GT(u'Changelog'),
                    u'https://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog',),
            (refid.UPM, GT(u'Ubuntu Policy Manual'),
                    u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/',),
            (refid.LINT_TAGS, GT(u'Lintian Tags Explanation'),
                    u'https://lintian.debian.org/tags-all.html',),
            (refid.LINT_OVERRIDE, GT(u'Overriding Lintian Tags'),
                    u'https://lintian.debian.org/manual/section-2.4.html',),
            (refid.LAUNCHERS, GT(u'Launchers / Desktop entries'),
                    u'https://www.freedesktop.org/wiki/Specifications/desktop-entry-spec/',),
            # Unofficial links
            None,
            (refid.DEBSRC, GT(u'Building debs from Source'),
                    u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source',), # This is here only temporarily for reference
            (refid.MAN, GT(u'Writing manual pages'),
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
        
        menubar.Append(self.menu_page, GT(u'Page'), menuid.PAGE)
        menubar.Append(menu_action, GT(u'Action'), menuid.ACTION)
        
        if menu_opt.GetMenuItemCount():
            menubar.Append(menu_opt, GT(u'Options'), menuid.OPTIONS)
        
        menubar.Append(menu_help, GT(u'Help'), menuid.HELP)
        
        self.Wizard = Wizard(self)
        
        # Menu for debugging & running tests
        if DebugEnabled():
            self.menu_debug = wx.Menu()
            
            menubar.Append(self.menu_debug, GT(u'Debug'), menuid.DEBUG)
            
            self.menu_debug.AppendItem(wx.MenuItem(self.menu_debug, ident.LOG, GT(u'Show log'),
                    GT(u'Toggle debug log window'), kind=wx.ITEM_CHECK))
            
            if u'log-window' in parsed_args_s:
                self.menu_debug.Check(ident.LOG, True)
            
            self.log_window = None
            
            # Window colors
            self.menu_debug.AppendItem(
                wx.MenuItem(self.menu_debug, ident.THEME, GT(u'Toggle window colors')))
            
            wx.EVT_MENU(self, ident.THEME, self.OnToggleTheme)
        
        # *** Current Project Status *** #
        
        self.LoadedProject = None
        self.ProjectDirty = False
        self.dirty_mark = u' *'
        
        self.menu_file.Enable(wx.ID_SAVE, self.ProjectDirty)
        
        # *** Event Handling *** #
        
        wx.EVT_MENU(self, menuid.NEW, self.OnProjectNew)
        wx.EVT_MENU(self, menuid.OPEN, self.OnProjectOpen)
        wx.EVT_MENU(self, menuid.SAVE, self.OnProjectSave)
        wx.EVT_MENU(self, menuid.SAVEAS, self.OnProjectSaveAs)
        wx.EVT_MENU(self, menuid.QBUILD, self.OnQuickBuild)
        wx.EVT_MENU(self, menuid.EXIT, self.OnQuit)
        
        wx.EVT_MENU(self, menuid.TOOLTIPS, self.OnToggleToolTips)
        wx.EVT_MENU(self, menuid.DIST, self.OnUpdateDistNamesCache)
        
        wx.EVT_MENU(self, menuid.UPDATE, self.OnCheckUpdate)
        wx.EVT_MENU(self, menuid.HELP, self.OnHelp)
        wx.EVT_MENU(self, menuid.ABOUT, self.OnAbout)
        
        self.Bind(EVT_CHANGE_PAGE, self.OnWizardBtnPage)
        
        # Custom close event shows a dialog box to confirm quit
        wx.EVT_CLOSE(self, self.OnQuit)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.Wizard, 1, wx.EXPAND)
        
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
        
        Logger.Warn(__name__, GT(u'Did not find compatible compression ID, using default'))
        
        return DEFAULT_COMPRESSION_ID
    
    
    ## Retrieves the Wizard instance
    #  
    #  \return
    #        wiz.wizard.Wizard
    def GetWizard(self):
        return self.Wizard
    
    
    ## Sets the pages in the wiz.wizard.Wizard instance
    def InitWizard(self):
        pg_info = PageGreeting(self.Wizard)
        pg_info.SetInfo()
        PageControl(self.Wizard)
        PageDepends(self.Wizard)
        PageFiles(self.Wizard)
        
        # TODO: finish manpage section
        if u'alpha' in GetTestList() or DebugEnabled():
            PageMan(self.Wizard)
        
        PageScripts(self.Wizard)
        PageChangelog(self.Wizard)
        PageCopyright(self.Wizard)
        PageLaunchers(self.Wizard)
        pg_build = PageBuild(self.Wizard)
        
        # Action menu events
        wx.EVT_MENU(self, genid.BUILD, pg_build.OnBuild)
        
        self.Wizard.InitPages()
    
    
    ## Opens a dialog box with information about the program
    def OnAbout(self, event=None):
        about = AboutDialog(self)
        
        about.SetGraphic(LOGO)
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
        
        about.AddJob(u'Benji Park', GT(u'Button Base Image Designer'))
        
        about.SetChangelog()
        
        about.SetLicense()
        
        about.ShowModal()
        about.Destroy()
    
    
    ## Checks for new release availability
    def OnCheckUpdate(self, event=None):
        update_test = u'update-fail' in GetTestList()
        
        if UsingDevelopmentVersion() and not update_test:
            DetailedMessageDialog(self, GT(u'Update'),
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
            current = GS(current)
            ShowErrorDialog(error_remote, current)
        
        elif isinstance(current, tuple) and current > VERSION_tuple:
            current = u'{}.{}.{}'.format(current[0], current[1], current[2])
            l1 = GT(u'Version {} is available!').format(current)
            l2 = GT(u'Would you like to go to Debreate\'s website?')
            if ConfirmationDialog(self, GT(u'Update'), u'{}\n\n{}'.format(l1, l2)).Confirmed():
                wx.LaunchDefaultBrowser(APP_homepage)
        
        elif isinstance(current, (unicode, str)):
            ShowErrorDialog(error_remote, current)
        
        else:
            DetailedMessageDialog(self, GT(u'Debreate'), text=GT(u'Debreate is up to date!')).ShowModal()
    
    
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
    
    
    ## Changes wizard page from menu
    def OnMenuChangePage(self, event=None):
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
        
        self.Wizard.ShowPage(page_id)
    
    
    ## TODO: Doxygen
    def OnQuickBuild(self, event=None):
        QB = QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
    
    
    ## Shows a dialog to confirm quit and write window settings to config file
    def OnQuit(self, event=None):
        if self.ProjectDirty:
            if not ConfirmationDialog(self, GT(u'Quit?'),
                    text=GT(u'You will lose any unsaved information')).Confirmed():
                
                return
        
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
    
    
    ## Handles events from fields that are essential to project
    #  
    #  \return
    #    \b \e True if 'dirty' status was changed
    def OnProjectChanged(self, event=None):
        changed = False
        
        if not self.ProjectDirty:
            changed = self.ProjectSetDirty()
        
        if DebugEnabled():
            Logger.Debug(__name__, u'MainWindow.OnProjectChanged: {}'.format(changed), newline=True)
            print(u'  Object: {}'.format(event.GetEventObject()))
        
        return changed
    
    
    ## Clears current project & restores fields to defaults
    #  
    #  \return
    #    \b \e True if project state is reset to default
    def OnProjectNew(self, event=None):
        Logger.Debug(__name__, GT(u'Project loaded before OnProjectNew: {}').format(self.ProjectIsLoaded()))
        
        return self.ProjectClose()
    
    
    ## TODO: Doxygen
    def OnProjectOpen(self, event=None):
        return self.ProjectOpen()
    
    
    ## TODO: Doxygen
    def OnProjectSave(self, event=None):
        # Open a file save dialog for new projects
        # FIXME: Necessary?
        if not self.ProjectIsLoaded():
            self.OnProjectSaveAs(event)
            
            return
        
        # 'Save' menu item is enabled
        Logger.Debug(__name__, GT(u'Project loaded; Saving without showing dialog'))
        
        # Saving over currently loaded project
        self.ProjectSave(self.LoadedProject)
    
    
    ## TODO: Doxygen
    def OnProjectSaveAs(self, event=None):
        self.ProjectSaveAs()
    
    
    ## Writes compression value to config in real time
    def OnSetCompression(self, event=None):
        if event:
            event_id = event.GetId()
            Logger.Debug(__name__, GT(u'OnSetCompression; Event ID: {}').format(event_id))
            Logger.Debug(__name__, GT(u'OnSetCompression; Compression from event ID: {}').format(compression_formats[event_id]))
            
            if event_id in compression_formats:
                WriteConfig(u'compression', compression_formats[event_id])
                return
        
        Logger.Warn(__name__,
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
    
    
    ## Updates the page menu to reflect current page
    def OnWizardBtnPage(self, event=None):
        ID = self.Wizard.GetCurrentPageId()
        Logger.Debug(__name__, GT(u'Event: EVT_CHANGE_PAGE, Page ID: {}').format(ID))
        
        if not self.menu_page.IsChecked(ID):
            self.menu_page.Check(ID, True)
    
    
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
    
    
    ## Closes currently open project & resets pages to default
    #  
    #  \return
    #    \b \e True if the project was closed, \b \e False if should not continue
    def ProjectClose(self):
        if not self.ProjectIsDirty():
            self.Wizard.ResetPagesInfo()
            self.LoadedProject = None
            
            # Everything okay to continue
            return True
        
        msg_l1 = GT(u'{} is unsaved, any changes will be lost').format(self.LoadedProject)
        confirmed = ConfirmSaveDialog(self, GT(u'Unsaved Changes'),
                text=GT(u'{}\n\n{}'.format(msg_l1, GT(u'Continue?')))).ShowModal()
        
        if confirmed == wx.ID_SAVE:
            if self.LoadedProject:
                Logger.Debug(__name__, u'Saving modified project ...')
                
                self.ProjectSave(self.LoadedProject)
            
            else:
                Logger.Debug(__name__, u'Saving new project ...')
                
                # Open file save dialog for new project
                if self.ProjectSaveAs() != dbrerrno.SUCCESS:
                    return False
        
        elif confirmed != wx.ID_OK:
            return False
        
        self.Wizard.ResetPagesInfo()
        self.LoadedProject = None
        self.ProjectSetDirty(False)
        
        return not self.ProjectIsLoaded()
    
    
    ## Retrieves filename of loaded project
    def ProjectGetLoaded(self):
        return self.LoadedProject
    
    
    ## Checks if current project is dirty
    def ProjectIsDirty(self):
        return self.ProjectDirty
    
    
    ## Checks if a project is loaded
    def ProjectIsLoaded(self):
        return self.LoadedProject != None
    
    
    ## Tests project type & calls correct method to read project file
    #  
    #  Opens a file dialog if not project file is specified.
    #  \param project_file
    #    \b \e unicode|str : Path to project file
    def ProjectOpen(self, project_file=None):
        Logger.Debug(__name__, u'Opening project: {}'.format(project_file))
        
        # Need to show file open dialog because no project file was specified
        if not project_file:
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
            if not ShowDialog(open_dialog):
                return dbrerrno.ECNCLD
            
            # Get the path and set the saved project
            project_file = open_dialog.GetPath()
        
        # Failsafe check that file exists
        if not os.path.isfile(project_file):
            err_l1 = GT(u'Cannot open project:')
            err_details = GT(u'File does not exist')
            
            ShowErrorDialog(u'{} {}'.format(err_l1, project_file), err_details)
            
            return dbrerrno.ENOENT
        
        # Check for unsaved changes & reset project to defaults
        if not self.ProjectClose():
            return dbrerrno.ECNCLD
        
        mime_type = GetFileMimeType(project_file)
        
        Logger.Debug(__name__, GT(u'Project mime type: {}').format(mime_type))
        
        opened = None
        if mime_type == u'text/plain':
            p_text = ReadFile(project_file)
            
            filename = os.path.split(project_file)[1]
            
            # Legacy projects should return None since we can't save in that format
            opened = self.ProjectOpenLegacy(p_text, filename)
        
        else:
            opened = self.ProjectOpenArchive(project_file, mime_type)
        
        Logger.Debug(__name__, GT(u'Project loaded before OnProjectOpen: {}').format(self.ProjectIsLoaded()))
        
        if opened == dbrerrno.SUCCESS:
            self.LoadedProject = project_file
            
            # Set project 'unmodified' for newly opened project
            self.ProjectSetDirty(False)
        
        Logger.Debug(__name__, GT(u'Project loaded after OnOpenPreject: {}').format(self.ProjectIsLoaded()))
        
        if DebugEnabled() and self.ProjectIsLoaded():
            Logger.Debug(__name__, GT(u'Loaded project: {}').format(self.LoadedProject))
        
        return opened
    
    
    ## TODO: Doxygen
    def ProjectOpenArchive(self, filename, file_type):
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
        
        stage = CreateStage()
        
        p_archive = CompressionHandler(compression_id)
        ret_code = p_archive.Uncompress(filename, stage)
        
        if isinstance(ret_code, tuple) and ret_code[0]:
            ShowErrorDialog(u'{}: {}'.format(GT(u'Project load error'), ret_code[1]),
                    ret_code[0], parent=self)
            
            return dbrerrno.EBADFT
        
        self.Wizard.ImportPagesInfo(stage)
        RemoveStage(stage)
        
        # Mark project as loaded
        return dbrerrno.SUCCESS
    
    
    ## TODO: Doxygen
    def ProjectOpenLegacy(self, data, filename):
        Logger.Debug(__name__, GT(u'Legacy project format (text) detected'))
        
        def ProjectError():
            wx.MessageDialog(self, GT(u'Not a valid Debreate project'), GT(u'Error'),
                      style=wx.OK|wx.ICON_ERROR).ShowModal()
        
        if data == wx.EmptyString:
            ProjectError()
            return dbrerrno.EBADFT
        
        lines = data.split(u'\n')
        app = lines[0].split(u'-')[0].split(u'[')[1]
        
        if app != u'DEBREATE':
            ProjectError()
            return dbrerrno.EBADFT
        
        # *** Get Control Data *** #
        control_data = data.split(u'<<CTRL>>\n')[1].split(u'\n<</CTRL>>')[0]
        depends_data = self.Wizard.GetPage(pgid.CONTROL).Set(control_data)
        self.Wizard.GetPage(pgid.DEPENDS).Set(depends_data)
        
        # *** Get Files Data *** #
        files_data = data.split(u'<<FILES>>\n')[1].split(u'\n<</FILES>>')[0]
        self.Wizard.GetPage(pgid.FILES).Set(files_data)
        
        # *** Get Scripts Data *** #
        scripts_data = data.split(u'<<SCRIPTS>>\n')[1].split(u'\n<</SCRIPTS>>')[0]
        self.Wizard.GetPage(pgid.SCRIPTS).Set(scripts_data)
        
        # *** Get Changelog Data *** #
        clog_data = data.split(u'<<CHANGELOG>>\n')[1].split(u'\n<</CHANGELOG>>')[0]
        self.Wizard.GetPage(pgid.CHANGELOG).Set(clog_data)
        
        # *** Get Copyright Data *** #
        try:
            cpright_data = data.split(u'<<COPYRIGHT>>\n')[1].split(u'\n<</COPYRIGHT')[0]
            self.Wizard.GetPage(pgid.COPYRIGHT).Set(cpright_data)
        
        except IndexError:
            pass
        
        # *** Get Menu Data *** #
        m_data = data.split(u'<<MENU>>\n')[1].split(u'\n<</MENU>>')[0]
        self.Wizard.GetPage(pgid.LAUNCHERS).Set(m_data)
        
        # Get Build Data
        build_data = data.split(u'<<BUILD>>\n')[1].split(u'\n<</BUILD')[0]
        self.Wizard.GetPage(pgid.BUILD).Set(build_data)
        
        self.ProjectSetDirty(False)
        
        # Legacy projects should return None since we can't save in that format
        return None
    
    
    ## Saves project in archive format
    #  
    #  Supported uncompressed formats are unix tarball.
    #  Supported compressed formats are Gzip & Bzip2
    #    tarballs.
    #  Proposed formats are xz compressed tarball &
    #    zip compressed file.
    #  \param target_path
    #    Absolute output filename
    def ProjectSave(self, target_path):
        Logger.Debug(__name__, GT(u'Saving in new project format'))
        Logger.Debug(__name__, GT(u'Saving to file {}').format(target_path))
        
        stage = CreateStage()
        
        if not os.path.exists(stage) or stage == dbrerrno.EACCES:
            ShowErrorDialog(u'{}: {}'.format(GT(u'Could not create staging directory'), stage),
                    parent=self)
            
            return dbrerrno.EACCES
        
        Logger.Debug(__name__, GT(u'Temp dir created: {}').format(stage))
        
        working_path = os.path.dirname(target_path)
        output_filename = os.path.basename(target_path)
        
        Logger.Debug(
            __name__,
            u'Save project\n\tWorking path: {}\n\tFilename: {}\n\tTemp directory: {}'.format(working_path,
                                                                                        output_filename, stage)
            )
        
        export_pages = (
            pgid.CONTROL,
            pgid.FILES,
            pgid.SCRIPTS,
            pgid.CHANGELOG,
            pgid.COPYRIGHT,
            pgid.LAUNCHERS,
            pgid.BUILD,
            )
        
        self.Wizard.ExportPages(export_pages, stage)
        
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
        
        if os.path.isfile(target_path) or target_path == self.LoadedProject:
            Logger.Debug(__name__, GT(u'Overwriting old project file: {}').format(target_path))
        
        p_archive.Compress(stage, u'{}'.format(target_path))
        
        # FIXME: Should check file timestamp
        if os.path.isfile(target_path):
            Logger.Debug(__name__, GT(u'Project saved: {}').format(target_path))
            
            # Cleanup
            RemoveStage(stage)
            self.ProjectSetDirty(False)
            
            return dbrerrno.SUCCESS
        
        ShowErrorDialog(u'{}: {}'.format(GT(u'Project save failed'), target_path), parent=self)
        
        return dbrerrno.EUNKNOWN
    
    
    ## Opens a dialog for saving a new project
    def ProjectSaveAs(self):
        wildcards = (
            u'{} (.{})'.format(GT(u'Debreate project files'), PROJECT_ext),
            u'*.{}'.format(PROJECT_ext),
        )
        
        save_dialog = GetFileSaveDialog(self, GT(u'Save Debreate Project'), wildcards,
                PROJECT_ext)
        
        if ShowDialog(save_dialog):
            project_path = save_dialog.GetPath()
            project_filename = save_dialog.GetFilename()
            
            Logger.Debug(__name__, GT(u'Project save path: {}').format(project_path))
            Logger.Debug(__name__, GT(u'Project save filename: {}').format(project_filename))
            
            saved = self.ProjectSave(project_path)
            if saved == dbrerrno.SUCCESS:
                self.ProjectSetDirty(False)
            
            return saved
        
        Logger.Debug(__name__, GT(u'Not saving project'))
        
        return dbrerrno.ECNCLD
    
    
    ## Sets the 'modified' state of the project
    #  
    #  \param dirty
    #    \b \e True means project is modified
    def ProjectSetDirty(self, dirty=True):
        # Wait for all fields to update before setting state
        wx.Yield()
        
        changed = False
        
        if self.ProjectDirty != dirty:
            self.ProjectDirty = dirty
            self.GetMenuBar().GetMenuById(menuid.FILE).Enable(wx.ID_SAVE, self.ProjectDirty)
            
            title = self.GetTitle()
            
            if self.ProjectDirty:
                self.SetTitle(u'{}{}'.format(title, self.dirty_mark))
            
            else:
                self.SetTitle(title[:-len(self.dirty_mark)])
            
            changed = True
        
        return changed
    
    
    ## Sets compression in the main menu
    #  
    #  \param compression_id
    #        \b \e int : Compression ID to search for in menu iteration
    def SetCompression(self, compression_id):
        for Z in self.GetMenuBar().GetMenuById(menuid.COMPRESS).GetMenuItems():
            Z_ID = Z.GetId()
            
            if compression_id == Z_ID:
                Z.Check()
                
                Logger.Debug(__name__,
                        GT(u'Project compression set to "{}"'.format(compression_formats[Z_ID])))
                
                return
        
        Logger.Debug(__name__,
                GT(u'Urecognized compression ID: {}'.format(compression_id)))
    
    
    ## TODO: Doxygen
    def SetLogWindow(self, window):
        self.log_window = window
        
        wx.EVT_MENU(self, ident.LOG, self.log_window.OnToggleWindow)
    
    
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
