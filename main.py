# -*- coding: iso8859-1 -*-
"""Main.py - Contains the core parts: Main, Pane, Tab, Tree classes """

import os
import time
import curses

import files
import keys
import wwind
import wcall
import color
from __init__ import *


class Main:
    """Main application class"""

    def __init__(self, win, paths, prefs):
        wwind.app =wcall.app= self
        self.win = win              # root window, needed for resizing
        self.prefs = prefs          # preferences
        self.maxh, self.maxw = self.win.getmaxyx()

        self.stdscr = curses.initscr()
        curses.cbreak()
        curses.raw()
        wwind.cursor_hide()

        curses.ACS_BTEE += CURSES_OFFSET 
        curses.ACS_CKBOARD += CURSES_OFFSET 
        curses.ACS_DARROW += CURSES_OFFSET 
        curses.ACS_HLINE += CURSES_OFFSET 
        curses.ACS_LLCORNER += CURSES_OFFSET 
        curses.ACS_LRCORNER += CURSES_OFFSET 
        curses.ACS_LTEE += CURSES_OFFSET 
        curses.ACS_DIAMOND += CURSES_OFFSET
        curses.ACS_RTEE += CURSES_OFFSET 
        curses.ACS_TTEE += CURSES_OFFSET 
        curses.ACS_UARROW += CURSES_OFFSET 
        curses.ACS_ULCORNER += CURSES_OFFSET 
        curses.ACS_URCORNER += CURSES_OFFSET 
        curses.ACS_VLINE += CURSES_OFFSET 

        if self.prefs.options['mouse_support']:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
            curses.mouseinterval(0)
        color.set_colors(self)

        self.statusbar= wwind.StatusBar(self.maxw,self.maxh,color.STATUS_BAR)
        self.tabbar = wwind.Bar(self.maxw, 1, color.NOCLR)
        if self.prefs.options['num_panes'] == 1:
            lmode, rmode = PANE_MODE_FULL, PANE_MODE_HIDDEN
        else:
            lmode, rmode = PANE_MODE_LEFT, PANE_MODE_RIGHT
        self.lpane = Pane(paths[0], lmode, self)
        self.rpane = Pane(paths[1], rmode , self)
        self.act_pane, self.noact_pane = self.lpane,  self.rpane

        self.click_tm = time.time()
        self.cmdruning = False


    def resize(self):
        """resize all gui elements """
        h, w = self.win.getmaxyx()
        self.maxh, self.maxw = h, w
        if w == 0 or h == 2:
            return
        self.win.resize(h, w)
        self.lpane.do_resize(h, w)
        self.rpane.do_resize(h, w)
        self.statusbar.resize(h, w)
        self.tabbar.resize(1,w)
        self.regenerate()
        self.display()        

    def display(self):
        """redraw all gui elements """
        self.tabbar.refresh()
        self.noact_pane.display()
        self.act_pane.display()
        self.statusbar.set_strings(self.act_pane.act_tab.build_status_line())
        self.statusbar.refresh()

    def regenerate(self):
        """rebuild all panels file lists"""
        self.lpane.regenerate()
        self.rpane.regenerate()

    def quit_program(self,icode):
        """save settings and prepare to quit"""
        import utils
        if self.prefs.options['save_conf_at_exit']:
            self.prefs.save()
        for tab in self.lpane.tabs + self.rpane.tabs:
            if tab.Vfs:
                tab.Vfs.exit()  #have to call explicitly to delete tmpdir

        #close avfs mount
        os.system('fusermount -uz %s' %os.path.expanduser('~/.avfs'))
        return utils.insert_backslash(self.act_pane.act_tab.path)

    def run(self):
        """run application"""
        while 1:
            self.display()
            ret = self.act_pane.manage_keys()
            if ret < 0:
                return self.quit_program(ret)



