# -*- coding: utf-8 -*-

## \package wizsrc.control

# MIT licensing
# See: docs/LICENSE.txt


import wx

from wiz.wizard     import WizardPage
from globals.ident  import pgid
from ui.layout      import BoxSizer


## Control page for source builds
class Page(WizardPage):
    ## Constructor
    #
    #  \param parent
    #    Parent <b><i>wx.Window</i></b> instance
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.CONTROL)
        
        # *** Layout *** #
        
        lyt_main = BoxSizer(wx.VERTICAL)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
