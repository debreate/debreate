## \page main.py Main Window Interface
#
#  Defines interface of the main window.

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, subprocess, urllib, webbrowser, wx.html
from urllib.error import HTTPError
from urllib.error import URLError

import util

from dbr.config           import GetDefaultConfigValue
from dbr.config           import WriteConfig
from dbr.event            import EVT_CHANGE_PAGE
from dbr.event            import EVT_TIMER_STOP
from dbr.functions        import GetCurrentVersion
from dbr.functions        import UsingDevelopmentVersion
from dbr.help             import HelpDialog
from dbr.icon             import Icon
from dbr.language         import GT
from dbr.timer            import DebreateTimer
from globals              import paths
from globals.application  import APP_homepage
from globals.application  import APP_project_gh
from globals.application  import APP_project_gl
from globals.application  import APP_project_sf
from globals.application  import AUTHOR_email
from globals.application  import AUTHOR_name
from globals.application  import VERSION_string
from globals.application  import VERSION_tuple
from globals.bitmaps      import LOGO
from globals.execute      import GetExecutable
from globals.ident        import menuid
from globals.ident        import pgid
from globals.moduleaccess import ModuleAccessCtrl
from globals.project      import PROJECT_ext
from globals.project      import PROJECT_txt
from globals.strings      import GS
from globals.threads      import Thread
from libdbr.fileio        import readFile
from libdbr.fileio        import writeFile
from startup.tests        import GetTestList
from ui.about             import AboutDialog
from ui.dialog            import ConfirmationDialog
from ui.dialog            import DetailedMessageDialog
from ui.dialog            import ShowErrorDialog
from ui.distcache         import DistNamesCacheDialog
from ui.layout            import BoxSizer
from ui.menu              import createMenuBar
from ui.progress          import ProgressDialog
from ui.quickbuild        import QuickBuild
from ui.statusbar         import StatusBar
from wiz.helper           import GetPage
from wiz.pginit           import Page as PageInit
from wiz.wizard           import Wizard


logger = util.getLogger()
default_title = GT("Debreate - Debian Package Builder")


