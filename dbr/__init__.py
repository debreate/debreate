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


from dbr.about import AboutDialog
from dbr.buttons import \
    ButtonAdd, ButtonBrowse, ButtonBrowse64, ButtonBuild, ButtonBuild64, \
    ButtonCancel, ButtonClear, ButtonConfirm, ButtonDel, ButtonImport, \
    ButtonNext, ButtonPipe, ButtonPrev, ButtonPreview, ButtonPreview64, \
    ButtonQuestion64, ButtonSave, ButtonSave64
from dbr.charctrl import CharCtrl
from dbr.constants import \
    application_path, home_path, local_path, \
    system_licenses_path, \
    APP_NAME, VER_MAJ, VER_MIN, VER_REL, VERSION, VERSION_STRING, \
    HOMEPAGE, gh_project, sf_project, PROJECT_FILENAME_SUFFIX, DEBUG, \
    PY_VER_MAJ, PY_VER_MIN, PY_VER_REL, PY_VER_STRING, WX_VER_STRING, \
    ID_OVERWRITE, ID_APPEND, ID_BIN, ID_SRC, ID_DSC, ID_CNG, \
    ID_COPYRIGHT, \
    ICON_ERROR, ICON_INFORMATION, \
    Mandatory, Recommended, Optional, Unused, Disabled
from dbr.custom import \
    OutputLog, OverwriteDialog, SingleFileTextDropTarget, Combo, LCReport, \
    OpenDir, OpenFile, SaveFile
from dbr.functions import \
    GetCurrentVersion, FieldEnabled, RunSudo, CommandExists, RequirePython, TextIsEmpty, \
    GetFileSaveDialog, ShowDialog, GetYear, GetDateTime, GetSystemLicensesList
from dbr.language import GT
from dbr.message import MessageDialog
from dbr.pathctrl import PathCtrl, PATH_DEFAULT, PATH_WARN
from dbr.templates import \
    application_templates_path, application_licenses_path, application_licenses_templates, \
    local_templates_path, local_licenses_path, local_licenses_templates, \
    GetLicenseTemplateFile, GetLicenseTemplatesList
from dbr.wizard import Wizard
from dbr.md5 import MD5

# Code after this does nothing. It is only used
# to document aliases with Doxygen.
if 0:
    ## Alias of dbr.functions.GetCurrentVersion
    def GetCurrentVersion():
        return 0
    ## Alias of dbr.functions.CommandExists
    def CommandExists(command):
        return 0