class Pane:
    """The Panel class"""

    def __init__(self, path, mode, app):
        self.app = app
        self.mode = mode
        self.maxh, self.maxw = app.maxh, app.maxw
        self.frame = wwind.PaneFrame(self.app, self.mode,\
                                        color.PANEL_ACT, color.PANEL_INACT,\
                                        color.PANEL_TITLE, color.PANEL_CLMN)
        self.tabs = []
        self.act_tab = Tab(path, self,0)
        self.tabs.append(self.act_tab)
        self.tree = Tree()

    def do_resize(self, h, w):
        """resize pane window"""
        self.maxh, self.maxw = h, w
        self.frame.resize()
        for tab in self.tabs:
            tab.fix_limits()

    def display(self):
        """draw pane window"""
        if self.maxw < 50:
            return
        self.act_tab.fix_limits()
        self.display_files()
        if self.mode not in [ PANE_MODE_TREE_LEFT, PANE_MODE_TREE_RIGHT]:
            self.display_cursorbar()
        self.display_tabs()


    def display_tabs(self):
        """draw tabs"""
        x, w =self.frame.dims[3], self.frame.dims[1]/4-1
        for i, tab in enumerate(self.tabs):
            path = tab.get_tab_caption()
            active_flag = 0
            if tab == self.act_tab:
                active_flag = 1

            tab.win.set_attrib(path,x,w,active_flag)
            tab.win.refresh()
            x += (tab.win.w+1)

    def regenerate(self):
        """rebuild file lists for all tabs"""
        for tab in self.tabs:
            tab.regenerate()
            tab.fix_limits()


    def display_files(self):
        """draw file attributes"""
        tab = self.act_tab
        w = self.frame.dims[1]
        self.frame.erase()
        active = 0
        if self == self.app.act_pane:
            active = 1

        if self.mode in [ PANE_MODE_TREE_LEFT, PANE_MODE_TREE_RIGHT]:
            # treeview data
            t = self.tree
            #reinitilize tree with the new path as the lowest level
            t.path =tab.path
            t.tree = t.get_tree()
            t.pos = t.get_curpos()
            h = self.frame.dims[0] - 3
            n = len(t.tree)
            a, z = int(t.pos/h) * h, (int(t.pos/h) + 1) * h
            if z > n:
                z = n
                a = max(z - h, 0)

            self.frame.active = True
            self.frame.refresh_colors()

            y = 1
            for i in range(a, z):
                y += 1
                clr = color.DIR
                sel = False
                if t.tree[i][2] == t.path and active:
                    sel = True
                    clr = color.FOCUS_ITEM
                self.frame.addtree_element(t, i, y,  clr, sel)
            a, n, i =a, n, t.pos
        else:
            # listview data
            for i in range(tab.file_z - tab.file_a + 1):
                filename = tab.sorted[i + tab.file_a]
                res = files.get_fileinfo_dict(tab.path, filename,\
                                tab.files[filename], self.frame.show_clms)
                attr = tab.get_ftype_clrpair(filename)
                buf = tab.get_fileinfo_str(res)

                self.frame.addline(i, buf,attr)
            a, n, i = tab.file_a, tab.nfiles, tab.file_i

        self.frame.set_attrib(tab.get_title_path(), \
                              tab.get_mountpoint_str(),\
                              self.mode, active, a, n, i)
        self.frame.refresh()



    def display_cursorbar(self, erase = 0):
        """draw cursor bar. two modes: erase and select"""
        if self != self.app.act_pane:
            return

        tab = self.act_tab
