
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module fields.cmdfield

from globals.strings import IsString
from globals.strings import RemoveEmptyLines
from libdbr.paths    import commandExists


## A field that requires a specific command or commands to be available on the system.
class CommandField:
  def __init__(self, commands=None, requireAll=False):
    self.Commands = commands
    self.RequireAll = requireAll

    if commands:
      if IsString(self.Commands) and " " in self.Commands:
        self.Commands = self.Commands.split(" ")
        self.Commands = RemoveEmptyLines(self.Commands)

    # check for the commands when the object is constructed
    self.Check()

  ## Disables the field if a command not found on system.
  def Check(self):
    if self.Commands:
      enabled = True
      if IsString(self.Commands):
        enabled = commandExists(self.Commands)
      else:
        if self.RequireAll:
          for CMD in self.Commands:
            if not commandExists(CMD):
              enabled = False
              break
        else:
          cmd_found = False
          for CMD in self.Commands:
            if commandExists(CMD):
              cmd_found = True
              break
          enabled = cmd_found

      self.Enable(enabled)

  ## Re-define in inheriting classes.
  def Enable(self, enabled):
    pass
