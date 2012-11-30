# -*- coding: iso8859-1 -*-
# foper.py - Contains classes and functions to perform file operations

import os
import files
import time
import wcall
import utils
import shutil
from fprocess import ProcessFunc, ProcessBaseLoop

import curses # for debugging only

###############################################################################
# Create or modify symlink
def modify_link(pointto, linkname):
    try:
        os.unlink(linkname)
        create_link(pointto, linkname)
    except (IOError, os.error), (errno, strerror):
        return (strerror, errno)

def create_link(pointto, linkname):
    try:
        os.symlink(pointto, linkname)
    except (IOError, os.error), (errno, strerror):
        return (strerror, errno)


###############################################################################
# Create directory
def mkdir(path, newdir):
    fullpath = os.path.join(path, newdir)
    try:
        os.makedirs(fullpath)
    except (IOError, os.error), (errno, strerror):
        return (strerror, errno)

###############################################################################
# Launch recursive delete operation with graphic and
class ProcessDeleteLoop(ProcessBaseLoop):

    def __init__(self, app, lst = [], *args):
        ProcessBaseLoop.__init__(self, app, 'Deleting files', self.delete, lst, *args)
        self.delete_all = not self.app.prefs.confirmations['delete']

    def ask_confirmation(self):
        if self.delete_all:
            return 2
        buf = 'Delete \'%s\'' % self.filename

        if self.app.prefs.confirmations['delete']:
            self.show_parent()

            del_def = 1
            if len(self.lst) == 1:
                del_def = 0
            ans = wcall.cfm_delete( buf, del_def)
            if ans == 2:
                self.delete_all = True
            elif ans == -2:
                return -1
            return ans

    def prepare_args(self):
        return (self.filename, ) + self.args

    def process_response(self, result):
        if type(result) == type((1,)):               # error from child
            wcall.err_general('%s \'%s\'' % (self.action, self.filename),
                           '%s (%s)' % result)
        return 0

    def do_delete(self,file):
        if os.path.islink(file):
            os.unlink(file)
        elif os.path.isdir(file):
            for f in os.listdir(file):
                self.do_delete(os.path.join(file, f))
            os.rmdir(file)
        else:
            os.unlink(file)

    def delete(self,file, path):
        fullpath = os.path.join(path, file)
        try:
            self.do_delete(fullpath)
        except (IOError, os.error), (errno, strerror):
            return (strerror, errno)

    def with_gui(self):
        return False


