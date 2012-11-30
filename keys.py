# -*- coding: iso8859-1 -*-

"""keys.py

This module contains actions to execute when keys are pressed.
"""
import os
import sys
import curses
from glob import glob

from foper import *
import files
import utils
import fcompress
import vfs
import wcall
import wcmd
import main
from __init__ import *


keytable = [
    # navigation
    ['cursor_down',[curses.KEY_DOWN,ord('j'), ord('J'),]],
    ['cursor_up', [curses.KEY_UP,ord('k'), ord('K'),]],
    ['page_previous',[curses.KEY_PPAGE, 0x08, 0x10]],#Ctrl-P
    ['page_next', [curses.KEY_NPAGE, 0x0E]], # Ctrl-N
    ['home', [curses.KEY_HOME, 0x16A, 0x001]],
    ['end', [curses.KEY_END,  0x181, 0x005]],
    ['cursor_left', [curses.KEY_LEFT,ord('h'), ord('H'),]],
    ['cursor_right', [curses.KEY_RIGHT,ord('l'), ord('L'),]],
    ['enter',[10,13]] ,
    ['mouse_event', [curses.KEY_MOUSE]],

    #bookmarks
    ['bookmark_0', [ord('0')]],
    ['bookmark_1', [ord('1')]],
    ['bookmark_2', [ord('2')]],
    ['bookmark_3', [ord('3')]],
    ['bookmark_4', [ord('4')]],
    ['bookmark_5', [ord('5')]],
    ['bookmark_6', [ord('6')]],
    ['bookmark_7', [ord('7')]],
    ['bookmark_8', [ord('8')]],
    ['bookmark_9', [ord('9')]],
    ['select_bookmark', [0x04, 0x1C]],              # Ctrl-D, Ctrl-\
    ['set_bookmark',[ord('b'),ord('B')]],

    # selections
    ['select_item',[curses.KEY_IC, ord(' ')]],
    ['select_group',[ ord('+')]],
    ['deselect_group',[ord('-')]],
    ['invert_select',[ ord('*')]],

    # panels/tabs
    ['toggle_active_pane', [ord('\t')]],
    ['toggle_panes', [ord('.')]],
    ['swap_tabs', [ord(','), 0x15]],                # Ctrl-U
    ['same_tabs', [ord('=')]],
    ['new_tab', [ord(':')]],
    ['close_tab', [ord('|')]],
    ['left_tab', [ord('<')]],
    ['right_tab', [ord('>')]],
    ['tree', [0x14]],                               # Ctrl-T

    # file opeartions
    ['view_file',[curses.KEY_F3]],          #add ord('v'), ord('V') optionally
    ['edit_file',[curses.KEY_F4]],          #add ord('e'), ord('E') optionally
    ['copy',[curses.KEY_F5]],
    ['move',[curses.KEY_F6]],
    ['rename',[curses.KEY_F18, ord('r'), ord('R')]],
    ['backup',[curses.KEY_F17, ord('u'), ord('U')]],
    ['delete',[curses.KEY_F8, curses.KEY_DC]],
    ['make_dir', [curses.KEY_F7]],

    #dialogs/menus/info
    ['goto_dir', [ord('g'),ord('G')]],
    ['goto_local_path', [ord('/')]],
    ['findgrep',[0x13]],                           # Ctrl-S
    ['sort', [ord('s'),ord('s')]],
    ['create_link', [ord('n'),ord('N')]],
    ['edit_link', [0x0C]],                          # Ctrl-L
    ['show_file_info',[ ord('i'),  ord('I')]],
    ['show_dirs_size',[ord('#'), ord('z'), ord('Z')]],
    ['show_help',[curses.KEY_F1, ord('h'), ord('H')]],
    ['file_menu', [curses.KEY_F2, ord('f'), ord('F')]],
    ['general_menu',[curses.KEY_F9]],
    ['do_something_on_file',[ord('@')]],

    #other
    ['resize_window',[curses.KEY_RESIZE]],
    ['refresh_screen',[0x12]],                   # Ctrl-R
    ['command_line', [ord('o'), ord('O'), ord('d'), ord('D')]],
    ['view_shell',[0x0F]],                       #Ctrl-O
    ['quit',[curses.KEY_F10]],              #add ord('Q'), ord('q') optionally
    ]
len_keytable = len(keytable)
ret = None

def do(tab, ch):
    for i in range(len_keytable):
        if ch in keytable[i][1]:
            act = 'ret = %s(tab)'  % keytable[i][0]
            exec(act)
            return ret

