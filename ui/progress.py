
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.progress

import wx

import ui.app

from dbr.event     import EVT_TIMER_STOP
from dbr.language  import GT
from dbr.timer     import DebreateTimer
from libdbr.logger import Logger
from ui.helper     import FieldEnabled


logger = Logger(__name__)
PD_DEFAULT_STYLE = wx.PD_APP_MODAL|wx.PD_AUTO_HIDE

## A progress dialog that is compatible between wx versions
class ProgressDialog(wx.ProgressDialog):
  def __init__(self, parent, title=GT("Progress"), message=wx.EmptyString, size=None, maximum=100,
      style=PD_DEFAULT_STYLE, detailed=False, resize=True):
    wx.ProgressDialog.__init__(self, title, message, maximum, parent, style)

    self.resize = resize
    self.active = None

    if wx.MAJOR_VERSION < 3 and self.GetWindowStyle() & wx.PD_CAN_ABORT:
      wx.EVT_CLOSE(self, self.OnAbort)
      for C in self.GetChildren():
        if isinstance(C, wx.Button) and C.GetId() == wx.ID_CANCEL:
          C.Bind(wx.EVT_BUTTON, self.OnAbort)

    if size:
      self.SetSize(size)

    self.detailed = detailed
    self.txt_tasks = None
    if detailed:
      lyt_main = self.GetSizer()

      self.txt_tasks = wx.StaticText(self, label="{} / {}".format(0, maximum))

      children = self.GetChildren()

      t_index = None
      for X in children:
        if isinstance(X, wx.StaticText):
          t_index = children.index(X)
          #lyt_main.Detach(X)
          break

      if t_index != None:
        lyt_main.Insert(t_index+1, self.txt_tasks, 0, wx.ALIGN_CENTER|wx.TOP, 5)
        lyt_main.Layout()

        dimensions_original = self.GetSize().Get()

        self.Fit()

        dimensions_new = self.GetSize().Get()

        # Preserve original width
        self.SetSize(wx.Size(dimensions_original[0], dimensions_new[1]))
        wx.GetApp().Yield()

    if parent:
      self.CenterOnParent()

    # Find the initial position to test if dialog has been moved by user
    self.initial_posY = self.GetPosition().Get()[1]

    self.user_moved = False

  ## Sets the active status to False
  #
  #  Calls ui.progress.ProgressDialog.OnAbort
  def Cancel(self):
    self.OnAbort()

  ## Closes & destroys the dialog
  #
  #  Method for compatibility between wx 3.0 & older versions
  #  For 3.0 & newer, simply overrides wx.ProgressDialog.Destroy
  #  For older versions, calls ui.progress.ProgressDialog.EndModal
  def Destroy(self, *args, **kwargs):
    # Re-enable parent/main window if previously disabled
    # ???: May not be necessary
    main_window = ui.app.getMainWindow()

    if not FieldEnabled(main_window):
      logger.debug("Re-enabling main window")
      main_window.Enable()

    if self.Parent and not FieldEnabled(self.Parent):
      logger.debug("Re-enabling parent")
      self.GetParent().Enable()

    if wx.MAJOR_VERSION < 3:
      self.EndModal(0)

    return wx.ProgressDialog.Destroy(self, *args, **kwargs)

  ## Retrieves the wx.Gauge child object
  #
  #  Mostly for compatibility with wx versions older than 3.0
  #  Older versions do not have many of methods for access & manipulation of the gauge
  def GetGauge(self):
    for C in self.GetChildren():
      if isinstance(C, wx.Gauge):
        return C

  ## Retrieves the message shown on the dialog
  #
  #  Method for compatibility between wx 3.0 & older versions
  #  For wx 3.0 & newer, simply overrides wx.ProgressDialog.GetMessage
  #  For older versions, finds the child wx.StaticText object & returns the label
  def GetMessage(self, *args, **kwargs):
    if wx.MAJOR_VERSION < 3:
      for C in self.GetChildren():
        if isinstance(C, wx.StaticText):
          return C.GetLabel()
      return
    return wx.ProgressDialog.GetMessage(self, *args, **kwargs)

  ## Retrieves the range, or maximum value of the gauge
  #
  #  Method for compatibility between wx 3.0 & older versions
  #  For 3.0 & newer, simply overrides wx.ProgressDialog.GetRange
  #  For older versions, calls GetRange on the child gauge object
  def GetRange(self, *args, **kwargs):
    if wx.MAJOR_VERSION < 3:
      return self.GetGauge().GetRange()
    return wx.ProgressDialog.GetRange(self, *args, **kwargs)

  ## Retrieves the current value of the gauge
  #
  #  Method for compatibility between wx 3.0 & older versions
  #  for 3.0 & newer, simply overrides wx.ProgressDialog.GetValue
  #  For older versions, calls GetValue() on the child wx.Gauge object
  def GetValue(self, *args, **kwargs):
    if wx.MAJOR_VERSION < 3:
      return self.GetGauge().GetValue()
    return wx.ProgressDialog.GetValue(self, *args, **kwargs)

  ## Sets the active status to False
  #
  #  The dialog will be destroyed when ui.progress.ProgressDialog.WasCancelled is called
  def OnAbort(self, event=None):
    self.active = False
    if event:
      event.Skip()

  ## @todo Doxygen
  def Pulse(self, *args, **kwargs):
    pulse_value = wx.ProgressDialog.Pulse(self, *args, **kwargs)
    if self.resize:
      self.UpdateSize()
    return pulse_value

  ## @todo Doxygen
  def SetMessage(self, message):
    for C in self.GetChildren():
      if isinstance(C, wx.StaticText):
        return C.SetLabel(message)
    return False

  ## @todo Doxygen
  def SetRange(self, *args, **kwargs):
    if wx.MAJOR_VERSION < 3:
      return self.GetGauge().SetRange(*args, **kwargs)
    return wx.ProgressDialog.SetRange(self, *args, **kwargs)

  ## @todo Doxygen
  def ShowModal(self, *args, **kwargs):
    if wx.MAJOR_VERSION < 3:
      self.active = True
    return wx.ProgressDialog.ShowModal(self, *args, **kwargs)

  ## @todo Doxygen
  def Update(self, *args, **kwargs):
    update_value = wx.ProgressDialog.Update(self, *args, **kwargs)
    if self.detailed:
      self.txt_tasks.SetLabel("{} / {}".format(args[0], self.GetRange()))
    if self.resize:
      self.UpdateSize()
    return update_value

  ## Currently only updates width
  #
  #  @todo
  #    - FIXME: Window updates immediately, but children do not
  #    - FIXME: Dialog could potentially resize outsize of display boundaries
  def UpdateSize(self):
    if not self.user_moved:
      if self.GetPosition().Get()[1] != self.initial_posY:
        self.user_moved = True

    resize = True
    size = self.GetSize().Get()
    parent = self.GetParent()

    if parent:
      # Don't resize if dialog is already as big or bigger than parent
      if size[0] >= parent.GetSize().Get()[0]:
        resize = False

    if resize:
      children = self.GetChildren()
      target_width = 0

      for C in children:
        child_width = C.GetSize().Get()[0]
        if child_width > target_width:
          target_width = child_width

      if children:
        padding_x = children[0].GetPosition().Get()[0]

        # Add padding
        target_width += (padding_x * 2)

        if target_width > size[0]:
          self.SetSize((target_width, size[1]))

          # Only center on parent if user did not move dialog manually
          # FIXME: Only works if dialog is moved vertically
          if parent and not self.user_moved:
            self.CenterOnParent()

      sizer = self.GetSizer()
      if sizer:
        sizer.Layout()
      else:
        self.Layout()

  ## Override wx.ProgressDialog.WasCancelled method for compatibility wx older wx versions
  def WasCancelled(self, *args, **kwargs):
    if wx.MAJOR_VERSION < 3:
      if self.active == None:
        return False
      return not self.active

    # Failsafe for compatibility between wx 3.0 & older versions
    if self.active == False:
      return True

    return wx.ProgressDialog.WasCancelled(self, *args, **kwargs)

