# -*- coding: iso8859-1 -*-

"""color.py"""

import curses

"""Color definitions used in program"""
CMDLINE_TTL, CMDLINE,\
PROGR_FULL, PROGR_NONE,\
ERR_WIND, ERR_TTL,\
WIND, WIND_TTL, WIND_TXT, BUTTON, ENTRY,\
PANEL_ACT, PANEL_INACT, PANEL_TITLE, PANEL_CLMN,\
STATUS_BAR, INFO,\
TAB, FOCUS_TAB, FOCUS_ITEM, FOCUS_SEL_ITEM,\
NOCLR, REG_FLS, SEL_FLS, EXE_FLS, DIR,\
TMP_FLS, DOC_FLS, MED_FLS, ARC_FLS, SRC_FLS, GRA_FLS, DAT_FLS\
= range(33)

clr = {
    'black': curses.COLOR_BLACK,
    'blue': curses.COLOR_BLUE,
    'cyan': curses.COLOR_CYAN,
    'green': curses.COLOR_GREEN,
    'magenta': curses.COLOR_MAGENTA,
    'red': curses.COLOR_RED,
    'white': curses.COLOR_WHITE,
    'yellow': curses.COLOR_YELLOW
    }

def __set_color_pair(app, i, strobj):
    """create and return color pair from string name"""
    try:
        pf_clr =app.prefs.colors
        c1,c2,s = pf_clr[strobj]
        curses.init_pair(i, clr[c1],clr[c2])
        clr_pair = curses.color_pair(i)
        if s == 'light': clr_pair |= curses.A_BOLD
    except:
        curses.endwin()
        print 'Attribute \'%s\' does not exist'% strobj
        clr_pair = curses.color_pair(0)
    return clr_pair

def set_colors(app):
    """Initialize all program colors"""
    global\
    CMDLINE_TTL, CMDLINE,\
    PROGR_FULL, PROGR_NONE,\
    ERR_WIND, ERR_TTL,\
    WIND, WIND_TTL, WIND_TXT, BUTTON, ENTRY,\
    PANEL_ACT, PANEL_INACT, PANEL_TITLE, PANEL_CLMN,\
    STATUS_BAR, INFO,\
    TAB, FOCUS_TAB, FOCUS_ITEM, FOCUS_SEL_ITEM,\
    NOCLR, REG_FLS, SEL_FLS, EXE_FLS, DIR,\
    TMP_FLS, DOC_FLS, MED_FLS, ARC_FLS, SRC_FLS, GRA_FLS, DAT_FLS

    DIR             = __set_color_pair(app, 1, 'directory')
    SEL_FLS         = __set_color_pair(app, 2, 'selected_files')
    EXE_FLS         = __set_color_pair(app, 3, 'exe_files')
    REG_FLS         = __set_color_pair(app, 4, 'regular_files')
    TMP_FLS         = __set_color_pair(app, 5, 'temp_files')
    DOC_FLS         = __set_color_pair(app, 6, 'document_files')
    MED_FLS         = __set_color_pair(app, 7, 'media_files')
    ARC_FLS         = __set_color_pair(app, 8, 'archive_files')
    SRC_FLS         = __set_color_pair(app, 9, 'source_files')
    GRA_FLS         = __set_color_pair(app, 10, 'graphics_files')
    DAT_FLS         = __set_color_pair(app, 11, 'data_files')

    CMDLINE         = __set_color_pair(app, 12, 'command_line')
    CMDLINE_TTL     = __set_color_pair(app, 13, 'command_line_title')
    PROGR_FULL      = __set_color_pair(app, 14, 'progress_full')
    PROGR_NONE      = __set_color_pair(app, 15, 'progress_none')

    ERR_WIND        = __set_color_pair(app, 16, 'err_window')
    ERR_TTL         = __set_color_pair(app, 17, 'err_title')

    INFO            = __set_color_pair(app, 18, 'info')
    WIND            = __set_color_pair(app, 19, 'window')
    WIND_TTL        = __set_color_pair(app, 20, 'window_title')
    WIND_TXT        = __set_color_pair(app, 21, 'window_text')
    
    BUTTON          = __set_color_pair(app, 22, 'button')
    ENTRY           = __set_color_pair(app, 23, 'entry_line')

    TAB             = __set_color_pair(app, 24, 'tab')
    FOCUS_TAB       = __set_color_pair(app, 25, 'focused_tab')
    FOCUS_ITEM      = __set_color_pair(app, 26, 'focused_item')
    FOCUS_SEL_ITEM  = __set_color_pair(app, 27, 'focused_sel_item')
    PANEL_ACT       = __set_color_pair(app, 28, 'panel_active')
    PANEL_INACT     = __set_color_pair(app, 29, 'panel_inactive')
    PANEL_TITLE     = __set_color_pair(app, 30, 'panel_title')
    PANEL_CLMN      = __set_color_pair(app, 32, 'panel_columns')
    STATUS_BAR      = __set_color_pair(app, 32, 'status_bar')
    NOCLR           = __set_color_pair(app, 33, 'nocolor')
