# -*- coding: utf-8 -*-

# ============================== MIT LICENSE ==================================
#
# Copyright (c) 2015 Jordan Irwin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# =============================================================================

## @package panel
#

import wx

ID_INFO = wx.NewId()

class InfoPanel(wx.Panel):
    def __init__(self, parent, id=ID_INFO, name=_('Information')):
        wx.Panel.__init__(self, parent, id, name=_('Information'))

        self.parent = parent # 3rd level) Allows executing 2st level methods

        # Mode Information
        m1 = _('Welcome to Debreate!')
        m2 = _('Debreate aids in building packages for installation on Debian based systems. Use the arrows located in the top-right corner or the "Page" menu to navigate through the program. For some information on Debian packages use the reference links in the "Help" menu.')
        m3 = _('For a video tutorial check the link below.')
        self.txt_bin = '%s\n\n%s\n\n%s' % (m1, m2, m3)
        self.txt_src = "This mode is not fully functional"
        self.txt_upd = "This mode is not fully functional"

        self.mode_info = (
            (0, "Build Package from Precompiled Files", self.txt_bin),
            (1, "Build Debian Source Package", self.txt_src),
            (2, "Update a Package", self.txt_upd)
            )

        # ----- Helpful information to be displayed about each mode
        self.info = wx.StaticText(self, -1)
        self.vidlink = wx.HyperlinkCtrl(self, -1, _('Building a Debian Package with Debreate'), 'http://www.youtube.com/watch?v=kx4D5eL6HKE')
        self.info_border = wx.StaticBox(self, -1, size=(100, 100))
        info_box = wx.GridSizer()
        info_box.Add(self.info, 1, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

        # ----- Layout
        mode_sizer = wx.StaticBoxSizer(self.info_border, wx.VERTICAL)
        mode_sizer.Add(info_box, 4, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 10)
        mode_sizer.Add(self.vidlink, 2, wx.EXPAND | wx.ALIGN_CENTER)

        self.SetAutoLayout(True)
        self.SetSizer(mode_sizer)
        self.Layout()


    def SetInfo(self):
        self.parent.SetTitle('Testing')
        self.info.SetLabel(self.txt_bin)

        self.info.Wrap(600) # Keep characters within the width of the window

        # Refresh widget layout
        self.Layout()
