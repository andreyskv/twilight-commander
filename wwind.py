# -*- coding: iso8859-1 -*-

"""wwind.py"""

import sys
import os.path
import curses
import files
import color
import time

from wbase import *
from utils import insert_backslash

app = None

def cursor_show():
    try:
        curses.curs_set(2)
    except:
        curses.curs_set(1)

def cursor_hide():
    try:
        curses.curs_set(0)
    except:
        pass


class BookmarkWindow(Window):

    def __init__(self, title, text, btmtext):
        clr_w = color.WIND
        clr_t = color.WIND_TTL
        clr_txt = color.WIND_TXT
        Window.__init__(self,app,title, text, btmtext,\
                                             clr_t, clr_w, clr_txt, clr_txt)

    def run(self):
        while True:
            ch = self.pwin.window().getch()
            if ch in [0x03, 0x1B]:       # Ctrl-C, ESC
                self.pwin.hide()
                return -1
            elif 0x01 <= ch <= 0xFF:
                self.pwin.hide()
                return ch

class ProgressBarWindow(Window):

    def __init__(self, h, w, title, text, downtext, percent,
                 bd_att, bd_bg, pb_att, pb_bg, waitkey = 1, nprogress=1, copy_move = False):

        self.waitkey = waitkey
        self.nprogress = nprogress
        self.copy_move = copy_move
        #w, h = app.maxw - 20, 7
        if nprogress >= 2:
            h += 2
        Window.__init__(self, app, title, text, downtext,
                                    bd_att, bd_bg, pb_att, bd_bg, waitkey, w,h)
        self.bd_att, self.pb_att = bd_att, pb_att

        hpos = 4
        if self.copy_move:
            hpos += 2

        self.progress = ProgressBar(self.x+2, self.y + hpos , 1, self.w - 10, pb_att, pb_bg)
        if  nprogress >= 2:
            hpos += 2 
            self.progress2 = ProgressBar(self.x + 2, self.y + hpos , 1, self.w - 10, pb_att, pb_bg)

    def show(self, title, text, downtext, percent, percent2 = 0, txtFrom = '', txtTo = ''):
        try:
            win = self.pwin.window()
            win.erase()
            #win.box(0, 0)
            win.border(curses.ACS_VLINE, curses.ACS_VLINE,
                       curses.ACS_HLINE, curses.ACS_HLINE, 
                       curses.ACS_ULCORNER, curses.ACS_URCORNER,
                       curses.ACS_LLCORNER, curses.ACS_LRCORNER)

            hpos = 0
            win.addstr(hpos, int((self.w-len(title)-2)/2),' ' + title + ' ', self.bd_att)

            hpos += 2
            win.addstr(hpos, 2, text)

            if self.copy_move:
                hpos += 1
                win.addstr(hpos,2,'From: %s'% txtFrom, color.DIR)
                hpos += 1
                win.addstr(hpos,2,'To:   %s'% txtTo, color.SEL_FLS)

            hpos += 2
            win.addstr(hpos, self.w-8, '[%3d%%]' % percent)

            if  self.nprogress >= 2:
                hpos += 2
                win.addstr(hpos, self.w-8, '[%3d%%]' % percent2)

            win.addstr(self.h-1, int((self.w-len(downtext)-2)/2), ' ' + downtext + ' ')

            win.noutrefresh()
            self.progress.refresh(percent)
            if  self.nprogress >= 2:
                self.progress2.refresh(percent2)
            curses.doupdate()
        except:
            return

