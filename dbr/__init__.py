# -*- coding: utf-8 -*-

## \package dbr
#  Documentation for \b \e dbr package
#  
#  Most any member under a namespace can be called with
#    directly as a module of dbr.
#    
#    E.g: <i>dbr.<namespace>.<member></i> can be called as <i>dbr.<member></i>


from dbr.about          import AboutDialog
from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonBrowse
from dbr.buttons        import ButtonBrowse64
from dbr.buttons        import ButtonBuild
from dbr.buttons        import ButtonBuild64
from dbr.buttons        import ButtonCancel
from dbr.buttons        import ButtonClear
from dbr.buttons        import ButtonConfirm
from dbr.buttons        import ButtonDel
from dbr.buttons        import ButtonImport
from dbr.buttons        import ButtonNext
from dbr.buttons        import ButtonPipe
from dbr.buttons        import ButtonPrev
from dbr.buttons        import ButtonPreview
from dbr.buttons        import ButtonPreview64
from dbr.buttons        import ButtonQuestion64
from dbr.buttons        import ButtonSave
from dbr.buttons        import ButtonSave64
from dbr.charctrl       import CharCtrl
from dbr.custom         import Combo
from dbr.custom         import LCReport
from dbr.custom         import OpenDir
from dbr.custom         import OpenFile
from dbr.custom         import OutputLog
from dbr.custom         import OverwriteDialog
from dbr.custom         import SaveFile
from dbr.custom         import SingleFileTextDropTarget
from dbr.functions      import FieldEnabled
from dbr.functions      import GetCurrentVersion
from dbr.functions      import GetDate
from dbr.functions      import GetSystemLicensesList
from dbr.functions      import GetTime
from dbr.functions      import GetYear
from dbr.functions      import RequirePython
from dbr.functions      import RunSudo
from dbr.functions      import TextIsEmpty
from dbr.help           import HelpDialog
from dbr.log            import DebreateLogger
from dbr.md5            import MD5
from dbr.pathctrl       import PATH_DEFAULT
from dbr.pathctrl       import PATH_WARN
from dbr.pathctrl       import PathCtrl
from dbr.templates      import GetLicenseTemplateFile
from dbr.templates      import GetLicenseTemplatesList
from dbr.wizard         import Wizard
from globals.constants  import DEFAULT_POS
from globals.constants  import DEFAULT_SIZE
from globals.constants  import Disabled
from globals.constants  import Mandatory
from globals.constants  import Optional
from globals.constants  import Recommended
from globals.constants  import Unused
from globals.constants  import system_licenses_path


# Instantiate logger with default level & output path
Logger = DebreateLogger()

def DebugEnabled():
    return Logger.GetLogLevel() == Logger.DEBUG




# Code after this does nothing. It is only used
# to document aliases with Doxygen.
if 0:
    ## Alias of dbr.functions.GetCurrentVersion
    def GetCurrentVersion():
        return 0