## A progress dialog that uses a time
#
#  @todo Finish defining
class TimedProgressDialog(ProgressDialog):
  def __init__(self, parent, title=GT("Progress"), message=wx.EmptyString, size=None, maximum=100,
      style=PD_DEFAULT_STYLE, detailed=False, resize=True, interval=100):
    ProgressDialog.__init__(self, parent, title, message, size, maximum, style, detailed, resize)

    self.Timer = DebreateTimer(self)
    self.Interval = interval

    self.MessageCtrl = None
    for CHILD in self.GetChildren():
      if isinstance(CHILD, wx.TextCtrl):
        self.MessageCtrl = CHILD
        break

    # *** Event Handling *** #

    self.Bind(wx.EVT_TIMER, self.OnTimerPulse)
    self.Bind(EVT_TIMER_STOP, self.OnTimerStop)

  ## Retrievers timer instance
  def GetTimer(self):
    return self.Timer

  ## Pulses dialog on timer event
  def OnTimerPulse(self, event=None):
    self.Pulse()

  ## @todo Doxygen
  def OnTimerStop(self, event=None):
    logger.debug("Destroying TimedProgressDialog instance")
    if wx.MAJOR_VERSION <= 2:
      # Dialog needs to be closed before destroying for wx 2.8
      self.Close()
    self.Destroy()

  ## Starts the timer & begins pulsing dialog
  def Start(self):
    logger.debug("Starting TimedProgressDialog timer ...")
    self.Timer.Start(self.Interval)

  ## Stops the timer & destroys the progress dialog
  def Stop(self):
    logger.debug("Stopping TimedProgressDialog timer ...")
    self.Timer.Stop()
