# -*- coding: utf-8 -*-

## \package ui.distcache

# MIT licensing
# See: docs/LICENSE.txt


import os, traceback, wx
from wx.combo import OwnerDrawnComboBox

from dbr.language           import GT
from dbr.log                import Logger
from dbr.moduleaccess       import ModuleAccessCtrl
from dbr.timer              import DebreateTimer
from dbr.timer              import EVT_TIMER_STOP
from globals                import ident
from globals.fileio         import ReadFile
from globals.system         import FILE_distnames
from globals.system         import GetOSDistNames
from globals.system         import UpdateDistNamesCache
from globals.threads        import Thread
from globals.wizardhelper   import GetField
from ui.dialog              import BaseDialog
from ui.dialog              import ShowErrorDialog
from ui.dialog              import ShowMessageDialog
from ui.panel               import BorderedPanel
from ui.progress            import ProgressDialog
from ui.textpreview         import TextPreview


## Dialog displaying controls for updating distribution names cache file
class DistNamesCacheDialog(BaseDialog, ModuleAccessCtrl):
    def __init__(self):
        BaseDialog.__init__(self, title=GT(u'Update Dist Names Cache'),
                style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        ModuleAccessCtrl.__init__(self, __name__)
        
        self.SetMinSize(wx.Size(300, 150))
        
        txt_types = wx.StaticText(self, label=GT(u'Include the following:'))
        
        pnl_types = BorderedPanel(self)
        
        self.chk_unstable = wx.CheckBox(pnl_types, label=GT(u'Unstable'))
        self.chk_obsolete = wx.CheckBox(pnl_types, label=GT(u'Obsolete'))
        self.chk_generic = wx.CheckBox(pnl_types, label=GT(u'Generic (Debian names only)'))
        
        self.btn_preview = wx.Button(self, label=GT(u'Preview cache'))
        btn_update = wx.Button(self, label=GT(u'Update cache'))
        btn_clear = wx.Button(self, label=GT(u'Clear cache'))
        
        # Keep preview dialog in memory so position/size is saved
        self.preview = TextPreview(self, title=GT(u'Available Distribution Names'),
                size=(500,400))
        
        # Is instantiated as ProgressDialog when OnUpdateCache is called
        self.progress = None
        self.timer = DebreateTimer(self)
        
        # For setting error messages from other threads
        self.error_message = None
        
        # *** Event Handling *** #
        
        self.btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewCache)
        btn_update.Bind(wx.EVT_BUTTON, self.OnUpdateCache)
        btn_clear.Bind(wx.EVT_BUTTON, self.OnClearCache)
        
        self.Bind(wx.EVT_TIMER, self.OnTimerEvent)
        self.Bind(EVT_TIMER_STOP, self.OnTimerStop)
        
        # *** Layout *** #
        
        lyt_types = wx.BoxSizer(wx.VERTICAL)
        lyt_types.AddSpacer(5)
        
        for CHK in (self.chk_unstable, self.chk_obsolete, self.chk_generic,):
            lyt_types.Add(CHK, 0, wx.LEFT|wx.RIGHT, 5)
        
        lyt_types.AddSpacer(5)
        
        pnl_types.SetAutoLayout(True)
        pnl_types.SetSizerAndFit(lyt_types)
        pnl_types.Layout()
        
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(self.btn_preview, 1)
        lyt_buttons.Add(btn_update, 1)
        lyt_buttons.Add(btn_clear, 1)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(txt_types, 0, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        lyt_main.Add(pnl_types, 0, wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(lyt_buttons, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Post-layout Actions *** #
        
        if not os.path.isfile(FILE_distnames):
            self.btn_preview.Disable()
        
        if self.Parent:
            self.CenterOnParent()
    
    
    ## Checks for present error message & displays dialog
    #  
    #  \return
    #    \b \e False if no errors present
    def CheckErrors(self):
        if self.error_message:
            ShowErrorDialog(self.error_message, parent=self, linewrap=410)
            
            # Clear error message & return
            self.error_message = None
            return True
        
        return False
    
    
    ## Deletes the distribution names cache file
    def OnClearCache(self, event=None):
        if os.path.isfile(FILE_distnames):
            os.remove(FILE_distnames)
            
            # Update list on changelog page
            distname_input = GetField(ident.CHANGELOG, ident.DIST)
            if isinstance(distname_input, OwnerDrawnComboBox):
                distname_input.Set(GetOSDistNames())
            
            self.btn_preview.Disable()
        
        cache_exists = os.path.exists(FILE_distnames)
        
        self.btn_preview.Enable(cache_exists)
        return not cache_exists
    
    
    ## Opens cache file for previewing
    def OnPreviewCache(self, event=None):
        self.preview.SetValue(ReadFile(FILE_distnames))
        self.preview.ShowModal()
    
    
    ## Calls Pulse method on progress dialog when timer event occurs
    def OnTimerEvent(self, event=None):
        if self.progress:
            self.progress.Pulse()
    
    
    ## Closes & resets the progress dialog to None when timer stops
    def OnTimerStop(self, event=None):
        if self.progress:
            self.progress.EndModal(0)
            self.progress = None
        
        return not self.progress
    
    
    ## Creates/Updates the distribution names cache file
    def OnUpdateCache(self, event=None):
        try:
            # Timer must be started before executing new thread
            self.timer.Start(100)
            
            if not self.timer.IsRunning():
                self.error_message = GT(u'Could not start progress dialog timer')
                self.CheckErrors()
                return False
            
            self.Disable()
            
            # Start new thread for updating cache in background
            Thread(self.UpdateCache, None).Start()
            
            # Create the progress dialog & start timer
            # NOTE: Progress dialog is reset by timer stop event
            self.progress = ProgressDialog(self, message=GT(u'Contacting remote sites'),
                    style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
            
            # Use ShowModal to wait for timer to stop before continuing
            self.progress.ShowModal()
            
            self.Enable()
            
            if self.CheckErrors():
                return False
            
            # FIXME: Should check timestamps to make sure file was updated
            cache_updated = os.path.isfile(FILE_distnames)
            
            if cache_updated:
                distname_input = GetField(ident.CHANGELOG, ident.DIST)
                
                if isinstance(distname_input, OwnerDrawnComboBox):
                    distname_input.Set(GetOSDistNames())
                
                else:
                    ShowMessageDialog(
                        GT(u'The distribution names cache has been updated but Debreate needs to restart to reflect the changes on the changelog page'),
                        parent=self, linewrap=410)
            
            self.btn_preview.Enable(cache_updated)
            
            return cache_updated
        
        except:
            # Make sure dialog is re-enabled
            self.Enable()
            
            # Make sure progress dialog & background thread instances are reset to None
            if self.progress:
                self.progress.EndModal(0)
                self.progress = None
            
            cache_exists = os.path.isfile(FILE_distnames)
            
            err_msg = GT(u'An error occurred when trying to update the distribution names cache')
            err_msg2 = GT(u'The cache file exists but may not have been updated')
            if cache_exists:
                err_msg = u'{}\n\n{}'.format(err_msg, err_msg2)
            
            ShowErrorDialog(err_msg, traceback.format_exc(), self)
            
            self.btn_preview.Enable(cache_exists)
        
        return False
    
    
    ## Method that does the actual updating of the names cache list
    #  
    #  Called from a new thread
    #  FIXME: Show error if could not contact 1 or more remote sites???
    def UpdateCache(self, args=None):
        Logger.Debug(__name__, GT(u'Updating cache ...'))
        
        UpdateDistNamesCache(self.chk_unstable.GetValue(), self.chk_obsolete.GetValue(),
                self.chk_generic.GetValue())
        
        self.timer.Stop()
