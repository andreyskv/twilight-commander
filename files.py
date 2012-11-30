# -*- coding: iso8859-1 -*-

"""files.py"""

import sys
import os
import os.path
import stat
import time
import pwd
import grp

from __init__ import * 


# File Type:    dir, link to directory, link, nlink, char dev,
#               block dev, fifo, socket, executable, file
(FTYPE_DIR, FTYPE_LNK2DIR, FTYPE_LNK, FTYPE_NLNK, FTYPE_CDEV, FTYPE_BDEV,
 FTYPE_FIFO, FTYPE_SOCKET, FTYPE_EXE, FTYPE_REG, FTYPE_UNKNOWN) = range(11)

FILETYPES = { FTYPE_DIR: (os.sep, 'Directory'),
              FTYPE_LNK2DIR: ('~', 'Link to Directory'),
              FTYPE_LNK: ('@', 'Link'), 
              FTYPE_NLNK: ('!', 'No Link'),
              FTYPE_CDEV: ('-', 'Char Device'),
              FTYPE_BDEV: ('+', 'Block Device'),
              FTYPE_FIFO: ('|', 'Fifo'),
              FTYPE_SOCKET: ('#', 'Socket'),
              FTYPE_EXE: ('*', 'Executable'),
              FTYPE_REG: (' ', 'File'),
              FTYPE_UNKNOWN: ('?', 'Unknown type'),
              }


(FT_TYPE, FT_PERMS, FT_OWNER, FT_GROUP, FT_SIZE, FT_MTIME, FT_CTIME, FT_ATIME) = range(8)

(SORT_None, SORT_Name, SORT_Name_rev, SORT_Ext, SORT_Ext_rev,  SORT_Size,
 SORT_Size_rev, SORT_Mtime, SORT_Mtime_rev) = range(9)

suffix =  ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']

########################################################################

def get_rdev(file):
    r = os.stat(file).st_rdev
    return r>>8, r&255


def calcDirSize(arg, dir, files):
    for f in files:
        arg.append(os.lstat(os.path.join(dir, f))[stat.ST_SIZE])


def get_size(file):
    """return dir/file size """

    sizes = []
    try:
        os.path.walk(file, calcDirSize, sizes)
    except:
        pass
    return sum(sizes)

def get_size_lstat(file):
    return os.lstat(file)[stat.ST_SIZE]


def get_realpath(path, filename, filetype):
    """return absolute path"""
    if filetype in [FTYPE_LNK2DIR, FTYPE_LNK,  FTYPE_NLNK]:
        try:
            return '-> ' + os.readlink(os.path.join(path, filename))
        except os.error:
            pass
    return os.path.join(path, filename)


def get_linkpath(path, filename):
    """return absolute path to the destination of a link"""
    link_dest = os.readlink(os.path.join(path, filename))
    return os.path.normpath(os.path.join(path, link_dest))



def __get_filetype(st):
    """get the type of the file. See listed types above"""
    lmode = st[stat.ST_MODE]

    if stat.S_ISREG(lmode) and (lmode & 0111):
        return FTYPE_EXE
    elif stat.S_ISREG(lmode):
        return FTYPE_REG 
    elif stat.S_ISDIR(lmode):
        return FTYPE_DIR
    elif stat.S_ISLNK(lmode): 
        return FTYPE_LNK
    elif stat.S_ISCHR(lmode):
        return FTYPE_CDEV
    elif stat.S_ISBLK(lmode):
        return FTYPE_BDEV
    elif stat.S_ISFIFO(lmode):
        return FTYPE_FIFO
    elif stat.S_ISSOCK(lmode):
        return FTYPE_SOCKET
    else:
        return FTYPE_UNKNOWN

def get_fileinfo(file, pardir_flag = False, show_dirs_size = False):
    """return file attributes, format:
        (filetype, perms, owner, group, size, mtime) """
    try:    
        lst = os.lstat(file)
    except:
        return None

    type = __get_filetype(lst)
    if (type == FTYPE_DIR or type == FTYPE_LNK2DIR) and not pardir_flag \
       and show_dirs_size:
        size = get_size(file)

    elif type == FTYPE_LNK:
        try:
            st =  os.stat(file)
        except OSError:
            type = FTYPE_NLNK
        else:
            if stat.S_ISDIR(st[stat.ST_MODE]):
                type = FTYPE_LNK2DIR
            else:
                type = FTYPE_LNK

        size = lst[stat.ST_SIZE]
    elif type == FTYPE_CDEV or type == FTYPE_BDEV:
        # maj_red, min_rdev  are calculated at show time for performance 
        size = 0
    else:
        size = lst[stat.ST_SIZE]

    if lst[stat.ST_UID]:
        owner =  pwd.getpwuid(lst[stat.ST_UID])[0]
    else:
        owner = ""

    if lst[stat.ST_GID] > 0:
        group = grp.getgrgid(lst[stat.ST_GID])[0]
    else:
        group = ""

    return (type, stat.S_IMODE(lst[stat.ST_MODE]), owner, group,
            size, lst[stat.ST_MTIME], lst[stat.ST_CTIME], lst[stat.ST_ATIME])