## The main window interface
class MainWindow(wx.Frame, ModuleAccessCtrl):
  ## Constructor
  #
  #  \param pos
  #  <b><i>Integer tuple</i></b> or <b><i>wx.Point</i></b> instance indicating the screen position of the window
  #  \param size
  #  <b><i>Integer tuple</i></b> or <b><i>wx.Size</i></b> instance indicating the dimensions of the window
  def __init__(self, pos, size):
    wx.Frame.__init__(self, None, wx.ID_ANY, default_title, pos, size)
    ModuleAccessCtrl.__init__(self, __name__)

    self.timer = DebreateTimer(self)
    # placeholder for progress dialog
    self.progress = None

    self.Bind(wx.EVT_TIMER, self.__onTimerEvent)
    self.Bind(EVT_TIMER_STOP, self.__onTimerStop)

    # Make sure that this frame is set as the top window
    if not wx.GetApp().GetTopWindow() == self:
      logger.debug(GT("Setting MainWindow instance as top window"))

      wx.GetApp().SetTopWindow(self)

    if logger.debugging():
      self.SetTitle("{} ({})".format(default_title, GT("debugging")))

    self.SetMinSize(wx.Size(640, 400))

    # ----- Set Titlebar Icon
    self.SetIcon(Icon(LOGO))

    # *** Status Bar *** #
    StatusBar(self)

    # *** Menus *** #
    createMenuBar(self)

    self.Wizard = Wizard(self)

    # *** Current Project Status *** #

    self.LoadedProject = None
    self.ProjectDirty = False

    # *** Event Handling *** #

    self.Bind(wx.EVT_MENU, self.OnProjectNew, id=menuid.NEW)
    self.Bind(wx.EVT_MENU, self.OnProjectOpen, id=menuid.OPEN)
    self.Bind(wx.EVT_MENU, self.OnProjectSave, id=menuid.SAVE)
    self.Bind(wx.EVT_MENU, self.OnProjectSave, id=menuid.SAVEAS)
    self.Bind(wx.EVT_MENU, self.OnQuickBuild, id=menuid.QBUILD)
    self.Bind(wx.EVT_MENU, self.OnQuit, id=menuid.EXIT)

    self.Bind(wx.EVT_MENU, self.OnToggleToolTips, id=menuid.TOOLTIPS)
    self.Bind(wx.EVT_MENU, self.OnUpdateDistNamesCache, id=menuid.DIST)

    self.Bind(wx.EVT_MENU, self.OnCheckUpdate, id=menuid.UPDATE)
    self.Bind(wx.EVT_MENU, self.OnHelp, id=menuid.HELP)
    self.Bind(wx.EVT_MENU, self.OnAbout, id=menuid.ABOUT)

    self.Bind(EVT_CHANGE_PAGE, self.OnWizardBtnPage)

    # Custom close event shows a dialog box to confirm quit
    self.Bind(wx.EVT_CLOSE, self.OnQuit)

    # *** Layout *** #

    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.Add(self.Wizard, 1, wx.EXPAND)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()


  ## Retrieves menu by ID
  def GetMenu(self, menuId):
    return self.GetMenuBar().GetMenuById(menuId)


  ## Retrieves the Wizard instance
  #
  #  \return
  #  	wiz.wizard.Wizard
  def GetWizard(self):
    return self.Wizard


  ## Sets the pages in the wiz.wizard.Wizard instance
  def InitWizard(self):
    self.Wizard.AddPage(PageInit(self.Wizard))
    self.Wizard.SetModeBin(0)


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
    if title[-1] == "*":
      return False

    else:
      return True


  ## Opens a dialog box with information about the program
  def OnAbout(self, event=None): #@UnusedVariable
    about = AboutDialog(self)

    about.SetGraphic(LOGO)
    about.SetVersion(VERSION_string)
    about.SetDescription(GT("A package builder for Debian based systems"))
    about.SetAuthor(AUTHOR_name)

    about.SetWebsites((
      (GT("Homepage"), APP_homepage),
      (GT("GitHub Project"), APP_project_gh),
      (GT("GitLab Project"), APP_project_gl),
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
  def OnCheckUpdate(self, event=None): #@UnusedVariable
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

    logger.debug(GT("URL request result: {}").format(current))

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


  def __cacheManualFiles(self, args):
    url_manual = args[0]
    manual_cache = args[1]
    manual_index = args[2]
    main_dir = os.getcwd()
    os.chdir(manual_cache)

    try:
      subprocess.Popen(["wget", "-rkp", "-nd", "-np", "-H", "-D",
          "debreate.wordpress.com,antumdeluge.github.io", url_manual]).communicate()
      # FIXME: use Python commands
      subprocess.Popen(["sed", "-i", "-e", "s|<a.*>||g", "-e", "s|</a>||g", manual_index]).communicate()
    except:
      # FIXME: show error message
      pass

    os.chdir(main_dir)
    self.timer.Stop()

  ## Calls Pulse method on progress dialog when timer event occurs
  def __onTimerEvent(self, event=None):
    if self.progress:
      self.progress.Pulse()

  def __onTimerStop(self, event=None):
    if self.progress:
      self.progress.EndModal(0)
      self.progress = None

    if not self.IsEnabled():
      self.Enable()

    return not self.progress


  ## Action to take when 'Help' is selected from the help menu
  #
  #  Opens a help dialog if using 'alpha' test. Otherwise, opens
  #  PDF usage document. If opening usage document fails, attempts
  #  to open web browser in remote usage page.
  #  TODO: Use dialog as main method
  def OnHelp(self, event=None): #@UnusedVariable
    if "alpha" in GetTestList():
      HelpDialog(self).ShowModal()
    else:
      # FIXME: files should be re-cached when Debreate upgraded to new version
      # TODO: trim unneeded text
      cached = False
      manual_cache = os.path.join(paths.getCacheDir(), "manual")
      manual_index = os.path.join(manual_cache, "index.html")
      if not os.path.isdir(manual_cache):
        os.makedirs(manual_cache)
      elif os.path.isfile(manual_index):
        cached = True
      url_manual = "https://debreate.wordpress.com/manual/"
      # NOTE: use urllib.request.urlopen for Python 3
      manual_data = urllib.request.urlopen(url_manual)
      url_state = manual_data.getcode()
      if url_state == 200:
        # cache files
        if not cached:
          self.progress = ProgressDialog(self, message=GT("Caching manual files"),
              style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
          self.Disable()
          self.timer.Start(100)
          Thread(self.__cacheManualFiles, (url_manual, manual_cache, manual_index,)).Start()
          self.progress.ShowModal()
        manual_dialog = wx.Dialog(self, title="Debreate Manual", size=(800,500), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        manual = wx.html.HtmlWindow(manual_dialog)
        wx.GetApp().Yield()
        if manual.LoadFile(manual_index):
          manual_dialog.CenterOnParent()
          manual_dialog.ShowModal()
        else:
          wx.GetApp().Yield()
          webbrowser.open(url_manual)
        manual_dialog.Destroy()
      else:
        # open local document
        wx.GetApp().Yield()
        subprocess.call(["xdg-open", "{}/docs/usage.pdf".format(paths.getAppDir())])


  ## Opens the logs directory in the system's default file manager
  def OnLogDirOpen(self, event=None): #@UnusedVariable
    logger.debug(GT("Opening log directory ..."))

    subprocess.check_output([GetExecutable("xdg-open"), "{}/logs".format(paths.getLocalDir())], stderr=subprocess.STDOUT)


  ## Changes wizard page from menu
  def OnMenuChangePage(self, event=None):
    if isinstance(event, int):
      page_id = event

    else:
      page_id = event.GetId()

    self.Wizard.ShowPage(page_id)


  ## TODO: Doxygen
  def OnProjectNew(self, event=None): #@UnusedVariable
    self.ResetPages()


  ## TODO: Doxygen
  def OnProjectOpen(self, event=None): #@UnusedVariable
    projects_filter = "|*.{};*.{}".format(PROJECT_ext, PROJECT_txt)
    d = GT("Debreate project files")

    dia = wx.FileDialog(self, GT("Open Debreate Project"), os.getcwd(), "",
        "{}{}".format(d, projects_filter), wx.FD_CHANGE_DIR)
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
        data = (
          GetPage(pgid.CONTROL).GetSaveData(),
          GetPage(pgid.FILES).GetSaveData(),
          GetPage(pgid.SCRIPTS).GetSaveData(),
          GetPage(pgid.CHANGELOG).GetSaveData(),
          GetPage(pgid.COPYRIGHT).GetSaveData(),
          GetPage(pgid.MENU).GetSaveData(),
          GetPage(pgid.BUILD).GetSaveData(),
          )

        # Create a backup of the project
        overwrite = False
        if os.path.isfile(path):
          backup = "{}.backup".format(path)
          shutil.copy(path, backup)
          overwrite = True

        # This try statement can be removed when unicode support is enabled
        try:
          writeFile(path, "[DEBREATE-{}]\n{}".format(VERSION_string, "\n".join(data)))

          if overwrite:
            os.remove(backup)

        except UnicodeEncodeError:
          detail1 = GT("Unfortunately Debreate does not support unicode yet.")
          detail2 = GT("Remove any non-ASCII characters from your project.")

          ShowErrorDialog(GT("Save failed"), "{}\n{}".format(detail1, detail2), title=GT("Unicode Error"))

          if overwrite:
            os.remove(path)
            # Restore project backup
            shutil.move(backup, path)

    def OnSaveAs():
      dbp = "|*.dbp"
      d = GT("Debreate project files")
      dia = wx.FileDialog(self, GT("Save Debreate Project"), os.getcwd(), "", "{}{}".format(d, dbp),
                  wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
      if dia.ShowModal() == wx.ID_OK:
        filename = dia.GetFilename()
        if filename.split(".")[-1] == "dbp":
          filename = ".".join(filename.split(".")[:-1])

        self.LoadedProject = "{}/{}.dbp".format(os.path.split(dia.GetPath())[0], filename)

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
  def OnQuickBuild(self, event=None): #@UnusedVariable
    QB = QuickBuild(self)
    QB.ShowModal()
    QB.Destroy()


  ## Shows a dialog to confirm quit and write window settings to config file
  def OnQuit(self, event=None): #@UnusedVariable
    if ConfirmationDialog(self, GT("Quit?"),
        text=GT("You will lose any unsaved information")).ShowModal() in (wx.ID_OK, wx.OK):

      maximized = self.IsMaximized()
      WriteConfig("maximize", maximized)

      if maximized:
        WriteConfig("position", GetDefaultConfigValue("position"))
        WriteConfig("size", GetDefaultConfigValue("size"))
        WriteConfig("center", True)

      else:
        WriteConfig("position", self.GetPosition().Get())
        WriteConfig("size", self.GetSize().Get())
        WriteConfig("center", False)

      WriteConfig("workingdir", os.getcwd())

      self.Destroy()


  ## TODO: Doxygen
  def OnToggleTheme(self, event=None): #@UnusedVariable
    self.ToggleTheme(self)


  ## Shows or hides tooltips
  def OnToggleToolTips(self, event=None): #@UnusedVariable
    enabled = self.opt_tooltips.IsChecked()
    wx.ToolTip.Enable(enabled)

    WriteConfig("tooltips", enabled)


  ## Opens a dialog for creating/updating list of distribution names cache file
  def OnUpdateDistNamesCache(self, event=None): #@UnusedVariable
    DistNamesCacheDialog().ShowModal()


  ## Updates the page menu to reflect current page
  def OnWizardBtnPage(self, event=None): #@UnusedVariable
    ID = self.Wizard.GetCurrentPageId()
    logger.debug(GT("Event: EVT_CHANGE_PAGE, Page ID: {}").format(ID))

    menu_page = self.GetMenu(menuid.PAGE)
    if not menu_page.IsChecked(ID):
      menu_page.Check(ID, True)


  ## Deletes cache directory located at ~/.local/share/debreate/cache
  def OnClearCache(self, event=None):
    dir_cache = paths.getCacheDir()
    if os.path.isdir(dir_cache):
      shutil.rmtree(dir_cache)


  ## Opens web links from the help menu
  def OpenPolicyManual(self, event=None):
    if isinstance(event, wx.CommandEvent):
      event_id = event.GetId()

    elif isinstance(event, int):
      event_id = event

    else:
      logger.error("Cannot open policy manual link with object type {}".format(type(event)))

      return

    url = self.menu_policy.GetHelpString(event_id)
    webbrowser.open(url)


  ## Retrieves filename of loaded project
  def ProjectGetLoaded(self):
    return self.LoadedProject


  ## Tests project type & calls correct method to read project file
  #
  #  \param project_file
  #  \b \e str : Path to project file
  def OpenProject(self, project_file):
    logger.debug("Opening project: {}".format(project_file))

    if not os.path.isfile(project_file):
      ShowErrorDialog(GT("Could not open project file"),
          GT("File does not exist or is not a regular file: {}").format(project_file))
      return False

    data = readFile(project_file)

    lines = data.split("\n")

    # FIXME: Need a better way to determine valid project
    app = lines[0].lstrip("[")
    if not app.startswith("DEBREATE"):
      ShowErrorDialog(GT("Could not open project file"),
          GT("Not a valid Debreate project: {}").format(project_file))
      return False

    if self.LoadedProject and not self.ResetPages():
      return False

    # *** Get Control Data *** #
    control_data = data.split("<<CTRL>>\n")[1].split("\n<</CTRL>>")[0]
    depends_data = self.Wizard.GetPage(pgid.CONTROL).Set(control_data)
    self.Wizard.GetPage(pgid.DEPENDS).Set(depends_data)

    # *** Get Files Data *** #
    files_data = data.split("<<FILES>>\n")[1].split("\n<</FILES>>")[0]
    opened = self.Wizard.GetPage(pgid.FILES).Set(files_data)

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
    self.Wizard.GetPage(pgid.MENU).SetLauncherData(m_data, enabled=True)

    # Get Build Data
    build_data = data.split("<<BUILD>>\n")[1].split("\n<</BUILD")[0]#.split("\n")
    self.Wizard.GetPage(pgid.BUILD).Set(build_data)

    return opened


  ## TODO: Doxygen
  def ProjectChanged(self, event=None):
    if logger.debugging():
      logger.debug("MainWindow.OnProjectChanged:")
      print("  Object: {}".format(event.GetEventObject()))

    self.ProjectDirty = True


  ## TODO: Doxygen
  def ResetPages(self):
    warn_msg = GT("You will lose any unsaved information.")
    warn_msg = "{}\n\n{}".format(warn_msg, GT("Continue?"))

    if ConfirmationDialog(self, text=warn_msg).ShowModal() not in (wx.ID_OK, wx.OK):
      return False

    for page in self.Wizard.GetAllPages():
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
        self.SetTitle("{}*".format(title))


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
