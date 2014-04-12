#!/usr/bin/env python3

import sys
import copy

from twin import TWin
from term import Term
from functools import reduce

class TableField():
  def __init__(self, width_min = 0, width_max = -1):
    self.width = {}
    self.width['min'] = width_min
    self.width['max'] = width_max
    self.width['act'] = None
    self.fmt = '{content:<{width}}'
    self.formatter = self.default_formatter

  def default_formatter( self, column_content ):
    formatted = self.fmt.format(content=column_content, width=self.width['act'])
    return formatted[:self.width['act']]

  def set_format( self, fmt ): self.fmt = fmt

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
    #self.rows = list()
    self.rows = [["12345", "98765", "Hallo Welt!"]]
    self.row_format = [TableField() for _ in range(ncols)]
    super().__init__( x, y, width, height )

  def test_coln(self, *cols):
    if( len(*cols) != self.ncols ):
      error = "Number of Arguments specified must match number of columns."
      raise TypeError( error )

  def set_colw(self, which, *colw):
    self.test_coln(colw)
    for col_f, w in zip(self.row_format, colw): col_f.width[which] = int(w)

  def set_min_colw(self, *colw): self.set_colw( 'min', *colw )
  def set_max_colw(self, *colw): self.set_colw( 'max', *colw )

  def push_row(self, *cols):
    self.test_coln(*cols)
    self.rows.append(copy.deepcopy(cols))

  def test_column_sizes(self):
    for col_f in self.row_format:
      if col_f.width['max'] > 0 and col_f.width['max'] < col_f.width['min']:
        error = "minimum colum size exceeds maximum column size for column {0}"
        raise Exception( error.format(i) )

  def calculate_column_sizes(self):
    self.test_column_sizes()
    x, y, max_cum_colw, h = self.get_inner_dimensions()
    max_cum_colw -= len(self.colsep) * (self.ncols-1)

    rf = self.row_format

    # init maximum col sizes to terminal width, if they are -1
    for col_w in (col_f.width for col_f in self.row_format):
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

    # because of rounding down with int, we might have to add some 1s
    cum_col_size = reduce( lambda size,cf: size+cf.width['act'], rf, 0 )
    for cf in rf:
      if cum_col_size == max_cum_colw: break
      if cf.width['act'] < cf.width['max'] or cf.width['max'] < 0:
        cf.width['act'] += 1
        cum_col_size += 1

    return True

  def draw(self):
    self.calculate_column_sizes()
    seperators = (self.ncols-1) * [self.colsep] + ['']
    x, y, win_width, win_height = self.get_inner_dimensions()
    num_rows = min(win_height, len(self.rows))
    for nrow in range(num_rows):
      self.move_xy(1, nrow+1)
      for col, fmt, sep in zip( self.rows[nrow], self.row_format, seperators ):
        formatted_text = fmt.formatter(col) + sep
        sys.stdout.write(formatted_text)
    super().draw()

    #super().draw()
    #self.move_write_xy( 1, 1, "hello worlds" )
    #self.calculate_column_sizes()
    #sizes = list(cf.width['act'] for cf in self.row_format)
    #self.move_write_xy( 1, 2, repr(sizes) )
    #self.move_write_xy( 1, 3, repr(self.get_inner_dimensions()) )

if __name__ == "__main__":
  table = Table(3, x=1, y=1)
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
  table.set_max_colw(3,2,-1)
  table.scroll_clear()
  table.draw()
  Term.move_xy(0, 0)
  table.flush()
  table.get_char_raw()
  print()
