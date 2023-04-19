from functools import cmp_to_key

from row import *
import sys

sys.path.append("./src")
from cols import *
from utils import *


class DATA:
    def __init__(self, src=None, rows=None):
        self.rows = []
        self.cols = None
        if src or rows:
            if isinstance(src, str):
                csv(src, self.add)
            else:
                self.cols = Col(src.cols.names)
                for row in rows:
                    self.add(row)

    def add(self, t):
        '''
        Adds row
        '''
        if self.cols:
            print("")
            t = t if isinstance(t, Row) else Row(t)
            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols = Col(t)

    def clone(data, ts={}):
        data1 = DATA()
        data1.add(data.cols.names)
        for _, t in enumerate(ts or {}):
            data1.add(t)
        return data1

    def stats(self, cols=None, nPlaces=2, what='mid'):
        stats_dict = dict(sorted({col.txt: rnd(getattr(col, what)(), nPlaces) for col in cols or self.cols.y}.items()))
        stats_dict["N"] = len(self.rows)
        return stats_dict

    def dist(self, row1, row2, cols=None):
        n, d = 0, 0
        for col in cols or self.cols.x:
            n = n + 1
            d = d + col.dist(row1.cells[col.at], row2.cells[col.at]) ** the['p']
        return (d / n) ** (1 / the['p'])

    def around(self, row1, rows=None, cols=None):

        if rows is None: rows = self.rows

        def function(row2):
            return {"row": row2, "dist": self.dist(row1, row2, cols)}

        mapped = map(function, rows)
        return sorted(mapped, key=lambda x: x["dist"])

    def half(self, rows=None, cols=None, above=None):
        def gap(row1,row2): 
            return self.dist(row1,row2,cols)
        def project(row):
            return {'row' : row, 'dist' : cosine(gap(row,A), gap(row,B), c)}
        rows = rows or self.rows
        some = many(rows,options['Halves'])
        A    = above if above and options['Reuse'] else any(some)
        tmp = sorted([{'row': r, 'dist': gap(r, A)} for r in some], key=lambda x: x['dist'])
        far = tmp[int((len(tmp) - 1) * options['Far'])]
        B    = far['row']
        c    = far['dist']
        left, right = [], []
        for n,tmp in enumerate(sorted(map(project, rows), key=lambda x: x['dist'])):
            if (n + 1) <= (len(rows) / 2):
                left.append(tmp["row"])
            else:
                right.append(tmp["row"])
        evals = 1 if options['Reuse'] and above else 2
        return left, right, A, B, c, evals

    def cluster(self, rows=None, min=None, cols=None, above=None):
        rows = rows or self.rows
        min = min or (len(rows) ** options['min'])
        cols = cols or self.cols.x
        node = {'data': self.clone(rows)}

        if len(rows) >= 2 * min:
            left, right, node['A'], node['B'], node['mid'], _ = self.half(rows, cols, above)
            node['left'] = self.cluster(left, min, cols, node['A'])
            node['right'] = self.cluster(right, min, cols, node['B'])
        return node

    def better(self, row1, row2):
        s1, s2, ys = 0, 0, self.cols.y
        for col in ys:
            x = col.norm(row1.cells[col.at])
            y = col.norm(row2.cells[col.at])
            s1 = s1 - math.exp(col.w * (x - y) / len(ys))
            s2 = s2 - math.exp(col.w * (y - x) / len(ys))
        return s1 / len(ys) < s2 / len(ys)

    def tree(self, rows = None , min = None, cols = None, above = None):
        rows = rows or self.rows
        min  = min or len(rows)**options['min']
        cols = cols or self.cols.x
        node = { 'data' : self.clone(rows) }
        if len(rows) >= 2*min:
            left, right, node['A'], node['B'], _, _ = self.half(rows,cols,above)
            node['left']  = self.tree(left,  min, cols, node['A'])
            node['right'] = self.tree(right, min, cols, node['B'])
        return node

    def sway(self):
        data = self
        def worker(rows, worse, evals0 = None, above = None):
            if len(rows) <= len(data.rows)**options['min']:
                return rows, many(worse, options['rest']*len(rows)), evals0
            else:
                l,r,A,B,c,evals = self.half(rows, None, above)
                if self.better(B,A):
                    l,r,A,B = r,l,B,A
                for row in r:
                    worse.append(row)
                return worker(l,worse,evals+evals0,A)
        best,rest,evals = worker(data.rows,[],0)
        return DATA.clone(self, best), DATA.clone(self, rest), evals

    def betters(self,n):
        key = cmp_to_key(lambda row1, row2: -1 if self.better(row1, row2) else 1)
        tmp = sorted(self.rows, key = key)
        if n is None:
            return tmp
        else:
            return tmp[1:n], tmp[n+1:]

    def RULE(self, ranges,maxSize):
        t={}
        for range in ranges:
            t[range.txt] = t.get(range.txt, [])
            t[range.txt].append({'lo':range.lo,'hi':range.hi,'at':range.at})
        return self.prune(t, maxSize)

    def showRule(rule):
        def pretty(range):
            return range['lo'] if range['lo'] == range['hi'] else [range['lo'], range['hi']]

        def merges(attr, ranges):
            return list(map(pretty, merge(sorted(ranges, key=lambda x: x['lo'])))), attr

        def merge(t0):
            t = []
            j = 0
            while j < len(t0):
                left = t0[j]
                right = None if j + 1 >= len(t0) else t0[j + 1]
                if right and left['hi'] == right['lo']:
                    left['hi'] = right['hi']
                    j = j + 1
                t.append({'lo': left['lo'], 'hi': left['hi']})
                j = j + 1
            return t if len(t0) == len(t) else merge(t)

        return kap(rule, merges)

    def xpln(self, data, best, rest):
        def v(has):
            return value(has, len(best.rows), len(rest.rows), 'best')

        tmp, self.maxSizes = [], {}
        for _, ranges in enumerate(bins(data.cols.x, {'best': best.rows, 'rest': rest.rows})):
            self.maxSizes[ranges[0].txt] = len(ranges)
            for _, range in enumerate(ranges):
                tmp.append({'range': range, 'max': len(ranges), 'val': v(range.y.has)})
        rule, most = firstN(sorted(tmp, key=lambda x: x['val'], reverse=True), self.score)
        return rule, most

    def selects(rule, rows):
        def disjunction(ranges, row):
            for rang in ranges:
                at = rang['at']
                x = row.cells[at]
                lo = rang['lo']
                hi = rang['hi']
                if x == '?' or (lo == hi and lo == x) or (lo <= x and x < hi):
                    return True
            return False

        def conjunction(row):
            for _, ranges in rule.items():
                if not disjunction(ranges, row):
                    return False
            return True

        def function(r):
            return r if conjunction(r) else None

        r = []
        for item in list(map(function, rows)):
            if item:
                r.append(item)
        return r