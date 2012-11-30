# -*- coding: iso8859-1 -*-

"""config.py"""

import os
#import os.path
from ConfigParser import SafeConfigParser

#from __init__ import PROG_NAME
from __init__ import * 
from files import SORT_Name
from utils import get_shell_output


######################################################################
##### Some variables and default values
CONFIG_FILE = '.tc'

options = { 'save_conf_at_exit': 1,
            #'show_output_after_exec': 1,
            'rebuild_vfs': 0,
            'detach_terminal_at_exec': 1,
            'show_dotfiles': 1,
            'num_panes': 2,
            'sort': SORT_Name,
            'sort_mix_dirs': 0,
            'sort_mix_cases': 0,
            'color_files': 1,
            'mouse_support':1,
            'show_mountpoint_info':1,
            'archive_size_show_gui':3000,
            'cygwin': 0}

confirmations = { 'delete': 1,
                  'overwrite': 1,
                  'quit': 0,
                  'ask_rebuild_vfs': 1 }


column_names =  [
                [ NAME, PERMS, PERMSNUM, OWNER, GROUP, SIZE, SIZEHUMN, MTIME_LONG, MTIME,
                  MTIME_MC, CTIME_LONG, CTIME, CTIME_MC, ATIME_LONG, ATIME, ATIME_MC],
                [ 'name', 'perms', 'permsnum', 'owner', 'group', 'size', 'sizehumn', 'mtime_long', 'mtime',
                  'mtime_mc', 'ctime_long', 'ctime', 'ctime_mc', 'atime_long','atime', 'atime_mc']
               ]
 
panels = {'left_columns'    :(NAME, SIZE, MTIME, PERMS),
          'right_columns'   :(NAME, SIZEHUMN, MTIME_MC, PERMSNUM),
          'fullpane_columns':(PERMS, OWNER, GROUP, SIZE, MTIME_LONG, NAME)
         }

colors = {
           'info':('yellow', 'black','light'),
           'window':('red', 'black','light'),
           'window_title':('white', 'red','light'),
           'window_text':('red', 'black','normal'),
           'button':('green', 'black','normal'),
           'entry_line':('white', 'black','normal'),
           'err_title':('yellow', 'red','light'),
           'err_window':('white', 'red','light'),
           'progress_none': ('white', 'red','light'),
           'progress_full': ('blue', 'blue','light'),
           'tab': ('green', 'black','normal'),
           'focused_tab': ('white', 'cyan','light'),
           'focused_item': ('white', 'cyan','light'),
           'focused_sel_item': ('yellow', 'cyan','light'),
           'status_bar': ('yellow', 'black','normal'),
           'command_line': ('white', 'black','light'),
           'command_line_title': ('red', 'black','light'),
           'panel_active': ('green', 'black','normal'),
           'panel_inactive': ('white', 'black','normal'),
           'panel_title': ('red', 'black','light'),
           'panel_columns': ('white', 'black','light'),
           'nocolor': ('white', 'black','normal'),
           'regular_files': ('white', 'black','light'),
           'selected_files': ('yellow', 'black','light'),
           'directory': ('green', 'black','normal'),
           'exe_files': ('red', 'black','light'),
           'temp_files':( 'white', 'black','normal'),
           'document_files':('blue', 'black','normal'),
           'media_files': ('blue', 'black','light'),
           'archive_files':('yellow', 'black','normal'),
           'source_files':('cyan', 'black','normal'),
           'graphics_files': ('magenta', 'black','light'),
           'data_files':('magenta', 'black','normal')}

