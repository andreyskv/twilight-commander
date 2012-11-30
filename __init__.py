# -*- coding: iso8859-1 -*-

"""

"""

######################################################################
VERSION = '2.2'
DATE = '2008'
PROG_NAME = 'tc - Twilight Commander'


import locale
locale.setlocale(locale.LC_ALL, '')
g_encoding = locale.getpreferredencoding()


TOGGLE_PANE, TAB_NEW, TAB_CLOSE = range(1, 4)

#Pane state types
PANE_MODE_HIDDEN, PANE_MODE_LEFT, PANE_MODE_RIGHT, PANE_MODE_FULL, PANE_MODE_TREE_LEFT, PANE_MODE_TREE_RIGHT = range(6)
SELECT_UPDATE = 100

#Column types
(NAME, TYPE, PERMS, PERMSNUM, OWNER, GROUP, SIZE, SIZEHUMN, MTIME_LONG, MTIME, MTIME_MC,
    CTIME_LONG, CTIME, CTIME_MC, ATIME_LONG, ATIME, ATIME_MC) = range(17)

# In standard terminals set CURSES_OFFSET = 0
# If line characters are shown incorrectly adjust the value (cygwin rxvt.exe requires 32)
CURSES_OFFSET = 0 

def enc_str(string):
    try:
        return string.encode(g_encoding)
    except:
        return string

def dec_str(string):
    try:
        return string.decode(g_encoding)
    except:
        return string
