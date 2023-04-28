
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Defines interface of the main window.
#
#  @module ui.main

import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import urllib
import webbrowser

_have_wget = False
try:
  import wget
  _have_wget = True
except ModuleNotFoundError:
  pass

from urllib.error import HTTPError
from urllib.error import URLError

import wx
import wx.html2

import globals.paths
import ui.app

from dbr.config           import GetDefaultConfigValue
from dbr.event            import EVT_CHANGE_PAGE
from dbr.event            import EVT_TIMER_STOP
from dbr.functions        import GetCurrentVersion
from dbr.functions        import UsingDevelopmentVersion
from dbr.icon             import Icon
from dbr.language         import GT
from dbr.timer            import DebreateTimer
from globals              import threads
from globals              import tooltips
from globals.bitmaps      import LOGO
from globals.project      import PROJECT_ext
from globals.project      import PROJECT_txt
from libdbr               import config
from libdbr               import fileio
from libdbr               import paths
from libdbr               import strings
from libdbr.logger        import Logger
from libdebreate          import appinfo
from libdebreate.ident    import menuid
from libdebreate.ident    import pgid
from libdebreate.ident    import pnlid
from startup              import tests
from ui.about             import AboutDialog
from ui.dialog            import ConfirmationDialog
from ui.dialog            import DetailedMessageDialog
from ui.dialog            import ShowErrorDialog
from ui.distcache         import DistNamesCacheDialog
from ui.help              import HelpDialog
from ui.helper            import GetPage
from ui.layout            import BoxSizer
from ui.menu              import createMenuBar
from ui.progress          import ProgressDialog
from ui.quickbuild        import QuickBuild
from ui.startpage         import Page as PageInit
from ui.wizard            import Wizard


logger = Logger(__name__)
default_title = GT("Debreate - Debian Package Builder")

