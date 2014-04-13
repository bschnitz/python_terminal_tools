#!/usr/bin/env python3

class EditLine():
  def __init__( self, line ):
    self.cursor_x = 0
    self.line = line

  def xcx( self, before, num_chars=None ):
    """ Get a slice of the line, around the cursor position

    Args:
        before:
            Start at most <before> characters before the cursor. If there
            aren't that many characters before the cursor, start at 0.
        num_chars: 
            Get at most <num_chars> characters. If there aren't that many
            characters after the start position - determined by <before> -, or
            if <num_chars> equals None get all characters from the start
            position until the end of the line.
    """
    start = max( self.cursor_x - before, 0 )
    end   = None if num_chars == None else start+num_chars
    return self.line[ start : end ]

  def nchars_before_cursor( self, max_num_chars ):
    """ returns how many characters are before the cursor, but at most
        max_num_chars
    """
    return min( self.cursor_x, max_num_chars )

  def move_at( self, x ):
    """ Move cursor at <x>.

    Args:
        x:  If <x> is negative, start moving from the left, where the index of
            the leftmost character is -2 (so <x> == -1 moves the cursor one
            character behind the end of the line)

    Returns the number of characters, the cursor was actually moved. The return
    value is negative, if the cursor was moved to the left, 0 if the cursor was
    not moved and otherwise positive.
    """
    if x >= 0: num_chars_moved = x                      - self.cursor_x
    else:      num_chars_moved = len(self.line) + x + 1 - self.cursor_x
    self.cursor_x += num_chars_moved
    return num_chars_moved

  def xpos( self ):
    return self.cursor_x

  def __getitem__( self, at ):
    return self.line[at]

  def insert_before_cursor( self, string ):
    self.line = self.line[0:self.cursor_x] + string + self.line[self.cursor_x:]
    self.cursor_x += len(string)

  def delete_at_cursor( self, num_chars ):
    """ deletes min(num_chars, number of characters from cursor to end) from the
        position to the right and returns how many characters were deleted.
    """
    num_chars = min( num_chars, len(self.line) - self.cursor_x )
    self.line = self.line[0:self.cursor_x] + \
                self.line[self.cursor_x + num_chars:]
    return num_chars

  def move_cursor_right( self, num_chars ):
    """ moves the cursor min(num_chars, number of characters from cursor to end)
        characters to the right. Returns how many characters the cursor was
        actually moved.
    """
    num_chars = min( num_chars, len(self.line) - self.cursor_x )
    self.cursor_x += num_chars
    return num_chars

  def move_cursor_left( self, num_chars ):
    """ moves the cursor min( num_chars, number of characters before cursor )
        characters to the left. Returns how many characters the cursor was
        actually moved.
    """
    num_chars = min( num_chars, self.cursor_x )
    self.cursor_x -= num_chars
    return num_chars

  def get( self ):
    return self.line
