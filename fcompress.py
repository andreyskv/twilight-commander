# -*- coding: iso8859-1 -*-

"""fcompress.py

This module contains archive pack/unpack functions.
"""
import os 
import files
from fprocess import  ProcessBaseLoop
import utils
import wcall

######################################################################

class PackagerBase:
    def __init__(self, filename):
        while filename[-1] == os.sep:
            filename = filename[:-1]
        self.fullname = filename
        self.dirname = os.path.dirname(filename)
        self.filename = os.path.basename(filename)


    def build_uncompress_cmd(self):
        return self.uncompress_cmd % self.fullname


    def build_compress_cmd(self):

        newfile = self.filename + self.exts[0]

        if os.path.isfile(self.fullname):
            if self.type in ('bz2:', 'gz:'):
                return self.compress_cmd % self.filename

            elif self.type in ('tbz2:', 'tgz:'):
                return # Don't use tar, it's a file
            else:
                return self.compress_cmd % (self.filename, newfile)

        elif os.path.isdir(self.fullname):
            if self.type in ('bz2:', 'gz:'):
                return # Don't compress without tar, it's a dir

            if self.need_tar:
                return self.compress_cmd % (self.filename, newfile)
            else:
                return self.compress_cmd % (newfile, self.filename)


class PackagerTAR(PackagerBase):
    type = 'tar:'
    exts = ('.tar',)
    need_tar = False
    uncompress_cmd = 'tar xf \"%s\"'
    compress_cmd   = 'tar cf - \"%s\" > \"%s\"'
    compressXXX_cmd = 'tar cf - * \"%s\"'

class PackagerTBZ2(PackagerBase):
    type = 'tbz2:'
    exts = ('.tar.bz2', '.tbz2')
    need_tar = True
    uncompress_cmd  = 'bzip2 -d \"%s\" -c | tar xfi -'
    compress_cmd    = 'tar cf - \"%s\" | bzip2 > \"%s\"'
    compressXXX_cmd = 'tar cf - * | bzip2 > \"%s\"'

class PackagerBZ2(PackagerBase):
    type = 'bz2:'
    exts = ('.bz2', )
    need_tar = False
    uncompress_cmd  = 'bzip2 -d \"%s\"'
    compress_cmd    = 'bzip2 \"%s\"'
    compressXXX_cmd = 'bzip2 *'

class PackagerTGZ(PackagerBase):
    type = 'tgz:'
    exts = ('.tar.gz', '.tgz', '.tar.Z')
    need_tar = True
    uncompress_cmd =  'gzip -d \"%s\" -c | tar xfi -'
    compress_cmd =    'tar cf - \"%s\" | gzip  > \"%s\"'
    compressXXX_cmd = 'tar cf - * | gzip > \"%s\"'

class PackagerGZ(PackagerBase):
    type = 'gz:'
    exts = ('.gz', )
    need_tar = False
    uncompress_cmd = 'gzip -d \"%s\"'
    compress_cmd   = 'gzip \"%s\"'

class PackagerZIP(PackagerBase):
    type = 'zip:'
    exts = ('.zip', )
    need_tar = False
    uncompress_cmd  = 'unzip -q \"%s\"'
    compress_cmd    = 'zip -qr \"%s\" \"%s\"'
    compressXXX_cmd = 'zip -qr \"%s\" *'

class PackagerRAR(PackagerBase):
    type = 'rar:'
    exts = ('.rar', )
    need_tar = False
    uncompress_cmd  = 'rar x \"%s\"'
    compress_cmd    = 'rar a \"%s\" \"%s\"'
    compressXXX_cmd = 'rar a \"%s\" *'

class PackagerDEB(PackagerBase):
    type = 'deb:'
    exts = ('.deb', )
    need_tar = True
    uncompress_cmd = 'ar -p \"%s\" ./data.tar.gz | tar zxpf -'

class PackagerRPM(PackagerBase):
    type = 'rpm:'
    exts = ('.rpm', )
    need_tar = True
    uncompress_cmd = 'rpm2cpio \"%s\" | cpio -idm --quiet '

class PackagerCAB(PackagerBase):
    type = 'cab:'
    exts = ('.cab', '.Cab', '.CAB' )
    need_tar = True
    uncompress_cmd = 'cabextract -q \"%s\"'

#class PackagerACE(PackagerBase):
    #type = 'unace'
    #exts = ('.ace', )
    #need_tar = False
    #uncompress_cmd = 'unace x -y \"%s\ "' +'> /dev/null'

fpackagers = (PackagerBZ2, PackagerGZ )
dpackagers = (PackagerTAR, PackagerTGZ, PackagerTBZ2,
              PackagerZIP, PackagerRAR, PackagerCAB,
              PackagerDEB, PackagerRPM #, PackagerACE
              )

