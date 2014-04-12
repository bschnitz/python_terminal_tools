#!/usr/bin/env python3

import os
from term import Term
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
