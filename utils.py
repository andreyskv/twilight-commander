# -*- coding: iso8859-1 -*-

"""utils.py"""

import os
#import popen2
#import select
#import time


def run_shell(cmd, path, return_output = False):
    """ run command in shell """
    if  cmd:            
        cmd = 'cd "%s"; %s' % (path, cmd)   
        try:    
            buf = os.popen(cmd).readlines()
        except (IOError, os.error), (errno, strerror):
            return -1, strerror
        else:        
            if return_output:
                return 0, ''.join(buf)
            else:
                return 0, ''
    return 0, ''

#
#def run_shell(cmd, path, return_output = False):
#    """ run command in shell """
#    if not cmd:
#        return 0, ''
#    
#    p = popen2.Popen3(cmd, capturestderr=True)
#    p.tochild.close()
#    outfd = p.fromchild
#    errfd = p.childerr
#    output = []
#    error = []
#    while True:
#        # check if finished
#        (pid, status) = os.waitpid(p.pid, os.WNOHANG)
#        if pid > 0:
#            status = status >> 8
#            o = p.fromchild.readline()
#            while o: # get output before quit
#                o = o.strip()
#                if o:
#                    output.append(o)
#                o = p.fromchild.readline()
#            e = p.childerr.readline()
#            while e: # get error before quit
#                e = e.strip()
#                if e:
#                    error.append(e)
#                e = p.childerr.readline()
#            break
#        # check for output
#        ready = select.select([outfd, errfd], [], [], .01)
#        if outfd in ready[0]:
#            o = p.fromchild.readline()
#            if o:
#                output.append(o)
#        if errfd in ready[0]:
#            e = p.childerr.readline()
#            while e: # get the whole error message
#                e = e.strip()
#                if e:
#                    error.append(e)
#                e = p.childerr.readline()
#            status = p.wait() >> 8
#            break
#        time.sleep(0.1) # extra time to update output in case execution is too fast
#    # return
#    p.fromchild.close()
#    p.childerr.close()
#    if status != 0:
#        error.insert(0, 'Exit code: %d' % status)
#        return -1, '\n'.join(error)
#    if error != []:
#        return -1, '\n'.join(error)
#    if return_output:
##        return 0, '\n'.join(output)       
#    else:
#        return 0, ''


def run_detached(prog, *args):
    """ run program detached from terminal """
    pid = os.fork()
    if pid == 0:
        os.setsid()
        os.chdir('/')
        try:
            maxfd = os.sysconf("SC_OPEN_MAX")
        except (AttributeError, ValueError):
            maxfd = 256       # default maximum
        for fd in range(0, maxfd):
            try:
                os.close(fd)
            except OSError:   # ERROR (ignore)
                pass
        # Redirect the standard file descriptors to /dev/null.
        os.open("/dev/null", os.O_RDONLY)    # standard input (0)
        os.open("/dev/null", os.O_RDWR)       # standard output (1)
        os.open("/dev/null", os.O_RDWR)       # standard error (2)
        pid2 = os.fork()
        if pid2 == 0:
            os.execlp(prog, prog, *args)
        else:
            os.waitpid(-1, os.P_NOWAIT)
        os._exit(0)
    else:
        os.wait()


def get_shell_output(cmd):
    """ get output from a command run in shell"""
    i, a = os.popen4(cmd)
    buf = a.read()
    i.close(), a.close()
    return buf.strip()


#def get_shell_output2(cmd):
#    """ get output from a command run in shell, no stderr """
#    i, o, e = os.popen3(cmd)
#    buf = o.read()
#    i.close(), o.close(), e.close()
#    if not buf:
#        return ''
#    else:
#        return buf.strip()


def insert_backslash(s):
    inp = ['\\',' ','(',')','$','&','<','>','|','\'','\"','`']
    out = ['\\\\','\\ ','\(','\)','\$','\&','\<','\>','\|','\\\'','\\\"','\`']
    for i, o in zip(inp, out):
        s = s.replace(i,o)
    return s