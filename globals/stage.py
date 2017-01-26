# -*- coding: utf-8 -*-

## \package globals.stage

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil

from globals.application    import APP_name
from globals.application    import VERSION_string
from globals.dateinfo       import GetDate
from globals.dateinfo       import dtfmt
from globals.strings        import GS


## Creates a directory for storing temporary files
#  
#  \return
#    Path to new stage directory, or None if failed
def CreateStage():
    stage = u'/tmp'
    
    # Use current working directory if no write access to /tmp
    if not os.access(stage, os.W_OK):
        stage = os.getcwd()
    
    #suffix = u'{}{}{}_'.format(GetYear(), GetMonthInt(), GetDayInt())
    
    #suffix = u'_temp'
    suffix = GetDate(dtfmt.STAMP)
    
    stage = u'{}/{}-{}_{}'.format(stage, GS(APP_name).lower(), VERSION_string, suffix)
    
    if os.access(os.path.dirname(stage), os.W_OK):
        # Start with fresh directory
        if os.path.isdir(stage):
            shutil.rmtree(stage)
        
        elif os.path.isfile(stage):
            os.remove(stage)
        
        os.makedirs(stage)
        
        if os.path.isdir(stage):
            return stage


## Remove a previously created stage directory
#  
#  \param stage
#    Absolute path to directory to remove
#  \return
#    \b \e True if stage does not exist
def RemoveStage(stage):
    if os.access(stage, os.W_OK):
        shutil.rmtree(stage)
    
    return not os.path.exists(stage)
