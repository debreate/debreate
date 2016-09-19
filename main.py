# This script is no longer executable, use init.py
# -*- coding: utf-8 -*-


import os, shutil, subprocess
from urllib2 import URLError, HTTPError
import webbrowser
from wx import \
	CANCEL as wxCANCEL, \
	EXPAND as wxEXPAND, \
	ICON_ERROR as wxICON_ERROR, \
	ICON_INFORMATION as wxICON_INFORMATION, \
	ICON_QUESTION as wxICON_QUESTION, \
	ITEM_CHECK as wxITEM_CHECK, \
	ITEM_RADIO as wxITEM_RADIO, \
	NO_DEFAULT as wxNO_DEFAULT, \
	OK as wxOK, \
	VERTICAL as wxVERTICAL, \
	YES_NO as wxYES_NO, \
	ID_ABOUT as wxID_ABOUT, \
	ID_EXIT as wxID_EXIT, \
	ID_HELP as wxID_HELP, \
	ID_NEW as wxID_NEW, \
	ID_OK as wxID_OK, \
	ID_OPEN as wxID_OPEN, \
	ID_SAVE as wxID_SAVE, \
	ID_SAVEAS as wxID_SAVEAS, \
	ID_YES as wxID_YES, \
	FD_CHANGE_DIR as wxFD_CHANGE_DIR, \
	FD_OVERWRITE_PROMPT as wxFD_OVERWRITE_PROMPT, \
	FD_SAVE as wxFD_SAVE, \
	BITMAP_TYPE_PNG as wxBITMAP_TYPE_PNG, \
	EVT_CLOSE as wxEVT_CLOSE, \
	EVT_MAXIMIZE as wxEVT_MAXIMIZE, \
	EVT_MENU as wxEVT_MENU, \
    ICON_EXCLAMATION as wxICON_EXCLAMATION
from wx import \
	NewId as wxNewId, \
	Bitmap as wxBitmap, \
	BoxSizer as wxBoxSizer, \
	EmptyString as wxEmptyString, \
	FileDialog as wxFileDialog, \
	Frame as wxFrame, \
	Icon as wxIcon, \
	LaunchDefaultBrowser as wxLaunchDefaultBrowser, \
	Menu as wxMenu, \
	MenuBar as wxMenuBar, \
	MenuItem as wxMenuItem, \
	MessageDialog as wxMessageDialog, \
	SafeYield as wxSafeYield, \
	StatusBar as wxStatusBar, \
    Yield as wxYield

import dbr
from dbr.constants import VERSION, VERSION_STRING, HOMEPAGE
'''from page import \
	info as InfoPage, \
    control as ControlPage, \
    depends as DependsPage, \
    files as FilesPage, \
    scripts as ScriptsPage, \
    clog as ClogPage, \
    copyright as CopyrightPage, \
	menu as MenuPage, \
    build as BuildPage
    '''
import wiz_bin


# Pages
ID_Dialogs = wxNewId()

# Debian Policy Manual IDs
ID_DPM = wxNewId()
ID_DPMCtrl = wxNewId()
ID_DPMLog = wxNewId()
ID_UPM = wxNewId()
ID_Lintian = wxNewId()

# Page IDs
ID_INFO = wxNewId()
ID_CTRL = wxNewId()
ID_DEPS = wxNewId()
ID_FILES = wxNewId()
ID_SCRIPTS = wxNewId()
ID_CLOG = wxNewId()
ID_CPRIGHT = wxNewId()
ID_MENU = wxNewId()
ID_BUILD = wxNewId()
ID_QBUILD = wxNewId()
ID_UPDATE = wxNewId()



