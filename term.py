#!/usr/bin/env python3

import sys
import tty
import fcntl
import struct
import termios

class Term:
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
  def scroll_clear():
    """ Add new lines, until the line below the cursor is the Terminals top line
    """
    x, y = Term.get_xy()
    w, h = Term.get_size()
    print("\n")
    clear = " "*w
    print(clear*(h-x-2))

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
