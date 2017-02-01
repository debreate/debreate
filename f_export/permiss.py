# -*- coding: utf-8 -*-

## \package output.perm

# MIT licensing
# See: docs/LICENSE.txt


import os


## Sets files executable bit
#
#  FIXME: Check timestamp
#
#  \param target
#    Absolute path to file
#  \param executable
#    Sets or removes executable bit
def SetFileExecutable(target, executable=True):
    if os.path.isfile(target):
        if executable:
            mode = 0755
        
        else:
            mode = 0644
        
        os.chmod(target, mode)
        
        if os.access(target, mode):
            return True
    
    return False
