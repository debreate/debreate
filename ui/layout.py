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
    
    
    ## Retrieves all sizers contained with the sizer
    def GetChildSizers(self):
        sizers = []
        
        for SIZER in self.GetChildren():
            SIZER = SIZER.GetSizer()
            
            if SIZER:
                sizers.append(SIZER)
        
        return tuple(sizers)
    
    
    ## Retrieves all windows contained within the sizer
    def GetChildWindows(self):
        windows = []
        
        for WIN in self.GetChildren():
            WIN = WIN.GetWindow()
            
            if WIN:
                windows.append(WIN)
        
        return tuple(windows)
    
    
    ## Retrieves item at give index
    #
    #  \param index
    #    \b \e Integer index of item to retrieve
    #  \param sizer
    #    Get sizer instance instead of window
    def GetItemAtIndex(self, index, sizer=False):
        items = self.GetChildren()
        
        if items:
            if sizer:
                return items[0].GetSizer()
            
            return items[0].GetWindow()
    
    
    ## Returns the number of items in the sizer
    #  
    #  Compatibility method for legacy wx versions
    def GetItemCount(self):
        if wx.MAJOR_VERSION > 2:
            return wx.Sizer.GetItemCount(self)
        
        return len(self.GetChildren())
    
    
    ## Finds index of an item
    def GetItemIndex(self, item):
        index = 0
        for I in self.GetChildren():
            S = I.GetSizer()
            I = I.GetWindow()
            
            if not I:
                I = S
            
            if I == item:
                return index
            
            index += 1
        
        return None


class BoxSizer(Sizer, wx.BoxSizer):
    def __init__(self, orient):
        wx.BoxSizer.__init__(self, orient)
