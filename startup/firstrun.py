
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Handles creation of first run dialog.
#
#  @module startup.firstrun

import wx

import ui.app

from dbr.language  import GT
from globals       import bitmaps
from libdbr        import paths
from libdbr.logger import Logger
from ui.style      import layout as lyt


__logger = Logger(__name__)


## Shows the first run dialog.
def launch():
  __logger.debug("launching first run dialog ...")

  fr = __buildDialog(ui.app.getMainWindow())
  fr_size = wx.Size(450, 300)
  fr.SetSize(fr_size)
  fr.CenterOnParent()
  fr.ShowModal()


## Builds first run dialog.
#
#  @param parent
#    Parent window for modal.
def __buildDialog(parent):
  fr = wx.Dialog(parent, wx.ID_ANY, GT("Debreate First Run"))

  m2 = GT("This message only displays on the first run, or if\nthe configuration file becomes corrupted.")
  m3 = GT("The default configuration file will now be created.")
  m4 = GT("To delete this file, type the following command in a\nterminal:")

  message1 = GT("Thank you for using Debreate.")
  message1 = "{}\n\n{}".format(message1, m2)

  message2 = m3
  message2 = "{}\n{}".format(message2, m4)

  path_icon = paths.join(paths.getAppDir(), "bitmaps/icon/64/logo.png")
  # set the titlebar icon
  fr.SetIcon(wx.Icon(bitmaps.LOGO, wx.BITMAP_TYPE_PNG))

  # Display a message to create a config file
  text1 = wx.StaticText(fr, label=message1)
  text2 = wx.StaticText(fr, label=message2)

  rm_cmd = wx.TextCtrl(fr, value="rm -f ~/.config/debreate.conf",
      style=wx.TE_READONLY|wx.BORDER_NONE)
  rm_cmd.SetBackgroundColour(fr.BackgroundColour)

  layout_V1 = wx.BoxSizer(wx.VERTICAL)
  layout_V1.Add(text1, 1)
  layout_V1.Add(text2, 1, wx.TOP, 15)
  layout_V1.Add(rm_cmd, 0, wx.EXPAND|wx.TOP, 10)

  # Show the Debreate icon
  icon = wx.StaticBitmap(fr, bitmap=wx.Bitmap(path_icon))

  # Button to confirm
  fr.button_ok = wx.Button(fr, wx.ID_OK)

  # Nice border
  fr.border = wx.StaticBox(fr, -1)
  border_box = wx.StaticBoxSizer(fr.border, wx.HORIZONTAL)
  border_box.AddSpacer(10)
  border_box.Add(icon, 0, wx.ALIGN_CENTER)
  border_box.AddSpacer(10)
  border_box.Add(layout_V1, 1, wx.ALIGN_CENTER)

  # Set Layout
  sizer = wx.BoxSizer(wx.VERTICAL)
  sizer.Add(border_box, 1, wx.EXPAND|lyt.PAD_LR, 5)
  sizer.Add(fr.button_ok, 0, wx.ALIGN_RIGHT|lyt.PAD_RB|wx.TOP, 5)

  fr.SetSizer(sizer)
  fr.Layout()

  return fr
