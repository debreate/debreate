# -*- coding: utf-8 -*-

## \package command_line


# System modules
import sys



#short_args = u'hvg:'
#long_args = [u'help', u'version', u'log-level=', u'log-interval=']

solo_args = (
    (u'h', u'help'),
    (u'v', u'version'),
)

value_args = (
    (u'l', u'log-level'),
    (u'i', u'log-interval'),
)

cmds = (
    u'clean',
    u'compile',
    u'legacy',
)

parsed_args_s = []
parsed_args_v = {}
parsed_commands = []
parsed_path = None

def ArgOK(arg, group):
    for s, l in group:
        if arg in (s, l,):
            return True
    
    return False

def ArgIsDefined(arg, a_type):
    for group in (solo_args, value_args):
        for S in group:
            for A in S:
                if arg == A:
                    return True
    
    return False

def GetArgType(arg):
    dashes = 0
    for C in arg:
        if C != u'-':
            break
        
        dashes += 1
    
    if dashes:
        if dashes == 2 and len(arg.split(u'=')[0]) > 2:
            if not arg.count(u'='):
                return u'long'
            
            if arg.count(u'=') == 1:
                return u'long-value'
        
        elif dashes == 1 and len(arg.split(u'=')[0]) == 2:
            if not arg.count(u'='):
                return u'short'
            
            if arg.count(u'=') == 1:
                return u'short-value'
        
        return None
    
    if arg in cmds:
        return u'command'
    
    return u'path'


def ParseArguments(arg_list):
    global parsed_path
    
    for A in arg_list:
        arg_type = GetArgType(A)
        
        if arg_type == None:
            print(u'ERROR: Malformed argument: {}'.format(A))
            sys.exit(1)
        
        if arg_type == u'command':
            parsed_commands.append(A)
            continue
        
        if arg_type == u'path':
            if parsed_path != None:
                print(u'ERROR: Multiple input files specified: {}, {}'.format(parsed_path, A))
                # FIXME: Use errno here
                sys.exit(1)
            
            parsed_path = A
            continue
        
        clip = 0
        for C in A:
            if C != u'-':
                break
            
            clip += 1
        
        if arg_type in (u'long', u'short'):
            parsed_args_s.append(A[clip:])
            continue
        
        # Anything else should be a value type
        key, value = A.split(u'=')
        
        # FIXME: Value args can be declared multiple times
        
        if not value.strip():
            print(u'ERROR: Value argument with empty value: {}'.format(key))
            # FIXME: Use errno here
            sys.exit(1)
        
        key = key[clip:]
        
        # Use long form
        for S, L in value_args:
            if key == S:
                key = L
                break
        
        parsed_args_v[key] = value
    
    
    # Testing arguments
    
    for A in parsed_args_s:
        if not ArgOK(A, solo_args):
            for S, L in value_args:
                if A in (S, L,):
                    print(u'ERROR: Value argument with empty value: {}'.format(A))
                    # FIXME: Use errno here:
                    sys.exit(1)
            
            print(u'ERROR: Unknown argument: {}'.format(A))
            # FIXME: Use errno here
            sys.exit(1)
        
        # Use long form
        arg_index = parsed_args_s.index(A)
        for S, L in solo_args:
            if A == S:
                parsed_args_s[arg_index] = L
    
    
    for A in parsed_args_v:
        if not ArgOK(A, value_args):
            print(u'ERROR: Unknown argument: {}'.format(A))
            # FIXME: Use errno here
            sys.exit(1)
    
    for S, L in solo_args:
        s_count = parsed_args_s.count(S)
        l_count = parsed_args_s.count(L)
        
        if s_count + l_count > 1:
            print(u'ERROR: Duplicate arguments: -{}|--{}'.format(S, L))
            # FIXME: Use errno here
            sys.exit(1)


## Checks if an argument was used
def FoundArg(arg):
    for group in (parsed_args_s, parsed_args_v):
        for A in group:
            if A == arg:
                return True
    
    return False


## Checks if a command was used
def FoundCmd(cmd):
    return cmd in parsed_commands


def GetParsedPath():
    return parsed_path