class ProcessCopyMoveLoop(ProcessBaseLoop,ProcessDeleteLoop):

    def __init__(self, app, action = '', func = None, lst = [], *args):

        if func in ['copy', 'backup']:
            func, action  = self.copy, 'Copying files'
        elif func in ['move', 'rename']:
            func, action = self.move, 'Moving files'

        #initilize size to copy
        self.total_size , self.cur_total_size = 0,0
        self.cur_dest_size, self.cur_source_size = 0,0
        self.dest_file  = ''

        self.src_file = ''


        #self.time = 0
        #self.speed = 0 
        #self.cur_size_previous = 0 
        #self.time_previous = 0


        self.cur_tim,  self.prev_tim = 0, 0
        for i in range(len(lst)):
            self.total_size += files.get_size(os.path.join(args[0],lst[i]))

        ProcessBaseLoop.__init__(self, app, action, func, lst, *args)
        self.overwrite_all = not self.app.prefs.confirmations['overwrite']
        self.overwrite_none = False

    def init_gui(self):
        if self.with_gui():
            #self.dlg = wcall.win_progress_double()
            self.dlg = wcall.win_progress_move_copy()
            self.dlg.pwin.window().nodelay(1)
            self.show_win()


    def show_win(self):

        if self.with_gui():
            if self.dlg.pwin.hidden():
                self.dlg.pwin.show()
            if self.dest_file:
                try:
                    #self.cur_dest_size = os.lstat(self.dest_file)[stat.ST_SIZE]
                    self.cur_dest_size = files.get_size_lstat(self.dest_file)

                    #self.time = time.clock()
                    #if (self.time - self.time_previous) > 0:
                        #self.speed = (self.cur_dest_size- self.cur_size_previous)/(self.time -\
                            #self.time_previous)/1024.0/1024.0

                    #self.cur_size_previous = self.cur_dest_size
                    #self.time_previous = self.time

                except:
                    pass
                self.filename = os.path.basename(self.dest_file)

            title = self.action + ' %d/%d' % (self.file_i+1, self.length)
            percent = percent2 = 0
            if self.total_size:
                percent = max(min(100*self.cur_total_size/self.total_size, 100),0)
                

            if  self.cur_source_size:
                percent2 = max(min(100*self.cur_dest_size/self.cur_source_size, 100),0)


            #self.dlg.show(title, self.filename, ' Press Esc to stop ', percent, percent2)
            #self.dlg.show(title, self.filename, ' Press Esc to stop %.3f' % self.speed , percent, percent2,\
                                            #os.path.dirname(self.src_file), self.dest_file)

            self.dlg.show(title, self.filename, ' Press Esc to stop ', percent, percent2,\
                                            os.path.dirname(self.src_file), self.dest_file)


    def prepare_args(self):
        if self.overwrite_all:
            return (self.filename, ) + self.args + (False, )
        else:
            return (self.filename, ) + self.args

    def process_response(self, result):

        if isinstance(result, str): # overwrite file?
            if self.overwrite_none:
                return 0
            n = 0
            if len(self.lst) >1: n = 1

            src = os.path.join(self.args[0], self.filename)
            if not os.path.isfile (self.args[1]):
                dest = os.path.join( self.args[1], result)
            else:
                dest = self.args[1]

            size_src, mtime_src, size_dest, mtime_dest = '','','',''
            try:
                finfo_src = files.get_fileinfo(src)

                size_src = finfo_src[files.FT_SIZE]
                mtime_src = time.strftime('%a %b %d %Y %H:%M', \
                                        time.localtime(finfo_src[files.FT_MTIME]))

                finfo_dest = files.get_fileinfo(dest)
                size_dest = finfo_dest[files.FT_SIZE]
                mtime_dest = time.strftime('%a %b %d %Y %H:%M', \
                                        time.localtime(finfo_dest[files.FT_MTIME]))
            except:
                pass

            ans = wcall.cfm_overwrite(self.action, dest, mtime_src, size_src,\
                                            mtime_dest, size_dest, n)

            if ans == -1:
                return -1
            elif ans == -2:
                self.overwrite_none = True
                return -1
            elif ans == 0:
                return 0
            elif ans == 1:
                pass
            elif ans == 2:
                self.overwrite_all = True

            self.ret=[] # need to reset child return value
            args = (self.filename, ) + self.args + (False, ) #False is overwrite flag
            self.p2c.send(('exec', args))
            #return 1
            return self.wait_for_answer()

        elif isinstance(result, tuple): # error from child
            wcall.err_general('%s \'%s\'' % (self.action, self.filename),
                           '%s (%s)' % result)
            return 0
        return 0    #continue copying/moving


