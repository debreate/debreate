
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module f_export.ofield


## Defines a label to be used for exporting to text file
class OutputField:
  Name = None

  def __init__(self, outLabel=None):
    # Name that can be used field output labels
    self.OutLabel = outLabel
    if self.OutLabel == None:
      self.OutLabel = self.GetName()

  ## Re-define in inheriting classes
  def GetName(self):
    return self.Name

  ## Retrieves label for exporting to text file
  def GetOutLabel(self):
    return self.OutLabel

  ## Sets the output label.
  #
  #  @param outLabel
  #    New text label to use.
  def SetOutLabel(self, outLabel):
    self.OutLabel = outLabel
