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
from dbr.custom             import OpenFile
from dbr.custom             import SaveFile
from dbr.custom             import StatusBar
from dbr.functions          import GetCurrentVersion
from dbr.language           import GT
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from dbr.moduleaccess       import ModuleAccessCtrl
from dbr.quickbuild         import QuickBuild
from dbr.wizard             import Wizard
from globals.application    import APP_homepage
from globals.application    import APP_project_gh
from globals.application    import APP_project_sf
from globals.application    import AUTHOR_email
from globals.application    import AUTHOR_name
from globals.application    import VERSION_string
from globals.application    import VERSION_tuple
from globals.ident          import ID_BUILD
from globals.ident          import ID_CHANGELOG
from globals.ident          import ID_CONTROL
from globals.ident          import ID_COPYRIGHT
from globals.ident          import ID_DEPENDS
from globals.ident          import ID_DIALOGS
from globals.ident          import ID_FILES
from globals.ident          import ID_GREETING
from globals.ident          import ID_MENU
from globals.ident          import ID_MENU_TT
from globals.ident          import ID_SCRIPTS
from globals.paths          import PATH_app
from globals.project        import PROJECT_ext
from globals.project        import PROJECT_txt
from wiz_bin.build          import Panel as PanelBuild
from wiz_bin.changelog      import Panel as PanelChangelog
from wiz_bin.control        import Panel as PanelControl
from wiz_bin.copyright      import Panel as PanelCopyright
from wiz_bin.depends        import Panel as PanelDepends
from wiz_bin.files          import Panel as PanelFiles
from wiz_bin.info           import Panel as PanelInfo
from wiz_bin.menu           import Panel as PanelMenu
from wiz_bin.scripts        import Panel as PanelScripts


# Debian Policy Manual IDs
ID_DPM = wx.NewId()
ID_DPMCtrl = wx.NewId()
ID_DPMLog = wx.NewId()
ID_UPM = wx.NewId()
ID_Lintian = wx.NewId()
ID_Launchers = wx.NewId()

# Misc. IDs
ID_QBUILD = wx.NewId()
ID_UPDATE = wx.NewId()

default_title = GT(u'Debreate - Debian Package Builder')