files_ext  = {'temp_files':('.tmp','.$$$','~','.bak'),
              'document_files':( '.txt','.doc','.rtf','.diz','.ctl','.me',\
                                '.ps','.pdf','.dvi','.xml','.xsd','.xslt',\
                                '.dtd','.html','.shtml','.htm','.mail',\
                                '.msg','.lsm','.po','.man','.bib','.tex',\
                                '.sgml','.css','.text','.letter','.odt',\
                                '.sxw'),
              'media_files'   :('.mp2','.mp3','.mpg','.ogg','.mpeg','.wav',\
                                '.avi','.asf','.mov','.mol','.mpl','.xm',\
                                '.med','.mid','.midi','.umx', '.wma','.acc',\
                                '.wmv','.swf','.mp4', '.flv'),
              'archive_files' :('.gz','.bz2','.tar','.tgz','.rpm','.deb',\
                                '.Z','.rar','.zip','.arj','.cab','.lzh',\
                                '.lha','.zoo','.arc','.ark', '.ace'),
              'source_files'  :('.f','.f90','.pov','.m','.c','.h','.cc',\
                                '.hh','.cpp','.hpp','.asm','.py','.pl',\
                                '.pm','.inc','.cgi','.php','.phps','.js',\
                                '.java','.jav','.jasm','.sh','.bash','.diff',\
                                '.patch','.pas','.tcl','.tk','.awk','.m4',\
                                '.st','.mak','.sl','.ada','.caml','.ml',\
                                '.mli','.mly','.mll','.mlp','.prg'),
              'graphics_files':('.jpg','.jpeg','.gif','.png','.tif','.tiff',\
                                '.pcx','.bmp', '.ppm', '.pbm',\
                                '.xpm','.xbm','.eps','.pic',\
                                '.rle','.ico','.wmf','.omf','.ai','.cdr'),
              'data_files'    :('.dta','.nc','.dbf','.mdn','.db','.mdb',\
                                '.dat','.fox','.dbx','.mdx','.sql','.mssql',\
                                '.msql','.ssql','.pgsql','.xls','.cdx','.dbi'),
             'cygwin_exe_files':('.exe','.bat','.com')
                                }

defaultprogs = { 'shell': 'bash',
                 'pager': 'vimpager',
                 'editor': 'vim',
                 'web': 'firefox',
                 'ogg': 'ogg123',
                 'mp3': 'mpg321',
                 'audio': 'esdplay',
                 'video': 'mplayer',
                 'graphics': 'kuickshow',
                 'pdf': 'acroread',
                 'ps': 'gv',
                 'doc': 'oowriter' }

filetypes = { 'web': ('html', 'htm','shtml','php'),
              'ogg': ('ogg', ),
              'mp3': ('mp3', ),
              'audio': ('wav', 'au', 'midi'),
              'video': ('mpeg', 'mpg', 'avi', 'asf','mov','wmv', 'mp4', 'flv'),
              'graphics': ('png', 'jpeg', 'jpg', 'gif', 'tiff', 'tif', 'xpm', 'svg',\
                           'ppm', 'pbm', 'pxm', 'pnm',  'bmp'),
              'pdf': ('pdf', ),
              'ps': ('ps','eps'),
              'doc': ('txt','doc','rtf','odt','sxw')}

bookmarks = [ '/',
              '/home',
              '/home',
              '/home',
              '/usr',
              '/opt',
              '/',
              '/etc',
              '/usr',
              '/root' ]

               

