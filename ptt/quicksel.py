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

"""
.. module:: QuickSel
   :platform: Linux
   :synopsis: Quick select terminal menu

   .. moduleauthor:: Benjamin Schnitzler <benjaminschnitzler@googlemail.com>
"""

from term.terminal import Term
from term.twin import TWin
from term.twedit import TWEdit

class QuickSel(TWEdit):
  def __init__( self, selections, x=2, y=None, width=-1, height=5 ):
    if height < 0: height = Term.get_size()[1]+height
    assert( height >= 3 )
    self.scroll_terminal( height )
    super(QuickSel, self).__init__( x, y, width )
    self.selections = selections
    self.sel_win = TWin( self.x, self.y+1, self.width, height-1 )
    self.init_selection_window()

  def __exit__( self, type, value, traceback ):
    super(QuickSel, self).__exit__( type, value, traceback )
    self.sel_win.move_xy( self.sel_win.width-1, self.sel_win.height-1 )
    print()

  def quit( self, key ):
    self.quit_loop = True
    self.quit_value = self.get_selection( 2 )

  def init_selection_window( self ):
    self.sel_win.set_border_top( "=" )
    self.sel_win.set_border_top_left( "=" )
    self.sel_win.set_border_top_right( "=" )
    self.sel_win.draw()
    self.display_selection( 0 )

  def scroll_terminal( self, max_num_lines ):
    """ Outputs as many new lines, as necessary that there are at least
        max_num_lines from the current line to the bottom of the terminal.
        (So this will move the current line at most max_num_lines-1 up.)
        After that the cursor is moved up, as many lines, as the terminal was
        scrolled down.
    """
    xy = Term.get_xy()
    wh = Term.get_size()

    linediff = xy[1] + max_num_lines - 1 - wh[1]
    if( linediff > 0 ):
      Term.move_xy( 1, wh[1] )
      print( (linediff) * "\n", end = "" )
      Term.move_xy( xy[0], xy[1]-max_num_lines+1 )

  def process_key( self, key ):
    self.move_xy( self.cursor_x, 1 )
    super(QuickSel, self).process_key( key )
    self.display_selection()
    self.move_xy( self.cursor_x, 1 )

  def get_selection( self, time=1 ):
    """ Get the selection by using self.selections and the user input

        Args:
            <time>
            Tells when this function is used:
            <time=0>: At initialization -
                      return value is used in display_selection
            <time=1>: After user input  -
                      return value is used in display_selection
            <time=2>: When quitting -
                      return value is used as return value of the key loop
    """
    if time == 0:
      selected = self.selections
    else:
      selected = self.filter_list( self.selections, self.line.get() )
    return selected

  def display_selection( self, time=1 ):
    """ Display the selection retrieved by get_selection() in self.sel_win

        Args:
            <time>
            Tells when this function is used:
            <time=0>: At initialization, before user input
            <time=1>: After user input to update self.sel_win
    """
    self.sel_win.list( self.get_selection( time ), "  " )

  def filter_list( self, list, words ):
    """ Filter <list> with <words>

    Filters all strings from <list>, which contain all of the words from
    the string <words>.
    """
    words = words.split()
    result = []
    for string in list:
      filter_me = False
      for word in words:
        if word not in string:
          filter_me = True
          break
      if not filter_me:
        result.append(string)

    return result

if __name__ == "__main__":
  testlist = [
      "hallo", "welt", "ich", "bin", "ein",
      "sehr", "schöner", "Mensch", "ohne", "Makel"
  ]

  with QuickSel( testlist ) as qsel:
    selected = qsel.event_loop()

  print(selected)
