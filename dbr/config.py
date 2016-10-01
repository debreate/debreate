# -*- coding: utf-8 -*-

## \package dbr.config
#  
#  Parsing & writing configuration.


# System modules
import wx, os

# Local modules
from dbr import Logger
from dbr.language import GT
from dbr.constants import home_path, compression_formats, ID_ZIP_BZ2
from dbr.functions import TextIsEmpty, GetBoolean, GetInteger, GetIntTuple


## Configuration codes
class ConfCode:
    SUCCESS = 0
    ERR_READ = wx.NewId()
    ERR_WRITE = wx.NewId()
    FILE_NOT_FOUND = wx.NewId()
    WRONG_TYPE = wx.NewId()
    KEY_NO_EXIST = wx.NewId()
    KEY_NOT_DEFINED = wx.NewId()

# Version of configuration to use
config_version = (1, 1)

# Default configuration
default_config_dir = u'{}/.config/debreate'.format(home_path)
default_config = u'{}/config'.format(default_config_dir)

# Key type definitions
key_types = {
    u'center': GetBoolean,
    u'dialogs': GetBoolean,
    u'maximize': GetBoolean,
    u'position': GetIntTuple,
    u'size': GetIntTuple,
    u'workingdir': unicode,
    u'compression': unicode,
}

default_config_values = {
    u'center': True,
    u'dialogs': False,
    u'maximize': False,
    u'position': (0, 0),
    u'size': (800, 640),
    u'workingdir': home_path,
    u'compression': compression_formats[ID_ZIP_BZ2],
}


## Opens configuration & searches for key
#  
#  \param k_name
#        \b \e unicode|str : Key to search for
#  \return
#        Value of key if found, otherwise ConfCode
def ReadConfig(k_name, conf=default_config):
    Logger.Debug(__name__, GT(u'Reading configuration file: {}'.format(conf)))
    
    if not os.path.isfile(conf):
        Logger.Warning(__name__, u'Configuration file does not exist: {}'.format(conf))
        return ConfCode.FILE_NOT_FOUND
    
    # Use the string '__test__' for test when app is initialized
    if k_name == u'__test__':
        return ConfCode.SUCCESS
    
    # Only read pre-defined keys
    if k_name not in key_types:
        Logger.Warning(__name__, u'Cannot read from config, key not defined: {}'.format(k_name))
        return ConfCode.KEY_NOT_DEFINED
    
    conf_opened = open(conf, u'r')
    conf_lines = conf_opened.read().split(u'\n')
    conf_opened.close()
    
    for L in conf_lines:
        if u'=' in L:
            key = L.split(u'=')
            value = key[1]
            key = key[0]
            
            if k_name == key:
                value = key_types[key](value)
                
                Logger.Debug(__name__, u'Retrieved key-value: {}={}, value type: {}'.format(key, value, type(value)))
                return value
    
    Logger.Warning(__name__, u'Configuration does not contain key: {}'.format(k_name))
    return ConfCode.KEY_NO_EXIST


## Writes a key=value combination to configuration
#  
#  \param k_name
#        \b \e unicode|str : Key to write
#  \param k_value
#        \b \e unicode|str|tuple|int|bool : Value of key
#  \return
#        \b \e int : ConfCode
def WriteConfig(k_name, k_value, conf=default_config):
    conf_dir = os.path.dirname(conf)
    
    if not os.path.isdir(conf_dir):
        if os.path.exists(conf_dir):
            Logger.Error(__name__, u'Cannot create config directory, file exists: {}'.format(conf_dir))
            return ConfCode.ERR_WRITE
        
        os.makedirs(conf_dir)
    
    # Only write pre-defined keys
    if k_name not in key_types:
        Logger.Warning(__name__, u'Cannot write to config, key not defined: {}'.format(k_name))
        return ConfCode.KEY_NOT_DEFINED
    
    # Make sure we are writing the correct type
    k_value = key_types[k_name](k_value)
    
    if k_value == None:
        Logger.Warning(__name__, u'Value is of wrong type for key "{}"'.format(k_name))
        return ConfCode.WRONG_TYPE
    
    # tuple is the only type we need to format
    if type(k_value) == tuple:
        k_value = u'{},{}'.format(unicode(k_value[0]), unicode(k_value[1]))
    else:
        k_value = unicode(k_value)
    
    conf_text = wx.EmptyString
    
    # Save current config to buffer
    if os.path.exists(conf):
        if not os.path.isfile(conf):
            Logger.Error(__name__, u'Cannot open config for writing, directory exists: {}'.format(conf))
            return ConfCode.ERR_WRITE
        
        conf_opened = open(conf, u'r')
        conf_text = conf_opened.read()
        conf_opened.close()
    
    else:
        conf_text = u'[CONFIG-{}.{}]'.format(unicode(config_version[0]), unicode(config_version[1]))
    
    conf_lines = conf_text.split(u'\n')
    
    key_exists = False
    for L in conf_lines:
        l_index = conf_lines.index(L)
        if u'=' in L:
            key = L.split(u'=')[0]
            
            if k_name == key:
                key_exists = True
                
                conf_lines[l_index] = u'{}={}'.format(k_name, k_value)
    
    if not key_exists:
        conf_lines.append(u'{}={}'.format(k_name, k_value))
    
    conf_text = u'\n'.join(conf_lines)
    
    if TextIsEmpty(conf_text):
        Logger.Warning(__name__, u'Not writing empty text to configuration')
        return ConfCode.ERR_WRITE
    
    # Actual writing to configuration
    conf_opened = open(conf, u'w')
    conf_opened.write(conf_text)
    conf_opened.close()
    
    return ConfCode.SUCCESS


## Function used to create the inital configuration file
#  
#  \param conf
#        \b \e unicode|str : File to be written
#  \return
#        \b \e ConfCode
def InitializeConfig(conf=default_config):
    for V in default_config_values:
        exit_code = WriteConfig(V, default_config_values[V], conf)
        
        if exit_code != ConfCode.SUCCESS:
            return exit_code
    
    return ConfCode.SUCCESS


## Retrieves default configuration value for a key
#  
#  \param key
#        \b \e unicode|str : Key to check
#  \return
#        Default value for the key or ConfCode.KEY_NO_EXIST
def GetDefaultConfigValue(key):
    if key in default_config_values:
        return default_config_values[key]
    
    return ConfCode.KEY_NO_EXIST
