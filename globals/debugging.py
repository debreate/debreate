# -*- coding: utf-8 -*-

## \package globals.debugging
#  
#  Helper functions for printing debugging messages to terminal

# MIT licensing
# See: docs/LICENSE.txt


## Prints a message to the terminal
#  
#  \param message
#    \b \e string : Text do be output
#  \param mode
#    \b \e string : Message prefix printed in all capitals
#  \param newline
#    \b \e bool : If True, prepends an empty newline to printed message
def HelperMessage(message, mode, newline=True):
    message = u'{}: {}'.format(mode.upper(), message)
    
    if newline:
        message = u'\n{}'.format(message)
    
    print(message)


## Prints a DEBUG message to the terminal
#  
#  \param message
#    \b \e string : Text do be output
#  \param newline
#    \b \e bool : If True, prepends an empty newline to printed message
def DebugMessage(message, newline=True):
    HelperMessage(message, u'DEBUG', newline)


## Prints a TODO message to the terminal
#  
#  \param message
#    \b \e string : Text do be output
#  \param newline
#    \b \e bool : If True, prepends an empty newline to printed message
def TodoMessage(message, newline=True):
    HelperMessage(message, u'TODO', newline)
