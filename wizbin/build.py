# MIT licensing
# See: docs/LICENSE.txt


import math, os, subprocess, time, traceback, wx

from dbr.functions       import GetBoolean
from dbr.language        import GT
from dbr.log             import DebugEnabled
from dbr.log             import Logger
from dbr.md5             import WriteMD5
from globals.application import AUTHOR_email
from globals.bitmaps     import ICON_EXCLAMATION
from globals.bitmaps     import ICON_INFORMATION
from globals.cmdcheck    import CommandExists
from globals.errorcodes  import dbrerrno
from globals.execute     import GetCommandOutput
from globals.execute     import GetExecutable
from globals.execute     import GetSystemInstaller
from globals.fileio      import ReadFile
from globals.ident       import btnid
from globals.ident       import chkid
from globals.ident       import inputid
from globals.ident       import pgid
from globals.paths       import ConcatPaths
from globals.paths       import PATH_app
from globals.stage       import CreateStage
from globals.stage       import RemoveStage
from globals.strings     import GS
from globals.strings     import RemoveEmptyLines
from globals.strings     import TextIsEmpty
from globals.tooltips    import SetPageToolTips
from input.toggle        import CheckBox
from input.toggle        import CheckBoxCFG
from input.toggle        import CheckBoxESS
from startup.tests       import UsingTest
from ui.button           import AddCustomButtons
from ui.button           import CreateButton
from ui.checklist        import CheckListDialog
from ui.dialog           import DetailedMessageDialog
from ui.dialog           import GetFileSaveDialog
from ui.dialog           import ShowDialog
from ui.dialog           import ShowErrorDialog
from ui.layout           import BoxSizer
from ui.output           import OutputLog
from ui.panel            import BorderedPanel
from ui.progress         import PD_DEFAULT_STYLE
from ui.progress         import ProgressDialog
from ui.progress         import TimedProgressDialog
from ui.style            import layout as lyt
from ui.textpreview      import TextPreview
from wiz.helper          import FieldEnabled
from wiz.helper          import GetField
from wiz.helper          import GetFieldValue
from wiz.helper          import GetMainWindow
from wiz.helper          import GetPage
from wiz.helper          import GetWizard
from wiz.wizard          import WizardPage


