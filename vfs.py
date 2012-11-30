# -*- coding: iso8859-1 -*-

"""vfs.py

This module manages vfs connections via avfs, sshfs, curlftpfs
"""
import os
from tempfile import mkdtemp

import curses

import wcall
from utils import get_shell_output

######################################################################
arch_vfs = ('tar:', 'tbz2:', 'tgz:', 'gz:', 'zip:', 'rar:', 'cab:', 'deb:', 'rpm:')
net_vfs = ('ssh:', 'ftp:')

pkg_exts = ('.tar', '.tar.bz2', '.tbz2', '.bz2', '.tar.gz', '.tgz', '.tar.Z', '.gz',  '.zip','.rar','.deb','.rpm','cpio','lha','zoo')

def check_avfs_type(filename):

    for e in pkg_exts:
        if filename.endswith(e):
            return True
    return False

class VFS:

    def __init__(self, vfs_path, tab_path, filename, vfstype = 'pkg:'):

        self.base =''
        self.prev_path = ''
        self.avfs = os.path.expanduser('~/.avfs')
        self.server = vfs_path
        self.__execute_command()
        self.set_virtual_base()
        self.mounted = True
        if not os.path.isdir(self.base) or not os.listdir(self.base):
            self.mounted = False
            self.exit()
        
        self.prev_path = tab_path
        self.sel_file = filename

    def __execute_command(self):

        cmd = 'mountavfs'
        get_shell_output(cmd)
        self.base = self.avfs + self.server

    def set_virtual_base(self):
        """set prefix for the virtual path, like 'ssh://me@myserver.com'"""
        self.vbase = 'pkg://'+self.base.replace(self.avfs, '')

    def __del(self):
        self.exit()

    def exit(self):

        self.base = ''
        self.vfs = ''
        self.vbase = ''
        self.vfs_file = ''

    def check_exit(self,path):

        normpath = os.path.normpath(path)
        if normpath.find(os.path.basename(self.server)) <= 0: #tmpdirname not in path ?
            self.exit()
            if os.path.basename(path) == os.pardir:
                path = os.path.dirname(self.vbase)
            self.vfs, self.base, self.vbase = '', '',''
            return self.sel_file, self.prev_path # exit vfs
        return '','' # do not exit vfs

    def vfs_name(self):
        return self.server

    def vfs_path(self, path):
        '''return full virtual path, i.e vbase + server path '''
        return 'pkg://'+path.replace(self.avfs, '')



class VFS_net:


    def __init__(self, app, vfs_path, tab_path, filename, vfstype):

        self.app = app
        self.base =''
        self.cmd = ''
        self.prev_path = ''
        self.vfs = vfstype

        if vfstype in net_vfs:
            if not self.__parse_command(vfs_path):
                return

            if not self.__build_command():
                return

            self.__execute_command()
            self.vbase = self.__set_virtual_base()

        self.mounted = True
        if not os.listdir(self.base):
            self.mounted = False
            self.exit()

        self.prev_path = tab_path
        self.sel_file = filename



    def __execute_command(self):

        self.base = mkdtemp('',self.server) # tempdir basename
        curses.endwin()
        cmd = 'echo \'Connecting to host %s..\'; %s %s'\
                                         %(self.server,self.cmd, self.base)

        os.system(cmd)
        curses.curs_set(0)


    def __parse_command(self, path):
        self.protocol, self.login, self.server, self.port, self.path =\
                                                            '','','','',''
        try:
            self.protocol, cmd = path.split('//',1)
        except:
            wcall.err_unsuported_protocol()
            return False

        lst = cmd.split('@',1)
        if len(lst) > 1:
            self.login, cmd = lst[0], lst[1]
        else:
            cmd = lst[0]
        lst2 =cmd.split('/',1)
        if len(lst2) > 1:
            self.path = os.sep + lst2[1]
        lst3 = lst2[0].split(':',1)
        self.server = lst3[0]
        if len(lst3) > 1:
            self.port = lst3[1]
        return True


    def __build_command(self):

        if self.protocol == 'ssh:':
            self.cmd = self.server
            if self.login:
                self.cmd = ''.join([self.login,'@',self.cmd])

            if not self.path:
                self.path = os.sep
            #instead of path add use server root dir for mounting
            self.cmd = ''.join([self.cmd, ':' ,os.sep])

            if self.port:
                self.cmd = ''.join([self.cmd,' -p ',self.port])
            self.cmd = ''.join(['sshfs ', self.cmd, ' '])

        elif self.protocol == 'ftp:':
            self.cmd = self.server
            if not self.login:
                self.login = 'anonymous:no'
            self.cmd = ''.join(['-o user=', self.login,' ',self.cmd])


            if self.port:
                self.cmd = ''.join([self.cmd, ':', self.port])

            if not self.path:
                self.path = os.sep
            #instead of path add use server root dir for mounting
            self.cmd = ''.join([self.cmd, os.sep])


            self.cmd = ''.join(['curlftpfs ', self.cmd, ' '])
        else:
            wcall.err_unsuported_protocol()
            return False
        return True


    def __set_virtual_base(self):
        """set prefix for the virtual path, like 'ssh://me@myserver.com'"""
        vbase = ''.join([self.protocol,'//',self.login,'@',self.server])
        if self.port:
            vbase = ''.join([vbase, ':', self.port])
        return vbase


    def __del(self):
        self.exit()

    def exit(self):

        if self.base:
            if self.mounted:
                os.system('fusermount -u %s' %(self.base))
            try:
                os.rmdir(self.base)
            except:
                pass
        self.base = ''
        self.vfs = ''
        self.vbase = ''
        self.vfs_file = ''


    def check_exit(self,path):
        normpath = os.path.normpath(path)
        if normpath.find(os.path.basename(self.base)) <= 0: #tmpdirname not in path ?
            self.exit()
            if os.path.basename(path) == os.pardir:
                path = os.path.dirname(self.vbase)
            self.vfs, self.base, self.vbase = '', '',''
            return self.sel_file, self.prev_path # exit vfs
        return '','' # do not exit vfs

    def vfs_name(self):
        return self.server


    def vfs_path(self, path):
        '''return full virtual path, i.e vbase + server path '''
        return self.vbase + path.replace(self.base, '')

