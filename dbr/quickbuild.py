# -*- coding: utf-8 -*-

## \package dbr.quickbuild


import wx, os

from dbr.buttons    import ButtonBrowse
from dbr.buttons    import ButtonBuild
from dbr.buttons    import ButtonCancel
from dbr.dialogs    import GetDirDialog, GetFileSaveDialog, ErrorDialog
from dbr.dialogs    import ShowDialog
from dbr.language   import GT
from globals.ident  import ID_STAGE
from globals.ident  import ID_TARGET
from dbr.log import Logger
from dbr.functions import BuildDebPackage


class QuickBuild(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=GT(u'Quick Build'), pos=wx.DefaultPosition,
                size=wx.Size(400,260))
        
        self.debreate = parent.GetDebreateWindow()
        
        label_stage = wx.StaticText(self, label=GT(u'Staged directory tree'))
        self.input_stage = wx.TextCtrl(self)
        self.input_stage.SetToolTip(wx.ToolTip(GT(u'Root directory of build tree')))
        
        btn_browse_stage = ButtonBrowse(self, ID_STAGE)
        btn_browse_stage.Bind(wx.EVT_BUTTON, self.OnBrowse)
        
        label_target = wx.StaticText(self, label=GT(u'Target file'))
        self.input_target = wx.TextCtrl(self)
        self.input_target.SetToolTip(wx.ToolTip(GT(u'Target output file')))
        
        btn_browse_target = ButtonBrowse(self, ID_TARGET)
        btn_browse_target.Bind(wx.EVT_BUTTON, self.OnBrowse)
        
        btn_build = ButtonBuild(self)
        btn_build.SetToolTip(wx.ToolTip(GT(u'Start building')))
        btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)
        
        btn_cancel = ButtonCancel(self)
        btn_cancel.SetToolTip(wx.ToolTip(GT(u'Cancel build')))
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)
        
        self.gauge = wx.Gauge(self, 100)
        
        self.ID_TIMER = wx.NewId()
        self.timer = wx.Timer(self, self.ID_TIMER)
        wx.EVT_TIMER(self, self.ID_TIMER, self.OnUpdateProgress)
        
        
        # *** Layout *** #
        
        Lstage_V1 = wx.BoxSizer(wx.VERTICAL)
        Lstage_V1.Add(label_stage, 0, wx.ALIGN_LEFT)
        Lstage_V1.Add(self.input_stage, 1, wx.EXPAND)
        
        Lstage_H1 = wx.BoxSizer(wx.HORIZONTAL)
        Lstage_H1.Add(Lstage_V1, 3, wx.ALIGN_TOP)
        Lstage_H1.Add(btn_browse_stage, 0, wx.ALIGN_TOP|wx.TOP, 7)
        
        Ltarget_V1 = wx.BoxSizer(wx.VERTICAL)
        Ltarget_V1.Add(label_target, 0, wx.ALIGN_LEFT)
        Ltarget_V1.Add(self.input_target, 1, wx.EXPAND)
        
        Ltarget_H1 = wx.BoxSizer(wx.HORIZONTAL)
        Ltarget_H1.Add(Ltarget_V1, 3, wx.ALIGN_TOP)
        Ltarget_H1.Add(btn_browse_target, 0, wx.ALIGN_TOP|wx.TOP, 7)
        
        Lbtn_H1 = wx.BoxSizer(wx.HORIZONTAL)
        Lbtn_H1.Add(btn_build, 1, wx.ALIGN_BOTTOM|wx.RIGHT, 2)
        Lbtn_H1.Add(btn_cancel, 1, wx.ALIGN_BOTTOM|wx.LEFT, 2)
        
        Lguage_H1 = wx.BoxSizer(wx.HORIZONTAL)
        Lguage_H1.Add(self.gauge, 1, wx.LEFT|wx.RIGHT, 5)
        
        Lmain_V = wx.BoxSizer(wx.VERTICAL)
        Lmain_V.AddSpacer(1, wx.EXPAND)
        Lmain_V.Add(Lstage_H1, -1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        Lmain_V.Add(Ltarget_H1, -1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        Lmain_V.Add(Lbtn_H1, -1, wx.ALIGN_CENTER|wx.ALL, 5)
        Lmain_V.Add(Lguage_H1, -1, wx.EXPAND|wx.ALL, 5)
        Lmain_V.AddSpacer(1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(Lmain_V)
        self.Layout()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.CenterOnParent()
    
    
    def OnBrowse(self, event=None):
        if event:
            debreate = self.GetParent().GetDebreateWindow()
            
            button_id = event.GetEventObject().GetId()
            
            if button_id == ID_STAGE:
                stage = GetDirDialog(debreate, GT(u'Choose Directory'))
                stage.CenterOnParent()
                
                if (ShowDialog(stage)):
                    self.input_stage.SetValue(stage.GetPath())
            
            elif button_id == ID_TARGET:
                target = GetFileSaveDialog(debreate, GT(u'Choose Filename'), (GT(u'Debian packages'), u'*.deb'), u'deb')
                target.CenterOnParent()
                
                if (ShowDialog(target)):
                    self.input_target.SetValue(target.GetPath())
    
    
    def OnBuild(self, event=None):
        debreate = self.GetParent().GetDebreateWindow()
        stage = self.input_stage.GetValue()
        target = self.input_target.GetValue()
        
        if not os.path.isdir(stage):
            err_msg = GT(u'Invalid stage directory')
            
            Logger.Warning(__name__, u'{}: {}'.format(err_msg, stage))
            ErrorDialog(debreate, err_msg, target).ShowModal()
            
            return
        
        target_path = os.path.dirname(target)
        if not os.access(target_path, os.W_OK):
            err_msg = GT(u'No write access to target path')
            
            Logger.Warning(__name__, u'{}: {}'.format(err_msg, target_path))
            ErrorDialog(debreate, err_msg, target_path).ShowModal()
            
            return
        
        BuildDebPackage(stage, target)
    
    
    ## Closes the Quick Build dialog & destroys instance
    def OnClose(self, event=None):
        self.EndModal(True)
    
    
    ## Updates the progress bar
    def OnUpdateProgress(self, event=None):
        self.gauge.Pulse()
