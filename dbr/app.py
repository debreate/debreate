
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.app

import wx


## Custom wx.App class for setting & retrieving main window instance
class DebreateApp(wx.App):
  ## Constructor
  def __init__(self):
    wx.App.__init__(self)

    self.MainWindow = None


  ## Retrieves the main window
  #
  #  \return
  #  <b><i>main.MainWindow</i></b> instance
  def GetMainWindow(self):
    return self.MainWindow


  ## Retrieves the wizard
  #
  #  \return
  #  <b><i>wiz.wizard.Wizard</i></b> instance
  def GetWizard(self):
    if self.MainWindow:
      return self.MainWindow.GetWizard()


  ## Set the main window instance
  #
  #  \param window
  #  <b><i>wx.Frame</i></b> instance to use for main window
  #  \return
  #  <b><i>None</i></b>
  def SetMainWindow(self, window):
    self.MainWindow = window
