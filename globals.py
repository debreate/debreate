# -*- coding: utf-8 -*-

## \package dbr.globals
#  
#  Global variables & settings


# System modules
import os


# *** System paths *** #

## Directory where app is installed
PATH_app = os.path.dirname(__file__)

## User's home directory
#  
#  Used to set config directory.
PATH_home = os.getenv(u'HOME')

## Local folder to store files such as custom templates
PATH_local = u'{}/.local/share/debreate'.format(PATH_home)
