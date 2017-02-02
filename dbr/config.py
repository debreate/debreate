# -*- coding: utf-8 -*-

## \package dbr.config
#  
#  Parsing & writing configuration.

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, wx

from dbr.functions      import GetBoolean
from dbr.functions      import GetIntTuple
from dbr.functions      import IsIntTuple
from dbr.language       import GT
from dbr.log            import Logger
from globals.fileio     import ReadFile
from globals.fileio     import WriteFile
from globals.paths      import PATH_home
from globals.strings    import GS
from globals.strings    import TextIsEmpty


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
    u'maximize': (GetBoolean, False),
    u'position': (GetIntTuple, (0, 0)),
    u'size': (GetIntTuple, (800, 640)),
    u'workingdir': (GS, PATH_home),
    u'tooltips': (GetBoolean, True),
}


## TODO: Doxygen
def SetDefaultConfigKey(key, value):
    global default_config_values
    
    # Default type is string
    func = GS
    
    if isinstance(value, bool):
        func = GetBoolean
    
    elif IsIntTuple(value):
        func = GetIntTuple
    
    default_config_values[key] = (func, value,)


## Opens configuration & searches for key
#  
#  \param k_name
#        \b \e unicode|str : Key to search for
#  \return
#        Value of key if found, otherwise ConfCode
def ReadConfig(k_name, conf=default_config):
    Logger.Debug(__name__, GT(u'Reading configuration file: {}'.format(conf)), newline=True)
    
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
    
    conf_lines = ReadFile(conf)
    if conf_lines:
        conf_lines = conf_lines.split(u'\n')
        
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
def WriteConfig(k_name, k_value, conf=default_config, sectLabel=None):
    conf_dir = os.path.dirname(conf)
    
    if not os.path.isdir(conf_dir):
        if os.path.exists(conf_dir):
            print(u'{}: {}: {}'.format(GT(u'Error'), GT(u'Cannot create config directory, file exists'), conf_dir))
            return ConfCode.ERR_WRITE
        
        os.makedirs(conf_dir)
    
    # Only write pre-defined keys
    if k_name not in default_config_values:
        print(u'{}: {}: {}'.format(GT(u'Error'), GT(u'Configuration key not found'), k_name))
        return ConfCode.KEY_NOT_DEFINED
    
    # Make sure we are writing the correct type
    k_value = default_config_values[k_name][0](k_value)
    
    if k_value == None:
        print(u'{}: {}: {}'.format(GT(u'Error'), GT(u'Wrong value type for configuration key'), k_name))
        return ConfCode.WRONG_TYPE
    
    # tuple is the only type we need to format
    if isinstance(k_value, tuple):
        k_value = u'{},{}'.format(GS(k_value[0]), GS(k_value[1]))
    
    else:
        k_value = GS(k_value)
    
    conf_text = wx.EmptyString
    
    # Save current config to buffer
    if os.path.exists(conf):
        if not os.path.isfile(conf):
            print(u'{}: {}: {}'.format(GT(u'Error'), GT(u'Cannot open config for writing, directory exists'), conf))
            return ConfCode.ERR_WRITE
        
        conf_text = ReadFile(conf)
        
        # FIXME: ReadFile returns None type if config file exists but is empty
        if conf_text == None:
            conf_text = u''
    
    else:
        conf_text = u'[CONFIG-{}.{}]'.format(GS(config_version[0]), GS(config_version[1]))
    
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
        print(u'{}: {}'.format(GT(u'Warning'), GT(u'Not writing empty text to configuration')))
        return ConfCode.ERR_WRITE
    
    # Actual writing to configuration
    WriteFile(conf, conf_text)
    
    if os.path.isfile(conf):
        return ConfCode.SUCCESS
    
    return ConfCode.ERR_WRITE


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


## Checks if value type is correct
def _check_config_values(keys):
    for KEY in keys:
        try:
            if not isinstance(keys[KEY], type(default_config_values[KEY][1])):
                sys.stderr.write(u'Config error:\n')
                sys.stderr.write(u'  Key: {}\n'.format(KEY))
                sys.stderr.write(u'  Value: {}\n'.format(keys[KEY]))
                sys.stderr.write(u'  Value type: {}\n'.format(type(keys[KEY])))
                sys.stderr.write(u'  Target type: {}\n'.format(type(default_config_values[KEY][1])))
                sys.stderr.write(u'Bad value type\n')
                
                return False
        
        except KeyError:
            sys.stderr.write(u'Config error:\n')
            sys.stderr.write(u'  KeyError: {}\n'.format(KEY))
            
            return False
    
    return True


## Reads in all values found in configuration file
#  
#  \return
#    Configuration keys found in config file or None if error occurred
def GetAllConfigKeys():
    keys = {}
    
    # Read key/values from configuration file
    for KEY in default_config_values:
        keys[KEY] = ReadConfig(KEY)
    
    if not _check_config_values(keys):
        return None
    
    return keys
