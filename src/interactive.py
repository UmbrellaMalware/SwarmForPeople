# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA.
import fcntl
import os
import pty
import socket
import sys
from paramiko.py3compat import u

# windows does not have termios...
try:
    import termios
    import tty

    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan, start_command):
    if has_termios:
        master, slave = pty.openpty()

    posix_shell(chan, start_command=start_command)


def posix_shell(chan, start_command=None):
    import select
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    try:
        tty.setraw(fd)
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        tty.setcbreak(fd)
        chan.settimeout(0.0)
        if start_command is not None:
            chan.send(start_command)
        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = chan.recv(1024)
                    if len(x) == 0:
                        sys.stdout.write("\r\n*** EOF\r\n")
                        break
                    sys.stdout.buffer.raw.write(x)
                    sys.stdout.buffer.raw.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.buffer.raw.read(1024)
                if len(x) == 0:
                    break
                chan.send(x)

    finally:
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
