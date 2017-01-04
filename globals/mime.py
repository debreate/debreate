# -*- coding: utf-8 -*-

## \package globals.mime

# MIT licensing
# See: docs/LICENSE.txt


from dbr.log            import Logger
from globals.commands   import CMD_file
from globals.commands   import GetCommandOutput


## TODO: Doxygen
def GetFileMimeType(filename):
    if not CMD_file:
        Logger.Error(__name__, u'"file" command not present on system')
        return None
    
    return GetCommandOutput(CMD_file, (u'--mime-type', u'--brief', filename,))
