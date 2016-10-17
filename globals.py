# -*- coding: utf-8 -*-

## \package dbr.globals
#  
#  Global variables & settings


# System modules
import wx, os


# *** System paths *** #

## Directory where app is installed
PATH_app = os.path.dirname(__file__)

## User's home directory
#  
#  Used to set config directory.
PATH_home = os.getenv(u'HOME')

## Local folder to store files such as custom templates
PATH_local = u'{}/.local/share/debreate'.format(PATH_home)


# *** Application information *** #

## Debreate's main homepage
APP_homepage = u'https://antumdeluge.github.io/debreate-web/'

## GitHub project page
APP_project_gh = u'https://github.com/AntumDeluge/debreate'

## Sourceforge project page
APP_project_sf = u'https://sourceforge.net/projects/debreate'

## Application's logo
APP_logo = wx.Icon(u'{}/bitmaps/debreate64.png'.format(PATH_app), wx.BITMAP_TYPE_PNG)

## Name of application
APP_name = u'Debreate'


# *** Author information *** #

## Author's email
AUTHOR_email = u'antumdeluge@gmail.com'

## Application's author
AUTHOR_name = u'Jordan Irwin'


# *** Version information *** #

VERSION_maj = 0
VERSION_min = 8
VERSION_rel = 0
VERSION_tuple = (VERSION_maj, VERSION_min, VERSION_rel)
VERSION_string = u'.'.join(VERSION_tuple)

# Development version
RELEASE = 0
if not RELEASE:
    VERSION_string = u'{}-dev'.format(VERSION_string)
