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

## @package decor
#

import wx, os

from common import setWXVersion


setWXVersion()


application_path = "%s/.." % os.path.dirname(__file__)

# *** Buttons *** #

class ButtonAdd(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_RETURN):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/add32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Add')))

class ButtonBrowse(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/browse32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Browse')))

class ButtonBrowse64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/browse64.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Browse')))

class ButtonBuild(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/build32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Build')))

class ButtonBuild64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/build64.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Build')))

class ButtonCancel(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_CANCEL):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/cancel32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Cancel')))

class ButtonClear(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_ESCAPE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/clear32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Clear')))

class ButtonConfirm(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_OK):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/confirm32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Ok')))

class ButtonDel(wx.BitmapButton):
    def __init__(self, parent, id=wx.WXK_DELETE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/del32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Remove')))

class ButtonImport(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/import32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Import')))

class ButtonNext(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/next32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Next')))

class ButtonPipe(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/pipe32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Append')))

class ButtonPrev(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/prev32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Previous')))

class ButtonPreview(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/preview32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Preview')))

class ButtonPreview64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/preview64.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Preview')))

class ButtonQuestion64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_HELP):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/question64.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Help')))

class ButtonSave(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/save32.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Save')))

class ButtonSave64(wx.BitmapButton):
    def __init__(self, parent, id=wx.ID_SAVE):
        wx.BitmapButton.__init__(self, parent, id, wx.Bitmap("%s/bitmaps/save64.png" % application_path),
                style=wx.NO_BORDER)
        self.SetToolTip(wx.ToolTip(_('Save')))