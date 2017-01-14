# -*- coding: utf-8 -*-


# System imports
import wx

import globals.ident as ident
from dbr.hyperlink  import Hyperlink
from dbr.language   import GT
from dbr.wizard     import WizardPage


class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.GREETING)
        
        self.parent = parent
        
        # Bypass checking this page for build
        self.prebuild_check = False
        
        # Mode Information
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
        
        # ----- Helpful information to be displayed about each mode
        self.info = wx.StaticText(self)
        self.vidlink = Hyperlink(
                self, -1,
                GT(u'Building a Debian Package with Debreate'),
                u'http://www.youtube.com/watch?v=kx4D5eL6HKE'
        )
        self.vidlink.SetToolTip(wx.ToolTip(self.vidlink.url))
        
        self.info_border = wx.StaticBox(self, -1, size=(100,100))
        info_box = wx.GridSizer()
        info_box.Add(self.info, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        
        # ----- Layout
        mode_sizer = wx.StaticBoxSizer(self.info_border, wx.VERTICAL)
        mode_sizer.Add(info_box, 4, wx.ALIGN_CENTER|wx.ALL, 10)
        mode_sizer.Add(self.vidlink, 2, wx.ALIGN_CENTER)
        
        self.SetAutoLayout(True)
        self.SetSizer(mode_sizer)
        self.Layout()
        
        
    def SetInfo(self):
        self.parent.SetTitle(u'Testing')
        self.info.SetLabel(self.txt_bin)
        
        self.info.Wrap(600) # Keep characters within the width of the window
        
        # Refresh widget layout
        self.Layout()
    
    
    ## Override Wizard.ResetPage & do nothing
    def ResetPage(self):
        pass
