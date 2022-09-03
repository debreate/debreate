## \page main.py Main Window Interface
#
#  Defines interface of the main window.

# MIT licensing
# See: docs/LICENSE.txt


import os, subprocess, webbrowser, wx
from urllib.error import HTTPError
from urllib.error import URLError

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
from globals.ident          import menuid
from globals.ident          import pgid
from globals.ident          import refid
from globals.mime           import GetFileMimeType
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
from wiz.pginit             import Page as PageInit
from wiz.wizard             import Wizard


default_title = GT("Debreate - Debian Package Builder")


## The main window interface
class MainWindow(wx.Frame):
    ## Constructor
    #
    #  \param pos
    #    <b><i>Integer tuple</i></b> or <b><i>wx.Point</i></b> instance indicating the screen position of the window
    #  \param size
    #    <b><i>Integer tuple</i></b> or <b><i>wx.Size</i></b> instance indicating the dimensions of the window
    def __init__(self, pos, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, default_title, pos, size)

        # Make sure that this frame is set as the top window
        if not wx.GetApp().GetTopWindow() == self:
            Logger.Debug(__name__, GT("Setting MainWindow instance as top window"))

            wx.GetApp().SetTopWindow(self)

        testing = "alpha" in GetTestList() or DebugEnabled()

        if DebugEnabled():
            self.SetTitle("{} ({})".format(default_title, GT("debugging")))

        self.SetMinSize(wx.Size(640, 400))

        # ----- Set Titlebar Icon
        self.SetIcon(Icon(LOGO))

        # *** Status Bar *** #
        StatusBar(self)

        # *** Menus *** #
        menubar = MenuBar(self)

        menu_file = wx.Menu()

        menubar.Append(menu_file, GT("File"), menuid.FILE)
        # This menu is filled from wiz.wizard.Wizard.SetPages
        menubar.Append(wx.Menu(), GT("Page"), menuid.PAGE)

        # *** File Menu *** #

        mitems_file = [
            (menuid.NEW, GT("New project"), GT("Start a new project"),),
            (menuid.OPEN, GT("Open"), GT("Open a previously saved project"),),
            (menuid.SAVE, GT("Save"), GT("Save current project"),),
            (menuid.SAVEAS, GT("Save as"), GT("Save current project with a new filename"),),
            None,
            (menuid.QBUILD, GT("Quick Build"), GT("Build a package from an existing build tree"), ICON_CLOCK,),
            None,
            (menuid.EXIT, GT("Quit"), GT("Exit Debreate"),),
            ]

        if testing:
            mitems_file.append((menuid.ALIEN, GT("Convert packages"), GT("Convert between package types")))

        # Adding all menus to menu bar

        mitems = (
            mitems_file,
            )

        for menu_list in mitems:
            for mitem in menu_list:
                if not mitem:
                    menu_file.AppendSeparator()

                else:
                    itm = wx.MenuItem(menu_file, mitem[0], mitem[1], mitem[2])
                    if len(mitem) > 3:
                        itm.SetBitmap(mitem[3])

                    menu_file.AppendItem(itm)

        # *** Action Menu *** #
        menu_action = wx.Menu()

        mitm_build = wx.MenuItem(menu_action, menuid.BUILD, GT("Build"),
                GT("Start building .deb package"))

        menu_action.AppendItem(mitm_build)

        # ----- Options Menu
        menu_opt = wx.Menu()

        # Show/Hide tooltips
        self.opt_tooltips = wx.MenuItem(menu_opt, menuid.TOOLTIPS, GT("Show tooltips"),
                GT("Show or hide tooltips"), kind=wx.ITEM_CHECK)

        # A bug with wx 2.8 does not allow tooltips to be toggled off
        if wx.MAJOR_VERSION > 2:
            menu_opt.AppendItem(self.opt_tooltips)

        if menu_opt.FindItemById(menuid.TOOLTIPS):
            show_tooltips = ReadConfig("tooltips")
            if show_tooltips != ConfCode.KEY_NO_EXIST:
                self.opt_tooltips.Check(show_tooltips)

            else:
                self.opt_tooltips.Check(GetDefaultConfigValue("tooltips"))

            self.OnToggleToolTips()

        # Project compression options
        self.menu_compress = wx.Menu()

        opt_z_none = wx.MenuItem(self.menu_compress, ident.ZIP_NONE,
                GT("Uncompressed"), GT("Use uncompressed tarball for project save format"),
                kind=wx.ITEM_RADIO)
        opt_z_gz = wx.MenuItem(self.menu_compress, ident.ZIP_GZ,
                GT("Gzip"), GT("Use compressed Gzip tarball for project save format"),
                kind=wx.ITEM_RADIO)
        opt_z_bz2 = wx.MenuItem(self.menu_compress, ident.ZIP_BZ2,
                GT("Bzip2"), GT("Use compressed Bzip2 tarball for project save format"),
                kind=wx.ITEM_RADIO)
        opt_z_zip = wx.MenuItem(self.menu_compress, ident.ZIP_ZIP,
                GT("Zip"), GT("Use compressed zip file for project save format"),
                kind=wx.ITEM_RADIO)

        opts_compress = [
            opt_z_none,
            opt_z_gz,
            opt_z_bz2,
            opt_z_zip,
        ]

        if GetExecutable("tar") != None:
            opt_z_xz = wx.MenuItem(self.menu_compress, ident.ZIP_XZ,
                    GT("XZ"), GT("Use compressed xz tarball for project save format"),
                    kind=wx.ITEM_RADIO)
            opts_compress.insert(3, opt_z_xz)

        for OPT in opts_compress:
            self.menu_compress.AppendItem(OPT)
            wx.EVT_MENU(self.menu_compress, OPT.GetId(), self.OnSetCompression)

        # Default compression
        self.menu_compress.Check(ident.ZIP_BZ2, True)

        menu_opt.AppendSubMenu(self.menu_compress, GT("Project Compression"),
                GT("Set the compression type for project save output"))

        # *** Option Menu: open logs directory *** #

        if GetExecutable("xdg-open"):
            mitm_logs_open = wx.MenuItem(menu_opt, menuid.OPENLOGS, GT("Open logs directory"))
            menu_opt.AppendItem(mitm_logs_open)

            wx.EVT_MENU(menu_opt, menuid.OPENLOGS, self.OnLogDirOpen)

        # *** OS distribution names cache *** #

        opt_distname_cache = wx.MenuItem(menu_opt, menuid.DIST, GT("Update dist names cache"),
                GT("Creates/Updates list of distribution names for changelog page"))
        menu_opt.AppendItem(opt_distname_cache)

        # ----- Help Menu
        menu_help = wx.Menu()

        # ----- Version update
        mitm_update = wx.MenuItem(menu_help, menuid.UPDATE, GT("Check for update"),
                GT("Check if a new version is available for download"))
        mitm_update.SetBitmap(ICON_LOGO)

        menu_help.AppendItem(mitm_update)
        menu_help.AppendSeparator()

        # Menu with links to the Debian Policy Manual webpages
        self.menu_policy = wx.Menu()

        policy_links = (
            (refid.DPM, GT("Debian Policy Manual"),
                    "https://www.debian.org/doc/debian-policy",),
            (refid.DPMCtrl, GT("Control files"),
                    "https://www.debian.org/doc/debian-policy/ch-controlfields.html",),
            (refid.DPMLog, GT("Changelog"),
                    "https://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog",),
            (refid.UPM, GT("Ubuntu Policy Manual"),
                    "http://people.canonical.com/~cjwatson/ubuntu-policy/policy.html/",),
            (refid.LINT_TAGS, GT("Lintian Tags Explanation"),
                    "https://lintian.debian.org/tags-all.html",),
            (refid.LINT_OVERRIDE, GT("Overriding Lintian Tags"),
                    "https://lintian.debian.org/manual/section-2.4.html",),
            (refid.LAUNCHERS, GT("Launchers / Desktop entries"),
                    "https://www.freedesktop.org/wiki/Specifications/desktop-entry-spec/",),
            # Unofficial links
            None,
            (refid.DEBSRC, GT("Building debs from Source"),
                    "http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source",), # This is here only temporarily for reference
            (refid.MAN, GT("Writing manual pages"),
                    "https://liw.fi/manpages/",),
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

        mitm_help = wx.MenuItem(menu_help, wx.ID_HELP, GT("Help"), GT("Open a usage document"))
        mitm_about = wx.MenuItem(menu_help, wx.ID_ABOUT, GT("About"), GT("About Debreate"))

        menu_help.AppendMenu(-1, GT("Reference"), self.menu_policy)
        menu_help.AppendSeparator()
        menu_help.AppendItem(mitm_help)
        menu_help.AppendItem(mitm_about)

        menubar.Append(menu_action, GT("Action"), menuid.ACTION)

        if menu_opt.GetMenuItemCount():
            menubar.Append(menu_opt, GT("Options"), menuid.OPTIONS)

        menubar.Append(menu_help, GT("Help"), menuid.HELP)

        self.Wizard = Wizard(self)

        # Menu for debugging & running tests
        if DebugEnabled():
            self.menu_debug = wx.Menu()

            menubar.Append(self.menu_debug, GT("Debug"), menuid.DEBUG)

            self.menu_debug.AppendItem(wx.MenuItem(self.menu_debug, menuid.LOG, GT("Show log"),
                    GT("Toggle debug log window"), kind=wx.ITEM_CHECK))

            if "log-window" in parsed_args_s:
                self.menu_debug.Check(menuid.LOG, True)

            self.log_window = None

            # Window colors
            self.menu_debug.AppendItem(
                wx.MenuItem(self.menu_debug, menuid.THEME, GT("Toggle window colors")))

            wx.EVT_MENU(self, menuid.THEME, self.OnToggleTheme)

        # *** Current Project Status *** #

        self.LoadedProject = None
        self.ProjectDirty = False
        self.dirty_mark = " *"

        menu_file.Enable(wx.ID_SAVE, self.ProjectDirty)

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

        default_compression = GetDefaultConfigValue("compression")

        Logger.Debug(__name__,
                GT("Setting compression to default value: {}".format(default_compression)))

        return default_compression


    ## TODO: Doxygen
    def GetCompressionId(self):
        for Z in self.menu_compress.GetMenuItems():
            Z_ID = Z.GetId()
            if self.menu_compress.IsChecked(Z_ID):
                return Z_ID

        Logger.Warn(__name__, GT("Did not find compatible compression ID, using default"))

        return DEFAULT_COMPRESSION_ID


    ## Retrieves menu by ID
    def GetMenu(self, menuId):
        return self.GetMenuBar().GetMenuById(menuId)


    ## Retrieves the Wizard instance
    #
    #  \return
    #        wiz.wizard.Wizard
    def GetWizard(self):
        return self.Wizard


    ## Sets the pages in the wiz.wizard.Wizard instance
    def InitWizard(self):
        pg_init = PageInit(self.Wizard)
        pg_init.SetInfo()

        self.Wizard.AddPage(pg_init)
        self.Wizard.SetModeBin(0)


    ## Opens a dialog box with information about the program
    def OnAbout(self, event=None):
        about = AboutDialog(self)

        about.SetGraphic(LOGO)
        about.SetVersion(VERSION_string)
        about.SetDescription(GT("A package builder for Debian based systems"))
        about.SetAuthor(AUTHOR_name)

        about.SetWebsites((
            (GT("Homepage"), APP_homepage),
            (GT("GitHub Project"), APP_project_gh),
            (GT("Sourceforge Project"), APP_project_sf),
        ))

        about.AddJobs(
            AUTHOR_name,
            (
                GT("Head Developer"),
                GT("Packager"),
                "{} (es, it)".format(GT("Translation")),
            ),
            AUTHOR_email
        )

        about.AddJobs(
            "Hugo Posnic",
            (
                GT("Code Contributor"),
                GT("Website Designer & Author"),
            ),
            "hugo.posnic@gmail.com"
        )

        about.AddJob("Lander Usategui San Juan", GT("General Contributor"), "lander@erlerobotics.com")

        about.AddTranslator("Karim Oulad Chalha", "herr.linux88@gmail.com", "ar", )
        about.AddTranslator("Philippe Dalet", "philippe.dalet@ac-toulouse.fr", "fr")
        about.AddTranslator("Zhmurkov Sergey", "zhmsv@yandex.ru", "ru")

        about.AddJob("Benji Park", GT("Button Base Image Designer"))

        about.SetChangelog()

        about.SetLicense()

        about.ShowModal()
        about.Destroy()


    ## Checks for new release availability
    def OnCheckUpdate(self, event=None):
        update_test = "update-fail" in GetTestList()

        if UsingDevelopmentVersion() and not update_test:
            DetailedMessageDialog(self, GT("Update"),
                    text=GT("Update checking is disabled in development versions")).ShowModal()
            return

        wx.SafeYield()

        if update_test:
            # Set a bad url to force error
            current = GetCurrentVersion("http://dummyurl.blah/")

        else:
            current = GetCurrentVersion()

        Logger.Debug(__name__, GT("URL request result: {}").format(current))

        error_remote = GT("An error occurred attempting to contact remote website")

        if isinstance(current, (URLError, HTTPError)):
            current = GS(current)
            ShowErrorDialog(error_remote, current)

        elif isinstance(current, tuple) and current > VERSION_tuple:
            current = "{}.{}.{}".format(current[0], current[1], current[2])
            l1 = GT("Version {} is available!").format(current)
            l2 = GT("Would you like to go to Debreate's website?")
            if ConfirmationDialog(self, GT("Update"), "{}\n\n{}".format(l1, l2)).Confirmed():
                wx.LaunchDefaultBrowser(APP_homepage)

        elif isinstance(current, str):
            ShowErrorDialog(error_remote, current)

        else:
            DetailedMessageDialog(self, GT("Debreate"), text=GT("Debreate is up to date!")).ShowModal()


    ## Action to take when 'Help' is selected from the help menu
    #
    #  Opens a help dialog if using 'alpha' test. Otherwise, opens
    #  PDF usage document. If openening usage document fails, attempts
    #  to open web browser in remote usage page.
    #  TODO: Use dialog as main method
    def OnHelp(self, event=None):
        if "alpha" in GetTestList():
            HelpDialog(self).ShowModal()

        else:
            # First tries to open pdf help file. If fails tries to open html help file. If fails opens debreate usage webpage
            wx.Yield()
            status = subprocess.call(["xdg-open", "{}/docs/usage.pdf".format(PATH_app)])
            if status:
                wx.Yield()
                status = subprocess.call(["xdg-open", "{}/docs/usage".format(PATH_app)])

            if status:
                wx.Yield()
                webbrowser.open("http://debreate.sourceforge.net/usage")


    ## Opens the logs directory in the system's default file manager
    def OnLogDirOpen(self, event=None):
        Logger.Debug(__name__, GT("Opening log directory ..."))

        subprocess.check_output([GetExecutable("xdg-open"), "{}/logs".format(PATH_local)], stderr=subprocess.STDOUT)


    ## Changes wizard page from menu
    def OnMenuChangePage(self, event=None):
        page_id = None

        if event:
            page_id = event.GetId()

            Logger.Debug(__name__, GT("Page ID from menu event: {}").format(page_id))

        else:
            for M in self.GetMenu(menuid.PAGE).GetMenuItems():
                if M.IsChecked():
                    page_id = M.GetId()

                    Logger.Debug(__name__, GT("Page ID from menu item: {}").format(page_id))

                    break

        if page_id == None:
            Logger.Error(__name__, GT("Could not get page ID"))

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
            if not ConfirmationDialog(self, GT("Quit?"),
                    text=GT("You will lose any unsaved information")).Confirmed():

                return

        maximized = self.IsMaximized()

        # Get window attributes and save to config file

        # Save default window settings if maximized
        # FIXME: Better solution?
        if maximized:
            WriteConfig("size", GetDefaultConfigValue("size"))
            WriteConfig("position", GetDefaultConfigValue("position"))
            WriteConfig("center", GetDefaultConfigValue("center"))
            WriteConfig("maximize", True)

        else:
            WriteConfig("position", self.GetPositionTuple())
            WriteConfig("size", self.GetSizeTuple())
            WriteConfig("center", False)
            WriteConfig("maximize", False)

        config_wdir = ReadConfig("workingdir")
        current_wdir = os.getcwd()

        # Workaround for issues with some dialogs not writing to config
        if config_wdir != current_wdir:
            WriteConfig("workingdir", current_wdir)

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
            Logger.Debug(__name__, "MainWindow.OnProjectChanged: {}".format(changed), newline=True)
            print("  Object: {}".format(event.GetEventObject()))

        return changed


    ## Clears current project & restores fields to defaults
    #
    #  \return
    #    \b \e True if project state is reset to default
    def OnProjectNew(self, event=None):
        Logger.Debug(__name__, GT("Project loaded before OnProjectNew: {}").format(self.ProjectIsLoaded()))

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
        Logger.Debug(__name__, GT("Project loaded; Saving without showing dialog"))

        # Saving over currently loaded project
        self.ProjectSave(self.LoadedProject)


    ## TODO: Doxygen
    def OnProjectSaveAs(self, event=None):
        self.ProjectSaveAs()


    ## Writes compression value to config in real time
    def OnSetCompression(self, event=None):
        if event:
            event_id = event.GetId()
            Logger.Debug(__name__, GT("OnSetCompression; Event ID: {}").format(event_id))
            Logger.Debug(__name__, GT("OnSetCompression; Compression from event ID: {}").format(compression_formats[event_id]))

            if event_id in compression_formats:
                WriteConfig("compression", compression_formats[event_id])
                return

        Logger.Warn(__name__,
                GT("OnSetCompression; Could not write to config, ID not found in compression formats: {}").format(event_id))


    ## TODO: Doxygen
    def OnToggleLogWindow(self, event=None):
        Logger.Debug(__name__, GT("Toggling log window"))

        if event != None:
            self.ShowLogWindow(self.menu_debug.IsChecked(menuid.DEBUG))
            return

        self.menu_debug.Check(menuid.DEBUG, self.log_window.IsShown())


    ## TODO: Doxygen
    def OnToggleTheme(self, event=None):
        self.ToggleTheme(self)


    ## Shows or hides tooltips
    def OnToggleToolTips(self, event=None):
        enabled = self.opt_tooltips.IsChecked()
        wx.ToolTip.Enable(enabled)

        WriteConfig("tooltips", enabled)


    ## Opens a dialog for creating/updating list of distribution names cache file
    def OnUpdateDistNamesCache(self, event=None):
        DistNamesCacheDialog().ShowModal()


    ## Updates the page menu to reflect current page
    def OnWizardBtnPage(self, event=None):
        ID = self.Wizard.GetCurrentPageId()
        Logger.Debug(__name__, GT("Event: EVT_CHANGE_PAGE, Page ID: {}").format(ID))

        menu_page = self.GetMenu(menuid.PAGE)
        if not menu_page.IsChecked(ID):
            menu_page.Check(ID, True)


    ## Opens web links from the help menu
    def OpenPolicyManual(self, event=None):
        if isinstance(event, wx.CommandEvent):
            event_id = event.GetId()

        elif isinstance(event, int):
            event_id = event

        else:
            Logger.Error(__name__,
                    "Cannot open policy manual link with object type {}".format(type(event)))

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

        msg_l1 = GT("{} is unsaved, any changes will be lost").format(self.LoadedProject)
        confirmed = ConfirmSaveDialog(self, GT("Unsaved Changes"),
                text=GT("{}\n\n{}".format(msg_l1, GT("Continue?")))).ShowModal()

        if confirmed == wx.ID_SAVE:
            if self.LoadedProject:
                Logger.Debug(__name__, "Saving modified project ...")

                self.ProjectSave(self.LoadedProject)

            else:
                Logger.Debug(__name__, "Saving new project ...")

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
    #    \b \e str : Path to project file
    def ProjectOpen(self, project_file=None):
        Logger.Debug(__name__, "Opening project: {}".format(project_file))

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

            open_dialog = GetFileOpenDialog(self, GT("Open Debreate Project"), wildcards)
            if not ShowDialog(open_dialog):
                return dbrerrno.ECNCLD

            # Get the path and set the saved project
            project_file = open_dialog.GetPath()

        # Failsafe check that file exists
        if not os.path.isfile(project_file):
            err_l1 = GT("Cannot open project:")
            err_details = GT("File does not exist")

            ShowErrorDialog("{} {}".format(err_l1, project_file), err_details)

            return dbrerrno.ENOENT

        # Check for unsaved changes & reset project to defaults
        if not self.ProjectClose():
            return dbrerrno.ECNCLD

        mime_type = GetFileMimeType(project_file)

        Logger.Debug(__name__, GT("Project mime type: {}").format(mime_type))

        opened = None
        if mime_type == "text/plain":
            p_text = ReadFile(project_file)

            filename = os.path.split(project_file)[1]

            # Legacy projects should return None since we can't save in that format
            opened = self.ProjectOpenLegacy(p_text, filename)

        else:
            opened = self.ProjectOpenArchive(project_file, mime_type)

        Logger.Debug(__name__, GT("Project loaded before OnProjectOpen: {}").format(self.ProjectIsLoaded()))

        if opened == dbrerrno.SUCCESS:
            self.LoadedProject = project_file

            # Set project 'unmodified' for newly opened project
            self.ProjectSetDirty(False)

        Logger.Debug(__name__, GT("Project loaded after OnOpenPreject: {}").format(self.ProjectIsLoaded()))

        if DebugEnabled() and self.ProjectIsLoaded():
            Logger.Debug(__name__, GT("Loaded project: {}").format(self.LoadedProject))

        return opened


    ## TODO: Doxygen
    def ProjectOpenArchive(self, filename, file_type):
        Logger.Debug(__name__, GT("Compressed project archive detected"))

        if file_type not in compression_mimetypes:
            Logger.Error(__name__, GT("Cannot open project with compression mime type \"{}\"".format(file_type)))

            return dbrerrno.EBADFT

        compression_id = compression_mimetypes[file_type]

        z_format = compression_formats[compression_id]

        if z_format in ("tar", "zip"):
            z_format = "r"

        else:
            z_format = "r:{}".format(z_format)

        Logger.Debug(__name__, GT("Opening compressed project with \"{}\" format").format(z_format))

        stage = CreateStage()

        p_archive = CompressionHandler(compression_id)
        ret_code = p_archive.Uncompress(filename, stage)

        if isinstance(ret_code, tuple) and ret_code[0]:
            ShowErrorDialog("{}: {}".format(GT("Project load error"), ret_code[1]),
                    ret_code[0], parent=self)

            return dbrerrno.EBADFT

        self.Wizard.ImportPagesInfo(stage)
        RemoveStage(stage)

        # Mark project as loaded
        return dbrerrno.SUCCESS


    ## TODO: Doxygen
    def ProjectOpenLegacy(self, data, filename):
        Logger.Debug(__name__, GT("Legacy project format (text) detected"))

        def ProjectError():
            wx.MessageDialog(self, GT("Not a valid Debreate project"), GT("Error"),
                      style=wx.OK|wx.ICON_ERROR).ShowModal()

        if data == wx.EmptyString:
            ProjectError()
            return dbrerrno.EBADFT

        lines = data.split("\n")
        app = lines[0].split("-")[0].split("[")[1]

        if app != "DEBREATE":
            ProjectError()
            return dbrerrno.EBADFT

        # *** Get Control Data *** #
        control_data = data.split("<<CTRL>>\n")[1].split("\n<</CTRL>>")[0]
        depends_data = self.Wizard.GetPage(pgid.CONTROL).Set(control_data)
        self.Wizard.GetPage(pgid.DEPENDS).Set(depends_data)

        # *** Get Files Data *** #
        files_data = data.split("<<FILES>>\n")[1].split("\n<</FILES>>")[0]
        self.Wizard.GetPage(pgid.FILES).Set(files_data)

        # *** Get Scripts Data *** #
        scripts_data = data.split("<<SCRIPTS>>\n")[1].split("\n<</SCRIPTS>>")[0]
        self.Wizard.GetPage(pgid.SCRIPTS).Set(scripts_data)

        # *** Get Changelog Data *** #
        clog_data = data.split("<<CHANGELOG>>\n")[1].split("\n<</CHANGELOG>>")[0]
        self.Wizard.GetPage(pgid.CHANGELOG).Set(clog_data)

        # *** Get Copyright Data *** #
        try:
            cpright_data = data.split("<<COPYRIGHT>>\n")[1].split("\n<</COPYRIGHT")[0]
            self.Wizard.GetPage(pgid.COPYRIGHT).Set(cpright_data)

        except IndexError:
            pass

        # *** Get Menu Data *** #
        m_data = data.split("<<MENU>>\n")[1].split("\n<</MENU>>")[0]
        self.Wizard.GetPage(pgid.LAUNCHERS).Set(m_data)

        # Get Build Data
        build_data = data.split("<<BUILD>>\n")[1].split("\n<</BUILD")[0]
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
        Logger.Debug(__name__, GT("Saving in new project format"))
        Logger.Debug(__name__, GT("Saving to file {}").format(target_path))

        stage = CreateStage()

        if not os.path.exists(stage) or stage == dbrerrno.EACCES:
            ShowErrorDialog("{}: {}".format(GT("Could not create staging directory"), stage),
                    parent=self)

            return dbrerrno.EACCES

        Logger.Debug(__name__, GT("Temp dir created: {}").format(stage))

        working_path = os.path.dirname(target_path)
        output_filename = os.path.basename(target_path)

        Logger.Debug(
            __name__,
            "Save project\n\tWorking path: {}\n\tFilename: {}\n\tTemp directory: {}".format(working_path,
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
                GT("Compressing \"{}\" with format: {} ({})").format
                    (
                        target_path,
                        p_archive.GetCompressionFormat(),
                        p_archive.GetCompressionMimetype()
                    )
        )

        if os.path.isfile(target_path) or target_path == self.LoadedProject:
            Logger.Debug(__name__, GT("Overwriting old project file: {}").format(target_path))

        p_archive.Compress(stage, "{}".format(target_path))

        # FIXME: Should check file timestamp
        if os.path.isfile(target_path):
            Logger.Debug(__name__, GT("Project saved: {}").format(target_path))

            # Cleanup
            RemoveStage(stage)
            self.ProjectSetDirty(False)

            return dbrerrno.SUCCESS

        ShowErrorDialog("{}: {}".format(GT("Project save failed"), target_path), parent=self)

        return dbrerrno.EUNKNOWN


    ## Opens a dialog for saving a new project
    def ProjectSaveAs(self):
        wildcards = (
            "{} (.{})".format(GT("Debreate project files"), PROJECT_ext),
            "*.{}".format(PROJECT_ext),
        )

        save_dialog = GetFileSaveDialog(self, GT("Save Debreate Project"), wildcards,
                PROJECT_ext)

        if ShowDialog(save_dialog):
            project_path = save_dialog.GetPath()
            project_filename = save_dialog.GetFilename()

            Logger.Debug(__name__, GT("Project save path: {}").format(project_path))
            Logger.Debug(__name__, GT("Project save filename: {}").format(project_filename))

            saved = self.ProjectSave(project_path)
            if saved == dbrerrno.SUCCESS:
                self.ProjectSetDirty(False)

            return saved

        Logger.Debug(__name__, GT("Not saving project"))

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
            self.GetMenu(menuid.FILE).Enable(wx.ID_SAVE, self.ProjectDirty)

            title = self.GetTitle()

            if self.ProjectDirty:
                self.SetTitle("{}{}".format(title, self.dirty_mark))

            else:
                self.SetTitle(title[:-len(self.dirty_mark)])

            changed = True

        return changed


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
                        GT("Project compression set to \"{}\"".format(compression_formats[Z_ID])))

                return

        Logger.Debug(__name__,
                GT("Urecognized compression ID: {}".format(compression_id)))


    ## TODO: Doxygen
    def SetLogWindow(self, window):
        self.log_window = window

        wx.EVT_MENU(self, menuid.LOG, self.log_window.OnToggleWindow)


    ## TODO: Doxygen
    def ShowLogWindow(self, show=True):
        Logger.Debug(__name__, GT("Show log window: {}").format(show))

        self.log_window.Show(show)

        if self.menu_debug.IsChecked(menuid.DEBUG) != show:
            self.menu_debug.Check(menuid.DEBUG, show)


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
