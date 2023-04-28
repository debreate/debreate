
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module wizbin.build

import os
import shutil
import subprocess
import traceback

import wx

import ui.app
import globals.execute
import globals.paths
import libdbr.bin
import ui.page

from dbr.functions      import fileUnstripped
from dbr.language       import GT
from dbr.md5            import WriteMD5
from globals.bitmaps    import ICON_EXCLAMATION
from globals.bitmaps    import ICON_INFORMATION
from globals.errorcodes import dbrerrno
from globals.strings    import RemoveEmptyLines
from globals.system     import PY_VER_MAJ
from globals.tooltips   import SetPageToolTips
from input.toggle       import CheckBox
from input.toggle       import CheckBoxCFG
from libdbr             import fileio
from libdbr             import paths
from libdbr             import strings
from libdbr.logger      import Logger
from libdebreate.ident  import btnid
from libdebreate.ident  import chkid
from libdebreate.ident  import inputid
from libdebreate.ident  import pgid
from startup            import tests
from ui.button          import CreateButton
from ui.checklist       import CheckListDialog
from ui.dialog          import DetailedMessageDialog
from ui.dialog          import ShowErrorDialog
from ui.helper          import FieldEnabled
from ui.helper          import GetField
from ui.layout          import BoxSizer
from ui.output          import OutputLog
from ui.panel           import BorderedPanel
from ui.progress        import PD_DEFAULT_STYLE
from ui.progress        import ProgressDialog
from ui.progress        import TimedProgressDialog
from ui.style           import layout as lyt


logger = Logger(__name__)