class ConfirmWindow(Window):
    #yes=1, all=0, no=1, none=0, abort=0
    def __init__(self,title, question, btn_flags = [1,0,1,0,0] , default = 0, h = 6):


        lines = question.split('\n')
        length = max(map(len, lines))
        w = min(max(50, length+5), app.maxw - 2)
        #w = min(max(50, len(question)+5), app.maxw - 2)

        self.clr_sel = color.FOCUS_ITEM
        self.clr_def = color.BUTTON
        clr_w = color.WIND
        clr_t = color.WIND_TTL
        clr_txt = color.WIND_TXT
        Window.__init__(self, app,title, question, '',
                                         clr_t, clr_w, clr_w, clr_txt, 0, w, h)
        cursor_hide()
        self.row = self.y + self.h - 2
        self.btn_flags = btn_flags
        dx = (self.w - 8*sum(btn_flags)) / (sum(btn_flags)+1)
        self.btn = []
        names = ['[ Yes ]', '[ All ]', '[ No ]', '[ NOne ]', '[ AborT ]']
        pids  = [1, 2, 0, -1, -2]
        col = self.x
        for i in range (0, len(pids)):
            if btn_flags[i] == 1:
                col += (dx + 1)
                b = Button(names[i], col, self.row, pids[i],self.clr_def )
                self.btn.append(b)
                col += b.w
        self.btn_len = len(self.btn)
        self.i = min(default, self.btn_len-1)

    def run(self):
        i, btn = self.i, self.btn
        while 1:
            for k in range(0,self.btn_len):
                btn[k].refresh(self.clr_def)
            btn[i].refresh( self.clr_sel)
            ch = self.pwin.window().getch()
            if ch in [curses.KEY_UP,  curses.KEY_RIGHT, ord('\t')]:
                i += 1
                if i >= self.btn_len:
                    i = 0
            elif ch in [curses.KEY_DOWN, curses.KEY_LEFT,]:
                i -= 1
                if i < 0:
                    i = self.btn_len-1
            elif ch in [ord('Y'), ord('y')] and self.btn_flags[0]:
                return 1
            elif ch in [ord('A'), ord('a')] and self.btn_flags[1]:
                return 2
            elif ch in [ord('N'), ord('n')] and self.btn_flags[2]:
                return 0
            elif ch in [ord('O'), ord('o')] and self.btn_flags[3]:
                return -1
            elif ch in [ord('T'), ord('t')]  and self.btn_flags[4]:
                return -2
            elif ch in [0x03, 0x1B]:
                return -2               # Ctrl-C, ESC
            elif ch in [10, 13]:        # Enter
                return self.btn[i].rid
            #process mouse
            elif ch == curses.KEY_MOUSE:
                n,x,y,z,event = curses.getmouse()
                if event == curses.BUTTON1_PRESSED:
                    for j in range(0,self.btn_len):
                        if btn[j].check_focus(x,y):
                            i = j
                            break
                elif event == curses.BUTTON1_RELEASED and btn[i].check_focus(x,y):
                    return btn[i].rid
        self.pwin.hide()
        return 0



class EntryLineComplete(EntryLine):

    # complete
    def complete(self, entrypath, panelpath):
        if not entrypath:
            path = panelpath
        elif entrypath[0] == os.sep:
            path = entrypath
        else:
            path = os.path.join(panelpath, entrypath)

        fs = []
        if os.path.isdir(path):
            basedir = path
            try:
                fs = os.listdir(path)
            except OSError:
                fs = []
        else:
            basedir = os.path.dirname(path)
            start = os.path.basename(path)
            try:
                entries = os.listdir(basedir)
            except OSError:
                entries = []
            fs = []
            for f in entries:
                if f.find(start, 0) == 0:
                    fs.append(f)
        # sort files with dirs. first
        d1,d2 = [],[]
        for f in fs:
            ff = os.path.join(basedir, f)
            if os.path.isdir(ff):
                d1.append(f + os.sep)
            else:
                d2.append(f)
        d1.sort()
        d2.sort()
        d1.extend(d2)
        return d1

    #complete from $PATH
    def complete_exe(self, entry):
        path = os.environ.get('PATH').split(':')
        #remove duplicates and non existant paths
        path.sort()
        last = path[-1]
        for i in range(len(path)-2, -1, -1):
            if last==path[i]: del path[i]
            else:
                if(not os.access(path[i],os.R_OK)):
                    del path[i]
                else:
                    last=path[i]
        #all files in $PATH
        files = []
        for i in range(len(path)):
            try:
                pathlist = os.listdir(path[i])
            except OSError:
                pathlist = []
            for j in range(len(pathlist)):
                if pathlist[j].find(entry, 0) == 0:
                    files.append(pathlist[j])
        files.sort()
        return files

    def join(self, directory, file):
        if not os.path.isdir(directory):
            directory = os.path.dirname(directory)
        return os.path.join(directory, file)


    def autocomplete(self, exe_comp, pth_comp):
        text = self.text
        inp_text = text[:self.pos].lstrip()
        inp_stings = inp_text.split()
        l = len(inp_stings)
        edit=''
        if l:
            edit=inp_stings[l-1]
            for i in range (l):
                if inp_stings[l-i-2].endswith('\\'):
                    edit = inp_stings[l-i-2].replace('\\',' ')+edit
                else:
                    break

        search = enc_str(edit)
        if os.sep in edit:                   #completing path
            if(pth_comp):
                entries = self.complete(os.path.expanduser(search), self.panelpath)
        else:                                #completing command
            if(exe_comp):
                entries = self.complete_exe(search)

        if not entries:
            return
        elif len(entries) == 1:
            selected = entries.pop()
        else:
            y, x = self.entry.getbegyx()
            if y == app.maxh - 1:                    #for command line
                y -= (min(len(entries)+4, app.maxh-1))

            cursor_hide()
