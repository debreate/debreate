# -*- coding: utf-8 -*-

## \package globals.fileio
#
#  File I/O operations

# MIT licensing
# See: docs/LICENSE.txt


import codecs, os

from globals.paths      import ConcatPaths
from globals.strings    import GS


## Append text to end of a file
#
#  \param path
#    Absolute path of file to read/write
#  \param contents
#    Text to be written to file
#  \param noStrip
#    \b \e String of leading & trailing characters to not strip
#  \param inputOnly
#    Only strip characters from text read from file
def AppendFile(path, contents, noStrip=None, inputOnly=False):
    # Do not append to non-existent file
    if os.path.isfile(path):
        contents = u'{}\n{}'.format(ReadFile(path, noStrip=noStrip), contents)
    
    if inputOnly:
        noStrip = None
    
    WriteFile(path, contents, noStrip)


## Retrieves the contents of a text file using utf-8 encoding
#
#  \param path
#    Absolute path of file to read
#  \param split
#    If \b \e True, splits the text into a list
#  \param convert
#    Type of list to split contents into (can be \b \e tuple or \b \e list)
#    FIXME: Use boolean???
#  \param noStrip
#    \b \e String of leading & trailing characters to not strip
def ReadFile(path, split=False, convert=tuple, noStrip=None):
    strip_chars = u' \t\n\r'
    if noStrip:
        for C in noStrip:
            strip_chars = strip_chars.replace(C, u'')
    
    if not os.path.isfile(path):
        return
    
    FILE_BUFFER = codecs.open(path, u'r', u'utf-8')
    contents = u''.join(FILE_BUFFER).strip(strip_chars)
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
#
#  \param path
#    Absolute path of file to write
#  \param contents
#    Text to be written to file
#  \param noStrip
#    \b \e String of leading & trailing characters to not strip
def WriteFile(path, contents, noStrip=None):
    strip_chars = u' \t\n\r'
    if noStrip:
        for C in noStrip:
            strip_chars = strip_chars.replace(C, u'')
    
    # Ensure we are dealing with a string
    if isinstance(contents, (tuple, list)):
        contents = u'\n'.join(contents)
    
    contents = contents.strip(strip_chars)
    
    if u'/' in path:
        target_dir = os.path.dirname(path)
    
    else:
        target_dir = os.getcwd()
        path = u'{}/{}'.format(target_dir, path)
    
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    
    FILE_BUFFER = codecs.open(path, u'w', encoding=u'utf-8')
    FILE_BUFFER.write(contents)
    FILE_BUFFER.close()
    
    if not os.path.isfile(path):
        return False
    
    return True


## Retrieves a list of all files from the given path
#
#  \param path
#    Directory to search for license templates
#  \param flag
#    Filter files with given permission flags
def GetFiles(path, flag=None):
    file_list = []
    
    for PATH, DIRS, FILES in os.walk(path):
        for F in FILES:
            file_path = ConcatPaths((path, F))
            
            if os.path.isfile(file_path):
                # Don't add files that do not match 'flag' attributes
                if flag:
                    if not os.access(file_path, flag):
                        continue
                
                file_list.append(F)
    
    return sorted(file_list, key=GS.lower)


## Retrieve's a file's timestamp
#
#  \param path
#    Absolute path of file to read
#  \return
#    \b \e Float formatted timestamp
def GetTimestamp(path):
    if isinstance(path, FileItem):
        path = path.GetPath()
    
    return os.stat(path).st_mtime


## Checks if a file has been modified via timestamp
#
#  \param path
#    Absolute path of file to read
#  \param prevStamp
#    The previously saved timestamp
#  \return
#    \b \e True if timestamps are not the same
def TimestampChanged(path, prevStamp):
    return GetTimestamp(path) != prevStamp
