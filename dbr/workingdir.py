# -*- coding: utf-8 -*-

## \package dbr.workingdir

# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.config     import ReadConfig
from dbr.config     import WriteConfig
from dbr.log        import DebugEnabled
from dbr.log        import Logger
from globals.paths  import PATH_home


## Changes working directory & writes to config
#  
#  This method should be called in code instead of os.chdir
#    unless there is an explicit reason to do otherwise.
#  \param target_dir
#        \b \e unicode|str : Path to set as new working directory
def ChangeWorkingDirectory(target_dir):
    if DebugEnabled():
        Logger.Debug(__name__, u'ChangeWorkingDirectory: {}'.format(target_dir), newline=True)
        print(u'  Working dir before: {}'.format(os.getcwd()))
    
    success = False
    
    try:
        os.chdir(target_dir)
        config_dir = ReadConfig(u'workingdir')
        
        if config_dir != target_dir:
            WriteConfig(u'workingdir', target_dir)
            success = True
    
    except OSError:
        # Default to the user's home directory
        if os.path.isdir(PATH_home):
            os.chdir(PATH_home)
    
    if DebugEnabled():
        print(u'  Working dir after:  {}\n'.format(os.getcwd()))
    
    return success