#             selected = ListBox(entries, y+1 , x+self.pos ).run()
            selected = ListBox(app,entries,'', y + 1 , x+self.pos ).run()
            cursor_show()

            app.act_pane.display()
            app.noact_pane.display()

        if selected != -1:
            selected = insert_backslash(dec_str(selected))
            if os.sep in edit:
                text_l = self.join(text[:self.pos], selected)
            else:
                text_l = ''.join([text[:self.pos-len(edit)], selected])
            self.text = (text_l+ text[self.pos:])
            self.pos = len(text_l)


######################################################################
class Entry(Window):
    """An entry window to enter a dir. or file, a pattern, ..."""

    def __init__(self, title, help, path = '', with_historic = 1,
                 with_complete = 1, panelpath = '', h = 8):
      
        w = min(max(60, len(dec_str(help))+5), app.maxw - 2)

        self.clr_w = clr_w = color.WIND
        self.clr_ttl = clr_t = color.WIND_TTL
        self.clr_txt = clr_txt = color.WIND_TXT
        self.clr_sel = color.FOCUS_ITEM
        self.clr_def = color.BUTTON
        self.clr_ent = color.ENTRY
        Window.__init__(self, app, title, help, '', clr_t, clr_w,\
                                                    clr_w, clr_txt, 0,w,h)
        self.entry = EntryLineComplete(w-5, h,
                                   int((app.maxw - w + 4)/2),
                                   int((app.maxh - h)/2) + (h-6),                                   
                                   path,
                                   with_historic, with_complete,
                                   panelpath,
                                   self.clr_ent,
                                   self.clr_w,                 
                                   1)
        self.row  =  self.y + h - 2
        col1 = self.x + int(w*0.2) + 1
        col2 = self.x + int(w*0.8) - 6


        self.btn = []
        self.btn.append(Button('[ <Ok> ]', col1, self.row, 1, self.clr_def))
        self.btn.append(Button('[Cancel]', col2, self.row, 0, self.clr_def))
        self.btn.append(self.entry)
        self.with_historic = with_historic

        self.i = 2

    def run(self):
        i = self.i
        btn, btn_len = self.btn, len(self.btn)
        entrylist = []
        ret = 0
        while 1:
            self.show_window()
            for k in range(btn_len):
                if not isinstance(btn[k], EntryLine):
                    btn[k].refresh(self.clr_def)
                else:
                    btn[k].show()
            if isinstance(btn[i], EntryLine):
                cursor_show()
                ch = btn[i].manage_keys()
            else:
                cursor_hide()
                btn[i].refresh(self.clr_sel)
                ch = self.pwin.window().getch()
            #check pressed key
            if ch in [0x03, 0x1B]:      # Ctrl-C, ESC
                ret = 0
                break
            elif ch in [10, 13]:        # enter
                if  btn[i].rid == 0:    # cancel button
                    ret = 0
                else:
                    ret = 1
                break
            elif ch in [curses.KEY_UP,  curses.KEY_RIGHT, ord('\t')]:
                i += 1
                if i >= btn_len:
                    i = 0
            elif ch in [curses.KEY_DOWN, curses.KEY_LEFT,]:
                i -= 1
                if i < 0:
                    i = btn_len-1
            elif ch in [ord('O'), ord('o')]:
                ret = 1
                break
            elif ch in [ord('C'), ord('c')]:
                ret = 0
                break
            elif ch == curses.KEY_MOUSE:
                n,x,y,z,event = curses.getmouse()
                if event == curses.BUTTON1_PRESSED:
                    for j in range(0,btn_len):
                        if btn[j].check_focus(x,y):
                            i = j
                            break
                elif event == curses.BUTTON1_RELEASED and btn[i].check_focus(x,y):
                    ret = btn[i].rid
                    break
        for k in range(btn_len):
            if isinstance(btn[k], EntryLine):
                if self.with_historic and btn[k].text not in [None,'','*']:
                    historic.append(enc_str(btn[k].text))  #unlimited history list
                if ret:
                    entrylist.append(enc_str(btn[k].text))
                else:
                    entrylist.append(None)
        cursor_hide()
        self.pwin.hide()
        return entrylist