def __get_selections_list(tab):
    if tab.selections:
        lst = tab.selections
    else:
        lst = [tab.sorted[tab.file_i]]
    return lst

###############################################################################
# Navigation
def cursor_down(tab):
    if tab.pane.mode in [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        t=tab.pane.tree
        if t.pos == len(t.tree)-1 or t.tree[t.pos][1] != t.tree[t.pos+1][1]:
            return
        t.pos +=1
        t.pos = min(t.pos, len(t.tree)-1)
        tab.path = t.tree[t.pos][2]
    else:
        tab.file_i_prev = tab.file_i
        tab.file_i += 1
        return SELECT_UPDATE

def cursor_up(tab):
    if tab.pane.mode in  [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        t=tab.pane.tree
        t.pos -=1
        t.pos = max(t.pos,0)
        tab.path = t.tree[t.pos][2]
        return
    else:
        tab.file_i_prev = tab.file_i
        tab.file_i -= 1
        return SELECT_UPDATE

def page_previous(tab):
    if tab.pane.mode in  [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        app, t = tab.pane.app, tab.pane.tree               #t - tree
        depth = t.tree[t.pos][1]
        if t.pos - (app.maxh-4) >= 0 and\
                    depth  == t.tree[t.pos - (app.maxh-4)][1]:
            newpos = t.pos - (app.maxh-4)
        else:
            newpos = t.pos
            while 1:
                if newpos - 1 < 0:
                    break
                if t.tree[newpos-1][1] != depth:
                    break
                newpos -= 1
        tab.path = t.tree[newpos][2]
    else:
        tab.file_i -= tab.pane.frame.dims[0]


def page_next(tab):
    if tab.pane.mode in  [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        app, t = tab.pane.app, tab.pane.tree                #t - tree
        depth = t.tree[t.pos][1]
        if t.pos + (app.maxh-4) <= len(t.tree) - 1 and\
                            depth  == t.tree[t.pos + (app.maxh-4)][1]:
            newpos = t.pos + (app.maxh-4)
        else:
            newpos = t.pos
            while 1:
                if newpos + 1 == len(t.tree):
                    break
                if t.tree[newpos+1][1] != depth:
                    break
                newpos += 1
        tab.path = t.tree[newpos][2]
    else:
        tab.file_i += tab.pane.frame.dims[0]


def home(tab):
    if tab.pane.mode in  [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        t=tab.pane.tree
        tab.path = t.tree[1][2]
    else:
        tab.file_i = 0

def end(tab):
    if tab.pane.mode in  [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        t=tab.pane.tree
        tab.path = t.tree[len(t.tree)-1][2]
    else:
        tab.file_i = tab.nfiles - 1

def __enter_path__(tab, filename):
    ftype = tab.files[filename][files.FT_TYPE]
    
    if (ftype in [files.FTYPE_REG, files.FTYPE_LNK]):
        
        if vfs.check_avfs_type(filename) and \
                        not tab.pane.app.prefs.options['cygwin']:
            
            full_path = os.path.join(tab.path, filename+'#')
            if tab.Vfs != None:
                ret =  tab.Vfs.check_exit(full_path)
                if ret[0] == '':
                    tab.Vfs.base= full_path
                    tab.Vfs.set_virtual_base()
            else:
                tab.Vfs = vfs.VFS(full_path, tab.path, filename)

            if not tab.Vfs.base:
                tab.Vfs = None
                return 1
            tab.init(tab.Vfs.base)
        else:
            return 0
    elif ftype in [files.FTYPE_DIR, files.FTYPE_LNK2DIR]:
        tab.init(os.path.join(tab.path, filename))
    else:
        return 0
    return 1


def cursor_left(tab):
    if tab.pane.mode in [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        t=tab.pane.tree
        newdepth = t.tree[t.pos][1] - 1
        for i in range(t.pos-1, -1, -1):
            if t.tree[i][1] == newdepth:
                break
        t.pos = max(i,0)
        tab.path = t.tree[t.pos][2]
    else:
        if tab.path != os.sep:
            __enter_path__(tab, os.pardir)

def cursor_right(tab):
    if tab.pane.mode in [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        t=tab.pane.tree
        child_dirs = t.get_dirs(t.path)
        if len(child_dirs) > 0:
            tab.path = os.path.join(t.path, child_dirs[0])
    else:
        filename = tab.sorted[tab.file_i]
        __enter_path__(tab, filename)

def enter(tab):
    if tab.pane.mode in  [PANE_MODE_TREE_LEFT,  PANE_MODE_TREE_RIGHT]:
        t=tab.pane.tree
        othertab = tab.pane.app.noact_pane.act_tab
        othertab.init(t.path)
    else:
        fname = tab.sorted[tab.file_i]
        ftype = tab.files[fname][files.FT_TYPE]
        if __enter_path__(tab, fname):
            return
    
        if  not tab.pane.app.prefs.options['cygwin']:
            if ftype == files.FTYPE_EXE:
                do_execute_file(tab)
            elif ftype == files.FTYPE_REG:
                do_special_view_file(tab)
        else:
            ext = os.path.splitext(fname)[1].lower()
            if ext in tab.pane.app.prefs.files_ext['cygwin_exe_files']:
                do_execute_file(tab)
            else:
                do_special_view_file(tab)


def mouse_event(tab):
    i,x,y,z,event = curses.getmouse()
    app = tab.pane.app
    h, w = app.win.getmaxyx()
    click_tm =  app.click_tm
    app.click_tm = time.time()
    if event == curses.BUTTON2_PRESSED:
        curses.ungetmouse(0,0,0,0,0)
        return page_next(tab)
    elif event == curses.BUTTON4_PRESSED:
        curses.ungetmouse(0,0,0,0,0)
        return page_previous(tab)
    elif event in [curses.BUTTON1_PRESSED, curses.BUTTON3_PRESSED]:

        #command line if click is at  bottom line
        if y == h-1:
            return command_line(tab)

        #pane click (select pane and file)
        if not app.act_pane.mode in [PANE_MODE_HIDDEN, PANE_MODE_FULL]:
                #x1,x2 = 0.,w
        #else:
            if x > int(w/2):
                if app.lpane.mode in [PANE_MODE_LEFT, PANE_MODE_TREE_LEFT]:
                    app.act_pane, app.noact_pane = app.rpane, app.lpane
                else:
                    app.act_pane, app.noact_pane = app.lpane, app.rpane
                    #x1,x2 = w/2,w
            else:
                if app.lpane.mode in [PANE_MODE_LEFT, PANE_MODE_TREE_LEFT]:
                    app.act_pane, app.noact_pane  = app.lpane, app.rpane
                else:
                    app.act_pane, app.noact_pane = app.rpane, app.lpane
                    #x1,x2 = 0.,w/2

        #open/close new tab if click is at top line
        if y== 0:
            for i, t in enumerate(tab.pane.tabs):
                if t.win.check_focus(x,0):
                    if event == curses.BUTTON1_PRESSED:
                        tab.pane.act_tab = tab.pane.tabs[i]
                    elif event == curses.BUTTON3_PRESSED:
                        if len(tab.pane.tabs)>1:
                            close_tab(tab.pane.act_tab)
                        return 10
                    break
            else:
                if event == curses.BUTTON1_PRESSED:
                    #newtab doubleclick at empty space
                    if time.time() - click_tm < 0.3:
                        new_tab(tab.pane.act_tab)
                return 10

        #file click (select  file)
        if app.act_pane.mode not in [PANE_MODE_TREE_RIGHT, PANE_MODE_TREE_LEFT]:
            tab = app.act_pane.act_tab
            tab.file_i = tab.file_a + y - 3
            if tab.file_i > tab.file_z:
                tab.file_i = tab.file_z
                return 10
        #double click processing
        if event == curses.BUTTON1_PRESSED and y not in [0,1,2,h-1]:
            #double click delay 300ms
            tm =time.time()
            if tm - click_tm < 0.3:# and app.last_event == 1:
                curses.mousemask(0)
                enter(tab)
                curses.mousemask(curses.ALL_MOUSE_EVENTS)
                curses.ungetmouse(0,0,0,0,0)
        #files selection
        if event in [curses.BUTTON3_PRESSED] and y not in [1]:
            filename = tab.sorted[tab.file_i]
            if tab.selections.count(filename):
                tab.selections.remove(filename)
            else:
                tab.selections.append(filename)
    return 10


def __goto(path, tab):  #accepts only full path

    dirname, basename = '', ''
    if path.startswith(vfs.net_vfs):          #tuple as argument. req: python 2.5
        try:
            protocol, cmd = path.split('//',1)
        except:
            return
        fname = tab.sorted[tab.file_i]
        if tab.Vfs:
            tab.Vfs.exit()
        tab.Vfs = vfs.VFS_net(tab.pane.app, path, tab.path, fname, protocol)
        if not tab.Vfs.base:
            tab.Vfs = None
            return
        dirname, basename = ''.join([tab.Vfs.base, tab.Vfs.path]), ''
    elif path.startswith('pkg:'):
        try:
            protocol, cmd = path.split('//',1)
        except:
            return
        fname = tab.sorted[tab.file_i]
        if tab.Vfs:
            fname, tab.path = tab.Vfs.check_exit(cmd)

        tab.Vfs = vfs.VFS(cmd, tab.path, fname, protocol)
        if not tab.Vfs.base:
            tab.Vfs = None
            return
        dirname, basename = tab.Vfs.base, ''
    elif os.path.isabs(path):
        if os.path.isfile(path):
            dirname, basename = os.path.split(path)
        else:
            dirname, basename = path, ''
    else:
        pathfull = os.path.join(tab.path, path)
        if os.path.isfile(pathfull):
            dirname, basename = os.path.split(pathfull)
        else:
            dirname, basename = pathfull, ''

    if dirname and dirname != tab.path:
        tab.init(dirname)

    if basename:
        try:
            tab.file_i = tab.sorted.index(basename)
        except:
            tab.file_i = 0


def goto_dir(tab):
    todir = wcall.entry_gotodir(tab.path)
    tab.pane.app.display()
    if todir:
        __goto(todir, tab)


def goto_local_path(tab):
    tofile = wcall.entry_gotofile(tab.path)
    tab.pane.app.display()
    if tofile :
        thefiles = tab.sorted[tab.file_i:]
        for f in thefiles:
            if f.find(tofile) == 0:
                break
        else:
            return
        __goto(f, tab)
###############################################################################
# Bookmarks
def goto_bookmark(tab, num):
    todir = tab.pane.app.prefs.bookmarks[num]
    __goto(todir, tab)
    #tab.init(todir)

def bookmark_0(tab):
    goto_bookmark(tab, 0)
def bookmark_1(tab):
    goto_bookmark(tab, 1)
def bookmark_2(tab):
    goto_bookmark(tab, 2)
def bookmark_3(tab):
    goto_bookmark(tab, 3)
def bookmark_4(tab):
    goto_bookmark(tab, 4)
def bookmark_5(tab):
    goto_bookmark(tab, 5)
def bookmark_6(tab):
    goto_bookmark(tab, 6)
def bookmark_7(tab):
    goto_bookmark(tab, 7)
def bookmark_8(tab):
    goto_bookmark(tab, 8)
def bookmark_9(tab):
    goto_bookmark(tab, 9)

def select_bookmark(tab):

    bkm_list = []
    for i in range(len(tab.pane.app.prefs.bookmarks)):
        bkm_list.append(str(i)+': '+tab.pane.app.prefs.bookmarks[i])

    ret = wcall.menu_bookmark(bkm_list)
    if ret != -1:
        ret = ret.split(': ',1)
        if len(ret) == 2: ret = ret[1]
        __goto(ret, tab)


def set_bookmark(tab):

    while True:
        if tab.Vfs:
            path_bookmark = tab.Vfs.vfs_path(tab.path)
        else:
            path_bookmark = tab.path

        ch = wcall.get_bookmark_key()
        if 0x30 <= ch <= 0x39:         # 0..9
            tab.pane.app.prefs.bookmarks[ch-0x30] = path_bookmark
            break
        elif ch in [ord('a'), ord('A')]:            #A
            tab.pane.app.prefs.bookmarks.append(path_bookmark)
            break
        elif ch == -1:                 # Esc
            break


###############################################################################
# Selection
def select_item(tab):
    filename = tab.sorted[tab.file_i]
    tab.file_i_prev = tab.file_i
    tab.file_i += 1
    if filename == os.pardir:
        return SELECT_UPDATE
    if tab.selections.count(filename):
        tab.selections.remove(filename)
    else:
        tab.selections.append(filename)
    return SELECT_UPDATE

def select_group(tab):
    pattern = wcall.entry_select(tab.path)
    if pattern not in [None, '']:
        fullpath = os.path.join(tab.path, pattern)
        [tab.selections.append(os.path.basename(f)) for f in glob(fullpath)]

def deselect_group(tab):
    pattern = wcall.entry_deselect(tab.path)
    if pattern not in [None, '']:
        fullpath = os.path.join(tab.path, pattern)
        for f in [os.path.basename(f) for f in glob(fullpath)]:
            if f in tab.selections:
                tab.selections.remove(f)

def invert_select(tab):
    selections_old = tab.selections[:]
    tab.selections = []
    for f in tab.sorted:
        if f not in selections_old and f != os.pardir:
            tab.selections.append(f)


###############################################################################
# Panes and Tabs
def toggle_active_pane(tab):
    if tab.pane.mode == PANE_MODE_FULL or tab.pane.mode == PANE_MODE_HIDDEN:
        return
    else:
        app = tab.pane.app
        if app.act_pane == app.lpane:
            app.act_pane, app.noact_pane = app.rpane,app.lpane
        else:
            app.act_pane, app.noact_pane = app.lpane, app.rpane
    return 1

def toggle_panes(tab):
    app = tab.pane.app
    if tab.pane.mode == PANE_MODE_FULL:
        # now => 2-panes mode
        app.lpane.mode, app.rpane.mode = PANE_MODE_LEFT, PANE_MODE_RIGHT
    else:
        # now => 1-pane mode
        app.act_pane.mode, app.noact_pane.mode = PANE_MODE_FULL, PANE_MODE_HIDDEN
    app.display()

    for tab in app.lpane.tabs + app.rpane.tabs:
        tab.fix_limits()

def swap_tabs(tab):
    if tab.pane.mode == PANE_MODE_FULL:
        return
    app = tab.pane.app
    app.lpane.mode, app.rpane.mode = app.rpane.mode, app.lpane.mode
    app.display()

def same_tabs(tab):
    othertab = tab.pane.app.noact_pane.act_tab
    othertab.init(tab.path)
    othertab.Vfs = tab.Vfs

def new_tab(tab):
    if len(tab.pane.tabs) >= 4:
        wcall.err_create_tabs()
        return
    app=tab.pane.app
    path = tab.path
    if tab.Vfs:
        #path = os.path.dirname(tab.Vfs.vbase)
        path = os.sep

    idx = app.act_pane.tabs.index(tab)
    newtab = main.Tab(path, app.act_pane,idx+1)
    app.act_pane.tabs.insert(idx+1, newtab)
    app.act_pane.act_tab = newtab

def close_tab(tab):
    if len(tab.pane.tabs) == 1:
        wcall.err_last_tab()
        return
    app=tab.pane.app
    idx = app.act_pane.tabs.index(tab)
    app.act_pane.act_tab = app.act_pane.tabs[idx-1]
    app.act_pane.tabs.remove(tab)

def left_tab(tab):
    idx = tab.pane.tabs.index(tab)
    if idx > 0:
        tab.pane.act_tab = tab.pane.tabs[idx-1]

def right_tab(tab):
    idx = tab.pane.tabs.index(tab)
    if idx < len(tab.pane.tabs) - 1: # and idx < 3
        tab.pane.act_tab = tab.pane.tabs[idx+1]

def tree(tab):
    if tab.Vfs:
        return
    app = tab.pane.app
    if app.act_pane.mode == PANE_MODE_LEFT:
        app.act_pane.mode = PANE_MODE_TREE_LEFT
        return
    elif app.act_pane.mode == PANE_MODE_RIGHT:
        app.act_pane.mode = PANE_MODE_TREE_RIGHT
        return
    elif  app.act_pane.mode == PANE_MODE_TREE_LEFT:
        app.act_pane.mode = PANE_MODE_LEFT
    elif  app.act_pane.mode == PANE_MODE_TREE_RIGHT:
        app.act_pane.mode = PANE_MODE_RIGHT

    t=tab.pane.tree
    tab.pane.display()
    tab.init(t.path)



###############################################################################
# File opeartions

def __file_cpmv__(tab, func):

  
    fs = __get_selections_list(tab)
    if fs[0] == os.pardir:
            return

    fs = map(enc_str, fs)    
    path = enc_str(tab.path)
    #curses.endwin()
    #print fs
    
    if func == 'delete':
        ProcessDeleteLoop(tab.pane.app, fs, path).run()
    elif func in ['copy', 'move']:

        destdir = tab.pane.app.noact_pane.act_tab.path + os.sep
        destdir = wcall.entry_destination(tab.path, func, fs, destdir)

        if destdir:
            destdir = enc_str(destdir)
            ProcessCopyMoveLoop(tab.pane.app, '', func,
                                    fs, path, destdir).run()
        else:
            return
    elif func in ['rename', 'backup']:

        for filename in fs:            
            newname =wcall.entry_destination(path, func, [filename], filename)

            newname = enc_str(newname)
            filename = enc_str(filename)
           
            #curses.endwin()
            #print newname
            #print filename

            #if dec_str(newname) and dec_str(newname) != dec_str(filename):
            if newname and newname != filename:
                ProcessRenameBackupLoop(tab.pane.app, '', func,
                                    [filename], path, newname).run()
    tab.selections = []
    tab.refresh()


def copy(tab):
    __file_cpmv__(tab,'copy')

def move(tab):
    __file_cpmv__(tab,'move')

def rename(tab):
    __file_cpmv__(tab,'rename')

def backup(tab):
    __file_cpmv__(tab,'backup')

def delete(tab):
    __file_cpmv__(tab,'delete')

def make_dir(tab):
    newdir = wcall.entry_makedir(tab.path)
    if newdir :
        ans = mkdir(tab.path, newdir)
        if ans:
            wcall.err_makedir('%s (%s)' % (ans, newdir))
            return
        tab.pane.app.regenerate()


###############################################################################
# Dialogs/Menus/Info

def create_link(tab):
    othertab = tab.pane.app.noact_pane.act_tab
    pointto = os.path.join(tab.path, tab.sorted[tab.file_i])
    newlink = os.path.join(othertab.path, tab.sorted[tab.file_i])

    newlink, pointto = wcall.dentry_createlink(pointto, newlink)

    if newlink == None or pointto == None:
        return
    if newlink == '':
        wcall.err_emptylink()
        return
    if pointto == '':
        wcall.err_emptyfilename()
        return
    try:
        os.symlink(pointto, newlink)
    except OSError, e:
        wcall.err_editlink('%s (%s)' % (e, tab.sorted[tab.file_i]))
    tab.pane.app.regenerate()


def edit_link(tab):
    fullfilename = os.path.join(tab.path, tab.sorted[tab.file_i])
    if not os.path.islink(fullfilename):
        return
    pointto = wcall.entry_editlink(tab.path, tab.sorted[tab.file_i], os.readlink(fullfilename))
    if pointto in [None, '']:
        return
    elif pointto != os.readlink(fullfilename):
        ans = modify_link(pointto, fullfilename)
        if ans:
            wcall.err_editlink('%s (%s)' % (ans, tab.sorted[tab.file_i]))
    tab.pane.app.regenerate()



def __compress( tab, func,  dest = None, arc_type = None):
    args = tab.path, dest, arc_type
    fs = __get_selections_list(tab)
    fcompress.ProcessUnCompressLoop(tab.app, func, fs, *args).run()
    tab.selections = []


def file_menu(tab):
    app = tab.pane.app
    cmd = wcall.menu_file()
    if cmd == -1:
        return
    app.display()
    cmd = cmd[0]
    if cmd == '@':
        do_something_on_file(tab)
    elif cmd == 'i':
        show_file_info(tab)
    elif cmd == 'l':
        edit_link(tab)
    elif cmd == 'n':
        create_link(tab)
    elif cmd == 'p':
        i, change_all = 0, 0
        selections = __get_selections_list(tab)
        for f in selections:
            i += 1
            if not change_all:
                ret = wcall.win_chmod_chown(f, tab.files[f], app, i, len(selections))
                if ret == -1:
                    break
                elif ret == 0:
                    continue
                elif ret[3] == 1:
                    change_all = 1
            filename = os.path.join(tab.path, f)
            ans = files.chmod(filename, ret[0])
            if ans:
                wcall.err_chmod('%s (%s)' % (ans, filename))

            ans = files.chown(filename, ret[1], ret[2])
            if ans:
                wcall.err_chown('%s (%s)' % (ans, filename))
        tab.selections = []
    elif cmd == 'g':
        __compress(tab, 'ucomp_file', tab.path, 'gz:')
    elif cmd == 'b':
        __compress(tab, 'ucomp_file', tab.path, 'bz2:')
    elif cmd == 'x':
        __compress(tab, 'uncomp_dir', tab.path)
    elif cmd == 'u':
        __compress(tab, 'uncomp_dir', app.noact_pane.act_tab.path)
    elif cmd == 'c':
        __compress(tab, 'comp_dir', tab.path, 'tgz:')
    elif cmd == 'd':
        __compress(tab, 'comp_dir', tab.path, 'tbz2:')
    elif cmd == 'z':
        __compress(tab, 'comp_dir', tab.path, 'zip:')
    elif cmd == 'r':
        __compress(tab, 'comp_dir', tab.path, 'rar:')
    app.regenerate()


def general_menu(tab):
    cmd = wcall.menu_general()
    if cmd == -1:
        return
    tab.pane.app.display()
    cmd = cmd[0]
    if cmd == '/':
        findgrep(tab)
    elif cmd == 'g':
        goto_dir(tab)
    elif cmd == '#':
        show_dirs_size(tab)
    elif cmd == 's':
        sort(tab)
    elif cmd == 't':
        tree(tab)
    elif cmd == 'f':
        show_fs_info()
    elif cmd == 'o':
        #command_line(tab)
        open_shell(tab)
    elif cmd == 'c':
        __view_edit(tab.app, utils.insert_backslash(tab.app.prefs.file), 0, True)
        tab.app.prefs.load()
    elif cmd == 'd':
        tab.app.prefs.check_progs()
        tab.app.prefs.save()
        tab.app.prefs.load()
        wcall.msg_default_settings()


def resize_window(tab):
    tab.app.resize()


def refresh_screen(tab):
    tab.app.regenerate()


def quit(tab):
    if tab.pane.app.prefs.confirmations['quit']:
        if wcall.cfm_quit() != 1:
            return
    return -1

def open_shell(tab):

    curses.endwin()
    path = utils.insert_backslash(tab.path)
    os.system('cd \"%s\"; %s ' % (tab.path, tab.pane.app.prefs.progs['shell']))
    

def view_shell(tab):

    curses.endwin()
    curses.cbreak()
    tab.pane.frame.win.nodelay(0)
    c = tab.pane.frame.win.getch()

    if c == ord('o'):
        open_shell(tab)

    tab.pane.frame.win.nodelay(1)
    #curses.curs_set(0)
    tab.refresh()
    curses.raw()


def command_line(tab):
    app = tab.pane.app

    app.cmdrunning = True
    com = wcmd.CommandEntry(app,1,1,tab.path).run()
    app.cmdrunning = False
    if com:
        curses.endwin()

        path = utils.insert_backslash(tab.path)
        strln = (max(app.maxw/2 - len(com)-2, 0))*"-"
        os.system("%s --login -i -c\
                    \"echo -e '\E[32mCommand: \E[31m%s \E[32m%s';\
                    tput sgr0; cd %s; %s\""\
                    % (app.prefs.progs['shell'], com, strln ,path, com))

        curses.curs_set(0)
        return 10


######################################################################
##### Utils

def __cygwin_convert_path(path):
    try:
        path = utils.insert_backslash(os.popen('cygpath.exe -w %s' %path).readlines()[0])
    except:
        return None
    return path


def __view_edit(app, path, line, edit = 0):

    if not path:
        wcall.err_view(path)
        return

    #need to convert path under cygwin
    if app.prefs.options['cygwin']:
        path = __cygwin_convert_path(path)
        if not path: 
            return

    if edit:
        prog = app.prefs.progs['editor']
    else:
        prog = app.prefs.progs['pager']

    if line > 0:
        cmd ='%s +%d \"%s\"' % (prog, line, path)
    else:
        cmd = '%s %s' % (prog, path)

    curses.curs_set(0)
    curses.endwin()
    #os.system(cmd)
    os.system("%s --login -i -c \'cd %s; %s \'"\
                % (app.prefs.progs['shell'], os.path.dirname(path), cmd))

    curses.curs_set(0)
    app.regenerate()


def view_file(tab):
    path = os.path.join(tab.path, tab.sorted[tab.file_i])

    __view_edit(tab.app, utils.insert_backslash(path), 0, False) #view


def edit_file(tab):
    path = os.path.join(tab.path, tab.sorted[tab.file_i])
    __view_edit(tab.app,  utils.insert_backslash(path), 0, True) #edit

def do_execute_file(tab):
    filename = tab.sorted[tab.file_i]
    filename = os.path.join(tab.path, filename)
    sys.stdout = sys.stderr = '/dev/null'
    curses.endwin()
    if tab.pane.app.prefs.options['detach_terminal_at_exec']:
        utils.run_detached(filename)
        curses.curs_set(0)
    else:
        os.system('"%s"' % filename)
        curses.curs_set(0)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def __cmd_file(tab, cmd, file):
    if cmd:
        curses.endwin()
        #os.system('%s \"%s\"' % (cmd, file))
        os.system('cd \"%s\"; %s \"%s\"' % (tab.path, cmd, file))
        curses.curs_set(0)
        tab.pane.app.regenerate()


def do_something_on_file(tab):
    cmd = wcall.entry_dosmthing(tab.path)
    if cmd:
        selections = __get_selections_list(tab)
        for f in selections:
            __cmd_file(tab, cmd, f)
        tab.selections = []


def show_file_info(tab):
    selections = __get_selections_list(tab)
    for f in selections:
        buf = files.full_file_info(tab.path, f, tab.app.maxw)
        wcall.win_info_file(f, buf)
    tab.selections = []


def show_fs_info():
    ret = files.get_fs_info_buf()
    if ret[0] == -1:                # error
        wcall.err_filesyst(ret[1])
    else:
        wcall.win_info_fsystem(ret)

def __do_show_dirs_size(filename, path):
    return files.get_fileinfo(os.path.join(path, filename), False, True)

def show_dirs_size(tab):
    if tab.selections:
        lst = tab.selections
    else:
        lst = tab.files.keys()
    dirs = []
    for f in lst:
        if  tab.files[f][files.FT_TYPE] in [files.FTYPE_DIR, files.FTYPE_LNK2DIR] \
            and f != os.pardir:
            dirs.append(f)

    res = ProcessDirSizeLoop(tab.pane.app, 'Calculate Directories Size',
                             __do_show_dirs_size, dirs, tab.path).run()
    if res != None and type(res) == type([]) and len(res):
        for i, f in enumerate(dirs):
            try:
                tab.files[f] = res[i]
            except IndexError: # if stopped by user len(res) < len(dirs)
                pass

def sort(tab):
    options = tab.pane.app.prefs.options
    ktable = {
        ord('o'):files.SORT_None,
        ord('O'):files.SORT_None,
        ord('n'):files.SORT_Name,
        ord('N'):files.SORT_Name_rev,
        ord('e'):files.SORT_Ext,
        ord('E'):files.SORT_Ext_rev,
        ord('s'):files.SORT_Size,
        ord('S'):files.SORT_Size_rev,
        ord('m'):files.SORT_Mtime,
        ord('M'):files.SORT_Mtime_rev,
        }

    ch = wcall.menu_sort()
    if ch == -1:
        return
    ch = ch[0]
    options['sort'] =ktable[ord(ch)]

    #while True:
        #ch = wcall.get_sort_key()
        #if ktable.has_key(ch):
            #options['sort'] =ktable[ch]
            #break
        #elif ch == -1:                 #Esc
            #break

    old_filename = tab.sorted[tab.file_i]
    old_selections = tab.selections[:]
    tab.init(tab.path)
    tab.file_i = tab.sorted.index(old_filename)
    tab.fix_limits()
    tab.selections = old_selections


def do_special_view_file(tab):
    fullfilename = os.path.join(tab.path, tab.sorted[tab.file_i])
            
    prog = None    
    if tab.pane.app.prefs.options['cygwin']:
        prog = 'cygstart'
    else:
        ext = os.path.splitext(fullfilename)[1].lower()[1:]
        for type, exts in tab.pane.app.prefs.filetypes.items():
            if ext in exts:
                prog = tab.pane.app.prefs.progs[type]
                break
            
    
    if prog:
        sys.stdout = sys.stderr = '/dev/null'
        if tab.pane.app.prefs.options['detach_terminal_at_exec']:
            utils.run_detached(prog, fullfilename)
            curses.curs_set(0)
        else:
            curses.endwin()
            os.system('%s \"%s\"' % (prog, fullfilename))
            curses.curs_set(0)
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            
    elif not prog:
        if wcall.err_runprog():
            view_file(tab)            
            

    tab.pane.app.regenerate()

def __panelize(tab, path, lst):
    tab.nfiles =  len(lst)
    tab.sorted = lst
    for f in lst:
        path = os.path.join(tab.path, f)
        tab.files[f]  = files.get_fileinfo(path, 0)
    tab.fix_limits()


def findgrep(tab):
    fs, pat = wcall.dentry_findgrep(tab.path)
    if fs == None or fs == '':
        return
    path = os.path.dirname(fs)
    fs = os.path.basename(fs)

    if path in [None, '']:
        path = tab.path
    if path[0] != os.sep:
        path = os.path.join(tab.path, path)

    tab.app.display() #clear screen from previos dialog
    st, m = wcall.win_searching(tab.pane.app, path, fs, pat)
    if st ==-1:
        return

    par = ''
    while 1:
        cmd, par = wcall.win_search_list(m, par)
        f, line = '', 0
        if par:
            if pat:
                try:
                    line = int(par.split(':')[0])
                except ValueError:
                    f = os.path.join(path, par)
                else:
                    f = os.path.join(path, par[par.find(':')+1:])
            else:
                f = os.path.join(path, par)
        if cmd == 0:             # goto file
            __goto(f, tab)
            break
        elif cmd == 1:           # panelize
            __panelize(tab, path, m)
            break
        elif cmd == 2:           # view
            __view_edit(tab.app, utils.insert_backslash(f), line, 0)
        elif cmd == 3:           # edit
            __view_edit(tab.app, utils.insert_backslash(f), line, 1)
        elif cmd == 4:
            cmd2 = wcall.entry_dosmthing(tab.path)
            __cmd_file(tab, cmd2, f)
        else:
            break
