
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.moduleaccess

from libdbr.logger import Logger


## This class allows access to a 'name' attribute.
#
#  @param module_name
#    \b \e str : Ideally set to the module's __name__ attribute.
class ModuleAccessCtrl:
  def __init__(self, moduleName):
    Logger(__name__).deprecated(ModuleAccessCtrl)

    self.ModuleName = moduleName

  ## Retrieves the module_name attribute.
  #
  #  @return
  #    \b \e str : Module's name.
  def GetModuleName(self):
    return self.ModuleName
