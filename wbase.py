# -*- coding: iso8859-1 -*-

"""wbase.py"""

import sys
import os.path
import curses
import curses.panel
import wcall
from __init__ import *


historic = []
###############################################################################
class Window:

    def __init__(self, app, title, text, btmtext, clr_ttl, clr_wnd, clr_btm,\
                             clr_txt, waitkey = 1, w = 0, h = 0, x = 0, y = 0):

        self.waitkey = waitkey
        
        self.title = dec_str(title)
        #self.text = enc_str(text)
        
        self.btmtext = dec_str(btmtext)
        
        self.lines = (dec_str(text.replace('\t', ' ' * 4))).split('\n')
        
        self.length, self.blength, self.tlength = \
                                 max(map(len, self.lines)),\
                                 len(self.btmtext ), len( self.title)
                                 
        self.clr_ttl, self.clr_wnd, self.clr_btm, self.clr_txt =\
                                  clr_ttl, clr_wnd, clr_btm, clr_txt

        if w:
            self.w, self.h = w, h
        else:
            maxln = max(self.tlength, self.blength, self.length)            
            self.w, self.h = min(maxln+6, (app.maxw - 2)),  len(self.lines) + 4
            w, h = self.w, self.h
            
        if x:
            self.y, self.x = y, x
        else:
            self.y, self.x = int((app.maxh- h)/2), int((app.maxw - w)/2)
            
        try:
            win = curses.newwin(h, w, self.y, self.x)
            self.pwin = curses.panel.new_panel(win)
            self.pwin.top()
        except curses.error:
            print 'Can\'t create window'            
            sys.exit(-1)
            
        self.show_window()


    def show_window(self):
              
#        bd_att  =  self.bd_att
        title, btmtext = self.title, self.btmtext
        tlength, blength = self.tlength, self.blength
        w, h = self.w, self.h

        win = self.pwin.window()
        win.attrset(self.clr_wnd)
        win.bkgdset(self.clr_txt)
        win.erase()

        win.border(curses.ACS_VLINE, curses.ACS_VLINE,
                   curses.ACS_HLINE, curses.ACS_HLINE, 
                   curses.ACS_ULCORNER, curses.ACS_URCORNER,
                   curses.ACS_LLCORNER, curses.ACS_LRCORNER)
        
        win.addstr(0, max(int((w-tlength-2)/2),0), ' ' + enc_str(title[:w-2])+\
                                                             ' ', self.clr_ttl)
        
        for i in range(len(self.lines)):
            line = enc_str(self.lines[i][:w-4])
            try:
                win.addstr(2+i, 2, line, self.clr_txt)
            except:
                pass                
             
        win.addstr(h-1, int((w-blength)/2), enc_str(btmtext[:w-2]), self.clr_btm)
        win.refresh()
        win.keypad(1)

    def run(self):
        if self.waitkey:
            while not self.pwin.window().getch():
                pass
        else:
            pass
        self.pwin.hide()

class ProgressBar:
    def __init__(self, x, y, h, w, clr1, clr2):
        self.x, self.y, self.h, self.w =  x, y, h, w
        self.clr1 = clr1
        self.progressbar = curses.newpad(self.h, w)
        self.progressbar.attrset(clr1)
        self.progressbar.bkgd(curses.ACS_CKBOARD, clr2)
        self.pw = -1

    def refresh(self, percent):
        try:
            percent = min(max(percent,0),100)
            pw = int(percent*(self.w-1)/100.)
            self.progressbar.erase()
            self.progressbar.addstr(0, 0, ' '*pw, self.clr1)
            self.progressbar.noutrefresh(0, 0, self.y, self.x, self.y + self.h, self.x + self.w)
        except:
            return

class Button:
    def __init__(self, name, x,y, rid = 0, clr = None):
        self.name = name
        self.rid = rid
        self.w = len(name)
        self.pad = curses. newpad(1, self.w+1)
        self.y, self.x = y, x

    def setname(self,name):
        self.name = name

    def refresh(self, clr):
        try:
            self.pad.erase()
            self.pad.addstr(0, 0, self.name,  clr)
            self.pad.refresh(0, 0, self.y, self.x, self.y+1, self.x+self.w-1)
        except:
            return

    def check_focus(self,x,y):
        if  self.x <= x <= self.x+self.w and self.y == y:
            return True
        return False


