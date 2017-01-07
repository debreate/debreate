# -*- coding: utf-8 -*-

## \package globals.strings
#  
#  Module for manipulating strings & string lists

# MIT licensing
# See: docs/LICENSE.txt


## Checks if a text string is empty
#  
#  \param text
#        The string to be checked
def TextIsEmpty(text):
    return not text.strip(u' \t\n\r')


## Removes empty lines from a string or string list
#  
#  \param text
#    \b \e String or \b \e list to be checked
#  \return
#    \b \e String or \b \e tuple with empty lines removed
def RemoveEmptyLines(text):
    fmt_string = False
    
    if isinstance(text, (unicode, str)):
        fmt_string = True
        text = text.split(u'\n')
    
    elif isinstance(text, tuple):
        text = list(text)
    
    # Iterate in reverse to avoid skipping indexes
    for INDEX in reversed(range(len(text))):
        if TextIsEmpty(text[INDEX]):
            text.pop(INDEX)
    
    if fmt_string:
        return u'\n'.join(text)
    
    return tuple(text)


## Tests if a string can be converted to int or float
#  
#  \param string
#    \b \e String to be tested
def StringIsNumerical(string):
    try:
        float(string)
        return True
    
    except ValueError:
        return False


## Tests if a string is formatted for versioning
def StringIsVersioned(string):
    for P in string.split(u'.'):
        if not P.isnumeric():
            return False
    
    return True