class DoubleEntry(Entry):
    #"""An entry window to enter 2 dirs. or files, patterns, ..."""
    def __init__(self, title, help1 = '', path1 = '',
                 with_historic1 = 1, with_complete1 = 1, panelpath1 = '',
                 help2 = '', path2 = '',
                 with_historic2 = 1, with_complete2 = 1, panelpath2 = '',
                 active_entry = 0):

        Entry.__init__(self, title, help1, path2, with_historic1,
                 with_complete1, panelpath1, 14)
        w, h = self.w, self.h
        self.entry2 = EntryLineComplete(w-5, h, int((app.maxw - w+4)/2),
                                    int((app.maxh - h)/2) + 3,                                    
                                    path1, 
                                    with_historic2, with_complete2,
                                    panelpath2,
                                    self.clr_ent,
                                    self.clr_w,
                                    2)
        
        self.btn.insert(2,self.entry2)
        self.i = 2
        self.entry.show()


class ListBox(Window):
    """A window to select an item"""   # h, hl - window, list height
    def __init__(self, app, entries, sel_item,
                                      y, x, h = 0, w = 0, frame = True):
        self.app = app
        self.frame = frame
        self.clr_w = clr_w = color.WIND_TXT
        self.clr_bar = color.FOCUS_ITEM

        self.entries = []
        for f in entries:
            self.entries.append(dec_str(f))

        self.x, self.y = x, y
        self.h, self.w  = self.__calculate_hw(h, w)
        self.hl, self.wl = self.h - 2, self.w -2

        Window.__init__(self, app, '','','', clr_w, clr_w, clr_w, clr_w,\
                              0, self.w, self.h, self.x, self.y)
        self.selcursor = Cursor(app, self.x + 1,\
                                            self.x + self.wl, self.y + 1)
        self.entry_i = self.__set_selected_item(sel_item)


    def __set_selected_item(self, item):
        ret =  0
        if len(self.entries):
            try:
                ret = self.entries.index(item)
            except:
                pass
        return ret


    def __calculate_hw(self, h, w):
        """ calculate window height and width
                         based on the number and length of list entries """
        if h == 0:
            h = min(self.app.maxh - self.y - 1, len(self.entries) + 2)
        if w == 0:
            w = min(max(map(len, self.entries)), int(self.app.maxw/2)) + 4
        return h, w


    def fix_limits(self):

        fi, nf, ht =  self.entry_i, len(self.entries), self.hl
        fi = max (min(fi, nf - 1), 0)
        if fi < (nf - ht) or nf <= ht:
            self.lastpage = 0
        elif fi > int(nf/ht)*ht - 1:
            self.lastpage = 1

        if not self.lastpage:
            fa = int(fi/ht)* ht
            fi_pos = fi % (ht)
#            fz = min(fa + ht - 1, nf-1)
        else:
            fa = nf - ht
            fi_pos = ht - (nf - fi)
