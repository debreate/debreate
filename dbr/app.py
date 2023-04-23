
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.app

import wx

from libdbr.logger import Logger


_logger = Logger(__name__)

## Custom wx.App class for setting & retrieving main window instance.
class DebreateApp(wx.App):
  ## App constructor.
  #
  #  @param window
  #    `wx.Window` instance to use as main window.
  def __init__(self, window=None):
    wx.App.__init__(self)
    self.setMainWindow(window)

  ## Retrieves the main window.
  #
  #  @return
  #    `ui.main.MainWindow` instance.
  def getMainWindow(self):
    return self.MainWindow

  ## Alias of `dbr.app.DebreateApp.getMainWindow`.
  #
  #  @return
  #    `ui.main.MainWindow` instance.
  #  @deprecated
  #    Use `dbr.app.DebreateApp.getMainWindow`.
  def GetMainWindow(self):
    _logger.deprecated(self.GetMainWindow, alt=self.getMainWindow)

    return self.getMainWindow()

  ## Retrieves the wizard.
  #
  #  @return
  #    `wiz.wizard.Wizard` instance.
  def getWizard(self):
    if self.MainWindow:
      return self.MainWindow.GetWizard()
    return None

  ## Alias of `dbr.app.DebreateApp.getWizard`.
  #
  #  @return
  #    `wiz.wizard.Wizard` instance.
  #  @deprecated
  #    Use `dbr.app.DebreateApp.getWizard`.
  def GetWizard(self):
    _logger.deprecated(self.GetWizard, alt=self.getWizard)

    return self.getWizard()

  ## Set the main window instance.
  #
  #  @param window
  #    `wx.Frame` instance to use for main window.
  def setMainWindow(self, window):
    self.MainWindow = window

  ## Alias of `dbr.app.DebreateApp.setMainWindow`.
  #
  #  @param window
  #    `wx.Frame` instance to use for main window.
  #  @deprecated
  #    Use `dbr.app.DebreateApp.setMainWindow`.
  def SetMainWindow(self, window):
    _logger.deprecated(self.SetMainWindow, alt=self.setMainWindow)

    self.setMainWindow(window)


## Helper function to get app instance.
#
#  @return
#    `dbr.app.DebreateApp` instance.
def get():
  return wx.GetApp()

## Helper function to get main window instance.
#
#  @return
#    `ui.main.MainWindow` instance.
def getMainWindow():
  return get().getMainWindow()
