# -*- coding: utf-8 -*-

## \package dbr.log


# System imports
import os

# Debreate imports
from dbr.constants import local_path
from dbr.functions import GetDate, GetTime


## A log class for outputting messages
#  
#  A log that will output messages to the terminal &
#    a log text file.
#  \param log_level
#    \b \e int|str : The level at which messages will be output
#  \param log_path
#    \b \e str : The file to which messages will be written
class DebreateLogger:
    # Logging levels
    INFO, WARNING, ERROR, DEBUG = range(4)
    
    log_level_list = {
        INFO: u'info',
        WARNING: u'warning',
        ERROR: u'error',
        DEBUG: u'debug',
    }
    
    def __init__(self, log_level=1, log_path=u'{}/logs'.format(local_path)):
        ## The level at which to output log messages
        #  
        #  Default is ERROR
        self.log_level = self.ERROR
        
        # Directory where logs is written
        self.log_path = log_path
        
        # Filename output information
        self.log_file = u'{}/{}.log'.format(self.log_path, GetDate())
        
        self.OnInit()
    
    
    def OnInit(self):
        if not os.path.isdir(self.log_path):
            os.makedirs(self.log_path)
        
        # Initialize the log with date & time
        date_time = u'{} {}'.format(GetDate(), GetTime())
        
        log_header = u'--------------- Start Log: {} ---------------\n\n'.format(date_time)
        
        # Add whitespace for new entries
        if os.path.isfile(self.log_file):
            log_header = u'\n\n{}'.format(log_header)
        
        # Write header to log file
        l_file = open(self.log_file, u'a')
        l_file.write(log_header)
        l_file.close()
    
    
    def OnClose(self):
        # Don't write to log if user deleted it
        if os.path.isfile(self.log_file):
            # Close the log with date & time
            date_time = u'{} {}'.format(GetDate(), GetTime())
            
            log_footer = u'\n--------------- End Log: {} ---------------\n\n'.format(date_time)
            
            l_file = open(self.log_file, u'a')
            l_file.write(log_footer)
            l_file.close()
    
    
    ## Checks if log can be written at suppliet level
    #  
    #  \param l_level
    #        \b \e int|str : The desired message level to output
    #  \return
    #        \b \e tuple container int & unicode/str values of output level,
    #          or None for invalid log level
    def CheckLogLevel(self, l_level):
        
        # Check if l_level is of type INFO, WARNING, ERROR, DEBUG
        if l_level in self.log_level_list:
            return l_level
        
        # Check if l_level is a string value of 'info', 'warning', 'error', 'debug'
        if isinstance(l_level, (unicode, str)):
            for L in self.log_level_list:
                if l_level.lower() == self.log_level_list[L].lower():
                    return L
        
        return None
    
    
    ## Prints a message to stdout & logs to file
    #  
    #  \param l_level
    #        \b \e int|str : Level at which to display the message
    def LogMessage(self, l_level, l_script, l_message):
        l_level = self.CheckLogLevel(l_level)
        
        if (l_level in self.log_level_list) and (l_level <= self.log_level):
            l_string = self.log_level_list[l_level].upper()
            message = u'{}: [{}] {}'.format(l_string, l_script, l_message)
            
            # Message is shown in terminal
            print(message)
            
            # Message is output to log file
            if not os.path.isdir(local_path):
                os.makedirs(local_path)
            
            # Open log for writing
            l_file = open(self.log_file, u'a')
            l_file.write(message)
            l_file.write(u'\n')
            l_file.close()
    
    
    def Info(self, l_script, l_message):
        self.LogMessage(u'info', l_script, l_message)
    
    def Warning(self, l_script, l_message):
        self.LogMessage(u'warning', l_script, l_message)
    
    
    def Error(self, l_script, l_message):
        self.LogMessage(u'error', l_script, l_message)
    
    
    def Debug(self, l_script, l_message):
        self.LogMessage(u'debug', l_script, l_message)
    
    
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
