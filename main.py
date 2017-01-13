# -*- coding: utf-8 -*-

## \package main

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, subprocess, webbrowser, wx
from urllib2 import HTTPError
from urllib2 import URLError

from dbr.about              import AboutDialog
from dbr.config             import ConfCode
from dbr.config             import GetDefaultConfigValue
from dbr.config             import ReadConfig
from dbr.config             import WriteConfig
from dbr.dialogs            import ConfirmationDialog
from dbr.dialogs            import DetailedMessageDialog
from dbr.dialogs            import ShowErrorDialog
from dbr.distcache          import DistNamesCacheDialog
from dbr.functions          import GetCurrentVersion
from dbr.functions          import UsingDevelopmentVersion
from dbr.icon               import Icon
from dbr.language           import GT
from dbr.log                import DebugEnabled
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
from globals.execute        import GetExecutable
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.paths          import PATH_app
from globals.paths          import PATH_local
from globals.project        import PROJECT_ext
from globals.project        import PROJECT_txt
from globals.tests          import GetTestList
from globals.wizardhelper   import GetTopWindow
from wiz_bin.build          import Panel as PanelBuild
from wiz_bin.changelog      import Panel as PanelChangelog
from wiz_bin.control        import Panel as PanelControl
from wiz_bin.copyright      import Panel as PanelCopyright
from wiz_bin.depends        import Panel as PanelDepends
from wiz_bin.files          import Panel as PanelFiles
from wiz_bin.info           import Panel as PanelInfo
from wiz_bin.menu           import Panel as PanelMenu
from wiz_bin.scripts        import Panel as PanelScripts


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
        menu_file = wx.Menu()
        
        mitm_new = wx.MenuItem(menu_file, wx.ID_NEW, GT(u'New project'),
                help=GT(u'Start a new project'))
        mitm_open = wx.MenuItem(menu_file, wx.ID_OPEN, GT(u'Open'),
                help=GT(u'Open a previously saved project'))
        mitm_save = wx.MenuItem(menu_file, wx.ID_SAVE, GT(u'Save'),
                help=GT(u'Save current project'))
        mitm_saveas = wx.MenuItem(menu_file, wx.ID_SAVEAS, GT(u'Save as'),
                help=GT(u'Save current project with a new filename'))
        
        # Quick Build
        mitm_quickbuild = wx.MenuItem(menu_file, ident.QBUILD, GT(u'Quick Build'),
                GT(u'Build a package from an existing build tree'))
        mitm_quickbuild.SetBitmap(ICON_CLOCK)
        
        mitm_quit = wx.MenuItem(menu_file, wx.ID_EXIT, GT(u'Quit'),
                help=GT(u'Exit Debreate'))
        
        menu_file.AppendItem(mitm_new)
        menu_file.AppendItem(mitm_open)
        menu_file.AppendItem(mitm_save)
        menu_file.AppendItem(mitm_saveas)
        menu_file.AppendSeparator()
        menu_file.AppendItem(mitm_quickbuild)
        menu_file.AppendSeparator()
        menu_file.AppendItem(mitm_quit)
        
        # *** Page Menu *** #
        ## This menu is filled from dbr.wizard.Wizard
        self.menu_page = wx.Menu()
        
        # ----- Options Menu
        self.menu_opt = wx.Menu()
        
        # Show/Hide tooltips
        self.opt_tooltips = wx.MenuItem(self.menu_opt, ident.TOOLTIPS, GT(u'Show tooltips'),
                GT(u'Show or hide tooltips'), kind=wx.ITEM_CHECK)
        
        # A bug with wx 2.8 does not allow tooltips to be toggled off
        if wx.MAJOR_VERSION > 2:
            self.menu_opt.AppendItem(self.opt_tooltips)
        
        if self.menu_opt.FindItemById(ident.TOOLTIPS):
            show_tooltips = ReadConfig(u'tooltips')
            if show_tooltips != ConfCode.KEY_NO_EXIST:
                self.opt_tooltips.Check(show_tooltips)
            
            else:
                self.opt_tooltips.Check(GetDefaultConfigValue(u'tooltips'))
            
            self.OnToggleToolTips()
        
        # *** Option Menu: open logs directory *** #
        
        if GetExecutable(u'xdg-open'):
            mitm_logs_open = wx.MenuItem(self.menu_opt, ident.OPENLOGS, GT(u'Open logs directory'))
            self.menu_opt.AppendItem(mitm_logs_open)
            
            wx.EVT_MENU(self, ident.OPENLOGS, self.OnLogDirOpen)
        
        # *** OS distribution names cache *** #
        
        opt_distname_cache = wx.MenuItem(self.menu_opt, ident.DIST, GT(u'Update dist names cache'),
                GT(u'Creates/Updates list of distribution names for changelog page'))
        self.menu_opt.AppendItem(opt_distname_cache)
        
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
        
        mitm_dpm = wx.MenuItem(self.menu_policy, ident.DPM, GT(u'Debian Policy Manual'),
                u'http://www.debian.org/doc/debian-policy')
        mitm_dpm.SetBitmap(ICON_GLOBE)
        mitm_dpm_ctrl = wx.MenuItem(self.menu_policy, ident.DPMCtrl, GT(u'Control files'),
                u'http://www.debian.org/doc/debian-policy/ch-controlfields.html')
        mitm_dpm_ctrl.SetBitmap(ICON_GLOBE)
        mitm_dpm_log = wx.MenuItem(self.menu_policy, ident.DPMLog, GT(u'Changelog'),
                u'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog')
        mitm_dpm_log.SetBitmap(ICON_GLOBE)
        mitm_upm = wx.MenuItem(self.menu_policy, ident.UPM, GT(u'Ubuntu Policy Manual'),
                u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/')
        mitm_upm.SetBitmap(ICON_GLOBE)
        # FIXME: Use wx.NewId()
        mitm_deb_src = wx.MenuItem(self.menu_policy, 222, GT(u'Building debs from source'),
                u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source') # This is here only temporarily for reference
        mitm_deb_src.SetBitmap(ICON_GLOBE)
        mitm_lint_tags = wx.MenuItem(self.menu_policy, ident.LINT_TAGS, GT(u'Lintian tags explanation'),
                u'http://lintian.debian.org/tags-all.html')
        mitm_lint_tags.SetBitmap(ICON_GLOBE)
        mitm_launchers = wx.MenuItem(self.menu_policy, ident.LAUNCHERS, GT(u'Launchers / Desktop entries'),
                u'https://www.freedesktop.org/wiki/Specifications/desktop-entry-spec/')
        mitm_launchers.SetBitmap(ICON_GLOBE)
        
        self.menu_policy.AppendItem(mitm_dpm)
        self.menu_policy.AppendItem(mitm_dpm_ctrl)
        self.menu_policy.AppendItem(mitm_dpm_log)
        self.menu_policy.AppendItem(mitm_upm)
        self.menu_policy.AppendItem(mitm_deb_src)
        self.menu_policy.AppendItem(mitm_lint_tags)
        self.menu_policy.AppendItem(mitm_launchers)
        
        lst_policy_ids = (
            ident.DPM,
            ident.DPMCtrl,
            ident.DPMLog,
            ident.UPM,
            222,
            ident.LINT_TAGS,
            ident.LAUNCHERS,
            )
        
        for ID in lst_policy_ids:
            wx.EVT_MENU(self, ID, self.OpenPolicyManual)
        
        mitm_help = wx.MenuItem(menu_help, wx.ID_HELP, GT(u'Help'), GT(u'Open a usage document'))
        mitm_about = wx.MenuItem(menu_help, wx.ID_ABOUT, GT(u'About'), GT(u'About Debreate'))
        
        menu_help.AppendMenu(-1, GT(u'Reference'), self.menu_policy)
        menu_help.AppendSeparator()
        menu_help.AppendItem(mitm_help)
        menu_help.AppendItem(mitm_about)
        
        menubar = MenuBar(self)
        
        menubar.Append(menu_file, GT(u'File'), wx.ID_FILE)
        menubar.Append(self.menu_page, GT(u'Page'), ident.PAGE)
        
        if self.menu_opt.GetMenuItemCount():
            menubar.Append(self.menu_opt, GT(u'Options'), ident.OPTIONS)
        
        menubar.Append(menu_help, GT(u'Help'), wx.ID_HELP)
        
        self.wizard = Wizard(self)
        
        self.page_info = PanelInfo(self.wizard)
        self.page_control = PanelControl(self.wizard)
        self.page_depends = PanelDepends(self.wizard)
        self.page_files = PanelFiles(self.wizard)
        self.page_scripts = PanelScripts(self.wizard)
        self.page_clog = PanelChangelog(self.wizard)
        self.page_cpright = PanelCopyright(self.wizard)
        self.page_menu = PanelMenu(self.wizard)
        self.page_build = PanelBuild(self.wizard)
        
        self.all_pages = (
            self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_menu, self.page_build
            )
        
        bin_pages = (
            self.page_info, self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_menu, self.page_build
            )
        
        self.wizard.SetPages(bin_pages)
        
        # *** Event Handling *** #
        
        wx.EVT_MENU(self, wx.ID_NEW, self.OnNewProject)
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnOpenProject)
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnSaveProject)
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveProject)
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
        
        wx.EVT_CLOSE(self, self.OnQuit) # Custom close event shows a dialog box to confirm quit
        
        # *** Layout *** #
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.wizard, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # Saving
        # First item is name of saved file displayed in title
        # Second item is actual path to project file
        self.saved_project = wx.EmptyString
    
    
    ## Retrieves the Wizard instance
    #  
    #  \return
    #        dbr.wizard.Wizard
    def GetWizard(self):
        return self.wizard
    
    
    ## Changes wizard page
    #  
    #  \param event
    #        \b \e wx.MenuEvent|int : The event or integer to use as page ID
    def GoToPage(self, event=None):
        if isinstance(event, int):
            event_id = event
        
        else:
            event_id = event.GetId()
        
        self.wizard.ShowPage(event_id)
    
    
    ## TODO: Doxygen
    def IsNewProject(self):
        title = self.GetTitle()
        if title == default_title:
            return True
        
        else:
            return False
    
    
    ## TODO: Doxygen
    def IsSaved(self):
        title = self.GetTitle()
        if title[-1] == u'*':
            return False
        
        else:
            return True
    
    
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
        if isinstance(current, (URLError,  HTTPError)):
            current = unicode(current)
            ShowErrorDialog(GT(u'An error occurred attempting to contact remote website'), current)
        
        elif isinstance(current, tuple) and current > VERSION_tuple:
            current = u'{}.{}.{}'.format(current[0], current[1], current[2])
            l1 = GT(u'Version {} is available!').format(current)
            l2 = GT(u'Would you like to go to Debreate\'s website?')
            update = ConfirmationDialog(GetTopWindow(), GT(u'Update'), u'{}\n\n{}'.format(l1, l2)).Confirmed()
            if update:
                wx.LaunchDefaultBrowser(APP_homepage)
        
        elif isinstance(current, (unicode, str)):
            ShowErrorDialog(GT(u'An error occurred attempting to contact remote website'), current)
        
        else:
            DetailedMessageDialog(GetTopWindow(), GT(u'Debreate'), text=GT(u'Debreate is up to date!')).ShowModal()
    
    
    ## Action to take when 'Help' is selected from the help menu
    #  
    #  First tries to open pdf help file. If fails tries
    #  to open html help file. If fails opens debreate usage
    #  webpage
    def OnHelp(self, event=None):
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
        self.ResetPages()
    
    
    ## TODO: Doxygen
    def OnOpenProject(self, event=None):
        projects_filter = u'|*.{};*.{}'.format(PROJECT_ext, PROJECT_txt)
        d = GT(u'Debreate project files')
        
        dia = wx.FileDialog(self, GT(u'Open Debreate Project'), os.getcwd(), u'',
                u'{}{}'.format(d, projects_filter), wx.FD_CHANGE_DIR)
        if dia.ShowModal() != wx.ID_OK:
            return
        
        # Get the path and set the saved project
        project = dia.GetPath()
        
        filename = os.path.basename(project)
        
        if self.OpenProject(filename):
            # Only set project open in memory if loaded completely
            self.saved_project = project
        
        else:
            self.saved_project = None
    
    
    ## TODO: Doxygen
    def OnQuickBuild(self, event=None):
        QB = QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
    
    
    ## Shows a dialog to confirm quit and write window settings to config file
    def OnQuit(self, event=None):
        if ConfirmationDialog(self, GT(u'Quit?'),
                text=GT(u'You will lose any unsaved information')).ShowModal() in (wx.ID_OK, wx.OK):
            
            maximized = self.IsMaximized()
            WriteConfig(u'maximize', maximized)
            
            if maximized:
                WriteConfig(u'position', GetDefaultConfigValue(u'position'))
                WriteConfig(u'size', GetDefaultConfigValue(u'size'))
                WriteConfig(u'center', True)
            
            else:
                WriteConfig(u'position', self.GetPositionTuple())
                WriteConfig(u'size', self.GetSizeTuple())
                WriteConfig(u'center', False)
            
            WriteConfig(u'workingdir', os.getcwd())
            
            self.Destroy()
    
    
    ## TODO: Doxygen
    def OnSaveProject(self, event=None):
        event_id = event.GetId()
        
        def SaveIt(path):
                # Gather data from different pages
                data = (self.page_control.GatherData(), self.page_files.GatherData(),
                        self.page_scripts.GatherData(), self.page_clog.GatherData(),
                        self.page_cpright.GatherData(), self.page_menu.GatherData(),
                        self.page_build.GatherData())
                
                # Create a backup of the project
                overwrite = False
                if os.path.isfile(path):
                    backup = u'{}.backup'.format(path)
                    shutil.copy(path, backup)
                    overwrite = True
                
                # This try statement can be removed when unicode support is enabled
                try:
                    WriteFile(path, u'[DEBREATE-{}]\n{}'.format(VERSION_string, u'\n'.join(data)))
                    
                    if overwrite:
                        os.remove(backup)
                
                except UnicodeEncodeError:
                    detail1 = GT(u'Unfortunately Debreate does not support unicode yet.')
                    detail2 = GT(u'Remove any non-ASCII characters from your project.')
                    
                    ShowErrorDialog(GT(u'Save failed'), u'{}\n{}'.format(detail1, detail2), title=GT(u'Unicode Error'))
                    
                    if overwrite:
                        os.remove(path)
                        # Restore project backup
                        shutil.move(backup, path)
        
        def OnSaveAs():
            dbp = u'|*.dbp'
            d = GT(u'Debreate project files')
            dia = wx.FileDialog(self, GT(u'Save Debreate Project'), os.getcwd(), u'', u'{}{}'.format(d, dbp),
                                    wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
            if dia.ShowModal() == wx.ID_OK:
                filename = dia.GetFilename()
                if filename.split(u'.')[-1] == u'dbp':
                    filename = u'.'.join(filename.split(u'.')[:-1])
                
                self.saved_project = u'{}/{}.dbp'.format(os.path.split(dia.GetPath())[0], filename)
                
                SaveIt(self.saved_project)
        
        if event_id == wx.ID_SAVE:
            # Define what to do if save is pressed
            # If project already exists, don't show dialog
            if not self.IsSaved() or not self.saved_project or not os.path.isfile(self.saved_project):
                OnSaveAs()
            
            else:
                SaveIt(self.saved_project)
        
        else:
            # If save as is press, show the save dialog
            OnSaveAs()
    
    
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
        
        if not os.path.isfile(project_file):
            ShowErrorDialog(GT(u'Could not open project file'),
                    GT(u'File does not exist or is not a regular file: {}').format(project_file))
            return False
        
        data = ReadFile(project_file)
        
        lines = data.split(u'\n')
        
        # FIXME: Need a better way to determine valid project
        app = lines[0].lstrip(u'[')
        if not app.startswith(u'DEBREATE'):
            ShowErrorDialog(GT(u'Could not open project file'),
                    GT(u'Not a valid Debreate project: {}').format(project_file))
            return False
        
        if self.saved_project and not self.ResetPages():
            return False
        
        # *** Get Control Data *** #
        control_data = data.split(u'<<CTRL>>\n')[1].split(u'\n<</CTRL>>')[0]
        depends_data = self.page_control.SetFieldData(control_data)
        self.page_depends.SetFieldData(depends_data)
        
        # *** Get Files Data *** #
        files_data = data.split(u'<<FILES>>\n')[1].split(u'\n<</FILES>>')[0]
        opened = self.page_files.SetFieldData(files_data)
        
        # *** Get Scripts Data *** #
        scripts_data = data.split(u'<<SCRIPTS>>\n')[1].split(u'\n<</SCRIPTS>>')[0]
        self.page_scripts.SetFieldData(scripts_data)
        
        # *** Get Changelog Data *** #
        clog_data = data.split(u'<<CHANGELOG>>\n')[1].split(u'\n<</CHANGELOG>>')[0]
        self.page_clog.SetChangelog(clog_data)
        
        # *** Get Copyright Data *** #
        try:
            cpright_data = data.split(u'<<COPYRIGHT>>\n')[1].split(u'\n<</COPYRIGHT')[0]
            self.page_cpright.SetCopyright(cpright_data)
        
        except IndexError:
            pass
        
        # *** Get Menu Data *** #
        menu_data = data.split(u'<<MENU>>\n')[1].split(u'\n<</MENU>>')[0]
        self.page_menu.SetLauncherData(menu_data, enabled=True)
        
        # Get Build Data
        build_data = data.split(u'<<BUILD>>\n')[1].split(u'\n<</BUILD')[0]#.split(u'\n')
        self.page_build.SetFieldData(build_data)
        
        return opened
    
    
    ## TODO: Doxygen
    def ResetPages(self):
        warn_msg = GT(u'You will lose any unsaved information.')
        warn_msg = u'{}\n\n{}'.format(warn_msg, GT(u'Continue?'))
        
        if ConfirmationDialog(self, text=warn_msg).ShowModal() not in (wx.ID_OK, wx.OK):
            return False
        
        for page in self.all_pages:
            page.ResetAllFields()
        
        self.SetTitle(default_title)
        
        # Reset the saved project field so we know that a project file doesn't exists
        self.saved_project = wx.EmptyString
        
        return True
    
    
    ## TODO: Doxygen
    def SetSavedStatus(self, status):
        if status: # If status is changing to unsaved this is True
            title = self.GetTitle()
            if self.IsSaved() and title != default_title:
                self.SetTitle(u'{}*'.format(title))
