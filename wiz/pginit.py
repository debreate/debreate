
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module wiz.pginit
#
#  The initial wizard page

import wx

from dbr.language  import GT
from globals.ident import pgid
from ui.hyperlink  import Hyperlink
from ui.layout     import BoxSizer
from wiz.wizard    import WizardPage


## The initial wizard page
class Page(WizardPage):
  def __init__(self, parent):
    WizardPage.__init__(self, parent, pgid.GREETING)

    m1 = GT("Welcome to Debreate!")
    m2 = GT("Debreate aids in building packages for installation on Debian based systems. Use the arrows located in the top-right corner or the \"Page\" menu to navigate through the program. For some information on Debian packages use the reference links in the \"Help\" menu.")
    m3 = GT("For a video tutorial check the link below.")
    str_info = "{}\n\n{}\n\n{}".format(m1, m2, m3)

    # --- Information to be displayed about each mode
    txt_info = wx.StaticText(self, label=str_info)
    # Keep characters within the width of the window
    txt_info.Wrap(600)

    lnk_video = Hyperlink(self, wx.ID_ANY, GT("Building a Debian Package with Debreate"),
        "http://www.youtube.com/watch?v=kx4D5eL6HKE")
    lnk_video.SetToolTip(lnk_video.url)

    # *** Layout *** #

    lyt_info = wx.GridSizer(1, 1, 0, 0)
    lyt_info.Add(txt_info, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)

    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.Add(lyt_info, 4, wx.ALIGN_CENTER|wx.ALL, 10)
    lyt_main.Add(lnk_video, 2, wx.ALIGN_CENTER)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()
