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

from term.terminal import Term

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
              if width < 0: width = terminal_width - width - y + 1
      height: number of rows window will span
              if height = None: width = terminal_heigth - x + 1
              if height < 0: height = terminal_width - height - x + 1
    """
    self.x = x
    self.y = y

    tsize = super(TWin, self).get_size()

    if x == None or y == None or x<0 or y<0:
      xy = self.get_xy()

      if x == None: self.x = xy[0]
      elif x < 0: self.x = tsize[0] + x

      if y == None: self.y = xy[1]
      elif y < 0: self.y = tsize[1] + y

    if width  == None: width  = tsize[0] - self.x + 1
    if height == None: height = tsize[1] - self.y + 1

    if width < 0:  width  = max( tsize[0] + width  - self.x + 1, 0 )
    if height < 0: height = max( tsize[1] + height - self.y + 1, 0 )
     
    self.width = width
    self.height = height

    self.tbc = None # top border character
    self.bbc = None # bottom border character
    self.lbc = None # left border character
    self.rbc = None # right border character

    self.tlc = None # top left corner character
    self.trc = None # top right corner character
    self.blc = None # bottom left corner character
    self.brc = None # bottom right corner character

  def resize( self, width = None, height = None ):
    tsize = super(TWin, self).get_size()

    if width  == None: width  = tsize[0] - self.x + 1
    if height == None: height = tsize[1] - self.y + 1

    if width  < 0: width  = max( tsize[0] + width  - self.x + 1, 0 )
    if height < 0: height = max( tsize[1] + height - self.y + 1, 0 )
     
    self.width = width
    self.height = height

  def move( self, x = None, y = None ):
    self.x = x
    self.y = y

    tsize = super(TWin, self).get_size()

    if x == None or y == None or x<0 or y<0:
      xy = self.get_xy()

      if x == None: self.x = xy[0]
      elif x < 0: self.x = tsize[0] + x

      if y == None: self.y = xy[1]
      elif y < 0: self.y = tsize[1] + y

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

  def set_border_top_left( self, character ):
    """ Set the top left corner of the window to character

    Args:
      character: character to display in the corner

    .. note::
    · will have no effect, if the window does not have a top or a left border
    """
    self.tlc = character

  def set_border_top_right( self, character ):
    """ Set the top left corner of the window to character

    Args:
      character: character to display in the corner

    .. note::
    · will have no effect, if the window does not have a top or a right border
    """
    self.trc = character

  def set_border_bottom_left( self, character ):
    self.blc = character

  def set_border_bottom_right( self, character ):
    self.brc = character

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

  def set_border_right( self, character ):
    self.rbc = character

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

      if (self.tbc != None or self.rbc != None) and self.trc != None:
        self.move_write_xy( remaining_cols, line, self.trc, True )

      if (self.tbc != None or self.lbc != None) and self.tlc != None:
        self.move_write_xy( 1, line, self.tlc, True )

      if self.tbc != None and remaining_lines > 0:
        self.move_write_xy( 2, line, self.tbc * (remaining_cols-2), True )
        remaining_lines -= 1
        line += 1


      if self.bbc != None: remaining_lines -= 1

      while remaining_lines > 0:
        if self.lbc != None:
          self.move_write_xy( 1, line, self.lbc, True )
        if self.rbc != None:
          self.move_write_xy( remaining_cols, line, self.rbc, True )
        remaining_lines -= 1
        line = line+1

      if self.bbc != None and remaining_lines > -1:
        self.move_write_xy( 2, line, self.bbc * (remaining_cols-2), True )

      if (self.bbc != None or self.lbc != None) and self.blc != None:
        self.move_write_xy( 1, line, self.blc, True )

      if (self.bbc != None or self.rbc != None) and self.brc != None:
        self.move_write_xy( remaining_cols, line, self.brc, True )

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

  def list( self, items, item_sep, max_num_cols=-1 ):
    """ write the strings in items into the window

    This function will print the strings inside items into the interior of the
    window. The items will be arranged in a grid (just like it is done by the
    shell command 'ls' by default). There will only be as much items listed, as
    one can fit the interior of the window (when using the 'ls' display method).
    The items will be inserted into the grid column by column from left to
    right. The columns of the grid will be seperated by item_sep.

    Args:
        max_num_cols:
            This is the maximum number of columns to be created in the grid. If
            this is negative, as many columns as fitting into the window will be
            created.

    """
    x, y, width, height = self.get_inner_dimensions()

    if width == 0 or height == 0: return

    # create the lines to print column by column, until a line becomes to long
    i = 0
    lines = [""]*height
    max_line_len_prev = 0
    max_line_len_curr = 0
    for item in  items:
      if max_num_cols == 0: break
      format = "%-" + str(max_line_len_prev) + "s"
      line = (format % lines[i%height])
      if i >= height: line += item_sep
      line += item

      max_line_len_curr = max( max_line_len_curr, len(line) )
      if max_line_len_curr > width: break

      lines[i%height] = line

      i += 1
      if i % height == 0:
        max_line_len_prev = max_line_len_curr
        max_num_cols -= 1


    for i in range(len(lines)):
      format = "%-" + str(width) + "s"
      line = format % lines[i]
      self.move_write_xy( 1, i+1, line )
  

if __name__ == "__main__":
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
