
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.help


import os
import subprocess

import wx

from wx.richtext import RE_READONLY
from wx.richtext import RichTextCtrl

from ui.layout import BoxSizer

from libdbr.logger import Logger


_logger = Logger(__name__)

# FIXME: This should use a global manpage file
#app_man = "{}/man/debreate.1"
app_man = "man/man1/debreate.1"
local_manpath = "man"
man_section = "1"


## Parses & returns Debreate's manpage as RichText.
#
#  @return
#    RichText help reference.
#  @deprecated
def ParseManpage():
  _logger.deprecated(ParseManpage)

  help_text = "ERROR: Could not parse '{}'".format(app_man)

  if os.path.isfile(app_man):
    # FIXME: Should text if application is installed on system
    c_man = "man --manpath={} {} debreate".format(local_manpath, man_section)
    res = subprocess.run([c_man])

    # Command exited successfully
    if res.returncode == 0:
      help_text = res.stdout

  return help_text


## @todo Doxygen
class HelpDialog(wx.Dialog):
  def __init__(self, parent):
    wx.Dialog.__init__(self, parent, wx.ID_HELP, "Help",
               style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

    dialog_size = wx.Size(200, 200)

    self.SetSize(wx.DefaultSize)
    self.SetMinSize(dialog_size)

    bg = wx.Panel(self)

    help_display = RichTextCtrl(bg, style=RE_READONLY)

    sizer_v1 = BoxSizer(wx.VERTICAL)
    sizer_v1.Add(help_display, 1, wx.EXPAND)

    bg.SetSizer(sizer_v1)
    bg.SetAutoLayout(True)
    bg.Layout()
