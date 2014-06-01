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
from ptt.twin import TWin
from ptt.terminal import Term

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
