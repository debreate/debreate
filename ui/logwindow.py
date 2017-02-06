# -*- coding: utf-8 -*-

## \package dbr.logwindow

# MIT licensing
# See: docs/LICENSE.txt


import os, thread, threading, time, traceback, wx

from dbr.event              import EVT_REFRESH_LOG
from dbr.event              import RefreshLogEvent
from dbr.font               import GetMonospacedFont
from dbr.language           import GT
from dbr.log                import Logger
from globals                import ident
from globals.application    import APP_logo
from globals.fileio         import ReadFile
from globals.ident          import menuid
from globals.paths          import PATH_logs
from globals.strings        import GS
from input.text             import TextAreaPanel
from ui.dialog              import GetFileOpenDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from wiz.helper             import GetMainWindow
from wiz.helper             import GetMenu


# How often the log window will be refreshed
LOG_WINDOW_REFRESH_INTERVAL = 1

def SetLogWindowRefreshInterval(value):
    global LOG_WINDOW_REFRESH_INTERVAL
    LOG_WINDOW_REFRESH_INTERVAL = value

def GetLogWindowRefreshInterval():
    return LOG_WINDOW_REFRESH_INTERVAL


## Window displaying Logger messages
#
#  \param parent
#    Parent \b \e wx.Window instance
#  \param logFile
#    Absolute path to file where log contents are written/read
class LogWindow(wx.Dialog):
    def __init__(self, parent, logFile):
        wx.Dialog.__init__(self, parent, ident.DEBUG, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.SetIcon(APP_logo)
        
        self.LogFile = logFile
        
        self.SetTitle(self.LogFile)
        
        self.LogPollThread = None
        
        self.DspLog = TextAreaPanel(self, style=wx.TE_READONLY)
        self.DspLog.font_size = 8
        self.DspLog.SetFont(GetMonospacedFont(self.DspLog.font_size))
        
        btn_open = wx.Button(self, wx.ID_OPEN)
        btn_font = wx.Button(self, wx.ID_PREVIEW_ZOOM, GT(u'Font Size'))
        btn_refresh = wx.Button(self, wx.ID_REFRESH)
        btn_hide = wx.Button(self, wx.ID_CLOSE, GT(u'Hide'))
        
        # *** Event Handling *** #
        
        EVT_REFRESH_LOG(self, wx.ID_ANY, self.OnLogTimestampChanged)
        
        wx.EVT_BUTTON(self, wx.ID_OPEN, self.OnOpenLogFile)
        wx.EVT_BUTTON(self, wx.ID_PREVIEW_ZOOM, self.OnChangeFont)
        wx.EVT_BUTTON(self, wx.ID_REFRESH, self.RefreshLog)
        wx.EVT_BUTTON(self, wx.ID_CLOSE, self.OnClose)
        
        wx.EVT_CLOSE(self, self.OnClose)
        wx.EVT_SHOW(self, self.OnShow)
        wx.EVT_SHOW(GetMainWindow(), self.OnShowMainWindow)
        
        # *** Layout *** #
        
        layout_btnF1 = wx.FlexGridSizer(cols=5)
        layout_btnF1.AddGrowableCol(1, 1)
        layout_btnF1.Add(btn_open, 0, wx.LEFT, 5)
        layout_btnF1.AddStretchSpacer(1)
        layout_btnF1.Add(btn_font, 0, wx.RIGHT, 5)
        layout_btnF1.Add(btn_refresh, 0, wx.RIGHT, 5)
        layout_btnF1.Add(btn_hide, 0, wx.RIGHT, 5)
        
        layout_mainV1 = BoxSizer(wx.VERTICAL)
        layout_mainV1.Add(self.DspLog, 1, wx.ALL|wx.EXPAND, 5)
        layout_mainV1.Add(layout_btnF1, 0, wx.EXPAND|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_mainV1)
        self.Layout()
        
        self.SetMinSize(self.GetSize())
        
        self.SetSize(wx.Size(600, 600))
        
        self.AlignWithMainWindow()
        
        # Make sure log window is not shown at initialization
        self.Show(False)
        
        self.log_timestamp = os.stat(self.LogFile).st_mtime
    
    
    ## Destructor clears the log polling thead
    def __del__(self):
        if self.LogPollThread and self.LogPollThread.is_alive():
            self.LogPollThread.clear()
    
    
    ## Positions the log window relative to the main window
    def AlignWithMainWindow(self):
        debreate_pos = GetMainWindow().GetPosition()
        width = self.GetSize()[0]
        posX = debreate_pos[0] - width
        posY = debreate_pos[1]
        
        self.SetPosition(wx.Point(posX, posY))
    
    
    ## Hides the log window & clears contents
    def HideLog(self):
        self.Show(False)
        self.DspLog.Clear()
    
    
    ## Changes the font size
    def OnChangeFont(self, event=None):
        font_sizes = {
            7: 8,
            8: 10,
            10: 7,
        }
        
        current_font_size = self.DspLog.font_size
        
        for S in font_sizes:
            if S == current_font_size:
                self.DspLog.SetFont(GetMonospacedFont(font_sizes[S]))
                self.DspLog.font_size = font_sizes[S]
                
                return
        
        Logger.Error(__name__, GT(u'Can\'t change log window font'))
    
    
    ## Hides the log window when close event occurs
    def OnClose(self, event=None):
        self.HideLog()
    
    
    ## Called by refresh event to update the log display
    def OnLogTimestampChanged(self, event=None):
        self.RefreshLog()
    
    
    ## Opens a new log file
    def OnOpenLogFile(self, event=None):
        log_select = GetFileOpenDialog(self, GT(u'Open Log'), directory=PATH_logs)
        
        if ShowDialog(log_select):
            logFile = log_select.GetPath()
            
            if os.path.isfile(logFile):
                self.SetLogFile(logFile)
                
                return
            
            ShowErrorDialog(u'{}: {}'.format(GT(u'File does not exist'), logFile),
                    parent=self)
    
    
    ## Guarantees that menu item is synced with window's shown status
    def OnShow(self, event=None):
        menu_debug = GetMenu(menuid.DEBUG)
        
        # In case main window has been destroyed, but sub thread still active
        if GetMainWindow():
            window_shown = self.IsShown()
            m_checked = menu_debug.IsChecked(menuid.LOG)
            
            if m_checked != window_shown:
                menu_debug.Check(menuid.LOG, window_shown)
        
        else:
            Logger.Warn(__name__, u'Log thread still active!')
    
    
    ## Use an event to show the log window
    #
    #  By waiting until the main window emits a show event
    #    a separate item is not added in the system window
    #    list for the log.
    def OnShowMainWindow(self, event=None):
        main_window = GetMainWindow()
        
        # Make sure the main window has not been destroyed before showing log
        if main_window and main_window.IsShown():
            if GetMenu(menuid.DEBUG).IsChecked(menuid.LOG):
                self.ShowLog()
    
    
    ## Toggles the log window shown or hidden
    def OnToggleWindow(self, event=None):
        show = GetMenu(menuid.DEBUG).IsChecked(menuid.LOG)
        
        if show:
            self.ShowLog()
            return
        
        self.HideLog()
        
        if event:
            event.Skip(True)
    
    
    ## Creates a thread that polls for changes in log file
    def PollLogFile(self, args=None):
        self.LogPollThread = threading.current_thread()
        
        previous_timestamp = os.stat(self.LogFile).st_mtime
        while self.IsShown():
            current_timestamp = os.stat(self.LogFile).st_mtime
            
            if current_timestamp != previous_timestamp:
                print(u'Log timestamp changed, loading new log ...')
                
                wx.PostEvent(self, RefreshLogEvent(0))
                
                previous_timestamp = current_timestamp
            
            time.sleep(LOG_WINDOW_REFRESH_INTERVAL)
    
    
    ## Fills log with text file contents
    def RefreshLog(self, event=None):
        if os.path.isfile(self.LogFile):
            log_data = ReadFile(self.LogFile)
            
            if not self.DspLog.IsEmpty():
                self.DspLog.Clear()
            
            self.DspLog.SetValue(log_data)
            
            try:
                # Yield here to make sure last line is displayed
                # FIXME: Causes delay when debug enabled
                wx.SafeYield()
                self.DspLog.ShowPosition(self.DspLog.GetLastPosition())
            
            except wx.PyDeadObjectError:
                tb_error = GS(traceback.format_exc())
                
                Logger.Warn(__name__, u'Error refreshing log window. Details below:\n\n{}'.format(tb_error))
    
    
    ## Changes the file to be loaded & displayed
    #
    #  \param logFile
    #    Absolute path of file to load
    def SetLogFile(self, logFile):
        self.LogFile = logFile
        self.RefreshLog()
        self.SetTitle(self.LogFile)
    
    
    ## Shows the log window
    def ShowLog(self):
        self.RefreshLog()
        self.Show(True)
        
        thread.start_new_thread(self.PollLogFile, ())
