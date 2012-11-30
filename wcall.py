# -*- coding: iso8859-1 -*-

"""wcall.py"""

from wwind import *
import foper
import color
app = None
######################################################################

# Error dialogs
def __error(title, msg = '', file = ''):
    """show an error window"""
    if file == '':
        buf = msg
    else:
        buf = '%s: %s' % (file, msg)
    Window(app,title, buf,' Press any key ',
                 color.ERR_TTL,
                 color.ERR_WIND,
                 color.ERR_WIND,
                 color.ERR_WIND,
                 ).run()

def err_create_tabs():
    __error('New tab', 'Can\'t create more tabs')

def err_last_tab():
    __error('Close tab', 'Can\'t close last tab')

def err_init_pane():
    __error('Initialize Panes Error','Incorrect pane ID')

def err_makedir(error):
    __error('Make directory', error)

def err_emptylink():
    __error('Edit link', 'Empty link name field')

def err_emptyfilename():
    __error('Edit link', 'Empty file name field')

def err_editlink(error):
    __error('Edit link', error)

def err_chmod(error):
    __error('Chmod', error)

def err_chown(error):
    __error('Chown', error)

def err_runprog():    
    return confirm('No associated program', 'Open file with a viewer(F3) ?')
#    , yes=1, all=0, no=1, none=0, abort=0, default = 0, h = 6):
#    
#    __error('Open file error',\
#                'No associated program, defaulting to view')

def err_filesyst(error):
    __error('Show filesystems info', error)

def err_search(title):
    __error(title,'No files found',)

def err_view(file):
    __error('View/Edit', 'Can\'t open target', file)

def err_parent(action, result):
    __error(action, 'Parent: Error: ' + result)

def err_parent_transport(action, result):
    __error(action, 'Parent: Internal Transport Error: ' + result)

def err_run_func(action):
    __error(action, 'Can\'t run function')

def err_general(action, result):
    __error(action, result)

def err_create_vfs(error):
    __error('Creating archive VFS', error)

def err_regenerate_vfs(error):
    __error('Error regbuilding archive file',error)

def err_enter_directory(error, path):
    __error('Enter directory', error, path)


def err_undefined_column():
    __error('Columns initialization', 'Column name error')


def err_unsuported_protocol():
    __error('VFS connection', 'Unsupported protocol')


# Messages
def win(title, text):
    """show a message window and wait for a key"""
    Window(app, title, text,' Press any key ',
                 color.WIND_TTL, color.WIND,
                 color.WIND, color.WIND_TXT).run()


def msg_default_settings():
    win('Default settings', 'Reset to default configuration succeeded')



#Dialogs
def win_nokey(app, title, text):
    return Window(app, title, text,  ' Press Esc to stop ',
                        color.WIND_TTL, color.WIND,
                        color.WIND, color.WIND_TXT,
                        0, app.maxw - 20, 5)

def win_progress():
    return ProgressBarWindow(7, app.maxw-20, '', '', '', 0,
            color.WIND_TTL, color.WIND,
            color.PROGR_FULL, color.PROGR_NONE,
            waitkey = 0)

def win_progress_double():
    return ProgressBarWindow( 7, app.maxw-20, '', '', '', 0,
            color.WIND_TTL, color.WIND,
            color.PROGR_FULL, color.PROGR_NONE,
            0, 2)


def win_progress_move_copy():
    return ProgressBarWindow(9, app.maxw-20, '', '', '', 0,
            color.WIND_TTL, color.WIND,
            color.PROGR_FULL, color.PROGR_NONE,
            0, 2, True )

def win_search_list(entries, entry):
    return FindfilesWin(entries, entry).run()

def win_searching(app, path, fs, pat):
    search = foper.SearchFunc(app, path, fs, pat)
    search.run()    
    st, m = search.get_result()
    if st < 0: # error
        if st == -100: # stopped by user
            return -1,-1
        else: # some other error
            app.display()
            wcall.err_general('Find/Grep', m)
            return -1,-1

    return st, m


def win_chmod_chown(file, fileinfo, app, i, n ):
    return ChangePerms(file, fileinfo, app, i, n).run()

def  win_info_file(file, text):
    ViewInfo(text).run()

def win_info_fsystem(text):
    ViewInfo(text).run()

def win_dash():
    return RotatingDash(app, color.TAB)

# Return key presses dialogs
def get_bookmark_key():
    return BookmarkWindow('Set bookmark',\
     'Press 0-9 to associate bookmark or \'A\' to append',\
     ' Press Esc to cancel ').run()

def get_sort_key():
    return BookmarkWindow('Sorting mode',
                'file(n)ame, (e)xtension, (s)ize, (m)time, (u)nsort\n    uppercase - reverse order',
                ' Press Esc to cancel ').run()



