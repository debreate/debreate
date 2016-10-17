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

## Application's logo
APP_logo = wx.Icon(u'{}/bitmaps/debreate64.png'.format(PATH_app), wx.BITMAP_TYPE_PNG)

## Name of application
APP_name = u'Debreate'

## Author's email
AUTHOR_email = u'antumdeluge@gmail.com'

## Application's author
AUTHOR_name = u'Jordan Irwin'