def get_dir(path, show_dotfiles = 1):
    """return a dict with file name as key and
         (filetype, perms, owner, group, size, mtime)  as value.
    """
    path = os.path.normpath(path)
    files_dict = {}
    if path != os.sep:
        files_dict[os.pardir] = get_fileinfo(os.path.dirname(path), 1)
    files_list = os.listdir(path)
    if not show_dotfiles:
        files_list = [f for f in files_list if f[0] != '.']
        
    for file in files_list:            
         finfo = get_fileinfo(os.path.join(path, file))
         if finfo:
             files_dict[file] = finfo
    return len(files_dict), files_dict


def get_fileinfo_dict(path, filename, filevalues, columns):
    res = {}

    if NAME in columns:
        res[NAME] = filename
        res[TYPE] = FILETYPES[filevalues[FT_TYPE]][0]
   
    if SIZE in columns:
        typ = filevalues[FT_TYPE]
        if typ in [FTYPE_CDEV ,FTYPE_BDEV]:
            maj_rdev, min_rdev = get_rdev(os.path.join(path, filename))
            res[SIZE] = '%3d,%3d' %(maj_rdev, min_rdev) #rdevs in size column
        else:
            i, sz = 0, filevalues[FT_SIZE]
            while sz > 1000000 and i < len(suffix):
                sz = sz/1024
                i += 1
            res[SIZE]  = ''.join([str(sz), suffix[i]])

    if SIZEHUMN in columns:
        i, sz = 0, filevalues[FT_SIZE]
        while sz > 1000 and i < len(suffix):
            sz = sz/1024.
            i += 1
        sz = round(sz,1)
        res[SIZEHUMN]  = ''.join([str(sz), suffix[i]])

    if PERMS in columns:
        res[PERMS] = perms2str(filevalues[1])

    if PERMSNUM in columns:
        res[PERMSNUM] = str(oct(filevalues[1]))

    if OWNER in columns:
        res[OWNER] = filevalues[FT_OWNER]

    if GROUP in columns:
        res[GROUP] = filevalues[FT_GROUP]

    if MTIME in columns:
        mtime = time.strftime('%d/%m/%y %H:%M', time.localtime(filevalues[FT_MTIME]))
        res[MTIME] = mtime

    if MTIME_LONG in columns:
        mtime = time.strftime('%b %d %Y %H:%M', time.localtime(filevalues[FT_MTIME]))
        res[MTIME_LONG] = mtime

    if MTIME_MC in columns:
        # filedate < 6 months from now, past or future
        if (time.time() - filevalues[FT_MTIME]) < 15552000:
            mtime = time.strftime('%d %b %H:%M', time.localtime(filevalues[FT_MTIME]))
        else:
            mtime = time.strftime('%d %b  %Y', time.localtime(filevalues[FT_MTIME]))
        res[MTIME_MC] = mtime

    if CTIME in columns:
        ctime = time.strftime('%d/%m/%y %H:%M', time.localtime(filevalues[FT_CTIME]))
        res[CTIME] = ctime

    if CTIME_LONG in columns:
        ctime = time.strftime('%b %d %Y %H:%M', time.localtime(filevalues[FT_CTIME]))
        res[CTIME_LONG] = ctime

    if CTIME_MC in columns:
        # filedate < 6 months from now, past or future
        if (time.time() - filevalues[FT_CTIME]) < 15552000:
            ctime = time.strftime('%d %b %H:%M', time.localtime(filevalues[FT_CTIME]))
        else:
            ctime = time.strftime('%d %b  %Y', time.localtime(filevalues[FT_CTIME]))
        res[CTIME_MC] = ctime

    if ATIME in columns:
        atime = time.strftime('%d/%m/%y %H:%M', time.localtime(filevalues[FT_ATIME]))
        res[ATIME] = atime

    if ATIME_LONG in columns:
        atime = time.strftime('%b %d %Y %H:%M', time.localtime(filevalues[FT_ATIME]))
        res[ATIME_LONG] = atime

    if ATIME_MC in columns:
        # filedate < 6 months from now, past or future
        if (time.time() - filevalues[FT_ATIME]) < 15552000:
            atime = time.strftime('%d %b %H:%M', time.localtime(filevalues[FT_ATIME]))
        else:
            atime = time.strftime('%d %b  %Y', time.localtime(filevalues[FT_ATIME]))
        res[ATIME_MC] = atime

    return res



