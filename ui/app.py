
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Classes & functions for managing app interface.
#
#  @module ui.app

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

  ## Alias of `ui.app.DebreateApp.getMainWindow`.
  #
  #  @return
  #    `ui.main.MainWindow` instance.
  #  @deprecated
  #    Use `ui.app.DebreateApp.getMainWindow`.
  def GetMainWindow(self):
    _logger.deprecated(self.GetMainWindow, alt=self.getMainWindow)

    return self.getMainWindow()

  ## Retrieves the wizard.
  #
  #  @return
  #    `ui.wizard.Wizard` instance.
  def getWizard(self):
    if self.MainWindow:
      return self.MainWindow.GetWizard()
    return None

  ## Alias of `ui.app.DebreateApp.getWizard`.
  #
  #  @return
  #    `ui.wizard.Wizard` instance.
  #  @deprecated
  #    Use `ui.app.DebreateApp.getWizard`.
  def GetWizard(self):
    _logger.deprecated(self.GetWizard, alt=self.getWizard)

    return self.getWizard()

  ## Set the main window instance.
  #
  #  @param window
  #    `wx.Frame` instance to use for main window.
  def setMainWindow(self, window):
    self.MainWindow = window

  ## Alias of `ui.app.DebreateApp.setMainWindow`.
  #
  #  @param window
  #    `wx.Frame` instance to use for main window.
  #  @deprecated
  #    Use `ui.app.DebreateApp.setMainWindow`.
  def SetMainWindow(self, window):
    _logger.deprecated(self.SetMainWindow, alt=self.setMainWindow)

    self.setMainWindow(window)


## Helper function to get app instance.
#
#  @return
#    `ui.app.DebreateApp` instance.
def get():
  return wx.GetApp()

## Helper function to get main window instance.
#
#  @return
#    `ui.main.MainWindow` instance.
def getMainWindow():
  return get().getMainWindow()

## Helper function to get the wizard interface instance.
#
#  @return
#    `ui.wizard.Wizard` instance.
def getWizard():
  return get().getWizard()
