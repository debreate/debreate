# -*- coding: utf-8 -*-


import os, db, webbrowser, shutil, subprocess, wx
from urllib2 import HTTPError
from urllib2 import URLError

from dbr.about              import AboutDialog
from dbr.config             import ConfCode
from dbr.config             import GetDefaultConfigValue
from dbr.config             import ReadConfig
from dbr.config             import WriteConfig
from dbr.functions          import GetCurrentVersion
from dbr.language           import GT
from dbr.log                import Logger
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

# Misc. IDs
ID_QBUILD = wx.NewId()
ID_UPDATE = wx.NewId()


class MainWindow(wx.Frame):
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, _('Debreate - Debian Package Builder'), pos, size)
        
        # The default title
        self.default_title = _('Debreate - Debian Package Builder')
        
        self.SetMinSize((640,400))
        
        # ----- Set Titlebar Icon
        self.main_icon = wx.Icon("%s/bitmaps/debreate64.png" % PATH_app, wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.main_icon)
        
        # ----- Status Bar
        self.stat_bar = wx.StatusBar(self, -1)
        self.SetStatusBar(self.stat_bar)
        
        
        
        # ***** Menu Bar ***** #
        
        # ----- File Menu
        self.menu_file = wx.Menu()
        
        # Quick Build
        self.QuickBuild = wx.MenuItem(self.menu_file, ID_QBUILD, _('Quick Build'),
                _('Build a package from an existing build tree'))
        self.QuickBuild.SetBitmap(wx.Bitmap("%s/bitmaps/clock16.png" % PATH_app))
        
        self.menu_file.Append(wx.ID_NEW, help=_('Start a new project'))
        self.menu_file.Append(wx.ID_OPEN, help=_('Open a previously saved project'))
        self.menu_file.Append(wx.ID_SAVE, help=_('Save current project'))
        self.menu_file.Append(wx.ID_SAVEAS, help=_('Save current project with a new filename'))
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
        
        self.p_info = wx.MenuItem(self.menu_page, ID_GREETING, _('Information'),
                _('Go to Information section'), kind=wx.ITEM_RADIO)
        self.p_ctrl = wx.MenuItem(self.menu_page, ID_CONTROL, _('Control'),
                _('Go to Control section'), kind=wx.ITEM_RADIO)
        self.p_deps = wx.MenuItem(self.menu_page, ID_DEPENDS, _('Dependencies'),
                _('Go to Dependencies section'), kind=wx.ITEM_RADIO)
        self.p_files = wx.MenuItem(self.menu_page, ID_FILES, _('Files'),
                _('Go to Files section'), kind=wx.ITEM_RADIO)
        self.p_scripts = wx.MenuItem(self.menu_page, ID_SCRIPTS, _('Scripts'),
                _('Go to Scripts section'), kind=wx.ITEM_RADIO)
        self.p_clog = wx.MenuItem(self.menu_page, ID_CHANGELOG, _('Changelog'),
                _('Go to Changelog section'), kind=wx.ITEM_RADIO)
        self.p_cpright = wx.MenuItem(self.menu_page, ID_COPYRIGHT, _('Copyright'),
                _('Go to Copyright section'), kind=wx.ITEM_RADIO)
        self.p_menu = wx.MenuItem(self.menu_page, ID_MENU, _('Menu Launcher'),
                _('Go to Menu Launcher section'), kind=wx.ITEM_RADIO)
        self.p_build = wx.MenuItem(self.menu_page, ID_BUILD, _('Build'),
                _('Go to Build section'), kind=wx.ITEM_RADIO)
        
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
        self.cust_dias = wx.MenuItem(self.menu_opt, ID_DIALOGS, _('Use Custom Dialogs'),
            _('Use System or Custom Save/Open Dialogs'), kind=wx.ITEM_CHECK)
        
        self.menu_opt.AppendItem(self.cust_dias)
        
        # ----- Help Menu
        self.menu_help = wx.Menu()
        
        # ----- Version update
        self.version_check = wx.MenuItem(self.menu_help, ID_UPDATE, _('Check for Update'))
        self.menu_help.AppendItem(self.version_check)
        self.menu_help.AppendSeparator()
        
        wx.EVT_MENU(self, ID_UPDATE, self.OnCheckUpdate)
        
        # Menu with links to the Debian Policy Manual webpages
        self.Policy = wx.Menu()
        
        globe = wx.Bitmap("%s/bitmaps/globe16.png" % PATH_app)
        self.DPM = wx.MenuItem(self.Policy, ID_DPM, _('Debian Policy Manual'), 'http://www.debian.org/doc/debian-policy')
        self.DPM.SetBitmap(globe)
        self.DPMCtrl = wx.MenuItem(self.Policy, ID_DPMCtrl, _('Control Files'), 'http://www.debian.org/doc/debian-policy/ch-controlfields.html')
        self.DPMCtrl.SetBitmap(globe)
        self.DPMLog = wx.MenuItem(self.Policy, ID_DPMLog, _('Changelog'), 'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog')
        self.DPMLog.SetBitmap(globe)
        self.UPM = wx.MenuItem(self.Policy, ID_UPM, _('Ubuntu Policy Manual'), 'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/')
        self.UPM.SetBitmap(globe)
        self.DebFrmSrc = wx.MenuItem(self.Policy, 222, _('Building debs from Source'), 'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source') # This is here only temporarily for reference
        self.DebFrmSrc.SetBitmap(globe)
        self.LintianTags = wx.MenuItem(self.Policy, ID_Lintian, _('Lintian Tags Explanation'), 'http://lintian.debian.org/tags-all.html')
        self.LintianTags.SetBitmap(globe)
        
        self.Policy.AppendItem(self.DPM)
        self.Policy.AppendItem(self.DPMCtrl)
        self.Policy.AppendItem(self.DPMLog)
        self.Policy.AppendItem(self.UPM)
        self.Policy.AppendItem(self.DebFrmSrc)
        self.Policy.AppendItem(self.LintianTags)
        
        self.references = {
                    ID_DPM: 'http://www.debian.org/doc/debian-policy',
                    ID_DPMCtrl: 'http://www.debian.org/doc/debian-policy/ch-controlfields.html',
                    ID_DPMLog: 'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog',
                    ID_UPM: 'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/',
                    222: 'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source',
                    ID_Lintian: 'http://lintian.debian.org/tags-all.html'
                    }
        for ID in self.references:
            wx.EVT_MENU(self, ID, self.OpenPolicyManual)
        
        
        self.Help = wx.MenuItem(self.menu_help, wx.ID_HELP, _('Help'), _('Open a usage document'))
        self.About = wx.MenuItem(self.menu_help, wx.ID_ABOUT, _('About'), _('About Debreate'))
        
        self.menu_help.AppendMenu(-1, _('Reference'), self.Policy)
        self.menu_help.AppendSeparator()
        self.menu_help.AppendItem(self.Help)
        self.menu_help.AppendItem(self.About)
        
        wx.EVT_MENU(self, wx.ID_HELP, self.OnHelp)
        wx.EVT_MENU(self, wx.ID_ABOUT, self.OnAbout)
        
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        
        self.menubar.Insert(0, self.menu_file, _('File'))
        self.menubar.Insert(1, self.menu_page, _('Page'))
        self.menubar.Insert(2, self.menu_opt, _('Options'))
        self.menubar.Insert(3, self.menu_help, _('Help'))
        
        # ***** END MENUBAR ***** #
        
        self.Wizard = Wizard(self) # Binary
        
        self.page_info = PanelInfo(self.Wizard)
        self.page_info.SetInfo()
        self.page_control = PanelControl(self.Wizard)
        self.page_depends = PanelDepends(self.Wizard)
        self.page_files = PanelFiles(self.Wizard)
        self.page_scripts = PanelScripts(self.Wizard)
        self.page_clog = PanelChangelog(self.Wizard)
        self.page_cpright = PanelCopyright(self.Wizard)
        self.page_menu = PanelMenu(self.Wizard)
        self.page_build = PanelBuild(self.Wizard)
        
        self.all_pages = (
            self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_menu, self.page_build
            )
        
        self.bin_pages = (
            self.page_info, self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_menu, self.page_build
            )
        
        self.Wizard.SetPages(self.bin_pages)
        
        self.pages = {self.p_info: self.page_info, self.p_ctrl: self.page_control, self.p_deps: self.page_depends,
                self.p_files: self.page_files, self.p_scripts: self.page_scripts, self.p_clog: self.page_clog,
                self.p_cpright: self.page_cpright, self.p_menu: self.page_menu, self.p_build: self.page_build}
        for p in self.pages:
            wx.EVT_MENU(self, p.GetId(), self.GoToPage)
        
        # ----- Layout
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.Wizard, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.main_sizer)
        self.Layout()
        
        # Saving
        # First item is name of saved file displayed in title
        # Second item is actual path to project file
        self.saved_project = wx.EmptyString
    
    
    ### ***** Check for New Version ***** ###
    def OnCheckUpdate(self, event):
        if u'-dev' in VERSION_string:
            wx.MessageDialog(self, _(u'Update checking not supported in development versions'),
                    _(u'Update'), wx.OK|wx.ICON_INFORMATION).ShowModal()
            return
        
        wx.SafeYield()
        current = GetCurrentVersion()
        Logger.Debug(__name__, GT(u'URL request result: {}').format(current))
        if type (current) == URLError or type(current) == HTTPError:
            current = unicode(current)
            wx.MessageDialog(self, current, _(u'Error'), wx.OK|wx.ICON_ERROR).ShowModal()
        elif isinstance(current, tuple) and current > VERSION_tuple:
            current = '%s.%s.%s' % (current[0], current[1], current[2])
            l1 = _(u'Version %s is available!').decode('utf-8') % (current)
            l2 = _(u"Would you like to go to Debreate's website?").decode('utf-8')
            update = wx.MessageDialog(self, u'%s\n\n%s' % (l1, l2), _(u'Debreate'), wx.YES_NO|wx.ICON_INFORMATION).ShowModal()
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
            err = wx.MessageDialog(self, _(u'Debreate is up to date!'), _(u'Debreate'), wx.OK|wx.ICON_INFORMATION)
            err.CenterOnParent()
            err.ShowModal()
    
    
    ### ***** Menu Handlers ***** ###
    
    def OnNewProject(self, event):
        dia = wx.MessageDialog(self, _('You will lose any unsaved information\n\nContinue?'),
                _('Start New Project'), wx.YES_NO|wx.NO_DEFAULT)
        if dia.ShowModal() == wx.ID_YES:
            self.NewProject()
            #self.SetMode(None)
    
    def NewProject(self):
        for page in self.all_pages:
            page.ResetAllFields()
        self.SetTitle(self.default_title)
        
        # Reset the saved project field so we know that a project file doesn't exists
        self.saved_project = wx.EmptyString
    
    def OnOpenProject(self, event):
        cont = False
        dbp = '|*.dbp'
        d = _('Debreate project files')
        if self.cust_dias.IsChecked():
            dia = db.OpenFile(self, _('Open Debreate Project'))
            dia.SetFilter('%s%s' % (d, dbp))
            if dia.DisplayModal():
                cont = True
        else:
            dia = wx.FileDialog(self, _('Open Debreate Project'), os.getcwd(), '', '%s%s' % (d, dbp), wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                cont = True
        
        if cont:
            # Get the path and set the saved project
            self.saved_project = dia.GetPath()
            
            file = open(self.saved_project, 'r')
            data = file.read()
            file.close()
            
            filename = os.path.split(self.saved_project)[1]
            
            self.OpenProject(data, filename)
    
    
    ## Shows or hides tooltips
    def OnToggleToolTips(self, event=None):
        enabled = self.opt_tooltips.IsChecked()
        wx.ToolTip.Enable(enabled)
        
        WriteConfig(u'tooltips', enabled)
    
    
    def OpenProject(self, data, filename):
        lines = data.split('\n')
        app = lines[0].split('-')[0].split('[')[1]
        ver = lines[0].split('-')[1].split(']')[0]
        if app != 'DEBREATE':
            bad_file = wx.MessageDialog(self, _('Not a valid Debreate project'), _('Error'),
                    style=wx.OK|wx.ICON_ERROR)
            bad_file.ShowModal()
        else: 
            # Set title to show open project
            #self.SetTitle('Debreate - %s' % filename)
            
            # *** Get Control Data *** #
            control_data = data.split("<<CTRL>>\n")[1].split("\n<</CTRL>>")[0]
            depends_data = self.page_control.SetFieldData(control_data)
            self.page_depends.SetFieldData(depends_data)
            
            # *** Get Files Data *** #
            files_data = data.split("<<FILES>>\n")[1].split("\n<</FILES>>")[0]
            self.page_files.SetFieldData(files_data)
            
            # *** Get Scripts Data *** #
            scripts_data = data.split("<<SCRIPTS>>\n")[1].split("\n<</SCRIPTS>>")[0]
            self.page_scripts.SetFieldData(scripts_data)
            
            # *** Get Changelog Data *** #
            clog_data = data.split("<<CHANGELOG>>\n")[1].split("\n<</CHANGELOG>>")[0]
            self.page_clog.SetChangelog(clog_data)
            
            # *** Get Copyright Data *** #
            try:
                cpright_data = data.split("<<COPYRIGHT>>\n")[1].split("\n<</COPYRIGHT")[0]
                self.page_cpright.SetCopyright(cpright_data)
            except IndexError:
                pass
            
            # *** Get Menu Data *** #
            menu_data = data.split("<<MENU>>\n")[1].split("\n<</MENU>>")[0]
            self.page_menu.SetLauncherData(menu_data, enabled=True)
            
            # Get Build Data
            build_data = data.split("<<BUILD>>\n")[1].split("\n<</BUILD")[0]#.split("\n")
            self.page_build.SetFieldData(build_data)
    
    
    def OnQuit(self, event):
        """Show a dialog to confirm quit and write window settings to config file"""
        confirm = wx.MessageDialog(self, _('You will lose any unsaved information'), _('Quit?'),
                                   wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_OK: # Show a dialog to confirm quit
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
            
            WriteConfig(u'dialogs', self.cust_dias.IsChecked())
            WriteConfig(u'workingdir', os.getcwd())
            
            self.Destroy()
        else:
            confirm.Destroy()
    
    
    ## Changes wizard page
    #  
    #  \param event
    #        \b \e wx.MenuEvent|int : The event or integer to use as page ID
    def GoToPage(self, event):
        if isinstance(event, int):
            ID = event
        
        else:
            ID = event.GetId()
        
        self.Wizard.ShowPage(ID)
    
    # ----- Help Menu
    def OpenPolicyManual(self, event):
        id = event.GetId()  # Get the id for the webpage link we are opening
        webbrowser.open(self.references[id])
        #os.system("xdg-open %s" % self.references[id])  # Look in "manual" for the id and open the webpage
    
    
    ## Opens a dialog box with information about the program
    def OnAbout(self, event):
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
    
    
    def OnHelp(self, event):
        # First tries to open pdf help file. If fails tries to open html help file. If fails opens debreate usage webpage
        wx.Yield()
        status = subprocess.call(['xdg-open', '%s/docs/usage.pdf' % PATH_app])
        if status:
            wx.Yield()
            status = subprocess.call(['xdg-open', '%s/docs/usage' % PATH_app])
        if status:
            wx.Yield()
            webbrowser.open('http://debreate.sourceforge.net/usage')
    
    # *** SAVING *** #
    
    def IsSaved(self):
        title = self.GetTitle()
        if title[-1] == "*":
            return False
        else:
            return True
    
    def IsNewProject(self):
        title = self.GetTitle()
        if title == self.default_title:
            return True
        else:
            return False
    
    def SetSavedStatus(self, status):
        if status: # If status is changing to unsaved this is True
            title = self.GetTitle()
            if self.IsSaved() and title != self.default_title:
                self.SetTitle("%s*" % title)
    
    def OnSaveProject(self, event):
        id = event.GetId()
        
        def SaveIt(path):
                # Gather data from different pages
                data = (self.page_control.GatherData(), self.page_files.GatherData(),
                        self.page_scripts.GatherData(), self.page_clog.GatherData(),
                        self.page_cpright.GatherData(), self.page_menu.GatherData(),
                        self.page_build.GatherData())
                
                # Create a backup of the project
                overwrite = False
                if os.path.isfile(path):
                    backup = '%s.backup' % path
                    shutil.copy(path, backup)
                    overwrite = True
                
                savefile = open(path, 'w')
                # This try statement can be removed when unicode support is enabled
                try:
                    savefile.write("[DEBREATE-%s]\n%s" % (VERSION_string, "\n".join(data).encode('utf-8')))
                    savefile.close()
                    if overwrite:
                        os.remove(backup)
                except UnicodeEncodeError:
                    serr = _('Save failed')
                    uni = _('Unfortunately Debreate does not support unicode yet. Remove any non-ASCII characters from your project.')
                    UniErr = wx.MessageDialog(self, '%s\n\n%s' % (serr, uni), _('Unicode Error'), style=wx.OK|wx.ICON_EXCLAMATION)
                    UniErr.ShowModal()
                    savefile.close()
                    if overwrite:
                        os.remove(path)
                        # Restore project backup
                        shutil.move(backup, path)
                # Change the titlebar to show name of project file
                #self.SetTitle("Debreate - %s" % os.path.split(path)[1])
        
        def OnSaveAs():
            dbp = '|*.dbp'
            d = _('Debreate project files')
            cont = False
            if self.cust_dias.IsChecked():
                dia = db.SaveFile(self, _('Save Debreate Project'), 'dbp')
                dia.SetFilter('%s%s' % (d, dbp))
                if dia.DisplayModal():
                    cont = True
                    filename = dia.GetFilename()
                    if filename.split('.')[-1] == 'dbp':
                        filename = ".".join(filename.split(".")[:-1])
                    self.saved_project = "%s/%s.dbp" % (dia.GetPath(), filename)
            else:
                dia = wx.FileDialog(self, _('Save Debreate Project'), os.getcwd(), '', '%s%s' % (d, dbp),
                                        wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
                if dia.ShowModal() == wx.ID_OK:
                    cont = True
                    filename = dia.GetFilename()
                    if filename.split(".")[-1] == "dbp":
                        filename = ".".join(filename.split(".")[:-1])
                    self.saved_project = "%s/%s.dbp" %(os.path.split(dia.GetPath())[0], filename)
            
            if cont:
                SaveIt(self.saved_project)
        
        if id == wx.ID_SAVE:
            # Define what to do if save is pressed
            # If project already exists, don't show dialog
            if not self.IsSaved() or self.saved_project == wx.EmptyString or not os.path.isfile(self.saved_project):
                OnSaveAs()
            else:
                SaveIt(self.saved_project)
        else:
            # If save as is press, show the save dialog
            OnSaveAs()
    
    def OnQuickBuild(self, event):
        QB = QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
