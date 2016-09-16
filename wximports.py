# -*- coding: utf-8 -*-

# Everything from wx that needs to be accessed will be imported here
'''
import wxversion
wxversion.select(['3.0', '2.8'])
#wxversion.select('2.8')

# wx system
from wx import \
	MAJOR_VERSION as wxMAJOR_VERSION, \
	MINOR_VERSION as wxMINOR_VERSION, \
	RELEASE_VERSION as wxRELEASE_VERSION, \
	SetDefaultPyEncoding as wxSetDefaultPyEncoding

# Functions
from wx import \
    GetPasswordFromUser as wxGetPasswordFromUser, \
    NewId as wxNewId

# General wx imports
from wx import \
	Bitmap as wxBitmap, \
	Button as wxButton, \
	CheckBox as wxCheckBox, \
	Choice as wxChoice, \
	ComboBox as wxComboBox, \
	DefaultPosition as wxDefaultPosition, \
	Dialog as wxDialog, \
	DirDialog as wxDirDialog, \
	EmptyString as wxEmptyString, \
	FileDialog as wxFileDialog, \
	FileDropTarget as wxFileDropTarget, \
	Frame as wxFrame, \
	Gauge as wxGauge, \
	GenericDirCtrl as wxGenericDirCtrl, \
	HyperlinkCtrl as wxHyperlinkCtrl, \
	Icon as wxIcon, \
	LaunchDefaultBrowser as wxLaunchDefaultBrowser, \
	ListCtrl as wxListCtrl, \
	Menu as wxMenu, \
	MenuBar as wxMenuBar, \
	MenuItem as wxMenuItem, \
	MessageDialog as wxMessageDialog, \
	Panel as wxPanel, \
	ProgressDialog as wxProgressDialog, \
	RadioButton as wxRadioButton, \
	ScrolledWindow as wxScrolledWindow, \
	SafeYield as wxSafeYield, \
	StaticBox as wxStaticBox, \
	StaticText as wxStaticText, \
	StatusBar as wxStatusBar, \
	TextCtrl as wxTextCtrl, \
	Timer as wxTimer, \
	ToolTip as wxToolTip, \
	Yield as wxYield

# wx.mixins control widgets
from wx.lib.mixins import \
	listctrl as wxMixinListCtrl

# wx layout controls
from wx import \
	BoxSizer as wxBoxSizer, \
	FlexGridSizer as wxFlexGridSizer, \
	GridSizer as wxGridSizer, \
	StaticBoxSizer as wxStaticBoxSizer

# General constants
from wx import \
	ALL as wxALL, \
	BITMAP_TYPE_PNG as wxBITMAP_TYPE_PNG, \
	BORDER_SIMPLE as wxBORDER_SIMPLE, \
	BOTH as wxBOTH, \
	BOTTOM as wxBOTTOM, \
	CANCEL as wxCANCEL, \
	EXPAND as wxEXPAND, \
	HORIZONTAL as wxHORIZONTAL, \
	ICON_ERROR as wxICON_ERROR, \
    ICON_EXCLAMATION as wxICON_EXCLAMATION, \
	ICON_INFORMATION as wxICON_INFORMATION, \
	ICON_QUESTION as wxICON_QUESTION, \
    ICON_WARNING as wxICON_WARNING, \
	ITEM_CHECK as wxITEM_CHECK, \
	ITEM_RADIO as wxITEM_RADIO, \
	LC_REPORT as wxLC_REPORT, \
	LC_SINGLE_SEL as wxLC_SINGLE_SEL, \
	LEFT as wxLEFT, \
	LIST_AUTOSIZE as wxLIST_AUTOSIZE, \
	NO_DEFAULT as wxNO_DEFAULT, \
	OK as wxOK, \
	RB_GROUP as wxRB_GROUP, \
	RIGHT as wxRIGHT, \
	TE_READONLY as wxTE_READONLY, \
	TE_MULTILINE as wxTE_MULTILINE, \
	TOP as wxTOP, \
	VERTICAL as wxVERTICAL, \
	YES_NO as wxYES_NO

# Layout constants
from wx import \
	ALIGN_BOTTOM as wxALIGN_BOTTOM, \
	ALIGN_CENTER as wxALIGN_CENTER, \
	ALIGN_CENTER_VERTICAL as wxALIGN_CENTER_VERTICAL, \
	ALIGN_RIGHT as wxALIGN_RIGHT

# Dialog constants
from wx import \
	CHANGE_DIR as wxCHANGE_DIR, \
	DD_CHANGE_DIR as wxDD_CHANGE_DIR, \
	FD_CHANGE_DIR as wxFD_CHANGE_DIR, \
	FD_OVERWRITE_PROMPT as wxFD_OVERWRITE_PROMPT, \
	FD_SAVE as wxFD_SAVE

# Progress dialog constants
from wx import \
	PD_AUTO_HIDE as wxPD_AUTO_HIDE, \
	PD_CAN_ABORT as wxPD_CAN_ABORT, \
	PD_ELAPSED_TIME as wxPD_ELAPSED_TIME, \
	PD_ESTIMATED_TIME as wxPD_ESTIMATED_TIME

# Input constants
from wx import \
	WXK_DELETE as wxWXK_DELETE, \
	WXK_ESCAPE as wxWXK_ESCAPE, \
	WXK_NUMPAD_ENTER as wxWXK_NUMPAD_ENTER, \
	WXK_RETURN as wxWXK_RETURN

# Event constants
from wx import \
	EVT_BUTTON as wxEVT_BUTTON, \
	EVT_CHECKBOX as wxEVT_CHECKBOX, \
	EVT_CLOSE as wxEVT_CLOSE, \
	EVT_CONTEXT_MENU as wxEVT_CONTEXT_MENU, \
	EVT_KEY_DOWN as wxEVT_KEY_DOWN, \
	EVT_KEY_UP as wxEVT_KEY_UP, \
	EVT_MAXIMIZE as wxEVT_MAXIMIZE, \
	EVT_MENU as wxEVT_MENU, \
	EVT_RADIOBUTTON as wxEVT_RADIOBUTTON, \
	EVT_SHOW as wxEVT_SHOW, \
	EVT_SIZE as wxEVT_SIZE, \
	EVT_TIMER as wxEVT_TIMER

# ID constants
from wx import \
	ID_ABOUT as wxID_ABOUT, \
	ID_ANY as wxID_ANY, \
	ID_EXIT as wxID_EXIT, \
	ID_HELP as wxID_HELP, \
	ID_NEW as wxID_NEW, \
	ID_OK as wxID_OK, \
	ID_OPEN as wxID_OPEN, \
	ID_SAVE as wxID_SAVE, \
	ID_SAVEAS as wxID_SAVEAS, \
	ID_YES as wxID_YES'''
