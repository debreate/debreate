#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

## Script to set configurations and launch Debreate
#  
#  Checks if the config file exists in ~/.config/debreate. If
#  not, a new file will be created (~/.config/debreate/config).
#  If the config file already exists but is corrupted, it will
#  reset it to its default settings.


import sys

# Modules to define required version of wx
import wxversion

if len(sys.argv) > 1 and sys.argv[1] == u'legacy':
    wxversion.select([u'2.8'])

else:
    wxversion.select([u'3.0', u'2.8'])


# System modules
import wx, os, gettext

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
    default_config, GetDefaultConfigValue
from dbr.custom import FirstRun
from main import MainWindow
import dbr.command_line as CL
from dbr.compression import GetCompressionId
from dbr.command_line import parsed_args_v

# FIXME: How to check of text domain is set correctly?
if INSTALLED:
    LOCALE_DIR = u'{}/share/locale'.format(PREFIX)
    gettext.install(TRANSLATION_DOMAIN, LOCALE_DIR, unicode=True)


script_name = os.path.basename(__file__)
if u'.py' in script_name:
    script_name = script_name.split(u'.py')[0]

Logger.Info(script_name, u'Python version: {}'.format(PY_VER_STRING))
Logger.Info(script_name, u'wx.Python version: {}'.format(WX_VER_STRING))
Logger.Info(script_name, u'Debreate version: {}'.format(VERSION_STRING))

exit_now = 0

# Get command line arguments
project_file = 0 # Set project file to false
if len(sys.argv) > 1:
    arg1 = sys.argv[1]
    filename = sys.argv[1] # Get the filename to show in window title
    if os.path.isfile(arg1):
        arg1 = open(arg1, u'r')
        project_file = arg1.read()
        arg1.close()

CL.ParseArguments(sys.argv[1:])
if u'log-level' in parsed_args_v:
    Logger.SetLogLevel(parsed_args_v[u'log-level'])


# First time Debreate is run
if ReadConfig(u'__test__') == ConfCode.FILE_NOT_FOUND:
    FR_dialog = FirstRun()
    debreate_app.SetTopWindow(FR_dialog)
    FR_dialog.ShowModal()
    FR_dialog.Destroy()
    
    init_conf_code = InitializeConfig()
    Logger.Debug(script_name, init_conf_code == ConfCode.SUCCESS)
    if (init_conf_code != ConfCode.SUCCESS) or (not os.path.isfile(default_config)):
        Logger.Error(script_name, GT(u'Could not create configuration, exiting ...'))
        exit_now = init_conf_code
    

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

if len(sys.argv) > 1 and os.path.isfile(sys.argv[-1]):
    project_file = sys.argv[-1]
    Logger.Debug(script_name, GT(u'Opening project from argument: {}').format(project_file))
    
    Debreate.OpenProject(project_file)

debreate_app.SetTopWindow(Debreate)
Debreate.Show(True)
debreate_app.MainLoop()

sys.exit(0)
