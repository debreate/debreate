#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

## \page init.py Initialization Script
#  Script to set configurations and launch Debreate
#  
#  Checks if the config file exists in ~/.config/debreate. If
#  not, a new file will be created (~/.config/debreate/config).
#  If the config file already exists but is corrupted, it will
#  reset it to its default settings.


import os, sys

from command_line   import GetParsedPath
from command_line   import ParseArguments
from command_line   import parsed_commands
from command_line   import parsed_args_s
from command_line   import parsed_args_v
from globals.paths  import PATH_app
from globals.paths  import ConcatPaths


## Module name displayed for Logger output.
#  Should be set to 'init' or actual name of executable script.
script_name = os.path.basename(__file__)

# *** Command line arguments
ParseArguments(sys.argv[1:])

# GetParsedPath must be called after ParseArguments
parsed_path = GetParsedPath()


# Compiles python source into bytecode
if u'compile' in parsed_commands:
    import compileall, errno
    
    
    compile_dirs = (
        u'dbr',
        u'globals',
        u'wizbin',
        )
    
    if not os.access(PATH_app, os.W_OK):
        print(u'ERROR: No write privileges for {}'.format(PATH_app))
        sys.exit(errno.EACCES)
    
    print(u'Compiling Python modules (.py) to bytecode (.pyc) ...\n')
    
    print(u'Compiling root directory: {}'.format(PATH_app))
    for F in os.listdir(PATH_app):
        if os.path.isfile(F) and F.endswith(u'.py') and F != u'init.py':
            F = ConcatPaths((PATH_app, F))
            compileall.compile_file(F)
    
    print
    
    for D in os.listdir(PATH_app):
        D = ConcatPaths((PATH_app, D))
        if os.path.isdir(D) and os.path.basename(D) in compile_dirs:
            print(u'Compiling directory: {}'.format(D))
            compileall.compile_dir(D)
            print
    
    sys.exit(0)


if u'clean' in parsed_commands:
    import errno
    
    
    if not os.access(PATH_app, os.W_OK):
        print(u'ERROR: No write privileges for {}'.format(PATH_app))
        sys.exit(errno.EACCES)
    
    print(u'Cleaning Python bytecode (.pyc) ...\n')
    
    for ROOT, DIRS, FILES in os.walk(PATH_app):
        for F in FILES:
            F = ConcatPaths((ROOT, F))
            
            if os.path.isfile(F) and F.endswith(u'.pyc'):
                print(u'Removing file: {}'.format(F))
                os.remove(F)
    
    sys.exit(0)


# Modules to define required version of wx
import wxversion

if u'legacy' in parsed_commands:
    try:
        wxversion.select([u'2.8'])
    
    except wxversion.VersionError:
        print(u'Warning: Could not find legacy version of wx on system. Reverting to default settings.')

# Ensure that "legacy" version isn't already in use
if not wxversion._selected:
    wxversion.select([u'3.0', u'2.8'])


import commands, gettext, wx

# Python & wx.Python encoding to UTF-8
if (sys.getdefaultencoding() != u'utf-8'):
    reload(sys)
    # FIXME: Recommended not to use
    sys.setdefaultencoding(u'utf-8')
wx.SetDefaultPyEncoding('UTF-8')


from dbr.app import DebreateApp

# Initialize app before importing local modules
debreate_app = DebreateApp()

from dbr.config             import ConfCode
from dbr.config             import GetAllConfigKeys
from dbr.config             import GetDefaultConfigValue
from dbr.language           import GetLocaleDir
from dbr.language           import GT
from dbr.language           import SetLocaleDir
from dbr.language           import TRANSLATION_DOMAIN
from dbr.log                import DebugEnabled
from dbr.log                import Logger
from dbr.workingdir         import ChangeWorkingDirectory
from globals.application    import VERSION_string
from globals.compression    import GetCompressionId
from globals.constants      import INSTALLED
from globals.constants      import PREFIX
from globals.strings        import GS
from globals.system         import PY_VER_STRING
from globals.system         import WX_VER_STRING
from main                   import MainWindow
from startup.firstrun       import LaunchFirstRun
from startup.startup        import SetAppInitialized


