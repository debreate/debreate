# -*- coding: utf-8 -*-

## \package dbr.workingdir


# System modules
import os

# Local modules
from dbr.config import ReadConfig, WriteConfig


## Changes working directory & writes to config
#  
#  This method should be called in code instead of os.chdir
#    unless there is an explicit reason to do otherwise.
#  \param target_dir
#        \b \e unicode|str : Path to set as new working directory
def ChangeWorkingDirectory(target_dir):
    os.chdir(target_dir)
    config_dir = ReadConfig(u'workingdir')
    
    if config_dir != target_dir:
        WriteConfig(u'workingdir', target_dir)
        return
