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