#            fz = nf - 1
        return fa, fi, fi_pos


    def show(self):
        win = self.pwin.window()
        win.erase()
        if self.frame:
            #win.box(0, 0)
            win.border(curses.ACS_VLINE, curses.ACS_VLINE,
                       curses.ACS_HLINE, curses.ACS_HLINE, 
                       curses.ACS_ULCORNER, curses.ACS_URCORNER,
                       curses.ACS_LLCORNER, curses.ACS_LRCORNER)

        h, w, hl, y, x = self.h, self.w, self.hl, self.y, self.x
        entry_a, self.entry_i, sel = self.fix_limits()

        ScrollBar(win, entry_a, len(self.entries), self.entry_i, 1, hl, w)
        linecursor = ''
        for i in range(hl):
            try:
                line = self.entries[entry_a + i]
            except IndexError:
                line = ''
            if len(line) > w - 3:
                pos = int((w-3)/2)
                line = (line[:pos] + '~' + line[-pos+2:])
            if line:
                line = enc_str(line)
                win.addstr(i+1, 2, line, self.clr_w)

            if  (entry_a + i) == self.entry_i:
                linecursor = ' '+line

        win.noutrefresh()

        self.selcursor.set_attrib(sel, linecursor, self.clr_bar)
        self.selcursor.refresh()
        curses.doupdate()


    def switch_keys(self, ch):
        if ch in [curses.KEY_UP, ord('k'), ord('K')]:
            self.entry_i -= 1
        elif ch in [curses.KEY_DOWN, ord('j'), ord('J')]:
            self.entry_i += 1
        elif ch in [curses.KEY_PPAGE, curses.KEY_BACKSPACE, 0x08, 0x10]:
            self.entry_i -= self.hl
        elif ch in [curses.KEY_NPAGE, ord(' '), 0x0E]:
            self.entry_i += self.hl
        elif ch in [curses.KEY_HOME, 0x16A]:
            self.entry_i = 0
        elif ch in [curses.KEY_END, 0x181]:
            self.entry_i = len(self.entries) - 1
        elif ch in [0x13]:     # Ctrl-S
            theentries = self.entries[self.entry_i:]
            ch2 = self.pwin.window().getkey()
            for e in theentries:
                if e.find(ch2) == 0:
                    break
            else:
                return
            self.entry_i = self.entries.index(e)
        elif ch == curses.KEY_MOUSE:
            ret = self.__process_mouse_event()
            if ret:
                return ret


    def __process_mouse_event(self):
        i,x,y,z,event = curses.getmouse()

        if event == curses.BUTTON2_PRESSED:
            curses.ungetmouse(0,0,0,0,0)
            self.entry_i += self.hl
        elif event == curses.BUTTON4_PRESSED:
            curses.ungetmouse(0,0,0,0,0)
            self.entry_i -= self.hl
        elif event in [curses.BUTTON1_PRESSED, curses.BUTTON3_PRESSED]:
            if  self. y <= y <= self.y + self.h:
                fi, nf, ht =  self.entry_i, len(self.entries), self.hl
                if fi < (nf - ht):
                    self.entry_i =  int(fi/ht)*ht + max (y - self.y - 1, 0)
                else: # lastpage
                    self.entry_i = nf - (ht - max (y - self.y - 1, 0))

                # process double click
                click_tm =  self.app.click_tm
                if time.time() - click_tm < 0.3:
                    return dec_str(self.entries[self.entry_i])
                self.app.click_tm = time.time()


    def manage_keys(self):
        h, w = self.pwin.window().getmaxyx()
        while True:
            self.show()
            ch = self.pwin.window().getch()
            if ch in [0x03, 0x1B, ord('q'), ord('Q')]:       # Ctrl-C, ESC
                return -1
            elif ch in [10, 13]:   # enter
                return dec_str(self.entries[self.entry_i])
            else:
                ret = self.switch_keys(ch)
                if ret:
                    return ret

    def run(self):
        selected = self.manage_keys()
        self.pwin.hide()
        return selected

