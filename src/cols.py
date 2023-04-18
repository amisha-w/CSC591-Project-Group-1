import math , sys
sys.path.append("./src")
from sym import Sym
from num import Num

class Col:
    '''
    Create Num or Sym for non-skipped columns Columns
    '''
    def __init__(self, t):
        self.names = t
        self.all = []
        self.x = []
        self.y = []
        self.klass = None

        for column in t:
            if column[0].isupper():
                col = Num(t.index(column), column)
            else:
                col = Sym(t.index(column), column)
            self.all.append(col)

            if not column[-1] == "X":
                if "-" in column or "+" in column or "!" in column:
                    self.y.append(col)
                else:
                    self.x.append(col)
                if "!" in column:
                    self.klass=col

    def add(self, row):
        '''
        Add row to columns
        '''
        for list in [self.x, self.y]:
            for col in list:
                col.add(row.cells[col.at])