# -*- coding: utf-8 -*-

## \package dbr.command_line


# System modules
import os, sys

# Local modules
from dbr.language import GT
import errno


parsed_args_s = []
parsed_args_v = {}

#short_args = u'hvg:'
#long_args = [u'help', u'version', u'log-level=', u'log-interval=']

solo_args = (
    (u'h', u'help'),
    (u'v', u'version'),
)

value_args = (
    (u'g', u'log-level'),
    (u'i', u'log-interval'),
)

def CheckArg():
    return

def ParseArguments(arg_list):
    for arg_index in range(len(arg_list)):
        # HACK: Allow loading project files
        if os.path.isfile(arg_list[arg_index]):
            continue
        
        key = arg_list[arg_index]
        value = None
        
        long_arg = 0
        key_index = 0
        for C in key:
            if (C != u'-'):
                break
            
            key_index += 1
            
            if key_index > 1:
                long_arg = 1
                break
        
        key = key[key_index:]
        
        
        # Check for bad arguments
        arg_ok = False
        if long_arg:
            for S, L in solo_args:
                if key == L:
                    arg_ok = True
            
            for S, L, in value_args:
                if key == L:
                    arg_ok = True
        
        else:
            for S, L in solo_args:
                if key == S:
                    arg_ok = True
            
            for S, L in value_args:
                if key == S:
                    arg_ok = True
        
        if not arg_ok:
            print(GT(u'ERROR: Unrecognized argument: {}').format(key))
            
            sys.exit(errno.EINVAL)
        
        
        if u'=' in key:
            value = key.split(u'=')[1]
            key = key.split(u'=')[0]
            
            for A in value_args:
                if key == A[long_arg]:
                    parsed_args_v[A[1]] = value
            
            arg_index += 1
            continue
        
        for A in solo_args:
            if key == A[long_arg]:
                parsed_args_s.append(A[1])
        
        for A in value_args:
            if key == A[long_arg]:
                try:
                    if not value:
                        value = arg_list[arg_index + 1]
                    parsed_args_v[A[1]] = value
                
                except IndexError:
                    print(u'ERROR: Argument "{}" requires a value'.format(key))
            
            if value and value[0] == u'-':
                print(u'ERROR: Argument found after argument requiring value')
        
        arg_index += 1
