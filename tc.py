#!/usr/bin/env python
# -*- coding: iso8859-1 -*-

"""tc 'Twilight commander ver. 2.5.1' is a console file manager for Linux with
the goal to offer an alternative to midnight commander cli file manager.
Python allows much faster development, leading to better functionality, features,
and easier support. The speed penalty is relatively small on modern hardware.
The program is a fork and almost complete rewrite of the "last file manager" v 1.99.
Released under GNU Public License v3, read COPYING file for more details.
007 (C) by Andrey Skvortsov <stingo000@yahoo.ca>


Usage:\ttc <options> [path1 [path2]]
Config:
    ~/.tc

Arguments:
    path1            Left pane starting directory
    path2            Right pane starting directory
Options:
    -h, --help       Show help
"""

"""
Copyright (C) 2007 -       Andrey Skvortsov
              2001 - 2006  Inigo Serna

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os
import getopt
import curses
import sys
import config
import main


######################################################################
#from optparse import OptionParser

def usage(msg = ''):
    if msg != "":
        print 'tc:\t%s\n' % msg
    print __doc__


def parse_command_line(cmd_args):

    paths = []

    # parse args
    # hack, shell function returns a string, not a list,
    # so we have to build a list

    if len(cmd_args) <= 2:
        lst = cmd_args[:]
        cmd_args = [lst[0]]
        if len(lst) > 1:
            cmd_args.extend(lst[1].split())
    try:
        opts, args = getopt.getopt(cmd_args[1:], '12dh', ['debug', 'help'])
    except getopt.GetoptError:
        usage('Bad argument(s)')
        __program_quit(-1)
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            __program_quit(2)

    if len(args) == 0:
        paths.append(os.path.abspath('.'))
        paths.append(os.path.abspath('.'))
    elif len(args) == 1:

        buf = os.path.abspath(args[0])
        if not os.path.isdir(buf):
            usage('<%s> is not a directory' % args[0])
            __program_quit(-1)
        paths.append(buf)
        paths.append(os.path.abspath('.'))

    elif len(args) == 2:

        buf = os.path.abspath(args[0])
        if not os.path.isdir(buf):
            usage('<%s> is not a directory' % args[0])
            __program_quit(-1)
        paths.append(buf)
        buf = os.path.abspath(args[1])

        if not os.path.isdir(buf):
            usage('<%s> is not a directory' % args[1])
            __program_quit(-1)
        paths.append(buf)
    else:
        usage('Incorrect number of arguments')
        __program_quit(-1)

    return paths

def __program_start(args):

    prefs = config.Config()
    ret = prefs.load()
    if ret in [-1, -2]:
        print 'Configuration file does not exist or corrupted. Setting defaults.'
        prefs.save()
        #time.sleep(1)
    paths = parse_command_line(args)
    path = curses.wrapper(__run, paths, prefs)
    __program_quit(0, path)


def __run(win, paths, prefs):
    app = main.Main(win, paths, prefs)
    if app == OSError:
        sys.exit(-1)
    ret = app.run()
    return ret


def __program_quit(ret_code, ret_path = '.'):

    # Return and execute path in the parent console
    # Warning! It may not work properly on some terminals
    try:
        import fcntl, termios
        ret = 'cd %s \n'% ret_path
        for c in ret:
            fcntl.ioctl(1, termios.TIOCSTI,c)
    except:
        pass
    sys.exit(ret_code)


if __name__ == '__main__':
    __program_start(sys.argv)
