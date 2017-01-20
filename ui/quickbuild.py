# -*- coding: utf-8 -*-

## \package ui.quickbuild

# MIT licensing
# See: docs/LICENSE.txt


import os, thread, traceback, wx

from dbr.functions          import BuildDebPackage
from dbr.language           import GT
from dbr.log                import Logger
from dbr.moduleaccess       import ModuleAccessCtrl
from dbr.timer              import DebreateTimer
from dbr.timer              import EVT_TIMER_STOP
from globals                import ident
from globals.errorcodes     import dbrerrno
from globals.fileio         import ReadFile
from globals.paths          import ConcatPaths
from ui.button              import ButtonBrowse
from ui.button              import ButtonBuild
from ui.button              import ButtonCancel
from ui.dialog              import GetDirDialog
from ui.dialog              import GetFileSaveDialog
from ui.dialog              import OverwriteDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.dialog              import ShowMessageDialog


GAUGE_MAX = 100


class QuickBuild(wx.Dialog, ModuleAccessCtrl):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=GT(u'Quick Build'), pos=wx.DefaultPosition,
                size=wx.Size(400,260))
        ModuleAccessCtrl.__init__(self, __name__)
        
        self.title = self.GetTitle()
        
        label_stage = wx.StaticText(self, label=GT(u'Staged directory tree'))
        self.input_stage = wx.TextCtrl(self)
        self.input_stage.SetToolTip(wx.ToolTip(GT(u'Root directory of build tree')))
        
        btn_browse_stage = ButtonBrowse(self, ident.STAGE)
        btn_browse_stage.Bind(wx.EVT_BUTTON, self.OnBrowse)
        
        label_target = wx.StaticText(self, label=GT(u'Target file'))
        self.input_target = wx.TextCtrl(self)
        self.input_target.SetToolTip(wx.ToolTip(GT(u'Target output file')))
        
        btn_browse_target = ButtonBrowse(self, ident.TARGET)
        btn_browse_target.Bind(wx.EVT_BUTTON, self.OnBrowse)
        
        btn_build = ButtonBuild(self)
        btn_build.SetToolTip(wx.ToolTip(GT(u'Start building')))
        btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)
        
        btn_cancel = ButtonCancel(self)
        btn_cancel.SetToolTip(wx.ToolTip(GT(u'Cancel build')))
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)
        
        self.gauge = wx.Gauge(self, GAUGE_MAX)
        
        self.timer = DebreateTimer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdateProgress)
        self.Bind(EVT_TIMER_STOP, self.OnTimerStop)
        
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
        
        # For showing error dialog after build thread exits
        self.build_error = None
    
    
    ## TODO: Doxygen
    def Build(self, stage, target):
        completed_status = (0, GT(u'errors'))
        
        try:
            output = BuildDebPackage(stage, target)
            if output[0] == dbrerrno.SUCCESS:
                completed_status = (GAUGE_MAX, GT(u'finished'))
            
            else:
                self.build_error = (
                    GT(u'Could not build .deb package'),
                    GT(u'Is the staged directory formatted correctly?'),
                    stage,
                    output[1],
                )
        
        except:
            self.build_error = (
                GT(u'An unhandled error occured'),
                traceback.format_exc(),
                )
        
        self.timer.Stop()
        self.gauge.SetValue(completed_status[0])
        self.SetTitle(u'{} ({})'.format(self.title, completed_status[1]))
        self.Enable()
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event=None):
        if event:
            button_id = event.GetEventObject().GetId()
            
            if button_id == ident.STAGE:
                stage = GetDirDialog(self, GT(u'Choose Directory'))
                
                if (ShowDialog(stage)):
                    self.input_stage.SetValue(stage.GetPath())
            
            elif button_id == ident.TARGET:
                target = GetFileSaveDialog(self, GT(u'Choose Filename'), (GT(u'Debian packages'), u'*.deb'),
                        u'deb', False)
                
                if (ShowDialog(target)):
                    self.input_target.SetValue(target.GetPath())
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Check timestamp of created .deb package (should be done for main build as well)
    def OnBuild(self, event=None):
        stage = self.input_stage.GetValue()
        target = self.input_target.GetValue().rstrip(u'/')
        
        # Attempt to use DEBIAN/control file to set output filename. This is normally
        # done automatically by the dpkg command, but we need to set it manually to
        # check for overwriting a file.
        if os.path.isdir(target):
            control_file = ConcatPaths((stage, u'DEBIAN/control'))
            if os.path.isfile(control_file):
                control_lines = ReadFile(control_file, split=True)
                
                name = None
                version = None
                arch = None
                
                for LINE in control_lines:
                    if LINE.startswith(u'Package:'):
                        name = LINE.replace(u'Package: ', u'').strip()
                    
                    elif LINE.startswith(u'Version:'):
                        version = LINE.replace(u'Version: ', u'').strip()
                    
                    elif LINE.startswith(u'Architecture:'):
                        arch = LINE.replace(u'Architecture: ', u'').strip()
                
                if name and version and arch:
                    target = ConcatPaths((target, u'{}.deb'.format(u'_'.join((name, version, arch,)))))
        
        # Automatically add .deb filename extension if not present
        elif not target.lower().endswith(u'.deb'):
            target = u'{}.deb'.format(target)
        
        if not os.path.isdir(stage):
            ShowErrorDialog(GT(u'Stage directory does not exist'), stage, self, True)
            return
        
        target_path = os.path.dirname(target)
        if not os.path.isdir(target_path):
            ShowErrorDialog(GT(u'Target directory does not exist'), target_path, self, True)
            return
        
        elif not os.access(target_path, os.W_OK):
            ShowErrorDialog(GT(u'No write access to target directory'), target_path, self, True)
            return
        
        # Update the text input if target altered
        if target != self.input_target.GetValue():
            self.input_target.SetValue(target)
        
        # Check for pre-existing file
        if os.path.isfile(target):
            if not OverwriteDialog(self, target).Confirmed():
                return
        
        self.SetTitle(u'{} ({})'.format(self.title, GT(u'in progress')))
        
        # Don't allow dialog to be closed while build in progress
        self.Disable()
        self.timer.Start(100)
        
        self.build_thread = thread.start_new_thread(self.Build, (stage, target))
    
    
    ## Closes the Quick Build dialog & destroys instance
    def OnClose(self, event=None):
        self.EndModal(True)
    
    
    ## TODO: Doxygen
    def OnTimerStop(self, event=None):
        Logger.Debug(__name__, u'OnTimerStop')
        
        if not self.timer.IsRunning():
            Logger.Debug(__name__, GT(u'Timer is stopped'))
        
        else:
            Logger.Debug(__name__, GT(u'Timer is running'))
        
        if self.build_error:
            error_lines = self.build_error[:-1]
            error_output = self.build_error[-1]
            
            ShowErrorDialog(error_lines, error_output, self)
            
            # Needs to be reset or error dialog will successively show
            self.build_error = None
            
            return
        
        msg_lines = (
            GT(u'Quick build complete'),
            self.input_target.GetValue(),
        )
        ShowMessageDialog(msg_lines, GT(u'Build Complete'), module=__name__)
    
    
    ## Updates the progress bar
    def OnUpdateProgress(self, event=None):
        if event:
            if isinstance(event, wx.TimerEvent):
                if not self.timer.IsRunning():
                    Logger.Debug(__name__, GT(u'Timer stopped. Stopping gauge ...'))
                    
                    return
        
        self.gauge.Pulse()