## TODO: Doxygen
class MainWindow(wx.Frame, ModuleAccessCtrl):
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, default_title, pos, size)
        ModuleAccessCtrl.__init__(self, __name__)
        
        # Make sure that this frame is set as the top window
        if not wx.GetApp().GetTopWindow() == self:
            Logger.Debug(__name__, GT(u'Not set as top window'))
            
            wx.GetApp().SetTopWindow(self)
        
        if DebugEnabled():
            self.SetTitle(u'{} ({})'.format(default_title, GT(u'debugging')))
        
        self.SetMinSize((640,400))
        
        # ----- Set Titlebar Icon
        self.main_icon = wx.Icon(u'{}/bitmaps/debreate64.png'.format(PATH_app), wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.main_icon)
        
        # ----- Status Bar
        self.stat_bar = StatusBar(self)
        
        # ----- File Menu
        self.menu_file = wx.Menu()
        
        # Quick Build
        self.QuickBuild = wx.MenuItem(self.menu_file, ID_QBUILD, GT(u'Quick Build'),
                GT(u'Build a package from an existing build tree'))
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
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveProject)
        wx.EVT_MENU(self, ID_QBUILD, self.OnQuickBuild)
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnQuit)
        wx.EVT_CLOSE(self, self.OnQuit) #custom close event shows a dialog box to confirm quit
        
        # ----- Page Menu
        self.menu_page = wx.Menu()
        
        self.p_info = wx.MenuItem(self.menu_page, ID_GREETING, GT(u'Information'),
                GT(u'Go to Information section'), kind=wx.ITEM_RADIO)
        self.p_ctrl = wx.MenuItem(self.menu_page, ID_CONTROL, GT(u'Control'),
                GT(u'Go to Control section'), kind=wx.ITEM_RADIO)
        self.p_deps = wx.MenuItem(self.menu_page, ID_DEPENDS, GT(u'Dependencies'),
                GT(u'Go to Dependencies section'), kind=wx.ITEM_RADIO)
        self.p_files = wx.MenuItem(self.menu_page, ID_FILES, GT(u'Files'),
                GT(u'Go to Files section'), kind=wx.ITEM_RADIO)
        self.p_scripts = wx.MenuItem(self.menu_page, ID_SCRIPTS, GT(u'Scripts'),
                GT(u'Go to Scripts section'), kind=wx.ITEM_RADIO)
        self.p_clog = wx.MenuItem(self.menu_page, ID_CHANGELOG, GT(u'Changelog'),
                GT(u'Go to Changelog section'), kind=wx.ITEM_RADIO)
        self.p_cpright = wx.MenuItem(self.menu_page, ID_COPYRIGHT, GT(u'Copyright'),
                GT(u'Go to Copyright section'), kind=wx.ITEM_RADIO)
        self.p_menu = wx.MenuItem(self.menu_page, ID_MENU, GT(u'Menu Launcher'),
                GT(u'Go to Menu Launcher section'), kind=wx.ITEM_RADIO)
        self.p_build = wx.MenuItem(self.menu_page, ID_BUILD, GT(u'Build'),
                GT(u'Go to Build section'), kind=wx.ITEM_RADIO)
        
        self.menu_page.AppendItem(self.p_info)
        self.menu_page.AppendItem(self.p_ctrl)
        self.menu_page.AppendItem(self.p_deps)
        self.menu_page.AppendItem(self.p_files)
        self.menu_page.AppendItem(self.p_scripts)
        self.menu_page.AppendItem(self.p_clog)
        self.menu_page.AppendItem(self.p_cpright)
        self.menu_page.AppendItem(self.p_menu)
        self.menu_page.AppendItem(self.p_build)
        
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
        self.cust_dias = wx.MenuItem(self.menu_opt, ID_DIALOGS, GT(u'Use Custom Dialogs'),
            GT(u'Use System or Custom Save/Open Dialogs'), kind=wx.ITEM_CHECK)
        
        wx.EVT_MENU(self, ID_DIALOGS, self.OnEnableCustomDialogs)
        
        self.menu_opt.AppendItem(self.cust_dias)
        
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
        self.DPM = wx.MenuItem(self.Policy, ID_DPM, GT(u'Debian Policy Manual'),
                u'http://www.debian.org/doc/debian-policy')
        self.DPM.SetBitmap(globe)
        self.DPMCtrl = wx.MenuItem(self.Policy, ID_DPMCtrl, GT(u'Control Files'),
                u'http://www.debian.org/doc/debian-policy/ch-controlfields.html')
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
        self.LintianTags = wx.MenuItem(self.Policy, ID_Lintian, GT(u'Lintian Tags Explanation'),
                u'http://lintian.debian.org/tags-all.html')
        self.LintianTags.SetBitmap(globe)
        self.Launchers = wx.MenuItem(self.Policy, ID_Launchers, GT(u'Launchers / Desktop Entries'),
                u'https://www.freedesktop.org/wiki/Specifications/desktop-entry-spec/')
        self.Launchers.SetBitmap(globe)
        
        self.Policy.AppendItem(self.DPM)
        self.Policy.AppendItem(self.DPMCtrl)
        self.Policy.AppendItem(self.DPMLog)
        self.Policy.AppendItem(self.UPM)
        self.Policy.AppendItem(self.DebFrmSrc)
        self.Policy.AppendItem(self.LintianTags)
        self.Policy.AppendItem(self.Launchers)
        
        self.references = {
                    ID_DPM: u'http://www.debian.org/doc/debian-policy',
                    ID_DPMCtrl: u'http://www.debian.org/doc/debian-policy/ch-controlfields.html',
                    ID_DPMLog: u'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog',
                    ID_UPM: u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/',
                    222: u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source',
                    ID_Lintian: u'http://lintian.debian.org/tags-all.html',
                    ID_Launchers: u'https://www.freedesktop.org/wiki/Specifications/desktop-entry-spec/',
                    }
        for ID in self.references:
            wx.EVT_MENU(self, ID, self.OpenPolicyManual)
        
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
        
        self.menubar.Insert(0, self.menu_file, GT(u'File'))
        self.menubar.Insert(1, self.menu_page, GT(u'Page'))
        self.menubar.Insert(2, self.menu_opt, GT(u'Options'))
        self.menubar.Insert(3, self.menu_help, GT(u'Help'))
        
        # ***** END MENUBAR ***** #
        
        self.wizard = Wizard(self) # Binary
        
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
        
        self.pages = {
            self.p_info: self.page_info,
            self.p_ctrl: self.page_control,
            self.p_deps: self.page_depends,
                self.p_files: self.page_files,
                self.p_scripts: self.page_scripts,
                self.p_clog: self.page_clog,
                self.p_cpright: self.page_cpright,
                self.p_menu: self.page_menu,
                self.p_build: self.page_build,
                }
        
        for p in self.pages:
            wx.EVT_MENU(self, p.GetId(), self.GoToPage)
        
        # ----- Layout
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.wizard, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.main_sizer)
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
    
    
    ## TODO: Doxygen
    def NewProject(self):
        for page in self.all_pages:
            page.ResetAllFields()
        self.SetTitle(default_title)
        
        # Reset the saved project field so we know that a project file doesn't exists
        self.saved_project = wx.EmptyString
    
    
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
        if u'-dev' in VERSION_string:
            wx.MessageDialog(self, GT(u'Update checking not supported in development versions'),
                    GT(u'Update'), wx.OK|wx.ICON_INFORMATION).ShowModal()
            return
        
        wx.SafeYield()
        current = GetCurrentVersion()
        Logger.Debug(__name__, GT(u'URL request result: {}').format(current))
        if type (current) == URLError or type(current) == HTTPError:
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
    
    
    ## Writes dialog settings to config
    def OnEnableCustomDialogs(self, event=None):
        WriteConfig(u'dialogs', self.cust_dias.IsChecked())
    
    
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
    
    
    ## TODO: Doxygen
    def OnNewProject(self, event=None):
        dia = wx.MessageDialog(self, GT(u'You will lose any unsaved information\n\nContinue?'),
                GT(u'Start New Project'), wx.YES_NO|wx.NO_DEFAULT)
        if dia.ShowModal() == wx.ID_YES:
            self.NewProject()
    
    
    ## TODO: Doxygen
    def OnOpenProject(self, event=None):
        cont = False
        projects_filter = u'|*.{};*.{}'.format(PROJECT_ext, PROJECT_txt)
        d = GT(u'Debreate project files')
        if self.cust_dias.IsChecked():
            dia = OpenFile(self, GT(u'Open Debreate Project'))
            dia.SetFilter(u'{}{}'.format(d, projects_filter))
            if dia.DisplayModal():
                cont = True
        
        else:
            dia = wx.FileDialog(self, GT(u'Open Debreate Project'), os.getcwd(), u'',
                    u'{}{}'.format(d, projects_filter), wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                cont = True
        
        if cont:
            # Get the path and set the saved project
            self.saved_project = dia.GetPath()
            
            FILE_BUFFER = open(self.saved_project, u'r')
            data = FILE_BUFFER.read()
            FILE_BUFFER.close()
            
            filename = os.path.split(self.saved_project)[1]
            
            self.OpenProject(data, filename)
    
    
    ## TODO: Doxygen
    def OnQuickBuild(self, event=None):
        QB = QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
    
    
    ## Shows a dialog to confirm quit and write window settings to config file
    def OnQuit(self, event=None):
        confirm = wx.MessageDialog(self, GT(u'You will lose any unsaved information'), GT(u'Quit?'),
                                   wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_OK:
            confirm.Destroy()
            
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
        
        else:
            confirm.Destroy()
    
    
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
                
                savefile = open(path, u'w')
                
                # This try statement can be removed when unicode support is enabled
                try:
                    savefile.write(u'[DEBREATE-{}]\n{}'.format(VERSION_string, u'\n'.join(data)))
                    savefile.close()
                    if overwrite:
                        os.remove(backup)
                
                except UnicodeEncodeError:
                    serr = GT(u'Save failed')
                    uni = GT(u'Unfortunately Debreate does not support unicode yet. Remove any non-ASCII characters from your project.')
                    UniErr = wx.MessageDialog(self, u'{}\n\n{}'.format(serr, uni), GT(u'Unicode Error'), style=wx.OK|wx.ICON_EXCLAMATION)
                    UniErr.ShowModal()
                    savefile.close()
                    if overwrite:
                        os.remove(path)
                        # Restore project backup
                        shutil.move(backup, path)
        
        
        ## TODO: Doxygen
        def OnSaveAs():
            dbp = u'|*.dbp'
            d = GT(u'Debreate project files')
            cont = False
            if self.cust_dias.IsChecked():
                dia = SaveFile(self, GT(u'Save Debreate Project'), u'dbp')
                dia.SetFilter(u'{}{}'.format(d, dbp))
                if dia.DisplayModal():
                    cont = True
                    filename = dia.GetFilename()
                    if filename.split(u'.')[-1] == u'dbp':
                        filename = u'.'.join(filename.split(u'.')[:-1])
                    
                    self.saved_project = u'{}/{}.dbp'.format(dia.GetPath(), filename)
            
            else:
                dia = wx.FileDialog(self, GT(u'Save Debreate Project'), os.getcwd(), u'', u'{}{}'.format(d, dbp),
                                        wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
                if dia.ShowModal() == wx.ID_OK:
                    cont = True
                    filename = dia.GetFilename()
                    if filename.split(u'.')[-1] == u'dbp':
                        filename = u'.'.join(filename.split(u'.')[:-1])
                    
                    self.saved_project = u'{}/{}.dbp'.format(os.path.split(dia.GetPath())[0], filename)
            
            if cont:
                SaveIt(self.saved_project)
        
        if event_id == wx.ID_SAVE:
            # Define what to do if save is pressed
            # If project already exists, don't show dialog
            if not self.IsSaved() or self.saved_project == wx.EmptyString or not os.path.isfile(self.saved_project):
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
    
    
    ## Opens web links from the help menu
    def OpenPolicyManual(self, event=None):
        event_id = event.GetId()  # Get the id for the webpage link we are opening
        webbrowser.open(self.references[event_id])
    
    
    ## TODO: Doxygen
    def OpenProject(self, data, filename):
        lines = data.split(u'\n')
        app = lines[0].split(u'-')[0].split(u'[')[1]
        if app != u'DEBREATE':
            bad_file = wx.MessageDialog(self, GT(u'Not a valid Debreate project'), GT(u'Error'),
                    style=wx.OK|wx.ICON_ERROR)
            bad_file.ShowModal()
        
        else: 
            # *** Get Control Data *** #
            control_data = data.split(u'<<CTRL>>\n')[1].split(u'\n<</CTRL>>')[0]
            depends_data = self.page_control.SetFieldData(control_data)
            self.page_depends.SetFieldData(depends_data)
            
            # *** Get Files Data *** #
            files_data = data.split(u'<<FILES>>\n')[1].split(u'\n<</FILES>>')[0]
            self.page_files.SetFieldData(files_data)
            
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
    
    
    ## TODO: Doxygen
    def SetSavedStatus(self, status):
        if status: # If status is changing to unsaved this is True
            title = self.GetTitle()
            if self.IsSaved() and title != default_title:
                self.SetTitle(u'{}*'.format(title))