#        w = self.frame.dims[1]

        if (erase):
            filename = tab.sorted[tab.file_i_prev]
            attr = tab.get_ftype_clrpair(filename)
            attr2 = color.PANEL_ACT
            file_i_pos = tab.file_i_pos + (tab.file_i_prev - tab.file_i)
        else:
            filename = tab.sorted[tab.file_i]
            if  tab.selections.count(filename):
                attr =  color.FOCUS_SEL_ITEM
            else:
                attr = color.FOCUS_ITEM
            attr2 = attr
            file_i_pos = tab.file_i_pos

        res = files.get_fileinfo_dict(tab.path, filename,\
                                tab.files[filename], self.frame.show_clms)
        buf = tab.get_fileinfo_str(res)

        self.frame.draw_cursor(file_i_pos, buf, attr, attr2)


    def manage_keys(self):
        """process key presses"""
        self.frame.win.nodelay(1)
        while 1:
            ch = self.frame.win.getch()
            if ch == -1:                 # no key pressed
                curses.napms(1)
                curses.doupdate()
                continue
            #print 'key: \'%s\' <=> %c <=> 0x%X <=> %d' % \
                    #(curses.keyname(ch), ch & 255, ch, ch)
            ret = keys.do(self.act_tab, ch)
            if ret == SELECT_UPDATE:
                if self.act_tab.fix_limits() ==1:
                    self.app.display()
                else:
                    self.display_cursorbar(1)   #erase
                    self.display_cursorbar(0)   #draw
                    self.app.statusbar.set_strings(\
                                 self.app.act_pane.act_tab.build_status_line())
                    self.app.statusbar.refresh()
                continue
            if ret != None:
                return ret
            self.app.display()