packagers_by_type = { 'tar:': PackagerTAR,
                      'tbz2:': PackagerTBZ2,
                      'bz2:': PackagerBZ2,
                      'tgz:': PackagerTGZ,
                      'gz:': PackagerGZ,
                      'zip:': PackagerZIP,
                      'rar:': PackagerRAR,
                      'cab:': PackagerCAB,
                      #'unace:': PackagerACE,
                      'deb:': PackagerDEB,
                      'rpm:': PackagerRPM
                       }


def check_compressed(filename,  pack_type):

    if pack_type == 'file':
        packagers = fpackagers
    elif pack_type == 'dir':
        packagers = dpackagers
    for p in packagers:
        for e in p.exts:
            if filename.endswith(e):
                return p(filename)
    return None


def check_compressed_file_type(filename):
    c = check_compressed(filename, 'dir')
    if c:
        return c.type
    return None


def strip_archive_extension(fname):
    for p in dpackagers:
        for e in p.exts:
            if fname.endswith(e):
                return fname.split(e)[0]
    for p in fpackagers:
        for e in p.exts:
            if fname.endswith(e):
                return fname.split(e)[0]
    return fname


def do_delete(file):
    if os.path.islink(file):
        os.unlink(file)
    elif os.path.isdir(file):
        for f in os.listdir(file):
            do_delete(os.path.join(file, f))
        os.rmdir(file)
    else:
        try:
            os.unlink(file)
        except:
            pass


######################################################################
class ProcessUnCompressLoop(ProcessBaseLoop):

    def __init__(self, app, func = None, lst = [], *args):

        self.app = app
        #self.unpack_flag = False
        if func == 'comp_dir':
            func = self.do_compress_uncompress_dir
            action= 'Compressing directory'

        elif func == 'uncomp_dir':
            func = self.do_compress_uncompress_dir
            action = 'Uncompressing directory'
            #self.unpack_flag = True

        elif func == 'ucomp_file':
            func = self.do_compress_uncompress_file
            action = '(Un)Compressing file'

        #elif func == 'uncomp_vfs':
            #func = self.do_compress_uncompress_dir
            #action = 'Creating archive VFS'
            ##self.unpack_flag = True

        #elif func == 'comp_vfs':

            #func = self.do_compress_vfs
            #action = 'Rebuilding archive'

        else:
            return

        #self.source_file = args[0]+os.sep+lst[0]
        self.source_file = os.path.join(args[0], lst[0])
        self.source_size = files.get_size(self.source_file)
        ProcessBaseLoop.__init__(self, app, action, func, lst, *args)
    def prepare_args(self):
        return (self.filename, ) + self.args


    def process_response(self, result):
        if type(result) == type((1, )): # error
            st, msg = result
            if st == -1:
                self.show_parent()
                wcall.err_general(self.action, msg)
        self.ret = result
        return 0


    def with_gui(self):

        # show gui if size of the archive is greater than arch_size (Kb)
        if not self.source_size >1024*self.app.prefs.options['archive_size_show_gui']:
            return False
        return True


    def do_compress_uncompress_file(self, filename, path, dest, type):

        fullfile = os.path.join(path, filename)
        if not os.path.isfile(fullfile):
            return -1, '%s: can\'t un/compress' % filename

        c = check_compressed(fullfile,'file')
        if c == None or c.type != type:

            #return -1, '%s: file type' % c.type
            packager = packagers_by_type[type]
            c = packager(fullfile)
            cmd = c.build_compress_cmd()
        else:
            cmd = c.build_uncompress_cmd()
        st, msg = utils.run_shell(cmd, path, return_output = True)
        return st, msg


    def do_compress_uncompress_dir(self, filename, path, dest, type):

        fullfile = os.path.join(path, filename)

        if  os.path.isfile(fullfile):
            c = check_compressed(fullfile, 'dir')
            if c:
                cmd = c.build_uncompress_cmd()
            else:
                return -1, '%s: can\'t uncompress' % filename

        elif os.path.isdir(fullfile) and type:
            c = packagers_by_type[type](fullfile)
            if c == None:
                return -1, '%s: can\'t compress' % filename

            cmd = c.build_compress_cmd()
        else:
            return -1, '%s: can\'t un/compress' % filename

        return utils.run_shell(cmd, dest, return_output = True)

#old vfs code
    #def do_compress_vfs(self, filename, path, vfs_path, dest):

        #fullfile = os.path.join(path, filename)
        #c = check_compressed(vfs_path,'dir')
        #if c:
            #cmd = c.compressXXX_cmd % (path + c.exts[0])
        #else:
            #return -1, '%s: can\'t rebuild archive' % filename

        #return utils.run_shell(cmd, dest, return_output = True)