######################################################################
#class FindfilesWin(ListBoxNew):
class FindfilesWin(Window):
    """A window to select a file"""

    def __init__(self, entries, str_entry_i = ''):

        entr, length = [], 0
        for f in entries: entr.append(dec_str(f))
        if entr:
            length = max(map(len, entr))
        y0 = 1
        w, h = min(max(length,60), int(app.maxw/2)), app.maxh - y0 -1
        x0 = int((app.maxw - w)/2)

        clr_w = color.WIND
        Window.__init__(self, app, '','','', clr_w, clr_w, clr_w, clr_w,\
                              0, w, h, x0, y0)

        self.Listbox = ListBox(app, entries, str_entry_i, y0, x0, h-2, w)
        dx = (w - 53)/7
        self.clr_sel = color.FOCUS_ITEM
        self.clr_def = color.BUTTON
        self.btn = []
        names = ['[< Go >]', '[ Panel ]', '[ View ]', '[ Edit ]', '[ Do ]', '[ Quit ]']
        col = x0+dx/2
        rid = [0, 1, 2, 3, 4, -1]
        for i in range (0, len(names)):
                col += (dx + 1)
                b = Button(names[i], col, self.h-1, rid[i], self.clr_def)
                self.btn.append(b)
                col += b.w
        self.btn_len = len(self.btn)
        self.btn_sel = 0

    def show2(self):

        h,w = self.h, self.w
        win = self.pwin.window()
        win.hline(h - 3, 1, curses.ACS_HLINE, w - 2)
        win.hline(h - 3, 0, curses.ACS_LTEE, 1)
        win.hline(h - 3, w - 1, curses.ACS_RTEE, 1)

        self.Listbox.show()
        for i in range (0,  self.btn_len):
            self.btn[i].refresh(self.clr_def)

        self.btn[self.btn_sel].refresh(self.clr_sel)


    def manage_keys2(self):
        h, w = self.pwin.window().getmaxyx()
        btn, btn_len = self.btn, self.btn_len
        retid = 0
        while True:
            self.show2()
            ch = self.pwin.window().getch()
            if ch in [curses.KEY_RIGHT, ord('\t')]:
                self.btn_sel += 1
                if self.btn_sel >= btn_len:
                    self.btn_sel = 0
            elif ch in [curses.KEY_LEFT]:
                self.btn_sel -= 1
                if self.btn_sel < 0:
                    self.btn_sel = btn_len-1
            elif ch in [10, 13]:   # enter
                retid =  btn[self.btn_sel].rid
                break
            elif ch in [0x03, 0x1B, ord('q'), ord('Q')]:       # Ctrl-C, ESC
                return -1, None
            elif ch in [ord('a'), ord('A')]:
                retid = 1
                break
            elif ch in [curses.KEY_F3, ord('v'), ord('V')]:
                retid = 2
                break
            elif ch in [curses.KEY_F4, ord('e'), ord('E')]:
                retid = 3
                break
            elif ch in [ord('@'), ord('d'), ord('D')]:
                retid = 4
                break
            else:
                self.Listbox.switch_keys(ch)
        try:
            rettext = enc_str( self.Listbox.entries[ self.Listbox.entry_i])
        except:
            rettext = ''
        return retid, rettext

    def run(self):
        selected = self.manage_keys2()
        self.pwin.hide()
        return selected

######################################################################
class MenuWin(Window):
    """A window to select a menu option"""

    def __init__(self, title, entries):

        h = len(entries) + 4
        w=  max(max(map(len, entries)), len(title)) + 6

        clr_w = color.WIND
        clr_t = color.WIND_TTL
        clr_txt = color.WIND_TXT
        self.clr_bar = color.FOCUS_ITEM

        Window.__init__(self, app,title,'','',clr_t, clr_w, clr_w, clr_txt, 0,w,h)
        self.Listbox = ListBox(app, entries, '',
                                    self.y+1, self.x+1, h-2, w-2, False)
        self.entries = entries
        self.keys = [e[0] for e in entries]



    def manage_keys(self):

        while True:
            self.Listbox.show()
            ch = self.pwin.window().getch()
            if ch in [0x03, 0x1B, ord('q'), ord('Q')]:       # Ctrl-C, ESC
                return -1
            elif ch in [10, 13]:   # enter
                return dec_str(self.entries[self.Listbox.entry_i])
            elif 0 <= ch <= 255 and chr(ch).lower() in self.keys:
                return self.entries[self.keys.index(chr(ch).lower())]
            else:
                ret = self.Listbox.switch_keys(ch)
                if ret:
                    return ret

    def run(self):
        selected = self.manage_keys()
        self.pwin.hide()
        return selected