class Bar:
    def __init__(self, w, y,  clr):
        self.w, self.y, self.clr = w, y,  clr
        self.pad = curses. newpad(1, self.w)
        self.refresh()

    def refresh(self):
        try:
            self.pad.attrset(self.clr)
            self.pad.bkgdset(self.clr)
            self.pad.erase()
            self.pad.noutrefresh(0, 0, 0, 0, self.y, self.w-1)
        except:
            return

    def resize(self, y, w):
        self.y, self.w = y, w
        self.pad.resize(1, w)
        self.refresh()


class StatusBar(Bar):

    def __init__(self, w, y, clr):
        self.s =[]
        Bar.__init__(self,w, y,  clr)

    def set_strings(self,s):
        self.s = s

    def refresh(self):
        try:
            self.pad.attrset(self.clr)
            self.pad.bkgdset(self.clr)
            self.pad.erase()
            self.pad.addstr(self.s[0])
            self.pad.addstr(0, 20, self.s[1])
            self.pad.addstr(0, self.w-len(self.s[2]), self.s[2])
        except:
            pass
        try:
            self.pad.noutrefresh(0, 0, self.y-1, 0, self.y, self.w-1)
        except:
            return


class TabButton:

    def __init__(self, y, w, clr_act, clr_inact):
        self.w = w
        self.pad = curses. newpad(1, self.w)
        self.y, self.x = y, 0
        self.clr_act, self.clr_inact = clr_act, clr_inact

    def fit_text(self, text, w):

        text = dec_str(text)
        l = len(text)
        if l > w-2:
            text = ('%s~' % text[:w-3])
        else:
            text = text + ' '*(w-2-l)
        return enc_str(text)


    def set_attrib(self,text,x,w,active_flag):
        self.text = self.fit_text(text,w)
        self.x, self.w = x, w
        self.active_flag = active_flag

    def refresh(self):
        clr = self.clr_inact
        if self.active_flag:
            clr = self.clr_act
        try:
            self.pad.attrset(self.clr_inact)
            self.pad.bkgdset(self.clr_inact)
            self.pad.erase()
            self.pad.addstr(0, 0, '(',  self.clr_inact)
            self.pad.addstr(0, 1, self.text,  clr)
            self.pad.addstr(0, self.w-1, ')',  self.clr_inact)
            self.pad.noutrefresh(0, 0, self.y, self.x, self.y+1, self.x+self.w-1)
        except:
            return

    def check_focus(self,x,y):
        if  self.x <= x <= self.x+self.w and self.y == y:
            return True
        return False


