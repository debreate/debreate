# -*- coding: utf-8 -*-

## \package dbr.config
#  
#  Parsing & writing configuration.


import os, wx

from dbr.compression    import DEFAULT_COMPRESSION_ID
from dbr.compression    import compression_formats
from dbr.functions      import GetBoolean
from dbr.functions      import GetIntTuple
from dbr.functions      import TextIsEmpty
from globals.paths      import PATH_home


## Configuration codes
class ConfCode:
    SUCCESS = 0
    ERR_READ = wx.NewId()
    ERR_WRITE = wx.NewId()
    FILE_NOT_FOUND = wx.NewId()
    WRONG_TYPE = wx.NewId()
    KEY_NO_EXIST = wx.NewId()
    KEY_NOT_DEFINED = wx.NewId()
    
    string = {
        SUCCESS: u'SUCCESS',
        ERR_READ: u'ERR_READ',
        ERR_WRITE: u'ERR_WRITE',
        FILE_NOT_FOUND: u'FILE_NOT_FOUND',
        WRONG_TYPE: u'WRONG_TYPE',
        KEY_NO_EXIST: u'KEY_NO_EXIST',
        KEY_NOT_DEFINED: u'KEY_NOT_DEFINED',
    }

# Version of configuration to use
config_version = (1, 1)

# Default configuration
default_config_dir = u'{}/.config/debreate'.format(PATH_home)
default_config = u'{}/config'.format(default_config_dir)

# name = (function, default value)
default_config_values = {
    u'center': (GetBoolean, True),
    u'dialogs': (GetBoolean, False),
    u'maximize': (GetBoolean, False),
    u'position': (GetIntTuple, (0, 0)),
    u'size': (GetIntTuple, (800, 640)),
    u'workingdir': (unicode, PATH_home),
    u'compression': (unicode, compression_formats[DEFAULT_COMPRESSION_ID]),
    u'tooltips': (GetBoolean, True),
    u'hiddenfiles': (GetBoolean, True),
}


## Opens configuration & searches for key
#  
#  \param k_name
#        \b \e unicode|str : Key to search for
#  \return
#        Value of key if found, otherwise ConfCode
def ReadConfig(k_name, conf=default_config):
    #Logger.Debug(__name__, GT(u'Reading configuration file: {}'.format(conf)))
    
    if not os.path.isfile(conf):
        #Logger.Warning(__name__, u'Configuration file does not exist: {}'.format(conf))
        return ConfCode.FILE_NOT_FOUND
    
    # Use the string '__test__' for test when app is initialized
    if k_name == u'__test__':
        return ConfCode.SUCCESS
    
    # Only read pre-defined keys
    if k_name not in default_config_values:
        #Logger.Warning(__name__, u'Undefined key, not attempting to retrieve value: {}'.format(k_name))
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
                value = default_config_values[key][0](value)
                
                #Logger.Debug(__name__, u'Retrieved key-value: {}={}, value type: {}'.format(key, value, type(value)))
                return value
    
    if k_name in default_config_values:
        #Logger.Debug(__name__, u'Configuration does not contain key, retrieving default value: {}'.format(k_name))
        
        return GetDefaultConfigValue(k_name)
    
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
            #Logger.Error(__name__, u'Cannot create config directory, file exists: {}'.format(conf_dir))
            return ConfCode.ERR_WRITE
        
        os.makedirs(conf_dir)
    
    # Only write pre-defined keys
    if k_name not in default_config_values:
        #Logger.Warning(__name__, u'Cannot write to config, key not defined: {}'.format(k_name))
        return ConfCode.KEY_NOT_DEFINED
    
    # Make sure we are writing the correct type
    k_value = default_config_values[k_name][0](k_value)
    
    if k_value == None:
        #Logger.Warning(__name__, u'Value is of wrong type for key "{}"'.format(k_name))
        return ConfCode.WRONG_TYPE
    
    # tuple is the only type we need to format
    if isinstance(k_value, tuple):
        k_value = u'{},{}'.format(unicode(k_value[0]), unicode(k_value[1]))
    else:
        k_value = unicode(k_value)
    
    conf_text = wx.EmptyString
    
    # Save current config to buffer
    if os.path.exists(conf):
        if not os.path.isfile(conf):
            #Logger.Error(__name__, u'Cannot open config for writing, directory exists: {}'.format(conf))
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
        #Logger.Warning(__name__, u'Not writing empty text to configuration')
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
        exit_code = WriteConfig(V, default_config_values[V][1], conf)
        
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
    if key in default_config:
        return default_config_values[key][1]
    
    return ConfCode.KEY_NO_EXIST
