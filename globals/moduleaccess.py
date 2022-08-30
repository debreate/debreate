## \package dbr.moduleaccess

# MIT licensing
# See: docs/LICENSE.txt


## This class allows access to a 'name' attribute
#
#  \param module_name
#		\b \e str : Ideally set to the module's __name__ attribute
class ModuleAccessCtrl:
	def __init__(self, moduleName):
		self.ModuleName = moduleName


	## Retrieves the module_name attribute
	#
	#  \return
	#		\b \e str : Module's name
	def GetModuleName(self):
		return self.ModuleName
