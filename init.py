#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

## Script to set configurations and launch Debreate
#  
#  Checks if the config file exists in ~/.config/debreate. If
#  not, a new file will be created (~/.config/debreate/config).
#  If the config file already exists but is corrupted, it will
#  reset it to its default settings.


import sys

import command_line as CL
from command_line import parsed_commands, parsed_args_s, parsed_args_v,\
    GetParsedPath

# *** Command line arguments
CL.ParseArguments(sys.argv[1:])

# Modules to define required version of wx
import wxversion

if u'legacy' in parsed_commands:
    wxversion.select([u'2.8'])
else:
    wxversion.select([u'3.0', u'2.8'])

# System modules
import wx, os, gettext, commands

# Python & wx.Python encoding to UTF-8
if (sys.getdefaultencoding() != u'utf-8'):
    reload(sys)
    # FIXME: Recommended not to use
    sys.setdefaultencoding(u'utf-8')
wx.SetDefaultPyEncoding('UTF-8')


# Initialize app before importing local modules
debreate_app = wx.App()

# Local modules
from dbr import Logger
from dbr.language import GT, TRANSLATION_DOMAIN, LOCALE_DIR
from dbr.constants import PY_VER_STRING, WX_VER_STRING, VERSION_STRING,\
    INSTALLED, PREFIX
from dbr.config import ReadConfig, ConfCode, InitializeConfig,\
    GetDefaultConfigValue, default_config
from dbr.custom import FirstRun
from main import MainWindow
from dbr.compression import GetCompressionId
from dbr.error import ShowError

from globals import APP_name
from globals import PATH_app


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
    print(u'{} {}'.format(APP_name, VERSION_STRING))
    
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
Logger.Info(script_name, u'Debreate version: {}'.format(VERSION_STRING))

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

# Set working directory (Not necessary to call ChangeWorkingDirectory here)
os.chdir(conf_values[u'workingdir'])

# Set project compression
Debreate.SetCompression(GetCompressionId(conf_values[u'compression']))

parsed_path = GetParsedPath()
if parsed_path:
    project_file = parsed_path
    Logger.Debug(script_name, GT(u'Opening project from argument: {}').format(project_file))
    
    Debreate.OpenProject(project_file)

debreate_app.SetTopWindow(Debreate)
Debreate.Show(True)
debreate_app.MainLoop()

sys.exit(0)
