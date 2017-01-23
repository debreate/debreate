# -*- coding: utf-8 -*-

## \package startup.startup
#  
#  Used mainly to prevent project being marked dirty at startup

# MIT licensing
# See: docs/LICENSE.txt


initialized = False


## Checks the initialization state of the app
#  
#  \return
#    \b \e True if initialization is complete
def AppInitialized():
    global initialized
    
    return initialized


## Sets the app's initialization state
#  
#  \param init
#    \b \e True means initialization complete
def SetAppInitialized(init=True):
    global initialized
    
    initialized = init
