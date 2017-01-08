# -*- coding: utf-8 -*-


## \package dbr.firstrun
# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.config     import ConfCode
from dbr.config     import InitializeConfig
from dbr.config     import default_config
from dbr.dialogs    import FirstRun
from dbr.dialogs    import ShowErrorDialog
from dbr.language   import GT
from dbr.log        import Logger


## Shows the first run dialog
def LaunchFirstRun(debreate_app):
    FR_dialog = FirstRun()
    debreate_app.SetTopWindow(FR_dialog)
    FR_dialog.ShowModal()
    
    init_conf_code = InitializeConfig()
    Logger.Debug(__name__, init_conf_code == ConfCode.SUCCESS)
    if (init_conf_code != ConfCode.SUCCESS) or (not os.path.isfile(default_config)):
        ShowErrorDialog(GT(u'Could not create configuration, exiting ...'))
        
        return init_conf_code
    
    FR_dialog.Destroy()
    
    # Delete first run dialog from memory
    del(FR_dialog)
    
    return init_conf_code
