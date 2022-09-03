## \package globals.mime

# MIT licensing
# See: docs/LICENSE.txt


from globals.execute import GetCommandOutput
from globals.execute import GetExecutable


## TODO: Doxygen
def GetFileMimeType(filename):
    CMD_file = GetExecutable("file")

    if not CMD_file:
        return None

    return GetCommandOutput(CMD_file, ("--mime-type", "--brief", filename,))
