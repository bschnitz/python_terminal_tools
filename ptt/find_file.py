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
from term.terminal import Term
from quicksel import QuickSel

class FindFile(QuickSel):
  def __init__( self, path=".", x=2, y=None, width=-1, height=25 ):
    super(FindFile, self).__init__( [], x, y, width, height )
    self.selections = self.scan_path( path )
    self.display_selection( 0 )

  def scan_path( self, path ):
    files = []
    for root, dirs, filenames in os.walk(path):
      for filename in filenames:
        files.append( (root + "/" + filename)[-self.width:] )
    return files

  def display_selection( self, time=1 ):
    self.sel_win.list( self.get_selection(time), "  ", 1 )

if __name__ == "__main__":
  with FindFile() as find_file:
    selected = find_file.event_loop()

  print(selected[0])