class PaneFrame:
    def __init__(self, app, mode, clr_act, clr_inact, clr_clmn, clr_pth):
        self.app = app
        self.mode = mode

        self.title_path = '' #header string
        self.footer_str = '' #footer string

        self.active = 0
        self.sc_a, self.sc_n, self.sc_i,= 0,0,0
        self.dims = self.__calculate_dims()

        self.clms = { NAME:['Name', 0],
                      PERMS:['Perm', 10],
                      PERMSNUM:['Perm', 6],
                      OWNER:['Owner', 8],
                      GROUP:['Group', 8],
                      SIZE:['Size', 8],
                      SIZEHUMN:['Size', 7],
                      MTIME_LONG:['Mtime', 18],
                      MTIME:['Mtime', 15],
                      MTIME_MC:['Mtime', 13],
                      CTIME_LONG:['Ctime', 18],
                      CTIME:['Ctime', 15],
                      CTIME_MC:['Ctime', 13],
                      ATIME_LONG:['Atime', 18],
                      ATIME:['Atime', 15],
                      ATIME_MC:['Atime', 13],
                     }
        #self.clms =  {  'name':['Name', 0],
                        #'perms':['Perm', 10],
                        #'permsnum':['Perm', 6],
                        #'owner':['Owner', 8],
                        #'group':['Group', 8],
                        #'size':['Size', 8],
                        #'sizehumn':['Size', 7],
                        #'mtime_long':['Mtime', 18],
                        #'mtime':['Mtime', 15],
                        #'mtime_mc':['Mtime', 13],
                        #'ctime_long':['Ctime', 18],
                        #'ctime':['Ctime', 15],
                        #'ctime_mc':['Ctime', 13],
                        #'atime_long':['Atime', 18],
                        #'atime':['Atime', 15],
                        #'atime_mc':['Atime', 13],
                     #}

        try:
            self.win = curses.newwin(self.dims[0], self.dims[1],\
                                                 self.dims[2], self.dims[3])
        except curses.error:
            print 'Can\'t create Panel window'
            sys.exit(-1)

        self.cursor = Cursor(self.app, self.dims[3]+1, self.dims[3]+self.dims[1]-2 ,0,)
        self.win.keypad(1)
        self.clr_act, self.clr_inact, self.clr_clmn, self.clr_pth =\
                                                  clr_act, clr_inact, clr_clmn, clr_pth
        self.refresh_colors()
        self.__calculate_columns()


    def refresh_colors(self):
        if self.active:
            self.win.attrset(self.clr_act)
            self.win.bkgdset(self.clr_act)
            self.attr1 = self.clr_clmn
        else:
            self.win.attrset(self.clr_inact)
            self.win.bkgdset(self.clr_inact)
            self.attr1 = self.clr_inact
        self.attr2 = self.clr_pth

    def __calculate_dims(self):
        a = self.app
        if self.mode == PANE_MODE_HIDDEN:
            h, w, y0, x0 = 1, 1, 0, 0
        elif self.mode in [PANE_MODE_LEFT, PANE_MODE_TREE_LEFT ]:
            h, w, y0, x0 = a.maxh-2, int(a.maxw/2), 1, 0
        elif self.mode in [PANE_MODE_RIGHT, PANE_MODE_TREE_RIGHT ]:
            h, w, y0, x0 = a.maxh-2, a.maxw-int((a.maxw)/2), 1, int(a.maxw/2)
        elif self.mode == PANE_MODE_FULL:
            h, w, y0, x0  = a.maxh-2, a.maxw, 1, 0
        else:
            wcall.err_init_pane()
            h, w, y0, x0 = 0, 0, 0, 0
        return [h, w, y0, x0]


    def __set_show_columns(self):
        if self.mode == PANE_MODE_LEFT:
            self.show_clms = self.app.prefs.panels['left_columns'][:]
        elif self.mode == PANE_MODE_RIGHT:
            self.show_clms = self.app.prefs.panels['right_columns'][:]
        elif self.mode == PANE_MODE_FULL:
            self.show_clms = self.app.prefs.panels['fullpane_columns'][:]
        else:
            self.show_clms = []


    def __calculate_columns(self):

        self.__set_show_columns()
        w_name_col = self.dims[1]-2
        self.clms[NAME][1] = 0
        for c in self.show_clms:
            w_name_col-= self.clms[c][1]

        self.clms[NAME][1] = max(w_name_col,0)

        self.vlines_pos = []
        s = 1
        for c in self.show_clms:
            try:
                s += self.clms[c][1]
            except:
                wcall.err_undefined_column()
                continue
            if s < self.dims[1]:
                self.vlines_pos.append(s)


    def resize(self):
        self.dims = self.__calculate_dims()
        try:
            self.win.resize(self.dims[0], self.dims[1])
            self.win.mvwin(self.dims[2], self.dims[3])
        except:
            pass

        self.__calculate_columns()
        self.cursor.resize(self.dims[3]+1, self.dims[3]+ self.dims[1] - 2, 0)

    def erase(self):
        self.win.erase()


    def addline(self, y, buf, clr):
        if self.mode != PANE_MODE_HIDDEN:
            try:
                self.win.addstr(self.dims[2] + y +1, 1, buf, clr)
            except:
                pass

    def addtree_element(self, t, i, y, clr, selection = False):
        name, depth, f = t.tree[i]
        # build tree skeleton
        try:
            self.win.move(y, 1)
            if name != os.sep:
                for kk in range(depth):
                    self.win.addstr(' ')
                    self.win.addch(curses.ACS_VLINE)
                    self.win.addstr(' ')
                self.win.addstr(' ')
                if i == len(t.tree) - 1 or depth > t.tree[i+1][1]:
                    self.win.addch(curses.ACS_LLCORNER)
                else:
                    self.win.addch(curses.ACS_LTEE)
                self.win.addch(curses.ACS_HLINE)
            self.win.addstr(' ')

            # build tree items
            wl = self.dims[1] - 3*depth - 7
            if selection:
                self.win.addstr(name[:wl], clr)
                child_dirs = t.get_dirs(t.path)
                if len(child_dirs) > 0:
                    self.win.addstr(' ')
                    self.win.addch(curses.ACS_HLINE)
                    self.win.addch(curses.ACS_DIAMOND)
            else:
                self.win.addstr(name[:wl], clr)
        except:
            return


    def draw_cursor(self, i, line, clr, clr2):
        if self.mode != PANE_MODE_FULL:
            self.cursor.set_attrib(i, line, clr, clr2, self.vlines_pos)
        else:
            self.cursor.set_attrib(i, line, clr)
        self.cursor.refresh()


    def set_attrib(self, title_path, footer_str, mode, active, sc_a, sc_n, sc_i):
        self.title_path = title_path
        self.footer_str = footer_str
        self.mode = mode
        self.active = active
        self.sc_a, self.sc_n, self.sc_i,= sc_a, sc_n, sc_i
        self.resize()



    def refresh(self):
        
        if self.mode == PANE_MODE_HIDDEN:
            self.erase()
            return

        self.refresh_colors()
        self.cursor.resize(self.dims[3]+1, self.dims[3]+ self.dims[1] - 2, 0)

        buf=''
        if self.mode in [PANE_MODE_LEFT, PANE_MODE_RIGHT, PANE_MODE_FULL]:
            for i,c in enumerate(self.show_clms):
                try:
                    buf ='%s%s'% (buf, self.clms[c][0].center(self.clms[c][1]))
                except:
                    continue
        elif self.mode in [PANE_MODE_TREE_LEFT, PANE_MODE_TREE_RIGHT]:
            buf = 'Tree'

        if self.mode in [PANE_MODE_LEFT, PANE_MODE_RIGHT]:
            try:
                for col in self.vlines_pos:
                    self.win.vline(1, col, curses.ACS_VLINE, self.dims[0]-1)
            except:
                pass

        try:
            self.win.border(curses.ACS_VLINE, curses.ACS_VLINE,
                            curses.ACS_HLINE, curses.ACS_HLINE, 
                            curses.ACS_ULCORNER, curses.ACS_URCORNER,
                            curses.ACS_LLCORNER, curses.ACS_LRCORNER)
            #self.win.box()

            self.win.addstr(1, self.dims[2], buf, self.attr2)
            self.win.addstr(0, self.dims[2] + 1, self.title_path, self.attr1)

            self.win.addstr(  self.dims[0]-1, self.dims[2], self.footer_str, self.attr1)
        except:
            pass

        ScrollBar(self.win,  self.sc_a, self.sc_n, self.sc_i,\
                                 self.dims[2]+1,self.dims[0]-3,self.dims[1])

        self.win.noutrefresh()


