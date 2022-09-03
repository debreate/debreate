## \package wizbin.launchers

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language       import GT
from globals.ident      import btnid
from globals.ident      import inputid
from globals.ident      import listid
from globals.ident      import pgid
from globals.ident      import pnlid
from globals.tooltips   import SetPageToolTips
from ui.launcher        import LauncherTemplate
from ui.layout          import BoxSizer
from ui.notebook        import MultiTemplate
from wiz.helper         import GetField
from wiz.wizard         import WizardPage


## Page for creating a system launchers
class Page(WizardPage):
    ## Constructor
    #
    #  \param parent
    #    Parent <b><i>wx.Window</i></b> instance
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.LAUNCHERS)

        # Override default title
        self.SetTitle(GT("Menu Launchers"))

        self.IgnoreResetIds = [
            inputid.OTHER,
            listid.CAT,
            ]

        templates = MultiTemplate(self, LauncherTemplate, pnlid.TABS)

        templates.RenameButton(btnid.ADD, GT("Add Launcher"))
        templates.RenameButton(btnid.RENAME, GT("Rename Launcher"))

        SetPageToolTips(self)

        # *** Event Handling *** #

        self.Bind(wx.EVT_BUTTON, self.OnAddTab, id=wx.ID_ADD)

        # *** Layout *** #

        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.Add(templates, 1, wx.EXPAND|wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()


    ## Retrieves data from all launchers
    #
    #  \return
    #    Name:Data <b><i>tuple</i></b> list
    def Get(self, getModule=False):
        launchers_data = []

        for LAUNCHER in GetField(self, pnlid.TABS).GetAllPages():
            launchers_data.append((LAUNCHER.GetName(), LAUNCHER.Get(),))

        return tuple(launchers_data)


    ## Retrieves number of launchers for export or build
    def GetLaunchersCount(self):
        return GetField(self, pnlid.TABS).GetPageCount()


    ## Updates tooltips for new tab
    def OnAddTab(self, event=None):
        SetPageToolTips(self)


    ## FIXME: Not defined
    def Set(self, data):
        print("\nFIXME: Launchers.Set: Not defined")
        print("Data:\n{}".format(data))
