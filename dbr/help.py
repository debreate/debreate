## \package dbr.help

# MIT licensing
# See: docs/LICENSE.txt


import os, subprocess, wx
from wx.richtext import RE_READONLY
from wx.richtext import RichTextCtrl

from ui.layout import BoxSizer


# FIXME: This should use a global manpage file
#app_man = "{}/man/debreate.1"
app_man = "man/man1/debreate.1"
local_manpath = "man"
man_section = "1"


## Parses & returns Debreate's manpage as RichText
#
#  \return
#       RichText help reference
def ParseManpage():
  help_text = "ERROR: Could not parse '{}'".format(app_man)

  if os.path.isfile(app_man):
    # FIXME: Should text if application is installed on system
    res = subprocess.run(["man", "--manpath={}".format(local_manpath), man_section, "debreate"], capture_output=True)
    c_output = (res.returncode, res.stdout.decode("utf-8"))

    # Command exited successfully
    if not c_output[0]:
      help_text = c_output[1]

  return help_text


## TODO: Doxygen
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