class Cursor:
    def __init__(self, app, x1, x2, y, vlines_pos=[]):
        self.x1, self.x2, self.y, = x1, x2, y
        self.pad = curses.newpad(1, app.maxw*3)
        self.vlines_pos = vlines_pos

    def set_attrib(self, i, line, clr, clr2 = None, vlines_pos=[] ):
        self.vlines_pos = vlines_pos
        self.line = line
        self.clr, self.clr2 = clr, clr2
        if not self.clr2:
            self.clr2 = self.clr
        self.i = i

    def resize(self, x1, x2, y):
        self.x1, self.x2, self.y = x1, x2, y

    def refresh(self):
        try:
            x1, x2, y, i = self.x1, self.x2, self.y, self.i
            self.pad.attrset(self.clr2)
            self.pad.bkgdset(self.clr2)
            self.pad.erase()
            self.pad.addstr(0, 0, self.line, self.clr)
            for col in self.vlines_pos:
                self.pad.addch(0, col-1, curses.ACS_VLINE)
            self.pad.noutrefresh(0, 0, y + i, x1, y + i + 1, x2)
        except:
            return


class RotatingDash:

    def __init__(self, app, clr):
        self.anim_char = ('|', '/', '-', '\\')
        self.cursor_i = 0
        self.cur_win = curses.newpad(1, 2)
        self.cur_win.nodelay(1)
        self.clr = clr
        self.cur_win.attrset(self.clr )
        self.cur_win.bkgdset(self.clr )
        self.app = app

    def update(self):
        try:
            self.cur_win.erase()
            self.cur_win.addch(self.anim_char[self.cursor_i%4], self.clr)
            self.cur_win.refresh(0, 0, 0, self.app.maxw-2, 1, self.app.maxw-1)
            self.cursor_i += 1
            if self.cursor_i > 3:
                self.cursor_i = 0
        except:
            return


