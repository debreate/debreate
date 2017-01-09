# -*- coding: utf-8 -*-

## \package globals.fileio
#  
#  File I/O operations

# MIT licensing
# See: docs/LICENSE.txt


import codecs, os


## TODO: Doxygen
def AppendFile(filename, contents, no_strip=None, input_only=False):
    contents = u'{}\n{}'.format(ReadFile(filename, no_strip=no_strip), contents)
    
    # Only strip characters from text read from file
    if input_only:
        no_strip = None
    
    WriteFile(filename, contents, no_strip)


## Retrieves the contents of a text file using utf-8 encoding
#  
#  \param filename
#    \b \e string : Path to filename to read
#  \param split
#    \b \e bool : If True, output will be split into a list or tuple
#  \param convert
#    \b \e tuple|list : Converts the output to value type if 'split' is True
def ReadFile(filename, split=False, convert=tuple, no_strip=None):
    chars = u' \t\n\r'
    if no_strip:
        for C in no_strip:
            chars = chars.replace(C, u'')
    
    if not os.path.isfile(filename):
        return
    
    FILE_BUFFER = codecs.open(filename, u'r', u'utf-8')
    contents = u''.join(FILE_BUFFER).strip(chars)
    FILE_BUFFER.close()
    
    if split:
        contents = convert(contents.split(u'\n'))
    
    # FIXME: Should return contents even if it is empty string or list
    if contents:
        return contents


## Outputs text content to file using utf-8 encoding
#  
#  FIXME: Needs exception handling
#  FIXME: Set backup & restore on error/failure
#  \param filename
#    File to write to
#  \param contents
#    Text to write to file
#  \param no_strip
#    Characters to not strip from contents
def WriteFile(filename, contents, no_strip=None):
    chars = u' \t\n\r'
    if no_strip:
        for C in no_strip:
            chars = chars.replace(C, u'')
    
    # Ensure we are dealing with a string
    if isinstance(contents, (tuple, list)):
        contents = u'\n'.join(contents)
    
    contents = contents.strip(chars)
    
    if u'/' in filename:
        target_dir = os.path.dirname(filename)
    
    else:
        target_dir = os.getcwd()
        filename = u'{}/{}'.format(target_dir, filename)
    
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    
    FILE_BUFFER = codecs.open(filename, u'w', encoding=u'utf-8')
    FILE_BUFFER.write(contents)
    FILE_BUFFER.close()
    
    if not os.path.isfile(filename):
        return False
    
    return True
