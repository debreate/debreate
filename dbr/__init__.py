# -*- coding: utf-8 -*-

## \package dbr
#  Documentation for \b \e dbr package
#  
#  Most any member under a namespace can be called with
#    directly as a module of dbr.
#    
#    E.g: <i>dbr.<namespace>.<member></i> can be called as <i>dbr.<member></i>


# Logger needs to be set up first
from dbr.log import DebreateLogger

# Instantiate logger with default level & output path
Logger = DebreateLogger()

def DebugEnabled():
    return Logger.GetLogLevel() == Logger.DEBUG


from dbr.about import AboutDialog
from dbr.buttons import \
    ButtonAdd, ButtonBrowse, ButtonBrowse64, ButtonBuild, ButtonBuild64, \
    ButtonCancel, ButtonClear, ButtonConfirm, ButtonDel, ButtonImport, \
    ButtonNext, ButtonPipe, ButtonPrev, ButtonPreview, ButtonPreview64, \
    ButtonQuestion64, ButtonSave, ButtonSave64
from dbr.charctrl import CharCtrl
from dbr.constants import \
    system_licenses_path, \
    Mandatory, Recommended, Optional, Unused, Disabled, \
    DEFAULT_SIZE, DEFAULT_POS
from dbr.custom import \
    OutputLog, OverwriteDialog, SingleFileTextDropTarget, Combo, LCReport, \
    OpenDir, OpenFile, SaveFile
from dbr.help import HelpDialog
from dbr.functions import \
    GetCurrentVersion, FieldEnabled, RunSudo, RequirePython, TextIsEmpty, \
    GetYear, GetDate, GetTime, GetSystemLicensesList
from dbr.pathctrl import PathCtrl, PATH_DEFAULT, PATH_WARN
from dbr.templates import \
    GetLicenseTemplateFile, GetLicenseTemplatesList
from dbr.wizard import Wizard
from dbr.md5 import MD5

# Code after this does nothing. It is only used
# to document aliases with Doxygen.
if 0:
    ## Alias of dbr.functions.GetCurrentVersion
    def GetCurrentVersion():
        return 0