## The main window interface.
class MainWindow(wx.Frame):
  ## Constructor
  #
  #  @param pos
  #  <b><i>Integer tuple</i></b> or <b><i>wx.Point</i></b> instance indicating the screen position of the window
  #  @param size
  #  <b><i>Integer tuple</i></b> or <b><i>wx.Size</i></b> instance indicating the dimensions of the window
  def __init__(self):#, pos, size):
    wx.Frame.__init__(self, None, pnlid.MAIN)
    self.error = {}

    self.sub_thread_id = None

    self.timer = DebreateTimer(self)
    # placeholder for progress dialog
    self.progress = None

    self.Bind(wx.EVT_TIMER, self.__onTimerEvent)
    self.Bind(EVT_TIMER_STOP, self.__onTimerStop)

    # Make sure that this frame is set as the top window
    if not wx.GetApp().GetTopWindow() == self:
      logger.debug(GT("Setting MainWindow instance as top window"))

      wx.GetApp().SetTopWindow(self)

    title_st = default_title
    if logger.debugging():
      title_st += " (" + GT("debugging") + ")"
    self.SetTitle(title_st)

    self.SetMinSize(wx.Size(640, 400))

    # ----- Set Titlebar Icon
    self.SetIcon(Icon(LOGO))

    # *** Status Bar *** #
    self.SetStatusBar(wx.StatusBar(self, style=wx.STB_SIZEGRIP))

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
    self.Bind(wx.EVT_MENU, self.onCacheLintianTags, id=menuid.LINTTAGS)

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

  ## Actions that should be called after the main window has been created & set in the `wx.App`.
  def onInit(self):
    logger.debug("calling '{}.{}'".format(self.__class__.__name__, self.onInit.__name__))
    self.OnToggleToolTips()

  ## Retrieves menu by ID
  #
  #  @return
  #    `wx.Menu` instance.
  def getMenu(self, menuId):
    return self.getMenuBar().GetMenuById(menuId)

  ## Alias of `ui.main.MainWindow.getMenu` for backward compatibility.
  #
  #  @deprecated
  #    Use `ui.main.MainWindow.getMenu`.
  def GetMenu(self, menuId):
    logger.deprecated(self.GetMenu, alt=self.getMenu)

    return self.getMenu(menuId)

  ## Retrieves the main menu bar.
  #
  #  @return
  #    `wx.MenuBar` instance.
  def getMenuBar(self):
    return super().GetMenuBar()

  ## Alias of `ui.main.MainWindow.getMenuBar` for backward compatibility.
  #
  #  @deprecated
  #    Use `ui.main.MainWindow.getMenuBar`.
  def GetMenuBar(self):
    logger.deprecated(self.GetMenuBar, alt=self.getMenuBar)

    return self.getMenuBar()

  ## Retrieves the Wizard instance
  #
  #  @return
  #    `ui.wizard.Wizard` instance.
  def GetWizard(self):
    return self.Wizard

  ## Sets the pages in the `ui.wizard.Wizard` instance.
  def InitWizard(self):
    self.Wizard.AddPage(PageInit(self.Wizard))
    self.Wizard.SetModeBin(0)

  ## @todo Doxygen
  def IsNewProject(self):
    title = self.GetTitle()
    if title == default_title:
      return True
    else:
      return False

  ## @todo Doxygen
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
    about.SetVersion(appinfo.getVersionString())
    about.SetDescription(GT("A package builder for Debian based systems"))
    about.SetAuthor(appinfo.getAuthor())

    proj_pages = appinfo.getProjectPages()
    about.SetWebsites((
      (GT("Homepage"), appinfo.getHomePage()),
      (GT("GitHub Project"), proj_pages[0]),
      (GT("GitLab Project"), proj_pages[1]),
      (GT("SourceForge Project"), proj_pages[2]),
    ))

    about.AddJobs(
      appinfo.getAuthor(),
      (
        GT("Head Developer"),
        GT("Packager"),
        "{} (es, it)".format(GT("Translation")),
        GT("Website Designer & Author")
      ),
      appinfo.getEmail()
    )

    about.AddJobs(
      "Hugo Posnic",
      (
        GT("Code Contributor"),
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

  ## Starts thread for downloading lintian tags & creates a progress dialog.
  #
  #  @todo
  #    - use custom progress dialog
  #    - add confirmation dialog
  def onCacheLintianTags(self, evt=None):
    self.sub_thread_id = threads.create(self.cacheLintianTags)
    progress = wx.ProgressDialog(GT("Lintian Tags"), GT("Caching Lintian tags"), maximum=100,
        parent=self, style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
    self.Disable()
    progress.Show()
    pulse_time = time.time()
    while threads.isActive(self.sub_thread_id):
      if progress.WasCancelled():
        break
      iter_time = time.time()
      # pulse every 50 milliseconds
      if iter_time - pulse_time >= 0.05:
        progress.Pulse()
        pulse_time = iter_time
    threads.end(self.sub_thread_id)
    progress.Destroy()
    self.Enable()

  ## Caches list of tags recognized by lintian & stores them in local cache directory.
  def cacheLintianTags(self):
    dir_cache = globals.paths.getCacheDir()
    if not os.path.isdir(dir_cache):
      fileio.makeDir(dir_cache)
    file_tags = paths.join(dir_cache, "lintian_tags")
    logger.debug("caching lintian tags to '{}'".format(file_tags))
    res, msg = self.parseLintianTags()
    if type(res) == int:
      return res, msg
    logger.debug("found {} tags".format(len(res)))
    fileio.writeFile(file_tags, res)
    return 0, None

  ## Downloads & parses tags information from remote page.
  #
  #  @return
  #    List of available tags.
  def parseLintianTags(self):
    l_tags = []
    contents = None
    try:
      req = urllib.request.urlopen("https://lintian.debian.org/tags")
      contents = req.read().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
      req.close()
    except (HTTPError, URLError):
      return 1, traceback.format_exc()
    if contents == None:
      return 1, "an unknown error occurred when trying to download lintian tags info"
    for li in contents.split("\n"):
      li = li.strip()
      if li.startswith("<a href=\"/tags/"):
        l_tags.append(li.split(">", 1)[-1].split("</a>", 1)[0])
    if not l_tags:
      return 1, "an unknown error occurred when trying to parse lintian tags info"
    return l_tags, None

  ## Checks for new release availability
  def OnCheckUpdate(self, event=None): #@UnusedVariable
    update_test = tests.isActive("update-fail")

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
      current = strings.toString(current)
      ShowErrorDialog(error_remote, current)
    elif isinstance(current, tuple) and current > appinfo.getVersion():
      current = "{}.{}.{}".format(current[0], current[1], current[2])
      l1 = GT("Version {} is available!").format(current)
      l2 = GT("Would you like to go to Debreate's website?")
      if ConfirmationDialog(self, GT("Update"), "{}\n\n{}".format(l1, l2)).Confirmed():
        wx.LaunchDefaultBrowser(appinfo.getHomePage())
    elif isinstance(current, str):
      ShowErrorDialog(error_remote, current)
    else:
      DetailedMessageDialog(self, GT("Debreate"), text=GT("Debreate is up to date!")).ShowModal()

  ## @todo Doxygen
  def __resetError(self):
    self.error = {}

  ## @todo Doxygen
  def __cacheManualFiles(self, *args, **kwargs):
    manual_url = "https://debreate.github.io/help/usage.html"
    logger.debug("caching manual from {}".format(manual_url))

    manual_cache = args[0]
    dir_orig = os.getcwd()
    os.chdir(manual_cache)

    try:
      cmd_wget = paths.getExecutable("wget")
      if cmd_wget:
        subprocess.run([cmd_wget, "-rkp", "-nd", "-np", "-D", "debreate.github.io",
            manual_url])
      elif _have_wget:
        # wget module does not download required accompanying files
        wget.download(manual_url)
      else:
        # TODO: fallback to urllib
        pass
    except:
      self.error["message"] = "the following error occurred when trying to cache remote manual pages"
      self.error["details"] = traceback.format_exc()

    os.chdir(dir_orig)
    self.timer.Stop()

  ## Calls Pulse method on progress dialog when timer event occurs
  def __onTimerEvent(self, event=None):
    if self.progress:
      self.progress.Pulse()

  ## @todo Doxygen
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
  #
  #  @todo Use dialog as main method
  def OnHelp(self, event=None): #@UnusedVariable
    if tests.isActive("alpha"):
      HelpDialog(self).ShowModal()
    else:
      # FIXME: files should be re-cached when Debreate upgraded to new version
      # TODO: trim unneeded text
      # ~ cached = False
      manual_cache = paths.join(globals.paths.getCacheDir(), "manual")
      manual_index = paths.join(manual_cache, "usage.html")
      if not os.path.isdir(manual_cache):
        os.makedirs(manual_cache)
      if not os.path.isfile(manual_index):
        self.progress = ProgressDialog(self, message=GT("Caching manual files"),
            style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        self.Disable()
        self.timer.Start(100)
        threads.create(self.__cacheManualFiles, manual_cache)
        self.progress.ShowModal()
        self.Enable()
        if self.error:
          msg = self.error["message"]
          msg = GT(re.sub(r"^(.)", msg[0].title(), msg))
          ShowErrorDialog(msg, self.error["details"])
          self.__resetError()
      if os.path.isfile(manual_index):
        manual_dialog = wx.Dialog(self, title=GT("Debreate Manual"), size=wx.Size(800, 500),
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        manual = wx.html2.WebView.New()
        manual.Create(manual_dialog, url="file://" + manual_index)
        manual_dialog.ShowModal()
        manual_dialog.Destroy()
      else:
        # fallback to local PDF document
        cmd_xdg_open = paths.getExecutable("xdg-open")
        if cmd_xdg_open:
          wx.GetApp().Yield()
          subprocess.run([cmd_xdg_open, paths.join(paths.getAppDir(), "docs/usage.pdf")])

  ## Opens the logs directory in the system's default file manager
  def OnLogDirOpen(self, event=None): #@UnusedVariable
    dir_logs = globals.paths.getLogsDir()
    if os.path.isdir(dir_logs):
      fileio.openFileManager(dir_logs)
      return
    logger.debug("log directory not available")

  ## Changes wizard page from menu
  def OnMenuChangePage(self, event=None):
    if isinstance(event, int):
      page_id = event
    else:
      page_id = event.GetId()
    self.Wizard.ShowPage(page_id)

  ## @todo Doxygen
  def OnProjectNew(self, event=None): #@UnusedVariable
    self.ResetPages()

  ## @todo Doxygen
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

  ## @todo Doxygen
  def OnProjectSave(self, event=None):
    event_id = event.GetId()

    def SaveIt(path):
        # Gather data from different pages
        data = []
        for page in self.Wizard.GetAllPages():
          p_data = page.GetSaveData() if hasattr(page, "GetSaveData") else None
          logger.debug(page.GetLabel() + ": " + ("<data>" if p_data != None else str(None)))
          if p_data != None:
            data.append(p_data)

        # Create a backup of the project
        overwrite = False
        if os.path.isfile(path):
          backup = "{}.backup".format(path)
          shutil.copy(path, backup)
          overwrite = True

        # This try statement can be removed when unicode support is enabled
        try:
          fileio.writeFile(path, "[DEBREATE-{}]\n{}".format(appinfo.getVersionString(),
              "\n".join(data)))
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

    ## @todo Doxygen
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

  ## @todo Doxygen
  def OnQuickBuild(self, event=None): #@UnusedVariable
    QB = QuickBuild(self)
    QB.ShowModal()
    QB.Destroy()

  ## Shows a dialog to confirm quit and write window settings to config file
  def OnQuit(self, event=None): #@UnusedVariable
    if ConfirmationDialog(self, GT("Quit?"),
        text=GT("You will lose any unsaved information")).ShowModal() in (wx.ID_OK, wx.OK):
      self.saveConfigAndShutdown()

  ## Stores configuration settings & closes app.
  def saveConfigAndShutdown(self):
    # check sub-threads
    for t_id, t in threads.getActive().items():
      if t.is_alive():
        logger.warn("found active thread at shutdown: {}".format(t_id))

    cfg_user = config.get("user")
    maximized = self.IsMaximized()
    cfg_user.setValue("maximize", maximized)
    if maximized:
      cfg_user.setValue("position", GetDefaultConfigValue("position"), sep=",")
      cfg_user.setValue("size", GetDefaultConfigValue("size"), sep=",")
      cfg_user.setValue("center", True)
    else:
      cfg_user.setValue("position", self.GetPosition().Get(), sep=",")
      cfg_user.setValue("size", self.GetSize().Get(), sep=",")
      cfg_user.setValue("center", False)
    cfg_user.setValue("workingdir", os.getcwd())
    cfg_user.save()
    self.Destroy()

  ## @todo Doxygen
  def OnToggleTheme(self, event=None): #@UnusedVariable
    self.ToggleTheme(self)

  ## Shows or hides tooltips
  def OnToggleToolTips(self, event=None): #@UnusedVariable
    enabled = self.opt_tooltips.IsChecked()
    if not tooltips.enable(enabled):
      logger.error("an error occurred while setting tooltips state")
    cfg_user = config.get("user")
    cfg_user.setValue("tooltips", enabled)
    cfg_user.save()

  ## Opens a dialog for creating/updating list of distribution names cache file
  def OnUpdateDistNamesCache(self, event=None): #@UnusedVariable
    DistNamesCacheDialog().ShowModal()

  ## Updates the page menu to reflect current page
  def OnWizardBtnPage(self, event=None): #@UnusedVariable
    ID = self.Wizard.GetCurrentPageId()
    logger.debug(GT("Event: EVT_CHANGE_PAGE, Page ID: {}").format(ID))

    menu_page = self.getMenu(menuid.PAGE)
    if not menu_page.IsChecked(ID):
      menu_page.Check(ID, True)

  ## Deletes cache directory located at ~/.local/share/debreate/cache
  def OnClearCache(self, event=None):
    dir_cache = globals.paths.getCacheDir()
    if os.path.isdir(dir_cache):
      dia = ConfirmationDialog(self, text=GT("Delete '{}'?").format(dir_cache))
      if dia.ShowModal() != wx.ID_OK:
        return
      shutil.rmtree(dir_cache)
      # update list of distribution names on changelog page
      ui.app.getPage(pgid.CHANGELOG).reloadDistNames()

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
  #  @param project_file
  #    \b \e str : Path to project file
  def OpenProject(self, project_file):
    project_file = os.path.realpath(project_file)
    logger.debug("Opening project: {}".format(project_file))

    if not os.path.isfile(project_file):
      ShowErrorDialog(GT("Could not open project file"),
          GT("File does not exist or is not a regular file: {}").format(project_file))
      return False

    data = fileio.readFile(project_file)

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
    depends_data = self.Wizard.getPage(pgid.CONTROL).Set(control_data)
    self.Wizard.getPage(pgid.DEPENDS).Set(depends_data)

    # *** Get Files Data *** #
    files_data = data.split("<<FILES>>\n")[1].split("\n<</FILES>>")[0]
    opened = self.Wizard.getPage(pgid.FILES).Set(files_data)

    # *** Get Scripts Data *** #
    scripts_data = data.split("<<SCRIPTS>>\n")[1].split("\n<</SCRIPTS>>")[0]
    self.Wizard.getPage(pgid.SCRIPTS).Set(scripts_data)

    # *** Get Changelog Data *** #
    clog_data = data.split("<<CHANGELOG>>\n")[1].split("\n<</CHANGELOG>>")[0]
    self.Wizard.getPage(pgid.CHANGELOG).Set(clog_data)

    # *** Get Copyright Data *** #
    try:
      cpright_data = data.split("<<COPYRIGHT>>\n")[1].split("\n<</COPYRIGHT")[0]
      self.Wizard.getPage(pgid.COPYRIGHT).Set(cpright_data)

    except IndexError:
      pass

    # *** Get Menu Data *** #
    m_data = data.split("<<MENU>>\n")[1].split("\n<</MENU>>")[0]
    self.Wizard.getPage(pgid.MENU).SetLauncherData(m_data, enabled=True)

    # Get Build Data
    # ~ build_data = data.split("<<BUILD>>\n")[1].split("\n<</BUILD")[0]#.split("\n")
    # ~ self.Wizard.getPage(pgid.BUILD).Set(build_data)

    return opened

  ## @todo Doxygen
  def ProjectChanged(self, event=None):
    if logger.debugging():
      logger.debug("MainWindow.OnProjectChanged:")
      print("  Object: {}".format(event.GetEventObject()))
    self.ProjectDirty = True

  ## @todo Doxygen
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

  ## @todo Doxygen
  def SetSavedStatus(self, status):
    if status: # If status is changing to unsaved this is True
      title = self.GetTitle()
      if self.IsSaved() and title != default_title:
        self.SetTitle("{}*".format(title))

  ## @todo Doxygen
  #  @todo Finish definition
  def ToggleTheme(self, window):
    for C in window.GetChildren():
      self.ToggleTheme(C)

    bg_color = window.GetBackgroundColour()
    fg_color = window.GetForegroundColour()

    window.SetBackgroundColour(fg_color)
    window.SetForegroundColour(bg_color)