class Tab:
    """Tab class. Manages tab content."""
    def __init__(self, path, pane, idx):

        self.win = None
        self.path = ''
        self.nfiles = 0
        self.files, self.sorted, self.selected  = [],[],[]

        self.Vfs = None
        self.pane = pane
        self.app = pane.app
        self.idx = idx
        self.init(path)

        self.prev_path = os.sep
        self.prev_mntpoint = os.sep
        self.mntpoint_info = ''

    def __del__(self):
        if self.Vfs:
            del self.Vfs
            self.Vfs = None


    def init(self, path, prev_file = ''):
        """create or reinitilize tab"""
        if self.Vfs:
            prev_file, vbase = self.Vfs.check_exit(path)
            #vbase = self.Vfs.check_exit(path)
            if vbase:
                path = vbase
                self.Vfs = None

        if os.path.basename(path) == os.pardir: # move to ..
            prev_file = os.path.basename(os.path.dirname(path).rstrip(os.sep))


        if  self.init_dir(path, self.pane.app):

            self.file_i, self.file_i_prev, self.file_i_pos  = 0, 0, 0
            self.lastpage = 0
            if prev_file:
                try:
                    self.file_i = self.sorted.index(prev_file)
                except ValueError:
                    self.file_i = 0

            self.fix_limits()
            if not self.win:
                self.win = wwind.TabButton(0,self.pane.frame.dims[1],\
                             color.FOCUS_TAB, color.TAB)


    def init_dir(self, path, application = None):
        """build file list for the given path"""
        app = self.pane.app
        self.sort_mode = app.prefs.options['sort']
        sort_mix_dirs = app.prefs.options['sort_mix_dirs']
        sort_mix_cases = app.prefs.options['sort_mix_cases']
        show_dotfiles = app.prefs.options['show_dotfiles']
        try:
            self.nfiles, self.files = files.get_dir(path, show_dotfiles)
            self.sorted = files.sort_dir(self.files, self.sort_mode,\
                                         sort_mix_dirs, sort_mix_cases)
            self.path = os.path.abspath(path)
            self.selections = []
        except (IOError, OSError), (errno, strerror):
            wcall.err_enter_directory( '%s (%d)' %(strerror, errno), path)
            return False

        return True

    def regenerate(self):
        """Rebuild tabs' directories"""
        path = self.path
        while not os.path.exists(path):
            path = os.path.dirname(path)
        self.path = path
        self.init_dir(self.path)


    def refresh(self):
        """"""
        self.pane.app.regenerate()
        self.fix_limits()


    def get_selected_files_size(self):
        lsel = len(self.selections)
        if lsel:
            size = 0
            for f in  self.selections:
                size += self.files[f][files.FT_SIZE]
            return size, lsel
        return -1, lsel


    def filesize_to_str(self,num):
        num_list = []
        while num / 1000.0 >= 0.001:
            num_list.append('%.3d' % (num % 1000))
            num /= 1000.0
        else:
            num_str = '0'
        if len(num_list) != 0:
            num_list.reverse()
            num_str = ','.join(num_list)
            while num_str[0] == '0':
                num_str = num_str[1:]
        return num_str


    def build_status_line(self):
        s1 = s2 = s3 = ''
        if self.app.maxw >= 80:
            size, num = self.get_selected_files_size()
            if size != -1:
                s1 = '   %s bytes in %d files' % (self.filesize_to_str(size), num)
            else:
                s1 = 'File: %4d of %-4d' %(self.file_i + 1, self.nfiles)
                filename = self.sorted[self.file_i]


                #curses.endwin()
                #print filename

                res = files.get_fileinfo_dict(self.path, filename,\
                                 self.files[filename],\
                                #['size', 'mtime', 'perms', 'owner', 'group'])
                                [SIZE, MTIME, PERMS, OWNER, GROUP])

                s2 = ''.join([filename,' (', res[SIZE],', ',\
                                res[MTIME], ', ', res[PERMS], ', ',\
                                res[OWNER], ', ', res[GROUP],  ')'])

                s2=enc_str(s2)



        if self.app.maxw > 20:
            s3 = 'F2;F9=Menu'
        return s1, s2, s3


    def get_tab_caption(self):
        if self.win.w < 8:
            name = str(self.idx+1)
        else:
            if self.Vfs:
                name = self.Vfs.vfs_name()
            else:
                name = os.path.basename(self.path)
                if name == '':
                    name = os.path.dirname(self.path)
        return name

    def get_mountpoint_str(self):

        if self.app.prefs.options['show_mountpoint_info']:
            if self.Vfs:
                path = self.Vfs.vfs_name()
            else:
                path = self.path

            cur_mntpoint = files.mountpoint(path)
            if self.prev_mntpoint != cur_mntpoint:
               self.prev_mntpoint = cur_mntpoint
               self.mntpoint_info = files.get_mntpoint_data(cur_mntpoint)

        return self.mntpoint_info


    def get_title_path(self):
        w = self.pane.frame.dims[1]

        if self.Vfs:
            path = self.Vfs.vfs_path(self.path)
        else:
            path = self.path

        path = dec_str(path)
        if len(path) > w :
            title_path = '~' + path[-w+5:]
        else:
            title_path = path

        title_path = enc_str(title_path)
        return title_path



    def get_fileinfo_str(self, res):

        clms, show_clms = self.pane.frame.clms, self.pane.frame.show_clms
        try:
            fwidth = clms[NAME][1]
            f = ''.join([res[TYPE], res[NAME]])
            f = dec_str(f)
            if show_clms[0] != NAME:
                f = ''.join([' ',f])
            if len(f) > fwidth:
                h1 = int(fwidth/2)
                h2 = fwidth - h1
                f = ''.join([f[:h1],'~',f[-h2+1:]])
            f = f.ljust(fwidth)
            f = enc_str(f)
        except:
            pass

        buf =''
        for c in show_clms:
            try:
                if c == NAME:
                    buf = '%s%s'% (buf,f)
                elif c in [GROUP, OWNER]:
                    buf ='%s %s'% (buf, res[c].rjust(clms[c][1]-1)[:clms[c][1]-1])
                else:
                    buf ='%s%s'% (buf, res[c].rjust(clms[c][1]))
            except:
                continue
        return buf


    def get_ftype_clrpair(self,fname):

        if not self.selections.count(fname):
            prefs = self.app.prefs
            if prefs.options['color_files']:

                ftype = self.files[fname][files.FT_TYPE]
                if ftype == files.FTYPE_DIR:
                    return color.DIR
                elif ftype == files.FTYPE_EXE and not prefs.options['cygwin']:
                    return color.EXE_FLS
                ext = os.path.splitext(fname)[1].lower()
                if ext in prefs.files_ext['temp_files']:
                    return color.TMP_FLS
                elif ext in prefs.files_ext['document_files']:
                    return color.DOC_FLS
                elif ext in prefs.files_ext['media_files']:
                    return color.MED_FLS
                elif ext in prefs.files_ext['archive_files']:
                    return color.ARC_FLS
                elif ext in prefs.files_ext['source_files']:
                    return color.SRC_FLS
                elif ext in prefs.files_ext['graphics_files']:
                    return color.GRA_FLS
                elif ext in prefs.files_ext['data_files']:
                    return color.DAT_FLS
                elif prefs.options['cygwin'] and ext in prefs.files_ext['cygwin_exe_files']:
                    return color.EXE_FLS
                else:
                    return color.REG_FLS
            else:
                return color.NOCLR
        else:
            return color.SEL_FLS


    def fix_limits(self):

        dh = 3      # indent from top
        fi, nf =  self.file_i, self.nfiles
        ht = max(self.pane.frame.dims[0] - dh, 1)
        last_page = self.lastpage

        fi = max (min(fi, nf - 1), 0)
        if fi < (nf - ht) or nf <= ht:
            self.lastpage = 0
        elif fi > int(nf/ht)*ht - 1:
            self.lastpage = 1

        if not self.lastpage:
            fa = int(fi/ht)* ht
            fz = min(fa + ht - 1, nf-1)
            fi_pos = fi % (ht) + dh
        else:
            fz = nf - 1
            fa = nf - ht
            fi_pos = ht - (nf - fi) + dh

        self.file_i, self.file_a, self.file_z, self.nfiles, self.file_i_pos =\
                                                        fi, fa, fz, nf, fi_pos

        if last_page != self.lastpage or fi in [fa, fz]:
            return True     # redraw pane if page is changed or the boundaries
        return False        # do not activate pane redraw


