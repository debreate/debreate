# -*- coding: utf-8 -*-

## \package globals.cmdcheck

# MIT licensing
# See: docs/LICENSE.txt


import commands


## Check if a command is available on the system
#  
#  The system's 'whereis' command is used to
#    find locations for the target command.
#    If one of those locations is found to
#    be an executable file, a tuple containing
#    a True value & the location to the executable
#    is returned.
#  \param cmd
#        \b \e unicode|str : Command to check for
#  \return
#        \b \e unicode|str|None : A string path to executable or None if not found
def CommandExists(cmd):
    cmd_result, cmd = commands.getstatusoutput(u'which {}'.format(cmd))
    
    if not cmd_result:
        return cmd
    
    return None
