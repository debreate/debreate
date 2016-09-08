# -*- coding: utf-8 -*-

# Everything from wx that needs to be accessed will be imported here

import wxversion
#wxversion.select(['3.0', '2.8'])
wxversion.select('2.8')

# wx system
from wx import MAJOR_VERSION as wxMAJOR_VERSION
from wx import MINOR_VERSION as wxMINOR_VERSION
from wx import RELEASE_VERSION as wxRELEASE_VERSION
from wx import SetDefaultPyEncoding

# wx functions
from wx import NewId as wxNewId

# wx controls
from wx import BoxSizer as wxBoxSizer
from wx import CheckBox as wxCheckBox
from wx import Dialog as wxDialog
from wx import FileDropTarget as wxFileDropTarget
from wx import Panel as wxPanel
from wx import StaticBox as wxStaticBox
from wx import StaticBoxSizer as wxStaticBoxSizer
from wx import TextCtrl as wxTextCtrl
from wx import ToolTip as wxToolTip

# wx constants
from wx import ALIGN_CENTER as wxALIGN_CENTER
from wx import BOTTOM as wxBOTTOM
from wx import EXPAND as wxEXPAND
from wx import HORIZONTAL as wxHORIZONTAL
from wx import LEFT as wxLEFT
from wx import RIGHT as wxRIGHT
from wx import TE_READONLY as wxTE_READONLY
from wx import TE_MULTILINE as wxTE_MULTILINE
from wx import VERTICAL as wxVERTICAL

# wx event constants
from wx import EVT_BUTTON as wxEVT_BUTTON
