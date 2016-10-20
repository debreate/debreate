# -*- coding: utf-8 -*-

## \package globals.tooltips
#  
#  Defines tooltips that have longer texts

# MIT licensing
# See: docs/LICENSE.txt


import wx
from wx.lib.agw.balloontip import BalloonTip, BT_ROUNDED

from dbr.font           import FONT_tt
from dbr.language       import GT
from dbr.log            import Logger
from globals.characters import ARROW_RIGHT
from globals.colors     import COLOR_tooltip


tooltips_enabled = True

def ToggleToolTips(enabled=not tooltips_enabled):
    tooltips_enabled = enabled

def ToolTipsEnabled():
    return tooltips_enabled


## FIXME: Custom tooltips not working
class ToolTip(wx.Panel):
    def __init__(self, parent, message=wx.EmptyString, icon=wx.EmptyString):
        self.actual_parent = parent
        if isinstance(parent, wx.Button):
            self.actual_parent = parent.GetParent()
        
        wx.Panel.__init__(self, self.actual_parent)
        
        self.faux_parent = parent
        
        self.SetBackgroundColour(COLOR_tooltip)
        '''
        self.icon = icon
        if isinstance(self.icon, (unicode, str)):
            self.icon = wx.Bitmap(self.icon)
        '''
        self.message = wx.StaticText(self, label=message)
                
        padding = 5
        
        layoutH_MAIN = wx.BoxSizer(wx.HORIZONTAL)
        layoutH_MAIN.Add(self.message, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, padding)
        
        size = self.message.GetSize()
        self.SetSize(wx.Size(size[0]+padding+5, size[1]+padding))
        
        self.SetAutoLayout(True)
        self.SetSizer(layoutH_MAIN)
        self.Layout()
        
        self.Show(False)
        
        # FIXME: How to get tooltip to disappear when button pressed?
        if isinstance(parent, wx.Button):
            parent.Bind(wx.EVT_BUTTON, self.OnHide)
        
            print(u'DEBUG: [globals.tooltips] TT parent type: {}'.format(type(parent)))
        
        wx.EVT_ENTER_WINDOW(parent, self.OnShow)
        wx.EVT_LEAVE_WINDOW(parent, self.OnHide)
    
    
    def GetMessage(self):
        return self.message.GetLabel()
    
    
    ## Retrieves the parent control
    #  
    #  This needs to be overriden because the panels actual parent
    #    is set from parent.GetParent().
    def GetParent(self, *args, **kwargs):
        Logger.Debug(__name__,
                GT(u'Faux parent: {}; Actual parent: {}').format(type(self.faux_parent), type(self.actual_parent)))
        
        return self.faux_parent
    
    
    def GetRealParent(self):
        return self.actual_parent
    
    
    ## FIXME: Endless event loop occurring?
    def OnHide(self, event=None):
        self.Show(False)
        
        if event:
            event.Skip()
    
    
    ## FIXME: Endless event loop occurring?
    def OnShow(self, event=None):
        #relative_pos = wx.GetMousePosition() - self.GetRealParent().GetDebreateWindow().GetScreenPosition()
        parent_height = self.faux_parent.GetSize()[1]
        
        #Logger.Debug(__name__, GT(u'Relative pos: {}').format(relative_pos))
        #mouse_state = wx.GetMouseState()
        if tooltips_enabled:
            self.SetPosition(self.faux_parent.GetPosition() + wx.Point(0, parent_height))
            self.Show(True)
        
        if event:
            event.Skip()
    
    
    def SetMessage(self, message):
        self.message.SetLabel(message)


## Sets a custom tooltip
#  
#  TODO: Enable/Disable bubble tips globally
def SetBubbleToolTip(control, tooltip):
    tt = BalloonTip(message=tooltip, shape=BT_ROUNDED)
    tt.SetMessageFont(FONT_tt)
    tt.SetTarget(control)

## Universal function for setting window/control tooltips
def SetToolTip(control, tooltip):
    if isinstance(tooltip, (unicode, str)) and tooltip != wx.EmptyString:
        control.SetToolTipString(tooltip)
    
    elif isinstance(tooltip, wx.ToolTip) and tooltip.GetTip() != wx.EmptyString:
        control.SetToolTip(tooltip)


## Sets multip tooltips at once
def SetToolTips(control_list):
    for C in control_list:
        SetToolTip(C[0], C[1])


# *** Wizard buttons ***#

TT_wiz_prev = wx.ToolTip(GT(u'Previous page'))
TT_wiz_next = wx.ToolTip(GT(u'Next page'))

# *** Files page *** #
TT_files_refresh = wx.ToolTip(GT(u'Update files\' executable status & availability'))

# *** Build page *** #

TT_chk_md5 = wx.ToolTip(GT(u'Creates a checksums in the package for all packaged files'))
TT_chk_del = wx.ToolTip(GT(u'Delete staged directory tree after package has been created'))
TT_chk_lint = wx.ToolTip(GT(u'Checks the package for warnings & errors according to lintian\'s specifics\n\
(See: Help {0} Reference {0} Lintian Tags Explanation)').format(ARROW_RIGHT))
TT_chk_dest = wx.ToolTip(GT(u'Choose the folder where you would like the .deb to be created'))
