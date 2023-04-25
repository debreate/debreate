
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.quickbuild

import os
import traceback

import wx

from dbr.event            import EVT_TIMER_STOP
from dbr.functions        import BuildDebPackage
from dbr.language         import GT
from dbr.timer            import DebreateTimer
from globals              import threads
from globals              import tooltips
from globals.errorcodes   import dbrerrno
from libdbr.fileio        import readFile
from libdbr.logger        import Logger
from libdebreate.ident    import btnid
from ui.button            import CreateButton
from ui.dialog            import GetDirDialog
from ui.dialog            import GetFileSaveDialog
from ui.dialog            import OverwriteDialog
from ui.dialog            import ShowDialog
from ui.dialog            import ShowErrorDialog
from ui.dialog            import ShowMessageDialog
from ui.layout            import BoxSizer
from ui.style             import layout as lyt


logger = Logger(__name__)
GAUGE_MAX = 100

## A dialog that takes a pre-formatted directory tree & creates a .deb package
class QuickBuild(wx.Dialog):
  def __init__(self, parent):
    wx.Dialog.__init__(self, parent, title=GT("Quick Build"), pos=wx.DefaultPosition,
        size=wx.Size(400,260))
    self.title = self.GetTitle()

    # track build status
    self.__status = None
    # build thread ID
    self.__thread_id = None

    label_stage = wx.StaticText(self, label=GT("Staged directory tree"))
    self.input_stage = wx.TextCtrl(self)
    tooltips.register(self.input_stage, GT("Root directory of build tree"))

    btn_browse_stage = CreateButton(self, btnid.STAGE, image="browse")
    btn_browse_stage.Bind(wx.EVT_BUTTON, self.OnBrowse)

    label_target = wx.StaticText(self, label=GT("Target file"))
    self.input_target = wx.TextCtrl(self)
    tooltips.register(self.input_target, GT("Target output file"))

    btn_browse_target = CreateButton(self, btnid.TARGET, image="browse")
    btn_browse_target.Bind(wx.EVT_BUTTON, self.OnBrowse)

    btn_build = CreateButton(self, btnid.BUILD)
    tooltips.register(btn_build, GT("Start building"))
    btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)

    btn_cancel = CreateButton(self, btnid.EXIT)
    tooltips.register(btn_cancel, GT("Close dialog"))
    btn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)

    self.gauge = wx.Gauge(self, GAUGE_MAX)

    self.timer = DebreateTimer(self)
    self.Bind(wx.EVT_TIMER, self.OnUpdateProgress)
    self.Bind(EVT_TIMER_STOP, self.OnTimerStop)

    # *** Layout *** #

    Lstage_V1 = BoxSizer(wx.VERTICAL)
    Lstage_V1.Add(label_stage, 0, wx.ALIGN_LEFT)
    Lstage_V1.Add(self.input_stage, 1, wx.EXPAND)

    Lstage_H1 = BoxSizer(wx.HORIZONTAL)
    Lstage_H1.Add(Lstage_V1, 3, wx.ALIGN_TOP)
    Lstage_H1.Add(btn_browse_stage, 0, wx.ALIGN_TOP|wx.TOP, 7)

    Ltarget_V1 = BoxSizer(wx.VERTICAL)
    Ltarget_V1.Add(label_target, 0, wx.ALIGN_LEFT)
    Ltarget_V1.Add(self.input_target, 1, wx.EXPAND)

    Ltarget_H1 = BoxSizer(wx.HORIZONTAL)
    Ltarget_H1.Add(Ltarget_V1, 3, wx.ALIGN_TOP)
    Ltarget_H1.Add(btn_browse_target, 0, wx.ALIGN_TOP|wx.TOP, 7)

    Lbtn_H1 = BoxSizer(wx.HORIZONTAL)
    Lbtn_H1.Add(btn_build, 1, wx.ALIGN_BOTTOM|wx.RIGHT, 2)
    Lbtn_H1.Add(btn_cancel, 1, wx.ALIGN_BOTTOM|wx.LEFT, 2)

    Lguage_H1 = BoxSizer(wx.HORIZONTAL)
    Lguage_H1.Add(self.gauge, 1, lyt.PAD_LR, 5)

    Lmain_V = BoxSizer(wx.VERTICAL)
    Lmain_V.AddSpacer(1)
    Lmain_V.Add(Lstage_H1, -1, wx.EXPAND|lyt.PAD_LR, 5)
    Lmain_V.Add(Ltarget_H1, -1, wx.EXPAND|lyt.PAD_LR, 5)
    Lmain_V.Add(Lbtn_H1, -1, wx.ALIGN_CENTER|wx.ALL, 5)
    Lmain_V.Add(Lguage_H1, -1, wx.EXPAND|wx.ALL, 5)
    Lmain_V.AddSpacer(1)

    self.SetAutoLayout(True)
    self.SetSizer(Lmain_V)
    self.Layout()

    self.Bind(wx.EVT_CLOSE, self.OnClose)

    self.CenterOnParent()

    # For showing error dialog after build thread exits
    self.build_error = None

  ## Build process is done in background thread
  #
  #  @param stage
  #    Location of the source formatted directory tree
  #  @param target
  #    Absolute output target filename
  def Build(self, stage, target):
    self.__status = (0, GT("errors"))

    try:
      output = BuildDebPackage(stage, target)
      if output[0] == dbrerrno.SUCCESS:
        self.__status = (GAUGE_MAX, GT("finished"))

      else:
        self.build_error = (
          GT("Could not build .deb package"),
          GT("Is the staged directory formatted correctly?"),
          stage,
          output[1],
        )

    except:
      self.build_error = (
        GT("An unhandled error occurred"),
        traceback.format_exc(),
        )

    self.timer.Stop()

  ## Opens directory stage for target & file save dialog for target
  def OnBrowse(self, event=None):
    if event:
      button_id = event.GetEventObject().GetId()
      if button_id == btnid.STAGE:
        stage = GetDirDialog(self, GT("Choose Directory"))
        if (ShowDialog(stage)):
          self.input_stage.SetValue(stage.GetPath())
      elif button_id == btnid.TARGET:
        target = GetFileSaveDialog(self, GT("Choose Filename"), (GT("Debian packages"), "*.deb",),
            "deb")
        if (ShowDialog(target)):
          self.input_target.SetValue(target.GetPath())

  ## Checks & preps when build button is pressed
  #
  #  @todo Check timestamp of created .deb package (should be done for main build as well)
  def OnBuild(self, event=None):
    stage = self.input_stage.GetValue()
    target = self.input_target.GetValue().rstrip(os.sep)

    # Attempt to use DEBIAN/control file to set output filename. This is normally
    # done automatically by the dpkg command, but we need to set it manually to
    # check for overwriting a file.
    if os.path.isdir(target):
      control_file = os.path.join(stage, "DEBIAN", "control")
      if os.path.isfile(control_file):
        control_lines = readFile(control_file).split("\n")

        name = None
        version = None
        arch = None

        for LINE in control_lines:
          if LINE.startswith("Package:"):
            name = LINE.replace("Package: ", "").strip()
          elif LINE.startswith("Version:"):
            version = LINE.replace("Version: ", "").strip()
          elif LINE.startswith("Architecture:"):
            arch = LINE.replace("Architecture: ", "").strip()

        if name and version and arch:
          target = os.path.join(target, "{}.deb".format("_".join((name, version, arch))))

    # Automatically add .deb filename extension if not present
    elif not target.lower().endswith(".deb"):
      target = "{}.deb".format(target)

    if not os.path.isdir(stage):
      ShowErrorDialog(GT("Stage directory does not exist"), stage, self, True)
      return

    target_path = os.path.dirname(target)
    if not os.path.isdir(target_path):
      ShowErrorDialog(GT("Target directory does not exist"), target_path, self, True)
      return

    elif not os.access(target_path, os.W_OK):
      ShowErrorDialog(GT("No write access to target directory"), target_path, self, True)
      return

    # Update the text input if target altered
    if target != self.input_target.GetValue():
      self.input_target.SetValue(target)

    # Check for pre-existing file
    if os.path.isfile(target):
      dia = OverwriteDialog(self, target)
      res = dia.Confirmed()
      # ensure dialog does not persist
      dia.Destroy()
      if not res:
        return

    self.SetTitle("{} ({})".format(self.title, GT("in progress")))

    # Don't allow dialog to be closed while build in progress
    self.Disable()
    self.timer.Start(100)

    # Start new thread for background process
    self.__thread_id = threads.create(self.Build, stage, target)

  ## Closes the Quick Build dialog & destroys instance
  def OnClose(self, event=None):
    self.EndModal(True)

  ## Closes the progress dialog & shows status message when timer is stopped
  def OnTimerStop(self, event=None):
    logger.debug("OnTimerStop")
    if not self.timer.IsRunning():
      logger.debug(GT("Timer is stopped"))
    else:
      logger.debug(GT("Timer is running"))

    # remove thread ID from active list
    threads.end(self.__thread_id)
    self.Enable()
    if self.__status:
      self.gauge.SetValue(self.__status[0])
      self.SetTitle("{} ({})".format(self.title, self.__status[1]))
      # reset status tracker
      self.__status = None

    if self.build_error:
      error_lines = self.build_error[:-1]
      error_output = self.build_error[-1]

      ShowErrorDialog(error_lines, error_output, self)

      # Needs to be reset or error dialog will successively show
      self.build_error = None

      return

    msg_lines = (
      GT("Quick build complete"),
      self.input_target.GetValue(),
      )

    ShowMessageDialog(msg_lines, GT("Build Complete"), module=__name__)

  ## Updates the progress bar
  def OnUpdateProgress(self, event=None):
    if event:
      if isinstance(event, wx.TimerEvent):
        if not self.timer.IsRunning():
          logger.debug(GT("Timer stopped. Stopping gauge ..."))
          return
    self.gauge.Pulse()
