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

# wx controls
from wx import \
	CheckBox as wxCheckBox, \
	Choice as wxChoice, \
	ComboBox as wxComboBox, \
	Dialog as wxDialog, \
	EmptyString as wxEmptyString, \
	FileDropTarget as wxFileDropTarget, \
	HyperlinkCtrl as wxHyperlinkCtrl, \
	Panel as wxPanel, \
	ScrolledWindow as wxScrolledWindow, \
	StaticBox as wxStaticBox, \
	StaticText as wxStaticText, \
	TextCtrl as wxTextCtrl, \
	ToolTip as wxToolTip

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
	ALL as wxALL, \
	BOTTOM as wxBOTTOM, \
	EXPAND as wxEXPAND, \
	HORIZONTAL as wxHORIZONTAL, \
	LEFT as wxLEFT, \
	RIGHT as wxRIGHT, \
	TE_READONLY as wxTE_READONLY, \
	TE_MULTILINE as wxTE_MULTILINE, \
	VERTICAL as wxVERTICAL

# wx event constants
from wx import \
	EVT_BUTTON as wxEVT_BUTTON, \
	EVT_KEY_DOWN as wxEVT_KEY_DOWN, \
	EVT_KEY_UP as wxEVT_KEY_UP, \
	EVT_SHOW as wxEVT_SHOW, \
	EVT_SIZE as wxEVT_SIZE
