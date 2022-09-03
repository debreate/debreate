## \package globals.errno
#
#  Redefines & adds some new codes to the system errno module

# MIT licensing
# See: docs/LICENSE.txt


import wx, errno

# TODO: Convert these to dbrerror
ERR_DIR_NOT_AVAILABLE = wx.NewId()
ERR_FILE_READ = wx.NewId()
ERR_FILE_WRITE = wx.NewId()

error_definitions = {
    ERR_DIR_NOT_AVAILABLE: "Directory Not Available",
    ERR_FILE_READ: "Could Not Read File",
    ERR_FILE_WRITE: "Could Not Write File",
}


current_code = sorted(errno.errorcode.keys())[-1]
def AddNewCode(code_def):
    global current_code

    current_code += 1
    errno.errorcode[current_code] = code_def

    return current_code

dbrerrno = errno

dbrerrno.SUCCESS = 0
dbrerrno.errorcode[dbrerrno.SUCCESS] = "SUCCESS"

dbrerrno.EBADFT = AddNewCode("EBADFT")
dbrerrno.ECNCLD = AddNewCode("ECNCLD")
dbrerrno.FEMPTY = AddNewCode("FEMPTY")
dbrerrno.EUNKNOWN = AddNewCode("EUNKNOWN")
