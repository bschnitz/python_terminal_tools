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

  """ When using get_control_char and reading <ESC> we must also read the
      next character, to determine, if we read <ESC> or another control
      character. If it was just <ESC>, we must store the next character and
      provide it when the next invokation of get_char_raw/get_control_char is
      done.
  """
  last_char = None
  @staticmethod
  def get_char_raw():
    if Term.last_char != None:
      char = Term.last_char
      Term.last_char = None
      return char

    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)

    tty.setraw(fd)

    try:
      char = sys.stdin.read(1)
    finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, settings)

    return char

  @staticmethod
  def get_control_char():
    char = Term.get_char_raw()
    if char == "":
      next_char = Term.get_char_raw()
      if next_char != [3~:q
      Term.last_char = Term.get_char_raw()
      return "a"
      #if next != "[":
      #  sys.stdout.write(next)
    else:
      return char

  @staticmethod
  def erase_line():
    sys.stdout.write("\033[2J")

  @staticmethod
  def move_cursor(x, y):
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
    Term.move_cursor( x, y )
    print( line, end="" )

class TWin(Term):
  def __init__( self, x = None, y = None, width = None, height = None ):
    """ Initialize a Terminal Window (TWin) Object
    Args:
      x: Column in which the top left edge of the window is located
         if x = None, x will default to the x-Pos of the cursor
      y: Row    in which the top left edge of the window is located
         if y = None, x will default to the y-Pos of the cursor

      width:  number of columns window will span
              if width = None: width = terminal_width - y + 1
      height: number of rows window will span
              if height = None: width = terminal_heigth - x + 1
    """
    self.x = x
    self.y = y
    if x == None or y == None: xy = self.get_xy()
    if x == None:              self.x = xy[0]
    if y == None:              self.y = xy[1]

    if width  == None or height == None: tsize = super(TWin, self).get_size()
    if width  == None:                   width  = tsize[0] - self.x + 1
    if height == None:                   height = tsize[1] - self.y + 1

    self.width = width
    self.height = height

    self.tbc = None # top border character
    self.bbc = None # bottom border character
    self.lbc = None # left border character
    self.rbc = None # right border character

  def set_border_top( self, character ):
    """ Set the top border for the window

    Args:
      character: character to use for the border at the top of the window

    .. note::
    · The top border does not include the left and right edges
    · The space of the border will take space of the window's height.
      If the window's height is to small, contents and borders might not be
      displayed.
    """
    self.tbc = character

  def set_border_bottom( self, character ):
    """ Set the bottom border for the window

    Args:
      character: character to use for the border at the bottom of the window

    .. note::
    · The bottom border does not include the left and right edges
    · The space of the border will take space of the window's height.
      If the window's height is to small, contents and borders might not be
      displayed.
    """
    self.bbc = character

  def set_border_left( self, character ):
    """ Set the left border for the window

    Args:
      character: character to use for the border at the left of the window

    .. note::
    · The left border does not include the top and bottom edges
    · The space of the border will take space of the window's width.
      If the window's height is to small, contents and borders might not be
      displayed.
    """
    self.lbc = character

  def draw( self ):
    """ Draw the window's borders

    .. note ::
      If the window is too large ( considering terminal dimensions ) it will be
      clipped off
    """
    term_w, term_h = super(TWin, self).get_size()

    remaining_cols  = min( term_w - self.x + 1, self.width )
    remaining_lines = min( term_h - self.y + 1, self.height )

    if remaining_cols > 0:
      line = 1
      if self.tbc != None and remaining_lines > 0:
        self.move_write_xy( 2, line, self.tbc * (remaining_cols-2), True )
        remaining_lines -= 1
        line += 1

      if self.bbc != None: remaining_lines -= 1

      while remaining_lines > 0:
        if self.lbc != None: self.move_write_xy( 1, line, self.lbc, True )
        remaining_lines -= 1
        line = line+1

      if self.bbc != None and remaining_lines > -1:
        self.move_write_xy( 2, line, self.bbc * (remaining_cols-2), True )

  def move_write_xy( self, x, y, line, ignore_border=False ):
    """ Write into the window

    If ignore_border is false, this function writes into the window at pos
    (x, y) relative to the window's interior top left position (see
    get_inner_dimensions) otherwise borders are ignored and the real window
    dimensions are used. Coordinates start at (1,1). If part of the line lies
    outside of the window's interior, it will be clipped (respectively outside
    the real window dimensions, if ignore_border is True). line must not contain
    newline characters.

    .. todo:: implement clipping
    """
    x_off = -1
    y_off = -1
    if ignore_border == False:
      if self.lbc != None: x_off += 1
      if self.tbc != None: y_off += 1

    super(TWin, self).move_write_xy( self.x+x+x_off, self.y+y+y_off, line )
  
  def get_inner_dimensions( self ):
    """ Get the dimensions of the interior of the window

    The interior of the window is the maximum displayed area of the window,
    without its borders.

    This function will return a list of the form [ x, y, width, height ]
    x and y are the left and top coordinates of the beginning of the interior
    of the window, width, height are the width and the height of the interior
    of the window.
    """
    term_w, term_h = super(TWin, self).get_size()

    x = self.x
    y = self.y
    max_cols  = min( term_w - self.x + 1, self.width )
    max_lines = min( term_h - self.y + 1, self.height )

    if max_cols  == self.width  and self.rbc != None: max_cols  -= 1
    if max_lines == self.height and self.bbc != None: max_lines -= 1

    if self.tbc != None:
      max_lines -= 1
      y += 1

    if self.lbc != None:
      max_cols -= 1
      x += 1

    return [ x, y, max_cols, max_lines ]

  def list( self, items, item_sep ):
    """ write the strings in items into the window

    This function will print the strings inside items into the interior of the
    window. The items will be arranged in a grid (just like it is done by the
    shell command 'ls' by default). There will only be as much items listed, as
    one can fit the interior of the window (when using the 'ls' display method).
    The items will be inserted into the grid column by column from left to
    right. The columns of the grid will be seperated by item_sep.
    """
    x, y, width, height = self.get_inner_dimensions()

    if width == 0 or height == 0: return

    # create the lines to print column by column, until a line becomes to long
    i = 0
    lines = [""]*height
    max_line_len_prev = 0
    max_line_len_curr = 0
    while len(items) > 0:
      format = "%-" + str(max_line_len_prev) + "s"
      line = (format % lines[i%height])
      if i >= height: line += item_sep
      line += items.pop(0)

      max_line_len_curr = max( max_line_len_curr, len(line) )
      if max_line_len_curr > width: break

      lines[i%height] = line

      i += 1
      if i % height == 0: max_line_len_prev = max_line_len_curr


    for i in range(len(lines)):
      format = "%-" + str(width) + "s"
      line = format % lines[i]
      self.move_write_xy( 1, i+1, line )

class Edit(TWin, dict):
  def __init__( self, x = None, y = None, width = None ):
    self.cursor_x = x
    super(Edit, self).__init__( x, y, width, 1 )

  def event_loop( self ):
    while True:
      char = Term.get_control_char()
      if not self.process_character(char): return

  def process_character( self, char ):
    if char == 'q': return False
    if char == "": print("Hello Worlds!")
    self.move_write_xy( self.cursor_x, 1, char )
    self.cursor_x += 1
    sys.stdout.flush()
    return True




#term = Term()
#response = term.query("\033[6n", "R")
#print(response[1:], end="")
#term.erase_line()
#term.move_cursor(0,0)
#print( term.get_xy() )
#x = term.get_xy()[0]
#print("\n" * 6)
#y = term.get_xy()[1]
#term.move_cursor( x, y-7 )
#term.print_hello()

#char = term.get_char_raw()
#while char != "q":
#  print(char, end="")
#  sys.stdout.flush()
#  char = term.get_char_raw()

#print( term.get_size() )

if False:
  win_h = 5
  print("\n" * win_h, end="")
  sys.stdout.flush()
  x, y = Term.get_xy()
  y -= (win_h-1) 
  win = TWin( x, y, None, win_h )
  win.set_border_top( "=" )
  #win.set_border_bottom( "=" )
  win.set_border_left( " " )
  win.draw()
  win.list( [ "hallo", "welt", "ich", "bin", "ein",
              "sehr", "schöner", "Mensch", "ohne", "Makel" ], "  " )
  if True:
    Term.move_cursor( 2, y-1)
    sys.stdout.flush()
    char = Term.get_char_raw()
    while char != "q":
      win.draw()
      win.list( [ "hallo", "welt", "ich", "bin", "ein",
                  "sehr", "schöner", "Mensch", "ohne", "Makel" ], "  " )
      Term.move_cursor( 2, y-1)
      sys.stdout.flush()
      char = Term.get_char_raw()
    Term.move_cursor( 1, y+(win_h-1))
  print()

x, y = Term.get_xy()
edit = Edit( x, y )
edit.event_loop()
#edit.set_border_top("#")
#edit.draw()


#print( win.get_inner_dimensions() )
#print( win.get_size() )
