# -*- coding: utf-8 -*-

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
    ERR_DIR_NOT_AVAILABLE: u'Directory Not Available',
    ERR_FILE_READ: u'Could Not Read File',
    ERR_FILE_WRITE: u'Could Not Write File',
}


current_code = errno.errorcode.keys()[-1]
def AddNewCode(code_def):
    global current_code
    
    current_code += 1
    errno.errorcode[current_code] = code_def
    
    return current_code

dbrerrno = errno

dbrerrno.SUCCESS = 0
dbrerrno.errorcode[dbrerrno.SUCCESS] = u'SUCCESS'

dbrerrno.EBADFT = AddNewCode(u'EBADFT')
dbrerrno.ECNCLD = AddNewCode(u'ECNCLD')
dbrerrno.FEMPTY = AddNewCode(u'FEMPTY')
dbrerrno.EUNKNOWN = AddNewCode(u'EUNKNOWN')