# Confirmations
def confirm(title, question, yes=1, all=0, no=1, none=0, abort=0, default = 0, h = 6):
    """show a yes/all/no/none/stop window, returning 1/2/0/-2/-1"""
    return ConfirmWindow(title, question, [yes, all, no, none, abort], default, h).run()


def cfm_stop(text):
    return confirm('Stop process',text)

def cfm_delete(text,default):
    return confirm('Delete', text, 1,1,1,1,0, default)

#def cfm_overwrite(action, result, default):
def cfm_overwrite(action, file,  mtime_src, size_src, mtime_dest, size_dest, default):

    source = 'Source date: '+ mtime_src+', size: '+ str(size_src)
    dest = 'Target date: '+ mtime_dest+', size: '+ str(size_dest)
    text =  'Overwrite file: '+ file + ' ?\n\n'
    text += source+'\n'
    text += dest

    return confirm(action, text, 1,1,1,1,1, default, 9)
    #return confirm(action, 'Overwrite %s' % result, 1,1,1,1,1, default, 8)

def cfm_quit():

    return confirm('Twilight Commander', 'Quit Twilight Commander')

def cfm_rebuild_vfs():
    return confirm('Rebuild archive file', 'Rebuild archive file')


# Entry Dialogs
def __doEntry(tabpath,title, help,path = '', h = 9):
    path = Entry(title, help, path, 1, 1, tabpath, h).run()
    return path[0]


def entry_select(path):
    return __doEntry(path, 'Select group', 'Enter pattern', '*')

def entry_deselect(path):
    return __doEntry(path, 'Deselect group', 'Enter pattern', '*')


def entry_destination(path, func, lst, destdir):
    if func == 'move':
        t1 = 'Move'
    elif func == 'copy':
        t1 = 'Copy'
    elif func == 'rename':
        t1 = 'Rename/Move'
    elif func == 'backup':
        t1 = 'Backup/Copy'
    else:
        t1 = 'Error'

    if len(lst) > 1:
        buf = '%s %d items to' % (t1, len(lst))
    else:
        buf = '%s \'%s\' to' % (t1, lst[0])

    return __doEntry(path, t1, buf, destdir)

def entry_makedir(path):
    return __doEntry(path, 'Make directory', 'Enter directory name:')

def entry_gotodir(path):
    return __doEntry(path, 'Go to', 'Enter local/remote path (ssh:// ftp:// pkg://)')

def entry_gotofile(path):
    return __doEntry(path, 'Go to file', 'Enter file name:')

def entry_touchfile(path):
    return __doEntry(path, 'Touch file', 'Enter file name:')

def entry_editlink(path, link, pointto):
    return __doEntry(path, 'Edit link', 'Link \'%s\' points to' % link, pointto)

def entry_dosmthing(path):
    return __doEntry(path, 'Do something on file(s)', 'Enter command:')


def dentry_createlink(path, pointto):
    curses.endwin()
    print path, pointto

    return DoubleEntry('Create link', 'Symlink name:\n\n\n\n\nPointing to:', pointto, 1, 1,\
            '', '', path, 1, 1, '', 0).run()


def dentry_findgrep(path):
    return DoubleEntry('Search files', 'Find:\n\n\n\n\nGrep:', '*', 1, 1,path,\
                            'Content', '', 1, 0,path, 0).run()



# Menus
def menu_bookmark(bookmarks):
    return  MenuWin('Select Bookmark', bookmarks).run()

def menu_file():
    menu = [ '@    Do something on file',
            'i    File info',
            'p    Chmod and chown',
            'l    Edit symlink',
            'n    Create symlink',
            'g    Gzip/gunzip file',
            'b    Bzip2/bunzip2 file',
            'c    Tar.gz directory',
            'd    Tar.bz2 directory',
            'z    Zip directory',
            'r    Rar directory',
            'x    Unpack',
            'u    Unpack to other panel',

             ]
    return MenuWin('File Menu', menu).run()

def menu_general():
    menu = [ '/    Find/grep file(s)',
             'g    Goto path, ssh, ftp',
             '#    Directories size',
             's    Sort files',
             't    Tree/List view',
             'f    Filesystems info',
             'o    Open shell',
             'c    Edit configuration',
             'd    Reset settings' ]
    return MenuWin('General Menu', menu).run()


def menu_sort():
    menu = [ 
             'n    Filename',
             'e    Extension',
             's    Size',
             'm    Modify time',
             'N    Filename reverse',
             'E    Extension reverse',
             'S    Size reverse',
             'M    Modify time reverse',
             'o    Unsort']
    return MenuWin('Sort Menu', menu).run()

#DoubleEntry(title, help1, path1, with_historic1, with_complete1, tabpath, help2, path2, with_historic2, with_complete2, tabpath,   0).run()
#doDoubleEntry(tab.path, 'Create link', 'Link name', '', 1, 1, 'Pointing to', otherfile, 1, 1)


