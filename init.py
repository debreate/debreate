#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

## Script to set configurations and launch Debreate
#  
#  Checks if the config file exists in ~/.config/debreate. If
#  not, a new file will be created (~/.config/debreate/config).
#  If the config file already exists but is corrupted, it will
#  reset it to its default settings.


import os, sys

import command_line as CL
from command_line   import GetParsedPath
from command_line   import parsed_commands
from command_line   import parsed_args_s
from command_line   import parsed_args_v
from globals.paths  import PATH_app
from globals.paths  import ConcatPaths

# *** Command line arguments
CL.ParseArguments(sys.argv[1:])


# Compiles python source into bytecode
if u'compile' in parsed_commands:
    import compileall, errno
    
    
    compile_dirs = (
        u'dbr',
        u'globals',
        u'wiz_bin',
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
        if os.path.isdir(D) and D in compile_dirs:
            D = ConcatPaths((PATH_app, D))
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


# Initialize app before importing local modules
debreate_app = wx.App()

from dbr.config             import ConfCode
from dbr.config             import default_config
from dbr.config             import GetDefaultConfigValue
from dbr.config             import InitializeConfig
from dbr.config             import ReadConfig
from dbr.compression        import GetCompressionId
from dbr.dialogs            import FirstRun
from dbr.error              import ShowError
from dbr.language           import GT
from dbr.language           import LOCALE_DIR
from dbr.language           import TRANSLATION_DOMAIN
from dbr.log                import Logger
from dbr.workingdir         import ChangeWorkingDirectory
from globals.application    import VERSION_string
from globals.constants      import INSTALLED
from globals.constants      import PREFIX
from globals.system         import PY_VER_STRING
from globals.system         import WX_VER_STRING
from main                   import MainWindow


# Log window refresh interval
if u'log-interval' in parsed_args_v:
    from dbr.log import SetLogWindowRefreshInterval
    if unicode(parsed_args_v[u'log-interval']).isnumeric():
        SetLogWindowRefreshInterval(int(parsed_args_v[u'log-interval']))


# FIXME: How to check of text domain is set correctly?
if INSTALLED:
    LOCALE_DIR = u'{}/share/locale'.format(PREFIX)
    gettext.install(TRANSLATION_DOMAIN, LOCALE_DIR, unicode=True)


script_name = os.path.basename(__file__)
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
    
    
    help_output = unicode(help_output[1])
    print(u'\n'.join(help_output.split(u'\n')[2:-1]))
    
    sys.exit(0)


if u'log-level' in parsed_args_v:
    Logger.SetLogLevel(parsed_args_v[u'log-level'])


Logger.Info(script_name, u'Python version: {}'.format(PY_VER_STRING))
Logger.Info(script_name, u'wx.Python version: {}'.format(WX_VER_STRING))
Logger.Info(script_name, u'Debreate version: {}'.format(VERSION_string))

# First time Debreate is run
if ReadConfig(u'__test__') == ConfCode.FILE_NOT_FOUND:
    FR_dialog = FirstRun()
    debreate_app.SetTopWindow(FR_dialog)
    FR_dialog.ShowModal()
    
    init_conf_code = InitializeConfig()
    Logger.Debug(script_name, init_conf_code == ConfCode.SUCCESS)
    if (init_conf_code != ConfCode.SUCCESS) or (not os.path.isfile(default_config)):
        fr_error = GT(u'Could not create configuration, exiting ...')
        ShowError(FR_dialog, fr_error, ConfCode.string[init_conf_code])
        
        exit_now = init_conf_code
    
    FR_dialog.Destroy()
    
    # Delete first run dialog from memory
    del(FR_dialog)
    

if exit_now:
    sys.exit(exit_now)


conf_values = {
    u'center': ReadConfig(u'center'),
    u'position': ReadConfig(u'position'),
    u'size': ReadConfig(u'size'),
    u'maximize': ReadConfig(u'maximize'),
    u'dialogs': ReadConfig(u'dialogs'),
    u'workingdir': ReadConfig(u'workingdir'),
    u'compression': ReadConfig(u'compression'),
}

for V in conf_values:
    key = V
    value = conf_values[V]
    
    if value == None:
        value = GetDefaultConfigValue(key)
    
    Logger.Debug(script_name, GT(u'Configuration key "{}" = "{}", type: {}'.format(key, unicode(value), type(value))))

Debreate = MainWindow(conf_values[u'position'], conf_values[u'size'])

if conf_values[u'center']:
    Debreate.Center()
if conf_values[u'maximize']:
    Debreate.Maximize()

# Set project compression
Debreate.SetCompression(GetCompressionId(conf_values[u'compression']))

working_dir = conf_values[u'workingdir']

parsed_path = GetParsedPath()
if parsed_path:
    project_file = parsed_path
    Logger.Debug(script_name, GT(u'Opening project from argument: {}').format(project_file))
    
    if Debreate.OpenProject(project_file):
        working_dir = os.path.dirname(project_file)

# Set working directory
ChangeWorkingDirectory(working_dir)

Debreate.Show(True)
debreate_app.MainLoop()

Logger.OnClose()

sys.exit(0)
