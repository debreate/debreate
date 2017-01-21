# -*- coding: utf-8 -*-

## \package ui.layout
#  
#  Custom sizer classes

# MIT licensing
# See: docs/LICENSE.txt


import wx


class Sizer(wx.Sizer):
    ## Retains spacer at end of items
    #  
    #  FIXME: Detect spacer as last item, otherwise call Add instead of Insert
    def AddKeepLast(self, item, proportion=0, flag=0, border=0, userData=None):
        last_index = self.GetItemCount() - 1
        
        return self.Insert(last_index, item, proportion, flag, border, userData)
        
        #self.Add(item, proportion, flag, border, userData)
    
    
    ## Returns the number of items in the sizer
    #  
    #  Compatibility method for legacy wx versions
    def GetItemCount(self):
        if wx.MAJOR_VERSION > 2:
            return wx.BoxSizer.GetItemCount(self)
        
        return len(self.GetChildren())
    
    
    ## Finds index of an item
    def GetItemIndex(self, item):
        index = 0
        for I in self.GetChildren():
            if I == item:
                return index
            
            index += 1
        
        return None


class BoxSizer(Sizer, wx.BoxSizer):
    def __init__(self, orient):
        wx.BoxSizer.__init__(self, orient)
