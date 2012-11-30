import sys
import os.path
import curses
import files
import wwind
import socket
import keys
import color
from __init__ import *
from utils import *

historic_commands = []


######################################################################
class EntryCommandLine(wwind.EntryLineComplete):

    def __init__(self,app, w, h, x, y, w_historic, w_complete, panelpath):

        self.app =app
        self.clr = color.CMDLINE
        wwind.EntryLineComplete.__init__(self, w, h, x, y,'',\
                                     w_historic, w_complete, panelpath,\
                                     self.clr
                                     )
        if w_historic:
            self.historic = historic_commands[:]
            self.historic_i = len(self.historic)

    def fm_navigation(self, ch, tab, app):
        if ch in [curses.KEY_UP, 0x208]:         #Up
            keys.cursor_up(tab)
        elif ch in [curses.KEY_DOWN, 0x201]:     #Down
            keys.cursor_down(tab)
        elif ch in [0x203] or (ch in [curses.KEY_LEFT] and self.text ==''):
            keys.cursor_left(tab)             #Ctrl+Left or Left if empty
        elif ch in [0x205] or (ch in [curses.KEY_RIGHT] and self.text ==''):
            keys.cursor_right(tab)            #Ctrl+Right or Right if empty
        elif ch in [curses.KEY_PPAGE]:           #PageUp
            keys.page_previous(tab)
        elif ch in [curses.KEY_NPAGE]:           #PageDown
            keys.page_next(tab)
        elif ch in [curses.KEY_IC]:              #Insert
            keys.select_item(tab)
        elif ch in [curses.KEY_F10]:             #F10
            app.quit_program(-2)
            sys.exit()
        elif ch in [0x0F]:                       #Ctrl-O
            keys.open_shell(tab)
        elif ch in [ord('\t')]:                  #Tab
            keys.toggle_active_pane(tab)
        else:
            return 0
        return 1


    def manage_keys(self):
        app = self.app
        tab = app.act_pane.act_tab
        while 1:
            self.show()
            #print 'key: \'%s\' <=> %c <=> 0x%X <=> %d' % \
                    #(curses.keyname(ch), ch & 255, ch, ch)
            ch  = self.entry.getch()

            if self.fm_navigation(ch, tab, app):
                return
            #Alt+ or Esc+ key
            ###################################################################
            if self.ch_prev in [0x1B]:
                self.ch_prev = ''
                if ch in [0xA]:          #Alt + enter
                    sl, sr = self.text[0: self.pos], self.text[self.pos:self.len_text]
                    sel =''
                    if tab.selections:
                        for f in tab.selections:
                            sel += (insert_backslash(f) + ' ')
                        tab.selections = []
                        sel = sel.rstrip()
                    else:
                        sel = insert_backslash(tab.sorted[tab.file_i])
                    sel = dec_str(sel)
                    self.pos += len(sel)
                    self.text ="".join([sl,sel,sr])
                elif ch in [ord('a'), ord('A')]:        #Alt + a
                    path = tab.get_title_path()
                    sl, sr = self.text[0: self.pos], self.text[self.pos:self.len_text]
                    self.pos += len(path)
                    self.text ="".join([sl,path,sr])
                elif ch in [ord('p'), ord('P')]:     #Alt + p
                    if self.w_historic:
                        if self.historic_i > 0:
                            if self.historic_i == len(self.historic):
                                self.historic.append('')
                            self.historic_i -= 1
                            self.text = self.historic[self.historic_i]
                            self.pos = len(self.text)
                elif ch in [ord('n'), ord('N')]:            #Alt + n
                    if self.w_historic:
                        if self.historic_i < len(self.historic) - 1:
                            self.historic_i += 1
                            self.text = self.historic[self.historic_i]
                            self.pos = len(self.text)
                elif ch in [ord('c'), ord('C'), 0x1B]:    #Alt + c,  Alt + ESC
                    return 0x03
                continue
            elif ch in [0x1B]:      #Esc or Alt
                self.ch_prev = ch
                continue
            elif ch == curses.KEY_RESIZE:
                return ch


            ###################################################################
            ret =  self.standard_input(ch)
            if ret:
                return ret

class CommandEntry:
    def __init__(self,app, with_historic=1, with_complete=1, panelpath=''):

        self.app = app            
#        self.title = os.getlogin() +'@'+socket.gethostname() +  '>'
#        self.title = os.popen("whoami").read().split()[0] +'@'+socket.gethostname() +  ' $ '
        self.title = os.popen("whoami").read().split()[0] \
        +'@'+socket.gethostname() +' ../'+(os.path.basename(app.act_pane.act_tab.path) or '/')+' $'
        try:
            self.label = curses.newwin(1, len(self.title)+1 ,(app.maxh-1),0)
            self.entry = EntryCommandLine(app,max(app.maxw-len(self.title),0), 1,
                                   len(self.title),app.maxh-1,
                                   with_historic, with_complete, panelpath)
        except curses.error:
            print 'Can\'t start command line'
            sys.exit(-1)


        self.label.attrset(color.CMDLINE_TTL)
        self.label.bkgdset(color.CMDLINE_TTL)
        self.label.addstr('%s' % self.title)
        self.label.refresh()
        self.with_historic = with_historic

    def show_title(self):
        self.label.erase()
        self.label.addstr(self.title)
        self.label.refresh()

    def update_history(self):
        if self.with_historic:
            if self.entry.text not in [None,'','*']:
                historic_commands.append(self.entry.text)

    def run(self):
        self.entry.show()
        wwind.cursor_show()
        while 1:
            #self.label.refresh()
            self.app.act_pane.display()
            self.app.noact_pane.display()
            ans = self.entry.manage_keys()
            if ans == 0x03:              # Ctrl-C
                return
            elif ans == 10:              # return values
                self.update_history()
                break
            elif ans in [curses.KEY_MOUSE]:
                keys.mouse_event(self.app.act_pane.act_tab)
                wwind.cursor_show()
            elif ans == curses.KEY_RESIZE:
                self.app.resize()
                break

        wwind.cursor_hide()
        #return self.entry.text.encode(g_encoding) #, self.entry.pos
        return enc_str(self.entry.text)
