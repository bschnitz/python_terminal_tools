#!/usr/bin/env python3

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
