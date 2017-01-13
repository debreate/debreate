# -*- coding: utf-8 -*-

## \package globals.mime

# MIT licensing
# See: docs/LICENSE.txt


from globals.commands   import GetCommandOutput
from globals.commands   import GetExecutable


## TODO: Doxygen
def GetFileMimeType(filename):
    CMD_file = GetExecutable(u'file')
    
    if not CMD_file:
        return None
    
    return GetCommandOutput(CMD_file, (u'--mime-type', u'--brief', filename,))
