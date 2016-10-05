# This script is no longer executable, use init.py
# -*- coding: utf-8 -*-


# System modules
import wx, os, shutil, subprocess, webbrowser, tarfile, magic
from urllib2 import URLError, HTTPError

# Local modules
import dbr, wiz_bin
from dbr import Logger, DebugEnabled
from dbr.language import GT
from dbr.constants import VERSION, VERSION_STRING, HOMEPAGE, AUTHOR, \
    ID_BUILD, ID_CHANGELOG, ID_MAN, ID_CONTROL, ID_COPYRIGHT, ID_DEPENDS,\
    ID_GREETING, ID_FILES, ID_SCRIPTS, ID_MENU, ID_ZIP_NONE,\
    ID_ZIP_GZ, ID_ZIP_BZ2, ID_ZIP_XZ, compression_formats, ID_ZIP_ZIP,\
    PROJECT_FILENAME_SUFFIX, PROJECT_LEGACY_SUFFIX, compression_mimetypes, \
    custom_errno
from dbr.config import GetDefaultConfigValue, WriteConfig


# Pages
ID_Dialogs = wx.NewId()

# Debian Policy Manual IDs
ID_DPM = wx.NewId()
ID_DPMCtrl = wx.NewId()
ID_DPMLog = wx.NewId()
ID_UPM = wx.NewId()
ID_Lintian = wx.NewId()

ID_QBUILD = wx.NewId()
ID_UPDATE = wx.NewId()


default_title = GT(u'Debreate - Debian Package Builder')


