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

import sys
import tty
import fcntl
import struct
import termios

class Term:
  sgr_map = {
      'bold':'1',
      'b':'1',
      'underline':'4',
      'underlined':'4',
      'u':'4',
  }

  @staticmethod
  def query( sequence, end ):
    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)

    # Set stdin to raw mode; this means, that the app can and must process all
    # I/O; it is necessary to intercept the response to the query from the
    # terminal
    tty.setraw(fd)
 
    # Send query
    sys.stdout.write("\033[6n")

    # prevent our query from beeing blocked
    sys.stdout.flush()

    elen = len(end);

    # Read response one character at a time until end occeurs in the response
    response = ""
    try:
      while len(response) < elen or response[-elen:] != end:
        response += sys.stdin.read(1)
    finally:
      # Restore previous stdin configuration
      termios.tcsetattr(fd, termios.TCSADRAIN, settings)

    return response

  @staticmethod
  def get_char_raw():
    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)

    tty.setraw(fd)

    try:
      char = sys.stdin.read(1)
    finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, settings)

    return char

  @staticmethod
  def erase_line():
    sys.stdout.write("\033[2J")

  @staticmethod
  def sgr_esc(text, *flags, **params):
    escape = ""
    for flag in flags: escape += "\033["+Term.sgr_map[flag]+"m"
    if 'fg' in params: escape += "\033[38;5;"+str(params['fg'])+"m"
    if 'bg' in params: escape += "\033[48;5;"+str(params['bg'])+"m"
    for flag in params.get('flags', ''): escape +="\033["+Term.sgr_map[flag]+"m"
    return escape + text + params.get( 'reset', "\033[0m" )

  @staticmethod
  def move_xy(x, y):
    if x <= 0 or y <= 0:
      w, h = Term.get_size()
      if x <= 0: x = max( w+x, 0 )
      if y <= 0: y = max( h+x, 0 )
    sys.stdout.write( "\033[%d;%dH" % (y, x) )

  @staticmethod
  def get_xy():
    pos = Term.query("\033[6n", "R")
    return [int(x) for x in reversed(pos[2:-1].split(";"))]

  @staticmethod
  def get_size(fd=1):
    """ Get width and height of terminal window

    Args:
      fd: the filedescriptor to use (defaults to stdout)
    """
    hw = struct.unpack( 'hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234') )
    return ( hw[1], hw[0] )

  @staticmethod
  def move_write_xy( x, y, line ):
    """ Move to position (x,y) and print line (no newline will be added)
    """
    Term.move_xy( x, y )
    sys.stdout.write(line)

  @staticmethod
  def flush(): sys.stdout.flush()

  @staticmethod
  def scroll_clear(nlines=None):
    """ Ensure, that at least nlines follow the current cursor position, by
        adding an appropriate number of lines.

        This method will however output no more lines, than the height of the
        terminal in lines.
    """
    x,y = Term.get_xy()
    w,h = Term.get_size()
    nlines = min(nlines, h)
    num_new_lines = y-h+nlines
    sys.stdout.write("\n"*(nlines-1))
    if num_new_lines > 0: Term.move_xy(x,y-num_new_lines+1)
    else:                 Term.move_xy(x,y)

if __name__ == "__main__":
  term = Term()
  x, y = term.get_xy()
  term.move_xy(1,1)
  term.erase_line()
  print( x, y )
  print( term.get_size() )

  char = term.get_char_raw()
  while char != "q":
    print(char, end="")
    sys.stdout.flush()
    char = term.get_char_raw()

  term.move_xy( x, y )
