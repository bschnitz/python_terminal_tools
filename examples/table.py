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
import ptt
from ptt.table import Table

if __name__ == "__main__":
  Table.scroll_clear(12)

  table = Table(3, x=1, height=12)
  table.flush()
  table.set_border_top("═")
  table.set_border_bottom("═")
  #table.set_border_left("║")
  #table.set_border_right("║")
  #table.set_border_top_right("╗")
  #table.set_border_top_left("╔")
  table.set_border_top_right("═")
  table.set_border_top_left("═")
  table.set_border_bottom_left("═")
  table.set_border_bottom_right("═")
  #table.set_border_bottom_left("╚")
  #table.set_border_bottom_right("╝")
  table.set_max_colw(3,3,-1)
  #table.set_format(0, '\033[0;31m{content:>{width}}\033[0m')
  table.set_format(0, '{content:>{width}}')
  table.set_format(1, '{content:>{width}}')

  # add and format table header
  table.add_header(" Id", "-!-", "Todobidubido")
  #fmt_h = Term.sgr_esc("{content:<{width}}", flags="ub", fg=0x00, bg=0x76 )
  fmt_h = Table.sgr_esc("{content:<{width}}", flags="b", fg=0x76 )
  #fmt_h1 = "\033[48;5;\xca{content:>{width}}\033[0m"
  table.set_format(0, fmt_h, True)
  table.set_format(1, fmt_h, True)
  table.set_format(2, fmt_h, True)

  with open( os.path.dirname(__file__) + '/files/table_test' ) as fp:
    for line in fp: table.append_row(*line.strip().split(','))
  table.set_lt( 1, lambda f1, f2: int(f1.content) > int(f2.content) )
  table.set_sort_order( 1, 2 )
  table.sort()
  table.draw()
  table.flush()
  table.get_char_raw()
  print()
