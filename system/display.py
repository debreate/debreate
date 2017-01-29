# -*- coding: utf-8 -*-

## \package system.display

# MIT licensing
# See: docs/LICENSE.txt


from dbr.log            import DebugEnabled
from dbr.log            import Logger
from globals.execute    import GetCommandOutput
from globals.execute    import GetExecutable
from globals.strings    import StringIsNumeric


## Retrieves dimensions of primary display
#
#  FIXME: Use 1 or 2 alternate methods (wx.Display???)
def GetPrimaryDisplayRect():
    CMD_xrand = GetExecutable(u'xrandr')
    
    if not CMD_xrand:
        return None
    
    output = GetCommandOutput(CMD_xrand).split(u'\n')
    
    for LINE in output:
        LINE = LINE.lower()
        if u'primary' in LINE:
            LINE = LINE.split(u'primary')[1].strip().split(u' ')[0]
            posX = LINE.split(u'x')
            posY = posX[1].split(u'+')
            posX = posX[0]
            width = posY[1]
            height = posY[2]
            posY = posY[0]
            
            rect = [posX, posY, width, height,]
            for INDEX in range(len(rect)):
                X = rect[INDEX]
                if not StringIsNumeric(X):
                    # FIXME: Break out of second loop & call continue on first?
                    return None
                
                rect[INDEX] = int(X)
            
            return tuple(rect)


## Centers the window on the primary display
#
#  \param window
#    \b \e wx.Window instance to be centered
def CenterOnPrimaryDisplay(window):
    Logger.Debug(__name__, u'Attempting to center window: {} ({})'.format(window.Name, window))
    
    display_rect = GetPrimaryDisplayRect()
    
    Logger.Debug(__name__, u'Primary display: {}'.format(display_rect))
    
    if not display_rect:
        return False
    
    window_size = window.GetSizeTuple()
    
    dx = display_rect[2]
    dy = display_rect[3]
    dw = display_rect[0]
    dh = display_rect[1]
    
    x_diff = (dw - window_size[0]) / 2
    y_diff = (dh - window_size[1]) / 2
    
    debug = DebugEnabled()
    
    if debug:
        print(u'  X difference: {}'.format(x_diff))
        print(u'  Y difference: {}'.format(y_diff))
    
    # NOTE: May be a few pixels off
    pos_x = dx + x_diff
    pos_y = dy + y_diff
    
    if debug:
        print(u'\n  Theoretical position: {}'.format((pos_x, pos_y,)))
        print(u'  Actual Position:      {}'.format(window.GetPositionTuple()))
    
    window.SetPosition((pos_x, pos_y))
    
    return True
