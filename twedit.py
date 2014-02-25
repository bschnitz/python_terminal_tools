#!/usr/bin/env python3

import os
import sys
import termios

from twin import TWin
from keys import Keys, ansi

class EditLine:
  def __init__( self, line="" ):
    self.line = line
    self.cursor_x = len(line)

  def insert_before_cursor( self, string ):
    self.line = self.line[0:self.cursor_x] + string + self.line[self.cursor_x:]
    self.cursor_x += len(string)

  def delete_before_cursor( self, num_chars ):
    """ deletes min(num_chars, number of characters before cursor) before cursor
        position and returns how many characters were deleted.
    """
    if num_chars > self.cursor_x: num_chars = self.cursor_x
    self.line = self.line[0:self.cursor_x-num_chars] + self.line[self.cursor_x:]
    self.cursor_x -= num_chars
    return num_chars

  def delete_from_cursor_to_end( self, num_chars ):
    """ deletes min(num_chars, number of characters after cursor) after cursor
        position and returns how many characters were deleted.
    """
    if num_chars > len(self.line) - self.cursor_x:
      num_chars = len(self.line) - self.cursor_x
    self.line = self.line[0:self.cursor_x] + \
                self.line[self.cursor_x + num_chars:]
    return num_chars

  def get_cursor_x( self ): return self.cursor_x

  def get_nchars_from_cursor_to_end( self ):
    """ Get the number of characters counted from the current cursor position to
        the end of the line.
    """
    return len(self.line) - self.cursor_x

  def get_nchars_before_cursor( self ):
    """ Get the number of characters before the cursor.
    """
    return self.cursor_x

  def get_line_before_cursor( self, num_chars )
    """ return at most min( num_chars, number of characters before cursor )
        characters in the line, before the cursor position.
    """
    num_chars = min( self.cursor_x, num_chars )
    return self.line[ self.cursor_x-num_chars:self.cursor_x ]


  def get_line_from_cursor_to_right( self, num_chars=None ):
    """ Get num_chars from and including the character at cursor position to the
        right; if num_chars = None: return all characters from and including the
        one at the cursor position to the right. if 
    """
    return self.line[self.cursor_x:]

  def move_cursor_right( self, num_chars ):
    """ moves the cursor min( num_chars, self.get_nchars_from_cursor_to_end() )
        characters to the right.
    """
    self.cursor_x += min( num_chars, self.get_nchars_from_cursor_to_end() )

  def move_cursor_left( self, num_chars )
    """ moves the cursor min( num_chars, self.get_nchars_before_cursor() )
        characters to the left. Returns how many characters the cursor was
        moved
    """
    num_chars = min( num_chars, self.get_nchars_before_cursor() )
    self.cursor_x -= num_chars
    return num_chars

  def get_length( self ): return len(self.line)



class TWEdit(TWin):
  def __init__( self, x = None, y = None, width = None ):
    self.map_keys()
    self.line = EditorLines("")
    self.cursor_x = 1
    self.quit_loop = False
    super(TWEdit, self).__init__( x, y, width, 1 )

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
    self.line.insert_before_cursor( key )
    x, y, width, height = self.get_inner_dimensions()
    if self.cursor_x == width:
      self.cursor_x = int(width/2)
      characters_after_cursor = self.line.get_line_from_cursor_to_right(width)
      self.replace_to_right( characters_after_cursor, 1, width)
    else:
      self.move_xy( self.cursor_x, 1 )
      max_num_chars = min( self.line.get_length(), width-self.cursor_x )
      sys.stdout.write( self.line.get_line_from_cursor_to_right(max_num_chars) )
      self.move_xy( self.cursor_x+1, 1 )
    self.cursor_x += 1
    sys.stdout.flush()

  def move_left( self, key ):
    num_chars_moved = self.line.move_cursor_left(1)
    if self.cursor_x > num_chars_moved:
      self.move_xy( self.cursor_x-num_chars_moved, 1 )
      self.line.move_left()
      self.cursor_x -= 1
    elif num_chars_moved > 0:
      x, y, width, height = self.get_inner_dimensions()
      chars_before_cursor = self.line.get_line_before_cursor( width/2 )
      self.cursor_x = len(chars_before_cursor)
      self.replace_to_right( chars_before_cursor, 1 )
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
    else:
      from_back    = len(self.line) - self.line_x
      to_beginning = from_back + self.cursor_x - 1
      self.cursor_x = to_beginning + 1
      self.line_x   = len(self.line)
      self.move_xy( self.cursor_x, 1 )

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


if __name__ == "__main__":
  x, y = TWEdit.get_xy()
  with TWEdit( 4, y ) as edit:
    edit.event_loop()
  print()