######################################################################
class ChangePerms (Window):
    """A window to change permissions, owner or group"""

    def __init__(self, file, fileinfo, app, i = 0, n = 1):

        h,w = 12, 60
        self.clr_w = clr_w = color.WIND
        self.clr_t = clr_t = color.WIND_TTL
        self.clr_sel = color.FOCUS_ITEM
        self.clr_def = color.BUTTON
        self.clr_lbl = color.WIND
        self.clr_att = color.BUTTON

        Window.__init__(self, app,'','','',clr_t, clr_w, clr_w,clr_w,0,w,h)
        self.app, self.file = app, enc_str(file)
        self.perms_old = files.perms2str(fileinfo[files.FT_PERMS])
        self.perms = ''.join(self.perms_old)
        self.l = l = len('----------')

        self.owner = fileinfo[files.FT_OWNER]
        self.group = fileinfo[files.FT_GROUP]
        self.newowner = self.owner
        self.newgroup = self.group


        #self.owner_old, self.group_old = self.owner[:], self.group[:]
        self.i, self.n = i, n
        self.entry_i = 0
        w, h = self.w, self.h
        pm = self.perms_old

        self.btn, self.stc = [],[]

        owner = self.owner[:l] + '-'*(l-min(len(self.owner),l))
        group = self.group[:l] + '-'*(l-min(len(self.group),l))
        names = [pm[0:3], pm[3:6], pm[6:9], owner, group,\
                   '[ All ]', '[ Ignore ]', '[ <Ok> ]', '[ Cancel ]']
        pids  = [0, 0, 0, 0, 0, 2, -1, 1, -2]
        y = [5, 5, 5, 5, 5, h -2, h -2, h -2, h -2]
        x = [8, 15, 22, 32, 46, 3, 12,  w-21, w - 13]
        for i in range (0, len(pids)):
            if i in [5,6] and self.n == 1:
                continue
            b = Button(names[i], self.x + x[i],  self.y + y[i], pids[i],self.clr_def)
            self.btn.append(b)
            if i < 5:
                s = Button(names[i], self.x + x[i], self.y + y[i]+1,\
                                                 pids[i],self.clr_lbl)
                self.stc.append(s)

        self.btn_len, self.stc_len = len(self.btn), len(self.stc)
        cursor_hide()

    def show(self):
        win = self.pwin.window()
        win.getmaxyx()
        win.erase()
        #win.box(0, 0)
        win.border(curses.ACS_VLINE, curses.ACS_VLINE,
                   curses.ACS_HLINE, curses.ACS_HLINE, 
                   curses.ACS_ULCORNER, curses.ACS_URCORNER,
                   curses.ACS_LLCORNER, curses.ACS_LRCORNER)
        title = 'Change permissions, owner or group'
        win.addstr(0, int((self.w-len(title)-2)/2), ' %s ' % title, self.clr_t)
        win.addstr(2, 2, '\'%s\'' % self.file, self.clr_w)
        if self.n > 1:
            win.addstr(2, self.w-14, '%4d of %-4d' % (self.i, self.n))
        win.addstr(4, 7, 'owner  group  other        owner         group')
        win.addstr(5, 2, 'new: [---]  [---]  [---]     [----------]  [----------]')
        win.addstr(6, 2, 'old: [---]  [---]  [---]     [----------]  [----------]')
        win.refresh()
        #show buttons
        for k in range(0,self.stc_len):
            self.stc[k].refresh(self.clr_w)
        for k in range(0,self.btn_len):
            self.btn[k].refresh(self.clr_att)
        sel_col = self.clr_sel      #selection color
        #if  self.entry_i < 5:
            #sel_col = self.clr_att
        self.btn[self.entry_i].refresh(sel_col)

    def exchange_chars(self, chcur, ch1, ch2):
        if chcur == ch1: return ch2
        else: return ch1

    def manage_keys(self):
        #y, x = self.pwin.window().getbegyx()
        y, x = self.y, self.x
        btn = self.btn
        l = self.l
        pressed_id = 0
        while 1:
            self.show()
            i = self.entry_i
            ch = self.pwin.window().getch()
            if ch in [0x03, 0x1B, ord('c'), ord('C'), ord('q'), ord('Q')]:
                return -1
            elif ch in [ord('\t'), 0x09, curses.KEY_DOWN, curses.KEY_RIGHT]:
                i += 1
                if i >= self.btn_len:
                    i = 0
            elif ch in [curses.KEY_UP, curses.KEY_LEFT]:
                i -= 1
                if i < 0:
                    i = self.btn_len-1
            elif ch in [ord('r'), ord('R')] and i < 3:
                lst = list(btn[i].name)
                lst[0] = self.exchange_chars(btn[i].name[0],'r','-')
                btn[i].name = ''.join(lst)
            elif ch in [ord('w'), ord('W')] and i < 3:
                lst = list(btn[i].name)
                lst[1] = self.exchange_chars(btn[i].name[1],'w','-')
                btn[i].name = ''.join(lst)
            elif ch in [ord('x'), ord('X')] and i < 3:
                lst = list(btn[i].name)
                lst[2] = self.exchange_chars(btn[i].name[2],'x','-')
                btn[i].name = ''.join(lst)
            elif ch in [ord('t'), ord('T')] and i == 2:
                lst = list(btn[i].name)
                lst[2] = self.exchange_chars(btn[i].name[2],'t','-')
                btn[i].name = ''.join(lst)
            elif ch in [ord('s'), ord('S')] and i < 2:
                lst = list(btn[i].name)
                lst[2] = self.exchange_chars(btn[i].name[2],'s','-')
                btn[i].name = ''.join(lst)
            elif ch in [10, 13]:
                if  i == 3:
                    owners = files.get_owners()
                    owners.sort()
                    #ret = ListBox(owners, self.y + 6, self.x + 32, btn[i].name).run()
                    ret= ListBox(app, owners,btn[i].name, self.y + 6, self.x + 32).run()
                    if ret != -1:
                        btn[i].name = ret[:l] + '-'*(l-min(len(ret),l))
                        self.newowner = ret
                    self.app.display()
                elif i == 4:
                    groups = files.get_groups()
                    groups.sort()
                    #ret = ListBox(groups, self.y + 6, self.x + 32, btn[i].name ).run()
                    ret= ListBox(app, groups,btn[i].name, self.y + 6, self.x + 32).run()
                    if ret != -1:
                        btn[i].name = ret[:l] + '-'*(l-min(len(ret),l))
                        self.newgroup= ret
                    self.app.display()
                elif btn[i].rid:
                    pressed_id = btn[i].rid
                    break
            elif ch in [ord('o'),ord('O')]:     #Ok
                pressed_id = 1
                break
            elif ch in [ord('i'), ord('I')] and self.n > 1  : #Ignore
                pressed_id = -1
                break
            elif ch in [ord('a'), ord('A')] and self.n > 1  : #All
                pressed_id = 2
                break
