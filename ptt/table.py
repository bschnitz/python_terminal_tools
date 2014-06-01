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
import copy

from term.twin import TWin
from functools import reduce


class TableFieldFormat():
  def __init__(self, width_min = 0, width_max = -1):
    self.width = {}
    self.width['min'] = width_min
    self.width['max'] = width_max
    self.width['act'] = None
    self.fmt = '{content:<{width}}'
    self.formatter = self.default_formatter
    self.lt = lambda f1, f2: f1.content < f2.content

  def default_formatter( self, field ):
    field_content = field.content[:self.width['act']]
    return self.fmt.format(content=field_content, width=self.width['act'])

  def set_format( self, fmt ): self.fmt = fmt

  def format( self, field ): return self.formatter( field )

class TableRowFormat():
  def __init__(self, num_cols):
    self.sort_order = range(num_cols)

  def set_sort_order(self, *column_indexes):
    self.sort_order = column_indexes

class TableField():
  def __init__(self, field_content, field_format):
    self.content = field_content
    self.fmt = field_format

  def get_formatted_content(self, field_format=None):
    if field_format == None: field_format = self.fmt
    return field_format.format(self)

  def __lt__(self, other): return self.fmt.lt(self, other)

class TableRow():
  def __init__(self, row_format, *cols):
    self.cols = cols
    self.fmt = row_format

  def __lt__( self, other ):
    for i in self.fmt.sort_order:
      if self.cols[i] < other.cols[i]: return True
      elif self.cols[i] > other.cols[i]: return False
    return False

