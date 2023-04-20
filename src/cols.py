import re
from sym import *
from num import *

class Col:
    def __init__(self, t):
        self.names = t
        self.all = []
        self.x = []
        self.y = []
        self.klass = None

        for col_name in t:
            n = t.index(col_name)
            col_name = col_name.strip()
            if col_name[0].isupper():
                col = Num(n, col_name)
            else:
                col = Sym(n, col_name)
            self.all.append(col)

            if not col_name[-1] == "X":
                if "!" in col_name:
                    self.klass=col
                self.y.append(col) if re.findall("[!+-]$", col_name) else self.x.append(col)

    def add(self, row):
        for t in [self.x, self.y]:
            for col in t:
                col.add(row.cells[col.at])