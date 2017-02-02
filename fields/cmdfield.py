# -*- coding: utf-8 -*-

## \package fields.cmdfield

# MIT licensing
# See: docs/LICENSE.txt


from globals.execute import GetExecutable
from globals.strings import IsString


## A field that requires a specific command or commands to be available on the system
class CommandField:
    def __init__(self, commands):
        self.Commands = commands
        
        # Check for the commands when the object is constructed
        self.Check()
    
    
    ## Disables the field if a command not found on system
    def Check(self):
        if IsString(self.Commands):
            self.Enable(GetExecutable(self.Commands))
            
            return
        
        for CMD in self.Commands:
            if not GetExecutable(CMD):
                self.Disable()
                
                return
        
        self.Enable()
