# -*- coding: utf-8 -*-

## \package wiz.helper

# MIT licensing
# See: docs/LICENSE.txt


from globals.wizardhelper import GetMainWindow


## Retrieves a menu from the main window's menu bar by ID
#  
#  \param menuId
#    \b \e Integer ID of desired menu
#  \retun
#    The \b \e wx.Menu instance
def GetMenu(menuId):
    return GetMainWindow().GetMenu()
