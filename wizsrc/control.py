# -*- coding: utf-8 -*-


from wx import \
    BoxSizer as wxBoxSizer, \
    NewId as wxNewId, \
    Panel as wxPanel
from wx import \
    VERTICAL as wxVERTICAL

from dbr.language import GT


ID = wxNewId()


class Panel(wxPanel):
    def __init__(self, parent, name=GT(u'Control')):
        wxPanel.__init__(self, parent, ID, name=name)
        
        page_layout = wxBoxSizer(wxVERTICAL)
