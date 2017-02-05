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
from globals.paths          import PATH_logs
from globals.strings        import GS
from input.text             import TextAreaPanel
from ui.dialog              import GetFileOpenDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from wiz.helper             import GetMainWindow


# How often the log window will be refreshed
LOG_WINDOW_REFRESH_INTERVAL = 1

def SetLogWindowRefreshInterval(value):
    global LOG_WINDOW_REFRESH_INTERVAL
    LOG_WINDOW_REFRESH_INTERVAL = value

def GetLogWindowRefreshInterval():
    return LOG_WINDOW_REFRESH_INTERVAL


## Window displaying Logger messages
#  
#  FIXME: Creates separate task list window on initialization
#  TODO: Watch for changes in log file
class LogWindow(wx.Dialog):
    def __init__(self, parent, log_file):
        wx.Dialog.__init__(self, parent, ident.DEBUG, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.SetIcon(APP_logo)
        
        self.log_file = log_file
        
        self.SetTitle(self.log_file)
        
        self.main_process_id = os.getpid()
        self.log_poll_thread = None
        self.THREAD_ID = None
        self.MAIN_THREAD_ID = thread.get_ident()
        
        EVT_REFRESH_LOG(self, wx.ID_ANY, self.OnLogTimestampChanged)
        
        self.log = TextAreaPanel(self, style=wx.TE_READONLY)
        self.log.font_size = 8
        self.log.SetFont(GetMonospacedFont(self.log.font_size))
        
        btn_open = wx.Button(self, wx.ID_OPEN)
        wx.EVT_BUTTON(self, wx.ID_OPEN, self.OnOpenLogFile)
        
        btn_font = wx.Button(self, wx.ID_PREVIEW_ZOOM, GT(u'Font Size'))
        wx.EVT_BUTTON(self, wx.ID_PREVIEW_ZOOM, self.OnChangeFont)
        
        btn_refresh = wx.Button(self, wx.ID_REFRESH)
        wx.EVT_BUTTON(self, wx.ID_REFRESH, self.RefreshLog)
        
        btn_hide = wx.Button(self, wx.ID_CLOSE, GT(u'Hide'))
        wx.EVT_BUTTON(self, wx.ID_CLOSE, self.OnClose)
        
        layout_btnF1 = wx.FlexGridSizer(cols=5)
        layout_btnF1.AddGrowableCol(1, 1)
        layout_btnF1.Add(btn_open, 0, wx.LEFT, 5)
        layout_btnF1.AddStretchSpacer(1)
        layout_btnF1.Add(btn_font, 0, wx.RIGHT, 5)
        layout_btnF1.Add(btn_refresh, 0, wx.RIGHT, 5)
        layout_btnF1.Add(btn_hide, 0, wx.RIGHT, 5)
        
        layout_mainV1 = BoxSizer(wx.VERTICAL)
        layout_mainV1.Add(self.log, 1, wx.ALL|wx.EXPAND, 5)
        layout_mainV1.Add(layout_btnF1, 0, wx.EXPAND|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_mainV1)
        self.Layout()
        
        wx.EVT_CLOSE(self, self.OnClose)
        wx.EVT_SHOW(self, self.OnShow)
        wx.EVT_SHOW(GetMainWindow(), self.OnShowMainWindow)
        
        self.SetMinSize(self.GetSize())
        
        self.SetSize(wx.Size(600, 600))
        
        self.AlignWithMainWindow()
        
        # Make sure log window is not shown at initialization
        self.Show(False)
        
        self.log_timestamp = os.stat(self.log_file).st_mtime
    
    
    ## Destructor clears the log polling thead
    def __del__(self):
        if self.log_poll_thread and self.log_poll_thread.is_alive():
            self.log_poll_thread.clear()
    
    
    ## Positions the log window relative to the main window
    def AlignWithMainWindow(self):
        debreate_pos = GetMainWindow().GetPosition()
        width = self.GetSize()[0]
        posX = debreate_pos[0] - width
        posY = debreate_pos[1]
        
        self.SetPosition(wx.Point(posX, posY))
    
    
    ## Hides the log window
    def HideLog(self):
        self.Show(False)
        self.log.Clear()
    
    
    ## Changes the font size
    def OnChangeFont(self, event=None):
        font_sizes = {
            7: 8,
            8: 10,
            10: 7,
        }
        
        current_font_size = self.log.font_size
        
        for S in font_sizes:
            if S == current_font_size:
                self.log.SetFont(GetMonospacedFont(font_sizes[S]))
                self.log.font_size = font_sizes[S]
                
                return
        
        print(GT(u'Error: Can\'t change log window font'))
    
    
    ## Hides the log window when close event occurs
    def OnClose(self, event=None):
        self.HideLog()
    
    
    def OnLogTimestampChanged(self, event=None):
        self.RefreshLog()
    
    
    ## Opens a new log file
    def OnOpenLogFile(self, event=None):
        log_select = GetFileOpenDialog(self, GT(u'Open Log'), directory=PATH_logs)
        
        if ShowDialog(log_select):
            log_file = log_select.GetPath()
            
            if os.path.isfile(log_file):
                self.SetLogFile(log_file)
                
                return
            
            ShowErrorDialog(u'{}: {}'.format(GT(u'File does not exist'), log_file),
                    parent=self)
    
    
    ## Guarantess that menu item is synched with window's shown status
    def OnShow(self, event=None):
        main_window = GetMainWindow()
        
        # In case main window has been destroyed, but sub thread still active
        if main_window:
            window_shown = self.IsShown()
            m_checked = main_window.menu_debug.IsChecked(ident.LOG)
            
            if m_checked != window_shown:
                main_window.menu_debug.Check(ident.LOG, window_shown)
        
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
            if main_window.menu_debug.IsChecked(ident.LOG):
                self.ShowLog()
    
    
    ## Toggles the log window shown or hidden
    def OnToggleWindow(self, event=None):
        show = GetMainWindow().menu_debug.IsChecked(ident.LOG)
        
        if show:
            self.ShowLog()
            return
        
        self.HideLog()
        
        if event:
            event.Skip(True)
    
    
    ## Creates a thread that polls for changes in log file
    def PollLogFile(self, args=None):
        self.log_poll_thread = threading.current_thread()
        self.log_poll_thread.name = u'log_poll_thread'
        
        previous_timestamp = os.stat(self.log_file).st_mtime
        while self.IsShown():
            current_timestamp = os.stat(self.log_file).st_mtime
            
            if current_timestamp != previous_timestamp:
                print(u'Log timestamp changed, loading new log ...')
                
                wx.PostEvent(self, RefreshLogEvent(0))
                
                previous_timestamp = current_timestamp
            
            time.sleep(LOG_WINDOW_REFRESH_INTERVAL)
            
    
    
    ## Fills log with text file contents
    def RefreshLog(self, event=None):
        if os.path.isfile(self.log_file):
            log_data = ReadFile(self.log_file)
            
            if not self.log.IsEmpty():
                self.log.Clear()
            
            self.log.SetValue(log_data)
            
            try:
                # Yield here to make sure last line is displayed
                # FIXME: Causes delay when debug enabled
                wx.SafeYield()
                self.log.ShowPosition(self.log.GetLastPosition())
            
            except wx.PyDeadObjectError:
                tb_error = GS(traceback.format_exc())
                
                Logger.Warn(__name__, u'Error refreshing log window. Details below:\n\n{}'.format(tb_error))
    
    
    ## Changes the file to be loaded & displayed
    #  
    #  \param log_file
    #        \b \e unicode|str : File to load
    def SetLogFile(self, log_file):
        self.log_file = log_file
        self.RefreshLog()
        self.SetTitle(self.log_file)
    
    
    ## Shows the log window
    #  
    #  FIXME: Creates separate task list window on initialization
    def ShowLog(self):
        self.RefreshLog()
        self.Show(True)
        
        thread.start_new_thread(self.PollLogFile, ())