## Build page
class Page(ui.page.Page):
  ## Constructor
  #
  #  @param parent
  #    Parent <b><i>wx.Window</i></b> instance
  def __init__(self, parent):
    super().__init__(parent, pgid.BUILD)

    # ----- Extra Options

    pnl_options = BorderedPanel(self)

    self.chk_md5 = CheckBoxCFG(pnl_options, chkid.MD5, GT("Create md5sums file"), name="MD5",
        defaultValue=True, cfgKey="md5sums", cfgSect="build")
    # The » character denotes that an alternate tooltip should be shown if the control is disabled
    self.chk_md5.tt_name = "md5»"
    self.chk_md5.col = 0

    # Option to strip binaries
    self.chk_strip = CheckBoxCFG(pnl_options, chkid.STRIP, GT("Strip binaries"), name="strip»",
        defaultValue=True, commands="strip", cfgKey="strip", cfgSect="build")
    self.chk_strip.col = 0

    self.chk_permiss = CheckBoxCFG(pnl_options, chkid.PERMISS, GT("Standardize file permissions"),
        name="permiss", defaultValue=True, cfgKey="standard_permissions", cfgSect="build")
    self.chk_permiss.col = 0

    # Deletes the temporary build tree
    self.chk_rmstage = CheckBoxCFG(pnl_options, chkid.DELETE, GT("Delete staged directory"),
        name="RMSTAGE", defaultValue=True, cfgKey="delete_stage", cfgSect="build")
    self.chk_rmstage.col = 0

    # Checks the output .deb for errors
    self.chk_lint = CheckBoxCFG(pnl_options, chkid.LINT, GT("Check package for errors with lintian"),
        name="LINTIAN", defaultValue=True, commands="lintian", cfgKey="lintian", cfgSect="build")
    self.chk_lint.tt_name = "lintian»"
    self.chk_lint.col = 0

    # Installs the deb on the system
    self.chk_install = CheckBox(pnl_options, chkid.INSTALL, GT("Install package after build"),
        name="INSTALL", commands=globals.execute.getDebInstallerList())
    self.chk_install.tt_name = "install»"
    self.chk_install.col = 0

    # *** Lintian Overrides *** #

    if tests.isActive("alpha"):
      # FIXME: Move next to lintian check box
      logger.info("Enabling alpha feature \"lintian overrides\" option")
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
    for CHK in pnl_options.GetChildren():
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

    if tests.isActive("alpha"):
      #lyt_main.Add(wx.StaticText(self, label=GT("Lintian overrides")), 0, wx.LEFT, 5)
      lyt_main.Add(btn_lint_overrides, 0, wx.LEFT, 5)

    lyt_main.AddSpacer(5)
    lyt_main.Add(lyt_buttons, 0, lyt.ALGN_C)
    lyt_main.Add(dsp_log, 2, wx.EXPAND|wx.ALL, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()

  ## @override ui.page.Page.init
  def init(self):
    return True

  ## Method that builds the actual Debian package
  #
  #  @param task_list
  #    \b \e dict : Task string IDs & page data
  #  @param build_path
  #    \b \e str : Directory where .deb will be output
  #  @param filename
  #    \b \e str : Basename of output file without .deb extension
  #  @return
  #    \b \e dbrerror : SUCCESS if build completed successfully
  def Build(self, task_list, build_path, filename):
    # Declare this here in case of error before progress dialog created
    build_progress = None

    try:
      # Other mandatory tasks that will be processed
      mandatory_tasks = (
        "stage",
        "install_size",
        "control",
        "build",
        )

      # Add other mandatory tasks
      for T in mandatory_tasks:
        task_list[T] = None

      task_count = len(task_list)

      # Add each file for updating progress dialog
      if "files" in task_list:
        task_count += len(task_list["files"])

      # Add each script for updating progress dialog
      if "scripts" in task_list:
        task_count += len(task_list["scripts"])

      if logger.debugging():
        task_msg = GT("Total tasks: {}").format(task_count)
        print("DEBUG: [{}] {}".format(__name__, task_msg))
        for T in task_list:
          print("\t{}".format(T))

      create_changelog = "changelog" in task_list
      create_copyright = "copyright" in task_list

      pg_control = ui.app.getPage(pgid.CONTROL)
      pg_menu = ui.app.getPage(pgid.MENU)

      stage_dir = "{}/{}__dbp__".format(build_path, filename)

      if os.path.isdir("{}/DEBIAN".format(stage_dir)):
        try:
          shutil.rmtree(stage_dir)

        except OSError:
          ShowErrorDialog(GT("Could not free stage directory: {}").format(stage_dir),
              title=GT("Cannot Continue"))

          return (dbrerrno.EEXIST, None)

      # Actual path to new .deb
      deb = paths.join(build_path, "{}.deb".format(filename))

      progress = 0

      task_msg = GT("Preparing build tree")
      logger.debug(task_msg)

      wx.GetApp().Yield()
      build_progress = ProgressDialog(ui.app.getMainWindow(), GT("Building"), task_msg,
          maximum=task_count,
          style=PD_DEFAULT_STYLE|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_CAN_ABORT)

      DIR_debian = os.path.join(stage_dir, "DEBIAN")

      # Make a fresh build tree
      os.makedirs(DIR_debian)
      progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      def UpdateProgress(current_task, message=None):
        task_eval = "{} / {}".format(current_task, task_count)

        if message:
          logger.debug("{} ({})".format(message, task_eval))

          wx.GetApp().Yield()
          build_progress.Update(current_task, message)

          return (None, None)

        wx.GetApp().Yield()
        build_progress.Update(current_task)

      # *** Files *** #
      if "files" in task_list:
        UpdateProgress(progress, GT("Copying files"))

        no_follow_link = GetField(ui.app.getPage(pgid.FILES), chkid.SYMLINK).IsChecked()

        # TODO: move this into a file functions module
        def _copy(f_src, f_tgt, exe=False):
          # NOTE: Python 3 appears to have follow_symlinks option for shutil.copy
          # FIXME: copying nested symbolic link may not work

          if os.path.isdir(f_src):
            if os.path.islink(f_src) and no_follow_link:
              logger.debug("Adding directory symbolic link to stage: {}".format(f_tgt))

              os.symlink(os.readlink(f_src), f_tgt)
            else:
              logger.debug("Adding directory to stage: {}".format(f_tgt))

              shutil.copytree(f_src, f_tgt)
              os.chmod(f_tgt, 0o0755)
          elif os.path.isfile(f_src):
            if os.path.islink(f_src) and no_follow_link:
              logger.debug("Adding file symbolic link to stage: {}".format(f_tgt))

              os.symlink(os.readlink(f_src), f_tgt)
            else:
              if exe:
                logger.debug("Adding executable to stage: {}".format(f_tgt))
              else:
                logger.debug("Adding file to stage: {}".format(f_tgt))

              shutil.copy(f_src, f_tgt)

              # Set FILE permissions
              if exe:
                os.chmod(f_tgt, 0o0755)

              else:
                os.chmod(f_tgt, 0o0644)

        files_data = task_list["files"]
        for FILE in files_data:
          file_defs = FILE.split(" -> ")

          source_file = file_defs[0]
          target_file = "{}{}/{}".format(stage_dir, file_defs[2], file_defs[1])
          target_dir = os.path.dirname(target_file)

          if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

          # Remove asterisks from executables
          exe = False
          if source_file[-1] == "*":
            exe = True
            source_file = source_file[:-1]

          _copy(source_file, "{}/{}".format(target_dir, os.path.basename(source_file)), exe)

          # Individual files
          progress += 1
          UpdateProgress(progress)

        # Entire file task
        progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # *** Strip files ***#
      # FIXME: Needs only be run if 'files' step is used
      if "strip" in task_list:
        UpdateProgress(progress, GT("Stripping binaries"))

        for ROOT, DIRS, FILES in os.walk(stage_dir): #@UnusedVariable
          for F in FILES:
            # Don't check files in DEBIAN directory
            if ROOT != DIR_debian:
              F = paths.join(ROOT, F)
              if fileUnstripped(F):
                logger.debug("unstripped file: {}".format(F))
                err, msg = libdbr.bin.execute(paths.getExecutable("strip"), F)

        progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      package = GetField(pg_control, inputid.PACKAGE).GetValue()

      # Make sure that the directory is available in which to place documentation
      if create_changelog or create_copyright:
        doc_dir = "{}/usr/share/doc/{}".format(stage_dir, package)
        if not os.path.isdir(doc_dir):
          os.makedirs(doc_dir)

      # *** Changelog *** #
      if create_changelog:
        UpdateProgress(progress, GT("Creating changelog"))

        # If changelog will be installed to default directory
        changelog_target = task_list["changelog"][0]
        if changelog_target == "STANDARD":
          changelog_target = os.path.join("{}/usr/share/doc".format(stage_dir), package)

        else:
          changelog_target = os.path.join(stage_dir, changelog_target)

        if not os.path.isdir(changelog_target):
          os.makedirs(changelog_target)

        fileio.writeFile("{}/changelog".format(changelog_target), task_list["changelog"][1])

        CMD_gzip = paths.getExecutable("gzip")

        if CMD_gzip:
          UpdateProgress(progress, GT("Compressing changelog"))
          res = subprocess.run([CMD_gzip, "-n", "--best", "{}/changelog".format(changelog_target)], stdout=subprocess.PIPE)
          if res.returncode != 0:
            ShowErrorDialog(GT("Could not compress changelog"), res.stdout.decode("utf-8"), warn=True, title=GT("Warning"))

        progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # *** Copyright *** #
      if create_copyright:
        UpdateProgress(progress, GT("Creating copyright"))

        fileio.writeFile("{}/usr/share/doc/{}/copyright".format(stage_dir, package), task_list["copyright"])

        progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # Characters that should not be in filenames
      invalid_chars = (" ", "/", "\\")

      # *** Menu launcher *** #
      if "launcher" in task_list:
        UpdateProgress(progress, GT("Creating menu launcher"))

        # This might be changed later to set a custom directory
        menu_dir = "{}/usr/share/applications".format(stage_dir)

        menu_filename = pg_menu.GetOutputFilename()

        # Remove invalid characters from filename
        for char in invalid_chars:
          menu_filename = menu_filename.replace(char, "_")

        if not os.path.isdir(menu_dir):
          os.makedirs(menu_dir)

        fileio.writeFile("{}/{}.desktop".format(menu_dir, menu_filename), task_list["launcher"])

        progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # *** md5sums file *** #
      # Good practice to create hashes before populating DEBIAN directory
      if "md5sums" in task_list:
        UpdateProgress(progress, GT("Creating md5sums"))

        if not WriteMD5(stage_dir, parent=build_progress):
          # Couldn't call md5sum command
          build_progress.Cancel()

        progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # *** Scripts *** #
      if "scripts" in task_list:
        UpdateProgress(progress, GT("Creating scripts"))

        scripts = task_list["scripts"]
        for SCRIPT in scripts:
          script_name = SCRIPT
          script_text = scripts[SCRIPT]

          script_filename = os.path.join(stage_dir, "DEBIAN", script_name)

          fileio.writeFile(script_filename, script_text)

          os.chmod(script_filename, 0o0775)

          # Individual scripts
          progress += 1
          UpdateProgress(progress)

        # Entire script task
        progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # *** Control file *** #
      UpdateProgress(progress, GT("Getting installed size"))

      # Get installed-size
      installed_size = os.popen(("du -hsk \"{}\"".format(stage_dir))).readlines()
      installed_size = installed_size[0].split("\t")
      installed_size = installed_size[0]

      # Insert Installed-Size into control file
      control_data = pg_control.Get().split("\n")
      control_data.insert(2, "Installed-Size: {}".format(installed_size))

      progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # Create final control file
      UpdateProgress(progress, GT("Creating control file"))

      # dpkg fails if there is no newline at end of file
      control_data = "\n".join(control_data).strip("\n")
      # Ensure there is only one empty trailing newline
      # Two '\n' to show physical empty line, but not required
      # Perhaps because string is not null terminated???
      control_data = "{}\n\n".format(control_data)

      fileio.writeFile("{}/DEBIAN/control".format(stage_dir), control_data)

      progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # *** Final build *** #
      UpdateProgress(progress, GT("Running dpkg"))

      working_dir = os.path.split(stage_dir)[0]
      c_tree = os.path.split(stage_dir)[1]
      deb_package = "{}.deb".format(filename)

      # Move the working directory because dpkg seems to have problems with spaces in path
      os.chdir(working_dir)

      if "permiss" in task_list:
        UpdateProgress(progress, GT("Cleaning up file permissions"))
        for ROOT, DIRS, FILES in os.walk(stage_dir):
          for D in DIRS:
            D = "{}/{}".format(ROOT, D)
            os.chmod(D, 0o755)
          for F in FILES:
            F = "{}/{}".format(ROOT, F)
            if os.access(F, os.X_OK):
              os.chmod(F, 0o755)
            else:
              os.chmod(F, 0o644)
        progress += 1

      # FIXME: Should check for working fakeroot & dpkg-deb executables
      res = subprocess.run([paths.getExecutable("fakeroot"), paths.getExecutable("dpkg-deb"), "-b", c_tree, deb_package],
          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      build_status = (res.returncode, res.stdout.decode("utf-8"))

      progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # *** Delete staged directory *** #
      if "rmstage" in task_list:
        UpdateProgress(progress, GT("Removing temp directory"))

        try:
          shutil.rmtree(stage_dir)

        except OSError:
          ShowErrorDialog(GT("An error occurred when trying to delete the build tree"),
              parent=build_progress)

        progress += 1

      if build_progress.WasCancelled():
        build_progress.Destroy()
        return (dbrerrno.ECNCLD, None)

      # *** ERROR CHECK
      if "lintian" in task_list:
        UpdateProgress(progress, GT("Checking package for errors"))

        # FIXME: Should be set as class member?
        CMD_lintian = paths.getExecutable("lintian")
        err, msg = libdbr.bin.execute(CMD_lintian, "--no-tag-display-limit", deb, usestderr=True)

        if logger.debugging():
          logger.debug("lintian result: {}".format(err))
          print(msg)

        if not strings.isEmpty(msg):
          e1 = GT("Lintian found some issues with the package.")
          e2 = GT("Details saved to {}").format(filename)

          fileio.writeFile("{}/{}.lintian".format(build_path, filename), msg)

          DetailedMessageDialog(build_progress, GT("Lintian Errors"),
              ICON_INFORMATION, "{}\n{}.lintian".format(e1, e2), msg).ShowModal()

        progress += 1

      # Close progress dialog
      wx.GetApp().Yield()
      build_progress.Update(progress)
      build_progress.Destroy()

      # Build completed successfully
      if not build_status[0]:
        return (dbrerrno.SUCCESS, deb_package)

      if PY_VER_MAJ <= 2:
        # Unicode decoder has trouble with certain characters. Replace any
        # non-decodable characters with � (0xFFFD).
        build_output = list(build_status[1])

        # String & unicode string incompatibilities
        index = 0
        for C in build_output:
          try:
            strings.toString(C)

          except UnicodeDecodeError:
            build_output[index] = "�"

          index += 1

        build_status = (build_status[0], "".join(build_output))

      # Build failed
      return (build_status[0], build_status[1])

    except:
      if build_progress:
        build_progress.Destroy()

      return(dbrerrno.EUNKNOWN, traceback.format_exc())

  ## @todo Doxygen
  #
  #  @return
  #    \b \e tuple containing Return code & build details
  def BuildPrep(self):
    # Declare these here in case of error before dialogs created
    save_dia = None
    prebuild_progress = None

    try:
      # List of tasks for build process
      # 'stage' should be very first task
      task_list = {}

      # Control page
      pg_control = ui.app.getPage(pgid.CONTROL)
      fld_package = GetField(pg_control, inputid.PACKAGE)
      fld_version = GetField(pg_control, inputid.VERSION)
      fld_maint = GetField(pg_control, inputid.MAINTAINER)
      fld_email = GetField(pg_control, inputid.EMAIL)
      fields_control = (
        fld_package,
        fld_version,
        fld_maint,
        fld_email,
        )

      # Check to make sure that all required fields have values
      required = list(fields_control)

      # files page
      pg_files = ui.app.getPage(pgid.FILES)
      if not pg_files.isOkay():
        return (pg_files.getError())

      # Menu launcher page
      pg_launcher = ui.app.getPage(pgid.MENU)
      if pg_launcher.IsOkay():
        task_list["launcher"] = pg_launcher.Get()

        required.append(GetField(pg_launcher, inputid.NAME))

        if not GetField(pg_launcher, chkid.FNAME).GetValue():
          required.append(GetField(pg_launcher, inputid.FNAME))

      for item in required:
        if strings.isEmpty(item.GetValue()):
          field_name = GT(item.GetName().title())
          page_name = pg_control.GetName()
          if item not in fields_control:
            page_name = pg_launcher.GetName()
          return (dbrerrno.FEMPTY, "{} ➜ {}".format(page_name, field_name))

      # Get information from control page for default filename
      package = fld_package.GetValue()
      # Remove whitespace
      package = package.strip(" \t")
      package = "-".join(package.split(" "))

      version = fld_version.GetValue()
      # Remove whitespace
      version = version.strip(" \t")
      version = "".join(version.split())

      arch = GetField(pg_control, inputid.ARCH).GetStringSelection()

      # Dialog for save destination
      ttype = GT("Debian packages")
      save_dia = wx.FileDialog(self, GT("Save"), os.getcwd(), wx.EmptyString, "{}|*.deb".format(ttype),
          wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
      save_dia.SetFilename("{}_{}_{}.deb".format(package, version, arch))
      if not save_dia.ShowModal() == wx.ID_OK:
        return (dbrerrno.ECNCLD, None)

      build_path = os.path.split(save_dia.GetPath())[0]
      filename = os.path.split(save_dia.GetPath())[1].split(".deb")[0]

      # Control, menu, & build pages not added to this list
      page_checks = (
        (pgid.FILES, "files"),
        (pgid.SCRIPTS, "scripts"),
        (pgid.CHANGELOG, "changelog"),
        (pgid.COPYRIGHT, "copyright"),
        )

      # Install step is not added to this list
      # 'control' should be after 'md5sums'
      # 'build' should be after 'control'
      other_checks = (
        (self.chk_md5, "md5sums"),
        (self.chk_strip, "strip"),
        (self.chk_permiss, "permiss"),
        (self.chk_rmstage, "rmstage"),
        (self.chk_lint, "lintian"),
        )

      prep_task_count = len(page_checks) + len(other_checks)

      progress = 0

      wx.GetApp().Yield()
      prebuild_progress = ProgressDialog(ui.app.getMainWindow(), GT("Preparing to build"),
          maximum=prep_task_count)

      if wx.MAJOR_VERSION < 3:
        # Resize dialog for better fit
        pb_size = prebuild_progress.GetSize().Get()
        pb_size = (pb_size[0]+200, pb_size[1])
        prebuild_progress.SetSize(pb_size)
        prebuild_progress.CenterOnParent()

      for PID, id_string in page_checks:
        wx.GetApp().Yield()
        prebuild_progress.Update(progress, GT("Checking {}").format(id_string))

        wizard_page = ui.app.getPage(PID)
        if wizard_page.IsOkay():
          task_list[id_string] = wizard_page.Get()
        progress += 1

      for task_check, id_string in other_checks:
        wx.GetApp().Yield()
        prebuild_progress.Update(progress, GT("Testing for: {}").format(task_check.GetLabel()))
        if task_check.GetValue():
          task_list[id_string] = None
        progress += 1

      # Close progress dialog
      wx.GetApp().Yield()
      prebuild_progress.Update(progress)
      prebuild_progress.Destroy()

      return (dbrerrno.SUCCESS, (task_list, build_path, filename))

    except:
      if save_dia:
        save_dia.Destroy()
      if prebuild_progress:
        prebuild_progress.Destroy()
      return (dbrerrno.EUNKNOWN, traceback.format_exc())

  ## @todo Doxygen
  def GetSaveData(self):
    return None
    # ~ build_list = []

    # ~ options = (
      # ~ self.chk_md5,
      # ~ self.chk_rmstage,
      # ~ self.chk_lint,
      # ~ )

    # ~ for O in options:
      # ~ if O.GetValue():
        # ~ build_list.append("1")
      # ~ else:
        # ~ build_list.append("0")

    # ~ if self.chk_strip.GetValue():
      # ~ build_list.append("strip")

    # ~ return "<<BUILD>>\n{}\n<</BUILD>>".format("\n".join(build_list))

  ## @override ui.page.Page.toString
  def toString(self):
    return self.GetSaveData()

  ## Installs the built .deb package onto the system
  #
  #  Uses the system's package installer:
  #  gdebi if available or dpkg
  #
  #  Shows a success dialog if installed. Otherwise shows an
  #  error dialog.
  #
  #  @param package
  #    \b \e str : Path to package to be installed
  def InstallPackage(self, package):
    system_installer = globals.execute.getDebInstaller()

    if not system_installer:
      ShowErrorDialog(
        GT("Cannot install package"),
        GT("A compatible package manager could not be found on the system"),
        __name__,
        warn=True
        )
      return

    logger.info(GT("Attempting to install package: {}").format(package))
    logger.info(GT("Installing with {}").format(system_installer))

    wx.GetApp().Yield()
    err, install_output = libdbr.bin.execute(system_installer, package)

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
        GT("Command executed: {} {}").format(system_installer, package),
        )

      ShowErrorDialog(
        GT("An error occurred during installation"),
        "\n".join(err_details),
        __name__
        )
      return

  ## @todo Doxygen
  def OnBuild(self, event=None):
    # Build preparation
    ret_code, build_prep = self.BuildPrep()

    if ret_code == dbrerrno.ECNCLD:
      return

    if ret_code == dbrerrno.FEMPTY:
      err_dia = DetailedMessageDialog(ui.app.getMainWindow(), GT("Cannot Continue"), ICON_EXCLAMATION,
          text="{}\n{}".format(GT("One of the required fields is empty:"), build_prep))
      err_dia.ShowModal()
      err_dia.Destroy()
      return

    if ret_code == dbrerrno.SUCCESS:
      task_list, build_path, filename = build_prep

      # Actual build
      ret_code, result = self.Build(task_list, build_path, filename)

      # FIXME: Check .deb package timestamp to confirm build success
      if ret_code == dbrerrno.SUCCESS:
        DetailedMessageDialog(ui.app.getMainWindow(), GT("Success"), ICON_INFORMATION,
            text=GT("Package created successfully")).ShowModal()

        # Installing the package
        if FieldEnabled(self.chk_install) and self.chk_install.GetValue():
          self.InstallPackage(result)
        return

      if result:
        ShowErrorDialog(GT("Package build failed"), result)
      else:
        ShowErrorDialog(GT("Package build failed with unknown error"))
      return

    if build_prep:
      ShowErrorDialog(GT("Build preparation failed"), build_prep)
    else:
      ShowErrorDialog(GT("Build preparation failed with unknown error"))

  ## @todo Doxygen
  #
  #  @todo
  #    - Show warning dialog that this could take a while
  #    - Add cancel option to progress dialog
  #    - FIXME: List should be cached so no need for re-scanning
  def OnSetLintOverrides(self, event=None):
    logger.debug(GT("Setting Lintian overrides..."))
    lintian_tags_file = "{}/data/lintian/tags".format(paths.getAppDir())
    # ~ if not os.path.isfile(lintian_tags_file):
      # ~ logger.error("Lintian tags file is missing: {}".format(lintian_tags_file))
      # ~ return False

    # ~ lint_tags = RemoveEmptyLines(fileio.readFile(lintian_tags_file).split("\n"))
    lint_tags = self.__getLintianTags()
    if lint_tags:
      logger.debug("Lintian tags set")

      # DEBUG: Start
      if logger.debugging() and len(lint_tags) > 50:
        print("  Reducing tag count to 200 ...")

        lint_tags = lint_tags[:50]

      logger.debug("Processing {} tags".format(len(lint_tags)))
      # DEBUG: End

      tag_count = len(lint_tags)

      def GetProgressMessage(message, count=tag_count):
        return "{} ({} {})".format(message, count, GT("tags"))

      progress = TimedProgressDialog(ui.app.getMainWindow(), GT("Building Tag List"),
          GetProgressMessage(GT("Scanning default tags")))
      progress.Start()

      wx.GetApp().Yield()

      # Create the dialog
      overrides_dialog = CheckListDialog(ui.app.getMainWindow(), title=GT("Lintian Overrides"),
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
          logger.debug(GT("Adding Lintian override: {}").format(L))
          self.lint_overrides.append(L)
      return True
    else:
      logger.debug("Setting lintian tags failed")
      return False

  ## @todo Doxygen
  def Set(self, data):
    pass
    # ~ # ???: Redundant
    # ~ self.Reset()
    # ~ build_data = data.split("\n")

    # ~ if paths.getExecutable("md5sum"):
      # ~ try:
        # ~ self.chk_md5.SetValue(int(build_data[0]))
      # ~ except IndexError:
        # ~ pass

    # ~ try:
      # ~ self.chk_rmstage.SetValue(int(build_data[1]))
    # ~ except IndexError:
      # ~ pass

    # ~ if paths.getExecutable("lintian"):
      # ~ try:
        # ~ self.chk_lint.SetValue(int(build_data[2]))
      # ~ except IndexError:
        # ~ pass

    # ~ self.chk_strip.SetValue(paths.getExecutable("strip") and "strip" in build_data)

  ## @todo Doxygen
  def SetSummary(self, event=None):
    pg_scripts = ui.app.getPage(pgid.SCRIPTS)

    # Make sure the page is not destroyed so no error is thrown
    if self:
      # Set summary when "Build" page is shown
      # Get the file count
      files_total = ui.app.getPage(pgid.FILES).GetFileCount()
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

  ## @override ui.page.Page.reset
  def reset(self):
    pass

  def __getLintianTags(self):
    l_tags = []
    file_tags = paths.join(globals.paths.getCacheDir(), "lintian_tags")
    if os.path.isfile(file_tags):
      for tag in fileio.readFile(file_tags).split("\n"):
        tag = tag.strip()
        if tag:
          l_tags.append(tag)
    return l_tags
