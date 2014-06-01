#!/usr/bin/env python3

# Copyright 2014 Benjamin Schnitzler <benjaminschnitzler@googlemail.com>

# This file is part of 'Python Terminal Tools'
# 
# 'Python Terminal Tools' is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# 'Python Terminal Tools' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# 'Python Terminal Tools'. If not, see <http://www.gnu.org/licenses/>.

import os
import select
import sys
import termios

class Keyboard:
  ESCAPE = 27
  LEFT = 1000
  RIGHT = 1001
  DOWN = 1002
  UP = 1003

  keylist = {
    b'\x1b'   : ESCAPE,
    b'\x1b[A' : UP,
    b'\x1b[B' : DOWN,
    b'\x1b[C' : RIGHT,
    b'\x1b[D' : LEFT,
  }

  def __init__(self):
    self.fd = sys.stdin.fileno()
    self.old = termios.tcgetattr(self.fd)
    self.new = termios.tcgetattr(self.fd)
    self.new[3] = self.new[3] & ~termios.ICANON & ~termios.ECHO
    self.new[6][termios.VMIN] = 1
    self.new[6][termios.VTIME] = 0
    termios.tcsetattr(self.fd, termios.TCSANOW, self.new)

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old)

  def getFile(self):
    return self.fd

  def read(self):
    keys = os.read(self.fd, 4)
    if keys in Keyboard.keylist:
      return Keyboard.keylist[keys]
    else:
      return 0

if __name__ == "__main__":
  with Keyboard() as keyboard:
    key = keyboard.read()
    while key != Keyboard.ESCAPE:
      print('%d' % key)
      key = keyboard.read()