class Table(TWin):
  """ Initialize a Table Terminal Window Object
  positional arguments:
      ncols:
          number of columns of the table

  optional arguments:
      x:  column in which the top left edge of the window is located,
          if not given, it will default to the x-Pos of the cursor
      y:  row in which the top left edge of the window is located
          if not given, it will default to the y-Pos of the cursor
      width:
          number of columns window will span.
          if width < 0: width = terminal_width - width - y + 1
          if not given: terminal_width - y + 1
      height:
          number of rows window will span.
          if height < 0: height = terminal_width - height - x + 1
          if not given:  height = terminal_heigth - x + 1
  """
  def __init__(self, ncols, x=None, y=None, width=None, height=None):
    self.ncols = ncols
    self.colsep = "  "
    self.rows = list()
    self.row_format = TableRowFormat(ncols)
    self.field_format = [TableFieldFormat() for _ in range(ncols)]
    self.header = None
    super().__init__( x, y, width, height )

  def add_header(self, *cols):
    self.test_coln(cols)
    row_format = TableRowFormat(self.ncols)
    field_format = [TableFieldFormat() for _ in range(self.ncols)]
    row = [TableField(col, fmt) for col,fmt in zip(cols, field_format)]
    self.header = TableRow(self.row_format, *row)

  def test_coln(self, *cols):
    if( len(*cols) != self.ncols ):
      error = "Number of Arguments specified must match number of columns."
      raise TypeError( error )

  def set_colw(self, which, *colw):
    self.test_coln(colw)
    for col_f, w in zip(self.field_format, colw): col_f.width[which] = int(w)

  def set_min_colw(self, *colw): self.set_colw( 'min', *colw )
  def set_max_colw(self, *colw): self.set_colw( 'max', *colw )

  def append_row(self, *cols):
    self.test_coln(cols)
    row = [TableField(col, fmt) for col,fmt in zip(cols, self.field_format)]
    self.rows.append( TableRow(self.row_format, *row) )

  def set_format( self, colnr, fmt, apply_on_header=False ):
    if not apply_on_header:
      self.field_format[colnr].set_format( fmt )
    else:
      if self.header != None:
        self.header.cols[colnr].fmt.set_format( fmt )
      else:
        error = "Header must be initialized, before its format can be changed."
        raise Exception( error )

  def test_column_sizes(self):
    for col_f in self.field_format:
      if col_f.width['max'] > 0 and col_f.width['max'] < col_f.width['min']:
        error = "minimum colum size exceeds maximum column size for column {0}"
        raise Exception( error.format(i) )

  def calculate_column_sizes(self):
    self.test_column_sizes()
    x, y, max_cum_colw, h = self.get_inner_dimensions()
    max_cum_colw -= len(self.colsep) * (self.ncols-1)

    rf = self.field_format

    # init maximum col sizes to terminal width, if they are -1
    for col_w in (col_f.width for col_f in self.field_format):
      col_w['act'] = max_cum_colw if col_w['max']<0 else col_w['max']

    i = 0
    width = max_cum_colw
    # reducable (in width) are all columns, which have min width < act width
    reducables = list(filter(lambda cf: cf.width['min'] < cf.width['act'], rf))
    cum_col_size = reduce( lambda size,cf: size+cf.width['act'], rf, 0 )
    while width > 0 and len(reducables) > 0:
      if i == 0:
        if cum_col_size <= width: break
        shrink_factor = width/cum_col_size
        cum_col_size = 0
      width_i = reducables[i].width
      width_i['act'] = int( shrink_factor * width_i['act'] )

      if width_i['act'] <= width_i['min']:
        width_i['act'] = width_i['min']
        width -= reducables.pop(i).width['act']
      else:
        cum_col_size += width_i['act']
        i = (i + 1) % len(reducables)

    if width < 0: # combined min width of colums is bigger than terminal width
      for col_f in reducables: col_f.width['act'] = col_f.width['min']
      cum_col_size = reduce( lambda size,cf: size+cf.width['act'], rf, 0 )
      shrink_factor = cum_col_size/max_cum_colw
      for cf in rf: cf.width['act'] = int( cf.width['act']*shrink_factor )

    # because of rounding down with int and because some of the columns
    # reduced to zero width, me might have some additional space to distribute
    # (we will not distribute that on columns which have zero width)
    ncols = reduce( lambda nc,cf: nc + 1 if cf.width['act']>0 else 0, rf, 0 )
    nc_diff = self.ncols - ncols
    cum_col_size = reduce( lambda size,cf: size+cf.width['act'], rf, 0 )
    cum_col_size += nc_diff * len(self.colsep)
    for cf in rf:
      if cum_col_size == max_cum_colw: break
      if cf.width['act'] > 0:
        if cf.width['act'] < cf.width['max'] or cf.width['max'] < 0:
          cf.width['act'] += 1
          cum_col_size += 1

    if self.header != None:
      for col,cf in zip(self.header.cols, rf):
        col.fmt.width['act'] = cf.width['act']


    return True

  def set_lt( self, ncol, lt ): self.field_format[ncol].lt = lt

  def set_sort_order( self, *column_indexes ):
    self.row_format.set_sort_order(*column_indexes)

  def sort( self ): self.rows.sort()

  def draw(self):
    self.calculate_column_sizes()
    seperators = (self.ncols-1) * [self.colsep] + ['']
    x, y, win_width, win_height = self.get_inner_dimensions()
    num_rows = min(win_height, len(self.rows))
    first_row = 0
    if self.header != None:
      self.move_xy(1, 1)
      for col, sep in zip( self.header.cols, seperators ):
        sys.stdout.write(col.get_formatted_content() + sep)
      first_row = 1
    for nrow in range(num_rows):
      self.move_xy(1, nrow+1+first_row)
      for col, sep in zip( self.rows[nrow].cols, seperators ):
        sys.stdout.write(col.get_formatted_content() + sep)
    super().draw()


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

  with open('table_test') as fp:
    for line in fp: table.append_row(*line.strip().split(','))
  table.set_lt( 1, lambda f1, f2: int(f1.content) > int(f2.content) )
  table.set_sort_order( 1, 2 )
  table.sort()
  table.draw()
  table.flush()
  table.get_char_raw()
  print()