# FIXME: How to check if text domain is set correctly?
if INSTALLED:
    SetLocaleDir(ConcatPaths((PREFIX, u'share/locale')))
    gettext.install(TRANSLATION_DOMAIN, GetLocaleDir(), unicode=True)


if u'.py' in script_name:
    script_name = script_name.split(u'.py')[0]

exit_now = 0

if u'version' in parsed_args_s:
    print(VERSION_string)
    
    sys.exit(0)


if u'help' in parsed_args_s:
    if INSTALLED:
        help_output = commands.getstatusoutput(u'man debreate')
    
    else:
        help_output = commands.getstatusoutput(u'man --manpath="{}/man" debreate'.format(PATH_app))
    
    
    if help_output[0]:
        print(u'ERROR: Could not locate manpage')
        
        sys.exit(help_output[0])
    
    
    help_output = GS(help_output[1])
    print(u'\n'.join(help_output.split(u'\n')[2:-1]))
    
    sys.exit(0)


if u'log-level' in parsed_args_v:
    Logger.SetLogLevel(parsed_args_v[u'log-level'])


Logger.Info(script_name, u'Python version: {}'.format(PY_VER_STRING))
Logger.Info(script_name, u'wx.Python version: {}'.format(WX_VER_STRING))
Logger.Info(script_name, u'Debreate version: {}'.format(VERSION_string))
Logger.Info(script_name, u'Logging level: {}'.format(Logger.GetLogLevel()))

# Check for & parse existing configuration
conf_values = GetAllConfigKeys()

if not conf_values:
    Logger.Debug(script_name, u'Launching First Run dialog ...')
    
    first_run = LaunchFirstRun(debreate_app)
    if not first_run == ConfCode.SUCCESS:
        
        sys.exit(first_run)
    
    conf_values = GetAllConfigKeys()

# Check that all configuration values are okay
for V in conf_values:
    key = V
    value = conf_values[V]
    
    # ???: Redundant???
    if value == None:
        value = GetDefaultConfigValue(key)
    
    Logger.Debug(script_name, GT(u'Configuration key "{}" = "{}", type: {}'.format(key, GS(value), type(value))))
    
    # FIXME: ConfCode values are integers & could cause problems with config values
    if conf_values[V] in (ConfCode.FILE_NOT_FOUND, ConfCode.KEY_NOT_DEFINED, ConfCode.KEY_NO_EXIST,):
        first_run = LaunchFirstRun(debreate_app)
        if not first_run == ConfCode.SUCCESS:
            sys.exit(first_run)
        
        break


Debreate = MainWindow(conf_values[u'position'], conf_values[u'size'])
debreate_app.SetMainWindow(Debreate)
Debreate.InitWizard()

if DebugEnabled():
    from ui.logwindow import LogWindow
    
    # Log window refresh interval
    if u'log-interval' in parsed_args_v:
        from ui.logwindow import SetLogWindowRefreshInterval
        
        if GS(parsed_args_v[u'log-interval']).isnumeric():
            SetLogWindowRefreshInterval(int(parsed_args_v[u'log-interval']))
    
    Debreate.SetLogWindow(LogWindow(Debreate, Logger.GetLogFile()))

if conf_values[u'maximize']:
    Debreate.Maximize()

elif conf_values[u'center']:
    from system.display import CenterOnPrimaryDisplay
    
    # NOTE: May be a few pixels off
    CenterOnPrimaryDisplay(Debreate)

# Set project compression
Debreate.SetCompression(GetCompressionId(conf_values[u'compression']))

working_dir = conf_values[u'workingdir']

if parsed_path:
    project_file = parsed_path
    Logger.Debug(script_name, GT(u'Opening project from argument: {}').format(project_file))
    
    if Debreate.ProjectOpen(project_file):
        working_dir = os.path.dirname(project_file)

# Set working directory (do not call os.chdir in case of opening project)
ChangeWorkingDirectory(working_dir)

Debreate.Show(True)

# Wait for window to be constructed (prevents being marked as dirty project after initialization)
wx.Yield()

# Set initializaton state to 'True'
SetAppInitialized()

debreate_app.MainLoop()

Logger.OnClose()

sys.exit(0)
