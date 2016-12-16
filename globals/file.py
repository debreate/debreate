# -*- coding: utf-8 -*-

## \package globals.file
#  
#  File I/O operations

# MIT licensing
# See: docs/LICENSE.txt


import codecs, os


## Retrieves the contents of a text file using utf-8 encoding
def ReadFile(filename):
    if not os.path.isfile(filename):
        return
    
    FILE_BUFFER = codecs.open(filename, u'r', u'utf-8')
    contents = u''.join(FILE_BUFFER).strip(u' \t\n')
    FILE_BUFFER.close()
    
    if contents:
        return contents


## Outputs text content to file using utf-8 encoding
#  
#  FIXME: Needs exception handling
def WriteFile(filename, contents):
    # Ensure we are dealing with a string
    if isinstance(contents, (tuple, list)):
        contents = u'\n'.join(contents).strip(u' \t\n\r')
    
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