######################################################################
##### Configuration
class Config:
    """Config class"""

    def __init__(self):
        self.file = os.path.abspath(os.path.expanduser(os.path.join('~', CONFIG_FILE)))
        self.file_start = '#' * 10 + ' ' + PROG_NAME + ' ' + \
                          'Configuration File' + ' ' + '#' * 10
        self.progs = {} # make a copy
        for k,v in defaultprogs.items():
            self.progs[k] = v


        self.filetypes      = filetypes
        self.bookmarks      = bookmarks[:]
        self.colors         = colors
        self.options        = options
        self.confirmations  = confirmations
        self.files_ext      = files_ext
        self.panels         = panels


    def check_progs(self):
        for k, v in defaultprogs.items():
            r = get_shell_output('which \"%s\"' %v)
            if r:
                self.progs[k] = v
            else:
                self.progs[k] = ''


    def load(self):
        # check config file
        if not os.path.exists(self.file) or not os.path.isfile(self.file):
            return -1
        f = open(self.file)
        title = f.readline()[:-1]
        f.close()
        if title and title != self.file_start:
            return -2
        # all ok, proceed
        cfg = SafeConfigParser()
        cfg.read(self.file)
        # programs
        for type, prog in cfg.items('Programs'):
            self.progs[type] = prog
        # file types
        for type, exts in cfg.items('File Types'):
            lst = [t.strip() for t in exts.split(',')]
            self.filetypes[type] = tuple(lst)

        # bookmarks
        self.bookmarks[:] = bookmarks[:]
        for num, path in cfg.items('Bookmarks'):
            try:
                num = int(num)
            except ValueError:
                print 'Bad bookmark number:', num
                continue
            if 0 <= num <= 9:
                self.bookmarks[num] = path
            else:
                self.bookmarks.append(path)

        # colors
        for sec, color in cfg.items('Colors'):
            if not self.colors.has_key(sec):
                print 'Bad object name:', sec
            else:
                (fg, bg, hl) = color.split(' ', 3)
                self.colors[sec.lower()] = (fg.lower(), bg.lower(), hl.lower())
        # options
        for what, val in cfg.items('Options'):
            try:
                val = int(val)
            except ValueError:
                print 'Bad option value: %s => %s' % (what, val)
            else:
                if what not in self.options.keys():
                    print 'Bad option: %s => %s' % (what, val)
                else:
                    self.options[what] = val
        if self.options['num_panes'] != 1 and self.options['num_panes'] != 2:
            self.options['num_panes'] = 2
        # confirmations
        for what, val in cfg.items('Confirmations'):
            try:
                val = int(val)
            except ValueError:
                print 'Bad confirmation value: %s => %s' % (what, val)
            else:
                if what not in self.confirmations.keys():
                    print 'Bad confirmation option: %s => %s' % (what, val)
                elif val != 0 and val != 1:
                    print 'Bad confirmation value: %s => %s' % (what, val)
                else:
                    self.confirmations[what] = val

        # File types for color
        for type, exts in cfg.items('Files'):
            lst = [t.strip() for t in exts.split(',')]
            self.files_ext[type] = tuple(lst)

        # Panels columns
        for pane, columns  in cfg.items('Columns'):
            lst = [t.strip() for t in columns.split('|')]
            self.panels[pane] = tuple(lst)
        
            lst2=[]
            for name in lst:
                try:
                    index = column_names[1].index(name)
                    lst2.append(column_names[0][index])
                except ValueError:
                    print 'Column name %s is undefined' % name
            self.panels[pane] = tuple(lst2)


    def save(self):
        # title
        buf = self.file_start + '\n'

        # options
        buf += '\n[Options]\n'
        buf += '# Sort types: None = 0, Name = 1, Name_rev = 2, Ext = 3, Ext_rev = 4, Size = 5, Size_rev = 6, Mtime = 7, Mtime_rev = 8\n'
        #buf += '# \t \n'
        for k, v in self.options.items():
            buf += '%s: %s\n' % (k, v)

        # confirmations
        buf += '\n[Confirmations]\n'
        for k, v in self.confirmations.items():
            buf += '%s: %s\n' % (k, v)

        # panels
        buf += '\n[Columns]\n'
        buf += '# Possible columns: name, size, sizehumn, mtime, mtime_mc, mtime_long, ctime, ctime_mc,\
                ctime_long, atime, atime_mc, atime_long, perms, permsnum, owner, group\n'
        for k, vs in self.panels.items():
            vs2 = []
            for i in vs: 
                try:
                    index = column_names[0].index(i)
                    vs2.append(column_names[1][index])
                except:
                    print 'Failed to convert column IDs to names'
            buf += '%s: %s\n' % (k, '|'.join(vs2))

        # colors
        buf += '\n[Colors]\n'
        for k, v in self.colors.items():
            buf += '%s: %s %s %s\n' % (k, v[0], v[1], v[2])

        # file types for color
        buf += '\n[Files]\n'
        for k, vs in self.files_ext.items():
            buf += '%s: %s\n' % (k, ', '.join(vs))

        # default progs
        buf += '\n[Programs]\n'
        for k, v in self.progs.items():
            buf += '%s: %s\n' % (k, v)

        # filetypes
        buf += '\n[File Types]\n'
        for k, vs in self.filetypes.items():
            buf += '%s: %s\n' % (k, ', '.join(vs))

        # bookmarks
        buf += '\n[Bookmarks]\n'
        for i, b in enumerate(self.bookmarks):
            buf += '%d: %s\n' % (i, b)

        # write to file
        f = open(self.file, 'w')
        f.write(buf)
        f.close()
######################################################################
