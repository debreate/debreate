
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.app

import wx


## Custom wx.App class for setting & retrieving main window instance.
class DebreateApp(wx.App):
  ## Constructor
  def __init__(self):
    wx.App.__init__(self)

    self.MainWindow = None

  ## Retrieves the main window.
  #
  #  @return
  #    `ui.main.MainWindow` instance.
  def GetMainWindow(self):
    return self.MainWindow

  ## Retrieves the wizard.
  #
  #  @return
  #    `wiz.wizard.Wizard` instance.
  def GetWizard(self):
    if self.MainWindow:
      return self.MainWindow.GetWizard()

  ## Set the main window instance.
  #
  #  @param window
  #    `wx.Frame` instance to use for main window.
  def SetMainWindow(self, window):
    self.MainWindow = window