######################################################################
##### Tree
class Tree:
    def __init__(self, path = os.sep):
        if not os.path.exists(path):
            return None

        if path[-1] == os.sep and path != os.sep:
            path = path[:-1]

        self.path = path
        self.tree = self.get_tree()
        self.pos = self.get_curpos()

    def get_dirs(self, path):
        """return a list of dirs in path"""
        ds = []
        try:
            for d in os.listdir(path):
                if os.path.isdir(os.path.join(path, d)):
                    ds.append(d)
        except OSError:
            pass
        ds.sort()
        return ds

    def __get_graph(self, path):
        """return 2 dicts with tree structure"""
        tree_n = {}
        tree_dir = {}
        expanded = None
        while path:
            if path == os.sep and tree_dir.has_key(os.sep):
                break
            tree_dir[path] = (self.get_dirs(path), expanded)
            expanded = os.path.basename(path)
            path = os.path.dirname(path)
        dir_keys = tree_dir.keys()
        dir_keys.sort()
        n = 0
        for d in dir_keys:
            tree_n[n] = d
            n += 1
        return tree_n, tree_dir

    def __get_node(self, i, tn, td, base):
        """expand branch"""
        lst2 = []
        node = tn[i]
        dirs, expanded_node = td[node]
        if not expanded_node:
            return []
        for d in dirs:
            if d == expanded_node:
                lst2.append([d, i, os.path.join(base, d)])
                lst3 = self.__get_node(i+1, tn, td, os.path.join(base, d))
                if lst3 != None:
                    lst2.extend(lst3)
            else:
                lst2.append([d, i, os.path.join(base, d)])
        return lst2

    def get_tree(self):
        """return list with tree structure"""
        tn, td = self.__get_graph(self.path)
        tree = [[os.sep, -1, os.sep]]
        tree.extend(self.__get_node(0, tn, td, os.sep))
        return tree

    def get_curpos(self):
        """get position of current dir"""
        for i in range(len(self.tree)):
            if self.path == self.tree[i][2]:
                return i
        else:
            return -1

    def regenerate_tree(self, newpos):
        """regenerate tree when changing to a new directory"""
        self.path = self.tree[newpos][2]
        self.tree = self.get_tree()
        self.pos = self.get_curpos()