class ScrollBar:

    def __init__(self, parent, entry_a, entry_n, entry_i, y, h, w):

        y0, n = self.__calculate_scrollbar_dims(h, entry_n, entry_i)
        try:
            parent.vline(y0 + y, w - 1, curses.ACS_CKBOARD, n)
        except:
            pass
        if entry_a != 0:
            try:
                parent.vline(y, w - 1, '^', 1)
                if n == 1 and y0 == 0:
                    parent.vline(y + 1, w - 1, curses.ACS_CKBOARD, n)
            except:
                pass
        if entry_n > entry_a + h:
            try:
                parent.vline(h + y - 1, w - 1, 'v', 1)
                if n == 1 and y0 == h - 1:
                    parent.vline(h + y - 2, w - 1, curses.ACS_CKBOARD, n)
            except:
                pass

    def __calculate_scrollbar_dims(self, h, nels, i):
        y0 = n = 0
        h = max(h,1)
        if nels > h:
            n = max(int(h*h/nels),1)
            y0 = min(max(int(int(i/h)*h*h/nels),0),h - n)
        return y0, n


class EntryLine:

    def __init__(self, w, h, x, y, path, w_hist, w_compl,  panelpath, clr, clrf = None, rid = 0):
#    def __init__(self, w, h, x, y, clr, path, w_hist, w_compl,  panelpath, rid=0):
        try:
            self.entry = curses.newwin(3, w + 1, y, x)
        except curses.error:
            print 'Can\'t create window'
            sys.exit(-1)
                
        self.entry.keypad(1)
        self.x, self.y, self.h, self.w = x, y, h, w
        self.entry_width = w                
        self.text =dec_str(path)
                    
        self.clr = clr
        self.clrf = clrf
        if self.clrf:
            self.init_pos = 1    # with frame            
        else:
            self.init_pos = 0    # without frame (command line)            
        
        self.entry.attrset(self.clr)
        self.entry.bkgdset(self.clr)
                
        self.len_text = len(dec_str(self.text)) + self.init_pos
        self.pos = self.init_pos
        
        self.panelpath = panelpath        
        self.chlocl = self.ch_prev =''
        self.rid = rid
        self.w_complete, self.w_historic = w_compl, w_hist
        if w_hist:
            self.historic = historic[:]
            self.historic_i = len(self.historic)

    def show(self):
        
        self.len_text = len(self.text)
        #self.len_text = len(dec_str(self.text))
        text, len_text, pos = self.text, self.len_text, self.pos
        ew = self.entry_width - 1 - self.init_pos
        
        if pos < ew + self.init_pos:
            relpos = pos
            if len_text < ew:
                textstr = text + ' '*(ew - len_text)
            else:
                textstr = text[:ew]
        else:
            if pos < len_text - ew:
                fw = int(pos/ew)*ew
                relpos = pos - fw
                textstr = text[fw:fw + ew]
            else:
                relpos = ew - (len_text - pos)
                textstr = text[len_text - ew:] + ' '

        textstr = enc_str(textstr)
        try:                                    
            self.entry.erase()             
            if self.clrf:
                clr = self.clrf                
                #self.entry.box(0, 0)                                                            
                self.entry.border(curses.ACS_VLINE, curses.ACS_VLINE,
                           curses.ACS_HLINE, curses.ACS_HLINE, 
                           curses.ACS_ULCORNER, curses.ACS_URCORNER,
                           curses.ACS_LLCORNER, curses.ACS_LRCORNER)
            else:                
                clr = self.clr
            self.entry.attrset(clr)
            self.entry.bkgdset(clr)                                                            
            self.entry.addstr(self.init_pos, self.init_pos, textstr, self.clr)
            self.entry.move(1, relpos)
            
            self.entry.refresh()
        except:
            return

    def autocomplete(self, exe_comp, pth_comp):
        # virtual method
        return

    def standard_input(self, ch):
        if ch in [10, 13]:           # enter
            return 10
        elif ch in [0x03, 0x1B]:     # Ctrl-C, Esc
            return 0x03
        elif ch in [ord('\t')]:      # tab
            return ord('\t')
        elif ch in [0x14]:           # Ctrl-T
            if self.w_complete:
                self.autocomplete(True, True)
                return
        elif ch in [0x17]:          # Ctrl-W
            text = self.text
            if text in [None, '']:
                return
            elif text == os.sep:
                text = ''
            else:
                if text[self.len_text - 1] == os.sep:
                    text = os.path.dirname(text)
                text = os.path.dirname(text)
                if text != '' and text != os.sep:
                    text += os.sep
            self.text = text
            self.pos = len(self.text)
        elif ch in [0x04]:          # Ctrl-D
            self.text = ''
            self.pos = self.init_pos
        elif (ch in [curses.KEY_HOME, 0x16A]):  # home
            self.pos = self.init_pos
        elif (ch in [curses.KEY_END, 0x181]):   # end
            self.pos = self.len_text + self.init_pos
        elif ch in [curses.KEY_LEFT] and self.pos > self.init_pos:
            self.pos -= 1
        elif ch in [curses.KEY_RIGHT] and self.pos < self.len_text + self.init_pos:
            self.pos += 1
        elif ch in [8,127, curses.KEY_BACKSPACE] and self.len_text > 0 and  self.pos > self.init_pos:
            self.text =self.text[:self.pos - self.init_pos-1]+self.text[self.pos - self.init_pos:]
            self.pos -= 1
        elif ch in [curses.KEY_DC] and self.pos < self.len_text + self.init_pos:  # del
            self.text = self.text[:self.pos - self.init_pos] + self.text[self.pos - self.init_pos + 1:]
        elif self.len_text < 8192 and 32 <= ch <= 255 and ch not in [127]:
            if  128 <= ch <= 255 and self.chlocl=='' and g_encoding=='UTF-8' :
                self.chlocl = chr(ch)
                return
            else:
                try:
                    char = dec_str(self.chlocl + chr(ch))
                    self.text = (self.text[:self.pos - self.init_pos] + char + self.text[self.pos - self.init_pos:])
                    self.chlocl =''
                    self.pos += 1
                except:
                    pass

        elif ch in [curses.KEY_MOUSE]:
            n,x,y,z,event = curses.getmouse()
            if event == curses.BUTTON1_PRESSED:
                if self.check_focus(x,y):
                    self.pos = min (x-self.x, self.len_text )
                else:
                    return ch

    def check_focus(self,x,y):
        if  self.x <= x <= self.x+self.w and self.y == y:
            return True
        return False

    def manage_keys(self):
        while 1:
            self.show()
            #print 'key: \'%s\' <=> %c <=> 0x%X <=> %d' % \
                    #(curses.keyname(ch), ch & 255, ch, ch)
            ch  = self.entry.getch()
            ret =  self.standard_input(ch)
            if ret:
                return ret