def full_file_info(path, file, w):

    fullpath = os.path.join(path, file)
    file_data = get_fileinfo(fullpath)
    file_data2 = os.lstat(fullpath)
    buf = []
    user = os.environ['USER']
    username = get_user_fullname(user)
    so, host, ver, tmp, arch = os.uname()
    buf.append('%s v%s executed by %s' % (PROG_NAME, VERSION, username))
    buf.append('<%s@%s> on a %s %s [%s]' % (user, host, so, ver, arch))
    buf.append('')

    fileinfo = os.popen('file \"%s\"' % fullpath).read()
    try:
        fileinfo = fileinfo.split(':')[1].strip()
    except:
        fileinfo ="install 'file' tool for info here"

    buf.append('%s: %s (%s)' % (FILETYPES[file_data[0]][1], file,
                                    fileinfo))
    buf.append('Path: %s' % path[-(w-8):])
    buf.append('Size: %s bytes' % file_data[FT_SIZE])
    buf.append('Mode: %s (%4.4o)' % \
                (perms2str(file_data[FT_PERMS]),
                    file_data[FT_PERMS]))
    buf.append('Links: %s' % file_data2[stat.ST_NLINK])
    buf.append('User ID: %s (%s) / Group ID: %s (%s)' % \
                (file_data[FT_OWNER], file_data2[stat.ST_UID],
                    file_data[FT_GROUP], file_data2[stat.ST_GID]))
    buf.append('Last access: %s' % time.ctime(file_data2[stat.ST_ATIME]))
    buf.append('Last modification: %s' % time.ctime(file_data2[stat.ST_MTIME]))
    buf.append('Last change: %s' % time.ctime(file_data2[stat.ST_CTIME]))
    buf.append('Location: %d, %d / Inode: #%X (%Xh:%Xh)' % \
                ((file_data2[stat.ST_DEV] >> 8) & 0x00FF,
                file_data2[stat.ST_DEV] & 0x00FF,
                file_data2[stat.ST_INO], file_data2[stat.ST_DEV],
                file_data2[stat.ST_INO]))
    fss = get_fs_info()
   
    fs = ['/dev', '0', '0', '0', '0%', '/', 'unknown']
    for e in fss:
        try:
            if fullpath.find(e[5]) != -1 and (len(e[5]) > len(fs[5]) or e[5] == os.sep):
                fs = e        
                buf.append('File system: %s on %s (%s) %d%% free' % \
                           (fs[0], fs[5], fs[6], 100 - int(fs[4][:-1])))
        except:
            pass    

    return buf


def perms2str(p):
    permis = ['x', 'w', 'r']
    perms = ['-'] * 9
    for i in range(9):
        if p & (0400 >> i):
            perms[i] = permis[(8-i) % 3]
    if p & 04000:
        perms[2] = 's'
    if p & 02000:
        perms[5] = 's'
    if p & 01000:
        perms[8] = 't'
    return "".join(perms)



def mountpoint(s):
    if (os.path.ismount(s) or len(s)==0):
        return s
    return mountpoint(os.path.split(s)[0])

def get_mntpoint_data(mnt_point):
    
    cmd = 'df -kh %s'%mnt_point
    try:
        out, buf = os.popen4(cmd)
        buf = buf.readlines()
    except:
        return mnt_point

    str_mountpoint = ''
    if len(buf) > 1:
        d = buf[1].split()
        #['/dev/sda2', '233G', '202G', '32G', '87%', '/home']
        try:
            str_mountpoint = ''.join([d[5], ' { ', d[3], ' of ', d[1], ' (', d[4], ')' ' }'])
        except:
            pass
    return str_mountpoint

def get_fs_info():
    """return a list containing the info from'df -k', i.e,
    file systems size and occupation, in Mb. And the filesystem type:
    [dev, size, used, available, use%, mount point, fs type]"""
    try:
        buf = os.popen('df -kh').readlines()
    except (IOError, os.error), (errno, strerror):
        return (strerror, errno)
    else:
        fs = []
        for l in buf:
            if l[0] != os.sep:
                continue
            e = l.split()
            fs.append(e)

        # get filesystems type
        if sys.platform[:5] == 'linux':
            es = open('/etc/fstab').readlines()
            fstype_pos = 2
        elif sys.platform[:5] == 'sunos':
            es = open('/etc/vfstab').readlines()
            fstype_pos = 3
        else:
            es = []
        for f in fs:
            fsdev = f[0]
            for e in es:
                if len(e) < 5:
                    continue
                if fsdev == e.split()[0]:
                    f.append(e.split()[fstype_pos])
                    break
            else:
                f.append('unknown')                                
        return fs

