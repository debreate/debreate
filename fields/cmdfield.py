# -*- coding: utf-8 -*-

## \package fields.cmdfield

# MIT licensing
# See: docs/LICENSE.txt


from globals.cmdcheck   import CommandExists
from globals.strings    import IsString
from globals.strings    import RemoveEmptyLines


## A field that requires a specific command or commands to be available on the system
class CommandField:
    def __init__(self, commands=None, requireAll=False):
        self.Commands = commands
        self.RequireAll = requireAll
        
        if commands:
            if IsString(self.Commands) and u' ' in self.Commands:
                self.Commands = self.Commands.split(u' ')
                self.Commands = RemoveEmptyLines(self.Commands)
        
        # Check for the commands when the object is constructed
        self.Check()
    
    
    ## Disables the field if a command not found on system
    def Check(self):
        if self.Commands:
            enabled = True
            
            if IsString(self.Commands):
                # FIXME: CommandExists should return boolean
                #self.Enable(not not CommandExists(self.Commands))
                enabled = not not CommandExists(self.Commands)
            
            else:
                if self.RequireAll:
                    for CMD in self.Commands:
                        if not CommandExists(CMD):
                            enabled = False
                            
                            break
                
                else:
                    cmd_found = False
                    for CMD in self.Commands:
                        if CommandExists(CMD):
                            cmd_found = True
                            
                            break
                    
                    enabled = cmd_found
            
            self.Enable(enabled)
