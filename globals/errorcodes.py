# -*- coding: utf-8 -*-

## \package globals.errno
#  
#  Redefines & adds some new codes to the system errno module

# MIT licensing
# See: docs/LICENSE.txt


import errno


class dbrerrno:
    def __init__(self):
        self = errno
        
        self.current_code = self.errorcode.keys()[-1]
        
        # ???: Should this be 0
        self.SUCCESS = -1
        self.errorcode[self.SUCCESS] = u'SUCCESS'
        
        self.EBADFT = self.AddNewCode(u'EBADFT')
    
    
    def AddNewCode(self, code_def):
        self.current_code += 1
        self.errorcode[self.current_code] = code_def
        
        return self.current_code