def get_fs_info_buf():
    fs = get_fs_info()
    if type(fs) != type([]):
        return -1, fs
    buf = []
    buf.append('Filesystem       FS type    Total Mb     Used   Avail.  Use%  Mount point')
    buf.append('-')
    for l in fs:
        try:
            buf.append('%-15s  %-10s  %7s  %7s  %7s  %4s  %s' % \
                       (l[0], l[6], l[1], l[2], l[3], l[4], l[5]))
        except:
            pass

    buf[1] = '-' * len(max(buf))
    return buf


def get_owners():
    owners = [e[0]  for e in pwd.getpwall()]
    return owners

def get_groups():
    groups = [e[0] for e in grp.getgrall()]
    return groups

def get_user_fullname(user):
    try:
        return pwd.getpwnam(user)[4]
    except KeyError:
        return '<unknown user name>'

def chmod(file, perms):
    """set permissions to a file"""

    ps = 0
    i = 8
    for p in perms:
        if p == 'x':
            ps += 1 * 8 ** int(i / 3)
        elif p == 'w':
            ps += 2 * 8 ** int(i / 3)
        elif p == 'r':
            ps += 4 * 8 ** int(i / 3)
        elif p == 't' and i == 0:
            ps += 1 * 8 ** 3
        elif p == 's' and (i == 6 or i == 3):
            if i == 6:
                ps += 4 * 8 ** 3
            else:
                ps += 2 * 8 ** 3
        i -= 1
    try:
        os.chmod(file, ps)
    except (IOError, os.error), (errno, strerror):
        return (strerror, errno)


def chown(file, owner, group):
    """set owner and group to a file"""

    try:
        owner_n = pwd.getpwnam(owner)[2]
    except:
        owner_n = -1 #int(owner)
    try:
        group_n = grp.getgrnam(group)[2]
    except:
        group_n = -1 # int(group)
    try:
        os.chown(file, owner_n, group_n)
    except (IOError, os.error), (errno, strerror):
        return (strerror, errno)

########################################################################
# Sort Type:    None, byName, bySize, byDate, byType(?)

def ext_key_func(str):
    s =  os.path.splitext(str)
    return ''.join([s[1], '.', s[0]])


def ext_key_func_lower(str):
    s =  os.path.splitext(str.lower())
    return ''.join([s[1], '.', s[0]])


def __do_sort(f_dict, mode, sort_mix_cases):

    if mode == SORT_None:
        names = f_dict.keys()

    if mode == SORT_Name:
        if sort_mix_cases:
            names = f_dict.keys()
            names.sort(key = str.lower, reverse = False)
        else:
            names = f_dict.keys()
            names.sort(reverse = False)

    elif mode == SORT_Name_rev:
        if sort_mix_cases:
            names = f_dict.keys()
            names.sort(key = str.lower, reverse = True)
        else:
            names = f_dict.keys()
            names.sort(reverse = True)

    elif mode == SORT_Ext:
        if sort_mix_cases:
            names = f_dict.keys()
            names.sort(key = ext_key_func_lower, reverse = False)
        else:
            names = f_dict.keys()
            names.sort(key = ext_key_func, reverse = False)

    elif mode == SORT_Ext_rev:
        if sort_mix_cases:
            names = f_dict.keys()
            names.sort(key = ext_key_func_lower, reverse = True)
        else:
            names = f_dict.keys()
            names.sort(key = ext_key_func, reverse = True)


    elif mode == SORT_Size:
        d = f_dict.items()
        d.sort(key = lambda x:x[1][4]) #sort by size column
        names = [n[0]for n in d]

    elif mode == SORT_Size_rev:
        d = f_dict.items()
        d.sort(key = lambda x:x[1][4], reverse = True )
        names = [n[0]for n in d]

    elif mode == SORT_Mtime:
        d = f_dict.items()
        d.sort(key = lambda x:x[1][5], reverse = False ) #sort by date column
        names = [n[0]for n in d]

    elif mode == SORT_Mtime_rev:
        d = f_dict.items()
        d.sort(key = lambda x:x[1][5], reverse = True )
        names = [n[0]for n in d]

    if names and names.count(os.pardir):
        names.remove(os.pardir)
        names.insert(0, os.pardir)
    return names


def sort_dir(files_dict, sortmode, sort_mix_dirs, sort_mix_cases):
    """return an array of files which are sorted by mode """
    d, f = {},{}
    if sort_mix_dirs:
        f = files_dict
    else:
        for k, v in files_dict.items():            
            if v[FT_TYPE] in [FTYPE_DIR, FTYPE_LNK2DIR]:
                d[k] = v
            else:
                f[k] = v
    
    d2 = __do_sort(f, sortmode, sort_mix_cases)
    if sortmode == SORT_Ext:
        sortmode = SORT_Name
    elif sortmode == SORT_Ext_rev:
        sortmode = SORT_Name_rev
    d1 = __do_sort(d, sortmode, sort_mix_cases)
    d1.extend(d2)
    return d1
