# -*- coding: utf-8 -*-

## \package wiz_bin.info

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.hyperlink  import Hyperlink
from dbr.language   import GT
from dbr.wizard     import WizardPage
from globals        import ident


## TODO: Doxygen
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.GREETING)
        
        # Bypass checking this page for build
        self.prebuild_check = False
        
        m1 = GT(u'Welcome to Debreate!')
        m2 = GT(u'Debreate aids in building packages for installation on Debian based systems. Use the arrows located in the top-right corner or the "Page" menu to navigate through the program. For some information on Debian packages use the reference links in the "Help" menu.')
        m3 = GT(u'For a video tutorial check the link below.')
        self.txt_bin = u'{}\n\n{}\n\n{}'.format(m1, m2, m3)
        self.txt_src = u'This mode is not fully functional'
        self.txt_upd = u'This mode is not fully functional'
        
        self.mode_info = (
            (0, u'Build Package from Precompiled Files', self.txt_bin),
            (1, u'Build Debian Source Package', self.txt_src),
            (2, u'Update a Package', self.txt_upd)
            )
        
        # --- Information to be displayed about each mode
        self.txt_info = wx.StaticText(self)
        # Keep characters within the width of the window
        self.txt_info.Wrap(600)
        
        lnk_video = Hyperlink(self, wx.ID_ANY, GT(u'Building a Debian Package with Debreate'),
                u'http://www.youtube.com/watch?v=kx4D5eL6HKE')
        lnk_video.SetToolTipString(lnk_video.url)
        
        # *** Layout *** #
        
        lyt_info = wx.GridSizer()
        lyt_info.Add(self.txt_info, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(lyt_info, 4, wx.ALIGN_CENTER|wx.ALL, 10)
        lyt_main.Add(lnk_video, 2, wx.ALIGN_CENTER)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        
    def SetInfo(self):
        self.Parent.SetTitle(u'Testing')
        self.txt_info.SetLabel(self.txt_bin)
        
        self.txt_info.Wrap(600) # Keep characters within the width of the window
        
        # Refresh widget layout
        self.Layout()
    
    
    ## Override Wizard.ResetPage & do nothing
    def ResetPage(self):
        pass
