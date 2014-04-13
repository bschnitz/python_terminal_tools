#!/usr/bin/env python3

import os
import sys
import tty
import fcntl
import struct
import termios

class Keys:
  ESC   = 1
  BS1   = 2
  BS2   = 3
  DEL   = 3
  UP    = 4
  DOWN  = 5
  LEFT  = 6
  RIGHT = 7
  HOME  = 8
  END   = 9

ansi = {}
ansi[ Keys.ESC   ] = '\033'
ansi[ Keys.BS1   ] = '\x7f'
ansi[ Keys.BS2   ] = '\x08'
ansi[ Keys.DEL   ] = '\033[3~'
ansi[ Keys.UP    ] = '\033[A'
ansi[ Keys.DOWN  ] = '\033[B'
ansi[ Keys.RIGHT ] = '\033[C'
ansi[ Keys.LEFT  ] = '\033[D'
ansi[ Keys.HOME  ] = '\033[7~'
ansi[ Keys.END   ] = '\033[8~'
