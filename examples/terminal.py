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
from ptt.terminal import Term

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
