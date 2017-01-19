# -*- coding: utf-8 -*-

## \package dbr.containers

# MIT licensing
# See: docs/LICENSE.txt


import wx


## Tests if a container contains any of a list of items
def Contains(cont, items, all_of=False):
    sizer = isinstance(cont, wx.Sizer)
    
    if not isinstance(items, (tuple, list, dict)):
        if sizer:
            items = (items,)
        
        else:
            return items in cont
    
    if sizer:
        for ITEM in items:
            for SI in cont.GetChildren():
                if SI:
                    if isinstance(SI, wx.SizerItem) and ITEM in (SI.GetWindow(), SI.GetSizer()):
                        return True
                    
                    if ITEM == SI:
                        return True
    
    else:
        for ITEM in items:
            if ITEM in cont:
                return True
    
    return False


## Retrieves the number of items contained within the object
#  
#  Compatibility function for older wx versions
def GetItemCount(cont):
    if wx.MAJOR_VERSION <= 2:
        return len(cont.GetChildren())
    
    return cont.GetItemCount()