## Build page
class Page(WizardPage):
  ## Constructor
  #
  #  \param parent
  #    Parent <b><i>wx.Window</i></b> instance
  def __init__(self, parent):
    WizardPage.__init__(self, parent, pgid.BUILD)

    # Bypass build prep check
    self.prebuild_check = False

    # Add checkable items to this list
    # FIXME: Use a different method
    self.build_options = []

    # ----- Extra Options

    pnl_options = BorderedPanel(self)

    self.chk_md5 = CheckBoxESS(pnl_options, chkid.MD5, GT("Create md5sums file"),
        name="MD5", defaultValue=True, commands="md5sum")
    # The » character denotes that an alternate tooltip should be shown if the control is disabled
    self.chk_md5.tt_name = "md5»"
    self.chk_md5.col = 0

    if UsingTest("alpha"):
      # Brings up control file preview for editing
      self.chk_editctrl = CheckBoxCFG(pnl_options, chkid.EDIT, GT("Preview control file for editing"),
          name="editctrl")
      self.chk_editctrl.col = 1

    # TODO: Use CheckBoxCFG instead of CheckBoxESS:
    #           Fields will be set from config instead of project file

    # Option to strip binaries
    self.chk_strip = CheckBoxESS(pnl_options, chkid.STRIP, GT("Strip binaries"),
        name="strip»", defaultValue=True, commands="strip")
    self.chk_strip.col = 0

    # Deletes the temporary build tree
    self.chk_rmstage = CheckBoxESS(pnl_options, chkid.DELETE, GT("Delete staged directory"),
        name="RMSTAGE", defaultValue=True)
    self.chk_rmstage.col = 0

    # Checks the output .deb for errors
    self.chk_lint = CheckBoxESS(pnl_options, chkid.LINT, GT("Check package for errors with lintian"),
        name="LINTIAN", defaultValue=True, commands="lintian")
    self.chk_lint.tt_name = "lintian»"
    self.chk_lint.col = 0

    # Installs the deb on the system
    self.chk_install = CheckBox(pnl_options, chkid.INSTALL, GT("Install package after build"),
        name="INSTALL", commands=("gdebi-gtk", "gdebi-kde",))
    self.chk_install.tt_name = "install»"
    self.chk_install.col = 0

    # *** Lintian Overrides *** #

    if UsingTest("alpha"):
      # FIXME: Move next to lintian check box
      self.lint_overrides = []
      btn_lint_overrides = CreateButton(self, label=GT("Lintian overrides"))
      btn_lint_overrides.Bind(wx.EVT_BUTTON, self.OnSetLintOverrides)

    btn_build = CreateButton(self, btnid.BUILD, GT("Build"), "build", 64)

    # Display log
    dsp_log = OutputLog(self)

    SetPageToolTips(self)

    # *** Event Handling *** #

    btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)

    # *** Layout *** #

    lyt_options = wx.GridBagSizer()

    next_row = 0
    prev_row = next_row
    for CHK in pnl_options.Children:
      row = next_row
      FLAGS = lyt.PAD_LR

      if CHK.col:
        row = prev_row
        FLAGS = wx.RIGHT

      lyt_options.Add(CHK, (row, CHK.col), flag=FLAGS, border=5)

      if not CHK.col:
        prev_row = next_row
        next_row += 1

    pnl_options.SetSizer(lyt_options)
    pnl_options.SetAutoLayout(True)
    pnl_options.Layout()

    lyt_buttons = BoxSizer(wx.HORIZONTAL)
    lyt_buttons.Add(btn_build, 1)

    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.AddSpacer(10)
    lyt_main.Add(wx.StaticText(self, label=GT("Extra Options")), 0,
        lyt.ALGN_L|wx.LEFT, 5)
    lyt_main.Add(pnl_options, 0, wx.LEFT, 5)
    lyt_main.AddSpacer(5)

    if UsingTest("alpha"):
      #lyt_main.Add(wx.StaticText(self, label=GT("Lintian overrides")), 0, wx.LEFT, 5)
      lyt_main.Add(btn_lint_overrides, 0, wx.LEFT, 5)

    lyt_main.AddSpacer(5)
    lyt_main.Add(lyt_buttons, 0, lyt.ALGN_C)
    lyt_main.Add(dsp_log, 2, wx.EXPAND|lyt.PAD_LRB, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()

    # *** Post-layout functions *** #

    self.InitDefaultSettings()


  ## Method that builds the actual Debian package
  #
  #  TODO: Test for errors when building deb package with other filename extension
  #  TODO: Remove deprecated methods that this one replaces
  #  \param outFile
  #        \b \e str : Absolute path to target file
  def Build(self, outFile):
    def log_message(msg, current_step, total_steps):
      return "{} ({}/{})".format(msg, current_step, total_steps)

    wizard = GetWizard()
    pages_build_ids = self.BuildPrep()

    if pages_build_ids != None:
      main_window = GetMainWindow()

      # Reported at the end of build
      build_summary = []

      steps_count = len(pages_build_ids)
      current_step = 0

      # Steps from build page
      for chk in self.chk_md5, self.chk_lint, self.chk_rmstage:
        if chk.IsChecked():
          steps_count += 1

      # Control file & .deb build step
      steps_count += 2

      stage = CreateStage()

      log_msg = GT("Starting build")

      wx.YieldIfNeeded()
      # FIXME: Enable PD_CAN_ABORT
      build_progress = ProgressDialog(main_window, GT("Building"), log_msg,
          maximum=steps_count)

      build_summary.append("{}:".format(log_msg))

      try:
        for P in wizard.GetAllPages():
          if build_progress.WasCancelled():
            break

          if P.GetId() in pages_build_ids:
            p_label = P.GetTitle()

            log_msg = log_message(
              GT("Processing page \"{}\"").format(p_label), current_step+1, steps_count)

            # FIXME: Progress bar not updating???
            wx.YieldIfNeeded()
            build_progress.Update(current_step, log_msg)

            ret_code, ret_value = P.ExportBuild(stage)

            build_summary.append("\n{}:\n{}".format(log_msg, ret_value))

            if ret_code > 0:
              build_progress.Destroy()

              ShowErrorDialog(GT("Error occurred during build"), ret_value)

              return

            current_step += 1

        # *** Control File *** #
        if not build_progress.WasCancelled():
          wx.YieldIfNeeded()

          log_msg = log_message(GT("Creating control file"), current_step+1, steps_count)
          build_progress.Update(current_step, log_msg)

          Logger.Debug(__name__, log_msg)

          # Retrieve control page
          pg_control = wizard.GetPage(pgid.CONTROL)
          if not pg_control:
            build_progress.Destroy()

            ShowErrorDialog(GT("Could not retrieve control page"),
                GT("Please contact the developer: {}").format(AUTHOR_email),
                title="Fatal Error")

            return

          installed_size = self.OnBuildGetInstallSize(stage)

          Logger.Debug(__name__, GT("Installed size: {}").format(installed_size))

          build_summary.append("\n{}:".format(log_msg))
          build_summary.append(
            pg_control.ExportBuild("{}/DEBIAN".format(stage).replace("//", "/"), installed_size)
            )

          current_step += 1

        # *** MD5 Checksum *** #
        if not build_progress.WasCancelled():
          if self.chk_md5.GetValue() and GetExecutable("md5sum"):
            log_msg = log_message(GT("Creating MD5 checksum"), current_step+1, steps_count)
            #log_msg = GT("Creating MD5 checksum")
            #step = "{}/{}".format(current_step+1, steps_count)

            Logger.Debug(__name__, log_msg)

            wx.YieldIfNeeded()
            build_progress.Update(current_step, log_msg)

            build_summary.append("\n{}:".format(log_msg))
            build_summary.append(self.OnBuildMD5Sum(stage))

            current_step += 1

        # *** Create .deb from Stage *** #
        if not build_progress.WasCancelled():
          log_msg = log_message(GT("Creating .deb package"), current_step+1, steps_count)

          wx.YieldIfNeeded()
          build_progress.Update(current_step, log_msg)

          build_summary.append("\n{}:".format(log_msg))
          build_summary.append(self.OnBuildCreatePackage(stage, outFile))

          current_step += 1

        # *** Lintian *** #
        if not build_progress.WasCancelled():
          if self.chk_lint.IsChecked():
            log_msg = log_message(GT("Checking package with lintian"), current_step+1, steps_count)

            wx.YieldIfNeeded()
            build_progress.Update(current_step, log_msg)

            build_summary.append("\n{}:".format(log_msg))
            build_summary.append(self.OnBuildCheckPackage(outFile))

            current_step += 1

        # *** Delete Stage *** #
        if not build_progress.WasCancelled():
          if self.chk_rmstage.IsChecked():
            log_msg = log_message(GT("Removing staged build tree"), current_step+1, steps_count)

            wx.YieldIfNeeded()
            build_progress.Update(current_step, log_msg)

            build_summary.append("\n{}:".format(log_msg))
            RemoveStage(stage)

            if not os.path.isdir(stage):
              build_summary.append(GT("Staged build tree removed successfully"))

            else:
              build_summary.append(GT("Failed to remove staged build tree"))

            current_step += 1

        # *** Show Completion Status *** #
        wx.YieldIfNeeded()
        build_progress.Update(steps_count, GT("Build completed"))

        # Show finished dialog for short moment
        time.sleep(1)

        # TODO: Add error count to build summary

        build_progress.Destroy()

        build_summary = "\n".join(build_summary)
        summary_dialog = DetailedMessageDialog(main_window, GT("Build Summary"),
            ICON_INFORMATION, GT("Build completed"), build_summary)
        summary_dialog.ShowModal()

      except:
        build_progress.Destroy()

        ShowErrorDialog(GT("Error occurred during build"), traceback.format_exc())

    return


  ## Checks pages for export & gets a count of how many tasks need be executed
  #
  #  \return
  #    <b><i>Tuple</i></b> containing data & label for each page
  def BuildPrep(self):
    wizard = GetWizard()
    prep_ids = []

    pages = wizard.GetAllPages()

    for P in pages:
      if P.prebuild_check:
        Logger.Debug(__name__, GT("Pre-build check for page \"{}\"".format(P.GetName())))
        prep_ids.append(P.GetId())

    try:
      main_window = GetMainWindow()

      # List of page IDs to process during build
      pg_build_ids = []

      steps_count = len(prep_ids)
      current_step = 0

      msg_label1 = GT("Prepping page \"{}\"")
      msg_label2 = GT("Step {}/{}")
      msg_label = "{} ({})".format(msg_label1, msg_label2)

      prep_progress = ProgressDialog(main_window, GT("Preparing Build"),
          msg_label2.format(current_step, steps_count), maximum=steps_count,
          style=PD_DEFAULT_STYLE|wx.PD_CAN_ABORT)

      for P in pages:
        if prep_progress.WasCancelled():
          break

        p_id = P.GetId()
        p_label = P.GetTitle()

        if p_id in prep_ids:
          Logger.Debug(__name__, msg_label.format(p_label, current_step+1, steps_count))

          wx.Yield()
          prep_progress.Update(current_step, msg_label.format(p_label, current_step+1, steps_count))

          if P.IsOkay():
            pg_build_ids.append(p_id)

          current_step += 1

      if not prep_progress.WasCancelled():
        wx.Yield()
        prep_progress.Update(current_step, GT("Prepping finished"))

        # Show finished dialog for short period
        time.sleep(1)

      prep_progress.Destroy()

      return pg_build_ids

    except:
      prep_progress.Destroy()

      ShowErrorDialog(GT("Error occurred during pre-build"), traceback.format_exc())

    return None


  ## Preview control file for editing
  def EditControl(self):
    pg_control = GetPage(pgid.CONTROL)

    ctrl_info = pg_control.GetCtrlInfo()

    preview = TextPreview(title=GT("Edit Control File"),
        text=ctrl_info, size=(600,400), readonly=False)
    AddCustomButtons(preview, (wx.ID_SAVE, wx.ID_CANCEL,), parent_sizer=True)

    if preview.ShowModal() == wx.ID_SAVE:
      Logger.Debug(__name__, "Updating control information ...")

      ctrl_info = preview.GetValue()


      depends_data = pg_control.Set(ctrl_info)
      GetPage(pgid.DEPENDS).Set(depends_data)


  ## Retrieves page data from fields
  def Get(self, getModule=False):
    # 'install after build' is not exported to project for safety

    fields = {}
    omit_options = (
      self.chk_install,
    )

    for O in self.build_options:
      # Leave options out that should not be saved
      if O not in omit_options:
        fields[O.GetName()] = GS(O.GetValue())

    page = wx.EmptyString

    for F in fields:
      if page == wx.EmptyString:
        page = "{}={}".format(F, fields[F])

      else:
        page = "{}\n{}={}".format(page, F, fields[F])

    if page == wx.EmptyString:
      page = None

    if getModule:
      page = (__name__, page,)

    return page


  ## Reads & parses page data from a formatted text file
  def ImportFromFile(self, filename):
    if not os.path.isfile(filename):
      return dbrerrno.ENOENT

    build_data = ReadFile(filename, split=True)

    options_definitions = {}

    for L in build_data:
      if "=" in L:
        key = L.split("=")
        value = GetBoolean(key[-1])
        key = key[0]

        options_definitions[key] = value

    for O in self.build_options:
      name = O.GetName()
      if name in options_definitions and isinstance(options_definitions[name], bool):
        O.SetValue(options_definitions[name])

    return 0


  ## Sets up page with default settings
  #
  #  FIXME: Deprecated/Replace with 'Reset' method???
  def InitDefaultSettings(self):
    self.build_options = []

    option_list = (
      (self.chk_md5, GetExecutable("md5sum"),),
      (self.chk_strip, GetExecutable("strip"),),
      (self.chk_rmstage, True,),
      (self.chk_lint, GetExecutable("lintian"),),
      (self.chk_install, GetSystemInstaller(),),
      )

    for option, command in option_list:
      # FIXME: Commands should be updated globally
      if not isinstance(command, bool) and command != None:
        command = CommandExists(command)

      option.Enable(bool(command))
      option.SetValue(FieldEnabled(option) and option.Default)

      if bool(command):
        self.build_options.append(option)


  ## Installs the built .deb package onto the system
  #
  #  Uses the system's package installer: gdebi-gtk or gdebi-kde if available
  #
  #  Shows a success dialog if installed. Otherwise shows an
  #  error dialog.
  #
  #  \param package
  #    Path of package to be installed
  def InstallPackage(self, package):
    system_installer = GetSystemInstaller()

    if not system_installer:
      ShowErrorDialog(
        GT("Cannot install package"),
        GT("A compatible package manager could not be found on the system"),
        __name__,
        warn=True
        )

      return

    Logger.Info(__name__, GT("Attempting to install package: {}").format(package))
    Logger.Info(__name__, GT("Installing with {}").format(system_installer))

    install_cmd = (system_installer, package,)

    wx.Yield()
    # FIXME: Use ExecuteCommand here
    install_output = subprocess.Popen(install_cmd)

    # Command appears to not have been executed correctly
    if install_output == None:
      ShowErrorDialog(
        GT("Could not install package: {}"),
        GT("An unknown error occurred"),
        __name__
        )

      return

    # Command executed but did not return success code
    if install_output.returncode:
      err_details = (
        GT("Process returned code {}").format(install_output.returncode),
        GT("Command executed: {}").format(" ".join(install_cmd)),
        )

      ShowErrorDialog(
        GT("An error occurred during installation"),
        "\n".join(err_details),
        __name__
        )

      return


  ## Handles event emitted by the 'build' button
  #
  #  Checks if required fields are filled & opens a file save dialog
  def OnBuild(self, event=None):
    if event:
      event.Skip()

    # Show control file preview for editing
    if UsingTest("alpha") and self.chk_editctrl.GetValue():
      self.EditControl()

    wizard = GetWizard()

    pg_control = wizard.GetPage(pgid.CONTROL)
    pg_files = wizard.GetPage(pgid.FILES)
    pg_launcher = wizard.GetPage(pgid.LAUNCHERS)

    required_fields = {
      GT("Control"): pg_control.GetRequiredFields(),
    }

    # Check if launchers are enabled for build
    if pg_launcher.GetLaunchersCount():
      required_fields[GT("Menu Launcher")] = pg_launcher.GetRequiredFields()

      # FIXME: Old code won't work with multiple launchers
      for RF in required_fields[GT("Menu Launcher")]:
        Logger.Debug(__name__, GT("Required field (Menu Launcher): {}").format(RF.GetName()))

    for p_name in required_fields:
      Logger.Debug(__name__, GT("Page name: {}").format(p_name))
      for F in required_fields[p_name]:
        if not isinstance(F, wx.StaticText) and TextIsEmpty(F.GetValue()):
          f_name = F.GetName()

          msg_l1 = GT("One of the required fields is empty:")
          msg_full = "{}: {} ➜ {}".format(msg_l1, p_name, f_name)

          Logger.Warn(__name__, msg_full)

          DetailedMessageDialog(GetMainWindow(), GT("Cannot Continue"), ICON_EXCLAMATION,
              text=msg_full).ShowModal()

          for P in wizard.GetAllPages():
            if P.GetTitle() == p_name:
              Logger.Debug(__name__, GT("Showing page with required field: {}").format(p_name))
              wizard.ShowPage(P.GetId())

          return

    if GetField(pg_files, inputid.LIST).MissingFiles():
      ShowErrorDialog(GT("Files are missing in file list"), warn=True, title=GT("Warning"))

      wizard.ShowPage(pgid.FILES)

      return

    ttype = GT("Debian Packages")
    save_dialog = GetFileSaveDialog(GetMainWindow(), GT("Build Package"),
        "{} (*.deb)|*.deb".format(ttype), "deb")

    package = GetFieldValue(pg_control, inputid.PACKAGE)
    version = GetFieldValue(pg_control, inputid.VERSION)
    arch = GetFieldValue(pg_control, inputid.ARCH)
    save_dialog.SetFilename("{}_{}_{}.deb".format(package, version, arch))

    if ShowDialog(save_dialog):
      self.Build(save_dialog.GetPath())


  ## Checks the final package for error with the lintian command
  #
  #  \param targetPackage
  #    Path of package to check
  def OnBuildCheckPackage(self, targetPackage):
    Logger.Debug(__name__,
        GT("Checking package \"{}\" for lintian errors ...").format(os.path.basename(targetPackage)))

    res = subprocess.run([GetExecutable("lintian"), targetPackage], capture_output=True)

    return res.stdout.decode("utf-8")


  ## Handles the process of building the package from the formatted stage directory
  #
  #  \param stage
  #    Path to formatted temporary staged directory
  #  \param targetFile
  #    Path of the target output .deb package
  def OnBuildCreatePackage(self, stage, targetFile):
    Logger.Debug(__name__, GT("Creating {} from {}").format(targetFile, stage))

    packager = GetExecutable("dpkg-deb")
    fakeroot = GetExecutable("fakeroot")

    if not fakeroot or not packager:
      return (dbrerrno.ENOENT, GT("Cannot run 'fakeroot dpkg'"))

    packager = os.path.basename(packager)

    Logger.Debug(__name__, GT("System packager: {}").format(packager))

    # DEBUG:
    cmd = "{} {} -b \"{}\" \"{}\"".format(fakeroot, packager, stage, targetFile)
    Logger.Debug(__name__, GT("Executing: {}").format(cmd))

    output = GetCommandOutput(fakeroot, (packager, "-b", stage, targetFile,))

    Logger.Debug(__name__, GT("Build output: {}").format(output))

    return output


  ## Retrieves total size of directory contents
  #
  #  TODO: Move this method to control page???
  #
  #  \param stage
  #    Path to formatted staged directory to scan file sizes
  #  \return
  #    <b><i>Integer</i></b> value representing installed size of all files in package
  def OnBuildGetInstallSize(self, stage):
    Logger.Debug(__name__, GT("Retrieving installed size for {}").format(stage))

    installed_size = 0
    for ROOT, DIRS, FILES in os.walk(stage):
      for F in FILES:
        if ROOT != "{}/DEBIAN".format(stage).replace("//", "/"):
          F = "{}/{}".format(ROOT, F).replace("//", "/")
          installed_size += os.stat(F).st_size

    # Convert to kilobytes & round up
    if installed_size:
      installed_size = int(math.ceil(float(installed_size) / float(1024)))

    return installed_size


  ## Creates an 'md5sum' file & populates with hashes for all files contained in package
  #
  #  FIXME: Hashes for .png images (binary files???) is not the same as those
  #         produced by debuild
  #
  #  \param stage
  #    Staged directory where files are scanned
  #  \return
  #    <b><i>String</i></b> message of result
  def OnBuildMD5Sum(self, stage):
    Logger.Debug(__name__,
        GT("Creating MD5sum file in {}").format(stage))

    WriteMD5(stage)

    return GT("md5sums file created: {}".format(os.path.isfile(ConcatPaths((stage, "DEBIAN/md5sums",)))))


  ## Retrieves list of available lintian tags (WIP)
  #
  #  TODO: Show warning dialog that this could take a while
  #  TODO: Add cancel option to progress dialog
  #  FIXME: List should be cached so no need for re-scanning
  def OnSetLintOverrides(self, event=None):
    Logger.Debug(__name__, GT("Setting Lintian overrides..."))

    lintian_tags_file = "{}/data/lintian/tags".format(PATH_app)

    if not os.path.isfile(lintian_tags_file):
      Logger.Error(__name__, "Lintian tags file is missing: {}".format(lintian_tags_file))

      return False

    lint_tags = RemoveEmptyLines(ReadFile(lintian_tags_file, split=True))

    if lint_tags:
      Logger.Debug(__name__, "Lintian tags set")

      # DEBUG: Start
      if DebugEnabled() and len(lint_tags) > 50:
        print("  Reducing tag count to 200 ...")

        lint_tags = lint_tags[:50]

      Logger.Debug(__name__, "Processing {} tags".format(len(lint_tags)))
      # DEBUG: End


      tag_count = len(lint_tags)

      def GetProgressMessage(message, count=tag_count):
        return "{} ({} {})".format(message, count, GT("tags"))


      progress = TimedProgressDialog(GetMainWindow(), GT("Building Tag List"),
          GetProgressMessage(GT("Scanning default tags")))
      progress.Start()

      wx.Yield()

      # Create the dialog
      overrides_dialog = CheckListDialog(GetMainWindow(), title=GT("Lintian Overrides"),
          allow_custom=True)
      # FIXME: Needs progress dialog
      overrides_dialog.InitCheckList(tuple(lint_tags))

      progress.SetMessage(GetProgressMessage(GT("Setting selected overrides")))

      for T in lint_tags:
        if T in self.lint_overrides:
          overrides_dialog.SetItemCheckedByLabel(T)
          self.lint_overrides.remove(T)

      progress.SetMessage(GetProgressMessage(GT("Adding custom tags"), len(self.lint_overrides)))

      # Remaining tags should be custom entries
      # FIXME:
      if self.lint_overrides:
        for T in self.lint_overrides:
          overrides_dialog.AddItem(T, True)

      progress.Stop()

      if overrides_dialog.ShowModal() == wx.ID_OK:
        # Remove old overrides
        self.lint_overrides = []
        for L in overrides_dialog.GetCheckedLabels():
          Logger.Debug(__name__, GT("Adding Lintian override: {}").format(L))

          self.lint_overrides.append(L)

      return True

    else:
      Logger.Debug(__name__, "Setting lintian tags failed")

      return False


  ## Resets page's fields to default settings
  def Reset(self):
    for O in self.build_options:
      O.SetValue(O.Default)


  ## Sets page's fields data
  #
  #  \param data
  #    <b><i>Text</i></b> to be parsed for values
  def Set(self, data):
    # ???: Redundant
    self.Reset()
    build_data = data.split("\n")

    if GetExecutable("md5sum"):
      self.chk_md5.SetValue(int(build_data[0]))

    self.chk_rmstage.SetValue(int(build_data[1]))

    if GetExecutable("lintian"):
      self.chk_lint.SetValue(int(build_data[2]))


  ## Sets the build summary for display & review after package is created
  def SetSummary(self, event=None):
    pg_scripts = GetPage(pgid.SCRIPTS)

    # Make sure the page is not destroyed so no error is thrown
    if self:
      # Set summary when "Build" page is shown
      # Get the file count
      files_total = GetPage(pgid.FILES).GetFileCount()
      f = GT("File Count")
      file_count = "{}: {}".format(f, files_total)

      # Scripts to make
      scripts_to_make = []
      scripts = (("preinst", pg_scripts.chk_preinst),
        ("postinst", pg_scripts.chk_postinst),
        ("prerm", pg_scripts.chk_prerm),
        ("postrm", pg_scripts.chk_postrm))

      for script in scripts:
        if script[1].IsChecked():
          scripts_to_make.append(script[0])

      s = GT("Scripts")
      if len(scripts_to_make):
        scripts_to_make = "{}: {}".format(s, ", ".join(scripts_to_make))

      else:
        scripts_to_make = "{}: 0".format(s)

      self.summary.SetValue("\n".join((file_count, scripts_to_make)))
