# -*- coding: utf-8 -*-

## \package dbr.quickbuild


# System modules
import wx, os

# Local modules
from dbr.language import GT
from dbr.buttons import ButtonBrowse, ButtonBuild, ButtonCancel
from dbr.functions import GetDirDialog, ShowDialog


class QuickBuild(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=GT(u'Quick Build'), pos=wx.DefaultPosition,
                size=wx.Size(400,260))
        
        self.debreate = parent.GetDebreateWindow()
        
        label_filename = wx.StaticText(self, label=GT(u'Name'))
        self.filename = wx.TextCtrl(self)
        self.filename.SetToolTip(wx.ToolTip(GT(u'Name to use for output file')))
        
        Lname_H1 = wx.BoxSizer(wx.HORIZONTAL)
        Lname_H1.Add(label_filename, 1, wx.ALIGN_BOTTOM)
        
        Lname_H2 = wx.BoxSizer(wx.HORIZONTAL)
        Lname_H2.Add(self.filename, 1, wx.ALIGN_TOP)
        
        #Lname_V1 = wx.BoxSizer(wx.VERTICAL)
        #Lname_V1.Add(self.filename, 1, wx.ALIGN_TOP)
        
        label_path = wx.StaticText(self, label=GT(u'Path to build tree'))
        self.path = wx.TextCtrl(self)
        self.path.SetToolTip(wx.ToolTip(GT(u'Root directory of build tree')))
        
        Lpath_V1 = wx.BoxSizer(wx.VERTICAL)
        Lpath_V1.Add(label_path, 0, wx.ALIGN_LEFT)
        Lpath_V1.Add(self.path, 1, wx.EXPAND)
        
        btn_browse = ButtonBrowse(self)
        btn_browse.Bind(wx.EVT_BUTTON, self.OnBrowse)
        
        Lpath_H1 = wx.BoxSizer(wx.HORIZONTAL)
        Lpath_H1.Add(Lpath_V1, 3, wx.ALIGN_TOP)
        Lpath_H1.Add(btn_browse, 0, wx.ALIGN_TOP|wx.TOP, 7)
        
        Lpath_V2 = wx.BoxSizer(wx.VERTICAL)
        Lpath_V2.Add(Lpath_H1, 1, wx.ALIGN_TOP|wx.EXPAND)
        
        btn_build = ButtonBuild(self)
        btn_build.SetToolTip(wx.ToolTip(GT(u'Start building')))
        btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)
        
        btn_cancel = ButtonCancel(self)
        btn_cancel.SetToolTip(wx.ToolTip(GT(u'Cancel build')))
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)
        
        Lbtn_H1 = wx.BoxSizer(wx.HORIZONTAL)
        Lbtn_H1.Add(btn_build, 1, wx.ALIGN_BOTTOM|wx.RIGHT, 2)
        Lbtn_H1.Add(btn_cancel, 1, wx.ALIGN_BOTTOM|wx.LEFT, 2)
        
        self.gauge = wx.Gauge(self, 100)
        
        Lguage_H1 = wx.BoxSizer(wx.HORIZONTAL)
        Lguage_H1.Add(self.gauge, 1, wx.LEFT|wx.RIGHT, 5)
        
        self.ID_TIMER = wx.NewId()
        self.timer = wx.Timer(self, self.ID_TIMER)
        wx.EVT_TIMER(self, self.ID_TIMER, self.OnUpdateProgress)
        
        Lmain_V = wx.BoxSizer(wx.VERTICAL)
        Lmain_V.AddSpacer(1, wx.EXPAND)
        Lmain_V.Add(Lname_H1, -1, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT, 5)
        Lmain_V.Add(Lname_H2, -1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        Lmain_V.Add(Lpath_V2, -1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        Lmain_V.Add(Lbtn_H1, -1, wx.ALIGN_CENTER|wx.ALL, 5)
        Lmain_V.Add(Lguage_H1, -1, wx.EXPAND|wx.ALL, 5)
        Lmain_V.AddSpacer(1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(Lmain_V)
        self.Layout()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.CenterOnParent()
    
    
    def OnBrowse(self, event=None):
        source = GetDirDialog(self.debreate, GT(u'Choose Directory'))
        source.CenterOnParent()
        
        if (ShowDialog(source)):
            self.path.SetValue(source.GetPath())
    
    
    def OnBuild(self, event=None):
        print(u'Building ...')
    
    
    ## Closes the Quick Build dialog & destroys instance
    def OnClose(self, event=None):
        self.EndModal(True)
    
    
    ## Updates the progress bar
    def OnUpdateProgress(self, event=None):
        self.gauge.Pulse()
