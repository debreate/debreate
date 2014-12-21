# This script is no longer executable, use launch.py
# -*- coding: utf-8 -*-

"""
    Debreate - Debian Package Builder v0.7.3
    Copyright (C) 2010  Jordan Irwin <antumdeluge@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from common import *
import os, sys, wx.lib.dialogs, db, webbrowser, language, shutil, subprocess
from os.path import exists
import paninfo, pancontrol, pandepends, panfiles, panscripts, panclog, panmenu, panbuild
import pancopyright

ID_Dialogs = wx.NewId()

# Debian Policy Manual IDs
ID_DPM = wx.NewId()
ID_DPMCtrl = wx.NewId()
ID_DPMLog = wx.NewId()
ID_UPM = wx.NewId()
ID_Lintian = wx.NewId()

# Page IDs
ID_INFO = wx.NewId()
ID_CTRL = wx.NewId()
ID_DEPS = wx.NewId()
ID_FILES = wx.NewId()
ID_SCRIPTS = wx.NewId()
ID_CLOG = wx.NewId()
ID_CPRIGHT = wx.NewId()
ID_MENU = wx.NewId()
ID_BUILD = wx.NewId()
ID_QBUILD = wx.NewId()
ID_UPDATE = wx.NewId()


from common import application_path

class MainWindow(wx.Frame):
    def __init__(self, parent, id, title, pos, size):
        wx.Frame.__init__(self, parent, id, title, pos, size)
        
        self.application_path = application_path
        
        # The default title
        self.default_title = _('Debreate - Debian Package Builder')
        
        self.SetMinSize((640,400))
        
        # ----- Set Titlebar Icon
        self.main_icon = wx.Icon("%s/bitmaps/debreate64.png" % application_path, wx.BITMAP_TYPE_PNG)
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
                                         _('Quick Build'), _('Build a package from an existing build tree'))
        self.QuickBuild.SetBitmap(wx.Bitmap("%s/bitmaps/clock16.png" % self.application_path))
        
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
        
        self.p_info = wx.MenuItem(self.menu_page, ID_INFO, _('Information'), _('Go to Information section'),
                kind=wx.ITEM_RADIO)
        self.p_ctrl = wx.MenuItem(self.menu_page, ID_CTRL, _('Control'), _('Go to Control section'),
                kind=wx.ITEM_RADIO)
        self.p_deps = wx.MenuItem(self.menu_page, ID_DEPS, _('Dependencies'), _('Go to Dependencies section'), kind=wx.ITEM_RADIO)
        self.p_files = wx.MenuItem(self.menu_page, ID_FILES, _('Files'), _('Go to Files section'), kind=wx.ITEM_RADIO)
        self.p_scripts = wx.MenuItem(self.menu_page, ID_SCRIPTS, _('Scripts'), _('Go to Scripts section'), kind=wx.ITEM_RADIO)
        self.p_clog = wx.MenuItem(self.menu_page, ID_CLOG, _('Changelog'), _('Go to Changelog section'), kind=wx.ITEM_RADIO)
        self.p_cpright = wx.MenuItem(self.menu_page, ID_CPRIGHT, _('Copyright'), _('Go to Copyright section'), kind=wx.ITEM_RADIO)
        self.p_menu = wx.MenuItem(self.menu_page, ID_MENU, _('Menu Launcher'), _('Go to Menu Launcher section'), kind=wx.ITEM_RADIO)
        self.p_build = wx.MenuItem(self.menu_page, ID_BUILD, _('Build'), _('Go to Build section'), kind=wx.ITEM_RADIO)
        
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
        
        # Dialogs options
        self.cust_dias = wx.MenuItem(self.menu_opt, ID_Dialogs, _('Use Custom Dialogs'),
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
        
        globe = wx.Bitmap("%s/bitmaps/globe16.png" % self.application_path)
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
        for id in self.references:
            wx.EVT_MENU(self, id, self.OpenPolicyManual)
        
        
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
        
        self.Wizard = db.Wizard(self) # Binary
        
        self.page_info = paninfo.Panel(self.Wizard, ID_INFO)
        self.page_info.SetInfo()
        self.page_control = pancontrol.Panel(self.Wizard, ID_CTRL)
        self.page_depends = pandepends.Panel(self.Wizard, ID_DEPS)
        self.page_files = panfiles.Panel(self.Wizard, ID_FILES)
        self.page_scripts = panscripts.Panel(self.Wizard, ID_SCRIPTS)
        self.page_clog = panclog.Panel(self.Wizard, ID_CLOG)
        self.page_cpright = pancopyright.Panel(self.Wizard, ID_CPRIGHT)
        self.page_menu = panmenu.Panel(self.Wizard, ID_MENU)
        self.page_build = panbuild.Panel(self.Wizard, ID_BUILD)
        
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
        
        
        
    def OnMaximize(self, event):
        print "Maximized"
    
    
    ### ***** Check for New Version ***** ###
    def OnCheckUpdate(self, event):
        wx.SafeYield()
        current = GetCurrentVersion()
        if type (current) == URLError or type(current) == HTTPError:
            current = unicode(current)
            wx.MessageDialog(self, current, _(u'Error'), wx.OK|wx.ICON_ERROR).ShowModal()
        elif (current > db_version):
            current = '%s.%s.%s' % (current[0], current[1], current[2])
            l1 = _(u'Version %s is available!').decode('utf-8') % (current)
            l2 = _(u"Would you like to go to Debreate's website?").decode('utf-8')
            update = wx.MessageDialog(self, u'%s\n\n%s' % (l1, l2), _(u'Debreate'), wx.YES_NO|wx.ICON_INFORMATION).ShowModal()
            if (update == wx.ID_YES):
                wx.LaunchDefaultBrowser(db_website)
        else:
            wx.MessageDialog(self, _(u'Debreate is up to date!'), _(u'Debreate'), wx.OK|wx.ICON_INFORMATION).ShowModal()
    
    
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
            self.page_menu.SetFieldData(menu_data)
            
            # Get Build Data
            build_data = data.split("<<BUILD>>\n")[1].split("\n<</BUILD")[0]#.split("\n")
            self.page_build.SetFieldData(build_data)
    
    # ----- File Menu
    def ConvertToRPM(self, event):
        # This app uses alien to convert debian binary/basic packages to red had format.
        # The acutal command is "fakeroot alien -rck [package_name].deb"
        # alien cannot convert packages that are in a path with spaces in it, and it will also fail
        # if the package's file extension is anything other than ".deb", e.g. ".DEB", ".DeB".
        app = debrpm.Dialog(self, -1, _("Deb to RPM"))
        app.ShowModal()
        app.Close()
    
    def OnQuit(self, event):
        """Show a dialog to confirm quit and write window settings to config file"""
        confirm = wx.MessageDialog(self, _('You will lose any unsaved information'), _('Quit?'),
                                   wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        if confirm.ShowModal() == wx.ID_OK: # Show a dialog to confirm quit
            confirm.Destroy()
            
            # Get window attributes and save to config file
            if self.IsMaximized():	# If window is maximized upon closing the program will set itself back to
                size = "800,650"		# an 800x650 window (ony when restored back down, the program will open
                maximize = 1        # maximized)
                pos = "0,0"
                center = 1
            else:
                size = "%s,%s" % (self.GetSize()[0], self.GetSize()[1])
                maximize = 0
                pos = "%s,%s" % (self.GetPosition()[0], self.GetPosition()[1])
                center = 0
            
            if self.cust_dias.IsChecked():
                dias = 1
            else:
                dias = 0
            
            # Save current working directory for next session
            cwd = os.getcwd()
            
            # Open and write new config file
            if not os.path.isdir(self.dbdir):
                os.mkdir (self.dbdir)
            config_file = open(self.dbconfig, "w")
            config_file.write("\
[CONFIG-1.1]\n\
position=%s\n\
size=%s\n\
maximize=%s\n\
center=%s\n\
dialogs=%s\n\
workingdir=%s" % (pos, size, maximize, center, dias, cwd))
            config_file.close()
            
            self.Destroy()
        else:
            confirm.Destroy()
    
    
    # ----- Page Menu
    def GoToPage(self, event):
        for p in self.pages:
            if p.IsChecked():
                id = p.GetId()
        
        self.Wizard.ShowPage(id)
    
    # ----- Help Menu
    def OpenPolicyManual(self, event):
        id = event.GetId()  # Get the id for the webpage link we are opening
        webbrowser.open(self.references[id])
        #os.system("xdg-open %s" % self.references[id])  # Look in "manual" for the id and open the webpage
    
    def OnAbout(self, event):
        """Opens a dialog box with information about the program"""
        about = db.AboutDialog(self, -1, _('About'))
        
        #about.SetGraphic("%s/bitmaps/debreate64.png" % application_path)
        about.SetVersion(_('Debreate'), debreate_version)
        about.SetAuthor('Jordan Irwin')
        #about.SetWebsite('http://debreate.sourceforge.net')
        about.SetDescription(_('A package builder for Debian based systems'))
        
        about.AddDeveloper("Jordan Irwin", "antumdeluge@gmail.com")
        about.AddPackager("Jordan Irwin", "antumdeluge@gmail.com")
        job = _(u'Translation')
        job = job.decode(u'utf-8')
        about.AddJob(_(u'Karim Oulad Chalha'), u'%s (ar_MA)' % (job), u'herr.linux88@gmail.com')
        about.AddJob(u'Jordan Irwin', u'%s (es)' % (job), u'antumdeluge@gmail.com')
        about.AddJob(_(u'Philippe Dalet'), u'%s (fr_FR)' % (job), u'philippe.dalet@ac-toulouse.fr')
        about.AddJob(_(u'Zhmurkov Sergey'), u'%s (ru)' % (job), u'zhmsv@yandex.ru')
        
        file = open('%s/docs/changelog' % (application_path), 'r')
        log = file.read()
        file.close()
        about.SetChangelog(log)
        
        file = open('%s/docs/gpl-3.0.txt' % application_path, 'r')
        license = file.read()
        file.close()
        about.SetLicense(license)
        
        about.ShowModal()
        about.Destroy()
        
    def OnHelp(self, event):
        # First tries to open pdf help file. If fails tries to open html help file. If fails opens debreate usage webpage
        wx.Yield()
        status = subprocess.call(['xdg-open', '%s/docs/usage.pdf' % application_path])
        if status:
            wx.Yield()
            status = subprocess.call(['xdg-open', '%s/docs/usage' % application_path])
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
                    savefile.write("[DEBREATE-%s]\n%s" % (debreate_version, "\n".join(data).encode('utf-8')))
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
        QB = panbuild.QuickBuild(self)
        QB.ShowModal()
        QB.Destroy()
