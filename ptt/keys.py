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
