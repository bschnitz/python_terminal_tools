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

  def move_xy( self, x, y, ignore_border=False ):
    x_off = -1
    y_off = -1
    if ignore_border == False:
      if self.lbc != None: x_off += 1
      if self.tbc != None: y_off += 1

    super(TWin, self).move_xy( self.x+x+x_off, self.y+y+y_off )

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
    self.move_xy( x, y, ignore_border )
    sys.stdout.write(line)
  
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

class Edit(TWin):
  def __init__( self, x = None, y = None, width = None ):
    self.map_keys()
    self.line_x = 0
    self.cursor_x = 1
    self.quit_loop = False
    self.line = None
    super(Edit, self).__init__( x, y, width, 1 )

  def map_keys(self):
    self.keymap = {}
    self.keymap[ansi[ Keys.ESC   ]] = self.quit
    self.keymap[ansi[ Keys.BS1   ]] = self.del_left
    self.keymap[ansi[ Keys.BS2   ]] = self.del_left
    self.keymap[ansi[ Keys.DEL   ]] = self.del_at
    self.keymap[ansi[ Keys.LEFT  ]] = self.move_left
    self.keymap[ansi[ Keys.RIGHT ]] = self.move_right
    self.keymap[ansi[ Keys.HOME  ]] = self.move_to_start
    self.keymap[ansi[ Keys.END   ]] = self.move_to_end

    self.keymap['default']          = self.write_char

  def quit( self, key ): self.quit_loop = True

  def write_char( self, key ):
    if self.line == None: self.line = ""

    self.line = self.line[0:self.line_x] + key + self.line[self.line_x:]
    x, y, width, height = self.get_inner_dimensions()
    if self.cursor_x == width:
      self.cursor_x = int(width/2)
      from_right = self.cursor_x + (len(self.line) - self.line_x - 1)
      self.replace_to_right( self.line[-from_right:], 1, width )
    else:
      self.move_xy( self.cursor_x, 1 )
      max_num_chars = min( len(self.line), width-self.cursor_x )
      sys.stdout.write( self.line[self.line_x:self.line_x+max_num_chars] )
      self.move_xy( self.cursor_x+1, 1 )
    self.cursor_x += 1
    self.line_x += 1
    sys.stdout.flush()

  def move_left( self, key ):
    if self.cursor_x > 1:
      self.move_xy( self.cursor_x-1, 1 )
      self.line_x -= 1
      self.cursor_x -= 1
    elif self.line_x > 0:
      x, y, width, height = self.get_inner_dimensions()
      self.line_x -= 1
      self.cursor_x = min( int(width/2), self.line_x+1 )
      line_start = max( 0, self.line_x - self.cursor_x + 1 )
      self.replace_to_right( self.line[line_start:], 1 )
    sys.stdout.flush()

  def move_right( self, key ):
    x, y, width, height = self.get_inner_dimensions()
    if self.cursor_x < width and self.line_x < len(self.line):
      self.move_xy( self.cursor_x+1, 1 )
      self.line_x += 1
      self.cursor_x += 1
    elif self.line_x < len(self.line):
      self.line_x += 1
      self.cursor_x = int(width/2)
      line_start = self.line_x - self.cursor_x + 1
      self.replace_to_right( self.line[line_start:], 1 )

  def move_to_start( self, key ):
    if self.cursor_x-1 < self.line_x:
      self.replace_to_right( self.line, 1 )
    self.cursor_x = 1
    self.line_x   = 0

  def move_to_end( self, key ):
    x, y, width, height = self.get_inner_dimensions()
    if (len(self.line) - self.line_x) > (width - self.cursor_x):
      self.cursor_x = int(width/2)
      line_start = self.line_x - self.cursor_x + 1
      self.replace_to_right( self.line[line_start:], 1 )
      self.line_x = len(self.line)

  def del_at( self, key ):
    if self.line_x < len(self.line):
      self.move_xy( self.cursor_x, 1 )
      self.line = self.line[:self.line_x] + self.line[self.line_x+1:]
      self.replace_to_right( self.line[self.line_x:] )
      sys.stdout.flush()

  def del_left( self, key ):
    if self.cursor_x > 1:
      self.move_left( key )
      self.del_at( key )

  def replace_to_right( self, replacement = "", x = None, num_chars = None ):
    """ replaced a part of the interior of the Edit Window

    Args:
      x:  replacement starts here (x is relative to the start of the window
          the first character of the edit window has position 1)
          if x = None, x will default to the current x-Pos of the cursor.

      num_chars:
          number of characters to replace in the edit window; if num_chars is
          greater than the windows interior size, the replacement will stop in
          the last column of the interior of the window if num_chars == None:
          everything starting from x to the end of the interior of the window
          will be replaced.

      replacment:
          The string to use as replacement. If is is shorter than num_chars, the
          remaining space will be filled with blanks, if it is larger than the
          remaining width from x to the end of the interior of the window, only
          as much characters, beginning from the start of replacement, as
          fitting will be written into the window.

    .. note ::
      After deletion cursor will be repositioned to the first character of
      replacement, if existing, or otherwise to the first character left to x
      if x != None or otherwise to the first character left to self.cursor_x, if
      existing, or otherwise to the start of the edit window.
    """
    win_x, win_y, width, height = self.get_inner_dimensions()

    if x != None: self.move_xy( x, 1 )
    else:         x = self.cursor_x

    if num_chars != None: num_chars = min( num_chars - x + 1, width - x + 1 )
    else:                 num_chars = width - x + 1

    sys.stdout.write( ("%-"+str(num_chars)+"s") % replacement[0:num_chars] )

    # relocate cursor
    if replacement != "":
      self.move_xy( x, 1 )
      return x
    elif x > 1:
      self.move_xy( x-1, 1 )
      return x-1
    else:
      self.move_xy( 1, 1 )
      return 1

  def change_filedescriptor_settings(self, filedescriptor):
    fd_settings = termios.tcgetattr(filedescriptor)
    fd_settings[3] = fd_settings[3] & ~termios.ICANON & ~termios.ECHO
    fd_settings[6][termios.VMIN]  = 1
    fd_settings[6][termios.VTIME] = 0
    termios.tcsetattr(filedescriptor, termios.TCSANOW, fd_settings)

  def __enter__(self):
    self.fd = sys.stdin.fileno()
    self.saved_fd_settings = termios.tcgetattr(self.fd)
    self.change_filedescriptor_settings(self.fd)
    return self

  def __exit__(self, type, value, traceback):
    termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.saved_fd_settings)

  def getch(self):
    return os.read(self.fd, 4).decode('utf-8')

  def event_loop( self ):
    self.move_xy( self.cursor_x, y )
    sys.stdout.flush()
    while not self.quit_loop:
      key = self.getch()
      self.process_key(key)
    return self.line

  def process_key( self, key ):
    if key in self.keymap: rval = self.keymap[key]( key )
    else:                  rval = self.keymap['default']( key )
    self.move_write_xy(1, -1, str(self.line_x))
    self.move_write_xy(1,  0, str(self.cursor_x))
    self.move_xy( self.cursor_x, 1 )
    self.flush()
    return rval




#term = Term()
#response = term.query("\033[6n", "R")
#print(response[1:], end="")
#term.erase_line()
#term.move_xy(0,0)
#print( term.get_xy() )
#x = term.get_xy()[0]
#print("\n" * 6)
#y = term.get_xy()[1]
#term.move_xy( x, y-7 )
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
    Term.move_xy( 2, y-1)
    sys.stdout.flush()
    char = Term.get_char_raw()
    while char != "q":
      win.draw()
      win.list( [ "hallo", "welt", "ich", "bin", "ein",
                  "sehr", "schöner", "Mensch", "ohne", "Makel" ], "  " )
      Term.move_xy( 2, y-1)
      sys.stdout.flush()
      char = Term.get_char_raw()
    Term.move_xy( 1, y+(win_h-1))
  print()

x, y = Term.get_xy()
with Edit( 4, y ) as edit:
  edit.event_loop()
print()
#edit.set_border_top("#")
#edit.draw()


#print( win.get_inner_dimensions() )
#print( win.get_size() )
