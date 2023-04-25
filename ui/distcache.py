
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.distcache

import os
import traceback

import wx

from wx.adv import OwnerDrawnComboBox

import ui.app

from dbr.event            import EVT_TIMER_STOP
from dbr.language         import GT
from dbr.timer            import DebreateTimer
from globals              import threads
from globals.system       import FILE_distnames
from globals.system       import GetOSDistNames
from globals.system       import UpdateDistNamesCache
from libdbr.fileio        import readFile
from libdbr.logger        import Logger
from libdebreate.ident    import inputid
from libdebreate.ident    import pgid
from ui.dialog            import BaseDialog
from ui.dialog            import ConfirmationDialog
from ui.dialog            import ShowErrorDialog
from ui.dialog            import ShowMessageDialog
from ui.layout            import BoxSizer
from ui.panel             import BorderedPanel
from ui.progress          import ProgressDialog
from ui.style             import layout as lyt
from ui.textpreview       import TextPreview


logger = Logger(__name__)

## Dialog displaying controls for updating distribution names cache file
class DistNamesCacheDialog(BaseDialog):
  def __init__(self):
    BaseDialog.__init__(self, title=GT("Update Dist Names Cache"),
        style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
    self.SetMinSize(wx.Size(300, 150))

    txt_types = wx.StaticText(self, label=GT("Include the following:"))

    pnl_types = BorderedPanel(self)

    self.chk_unstable = wx.CheckBox(pnl_types, label=GT("Unstable"))
    self.chk_obsolete = wx.CheckBox(pnl_types, label=GT("Obsolete"))
    self.chk_generic = wx.CheckBox(pnl_types, label=GT("Generic (Debian names only)"))

    self.btn_preview = wx.Button(self, label=GT("Preview cache"))
    btn_update = wx.Button(self, label=GT("Update cache"))
    btn_clear = wx.Button(self, label=GT("Clear cache"))

    # Keep preview dialog in memory so position/size is saved
    self.preview = TextPreview(self, title=GT("Available Distribution Names"),
        size=(500,400))

    # Is instantiated as ProgressDialog when OnUpdateCache is called
    self.progress = None
    self.timer = DebreateTimer(self)

    # For setting error messages from other threads
    self.error_message = None

    # *** Event Handling *** #

    self.btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewCache)
    btn_update.Bind(wx.EVT_BUTTON, self.OnUpdateCache)
    btn_clear.Bind(wx.EVT_BUTTON, self.OnClearCache)

    self.Bind(wx.EVT_TIMER, self.OnTimerEvent)
    self.Bind(EVT_TIMER_STOP, self.OnTimerStop)

    # *** Layout *** #

    lyt_types = BoxSizer(wx.VERTICAL)
    lyt_types.AddSpacer(5)

    for CHK in (self.chk_unstable, self.chk_obsolete, self.chk_generic,):
      lyt_types.Add(CHK, 0, lyt.PAD_LR, 5)

    lyt_types.AddSpacer(5)

    pnl_types.SetAutoLayout(True)
    pnl_types.SetSizerAndFit(lyt_types)
    pnl_types.Layout()

    lyt_buttons = BoxSizer(wx.HORIZONTAL)
    lyt_buttons.Add(self.btn_preview, 1)
    lyt_buttons.Add(btn_update, 1)
    lyt_buttons.Add(btn_clear, 1)

    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.Add(txt_types, 0, wx.ALIGN_CENTER|lyt.PAD_LRT, 5)
    lyt_main.Add(pnl_types, 0, wx.ALIGN_CENTER|lyt.PAD_LR, 5)
    lyt_main.Add(lyt_buttons, 1, wx.ALIGN_CENTER|wx.ALL, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()

    # *** Post-layout Actions *** #

    if not os.path.isfile(FILE_distnames):
      self.btn_preview.Disable()

    if self.Parent:
      self.CenterOnParent()

  ## Checks for present error message & displays dialog
  #
  #  @return
  #    \b \e False if no errors present
  def CheckErrors(self):
    if self.error_message:
      ShowErrorDialog(self.error_message, parent=self, linewrap=410)
      # Clear error message & return
      self.error_message = None
      return True
    return False

  ## Deletes the distribution names cache file
  def OnClearCache(self, event=None):
    if os.path.isfile(FILE_distnames):
      dia = ConfirmationDialog(self, text=GT("Delete '{}'?").format(FILE_distnames))
      if dia.ShowModal() != wx.ID_OK:
        return True
      os.remove(FILE_distnames)
      # Update list on changelog page
      ui.app.getPage(pgid.CHANGELOG).reloadDistNames()
      self.btn_preview.Disable()
    cache_exists = os.path.exists(FILE_distnames)
    self.btn_preview.Enable(cache_exists)
    return not cache_exists

  ## Opens cache file for previewing
  def OnPreviewCache(self, event=None):
    self.preview.SetValue(readFile(FILE_distnames))
    self.preview.ShowModal()

  ## Calls Pulse method on progress dialog when timer event occurs
  def OnTimerEvent(self, event=None):
    if self.progress:
      self.progress.Pulse()

  ## Closes & resets the progress dialog to None when timer stops
  def OnTimerStop(self, event=None):
    if self.progress:
      self.progress.EndModal(0)
      self.progress = None
    return not self.progress

  ## Creates/Updates the distribution names cache file
  def OnUpdateCache(self, event=None):
    try:
      # Timer must be started before executing new thread
      self.timer.Start(100)

      if not self.timer.IsRunning():
        self.error_message = GT("Could not start progress dialog timer")
        self.CheckErrors()
        return False

      self.Disable()

      # Start new thread for updating cache in background
      threads.create(self.UpdateCache)

      # Create the progress dialog & start timer
      # NOTE: Progress dialog is reset by timer stop event
      self.progress = ProgressDialog(self, message=GT("Contacting remote sites"),
          style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)

      # Use ShowModal to wait for timer to stop before continuing
      self.progress.ShowModal()
      self.Enable()

      if self.CheckErrors():
        return False

      # FIXME: Should check timestamps to make sure file was updated
      cache_updated = os.path.isfile(FILE_distnames)

      if cache_updated:
        if not ui.app.getPage(pgid.CHANGELOG).reloadDistNames():
          ShowMessageDialog(
            GT("The distribution names cache has been updated but Debreate needs to restart to reflect the changes on the changelog page"),
            parent=self, linewrap=410)
      self.btn_preview.Enable(cache_updated)
      return cache_updated
    except:
      # Make sure dialog is re-enabled
      self.Enable()

      # Make sure progress dialog & background thread instances are reset to None
      if self.progress:
        self.progress.EndModal(0)
        self.progress = None

      cache_exists = os.path.isfile(FILE_distnames)

      err_msg = GT("An error occurred when trying to update the distribution names cache")
      err_msg2 = GT("The cache file exists but may not have been updated")
      if cache_exists:
        err_msg = "{}\n\n{}".format(err_msg, err_msg2)

      ShowErrorDialog(err_msg, traceback.format_exc(), self)

      self.btn_preview.Enable(cache_exists)

    return False

  ## Method that does the actual updating of the names cache list
  #
  #  Called from a new thread
  #
  #  @todo
  #    FIXME: Show error if could not contact 1 or more remote sites???
  def UpdateCache(self):
    logger.debug(GT("Updating cache ..."))
    UpdateDistNamesCache(self.chk_unstable.GetValue(), self.chk_obsolete.GetValue(),
        self.chk_generic.GetValue())
    self.timer.Stop()