class MainWindow(wx.Frame):
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, default_title, pos, size)
        
        self.workingdir = None
        
        self.SetMinSize((640,400))
        
        # ----- Set Titlebar Icon
        self.main_icon = wx.Icon(u'{}/bitmaps/debreate64.png'.format(dbr.application_path), wx.BITMAP_TYPE_PNG)
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
        self.QuickBuild.SetBitmap(wx.Bitmap(u'{}/bitmaps/clock16.png'.format(dbr.application_path)))
        
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
        
        # Debugging
        if DebugEnabled():
            wx.EVT_MENU(self, wx.ID_SAVE, self.SaveProject)
        else:
            wx.EVT_MENU(self, wx.ID_SAVE, self.OnSaveProjectDeprecated)
        
        wx.EVT_MENU(self, wx.ID_SAVEAS, self.OnSaveProjectDeprecated)
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
        
        if DebugEnabled():
            # FIXME: Add to Gettext locale files
            self.p_man = wx.MenuItem(self.menu_page, ID_MAN, GT(u'Manpages'),
                    GT(u'Go to Manpages section'), kind=wx.ITEM_RADIO)
        
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
        
        if DebugEnabled():
            self.menu_page.AppendItem(self.p_man)
        
        self.menu_page.AppendItem(self.p_scripts)
        self.menu_page.AppendItem(self.p_clog)
        self.menu_page.AppendItem(self.p_cpright)
        self.menu_page.AppendItem(self.p_menu)
        self.menu_page.AppendItem(self.p_build)
        
        # ----- Options Menu
        self.menu_opt = wx.Menu()
        
        # Dialogs options
        self.cust_dias = wx.MenuItem(self.menu_opt, ID_Dialogs, GT(u'Use Custom Dialogs'),
            GT(u'Use System or Custom Save/Open Dialogs'), kind=wx.ITEM_CHECK)
        
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
        opt_compression_xz = wx.MenuItem(self.menu_compression, ID_ZIP_XZ,
                GT(u'XZ'), GT(u'Use compressed xz tarball for project save format'),
                kind=wx.ITEM_RADIO)
        opt_compression_zip = wx.MenuItem(self.menu_compression, ID_ZIP_ZIP,
                GT(u'Zip'), GT(u'Use compressed zip file for project save format'),
                kind=wx.ITEM_RADIO)
        
        compression_opts = (
            opt_compression_uncompressed,
            opt_compression_gz,
            opt_compression_bz2,
            opt_compression_xz,
            opt_compression_zip,
        )
        
        for OPT in compression_opts:
            self.menu_compression.AppendItem(OPT)
        
        # TODO: Re-enable when formats are ready for use
        self.menu_compression.Enable(ID_ZIP_XZ, False)
        self.menu_compression.Enable(ID_ZIP_ZIP, False)
        
        # Default compression
        self.menu_compression.Check(ID_ZIP_BZ2, True)
        
        self.menu_opt.AppendItem(self.cust_dias)
        self.menu_opt.AppendSubMenu(self.menu_compression, GT(u'Project Compression'),
                GT(u'Set the compression type for project save output'))
        
        # ----- Help Menu
        self.menu_help = wx.Menu()
        
        # ----- Version update
        self.version_check = wx.MenuItem(self.menu_help, ID_UPDATE, GT(u'Check for Update'))
        self.menu_help.AppendItem(self.version_check)
        self.menu_help.AppendSeparator()
        
        wx.EVT_MENU(self, ID_UPDATE, self.OnCheckUpdate)
        
        # Menu with links to the Debian Policy Manual webpages
        self.Policy = wx.Menu()
        
        globe = wx.Bitmap(u'{}/bitmaps/globe16.png'.format(dbr.application_path))
        self.DPM = wx.MenuItem(self.Policy, ID_DPM, GT(u'Debian Policy Manual'), u'http://www.debian.org/doc/debian-policy')
        self.DPM.SetBitmap(globe)
        self.DPMCtrl = wx.MenuItem(self.Policy, ID_DPMCtrl, GT(u'Control Files'), u'http://www.debian.org/doc/debian-policy/ch-controlfields.html')
        self.DPMCtrl.SetBitmap(globe)
        self.DPMLog = wx.MenuItem(self.Policy, ID_DPMLog, GT(u'Changelog'), u'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog')
        self.DPMLog.SetBitmap(globe)
        self.UPM = wx.MenuItem(self.Policy, ID_UPM, GT(u'Ubuntu Policy Manual'), u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/')
        self.UPM.SetBitmap(globe)
        self.DebFrmSrc = wx.MenuItem(self.Policy, 222, GT(u'Building debs from Source'), u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source') # This is here only temporarily for reference
        self.DebFrmSrc.SetBitmap(globe)
        self.LintianTags = wx.MenuItem(self.Policy, ID_Lintian, GT(u'Lintian Tags Explanation'), u'http://lintian.debian.org/tags-all.html')
        self.LintianTags.SetBitmap(globe)
        
        self.Policy.AppendItem(self.DPM)
        self.Policy.AppendItem(self.DPMCtrl)
        self.Policy.AppendItem(self.DPMLog)
        self.Policy.AppendItem(self.UPM)
        self.Policy.AppendItem(self.DebFrmSrc)
        self.Policy.AppendItem(self.LintianTags)
        
        self.references = {
                    ID_DPM: u'http://www.debian.org/doc/debian-policy',
                    ID_DPMCtrl: u'http://www.debian.org/doc/debian-policy/ch-controlfields.html',
                    ID_DPMLog: u'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog',
                    ID_UPM: u'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/',
                    222: u'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source',
                    ID_Lintian: u'http://lintian.debian.org/tags-all.html'
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
        
        self.menubar.Insert(0, self.menu_file, GT(u'File'))
        self.menubar.Insert(1, self.menu_page, GT(u'Page'))
        self.menubar.Insert(2, self.menu_opt, GT(u'Options'))
        self.menubar.Insert(3, self.menu_help, GT(u'Help'))
        
        # FIXME: QuickBuild broken
        self.QuickBuild.SetText(u'Quick Build (Broken)')
        self.QuickBuild.Enable(False)
        
        # ***** END MENUBAR ***** #
        
        self.wizard = dbr.Wizard(self) # Binary
        
        self.page_info = wiz_bin.PageGreeting(self.wizard)
        self.page_info.SetInfo()
        self.page_control = wiz_bin.PageControl(self.wizard)
        self.page_depends = wiz_bin.PageDepends(self.wizard)
        self.page_files = wiz_bin.PageFiles(self.wizard)
        
        if DebugEnabled():
            self.page_man = wiz_bin.PageMan(self.wizard)
        
        self.page_scripts = wiz_bin.PageScripts(self.wizard)
        self.page_clog = wiz_bin.PageChangelog(self.wizard)
        self.page_cpright = wiz_bin.PageCopyright(self.wizard)
        self.page_menu = wiz_bin.PageMenu(self.wizard)
        self.page_build = wiz_bin.PageBuild(self.wizard)
        
        self.all_pages = (
            self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_menu, self.page_build
            )
        
        self.bin_pages = [
            self.page_info, self.page_control, self.page_depends, self.page_files, self.page_scripts,
            self.page_clog, self.page_cpright, self.page_menu, self.page_build
            ]
        
        if DebugEnabled():
            self.bin_pages.insert(4, self.page_man)
        
        self.wizard.SetPages(self.bin_pages)
        
        self.pages = {self.p_info: self.page_info, self.p_ctrl: self.page_control, self.p_deps: self.page_depends,
                self.p_files: self.page_files, self.p_scripts: self.page_scripts, self.p_clog: self.page_clog,
                self.p_cpright: self.page_cpright, self.p_menu: self.page_menu, self.p_build: self.page_build}
        
        if DebugEnabled():
            self.pages[self.p_man] = self.page_man
        
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
    
    
    ## Sets working directory for file open/save dialogs
    #  
    #  FIXME: Unused?
    #  \param target
    #        \b \e unicode|str : Target directory
    def SetWorkingDirectory(self, target):
        if target != None:
            self.workingdir = target
        else:
            self.workingdir = GetDefaultConfigValue(u'workingdir')
        
        if not os.path.isdir(self.workingdir):
            Logger.Warning(__name__, GT(u'Working directory set to "{}" which is not an actual directory'.format(self.workingdir)))
    
        
    def OnMaximize(self, event):
        # FIXME: ???
        print(u'Maximized')
    
    
    ### ***** Check for New Version ***** ###
    def OnCheckUpdate(self, event):
        wx.SafeYield()
        current = dbr.GetCurrentVersion()
        if isinstance(current, URLError) or isinstance(current, HTTPError):
            current = unicode(current)
            wx.MessageDialog(self, current, GT(u'Error'), wx.OK|wx.ICON_ERROR).ShowModal()
        elif (current > VERSION):
            current = u'{}.{}.{}'.format(current[0], current[1], current[2])
            l1 = GT(u'Version %s is available!').decode(u'utf-8') % (current)
            l2 = GT(u'Would you like to go to Debreate\'s website?').decode(u'utf-8')
            update = wx.MessageDialog(self, u'{}\n\n{}'.format(l1, l2), GT(u'Debreate'), wx.YES_NO|wx.ICON_INFORMATION).ShowModal()
            if (update == wx.ID_YES):
                wx.LaunchDefaultBrowser(HOMEPAGE)
        elif (current < VERSION):
            wx.MessageDialog(self, GT(u'This is a development version, no updates available'),
                    GT(u'Debreate'), wx.OK|wx.ICON_INFORMATION).ShowModal()
        else:
            wx.MessageDialog(self, GT(u'Debreate is up to date!'), GT(u'Debreate'), wx.OK|wx.ICON_INFORMATION).ShowModal()
    
    
    ### ***** Menu Handlers ***** ###
    
    def OnNewProject(self, event):
        dia = wx.MessageDialog(self, GT(u'You will lose any unsaved information\n\nContinue?'),
                GT(u'Start New Project'), wx.YES_NO|wx.NO_DEFAULT)
        if dia.ShowModal() == wx.ID_YES:
            self.NewProject()
            #self.SetMode(None)
    
    def NewProject(self):
        for page in self.all_pages:
            page.ResetAllFields()
        self.SetTitle(default_title)
        
        # Reset the saved project field so we know that a project file doesn't exists
        self.saved_project = wx.EmptyString
    
    def OnOpenProject(self, event):
        cont = False
        dbp = u'|*.{};*.{}'.format(PROJECT_FILENAME_SUFFIX, PROJECT_LEGACY_SUFFIX)
        d = GT(u'Debreate projects (*.{}, *.{})'.format(PROJECT_FILENAME_SUFFIX, PROJECT_LEGACY_SUFFIX))
        if self.cust_dias.IsChecked():
            dia = dbr.OpenFile(self, GT(u'Open Debreate Project'))
            dia.SetFilter(u'{}{}'.format(d, dbp))
            if dia.DisplayModal():
                cont = True
        else:
            dia = wx.FileDialog(self, GT(u'Open Debreate Project'), os.getcwd(), u'', u'{}{}'.format(d, dbp), wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                cont = True
        
        if cont:
            # Get the path and set the saved project
            self.saved_project = dia.GetPath()
            
            file_identifier = magic.open(magic.MAGIC_MIME)
            file_identifier.load()
            file_type = file_identifier.file(self.saved_project).split(u';')[0]
            file_identifier.close()
            
            if file_type == u'text/plain':
                p_open = open(self.saved_project, u'r')
                p_text = p_open.read()
                p_open.close()
                
                filename = os.path.split(self.saved_project)[1]
                
                self.OpenProjectLegacy(p_text, filename)
                
                return
            
            self.OpenProject(self.saved_project, file_type)
    
    #  TODO: Finish defining
    def OpenProject(self, filename, file_type):
        if DebugEnabled():
            print(u'Opening project: {}, Type: {}'.format(filename, file_type))
        
        if file_type not in compression_mimetypes:
            Logger.Error(__name__, GT(u'Cannot open project with compression mime type "{}"'.format(file_type)))
            return custom_errno.EBADFT
        
        compression_id = compression_mimetypes[file_type]
        
        z_format = compression_formats[compression_id]
        
        if z_format == u'None':
            z_format = u'r'
        else:
            z_format = u'r:{}'.format(z_format)
        
        if DebugEnabled():
            print(u'Opening tarfile with "{}" format'.format(z_format))
        
        p_archive = tarfile.open(filename, z_format)
        
        if DebugEnabled():
            print(p_archive.getmembers())
            print(p_archive.getnames())
        
        # FIXME: This should be a global
        temp_dir = u'/tmp'
        temp_suffix = u'debreate_{}_temp'.format(VERSION_STRING)
        
        if os.access(temp_dir, os.W_OK):
            temp_dir = u'{}/{}'.format(temp_dir, temp_suffix)
        
        else:
            temp_dir = u'{}/{}'.format(os.getcwd(), temp_suffix)
        
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        
        os.makedirs(temp_dir)
        
        if os.access(temp_dir, os.W_OK):
            p_archive.extractall(temp_dir)
            p_archive.close()
            
            ret_code = self.wizard.ImportPagesInfo(temp_dir)
            
            shutil.rmtree(temp_dir)
            
            return ret_code
        
        Logger.Error(__name__, GT(u'Could not get permission to write temporary directory'))
        return custom_errno.EACCES
    
    
    def OpenProjectLegacy(self, data, filename):
        def ProjectError():
            wx.MessageDialog(self, GT(u'Not a valid Debreate project'), GT(u'Error'),
    		                       style=wx.OK|wx.ICON_ERROR).ShowModal()
        
        if data == wx.EmptyString:
            ProjectError()
            return
        
        lines = data.split(u'\n')
        app = lines[0].split(u'-')[0].split(u'[')[1]
        #ver = lines[0].split(u'-')[1].split(u']')[0]
        
        if app != u'DEBREATE':
            ProjectError()
            return
            
        # Set title to show open project
        #self.SetTitle(u'Debreate - %s' % filename)
        
        # *** Get Control Data *** #
        control_data = data.split(u'<<CTRL>>\n')[1].split(u'\n<</CTRL>>')[0]
        depends_data = self.page_control.SetFieldData(control_data)
        self.page_depends.SetFieldData(depends_data)
        
        # *** Get Files Data *** #
        files_data = data.split(u'<<FILES>>\n')[1].split(u'\n<</FILES>>')[0]
        self.page_files.SetFieldDataDeprecated(files_data)
        
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
        self.page_menu.SetFieldData(menu_data)
        
        # Get Build Data
        build_data = data.split(u'<<BUILD>>\n')[1].split(u'\n<</BUILD')[0]#.split(u'\n')
        self.page_build.SetFieldData(build_data)
    
    
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
            if maximized:	# Save default window settings if maximized
                WriteConfig(u'size', GetDefaultConfigValue(u'size'))
                WriteConfig(u'position', GetDefaultConfigValue(u'position'))
                WriteConfig(u'center', GetDefaultConfigValue(u'center'))
                WriteConfig(u'maximize', True)
            else:
                WriteConfig(u'size', (self.GetSize()[0], self.GetSize()[1]))
                WriteConfig(u'position', (self.GetPosition()[0], self.GetPosition()[1]))
                WriteConfig(u'center', False)
                WriteConfig(u'maximize', False)
            
            WriteConfig(u'workingdir', os.getcwd())
            WriteConfig(u'dialogs', self.cust_dias.IsChecked())
            WriteConfig(u'compression', self.GetCompression())
            
            self.Destroy()
        
        else:
            confirm.Destroy()
    
    
    # ----- Page Menu
    def GoToPage(self, event):
        for p in self.pages:
            if p.IsChecked():
                PAGE_ID = p.GetId()
        
        self.wizard.ShowPage(PAGE_ID)
    
    # ----- Help Menu
    def OpenPolicyManual(self, event):
        EVENT_ID = event.GetId()  # Get the id for the webpage link we are opening
        webbrowser.open(self.references[EVENT_ID])
    
    def OnAbout(self, event):
        '''Opens a dialog box with information about the program'''
        about = dbr.AboutDialog(self)
        
        about.SetGraphic(u'{}/bitmaps/debreate64.png'.format(dbr.application_path))
        about.SetVersion(VERSION_STRING)
        about.SetAuthor(AUTHOR)
        about.SetDescription(GT(u'A package builder for Debian based systems'))
        
        about.AddDeveloper(AUTHOR, u'antumdeluge@gmail.com')
        
        about.AddJob(u'Hugo Posnic', u'Code Contributer', u'hugo.posnic@gmail.com')
        
        about.AddPackager(AUTHOR, u'antumdeluge@gmail.com')
        
        about.AddTranslator(u'Karim Oulad Chalha', u'herr.linux88@gmail.com', u'ar', )
        about.AddTranslator(AUTHOR, u'antumdeluge@gmail.com', u'es, it')
        about.AddTranslator(u'Philippe Dalet', u'philippe.dalet@ac-toulouse.fr', u'fr')
        about.AddTranslator(u'Zhmurkov Sergey', u'zhmsv@yandex.ru', u'ru')
        
        about.SetChangelog()
        
        about.SetLicense()
        
        about.ShowModal()
        about.Destroy()
        
    def OnHelp(self, event):
        if dbr.DebugEnabled():
            dbr.HelpDialog(self).ShowModal()
        
        else:
            # First tries to open pdf help file. If fails tries to open html help file. If fails opens debreate usage webpage
            wx.Yield()
            status = subprocess.call([u'xdg-open', u'{}/docs/usage.pdf'.format(dbr.application_path)])
            if status:
                wx.Yield()
                status = subprocess.call([u'xdg-open', u'{}/docs/usage'.format(dbr.application_path)])
            if status:
                wx.Yield()
                webbrowser.open(u'http://debreate.sourceforge.net/usage')
    
    # *** SAVING *** #
    
    def IsSaved(self):
        title = self.GetTitle()
        
        return bool(title[-1] == "*")
    
    def IsNewProject(self):
        title = self.GetTitle()
        
        return bool(title == self.default_title)
    
    def SetSavedStatus(self, status):
        if status: # If status is changing to unsaved this is True
            title = self.GetTitle()
            if self.IsSaved() and title != default_title:
                self.SetTitle(u'{}*'.format(title))
    
    
    ## Saves project in archive format
    #  
    #  Supported uncompressed formats are unix tarball.
    #  Supported compressed formats are Gzip & Bzip2
    #    tarballs.
    #  Proposed formats are xz compressed tarball &
    #    zip compressed file.
    def SaveProject(self, event):
        Logger.Debug(__name__, GT(u'Saving in new project format'))
        
        title = GT(u'Save Debreate Project')
        suffix = dbr.PROJECT_FILENAME_SUFFIX
        
        # Set Displayed description & filename filter for dialog
        dbp = u'|*.{}'.format(suffix)
        description = GT(u'Debreate project files')
        ext_filter = u'{} (.{}){}'.format(description, suffix, dbp)
        
        file_save = dbr.GetFileSaveDialog(self, title,
                ext_filter, suffix)
        if dbr.ShowDialog(self, file_save):
            self.saved_project = file_save.GetPath()
            
            working_path = os.path.dirname(self.saved_project)
            output_filename = os.path.basename(self.saved_project)
            temp_path = u'{}_temp'.format(self.saved_project)
            
            Logger.Debug(
                __name__,
                u'Save project\n\tWorking path: {}\n\tFilename: {}\n\tTemp directory: {}'.format(working_path,
                                                                                            output_filename, temp_path)
            )
            
            if os.path.exists(temp_path):
                if wx.MessageDialog(self, GT(u'Temp directory already exists.\nOverwrite?'), GT(u'Warning'),
                                        wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION).ShowModal() == wx.ID_YES:
                
                    Logger.Debug(__name__, u'Overwriting temp directory: {}'.format(temp_path))
                    shutil.rmtree(temp_path)
                
                else:
                    Logger.Debug(__name__, u'Not Overwriting temp directory: {}'.format(temp_path))
                    return 0
            
            os.makedirs(temp_path)
            
            export_pages = (
                self.page_control,
                self.page_files,
                self.page_scripts,
                self.page_clog,
                self.page_cpright,
                self.page_menu,
                self.page_build,
            )
            self.wizard.ExportPages(export_pages, temp_path)
            
            file_list = []
            for PATH, DIRS, FILES in os.walk(temp_path):
                for F in FILES:
                    file_list.append(F)
            
            if DebugEnabled():
                print(u'DEBUG:')
                print(u'Output archive: {}.dbpz'.format(output_filename))
                print(u'Temp directory: {}'.format(temp_path))
                print(u'Working directory: {}'.format(working_path))
                print(u'File list: {}'.format(file_list))
            
            
            z_format = self.GetCompression()
            
            # Uncompressed tarball
            if z_format == u'None':
                z_format = u'w'
            else:
                z_format = u'w:{}'.format(z_format)
            
            Logger.Debug(__name__, u'Output compression: {}'.format(z_format))
            
            p_archive = tarfile.open(u'{}.dbpz'.format(self.saved_project), z_format)
            
            for F in file_list:
                if DebugEnabled():
                    print(u'DEBUG: Adding file "{}/{}"'.format(temp_path, F))
                
                p_archive.add(u'{}/{}'.format(temp_path, F), arcname=F)
            
            p_archive.close()
            
            #shutil.make_archive(temp_path, u'bztar', temp_path)
            
            #debug_output = commands.getoutput(u'tar -cjf "{}/{}.dbpz" "{}"'.format(working_path, output_filename, temp_path))
            
            #print(u'DEBUG: {}'.format(debug_output))
            
            if os.path.isfile(u'{}.dbpz'.format(self.saved_project)):
                #os.rename(u'{}.tar.bz2'.format(self.saved_project), u'{}.dbpz'.format(self.saved_project))
                shutil.rmtree(temp_path)
            
        
        return 0
    
    
    def GetCompression(self):
        for Z in self.menu_compression.GetMenuItems():
            Z_ID = Z.GetId()
            if self.menu_compression.IsChecked(Z_ID):
                return compression_formats[Z_ID]
        
        default_compression = GetDefaultConfigValue(u'compression')
        
        Logger.Debug(__name__,
                GT(u'Setting compression to default value: {}'.format(default_compression)))
        
        return default_compression
    
    
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
            
    
    
    def OnSaveProjectDeprecated(self, event):
        EVENT_ID = event.GetId()
        
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
                    savefile.write(u'[DEBREATE-{}]\n{}'.format(VERSION_STRING, u'\n'.join(data).encode(u'utf-8')))
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
                # Change the titlebar to show name of project file
                #self.SetTitle(u'Debreate - %s' % os.path.split(path)[1])
        
        def OnSaveAs():
            dbp = u'|*.dbp'
            d = GT(u'Debreate project files')
            cont = False
            if self.cust_dias.IsChecked():
                dia = dbr.SaveFile(self, GT(u'Save Debreate Project'), u'dbp')
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
        
        if EVENT_ID == wx.ID_SAVE:
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
        QB = wiz_bin.QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
