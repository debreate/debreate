
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.logwindow

import os
import time
import traceback

import wx

import ui.app

from dbr.event         import EVT_REFRESH_LOG
from dbr.event         import RefreshLogEvent
from dbr.language      import GT
from globals           import bitmaps
from globals           import paths
from globals           import threads
from globals.fileitem  import FileItem
from input.text        import TextAreaPanel
from libdbr            import strings
from libdbr.logger     import Logger
from libdebreate.ident import btnid
from libdebreate.ident import menuid
from ui.button         import CreateButton
from ui.dialog         import GetFileOpenDialog
from ui.dialog         import ShowDialog
from ui.dialog         import ShowErrorDialog
from ui.font           import GetMonospacedFont
from ui.layout         import BoxSizer


_logger = Logger(__name__)

# How often the log window will be refreshed
LOG_WINDOW_REFRESH_INTERVAL = 1


## @todo Doxygen
def SetLogWindowRefreshInterval(value):
  global LOG_WINDOW_REFRESH_INTERVAL
  LOG_WINDOW_REFRESH_INTERVAL = value


## @todo Doxygen
def GetLogWindowRefreshInterval():
  return LOG_WINDOW_REFRESH_INTERVAL


## Window displaying Logger messages
#
#  @param parent
#    Parent \b \e wx.Window instance
#  @param logFile
#    Absolute path to file where log contents are written/read
class LogWindow(wx.Dialog):
  def __init__(self, parent, logFile):
    wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

    self.SetIcon(wx.Icon(bitmaps.LOGO, wx.BITMAP_TYPE_PNG))

    self.LogFile = FileItem(logFile)
    self.SetTitle()

    self.thread_id = threads.create(self.PollLogFile, start=False)

    self.DspLog = TextAreaPanel(self, style=wx.TE_READONLY)
    self.DspLog.font_size = 8
    self.DspLog.SetFont(GetMonospacedFont(self.DspLog.font_size))

    btn_open = CreateButton(self, btnid.BROWSE, GT("Open and Display Log File"), "browse")
    btn_font = CreateButton(self, btnid.ZOOM, GT("Zoom Text"), "zoom")
    btn_refresh = CreateButton(self, btnid.REFRESH, GT("Refresh"), "refresh")
    btn_hide = CreateButton(self, btnid.CLOSE, GT("Hide"), "hide")

    # *** Event Handling *** #

    EVT_REFRESH_LOG(self, wx.ID_ANY, self.OnLogTimestampChanged)

    wx.EVT_BUTTON(self, btnid.BROWSE, self.OnOpenLogFile)
    wx.EVT_BUTTON(self, btnid.ZOOM, self.OnChangeFont)
    wx.EVT_BUTTON(self, btnid.REFRESH, self.RefreshLog)
    wx.EVT_BUTTON(self, btnid.CLOSE, self.OnClose)

    wx.EVT_CLOSE(self, self.OnClose)
    wx.EVT_SHOW(self, self.OnShow)
    wx.EVT_SHOW(ui.app.getMainWindow(), self.OnShowMainWindow)

    # *** Layout *** #

    layout_btnF1 = wx.FlexGridSizer(cols=5)
    layout_btnF1.AddGrowableCol(1, 1)
    layout_btnF1.Add(btn_open, 0, wx.LEFT, 5)
    layout_btnF1.AddStretchSpacer(1)
    layout_btnF1.Add(btn_font, 0, wx.RIGHT, 5)
    layout_btnF1.Add(btn_refresh, 0, wx.RIGHT, 5)
    layout_btnF1.Add(btn_hide, 0, wx.RIGHT, 5)

    layout_mainV1 = BoxSizer(wx.VERTICAL)
    layout_mainV1.Add(self.DspLog, 1, wx.ALL|wx.EXPAND, 5)
    layout_mainV1.Add(layout_btnF1, 0, wx.EXPAND|wx.BOTTOM, 5)

    self.SetAutoLayout(True)
    self.SetSizer(layout_mainV1)
    self.Layout()

    self.SetMinSize(self.GetSize())

    self.SetSize(wx.Size(600, 600))

    self.AlignWithMainWindow()

    # Make sure log window is not shown at initialization
    self.Show(False)

  ## Positions the log window relative to the main window
  def AlignWithMainWindow(self):
    debreate_pos = ui.app.getMainWindow().GetPosition()
    width = self.GetSize()[0]
    posX = debreate_pos[0] - width
    posY = debreate_pos[1]

    self.SetPosition(wx.Point(posX, posY))

  ## Hides the log window & clears contents
  def HideLog(self):
    self.Show(False)
    self.DspLog.Clear()

  ## Changes the font size
  def OnChangeFont(self, event=None):
    font_sizes = {
      7: 8,
      8: 10,
      10: 7,
    }

    current_font_size = self.DspLog.font_size

    for S in font_sizes:
      if S == current_font_size:
        self.DspLog.SetFont(GetMonospacedFont(font_sizes[S]))
        self.DspLog.font_size = font_sizes[S]
        return
    _logger.error(GT("Can't change log window font"))

  ## Hides the log window when close event occurs
  def OnClose(self, event=None):
    self.HideLog()

  ## Called by refresh event to update the log display
  def OnLogTimestampChanged(self, event=None):
    self.RefreshLog()

  ## Opens a new log file
  def OnOpenLogFile(self, event=None):
    log_select = GetFileOpenDialog(self, GT("Open Log"), directory=paths.getLogsDir())
    if ShowDialog(log_select):
      logFile = log_select.GetPath()
      if os.path.isfile(logFile):
        self.SetLogFile(logFile)
        return
      ShowErrorDialog("{}: {}".format(GT("File does not exist"), logFile),
          parent=self)

  ## Guarantees that menu item is synced with window's shown status
  def OnShow(self, event=None):
    menu_debug = ui.app.getMainWindow().getMenu(menuid.DEBUG)
    # In case main window has been destroyed, but sub thread still active
    if ui.app.getMainWindow():
      window_shown = self.IsShown()
      m_checked = menu_debug.IsChecked(menuid.LOG)
      if m_checked != window_shown:
        menu_debug.Check(menuid.LOG, window_shown)
    else:
      _logger.warn("Log thread still active!")

  ## Use an event to show the log window
  #
  #  By waiting until the main window emits a show event
  #  a separate item is not added in the system window
  #  list for the log.
  def OnShowMainWindow(self, event=None):
    main_window = ui.app.getMainWindow()

    # Make sure the main window has not been destroyed before showing log
    if main_window and main_window.IsShown():
      if ui.app.getMainWindow().getMenu(menuid.DEBUG).IsChecked(menuid.LOG):
        self.ShowLog()

  ## Toggles the log window shown or hidden
  def OnToggleWindow(self, event=None):
    show = ui.app.getMainWindow().getMenu(menuid.DEBUG).IsChecked(menuid.LOG)
    if show:
      self.ShowLog()
      return
    self.HideLog()
    if event:
      event.Skip(True)

  ## Creates a thread that polls for changes in log file
  def PollLogFile(self, args=None):
    while self and self.IsShown():
      if self.LogFile.TimestampChanged():
        print("Log timestamp changed, loading new log ...")
        wx.PostEvent(self, RefreshLogEvent(0))

      time.sleep(LOG_WINDOW_REFRESH_INTERVAL)

  ## Fills log with text file contents
  def RefreshLog(self, event=None):
    if self.LogFile.IsFile():
      log_data = self.LogFile.Read()

      if not self.DspLog.IsEmpty():
        self.DspLog.Clear()

      self.DspLog.SetValue(log_data)

      try:
        # Yield here to make sure last line is displayed
        # FIXME: Causes delay when debug enabled
        wx.SafeYield()
        self.DspLog.ShowPosition(self.DspLog.GetLastPosition())
      except RuntimeError:
        tb_error = strings.toString(traceback.format_exc())
        _logger.warn("Error refreshing log window. Details below:\n\n{}".format(tb_error))

  ## Changes the file to be loaded & displayed
  #
  #  @param logFile
  #    Absolute path of file to load
  def SetLogFile(self, logFile):
    self.LogFile = FileItem(logFile)
    self.RefreshLog()
    self.SetTitle()

  ## Updates the window's title using path of log file
  def SetTitle(self):
    new_title = self.LogFile.GetPath()
    if new_title:
      return wx.Dialog.SetTitle(self, new_title)

  ## Shows the log window
  def ShowLog(self):
    self.RefreshLog()
    self.Show(True)
    if not threads.isActive(self.thread_id):
      _logger.debug("starting log polling thread ...")
      threads.start(self.thread_id)
    else:
      _logger.debug("Log polling thread is already started")