class MainWindow(wxFrame):
    def __init__(self, parent, id, title, pos, size):
        wxFrame.__init__(self, parent, id, title, pos, size)

        # The default title
        self.default_title = _('Debreate - Debian Package Builder')

        self.SetMinSize((640,400))

        # ----- Set Titlebar Icon
        self.main_icon = wxIcon("{}/bitmaps/debreate64.png".format(dbr.application_path), wxBITMAP_TYPE_PNG)
        self.SetIcon(self.main_icon)

        # If window is maximized this will store last window size and position for next session
        wxEVT_MAXIMIZE(self, self.OnMaximize)

        # ----- Status Bar
        self.stat_bar = wxStatusBar(self, -1)
        self.SetStatusBar(self.stat_bar)



        # ***** Menu Bar ***** #

        # ----- File Menu
        self.menu_file = wxMenu()

        # Quick Build
        self.QuickBuild = wxMenuItem(self.menu_file, ID_QBUILD,
                                         _('Quick Build'), _('Build a package from an existing build tree'))
        self.QuickBuild.SetBitmap(wxBitmap("{}/bitmaps/clock16.png".format(dbr.application_path)))

        self.menu_file.Append(wxID_NEW, help=_('Start a new project'))
        self.menu_file.Append(wxID_OPEN, help=_('Open a previously saved project'))
        self.menu_file.Append(wxID_SAVE, help=_('Save current project'))
        self.menu_file.Append(wxID_SAVEAS, help=_('Save current project with a new filename'))
        self.menu_file.AppendSeparator()
        self.menu_file.AppendItem(self.QuickBuild)
        self.menu_file.AppendSeparator()
        self.menu_file.Append(wxID_EXIT)

        wxEVT_MENU(self, wxID_NEW, self.OnNewProject)
        wxEVT_MENU(self, wxID_OPEN, self.OnOpenProject)

        # Debugging
        if dbr.DEBUG:
            wxEVT_MENU(self, wxID_SAVE, self.SaveProject)
        else:
            wxEVT_MENU(self, wxID_SAVE, self.OnSaveProjectDeprecated)

        wxEVT_MENU(self, wxID_SAVEAS, self.OnSaveProjectDeprecated)
        wxEVT_MENU(self, ID_QBUILD, self.OnQuickBuild)
        wxEVT_MENU(self, wxID_EXIT, self.OnQuit)
        wxEVT_CLOSE(self, self.OnQuit) #custom close event shows a dialog box to confirm quit

        # ----- Page Menu
        self.menu_page = wxMenu()

        self.p_info = wxMenuItem(self.menu_page, ID_INFO, _('Information'), _('Go to Information section'),
                kind=wxITEM_RADIO)
        self.p_ctrl = wxMenuItem(self.menu_page, ID_CTRL, _('Control'), _('Go to Control section'),
                kind=wxITEM_RADIO)
        self.p_deps = wxMenuItem(self.menu_page, ID_DEPS, _('Dependencies'), _('Go to Dependencies section'), kind=wxITEM_RADIO)
        self.p_files = wxMenuItem(self.menu_page, ID_FILES, _('Files'), _('Go to Files section'), kind=wxITEM_RADIO)
        self.p_scripts = wxMenuItem(self.menu_page, ID_SCRIPTS, _('Scripts'), _('Go to Scripts section'), kind=wxITEM_RADIO)
        self.p_clog = wxMenuItem(self.menu_page, ID_CLOG, _('Changelog'), _('Go to Changelog section'), kind=wxITEM_RADIO)
        self.p_cpright = wxMenuItem(self.menu_page, ID_CPRIGHT, _('Copyright'), _('Go to Copyright section'), kind=wxITEM_RADIO)
        self.p_menu = wxMenuItem(self.menu_page, ID_MENU, _('Menu Launcher'), _('Go to Menu Launcher section'), kind=wxITEM_RADIO)
        self.p_build = wxMenuItem(self.menu_page, ID_BUILD, _('Build'), _('Go to Build section'), kind=wxITEM_RADIO)

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
        self.menu_opt = wxMenu()

        # Dialogs options
        self.cust_dias = wxMenuItem(self.menu_opt, ID_Dialogs, _('Use Custom Dialogs'),
            _('Use System or Custom Save/Open Dialogs'), kind=wxITEM_CHECK)

        self.menu_opt.AppendItem(self.cust_dias)

        # ----- Help Menu
        self.menu_help = wxMenu()

        # ----- Version update
        self.version_check = wxMenuItem(self.menu_help, ID_UPDATE, _('Check for Update'))
        self.menu_help.AppendItem(self.version_check)
        self.menu_help.AppendSeparator()

        wxEVT_MENU(self, ID_UPDATE, self.OnCheckUpdate)

        # Menu with links to the Debian Policy Manual webpages
        self.Policy = wxMenu()

        globe = wxBitmap("{}/bitmaps/globe16.png".format(dbr.application_path))
        self.DPM = wxMenuItem(self.Policy, ID_DPM, _('Debian Policy Manual'), 'http://www.debian.org/doc/debian-policy')
        self.DPM.SetBitmap(globe)
        self.DPMCtrl = wxMenuItem(self.Policy, ID_DPMCtrl, _('Control Files'), 'http://www.debian.org/doc/debian-policy/ch-controlfields.html')
        self.DPMCtrl.SetBitmap(globe)
        self.DPMLog = wxMenuItem(self.Policy, ID_DPMLog, _('Changelog'), 'http://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog')
        self.DPMLog.SetBitmap(globe)
        self.UPM = wxMenuItem(self.Policy, ID_UPM, _('Ubuntu Policy Manual'), 'http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/')
        self.UPM.SetBitmap(globe)
        self.DebFrmSrc = wxMenuItem(self.Policy, 222, _('Building debs from Source'), 'http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source') # This is here only temporarily for reference
        self.DebFrmSrc.SetBitmap(globe)
        self.LintianTags = wxMenuItem(self.Policy, ID_Lintian, _('Lintian Tags Explanation'), 'http://lintian.debian.org/tags-all.html')
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
            wxEVT_MENU(self, id, self.OpenPolicyManual)


        self.Help = wxMenuItem(self.menu_help, wxID_HELP, _('Help'), _('Open a usage document'))
        self.About = wxMenuItem(self.menu_help, wxID_ABOUT, _('About'), _('About Debreate'))

        self.menu_help.AppendMenu(-1, _('Reference'), self.Policy)
        self.menu_help.AppendSeparator()
        self.menu_help.AppendItem(self.Help)
        self.menu_help.AppendItem(self.About)

        wxEVT_MENU(self, wxID_HELP, self.OnHelp)
        wxEVT_MENU(self, wxID_ABOUT, self.OnAbout)

        self.menubar = wxMenuBar()
        self.SetMenuBar(self.menubar)

        self.menubar.Insert(0, self.menu_file, _('File'))
        self.menubar.Insert(1, self.menu_page, _('Page'))
        self.menubar.Insert(2, self.menu_opt, _('Options'))
        self.menubar.Insert(3, self.menu_help, _('Help'))

        # FIXME: QuickBuild broken
        self.QuickBuild.SetText('Quick Build (Broken)')
        self.QuickBuild.Enable(False)

        # ***** END MENUBAR ***** #

        self.Wizard = dbr.Wizard(self) # Binary

        self.page_info = wiz_bin.PageGreeting(self.Wizard, ID_INFO)
        self.page_info.SetInfo()
        self.page_control = wiz_bin.PageControl(self.Wizard, ID_CTRL)
        self.page_depends = wiz_bin.PageDepends(self.Wizard, ID_DEPS)
        self.page_files = wiz_bin.PageFiles(self.Wizard, ID_FILES)
        self.page_scripts = wiz_bin.PageScripts(self.Wizard, ID_SCRIPTS)
        self.page_clog = wiz_bin.PageChangelog(self.Wizard, ID_CLOG)
        self.page_cpright = wiz_bin.PageCopyright(self.Wizard, ID_CPRIGHT)
        self.page_menu = wiz_bin.PageMenu(self.Wizard, ID_MENU)
        self.page_build = wiz_bin.PageBuild(self.Wizard, ID_BUILD)

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
            wxEVT_MENU(self, p.GetId(), self.GoToPage)

        # ----- Layout
        self.main_sizer = wxBoxSizer(wxVERTICAL)
        self.main_sizer.Add(self.Wizard, 1, wxEXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(self.main_sizer)
        self.Layout()


        # Saving
        # First item is name of saved file displayed in title
        # Second item is actual path to project file
        self.saved_project = wxEmptyString



    def OnMaximize(self, event):
        print "Maximized"


    ### ***** Check for New Version ***** ###
    def OnCheckUpdate(self, event):
        wxSafeYield()
        current = dbr.GetCurrentVersion()
        if isinstance (current, URLError) or isinstance (current, HTTPError):
            current = unicode(current)
            wxMessageDialog(self, current, _(u'Error'), wxOK|wxICON_ERROR).ShowModal()
        elif (current > VERSION):
            current = '{}.{}.{}'.format(current[0], current[1], current[2])
            l1 = _(u'Version %s is available!').decode('utf-8') % (current)
            l2 = _(u"Would you like to go to Debreate's website?").decode('utf-8')
            update = wxMessageDialog(self, u'{}\n\n{}'.format(l1, l2), _(u'Debreate'), wxYES_NO|wxICON_INFORMATION).ShowModal()
            if (update == wxID_YES):
                wxLaunchDefaultBrowser(HOMEPAGE)
        elif (current < VERSION):
            wxMessageDialog(self, _(u'This is a development version, no updates available'),
                    _(u'Debreate'), wxOK|wxICON_INFORMATION).ShowModal()
        else:
            wxMessageDialog(self, _(u'Debreate is up to date!'), _(u'Debreate'), wxOK|wxICON_INFORMATION).ShowModal()


    ### ***** Menu Handlers ***** ###

    def OnNewProject(self, event):
        dia = wxMessageDialog(self, _('You will lose any unsaved information\n\nContinue?'),
                _('Start New Project'), wxYES_NO|wxNO_DEFAULT)
        if dia.ShowModal() == wxID_YES:
            self.NewProject()
            #self.SetMode(None)

    def NewProject(self):
        for page in self.all_pages:
            page.ResetAllFields()
        self.SetTitle(self.default_title)

        # Reset the saved project field so we know that a project file doesn't exists
        self.saved_project = wxEmptyString

    def OnOpenProject(self, event):
        cont = False
        dbp = '|*.dbp'
        d = _('Debreate project files')
        if self.cust_dias.IsChecked():
            dia = dbr.OpenFile(self, _('Open Debreate Project'))
            dia.SetFilter('{}{}'.format(d, dbp))
            if dia.DisplayModal():
                cont = True
        else:
            dia = wxFileDialog(self, _('Open Debreate Project'), os.getcwd(), '', '{}{}'.format(d, dbp), wxFD_CHANGE_DIR)
            if dia.ShowModal() == wxID_OK:
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
    	def ProjectError():
    		wxMessageDialog(self, _('Not a valid Debreate project'), _('Error'),
    			style=wxOK|wxICON_ERROR).ShowModal()

    	if data == wxEmptyString:
    		ProjectError()
    		return

        lines = data.split('\n')
        app = lines[0].split('-')[0].split('[')[1]
        ver = lines[0].split('-')[1].split(']')[0]

        if app != 'DEBREATE':
            ProjectError()
            return

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

    ''' DEPRECATED
    # ----- File Menu
    def ConvertToRPM(self, event):
        # This app uses alien to convert debian binary/basic packages to red had format.
        # The acutal command is "fakeroot alien -rck [package_name].deb"
        # alien cannot convert packages that are in a path with spaces in it, and it will also fail
        # if the package's file extension is anything other than ".deb", e.g. ".DEB", ".DeB".
        app = debrpm.Dialog(self, -1, _("Deb to RPM"))
        app.ShowModal()
        app.Close()'''

    def OnQuit(self, event):
        """Show a dialog to confirm quit and write window settings to config file"""
        confirm = wxMessageDialog(self, _('You will lose any unsaved information'), _('Quit?'),
                                   wxOK|wxCANCEL|wxICON_QUESTION)
        if confirm.ShowModal() == wxID_OK: # Show a dialog to confirm quit
            confirm.Destroy()

            # Get window attributes and save to config file
            if self.IsMaximized():	# If window is maximized upon closing the program will set itself back to
                size = "800,650"		# an 800x650 window (ony when restored back down, the program will open
                maximize = 1        # maximized)
                pos = "0,0"
                center = 1
            else:
                size = "{},{}".format(self.GetSize()[0], self.GetSize()[1])
                maximize = 0
                pos = "{},{}".format(self.GetPosition()[0], self.GetPosition()[1])
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
position={}\n\
size={}\n\
maximize={}\n\
center={}\n\
dialogs={}\n\
workingdir={}".format(pos, size, maximize, center, dias, cwd))
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
        about = dbr.AboutDialog(self, -1, _('About'))

        about.SetGraphic("{}/bitmaps/debreate64.png".format(dbr.application_path))
        about.SetVersion(VERSION_STRING)
        about.SetAuthor('Jordan Irwin')
        about.SetDescription(_('A package builder for Debian based systems'))

        about.AddDeveloper("Jordan Irwin", "antumdeluge@gmail.com")
        about.AddPackager("Jordan Irwin", "antumdeluge@gmail.com")
        about.AddTranslator(_(u'Karim Oulad Chalha'), u'herr.linux88@gmail.com', 'ar_MA', )
        about.AddTranslator(_(u'Jordan Irwin'), u'antumdeluge@gmail.com', 'es')
        about.AddTranslator(_(u'Philippe Dalet'), u'philippe.dalet@ac-toulouse.fr', 'fr_FR')

        about.SetChangelog()

        about.SetLicense()

        about.ShowModal()
        about.Destroy()

    def OnHelp(self, event):
        # First tries to open pdf help file. If fails tries to open html help file. If fails opens debreate usage webpage
        wxYield()
        status = subprocess.call(['xdg-open', '{}/docs/usage.pdf'.format(dbr.application_path)])
        if status:
            wxYield()
            status = subprocess.call(['xdg-open', '{}/docs/usage'.format(dbr.application_path)])
        if status:
            wxYield()
            webbrowser.open('http://debreate.sourceforge.net/usage')

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
            if self.IsSaved() and title != self.default_title:
                self.SetTitle("{}*".format(title))

    # FIXME: New format unused. Currently still using OnSaveProjectDeprecated
    def SaveProject(self, event):
        if dbr.DEBUG:
            print('DEBUG: Saving in new project format')

        title = _('Save Debreate Project')
        suffix = dbr.PROJECT_FILENAME_SUFFIX

        # Set Displayed description & filename filter for dialog
        dbp = '|*.{}'.format(suffix)
        description = _('Debreate project files')
        ext_filter = '{} (.{}){}'.format(description, suffix, dbp)

        file_save = dbr.GetFileSaveDialog(self, title,
                ext_filter, suffix)
        if dbr.ShowDialog(self, file_save):
            self.saved_project = file_save.GetPath()

            if dbr.DEBUG:
                print('DEBUG: Saving file "{}"'.format(self.saved_project))
        else:
            if dbr.DEBUG:
                print('DEBUG: Cancelled')

    def OnSaveProjectDeprecated(self, event):
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
                    backup = '{}.backup'.format(path)
                    shutil.copy(path, backup)
                    overwrite = True

                savefile = open(path, 'w')
                # This try statement can be removed when unicode support is enabled
                try:
                    savefile.write("[DEBREATE-{}]\n{}".format(VERSION_STRING, "\n".join(data).encode('utf-8')))
                    savefile.close()
                    if overwrite:
                        os.remove(backup)
                except UnicodeEncodeError:
                    serr = _('Save failed')
                    uni = _('Unfortunately Debreate does not support unicode yet. Remove any non-ASCII characters from your project.')
                    UniErr = wxMessageDialog(self, '{}\n\n{}'.format(serr, uni), _('Unicode Error'), style=wxOK|wxICON_EXCLAMATION)
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
                dia = dbr.SaveFile(self, _('Save Debreate Project'), 'dbp')
                dia.SetFilter('{}{}'.format(d, dbp))
                if dia.DisplayModal():
                    cont = True
                    filename = dia.GetFilename()
                    if filename.split('.')[-1] == 'dbp':
                        filename = ".".join(filename.split(".")[:-1])
                    self.saved_project = "{}/{}.dbp".format(dia.GetPath(), filename)
            else:
                dia = wxFileDialog(self, _('Save Debreate Project'), os.getcwd(), '', '{}{}'.format(d, dbp),
                                        wxFD_SAVE|wxFD_CHANGE_DIR|wxFD_OVERWRITE_PROMPT)
                if dia.ShowModal() == wxID_OK:
                    cont = True
                    filename = dia.GetFilename()
                    if filename.split(".")[-1] == "dbp":
                        filename = ".".join(filename.split(".")[:-1])
                    self.saved_project = "{}/{}.dbp".format(os.path.split(dia.GetPath())[0], filename)

            if cont:
                SaveIt(self.saved_project)

        if id == wxID_SAVE:
            # Define what to do if save is pressed
            # If project already exists, don't show dialog
            if not self.IsSaved() or self.saved_project == wxEmptyString or not os.path.isfile(self.saved_project):
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
