# -*- coding: utf-8 -*-

# Everything from wx that needs to be accessed will be imported here

import wxversion
#wxversion.select(['3.0', '2.8'])
wxversion.select('2.8')

# wx system
from wx import \
	MAJOR_VERSION as wxMAJOR_VERSION, \
	MINOR_VERSION as wxMINOR_VERSION, \
	RELEASE_VERSION as wxRELEASE_VERSION, \
	SetDefaultPyEncoding

# wx functions
from wx import NewId as wxNewId

# wx control widgets
from wx import \
	Button as wxButton, \
	CheckBox as wxCheckBox, \
	Choice as wxChoice, \
	ComboBox as wxComboBox, \
	Dialog as wxDialog, \
	EmptyString as wxEmptyString, \
	FileDropTarget as wxFileDropTarget, \
	GenericDirCtrl as wxGenericDirCtrl, \
	HyperlinkCtrl as wxHyperlinkCtrl, \
	ListCtrl as wxListCtrl, \
	Menu as wxMenu, \
	MenuItem as wxMenuItem, \
	Panel as wxPanel, \
	RadioButton as wxRadioButton, \
	ScrolledWindow as wxScrolledWindow, \
	StaticBox as wxStaticBox, \
	StaticText as wxStaticText, \
	TextCtrl as wxTextCtrl, \
	ToolTip as wxToolTip

# wx.mixins control widgets
from wx.lib.mixins import \
	listctrl as wxMixinListCtrl

# wx layout controls
from wx import \
	BoxSizer as wxBoxSizer, \
	FlexGridSizer as wxFlexGridSizer, \
	GridSizer as wxGridSizer, \
	StaticBoxSizer as wxStaticBoxSizer

# wx constants
from wx import \
	ALIGN_CENTER as wxALIGN_CENTER, \
	ALIGN_CENTER_VERTICAL as wxALIGN_CENTER_VERTICAL, \
	ALIGN_RIGHT as wxALIGN_RIGHT, \
	ALL as wxALL, \
	BORDER_SIMPLE as wxBORDER_SIMPLE, \
	BOTTOM as wxBOTTOM, \
	EXPAND as wxEXPAND, \
	HORIZONTAL as wxHORIZONTAL, \
	LC_REPORT as wxLC_REPORT, \
	LC_SINGLE_SEL as wxLC_SINGLE_SEL, \
	LEFT as wxLEFT, \
	RB_GROUP as wxRB_GROUP, \
	RIGHT as wxRIGHT, \
	TE_READONLY as wxTE_READONLY, \
	TE_MULTILINE as wxTE_MULTILINE, \
	TOP as wxTOP, \
	VERTICAL as wxVERTICAL

# wx event constants
from wx import \
	EVT_BUTTON as wxEVT_BUTTON, \
	EVT_CHECKBOX as wxEVT_CHECKBOX, \
	EVT_CONTEXT_MENU as wxEVT_CONTEXT_MENU, \
	EVT_KEY_DOWN as wxEVT_KEY_DOWN, \
	EVT_KEY_UP as wxEVT_KEY_UP, \
	EVT_MENU as wxEVT_MENU, \
	EVT_RADIOBUTTON as wxEVT_RADIOBUTTON, \
	EVT_SHOW as wxEVT_SHOW, \
	EVT_SIZE as wxEVT_SIZE

# wx id constants
from wx import \
	ID_ANY as wxID_ANY, \
	ID_HELP as wxID_HELP
