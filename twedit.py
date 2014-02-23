#!/usr/bin/env python3

import os
import sys
import termios
from term import Term

from keys import Keys, ansi
from twin import TWin

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

  def quit( self, key ):
    self.quit_loop = True

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
    #self.move_write_xy(1, -1, str(self.line_x))
    #self.move_write_xy(1,  0, str(self.cursor_x))
    #self.move_xy( self.cursor_x, 1 )
    #self.flush()
    return rval

if __name__ == "__main__":
  x, y = Term.get_xy()
  with Edit( 4, y ) as edit:
    edit.event_loop()
  print()
  #edit.set_border_top("#")
  #edit.draw()


  #print( win.get_inner_dimensions() )
  #print( win.get_size() )
