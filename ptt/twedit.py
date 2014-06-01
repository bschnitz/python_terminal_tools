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
import termios

from twin import TWin
from keys import Keys, ansi
from eline import EditLine

class TWEdit(TWin):
  def __init__( self, x = None, y = None, width = None ):
    self.map_keys()
    self.line = EditLine("")
    self.cursor_x = 1
    self.quit_loop = False
    self.debug = False
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


  def quit( self, key ):
    self.quit_loop = True
    self.quit_value = self.line.get_line()

  def write_char( self, key ):
    self.line.insert_before_cursor( key )
    x, y, width, height = self.get_inner_dimensions()
    if self.cursor_x == width:
      self.cursor_x = int(width/2)
      chars_around_cursor = self.line.xcx( self.cursor_x, width )
      self.replace_to_right( chars_around_cursor, 1 )
    else:
      chars_around_cursor = self.line.xcx( 1, width-self.cursor_x+1 )
      sys.stdout.write( chars_around_cursor )
    self.cursor_x += 1

  def move_left( self, key ):
    num_chars_moved = self.line.move_cursor_left(1)
    if num_chars_moved > 0:
      if self.cursor_x > num_chars_moved:
        self.cursor_x -= num_chars_moved
      else:
        x, y, width, height = self.get_inner_dimensions()
        chars_around_cursor = self.line.xcx( int(width/2), width )
        self.replace_to_right( chars_around_cursor, 1 )
        self.cursor_x = self.line.nchars_before_cursor( int(width/2) ) + 1

  def move_right( self, key ):
    num_chars_moved = self.line.move_cursor_right(1)
    if num_chars_moved > 0:
      x, y, width, height = self.get_inner_dimensions()
      if self.cursor_x < width:
        self.cursor_x += 1
      else:
        chars_around_cursor = self.line.xcx( int(width/2), width )
        self.replace_to_right( chars_around_cursor, 1 )
        self.cursor_x = self.line.nchars_before_cursor( int(width/2) ) + 1

  def move_to_start( self, key ):
    x, y, width, height = self.get_inner_dimensions()
    if self.cursor_x-1 < self.line.xpos():
      self.replace_to_right( self.line[0:width], 1 )
    self.line.move_at(0)
    self.cursor_x = 1

  def move_to_end( self, key ):
    x, y, width, height = self.get_inner_dimensions()
    num_chars_moved = self.line.move_at(-1)
    if num_chars_moved > (width - self.cursor_x):
      self.cursor_x = int(width/2)
      self.replace_to_right( self.line.xcx( self.cursor_x-1 ), 1 )
    else:
      self.cursor_x += num_chars_moved

  def del_at( self, key ):
    num_chars_deleted = self.line.delete_at_cursor(1)
    if num_chars_deleted > 0:
      self.move_xy( self.cursor_x, 1 )
      self.replace_to_right( self.line.xcx(0) )

  def del_left( self, key ):
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
    self.move_xy( 1, 1 )
    self.flush()
    while not self.quit_loop:
      key = self.getch()
      self.process_key(key)
      self.flush()
    return self.quit_value

  def process_key( self, key ):
    if key in self.keymap: rval = self.keymap[key]( key )
    else:                  rval = self.keymap['default']( key )
    self.move_xy( self.cursor_x, 1 )
    self.flush()
    if self.debug:
      self.move_write_xy(1, -1, " Line: %3d " % self.line.cursor_x)
      self.move_write_xy(1,  0, " Edit: %3d " % self.cursor_x)
      self.move_xy( self.cursor_x, 1 )
    return rval

if __name__ == "__main__":
  x, y = TWEdit.get_xy()
  with TWEdit( 4, y ) as edit:
    edit.event_loop()
  print()
