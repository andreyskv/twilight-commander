# -*- coding: iso8859-1 -*-
""" fprocess.py - Contains inter-process communication classes """

import os
import os.path
import signal
import select
import cPickle
import wcall

import files
#import time
import curses # for debugging only

class IPC:
    """
    Processes Communication
    Creates a pipe for transfering data btw parent and child processes
    For example, if one writes to wfd, another can read it at rfd (pipe!)
    """
    def __init__(self):
        pipe_r, pipe_w = os.pipe()
        self.rfd = os.fdopen(pipe_r, 'rb', 0)
        self.wfd = os.fdopen(pipe_w, 'wb', 0)

    def send(self, buf):
        """Send data to first pipe end """
        cPickle.dump(buf, self.wfd)
        #time.sleep(0.01)
        #cPickle.dump(None, self.wfd)

    def receive(self):
        """Read data from second pipe end """
        try:
            ready = select.select([self.rfd], [], [], 0.01)
        except:
            return 0, None
        if self.rfd in ready[0]:
            try:
                buf = cPickle.load(self.rfd)
            except:
                return -1, 'Error unmarshaling'
            if buf == None:
                return 0, None
            try:
                arg1, arg2 = buf
            except:
                return -1, 'Malformed response'
            return 1, buf
        return 0, None

    def close(self):
        """Close pipe descriptors"""
        self.rfd.close()
        self.wfd.close()


class ProcessFunc:
    """
    Manages one-way processes communication:
    1. child -> parent
    func with args is a function with arguments runing in child
    returns: (status, message)
    """
    def __init__(self, app, action = '', subtitle = '', func = None, *args):

        self.app, self.func, self.args = app, func, args
        self.action, self.subtitle = action[:app.maxw-14], subtitle[:app.maxw-14]

        self.ret = []
        self.animcursor = wcall.win_dash()
        self.init_gui()

    def init_gui(self):
        """Initilize parent dialog to show child status"""
        if self.with_gui():
            self.dlg = wcall.win_nokey( self.app, self.action, self.subtitle)
            self.dlg.pwin.window().nodelay(1)

    def end_gui(self):
        """Close window, redraw screen"""
        if self.with_gui():
            self.dlg.pwin.window().nodelay(0)
            self.show_parent()

    def show_parent(self):
        """Redraw screen"""
        self.app.display()

    def show_win(self):
        """Show progress dialog"""
        if self.with_gui():
            if self.dlg.pwin.hidden():
                self.dlg.pwin.show()


    def check_keys(self):
        """Check if user decided to interrupt"""
        ch = self.animcursor.cur_win.getch()
        if ch == 0x1B:  #Esc
            groupid = os.getpgid(self.pid_child)
            os.killpg(groupid, signal.SIGSTOP)
            if wcall.cfm_stop('%s %s' % (self.action, self.subtitle)):
                os.killpg(groupid, signal.SIGKILL)
                os.wait()
                return -100
            else:
                self.show_win()
                os.killpg(groupid, signal.SIGCONT)
        return 0


    def wait_for_answer(self):
        """ Parent checks if anything has 'arrived' through
        the pipe and acts accordingly """
        while True:
            self.show_win()
            self.animcursor.update()

            status = self.check_keys()
            if status == -100:   # stopped and ended by user
                self.ret = -100, 'stopped_by_user'
                return -1
            elif status == 1:    #stopped and continued by user
                continue

            #Check what  child sent to parent
            (code, buf) = self.c2p.receive()
            if code == 1:
                ans, result = buf
                if ans == 'error':
                    wcall.err_parent(self.action, result)
                    return 0
                elif ans == 'result':
                    return self.process_response(result)
                    #ret = self.process_response(result)
                    #if ret == 1:
                        #continue
                    #else:
                        #return ret
                elif ans == 'copysize':
                    self.cur_total_size = result
                elif ans == 'current':
                    self.dest_file = result[0]
                    self.src_file = result[1]
                    self.cur_source_size = files.get_size_lstat(result[1])
                else:
                    self.ret = buf
                    return 0            #happens when search or vfs is done
            elif code == -1:
                wcall.err_parent_transport(self.action, buf)
                return 0


    def initilize_child(self):
        """Open child->parent pipe and create child process"""
        self.c2p = IPC()
        self.pid_child = os.fork()  # fancy function
                                    # returns 0 in child and non zero in parent!
        if self.pid_child < 0:
            wcall.err_run_func(self.action)
            return
        elif self.pid_child == 0:
            os.setpgid(0, 0)
            self.child_process()



    def child_process(self):
        """Execute child command and send result to pipe"""
        res = self.func(*self.args)
        self.c2p.send((res))
        os._exit(0)

    def close_child_and_gui(self):
        """Close pipe and end dialog"""
        self.c2p.close()
        try:
            os.wait()
        except OSError:
            pass
        self.end_gui()

    def run(self):
        """Start child and parent processes"""

        # start child
        self.initilize_child()

        # start parent
        self.wait_for_answer()

        # parent decided to quit, close child
        self.close_child_and_gui()
        self.show_parent()
        return self.ret

    def process_response(self, result):
        """Process response"""
        self.ret.append(result)
        return 0

    def ask_confirmation(self):
        """Virtual method; always yes by default"""
        return 1

    def with_gui(self):
        """Virtual method; by default run with the dialog shown"""
        return 1


######################################################################
##### Process Base Loop
# This class manages two-way interaction:
# 1. child -> parent (inherited from ProcessFunc)
# 2. parent-> child (implemeted below)
class ProcessBaseLoop(ProcessFunc):

    def __init__(self, app, action = '', func = None, lst = [], *args):

        self.lst = lst
        self.file_i, self.filename =0, ''
        self.length = len(lst)
        ProcessFunc.__init__(self,app, action, '', func, *args)

    def init_gui(self):
        if self.with_gui():
            self.dlg = wcall.win_progress()
            self.dlg.pwin.window().nodelay(1)

    def show_win(self):
        if self.with_gui():
            if self.dlg.pwin.hidden():
                self.dlg.pwin.show()
            title = self.action + ' %d/%d' % (self.file_i+1, self.length)
            percent = 100 * (self.file_i+1)/self.length
            self.dlg.show(title, self.filename, 'Press Esc to stop', percent)


    def run(self):
        self.p2c = IPC()        # init parent
        self.initilize_child()  # init child

        #launch child execution


        for self.file_i, self.filename in enumerate(self.lst):
            ret = self.ask_confirmation()
            if ret == -1:
                break
            elif ret == 0:
                continue
            args = self.prepare_args()
            self.p2c.send(('exec', args))


            if self.wait_for_answer() ==-1:
                break

        # finish parent and child
        self.p2c.send(('quit', None))
        self.p2c.close()
        self.close_child_and_gui()
        return self.ret

    def child_process(self):
        while True:
            # wait for command from parent to execute
            while True:
                code, buf = self.p2c.receive()
                # the command arrived through the pipe
                if code == 1:
                    break
                elif code == -1:
                    self.c2p.send(('error', 'Child: ' + buf))

            cmd, args = buf
            if cmd == 'quit':
                break
            elif cmd == 'exec':
                res = self.func(*args)
                if res != 'empty':
                    self.c2p.send(('result', res))
            else:
                result = ('error', 'Child: Bad command from parent')
                self.c2p.send(('result', result))

        #time.sleep(.25) # time to let parent get return value
        os._exit(0)
