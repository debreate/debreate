# -*- coding: utf-8 -*-

## \package globals.debugging
#  
#  Helper functions for printing debugging messages to terminal

# MIT licensing
# See: docs/LICENSE.txt


import inspect


## Retrieves line number of script
def lineno():
    return inspect.currentframe().f_back.f_lineno


## Prints a message to the terminal
#  
#  \param message
#    \b \e string : Text do be output
#  \param mode
#    \b \e string : Message prefix printed in all capitals
#  \param script
#    \b \e string : Name of script from where function is being called
#  \param line
#    \b \e int : Line number of script where function is being called
#  \param newline
#    \b \e bool : If True, prepends an empty newline to printed message
def HelperMessage(message, mode, script=None, line=None, newline=True):
    if script:
        if line:
            script = u'{}:{}'.format(script, line)
        
        message = u'[{}] {}'.format(script, message)
    
    message = u'{}: {}'.format(mode.upper(), message)
    
    if newline:
        message = u'\n{}'.format(message)
    
    print(message)


## Prints a DEBUG message to the terminal
#  
#  \param message
#    \b \e string : Text do be output
#  \param script
#    \b \e string : Name of script from where function is being called
#  \param line
#    \b \e int : Line number of script where function is being called
#  \param newline
#    \b \e bool : If True, prepends an empty newline to printed message
def DebugMessage(message, script=None, line=None, newline=True):
    HelperMessage(message, u'DEBUG', script, line, newline)


## Prints a FIXME message to the terminal
#  
#  \param message
#    \b \e string : Text do be output
#  \param script
#    \b \e string : Name of script from where function is being called
#  \param line
#    \b \e int : Line number of script where function is being called
#  \param newline
#    \b \e bool : If True, prepends an empty newline to printed message
def FixmeMessage(message, script=None, line=None, newline=True):
    HelperMessage(message, u'FIXME', script, line, newline)


## Prints a TODO message to the terminal
#  
#  \param message
#    \b \e string : Text do be output
#  \param script
#    \b \e string : Name of script from where function is being called
#  \param line
#    \b \e int : Line number of script where function is being called
#  \param newline
#    \b \e bool : If True, prepends an empty newline to printed message
def TodoMessage(message, script=None, line=None, newline=True):
    HelperMessage(message, u'TODO', script, line, newline)