#process mouse
            elif ch == curses.KEY_MOUSE:
                n,x,y,z,event = curses.getmouse()
                j = 0
                if event == curses.BUTTON1_PRESSED:
                    for j in range(0,self.btn_len):
                        if btn[j].check_focus(x,y):
                            self.entry_i = j
                            break
                    continue
                elif event == curses.BUTTON1_RELEASED and  btn[i].rid\
                         and btn[j].check_focus(x,y):
                    pressed_id = btn[i].rid
                    break
            self.entry_i = i

        if pressed_id == -2:                    #Cancel
            return -1
        elif pressed_id == 2:                   #All
            return ''.join([btn[0].name,btn[1].name,btn[2].name]),\
                        self.newowner, self.newgroup, 1
                        #btn[3].name.rstrip('-'), btn[4].name.rstrip('-'), 1
        elif pressed_id == -1:                  #Ignore
            return 0
        elif pressed_id == 1:                   #Ok
            return ''.join([btn[0].name,btn[1].name,btn[2].name]),\
                        self.newowner, self.newgroup, 0
                        #btn[3].name.rstrip('-'), btn[4].name.rstrip('-'), 0

    def run(self):
        selected = self.manage_keys()
        self.pwin.hide()
        return selected




class ViewInfo:

    def __init__(self, buf, center = 1):

        self.buf, self.nlines = buf, len(buf)
        self.y0, self.x0 = 0,  0
        if self.nlines < app.maxh:
            self.y0 = int((app.maxh - self.nlines)/2)
        if center:
            col_max = max(map(len, self.buf))
            self.x0 = int((app.maxw - col_max)/2)

        self.clr =  color.INFO
        try:
            self.win_body = curses.newwin(app.maxh, 0, 0, 0)     # h, w, y, x
        except curses.error:
            print 'Can\'t create windows'
            sys.exit(-1)

        self.win_body.attrset(self.clr)
        self.win_body.bkgdset(self.clr)
        self.win_body.keypad(1)


    def show(self):
        self.win_body.erase()
        for i, s in enumerate(self.buf):
            try:
                self.win_body.addstr(self.y0 + i, self.x0, s, self.clr)
            except:
                continue
        self.win_body.refresh()

    def run(self):
        self.show()
        while not self.win_body.getch():
            pass
