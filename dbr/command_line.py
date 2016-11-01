# -*- coding: utf-8 -*-
'''
arguments_s = (
    (u'h', u'help'),
    (u'v', u'version'),
)

arguments_v = (
    (u'g', u'log-level'),
)'''

from dbr.log import Logger
from dbr.log import DebugEnabled


parsed_args_s = []
parsed_args_v = {}

'''
## Try to set an argument
def SetArgument(arg):
    arg_type = 0
    # Solo arguments
    for A in arguments_s:
        if arg in A:
            parsed_args_s.append(A[1])
            return True
    
    if u'=' in arg:
        arg = arg.split(u'=')
        value = arg[1]
        arg = arg[0]
        for A in arguments_v:
            if arg[0] in A:
                parsed_args_v[arg] = value
                return True
    
    print(u'Invalid argument: {}'.format(arg))
    return False
'''
'''
def ParseArguments(arg_list):
    for A in arg_list:
        #print(u'ARG: {}'.format(A))
        if A[:2] == u'--':
            print(u'Long arg: {}'.format(A))
            arg = A[2:]
            print(arg in arguments_s)
            SetArgument(arg)
        elif A[0] == u'-':
            print(u'Short arg: {}'.format(A))
            arg = A[1:]
            print(arg in arguments_v)
            SetArgument(arg)
    
    print(u'Parsed args S: {}'.format(parsed_args_s))
    print(u'Parsed args V: {}'.format(parsed_args_v))
'''

short_args = u'hvg:'
long_args = [u'help', u'version', u'log-level=']

solo_args = (
    (u'h', u'help'),
    (u'v', u'version'),
)

value_args = (
    (u'g', u'log-level'),
)

def CheckArg():
    return

def ParseArguments(arg_list):
    arg_index = 0
    
    while arg_index < len(arg_list):
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
        

def ExecuteArguments():
    if u'log-level' in parsed_args_v:
        Logger.SetLogLevel(parsed_args_v[u'log-level'])
    
    if DebugEnabled():
        print(u'Solo args:')
        for S in parsed_args_s:
            print(u'\t{}'.format(S))
        
        print(u'Value args:')
        for V in parsed_args_v:
            print(u'\t{}: {}'.format(V, parsed_args_v[V]))
