# -*- coding: utf-8 -*-

## \package output.field

# MIT licensing
# See: docs/LICENSE.txt


## Defines a label to be used for exporting to text file
class OutputField:
    def __init__(self, outLabel=None):
        # Name that can be used field output labels
        self.OutLabel = outLabel
        if self.OutLabel == None:
            self.OutLabel = self.GetName()
    
    
    ## Retrieves label for exporting to text file
    def GetOutLabel(self):
        return self.OutLabel
    
    
    ## Sets the output label
    #
    #  \param outLabel
    #    New text label to use
    def SetOutLabel(self, outLabel):
        self.OutLabel = outLabel
