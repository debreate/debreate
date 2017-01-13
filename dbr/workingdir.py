# -*- coding: utf-8 -*-

## \package dbr.workingdir

# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.config     import ReadConfig
from dbr.config     import WriteConfig
from globals.paths  import PATH_home


## Changes working directory & writes to config
#  
#  This method should be called in code instead of os.chdir
#    unless there is an explicit reason to do otherwise.
#  \param target_dir
#        \b \e unicode|str : Path to set as new working directory
def ChangeWorkingDirectory(target_dir):
    try:
        os.chdir(target_dir)
        config_dir = ReadConfig(u'workingdir')
        
        if config_dir != target_dir:
            WriteConfig(u'workingdir', target_dir)
            return True
    
    except OSError:
        # Default to the user's home directory
        if os.path.isdir(PATH_home):
            os.chdir(PATH_home)
        
        return False
