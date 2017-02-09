# -*- coding: utf-8 -*-

## \package dbr.log

# MIT licensing
# See: docs/LICENSE.txt


import os, sys

from globals.dateinfo   import GetDate
from globals.dateinfo   import GetTime
from globals.dateinfo   import dtfmt
from globals.fileio     import AppendFile
from globals.paths      import PATH_logs


## A log class for outputting messages
#
#  TODO: Add 'quiet' (0) log level.
#
#  A log that will output messages to the terminal &
#    a log text file.
class DebreateLogger:
    # Logging levels
    INFO, WARN, ERROR, DEBUG, TEST = range(5)
    
    log_level_list = {
        INFO: u'info',
        WARN: u'warn',
        ERROR: u'error',
        DEBUG: u'debug',
        TEST: u'test',
    }
    
    ## Constructor
    #
    #  \param level
    #    \b \e int|str : The level at which messages will be output (default is 2 (ERROR))
    #  \param logsPath
    #    \b \e str : The file to which messages will be written
    def __init__(self, level=ERROR, logsPath=PATH_logs):
        ## The level at which to output messages
        self.LogLevel = level
        
        ## Directory where logs are located
        self.LogsDir = logsPath
        
        ## Log file path
        self.LogFile = u'{}/{}.log'.format(self.LogsDir, GetDate(dtfmt.LOG))
        
        ## Forces space between header & first log entry (changed to None after first entry)
        self.NoStrip = u'\n'
        
        self.OnInit()
    
    
    ## Opens a log file or creates a new one & adds log header with timestamp
    def OnInit(self):
        if not os.path.isdir(self.LogsDir):
            os.makedirs(self.LogsDir)
        
        # Initialize the log with date & time
        date_time = u'{} {}'.format(GetDate(dtfmt.LOG), GetTime(dtfmt.LOG))
        
        log_header = u'--------------- Log Start: {} ---------------\n'.format(date_time)
        
        '''
        # Add whitespace for new entries
        if os.path.isfile(self.LogFile):
            log_header = u'\n\n{}'.format(log_header)
        '''
        
        # Write header to log file
        AppendFile(self.LogFile, log_header, noStrip=u'\n')
    
    
    ## Adds footer with timestamp to log file
    def OnClose(self):
        # Don't write to log if user deleted it
        if os.path.isfile(self.LogFile):
            # Close the log with date & time
            date_time = u'{} {}'.format(GetDate(dtfmt.LOG), GetTime(dtfmt.LOG))
            
            log_footer = u'\n--------------- Log End:   {} ---------------\n\n'.format(date_time)
            
            AppendFile(self.LogFile, log_footer, noStrip=u'\n')
    
    
    ## Checks if log can be written at supplied level
    #  
    #  \param level
    #        \b \e int|str : The desired message level to output
    #  \return
    #        \b \e tuple container int & unicode/str values of output level,
    #          or None for invalid log level
    def CheckLogLevel(self, level):
        
        # Check if level is of type INFO, WARN, ERROR, DEBUG, TEST
        if level in self.LogLevel_list:
            return level
        
        # Check if level is a string value of 'info', 'warn', 'error', 'debug', 'test'
        if isinstance(level, (unicode, str)):
            for L in self.LogLevel_list:
                if level.lower() == self.LogLevel_list[L].lower():
                    return L
        
        return None
    
    
    ## Prints a message to stdout & logs to file
    #
    #  \param level
    #    Level at which to display the message
    #  \param module
    #    Name of the script/module where the message originates
    #  \param message
    #    Message to display
    #  \param newline
    #    If <b><i>True</i></b>, prepends an empty line to beginning of message
    #  \param pout
    #    Stream to which message should be output (stdout/stderr)
    def LogMessage(self, level, module, message, newline=False, pout=sys.stdout):
        level = self.CheckLogLevel(level)
        
        if (level in self.LogLevel_list) and (level <= self.LogLevel):
            l_string = self.LogLevel_list[level].upper()
            message = u'{}: [{}] {}'.format(l_string, module, message)
            
            if newline:
                message = u'\n{}'.format(message)
            
            # Message is shown in terminal
            if pout not in (sys.stdout, sys.stderr,):
                print(message)
            
            else:
                # Need to manually add newline when using sys.stdout/sys.stderr
                pout.write(u'{}\n'.format(message))
            
            # Open log for writing
            AppendFile(self.LogFile, u'{}\n'.format(message), self.NoStrip)
            
            # Allow stripping leading & trailing newlines from opened log file
            if self.NoStrip:
                self.NoStrip = None
    
    
    ## Show a log message at 'info' level
    #
    #  \param module
    #    Name of the script/module where the message originates
    #  \param message
    #    Message to display
    #  \param newline
    #    If <b><i>True</i></b>, prepends an empty line to beginning of message
    def Info(self, module, message, newline=False):
        self.LogMessage(u'info', module, message, newline)
    
    
    ## Show a log message at 'warn' level
    #
    #  \param module
    #    Name of the script/module where the message originates
    #  \param message
    #    Message to display
    #  \param newline
    #    If <b><i>True</i></b>, prepends an empty line to beginning of message
    def Warn(self, module, message, newline=False):
        self.LogMessage(u'warn', module, message, newline)
    
    
    ## Show a log message at 'error' level
    #
    #  Messages at 'error' level are written to stderr
    #
    #  \param module
    #    Name of the script/module where the message originates
    #  \param message
    #    Message to display
    #  \param newline
    #    If <b><i>True</i></b>, prepends an empty line to beginning of message
    def Error(self, module, message, newline=False):
        self.LogMessage(u'error', module, message, newline, pout=sys.stderr)
    
    
    ## Show a log message at 'debug' level
    #
    #  \param module
    #    Name of the script/module where the message originates
    #  \param message
    #    Message to display
    #  \param newline
    #    If <b><i>True</i></b>, prepends an empty line to beginning of message
    def Debug(self, module, message, newline=False):
        self.LogMessage(u'debug', module, message, newline)
    
    
    ## Show a log message at '' level
    #
    #  \param module
    #    Name of the script/module where the message originates
    #  \param message
    #    Message to display
    #  \param newline
    #    If <b><i>True</i></b>, prepends an empty line to beginning of message
    def Test(self, module, message, newline=False):
        self.LogMessage(u'test', module, message, newline)
    
    
    ## Sets the level at which messages will be output to terminal & log file
    #  
    #  \param level
    #        Level at which to print & output messages
    #  \return
    #    <b><i>True</i></b> if log level successfully set
    def SetLogLevel(self, level):
        log_set = False
        
        if level.isdigit():
            level = int(level)
        
        if level in self.LogLevel_list:
            self.LogLevel = level
            log_set = True
        
        elif isinstance(level, (unicode, str)):
            for L in self.LogLevel_list:
                if level.lower() == self.LogLevel_list[L].lower():
                    self.LogLevel = L
                    log_set = True
        
        return log_set
    
    
    ## Retrieves the current logging level
    #
    #  \return
    #    <b><i>Integer</i></b> logging level
    def GetLogLevel(self):
        return self.LogLevel
    
    
    ## Retrieves the current file be written to
    #
    #  \return
    #    <b><i>String</i></b> path of log file
    def GetLogFile(self):
        return self.LogFile


## Instantiated logger with default level & output path
Logger = DebreateLogger()

## Checks if logging level is set to 'debug'
#
#  \return
#    <b><i>True</i></b> if logging level is 'debug'
def DebugEnabled():
    return Logger.GetLogLevel() >= Logger.DEBUG