#child processes
    def do_copy(self,source, dest):
        if os.path.islink(source):
            dest = os.path.join(os.path.dirname(dest), os.path.basename(source))
            try:
                create_link(os.readlink(source), dest)
            except (IOError, os.error), (errno, strerror):
                return (strerror, errno)
        elif os.path.isdir(source):
            try:
                os.mkdir(dest)
                #self.cur_total_size += os.lstat(dest)[stat.ST_SIZE]
                self.cur_total_size += files.get_size_lstat(dest)
                self.c2p.send(('copysize', self.cur_total_size))
            except (IOError, os.error), (errno, strerror):
                pass     # don't return if directory exists

            for f in os.listdir(source):
                self.do_copy(os.path.join(source, f), os.path.join(dest, f))
        elif source == dest:
            raise IOError, (0, "Source and destination are the same file")
        else:
            # send data to parent
            # format: 'current', path to destination and current files
            self.c2p.send(('current', (dest, source)))

            #perform copy operation
            shutil.copy2(source, dest)
            #self.cur_total_size += os.lstat(dest)[stat.ST_SIZE]
            self.cur_total_size += files.get_size_lstat(dest)
            # format: 'copysize', current total size
            self.c2p.send(('copysize', self.cur_total_size))


    def pre_copy_move(self, file, path, destdir, check_fileexists):

        fullpath = os.path.join(path, file)
        if destdir[0] != os.sep:
            destdir = os.path.join(path, destdir)

        if os.path.isdir(destdir):
            destdir = os.path.join(destdir, os.path.basename(file))
        if os.path.exists(destdir) and check_fileexists:
            self.c2p.send(('result', str(os.path.basename(destdir))))
            return '',''
        return fullpath, destdir


    def copy(self,file, path, destdir, check_fileexists = 1):
        fullpath, destdir =\
             self.pre_copy_move(file, path, destdir, check_fileexists)
        if not fullpath:
            return 'empty'  # need to return empty result
        try:
            self.do_copy(fullpath, destdir)
        except (IOError, os.error), (errno, strerror):
            return (strerror, errno)


    def move(self,file, path, destdir, check_fileexists = 1):
        fullpath, destdir =\
             self.pre_copy_move(file, path, destdir, check_fileexists)
        if not fullpath:
            return 'empty'  # need to return empty result
        try:
            os.rename(fullpath, destdir)
        except OSError:
            try:
                self.do_copy(fullpath, destdir)
            except (IOError, os.error), (errno, strerror):
                try:
                    self.do_delete(destdir)
                except (IOError, os.error), (errno, strerror):
                    return (strerror, errno)

            try:
                self.do_delete(fullpath)
            except (IOError, os.error), (errno, strerror):
                return (strerror, errno)


######################################################################
class ProcessRenameBackupLoop(ProcessCopyMoveLoop):

    def with_gui(self):
        return False

class ProcessDirSizeLoop(ProcessBaseLoop):

    #def ask_confirmation(self):
        #return 1

    def prepare_args(self):
        return (self.filename, ) + self.args

    #def process_response(self, result):
        ##self.ret.append(result)
        #return 0

######################################################################

class SearchFunc(ProcessFunc):
    #def __init__(self, app, action = '', subtitle = '', func = None, *args):
    def __init__(self, app, path, files, pattern, ignorecase = 0):

        self.pattern, self.path = pattern, path
        pattern_esc  = utils.insert_backslash(pattern)
        pathescape = utils.insert_backslash(path)
        ign = ''
        if ignorecase:
            ign = 'i'
        if pattern:
            cmd = 'find %s -name \"%s\" -exec grep -EHn%s \"%s\" {} \\;' % \
            (pathescape, files, ign, pattern_esc)
            text =  'Searching for \"%s\" in \"%s\" files' % (pattern, files)
        else:
            cmd = 'find %s -name \"%s\" -print' % (pathescape, files)
            text =  'Searching for \"%s\" files' % files

        args =  cmd, path, True
        ProcessFunc.__init__(self, app, 'Search', text, utils.run_shell, *args)


    def __parse_grep(self,line):
        line_num, filename = '', ''
        binl = 'Binary file '   #Grep return begins with this text for binary files
        if line[:12] == binl:
            f = line.replace(binl, '')
            f = f.split(' ')
            for i in range(len(f)):
                filename = ' '.join([filename,f[i]])
                filename = filename.strip()
                if os.path.exists(filename):
                    break
        else:
            f = line.split(':')
            for i in range(len(f)):
                filename = ':'.join([filename,f[i]])
                filename = filename.lstrip(':')
                if os.path.exists(filename):
                    if i+1 < len(f):
                        line_num = f[i+1]
                    break
        return filename, line_num


    def get_result(self):
        st, ret = self.ret
        if st < 0:          # (-100, -1) => error
            return st, ret
        ret = ret.split('\n')
        matches = []
        for l in ret:
            if not l:
                continue
            if self.pattern:
                filename, line_num = self.__parse_grep(l)  # grep
            else:
                filename, line_num = l, ''                 # find
            filename = filename.replace(self.path, '')
            if filename not in [None, '']:
                if filename[0] == os.sep and self.path != os.sep:
                    filename = filename.lstrip(os.sep)
                line = filename
                if line_num:
                    line = ':'.join([line_num, filename])
                matches.append(line)
        return 0, matches
