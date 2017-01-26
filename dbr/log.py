# -*- coding: utf-8 -*-

## \package dbr.log

# MIT licensing
# See: docs/LICENSE.txt


import os

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
#  \param log_level
#    \b \e int|str : The level at which messages will be output (default is 2 (ERROR))
#  \param log_path
#    \b \e str : The file to which messages will be written
class DebreateLogger:
    # Logging levels
    INFO, WARN, ERROR, DEBUG = range(4)
    
    log_level_list = {
        INFO: u'info',
        WARN: u'warn',
        ERROR: u'error',
        DEBUG: u'debug',
    }
    
    def __init__(self, log_level=ERROR, log_path=PATH_logs):
        ## The level at which to output log messages
        self.log_level = log_level
        
        # Directory where logs is written
        self.log_path = log_path
        
        # Filename output information
        self.log_file = u'{}/{}.log'.format(self.log_path, GetDate(dtfmt.LOG))
        
        # Forces space between header & first log entry (changed to None after first entry)
        self.no_strip = u'\n'
        
        self.OnInit()
    
    
    def OnInit(self):
        if not os.path.isdir(self.log_path):
            os.makedirs(self.log_path)
        
        # Initialize the log with date & time
        date_time = u'{} {}'.format(GetDate(dtfmt.LOG), GetTime(dtfmt.LOG))
        
        log_header = u'--------------- Log Start: {} ---------------\n'.format(date_time)
        
        '''
        # Add whitespace for new entries
        if os.path.isfile(self.log_file):
            log_header = u'\n\n{}'.format(log_header)
        '''
        
        # Write header to log file
        AppendFile(self.log_file, log_header, no_strip=u'\n')
    
    
    def OnClose(self):
        # Don't write to log if user deleted it
        if os.path.isfile(self.log_file):
            # Close the log with date & time
            date_time = u'{} {}'.format(GetDate(dtfmt.LOG), GetTime(dtfmt.LOG))
            
            log_footer = u'\n--------------- Log End:   {} ---------------\n\n'.format(date_time)
            
            AppendFile(self.log_file, log_footer, no_strip=u'\n')
    
    
    ## Checks if log can be written at supplied level
    #  
    #  \param l_level
    #        \b \e int|str : The desired message level to output
    #  \return
    #        \b \e tuple container int & unicode/str values of output level,
    #          or None for invalid log level
    def CheckLogLevel(self, l_level):
        
        # Check if l_level is of type INFO, WARN, ERROR, DEBUG
        if l_level in self.log_level_list:
            return l_level
        
        # Check if l_level is a string value of 'info', 'warn', 'error', 'debug'
        if isinstance(l_level, (unicode, str)):
            for L in self.log_level_list:
                if l_level.lower() == self.log_level_list[L].lower():
                    return L
        
        return None
    
    
    ## Prints a message to stdout & logs to file
    #  
    #  \param l_level
    #        \b \e int|str : Level at which to display the message
    def LogMessage(self, l_level, l_script, l_message, newline=False):
        l_level = self.CheckLogLevel(l_level)
        
        if (l_level in self.log_level_list) and (l_level <= self.log_level):
            l_string = self.log_level_list[l_level].upper()
            message = u'{}: [{}] {}'.format(l_string, l_script, l_message)
            
            if newline:
                message = u'\n{}'.format(message)
            
            # Message is shown in terminal
            print(message)
            
            # Open log for writing
            AppendFile(self.log_file, u'{}\n'.format(message), self.no_strip)
            
            # Allow stripping leading & trailing newlines from opened log file
            if self.no_strip:
                self.no_strip = None
    
    
    def Info(self, l_script, l_message, newline=False):
        self.LogMessage(u'info', l_script, l_message, newline)
    
    def Warn(self, l_script, l_message, newline=False):
        self.LogMessage(u'warn', l_script, l_message, newline)
    
    
    def Error(self, l_script, l_message, newline=False):
        self.LogMessage(u'error', l_script, l_message, newline)
    
    
    def Debug(self, l_script, l_message, newline=False):
        self.LogMessage(u'debug', l_script, l_message, newline)
    
    
    ## Sets the level at which messages will be output to terminal & log file
    #  
    #  \param l_level
    #        Level at which to print & output messages
    def SetLogLevel(self, l_level):
        log_set = False
        
        if l_level.isdigit():
            l_level = int(l_level)
        
        if l_level in self.log_level_list:
            self.log_level = l_level
            log_set = True
        
        elif isinstance(l_level, (unicode, str)):
            for L in self.log_level_list:
                if l_level.lower() == self.log_level_list[L].lower():
                    self.log_level = L
                    log_set = True
        
        return log_set
    
    
    def GetLogLevel(self):
        return self.log_level
    
    
    def GetLogFile(self):
        return self.log_file


# Instantiate logger with default level & output path
Logger = DebreateLogger()

## Checks if logging level is set to 'debug'
def DebugEnabled():
    return Logger.GetLogLevel() == Logger.DEBUG
