# -*- coding: utf-8 -*-

## \package main

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, subprocess, webbrowser, wx
from urllib2 import HTTPError
from urllib2 import URLError

from dbr.config             import ConfCode
from dbr.config             import GetDefaultConfigValue
from dbr.config             import ReadConfig
from dbr.config             import WriteConfig
from dbr.event              import EVT_CHANGE_PAGE
from dbr.functions          import GetCurrentVersion
from dbr.functions          import UsingDevelopmentVersion
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
from globals.execute        import GetExecutable
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.ident          import refid
from globals.moduleaccess   import ModuleAccessCtrl
from globals.paths          import PATH_app
from globals.paths          import PATH_local
from globals.project        import PROJECT_ext
from globals.project        import PROJECT_txt
from globals.strings        import GS
from startup.tests          import GetTestList
from ui.about               import AboutDialog
from ui.dialog              import ConfirmationDialog
from ui.dialog              import DetailedMessageDialog
from ui.dialog              import ShowErrorDialog
from ui.distcache           import DistNamesCacheDialog
from ui.layout              import BoxSizer
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
from wiz_bin.menu           import Panel as PageMenu
from wiz_bin.scripts        import Panel as PageScripts


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
        
        if DebugEnabled():
            self.SetTitle(u'{} ({})'.format(default_title, GT(u'debugging')))
        
        self.SetMinSize(wx.Size(640, 400))
        
        # ----- Set Titlebar Icon
        self.SetIcon(Icon(LOGO))
        
        # ----- Status Bar
        StatusBar(self)
        
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
        ## This menu is filled from ui.wizard.Wizard.SetPages
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
        
        menubar = MenuBar(self)
        
        menubar.Append(menu_file, GT(u'File'), wx.ID_FILE)
        menubar.Append(self.menu_page, GT(u'Page'), ident.PAGE)
        
        if self.menu_opt.GetMenuItemCount():
            menubar.Append(self.menu_opt, GT(u'Options'), ident.OPTIONS)
        
        menubar.Append(menu_help, GT(u'Help'), wx.ID_HELP)
        
        self.Wizard = Wizard(self)
        
        # *** Current Project Status *** #
        
        self.LoadedProject = None
        self.ProjectDirty = False
        
        # *** Event Handling *** #
        
        wx.EVT_MENU(self, wx.ID_NEW, self.OnProjectNew)
        wx.EVT_MENU(self, wx.ID_OPEN, self.OnProjectOpen)
        wx.EVT_MENU(self, wx.ID_SAVE, self.OnProjectSave)
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnProjectSave)
        wx.EVT_MENU(self, ident.QBUILD, self.OnQuickBuild)
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnQuit)
        
        wx.EVT_MENU(self, ident.TOOLTIPS, self.OnToggleToolTips)
        wx.EVT_MENU(self, ident.DIST, self.OnUpdateDistNamesCache)
        
        wx.EVT_MENU(self, ident.UPDATE, self.OnCheckUpdate)
        wx.EVT_MENU(self, wx.ID_HELP, self.OnHelp)
        wx.EVT_MENU(self, wx.ID_ABOUT, self.OnAbout)
        
        self.Bind(EVT_CHANGE_PAGE, self.OnWizardBtnPage)
        
        # Custom close event shows a dialog box to confirm quit
        wx.EVT_CLOSE(self, self.OnQuit)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(self.Wizard, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## Retrieves the Wizard instance
    #  
    #  \return
    #        ui.wizard.Wizard
    def GetWizard(self):
        return self.Wizard
    
    
    ## Sets the pages in the ui.wizard.Wizard instance
    def InitWizard(self):
        PageGreeting(self.Wizard)
        PageControl(self.Wizard)
        PageDepends(self.Wizard)
        PageFiles(self.Wizard)
        PageScripts(self.Wizard)
        PageChangelog(self.Wizard)
        PageCopyright(self.Wizard)
        PageMenu(self.Wizard)
        PageBuild(self.Wizard)
        
        self.Wizard.InitPages()
    
    
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
            update = ConfirmationDialog(self, GT(u'Update'), u'{}\n\n{}'.format(l1, l2)).Confirmed()
            if update:
                wx.LaunchDefaultBrowser(APP_homepage)
        
        elif isinstance(current, (unicode, str)):
            ShowErrorDialog(error_remote, current)
        
        else:
            DetailedMessageDialog(self, GT(u'Debreate'), text=GT(u'Debreate is up to date!')).ShowModal()
    
    
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
    
    
    ## Changes wizard page
    #  
    #  \param event
    #        \b \e wx.MenuEvent|int : The event or integer to use as page ID
    def OnMenuChangePage(self, event=None):
        if isinstance(event, int):
            event_id = event
        
        else:
            event_id = event.GetId()
        
        self.Wizard.ShowPage(event_id)
    
    
    ## TODO: Doxygen
    def OnProjectNew(self, event=None):
        self.ResetPages()
    
    
    ## TODO: Doxygen
    def OnProjectOpen(self, event=None):
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
            self.LoadedProject = project
        
        else:
            self.LoadedProject = None
    
    
    ## TODO: Doxygen
    def OnProjectSave(self, event=None):
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
                
                self.LoadedProject = u'{}/{}.dbp'.format(os.path.split(dia.GetPath())[0], filename)
                
                SaveIt(self.LoadedProject)
        
        if event_id == wx.ID_SAVE:
            # Define what to do if save is pressed
            # If project already exists, don't show dialog
            if not self.IsSaved() or not self.LoadedProject or not os.path.isfile(self.LoadedProject):
                OnSaveAs()
            
            else:
                SaveIt(self.LoadedProject)
        
        else:
            # If save as is press, show the save dialog
            OnSaveAs()
    
    
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
    
    
    ## Retrieves filename of loaded project
    def ProjectGetLoaded(self):
        return self.LoadedProject
    
    
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
        
        if self.LoadedProject and not self.ResetPages():
            return False
        
        # *** Get Control Data *** #
        control_data = data.split(u'<<CTRL>>\n')[1].split(u'\n<</CTRL>>')[0]
        depends_data = self.page_control.Set(control_data)
        self.page_depends.Set(depends_data)
        
        # *** Get Files Data *** #
        files_data = data.split(u'<<FILES>>\n')[1].split(u'\n<</FILES>>')[0]
        opened = self.page_files.Set(files_data)
        
        # *** Get Scripts Data *** #
        scripts_data = data.split(u'<<SCRIPTS>>\n')[1].split(u'\n<</SCRIPTS>>')[0]
        self.page_scripts.Set(scripts_data)
        
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
        self.page_build.Set(build_data)
        
        return opened
    
    
    ## TODO: Doxygen
    def ProjectChanged(self, event=None):
        if DebugEnabled():
            Logger.Debug(__name__, u'MainWindow.OnProjectChanged:')
            print(u'  Object: {}'.format(event.GetEventObject()))
        
        self.ProjectDirty = True
    
    
    ## TODO: Doxygen
    def ResetPages(self):
        warn_msg = GT(u'You will lose any unsaved information.')
        warn_msg = u'{}\n\n{}'.format(warn_msg, GT(u'Continue?'))
        
        if ConfirmationDialog(self, text=warn_msg).ShowModal() not in (wx.ID_OK, wx.OK):
            return False
        
        for page in self.all_pages:
            page.Reset()
        
        self.SetTitle(default_title)
        
        # Reset the saved project field so we know that a project file doesn't exists
        self.LoadedProject = None
        
        return True
    
    
    ## TODO: Doxygen
    def SetSavedStatus(self, status):
        if status: # If status is changing to unsaved this is True
            title = self.GetTitle()
            if self.IsSaved() and title != default_title:
                self.SetTitle(u'{}*'.format(title))
